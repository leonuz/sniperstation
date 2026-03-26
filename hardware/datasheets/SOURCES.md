# Component Datasheet Sources — SniperStation

All official documentation and datasheets for components used in this project.

---

## Main Controller

### M5Stack Station-485
- **Product page:** https://docs.m5stack.com/en/base/station_485
- **ESP32-D0WDQ6 datasheet:** https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf
- **ESP32 technical reference manual:** https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf
- **RTC BM8563 datasheet:** https://www.nxp.com/docs/en/data-sheet/PCF8563.pdf *(BM8563 is compatible with PCF8563)*

---

## Sensors

### DLight BH1750 — Light Sensor
- **Datasheet:** https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf
- **I2C address:** 0x23 (ADDR low) / 0x5C (ADDR high)
- **Key spec:** 1–65535 lx, 16-bit resolution

### SHT30 IOT-TH02 — Temperature & Humidity
- **Sensirion SHT30 datasheet:** https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
- **I2C address:** 0x44 (ADDR low) / 0x45 (ADDR high)
- **Key specs:** Temp ±0.3°C, Humidity ±2% RH, 2.15–5.5V supply

### M5Stack Earth Sensor — Soil Moisture
- **Product page:** https://docs.m5stack.com/en/unit/earth
- **Output:** Analog (0–3.3V) + Digital threshold (adjustable via potentiometer)
- **Key note:** Requires calibration with actual soil type

### XKC-Y25-V — Non-Contact Water Level Sensor
- **XKC-Y25-V product page:** https://www.xkc.com.cn/en/product/XKC-Y25-V.html
- **DFRobot driver wiki:** https://wiki.dfrobot.com/Non-contact_Liquid_Level_Sensor_XKC-Y25_T12V_SKU__SEN0204
- **Key specs:** 5–24V, digital output, works on plastic/glass walls ≤ 3mm, 4 sensitivity levels

---

## Actuators

### M5Stack Mini 3A Relay
- **Product page:** https://docs.m5stack.com/en/unit/mini_relay
- **Key specs:** 3A/30VDC, 3A/125VAC, Grove HY2.0 control, LOW = OFF, HIGH = ON

### Peristaltic Pump 12V DC
- Datasheet varies by supplier. Key verified specs:
  - Operating voltage: 12–24V DC
  - Flow rate: ~100 ml/min at 12V
  - Current: ~80mA at 12V
  - Reversible by polarity inversion
  - Tubing: silicone, food-safe

---

## Indoor Controller

### ESP8266 NodeMCU CP2102 (ESP-12E)
- **ESP8266 datasheet:** https://www.espressif.com/sites/default/files/documentation/0a-esp8266ex_datasheet_en.pdf
- **ESP8266 technical reference:** https://www.espressif.com/sites/default/files/documentation/esp8266-technical_reference_en.pdf
- **NodeMCU pinout reference:** https://components101.com/development-boards/nodemcu-esp8266-pinout-features-and-datasheet
- **CP2102 USB-UART bridge:** https://www.silabs.com/documents/public/data-sheets/CP2102-9.pdf

---

## Supporting Components

### 1N4007 Rectifier Diode (flyback protection)
- **Datasheet:** https://www.vishay.com/docs/88503/1n4007.pdf
- **Use:** Flyback/freewheeling diode across inductive loads (pump motors)

### L293D H-Bridge Motor Driver (optional — reversible pumps)
- **Datasheet:** https://www.ti.com/lit/ds/symlink/l293d.pdf
- **Use:** If bidirectional pump control is needed (drain tubing after irrigation)

### MCP3008 ADC (optional — expansion)
- **Datasheet:** https://ww1.microchip.com/downloads/en/DeviceDoc/21295d.pdf
- **Use:** 8-channel 10-bit SPI ADC for expanding analog inputs

---

## Software / Protocol References

### MQTT Protocol
- **MQTT 3.1.1 specification:** https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html

### InfluxDB 2.x
- **Documentation:** https://docs.influxdata.com/influxdb/v2/

### Grafana
- **Documentation:** https://grafana.com/docs/grafana/latest/

### Mosquitto MQTT Broker
- **Documentation:** https://mosquitto.org/documentation/

---

## Standards Referenced

| Standard | Description |
|---|---|
| CERN OHL v2 Permissive | Open hardware license used for this project |
| I2C specification | https://www.nxp.com/docs/en/user-guide/UM10204.pdf |
| Grove connector standard | HY2.0-4P, 2mm pitch, pin order: GND/VCC/GPIO_B/GPIO_A |
