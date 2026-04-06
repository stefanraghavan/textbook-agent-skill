#!/usr/bin/env python3
"""
=============================================================================
CONCEPTUAL DESIGN OF A 30-PASSENGER TWIN TURBOPROP REGIONAL AIRLINER
=============================================================================

Following Anderson's Seven Pivot Points (Ch. 7) and Propeller-Driven
Design Process (Ch. 8) from "Aircraft Performance and Design."

Requirements:
  - 30 pax @ 200 lb each (incl. baggage), crew: 2 pilots + 1 FA @ 200 lb
  - Range: 600 nmi with IFR reserves (45 min loiter)
  - Cruise: 300 kt at 25,000 ft
  - Takeoff field length: 3,500 ft over 50-ft obstacle (ISA, SL)
  - Landing field length: 3,000 ft over 50-ft obstacle (ISA, SL)
  - Rate of climb at SL: >= 1,500 ft/min
  - Service ceiling: 30,000 ft
  - FAR Part 25, pressurized cabin, twin turboprop
"""

import math
import numpy as np

# =============================================================================
# CONSTANTS
# =============================================================================
g = 32.174          # ft/s^2
rho_SL = 0.002377   # slug/ft^3  (ISA sea level)
a_SL = 1116.4       # ft/s speed of sound at sea level
T_SL = 518.67       # Rankine (59°F)

# ISA atmosphere model
def isa_density(h_ft):
    """Standard atmosphere density (slug/ft^3) up to 36,089 ft."""
    if h_ft <= 36089:
        T = 518.67 - 0.00356616 * h_ft  # Rankine
        p = 2116.22 * (T / 518.67) ** 5.2559  # lb/ft^2
    else:
        T = 389.97  # Rankine (constant in stratosphere)
        p = 2116.22 * 0.22336 * math.exp(-4.80614e-5 * (h_ft - 36089))
    rho = p / (1716.49 * T)
    return rho

def isa_temp(h_ft):
    if h_ft <= 36089:
        return 518.67 - 0.00356616 * h_ft
    return 389.97

def isa_speed_of_sound(h_ft):
    T = isa_temp(h_ft)
    return math.sqrt(1.4 * 1716.49 * T)

print("=" * 78)
print("  CONCEPTUAL DESIGN: 30-PAX TWIN TURBOPROP REGIONAL AIRLINER")
print("  Following Anderson Ch. 7 (Seven Pivot Points) & Ch. 8 (Prop Design)")
print("=" * 78)

# =============================================================================
# PIVOT POINT 1: REQUIREMENTS  (Anderson §7.3.1, §8.2)
# =============================================================================
print("\n" + "=" * 78)
print("  PIVOT POINT 1: REQUIREMENTS")
print("=" * 78)

n_pax = 30
W_per_pax = 200.0      # lb (passenger + baggage)
n_crew = 3              # 2 pilots + 1 FA
W_per_crew = 200.0      # lb

R_nmi = 600.0           # nautical miles
R_ft = R_nmi * 6076.12  # ft
loiter_min = 45.0       # IFR reserve loiter (minutes)

V_cruise_kt = 300.0     # knots
V_cruise_fps = V_cruise_kt * 1.6878  # ft/s
h_cruise = 25000.0      # ft

s_TO_max = 3500.0       # ft (takeoff over 50 ft)
s_L_max = 3000.0        # ft (landing over 50 ft)
ROC_min = 1500.0        # ft/min at sea level
h_ceiling = 30000.0     # ft (service ceiling)

W_crew = n_crew * W_per_crew
W_payload = n_pax * W_per_pax

print(f"  Passengers: {n_pax} x {W_per_pax:.0f} lb = {W_payload:.0f} lb payload")
print(f"  Crew: {n_crew} x {W_per_crew:.0f} lb = {W_crew:.0f} lb")
print(f"  Range: {R_nmi:.0f} nmi + {loiter_min:.0f} min IFR loiter reserve")
print(f"  Cruise: {V_cruise_kt:.0f} kt at {h_cruise:.0f} ft")
print(f"  Takeoff field: {s_TO_max:.0f} ft | Landing field: {s_L_max:.0f} ft")
print(f"  Min ROC at SL: {ROC_min:.0f} ft/min | Service ceiling: {h_ceiling:.0f} ft")

# =============================================================================
# PIVOT POINT 2: FIRST WEIGHT ESTIMATE  (Anderson §8.3, Eq. 8.1–8.8)
# =============================================================================
print("\n" + "=" * 78)
print("  PIVOT POINT 2: FIRST WEIGHT ESTIMATE")
print("=" * 78)

# --- W_e/W_0 estimation (Anderson §8.3.1, Fig. 8.1) ---
# Anderson uses 0.62 for piston props. For turboprops in the 25,000–45,000 lb
# class, historical data (Raymer Table 3.1, also Roskam) gives W_e/W_0 ≈ 0.58–0.62.
# Modern turboprops (ATR-42, Dash 8, Saab 340): W_e/W_0 ≈ 0.58–0.61.
# We use 0.59 as our initial estimate.
We_W0 = 0.59
print(f"\n  W_e/W_0 = {We_W0:.2f}  (historical turboprop data, Anderson Fig. 8.1/Raymer)")

# --- W_f/W_0 estimation via Breguet range equation (Anderson §8.3.2, Eq. 5.153) ---
# For turboprop: R = (eta_pr / c) * (L/D) * ln(W_i / W_f)
# where c is the power-specific fuel consumption

# Turboprop SFC: typical 0.5 lb/(shp·hr) (Anderson §3.6, Raymer)
c_bhp = 0.50  # lb/(hp·hr) — typical modern turboprop (PW100-series, CT7)
# Convert to consistent units: lb / (ft·lb/s · s)
c = c_bhp / (550.0 * 3600.0)  # lb per (ft·lb/s) per second

# Propeller efficiency at cruise
eta_pr = 0.85  # Anderson Eq. 8.13, typical for constant-speed prop

# Estimated L/D at cruise — turboprop transports typically achieve 14–17
# ATR-72 ≈ 16, Dash 8-300 ≈ 15. We estimate 15 for our design.
LD_cruise = 15.0

# Estimated L/D at loiter (max L/D) — slightly higher than cruise
LD_loiter = 16.0

print(f"  SFC = {c_bhp:.2f} lb/(shp·hr)")
print(f"  η_pr = {eta_pr:.2f}")
print(f"  (L/D)_cruise = {LD_cruise:.1f}")
print(f"  (L/D)_loiter = {LD_loiter:.1f}")

# Mission profile weight fractions (Anderson §8.3.2, Eqs. 8.9–8.18)
# Segment 0→1: Engine start, taxi, takeoff
W1_W0 = 0.97   # Anderson Eq. 8.9 (historical)
print(f"\n  Mission segment weight fractions:")
print(f"    W1/W0 (takeoff)  = {W1_W0:.3f}  [Anderson Eq. 8.9]")

# Segment 1→2: Climb to cruise altitude
W2_W1 = 0.985  # Anderson Eq. 8.10 (historical)
print(f"    W2/W1 (climb)    = {W2_W1:.3f}  [Anderson Eq. 8.10]")

# Segment 2→3: Cruise (Breguet, Eq. 5.153 / 8.14)
# R = (eta_pr / c) * (L/D) * ln(W2/W3)
# ln(W2/W3) = c * R / (eta_pr * L/D)
ln_W2_W3 = c * R_ft / (eta_pr * LD_cruise)
W3_W2 = 1.0 / math.exp(ln_W2_W3)
print(f"    W3/W2 (cruise)   = {W3_W2:.4f}  [Breguet, Anderson Eq. 8.14]")
print(f"      ln(W2/W3) = {ln_W2_W3:.4f}")

# Segment 3→4: Loiter (45 min IFR reserve) — use endurance Breguet
# For prop: E = (eta_pr / c) * (L/D) * (1/V_loiter) * ...
# Actually the loiter Breguet for prop aircraft:
# E = (eta_pr / c) * (L/D) * ln(W3/W4) — but E is in ft/(ft/s) = seconds
# Wait — the Breguet ENDURANCE equation for prop is:
# E = (1/c) * (L/D) * ln(W3/W4) in consistent units where c is in 1/s for power SFC
# Actually let's be careful. From Anderson Eq. 5.153:
#   R = (eta_pr/c) * (L/D) * ln(W_i/W_f)  — this gives range in feet
# For endurance (loiter), we want time. The endurance equation for propeller:
#   E = (eta_pr / (c * V)) * (L/D) * ln(W_i/W_f)  — but this doesn't simplify nicely.
#
# Actually for loiter, a simpler approach: convert loiter to equivalent range.
# Loiter speed ≈ best endurance speed. For prop aircraft, best endurance is at
# V for max C_L^(3/2)/C_D. Approximate loiter at ~180 kt.
V_loiter_kt = 180.0
V_loiter_fps = V_loiter_kt * 1.6878
E_loiter_s = loiter_min * 60.0  # seconds
R_loiter_ft = V_loiter_fps * E_loiter_s  # equivalent range during loiter

# Use Breguet for the loiter "range"
ln_W3_W4 = c * R_loiter_ft / (eta_pr * LD_loiter)
W4_W3 = 1.0 / math.exp(ln_W3_W4)
print(f"    W4/W3 (loiter)   = {W4_W3:.4f}  [45-min IFR reserve at {V_loiter_kt:.0f} kt]")

# Segment 4→5: Descent + Landing
W5_W4 = 0.995  # Anderson Eq. 8.18
print(f"    W5/W4 (land)     = {W5_W4:.3f}  [Anderson Eq. 8.18]")

# Product of all segment fractions (Anderson Eq. 8.6)
W5_W0 = W1_W0 * W2_W1 * W3_W2 * W4_W3 * W5_W4
print(f"\n    W5/W0 = {W5_W0:.4f}  [Anderson Eq. 8.6]")

# Fuel fraction with 5% reserve/trapped fuel allowance (Anderson Eq. 8.8 uses 6%)
Wf_W0 = 1.06 * (1.0 - W5_W0)
print(f"    W_f/W_0 = 1.06 × (1 - {W5_W0:.4f}) = {Wf_W0:.4f}  [Anderson Eq. 8.8]")

