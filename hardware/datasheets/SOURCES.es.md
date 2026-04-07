# Fuentes de Datasheets — SniperStation

Documentación oficial y datasheets de todos los componentes usados en este proyecto.

---

## Controlador Principal

### M5Stack Station-485
- **Página del producto:** https://docs.m5stack.com/en/base/station_485
- **Datasheet ESP32-D0WDQ6:** https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf
- **Manual técnico ESP32:** https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf
- **Datasheet RTC BM8563:** https://www.nxp.com/docs/en/data-sheet/PCF8563.pdf *(BM8563 es compatible con PCF8563)*

---

## Sensores

### DLight BH1750 — Sensor de Luz
- **Datasheet:** https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf
- **Dirección I2C:** 0x23 (ADDR bajo) / 0x5C (ADDR alto)
- **Especificación clave:** 1–65535 lx, resolución de 16 bits

### SHT30 IOT-TH02 — Temperatura y Humedad
- **Datasheet Sensirion SHT30:** https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
- **Dirección I2C:** 0x44 (ADDR bajo) / 0x45 (ADDR alto)
- **Especificaciones clave:** Temp ±0.3°C, Humedad ±2% RH, alimentación 2.15–5.5V

### M5Stack Earth Sensor — Humedad de Suelo
- **Página del producto:** https://docs.m5stack.com/en/unit/earth
- **Salida:** Analógica (0–3.3V) + digital de umbral (ajustable por potenciómetro)
- **Nota clave:** Requiere calibración con el tipo de suelo real

### XKC-Y25-V — Sensor de Nivel de Agua Sin Contacto
- **Página del producto XKC-Y25-V:** https://www.xkc.com.cn/en/product/XKC-Y25-V.html
- **Wiki DFRobot:** https://wiki.dfrobot.com/Non-contact_Liquid_Level_Sensor_XKC-Y25_T12V_SKU__SEN0204
- **Especificaciones clave:** 5–24V, salida digital, funciona en paredes de plástico/vidrio ≤ 3mm, 4 niveles de sensibilidad

---

## Actuadores

### M5Stack Mini Relay 3A
- **Página del producto:** https://docs.m5stack.com/en/unit/mini_relay
- **Especificaciones clave:** 3A/30VDC, 3A/125VAC, control Grove HY2.0, LOW = OFF, HIGH = ON

### Bomba Peristáltica 12V DC
- El datasheet varía según el proveedor. Especificaciones clave verificadas:
  - Voltaje de operación: 12–24V DC
  - Caudal: ~100 ml/min a 12V
  - Corriente: ~80mA a 12V
  - Reversible por inversión de polaridad
  - Tuberías: silicona, aptas para alimentos

---

## Controlador Interior

### ESP8266 NodeMCU CP2102 (ESP-12E)
- **Datasheet ESP8266:** https://www.espressif.com/sites/default/files/documentation/0a-esp8266ex_datasheet_en.pdf
- **Referencia técnica ESP8266:** https://www.espressif.com/sites/default/files/documentation/esp8266-technical_reference_en.pdf
- **Referencia pinout NodeMCU:** https://components101.com/development-boards/nodemcu-esp8266-pinout-features-and-datasheet
- **Bridge USB-UART CP2102:** https://www.silabs.com/documents/public/data-sheets/CP2102-9.pdf

---

## Componentes de Soporte

### Diodo Rectificador 1N4007 (protección flyback)
- **Datasheet:** https://www.vishay.com/docs/88503/1n4007.pdf
- **Uso:** Diodo flyback/freewheeling en cargas inductivas (motores de bomba)

### L293D H-Bridge Motor Driver (opcional — bombas reversibles)
- **Datasheet:** https://www.ti.com/lit/ds/symlink/l293d.pdf
- **Uso:** Si se necesita control bidireccional de bomba (drenar tuberías después del riego)

### MCP3008 ADC (opcional — expansión)
- **Datasheet:** https://ww1.microchip.com/downloads/en/DeviceDoc/21295d.pdf
- **Uso:** ADC SPI de 8 canales y 10 bits para ampliar entradas analógicas

---

## Referencias de Software / Protocolo

### Protocolo MQTT
- **Especificación MQTT 3.1.1:** https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html

### InfluxDB 2.x
- **Documentación:** https://docs.influxdata.com/influxdb/v2/

### Grafana
- **Documentación:** https://grafana.com/docs/grafana/latest/

### Mosquitto MQTT Broker
- **Documentación:** https://mosquitto.org/documentation/

---

## Estándares Referenciados

| Estándar | Descripción |
|---|---|
| CERN OHL v2 Permissive | Licencia de hardware abierto usada en este proyecto |
| Especificación I2C | https://www.nxp.com/docs/en/user-guide/UM10204.pdf |
| Estándar conector Grove | HY2.0-4P, paso 2mm, orden de pines: GND/VCC/GPIO_B/GPIO_A |
