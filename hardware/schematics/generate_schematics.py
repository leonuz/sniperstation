"""
SucuStation — Schematic generator
Generates electrical schematics as SVG and PDF using schemdraw.

Usage:
    python3 generate_schematics.py

Output files are written to ./generated/
"""

import schemdraw
import schemdraw.elements as elm
import matplotlib
matplotlib.use('Agg')  # headless backend, no display required
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'generated')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save(drawing, name):
    """Save drawing as SVG and PDF."""
    svg_path = os.path.join(OUTPUT_DIR, f'{name}.svg')
    pdf_path = os.path.join(OUTPUT_DIR, f'{name}.pdf')
    drawing.save(svg_path)
    drawing.save(pdf_path)
    print(f'  saved: {svg_path}')
    print(f'  saved: {pdf_path}')


# ---------------------------------------------------------------------------
# 1. Power distribution — 12V adapter → Station-485 + Pumps
# ---------------------------------------------------------------------------
def schematic_power():
    print('Generating: power_distribution')
    with schemdraw.Drawing(fontsize=11) as d:
        d.config(inches_per_unit=0.5)

        # 12V source
        V1 = d.add(elm.SourceV().up().label('12V\n2A', loc='left'))
        d.add(elm.Line().right(2))

        # Split to Station-485
        d.add(elm.Dot())
        top_rail = d.add(elm.Line().right(3))

        # Station-485 represented as a box
        d.add(elm.Resistor().right().label('Station-485\n(PWR485)\n~161mA', loc='top'))
        d.add(elm.Line().down())
        d.add(elm.Line().left(4))

        # Back to junction for relay branch
        d.add(elm.Dot())

        # Relay 1 → Pump 1 branch
        d.add(elm.Line().right(1))
        rel1 = d.add(elm.Switch().right().label('Relay 1', loc='top'))
        d.add(elm.Motor().right().label('Pump 1\n80mA', loc='top'))
        d.add(elm.Line().down(0.5))
        p1_gnd = d.add(elm.Line().left(3))

        # Diode flyback across pump 1
        d.add(elm.Diode().left().label('1N4007', loc='top').reverse())

        # Relay 2 → Pump 2 branch
        d.add(elm.Line().down(1.5).at(rel1.start))
        d.add(elm.Switch().right().label('Relay 2', loc='top'))
        d.add(elm.Motor().right().label('Pump 2\n80mA', loc='top'))
        d.add(elm.Line().down(0.5))
        d.add(elm.Line().left(3))
        d.add(elm.Diode().left().label('1N4007', loc='top').reverse())

        # GND symbol
        d.add(elm.Ground().at(V1.start))

        d.add(elm.Label().at(d.here).label('SucuStation — Power Distribution\n12V 2A, worst case ~341mA', loc='right'))

    save(d, '01_power_distribution')


# ---------------------------------------------------------------------------
# 2. I2C bus — BH1750 + SHT30 on shared bus (Ports A1 + A2)
# ---------------------------------------------------------------------------
def schematic_i2c():
    print('Generating: i2c_bus')
    with schemdraw.Drawing(fontsize=11) as d:
        d.config(inches_per_unit=0.5)

        # ESP32 (Station-485) SDA/SCL lines
        d.add(elm.Line().right(1).label('ESP32\nG32 (SDA)', loc='left'))
        sda_start = d.add(elm.Dot())
        d.add(elm.Line().right(5))

        # Pull-up SDA
        d.add(elm.Dot())
        pu_sda = d.add(elm.Resistor().up().label('4.7kΩ\npull-up', loc='right'))
        d.add(elm.Line().up(0.5).label('3.3V', loc='right'))

        # BH1750 on SDA
        d.add(elm.Line().right(1).at(sda_start.end))
        d.add(elm.Dot().label('BH1750\n(0x23)', loc='top'))

        # SHT30 on SDA
        d.add(elm.Line().right(3).at(sda_start.end))
        d.add(elm.Dot().label('SHT30\n(0x44)', loc='top'))

        # SCL line below
        d.add(elm.Line().right(1).at(d.here).label('ESP32\nG33 (SCL)', loc='left').down(3))
        d.add(elm.Line().right(1))
        scl_start = d.add(elm.Dot())
        d.add(elm.Line().right(5))

        d.add(elm.Dot())
        d.add(elm.Resistor().up().label('4.7kΩ\npull-up', loc='right'))
        d.add(elm.Line().up(0.5).label('3.3V', loc='right'))

        d.add(elm.Line().right(1).at(scl_start.end))
        d.add(elm.Dot().label('BH1750\nSCL', loc='bottom'))

        d.add(elm.Line().right(3).at(scl_start.end))
        d.add(elm.Dot().label('SHT30\nSCL', loc='bottom'))

        d.add(elm.Label().label('SucuStation — I2C Bus (shared A1+A2)\nBH1750 @ 0x23, SHT30 @ 0x44 — no address conflict', loc='bottom'))

    save(d, '02_i2c_bus')


