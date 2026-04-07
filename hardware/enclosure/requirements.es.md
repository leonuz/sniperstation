# Requisitos de Enclosure — Unidad Exterior SniperStation

**Entorno:** Exterior, Orlando FL — posible exposición total al sol, lluvia, humedad, extremos de temperatura

---

## Requisitos de Protección

| Parámetro | Mínimo | Notas |
|---|---|---|
| Clasificación IP | IP65 | A prueba de polvo + protegido contra chorros de agua |
| Temp. de operación (ambiente) | 0–55°C | Temp máxima interna M5Stack Station-485 es 60°C |
| Resistencia UV | Sí | El plástico se degrada rápidamente bajo el sol de Florida |
| Montaje | Mural o en poste | Cerca de los materos, evitar sol directo en el enclosure |

---

## Dimensiones Internas (mínimas)

| Dimensión | Mínimo |
|---|---|
| Largo | 150mm |
| Ancho | 120mm |
| Alto | 80mm |

**Justificación:** La huella del Station-485 es 54 x 54mm. Los módulos de relay x2 agregan ~30mm. El cableado y conectores necesitan ~40mm de espacio.

---

## Ventilación

El ESP32 del Station-485 genera calor. En un enclosure sellado bajo el sol de verano en Florida, la temperatura interna puede superar los 60°C (temperatura máxima del controlador).

**Obligatorio:** Al menos una de estas estrategias de ventilación:

1. **Ventilación pasiva:** Enclosure con persianas/ranuras en la parte inferior y superior (efecto chimenea). Las ranuras deben tener baffles para evitar ingreso de agua (persianas compatibles IP65).
2. **Ventilación activa:** Ventilador pequeño de 5V (disponible en el kit SunFounder) con toma de aire filtrada. Ventilador controlado por termistor — activar por encima de 45°C interno.

**Recomendado:** Instalar en **sombra permanente** (pared norte, bajo alero, o en lugar sombreado). Esta es la medida de gestión térmica más efectiva.

---

## Puntos de Entrada de Cables

Penetraciones requeridas en las paredes del enclosure:

| Entrada | Cable/Tubería | Tipo de Prensaestopa |
|---|---|---|
| Alimentación | Cable barrel jack 12V DC | Prensaestopa PG7 |
| Grove A1 | Sensor BH1750 | Prensaestopa PG7 |
| Grove A2 | SHT30 exterior | Prensaestopa PG7 |
| Grove B1 | Sensor de tierra 1 | Prensaestopa PG7 |
| Grove B2 | Sensor de tierra 2 | Prensaestopa PG7 |
| Relay C1 | Cable bomba 1 | Prensaestopa PG9 |
| Relay C2 | Cable bomba 2 | Prensaestopa PG9 |
| XKC-Y25 | Sensor nivel de agua | Prensaestopa PG7 |
| USB-A | VCC XKC-Y25 (5V) | Ruteo interno si es posible |

**Recomendado:** Prensaestopas impermeables en todas las entradas. Sellar con silicona después de rutear.

---

## Consideraciones de Montaje

- Montar **lejos del sol directo** — preferible norte o este, bajo alero
- Montar **sobre el nivel del suelo** — mínimo 30cm para evitar salpicaduras
- Asegurarse de tener agujeros de drenaje en la parte inferior del enclosure para evitar acumulación de agua si entra humedad
- Considerar el ruteo de cables — los cables Grove tienen máximo ~50cm, colocar el enclosure **cerca de los materos**

---

## Notas sobre Gestión Térmica

Peor caso medido para Orlando, FL:
- Temperatura ambiente exterior: 38°C (pico de verano)
- Sol directo en enclosure metálico: la superficie puede llegar a 70–80°C
- Dentro de un enclosure cerrado bajo sol directo: hasta 90°C posible

**Rango de operación de los componentes:**

| Componente | Temp. Máxima Nominal |
|---|---|
| Station-485 (ESP32) | 60°C |
| SHT30 | 125°C |
| BH1750 | 85°C |
| Sensores de tierra | 85°C |
| Relay M5Stack | 85°C |

**Acción requerida:** Colocar en sombra. Si la sombra no es posible, agregar ventilador forzado.

---

## Productos Recomendados (términos de búsqueda en Amazon)

- "IP65 weatherproof enclosure 150x120x80mm"
- "waterproof junction box with ventilation"
- "PG7 cable gland waterproof" (paquete de 10)
- "PG9 cable gland waterproof" (paquete de 10)
