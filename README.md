# SniperStation

Automatic irrigation system and weather station for two succulent planters located outdoors in Orlando, Florida.

**SucuFer** — Fernanda's succulent, planted April 22, 2024
**SucuRod** — Rodrigo's succulent, planted April 22, 2024

Monitors environmental conditions (temperature, humidity, light, soil moisture) and waters automatically based on sensor readings. Provides a color touchscreen dashboard (CYD), web dashboard (Grafana), Telegram push alerts, and full historical data logging.

---

## System Overview

```
[OUTSIDE]                                   [INSIDE]
Station-485 (main controller)               CYD ESP32-2432S028 x2
├── BH1750 light sensor    → Port A1        ├── Master Bedroom (SHT30 on CN1)
├── SHT30 outdoor          → Port A2        └── Kids Bedroom   (SHT30 on CN1)
├── Earth Sensor SucuFer   → Port B1                │
├── Earth Sensor SucuRod   → Port B2                │
├── Relay → Pump SucuFer   → Port C1                │
├── Relay → Pump SucuRod   → Port C2                │
└── XKC-Y25 water level    → Port B/C               │
          │                                         │
          └────────── WiFi → MQTT ──────────────────┘
                            │
                     [Proxmox LXC]
                     ├── Mosquitto (MQTT broker)
                     ├── InfluxDB 2.x (time-series database)
                     ├── Grafana (web/mobile dashboard)
                     └── Telegram Bot (push alerts)
```

---

## The Plants

| Plant | Owner | Age | Planted |
|---|---|---|---|
| SucuFer | Fernanda | ~2 years | April 22, 2024 |
| SucuRod | Rodrigo | ~2 years | April 22, 2024 |

The CYD touchscreen detail view for each plant displays the owner's photo with their succulent as the background, along with planting date and current soil moisture.

---

## Hardware Requirements

| Component | Model | Status |
|---|---|---|
| Main controller | M5Stack Station-485 | Have it |
| Light sensor | DLight BH1750 | Have it |
| Temp/humidity x2 | SHT30 IOT-TH02 | Purchased |
| Grove↔Dupont cable | HY2.0-4P to 2.54mm | Purchased |
| Peristaltic pumps x2 | DC 12-24V, 80mA | Purchased — arriving late April |
| Water level sensor | XKC-Y25-V + DFRobot driver | Purchased |
| Soil sensors x2 | M5Stack Earth Sensor | Purchased |
| Relay modules x2 | M5Stack Mini 3A Relay | Purchased |
| Indoor display x2 | CYD ESP32-2432S028 | Purchased — arriving Saturday |
| DC adapter | 12V 2A, 5.5mm jack | **Pending purchase** |
| Outdoor enclosure | IP65+, ventilated | **Pending purchase** |
| Indoor enclosure x2 | Custom 3D printed | **Pending design** |

Full BOM → [hardware/BOM.md](hardware/BOM.md)

---

## Software Stack

| Service | Port | Role |
|---|---|---|
| Mosquitto | 1883 | MQTT broker |
| InfluxDB 2.x | 8086 | Time-series database |
| Grafana | 3000 | Web/mobile dashboard |
| Telegram Bot | — | Push notifications |

All services run in a single Proxmox LXC container.

---

## Repository Structure

```
sniperstation/
├── hardware/
│   ├── BOM.md                        # Full bill of materials
│   ├── schematics/                   # Wiring diagrams
│   ├── datasheets/                   # Component datasheet references
│   └── enclosure/                    # Enclosure specifications + OpenSCAD
├── firmware/
│   ├── station485/                   # Arduino IDE — ESP32 (Station-485)
│   └── cyd_indoor/                   # Arduino IDE — CYD ESP32 (indoor x2)
├── software/
│   ├── mosquitto/                    # Broker config
│   ├── influxdb/                     # Database setup
│   ├── grafana/                      # Dashboard JSON exports
│   └── telegram_bot/                 # Alert bot
├── assets/
│   └── photos/                       # SucuFer + SucuRod plant photos (CYD backgrounds)
├── README.md
├── ROADMAP.md
├── TODO.md
└── CHANGELOG.md
```

---

## Irrigation Logic

```
Every 6 hours (via RTC BM8563):
  FOR each plant (SucuFer, SucuRod):
    IF soil_moisture < dry_threshold:
      IF air_humidity < 85% (not raining):
        IF water_available == TRUE:
          activate_pump(plant, 20 seconds)   // ~33ml at 100ml/min
          wait 30 minutes
          re-read soil_moisture
          IF still_dry: send Telegram alert
        ELSE:
          send Telegram alert "Water tank empty"
```

Pump flow reference: ~100 ml/min at 12V → 20 seconds = ~33 ml

---

## Soil Moisture Thresholds (calibrate with actual planters)

| State | Range | Action |
|---|---|---|
| Dry | < 30% | Irrigate |
| Moist | 30–60% | No action |
| Wet | > 60% | Alert — overwatering risk |

---

## Telegram Alerts

- Irrigation executed (SucuFer / SucuRod + ml delivered)
- Water tank empty
- Soil dry for more than 24h
- Outdoor temperature > 38°C (Orlando extreme heat)
- Sensor disconnected / read error

---

## CYD Touchscreen UI

| View | Content |
|---|---|
| Screensaver | Logo + compact temp summary all rooms |
| Main view | All sensors: exterior + master + kids + SucuFer + SucuRod |
| SucuFer detail | Fernanda's photo background + soil moisture + last watered + plant age |
| SucuRod detail | Rodrigo's photo background + soil moisture + last watered + plant age |

---

## Important Notes

### Orlando Heat
Station-485 max operating temperature is **60°C**. In direct Florida summer sun, enclosures can exceed this easily.
**Mandatory:** install in shade + passive or active ventilation. A 5V fan from inventory can be added if needed.

### GPIO Constraint — Port B2
Uses ESP32 GPIO G36, which **cannot be configured as OUTPUT**.
Earth Sensor SucuRod is read-only (analog input) — correct for this use case.
**Never connect a relay to Port B.**

### I2C Shared Bus (Ports A1/A2)
BH1750 (address 0x23) and SHT30 (address 0x44) share the same I2C bus on G32/G33.
Different addresses — no conflict.

---

## License

Open Hardware — CERN OHL v2 Permissive
Software — MIT