# ---------------------------------------------------------------------------
# 3. ESP8266 indoor — SHT30 with I2C pull-ups
# ---------------------------------------------------------------------------
def schematic_esp8266():
    print('Generating: esp8266_indoor')
    with schemdraw.Drawing(fontsize=11) as d:
        d.config(inches_per_unit=0.5)

        # 3V3 rail
        d.add(elm.Line().right(0.5).label('ESP8266\n3V3', loc='left'))
        d.add(elm.Dot())
        vcc = d.here

        # VCC to SHT30
        d.add(elm.Line().right(4))
        d.add(elm.Dot().label('SHT30\nVCC (red)', loc='right'))

        # Pull-up SDA
        d.add(elm.Line().down(1).at(vcc))
        d.add(elm.Dot())
        puda = d.here
        d.add(elm.Resistor().down().label('10KΩ', loc='right'))
        # SDA line
        d.add(elm.Dot())
        d.add(elm.Line().left(0.5).label('D2 (GPIO4)\nSDA', loc='left'))
        d.add(elm.Line().right(4).at(d.here))
        d.add(elm.Dot().label('SHT30\nSDA (white)', loc='right'))

        # Pull-up SCL
        d.add(elm.Line().down(1).at(puda))
        d.add(elm.Resistor().down().label('10KΩ', loc='right'))
        d.add(elm.Dot())
        d.add(elm.Line().left(0.5).label('D1 (GPIO5)\nSCL', loc='left'))
        d.add(elm.Line().right(4).at(d.here))
        d.add(elm.Dot().label('SHT30\nSCL (yellow)', loc='right'))

        # GND
        d.add(elm.Line().down(1).at(d.here))
        d.add(elm.Line().left(4))
        d.add(elm.Dot().label('SHT30\nGND (black)', loc='left'))
        d.add(elm.Line().left(0.5).label('ESP8266\nGND', loc='left'))

        d.add(elm.Label().label('SucuStation — ESP8266 Indoor Unit\nSHT30 @ I2C 0x44, 10KΩ pull-ups on SDA+SCL', loc='bottom'))

    save(d, '03_esp8266_indoor')


# ---------------------------------------------------------------------------
# 4. Relay + pump circuit detail
# ---------------------------------------------------------------------------
def schematic_relay_pump():
    print('Generating: relay_pump_circuit')
    with schemdraw.Drawing(fontsize=11) as d:
        d.config(inches_per_unit=0.5)

        # ESP32 GPIO → relay coil (in1/in2)
        d.add(elm.Line().right(0.5).label('ESP32\nG14 (Relay1)\nor G17 (Relay2)', loc='left'))
        relay = d.add(elm.Relay().right().label('M5Stack\nMini Relay\n3A/30VDC', loc='top'))

        # Switch side: 12V → relay.a (COM), relay.b → pump
        d.add(elm.SourceV().up().reverse().label('12V', loc='left').at(relay.a))
        vcc_top = d.here

        # Wire from 12V top across to pump positive
        d.add(elm.Line().right(2))
        d.add(elm.Dot())
        pump_plus = d.here

        # Pump motor
        d.add(elm.Motor().right().label('Peristaltic\nPump 12V\n~80mA', loc='top'))
        motor_end = d.here

        # Flyback diode across pump (cathode to +, anode to -)
        d.add(elm.Diode().left().label('1N4007\nflyback', loc='top').reverse())
        pump_minus = d.here

        # Wire from relay.b down to pump negative rail
        d.add(elm.Line().down().at(relay.b).toy(pump_minus))
        d.add(elm.Line().right().tox(pump_minus))

        # GND
        d.add(elm.Line().down(0.5).at(motor_end))
        d.add(elm.Ground())

        d.add(elm.Label().label('SucuStation — Relay + Pump Circuit\n(identical for Relay 1 → Pump 1 and Relay 2 → Pump 2)', loc='bottom'))

    save(d, '04_relay_pump_circuit')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print(f'Output directory: {OUTPUT_DIR}\n')
    schematic_power()
    schematic_i2c()
    schematic_esp8266()
    schematic_relay_pump()
    print('\nDone.')
