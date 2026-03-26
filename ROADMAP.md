# SniperStation — Roadmap

## Phase 1 — Hardware Assembly
**Goal:** All physical components wired, powered, and verified independently before any firmware.

- [ ] Purchase remaining components: outdoor IP65 enclosure
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

### Security — Phase 1
> Reference: `docs/security.md` sections 1.1, 1.3, 1.4, 14.3
- [ ] Use IP65 enclosure with **Torx or hexalobe security screws** (not Phillips) — prevents casual tampering
- [ ] Install **cable glands (PG7/PG9)** for every cable exiting the outdoor enclosure — mandatory for Orlando rain
- [ ] Seal cable glands with neutral silicone after installation
- [ ] 3D enclosure for CYD must **block access to EN (reset) button** — expose screen only
- [ ] **Document MAC address of each ESP32** before installation → save to `hardware/inventory.md`

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

### Security — Phase 2
> Reference: `docs/security.md` sections 6.6, 10.1, 10.2, 10.4, 10.5, 13.3, 14.4
- [ ] **`secrets.h` must be in `.gitignore` before first firmware commit** — never hardcode WiFi/MQTT credentials in source
  - Create `firmware/station485/secrets.h`, `firmware/cyd_indoor/secrets.h`, `firmware/timercam/secrets.h`
  - Provide `secrets.h.example` with placeholder values for each
- [ ] **Watchdog timer** in all ESP32 firmware (30s) — if loop hangs, device resets instead of leaving pump active
- [ ] **Relay absolute max duration** hardcoded in firmware: force pump OFF after 60s regardless of MQTT commands
- [ ] **Sanitize MQTT pump commands**: accept only `'1'`/`'0'`, length == 1, drop everything else silently
- [ ] **LWT (Last Will and Testament)** configured on all devices: publish `offline` to `sniperstation/sistema/lwt` on unexpected disconnect
- [ ] **Pump state persisted in NVS**: on reboot, if pump was active >2 minutes ago, force relay OFF before connecting to MQTT
- [ ] **OTA with password** configured on all ESP32 — never leave OTA open
- [ ] (Optional) Migrate credentials from `secrets.h` to NVS — allows changing credentials without reflashing

---

## Phase 3 — Software Stack (Proxmox LXC)
**Goal:** Full data pipeline from MQTT to Grafana dashboard + Telegram alerts.

- [ ] Provision LXC container (Debian 12)
- [ ] Install and configure Mosquitto broker
- [ ] Install and configure InfluxDB 2.x
  - [ ] Create org, bucket `sniperstation`, API token
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

### Security — Phase 3
> Reference: `docs/security.md` sections 2.1, 3.1–3.3, 4.1–4.4, 5.2–5.3, 6.1–6.5, 7.2–7.3, 9.2, 12.1–12.2, 13.1–13.2, 13.3, 13.5

**Router/Network (before provisioning LXC):**
- [ ] **Disable WPS** on the router — vulnerable to Pixie Dust attack
- [ ] **No port forwarding for Proxmox web UI (port 8006)** to internet — access only from LAN or VPN
- [ ] **Create IoT VLAN** (VLAN 10, 192.168.10.0/24) in pfSense/OPNsense with firewall rules:
  - IoT → LXC: allow ports 1883 (MQTT), 8883 (MQTTS), 443 (HTTPS photos), 123/UDP (NTP)
  - IoT → LAN: **block all**
  - IoT → Internet: allow 443 (OTA updates only)
- [ ] Assign static IPs to all ESP32 via DHCP static mappings (see `docs/security.md` §2.2)
- [ ] Static IP for LXC (192.168.1.50 or equivalent)

**Mosquitto:**
- [ ] **Disable anonymous access**: `allow_anonymous false`
- [ ] Create one MQTT user per device: `station485`, `cyd_master`, `cyd_kids`, `timercam`, `telegraf_bridge`, `telegram_bot`
- [ ] Configure **ACL file** — each device can only publish/subscribe to its own topics (full config in `docs/security.md` §6.2)
- [ ] Enable connection logging to `/var/log/mosquitto/mosquitto.log`

