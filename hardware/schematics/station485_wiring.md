# Station-485 Wiring Diagram

**Controller:** M5Stack Station-485 (ESP32-D0WDQ6)
**Input voltage:** 9–24V DC via PWR485 barrel jack
**Grove ports:** HY2.0-4P 4-pin (Pin order: GND, VCC, GPIO_B, GPIO_A)

---

## Grove Port Assignments

```
Station-485
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ┌──────┐                                              │
│  │ A1   │ GND │ 5V │ G33(SCL) │ G32(SDA) ──► BH1750  │
│  ├──────┤                                              │
│  │ A2   │ GND │ 5V │ G33(SCL) │ G32(SDA) ──► SHT30   │
│  │      │     │    │  (shared I2C bus A1+A2)           │
│  ├──────┤                                              │
│  │ B1   │ GND │ 5V │ G35      │ G25      ──► Earth S1 │
│  ├──────┤                                              │
│  │ B2   │ GND │ 5V │ G36(IN)  │ G26      ──► Earth S2 │
│  │      │     │    │  ⚠️ G36 input only               │
│  ├──────┤                                              │
│  │ C1   │ GND │ 5V │ G17      │ G14      ──► Relay 1  │
│  ├──────┤                                              │
│  │ C2   │ GND │ 5V │ G19      │ G17      ──► Relay 2  │
│  └──────┘                                              │
│                                                        │
│  USB-A 5V output ──────────────────────► XKC-Y25 VCC  │
│  GPIO (TBD) ───────────────────────────► XKC-Y25 OUT  │
│                                                        │
│  PWR485 ──────────────────────────────► 12V 2A input  │
└────────────────────────────────────────────────────────┘
```

> **⚠️ XKC-Y25 GPIO assignment pending:** Ports B1, B2, C1, C2 are fully used.
> Options: use an exposed GPIO header pin directly, or remap if a Grove port is freed.
> **Confirm before writing firmware.** Update this file with final GPIO number.

---

## BH1750 Light Sensor — Port A1

```
Grove Cable (A1)          BH1750
─────────────────────────────────────────
Black  (GND)    ──────►  GND
Red    (VCC 5V) ──────►  VCC
White  (SCL)    ──────►  SCL   (G33)
Yellow (SDA)    ──────►  SDA   (G32)
```

- I2C address: **0x23** (ADDR pin floating or tied to GND)
- Range: 1 – 65,535 lx
- Resolution modes: 1 lx (high res), 0.5 lx (high res 2)

---

## SHT30 Outdoor — Port A2

```
Grove Cable (A2)          SHT30 IOT-TH02 (loose wires)
────────────────────────────────────────────────────────
Black  (GND)    ──────►  Black  (GND)
Red    (VCC 5V) ──────►  Red    (VCC)
White  (SCL)    ──────►  Yellow (SCL)  ⚠️ COLORS CROSSED
Yellow (SDA)    ──────►  White  (SDA)  ⚠️ COLORS CROSSED
```

- I2C address: **0x44** (default, ADDR not pulled high)
- Shares I2C bus with BH1750 (0x23) — no address conflict ✅
- Temperature accuracy: ±0.3°C | Humidity accuracy: ±2% RH

---

## Earth Sensor SucuFer — Port B1

```
Grove Cable (B1)          M5Stack Earth Sensor
─────────────────────────────────────────────────
Black  (GND)    ──────►  GND
Red    (VCC 5V) ──────►  VCC
White  (G35)    ──────►  AOUT  (analog output)
Yellow (G25)    ──────►  DOUT  (digital threshold output)
```

- Analog read on **G25** (ADC1_CH8)
- Analog range: 0–4095 (12-bit ADC)
- Calibration required: measure raw value at dry soil and saturated soil

---

## Earth Sensor SucuRod — Port B2

```
Grove Cable (B2)          M5Stack Earth Sensor
─────────────────────────────────────────────────
Black  (GND)    ──────►  GND
Red    (VCC 5V) ──────►  VCC
White  (G36)    ──────►  AOUT  (analog — G36 is INPUT ONLY) ✅
Yellow (G26)    ──────►  DOUT  (digital threshold output)
```

> **⚠️ G36 is input-only on ESP32.** Only use for reading analog values. Never configure as output.

---

## Relay SucuFer (→ Pump SucuFer) — Port C1

```
Grove Cable (C1)          M5Stack Mini Relay 1
──────────────────────────────────────────────────
Black  (GND)    ──────►  GND
Red    (VCC 5V) ──────►  VCC
Yellow (G14)    ──────►  IN   (signal — HIGH = relay ON)

Relay 1 Contacts          Pump 1
──────────────────────────────────────────────────
COM             ──────►  +12V (from DC adapter)
NO              ──────►  Pump 1 (+) red wire
(GND common shared with pump GND)
```

---

## Relay SucuRod (→ Pump SucuRod) — Port C2

```
Grove Cable (C2)          M5Stack Mini Relay 2
──────────────────────────────────────────────────
Black  (GND)    ──────►  GND
Red    (VCC 5V) ──────►  VCC
Yellow (G17)    ──────►  IN   (signal — HIGH = relay ON)

Relay 2 Contacts          Pump 2
──────────────────────────────────────────────────
COM             ──────►  +12V (from DC adapter)
NO              ──────►  Pump 2 (+) red wire
(GND common shared with pump GND)
```

---

## XKC-Y25-V Water Level Sensor

```
DFRobot Driver Board      Station-485
──────────────────────────────────────────────────
VCC             ──────►  5V (USB-A output)
GND             ──────►  GND
OUT             ──────►  GPIO (TBD — confirm port)

Sensor probe    ──────►  Stick to outside of water reservoir (plastic)
```

- Output: HIGH = water present at sensor position, LOW = empty
- Sensitivity: adjustable via SET button on driver board (4 levels)
- For plastic containers ≤ 3mm wall thickness

---

## Power Distribution

```
12V 2A DC Adapter (5.5x2.1mm barrel)
        │
        └──► PWR485 (Station-485 power input)
                │
                ├── Regulates to 5V for Grove ports (internal)
                ├── Regulates to 3.3V for ESP32 core (internal)
                │
                ├── Relay 1 COM ──► Pump 1 (+)
                └── Relay 2 COM ──► Pump 2 (+)

GND rail (common):
    DC adapter GND ──► Station-485 GND ──► Pump 1 (-) ──► Pump 2 (-)

Recommended: 1N4007 flyback diode across each pump (cathode to +12V, anode to GND)
Recommended: 10µF electrolytic capacitor across power rails near relays
```

---

## I2C Bus Summary (Ports A1 + A2 — shared G32/G33)

| Device | Address | Port |
|---|---|---|
| BH1750 | 0x23 | A1 |
| SHT30 outdoor | 0x44 | A2 |

No address conflict. Both respond on the same SDA/SCL lines. ✅

---

## GPIO Summary

| GPIO | Function | Direction | Port |
|---|---|---|---|
| G32 | I2C SDA | I/O | A1 + A2 |
| G33 | I2C SCL | I/O | A1 + A2 |
| G25 | Earth Sensor SucuFer analog | INPUT | B1 |
| G35 | Earth Sensor SucuFer digital | INPUT | B1 |
| G26 | Earth Sensor SucuRod analog | INPUT | B2 |
| G36 | Earth Sensor SucuRod digital (input only) | INPUT | B2 |
| G14 | Relay 1 control | OUTPUT | C1 |
| G17 | Relay 2 control | OUTPUT | C2 |
| TBD | XKC-Y25 signal | INPUT | — |
