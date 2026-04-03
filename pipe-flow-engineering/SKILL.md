---
name: pipe-flow-engineering
version: 1.0.0
description: Pipe flow analysis using "Pipe Flow - A Practical and Comprehensive Guide." Covers friction factors, loss coefficients for all fittings, compressible flow, network analysis, transient analysis, cavitation, and water hammer.
---

# Pipe Flow Engineering Skill

You are a piping/fluid systems engineer. Use the Pipe Flow guide to analyze pressure drops, size piping, determine flow rates, and evaluate system performance.

## How to Use This Skill

1. **Identify the problem type** — Pressure drop? Pipe sizing? Flow rate? System analysis?
2. **Find the relevant chapter** using the index below
3. **Read the specific pages** from `pipeflow/pages/page_XXXX.md`
4. **Apply the formulas** — always use Python scripts for calculations, never mental math
5. **Show your work** — cite the chapter, section, table, and equation used

## Important Notes

- Part I (Chapters 1-7) covers methodology: fundamentals, conservation equations, flow analysis
- Part II (Chapters 8-19) is the loss coefficient reference — the core lookup section
- Part III (Chapters 20-23) covers special phenomena: cavitation, vibration, water hammer
- Appendices contain water properties, pipe data, and compressible flow tables
- Loss coefficients K are defined as: h_L = K * V^2 / (2g)
- The Moody chart is on page 99 (Diagram 8.1)

---

## Quick-Reference: Problem Type to Chapter

### Fundamentals (Chapters 1-3, pages 1-30)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Fluid properties | 1.2 | 4-6 | Density, viscosity, bulk modulus |
| Reynolds number / flow regime | 1.3, 1.6 | 6-8 | Laminar vs turbulent transition |
| Conservation equations | 2.1-2.5 | 13-18 | Mass, momentum, energy equations |
| Head loss concept | 2.6-2.8 | 18-20 | h_L definition, conventional head loss |
| Hydraulic / energy grade lines | 2.9 | 20-21 | HGL and EGL concepts |

### Friction Factor & Surface Roughness (Chapter 8, pages 77-100)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Colebrook-White equation | 8.2 | 78 | Implicit friction factor equation |
| Moody chart | 8.3, Diagram 8.1 | 79, 99 | Full-size Moody diagram |
| Explicit friction factor formulas | 8.4 | 79-80 | Churchill, Swamee-Jain, Haaland, etc. (10 alternatives) |
| Churchill's all-regime formula | 8.5 | 81 | Single equation for laminar + turbulent + transition |
| Surface roughness values | 8.6, Table 8.1 | 82-84, 96 | Absolute roughness for pipe materials |
| Friction factor tables | Table 8.2 | 97 | f vs pipe size, condition, and Reynolds number |
| Noncircular passages | 8.7 | 85 | Hydraulic diameter method |

### Entrances (Chapter 9, pages 89-100)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Sharp-edged entrance | 9.1 | 89-91 | K = 0.5 and variations |
| Rounded entrance | 9.2 | 91 | K vs r/D ratio |
| Beveled entrance | 9.3 | 91-92 | K vs bevel angle |
| Entrance through orifice | 9.4 | 92 | Submerged entrance with restriction |

### Contractions (Chapter 10, pages 101-112)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Sharp-edged contraction | 10.2 | 102-103 | K vs area ratio |
| Rounded contraction | 10.3 | 103-104 | K vs r/D and area ratio |
| Conical contraction | 10.4 | 104-106 | K vs half-angle and area ratio |
| Pipe reducer (contracting) | 10.7 | 107-111 | K for commercial reducers |

### Expansions & Diffusers (Chapter 11, pages 113-134)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Sudden expansion | 11.1 | 113-114 | Borda-Carnot loss, K = (1 - A1/A2)^2 |
| Conical diffuser | 11.2 | 114-120 | K vs half-angle and area ratio |
| Multistage diffusers | 11.3 | 117-120 | Optimized staged diffusers |
| Curved wall diffuser | 11.4 | 120-121 | Table 11.4 coefficients |
| Pipe reducer (expanding) | 11.5 | 121-130 | Table 11.5 — K for butt-weld reducers |

