"""
SniperStation Telegram Bot.

Features:
- Natural language queries via LLM agent (Claude or Ollama)
- Commands: /start, /estado, /riego, /foto
- MQTT LWT alert forwarding (device offline notifications)
- Scheduled email reports: daily x3, weekly x1, monthly x1
"""

import asyncio
import logging
import os
from datetime import time as dtime

import paho.mqtt.client as mqtt
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from agent import get_backend
from reports import send_daily_report, send_monthly_report, send_weekly_report

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

AUTHORIZED_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])

# Bilingual UI strings indexed by lang: 0=EN, 1=ES
STRINGS = {
    "start": [
        "🌵 SniperStation online.\n\n"
        "/estado — system status\n"
        "/riego <plant> — trigger irrigation (sucufer | sucurod)\n"
        "/foto <plant> — latest photo (sucufer | sucurod)\n\n"
        "Or just ask me anything about the plants.",

        "🌵 SniperStation en línea.\n\n"
        "/estado — estado del sistema\n"
        "/riego <planta> — riego manual (sucufer | sucurod)\n"
        "/foto <planta> — última foto (sucufer | sucurod)\n\n"
        "O pregúntame lo que quieras sobre las plantas.",
    ],
    "checking": ["Checking sensors…", "Consultando sensores…"],
    "no_data": ["No data (no ESP32 connected yet)", "Sin datos (ningún ESP32 conectado aún)"],
    "exterior": ["Exterior", "Exterior"],
    "water_ok": ["✅ OK", "✅ OK"],
    "water_empty": ["⚠️ EMPTY", "⚠️ VACÍO"],
    "water_na": ["N/A", "N/A"],
    "devices": ["Devices", "Dispositivos"],
    "status_header": ["📡 *System status*\n", "📡 *Estado del sistema*\n"],
    "riego_usage": ["Usage: /riego sucufer | /riego sucurod", "Uso: /riego sucufer | /riego sucurod"],
    "riego_ok": ["✅ Irrigation started for *{plant}*. Will stop automatically in 60s.",
                 "✅ Riego iniciado para *{plant}*. Se detendrá automáticamente en 60s."],
    "riego_error": ["Error sending command: {e}", "Error al enviar comando: {e}"],
    "foto_usage": ["Usage: /foto sucufer | /foto sucurod", "Uso: /foto sucufer | /foto sucurod"],
    "foto_none": ["No photos available for {plant}.", "No hay fotos disponibles para {plant}."],
    "foto_error": ["Error sending photo: {e}", "Error al enviar foto: {e}"],
    "foto_caption": ["📷 {plant} — {filename}", "📷 {plant} — {filename}"],
    "lwt_alert": ["⚠️ Device *{device}* went offline.", "⚠️ El dispositivo *{device}* se desconectó."],
    "report_daily_error": ["⚠️ Error sending daily email report.", "⚠️ Error enviando reporte diario por email."],
    "report_weekly_error": ["⚠️ Error sending weekly email report.", "⚠️ Error enviando reporte semanal por email."],
    "report_monthly_error": ["⚠️ Error sending monthly email report.", "⚠️ Error enviando reporte mensual por email."],
}

# Default language index: 0=EN, 1=ES
_LANG = int(os.environ.get("BOT_LANG", "1"))

_llm = None
# Reference to the running application, shared with the MQTT thread
_app = None


def t(key: str, **kwargs) -> str:
    """Return the UI string for the current language, with optional format args."""
    s = STRINGS[key][_LANG]
    return s.format(**kwargs) if kwargs else s


def _get_llm():
    global _llm
    if _llm is None:
        _llm = get_backend()
    return _llm


def _is_authorized(update: Update) -> bool:
    return update.effective_chat.id == AUTHORIZED_CHAT_ID


# --- MQTT LWT listener ---

def _on_lwt_message(client, userdata, message):
    """Forward device offline LWT messages to Telegram."""
    payload = message.payload.decode("utf-8", errors="ignore").strip()
    if payload != "offline":
        return

    # Extract device name from topic: sniperstation/sistema/lwt/<device>
    parts = message.topic.split("/")
    device = parts[-1] if len(parts) >= 4 else message.topic

    logger.warning("LWT offline received for device: %s", device)

    if _app is None:
        return

    async def _send_alert():
        await _app.bot.send_message(
            chat_id=AUTHORIZED_CHAT_ID,
            text=t("lwt_alert", device=device),
            parse_mode="Markdown",
        )

    asyncio.run_coroutine_threadsafe(_send_alert(), _app.update_queue._loop)


