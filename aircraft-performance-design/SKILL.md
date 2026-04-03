---
name: aircraft-performance-design
version: 1.0.0
description: Aircraft performance analysis and conceptual design using Anderson's Aircraft Performance and Design. Covers aerodynamics, propulsion, performance analysis (range, endurance, climb, takeoff/landing, turning), and conceptual design methodology.
---

# Aircraft Performance and Design Skill

You are an aerospace engineer. Use Anderson's Aircraft Performance and Design textbook to analyze aircraft performance problems and support conceptual design.

## How to Use This Skill

1. **Identify the problem type** — Performance analysis? Conceptual design? Aerodynamic estimation?
2. **Find the relevant chapter/section** using the index below
3. **Read the specific pages** from `anderson/pages/page_XXXX.md`
4. **Apply the formulas** — always use Python scripts for calculations, never mental math
5. **Show your work** — cite the chapter, section, equation, and example used

## Important Notes

- Part 1 (Chapters 1-3) covers fundamentals: aerodynamics, drag polars, propulsion characteristics
- Part 2 (Chapters 4-6) covers performance analysis: steady flight, accelerated flight, takeoff/landing
- Part 3 (Chapters 7-9) covers design methodology with real aircraft case studies
- The Gulfstream IV is used as a running example throughout Chapters 5-6 — look for these examples when doing transport aircraft analysis
- Design case studies (Wright Flyer, DC-3, Boeing 707/727, SR-71, F-16, F-22) provide validated design data

---

## Quick-Reference: Problem Type to Chapter

### Aerodynamics & Drag (Chapter 2, pages 51-155)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Airfoil lift and drag data | 2.5-2.7 | 62-77 | NACA airfoil nomenclature, coefficient variations |
| Finite wing lift (subsonic) | 2.8.1 | 78-103 | Lifting-line theory, aspect ratio effects, sweep corrections |
| Drag buildup | 2.8.3 | 105-124 | Parasitic drag, skin friction, form drag, wave drag |
| Drag polar construction | 2.9 | 126-141 | Building and using the drag polar, C_D = C_D,0 + KC_L^2 |
| Compressibility / transonic drag | 2.8, 5.8 | 105-124, 244-264 | Drag divergence, area rule, critical Mach number |
| Swept wing aerodynamics | 2.8.1 | 95-103 | Sweep corrections for lift and drag |
| Supersonic aerodynamics | 2.8.1 | 85-103 | Wave drag, supersonic lift, delta wings |

### Propulsion (Chapter 3, pages 145-185)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Reciprocating engine / propeller | 3.3 | 151-161 | Power, SFC, propeller efficiency variations |
| Turbojet performance | 3.4 | 162-169 | Thrust, TSFC vs velocity and altitude |
| Turbofan performance | 3.5 | 170-177 | Thrust, TSFC, bypass ratio effects |
| Turboprop performance | 3.6 | 178-182 | Power, SFC vs velocity and altitude |
| Specific fuel consumption | 3.3-3.7 | 151-185 | SFC/TSFC data for all engine types |

### Steady Flight Performance (Chapter 5, pages 199-320)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Thrust required / drag curve | 5.3 | 202-225 | Graphical and analytical methods for T_R vs V |
| Maximum velocity | 5.5, 5.7 | 226-243 | Thrust/power available intersection methods |
| Maximum L/D, C_L^(3/2)/C_D, C_L^(1/2)/C_D | 5.4.1 | 218-225 | Critical aerodynamic ratios for performance |
| Stall speed / C_L_max | 5.9 | 252-264 | Stall calculation, high-lift device data |
| High-lift devices | 5.9.3 | 257-264 | Flaps, slats, performance increments (Table 5.3) |
| Rate of climb | 5.10 | 265-286 | Graphical and analytical R/C methods |
| Glide performance | 5.10.3 | 282-286 | Unpowered flight, best glide angle/speed |
| Service / absolute ceiling | 5.11 | 287-289 | Ceiling determination methods |
| Time to climb | 5.12 | 290-292 | Graphical and analytical approaches |
| Range (prop aircraft) | 5.13.1 | 296-297 | Breguet range equation, propeller aircraft |
| Range (jet aircraft) | 5.13.2 | 297-299 | Breguet range equation, jet aircraft |
| Endurance (prop) | 5.14.1 | 303-304 | Maximum endurance conditions |
| Endurance (jet) | 5.14.2 | 305 | Maximum endurance conditions |
| Wind effects on range | 5.15.4 | 309-313 | Headwind/tailwind corrections |