# Calculate W_0 (Anderson Eq. 8.4)
W0 = (W_crew + W_payload) / (1.0 - Wf_W0 - We_W0)
print(f"\n  W_0 = (W_crew + W_payload) / (1 - W_f/W_0 - W_e/W_0)")
print(f"       = ({W_crew:.0f} + {W_payload:.0f}) / (1 - {Wf_W0:.4f} - {We_W0:.2f})")
print(f"       = {W_crew + W_payload:.0f} / {1.0 - Wf_W0 - We_W0:.4f}")
print(f"       = {W0:.0f} lb")
print(f"\n  *** First estimate: W_0 = {W0:.0f} lb ***")

W_fuel = Wf_W0 * W0
W_empty = We_W0 * W0
print(f"      W_fuel  = {W_fuel:.0f} lb")
print(f"      W_empty = {W_empty:.0f} lb")

# Amplification factor (Anderson p. 405)
amp = 1.0 / (1.0 - Wf_W0 - We_W0)
print(f"      Amplification factor = {amp:.2f} (every 1 lb payload → {amp:.2f} lb W_0)")

# =============================================================================
# PIVOT POINT 3: CRITICAL PERFORMANCE PARAMETERS  (Anderson §8.4)
# =============================================================================
print("\n" + "=" * 78)
print("  PIVOT POINT 3: CRITICAL PERFORMANCE PARAMETERS")
print("=" * 78)

# --- 3a. Maximum Lift Coefficients (Anderson §8.4.1, Eq. 8.24–8.25) ---
# For a turboprop regional: double-slotted Fowler flaps typical
# Clean: NACA 23018 root/23012 tip → avg (c_l)max ≈ 1.7, finite wing factor 0.9
# → (C_L)max_clean ≈ 0.9 × 1.7 = 1.53

# With flaps (landing, 40° Fowler): Δ(c_l)max ≈ 1.3 (Fowler, Anderson Fig. 5.28)
# → avg (c_l)max = 1.7 + 1.3 = 3.0 → (C_L)max_land = 0.9 × 3.0 = 2.7
# With flaps (takeoff, 15°): Δ(c_l)max ≈ 0.8
# → avg (c_l)max = 1.7 + 0.8 = 2.5 → (C_L)max_TO = 0.9 × 2.5 = 2.25

CL_max_clean = 1.53
CL_max_TO = 2.25   # flaps in takeoff setting
CL_max_land = 2.70  # flaps in landing setting

print(f"\n  Maximum lift coefficients (Anderson §8.4.1, Eq. 8.24):")
print(f"    (C_L)max clean   = {CL_max_clean:.2f}")
print(f"    (C_L)max takeoff = {CL_max_TO:.2f} (Fowler flaps, TO setting)")
print(f"    (C_L)max landing = {CL_max_land:.2f} (Fowler flaps, full)")

# --- 3b. Drag polar estimation (Anderson §2.9, §5.3) ---
# C_D = C_D0 + K*C_L^2  where K = 1/(pi*e*AR)
# For turboprop transports: C_D0 ≈ 0.022-0.028 (wetted area method)
# We estimate C_D0 = 0.025 initially (pressurized, fixed gear doors, nacelles)
# AR ≈ 10–12 typical for turboprops. Assume AR = 10, e = 0.80
# K = 1/(pi * 0.80 * 10) = 0.0398

AR = 10.0
e_oswald = 0.80
K = 1.0 / (math.pi * e_oswald * AR)
CD0 = 0.025

# Check (L/D)max = 1 / (2*sqrt(CD0*K))  — Anderson Eq. 5.30
LD_max = 1.0 / (2.0 * math.sqrt(CD0 * K))

print(f"\n  Drag polar (Anderson §2.9, Eq. 5.30):")
print(f"    C_D0 = {CD0:.4f}")
print(f"    AR = {AR:.1f},  e = {e_oswald:.2f}")
print(f"    K = 1/(π·e·AR) = {K:.5f}")
print(f"    (L/D)max = 1/(2√(C_D0·K)) = {LD_max:.2f}")

# --- 3c. Constraint Diagram: T/W vs W/S  (Anderson §7.3.8, Eqs. 7.1–7.3) ---
print(f"\n  --- CONSTRAINT DIAGRAM (Anderson §7.3.8) ---")

WS_range = np.linspace(30, 100, 500)  # W/S in lb/ft^2

# Cruise altitude properties
rho_cruise = isa_density(h_cruise)
sigma_cruise = rho_cruise / rho_SL
a_cruise = isa_speed_of_sound(h_cruise)
M_cruise = V_cruise_fps / a_cruise

print(f"\n  Cruise conditions at {h_cruise:.0f} ft:")
print(f"    ρ = {rho_cruise:.6f} slug/ft³  (σ = {sigma_cruise:.4f})")
print(f"    V_cruise = {V_cruise_fps:.1f} ft/s = {V_cruise_kt:.0f} kt")
print(f"    M_cruise = {M_cruise:.3f}")
print(f"    a = {a_cruise:.1f} ft/s")

# --- CONSTRAINT 1: TAKEOFF (Anderson Eq. 6.95 / 7.1) ---
# s_g = 1.21*(W/S) / (g*rho*CLmax_TO*(T/W))
# Total TO distance ≈ s_g + s_a. For over 50-ft obstacle:
# s_a ≈ R*sin(θ_OB) with R = 6.96*V_stall^2/g, θ_OB = arccos(1 - 50/R)
# We need T/W as function of W/S.
def takeoff_TW(WS, s_TO, CL_max_to, rho=rho_SL):
    """Return T/W required for given W/S to meet takeoff distance."""
    V_stall = math.sqrt(2.0 * WS / (rho * CL_max_to))
    V_LO = 1.1 * V_stall
    # Ground roll: Anderson Eq. 6.95, T/W at V = 0.7*V_LO
    # Airborne distance over 50-ft obstacle: Eq. 6.98-6.100
    R_TO = 6.96 * V_stall**2 / g
    if 50.0 / R_TO >= 1.0:
        return 999.0  # impossible
    theta_OB = math.acos(1.0 - 50.0 / R_TO)
    s_a = R_TO * math.sin(theta_OB)
    s_g_avail = s_TO - s_a
    if s_g_avail <= 0:
        return 999.0
    # From Eq. 6.95: T/W = 1.21*(W/S) / (g*rho*CLmax_TO*s_g)
    TW = 1.21 * WS / (g * rho * CL_max_to * s_g_avail)
    return TW

TW_TO = np.array([takeoff_TW(ws, s_TO_max, CL_max_TO) for ws in WS_range])

# --- CONSTRAINT 2: LANDING (Anderson §7.3.8, Curve B) ---
# Landing distance determines a maximum W/S (vertical line on constraint diagram)
# Approach: θ_a = 3°, V_f = 1.23*V_stall, R = V_f^2/(0.2g)
# For FAR 25 landing field length: total = s_a + s_f + s_g
# Landing weight < W_0: assume W_land = 0.95*W_0 (short range, little fuel burn)
W_land_frac = 0.95  # landing weight / W_0

def landing_max_WS(s_L, CL_max_l, rho=rho_SL, W_land_frac=0.95):
    """Find max W_0/S such that landing distance <= s_L.
    Returns W_0/S (not W_land/S)."""
    # Iterate: try W/S values and find the one that gives s_L
    for ws_land in np.linspace(1, 200, 5000):
        V_stall = math.sqrt(2.0 * ws_land / (rho * CL_max_l))
        V_f = 1.23 * V_stall
        V_TD = 1.15 * V_stall  # touchdown speed
        theta_a = math.radians(3.0)
        R_fl = V_f**2 / (0.2 * g)
        h_f = R_fl * (1.0 - math.cos(theta_a))
        s_a = (50.0 - h_f) / math.tan(theta_a)
        s_f = R_fl * math.sin(theta_a)
        # Ground roll (Anderson Eq. 8.28)
        j = 1.15
        N = 3.0  # free roll time
        mu_r = 0.4  # braking friction
        s_g = (j * N * math.sqrt(2.0 * ws_land / (rho * CL_max_l)) +
               j**2 * ws_land / (g * rho * CL_max_l * mu_r))
        s_total = s_a + s_f + s_g
        if s_total >= s_L:
            # ws_land is the max landing W/S
            # Convert to W_0/S
            return ws_land / W_land_frac
    return 200.0  # no constraint found

WS_land_max = landing_max_WS(s_L_max, CL_max_land)
print(f"\n  Landing constraint (Anderson §8.4.2):")
print(f"    Max W_0/S = {WS_land_max:.1f} lb/ft² (for {s_L_max:.0f} ft landing, W_land = {W_land_frac:.0f}×W_0)")

# --- CONSTRAINT 3: CRUISE SPEED (Anderson §5.3) ---
# At cruise: T_required = D = (1/2)*rho*V^2*S*CD
# T = D → (T/W) = (CD0 * q/WS) + K*(WS)/q  where q = 0.5*rho*V^2
# For turboprop, available thrust at altitude: P_avail = P_SL * sigma^0.7 (approx)
# T_avail = eta_pr * P_avail / V_cruise
# T/W at cruise must satisfy: T/W >= q*CD0/(W/S) + K*(W/S)/q
q_cruise = 0.5 * rho_cruise * V_cruise_fps**2

def cruise_TW(WS, q, CD0, K, sigma):
    """T_0/W_0 required for cruise at given conditions.
    Account for altitude lapse: T_avail at alt = T_SL * sigma^0.7 (turboprop)."""
    TW_cruise = q * CD0 / WS + K * WS / q
    # This is T/W at cruise altitude and cruise weight.
    # Convert to T_0/W_0 at sea level:
    # Assume cruise weight ≈ 0.95*W_0 (midcruise)
    # T_at_alt / T_SL = sigma^0.7 for turboprops
    TW_0 = TW_cruise * 0.95 / (sigma**0.7)
    return TW_0

TW_cruise = np.array([cruise_TW(ws, q_cruise, CD0, K, sigma_cruise) for ws in WS_range])

print(f"\n  Cruise constraint (Anderson §5.3):")
print(f"    q_cruise = {q_cruise:.2f} lb/ft²")

# --- CONSTRAINT 4: RATE OF CLIMB at SL (Anderson §5.10) ---
# For prop aircraft: excess power = eta*P - D*V
# R/C = (eta*P - D*V) / W = (T/W)*V - V^3*rho*CD0/(2*W/S) - 2*K*(W/S)/(rho*V)
# At best R/C velocity for prop: approximate R/C ≈ eta*P/W - sqrt(2*W/(rho*S)) * 1.155/(L/D)max
# Simpler: T/W >= ROC/V + q*CD0/(W/S) + K*(W/S)/q  at best climb speed

