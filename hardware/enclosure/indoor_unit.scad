// ============================================================
// SniperStation — Indoor Unit Enclosure v1.1
// ============================================================
// Contents:   ESP8266 NodeMCU CP2102 + SSH1106 OLED 1.3"
//             TTP223 touch sensor + SHT30 cased sensor (top)
// Mount:      Wall via keyhole slots on back plate
// USB exit:   Bottom face
//
// HOW TO PRINT:
//   Set PART = "shell"      → export shell STL
//   Set PART = "back_plate" → export back plate STL
//   Set PART = "all"        → preview both side by side
//
// PRINT ORIENTATION:
//   Shell:      front face DOWN on print bed (rotate -90° in slicer on X axis)
//   Back plate: flat face DOWN, no rotation needed
//
// License: CERN OHL v2 Permissive
// ============================================================
//
// Coordinate system (before slicer rotation):
//   x = width    (0 = left,   ext_w = right)
//   y = depth    (0 = front,  ext_d = back)
//   z = height   (0 = bottom, ext_h = top)
//
// ⚠️  Measurements to verify before first print:
//   - SHT30 casing actual dimensions (measured: ~35 x 20 x 12mm) — UPDATE when received
//   - NodeMCU PCB actual dimensions  (nominal:  49 x 26mm)
//   - OLED PCB actual dimensions     (nominal:  38.5 x 23mm)
//   - TTP223 PCB measured: 22.2 x 22.2mm (7/8" x 7/8") ✅
// ============================================================

/* [Part selector] */
PART = "all";    // "all" | "shell" | "back_plate"

/* [Shell — outer dimensions] */
wall  = 2.0;    // wall thickness (mm)
ext_w = 70.0;   // external width
ext_h = 90.0;   // external height (excl. SHT30 protrusion above top)
ext_d = 36.0;   // external depth (front face to back opening)

/* [OLED SSH1106 1.3"] */
// Visible window (show display glass area through front face)
oled_win_w       = 31.0;    // window width
oled_win_h       = 23.0;    // window height
oled_top_margin  = 14.0;    // distance from box top to top edge of window
// PCB dimensions (38.5 x 23mm + tolerance)
oled_pcb_w       = 39.5;    // PCB width  + 1mm tolerance
oled_pcb_h       = 24.0;    // PCB height + 1mm tolerance
// Retention frame depth (from inner face of front wall into interior)
oled_frame_d     =  6.0;

/* [TTP223 Touch Sensor] */
// No hole — capacitive sensing works through 2mm PLA
// Concentric rings engraved on front face indicate touch zone
touch_cz         = 22.0;    // touch area center height from box bottom
touch_ring_max_r =  9.0;    // outermost engraved ring radius
touch_ring_count =  4;      // number of concentric rings
touch_ring_depth =  0.5;    // engraving depth (mm)
touch_ring_w     =  0.8;    // ring line width (mm)
// TTP223 PCB measured: 22.2 x 22.2mm (7/8" x 7/8")
// Right-angle header — pins exit upward into interior (no interference)
ttp_pcb_w        = 23.0;    // 22.2mm + 0.8mm tolerance
ttp_pcb_h        = 23.0;    // 22.2mm + 0.8mm tolerance
ttp_shelf_depth  =  4.0;    // shelf depth from inner front wall

/* [USB slot — bottom face] */
usb_w = 12.0;   // slot width  (micro-USB plug + cable clearance)
usb_h =  9.0;   // slot height

/* [SHT30 cased sensor — top face] */
// ⚠️  Measure your actual SHT30 casing before printing
sht30_casing_w = 36.0;   // casing width  (measured)
sht30_casing_d = 21.0;   // casing depth  (measured)
sht30_lip      =  1.0;   // retaining lip on each side

/* [NodeMCU CP2102] */
// ⚠️  Verify your actual board — some versions differ
mcu_len        = 49.0;   // PCB length (long axis, vertical in enclosure)
mcu_wid        = 26.0;   // PCB width  (short axis, front-to-back)
mcu_ledge_h    =  3.0;   // standoff height (clears USB connector below)
mcu_ledge_w    =  5.0;   // ledge width (support surface)

/* [Back plate attachment] */
boss_od        =  7.0;   // boss outer diameter
boss_id        =  2.3;   // M2 pilot hole diameter
boss_depth     =  8.0;   // pilot hole depth (from back end)

