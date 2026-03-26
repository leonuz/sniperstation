# SniperStation — Roadmap

## Phase 1 — Hardware Assembly
**Goal:** All physical components wired, powered, and verified independently before any firmware.

- [ ] Purchase remaining components: 12V adapter, outdoor IP65 enclosure
- [ ] Redesign 3D enclosure for CYD form factor (simple wall frame) once boards arrive
- [ ] Send 3D enclosure to print x2 (master + kids bedroom)
- [ ] Wire Station-485 with all Grove sensors (BH1750, SHT30, Earth Sensors x2)
- [ ] Wire relay modules and connect peristaltic pumps
- [ ] Connect XKC-Y25 water level sensor (confirm GPIO port assignment)
- [ ] Wire CYD (master): SHT30 on CN1 connector (GPIO21/22), I2C pull-ups 10KΩ
- [ ] Wire CYD (kids): same as master
- [ ] Power-on test: verify 12V → Station-485 + pumps from single adapter
- [ ] Bench test each sensor individually (I2C scanner, analog reads)
- [ ] Bench test CYD display with TFT_eSPI (hello world + touch calibration)
- [ ] TimerCam X hardware setup
  - [ ] Test TimerCam X WiFi connection and photo capture
  - [ ] Mount in outdoor enclosure with acryllic window facing planters
  - [ ] Confirm 5V USB power supply (from Station-485 enclosure or separate)

---

## Phase 2 — Firmware Development
**Goal:** Both microcontrollers reading sensors and publishing to MQTT.

- [ ] Station-485 firmware (Arduino IDE)
  - [ ] I2C sensor reads: BH1750 + SHT30
  - [ ] Analog soil moisture reads (B1, B2)
  - [ ] Digital water level read (XKC-Y25)
  - [ ] Relay control for pumps (C1, C2)
  - [ ] WiFi connection + MQTT publish
  - [ ] Irrigation logic (6h cycle, RTC BM8563)
  - [ ] MQTT subscribe for manual override commands
  - [ ] Display status on built-in 1.14" screen
- [ ] CYD ESP32-2432S028 indoor firmware — identical for both units, `ROOM_ID` configurable (Arduino IDE)
  - [ ] SHT30 I2C read via CN1 connector (GPIO21 SDA, GPIO22 SCL)
  - [ ] TFT display init via TFT_eSPI library
  - [ ] Screensaver: animated cactus logo + compact temp summary all rooms (30s timeout → dim)
  - [ ] Main view: all rooms temp/hum + exterior + soil moisture
  - [ ] Detail view: tap a plant → owner photo background + soil data + plant age since Apr 22 2024
  - [ ] Resistive touch handling (XPT2046) → navigate views
  - [ ] Bilingual EN/ES — per device, stored in NVS flash, default EN
  - [ ] All UI strings in `strings.h` as `STR_xxx[2]` arrays indexed by `lang` (0=EN, 1=ES)
  - [ ] Adaptive brightness: active 255, screensaver 30, night 00–06h off
  - [ ] WiFi connection + NTP time sync (pool.ntp.org, America/New_York)
  - [ ] MQTT subscribe to all sniperstation/ topics (display all sensor data)
  - [ ] MQTT publish every 60s to `sniperstation/interior/{ROOM_ID}/temperatura|humedad`
- [ ] TimerCam X firmware
  - [ ] Configure RTC wake interval (default: every 4h)
  - [ ] HTTP POST photo to Proxmox LXC endpoint
  - [ ] MQTT publish `sniperstation/camaras/sucufer/captura` after each shot
  - [ ] Deep sleep return after upload (~80µA sleep current)

---

## Phase 3 — Software Stack (Proxmox LXC)
**Goal:** Full data pipeline from MQTT to Grafana dashboard + Telegram alerts.

- [ ] Provision LXC container (Debian 12)
- [ ] Install and configure Mosquitto broker
- [ ] Install and configure InfluxDB 2.x
  - [ ] Create org, bucket `sucustation`, API token
  - [ ] MQTT → InfluxDB bridge (Telegraf or custom Python script)
- [ ] Install and configure Grafana
  - [ ] Connect InfluxDB data source
  - [ ] Build dashboard (7 panels — see README)
  - [ ] Enable mobile-responsive view
- [ ] Telegram Bot
  - [ ] Create bot via BotFather
  - [ ] Implement alert triggers (empty tank, dry soil, high temp, sensor errors)
  - [ ] Implement manual irrigation command via bot
- [ ] Timelapse photo storage service (Proxmox LXC)
  - [ ] HTTP endpoint to receive photos from TimerCam X (Python/Flask or Nginx)
  - [ ] Store photos organized by date: `photos/sucufer/YYYY-MM-DD_HH.jpg`
  - [ ] Grafana panel: display latest photo per plant
  - [ ] Telegram command: `/foto sucufer` → sends latest photo

---

## Phase 4 — Field Calibration
**Goal:** System tuned to the actual planters and environment.

- [ ] Calibrate Earth Sensors with real planters (dry/moist/wet readings)
- [ ] Calibrate pump flow rate at 12V (measure ml/second with graduated cylinder)
- [ ] Adjust irrigation duration based on measured flow
- [ ] Adjust dry/moist/wet thresholds based on succulent species
- [ ] Stress test: observe full irrigation cycle end-to-end
- [ ] Validate Telegram alerts fire correctly

---

## Phase 5 — Deployment
**Goal:** Permanent outdoor installation.

- [ ] Final enclosure preparation (cable glands, ventilation, mounting)
- [ ] Install Station-485 in outdoor enclosure
- [ ] Route tubing from water reservoir to planters
- [ ] Run 72h unattended monitoring test
- [ ] Document final calibration values in firmware config

---

## Future Ideas

| Feature | Components Needed |
|---|---|
| Generate timelapse GIF/video from stored photos | ffmpeg on Proxmox LXC |
| Second TimerCam X (one per planter) | M5Stack TimerCam X |
| Local audio alert on empty tank | Active Buzzer + Station-485 |
| IR remote irrigation trigger | IR Receiver 38kHz + ESP8266 |
| Auto ventilation fan for enclosure | Fan 5V + Relay + Thermistor |
| Reversible pump (drain tubing) | L293D H-Bridge |
| Expand to more planters | MCP3008 ADC + extra relays |
| Visual water level display | LED Bar Graph (10 segment) |
| Manual control encoder | Rotary Encoder + Station-485 |