ROC_fps = ROC_min / 60.0  # ft/s

def climb_TW(WS, ROC_fps, rho=rho_SL):
    """T_0/W_0 required for given rate of climb at sea level."""
    # Best climb speed for propeller aircraft is close to V for (L/D)max
    V_climb = math.sqrt(2.0 * WS / (rho) * math.sqrt(K / CD0))
    q_climb = 0.5 * rho * V_climb**2
    # sin(gamma) = ROC/V, T/W = D/W + ROC/V
    sin_gamma = ROC_fps / V_climb
    TW = q_climb * CD0 / WS + K * WS / q_climb + sin_gamma
    return TW

TW_climb = np.array([climb_TW(ws, ROC_fps) for ws in WS_range])

print(f"\n  Climb constraint: ROC >= {ROC_min:.0f} ft/min at SL")

# --- CONSTRAINT 5: SERVICE CEILING (Anderson §5.10) ---
# At service ceiling, R/C = 100 ft/min
ROC_ceil_fps = 100.0 / 60.0  # ft/s
rho_ceil = isa_density(h_ceiling)
sigma_ceil = rho_ceil / rho_SL

def ceiling_TW(WS, h_ceil):
    """T_0/W_0 required for service ceiling."""
    rho_c = isa_density(h_ceil)
    sigma_c = rho_c / rho_SL
    V_ceil = math.sqrt(2.0 * WS / rho_c * math.sqrt(K / CD0))
    q_c = 0.5 * rho_c * V_ceil**2
    sin_gamma = ROC_ceil_fps / V_ceil
    TW_at_alt = q_c * CD0 / WS + K * WS / q_c + sin_gamma
    # Convert to SL T/W: T_alt = T_SL * sigma^0.7
    TW_0 = TW_at_alt / (sigma_c**0.7)
    return TW_0

TW_ceiling = np.array([ceiling_TW(ws, h_ceiling) for ws in WS_range])

print(f"  Ceiling constraint: {h_ceiling:.0f} ft (100 ft/min R/C)")
print(f"    ρ_ceil = {rho_ceil:.6f} slug/ft³  (σ = {sigma_ceil:.4f})")

# --- FIND DESIGN POINT ---
# The design point minimizes T/W while satisfying all constraints
# and W/S <= WS_land_max

# Build envelope: max of all T/W constraints at each W/S
TW_envelope = np.maximum.reduce([TW_TO, TW_cruise, TW_climb, TW_ceiling])

# Apply landing constraint
valid = WS_range <= WS_land_max
if not np.any(valid):
    print("  ERROR: No feasible design space!")
else:
    # Find minimum T/W in valid region
    TW_valid = TW_envelope.copy()
    TW_valid[~valid] = 999.0
    idx_best = np.argmin(TW_valid)
    WS_design = WS_range[idx_best]
    TW_design = TW_valid[idx_best]

    # Identify which constraint is active
    constraints_at_design = {
        'Takeoff': TW_TO[idx_best],
        'Cruise': TW_cruise[idx_best],
        'Climb': TW_climb[idx_best],
        'Ceiling': TW_ceiling[idx_best]
    }
    active = max(constraints_at_design, key=constraints_at_design.get)

    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║  DESIGN POINT (Anderson §7.3.8, Fig. 7.6)       ║")
    print(f"  ╠══════════════════════════════════════════════════╣")
    print(f"  ║  W_0/S = {WS_design:.1f} lb/ft²                         ║")
    print(f"  ║  T_0/W_0 = {TW_design:.4f}                            ║")
    print(f"  ║  Active constraint: {active:<28s}  ║")
    print(f"  ╚══════════════════════════════════════════════════╝")

    print(f"\n  Constraint values at design point (T/W required):")
    for name, val in constraints_at_design.items():
        marker = " ◄ ACTIVE" if name == active else ""
        print(f"    {name:12s}: T/W = {val:.4f}{marker}")
    print(f"    {'Landing':12s}: W/S ≤ {WS_land_max:.1f} lb/ft² (design: {WS_design:.1f})")

# Add margin: increase T/W by 10% for growth
TW_design_with_margin = TW_design * 1.10
print(f"\n  With 10% growth margin: T/W = {TW_design_with_margin:.4f}")

# =============================================================================
# DERIVED PARAMETERS FROM DESIGN POINT
# =============================================================================
print("\n" + "=" * 78)
print("  DERIVED PARAMETERS")
print("=" * 78)

# Wing area
S_wing = W0 / WS_design
print(f"  Wing area: S = W_0 / (W/S) = {W0:.0f} / {WS_design:.1f} = {S_wing:.1f} ft²")

# Total thrust required at sea level
T_total_SL = TW_design_with_margin * W0
print(f"  Total SL thrust: T_0 = {T_total_SL:.0f} lb")

# For turboprop: P = T*V/eta, but at static: use P = T * V / eta at some reference
# Better: shaft horsepower. For turboprop, T_static ≈ eta_static * 550 * SHP / V_ref
# Use: SHP_total = T_SL * V_ref / (eta_pr * 550) or directly from T/W and P/W relationship
# At cruise: P_req = T_cruise * V_cruise / eta_pr
# At SL static: SHP relates to T via eta_static ≈ 0 (static)
# For turboprops, manufacturers rate in SHP. Use P = W * (T/W) * V_climb / eta_pr as estimate
# More direct: power loading W/P, then P = W_0 / (W/P)

# Estimate SHP from cruise requirement
T_cruise_total = TW_design * 0.95 * W0 * (sigma_cruise**0.7)  # at altitude, midcruise
# Wait, let's be more careful. At cruise:
# T_cruise = D = W/(L/D) ≈ 0.95*W0 / LD_cruise (midcruise weight)
W_midcruise = 0.95 * W0
T_cruise_req = W_midcruise / LD_cruise

# SHP at cruise altitude
SHP_cruise = T_cruise_req * V_cruise_fps / (eta_pr * 550.0)
# SHP at SL = SHP_cruise / sigma^0.7  (turboprop power lapse)
SHP_SL = SHP_cruise / (sigma_cruise**0.7)
SHP_per_engine = SHP_SL / 2.0

print(f"\n  Power sizing:")
print(f"    T_cruise required = {T_cruise_req:.0f} lb")
print(f"    SHP at cruise alt = {SHP_cruise:.0f} hp")
print(f"    SHP at SL (total) = {SHP_SL:.0f} hp")
print(f"    SHP per engine    = {SHP_per_engine:.0f} hp")

# Cross-check with T/W method
SHP_from_TW = TW_design_with_margin * W0 * 250.0 / (eta_pr * 550.0)
# At V = 250 ft/s reference (approx takeoff climb speed)
# Actually for static: T = eta_static * 550 * SHP / V → ill-defined at V=0
# Use Raymer's rule: for turboprop, 1 SHP ≈ 2.5 lb static thrust
T_static_per_SHP = 2.5  # lb/SHP (typical for turboprops)
SHP_total_from_static = T_total_SL / T_static_per_SHP
SHP_per_engine_v2 = SHP_total_from_static / 2.0

print(f"\n  Cross-check via static thrust (2.5 lb/SHP rule):")
print(f"    SHP total = {SHP_total_from_static:.0f} hp")
print(f"    SHP/engine = {SHP_per_engine_v2:.0f} hp")

# Use the larger of the two estimates + round up to realistic engine
SHP_per_engine_final = max(SHP_per_engine, SHP_per_engine_v2)
# Round up to nearest 50
SHP_per_engine_final = math.ceil(SHP_per_engine_final / 50) * 50
SHP_total_final = 2 * SHP_per_engine_final

print(f"\n  *** Selected engine: {SHP_per_engine_final} SHP per engine ***")
print(f"  *** Total installed power: {SHP_total_final} SHP ***")
print(f"  (Comparable to PW127 class: ~2,500 SHP)")

# Recalculate actual T/W with selected power
T_static_actual = SHP_total_final * T_static_per_SHP
TW_actual = T_static_actual / W0
print(f"\n  Actual T_0/W_0 = {TW_actual:.4f}")

# =============================================================================
# PIVOT POINT 4: CONFIGURATION LAYOUT  (Anderson §8.6)
# =============================================================================
print("\n" + "=" * 78)
print("  PIVOT POINT 4: CONFIGURATION LAYOUT")
print("=" * 78)

# ─── 4a. WING CONFIGURATION (Anderson §8.6.2, Figs. 8.6–8.10) ───
print(f"\n  ── 4a. WING CONFIGURATION (Anderson §8.6.2) ──")

# Aspect ratio: typical turboprop transports AR = 10–12
# ATR-42: 11.1, Dash 8-300: 12.4, Saab 340: 11.0
# We chose AR = 10 in our drag polar; let's refine to 11
AR_wing = 11.0
# Recalculate K
e_oswald = 0.80
K = 1.0 / (math.pi * e_oswald * AR_wing)
LD_max = 1.0 / (2.0 * math.sqrt(CD0 * K))

# Taper ratio (Anderson §8.6.2, Fig. 8.9): λ = 0.4–0.6 typical
lambda_wing = 0.45

# Sweep: for 300-kt cruise (M ≈ 0.45), no sweep needed for wave drag.
# Small sweep for structural reasons: Λ_c/4 ≈ 0° to 3°
sweep_c4 = 0.0  # degrees (straight wing, like ATR/Dash 8)

# Airfoil selection (Anderson §8.4.1, Figs. 8.3–8.4)
airfoil_root = "NACA 23018"
airfoil_tip = "NACA 23012"

# Wing area (using updated AR)
S_wing = W0 / WS_design
b_wing = math.sqrt(AR_wing * S_wing)  # wingspan
c_root = 2.0 * S_wing / ((1.0 + lambda_wing) * b_wing)  # Anderson Eq. 8.55
c_tip = lambda_wing * c_root

# Mean aerodynamic chord (Anderson Eq. 8.58)
MAC = (2.0/3.0) * c_root * (1.0 + lambda_wing + lambda_wing**2) / (1.0 + lambda_wing)
# MAC spanwise location (Anderson Eq. 8.57)
y_MAC = (b_wing/6.0) * (1.0 + 2.0*lambda_wing) / (1.0 + lambda_wing)

# Wing position: HIGH WING for regional turboprop (cargo access, prop clearance)
wing_position = "High wing"
dihedral = 3.0  # degrees (less for high wing, Anderson §8.6.2)