/* [Keyhole slots — wall mounting] */
kh_big_d       =  5.8;   // large circle diameter (M3 screw head clears)
kh_sml_d       =  3.4;   // small circle diameter (M3 shaft, holds)
kh_slot_len    =  8.0;   // slot length (slide distance)
kh_spacing     = 50.0;   // horizontal center-to-center
kh_cz          = ext_h - 20.0;  // small circle center height from bottom

// ── Derived values ───────────────────────────────────────────

int_w = ext_w - 2 * wall;
int_h = ext_h - 2 * wall;

// OLED window center
oled_cx = ext_w / 2;
oled_cz = ext_h - oled_top_margin - oled_win_h / 2;

// Touch hole center
touch_cx = ext_w / 2;

// SHT30 slot outer opening
sht30_slot_w = sht30_casing_w + 2 * sht30_lip;
sht30_slot_d = sht30_casing_d + 2 * sht30_lip;

// Boss corner positions [x, z] — inside enclosure, near back corners
boss_pos = [
    [  9.0,   9.0 ],   // bottom-left
    [ 61.0,   9.0 ],   // bottom-right
    [  9.0,  81.0 ],   // top-left
    [ 61.0,  81.0 ],   // top-right
];

// ── Module: main shell ───────────────────────────────────────

module shell() {
    difference() {
        // Outer solid block
        cube([ext_w, ext_d, ext_h]);

        // Hollow interior — open at back (y = ext_d)
        translate([wall, wall, wall])
            cube([int_w, ext_d + 1, int_h]);

        // OLED window — front face (y = 0)
        translate([oled_cx - oled_win_w/2, -0.1, oled_cz - oled_win_h/2])
            cube([oled_win_w, wall + 0.2, oled_win_h]);

        // Touch zone — concentric rings engraved on front face (no hole)
        // Capacitive field penetrates 2mm PLA without issue
        for (i = [0 : touch_ring_count - 1]) {
            r = touch_ring_max_r - i * (touch_ring_max_r / touch_ring_count);
            translate([touch_cx, -0.1, touch_cz])
                rotate([-90, 0, 0])
                difference() {
                    cylinder(r=r,               h=touch_ring_depth + 0.1, $fn=64);
                    cylinder(r=r - touch_ring_w, h=touch_ring_depth + 0.2, $fn=64);
                }
        }

        // USB slot — bottom face (y from wall to ext_d-wall, centered in x)
        translate([(ext_w - usb_w) / 2, wall, -0.1])
            cube([usb_w, ext_d - 2 * wall, usb_h + 0.1]);

        // SHT30 slot — top face (centered, with retaining lip)
        translate([
            (ext_w - sht30_casing_w) / 2,
            (ext_d - sht30_casing_d) / 2,
            ext_h - wall - 0.1
        ])
            cube([sht30_casing_w, sht30_casing_d, wall + 0.2]);
    }
}

// ── Module: OLED retention frame ────────────────────────────
// Creates a U-channel inside the front wall to guide and hold the OLED PCB.
// OLED PCB slides in from the open back and rests against the front wall.
// PCB width (39.5mm) > window width (31mm) → PCB cannot fall through.

module oled_frame() {
    frame_t = 1.5;   // frame rail thickness

    pcb_x1 = oled_cx - oled_pcb_w / 2;
    pcb_x2 = oled_cx + oled_pcb_w / 2;
    pcb_z1 = oled_cz - oled_pcb_h / 2;
    pcb_z2 = oled_cz + oled_pcb_h / 2;

    // Bottom shelf — PCB rests on this
    translate([pcb_x1 - frame_t, wall, pcb_z1 - frame_t])
        cube([oled_pcb_w + 2 * frame_t, oled_frame_d, frame_t]);

    // Left rail
    translate([pcb_x1 - frame_t, wall, pcb_z1 - frame_t])
        cube([frame_t, oled_frame_d, oled_pcb_h + 2 * frame_t]);

    // Right rail
    translate([pcb_x2, wall, pcb_z1 - frame_t])
        cube([frame_t, oled_frame_d, oled_pcb_h + 2 * frame_t]);

    // Top lip — prevents PCB from tilting out at top
    translate([pcb_x1 - frame_t, wall, pcb_z2])
        cube([oled_pcb_w + 2 * frame_t, frame_t, frame_t]);
}

