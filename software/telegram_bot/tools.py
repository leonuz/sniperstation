"""
InfluxDB query tools for the SniperStation Telegram bot agent.
All functions return plain dicts suitable for JSON serialization.
"""

import os
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient

_client = None


def _get_client() -> InfluxDBClient:
    global _client
    if _client is None:
        _client = InfluxDBClient(
            url=os.environ["INFLUXDB_URL"],
            token=os.environ["INFLUXDB_READ_TOKEN"],
            org=os.environ["INFLUXDB_ORG"],
        )
    return _client


def _query(flux: str) -> list[dict]:
    """Execute a Flux query and return rows as list of dicts."""
    api = _get_client().query_api()
    tables = api.query(flux)
    rows = []
    for table in tables:
        for record in table.records:
            rows.append({
                "field": record.get_field(),
                "value": record.get_value(),
                "time": record.get_time().isoformat() if record.get_time() else None,
                "measurement": record.get_measurement(),
            })
    return rows


def get_exterior_conditions(hours: int = 1) -> dict:
    """Return the latest exterior temperature, humidity, and light level."""
    flux = f"""
    from(bucket: "{os.environ['INFLUXDB_BUCKET']}")
      |> range(start: -{hours}h)
      |> filter(fn: (r) => r._measurement =~ /sniperstation\\/exterior\\/.*/)
      |> last()
    """
    rows = _query(flux)
    result = {}
    for r in rows:
        field = r["measurement"].split("/")[-1]
        result[field] = {"value": r["value"], "time": r["time"]}
    return result


def get_soil_moisture(hours: int = 1) -> dict:
    """Return latest soil moisture readings for both planters."""
    flux = f"""
    from(bucket: "{os.environ['INFLUXDB_BUCKET']}")
      |> range(start: -{hours}h)
      |> filter(fn: (r) => r._measurement =~ /sniperstation\\/exterior\\/suelo.*/)
      |> last()
    """
    rows = _query(flux)
    result = {}
    for r in rows:
        key = r["measurement"].split("/")[-1]
        result[key] = {"value": r["value"], "time": r["time"]}
    return result


def get_interior_conditions(room: str = "all", hours: int = 1) -> dict:
    """Return latest temperature and humidity for indoor units (master/kids)."""
    if room == "all":
        filter_expr = 'r._measurement =~ /sniperstation\\/interior\\/.+/'
    else:
        filter_expr = f'r._measurement =~ /sniperstation\\/interior\\/{room}\\/.+/'
    flux = f"""
    from(bucket: "{os.environ['INFLUXDB_BUCKET']}")
      |> range(start: -{hours}h)
      |> filter(fn: (r) => {filter_expr})
      |> last()
    """
    rows = _query(flux)
    result = {}
    for r in rows:
        parts = r["measurement"].split("/")
        key = f"{parts[-2]}/{parts[-1]}" if len(parts) >= 2 else r["measurement"]
        result[key] = {"value": r["value"], "time": r["time"]}
    return result


def get_water_level(hours: int = 1) -> dict:
    """Return latest water reservoir level (digital: 1=OK, 0=empty)."""
    flux = f"""
    from(bucket: "{os.environ['INFLUXDB_BUCKET']}")
      |> range(start: -{hours}h)
      |> filter(fn: (r) => r._measurement =~ /sniperstation\\/exterior\\/agua.*/)
      |> last()
    """
    rows = _query(flux)
    if rows:
        return {"level": rows[0]["value"], "time": rows[0]["time"]}
    return {"level": None, "time": None}


def get_irrigation_history(hours: int = 24) -> list[dict]:
    """Return pump activation history for the last N hours."""
    flux = f"""
    from(bucket: "{os.environ['INFLUXDB_BUCKET']}")
      |> range(start: -{hours}h)
      |> filter(fn: (r) => r._measurement =~ /sniperstation\\/exterior\\/bomba.*/)
      |> filter(fn: (r) => r._value == 1.0)
    """
    return _query(flux)


def get_device_status() -> dict:
    """Return last-seen timestamp for all devices based on most recent data."""
    flux = f"""
    from(bucket: "{os.environ['INFLUXDB_BUCKET']}")
      |> range(start: -24h)
      |> last()
      |> keep(columns: ["_measurement", "_time"])
    """
    rows = _query(flux)
    devices: dict = {}
    for r in rows:
        parts = r["measurement"].split("/")
        device = parts[2] if len(parts) > 2 else r["measurement"]
        if device not in devices or r["time"] > devices[device]:
            devices[device] = r["time"]
    return devices


def get_historical_stats(field: str, hours: int = 168) -> dict:
    """Return min/max/mean for a given measurement over the past N hours."""
    flux = f"""
    data = from(bucket: "{os.environ['INFLUXDB_BUCKET']}")
      |> range(start: -{hours}h)
      |> filter(fn: (r) => r._measurement == "{field}")

    mean = data |> mean() |> map(fn: (r) => ({{ r with stat: "mean" }}))
    min  = data |> min()  |> map(fn: (r) => ({{ r with stat: "min" }}))
    max  = data |> max()  |> map(fn: (r) => ({{ r with stat: "max" }}))

    union(tables: [mean, min, max])
    """
    rows = _query(flux)
    result = {}
    for r in rows:
        result[r.get("stat", "?")] = r["value"]
    return result


# Tool definitions for the LLM agent
TOOL_DEFINITIONS = [
    {
        "name": "get_exterior_conditions",
        "description": "Get the latest exterior temperature, humidity, and light level from Station-485.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hours": {"type": "integer", "description": "How many hours back to look (default 1)", "default": 1}
            },
        },
    },
    {
        "name": "get_soil_moisture",
        "description": "Get the latest soil moisture readings for both succulent planters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hours": {"type": "integer", "description": "How many hours back to look (default 1)", "default": 1}
            },
        },
    },
    {
        "name": "get_interior_conditions",
        "description": "Get temperature and humidity from the indoor CYD displays (master bedroom and kids bedroom).",
        "input_schema": {
            "type": "object",
            "properties": {
                "room": {"type": "string", "description": "Room: 'master', 'kids', or 'all' (default)", "default": "all"},
                "hours": {"type": "integer", "description": "How many hours back to look (default 1)", "default": 1},
            },
        },
    },
    {
        "name": "get_water_level",
        "description": "Get the current water reservoir level (1=OK, 0=empty).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_irrigation_history",
        "description": "Get the irrigation (pump activation) history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "hours": {"type": "integer", "description": "How many hours back to look (default 24)", "default": 24}
            },
        },
    },
    {
        "name": "get_device_status",
        "description": "Get the last-seen timestamp for all connected devices.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_historical_stats",
        "description": "Get min/max/mean statistics for a specific sensor measurement over time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "field": {"type": "string", "description": "Full MQTT topic/measurement path"},
                "hours": {"type": "integer", "description": "Hours back to analyze (default 168 = 1 week)", "default": 168},
            },
            "required": ["field"],
        },
    },
]

TOOL_DISPATCH = {
    "get_exterior_conditions": get_exterior_conditions,
    "get_soil_moisture": get_soil_moisture,
    "get_interior_conditions": get_interior_conditions,
    "get_water_level": get_water_level,
    "get_irrigation_history": get_irrigation_history,
    "get_device_status": get_device_status,
    "get_historical_stats": get_historical_stats,
}
