# Unidad Interior — Especificación de Enclosure

**Unidades:** 2 (idénticas — Habitación Principal + Habitación de los Niños)
**Material:** PLA (estándar, suficiente para uso interior)
**Montaje:** Montaje en pared
**Color de impresión:** Blanco o gris claro recomendado (combina con la carcasa del SHT30)

---

## Componentes a Alojar

| Componente | Dimensiones PCB | Notas |
|---|---|---|
| ESP8266 NodeMCU CP2102 | 49 x 26 x 12mm | Micro-USB en el extremo corto (inferior) |
| OLED SSH1106 1.3" | 38.5 x 23 x 4mm | Visible a través de la ventana frontal |
| Sensor táctil TTP223 | 24 x 14 x 3mm | Accesible a través del orificio frontal |
| SHT30 (con carcasa) | ~35 x 20 x 12mm | Se monta en la parte superior, expuesto al aire |

---

## Dimensiones Externas

```
Ancho:  70mm
Alto:   90mm  (sin contar el SHT30 en la parte superior)
Fondo:  36mm
Pared:   2mm
```

---

## Distribución de la Cara Frontal

```
         70mm
┌─────────────────────┐  ─┐
│    ┌───────────┐    │   │  14mm margen superior
│    │  [OLED]   │    │   │  Ventana OLED: 35 x 24mm, centrada
│    │  35x24mm  │    │   │  (centrada horizontalmente)
│    └───────────┘    │   │
│                     │   │  90mm alto total
│    ───────────────  │   │  línea separadora (grabada, opcional)
│                     │   │
│       [ ◉ ]         │   │  círculo táctil: 16mm diámetro
│                     │   │
└──────────┬──────────┘  ─┘
           │ ranura USB
     (10mm A x 8mm H)
```

**Ventana OLED:** Recorte rectangular 35 x 24mm, 2mm desde la pared frontal → efecto vidrio
**Área táctil:** Orificio circular de 16mm, centrado horizontalmente, 58mm desde arriba
**Ranura USB:** 10mm A x 8mm H, centrada en el borde inferior — cable sale hacia abajo

---

## Distribución de la Cara Superior

```
         70mm
┌─────────────────────┐
│   ┌─────────────┐   │  Ranura SHT30: 37 x 22mm agujero rectangular
│   │  [SHT30]    │   │  SHT30 queda a nivel con la superficie superior
│   │  entra aquí │   │  ranuras de ventilación apuntan hacia arriba
│   └─────────────┘   │
└─────────────────────┘
```

La carcasa del SHT30 entra desde arriba y se sostiene por fricción o un pequeño tope (0.5mm).
Los cables pasan por el interior del enclosure hasta el NodeMCU.

---

## Distribución de la Cara Trasera

```
         70mm
┌─────────────────────┐
│                     │
│   ●             ●   │  2 agujeros de montaje, 4mm diámetro
│  (15mm desde     )  │  50mm entre centros (horizontal)
│  cada lado)      )  │  40mm desde arriba
│                     │
│                     │
│                     │
└─────────────────────┘
```

**Agujeros de montaje:** 4mm diámetro, avellanado, para tornillos M3 en tacos de pared.
**Alternativa:** Ranuras de ojo de cerradura (colgar en tornillos ya en la pared, sin herramientas para desmontar).

---

## Distribución Interna

```
Vista lateral (sección transversal):
       Frente                Fondo
         │                   │
         │  [OLED]           │
         │   ──────────────  │
         │                   │
         │  [PCB NodeMCU]    │
         │  ─────────────    │   ← NodeMCU sobre separadores de 3mm
         │                   │
         └───────────────────┘
                parte inf
                  │
               ranura USB
```

**Separadores NodeMCU:** 3mm de alto, 4 postes (uno en cada agujero de montaje del PCB NodeMCU).
**Montaje OLED:** Pequeña repisa o 4 postes en el frente, 2mm detrás de la pared frontal.
**TTP223:** Pegado por detrás del agujero táctil sobre una pequeña plataforma.
**Ruteo de cables:** Canal de 5mm en la parte inferior interna para cables I2C + táctil.

---

## Tolerancias

| Característica | Tolerancia |
|---|---|
| Ventana OLED | +0.3mm en todos los lados |
| Ranura SHT30 | +0.4mm en todos los lados (ligero ajuste por fricción) |
| Ranura USB | +1mm A, +0.5mm H |
| Agujero táctil | +0.2mm radio |
| Agujeros de montaje | exacto 4.2mm (holgura M3) |

---

## Orden de Ensamblaje

1. Insertar NodeMCU sobre los separadores
2. Conectar todos los cables (SDA/SCL/táctil/alimentación) antes de cerrar
3. Presionar OLED en la repisa de la ventana frontal desde adentro
4. Insertar TTP223 en la plataforma táctil desde adentro
5. Rutear cables del SHT30 por el canal interno
6. Colocar la carcasa del SHT30 en la ranura superior desde arriba
7. Cerrar la tapa (encaje o 2x tornillos M2 en los lados)

---

## Modelo 3D — Herramientas

Software recomendado para crear el STL:

| Herramienta | Costo | Dificultad | Notas |
|---|---|---|---|
| **TinkerCAD** | Gratis (navegador) | Fácil | Ideal para esta caja — arrastrar y soltar |
| **OpenSCAD** | Gratis (escritorio) | Medio | Basado en código, paramétrico — Claude puede escribirlo |
| **FreeCAD** | Gratis (escritorio) | Difícil | CAD completo, excesivo para una caja simple |
| **Fusion 360** | Gratis (personal) | Medio | Profesional, bueno para formas complejas |

**Recomendación:** OpenSCAD — Claude Code puede escribir el archivo `.scad` directamente desde esta especificación.

---

## Configuración de Impresión (recomendada)

| Parámetro | Valor |
|---|---|
| Altura de capa | 0.2mm |
| Relleno | 20% |
| Paredes | 3 perímetros |
| Soporte | No necesario (diseño sin voladizos) |
| Material | PLA |
| Peso estimado | ~30–40g por unidad |
| Tiempo estimado | ~2–3h por unidad |

---

## Servicios de Impresión (Orlando, FL)

| Servicio | Tipo | Costo Est. | Tiempo |
|---|---|---|---|
| **Orange County Library** | Local, gratis/barato | $1–3 | Misma semana (reservar turno) |
| **Treatstock.com** | Red local USA | $8–15 por unidad | 3–7 días |
| **JLCPCB.com** | En línea (China) | $3–5 por unidad + envío | 10–15 días |
| **Craftcloud3d.com** | Comparador de precios | variable | variable |

**Recomendado para primera iteración:** Orange County Library o Treatstock (entrega rápida para probar ajuste).
**Para versión final:** JLCPCB si el diseño está confirmado (más barato por unidad).