**InfluxDB:**
- [ ] Create **separate tokens with minimal permissions**: write-only for Telegraf, read-only for Grafana
- [ ] Never use the All Access admin token in services

**Grafana:**
- [ ] **Change default admin password** immediately after install (`admin:admin` is the first thing attackers try)
- [ ] Rename admin user, disable sign-up and anonymous access
- [ ] Enable 2FA (TOTP) on admin account
- [ ] Add security monitoring panel: last seen timestamp per device, reconnect counter, pump activation history

**Telegram Bot:**
- [ ] **Restrict bot to authorized `chat_id`** only — reject all other users silently

**HTTP photo endpoint (TimerCam X):**
- [ ] Require **Bearer token authentication** on `/upload` endpoint
- [ ] Configure **nginx rate limiting**: 10 req/min per IP
- [ ] HTTPS for the endpoint (self-signed cert from LXC CA)

**Secrets management:**
- [ ] All secrets in `/etc/sniperstation/secrets.env` — `chmod 600`, loaded via systemd `EnvironmentFile`
- [ ] Correct file permissions on all sensitive files (see `docs/security.md` §9.2)

**Monitoring:**
- [ ] **Fail2ban** for Mosquitto (5 failed auth → 1h ban) and Grafana
- [ ] Telegram alert when any ESP32 publishes `offline` to LWT topic

**MQTTS (after basic stack is working):**
- [ ] Generate self-signed CA + server cert (script in `docs/security.md` §8.2)
- [ ] Configure Mosquitto on port 8883 with TLS 1.2
- [ ] Update all ESP32 firmware with CA cert embedded (`setCACert()`)
- [ ] Switch firewall rule from port 1883 to 8883, remove 1883

---

## Phase 4 — Field Calibration
**Goal:** System tuned to the actual planters and environment.

- [ ] Calibrate Earth Sensors with real planters (dry/moist/wet readings)
- [ ] Calibrate pump flow rate at 12V (measure ml/second with graduated cylinder)
- [ ] Adjust irrigation duration based on measured flow
- [ ] Adjust dry/moist/wet thresholds based on succulent species
- [ ] Stress test: observe full irrigation cycle end-to-end
- [ ] Validate Telegram alerts fire correctly

### Security — Phase 4
- [ ] Verify watchdog fires: simulate a hung loop and confirm the ESP32 resets
- [ ] Verify relay max duration: send MQTT `'1'` and confirm pump stops at 60s regardless
- [ ] Verify LWT: kill WiFi on Station-485 and confirm Telegram alert fires within 30s
- [ ] Verify pump state recovery: cut power mid-pump, confirm relay is OFF after reboot

---

## Phase 5 — Deployment
**Goal:** Permanent outdoor installation.

- [ ] Final enclosure preparation (cable glands, ventilation, mounting)
- [ ] Install Station-485 in outdoor enclosure
- [ ] Route tubing from water reservoir to planters
- [ ] Run 72h unattended monitoring test
- [ ] Document final calibration values in firmware config

### Security — Phase 5
> Reference: `docs/security.md` sections 1.1–1.3, 14.1–14.2
- [ ] Confirm **Torx security screws** installed on outdoor enclosure
- [ ] Confirm **all cable glands sealed** with silicone — no open holes
- [ ] Confirm enclosure is in **permanent shade** — Orlando sun can exceed 60°C inside a closed box
- [ ] Passive ventilation: 10mm holes with mesh at bottom (inlet) and top (outlet) with rain covers
- [ ] Final security audit: verify VLAN rules, MQTTS active, all default passwords changed, `secrets.h` not in git history

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
| ESP32 flash encryption (AES-256) | — firmware change required |
| LUKS volume encryption for InfluxDB | — Proxmox storage change |
| MQTT topic anomaly monitoring | Custom broker plugin or bridge |
