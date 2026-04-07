# Diagrama de Conexiones — Station-485

**Controlador:** M5Stack Station-485 (ESP32-D0WDQ6)
**Voltaje de entrada:** 9–24V DC via conector barrel PWR485
**Puertos Grove:** HY2.0-4P 4 pines (Orden de pines: GND, VCC, GPIO_B, GPIO_A)

---

## Asignación de Puertos Grove

```
Station-485
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ┌──────┐                                              │
│  │ A1   │ GND │ 5V │ G33(SCL) │ G32(SDA) ──► BH1750  │
│  ├──────┤                                              │
│  │ A2   │ GND │ 5V │ G33(SCL) │ G32(SDA) ──► SHT30   │
│  │      │     │    │  (bus I2C compartido A1+A2)       │
│  ├──────┤                                              │
│  │ B1   │ GND │ 5V │ G35      │ G25      ──► Tierra S1│
│  ├──────┤                                              │
│  │ B2   │ GND │ 5V │ G36(IN)  │ G26      ──► Tierra S2│
│  │      │     │    │  ⚠️ G36 solo entrada              │
│  ├──────┤                                              │
│  │ C1   │ GND │ 5V │ G17      │ G14      ──► Relay 1  │
│  ├──────┤                                              │
│  │ C2   │ GND │ 5V │ G19      │ G17      ──► Relay 2  │
│  └──────┘                                              │
│                                                        │
│  Salida USB-A 5V ──────────────────────► XKC-Y25 VCC  │
│  GPIO (TBD) ───────────────────────────► XKC-Y25 OUT  │
│                                                        │
│  PWR485 ──────────────────────────────► Entrada 12V 2A │
└────────────────────────────────────────────────────────┘
```

> **⚠️ Asignación GPIO de XKC-Y25 pendiente:** Los puertos B1, B2, C1, C2 están totalmente ocupados.
> Opciones: usar un pin GPIO del header expuesto directamente, o remapear si se libera un puerto Grove.
> **Confirmar antes de escribir el firmware.** Actualizar este archivo con el número GPIO final.

---

## Sensor de Luz BH1750 — Puerto A1

```
Cable Grove (A1)          BH1750
─────────────────────────────────────────
Negro  (GND)    ──────►  GND
Rojo   (VCC 5V) ──────►  VCC
Blanco (SCL)    ──────►  SCL   (G33)
Amarillo (SDA)  ──────►  SDA   (G32)
```

- Dirección I2C: **0x23** (pin ADDR flotante o a GND)
- Rango: 1 – 65,535 lx
- Modos de resolución: 1 lx (alta res), 0.5 lx (alta res 2)

---

## SHT30 Exterior — Puerto A2

```
Cable Grove (A2)          SHT30 IOT-TH02 (cables sueltos)
────────────────────────────────────────────────────────
Negro  (GND)    ──────►  Negro  (GND)
Rojo   (VCC 5V) ──────►  Rojo   (VCC)
Blanco (SCL)    ──────►  Amarillo (SCL)  ⚠️ COLORES CRUZADOS
Amarillo (SDA)  ──────►  Blanco (SDA)   ⚠️ COLORES CRUZADOS
```

- Dirección I2C: **0x44** (por defecto, ADDR no elevado)
- Comparte bus I2C con BH1750 (0x23) — sin conflicto de dirección ✅
- Precisión temperatura: ±0.3°C | Precisión humedad: ±2% RH

---

## Sensor de Tierra SucuFer — Puerto B1

```
Cable Grove (B1)          Sensor Earth M5Stack
─────────────────────────────────────────────────
Negro  (GND)    ──────►  GND
Rojo   (VCC 5V) ──────►  VCC
Blanco (G35)    ──────►  AOUT  (salida analógica)
Amarillo (G25)  ──────►  DOUT  (salida digital de umbral)
```

- Lectura analógica en **G25** (ADC1_CH8)
- Rango analógico: 0–4095 (ADC de 12 bits)
- Se requiere calibración: medir valor crudo en suelo seco y suelo saturado

---

## Sensor de Tierra SucuRod — Puerto B2

