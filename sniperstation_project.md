# SniperStation — Complete Project

> Context document for Claude Code
> Generated from planning session in Claude.ai

---

## Project Description

Automatic irrigation + weather station system for two succulent planters located **outdoors** at a home in **Orlando, Florida**. The system monitors environmental conditions (temperature, humidity, sunlight, soil moisture) and automatically irrigates based on sensors, with a web dashboard, Telegram alerts, and historical data.

---

## System Architecture

```
[OUTDOORS]                                  [INDOORS]
Station-485 (main brain)                    CYD ESP32-2432S028
├── DLight BH1750    → Port A1              ├── SHT30 master bedroom
├── SHT30 exterior   → Port A2             └── SHT30 kids bedroom
├── Earth Sensor 1   → Port B1                  │
├── Earth Sensor 2   → Port B2                  │
├── Relay Pump 1     → Port C1                  │
├── Relay Pump 2     → Port C2                  │
└── Water Level      → GPIO                     │
     (XKC-Y25)                                  │
          │                                     │
          └──────── WiFi → MQTT ────────────────┘
                         │
                  [Proxmox LXC]
                  ├── Mosquitto (MQTT broker)
                  ├── InfluxDB (time-series database)
                  ├── Grafana (web / mobile dashboard)
                  └── Telegram Bot (alerts + NL agent)
```

---

## Complete Hardware List

### Confirmed / purchased

| Component | Model | Details | Source |
|---|---|---|---|
| Main controller | M5Stack Station-485 | ESP32, WiFi, 1.14" display, 6x Grove, RS485, 9-24V input | In hand |
| Light sensor | DLight BH1750 | I2C (0x23), 1-65535 lx, Grove HY2.0 | In hand |
| Temp/hum sensor x2 | SHT30 IOT-TH02 | I2C (0x44), 2.15-5.5V, color-coded loose wires | Amazon ✅ |
| Grove↔Dupont cable | HY2.0-4P to 2.54mm female | To connect SHT30 to Station-485 Grove ports | Amazon ✅ |
| Peristaltic pumps x2 | DC 12-24V | 0-100 ml/min, 80mA, reversible, with tubing | Amazon ✅ |
| Water level sensor | XKC-Y25-V + DFRobot driver | Non-contact, 5-24V, digital output, 4 sensitivity levels | Amazon ✅ |
| Soil moisture sensor x2 | M5Stack Earth Sensor | Analog + digital, Grove HY2.0 | M5Stack ✅ |
| Relay x2 | M5Stack Mini 3A Relay | 3A/30VDC, GPIO control, Grove HY2.0 | M5Stack ✅ |
| Indoor unit (all-in-one) | ESP32-2432S028 CYD x2 | ESP32 + 2.8" TFT 240x320 + touch + I2C SHT30 | Amazon ✅ |
| Timelapse camera | M5Stack ESP32 PSRAM Timer Camera X (OV3660) | 3MP, FOV 66.5°, WiFi, RTC, battery, sleep 2µA | M5Stack ✅ |

### Pending purchase (Amazon)

| Component | Specification | Notes |
|---|---|---|
| DC adapter | 12V 2A, 5.5mm connector | Powers Station-485 + pumps |
| Outdoor enclosure | Weatherproof with ventilation | Must handle Orlando summer heat (max 60°C) |

---

## Connections / Pinout

### Station-485 — Grove Ports

| Port | Sensor/Actuator | Protocol | Notes |
|---|---|---|---|
| A1 | DLight BH1750 | I2C (0x23) | Shared bus with A2 |
| A2 | SHT30 exterior | I2C (0x44) | Shared bus with A1 — no conflict |
| B1 | Earth Sensor SucuFer | Analog | G25/G35 |
| B2 | Earth Sensor SucuRod | Analog | G26/G36 ⚠️ G36 cannot be OUTPUT |
| C1 | Relay → Pump 1 | Digital OUTPUT | G14 |
| C2 | Relay → Pump 2 | Digital OUTPUT | G17 |
| USB-A output | XKC-Y25 sensor (VCC) | 5V power only | No signal |
| Free B or C | XKC-Y25 signal OUT | Digital INPUT | Confirm available port |

### SHT30 — Connection to Grove↔Dupont cable

```
Grove cable (Station-485)    →    SHT30 (loose wires)
Red    (5V)                  →    Red    (VCC)
Black  (GND)                 →    Black  (GND)
Yellow (SDA)                 →    White  (SDA) ⚠️ COLORS CROSSED
White  (SCL)                 →    Yellow (SCL) ⚠️ COLORS CROSSED
```

### Peristaltic pumps — Power

