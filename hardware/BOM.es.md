# Lista de Materiales — SniperStation

**Última actualización:** 2026-03-26
**Proyecto:** SniperStation — Riego automático de suculentas + estación meteorológica
**Ubicación:** Orlando, Florida (exterior, expuesto al sol y lluvia)

## Leyenda de Estado

| Estado | Significado |
|---|---|
| ✅ En mano | Físicamente disponible |
| 🚚 Ordenado | Comprado, en tránsito |
| ⏳ Pendiente | Aún no comprado |

---

## Componentes Principales

| # | Componente | Modelo / Parte | Cant | Voltaje | Notas | Proveedor | Estado |
|---|---|---|---|---|---|---|---|
| 1 | Controlador principal | M5Stack Station-485 | 1 | 9–24V entrada | ESP32, WiFi, pantalla 1.14", 6x Grove HY2.0, RS485, RTC BM8563 | M5Stack | ✅ En mano |
| 2 | Sensor de luz | DLight BH1750 | 1 | 3.3–5V | Dirección I2C 0x23, rango 1–65535 lx, Grove HY2.0 | M5Stack | ✅ En mano |
| 3 | Sensor temp/humedad (exterior) | SHT30 IOT-TH02 | 1 | 2.15–5.5V | Dirección I2C 0x44, cables sueltos codificados por color | Amazon | 🚚 Ordenado |
| 4 | Sensor temp/humedad (interior) | SHT30 IOT-TH02 | 1 | 2.15–5.5V | Dirección I2C 0x44, cables sueltos codificados por color | Amazon | 🚚 Ordenado |
| 5 | Sensor humedad de suelo | M5Stack Earth Sensor | 2 | 3.3–5V | Salida analógica + digital, Grove HY2.0 | M5Stack | 🚚 Ordenado |
| 6 | Módulo relay | M5Stack Mini Relay 3A | 2 | 5V control | 3A/30VDC, Grove HY2.0, NO/NC/COM | M5Stack | 🚚 Ordenado |
| 7 | Bomba peristáltica | Bomba DC 12–24V | 2 | 12V | ~100 ml/min, 80mA, reversible, tuberías incluidas | Amazon | 🚚 Ordenado |
| 8 | Sensor nivel agua | XKC-Y25-V + driver DFRobot | 1 | 5–24V | Sin contacto capacitivo, salida digital, 4 niveles de sensibilidad | Amazon | 🚚 Ordenado |
| 9 | Unidad interior (todo en uno) | ESP32-2432S028 CYD | 2 | 5V USB | ESP32 dual-core + TFT 2.8" 240x320 color + táctil resistivo. Una por habitación (principal + niños). I2C SHT30 en CN1 (GPIO21/22) | Amazon | 🚚 Ordenado |
| 10 | Cable Grove↔Dupont | HY2.0-4P a 2.54mm hembra 20cm | 2 | — | Conecta SHT30 a puertos Grove Station-485. WatangTech en Amazon | Amazon | 🚚 Ordenado |
| 11 | Cámara timelapse | M5Stack ESP32 PSRAM Timer Camera X (OV3660) | 1 | 5V USB | 3MP 2048x1536, FOV 66.5°, WiFi, RTC BM8563, batería 140mAh, sleep 2µA. Una unidad cubre ambos materos. 48x24x15mm | M5Stack | 🚚 Ordenado |

---

## Componentes de Alimentación y Enclosure

| # | Componente | Especificación | Cant | Notas | Proveedor | Costo Estimado |
|---|---|---|---|---|---|---|
| 13 | Adaptador DC | 12V 2A, conector barrel 5.5x2.1mm | 1 | Alimenta Station-485 + ambas bombas desde una sola fuente | Amazon | 🚚 Ordenado |
| 16 | Convertidor buck DC-DC | LM2596 ajustable, 4–40V entrada, 1.25–37V salida, 2A | 2 | Fijar salida en 5V (voltímetro incorporado). Alimenta TimerCam X desde riel 12V. 1 unidad + 1 repuesto | Amazon | 🚚 Ordenado |
| 17 | Conectores de distribución | Wago 221-415 (5 puertos) | 2 | Uno para riel +12V, uno para riel GND. Sin soldadura. 1 entrada → 4 salidas cada uno | Amazon | 🚚 Ordenado |
| 14 | Enclosure exterior resistente | IP65 mín, 150x120x80mm mín, ranuras de ventilación o montaje para ventilador | 1 | Debe soportar el calor del verano de Orlando — instalación en sombra obligatoria | Amazon | ⏳ Pendiente |
| 15 | Enclosure unidad interior x2 | Impresión 3D personalizada | 2 | Contiene CYD ESP32-2432S028 + SHT30 (marco de pared). Mismo diseño impreso dos veces | Servicio 3D | ⏳ Pendiente |

---

## Componentes de Soporte (del Kit SunFounder / Inventario)

Usados durante el prototipado y ensamblaje. Marcados con uso previsto.

| Componente | Cant | Valor | Uso en SniperStation |
|---|---|---|---|
| Resistor | 2 | 10KΩ | Pull-ups I2C en CN1 SDA/SCL del CYD para SHT30 (1 por unidad x 2 unidades) |
| Diodo 1N4007 | 2 | — | Protección flyback en salidas de relay de bombas |
| Capacitor electrolítico | 2 | 10µF | Filtro de ruido de alimentación cerca de relays de bombas |
| Cable jumper H/H | 4 | 20cm | Conexiones CYD CN1 ↔ SHT30 interior |
| Cable jumper M/M | 6 | 20cm | Prototipado en breadboard |
| Ventilador (5V DC) | 1 (opcional) | — | Ventilación del enclosure si la ventilación pasiva es insuficiente |

---

## No Usados en SniperStation (reservados para proyectos futuros)

| Componente | Cant | Uso Potencial |
|---|---|---|
| ESP8266 NodeMCU CP2102 | 2 | Liberados — proyectos futuros |
| Sensor táctil TTP223 | 2 | Liberados — proyectos futuros |
| HC-SR04 ultrasónico | 1 | Sensor alternativo de nivel de agua |
| L293D H-Bridge | 1 | Control reversible de bomba (drenar tuberías después del riego) |
| MCP3008 ADC | 1 | Expansión a más materos (más entradas analógicas) |
| Módulo de cámara (genérico) | 1 | Reemplazado por M5Stack TimerCam X (ordenado) |
| Sensor PIR de movimiento | 1 | Detección de presencia en el jardín |

---

## Presupuesto de Potencia

| Componente | Voltaje | Corriente (típica) | Corriente (pico) |
|---|---|---|---|
| Station-485 (reposo) | 12V | 120mA | — |
| Station-485 (WiFi activo) | 12V | 161mA | 200mA |
| Bomba 1 (activa) | 12V | 80mA | 100mA |
| Bomba 2 (activa) | 12V | 80mA | 100mA |
| Sensores Grove total | 5V (interno) | ~20mA | — |
| **Total (ambas bombas + WiFi)** | **12V** | **~341mA** | **~400mA** |

**Adaptador:** 12V 2A → capacidad 2000mA vs 400mA consumo pico. Margen de seguridad: **5x**. ✅

> Nota: Ambas bombas no se activarán simultáneamente por diseño (un matero a la vez).
> Peor caso real: 161mA (controlador) + 80mA (una bomba) = 241mA.

---

## Referencias de Datasheets

Ver [datasheets/SOURCES.md](datasheets/SOURCES.md) para los enlaces a todos los datasheets de componentes.
