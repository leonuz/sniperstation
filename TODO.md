# SniperStation — TODO

## Pending Purchase

- [x] ~~DC adapter 12V 2A, 5.5mm barrel jack~~ — ordered ✅
- [x] ~~DC-DC buck converter LM2596 (x2, adjustable, built-in voltmeter)~~ — ordered ✅
- [x] ~~Wago 221-415 lever nuts (5-port) x2~~ — ordered ✅
- [ ] Outdoor weatherproof enclosure — IP65 minimum, with ventilation slots or fan mount (Amazon)
- [ ] Grove↔Dupont cable HY2.0-4P to 2.54mm female 20cm — WatangTech on Amazon (if not already ordered)
- [x] ~~OLED SSH1106 1.3" I2C 128x64~~ — replaced by CYD ESP32-2432S028 (all-in-one)

## TimerCam X — Pending

- [ ] Test TimerCam X WiFi + photo capture (bench test when received)
- [ ] Decide mounting position: one camera covering both planters vs one per planter
- [ ] Confirm 5V power source for outdoor installation (shared enclosure with Station-485 or separate USB adapter)
- [ ] Design acryllic or glass window cutout in IP65 enclosure for camera lens

## Hardware — Unresolved

- [ ] **Confirm GPIO port for XKC-Y25 signal OUT** — ports B1 and B2 are used by Earth Sensors, C1 and C2 by relays. Options: use a spare digital GPIO directly or remap one sensor. Document final decision in `hardware/schematics/station485_wiring.md`.

## Indoor Units — Design Pending

- [ ] Redesign 3D enclosure for CYD ESP32-2432S028 (simple wall frame, 2.8" screen window + SHT30 slot on top)
  - [ ] Measure CYD board dimensions when received
  - [ ] Update indoor_unit.scad for new form factor
  - [ ] **BLOCKED: medir SHT30 casing real** — cuando llegue el pedido
  - [ ] Exportar STL y mandar a imprimir x2
- [ ] Find affordable 3D print service (local or online — JLCPCB, Treatstock, local library, etc.)
- [ ] Print x2 (master bedroom + kids bedroom)

## Documentation

- [ ] Translate hardware documents to Spanish:
  - [ ] `hardware/BOM.es.md`
  - [ ] `hardware/schematics/station485_wiring.es.md`
  - [ ] `hardware/schematics/esp8266_interior.es.md`
  - [ ] `hardware/schematics/system_overview.es.md`
  - [ ] `hardware/enclosure/indoor_unit_design.es.md`
  - [ ] `hardware/enclosure/requirements.es.md`
- [ ] Add Fritzing or KiCad schematic files to `hardware/schematics/` once final GPIO assignment is confirmed
- [ ] Add actual datasheet PDFs to `hardware/datasheets/` (currently only URLs in SOURCES.md)

## Phase 1 — Hardware (not started)

- [ ] Bench test BH1750 I2C scan (expected address 0x23)
- [ ] Bench test SHT30 I2C scan (expected address 0x44)
- [ ] Verify no I2C address conflict on shared A1/A2 bus
- [ ] Bench test Earth Sensor analog reads (raw ADC values at dry/wet)
- [ ] Bench test XKC-Y25 digital output (HIGH/LOW at water/no-water)
- [ ] Test relay actuation + pump spin at 12V
- [ ] Verify power budget: measure actual draw at 12V with all sensors + 1 pump active

## Phase 2 — Firmware (not started)

- [ ] Station-485 firmware (see ROADMAP Phase 2)
- [ ] CYD ESP32-2432S028 indoor firmware (see ROADMAP Phase 2)

## Phase 3 — Software (not started)

- [ ] Proxmox LXC provisioning
- [ ] Mosquitto + InfluxDB + Grafana + Telegram bot (see ROADMAP Phase 3)

## Decisions Pending

- [ ] Define cooldown logic: minimum time between irrigation cycles to avoid re-watering too soon
- [ ] Choose Telegram bot library (python-telegram-bot vs pyTelegramBotAPI)
- [ ] Define logo bitmap + UI layout for CYD TFT display (screensaver + main view + detail view)
- [ ] Get updated photos of Fernanda and Rodrigo with their grown succulents (current photos are from planting day 2024)
