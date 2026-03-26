# SniperStation — Proyecto Completo
> Documento de contexto para Claude Code  
> Generado desde sesión de planificación en Claude.ai

---

## 📋 Descripción del Proyecto

Sistema automático de riego + estación meteorológica para dos materos de suculentas ubicados **afuera** de una casa en **Orlando, Florida**. El sistema monitorea condiciones ambientales (temperatura, humedad, luz solar, humedad del suelo) y riega automáticamente en base a sensores, con dashboard web, alertas por Telegram e historial de datos.

---

## 🏗️ Arquitectura del Sistema

```
[AFUERA]                                    [ADENTRO]
Station-485 (cerebro principal)             ESP8266 NodeMCU
├── DLight BH1750    → Puerto A1            └── SHT30 interior (temp/hum AC)
├── SHT30 exterior   → Puerto A2                │
├── Earth Sensor 1   → Puerto B1                │
├── Earth Sensor 2   → Puerto B2                │
├── Relay Bomba 1    → Puerto C1                │
├── Relay Bomba 2    → Puerto C2                │
└── Sensor nivel H2O → Puerto B o C             │
     (XKC-Y25)                                  │
          │                                     │
          └──────── WiFi → MQTT ────────────────┘
                         │
                  [Proxmox LXC]
                  ├── Mosquitto (MQTT broker)
                  ├── InfluxDB (base de datos series de tiempo)
                  ├── Grafana (dashboard web / celular)
                  └── Bot Telegram (alertas)
```

---

## 📦 Lista Completa de Hardware

### ✅ Ya confirmado / comprado

| Componente | Modelo | Detalles | Origen |
|---|---|---|---|
| Controlador principal | M5Stack Station-485 | ESP32, WiFi, pantalla 1.14", 6x Grove, RS485, 9-24V input | Ya tiene |
| Sensor de luz | DLight BH1750 | I2C (0x23), 1-65535 lx, Grove HY2.0 | Ya tiene |
| Sensor temp/hum x2 | SHT30 IOT-TH02 | I2C (0x44), 2.15-5.5V, cables sueltos de colores | Amazon ✅ |
| Cable Grove↔Dupont | HY2.0-4P a 2.54mm female | Para conectar SHT30 al Station-485 | Amazon ✅ |
| Bombas peristálticas x2 | DC 12-24V | 0-100 ml/min, 80mA, reversible, con manguera | Amazon ✅ |
| Sensor nivel agua | XKC-Y25-V + driver DFRobot | No contacto, 5-24V, salida digital, 4 niveles sensibilidad | Amazon ✅ |
| Sensor humedad suelo x2 | M5Stack Earth Sensor | Analógico + digital, Grove HY2.0 | M5Stack ✅ |
| Relay x2 | M5Stack Mini 3A Relay | 3A/30VDC, control GPIO, Grove HY2.0 | M5Stack ✅ |
| Microcontrolador interior | ESP8266 NodeMCU CP2102 | WiFi, para SHT30 interior | Inventario ✅ |

### 🛒 Pendiente comprar (Amazon)

| Componente | Especificación | Notas |
|---|---|---|
| Adaptador DC | 12V 2A, conector 5.5mm | Alimenta Station-485 + bombas |
| Caja exterior | Weatherproof enclosure con ventilación | Proteger del calor de Orlando (máx 60°C) |
| Cable Grove↔Dupont | HY2.0-4P a Dupont female 20cm | Ya encontrado: WatangTech en Amazon |

---

## 🔌 Conexiones / Pinout

### Station-485 — Puertos Grove

| Puerto | Sensor/Actuador | Protocolo | Notas |
|---|---|---|---|
| A1 | DLight BH1750 | I2C (0x23) | Compartido bus con A2 |
| A2 | SHT30 exterior | I2C (0x44) | Compartido bus con A1 — sin conflicto |
| B1 | Earth Sensor SucuFer | Analógico | G25/G35 |
| B2 | Earth Sensor SucuRod | Analógico | G26/G36 ⚠️ G36 no puede ser OUTPUT |
| C1 | Relay → Bomba 1 | Digital OUTPUT | G14 |
| C2 | Relay → Bomba 2 | Digital OUTPUT | G17 |
| USB-A output | Sensor XKC-Y25 (VCC) | 5V power only | Sin señal |
| B o C libre | XKC-Y25 señal OUT | Digital INPUT | Confirmar puerto disponible |

