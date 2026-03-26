# Changelog

All notable changes to SniperStation will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
- Station-485 firmware (Phase 2)
- CYD ESP32-2432S028 indoor firmware x2 (Phase 2)
- TimerCam X firmware — timelapse capture + HTTP upload + MQTT event (Phase 2)
- Proxmox LXC software stack including photo storage endpoint + Grafana panel (Phase 3)
- Redesign + print indoor enclosure for CYD form factor (Phase 1)

## [0.5.0] — 2026-03-26

### Changed
- Project folder renamed: `sucustation/` → `sniperstation/`
- Project document renamed: `sucustation_project.md` → `sniperstation_project.md`

### Added
- M5Stack ESP32 PSRAM Timer Camera X (OV3660, 3MP) — ordered, one unit covering planters area
- MQTT topics: `sniperstation/camaras/sucufer/captura` and `sucurod/captura` for photo events
- Timelapse photo storage planned: HTTP POST from TimerCam → Proxmox LXC → `photos/sucufer/YYYY-MM-DD_HH.jpg`
- Grafana panel planned: latest photo per plant
- Telegram command planned: `/foto sucufer` sends latest photo
- Phase 3 task: Python/Flask HTTP endpoint to receive photos on Proxmox LXC

### Decisions
- TimerCam X (OV3660 3MP) over generic ESP32-CAM (OV2640 2MP): dedicated timelapse hardware, built-in battery + RTC, same M5Stack ecosystem
- Photo upload via HTTP POST (not MQTT): photos too large for MQTT — MQTT only used for capture event notification
- Deep sleep cycle default: every 4h (configurable via NVS)
- FOV 66.5° confirmed sufficient to cover both planters with a single camera unit
- LM2596 buck converter (adjustable, built-in voltmeter display) to power TimerCam X from 12V rail — Station-485 USB-A already reserved for XKC-Y25
- Wago 221-415 lever nuts (x2) for +12V and GND distribution rails — no soldering required
- Created `hardware/schematics/outdoor_power.md` as dedicated outdoor power distribution diagram

---

## [0.4.0] — 2026-03-26

### Changed
- Project renamed: **SucuStation → SniperStation**
- `matero1` renamed to **SucuFer** (Fernanda's succulent, planted April 22, 2024, age 10)
- `matero2` renamed to **SucuRod** (Rodrigo's succulent, planted April 22, 2024, age 6)
- All MQTT topics updated: `sucustation/` → `sniperstation/`, `matero1` → `sucufer`, `matero2` → `sucurod`
- Firmware directory renamed: `esp8266_interior/` → `cyd_indoor/`

### Added
- SucuFer detail view: Fernanda's photo as background + soil moisture + plant age since April 22, 2024
- SucuRod detail view: Rodrigo's photo as background + soil moisture + plant age since April 22, 2024
- `assets/photos/` directory planned for plant photos (CYD display backgrounds)

### Decisions
- Plant names are personal — Fernanda (10) and Rodrigo (6) each planted their succulent on the same day
- Photos of each child with their plant used as CYD background in detail view
- Plant age calculated dynamically from planting date (April 22, 2024) using NTP clock

---

## [0.2.0] — 2026-03-25

### Changed
- Indoor unit architecture expanded from 1 to **2 units** (Master Bedroom + Kids Bedroom)
- ESP8266 indoor unit upgraded: added OLED SSH1106 1.3" display + TTP223 touch sensor per unit
- MQTT topics updated: `sucustation/interior/temperatura` → `sucustation/interior/{master|kids}/temperatura|humedad`

### Added
- Bilingual EN/ES support — all documents available in both languages (separate .md and .es.md files)
- Per-device language selection (CYD + Station-485), stored in NVS flash, default English
- Bilingual firmware strings via `strings.h` with `STR_xxx[2]` arrays
- OpenSCAD enclosure model: `hardware/enclosure/indoor_unit.scad` — parametric, two pieces (shell + back plate), keyhole wall mount, USB bottom exit
- OLED display behavior: screensaver (logo, dim) → touch → active (data, bright) → 30s timeout
- Adaptive brightness logic: screensaver 10/255, active 200/255, night mode 00–06h display off
- NTP time sync (pool.ntp.org, America/New_York) — date/time shown on active display
- TTP223 capacitive touch sensor to wake display from screensaver
- 3D printed indoor enclosure planned (ESP8266 + OLED + TTP223 + SHT30 exposed top)
- OLED SSH1106 1.3" added to BOM pending purchase (HiLetgo pack of 2)
- Indoor enclosure (x2) added to BOM

### Decisions
- OLED SSH1106 1.3" over 0.96" SSD1306 — better logo visibility
- SSH1106 library: U8g2 (native SH1106 support)
- TTP223 from inventory as touch interface (replaces touchscreen OLED, same UX)
- SHT30 mounts on top of 3D enclosure using its built-in plastic casing with ventilation slots

---

## [0.3.0] — 2026-03-26

### Changed
- Indoor unit hardware replaced: ESP8266 + OLED SSH1106 + TTP223 → **CYD ESP32-2432S028** (all-in-one)
- Indoor firmware target changed to TFT_eSPI library (was U8g2)
- 3D enclosure redesign required for CYD form factor (simpler wall frame vs multi-component box)

### Added
- Multi-view UI planned: screensaver → main view (all rooms) → detail view (tap a room)
- CYD subscribes to all MQTT topics → shows exterior + both indoor rooms + soil + pumps on one screen
- Touch navigation between views (resistive XPT2046, integrated)

### Decisions
- CYD ESP32-2432S028 over ESP8266 + OLED + TTP223: color touchscreen, all-in-one, simpler enclosure, richer UI
- Library: TFT_eSPI (standard for CYD, well documented)
- ESP8266 x2 and TTP223 x2 freed back to inventory

---

## [0.1.0] — 2026-03-25

### Added
- Full project design and architecture documented in `sucustation_project.md` (planning session)
- Hardware selection finalized: M5Stack Station-485, SHT30 x2, BH1750, Earth Sensors x2, XKC-Y25, peristaltic pumps x2, relay modules x2, ESP8266 NodeMCU
- MQTT topic schema defined
- Irrigation logic designed (6h cycle, soil/humidity/water-level gating)
- Grafana dashboard panels planned (7 panels)
- Telegram alert types defined
- Full inventory catalogued (SunFounder kit + additional components)
- Project documentation structure created (README, ROADMAP, TODO, CHANGELOG, hardware/)
- Bill of Materials — `hardware/BOM.md`
- Wiring diagrams — `hardware/schematics/`
- Datasheet references — `hardware/datasheets/SOURCES.md`

### Decisions
- Peristaltic pump over submersible (precision for succulents)
- Single shared water reservoir for both pumps
- Capacitive water level sensor (XKC-Y25, no moving parts)
- Station-485 outdoors with planters (short cable runs)
- ESP8266 indoors for interior SHT30 (no wall penetration needed for main controller)
- Proxmox LXC for software stack (existing infrastructure)
- SHT30 generic instead of M5Stack ENV III (out of stock, same chip)