```
12V 2A Adapter
├── PWR485 → powers Station-485
├── Relay C1 (NO) → Pump 1 (+12V red)
└── Relay C2 (NO) → Pump 2 (+12V red)
Common GND shared across everything
```

### Water level sensor XKC-Y25-V

```
DFRobot Driver    →    Station-485
VCC               →    5V (USB-A output or Grove)
GND               →    GND
OUT               →    GPIO digital INPUT
```
- Attached to the **outside** of the plastic container
- 4 sensitivity levels with SET button
- HIGH = water present, LOW = empty container

### CYD ESP32 (indoor) — SHT30 indoor

```
CYD CN1 GPIO21   →    SHT30 SDA
CYD CN1 GPIO22   →    SHT30 SCL
10KΩ pull-up resistors on SDA and SCL
```

---

## Power Budget

| Component | Voltage | Current |
|---|---|---|
| Station-485 (normal operation) | 12V | ~161mA |
| Pump 1 (active) | 12V | 80mA |
| Pump 2 (active) | 12V | 80mA |
| Grove sensors | 5V | ~20mA total |
| **Maximum total** | **12V** | **~341mA** |

Recommended adapter: **12V 2A** (ample safety margin)

---

## Irrigation Logic

### Rules for succulents (very sensitive to overwatering)

```
Every 6 hours (via RTC BM8563):
  IF soil_moisture < dry_threshold:
    IF air_humidity < 85% (not raining):
      IF water_available == TRUE:
        activate_pump(planter, 20 seconds)  // ~33ml at 100ml/min
        wait 30 minutes
        read soil_moisture again
        IF still_dry: send Telegram alert
      ELSE:
        send Telegram alert "Empty water container"
```

### Reference flow rate (12V peristaltic pump)
- Maximum speed: ~100 ml/min = 1.67 ml/second
- 10 seconds = ~17 ml (gentle irrigation)
- 20 seconds = ~33 ml (normal succulent irrigation)
- 30 seconds = ~50 ml (heavy irrigation — avoid)

### Suggested thresholds (calibrate with Earth Sensor)
- Dry soil: < 30% moisture → irrigate
- Moist soil: 30-60% → do not irrigate
- Wet soil: > 60% → excess moisture alert

---

## Software Stack (Proxmox LXC)

### Services to install

| Service | Port | Function |
|---|---|---|
| Mosquitto | 1883 | MQTT broker — receives data from Station-485 and CYDs |
| InfluxDB 2.x | 8086 | Time-series database |
| Grafana | 3000 | Responsive web dashboard (mobile) |
| Telegram Bot | — | Automatic push alerts + NL agent |

### MQTT Topics

```
sniperstation/exterior/temperatura
sniperstation/exterior/humedad
sniperstation/exterior/luz
sniperstation/interior/master/temperatura
sniperstation/interior/master/humedad
sniperstation/interior/kids/temperatura
sniperstation/interior/kids/humedad
sniperstation/sucufer/humedad_suelo
sniperstation/sucurod/humedad_suelo
sniperstation/sucufer/bomba (0/1)
sniperstation/sucurod/bomba (0/1)
sniperstation/agua/nivel (0/1)
sniperstation/sistema/estado
```

### Telegram Alerts
- Irrigation executed (planter + ml delivered)
- Empty water container
- Soil very dry for more than 24h
- Exterior temperature > 38°C (extreme Orlando heat)
- Sensor disconnected / reading error

---

## Grafana Dashboard — Suggested Panels

1. **Exterior vs interior temperature** — timeline, last 24h
2. **Exterior vs interior humidity** — timeline
3. **Sunlight (lux)** — area, last 24h
4. **Soil moisture SucuFer and SucuRod** — gauge + history
5. **Recent irrigations** — table with timestamp and ml
6. **Water container level** — ON/OFF indicator
7. **Weekly summary** — temp min/max, total irrigations

---

## Important Considerations

### Orlando Heat
- Station-485 maximum temperature: **0~60°C**
- Orlando summer outdoors in direct sun: easily exceeds 60°C inside a closed box
- **Mandatory:** enclosure in **shade** + passive or active ventilation
- Consider a small 5V fan inside the box if needed

### Station-485 Port B2
- Uses GPIO G36 of ESP32
- G36 **CANNOT be configured as OUTPUT** on ESP32
- Earth Sensor 2 can only be INPUT (analog reading) — correct for this use
- Relays must NOT be connected to port B

### Shared I2C A1/A2
- DLight (0x23) and SHT30 (0x44) have different addresses → no conflict
- Both on the same I2C bus (G32/G33)

### Reversible pump
- Inverting polarity inverts flow direction
- Useful feature: drain tubing after irrigation to prevent residual moisture
- Implementable with double relay or H-bridge (L293D available in SunFounder kit)