print(f"    Aspect ratio AR = {AR_wing:.1f}")
print(f"    Taper ratio λ = {lambda_wing:.2f}")
print(f"    Sweep Λ_c/4 = {sweep_c4:.0f}°")
print(f"    Wing area S = {S_wing:.1f} ft²")
print(f"    Wingspan b = {b_wing:.2f} ft")
print(f"    Root chord c_r = {c_root:.2f} ft")
print(f"    Tip chord c_t = {c_tip:.2f} ft")
print(f"    MAC = {MAC:.2f} ft")
print(f"    MAC spanwise location ȳ = {y_MAC:.2f} ft")
print(f"    Airfoil: {airfoil_root} (root) / {airfoil_tip} (tip)")
print(f"    Position: {wing_position}, dihedral = {dihedral:.0f}°")
print(f"    (L/D)max = {LD_max:.2f} (updated with AR={AR_wing:.0f})")
print(f"    K = {K:.5f}")

# ─── 4b. FUSELAGE SIZING (Anderson §8.6.3) ───
print(f"\n  ── 4b. FUSELAGE SIZING (Anderson §8.6.3) ──")

# 30-pax regional: 2-abreast + aisle (typical for this size)
# Seat pitch: 31 in, seat width: 18 in, aisle: 14 in
# Cross-section: circular for pressurization, ~8.0–8.5 ft diameter
# Cabin length: 30 pax / 2 per row = 15 rows × 31 in pitch ≈ 38.75 ft
# Add cockpit (~7 ft), fwd galley/lav (5 ft), aft galley/lav (5 ft),
# nose section (6 ft), tail cone (10 ft)

seat_pitch_in = 31.0
seats_per_row = 2  # 1+1 with aisle
n_rows = math.ceil(n_pax / seats_per_row)
cabin_length_ft = n_rows * seat_pitch_in / 12.0

# Actually 30 pax at 2-abreast is unusual. Most 30-seaters use 3-abreast (1+2 or 2+1)
seats_per_row = 3
n_rows = math.ceil(n_pax / seats_per_row)
cabin_length_ft = n_rows * seat_pitch_in / 12.0

# Fuselage diameter for 3-abreast + pressurization
# Typical: seat width 18", aisle 18", wall structure 4" each side
# Inner width ≈ 3×18 + 18 + 2×3 = 78" = 6.5 ft → outer ≈ 7.2 ft
# Go with circular cross-section, external diameter ≈ 8.5 ft (like ATR-42: 8.92 ft)
d_fuse = 8.5  # ft (external diameter)
d_fuse_inner = d_fuse - 0.5  # ft (approx wall thickness effect)

# Cockpit + nose
L_nose = 8.0  # ft
# Forward service area
L_fwd_service = 4.0  # ft
# Cabin
L_cabin = cabin_length_ft
# Aft service area
L_aft_service = 4.0  # ft
# Tail cone
L_tail = 14.0  # ft (tapers to empennage)

L_fuse = L_nose + L_fwd_service + L_cabin + L_aft_service + L_tail
fineness_ratio = L_fuse / d_fuse

print(f"    Seating: {seats_per_row}-abreast, {n_rows} rows, {seat_pitch_in:.0f}\" pitch")
print(f"    Cabin length = {L_cabin:.1f} ft")
print(f"    Fuselage external diameter = {d_fuse:.1f} ft")
print(f"    Fuselage internal diameter ≈ {d_fuse_inner:.1f} ft")
print(f"    Fuselage length = {L_fuse:.1f} ft")
print(f"      Nose: {L_nose:.0f}, Fwd svc: {L_fwd_service:.0f}, Cabin: {L_cabin:.1f}, Aft svc: {L_aft_service:.0f}, Tail: {L_tail:.0f}")
print(f"    Fineness ratio L/D = {fineness_ratio:.2f}")
print(f"    (Ideal range 6–10 for min drag; Anderson §8.6.3)")

# ─── 4c. EMPENNAGE SIZING (Anderson §8.6.5, Eqs. 8.60–8.69) ───
print(f"\n  ── 4c. EMPENNAGE SIZING (Anderson §8.6.5) ──")

# Volume coefficients (Anderson Eqs. 8.62, 8.63)
# For twin-engine transport (Raymer Table 6.4):
V_HT = 0.90   # horizontal tail volume ratio (higher than single-engine 0.7)
V_VT = 0.08   # vertical tail volume ratio (higher for twin, OEI consideration)

# Moment arms (estimated from fuselage geometry)
# CG location ≈ 40% of fuselage length from nose
x_cg = 0.40 * L_fuse

# HT aerodynamic center: near tail end, about 90% of fuselage length
x_ac_HT = 0.90 * L_fuse
l_HT = x_ac_HT - x_cg

# VT aerodynamic center: slightly forward of HT
x_ac_VT = 0.88 * L_fuse
l_VT = x_ac_VT - x_cg

# Horizontal tail area (Anderson Eq. 8.60): V_HT = l_HT * S_HT / (MAC * S)
S_HT = V_HT * MAC * S_wing / l_HT

# Vertical tail area (Anderson Eq. 8.61): V_VT = l_VT * S_VT / (b * S)
S_VT = V_VT * b_wing * S_wing / l_VT

# HT geometry
AR_HT = 4.5  # typical (Anderson §8.6.5)
lambda_HT = 0.50
b_HT = math.sqrt(AR_HT * S_HT)
cr_HT = 2.0 * S_HT / ((1.0 + lambda_HT) * b_HT)
ct_HT = lambda_HT * cr_HT
MAC_HT = (2.0/3.0) * cr_HT * (1.0 + lambda_HT + lambda_HT**2) / (1.0 + lambda_HT)

# VT geometry (Anderson Eq. 8.69)
AR_VT = 1.5
lambda_VT = 0.50
h_VT = math.sqrt(AR_VT * S_VT)
cr_VT = 2.0 * S_VT / ((1.0 + lambda_VT) * h_VT)
ct_VT = lambda_VT * cr_VT
MAC_VT = (2.0/3.0) * cr_VT * (1.0 + lambda_VT + lambda_VT**2) / (1.0 + lambda_VT)

print(f"    Tail volume coefficients (Raymer Table 6.4, twin-engine transport):")
print(f"      V_HT = {V_HT:.2f}   V_VT = {V_VT:.2f}")
print(f"    CG location ≈ {x_cg:.1f} ft from nose")
print(f"    HT moment arm l_HT = {l_HT:.1f} ft")
print(f"    VT moment arm l_VT = {l_VT:.1f} ft")
print(f"\n    Horizontal Tail (Anderson Eq. 8.60):")
print(f"      S_HT = {S_HT:.1f} ft²")
print(f"      AR = {AR_HT}, λ = {lambda_HT}, b = {b_HT:.2f} ft")
print(f"      c_r = {cr_HT:.2f} ft, c_t = {ct_HT:.2f} ft, MAC = {MAC_HT:.2f} ft")
print(f"\n    Vertical Tail (Anderson Eqs. 8.61, 8.69):")
print(f"      S_VT = {S_VT:.1f} ft²")
print(f"      AR = {AR_VT}, λ = {lambda_VT}, h = {h_VT:.2f} ft")
print(f"      c_r = {cr_VT:.2f} ft, c_t = {ct_VT:.2f} ft, MAC = {MAC_VT:.2f} ft")

# T-tail configuration (common for turboprops to keep HT out of prop wash)
print(f"    Configuration: T-tail (HT mounted atop VT)")

# ─── 4d. PROPELLER SIZING (Anderson §8.6.6, Eqs. 8.71–8.75) ───
print(f"\n  ── 4d. PROPELLER SIZING (Anderson §8.6.6) ──")

# For turboprops, typically 4–6 blade props
# Raymer: D = 18*(HP)^(1/4) for 3-blade (Anderson Eq. 8.72)
# For 4-blade: D ≈ 16*(HP)^(1/4) (interpolated)
n_blades = 6  # Modern turboprop regional: 6-blade (like PW100/Hamilton Std 568F)

# Empirical: D = C * (SHP)^(1/4) where C depends on blade count
# 2-blade: 22, 3-blade: 18, 4-blade: ~16, 6-blade: ~13 (approximation)
C_prop = 13.0
D_prop_in = C_prop * SHP_per_engine_final**0.25
D_prop_ft = D_prop_in / 12.0

# Check tip speed (Anderson Eq. 8.73–8.75)
RPM = 1200  # typical turboprop prop speed (through reduction gearbox)
n_rps = RPM / 60.0
V_tip_static = math.pi * n_rps * D_prop_ft  # ft/s
V_tip_flight = math.sqrt(V_tip_static**2 + V_cruise_fps**2)

print(f"    Number of blades: {n_blades}")
print(f"    SHP per engine: {SHP_per_engine_final} hp")
print(f"    Prop diameter D = {C_prop}×({SHP_per_engine_final})^0.25 = {D_prop_in:.0f} in = {D_prop_ft:.1f} ft")
print(f"    RPM = {RPM}")
print(f"    Tip speed (static) = {V_tip_static:.0f} ft/s  [Anderson Eq. 8.73]")
print(f"    Tip speed (at V_cruise) = {V_tip_flight:.0f} ft/s  [Anderson Eq. 8.74]")
print(f"    Speed of sound (SL) = {a_SL:.0f} ft/s")
if V_tip_flight < a_SL:
    print(f"    ✓ Tip Mach = {V_tip_flight/a_SL:.3f} — subsonic, acceptable")
else:
    print(f"    ✗ Tip Mach = {V_tip_flight/a_SL:.3f} — SUPERSONIC, redesign needed!")
    # Adjust if needed
    while V_tip_flight >= 0.95 * a_SL and RPM > 800:
        RPM -= 50
        n_rps = RPM / 60.0
        V_tip_static = math.pi * n_rps * D_prop_ft
        V_tip_flight = math.sqrt(V_tip_static**2 + V_cruise_fps**2)
    print(f"    Adjusted RPM = {RPM}, tip Mach = {V_tip_flight/a_SL:.3f}")

# ─── 4e. LANDING GEAR LAYOUT (Anderson §8.6.7, Figs. 8.23–8.26) ───
print(f"\n  ── 4e. LANDING GEAR LAYOUT (Anderson §8.6.7) ──")

# Tricycle configuration (standard for Part 25 transport)
# Main gear retracts into fuselage/nacelle area
# Nose gear retracts forward into nose bay

# Main gear location: behind CG for stability
# Anderson: main wheels at wing center or slightly aft of CG
x_main = x_cg + 0.10 * MAC  # slightly aft of CG
x_nose = L_nose * 0.35  # in nose section