### Exits (Chapter 12, pages 131-137)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Straight pipe discharge | 12.1 | 131-132 | K = 1.0 (all kinetic energy lost) |
| Diffuser discharge | 12.2 | 132 | K for conical diffuser exit |
| Orifice discharge | 12.3 | 132-134 | Discharge through restriction |
| Nozzle discharge | 12.4 | 134 | Smooth nozzle exit loss |

### Orifices (Chapter 13, pages 139-158)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Sharp-edged orifice | 13.2 | 140-142 | K and discharge coefficient vs beta ratio |
| Round-edged orifice | 13.3 | 142-145 | K vs r/d and beta ratio |
| Bevel-edged orifice | 13.4 | 145-146 | K vs bevel angle |
| Thick-edged orifice | 13.5, Table 13.2 | 146-149, 158 | K vs t/d and beta ratio |
| Multihole orifices | 13.6 | 149 | Equivalent single orifice |

### Flow Meters (Chapter 14, pages 157-162)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Flow nozzle | 14.1 | 157-158 | ISA 1932, long-radius nozzle |
| Venturi tube | 14.2 | 158-159 | Classical venturi, truncated designs |
| Nozzle/venturi | 14.3 | 159 | Combined configurations |

### Bends & Elbows (Chapter 15, pages 163-180)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Pipe bends and elbows | 15.1 | 163-166 | K vs R/D ratio, bend angle, roughness |
| Coils | 15.2 | 166-168 | Helical coil friction augmentation |
| Miter bends | 15.3 | 168-169 | K for miter joints |
| Coupled bends (S, U, Z) | 15.4 | 169 | Interaction between sequential bends |
| Welded elbow K tables | Tables 15.5-15.8 | 177-178 | K by schedule and pipe size |
| Fabricated bend K tables | Tables 15.9-15.12 | 179-180 | K by schedule and pipe size |

### Tees & Junctions (Chapter 16, pages 177-200)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Diverging tees | 16.1 | 178-182 | K for branch and run, various flow splits |
| Converging tees | 16.2 | 182-200 | K for combining flows |

### Pipe Joints (Chapter 17, pages 201-208)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Weld protrusion | 17.1 | 201-202 | K for internal weld beads |
| Backing rings | 17.2, Table 17.1 | 202-203, 208 | K for backing ring joints |
| Misalignment | 17.3 | 203-204 | K for offset pipe joints |

### Valves (Chapter 18, pages 205-212)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Gate, globe, needle valves | 18.1 | 205-207 | Multiturn valve K values |
| Ball, butterfly, plug valves | 18.2 | 207-209 | Quarter-turn valve K values |
| Check, relief valves | 18.3 | 209-210 | Self-actuated valve K values |
| Control valves (C_v) | 18.4 | 210-211 | C_v to K conversion |

### Threaded Fittings (Chapter 19, pages 213-216)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Threaded reducers, elbows, tees | 19.1-19.5 | 213-215 | K values for screwed fittings |
| Threaded valves | 19.6 | 215 | K for threaded valve bodies |

### Compressible Flow (Chapter 4, pages 31-48)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Approximate method (incompressible eqs) | 4.2 | 32-37 | When and how to use incompressible equations for gas flow |
| Adiabatic flow with friction (Fanno) | 4.3 | 37-42 | Exact compressible flow in pipes |
| Isothermal flow with friction | 4.4 | 42-43 | Long pipelines with heat transfer |
| Compressible flow example | 4.5 | 43-47 | Worked example comparing methods |
| Mach number methods | Appendix E | 269-274 | Detailed Fanno flow solutions |
| Compressibility factor (Z) | Appendix D | 263-268 | Redlich-Kwong, Lee-Kesler equations |