---

## Complete Available Inventory

### Main Microcontrollers and Modules

| Component | Qty | Specifications | Potential Use |
|---|---|---|---|
| ESP8266 NodeMCU CP2102 | 2 | WiFi, ESP-12E, Arduino IDE/MicroPython compatible | Freed up — future projects |
| M5Stack Station-485 | 1 | ESP32, WiFi, RS485, 6x Grove, 1.14" display | SniperStation main brain |
| DLight BH1750 | 1 | I2C light sensor, 1-65535 lx, Grove | SniperStation exterior |

---

### SunFounder Raphael Ultimate Kit (337 pieces) — Detailed Inventory

#### Modules and Sensors
| Component | Qty | Specifications | Potential Use |
|---|---|---|---|
| I2C LCD 1602 | 1 | 16x2 display, I2C | Secondary display / status |
| Ultrasonic Ranging Module | 1 | HC-SR04, 2cm-400cm | Distance sensor / alternative water level |
| Dot Matrix Module | 1 | 8x8 LEDs | Animation display |
| Breadboard Power Module | 1 | 5V/3.3V | Prototype power supply |
| Rotary Encoder Module | 1 | — | Manual parameter control |
| Joystick | 1 | Analog X/Y + button | Menu navigation |
| MFRC522 RFID Module | 1 | 13.56MHz | Access control / authentication |
| Infrared Motion Sensor | 1 | PIR AS312 | Presence detection |
| Motor (DC) | 1 | — | Generic actuator |
| 9G Servo | 1 | SG90 | Valve control / movement |
| 4-Digit 7-segment Display | 1 | — | Numeric display |
| Keypad | 1 | 4x4 matrix | Data entry / PIN |
| Reed Switch Module | 1 | Magnetic | Box opening detection |
| Obstacle Avoidance Module | 1 | IR reflective | Proximity detection |
| Speed Sensor Module | 1 | LM393 + slot | Speed encoder / flow |
| Temperature and Humidity Sensor | 1 | DHT11 or DHT22 | Backup temp/hum sensor |
| MPU6050 Module | 1 | Accelerometer + gyroscope I2C | Motion / vibration detection |
| Audio Power Amplifier Module | 1 | — | Audio alerts |
| Touch Sensor Module | 1 | Capacitive | Manual irrigation touch button |
| Fan | 1 | 5V DC | Station-485 box ventilation if needed |
| LED Bar Graph | 1 | 10 segments | Visual water level indicator |
| Relay Module | 1 | 5V, 1 channel | Spare relay / future projects |
| Camera Module | 1 | For Raspberry Pi | Surveillance / plant timelapse |
| Speaker | 1 | — | Audio alerts |

#### Passive and Discrete Components
| Component | Qty | Value | Potential Use |
|---|---|---|---|
| Resistor | 10 | 10Ω | LED current limiting |
| Resistor | 10 | 100Ω | Current limiting |
| Resistor | 10 | 220Ω | Standard LEDs |
| Resistor | 10 | 330Ω | LEDs / voltage divider |
| Resistor | 10 | 1KΩ | Transistor base |
| Resistor | 10 | 2KΩ | Voltage dividers |
| Resistor | 10 | 5.1KΩ | Pull-down |
| Resistor | 10 | 10KΩ | I2C pull-up (CYD + ESP8266) |
| Resistor | 10 | 100KΩ | High impedance pull-down |
| Resistor | 10 | 1MΩ | High impedance |
| Zener Diode | 2 | — | Voltage regulation |
| 1N4007 Diode | 2 | — | Flyback protection for pumps |
| S8550 Transistor PNP | 5 | — | PNP switching |
| S8050 Transistor NPN | 5 | — | Load current control |
| Thermistor | 1 | NTC | Backup analog temperature |
| Electrolytic Capacitor | 5 | 10uF | Pump noise filtering |
| Ceramic Capacitor | 20 | 104/103 | Power supply decoupling |
| Photoresistor (LDR) | 1 | — | Backup analog light sensor |

#### Switches and Controls
| Component | Qty | Type | Potential Use |
|---|---|---|---|
| Button | 1 | Pushbutton | Reset / manual action |
| Potentiometer | 3 | — | Analog threshold adjustment |
| Micro Switch | 2 | — | End stop |
| Button Switch | 10 | Small pushbutton | Multiple interfaces |
| Slide Switch | 2 | — | Manual ON/OFF |
| Tilt Switch | 1 | — | Tilt / fall detection |