### SHT30 — Conexión al cable Grove↔Dupont

```
Cable Grove (Station-485)    →    SHT30 (cables sueltos)
Rojo   (5V)                  →    Rojo   (VCC)
Negro  (GND)                 →    Negro  (GND)
Amarillo (SDA)               →    Blanco (SDA) ⚠️ CRUZADO
Blanco   (SCL)               →    Amarillo (SCL) ⚠️ CRUZADO
```

### Bombas peristálticas — Alimentación

```
Adaptador 12V 2A
├── PWR485 → alimenta Station-485
├── Relay C1 (NO) → Bomba 1 (rojo +12V)
└── Relay C2 (NO) → Bomba 2 (rojo +12V)
Común GND compartido entre todo
```

### Sensor nivel agua XKC-Y25-V

```
Driver DFRobot    →    Station-485
VCC               →    5V (USB-A output o Grove)
GND               →    GND
OUT               →    GPIO digital INPUT
```
- Se pega por **fuera** del recipiente plástico
- 4 niveles de sensibilidad con botón SET
- HIGH = hay agua, LOW = recipiente vacío

### ESP8266 NodeMCU (interior) — SHT30 interior

```
ESP8266      →    SHT30 interior
3.3V         →    Rojo (VCC)
GND          →    Negro (GND)
D2 (GPIO4)   →    Blanco (SDA) ⚠️ cruzado vs color
D1 (GPIO5)   →    Amarillo (SCL) ⚠️ cruzado vs color
```
- Resistencias pull-up 10KΩ en SDA y SCL (disponibles en kit SunFounder)
- Publica por MQTT al broker Mosquitto en Proxmox

---

## ⚡ Presupuesto de Energía

| Componente | Voltaje | Corriente |
|---|---|---|
| Station-485 (operación normal) | 12V | ~161mA |
| Bomba 1 (activa) | 12V | 80mA |
| Bomba 2 (activa) | 12V | 80mA |
| Sensores Grove | 5V | ~20mA total |
| **Total máximo** | **12V** | **~341mA** |

Adaptador recomendado: **12V 2A** (margen de seguridad amplio)

---

## 🧠 Lógica de Riego

### Reglas para suculentas (muy sensibles a exceso de agua)

```
Cada 6 horas (via RTC BM8563):
  SI humedad_suelo < umbral_seco:
    SI humedad_aire < 85% (no está lloviendo):
      SI hay_agua == TRUE:
        activar_bomba(matero, 20 segundos)  // ~33ml a 100ml/min
        esperar 30 minutos
        leer humedad_suelo nuevamente
        SI sigue_seco: enviar alerta Telegram
      SINO:
        enviar alerta Telegram "Recipiente vacío"
```

### Caudal de referencia (bomba peristáltica 12V)
- Velocidad máxima: ~100 ml/min = 1.67 ml/segundo
- 10 segundos = ~17 ml (riego suave)
- 20 segundos = ~33 ml (riego normal suculenta)
- 30 segundos = ~50 ml (riego abundante — evitar)

### Umbrales sugeridos (calibrar con Earth Sensor)
- Suelo seco: < 30% humedad → regar
- Suelo húmedo: 30-60% → no regar
- Suelo mojado: > 60% → alerta de exceso

---

## 🖥️ Stack de Software (Proxmox LXC)

### Servicios a instalar

| Servicio | Puerto | Función |
|---|---|---|
| Mosquitto | 1883 | MQTT broker — recibe datos de Station-485 y ESP8266 |
| InfluxDB 2.x | 8086 | Base de datos de series de tiempo |
| Grafana | 3000 | Dashboard web responsive (celular) |
| Telegram Bot | — | Alertas push automáticas |

### Topics MQTT

```
sniperstation/exterior/temperatura
sniperstation/exterior/humedad
sniperstation/exterior/luz
sniperstation/interior/temperatura
sniperstation/interior/humedad
sniperstation/sucufer/humedad_suelo
sniperstation/sucurod/humedad_suelo
sniperstation/sucufer/bomba (0/1)
sniperstation/sucurod/bomba (0/1)
sniperstation/agua/nivel (0/1)
sniperstation/sistema/estado
```

