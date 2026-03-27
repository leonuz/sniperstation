"""
Scheduled email reports via Resend API.
- Daily x3: temperature + humidity + soil status
- Weekly x1: irrigation summary + trends
- Monthly x1: full historical stats
"""

import os
from datetime import datetime

import resend
from tools import (
    get_device_status,
    get_exterior_conditions,
    get_historical_stats,
    get_interior_conditions,
    get_irrigation_history,
    get_soil_moisture,
    get_water_level,
)


def _send(subject: str, html: str) -> bool:
    resend.api_key = os.environ["RESEND_API_KEY"]
    try:
        resend.Emails.send({
            "from": os.environ["RESEND_FROM"],
            "to": os.environ["RESEND_TO"],
            "subject": subject,
            "html": html,
        })
        return True
    except Exception as e:
        print(f"[reports] email error: {e}")
        return False


def _fmt_value(v, unit: str = "") -> str:
    if v is None:
        return "N/A"
    if isinstance(v, float):
        return f"{v:.1f}{unit}"
    return f"{v}{unit}"


def send_daily_report() -> bool:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    exterior = get_exterior_conditions(hours=1)
    interior = get_interior_conditions(hours=1)
    soil = get_soil_moisture(hours=1)
    water = get_water_level()

    temp_ext = _fmt_value(exterior.get("temperatura", {}).get("value"), "°C")
    hum_ext = _fmt_value(exterior.get("humedad", {}).get("value"), "%")
    water_status = "✅ OK" if water.get("level") == 1 else ("⚠️ EMPTY" if water.get("level") == 0 else "N/A")

    interior_rows = ""
    for key, data in interior.items():
        interior_rows += f"<tr><td>{key}</td><td>{_fmt_value(data.get('value'))}</td></tr>"

    soil_rows = ""
    for key, data in soil.items():
        soil_rows += f"<tr><td>{key}</td><td>{_fmt_value(data.get('value'))}</td></tr>"

    html = f"""
    <h2>🌵 SniperStation — Daily Report</h2>
    <p><b>{now}</b></p>
    <h3>Exterior</h3>
    <ul>
      <li>Temperature: {temp_ext}</li>
      <li>Humidity: {hum_ext}</li>
      <li>Water level: {water_status}</li>
    </ul>
    <h3>Interior</h3>
    <table border="1" cellpadding="4"><tr><th>Sensor</th><th>Value</th></tr>{interior_rows}</table>
    <h3>Soil Moisture</h3>
    <table border="1" cellpadding="4"><tr><th>Planter</th><th>Value</th></tr>{soil_rows}</table>
    """
    return _send(f"SniperStation Daily — {now}", html)


def send_weekly_report() -> bool:
    now = datetime.now().strftime("%Y-%m-%d")
    irrigations = get_irrigation_history(hours=168)
    devices = get_device_status()

    irrigation_rows = ""
    for event in irrigations:
        irrigation_rows += f"<tr><td>{event.get('measurement','?')}</td><td>{event.get('time','?')}</td></tr>"
    if not irrigation_rows:
        irrigation_rows = "<tr><td colspan='2'>No irrigation events this week</td></tr>"

    device_rows = ""
    for device, last_seen in devices.items():
        device_rows += f"<tr><td>{device}</td><td>{last_seen}</td></tr>"

    html = f"""
    <h2>🌵 SniperStation — Weekly Report</h2>
    <p><b>Week ending {now}</b></p>
    <h3>Irrigation Events (last 7 days)</h3>
    <table border="1" cellpadding="4"><tr><th>Pump</th><th>Time</th></tr>{irrigation_rows}</table>
    <h3>Device Last Seen</h3>
    <table border="1" cellpadding="4"><tr><th>Device</th><th>Last Seen</th></tr>{device_rows}</table>
    """
    return _send(f"SniperStation Weekly — {now}", html)


def send_monthly_report() -> bool:
    now = datetime.now().strftime("%Y-%m")
    measurements = [
        "sniperstation/exterior/temperatura",
        "sniperstation/exterior/humedad",
        "sniperstation/exterior/luz",
    ]
    stats_rows = ""
    for m in measurements:
        stats = get_historical_stats(m, hours=720)
        label = m.split("/")[-1]
        stats_rows += (
            f"<tr><td>{label}</td>"
            f"<td>{_fmt_value(stats.get('min'))}</td>"
            f"<td>{_fmt_value(stats.get('mean'))}</td>"
            f"<td>{_fmt_value(stats.get('max'))}</td></tr>"
        )

    html = f"""
    <h2>🌵 SniperStation — Monthly Report</h2>
    <p><b>{now}</b></p>
    <h3>30-Day Statistics</h3>
    <table border="1" cellpadding="4">
      <tr><th>Sensor</th><th>Min</th><th>Mean</th><th>Max</th></tr>
      {stats_rows}
    </table>
    """
    return _send(f"SniperStation Monthly — {now}", html)