# Prop clearance: D_prop/2 + 12 inches
prop_clearance = D_prop_ft / 2.0 + 1.0  # ft from ground to spinner
# For high-wing: gear needs to be long enough for ground clearance

# Wheel loads (Anderson Eqs. 8.80–8.81)
x1 = x_cg - x_nose   # distance from nosewheel to CG
x2 = x_main - x_cg    # distance from CG to main wheels
x3 = x1 + x2           # wheelbase

F_M = W0 * x1 / x3     # total main wheel load
F_N = W0 * x2 / x3     # nosewheel load

# Wheel sizing (Anderson Eq. 8.82, transport category)
# For transport aircraft, Raymer gives A=2.69, B=0.251 (diameter)
# and A=1.17, B=0.216 (width)
A_d, B_d = 2.69, 0.251  # diameter
A_w, B_w = 1.17, 0.216  # width

# Dual wheels on main gear (typical for this weight class)
load_per_main_wheel = F_M / 4.0  # 2 main struts × 2 wheels each
d_main = A_d * load_per_main_wheel**B_d
w_main = A_w * load_per_main_wheel**B_w

d_nose = A_d * (F_N / 2.0)**B_d  # twin nosewheels
w_nose = A_w * (F_N / 2.0)**B_w

print(f"    Configuration: Tricycle, retractable")
print(f"    Main gear location: {x_main:.1f} ft from nose")
print(f"    Nose gear location: {x_nose:.1f} ft from nose")
print(f"    Wheelbase: {x3:.1f} ft")
print(f"    CG at {x_cg:.1f} ft → {x1/x3*100:.1f}% aft of nose gear")
print(f"\n    Load distribution (Anderson Eqs. 8.80–8.81):")
print(f"      Main wheels (total): {F_M:.0f} lb ({F_M/W0*100:.1f}% of W_0)")
print(f"      Nosewheel:           {F_N:.0f} lb ({F_N/W0*100:.1f}% of W_0)")
print(f"\n    Wheel sizing (Anderson Eq. 8.82):")
print(f"      Main: {d_main:.1f}\" dia × {w_main:.1f}\" width (dual wheels per strut)")
print(f"      Nose: {d_nose:.1f}\" dia × {w_nose:.1f}\" width (twin)")
print(f"    Main gear track: ≈ {d_fuse + 2:.0f} ft (retracts into nacelle/fuselage fairing)")

# =============================================================================
# PIVOT POINT 5: BETTER WEIGHT ESTIMATE  (Anderson §8.7, Eqs. 8.83a–g)
# =============================================================================
print("\n" + "=" * 78)
print("  PIVOT POINT 5: REFINED WEIGHT ESTIMATE — Component Buildup")
print("  (Anderson §8.7, Eqs. 8.83a–g)")
print("=" * 78)

# Exposed areas (subtracting fuselage intersection)
fuse_width_at_wing = d_fuse  # ft
S_wing_exposed = S_wing - fuse_width_at_wing * c_root  # approximate
S_HT_exposed = S_HT * 0.95  # small fuselage intersection for T-tail root
S_VT_exposed = S_VT * 0.93  # some at fuselage

# Fuselage wetted area (Anderson §8.7, Fig. 8.28)
# Approximate as cylinder + nose cone + tail cone
S_wet_fuse_cyl = math.pi * d_fuse * (L_fuse - L_nose - L_tail)
S_wet_fuse_nose = 0.5 * math.pi * d_fuse * L_nose  # half ellipsoid
S_wet_fuse_tail = 0.5 * math.pi * d_fuse * math.sqrt((d_fuse/2)**2 + L_tail**2)
S_wet_fuse = S_wet_fuse_cyl + S_wet_fuse_nose + S_wet_fuse_tail

# Engine dry weight: PW127-class ≈ 1,060 lb per engine
W_engine_dry = 1060.0  # lb per engine
n_engines = 2

# Component buildup (Anderson Eqs. 8.83a–g, adapted for transport category)
# For a pressurized turboprop transport, we use slightly higher factors:
# Wing: 2.5 lb/ft² exposed (Anderson Eq. 8.83a) — increase to 3.5 for pressurized/larger
# HT: 2.0 → 2.5 for T-tail
# VT: 2.0 → 2.5 for T-tail structural penalty
# Fuselage: 1.4 → 2.0 for pressurized fuselage
# Landing gear: 0.057 W_0 → 0.043 W_0 (retractable, transport)
# Installed engine: 1.4 × dry weight
# All else empty: 0.17 W_0 (avionics, furnishings, anti-ice, pressurization, etc.)

factor_wing = 3.5       # lb/ft² (heavier for transport-category structure)
factor_HT = 2.5         # lb/ft² (T-tail)
factor_VT = 2.5         # lb/ft²
factor_fuse = 2.0        # lb/ft² wetted (pressurized)
factor_gear = 0.043      # fraction of W_0
factor_engine = 1.4      # installed/dry
factor_allelse = 0.17    # fraction of W_0

print(f"\n  Component weight factors (based on Anderson Eq. 8.83, adapted for")
print(f"  pressurized twin turboprop transport):")
print(f"    Wing:     {factor_wing} lb/ft² × S_exp = {factor_wing} × {S_wing_exposed:.0f} ft²")
print(f"    HT:       {factor_HT} lb/ft² × S_exp = {factor_HT} × {S_HT_exposed:.0f} ft²")
print(f"    VT:       {factor_VT} lb/ft² × S_exp = {factor_VT} × {S_VT_exposed:.0f} ft²")
print(f"    Fuselage: {factor_fuse} lb/ft² × S_wet = {factor_fuse} × {S_wet_fuse:.0f} ft²")
print(f"    L. Gear:  {factor_gear} × W_0")
print(f"    Engine:   {factor_engine} × {W_engine_dry:.0f} lb × {n_engines} engines")
print(f"    All else: {factor_allelse} × W_0")

# Iterative weight calculation (Anderson §8.7)
print(f"\n  Iterative convergence (Anderson §8.7):")
print(f"  {'Iter':>4s} {'W_wing':>8s} {'W_HT':>7s} {'W_VT':>7s} {'W_fuse':>8s} "
      f"{'W_gear':>7s} {'W_eng':>8s} {'W_else':>8s} {'W_e':>8s} {'W_f':>8s} {'W_0':>8s}")

W0_iter = W0  # start from first estimate
for iteration in range(20):
    W_wing_comp = factor_wing * S_wing_exposed
    W_HT_comp = factor_HT * S_HT_exposed
    W_VT_comp = factor_VT * S_VT_exposed
    W_fuse_comp = factor_fuse * S_wet_fuse
    W_gear_comp = factor_gear * W0_iter
    W_eng_comp = factor_engine * W_engine_dry * n_engines
    W_allelse_comp = factor_allelse * W0_iter

    W_e_new = (W_wing_comp + W_HT_comp + W_VT_comp + W_fuse_comp +
               W_gear_comp + W_eng_comp + W_allelse_comp)

    W_f_new = Wf_W0 * W0_iter

    W0_new = W_crew + W_payload + W_f_new + W_e_new

    if iteration < 8 or abs(W0_new - W0_iter) < 1.0:
        print(f"  {iteration+1:4d} {W_wing_comp:8.0f} {W_HT_comp:7.0f} {W_VT_comp:7.0f} "
              f"{W_fuse_comp:8.0f} {W_gear_comp:7.0f} {W_eng_comp:8.0f} {W_allelse_comp:8.0f} "
              f"{W_e_new:8.0f} {W_f_new:8.0f} {W0_new:8.0f}")

    if abs(W0_new - W0_iter) < 1.0:
        break
    W0_iter = W0_new

W0_refined = W0_new
W_e_refined = W_e_new
W_f_refined = Wf_W0 * W0_refined
We_W0_refined = W_e_refined / W0_refined

print(f"\n  ╔══════════════════════════════════════════════════╗")
print(f"  ║  REFINED WEIGHT ESTIMATE (Converged)             ║")
print(f"  ╠══════════════════════════════════════════════════╣")
print(f"  ║  W_0 (TOGW)     = {W0_refined:>8.0f} lb                   ║")
print(f"  ║  W_empty         = {W_e_refined:>8.0f} lb                   ║")
print(f"  ║  W_fuel          = {W_f_refined:>8.0f} lb                   ║")
print(f"  ║  W_crew          = {W_crew:>8.0f} lb                   ║")
print(f"  ║  W_payload       = {W_payload:>8.0f} lb                   ║")
print(f"  ║  W_e/W_0         = {We_W0_refined:>8.4f}                    ║")
print(f"  ╚══════════════════════════════════════════════════╝")

# Compare with initial estimate
print(f"\n  Comparison with first estimate:")
print(f"    First estimate W_0 = {W0:.0f} lb")
print(f"    Refined W_0        = {W0_refined:.0f} lb")
print(f"    Difference         = {W0_refined - W0:.0f} lb ({(W0_refined-W0)/W0*100:+.1f}%)")

# Update key parameters for performance verification
S_wing_final = W0_refined / WS_design
b_wing_final = math.sqrt(AR_wing * S_wing_final)
c_root_final = 2.0 * S_wing_final / ((1.0 + lambda_wing) * b_wing_final)
MAC_final = (2.0/3.0) * c_root_final * (1.0 + lambda_wing + lambda_wing**2) / (1.0 + lambda_wing)

# Recalculate T/W with refined weight
T_static_total = SHP_total_final * T_static_per_SHP
TW_refined = T_static_total / W0_refined

print(f"\n  Updated parameters with refined weight:")
print(f"    S = {S_wing_final:.1f} ft²")
print(f"    b = {b_wing_final:.2f} ft")
print(f"    T_0/W_0 = {TW_refined:.4f}")
print(f"    W/S = {WS_design:.1f} lb/ft² (unchanged)")

# =============================================================================
# PIVOT POINT 6: PERFORMANCE VERIFICATION  (Anderson §8.8)
# =============================================================================
print("\n" + "=" * 78)
print("  PIVOT POINT 6: PERFORMANCE VERIFICATION (Anderson §8.8)")
print("=" * 78)

W0_check = W0_refined
S_check = S_wing_final
WS_check = W0_check / S_check

# Use the refined weight for all checks
# Recalculate SHP needed
SHP_total_check = SHP_total_final

