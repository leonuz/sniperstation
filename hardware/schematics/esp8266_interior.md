# ESP8266 NodeMCU — Indoor Units Wiring

**Units:** 2 identical units — Master Bedroom + Kids Bedroom
**Controller:** ESP8266 NodeMCU v3 CP2102
**Purpose:** Read indoor temp/humidity, display on OLED, publish to MQTT over WiFi
**Power:** USB 5V (from USB charger)

---

## Components per Unit

| Component | Model | I2C Address | Interface |
|---|---|---|---|
| Temp/humidity sensor | SHT30 IOT-TH02 | 0x44 | I2C |
| OLED display | SSH1106 1.3" 128x64 | 0x3C | I2C |
| Touch sensor | TTP223 capacitive | — | Digital INPUT |

No I2C address conflict. ✅

---

## Wiring Diagram

```
ESP8266 NodeMCU CP2102
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  3V3  ──────────────────────────────────► SHT30 VCC       │
│  3V3  ──────────────────────────────────► OLED VCC        │
│  3V3  ──────────────────────────────────► TTP223 VCC      │
│  GND  ──────────────────────────────────► SHT30 GND       │
│  GND  ──────────────────────────────────► OLED GND        │
│  GND  ──────────────────────────────────► TTP223 GND      │
│                                                            │
│  D2 (GPIO4) ──── 10KΩ pull-up to 3V3 ──► SDA bus         │
│                                           ├── SHT30 SDA   │
│                                           └── OLED SDA    │
│                                                            │
│  D1 (GPIO5) ──── 10KΩ pull-up to 3V3 ──► SCL bus         │
│                                           ├── SHT30 SCL   │
│                                           └── OLED SCL    │
│                                                            │
│  D5 (GPIO14) ───────────────────────────► TTP223 OUT      │
│                                                            │
│  USB (micro) ───────────────────────────► USB 5V power    │
└────────────────────────────────────────────────────────────┘
```

---

## SHT30 Connection

```
ESP8266 / I2C bus         SHT30 IOT-TH02 (loose wires)
──────────────────────────────────────────────────────────
3V3             ──────►  Red    (VCC)
GND             ──────►  Black  (GND)
SDA bus (D2)    ──────►  White  (SDA)  ⚠️ COLORS CROSSED vs Grove standard
SCL bus (D1)    ──────►  Yellow (SCL)  ⚠️ COLORS CROSSED vs Grove standard
```

> **⚠️ SHT30 IOT-TH02 color mapping:** White = SDA, Yellow = SCL.
> Opposite of Grove HY2.0 standard. Verify before powering on.

---

## OLED SSH1106 Connection

```
ESP8266 / I2C bus         SSH1106 1.3" OLED (4-pin)
──────────────────────────────────────────────────────────
3V3             ──────►  VCC
GND             ──────►  GND
SDA bus (D2)    ──────►  SDA
SCL bus (D1)    ──────►  SCL
```

- Library: **U8g2** (`U8G2_SH1106_128X64_NONAME_F_HW_I2C`)
- I2C address: 0x3C

---

## TTP223 Touch Sensor Connection

```
ESP8266                   TTP223
──────────────────────────────────────────────────────────
3V3             ──────►  VCC
GND             ──────►  GND
D5 (GPIO14)     ──────►  OUT  (HIGH on touch)
```

- Configured as INPUT in firmware
- Triggers display wake from screensaver

---

## I2C Pull-up Resistors

External 10KΩ pull-ups required on both SDA and SCL (ESP8266 internal pull-ups insufficient for reliable I2C with two devices).

```
3V3 ──── 10KΩ ──── D2 (SDA bus)
3V3 ──── 10KΩ ──── D1 (SCL bus)
```

---

## GPIO Summary

| GPIO | NodeMCU Label | Function | Direction |
|---|---|---|---|
| GPIO4 | D2 | I2C SDA — SHT30 + OLED | I/O |
| GPIO5 | D1 | I2C SCL — SHT30 + OLED | I/O |
| GPIO14 | D5 | TTP223 touch signal | INPUT |

---

## Display Behavior & Brightness Logic

| State | Trigger | Brightness | Content |
|---|---|---|---|
| Screensaver | Default / 30s timeout | 10/255 | SniperStation logo (bitmap) |
| Active | Touch detected | 200/255 | Temp + humidity + date + time |
| Night mode | 00:00 – 06:00 (NTP) | 0 (display off) | — |

**State machine:**
```
SCREENSAVER ──── touch ────► ACTIVE (30s timer starts)
   ▲                              │
   └──────── timeout / night ─────┘
```

Brightness controlled via U8g2 `setContrast()` (maps to SSH1106 register 0x81, 0–255).

---

## OLED Layout — Active Mode (128x64)

```
┌────────────────────────────┐
│ [SS] SniperStation           │  ← small logo 16x16 + title (line 1)
│ ──────────────────────── │  ← separator
│  25.3°C        72% RH      │  ← sensor data (line 3)
│  Mar 25, 2026  14:23       │  ← NTP date + time (line 4)
└────────────────────────────┘
```

## OLED Layout — Screensaver Mode (128x64)

```
┌────────────────────────────┐
│                            │
│      [LOGO 48x48]          │  ← centered large bitmap
│      SniperStation           │  ← centered name below logo
│                            │
└────────────────────────────┘
```

---

## Date / Time — NTP

No RTC hardware needed. Time synced via WiFi on boot and every hour.

- Server: `pool.ntp.org`
- Timezone: `America/New_York` (Orlando, FL — UTC-5 / UTC-4 DST)
- Library: `NTPClient` + `ESP8266WiFi`
- Fallback if WiFi lost: display last known time + `(no sync)` indicator

---

## MQTT Topics

### Master Bedroom unit (`ROOM_ID = "master"`)

| Topic | Value | Frequency |
|---|---|---|
| `sniperstation/interior/master/temperatura` | float (°C) | Every 60s |
| `sniperstation/interior/master/humedad` | float (%) | Every 60s |

### Kids Bedroom unit (`ROOM_ID = "kids"`)

| Topic | Value | Frequency |
|---|---|---|
| `sniperstation/interior/kids/temperatura` | float (°C) | Every 60s |
| `sniperstation/interior/kids/humedad` | float (%) | Every 60s |

Firmware is identical for both units. Only `ROOM_ID` differs.

---

## Physical Enclosure

Custom 3D printed enclosure (same design for both units). Contains:
- ESP8266 NodeMCU (49 x 26mm)
- OLED 1.3" SSH1106 — front face cutout/window
- TTP223 touch sensor — front face, finger accessible
- SHT30 — top of enclosure, casing exposed to room air

See `hardware/enclosure/indoor_unit_design.md` for full specs (pending).

---

## Power Note

- Power via micro-USB (5V USB charger)
- SHT30 and OLED powered from 3V3 pin only
- Do **not** power SHT30 from 5V on this unit