### Network Analysis (Chapter 5, pages 49-60)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Series pipe systems | 5.2 | 50 | Equal flow, additive losses |
| Parallel pipe systems | 5.3 | 50-51 | Equal pressure drop, split flow |
| Branching networks | 5.4 | 51 | Three-reservoir and similar problems |
| Ring sparger example | 5.5 | 51-54 | Uniform distribution system |
| Core spray system example | 5.6 | 54-59 | Nuclear piping network analysis |

### Transient Analysis (Chapter 6, pages 61-68)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Vessel drain time | 6.2 | 62-65 | Transient draining calculations |
| Positive displacement pump | 6.3 | 65-67 | Pump startup/shutdown transients |
| Time-step integration | 6.4 | 67-68 | Numerical transient methods |

### Cavitation & NPSH (Chapter 20, pages 219-228)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Cavitation fundamentals | 20.1 | 219-220 | Vapor pressure, cavitation onset |
| Pipeline design for cavitation | 20.2 | 220 | Avoiding cavitation in piping |
| NPSH calculations | 20.3 | 220-221 | NPSH available vs required |
| NPSH tables | Tables 20.1-20.2 | 227 | NPSHA vs vessel pressure |

### Water Hammer & Vibration (Chapter 21, pages 225-230)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Steady flow vibration | 21.1 | 225 | Flow-induced vibration in pipes |
| Vortex shedding | 21.2 | 225-226 | External flow excitation |
| Water hammer | 21.3 | 226-227 | Pressure surge from rapid valve closure |
| Column separation | 21.4 | 227-228 | Vapor cavity formation and collapse |

### Uncertainty Analysis (Chapter 7, pages 69-84)

| Problem Type | Section | Pages | Description |
|---|---|---|---|
| Pressure drop uncertainty | 7.2 | 69-71 | Error propagation for ΔP |
| Flow rate uncertainty | 7.3 | 71-72 | Error propagation for Q |
| Suggested uncertainty values | Table 7.1 | 84 | Recommended values for inputs |

### Reference Data (Appendices)

| Data | Appendix | Pages | Description |
|---|---|---|---|
| Water properties (English) | A, Table A.1 | 241-244 | ρ, μ, ν, P_v vs temperature |
| Water properties (SI) | A, Table A.2 | 245 | Same in SI units |
| Commercial pipe dimensions | B | 245-252 | ID, OD, wall thickness, flow area by schedule |
| Physical constants & conversions | C | 253-262 | Unit conversion factors |
| Gas compressibility factors | D | 263-268 | Z-factor equations and constants |
| Velocity profiles | F | 275-278 | Turbulent velocity profile derivations |

---

## Common Workflows

### "What's the pressure drop through this piping system?"
1. Calculate Reynolds number: Re = ρVD/μ (Chapter 1.3)
2. Get friction factor from Moody chart (page 99) or Churchill's formula (Section 8.5)
3. Major losses: h_f = f(L/D)(V^2/2g) (Chapter 8)
4. Minor losses: sum K values for each fitting from Chapters 9-19
5. Total: h_L = h_f + Σ(K_i * V^2/2g)

### "What pipe size do I need for this flow rate?"
1. Start with velocity limits (typically 3-10 ft/s for water)
2. Pick a trial pipe size from Appendix B
3. Calculate pressure drop using the workflow above
4. Iterate until pressure drop is within the available driving head

### "Will this pump cavitate?"
1. Chapter 20 — calculate NPSH available
2. NPSHA = P_surface + z_elevation - h_L_suction - P_vapor (all in head)
3. Compare to pump NPSHR (from pump curve)
4. Need NPSHA > NPSHR with adequate margin

### "What's the water hammer pressure in this system?"
1. Chapter 21.3 — Joukowsky equation: ΔP = ρ * a * ΔV
2. Wave speed a depends on pipe material, D/t ratio, fluid bulk modulus
3. Check if valve closure time < 2L/a (rapid closure)