```
Cable Grove (B2)          Sensor Earth M5Stack
─────────────────────────────────────────────────
Negro  (GND)    ──────►  GND
Rojo   (VCC 5V) ──────►  VCC
Blanco (G36)    ──────►  AOUT  (analógico — G36 es SOLO ENTRADA) ✅
Amarillo (G26)  ──────►  DOUT  (salida digital de umbral)
```

> **⚠️ G36 es solo entrada en ESP32.** Usar únicamente para leer valores analógicos. Nunca configurar como salida.

---

## Relay SucuFer (→ Bomba SucuFer) — Puerto C1

```
Cable Grove (C1)          M5Stack Mini Relay 1
──────────────────────────────────────────────────
Negro  (GND)    ──────►  GND
Rojo   (VCC 5V) ──────►  VCC
Amarillo (G14)  ──────►  IN   (señal — HIGH = relay ON)

Contactos Relay 1          Bomba 1
──────────────────────────────────────────────────
COM             ──────►  +12V (del adaptador DC)
NO              ──────►  Bomba 1 (cable rojo +)
(GND común compartido con GND de la bomba)
```

---

## Relay SucuRod (→ Bomba SucuRod) — Puerto C2

```
Cable Grove (C2)          M5Stack Mini Relay 2
──────────────────────────────────────────────────
Negro  (GND)    ──────►  GND
Rojo   (VCC 5V) ──────►  VCC
Amarillo (G17)  ──────►  IN   (señal — HIGH = relay ON)

Contactos Relay 2          Bomba 2
──────────────────────────────────────────────────
COM             ──────►  +12V (del adaptador DC)
NO              ──────►  Bomba 2 (cable rojo +)
(GND común compartido con GND de la bomba)
```

---

## Sensor de Nivel de Agua XKC-Y25-V

```
Placa Driver DFRobot       Station-485
──────────────────────────────────────────────────
VCC             ──────►  5V (salida USB-A)
GND             ──────►  GND
OUT             ──────►  GPIO (TBD — confirmar puerto)

Sonda del sensor ──────►  Pegar en el exterior del recipiente de agua (plástico)
```

- Salida: HIGH = agua presente en la posición del sensor, LOW = vacío
- Sensibilidad: ajustable con el botón SET en la placa driver (4 niveles)
- Para recipientes plásticos con pared ≤ 3mm

---

## Distribución de Alimentación

```
Adaptador 12V 2A DC (conector barrel 5.5x2.1mm)
        │
        └──► PWR485 (entrada de alimentación Station-485)
                │
                ├── Regula a 5V para puertos Grove (interno)
                ├── Regula a 3.3V para núcleo ESP32 (interno)
                │
                ├── Relay 1 COM ──► Bomba 1 (+)
                └── Relay 2 COM ──► Bomba 2 (+)

Riel GND (común):
    GND adaptador DC ──► GND Station-485 ──► Bomba 1 (-) ──► Bomba 2 (-)

Recomendado: Diodo flyback 1N4007 en cada bomba (cátodo a +12V, ánodo a GND)
Recomendado: Capacitor electrolítico 10µF en los rieles de alimentación cerca de los relays
```

---

## Resumen Bus I2C (Puertos A1 + A2 — compartidos G32/G33)

| Dispositivo | Dirección | Puerto |
|---|---|---|
| BH1750 | 0x23 | A1 |
| SHT30 exterior | 0x44 | A2 |

Sin conflicto de dirección. Ambos responden en los mismos cables SDA/SCL. ✅

---

## Resumen GPIO

| GPIO | Función | Dirección | Puerto |
|---|---|---|---|
| G32 | I2C SDA | E/S | A1 + A2 |
| G33 | I2C SCL | E/S | A1 + A2 |
| G25 | Sensor tierra SucuFer analógico | ENTRADA | B1 |
| G35 | Sensor tierra SucuFer digital | ENTRADA | B1 |
| G26 | Sensor tierra SucuRod analógico | ENTRADA | B2 |
| G36 | Sensor tierra SucuRod digital (solo entrada) | ENTRADA | B2 |
| G14 | Control Relay 1 | SALIDA | C1 |
| G17 | Control Relay 2 | SALIDA | C2 |
| TBD | Señal XKC-Y25 | ENTRADA | — |