# ── CHECK 1: CRUISE SPEED ──
print(f"\n  ── CHECK 1: CRUISE SPEED ──")
rho_cr = isa_density(h_cruise)
q_cr = 0.5 * rho_cr * V_cruise_fps**2
CL_cruise = W0_check * 0.95 / (q_cr * S_check)  # midcruise weight
CD_cruise = CD0 + K * CL_cruise**2
LD_actual = CL_cruise / CD_cruise
D_cruise = q_cr * S_check * CD_cruise
T_req_cruise = D_cruise

# Available thrust at cruise altitude
# Turboprop: P_avail = P_SL × (rho/rho_SL)^0.7
sigma_cr = rho_cr / rho_SL
SHP_avail_cruise = SHP_total_check * sigma_cr**0.7
T_avail_cruise = eta_pr * SHP_avail_cruise * 550.0 / V_cruise_fps

print(f"    At {h_cruise:.0f} ft, V = {V_cruise_kt:.0f} kt:")
print(f"      C_L = {CL_cruise:.4f},  C_D = {CD_cruise:.5f}")
print(f"      L/D = {LD_actual:.2f}")
print(f"      Drag = {D_cruise:.0f} lb")
print(f"      Thrust required = {T_req_cruise:.0f} lb")
print(f"      Thrust available = {T_avail_cruise:.0f} lb")
if T_avail_cruise >= T_req_cruise:
    margin = (T_avail_cruise / T_req_cruise - 1.0) * 100
    print(f"      ✓ CRUISE SPEED MET — {margin:.1f}% thrust margin")
else:
    print(f"      ✗ CRUISE SPEED NOT MET")

# ── CHECK 2: RATE OF CLIMB AT SEA LEVEL ──
print(f"\n  ── CHECK 2: RATE OF CLIMB AT SEA LEVEL ──")
# Best climb speed
V_best_climb = math.sqrt(2.0 * WS_check / rho_SL * math.sqrt(K / CD0))
q_climb_sl = 0.5 * rho_SL * V_best_climb**2
CL_climb = W0_check / (q_climb_sl * S_check)
CD_climb = CD0 + K * CL_climb**2
D_climb = q_climb_sl * S_check * CD_climb

# Available power at sea level
P_avail_sl = eta_pr * SHP_total_check * 550.0  # ft·lb/s
T_avail_sl = P_avail_sl / V_best_climb

excess_power = (T_avail_sl - D_climb) * V_best_climb  # ft·lb/s
ROC_actual = excess_power / W0_check  # ft/s
ROC_actual_fpm = ROC_actual * 60.0

print(f"    Best climb speed: {V_best_climb:.1f} ft/s = {V_best_climb/1.6878:.0f} kt")
print(f"    T_avail (SL) = {T_avail_sl:.0f} lb")
print(f"    Drag at climb = {D_climb:.0f} lb")
print(f"    Excess thrust = {T_avail_sl - D_climb:.0f} lb")
print(f"    R/C = {ROC_actual_fpm:.0f} ft/min")
print(f"    Required: {ROC_min:.0f} ft/min")
if ROC_actual_fpm >= ROC_min:
    print(f"    ✓ CLIMB RATE MET — exceeds by {ROC_actual_fpm - ROC_min:.0f} ft/min")
else:
    print(f"    ✗ CLIMB RATE NOT MET — deficit of {ROC_min - ROC_actual_fpm:.0f} ft/min")

# ── CHECK 3: SERVICE CEILING ──
print(f"\n  ── CHECK 3: SERVICE CEILING ──")
# Find altitude where R/C = 100 ft/min
def calc_ROC(h, W, S, SHP_total):
    rho_h = isa_density(h)
    sigma_h = rho_h / rho_SL
    V_bc = math.sqrt(2.0 * (W/S) / rho_h * math.sqrt(K / CD0))
    q_h = 0.5 * rho_h * V_bc**2
    CL_h = W / (q_h * S)
    CD_h = CD0 + K * CL_h**2
    D_h = q_h * S * CD_h
    P_avail_h = eta_pr * SHP_total * sigma_h**0.7 * 550.0  # ft·lb/s
    T_avail_h = P_avail_h / V_bc
    ROC_h = (T_avail_h - D_h) * V_bc / W  # ft/s
    return ROC_h * 60.0  # ft/min

# Binary search for service ceiling
h_low, h_high = 20000, 45000
for _ in range(50):
    h_mid = (h_low + h_high) / 2.0
    roc_mid = calc_ROC(h_mid, W0_check, S_check, SHP_total_check)
    if roc_mid > 100.0:
        h_low = h_mid
    else:
        h_high = h_mid

h_service_ceiling = (h_low + h_high) / 2.0

print(f"    Service ceiling (R/C = 100 ft/min): {h_service_ceiling:.0f} ft")
print(f"    Required: {h_ceiling:.0f} ft")
if h_service_ceiling >= h_ceiling:
    print(f"    ✓ SERVICE CEILING MET — exceeds by {h_service_ceiling - h_ceiling:.0f} ft")
else:
    print(f"    ✗ SERVICE CEILING NOT MET — deficit of {h_ceiling - h_service_ceiling:.0f} ft")

# ── CHECK 4: TAKEOFF DISTANCE ──
print(f"\n  ── CHECK 4: TAKEOFF DISTANCE ──")
V_stall_TO = math.sqrt(2.0 * WS_check / (rho_SL * CL_max_TO))
V_LO = 1.1 * V_stall_TO
V_ref_TO = 0.7 * V_LO

# Ground roll (Anderson Eq. 6.95)
# T at 0.7 V_LO for turboprop
P_avail_TO = eta_pr * 0.70 * SHP_total_check * 550.0  # reduced eta at low speed
T_at_07VLO = P_avail_TO / V_ref_TO if V_ref_TO > 0 else T_static_total

s_g_TO = 1.21 * WS_check / (g * rho_SL * CL_max_TO * (T_at_07VLO / W0_check))

# Airborne distance (Anderson Eqs. 6.98–6.100)
R_TO = 6.96 * V_stall_TO**2 / g
theta_OB = math.acos(max(-1, min(1, 1.0 - 50.0 / R_TO)))
s_a_TO = R_TO * math.sin(theta_OB)
s_TO_total = s_g_TO + s_a_TO

print(f"    V_stall (TO config) = {V_stall_TO:.1f} ft/s = {V_stall_TO/1.6878:.0f} kt")
print(f"    V_LO = 1.1 × V_stall = {V_LO:.1f} ft/s")
print(f"    T at 0.7·V_LO = {T_at_07VLO:.0f} lb")
print(f"    Ground roll s_g = {s_g_TO:.0f} ft  [Anderson Eq. 6.95]")
print(f"    Airborne distance s_a = {s_a_TO:.0f} ft  [Anderson Eqs. 6.98–6.100]")
print(f"    Total TO distance = {s_TO_total:.0f} ft")
print(f"    Required: {s_TO_max:.0f} ft")
if s_TO_total <= s_TO_max:
    print(f"    ✓ TAKEOFF DISTANCE MET — margin of {s_TO_max - s_TO_total:.0f} ft")
else:
    print(f"    ✗ TAKEOFF DISTANCE NOT MET — exceeds by {s_TO_total - s_TO_max:.0f} ft")

# ── CHECK 5: LANDING DISTANCE ──
print(f"\n  ── CHECK 5: LANDING DISTANCE ──")
W_land = W_land_frac * W0_check
WS_land = W_land / S_check
V_stall_L = math.sqrt(2.0 * WS_land / (rho_SL * CL_max_land))
V_f_land = 1.23 * V_stall_L
theta_a_rad = math.radians(3.0)
R_flare = V_f_land**2 / (0.2 * g)
h_f = R_flare * (1.0 - math.cos(theta_a_rad))
s_a_land = (50.0 - h_f) / math.tan(theta_a_rad)
s_f_land = R_flare * math.sin(theta_a_rad)

# Ground roll (Anderson Eq. 8.28)
j_land = 1.15
N_land = 3.0
mu_r_land = 0.4
s_g_land = (j_land * N_land * math.sqrt(2.0 * WS_land / (rho_SL * CL_max_land)) +
            j_land**2 * WS_land / (g * rho_SL * CL_max_land * mu_r_land))
s_L_total = s_a_land + s_f_land + s_g_land

print(f"    Landing weight = {W_land:.0f} lb ({W_land_frac:.0f}×W_0)")
print(f"    V_stall (land config) = {V_stall_L:.1f} ft/s = {V_stall_L/1.6878:.0f} kt")
print(f"    Approach distance s_a = {s_a_land:.0f} ft")
print(f"    Flare distance s_f = {s_f_land:.0f} ft")
print(f"    Ground roll s_g = {s_g_land:.0f} ft  [Anderson Eq. 8.28]")
print(f"    Total landing distance = {s_L_total:.0f} ft")
print(f"    Required: {s_L_max:.0f} ft")
if s_L_total <= s_L_max:
    print(f"    ✓ LANDING DISTANCE MET — margin of {s_L_max - s_L_total:.0f} ft")
else:
    print(f"    ✗ LANDING DISTANCE NOT MET — exceeds by {s_L_total - s_L_max:.0f} ft")

# ── CHECK 6: RANGE ──
print(f"\n  ── CHECK 6: RANGE ──")
# Range using refined fuel weight and Breguet equation
# Available fuel for cruise = W_f - fuel for TO, climb, loiter, land
W_f_total = W_f_refined
W_after_TO_climb = W0_check * W1_W0 * W2_W1
W_f_cruise_available = W_f_total - (W0_check - W0_check * W5_W0) + \
                       W0_check * (1.0 - W1_W0) + W0_check * W1_W0 * (1.0 - W2_W1)
# Simpler: the Breguet fuel fraction already accounts for the mission profile
# The range is designed in, so verify the fuel fraction is consistent
W3_W0 = W1_W0 * W2_W1 * W3_W2
R_check = (eta_pr / c) * LD_actual * math.log(W2_W1 * W0_check * W1_W0 / (W3_W0 * W0_check / (W2_W1 * W1_W0)))
# Let's just recompute directly
W_begin_cruise = W0_check * W1_W0 * W2_W1
W_end_cruise = W_begin_cruise * W3_W2
R_computed_ft = (eta_pr / c) * LD_actual * math.log(W_begin_cruise / W_end_cruise)
R_computed_nmi = R_computed_ft / 6076.12

