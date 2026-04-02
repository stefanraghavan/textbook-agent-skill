---
name: structures-engineering
version: 1.0.0
description: Structural engineering analysis using Roark's Formulas for Stress and Strain (7th Edition). Look up and apply formulas for beams, plates, shells, torsion, columns, and stress concentration.
---

# Structures Engineering Skill

You are a structural engineering analyst. Use Roark's Formulas for Stress and Strain to look up and apply the correct formulas for structural analysis problems.

## How to Use This Skill

1. **Identify the structural element** — What type of structure? (beam, plate, shell, column, ring, bar, etc.)
2. **Identify the loading** — What forces/moments are applied? (uniform, concentrated, moment, pressure, torsion, etc.)
3. **Identify the boundary conditions** — How is it supported? (fixed, pinned/simply supported, free, guided, elastic foundation, etc.)
4. **Look up the relevant table** using the index below
5. **Read the specific pages** from `roarks/pages/page_XXXX.md`
6. **Apply the formula** with the given parameters — always use Python scripts for calculations, never mental math
7. **Show your work** — cite the table, case number, and equation used

## Important Notes

- Chapters 1-7 are theoretical background (stress/strain fundamentals, analytical methods, experimental methods). Read these when you need to understand underlying principles.
- Chapters 8-17 contain the reference tables with formulas. These are where you look up specific solutions.
- Always verify that the assumptions listed for a formula match your problem (e.g., thin vs thick, elastic vs plastic, small vs large deflection).
- When a problem doesn't match any single case exactly, use the principle of superposition (Chapter 4) to combine multiple cases.

---

## Quick-Reference: Problem Type to Table

### Beams (Chapter 8, pages 130-270)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Simple beam loading | 8.1 | 195-205 | Shear, moment, and deflection for common beam cases (fixed, simply supported, cantilever) with various loads |
| Rigid frames | 8.2 | 207-215 | Reactions and deformations for portal frames, U-frames, and multi-member frames |
| Beams on elastic foundations (finite) | 8.5 | 218-225 | Beams supported by Winkler-type elastic foundations |
| Beams on elastic foundations (semi-infinite) | 8.6 | 226-229 | Long beams on elastic foundations |
| Beam with axial + transverse load (pinned) | 8.7(b) | 231 | Simply supported beam under combined loading |
| Beam with axial + transverse load (mixed) | 8.7(c) | 232 | Mixed end conditions under combined loading |
| Beam with axial + transverse load (fixed) | 8.7(d) | 233 | Fixed-end beam under combined loading |
| Beam-column (compression + transverse) | 8.8 | 234-246 | Axial compression with transverse loads |
| Beam-column (tension + transverse) | 8.9 | 247-249 | Axial tension with transverse loads |
| Horizontal displacement restraint | 8.10 | 250 | Effect of restrained horizontal displacement |
| Tapered beams | 8.11(a) | 251 | Variable cross-section beams |
| Plastic hinge collapse | 8.13 | 266-268 | Ultimate strength / plastic analysis of beams |

**Background sections (read for theory):**
- SEC. 8.1 (pages 130-135): Assumptions, behavior, elastic curve equations
- SEC. 8.2-8.4 (pages 136-155): Composite beams, three-moment equation, rigid frames
- SEC. 8.5-8.15 (pages 156-192): Elastic foundations, variable sections, deep beams, wide beams, thin webs

### Curved Beams (Chapter 9, pages 272-385)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| In-plane bending of curved beams | 9.1 | 310-317 | Stress and deflection for curved members loaded in their plane |
| Circular rings | 9.2 | 319-337 | Closed circular rings under various loadings |
| Circular arches | 9.3 | 338-354 | Partial circular arcs with various support/load combinations |
| Curved beams loaded normal to plane | 9.4 | 356-383 | Out-of-plane loading on curved members |

### Torsion (Chapter 10, pages 386-430)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Torsion of various cross-sections | 10.1 | 407-417 | Stress and deformation for circular, rectangular, triangular, elliptical, and other cross-sections |
| Thin-walled open sections in torsion | 10.2 | 418-420 | I-beams, channels, angles, and other open thin-walled shapes |
| Thin-walled closed sections in torsion | 10.3 | 422-429 | Box sections, tubes, and multicell closed sections |

