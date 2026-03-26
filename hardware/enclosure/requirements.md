# Enclosure Requirements — SniperStation Outdoor Unit

**Environment:** Outdoors, Orlando FL — full sun exposure possible, rain, humidity, temperature extremes

---

## Protection Requirements

| Parameter | Minimum | Notes |
|---|---|---|
| IP rating | IP65 | Dust-tight + protected against water jets |
| Operating temp (ambient) | 0–55°C | M5Stack Station-485 max internal is 60°C |
| UV resistance | Yes | Plastic degrades quickly in Florida sun |
| Mounting | Wall or pole mount | Near planters, avoid direct sun on enclosure |

---

## Internal Dimensions (minimum)

| Dimension | Minimum |
|---|---|
| Length | 150mm |
| Width | 120mm |
| Height | 80mm |

**Rationale:** Station-485 footprint is 54 x 54mm. Relay modules x2 add ~30mm. Wiring and connectors need ~40mm clearance.

---

## Ventilation

The Station-485 ESP32 generates heat. In a sealed enclosure under Florida summer sun, internal temperatures can exceed 60°C (controller max rating).

**Mandatory:** At least one of these ventilation strategies:

1. **Passive ventilation:** Enclosure with louvers/slots on bottom and top (chimney effect). Slots must be baffled to prevent water ingress (IP65 compatible louvers).
2. **Active ventilation:** Small 5V fan (available in SunFounder kit) with filtered intake. Fan controlled by a thermistor — activate above 45°C internal.

**Recommended:** Install in **permanent shade** (north-facing wall, under eave, or in a shaded spot). This is the single most effective thermal management measure.

---

## Cable Entry Points

Required penetrations through enclosure walls:

| Entry | Cable/Pipe | Gland Type |
|---|---|---|
| Power | 12V DC barrel jack cable | PG7 cable gland |
| Grove A1 | BH1750 sensor | PG7 cable gland |
| Grove A2 | SHT30 outdoor | PG7 cable gland |
| Grove B1 | Earth Sensor 1 | PG7 cable gland |
| Grove B2 | Earth Sensor 2 | PG7 cable gland |
| Relay C1 | Pump 1 cable | PG9 cable gland |
| Relay C2 | Pump 2 cable | PG9 cable gland |
| XKC-Y25 | Water level sensor | PG7 cable gland |
| USB-A | XKC-Y25 VCC (5V) | Internal routing if possible |

**Recommended:** Waterproof cable glands on all entries. Seal with silicone after routing.

---

## Mounting Considerations

- Mount **away from direct sun** — north or east-facing, under eave preferred
- Mount **above ground level** — minimum 30cm to avoid splash water
- Ensure drain holes or weep holes at the bottom of the enclosure to prevent water accumulation if moisture enters
- Consider cable routing — Grove cables max length ~50cm, place enclosure **close to planters**

---

## Heat Management Notes

Measured worst-case scenario for Orlando, FL:
- Ambient outdoor temp: 38°C (summer peak)
- Direct sun on metal enclosure: surface temp can reach 70–80°C
- Inside a closed enclosure in direct sun: up to 90°C possible

**Operating envelope of components:**

| Component | Max Rated Temp |
|---|---|
| Station-485 (ESP32) | 60°C |
| SHT30 | 125°C |
| BH1750 | 85°C |
| Earth Sensors | 85°C |
| M5Stack Relay | 85°C |

**Action required:** Place in shade. If shade is not possible, add forced ventilation fan.

---

## Recommended Products (Amazon search terms)

- "IP65 weatherproof enclosure 150x120x80mm"
- "waterproof junction box with ventilation"
- "PG7 cable gland waterproof" (pack of 10)
- "PG9 cable gland waterproof" (pack of 10)
