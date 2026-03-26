# SniperStation — TODO

## Pending Purchase

- [x] ~~DC adapter 12V 2A, 5.5mm barrel jack~~ — ordered ✅
- [x] ~~DC-DC buck converter LM2596 (x2, adjustable, built-in voltmeter)~~ — ordered ✅
- [x] ~~Wago 221-415 lever nuts (5-port) x2~~ — ordered ✅
- [ ] Outdoor weatherproof enclosure — IP65 minimum, with ventilation slots or fan mount (Amazon)
- [x] ~~Grove↔Dupont cable HY2.0-4P to 2.54mm female 20cm~~ — ordered ✅
- [x] ~~OLED SSH1106 1.3" I2C 128x64~~ — replaced by CYD ESP32-2432S028 (all-in-one)

---

## Phase 1 — Hardware Assembly

### Hardware Tasks
- [ ] Bench test BH1750 I2C scan (expected address 0x23)
- [ ] Bench test SHT30 I2C scan (expected address 0x44)
- [ ] Verify no I2C address conflict on shared A1/A2 bus
- [ ] Bench test Earth Sensor analog reads (raw ADC values at dry/wet)
- [ ] Bench test XKC-Y25 digital output (HIGH/LOW at water/no-water)
- [ ] Test relay actuation + pump spin at 12V
- [ ] Verify power budget: measure actual draw at 12V with all sensors + 1 pump active
- [ ] **Confirm GPIO port for XKC-Y25 signal OUT** — ports B1/B2 used by Earth Sensors, C1/C2 by relays. Document in `hardware/schematics/station485_wiring.md`

### TimerCam X
- [ ] Test TimerCam X WiFi + photo capture (bench test when received)
- [ ] Decide mounting position: one camera covering both planters vs one per planter
- [ ] Confirm 5V power source for outdoor installation
- [ ] Design acrylic or glass window cutout in IP65 enclosure for camera lens

