# Distribución de Alimentación Exterior — SniperStation

**Fuente de alimentación:** Adaptador DC 12V 2A (conector barrel 5.5×2.1mm)
**Carga total:** ≤400mA @ 12V peor caso (margen de seguridad 5×)

---

## Árbol de Alimentación

```
┌─────────────────────────────────────────────────────────────────┐
│           ADAPTADOR DC 12V 2A (barrel 5.5×2.1mm)               │
│                         │                                        │
│               ┌─────────┘                                        │
│               │                                                   │
│               ▼                                                   │
│      ┌─────────────────┐   ┌─────────────────┐                  │
│      │  Wago 221-415   │   │  Wago 221-415   │                  │
│      │   RIEL +12V     │   │    RIEL GND     │                  │
│      │                 │   │                 │                  │
│      │ ENT:  Adapt. +  │   │ ENT:  Adapt. -  │                  │
│      │ SAL1: Station ──┤   ├── Station-485 - │                  │
│      │ SAL2: Relay1 COM┤   ├── Bomba 1 (-)  │                  │
│      │ SAL3: Relay2 COM┤   ├── Bomba 2 (-)  │                  │
│      │ SAL4: Buck ENT +┤   ├── Buck ENT -   │                  │
│      └─────────────────┘   └─────────────────┘                  │
│               │                                                   │
│       ┌───────┼───────────────────────────┐                      │
│       │       │                           │                      │
│       ▼       ▼                           ▼                      │
│  ┌─────────────────┐            ┌──────────────────┐            │
│  │  Station-485    │            │ Convertidor Buck  │            │
│  │  9–24V PWR485   │            │ 12V→5V           │            │
│  │                 │            │ (LM2596/MP1584)  │            │
│  │  5V interno ────┼──► Grove   │  5V salida ──────┼──► TimerCam X (USB-C)  │
│  │                 │    ├── BH1750  (~1mA)          │    activo: ~180mA      │
│  │                 │    ├── SHT30   (~1mA)          │    sleep:  ~0.001mA    │
│  │                 │    ├── Tierra×2 (~5mA c/u)    └──────────────────┘    │
│  │                 │    └── Relays  (~70mA activo)                           │
│  │  USB-A 5V ──────┼──► XKC-Y25 + driver (~10mA)                           │
│  │                 │                                                          │
│  │  Relay 1 NO ────┼──► Bomba SucuFer + (~80mA)                            │
│  │  Relay 2 NO ────┼──► Bomba SucuRod + (~80mA, nunca simultáneas)         │
│  └─────────────────┘                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Por Qué un Convertidor Buck Separado para TimerCam X

La salida USB-A del Station-485 ya está usada por la placa driver XKC-Y25.
Agregar la TimerCam X al mismo puerto USB-A puede generar inestabilidad cuando la cámara
se activa y consume ~180mA.

**Solución:** Un convertidor mini buck 12V→5V dedicado para la TimerCam X.

**Parte recomendada:** Módulo mini DC-DC step-down (LM2596 o MP1584)
- Entrada: 12V
- Salida: 5V fijo
- Corriente máxima: 2A (muy por encima de los 180mA pico de la TimerCam)
- Costo: ~$1–3 en Amazon
- Tamaño: ~23×17mm — cabe fácilmente en el enclosure IP65

---

## Presupuesto de Potencia (Exterior)

| Componente | Voltaje | Corriente (reposo) | Corriente (pico) | Notas |
|---|---|---|---|---|
| Station-485 | 12V | 120mA | 200mA | WiFi activo = 161mA |
| Bomba SucuFer | 12V | 0 | 100mA | via Relay 1 — nunca simultánea con Bomba 2 |
| Bomba SucuRod | 12V | 0 | 100mA | via Relay 2 — nunca simultánea con Bomba 1 |
| BH1750 | 5V (interno) | 0.2mA | 0.2mA | despreciable |
| SHT30 exterior | 5V (interno) | 0.8mA | 0.8mA | despreciable |
| Sensor Tierra ×2 | 5V (interno) | 5mA c/u | 5mA c/u | |
| XKC-Y25 + driver | 5V USB-A | 10mA | 10mA | USB-A del Station-485 |
| Relay ×2 | 5V (interno) | ~0mA | 70mA c/u | solo cuando bomba activa |
| TimerCam X | 5V (buck) | 0.001mA | 180mA | sleep 2µA, activo ~180mA |
| **TOTAL PEOR CASO** | **12V** | | **~380mA** | Station-485 WiFi + 1 bomba activa |

**Capacidad del adaptador:** 12V 2A = 2000mA
**Consumo peor caso:** ~380mA
**Margen de seguridad: 5×** ✅

> Peor caso: Station-485 WiFi activo (161mA) + 1 bomba (80mA) + TimerCam activa (180mA) ≈ **421mA**
> Aún dentro de la capacidad de 2A. ✅

---

## Componentes de Protección

| Componente | Valor | Ubicación | Propósito |
|---|---|---|---|
| Diodo 1N4007 | — | En bornes de cada bomba | Protección flyback (carga inductiva) |
| Capacitor electrolítico | 10µF | Cerca de salidas de relay | Filtro de ruido de alimentación |

---

## Notas de Cableado

- Todas las conexiones exteriores dentro del enclosure IP65
- Se requieren prensaestopas para: entrada 12V, cables Grove a sensores, tuberías, alimentación TimerCam X
- La TimerCam X se monta en la pared del enclosure con ventana de acrílico/vidrio para el lente
- Cable USB-C del convertidor buck a TimerCam X — mantener corto (≤30cm dentro del enclosure)