### Alertas Telegram
- 🚿 Riego ejecutado (matero + ml entregados)
- 💧 Recipiente de agua vacío
- 🌵 Suelo muy seco hace más de 24h
- 🌡️ Temperatura exterior > 38°C (calor extremo Orlando)
- ⚠️ Sensor desconectado / error de lectura

---

## 📊 Dashboard Grafana — Panels sugeridos

1. **Temperatura exterior vs interior** — línea de tiempo, últimas 24h
2. **Humedad exterior vs interior** — línea de tiempo
3. **Luz solar (lux)** — área, últimas 24h
4. **Humedad suelo SucuFer y 2** — gauge + histórico
5. **Últimos riegos** — tabla con timestamp y ml
6. **Nivel de agua recipiente** — indicador ON/OFF
7. **Resumen semanal** — temp min/max, riegos totales

---

## ⚠️ Consideraciones Importantes

### Calor de Orlando
- Station-485 temperatura máxima: **0~60°C**
- En verano Orlando afuera al sol: fácilmente supera 60°C dentro de caja cerrada
- **Obligatorio:** caja a la **sombra** + ventilación pasiva o activa
- Considerar ventilador pequeño 5V dentro de la caja si es necesario

### Puerto B2 del Station-485
- Usa GPIO G36 del ESP32
- G36 **NO puede configurarse como OUTPUT** en ESP32
- Earth Sensor 2 solo puede ser INPUT (lectura analógica) — correcto para este uso
- Los Relay NO deben conectarse al puerto B

### I2C compartido A1/A2
- DLight (0x23) y SHT30 (0x44) tienen direcciones diferentes → sin conflicto
- Ambos en el mismo bus I2C (G32/G33)

### Bomba reversible
- Invertir polaridad invierte dirección de flujo
- Feature útil: drenar manguera después de regar para evitar humedad residual
- Implementable con relay doble o H-bridge (L293D disponible en kit SunFounder)

---

## 🗂️ Inventario Completo Disponible

### Microcontroladores y Módulos Principales

| Componente | Cantidad | Especificaciones | Uso potencial |
|---|---|---|---|
| ESP8266 NodeMCU CP2102 | 2 | WiFi, ESP-12E, compatible Arduino IDE/MicroPython | 1x SHT30 interior (SniperStation) / 1x libre |
| M5Stack Station-485 | 1 | ESP32, WiFi, RS485, 6x Grove, pantalla 1.14" | Cerebro SniperStation |
| DLight BH1750 | 1 | Sensor luz I2C, 1-65535 lx, Grove | SniperStation exterior |

---

### Kit SunFounder Raphael Ultimate (337 piezas) — Inventario detallado

#### Módulos y Sensores
| Componente | Cantidad | Especificaciones | Uso potencial |
|---|---|---|---|
| I2C LCD 1602 | 1 | Display 16x2, I2C | Display secundario / status |
| Ultrasonic Ranging Module | 1 | HC-SR04, 2cm-400cm | Sensor distancia / nivel agua alternativo |
| Dot Matrix Module | 1 | 8x8 LEDs | Display animaciones |
| Breadboard Power Module | 1 | 5V/3.3V | Alimentación prototipos |
| Rotary Encoder Module | 1 | — | Control manual parámetros |
| Joystick | 1 | Analógico X/Y + botón | Navegación menús |
| MFRC522 RFID Module | 1 | 13.56MHz | Control acceso / autenticación |
| Infrared Motion Sensor | 1 | PIR AS312 | Detección presencia |
| Motor (DC) | 1 | — | Actuador genérico |
| 9G Servo | 1 | SG90 | Control válvula / movimiento |
| 4-Digit 7-segment Display | 1 | — | Display numérico |
| Keypad | 1 | 4x4 matricial | Entrada datos / PIN |
| Reed Switch Module | 1 | Magnético | Detección apertura caja |
| Obstacle Avoidance Module | 1 | IR reflexivo | Detección proximidad |
| Speed Sensor Module | 1 | LM393 + ranura | Encoder velocidad / flujo |
| Temperature and Humidity Sensor | 1 | DHT11 o DHT22 | Backup sensor temp/hum |
| MPU6050 Module | 1 | Acelerómetro + giroscopio I2C | Detección movimiento / vibración |
| Audio Power Amplifier Module | 1 | — | Alertas sonoras |
| Touch Sensor Module | 1 | Capacitivo | Botón táctil riego manual (SniperStation) |
| Fan (ventilador) | 1 | 5V DC | ⭐ Ventilación caja Station-485 si necesario |
| LED Bar Graph | 1 | 10 segmentos | Indicador nivel agua visual |
| Relay Module | 1 | 5V, 1 canal | Repuesto relay / proyectos futuros |
| Camera Module | 1 | Para Raspberry Pi | Vigilancia / timelapse plantas |
| Speaker | 1 | — | Alertas sonoras |