### Accelerated Flight & Maneuvers (Chapter 6, pages 321-375)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Level turn performance | 6.2 | 322-335 | Load factor, bank angle, turn radius, turn rate |
| Minimum turn radius | 6.2.1 | 329-331 | Corner velocity, structural/aerodynamic limits |
| Maximum turn rate | 6.2.2 | 332-335 | Sustained and instantaneous turn rates |
| Pull-up / pulldown | 6.3 | 336-339 | Vertical plane maneuvers |
| V-n diagram | 6.5 | 341-343 | Maneuver envelope, gust loads, structural limits |
| Specific excess power (P_s) | 6.6 | 344-352 | Energy methods, accelerated climb |
| Takeoff distance | 6.7 | 353-366 | Ground roll + airborne distance to clear obstacle |
| Landing distance | 6.8 | 367-375 | Approach, flare, and ground roll calculation |
| Rolling friction coefficients | 6.7 | 355 | Table 6.1 — μ_r for various surfaces |

### Conceptual Design Methodology (Chapter 7, pages 381-395)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Design phases overview | 7.2 | 382-386 | Conceptual, preliminary, detail design |
| Seven pivot points | 7.3 | 387-395 | Structured design methodology |
| Constraint diagram | 7.3.8 | 392-395 | T/W vs W/S design space, constraint analysis |
| Design requirements | 7.3.1 | 388-389 | How to define design requirements |

### Propeller Aircraft Design (Chapter 8, pages 397-485)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Weight estimation (first) | 8.3 | 398-405 | W_e/W_0 and W_f/W_0 estimation, Breguet-based |
| Maximum C_L estimation | 8.4.1 | 406-409 | Estimating max lift for design |
| Wing loading selection | 8.4.2 | 410-411 | W/S determination from constraints |
| Thrust-to-weight selection | 8.4.3 | 412-418 | T/W from takeoff, climb, cruise constraints |
| Wing configuration | 8.6.2 | 420-430 | Aspect ratio, taper, sweep, airfoil selection |
| Fuselage sizing | 8.6.3 | 431-432 | Fuselage layout and sizing |
| Tail sizing | 8.6.5 | 435-439 | Horizontal and vertical tail volume coefficients |
| Propeller sizing | 8.6.6 | 440-441 | Propeller diameter and activity factor |
| Landing gear layout | 8.6.7 | 442-447 | Gear placement, tipover/tipback criteria |
| Refined weight estimate | 8.7 | 449-452 | Component weight buildup |
| Performance verification | 8.8 | 453-458 | Checking design against requirements |

### Jet Aircraft Design (Chapter 9, pages 487-570)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Subsonic jet transport design | 9.2 | 489-525 | Boeing 707/727 case study |
| Supersonic aircraft design | 9.4 | 517+ | SR-71, F-16, F-22 case studies |
| Inlet design considerations | 9.4 | 517+ | Supersonic inlet types and integration |

---

## Design Case Studies (Validated Data)

| Aircraft | Type | Chapter | Key Value |
|---|---|---|---|
| Wright Flyer (1903) | Prop biplane | 8.10 (pages 458-461) | First powered flight analysis |
| Douglas DC-3 | Prop transport | 8.11 (pages 463+) | Definitive prop transport |
| Boeing 707 | Jet transport | 9.2 (pages 489-508) | First successful jet transport |
| Boeing 727 | Jet transport | 9.2.3 (pages 509+) | Short-field jet transport |
| SR-71 Blackbird | Supersonic recon | 9.4.2 (pages 525+) | Mach 3+ design challenges |
| F-16 Fighting Falcon | Fighter | 9.4.3 (pages 531+) | Constraint-based fighter design |
| F-22 Raptor | Stealth fighter | 9 (pages 545+) | Modern stealth/supercruise |

## Common Workflows

### "What's the range of this aircraft?"
1. Identify engine type (prop or jet)
2. For jets: Section 5.13.2 — Breguet range R = (V/c_t) * (L/D) * ln(W_0/W_1)
3. For props: Section 5.13.1 — Breguet range R = (η_pr/c) * (L/D) * ln(W_0/W_1)
4. Get L/D from drag polar (Chapter 2.9), SFC from propulsion data (Chapter 3)

### "What's the takeoff distance?"
1. Chapter 6.7 (pages 353-366)
2. Ground roll: Section 6.7.1 — integrate equations of motion or use approximate formula
3. Airborne distance: Section 6.7.2 — climb to clear 35 ft (FAR) or 50 ft obstacle
4. Need: W/S, T/W, C_L_max, μ_r (Table 6.1), air density

### "Design an airplane to meet these requirements"
1. Chapter 7.3 — follow the seven pivot points
2. First weight estimate: Chapter 8.3 (W_e/W_0 from historical data, W_f/W_0 from Breguet)
3. Constraint diagram: Chapter 7.3.8 — plot T/W vs W/S for each requirement
4. Configuration layout: Chapter 8.6 — wing, fuselage, tail, gear
5. Performance check: Chapter 8.8 — verify all requirements are met

### "What's the best speed for maximum endurance?"
1. Prop aircraft: fly at speed for minimum power required → max C_L^(3/2)/C_D (Section 5.4.1)
2. Jet aircraft: fly at speed for minimum thrust required → max L/D (Section 5.4.1)
3. Analytical expressions in Section 5.4.1, worked examples 5.4-5.5