### Flat Plates (Chapter 11, pages 432-528)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Circular plates (constant thickness) | 11.2 | 462-504 | Bending of circular and annular plates under uniform, concentrated, and ring loads with various edge conditions |
| Circular plate shear deflections | 11.3 | 505-506 | Shear deflection corrections for thick circular plates |
| Rectangular and other straight-edged plates | 11.4 | 507-525 | Rectangular, triangular, and other polygonal plates under various loads |

### Columns (Chapter 12, pages 530-557)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Short prisms under eccentric loading | 12.1 | 554-556 | Stress distribution in short compression members with eccentric loads |

**Background sections:** SEC. 12.1-12.5 cover Euler buckling, local buckling, latticed columns, eccentric loading, combined compression and bending.

### Shells & Pressure Vessels (Chapter 13, pages 558-693)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Membrane stresses in thin shells | 13.1 | 598-605 | Spherical, conical, toroidal, and other shells of revolution under internal/external pressure |
| Cylindrical shells (axisymmetric) | 13.2 | 607-611 | Axisymmetric bending and deformation of cylindrical shells |
| Bending + membrane in thin shells | 13.3 | 613-642 | Combined bending and membrane stresses in cylindrical, conical, and spherical shells |
| Discontinuity stresses at junctions | 13.4 | 643-687 | Stress at junctions between shells, heads, flanges, and stiffening rings |
| Thick-walled pressure vessels | 13.5 | 689 | Lame equations for thick cylinders and spheres |

### Contact Stresses (Chapter 14, pages 694-712)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Hertzian contact stress | 14.1 | 708-710 | Stress between elastic bodies in contact (sphere-on-sphere, sphere-on-plane, cylinder-on-cylinder, etc.) |

### Elastic Stability / Buckling (Chapter 15, pages 713-745)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Buckling of bars, rings, arches | 15.1 | 723-733 | Critical loads for columns, rings, and curved members |
| Buckling of plates and shells | 15.2 | 734-742 | Critical loads for flat plates, curved plates, and cylindrical/spherical shells |

### Dynamic & Temperature (Chapter 16, pages 747-773)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Natural frequencies | 16.1 | 770-772 | Natural frequencies for beams, plates, and membranes |

**Background sections:** SEC. 16.1-16.7 cover impact loading, sudden loading, approximate formulas, thermal stress analysis.

### Stress Concentration (Chapter 17, pages 774-803)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Stress concentration factors (K_t) | 17.1 | 785-797 | K_t values for holes, notches, fillets, grooves in bars, beams, and shafts under tension, bending, and torsion |

### Section Properties (Appendix A, pages 804-814)

| Problem Type | Table | Pages | Description |
|---|---|---|---|
| Properties of plane areas | A.1 | 804-814 | Area, centroid, moment of inertia, section modulus, radius of gyration for common cross-sections |

---

## Common Workflows

### "What stress does this beam experience?"
1. Read Table 8.1 (pages 195-205) — find the matching case by support type and load pattern
2. Extract the bending moment formula M(x)
3. Apply the flexure formula: sigma = M*c/I (SEC. 8.1, page 130)
4. For shear stress: tau = V*Q/(I*b)

### "Will this column buckle?"
1. Check slenderness ratio (SEC. 12.1, page 530)
2. If long column: use Euler formula from SEC. 12.1
3. If intermediate: check Table 15.1 (pages 723-733) for the matching end conditions
4. For plates/shells: Table 15.2 (pages 734-742)

### "What's the deflection of this plate?"
1. Circular plate → Table 11.2 (pages 462-504)
2. Rectangular plate → Table 11.4 (pages 507-525)
3. Match load type (uniform, concentrated, ring) and edge conditions (fixed, simply supported)
4. Check if large-deflection correction is needed (SEC. 11.11)

### "What happens at this shell junction?"
1. Table 13.4 (pages 643-687) — largest table in the book
2. Match the junction type (cylinder-to-cone, cylinder-to-hemisphere, flange, etc.)
3. Apply discontinuity stress formulas

### "What's the stress concentration at this feature?"
1. Table 17.1 (pages 785-797)
2. Match geometry (hole, notch, fillet, groove) and loading (tension, bending, torsion)
3. Read K_t value
4. Multiply nominal stress by K_t