### Indoor Units
- [ ] Redesign 3D enclosure for CYD ESP32-2432S028 (wall frame, 2.8" screen window + SHT30 slot on top)
  - [ ] Measure CYD board dimensions when received
  - [ ] Update `indoor_unit.scad` for new form factor
  - [ ] **BLOCKED:** measure real SHT30 casing — wait for delivery
  - [ ] Export STL and send to print x2
- [ ] Find affordable 3D print service (JLCPCB, Treatstock, local library)
- [ ] Print x2 (master bedroom + kids bedroom)

### Security — Phase 1
- [ ] Source IP65 enclosure with **Torx or hexalobe screws** — not Phillips
- [ ] Purchase **cable glands PG7/PG9** (one per cable exiting outdoor enclosure)
- [ ] CYD 3D enclosure design must block access to EN (reset) button
- [ ] Document MAC address of each ESP32 → `hardware/inventory.md`

---

## Phase 2 — Firmware

### Firmware Tasks
- [ ] Station-485 firmware (see ROADMAP Phase 2 for full spec)
- [ ] CYD ESP32-2432S028 indoor firmware (see ROADMAP Phase 2 for full spec)
- [ ] TimerCam X firmware (see ROADMAP Phase 2 for full spec)

### Security — Phase 2
- [ ] **Before first firmware commit:** add `secrets.h` entries to `.gitignore`
  - `firmware/station485/secrets.h`
  - `firmware/cyd_indoor/secrets.h`
  - `firmware/timercam/secrets.h`
- [ ] Create `secrets.h.example` with placeholder values for each firmware
- [ ] Implement watchdog timer (30s) in all ESP32 firmware
- [ ] Implement relay absolute max duration (60s force-off) in Station-485
- [ ] Sanitize MQTT pump commands: accept only `'0'`/`'1'`, length == 1
- [ ] Configure LWT on all devices (`sniperstation/sistema/lwt` → `offline`)
- [ ] Persist pump state in NVS — force relay OFF on reboot if pump was active
- [ ] Set OTA password on all ESP32

---

## Phase 3 — Software Stack

### Software Tasks
- [ ] Provision LXC container (Debian 12) on Proxmox
- [ ] Install and configure Mosquitto broker
- [ ] Install and configure InfluxDB 2.x (org, bucket, tokens)
- [ ] MQTT → InfluxDB bridge (Telegraf or Python)
- [ ] Install and configure Grafana (dashboard, datasource)
- [ ] Telegram bot (BotFather, alerts, manual irrigation command)
- [ ] HTTP endpoint for TimerCam X photo upload
- [ ] Photo storage: `photos/sucufer/YYYY-MM-DD_HH.jpg`
- [ ] Grafana panel: latest photo per plant
- [ ] Telegram command: `/foto sucufer`

### Security — Phase 3
**Network (do before provisioning):**
- [ ] Disable WPS on router
- [ ] No port forwarding for Proxmox UI (8006) to internet
- [ ] Create IoT VLAN 10 (192.168.10.0/24) with firewall rules blocking IoT → LAN
- [ ] Assign static IPs to all ESP32 via DHCP static mappings
- [ ] Static IP for LXC

**Mosquitto:**
- [ ] `allow_anonymous false` in `mosquitto.conf`
- [ ] Create one user per device (6 users — see `docs/security.md` §6.1)
- [ ] Configure ACL file (see `docs/security.md` §6.2 for full config)
- [ ] Enable connection logging

**InfluxDB:**
- [ ] Create write-only token for Telegraf
- [ ] Create read-only token for Grafana
- [ ] Never use All Access token in services

**Grafana:**
- [ ] Change default `admin:admin` password immediately after install
- [ ] Rename admin user, disable sign-up and anonymous access
- [ ] Enable 2FA (TOTP) on admin account
- [ ] Add security monitoring panel (device last seen, pump activations)

**Telegram Bot:**
- [ ] Restrict bot to authorized `chat_id` only

**HTTP photo endpoint:**
- [ ] Bearer token authentication on `/upload`
- [ ] nginx rate limiting: 10 req/min per IP
- [ ] HTTPS with self-signed cert

**Secrets & permissions:**
- [ ] All secrets in `/etc/sniperstation/secrets.env` with `chmod 600`
- [ ] Load secrets via systemd `EnvironmentFile`
- [ ] `chmod 600` on Mosquitto passwd and ACL files

**Monitoring:**
- [ ] Install and configure `fail2ban` for Mosquitto and Grafana
- [ ] Telegram alert on LWT `offline` message from any device

**MQTTS (after stack is working):**
- [ ] Generate CA + server cert (script in `docs/security.md` §8.2)
- [ ] Configure Mosquitto on port 8883 with TLS 1.2
- [ ] Update all ESP32 firmware with embedded CA cert
- [ ] Update firewall: allow 8883, remove 1883

---

## Phase 4 — Calibration

- [ ] Calibrate Earth Sensors (dry/moist/wet ADC values with real planters)
- [ ] Calibrate pump flow rate at 12V (ml/second)
- [ ] Adjust irrigation duration and thresholds
- [ ] Stress test: full irrigation cycle end-to-end
- [ ] Validate all Telegram alerts

### Security — Phase 4
- [ ] Verify watchdog: simulate hung loop → confirm ESP32 resets
- [ ] Verify relay max duration: send MQTT `'1'` → confirm pump stops at 60s
- [ ] Verify LWT: kill WiFi on Station-485 → confirm Telegram alert fires
- [ ] Verify pump state recovery: cut power mid-pump → confirm relay OFF after reboot

---

## Phase 5 — Deployment

- [ ] Install cable glands on outdoor enclosure, seal with silicone
- [ ] Install Station-485 in outdoor enclosure (shade location mandatory)
- [ ] Route tubing from water reservoir to planters
- [ ] Run 72h unattended monitoring test
- [ ] Document final calibration values in firmware config

### Security — Phase 5
- [ ] Confirm Torx security screws installed on enclosure
- [ ] Confirm all cable glands sealed — no open holes
- [ ] Confirm enclosure is in permanent shade
- [ ] Passive ventilation installed (10mm holes with mesh + rain covers)
- [ ] Final audit: VLAN rules active, MQTTS running, no default passwords, `secrets.h` not in git history

---

## Documentation

- [ ] Translate hardware documents to Spanish:
  - [ ] `hardware/BOM.es.md`
  - [ ] `hardware/schematics/station485_wiring.es.md`
  - [ ] `hardware/schematics/system_overview.es.md`
  - [ ] `hardware/enclosure/indoor_unit_design.es.md`
  - [ ] `hardware/enclosure/requirements.es.md`
- [ ] Add Fritzing or KiCad schematic files once GPIO assignment confirmed
- [ ] Add datasheet PDFs to `hardware/datasheets/`
- [ ] `hardware/inventory.md` — MAC addresses + serial numbers of all ESP32 devices

---

## Decisions Pending

- [ ] Define cooldown logic: minimum time between irrigation cycles
- [ ] Choose Telegram bot library (python-telegram-bot vs pyTelegramBotAPI)
- [ ] Define logo bitmap + UI layout for CYD display (screensaver + main + detail views)
- [ ] Get updated photos of Fernanda and Rodrigo with their grown succulents
