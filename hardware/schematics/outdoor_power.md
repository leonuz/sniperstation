# Outdoor Power Distribution — SniperStation

**Power source:** 12V 2A DC adapter (5.5×2.1mm barrel jack)
**Total load:** ≤400mA @ 12V worst case (safety margin 5×)

---

## Power Tree

```
┌─────────────────────────────────────────────────────────────────┐
│           12V 2A DC ADAPTER (5.5×2.1mm barrel)                  │
│                         │                                        │
│               ┌─────────┘                                        │
│               │                                                   │
│               ▼                                                   │
│      ┌─────────────────┐   ┌─────────────────┐                  │
│      │  Wago 221-415   │   │  Wago 221-415   │                  │
│      │   +12V RAIL     │   │    GND RAIL     │                  │
│      │                 │   │                 │                  │
│      │ IN:  Adapter +  │   │ IN:  Adapter -  │                  │
│      │ OUT1: Station ──┤   ├── Station-485 - │                  │
│      │ OUT2: Relay1 COM┤   ├── Pump 1 (-)   │                  │
│      │ OUT3: Relay2 COM┤   ├── Pump 2 (-)   │                  │
│      │ OUT4: Buck IN + ┤   ├── Buck IN -    │                  │
│      └─────────────────┘   └─────────────────┘                  │
│               │                                                   │
│       ┌───────┼───────────────────────────┐                      │
│       │       │                           │                      │
│       ▼       ▼                           ▼                      │
│  ┌─────────────────┐            ┌──────────────────┐            │
│  │  Station-485    │            │ 12V→5V Buck Conv │            │
│  │  9–24V PWR485   │            │ (LM2596/MP1584)  │            │
│  │                 │            │                  │            │
│  │  5V internal ───┼──► Grove   │  5V out ─────────┼──► TimerCam X (USB-C)  │
│  │                 │    ├── BH1750  (~1mA)          │    active: ~180mA      │
│  │                 │    ├── SHT30   (~1mA)          │    sleep:  ~0.001mA    │
│  │                 │    ├── Earth×2 (~5mA each)     └──────────────────┘    │
│  │                 │    └── Relays  (~70mA active)                           │
│  │  USB-A 5V ──────┼──► XKC-Y25 + driver (~10mA)                           │
│  │                 │                                                          │
│  │  Relay 1 NO ────┼──► Pump SucuFer + (~80mA)                             │
│  │  Relay 2 NO ────┼──► Pump SucuRod + (~80mA, never simultaneous)         │
│  └─────────────────┘                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Why a Separate Buck Converter for TimerCam X

The Station-485 USB-A output is already used by the XKC-Y25 driver board.
Adding the TimerCam X to the same USB-A port risks instability when the camera
wakes up and draws ~180mA.

**Solution:** A dedicated 12V→5V mini buck converter for the TimerCam X.

**Recommended part:** Mini DC-DC step-down module (LM2596 or MP1584)
- Input: 12V
- Output: 5V fixed
- Max current: 2A (well above TimerCam's 180mA peak)
- Cost: ~$1–3 on Amazon
- Physical: ~23×17mm — fits easily in the IP65 enclosure

---

## Power Budget (Outdoor)

| Component | Voltage | Current (idle) | Current (peak) | Notes |
|---|---|---|---|---|
| Station-485 | 12V | 120mA | 200mA | WiFi active = 161mA |
| Pump SucuFer | 12V | 0 | 100mA | via Relay 1 — never simultaneous with Pump 2 |
| Pump SucuRod | 12V | 0 | 100mA | via Relay 2 — never simultaneous with Pump 1 |
| BH1750 | 5V (internal) | 0.2mA | 0.2mA | negligible |
| SHT30 outdoor | 5V (internal) | 0.8mA | 0.8mA | negligible |
| Earth Sensor ×2 | 5V (internal) | 5mA each | 5mA each | |
| XKC-Y25 + driver | 5V USB-A | 10mA | 10mA | Station-485 USB-A |
| Relay ×2 | 5V (internal) | ~0mA | 70mA each | only when pump active |
| TimerCam X | 5V (buck) | 0.001mA | 180mA | sleep 2µA, active ~180mA |
| **TOTAL WORST CASE** | **12V** | | **~380mA** | Station-485 WiFi + 1 pump active |

**Adapter rating:** 12V 2A = 2000mA
**Worst case draw:** ~380mA
**Safety margin: 5×** ✅

> Worst case: Station-485 WiFi active (161mA) + 1 pump (80mA) + TimerCam active (180mA) ≈ **421mA**
> Still well within 2A capacity. ✅

---

## Protection Components

| Component | Value | Location | Purpose |
|---|---|---|---|
| Diode 1N4007 | — | Across each pump terminals | Flyback protection (inductive load) |
| Capacitor electrolytic | 10µF | Near relay outputs | Power supply noise filter |

---

## Wiring Notes

- All outdoor connections inside IP65 enclosure
- Cable glands required for: 12V power in, Grove cables to sensors, tubing out, TimerCam X power
- TimerCam X mounts on enclosure wall with acrylic/glass window for lens
- USB-C cable from buck converter to TimerCam X — keep short (≤30cm inside enclosure)