print(f"    Using actual L/D = {LD_actual:.2f} at cruise")
print(f"    W_begin_cruise = {W_begin_cruise:.0f} lb")
print(f"    W_end_cruise = {W_end_cruise:.0f} lb")
print(f"    Fuel burned in cruise = {W_begin_cruise - W_end_cruise:.0f} lb")
print(f"    Range (Breguet) = {R_computed_nmi:.0f} nmi")
print(f"    Required: {R_nmi:.0f} nmi + {loiter_min:.0f} min loiter (already in W_f/W_0)")
if R_computed_nmi >= R_nmi:
    print(f"    ✓ RANGE MET — exceeds by {R_computed_nmi - R_nmi:.0f} nmi")
else:
    print(f"    ✗ RANGE NOT MET — deficit of {R_nmi - R_computed_nmi:.0f} nmi")

# ── CHECK 7: STALL SPEED ──
print(f"\n  ── CHECK 7: APPROACH/STALL SPEED (FAR 25) ──")
V_stall_clean = math.sqrt(2.0 * WS_check / (rho_SL * CL_max_clean))
V_stall_land_full = math.sqrt(2.0 * WS_land / (rho_SL * CL_max_land))
V_ref = 1.3 * V_stall_land_full  # FAR 25 reference approach speed

print(f"    V_stall (clean) = {V_stall_clean:.1f} ft/s = {V_stall_clean/1.6878:.0f} kt")
print(f"    V_stall (landing, full flap) = {V_stall_land_full:.1f} ft/s = {V_stall_land_full/1.6878:.0f} kt")
print(f"    V_ref (1.3 V_s) = {V_ref:.1f} ft/s = {V_ref/1.6878:.0f} kt")

# =============================================================================
# PERFORMANCE SUMMARY
# =============================================================================
print("\n" + "=" * 78)
print("  PERFORMANCE VERIFICATION SUMMARY")
print("=" * 78)

checks = [
    ("Cruise Speed",    f"{V_cruise_kt:.0f} kt at {h_cruise:.0f} ft", T_avail_cruise >= T_req_cruise),
    ("Rate of Climb",   f"{ROC_actual_fpm:.0f} ft/min ≥ {ROC_min:.0f}", ROC_actual_fpm >= ROC_min),
    ("Service Ceiling", f"{h_service_ceiling:.0f} ft ≥ {h_ceiling:.0f}", h_service_ceiling >= h_ceiling),
    ("Takeoff Dist.",   f"{s_TO_total:.0f} ft ≤ {s_TO_max:.0f}", s_TO_total <= s_TO_max),
    ("Landing Dist.",   f"{s_L_total:.0f} ft ≤ {s_L_max:.0f}", s_L_total <= s_L_max),
    ("Range",           f"{R_computed_nmi:.0f} nmi ≥ {R_nmi:.0f}", R_computed_nmi >= R_nmi),
]

all_pass = True
for name, detail, passed in checks:
    status = "✓ PASS" if passed else "✗ FAIL"
    if not passed:
        all_pass = False
    print(f"  {status}  {name:18s}  {detail}")

if all_pass:
    print(f"\n  ═══ ALL REQUIREMENTS MET — NO ITERATION NEEDED ═══")
else:
    print(f"\n  ═══ SOME REQUIREMENTS NOT MET — ITERATION REQUIRED ═══")

# =============================================================================
# PIVOT POINT 7: ITERATION & OPTIMIZATION  (Anderson §7.3.6–7.3.7)
# =============================================================================
print("\n" + "=" * 78)
print("  PIVOT POINT 7: DESIGN ITERATION & OPTIMIZATION")
print("  (Anderson §7.3.6–7.3.7)")
print("=" * 78)

if not all_pass:
    print("\n  Range fell short because actual cruise L/D = {:.2f} < design assumption {:.1f}.".format(
        LD_actual, LD_cruise))
    print("  Re-sizing with actual aerodynamics (Anderson §7.3.6: iterate Pivot Points 3→6).")
    print()

    # ── ITERATION: recalculate fuel fraction with ACTUAL cruise L/D ──
    for design_iter in range(1, 6):
        print(f"  ── Design Iteration {design_iter} ──")

        # Use actual cruise L/D for Breguet
        LD_iter = LD_actual  # from performance check
        ln_W2_W3_iter = c * R_ft / (eta_pr * LD_iter)
        W3_W2_iter = 1.0 / math.exp(ln_W2_W3_iter)

        # Loiter with actual L/D (slightly less than max for loiter)
        LD_loiter_iter = LD_max * 0.95  # fly near (L/D)max for loiter
        ln_W3_W4_iter = c * R_loiter_ft / (eta_pr * LD_loiter_iter)
        W4_W3_iter = 1.0 / math.exp(ln_W3_W4_iter)

        W5_W0_iter = W1_W0 * W2_W1 * W3_W2_iter * W4_W3_iter * W5_W4
        Wf_W0_iter = 1.06 * (1.0 - W5_W0_iter)

        # Recalculate W_0 with the new fuel fraction
        W0_iter2 = (W_crew + W_payload) / (1.0 - Wf_W0_iter - We_W0)
        print(f"    L/D cruise = {LD_iter:.2f}, W_f/W_0 = {Wf_W0_iter:.4f}, W_0 (first est.) = {W0_iter2:.0f} lb")

        # Update wing area
        S_iter = W0_iter2 / WS_design

        # Re-run component weight buildup
        S_wing_exp_iter = S_iter - d_fuse * (2.0 * S_iter / ((1.0 + lambda_wing) * math.sqrt(AR_wing * S_iter)))
        b_iter = math.sqrt(AR_wing * S_iter)
        cr_iter = 2.0 * S_iter / ((1.0 + lambda_wing) * b_iter)
        MAC_iter = (2.0/3.0) * cr_iter * (1.0 + lambda_wing + lambda_wing**2) / (1.0 + lambda_wing)

        # Empennage (re-scale with new wing)
        S_HT_iter = V_HT * MAC_iter * S_iter / l_HT
        S_VT_iter = V_VT * b_iter * S_iter / l_VT

        W0_conv = W0_iter2
        for sub_iter in range(20):
            W_wing_i = factor_wing * S_wing_exp_iter
            W_HT_i = factor_HT * S_HT_iter * 0.95
            W_VT_i = factor_VT * S_VT_iter * 0.93
            W_fuse_i = factor_fuse * S_wet_fuse
            W_gear_i = factor_gear * W0_conv
            W_eng_i = factor_engine * W_engine_dry * n_engines
            W_allelse_i = factor_allelse * W0_conv
            W_e_i = W_wing_i + W_HT_i + W_VT_i + W_fuse_i + W_gear_i + W_eng_i + W_allelse_i
            W_f_i = Wf_W0_iter * W0_conv
            W0_new_i = W_crew + W_payload + W_f_i + W_e_i
            if abs(W0_new_i - W0_conv) < 1.0:
                break
            W0_conv = W0_new_i

        print(f"    Component buildup converged: W_0 = {W0_conv:.0f} lb, W_e = {W_e_i:.0f} lb, W_f = {W_f_i:.0f} lb")

        # Update performance check with converged weight
        S_final_iter = W0_conv / WS_design
        q_cr_iter = 0.5 * rho_cruise * V_cruise_fps**2
        CL_cruise_iter = W0_conv * 0.95 / (q_cr_iter * S_final_iter)
        CD_cruise_iter = CD0 + K * CL_cruise_iter**2
        LD_actual_iter = CL_cruise_iter / CD_cruise_iter

        # Check range with actual L/D
        W_bc_iter = W0_conv * W1_W0 * W2_W1
        W_ec_iter = W_bc_iter * W3_W2_iter
        R_iter_ft = (eta_pr / c) * LD_actual_iter * math.log(W_bc_iter / W_ec_iter)
        R_iter_nmi = R_iter_ft / 6076.12

        print(f"    Actual cruise L/D = {LD_actual_iter:.2f}, Range = {R_iter_nmi:.0f} nmi (req: {R_nmi:.0f})")

        if abs(LD_actual_iter - LD_iter) < 0.1 and R_iter_nmi >= R_nmi:
            print(f"    ✓ Converged! Range requirement met.")

            # Update all final values
            W0_refined = W0_conv
            W_e_refined = W_e_i
            W_f_refined = W_f_i
            We_W0_refined = W_e_refined / W0_refined
            Wf_W0 = Wf_W0_iter
            S_wing_final = S_final_iter
            b_wing_final = math.sqrt(AR_wing * S_wing_final)
            c_root_final = 2.0 * S_wing_final / ((1.0 + lambda_wing) * b_wing_final)
            MAC_final = (2.0/3.0) * c_root_final * (1.0 + lambda_wing + lambda_wing**2) / (1.0 + lambda_wing)
            TW_refined = T_static_total / W0_refined
            LD_actual = LD_actual_iter
            R_computed_nmi = R_iter_nmi

            # Re-run all performance checks with updated weight
            W0_check = W0_refined
            S_check = S_wing_final
            WS_check = W0_check / S_check
            SHP_total_check = SHP_total_final

            # Recalculate all performance
            CL_cruise = CL_cruise_iter
            CD_cruise = CD_cruise_iter

            T_avail_cruise = eta_pr * SHP_total_check * sigma_cruise**0.7 * 550.0 / V_cruise_fps
            T_req_cruise = q_cr_iter * S_check * CD_cruise

            V_best_climb2 = math.sqrt(2.0 * WS_check / rho_SL * math.sqrt(K / CD0))
            q_climb_sl2 = 0.5 * rho_SL * V_best_climb2**2
            D_climb2 = q_climb_sl2 * S_check * (CD0 + K * (W0_check / (q_climb_sl2 * S_check))**2)
            P_avail_sl2 = eta_pr * SHP_total_check * 550.0
            T_avail_sl2 = P_avail_sl2 / V_best_climb2
            ROC_actual_fpm = (T_avail_sl2 - D_climb2) * V_best_climb2 / W0_check * 60.0

            h_service_ceiling = h_low  # reuse from earlier (conservative)
            h_low2, h_high2 = 20000, 45000
            for _ in range(50):
                h_mid2 = (h_low2 + h_high2) / 2.0
                roc_m = calc_ROC(h_mid2, W0_check, S_check, SHP_total_check)
                if roc_m > 100.0:
                    h_low2 = h_mid2
                else:
                    h_high2 = h_mid2
            h_service_ceiling = (h_low2 + h_high2) / 2.0

            V_stall_TO2 = math.sqrt(2.0 * WS_check / (rho_SL * CL_max_TO))
            V_LO2 = 1.1 * V_stall_TO2
            V_ref_TO2 = 0.7 * V_LO2
            P_avail_TO2 = eta_pr * 0.70 * SHP_total_check * 550.0
            T_at_07VLO2 = P_avail_TO2 / V_ref_TO2
            s_g_TO2 = 1.21 * WS_check / (g * rho_SL * CL_max_TO * (T_at_07VLO2 / W0_check))
            R_TO2 = 6.96 * V_stall_TO2**2 / g
            theta_OB2 = math.acos(max(-1, min(1, 1.0 - 50.0 / R_TO2)))
            s_a_TO2 = R_TO2 * math.sin(theta_OB2)
            s_TO_total = s_g_TO2 + s_a_TO2

            W_land2 = W_land_frac * W0_check
            WS_land2 = W_land2 / S_check
            V_stall_L2 = math.sqrt(2.0 * WS_land2 / (rho_SL * CL_max_land))
            V_f_land2 = 1.23 * V_stall_L2
            R_flare2 = V_f_land2**2 / (0.2 * g)
            h_f2 = R_flare2 * (1.0 - math.cos(math.radians(3.0)))
            s_a_land2 = (50.0 - h_f2) / math.tan(math.radians(3.0))
            s_f_land2 = R_flare2 * math.sin(math.radians(3.0))
            s_g_land2 = (1.15 * 3.0 * math.sqrt(2.0 * WS_land2 / (rho_SL * CL_max_land)) +
                        1.15**2 * WS_land2 / (g * rho_SL * CL_max_land * 0.4))
            s_L_total = s_a_land2 + s_f_land2 + s_g_land2

            # Stall/approach speed
            V_stall_land_full = V_stall_L2
            V_ref = 1.3 * V_stall_land_full
            V_stall_clean = math.sqrt(2.0 * WS_check / (rho_SL * CL_max_clean))

            # Empennage update
            S_HT = V_HT * MAC_final * S_wing_final / l_HT
            S_VT = V_VT * b_wing_final * S_wing_final / l_VT
            b_HT = math.sqrt(AR_HT * S_HT)
            cr_HT = 2.0 * S_HT / ((1.0 + lambda_HT) * b_HT)
            ct_HT = lambda_HT * cr_HT
            h_VT = math.sqrt(AR_VT * S_VT)
            cr_VT = 2.0 * S_VT / ((1.0 + lambda_VT) * h_VT)
            ct_VT = lambda_VT * cr_VT

            break

        # Update L/D for next iteration
        LD_actual = LD_actual_iter

    # Print updated performance summary
    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║  ITERATED DESIGN (Anderson §7.3.6)               ║")
    print(f"  ╠══════════════════════════════════════════════════╣")
    print(f"  ║  W_0 = {W0_refined:>8.0f} lb                          ║")
    print(f"  ║  W_e = {W_e_refined:>8.0f} lb  (W_e/W_0 = {We_W0_refined:.3f})     ║")
    print(f"  ║  W_f = {W_f_refined:>8.0f} lb  (W_f/W_0 = {Wf_W0:.4f})    ║")
    print(f"  ║  S   = {S_wing_final:>8.1f} ft²                       ║")
    print(f"  ║  b   = {b_wing_final:>8.2f} ft                        ║")
    print(f"  ╚══════════════════════════════════════════════════╝")

    checks = [
        ("Cruise Speed",    f"{V_cruise_kt:.0f} kt at {h_cruise:.0f} ft", T_avail_cruise >= T_req_cruise),
        ("Rate of Climb",   f"{ROC_actual_fpm:.0f} ft/min ≥ {ROC_min:.0f}", ROC_actual_fpm >= ROC_min),
        ("Service Ceiling", f"{h_service_ceiling:.0f} ft ≥ {h_ceiling:.0f}", h_service_ceiling >= h_ceiling),
        ("Takeoff Dist.",   f"{s_TO_total:.0f} ft ≤ {s_TO_max:.0f}", s_TO_total <= s_TO_max),
        ("Landing Dist.",   f"{s_L_total:.0f} ft ≤ {s_L_max:.0f}", s_L_total <= s_L_max),
        ("Range",           f"{R_computed_nmi:.0f} nmi ≥ {R_nmi:.0f}", R_computed_nmi >= R_nmi),
    ]
    print(f"\n  UPDATED PERFORMANCE VERIFICATION:")
    all_pass = True
    for name, detail, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        if not passed:
            all_pass = False
        print(f"    {status}  {name:18s}  {detail}")

    if all_pass:
        print(f"\n  ═══ ALL REQUIREMENTS NOW MET AFTER ITERATION ═══")

