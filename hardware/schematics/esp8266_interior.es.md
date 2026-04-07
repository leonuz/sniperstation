# ESP8266 NodeMCU — Conexiones Unidades Interiores

**Unidades:** 2 unidades idénticas — Habitación Principal + Habitación de los Niños
**Controlador:** ESP8266 NodeMCU v3 CP2102
**Propósito:** Leer temp/humedad interior, mostrar en OLED, publicar en MQTT por WiFi
**Alimentación:** USB 5V (desde cargador USB)

---

## Componentes por Unidad

| Componente | Modelo | Dirección I2C | Interfaz |
|---|---|---|---|
| Sensor temp/humedad | SHT30 IOT-TH02 | 0x44 | I2C |
| Display OLED | SSH1106 1.3" 128x64 | 0x3C | I2C |
| Sensor táctil | TTP223 capacitivo | — | Digital ENTRADA |

Sin conflicto de dirección I2C. ✅

---

## Diagrama de Conexiones

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
│  D2 (GPIO4) ──── pull-up 10KΩ a 3V3 ──► Bus SDA          │
│                                           ├── SHT30 SDA   │
│                                           └── OLED SDA    │
│                                                            │
│  D1 (GPIO5) ──── pull-up 10KΩ a 3V3 ──► Bus SCL          │
│                                           ├── SHT30 SCL   │
│                                           └── OLED SCL    │
│                                                            │
│  D5 (GPIO14) ───────────────────────────► TTP223 OUT      │
│                                                            │
│  USB (micro) ───────────────────────────► Alimentación 5V │
└────────────────────────────────────────────────────────────┘
```

---

## Conexión SHT30

```
ESP8266 / Bus I2C          SHT30 IOT-TH02 (cables sueltos)
──────────────────────────────────────────────────────────
3V3             ──────►  Rojo    (VCC)
GND             ──────►  Negro   (GND)
Bus SDA (D2)    ──────►  Blanco  (SDA)  ⚠️ COLORES CRUZADOS vs estándar Grove
Bus SCL (D1)    ──────►  Amarillo (SCL) ⚠️ COLORES CRUZADOS vs estándar Grove
```

> **⚠️ Mapeo de colores SHT30 IOT-TH02:** Blanco = SDA, Amarillo = SCL.
> Opuesto al estándar Grove HY2.0. Verificar antes de encender.

---

## Conexión OLED SSH1106

```
ESP8266 / Bus I2C          SSH1106 1.3" OLED (4 pines)
──────────────────────────────────────────────────────────
3V3             ──────►  VCC
GND             ──────►  GND
Bus SDA (D2)    ──────►  SDA
Bus SCL (D1)    ──────►  SCL
```

- Librería: **U8g2** (`U8G2_SH1106_128X64_NONAME_F_HW_I2C`)
- Dirección I2C: 0x3C

---

## Conexión Sensor Táctil TTP223

```
ESP8266                   TTP223
──────────────────────────────────────────────────────────
3V3             ──────►  VCC
GND             ──────►  GND
D5 (GPIO14)     ──────►  OUT  (HIGH al tocar)
```

- Configurado como ENTRADA en el firmware
- Activa la pantalla desde el salvapantallas

---

## Resistencias Pull-up I2C

Se requieren pull-ups externos de 10KΩ en SDA y SCL (los pull-ups internos del ESP8266 son insuficientes para I2C confiable con dos dispositivos).

```
3V3 ──── 10KΩ ──── D2 (Bus SDA)
3V3 ──── 10KΩ ──── D1 (Bus SCL)
```

---

## Resumen GPIO

| GPIO | Etiqueta NodeMCU | Función | Dirección |
|---|---|---|---|
| GPIO4 | D2 | I2C SDA — SHT30 + OLED | E/S |
| GPIO5 | D1 | I2C SCL — SHT30 + OLED | E/S |
| GPIO14 | D5 | Señal táctil TTP223 | ENTRADA |

---

## Comportamiento de Pantalla y Lógica de Brillo

| Estado | Disparador | Brillo | Contenido |
|---|---|---|---|
| Salvapantallas | Por defecto / timeout 30s | 10/255 | Logo SniperStation (bitmap) |
| Activo | Toque detectado | 200/255 | Temp + humedad + fecha + hora |
| Modo noche | 00:00 – 06:00 (NTP) | 0 (pantalla apagada) | — |

**Máquina de estados:**
```
SALVAPANTALLAS ──── toque ────► ACTIVO (temporizador 30s inicia)
       ▲                              │
       └──────── timeout / noche ─────┘
```

Brillo controlado via `setContrast()` de U8g2 (mapea al registro SSH1106 0x81, 0–255).

---

## Distribución OLED — Modo Activo (128x64)

```
┌────────────────────────────┐
│ [SS] SniperStation           │  ← logo pequeño 16x16 + título (línea 1)
│ ──────────────────────── │  ← separador
│  25.3°C        72% RH      │  ← datos del sensor (línea 3)
│  Mar 25, 2026  14:23       │  ← fecha + hora NTP (línea 4)
└────────────────────────────┘
```

## Distribución OLED — Modo Salvapantallas (128x64)

```
┌────────────────────────────┐
│                            │
│      [LOGO 48x48]          │  ← bitmap grande centrado
│      SniperStation           │  ← nombre centrado debajo del logo
│                            │
└────────────────────────────┘
```

---

## Fecha / Hora — NTP

No se necesita hardware RTC. Hora sincronizada por WiFi al iniciar y cada hora.

- Servidor: `pool.ntp.org`
- Zona horaria: `America/New_York` (Orlando, FL — UTC-5 / UTC-4 DST)
- Librería: `NTPClient` + `ESP8266WiFi`
- Sin WiFi: mostrar última hora conocida + indicador `(sin sync)`

---

## Topics MQTT

### Unidad Habitación Principal (`ROOM_ID = "master"`)

| Topic | Valor | Frecuencia |
|---|---|---|
| `sniperstation/interior/master/temperatura` | float (°C) | Cada 60s |
| `sniperstation/interior/master/humedad` | float (%) | Cada 60s |

### Unidad Habitación de los Niños (`ROOM_ID = "kids"`)

| Topic | Valor | Frecuencia |
|---|---|---|
| `sniperstation/interior/kids/temperatura` | float (°C) | Cada 60s |
| `sniperstation/interior/kids/humedad` | float (%) | Cada 60s |

El firmware es idéntico para ambas unidades. Solo difiere el `ROOM_ID`.

---

## Enclosure Físico

Enclosure impreso en 3D a medida (mismo diseño para ambas unidades). Contiene:
- ESP8266 NodeMCU (49 x 26mm)
- OLED 1.3" SSH1106 — recorte/ventana en la cara frontal
- Sensor táctil TTP223 — cara frontal, accesible con el dedo
- SHT30 — parte superior del enclosure, carcasa expuesta al aire del cuarto

Ver `hardware/enclosure/indoor_unit_design.md` para especificaciones completas.

---

## Nota sobre Alimentación

- Alimentación por micro-USB (cargador USB 5V)
- SHT30 y OLED alimentados solo desde el pin 3V3
- **No** alimentar SHT30 desde 5V en esta unidad
