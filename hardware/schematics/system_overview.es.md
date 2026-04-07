# Visión General del Sistema — SniperStation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              UNIDAD EXTERIOR                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │               M5Stack Station-485                    │                   │
│  │                    (ESP32)                           │                   │
│  │                                                      │                   │
│  │  Puerto A1 ──── BH1750 (Luz, I2C 0x23)             │                   │
│  │  Puerto A2 ──── SHT30 exterior (Temp/Hum, I2C 0x44)│                   │
│  │  Puerto B1 ──── Sensor Tierra 1 (SucuFer, Analógico)│                   │
│  │  Puerto B2 ──── Sensor Tierra 2 (SucuRod, Analógico)│                   │
│  │  Puerto C1 ──── Relay 1 ──── Bomba 1 (SucuFer)     │                   │
│  │  Puerto C2 ──── Relay 2 ──── Bomba 2 (SucuRod)     │                   │
│  │  GPIO  ────── XKC-Y25 (Nivel agua, Digital)         │                   │
│  │                                                      │                   │
│  │  PWR485 ───── Adaptador DC 12V 2A                   │                   │
│  │  WiFi ──────────────────────────────────────────────┼──► Broker MQTT   │
│  └─────────────────────────────────────────────────────┘                   │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  ┌──────────────────┐    │
│  │ Bomba 1  │  │ Bomba 2  │  │ Sensor XKC-Y25  │  │ TimerCam X       │    │
│  │ 12V 80mA │  │ 12V 80mA │  │ + driver DFRobot│  │ OV3660 3MP       │    │
│  │ → SucuFer│  │ → SucuRod│  │ Recipiente agua │  │ ESP32 + batería  │    │
│  │          │  │          │  │ (sin contacto)  │  │ WiFi → HTTP/MQTT │    │
│  │ FOV 66.5°        │    │
│  │ sleep: 2µA       │    │
│  └──────────┘  └──────────┘  └─────────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      UNIDAD INTERIOR — HABITACIÓN PRINCIPAL                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │          CYD ESP32-2432S028  (ROOM_ID=master)        │                   │
│  │                                                      │                   │
│  │  CN1 GPIO21 ── I2C SDA ── SHT30 (0x44)              │                   │
│  │  CN1 GPIO22 ── I2C SCL ── SHT30 (0x44)              │                   │
│  │  Pull-ups 10KΩ en SDA + SCL                         │                   │
│  │                                                      │                   │
│  │  [TFT 2.8" 240x320 color] — integrado               │                   │
│  │  [XPT2046 táctil resistivo] — integrado             │                   │
│  │  [SHT30 con carcasa] ────── parte superior, expuesto│                   │
│  │                                                      │                   │
│  │  WiFi ──────────────────────────────────────────────┼──► Broker MQTT   │
│  └─────────────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                   UNIDAD INTERIOR — HABITACIÓN DE LOS NIÑOS                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │          CYD ESP32-2432S028  (ROOM_ID=kids)          │                   │
│  │                                                      │                   │
│  │  CN1 GPIO21 ── I2C SDA ── SHT30 (0x44)              │                   │
│  │  CN1 GPIO22 ── I2C SCL ── SHT30 (0x44)              │                   │
│  │  Pull-ups 10KΩ en SDA + SCL                         │                   │
│  │                                                      │                   │
│  │  [TFT 2.8" 240x320 color] — integrado               │                   │
│  │  [XPT2046 táctil resistivo] — integrado             │                   │
│  │  [SHT30 con carcasa] ────── parte superior, expuesto│                   │
│  │                                                      │                   │
│  │  WiFi ──────────────────────────────────────────────┼──► Broker MQTT   │
│  └─────────────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROXMOX LXC (Servidor)                              │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Mosquitto   │  │  InfluxDB    │  │ Grafana  │  │  Bot Telegram    │   │
│  │  Broker MQTT │→ │  2.x         │→ │  :3000   │  │  (Python)        │   │
│  │  :1883       │  │  :8086       │  │          │  │                  │   │
│  └──────────────┘  └──────────────┘  └──────────┘  └──────────────────┘   │
│         ▲                                                    ▲              │
│         │                                                    │              │
│    Datos MQTT desde                                  Alertas + comandos     │
│    Station-485 + ESP8266                             hacia/desde teléfono   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

```
Lectura de sensores (Station-485)
    │
    ├── Cada 60 segundos: publicar datos de sensores en topics MQTT
    │
    ├── Cada 6 horas: evaluar lógica de riego
    │       │
    │       ├── humedad_suelo < 30% Y humedad_aire < 85% Y agua_disponible
    │       │       └── activar bomba (20s) → esperar 30min → re-verificar
    │       │
    │       └── condición no cumplida → omitir
    │
    └── Umbral superado → publicar topic de alerta → Bot Telegram → teléfono

Lectura de sensores (CYD ESP32 interior)
    │
    └── Cada 60 segundos: publicar temp/hum interior en topics MQTT

TimerCam X (exterior, ciclo de sueño profundo)
    │
    ├── RTC despierta la cámara cada 4h (configurable)
    ├── Toma foto → HTTP POST → almacenamiento LXC Proxmox
    ├── Publica evento MQTT → panel Grafana se actualiza
    └── Vuelve a sueño profundo (~2µA)

MQTT → Telegraf/Bridge → InfluxDB → paneles Grafana
```

## Esquema de Topics MQTT

| Topic | Dirección | Tipo | Publicado por |
|---|---|---|---|
| `sniperstation/exterior/temperatura` | SALIDA | float (°C) | Station-485 |
| `sniperstation/exterior/humedad` | SALIDA | float (%) | Station-485 |
| `sniperstation/exterior/luz` | SALIDA | int (lx) | Station-485 |
| `sniperstation/interior/master/temperatura` | SALIDA | float (°C) | ESP8266 master |
| `sniperstation/interior/master/humedad` | SALIDA | float (%) | ESP8266 master |
| `sniperstation/interior/kids/temperatura` | SALIDA | float (°C) | ESP8266 kids |
| `sniperstation/interior/kids/humedad` | SALIDA | float (%) | ESP8266 kids |
| `sniperstation/sucufer/humedad_suelo` | SALIDA | float (%) | Station-485 |
| `sniperstation/sucurod/humedad_suelo` | SALIDA | float (%) | Station-485 |
| `sniperstation/sucufer/bomba` | SALIDA | int (0/1) | Station-485 |
| `sniperstation/sucurod/bomba` | SALIDA | int (0/1) | Station-485 |
| `sniperstation/sucufer/bomba/set` | ENTRADA | int (0/1) | Bot Telegram |
| `sniperstation/sucurod/bomba/set` | ENTRADA | int (0/1) | Bot Telegram |
| `sniperstation/agua/nivel` | SALIDA | int (0/1) | Station-485 |
| `sniperstation/sistema/estado` | SALIDA | string (JSON) | Station-485 |
| `sniperstation/alertas` | SALIDA | string (JSON) | Station-485 |
| `sniperstation/camaras/sucufer/captura` | SALIDA | string (nombre archivo) | TimerCam X |
| `sniperstation/camaras/sucurod/captura` | SALIDA | string (nombre archivo) | TimerCam X (2ª unidad, futuro) |