else:
    print("\n  Design meets all requirements. Proceeding to final summary.")

# =============================================================================
# FINAL DESIGN SUMMARY
# =============================================================================
print("\n" + "=" * 78)
print("  FINAL DESIGN SUMMARY")
print("  30-Passenger Twin Turboprop Regional Airliner")
print("=" * 78)

print(f"""
  WEIGHTS
  ───────────────────────────────────────
  Max Takeoff Weight (MTOW)    {W0_refined:>8.0f} lb
  Empty Weight                 {W_e_refined:>8.0f} lb
  Fuel Weight                  {W_f_refined:>8.0f} lb
  Payload (30 pax)             {W_payload:>8.0f} lb
  Crew (3)                     {W_crew:>8.0f} lb
  W_e/W_0                      {We_W0_refined:>8.3f}
  W_f/W_0                      {Wf_W0:>8.3f}

  POWERPLANT
  ───────────────────────────────────────
  Engines               2 × Turboprop (PW127 class)
  SHP per engine                {SHP_per_engine_final:>5d} hp
  Total SHP                     {SHP_total_final:>5d} hp
  Propeller             {n_blades}-blade, D = {D_prop_ft:.1f} ft ({D_prop_in:.0f} in)
  Propeller RPM                 {RPM:>5d}
  T_0/W_0                      {TW_refined:>8.4f}

  WING
  ───────────────────────────────────────
  Wing area S            {S_wing_final:>8.1f} ft²
  Wingspan b             {b_wing_final:>8.2f} ft
  Aspect ratio AR        {AR_wing:>8.1f}
  Taper ratio λ          {lambda_wing:>8.2f}
  Sweep Λ_c/4            {sweep_c4:>8.0f}°
  Root chord             {c_root_final:>8.2f} ft
  Tip chord              {lambda_wing * c_root_final:>8.2f} ft
  MAC                    {MAC_final:>8.2f} ft
  W/S                    {WS_check:>8.1f} lb/ft²
  Airfoil                {airfoil_root} / {airfoil_tip}
  Position               {wing_position}, {dihedral:.0f}° dihedral
  High-lift devices      Double-slotted Fowler flaps

  FUSELAGE
  ───────────────────────────────────────
  Length                 {L_fuse:>8.1f} ft
  External diameter      {d_fuse:>8.1f} ft
  Fineness ratio L/d     {fineness_ratio:>8.2f}
  Seating                {seats_per_row}-abreast, {n_rows} rows, {seat_pitch_in:.0f}" pitch
  Pressurized cabin      Yes (FAR 25)

  EMPENNAGE
  ───────────────────────────────────────
  Configuration          T-tail
  HT area S_HT           {S_HT:>7.1f} ft²
  HT span b_HT           {b_HT:>7.2f} ft
  HT AR / λ              {AR_HT:.1f} / {lambda_HT:.2f}
  VT area S_VT            {S_VT:>7.1f} ft²
  VT height h_VT          {h_VT:>7.2f} ft
  VT AR / λ               {AR_VT:.1f} / {lambda_VT:.2f}
  V_HT / V_VT            {V_HT:.2f} / {V_VT:.2f}

  LANDING GEAR
  ───────────────────────────────────────
  Configuration          Tricycle, retractable
  Main wheels            Dual per strut, {d_main:.0f}" dia
  Nose wheels            Twin, {d_nose:.0f}" dia
  Wheelbase              {x3:.1f} ft

  AERODYNAMICS
  ───────────────────────────────────────
  C_D0                   {CD0:>8.4f}
  K                      {K:>8.5f}
  (L/D)_max              {LD_max:>8.2f}
  L/D at cruise          {LD_actual:>8.2f}
  (C_L)max clean         {CL_max_clean:>8.2f}
  (C_L)max takeoff       {CL_max_TO:>8.2f}
  (C_L)max landing       {CL_max_land:>8.2f}

  PERFORMANCE
  ───────────────────────────────────────
  Cruise speed           {V_cruise_kt:>5.0f} kt at {h_cruise:.0f} ft (M {M_cruise:.3f})
  Max R/C (SL)           {ROC_actual_fpm:>5.0f} ft/min
  Service ceiling        {h_service_ceiling:>5.0f} ft
  Takeoff dist. (50 ft)  {s_TO_total:>5.0f} ft
  Landing dist. (50 ft)  {s_L_total:>5.0f} ft
  Range + reserves       {R_computed_nmi:>5.0f} nmi (+ {loiter_min:.0f} min loiter)
  V_stall (land config)  {V_stall_land_full/1.6878:>5.0f} kt
  V_ref (1.3 V_s)        {V_ref/1.6878:>5.0f} kt
""")

print("=" * 78)
print("  REFERENCES")
print("=" * 78)
print("""
  [1] Anderson, J.D., "Aircraft Performance and Design," McGraw-Hill, 1999.
      - Chapter 7: The Philosophy of Airplane Design (§7.3, Seven Pivot Points)
      - Chapter 8: Design of a Propeller-Driven Airplane
        §8.2  Requirements
        §8.3  Weight Estimation (Eqs. 8.1–8.8, Fig. 8.1)
        §8.4  Critical Performance Parameters (Eqs. 8.24–8.38)
        §8.6  Configuration Layout (Eqs. 8.55–8.82)
        §8.7  Better Weight Estimate (Eqs. 8.83a–g)
        §8.8  Performance Analysis
      - Chapter 5: §5.13.1 Breguet Range (Eq. 5.153), §5.4.1 (L/D)max (Eq. 5.30)
      - Chapter 6: §6.7 Takeoff (Eq. 6.95), §6.8 Landing (Eq. 6.123)
      - Chapter 3: §3.6 Turboprop Characteristics
  [2] Raymer, D.P., "Aircraft Design: A Conceptual Approach," AIAA, various editions.
      - Weight estimation, tail volume coefficients, propeller sizing
  [3] Comparable aircraft: ATR-42/72, Dash 8 Q300, Saab 340/2000, Embraer EMB 120
""")