#### LEDs and Indicators
| Component | Qty | Color | Potential Use |
|---|---|---|---|
| Green LED | 5 | Green | OK status |
| Yellow LED | 5 | Yellow | Warning |
| Blue LED | 5 | Blue | Info / active irrigation |
| Red LED | 5 | Red | Alert / error |
| White LED | 5 | White | General lighting |
| RGB LED | 1 | RGB | Multi-state indicator |

#### ICs and Special Modules
| Component | Qty | Description | Potential Use |
|---|---|---|---|
| MCP3008 | 1 | 8-channel SPI ADC | More analog inputs |
| L293D | 1 | H-Bridge motor driver | Reversible pump (drain tubing) |
| 74HC595 | 2 | 8-bit shift register | Expand digital outputs |

#### Buzzers
| Component | Qty | Type | Potential Use |
|---|---|---|---|
| Active Buzzer | 2 | Fixed frequency | Simple audio alerts |
| Passive Buzzer | 2 | Variable frequency | Melodies / custom alerts |

#### Cables and Connectors
| Component | Qty | Type | Potential Use |
|---|---|---|---|
| Jump Wire F/M | 10 | 20cm | Prototype connections |
| Jump Wire F/F | 10 | 20cm | Module-to-module connections |
| Jump Wire M/M | 65 | 20cm | Breadboard |
| 40 Pin GPIO Cable | 1 | Raspberry Pi ribbon | GPIO expansion |
| 9V Battery Cable | 1 | — | Portable power |
| Audio Cable | 1 | — | Audio |

#### Other
| Component | Qty | Description |
|---|---|---|
| Breadboard | 1 | 830 points — ESP8266 prototyping |
| T-shape Extension Board | 1 | Raspberry Pi GPIO expansion |

---

### Additional Inventory (outside SunFounder kit)

| Component | Qty | Specifications | Potential Use |
|---|---|---|---|
| Touch Sensor Button | 2 | Capacitive, Arduino/ESP compatible | Manual touch irrigation (SniperStation) |
| ESP8266 NodeMCU CP2102 | 2 | ESP-12E, WiFi, Arduino/MicroPython | Freed up — future projects |
| IR Receiver 38kHz | 5 | Digital, Dupont cable | IR remote control projects |
| IR Transmitter 38kHz | 5 | Digital, Dupont cable | IR emitter / device control |
| KY-037 Sound Sensor | 6 | 4 pins, microphone, digital/analog output | Sound detection / noise level |

---

### Future Project Ideas with this Inventory

| Project | Required inventory components |
|---|---|
| **Succulent timelapse camera** | Camera Module + Raspberry Pi |
| **Local audio alert** when container empty | Active Buzzer + Station-485 |
| **IR remote irrigation control** | IR Receiver 38kHz + ESP8266 |
| **Automatic fan** for Station-485 box | 5V Fan + Relay + Thermistor |
| **Garden presence monitor** | PIR Motion Sensor + ESP8266 |
| **RFID lock** for outdoor enclosure | MFRC522 + ESP8266 |
| **Status display** visible from a distance | LED Bar Graph (water level) |
| **Manual control** with rotary encoder | Rotary Encoder + Station-485 |
| **Expansion to more planters** | MCP3008 (more analog inputs) + relays |
| **Reversible pump** to drain tubing | L293D H-Bridge |

---

## Design Decisions Made

1. **Peristaltic pump** over submersible → greater precision for succulents (small water amounts)
2. **One large shared container** for both pumps → simpler, less refilling
3. **Capacitive water level sensor** (XKC-Y25) → non-contact, no moving parts
4. **Station-485 outdoors** next to the planters → short cables, everything together
5. **CYD ESP32** indoors per bedroom → no cables through walls
6. **Proxmox LXC** for the software stack → infrastructure already available
7. **InfluxDB + Grafana + Mosquitto** → standard IoT stack, well documented
8. **12V 2A adapter** → powers Station-485 and pumps from a single source
9. **Generic SHT30** instead of M5Stack ENV III → out of stock, same chip

---

## Next Steps

- [ ] Buy: 12V 2A adapter, weatherproof enclosure
- [ ] Write Station-485 firmware (Arduino IDE)
- [ ] Write CYD indoor firmware (Arduino IDE + LVGL)
- [ ] Write TimerCam X firmware
- [ ] Calibrate Earth Sensors with the actual planters
- [ ] Calibrate exact pump flow rate (ml/second at 12V)
- [ ] Adjust humidity thresholds for specific succulents
- [ ] Configure Grafana dashboard (7 panels)
- [ ] Implement HTTP photo upload endpoint for TimerCam X
- [ ] Install and test in the field

---

*Document generated: March 25, 2026*
*Continue development in Claude Code using this file as context*
