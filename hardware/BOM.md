# Bill of Materials — SniperStation

**Last updated:** 2026-03-25
**Project:** SniperStation — Automatic succulent irrigation + weather station
**Location:** Orlando, Florida (outdoor, exposed to sun and rain)

---

## Primary Components

| # | Component | Model / Part | Qty | Voltage | Notes | Supplier | Status |
|---|---|---|---|---|---|---|---|
| 1 | Main controller | M5Stack Station-485 | 1 | 9–24V input | ESP32, WiFi, 1.14" display, 6x Grove HY2.0, RS485, RTC BM8563 | M5Stack | ✅ Have it |
| 2 | Light sensor | DLight BH1750 | 1 | 3.3–5V | I2C address 0x23, range 1–65535 lx, Grove HY2.0 | M5Stack | ✅ Have it |
| 3 | Temp/humidity sensor (outdoor) | SHT30 IOT-TH02 | 1 | 2.15–5.5V | I2C address 0x44, loose color-coded wires | Amazon | ✅ Purchased |
| 4 | Temp/humidity sensor (indoor) | SHT30 IOT-TH02 | 1 | 2.15–5.5V | I2C address 0x44, loose color-coded wires | Amazon | ✅ Purchased |
| 5 | Soil moisture sensor | M5Stack Earth Sensor | 2 | 3.3–5V | Analog + digital output, Grove HY2.0 | M5Stack | ✅ Purchased |
| 6 | Relay module | M5Stack Mini 3A Relay | 2 | 5V control | 3A/30VDC, Grove HY2.0, NO/NC/COM | M5Stack | ✅ Purchased |
| 7 | Peristaltic pump | DC 12–24V pump | 2 | 12V | ~100 ml/min, 80mA, reversible, tubing included | Amazon | ✅ Purchased |
| 8 | Water level sensor | XKC-Y25-V + DFRobot driver | 1 | 5–24V | Non-contact capacitive, digital output, 4 sensitivity levels | Amazon | ✅ Purchased |
| 9 | Indoor unit (all-in-one) | ESP32-2432S028 CYD | 2 | 5V USB | ESP32 dual-core + 2.8" TFT 240x320 color + resistive touch. One per room (master + kids). I2C SHT30 on CN1 (GPIO21/22) | Amazon | ✅ Purchased |
| 10 | Grove↔Dupont cable | HY2.0-4P to 2.54mm female 20cm | 2 | — | Connects SHT30 to Station-485 Grove ports. WatangTech on Amazon | Amazon | ✅ Purchased |
| 11 | Timelapse camera | M5Stack ESP32 PSRAM Timer Camera X (OV3660) | 1 | 5V USB | 3MP 2048x1536, FOV 66.5°, WiFi, RTC BM8563, battery 140mAh, sleep 2µA. One unit covers both planters. 48x24x15mm | M5Stack | 🚚 Ordered |

---

## Pending Purchase

| # | Component | Specification | Qty | Notes | Supplier | Estimated Cost |
|---|---|---|---|---|---|---|
| 13 | DC power adapter | 12V 2A, 5.5x2.1mm barrel jack | 1 | Powers Station-485 + both pumps from single source | Amazon | ~$10 |
| 16 | DC-DC buck converter | LM2596 adjustable, 4–40V in, 1.25–37V out, 2A | 2 | Set to 5V output (built-in voltmeter display). Powers TimerCam X from 12V rail. 1 unit + 1 spare | Amazon | 🚚 Ordered |
| 17 | Power distribution connectors | Wago 221-415 lever nuts (5-port) | 2 | One for +12V rail, one for GND rail. No soldering required. 1 input → 4 outputs each | Amazon | 🚚 Ordered |
| 14 | Outdoor weatherproof enclosure | IP65 min, 150x120x80mm min, ventilation slots or fan mount | 1 | Must handle Orlando summer heat — shade installation mandatory | Amazon | ~$15–25 |
| 15 | Indoor unit enclosure x2 | Custom 3D printed | 2 | Contains CYD ESP32-2432S028 + SHT30 (wall frame). Same design printed twice | 3D Print Service | TBD |

---

## Supporting Components (from SunFounder Kit / Inventory)

Used during prototyping and assembly. Marked with intended use.

| Component | Qty | Value | Use in SniperStation |
|---|---|---|---|
| Resistor | 2 | 10KΩ | I2C pull-ups on CYD CN1 SDA/SCL for SHT30 (1 per unit x 2 units) |
| Diode 1N4007 | 2 | — | Flyback protection on pump relay outputs |
| Capacitor electrolytic | 2 | 10µF | Power supply noise filter near pump relays |
| Jump wire F/F | 4 | 20cm | CYD CN1 ↔ SHT30 indoor connections |
| Jump wire M/M | 6 | 20cm | Breadboard prototyping |
| Fan (5V DC) | 1 (optional) | — | Enclosure ventilation if passive ventilation is insufficient |

---

## Not Used in SniperStation (reserved for future projects)

| Component | Qty | Potential Use |
|---|---|---|
| ESP8266 NodeMCU CP2102 | 2 | Freed up — future projects |
| TTP223 touch sensor | 2 | Freed up — future projects |
| HC-SR04 ultrasonic | 1 | Alternative water level sensor |
| L293D H-Bridge | 1 | Reversible pump control (drain tubing after irrigation) |
| MCP3008 ADC | 1 | Expansion to more planters (more analog inputs) |
| Camera Module (generic) | 1 | Superseded by M5Stack TimerCam X (ordered) |
| PIR Motion Sensor | 1 | Presence detection in garden |

---

## Power Budget

| Component | Voltage | Current (typical) | Current (peak) |
|---|---|---|---|
| Station-485 (idle) | 12V | 120mA | — |
| Station-485 (WiFi active) | 12V | 161mA | 200mA |
| Pump 1 (active) | 12V | 80mA | 100mA |
| Pump 2 (active) | 12V | 80mA | 100mA |
| Grove sensors total | 5V (internal) | ~20mA | — |
| **Total (both pumps + WiFi)** | **12V** | **~341mA** | **~400mA** |

**Adapter:** 12V 2A → 2000mA capacity vs 400mA peak draw. Safety margin: **5x**. ✅

> Note: Both pumps will not activate simultaneously by design (one planter at a time).
> Real worst case: 161mA (controller) + 80mA (one pump) = 241mA.

---

## Datasheet References

See [datasheets/SOURCES.md](datasheets/SOURCES.md) for links to all component datasheets.
