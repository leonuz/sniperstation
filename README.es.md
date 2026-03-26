# SniperStation

Sistema automático de riego y estación meteorológica para dos materos de suculentas ubicados en exterior, Orlando, Florida.

**SucuFer** — Suculenta de Fernanda, sembrada el 22 de abril de 2024 (10 años)
**SucuRod** — Suculenta de Rodrigo, sembrada el 22 de abril de 2024 (6 años)

Monitorea condiciones ambientales (temperatura, humedad, luz solar, humedad del suelo) y riega automáticamente según los sensores. Incluye pantalla táctil a color (CYD), dashboard web (Grafana), alertas por Telegram e historial completo de datos.

---

## Arquitectura del Sistema

```
[AFUERA]                                    [ADENTRO]
Station-485 (controlador principal)         CYD ESP32-2432S028 x2
├── Sensor luz BH1750      → Puerto A1      ├── Master Bedroom (SHT30 en CN1)
├── SHT30 exterior         → Puerto A2      └── Kids Bedroom   (SHT30 en CN1)
├── Sensor suelo SucuFer   → Puerto B1               │
├── Sensor suelo SucuRod   → Puerto B2               │
├── Relay → Bomba SucuFer  → Puerto C1               │
├── Relay → Bomba SucuRod  → Puerto C2               │
└── Sensor nivel XKC-Y25   → Puerto B/C              │
          │                                          │
          └──────── WiFi → MQTT ────────────────────┘
                          │
                   [Proxmox LXC]
                   ├── Mosquitto (broker MQTT)
                   ├── InfluxDB 2.x (base de datos de series de tiempo)
                   ├── Grafana (dashboard web / celular)
                   └── Bot Telegram (alertas push)
```

---

## Las Plantas

| Planta | Dueño | Edad | Sembrada |
|---|---|---|---|
| SucuFer | Fernanda (10 años) | ~2 años | 22 de abril, 2024 |
| SucuRod | Rodrigo (6 años) | ~2 años | 22 de abril, 2024 |

La vista de detalle del CYD para cada planta muestra la foto del dueño con su suculenta como fondo, junto con la fecha de siembra y la humedad actual del suelo.

---

## Requisitos de Hardware

| Componente | Modelo | Estado |
|---|---|---|
| Controlador principal | M5Stack Station-485 | Disponible |
| Sensor de luz | DLight BH1750 | Disponible |
| Temp/humedad x2 | SHT30 IOT-TH02 | Comprado |
| Cable Grove↔Dupont | HY2.0-4P a 2.54mm | Comprado |
| Bombas peristálticas x2 | DC 12-24V, 80mA | Comprado — llega a finales de abril |
| Sensor nivel agua | XKC-Y25-V + driver DFRobot | Comprado |
| Sensores de suelo x2 | M5Stack Earth Sensor | Comprado |
| Módulos relay x2 | M5Stack Mini 3A Relay | Comprado |
| Pantalla interior x2 | CYD ESP32-2432S028 | Comprado — llega el sábado |
| Adaptador DC | 12V 2A, conector 5.5mm | **Pendiente comprar** |
| Caja exterior | IP65+, ventilada | **Pendiente comprar** |
| Carcasa interior x2 | Impresión 3D personalizada | **Pendiente diseño** |

BOM completo → [hardware/BOM.es.md](hardware/BOM.es.md)

---

## Stack de Software

| Servicio | Puerto | Función |
|---|---|---|
| Mosquitto | 1883 | Broker MQTT |
| InfluxDB 2.x | 8086 | Base de datos de series de tiempo |
| Grafana | 3000 | Dashboard web / celular |
| Bot Telegram | — | Notificaciones push |

Todos los servicios corren en un único contenedor LXC de Proxmox.

---

## Estructura del Repositorio

```
sniperstation/
├── hardware/
│   ├── BOM.md / BOM.es.md                # Lista de materiales
│   ├── schematics/                       # Diagramas de conexión
│   ├── datasheets/                       # Referencias de datasheets
│   └── enclosure/                        # Especificaciones + OpenSCAD
├── firmware/
│   ├── station485/                       # Arduino IDE — ESP32 (Station-485)
│   └── cyd_indoor/                       # Arduino IDE — CYD ESP32 (interior x2)
├── software/
│   ├── mosquitto/                        # Config del broker
│   ├── influxdb/                         # Setup de base de datos
│   ├── grafana/                          # JSON exports del dashboard
│   └── telegram_bot/                     # Bot de alertas
├── assets/
│   └── photos/                           # Fotos de SucuFer y SucuRod (fondos CYD)
├── README.md / README.es.md
├── ROADMAP.md / ROADMAP.es.md
├── TODO.md / TODO.es.md
└── CHANGELOG.md / CHANGELOG.es.md
```

---

## Lógica de Riego

```
Cada 6 horas (via RTC BM8563):
  PARA cada planta (SucuFer, SucuRod):
    SI humedad_suelo < umbral_seco:
      SI humedad_aire < 85% (no está lloviendo):
        SI hay_agua == TRUE:
          activar_bomba(planta, 20 segundos)   // ~33ml a 100ml/min
          esperar 30 minutos
          leer humedad_suelo nuevamente
          SI sigue_seco: enviar alerta Telegram
        SINO:
          enviar alerta Telegram "Recipiente vacío"
```

Flujo de referencia: ~100 ml/min a 12V → 20 segundos = ~33 ml

---

## Umbrales de Humedad del Suelo (calibrar con los materos reales)

| Estado | Rango | Acción |
|---|---|---|
| Seco | < 30% | Regar |
| Húmedo | 30–60% | Sin acción |
| Mojado | > 60% | Alerta — riesgo de exceso |

---

## Alertas Telegram

- Riego ejecutado (SucuFer / SucuRod + ml entregados)
- Recipiente de agua vacío
- Suelo muy seco por más de 24h
- Temperatura exterior > 38°C (calor extremo en Orlando)
- Sensor desconectado / error de lectura

---

## UI Pantalla Táctil CYD

| Vista | Contenido |
|---|---|
| Screensaver | Logo animado (cactus) + resumen compacto de temperaturas |
| Vista principal | Todos los sensores: exterior + master + kids + SucuFer + SucuRod |
| Detalle SucuFer | Foto de Fernanda de fondo + humedad suelo + último riego + edad de la planta |
| Detalle SucuRod | Foto de Rodrigo de fondo + humedad suelo + último riego + edad de la planta |

El idioma se selecciona por dispositivo (EN/ES) y se guarda en flash.

---

## Notas Importantes

### Calor en Orlando
Temperatura máxima del Station-485: **60°C**. En verano al sol directo puede superarse fácilmente.
**Obligatorio:** instalar en sombra + ventilación pasiva o activa.

### Restricción GPIO — Puerto B2
Usa GPIO G36 del ESP32, que **no puede configurarse como OUTPUT**.
El sensor de SucuRod es solo lectura analógica — correcto para este uso.
**Nunca conectar un relay al Puerto B.**

### Bus I2C compartido (Puertos A1/A2)
BH1750 (dirección 0x23) y SHT30 (dirección 0x44) comparten el mismo bus I2C en G32/G33.
Direcciones diferentes — sin conflicto.

---

## Licencia

Hardware Abierto — CERN OHL v2 Permissive
Software — MIT