#### Componentes Pasivos y Discretos
| Componente | Cantidad | Valor | Uso potencial |
|---|---|---|---|
| Resistor | 10 | 10Ω | Limitación corriente LEDs |
| Resistor | 10 | 100Ω | Limitación corriente |
| Resistor | 10 | 220Ω | LEDs estándar |
| Resistor | 10 | 330Ω | LEDs / divisor tensión |
| Resistor | 10 | 1KΩ | Base transistores |
| Resistor | 10 | 2KΩ | Divisores tensión |
| Resistor | 10 | 5.1KΩ | Pull-down |
| Resistor | 10 | 10KΩ | ⭐ Pull-up I2C ESP8266 |
| Resistor | 10 | 100KΩ | Pull-down alta impedancia |
| Resistor | 10 | 1MΩ | Alta impedancia |
| Zener Diode | 2 | — | Regulación voltaje |
| 1N4007 Diode | 2 | — | ⭐ Protección flyback bombas |
| S8550 Transistor PNP | 5 | — | Conmutación PNP |
| S8050 Transistor NPN | 5 | — | ⭐ Control corriente cargas |
| Thermistor | 1 | NTC | Temperatura analógica backup |
| Capacitor electrolítico | 5 | 10uF | ⭐ Filtrado ruido bombas |
| Capacitor cerámico | 20 | 104/103 | Desacople alimentación |
| Photoresistor (LDR) | 1 | — | Sensor luz analógico backup |

#### Switches y Controles
| Componente | Cantidad | Tipo | Uso potencial |
|---|---|---|---|
| Button | 1 | Pulsador | Reset / acción manual |
| Potentiometer | 3 | — | Ajuste umbrales analógico |
| Micro Switch | 2 | — | Fin de carrera |
| Button Switch | 10 | Pulsador pequeño | Interfaces múltiples |
| Slide Switch | 2 | — | ON/OFF manual |
| Tilt Switch | 1 | — | Detección inclinación / caída |

#### LEDs e Indicadores
| Componente | Cantidad | Color | Uso potencial |
|---|---|---|---|
| Green LED | 5 | Verde | Estado OK |
| Yellow LED | 5 | Amarillo | Advertencia |
| Blue LED | 5 | Azul | Info / riego activo |
| Red LED | 5 | Rojo | Alerta / error |
| White LED | 5 | Blanco | Iluminación general |
| RGB LED | 1 | RGB | Indicador multiestado |

#### ICs y Módulos Especiales
| Componente | Cantidad | Descripción | Uso potencial |
|---|---|---|---|
| MCP3008 | 1 | ADC 8 canales SPI | Más entradas analógicas |
| L293D | 1 | H-Bridge motor driver | ⭐ Bomba reversible (drenar manguera) |
| 74HC595 | 2 | Shift register 8-bit | Expandir salidas digitales |

#### Buzzer
| Componente | Cantidad | Tipo | Uso potencial |
|---|---|---|---|
| Active Buzzer | 2 | Frecuencia fija | Alertas sonoras simples |
| Passive Buzzer | 2 | Frecuencia variable | Melodías / alertas personalizadas |

