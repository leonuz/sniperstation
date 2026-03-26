# System Overview — SniperStation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OUTDOOR UNIT                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │               M5Stack Station-485                    │                   │
│  │                    (ESP32)                           │                   │
│  │                                                      │                   │
│  │  Port A1 ──── BH1750 (Light, I2C 0x23)             │                   │
│  │  Port A2 ──── SHT30 outdoor (Temp/Hum, I2C 0x44)   │                   │
│  │  Port B1 ──── Earth Sensor 1 (SucuFer, Analog)     │                   │
│  │  Port B2 ──── Earth Sensor 2 (SucuRod, Analog)     │                   │
│  │  Port C1 ──── Relay 1 ──── Pump 1 (SucuFer)        │                   │
│  │  Port C2 ──── Relay 2 ──── Pump 2 (SucuRod)        │                   │
│  │  GPIO  ────── XKC-Y25 (Water level, Digital)        │                   │
│  │                                                      │                   │
│  │  PWR485 ───── 12V 2A DC Adapter                     │                   │
│  │  WiFi ──────────────────────────────────────────────┼──► MQTT Broker   │
│  └─────────────────────────────────────────────────────┘                   │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  ┌──────────────────┐    │
│  │ Pump 1   │  │ Pump 2   │  │ XKC-Y25 Sensor  │  │ TimerCam X       │    │
│  │ 12V 80mA │  │ 12V 80mA │  │ + DFRobot driver│  │ OV3660 3MP       │    │
│  │ → SucuFer│  │ → SucuRod│  │ Water reservoir │  │ ESP32 + battery  │    │
│  │          │  │          │  │ (non-contact)   │  │ WiFi → HTTP/MQTT │    │
│  │ FOV 66.5°        │    │
│  │ sleep: 2µA       │    │
│  └──────────┘  └──────────┘  └─────────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         INDOOR UNIT — MASTER BEDROOM                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │          CYD ESP32-2432S028  (ROOM_ID=master)        │                   │
│  │                                                      │                   │
│  │  CN1 GPIO21 ── I2C SDA ── SHT30 (0x44)              │                   │
│  │  CN1 GPIO22 ── I2C SCL ── SHT30 (0x44)              │                   │
│  │  10KΩ pull-ups on SDA + SCL                         │                   │
│  │                                                      │                   │
│  │  [TFT 2.8" 240x320 color] — integrated              │                   │
│  │  [XPT2046 resistive touch] — integrated             │                   │
│  │  [SHT30 cased] ────────── top of enclosure, exposed │                   │
│  │                                                      │                   │
│  │  WiFi ──────────────────────────────────────────────┼──► MQTT Broker   │
│  └─────────────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         INDOOR UNIT — KIDS BEDROOM                          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │          CYD ESP32-2432S028  (ROOM_ID=kids)          │                   │
│  │                                                      │                   │
│  │  CN1 GPIO21 ── I2C SDA ── SHT30 (0x44)              │                   │
│  │  CN1 GPIO22 ── I2C SCL ── SHT30 (0x44)              │                   │
│  │  10KΩ pull-ups on SDA + SCL                         │                   │
│  │                                                      │                   │
│  │  [TFT 2.8" 240x320 color] — integrated              │                   │
│  │  [XPT2046 resistive touch] — integrated             │                   │
│  │  [SHT30 cased] ────────── top of enclosure, exposed │                   │
│  │                                                      │                   │
│  │  WiFi ──────────────────────────────────────────────┼──► MQTT Broker   │
│  └─────────────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROXMOX LXC (Server)                                │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Mosquitto   │  │  InfluxDB    │  │ Grafana  │  │  Telegram Bot    │   │
│  │  MQTT Broker │→ │  2.x         │→ │  :3000   │  │  (Python)        │   │
│  │  :1883       │  │  :8086       │  │          │  │                  │   │
│  └──────────────┘  └──────────────┘  └──────────┘  └──────────────────┘   │
│         ▲                                                    ▲              │
│         │                                                    │              │
│    MQTT data from                                    Alerts + commands      │
│    Station-485 + ESP8266                             from/to user phone     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Sensor read (Station-485)
    │
    ├── Every 60 seconds: publish sensor data to MQTT topics
    │
    ├── Every 6 hours: evaluate irrigation logic
    │       │
    │       ├── soil_moisture < 30% AND air_humidity < 85% AND water_available
    │       │       └── activate pump (20s) → wait 30min → re-check
    │       │
    │       └── condition not met → skip
    │
    └── Threshold breach → publish alert topic → Telegram Bot → user phone

Sensor read (CYD ESP32 indoor)
    │
    └── Every 60 seconds: publish indoor temp/hum to MQTT topics

TimerCam X (outdoor, deep sleep cycle)
    │
    ├── RTC wakes camera every 4h (configurable)
    ├── Takes photo → HTTP POST → Proxmox LXC storage
    ├── Publishes MQTT event → Grafana panel refreshes
    └── Returns to deep sleep (~2µA)

MQTT → Telegraf/Bridge → InfluxDB → Grafana panels
```

## MQTT Topic Schema

| Topic | Direction | Type | Published by |
|---|---|---|---|
| `sniperstation/exterior/temperatura` | OUT | float (°C) | Station-485 |
| `sniperstation/exterior/humedad` | OUT | float (%) | Station-485 |
| `sniperstation/exterior/luz` | OUT | int (lx) | Station-485 |
| `sniperstation/interior/master/temperatura` | OUT | float (°C) | ESP8266 master |
| `sniperstation/interior/master/humedad` | OUT | float (%) | ESP8266 master |
| `sniperstation/interior/kids/temperatura` | OUT | float (°C) | ESP8266 kids |
| `sniperstation/interior/kids/humedad` | OUT | float (%) | ESP8266 kids |
| `sniperstation/sucufer/humedad_suelo` | OUT | float (%) | Station-485 |
| `sniperstation/sucurod/humedad_suelo` | OUT | float (%) | Station-485 |
| `sniperstation/sucufer/bomba` | OUT | int (0/1) | Station-485 |
| `sniperstation/sucurod/bomba` | OUT | int (0/1) | Station-485 |
| `sniperstation/sucufer/bomba/set` | IN | int (0/1) | Telegram Bot |
| `sniperstation/sucurod/bomba/set` | IN | int (0/1) | Telegram Bot |
| `sniperstation/agua/nivel` | OUT | int (0/1) | Station-485 |
| `sniperstation/sistema/estado` | OUT | string (JSON) | Station-485 |
| `sniperstation/alertas` | OUT | string (JSON) | Station-485 |
| `sniperstation/camaras/sucufer/captura` | OUT | string (filename) | TimerCam X |
| `sniperstation/camaras/sucurod/captura` | OUT | string (filename) | TimerCam X (2nd unit, future) |