// ── Module: TTP223 mount shelf ───────────────────────────────
// Square pocket behind the touch zone on the front face.
// TTP223 PCB (22.2 x 22.2mm) slides in and sits flush against front wall.
// Touch pad faces forward (toward engraved rings on front face).
// Right-angle header pins exit upward into the open interior — no interference.

module touch_shelf() {
    translate([touch_cx - ttp_pcb_w / 2, wall, touch_cz - ttp_pcb_h / 2])
        difference() {
            // Shelf frame (outer)
            cube([ttp_pcb_w, ttp_shelf_depth, ttp_pcb_h]);
            // PCB pocket (inner — PCB slides in from open back)
            translate([0.5, 0, 0.5])
                cube([ttp_pcb_w - 1, ttp_shelf_depth + 0.1, ttp_pcb_h - 1]);
        }
}

// ── Module: back plate screw bosses ─────────────────────────
// Hollow bosses in the four interior corners.
// M2 screws go through back plate into these bosses to close the enclosure.

module bosses() {
    boss_h = ext_d - 2 * wall;   // boss from inner front wall to back opening

    for (p = boss_pos) {
        translate([p[0] - boss_od/2, wall, p[1] - boss_od/2])
            difference() {
                cube([boss_od, boss_h, boss_od]);
                // Pilot hole from back end
                translate([boss_od/2, boss_h - boss_depth, boss_od/2])
                    cylinder(d=boss_id, h=boss_depth + 0.1, $fn=16);
            }
    }
}

// ── Module: NodeMCU support ledges ───────────────────────────
// Two ledges inside bottom of enclosure — left and right of NodeMCU PCB.
// NodeMCU sits on ledges, USB connector faces bottom exit slot.
// PCB is centered horizontally and front-to-back.

module mcu_ledges() {
    mcu_cx  = ext_w / 2;
    mcu_y   = (ext_d - mcu_wid) / 2;   // centered front-to-back

    // Left ledge (outside left edge of NodeMCU)
    translate([mcu_cx - mcu_len/2 - mcu_ledge_w, mcu_y, wall])
        cube([mcu_ledge_w, mcu_wid, mcu_ledge_h]);

    // Right ledge (outside right edge of NodeMCU)
    translate([mcu_cx + mcu_len/2, mcu_y, wall])
        cube([mcu_ledge_w, mcu_wid, mcu_ledge_h]);
}

// ── Module: shell assembly ───────────────────────────────────

module shell_assembly() {
    union() {
        shell();
        oled_frame();
        touch_shelf();
        bosses();
        mcu_ledges();
    }
}

// ── Module: back plate ───────────────────────────────────────
// Flat slab with keyhole wall mounting slots and M2 screw holes.
// Print flat (no rotation needed in slicer).

module back_plate() {
    difference() {
        cube([ext_w, wall, ext_h]);

        // Keyhole slots — wall mounting (x2, symmetric)
        for (kx = [ext_w/2 - kh_spacing/2, ext_w/2 + kh_spacing/2]) {

            // Large circle — insert screw head
            translate([kx, -0.1, kh_cz + kh_slot_len])
                rotate([-90, 0, 0])
                cylinder(d=kh_big_d, h=wall + 0.2, $fn=32);

            // Sliding slot — screw shaft travels here
            translate([kx - kh_sml_d/2, -0.1, kh_cz])
                cube([kh_sml_d, wall + 0.2, kh_slot_len]);

            // Small circle — locks on screw shaft at rest position
            translate([kx, -0.1, kh_cz])
                rotate([-90, 0, 0])
                cylinder(d=kh_sml_d, h=wall + 0.2, $fn=32);
        }

        // M2 holes aligned with shell bosses
        for (p = boss_pos) {
            translate([p[0], -0.1, p[1]])
                rotate([-90, 0, 0])
                cylinder(d=2.5, h=wall + 0.2, $fn=16);
        }
    }
}

// ── Render ───────────────────────────────────────────────────

if (PART == "all" || PART == "shell") {
    color("WhiteSmoke", 0.9)
        shell_assembly();
}

if (PART == "all") {
    // Back plate shown offset for side-by-side visualization
    translate([ext_w + 15, 0, 0])
    color("Silver", 0.85)
        back_plate();
}

if (PART == "back_plate") {
    color("Silver", 0.85)
        back_plate();
}