def _start_mqtt_listener():
    """Start MQTT client in a background thread, subscribing to LWT topics."""
    client = mqtt.Client(client_id="telegram_bot_lwt")
    client.username_pw_set(
        username="telegram_bot",
        password=os.environ["MQTT_PASS_BOT"],
    )
    client.on_message = _on_lwt_message

    def _on_connect(c, userdata, flags, rc):
        if rc == 0:
            c.subscribe("sniperstation/sistema/lwt/#")
            logger.info("MQTT LWT listener connected and subscribed")
        else:
            logger.error("MQTT LWT listener failed to connect, rc=%d", rc)

    client.on_connect = _on_connect
    client.connect("localhost", 1883, keepalive=60)
    client.loop_start()


# --- Command handlers ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        return
    await update.message.reply_text(t("start"))


async def cmd_estado(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        return
    await update.message.reply_text(t("checking"))
    try:
        from tools import get_device_status, get_exterior_conditions, get_water_level
        exterior = get_exterior_conditions()
        water = get_water_level()
        devices = get_device_status()

        temp = exterior.get("temperatura", {}).get("value")
        hum = exterior.get("humedad", {}).get("value")
        water_val = water.get("level")

        if water_val == 1:
            water_str = t("water_ok")
        elif water_val == 0:
            water_str = t("water_empty")
        else:
            water_str = t("water_na")

        lines = [t("status_header")]
        lines.append(f"🌡️ {t('exterior')}: {temp:.1f}°C / {hum:.1f}%" if temp and hum else f"🌡️ {t('exterior')}: {t('no_data')}")
        lines.append(f"💧 {t('water_ok')[:2]}: {water_str}")
        lines.append(f"\n🔌 *{t('devices')}:*")

        if devices:
            for device, last_seen in devices.items():
                lines.append(f"  • {device}: {last_seen}")
        else:
            lines.append(f"  {t('no_data')}")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_riego(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        return
    args = context.args
    if not args or args[0] not in ("sucufer", "sucurod"):
        await update.message.reply_text(t("riego_usage"))
        return

    planta = args[0]
    pump_map = {"sucufer": "1", "sucurod": "2"}
    pump_id = pump_map[planta]

    try:
        import paho.mqtt.publish as publish
        publish.single(
            topic=f"sniperstation/sistema/comando/bomba{pump_id}",
            payload="1",
            hostname="localhost",
            port=1883,
            auth={"username": "telegram_bot", "password": os.environ["MQTT_PASS_BOT"]},
        )
        await update.message.reply_text(t("riego_ok", plant=planta), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(t("riego_error", e=e))


async def cmd_foto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        return
    args = context.args
    if not args or args[0] not in ("sucufer", "sucurod"):
        await update.message.reply_text(t("foto_usage"))
        return

    planta = args[0]
    import glob
    photos = sorted(glob.glob(f"/var/sniperstation/photos/{planta}/*.jpg"))
    if not photos:
        await update.message.reply_text(t("foto_none", plant=planta))
        return

    latest = photos[-1]
    try:
        with open(latest, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=t("foto_caption", plant=planta, filename=latest.split("/")[-1]),
            )
    except Exception as e:
        await update.message.reply_text(t("foto_error", e=e))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route free-text messages to the LLM agent."""
    if not _is_authorized(update):
        return

    user_text = update.message.text
    await update.message.reply_chat_action("typing")

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: _get_llm().query(user_text))
    await update.message.reply_text(response)


# --- Scheduled report jobs ---

async def _scheduled_daily(context: ContextTypes.DEFAULT_TYPE) -> None:
    if not send_daily_report():
        await context.bot.send_message(chat_id=AUTHORIZED_CHAT_ID, text=t("report_daily_error"))


async def _scheduled_weekly(context: ContextTypes.DEFAULT_TYPE) -> None:
    if not send_weekly_report():
        await context.bot.send_message(chat_id=AUTHORIZED_CHAT_ID, text=t("report_weekly_error"))


async def _scheduled_monthly(context: ContextTypes.DEFAULT_TYPE) -> None:
    if not send_monthly_report():
        await context.bot.send_message(chat_id=AUTHORIZED_CHAT_ID, text=t("report_monthly_error"))


def main() -> None:
    global _app

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    _app = ApplicationBuilder().token(token).build()

    _app.add_handler(CommandHandler("start", cmd_start))
    _app.add_handler(CommandHandler("estado", cmd_estado))
    _app.add_handler(CommandHandler("riego", cmd_riego))
    _app.add_handler(CommandHandler("foto", cmd_foto))
    _app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Daily reports at 07:00, 13:00, 19:00 America/New_York (UTC-4 in EDT)
    jq = _app.job_queue
    for hour in (11, 17, 23):
        jq.run_daily(_scheduled_daily, time=dtime(hour=hour, minute=0))

    # Weekly report every Monday 08:00 local (12:00 UTC)
    jq.run_daily(_scheduled_weekly, time=dtime(hour=12, minute=0), days=(0,))

    # Monthly report on the 1st at 08:00 local (12:00 UTC)
    jq.run_monthly(_scheduled_monthly, when=dtime(hour=12, minute=0), day=1)

    _start_mqtt_listener()

    logger.info("SniperStation bot starting...")
    _app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
