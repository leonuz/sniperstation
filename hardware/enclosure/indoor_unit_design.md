# Indoor Unit Enclosure — Design Specification

**Units:** 2 (identical — Master Bedroom + Kids Bedroom)
**Material:** PLA (standard, sufficient for indoor use)
**Mount:** Wall mount
**Print color:** White or light gray recommended (matches SHT30 casing)

---

## Components to Fit

| Component | PCB Dimensions | Notes |
|---|---|---|
| ESP8266 NodeMCU CP2102 | 49 x 26 x 12mm | Micro-USB on short end (bottom) |
| OLED SSH1106 1.3" | 38.5 x 23 x 4mm | Visible through front window |
| TTP223 touch sensor | 24 x 14 x 3mm | Accessible through front hole |
| SHT30 (cased) | ~35 x 20 x 12mm | Mounts on top, exposed to room air |

---

## External Dimensions

```
Width:  70mm
Height: 90mm  (not counting SHT30 on top)
Depth:  36mm
Wall:    2mm
```

---

## Front Face Layout

```
         70mm
┌─────────────────────┐  ─┐
│    ┌───────────┐    │   │  14mm top margin
│    │  [OLED]   │    │   │  OLED window: 35 x 24mm, centered
│    │  35x24mm  │    │   │  (centered horizontally)
│    └───────────┘    │   │
│                     │   │  90mm total height
│    ───────────────  │   │  separator line (engraved, optional)
│                     │   │
│       [ ◉ ]         │   │  touch circle: 16mm diameter
│                     │   │
└──────────┬──────────┘  ─┘
           │ USB slot
     (10mm W x 8mm H)
```

**OLED window:** 35 x 24mm rectangular cutout, 2mm from front wall → glass effect
**Touch area:** 16mm circular hole, centered horizontally, 58mm from top
**USB slot:** 10mm W x 8mm H, centered at bottom edge — cable exits downward

---

## Top Face Layout

```
         70mm
┌─────────────────────┐
│   ┌─────────────┐   │  SHT30 slot: 37 x 22mm rectangular hole
│   │  [SHT30]    │   │  SHT30 sits flush with top surface
│   │  fits here  │   │  ventilation slots face up (room air)
│   └─────────────┘   │
└─────────────────────┘
```

The SHT30 casing drops in from the top and is held by friction or a small lip (0.5mm).
Wires pass through inside the enclosure to the NodeMCU.

---

## Back Face Layout

```
         70mm
┌─────────────────────┐
│                     │
│   ●             ●   │  2x mounting holes, 4mm diameter
│  (15mm from      )  │  50mm center-to-center (horizontal)
│  (each side)     )  │  40mm from top
│                     │
│                     │
│                     │
└─────────────────────┘
```

**Mounting holes:** 4mm diameter, countersunk, for M3 screws into wall anchors.
**Alternative:** Keyhole slots (hang on screws already in wall, no tools needed to remove).

---

## Internal Layout

```
Side view (cross section):
       Front                Back
         │                   │
         │  [OLED]           │
         │   ──────────────  │
         │                   │
         │  [NodeMCU PCB]    │
         │  ─────────────    │   ← NodeMCU sits on 3mm standoffs
         │                   │
         └───────────────────┘
                bottom
                  │
               USB slot
```

**NodeMCU standoffs:** 3mm tall, 4 posts (one at each mounting hole of NodeMCU PCB).
**OLED mount:** Small shelf or 4 posts at front, 2mm behind front wall.
**TTP223:** Glued to back of touch hole with a small platform.
**Wire routing:** 5mm channel along bottom inside for I2C + touch wires.

---

## Tolerances

| Feature | Tolerance |
|---|---|
| OLED window | +0.3mm on all sides |
| SHT30 slot | +0.4mm on all sides (slight friction fit) |
| USB slot | +1mm W, +0.5mm H |
| Touch hole | +0.2mm radius |
| Mounting holes | exact 4.2mm (M3 clearance) |

---

## Assembly Order

1. Insert NodeMCU onto standoffs
2. Connect all wires (SDA/SCL/touch/power) before closing
3. Press OLED into front window shelf from inside
4. Insert TTP223 into touch platform from inside
5. Route SHT30 wires through internal channel
6. Drop SHT30 casing into top slot from above
7. Close lid (snap fit or 2x M2 screws on sides)

---

## 3D Model — Tools

Recommended software to create the STL:

| Tool | Cost | Difficulty | Notes |
|---|---|---|---|
| **TinkerCAD** | Free (browser) | Easy | Ideal for this box — drag and drop |
| **OpenSCAD** | Free (desktop) | Medium | Code-based, parametric — Claude can write it |
| **FreeCAD** | Free (desktop) | Hard | Full CAD, overkill for a simple box |
| **Fusion 360** | Free (personal) | Medium | Professional, good for complex shapes |

**Recommendation:** OpenSCAD — Claude Code can write the `.scad` file directly from this spec.

---

## Print Settings (recommended)

| Parameter | Value |
|---|---|
| Layer height | 0.2mm |
| Infill | 20% |
| Walls | 3 perimeters |
| Support | None needed (design to avoid overhangs) |
| Material | PLA |
| Estimated weight | ~30–40g per unit |
| Estimated print time | ~2–3h per unit |

---

## Print Services (Orlando, FL)

| Service | Type | Est. Cost | Turnaround |
|---|---|---|---|
| **Orange County Library** | Local, free/cheap | $1–3 | Same week (book slot) |
| **Treatstock.com** | Local network USA | $8–15 per unit | 3–7 days |
| **JLCPCB.com** | Online (China) | $3–5 per unit + shipping | 10–15 days |
| **Craftcloud3d.com** | Price comparison | varies | varies |

**Recommended for first iteration:** Orange County Library or Treatstock (fast turnaround to test fit).
**For final version:** JLCPCB if the design is confirmed (cheapest per unit).
