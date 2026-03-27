"""
SniperStation Telegram Bot
- Natural language queries via LLM agent (Claude or Ollama)
- Slash commands: /estado, /riego, /foto
- Alert forwarding from MQTT LWT events
- Scheduled email reports (daily x3, weekly x1, monthly x1)
"""

import asyncio
import logging
import os
import threading
from datetime import time as dtime

from dotenv import dotenv_values
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

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = get_backend()
    return _llm


def _is_authorized(update: Update) -> bool:
    return update.effective_chat.id == AUTHORIZED_CHAT_ID


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        return
    await update.message.reply_text(
        "🌵 SniperStation online.\n\n"
        "/estado — system status\n"
        "/riego <planta> — trigger irrigation (sucufer | sucurod)\n"
        "/foto <planta> — latest photo (sucufer | sucurod)\n\n"
        "Or just ask me anything about the plants."
    )


async def cmd_estado(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        return
    await update.message.reply_text("Consultando sensores…")
    try:
        from tools import get_device_status, get_exterior_conditions, get_water_level
        exterior = get_exterior_conditions()
        water = get_water_level()
        devices = get_device_status()

        temp = exterior.get("temperatura", {}).get("value")
        hum = exterior.get("humedad", {}).get("value")
        water_ok = water.get("level")

        lines = ["📡 *Estado del sistema*\n"]
        lines.append(f"🌡️ Exterior: {temp:.1f}°C / {hum:.1f}%" if temp and hum else "🌡️ Exterior: sin datos")
        lines.append(f"💧 Agua: {'✅ OK' if water_ok == 1 else '⚠️ VACÍO' if water_ok == 0 else 'N/A'}")
        lines.append("\n🔌 *Dispositivos:*")
        if devices:
            for device, last_seen in devices.items():
                lines.append(f"  • {device}: {last_seen}")
        else:
            lines.append("  Sin datos (ningún ESP32 conectado aún)")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def cmd_riego(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        return
    args = context.args
    if not args or args[0] not in ("sucufer", "sucurod"):
        await update.message.reply_text("Uso: /riego sucufer | /riego sucurod")
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
        await update.message.reply_text(f"✅ Riego iniciado para *{planta}*. Se detendrá automáticamente en 60s.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error al enviar comando: {e}")


async def cmd_foto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        return
    args = context.args
    if not args or args[0] not in ("sucufer", "sucurod"):
        await update.message.reply_text("Uso: /foto sucufer | /foto sucurod")
        return

    planta = args[0]
    import glob
    photos = sorted(glob.glob(f"/var/sniperstation/photos/{planta}/*.jpg"))
    if not photos:
        await update.message.reply_text(f"No hay fotos disponibles para {planta}.")
        return

    latest = photos[-1]
    try:
        with open(latest, "rb") as f:
            await update.message.reply_photo(photo=f, caption=f"📷 {planta} — {latest.split('/')[-1]}")
    except Exception as e:
        await update.message.reply_text(f"Error al enviar foto: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Natural language handler — routes to LLM agent."""
    if not _is_authorized(update):
        return

    user_text = update.message.text
    await update.message.reply_chat_action("typing")

    def _run_llm():
        return _get_llm().query(user_text)

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, _run_llm)
    await update.message.reply_text(response)


async def _scheduled_daily(context: ContextTypes.DEFAULT_TYPE) -> None:
    ok = send_daily_report()
    if not ok:
        await context.bot.send_message(chat_id=AUTHORIZED_CHAT_ID, text="⚠️ Error enviando reporte diario por email.")


async def _scheduled_weekly(context: ContextTypes.DEFAULT_TYPE) -> None:
    ok = send_weekly_report()
    if not ok:
        await context.bot.send_message(chat_id=AUTHORIZED_CHAT_ID, text="⚠️ Error enviando reporte semanal por email.")


async def _scheduled_monthly(context: ContextTypes.DEFAULT_TYPE) -> None:
    ok = send_monthly_report()
    if not ok:
        await context.bot.send_message(chat_id=AUTHORIZED_CHAT_ID, text="⚠️ Error enviando reporte mensual por email.")


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("estado", cmd_estado))
    app.add_handler(CommandHandler("riego", cmd_riego))
    app.add_handler(CommandHandler("foto", cmd_foto))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Daily reports at 07:00, 13:00, 19:00 America/New_York (UTC-4 in summer)
    jq = app.job_queue
    for hour in (11, 17, 23):  # UTC equivalents
        jq.run_daily(_scheduled_daily, time=dtime(hour=hour, minute=0))

    # Weekly report every Monday 08:00 local (12:00 UTC)
    jq.run_daily(_scheduled_weekly, time=dtime(hour=12, minute=0), days=(0,))

    # Monthly report on the 1st at 08:00 local
    jq.run_monthly(_scheduled_monthly, when=dtime(hour=12, minute=0), day=1)

    logger.info("SniperStation bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