#### Cables y Conectores
| Componente | Cantidad | Tipo | Uso potencial |
|---|---|---|---|
| Jump Wire F/M | 10 | 20cm | ⭐ Conexiones prototipo |
| Jump Wire F/F | 10 | 20cm | ⭐ Conexiones entre módulos |
| Jump Wire M/M | 65 | 20cm | ⭐ Breadboard |
| 40 Pin GPIO Cable | 1 | Cinta Raspberry Pi | Expansión GPIO |
| 9V Battery Cable | 1 | — | Alimentación portátil |
| Audio Cable | 1 | — | Audio |

#### Otros
| Componente | Cantidad | Descripción |
|---|---|---|
| Breadboard | 1 | 830 puntos — prototipado ESP8266 |
| T-shape Extension Board | 1 | Expansión GPIO Raspberry Pi |

---

### Inventario Adicional (fuera del kit SunFounder)

| Componente | Cantidad | Especificaciones | Uso potencial |
|---|---|---|---|
| Touch Sensor Button | 2 | Capacitivo, compatible Arduino/ESP | Riego manual táctil (SniperStation) |
| ESP8266 NodeMCU CP2102 | 2 | ESP-12E, WiFi, Arduino/MicroPython | 1x usado SniperStation / 1x libre |
| IR Receiver 38kHz | 5 | Digital, con cable Dupont | Control remoto IR proyectos |
| IR Transmitter 38kHz | 5 | Digital, con cable Dupont | Emisor IR / control dispositivos |
| KY-037 Sound Sensor | 6 | 4 pines, micrófono, salida digital/analógica | Detección sonido / nivel ruido |

---

### 💡 Ideas de Proyectos Futuros con este Inventario

| Proyecto | Componentes necesarios del inventario |
|---|---|
| **Cámara timelapse de las suculentas** | Camera Module + Raspberry Pi |
| **Alerta sonora local** cuando recipiente vacío | Active Buzzer + Station-485 |
| **Control remoto IR del riego** | IR Receiver 38kHz + ESP8266 |
| **Ventilador automático** para caja Station-485 | Fan 5V + Relay + Thermistor |
| **Monitor de presencia** en el jardín | PIR Motion Sensor + ESP8266 |
| **Cerradura RFID** para caja exterior | MFRC522 + ESP8266 |
| **Display de estado** visible desde lejos | LED Bar Graph (nivel agua) |
| **Control manual** con encoder rotativo | Rotary Encoder + Station-485 |
| **Expansión a más materos** | MCP3008 (más entradas analógicas) + relays |
| **Bomba reversible** para drenar mangueras | L293D H-Bridge |

---

## 📝 Decisiones de Diseño Tomadas

1. **Bomba peristáltica** sobre sumergible → mayor precisión para suculentas (poca agua)
2. **Un recipiente grande compartido** para las dos bombas → más simple, menos recarga
3. **Sensor nivel agua capacitivo** (XKC-Y25) → no contacto, sin partes móviles
4. **Station-485 afuera** junto a los materos → cables cortos, todo junto
5. **ESP8266 adentro** para SHT30 interior → sin cables atravesando paredes
6. **Proxmox LXC** para el stack de software → ya tiene infraestructura disponible
7. **InfluxDB + Grafana + Mosquitto** → stack estándar IoT, bien documentado
8. **Adaptador 12V 2A** → alimenta Station-485 y bombas desde una sola fuente
9. **SHT30 genérico** en vez de ENV III M5Stack → out of stock, mismo chip

---

## 🚀 Próximos Pasos

- [ ] Comprar: Adaptador 12V 2A, caja weatherproof, cable Grove↔Dupont
- [ ] Instalar LXC en Proxmox con Mosquitto + InfluxDB + Grafana
- [ ] Crear bot de Telegram
- [ ] Programar Station-485 (Arduino IDE)
- [ ] Programar ESP8266 (Arduino IDE)
- [ ] Calibrar Earth Sensors con los materos reales
- [ ] Calibrar caudal exacto de las bombas (ml/segundo a 12V)
- [ ] Ajustar umbrales de humedad para suculentas específicas
- [ ] Configurar dashboard Grafana
- [ ] Instalar y probar en campo

---

*Documento generado el 25 de Marzo 2026*  
*Continuar desarrollo en Claude Code con este archivo como contexto*
