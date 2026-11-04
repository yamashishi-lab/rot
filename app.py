import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbital Architect Pro: Photoreal Launch Broadcast", layout="wide")

st.title("🚀 Orbital Architect Pro - Extreme Rocket Engineering & Live Broadcast")
st.markdown("NASA / SpaceX official webcast experience. 1:1 Real-time simulation, authentic ATC radio comms, photorealistic coastal launch complex.")

# --- パーツデータベース ---
PROPELLANTS = {
    "RP-1 (Kerosene) / LOX [Dense / Atmospheric Booster]": {"base_isp_sl": 285, "base_isp_vac": 312, "base_thrust": 900, "density": 1.02, "temp_factor": 1.0, "flame_color": "0xffaa33"},
    "LCH4 (Methane) / LOX [Next-Gen Raptor Balance]": {"base_isp_sl": 325, "base_isp_vac": 360, "base_thrust": 1800, "density": 0.82, "temp_factor": 1.1, "flame_color": "0x44bbff"},
    "LH2 (Hydrogen) / LOX [Ultimate ISP / Huge Tank]": {"base_isp_sl": 340, "base_isp_vac": 445, "base_thrust": 1100, "density": 0.32, "temp_factor": 0.9, "flame_color": "0xff7733"}
}

PUMP_CYCLES = {
    "Gas Generator (GG) [Merlin style / Light & Reliable]": {"isp_mod": 0.96, "thrust_mod": 0.95, "mass_mod": 0.85, "max_pressure_limit": 140},
    "Expander Cycle [Upper stage only / Clean ISP]": {"isp_mod": 1.03, "thrust_mod": 0.65, "mass_mod": 1.0, "max_pressure_limit": 100},
    "Staged Combustion (SC) [High Power / Heavy]": {"isp_mod": 1.02, "thrust_mod": 1.15, "mass_mod": 1.20, "max_pressure_limit": 240},
    "Full-Flow Staged Combustion (FFSC) [Raptor Extreme]": {"isp_mod": 1.05, "thrust_mod": 1.35, "mass_mod": 1.30, "max_pressure_limit": 300}
}

MATERIALS = {
    "A2195 Aluminum-Lithium (Falcon 9 / Painted White)": {"base_dry_ratio": 0.065, "max_q_base": 45.0, "max_g_base": 6.0, "mat_id": "al"},
    "Torayca Carbon Composite (Electron / Matte Black)": {"base_dry_ratio": 0.042, "max_q_base": 34.0, "max_g_base": 5.2, "mat_id": "cf"},
    "304L Cold-Rolled Stainless (Starship / Bare Mirror Steel)": {"base_dry_ratio": 0.095, "max_q_base": 85.0, "max_g_base": 9.5, "mat_id": "ss"}
}

FAIRINGS = {
    "Standard Ogive Fairing (1,800K Rated)": {"mass": 1.8, "cd": 0.32, "heat_limit": 1800, "shape_id": "ogive"},
    "Sharp Needle Fairing (Low drag / 1,450K Tip limit)": {"mass": 1.4, "cd": 0.22, "heat_limit": 1450, "shape_id": "needle"},
    "Blunt Heavy Payload Fairing (2,400K High Thermal)": {"mass": 2.6, "cd": 0.46, "heat_limit": 2400, "shape_id": "blunt"}
}

PRESSURIZATION = {
    "Helium High-Pressure COPV Bottle": {"mass_penalty": 0.008, "g_bonus": 1.15},
    "Autogenous Self-Pressurization": {"mass_penalty": 0.002, "g_bonus": 0.90}
}

# --- UIタブ ---
tab1, tab2, tab3 = st.tabs(["🔥 Stage 1 (Booster)", "🛰️ Stage 2 & Payload", "📐 Flight Profile & Guidance"])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### Booster Propulsion")
        s1_prop = st.selectbox("Stage 1 Propellant", list(PROPELLANTS.keys()), index=1)
        s1_cycle = st.selectbox("Stage 1 Turbopump Cycle", list(PUMP_CYCLES.keys()), index=3)
        s1_eng_count = st.slider("Booster Engine Cluster Count", 1, 12, 4)
    with c2:
        st.markdown("#### Chamber & Nozzle")
        s1_pc = st.slider("Chamber Pressure Pc (bar)", 50, 350, 230, step=10)
        s1_eps = st.slider("Nozzle Expansion Ratio (ε)", 10, 80, 28, step=2)
        s1_tvc = st.slider("TVC Gimbal Max Angle (deg)", 2, 15, 8)
    with c3:
        st.markdown("#### Tank & Structure")
        s1_fuel = st.slider("Stage 1 Propellant Mass (tons)", 30.0, 500.0, 220.0, step=10.0)
        s1_mat = st.selectbox("Stage 1 Hull Material", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("Tank Wall Thickness (mm eq)", 1.5, 6.0, 3.0, step=0.2)
        s1_press = st.selectbox("Pressurization System", list(PRESSURIZATION.keys()), index=1)

with tab2:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### Stage 2 Propulsion")
        s2_prop = st.selectbox("Stage 2 Propellant", list(PROPELLANTS.keys()), index=2)
        s2_cycle = st.selectbox("Stage 2 Turbopump Cycle", list(PUMP_CYCLES.keys()), index=1)
        s2_eng_count = st.slider("Vacuum Engine Count", 1, 4, 1)
        s2_pc = st.slider("Stage 2 Chamber Pressure (bar)", 30, 250, 85, step=5)
        s2_eps = st.slider("Stage 2 Vacuum Expansion Ratio (ε)", 30, 200, 110, step=5)
    with c2:
        st.markdown("#### Stage 2 Structure")
        s2_fuel = st.slider("Stage 2 Propellant Mass (tons)", 5.0, 120.0, 42.0, step=1.0)
        s2_mat = st.selectbox("Stage 2 Material", list(MATERIALS.keys()), index=1)
        s2_thick = st.slider("Stage 2 Wall Thickness (mm)", 1.0, 5.0, 2.2, step=0.2)
    with c3:
        st.markdown("#### Payload & Fairing")
        fairing_type = st.selectbox("Fairing Aerodynamic Profile", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("Fairing Jettison Altitude (km)", 40.0, 150.0, 85.0, step=5.0)
        payload_mass = st.slider("Satellite Payload Mass (tons)", 0.5, 25.0, 4.5, step=0.5)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Gravity Turn Trajectory")
        turn_start_alt = st.slider("Pitchover Start Alt (km)", 1.0, 20.0, 4.5, step=0.5)
        turn_end_alt = st.slider("Horizontal Burn Alt (km)", 60.0, 180.0, 115.0, step=5.0)
        turn_exponent = st.slider("Turn Curvature Exponent", 0.4, 1.5, 0.80, step=0.05)
    with c2:
        st.markdown("#### Throttle & Structural Safety")
        throttle_maxq = st.slider("Max-Q Throttle Deep Cut (%)", 40, 100, 72)
        max_g_limit_cut = st.slider("G-Limiter Throttle (G)", 3.0, 10.0, 4.8, step=0.2)

def calc_stage_specs(prop_key, cycle_key, pc, eps, eng_count, fuel_mass, mat_key, thick, press_key=None):
    prop = PROPELLANTS[prop_key]
    cyc = PUMP_CYCLES[cycle_key]
    mat = MATERIALS[mat_key]

    pc_factor = 1.0 + (pc - 100.0) * 0.0006
    eps_vac_bonus = 1.0 + np.log10(eps / 25.0) * 0.08
    overexpansion_penalty = max(0.0, (eps - 35.0) * 0.006)

    isp_sl = prop["base_isp_sl"] * cyc["isp_mod"] * pc_factor * (1.0 - overexpansion_penalty)
    isp_vac = prop["base_isp_vac"] * cyc["isp_mod"] * pc_factor * eps_vac_bonus

    thrust_vac_per_eng = prop["base_thrust"] * cyc["thrust_mod"] * (pc / 150.0) ** 0.65
    thrust_sl_per_eng = thrust_vac_per_eng * (isp_sl / isp_vac)

    density_penalty = (1.0 / prop["density"]) ** 0.35
    thick_factor = thick / 3.0
    press_mass = PRESSURIZATION[press_key]["mass_penalty"] if press_key else 0.004
    press_g_mod = PRESSURIZATION[press_key]["g_bonus"] if press_key else 1.0

    dry_ratio = mat["base_dry_ratio"] * density_penalty * thick_factor + press_mass
    eng_mass = (thrust_vac_per_eng / 650.0) * cyc["mass_mod"] * (1.0 + eps * 0.003) * eng_count
    dry_mass = fuel_mass * dry_ratio + eng_mass

    max_q_resistance = mat["max_q_base"] * (thick_factor ** 1.1)
    max_g_resistance = mat["max_g_base"] * (thick_factor ** 0.85) * press_g_mod

    return {
        "isp_sl": float(isp_sl), "isp_vac": float(isp_vac),
        "thrust_sl": float(thrust_sl_per_eng * eng_count),
        "thrust_vac": float(thrust_vac_per_eng * eng_count),
        "dry_mass": float(dry_mass),
        "max_q": float(max_q_resistance),
        "max_g": float(max_g_resistance),
        "pc": pc, "pc_limit": cyc["max_pressure_limit"], "eps": eps,
        "cd_mod": density_penalty,
        "mat_id": mat["mat_id"],
        "flame_color": prop["flame_color"],
        "eng_count": eng_count
    }

s1_spec = calc_stage_specs(s1_prop, s1_cycle, s1_pc, s1_eps, s1_eng_count, s1_fuel, s1_mat, s1_thick, s1_press)
s2_spec = calc_stage_specs(s2_prop, s2_cycle, s2_pc, s2_eps, s2_eng_count, s2_fuel, s2_mat, s2_thick)
fair_spec = FAIRINGS[fairing_type]

total_s2_wet = s2_fuel + s2_spec["dry_mass"] + payload_mass + fair_spec["mass"]
total_s1_wet = s1_fuel + s1_spec["dry_mass"] + total_s2_wet

twr_init = s1_spec["thrust_sl"] / (total_s1_wet * 9.80665)
dv_s1 = s1_spec["isp_sl"] * 9.80665 * np.log(total_s1_wet / (total_s1_wet - s1_fuel))
dv_s2 = s2_spec["isp_vac"] * 9.80665 * np.log((total_s2_wet - fair_spec["mass"]) / (s2_spec["dry_mass"] + payload_mass))
total_dv = dv_s1 + dv_s2

# --- サマリーメトリクス ---
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Mass / Initial TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f}")
m2.metric("Total Theoretical ΔV", f"{total_dv:.0f} m/s", f"S1:{dv_s1:.0f} / S2:{dv_s2:.0f}")
m3.metric("Booster Max-Q / G-Limit", f"{s1_spec['max_q']:.1f} kPa", f"Limit: {s1_spec['max_g']:.1f} G")
m4.metric("Liftoff Thrust (Sea Level)", f"{s1_spec['thrust_sl']:.0f} kN", f"Isp: {s1_spec['isp_sl']:.0f} s")

# --- 物理計算エンジン ---
def run_simulation():
    dt = 0.5
    g0 = 9.80665
    R_earth = 6371000.0

    x, y = 0.0, R_earth
    vx, vy = 0.0, 0.0
    stage = 1
    fuel_rem = float(s1_fuel * 1000.0)
    fairing_attached = True

    history = []
    fail_reason = None

    # T-10s カウントダウン
    for cd_step in range(20):
        t_cd = -10.0 + cd_step * 0.5
        pre_ignition = bool(t_cd >= -3.0)
        history.append({
            "t": float(t_cd), "x": 0.0, "y": float(R_earth), "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "temp": 288.0, "stage": 1, "fairing": True,
            "exploded": False, "thrust": pre_ignition, "pitch": 0.0, "event": "COUNTDOWN"
        })

    # 発射台ハードウェアリミット
    if s1_spec["pc"] > s1_spec["pc_limit"]:
        fail_reason = "Catastrophic turbopump burst due to overpressure on pad."
        history.append({
            "t": 0.2, "x": 0.0, "y": float(R_earth + 2.0), "alt": 0.002, "v": 2.0,
            "q": 0.0, "g": 0.0, "temp": 1800.0, "stage": 1, "fairing": True,
            "exploded": True, "thrust": False, "pitch": 0.0, "event": "RUD_PAD"
        })
        return history, fail_reason

    if s1_spec["eps"] > 55:
        fail_reason = "Nozzle torn apart by sea-level flow separation and severe shockwave chatter."
        history.append({
            "t": 0.5, "x": 0.0, "y": float(R_earth + 12.0), "alt": 0.012, "v": 8.0,
            "q": 0.1, "g": 1.2, "temp": 1600.0, "stage": 1, "fairing": True,
            "exploded": True, "thrust": False, "pitch": 0.0, "event": "RUD_PAD"
        })
        return history, fail_reason

    if twr_init <= 1.02:
        fail_reason = "Insufficient thrust-to-weight ratio to clear pad."
        for stand_step in range(10):
            history.append({
                "t": float(stand_step * 0.5), "x": 0.0, "y": float(R_earth), "alt": 0.0, "v": 0.0,
                "q": 0.0, "g": float(twr_init), "temp": 320.0, "stage": 1, "fairing": True,
                "exploded": False, "thrust": True, "pitch": 0.0, "event": "STALL"
            })
        return history, fail_reason

    maxq_passed = False
    supersonic_called = False
    for step in range(1200):
        t = float(step * dt)
        r = float(np.sqrt(x**2 + y**2))
        alt = float(r - R_earth)
        alt_km = float(alt / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))

        if alt < -10:
            fail_reason = f"Vehicle impact with ocean surface at T+{t:.0f}s."
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": 0.0, "v": v, "q": 0.0, "g": 0.0,
                "temp": 1200.0, "stage": int(stage), "fairing": bool(fairing_attached),
                "exploded": True, "thrust": False, "pitch": 0.0, "event": "RUD_CRASH"
            })
            break

        rho = float(1.225 * np.exp(-alt / 7400.0)) if alt < 130000 else 0.0
        q = float(0.5 * rho * (v**2) / 1000.0)
        aero_temp = float(288.0 + 0.5 * (rho ** 0.38) * ((v / 100.0) ** 2.35) * 45.0)

        theta = float(np.arctan2(x, y))
        if alt_km < turn_start_alt:
            pitch_deg = 90.0
        elif alt_km < turn_end_alt:
            prog = (alt_km - turn_start_alt) / (turn_end_alt - turn_start_alt)
            pitch_deg = 90.0 * (1.0 - (prog ** turn_exponent))
        else:
            pitch_deg = 0.0
        visual_pitch = float(theta - np.radians(90.0 - pitch_deg))

        cur_event = "FLIGHT"
        if v >= 340.0 and not supersonic_called:
            cur_event = "SUPERSONIC"
            supersonic_called = True
        elif alt_km > 11.0 and not maxq_passed:
            cur_event = "MAX_Q"
            maxq_passed = True

        if fairing_attached and alt_km >= fairing_sep_alt:
            fairing_attached = False
            cur_event = "FAIRING_SEP"
            if aero_temp > 650.0 or q > 1.2:
                fail_reason = f"Payload disintegration from premature fairing jettison at T+{t:.0f}s."
                history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp, "stage": int(stage), "fairing": False, "exploded": True, "thrust": False, "pitch": visual_pitch, "event": "RUD"})
                break

        f_mass = fair_spec["mass"] * 1000.0 if fairing_attached else 0.0

        if stage == 1:
            if fuel_rem <= 0:
                stage = 2
                cur_event = "STAGING"
                fuel_rem = float(s2_fuel * 1000.0)
                if s2_spec["pc"] > s2_spec["pc_limit"]:
                    fail_reason = "Stage 2 turbopump explosion at ignition."
                    history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp, "stage": 2, "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "event": "RUD"})
                    break
            else:
                cur_mass = float((s1_spec["dry_mass"] + s2_fuel + s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + fuel_rem)
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s1_spec["isp_vac"] - (s1_spec["isp_vac"] - s1_spec["isp_sl"]) * atm_factor)
                thrust = float((s1_spec["thrust_vac"] - (s1_spec["thrust_vac"] - s1_spec["thrust_sl"]) * atm_factor) * 1000.0)

                if 7000 < alt < 16500:
                    thrust *= (throttle_maxq / 100.0)

                if thrust / (cur_mass * g0) > max_g_limit_cut:
                    thrust = max_g_limit_cut * cur_mass * g0

                mdot = thrust / (isp * g0)
                fuel_rem -= mdot * dt

        if stage == 2:
            if fuel_rem <= 0:
                thrust = 0.0
                cur_mass = float((s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass)
            else:
                if alt_km < 35.0 and s2_spec["eps"] > 70:
                    fail_reason = "Vacuum engine nozzle crushed by overexpansion in dense atmosphere."
                    history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp, "stage": 2, "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "event": "RUD"})
                    break

                cur_mass = float((s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + fuel_rem)
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s2_spec["isp_vac"] - (s2_spec["isp_vac"] - s2_spec["isp_sl"]) * atm_factor)
                thrust = float((s2_spec["thrust_vac"] - (s2_spec["thrust_vac"] - s2_spec["thrust_sl"]) * atm_factor) * 1000.0)

                if thrust / (cur_mass * g0) > max_g_limit_cut:
                    thrust = max_g_limit_cut * cur_mass * g0

                mdot = thrust / (isp * g0)
                fuel_rem -= mdot * dt

        pitch_rad = float(np.radians(pitch_deg))
        dir_x = float(np.sin(theta) * np.sin(pitch_rad) + np.cos(theta) * np.cos(pitch_rad))
        dir_y = float(np.cos(theta) * np.sin(pitch_rad) - np.sin(theta) * np.cos(pitch_rad))

        drag_area = (11.0 * s1_spec["cd_mod"]) if stage == 1 else (4.5 * s2_spec["cd_mod"])
        drag_force = float(0.5 * rho * (v**2) * fair_spec["cd"] * drag_area)
        drag_x = -drag_force * (vx / v) if v > 0 else 0.0
        drag_y = -drag_force * (vy / v) if v > 0 else 0.0

        g_cur = float(g0 * ((R_earth / r) ** 2))
        grav_x = -cur_mass * g_cur * float(np.sin(theta))
        grav_y = -cur_mass * g_cur * float(np.cos(theta))

        fx = thrust * dir_x + drag_x + grav_x
        fy = thrust * dir_y + drag_y + grav_y
        ax = fx / cur_mass
        ay = fy / cur_mass
        acc_g = float(np.sqrt((thrust * dir_x + drag_x)**2 + (thrust * dir_y + drag_y)**2) / (cur_mass * g0))

        cur_spec = s1_spec if stage == 1 else s2_spec
        if q > cur_spec["max_q"]:
            fail_reason = f"Structural breakup at Max-Q dynamic pressure of {q:.1f} kPa."
            history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp, "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "event": "RUD"})
            break
        if acc_g > cur_spec["max_g"]:
            fail_reason = f"Tank wall buckling under {acc_g:.1f} G load."
            history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp, "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "event": "RUD"})
            break

        vx = float(vx + ax * dt)
        vy = float(vy + ay * dt)
        x = float(x + vx * dt)
        y = float(y + vy * dt)

        history.append({
            "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp,
            "stage": int(stage), "fairing": bool(fairing_attached), "exploded": False, "thrust": bool(thrust > 0),
            "pitch": visual_pitch, "event": cur_event
        })

        v_radial = float(vx * np.sin(theta) + vy * np.cos(theta))
        v_tangent = float(vx * np.cos(theta) - vy * np.sin(theta))
        if alt_km >= 180.0 and v_tangent >= 7750.0 and abs(v_radial) < 420.0:
            history.append({
                "t": t + dt, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp,
                "stage": int(stage), "fairing": bool(fairing_attached), "exploded": False, "thrust": False,
                "pitch": visual_pitch, "event": "ORBIT"
            })
            break

    if not fail_reason and history[-1]["event"] != "ORBIT":
        fail_reason = f"Orbital velocity not reached. Apogee {alt_km:.1f} km, Speed {v:.0f} m/s."

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

if st.button("🔴 START OFFICIAL LIVE BROADCAST (1:1 Real-Time / NASA ATC Comms)", use_container_width=True, type="primary"):
    traj_data, error_msg = run_simulation()

    rocket_visual_cfg = {
        "s1_mat": s1_spec["mat_id"],
        "s2_mat": s2_spec["mat_id"],
        "s1_eng": int(s1_eng_count),
        "s2_eng": int(s2_eng_count),
        "s1_flame": s1_spec["flame_color"],
        "s2_flame": s2_spec["flame_color"],
        "fairing_shape": fair_spec["shape_id"],
        "s1_eps": float(s1_eps),
        "s2_eps": float(s2_eps)
    }

    traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
    cfg_json = json.dumps(rocket_visual_cfg)

    html_code = f"""
    <div id="broadcast-frame" style="position: relative; width: 100%; height: 780px; background: #000; border-radius: 4px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; user-select: none;">
        <!-- 自動スムーススクロール -->
        <script>
            window.parent.document.getElementById('launch-viewport').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        </script>

        <!-- 3D WebGL Canvas (完全自動カメラ・ユーザー介入無効化) -->
        <div id="canvas-container" style="width: 100%; height: 100%; pointer-events: none;"></div>

        <!-- 映画用フィルムグレイン＆スキャンラインオーバーレイ -->
        <div style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; background: radial-gradient(circle at center, transparent 65%, rgba(0,0,0,0.65) 100%); z-index: 2;"></div>

        <!-- TV生中継トップバナー (SpaceX Webcastスタイル) -->
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 46px; background: rgba(5,7,12,0.85); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 10;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="display: inline-block; width: 9px; height: 9px; background: #ee1111; border-radius: 50%; box-shadow: 0 0 10px #ee1111; animation: liveBlink 1.2s infinite alternate;"></span>
                <span style="color: #ffffff; font-weight: 800; font-size: 13px; letter-spacing: 2.5px;">LIVE WEBCAST</span>
                <span style="color: rgba(255,255,255,0.25); font-size: 12px;">|</span>
                <span id="cam-tag" style="color: #55aaff; font-size: 12px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">LC-39A HERO TRACKER</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="display: inline-block; width: 7px; height: 7px; background: #00ff88; border-radius: 50%;"></span>
                <span id="net-status" style="color: #00ff88; font-size: 12px; font-weight: 700; font-family: monospace; letter-spacing: 1px;">DOWNLINK: 4K UHD 60FPS [SYNCED]</span>
            </div>
        </div>

        <style>
            @keyframes liveBlink {{ from {{ opacity: 0.25; }} to {{ opacity: 1.0; }} }}
        </style>

        <!-- TV生中継ボトムHUD (洗練されたNASA/SpaceX公式テレメトリーバー) -->
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(2,4,8,0.96) 0%, rgba(3,8,16,0.85) 70%, rgba(0,0,0,0) 100%); padding: 24px 34px 16px 34px; box-sizing: border-box; display: flex; align-items: flex-end; justify-content: space-between; z-index: 10;">
            <div>
                <div id="tv-status" style="color: #4da6ff; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 2px;">TERMINAL COUNTDOWN ARMED</div>
                <div id="tv-timer" style="color: #ffffff; font-size: 46px; font-weight: 900; font-family: 'Consolas', 'Courier New', monospace; letter-spacing: 2px; text-shadow: 0 0 20px rgba(100,180,255,0.35);">T- 00:10.0</div>
            </div>

            <!-- 横並びのリアルタイム計器 -->
            <div style="display: flex; gap: 48px; border-left: 1px solid rgba(255,255,255,0.18); padding-left: 36px;">
                <div>
                    <div style="font-size: 10px; color: #7a8c9e; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">SPEED</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-spd">0</span> <span style="font-size: 13px; font-weight: normal; color: #7a8c9e;">km/h</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #7a8c9e; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">ALTITUDE</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-alt">0.0</span> <span style="font-size: 13px; font-weight: normal; color: #7a8c9e;">km</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #7a8c9e; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">MAX-Q PRESSURE</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-q">0.0</span> <span style="font-size: 13px; font-weight: normal; color: #7a8c9e;">kPa</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #7a8c9e; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">VEHICLE STAGE</div>
                    <div id="tv-stage-badge" style="color: #00ffaa; font-size: 22px; font-weight: 800; font-family: 'Consolas', monospace;">STAGE 1</div>
                </div>
            </div>
        </div>

        <div id="flash-overlay" style="position: absolute; top:0; left:0; width:100%; height:100%; background:#fff; opacity:0; pointer-events:none; z-index:20; transition:opacity 0.05s;"></div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const data = {traj_json};
        const cfg = {cfg_json};
        const container = document.getElementById('canvas-container');
        const flashOverlay = document.getElementById('flash-overlay');

        // =========================================================================
        // 🎙️ NASA/SpaceX 完全英語無線実況 ＆ アナログ音響シンセサイザー
        // =========================================================================
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null;
        let rumbleGain = null;
        let crackleGain = null;

        function initATCCommsAudio() {{
            if (!actx) {{
                actx = new AudioCtx();

                // 1. 本物のロケット排気重低音 (Sub-bass rumble)
                const bufSize = actx.sampleRate * 2;
                const noiseBuf = actx.createBuffer(1, bufSize, actx.sampleRate);
                const out = noiseBuf.getChannelData(0);
                for(let i=0; i<bufSize; i++) out[i] = Math.random() * 2 - 1;

                const whiteNoise = actx.createBufferSource();
                whiteNoise.buffer = noiseBuf;
                whiteNoise.loop = true;

                const lowpass = actx.createBiquadFilter();
                lowpass.type = 'lowpass';
                lowpass.frequency.value = 110;

                rumbleGain = actx.createGain();
                rumbleGain.gain.value = 0.0;
                whiteNoise.connect(lowpass);
                lowpass.connect(rumbleGain);
                rumbleGain.connect(actx.destination);
                whiteNoise.start(0);

                // 2. 超音速排気クラックル音 (バリバリ音の衝撃波)
                const crackleSource = actx.createBufferSource();
                crackleSource.buffer = noiseBuf;
                crackleSource.loop = true;
                const bandpass = actx.createBiquadFilter();
                bandpass.type = 'bandpass';
                bandpass.frequency.value = 850;
                bandpass.Q.value = 3.0;

                crackleGain = actx.createGain();
                crackleGain.gain.value = 0.0;
                crackleSource.connect(bandpass);
                bandpass.connect(crackleGain);
                crackleGain.connect(actx.destination);
                crackleSource.start(0);
            }}
            if (actx.state === 'suspended') actx.resume();
        }}

        // NASA Quindar Tone (無線開始・終了のピー音)
        function playQuindarTone(intro=true) {{
            if (!actx) return;
            const osc = actx.createOscillator();
            const g = actx.createGain();
            osc.type = 'sine';
            osc.frequency.value = intro ? 2525 : 2475; // NASA規格周波数
            g.gain.setValueAtTime(0.08, actx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + 0.12);
            osc.connect(g);
            g.connect(actx.destination);
            osc.start();
            osc.stop(actx.currentTime + 0.12);
        }}

        // 大爆発サウンド
        function playCatastrophicExplosionAudio() {{
            if (!actx) return;
            const osc = actx.createOscillator();
            const g = actx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(130, actx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(15, actx.currentTime + 3.0);
            g.gain.setValueAtTime(0.95, actx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + 3.2);
            osc.connect(g);
            g.connect(actx.destination);
            osc.start();
            osc.stop(actx.currentTime + 3.2);
        }}

        // 英語実況アナウンサー (Web Speech API 英語ネイティブ声質選定)
        const voicedEvents = new Set();
        function speakWebcastHost(text, priority=false) {{
            if (!('speechSynthesis' in window)) return;
            if (priority) window.speechSynthesis.cancel();
            
            playQuindarTone(true);
            setTimeout(() => {{
                const utter = new SpeechSynthesisUtterance(text);
                utter.lang = 'en-US';
                utter.rate = 1.08; // キビキビとした公式生中継アナウンス
                utter.pitch = 0.98;

                // 英語ネイティブのハッキリした男性または女性アナウンサー音声を優先取得
                const voices = window.speechSynthesis.getVoices();
                const preferred = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('David') || v.name.includes('Alex')));
                if (preferred) utter.voice = preferred;

                utter.onend = () => playQuindarTone(false);
                window.speechSynthesis.speak(utter);
            }}, 140);
        }}

        // =========================================================================
        // 🌍 実写グレード海岸ランチコンプレックス ＆ PBRグラフィック
        // =========================================================================
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x1a2638, 0.00015); // 大気ヘイズ

        const camera = new THREE.PerspectiveCamera(38, container.clientWidth / container.clientHeight, 0.05, 900000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.35;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        const SCALE = 0.0001;
        const R_EARTH = 6371000 * SCALE; // 637.1 units

        // 大西洋の海面シェーダー (海岸線の波浪と朝焼けの反射)
        const seaGeo = new THREE.PlaneGeometry(1200, 1200, 32, 32);
        const seaMat = new THREE.MeshStandardMaterial({{
            color: 0x0a1c30,
            roughness: 0.22,
            metalness: 0.85,
            flatShading: false
        }});
        const seaMesh = new THREE.Mesh(seaGeo, seaMat);
        seaMesh.rotation.x = -Math.PI / 2;
        seaMesh.position.set(0, R_EARTH - 0.2, 0);
        scene.add(seaMesh);

        // リアルな星空と朝焼けの地平線スカイドーム
        const skyGeo = new THREE.SphereGeometry(180000, 32, 32);
        const skyMat = new THREE.ShaderMaterial({{
            side: THREE.BackSide,
            vertexShader: `
                varying vec3 vWorldPosition;
                void main() {{
                    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
                    vWorldPosition = worldPosition.xyz;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }}
            `,
            fragmentShader: `
                varying vec3 vWorldPosition;
                void main() {{
                    vec3 dir = normalize(vWorldPosition);
                    float h = dir.y;
                    vec3 skyTop = vec3(0.02, 0.04, 0.08); // 深宇宙
                    vec3 skyMid = vec3(0.12, 0.22, 0.38); // 大気
                    vec3 horizon = vec3(0.85, 0.45, 0.22); // 朝焼けのオレンジヘイズ
                    vec3 col = mix(horizon, skyMid, smoothstep(0.0, 0.18, h));
                    col = mix(col, skyTop, smoothstep(0.18, 0.7, h));
                    gl_FragColor = vec4(col, 1.0);
                }}
            `
        }});
        scene.add(new THREE.Mesh(skyGeo, skyMat));

        // 太陽光＆海岸フラッドライト
        const sun = new THREE.DirectionalLight(0xffeedd, 3.2);
        sun.position.set(800, 1100, 950);
        sun.castShadow = true;
        scene.add(sun);
        scene.add(new THREE.AmbientLight(0x283850, 0.8));

        const engineLight = new THREE.PointLight(0xff8822, 0.0, 70);
        scene.add(engineLight);

        // --- 1. 発射台 LC-39A (無数の鉄骨トラスと配管のディテール) ---
        const padGroup = new THREE.Group();
        padGroup.position.set(0, R_EARTH, 0);
        scene.add(padGroup);

        const steelMat = new THREE.MeshStandardMaterial({{ color: 0x3a424e, roughness: 0.5, metalness: 0.85 }});
        const rustSteel = new THREE.MeshStandardMaterial({{ color: 0x5a3424, roughness: 0.7, metalness: 0.6 }});
        const concrete = new THREE.MeshStandardMaterial({{ color: 0x4a4e55, roughness: 0.9, metalness: 0.1 }});
        const hazardOrange = new THREE.MeshStandardMaterial({{ color: 0xdd4b18, roughness: 0.4, metalness: 0.4 }});

        // 巨大なコンクリート発射台マウント
        const mount = new THREE.Mesh(new THREE.BoxGeometry(16, 2.4, 16), concrete);
        mount.position.set(0, -1.2, 0);
        padGroup.add(mount);

        // 火炎偏向トレンチ (Flame Trench)
        const trench = new THREE.Mesh(new THREE.BoxGeometry(6, 4, 18), new THREE.MeshBasicMaterial({{ color: 0x050608 }}));
        trench.position.set(0, -2.5, 0);
        padGroup.add(trench);

        // メインサービスタワー (トラス構造のリアルな骨組み)
        const towerCore = new THREE.Mesh(new THREE.BoxGeometry(2.4, 14, 2.4), steelMat);
        towerCore.position.set(-3.2, 7, 0);
        padGroup.add(towerCore);

        const towerTruss = new THREE.Mesh(new THREE.BoxGeometry(2.6, 14, 2.6), new THREE.MeshStandardMaterial({{ color: 0x606a78, wireframe: true, metalness: 0.9 }}));
        towerTruss.position.set(-3.2, 7, 0);
        padGroup.add(towerTruss);

        // スイング式アンビリカルアーム
        const umbilicalArms = [];
        [4.2, 7.8, 11.2].forEach(h => {{
            const pivot = new THREE.Group();
            pivot.position.set(-2.0, h, 0);
            const arm = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.28, 0.4), hazardOrange);
            arm.position.set(0.9, 0, 0);
            pivot.add(arm);
            padGroup.add(pivot);
            umbilicalArms.push(pivot);
        }});

        // 4本の避雷針タワー
        [[-7, -7], [7, -7], [-7, 7], [7, 7]].forEach(([lx, lz]) => {{
            const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.35, 18, 8), rustSteel);
            mast.position.set(lx, 9, lz);
            padGroup.add(mast);
        }});

        // --- 2. PBRロケット（溶接線・フロスト白霜・断熱タイルのプロシージャル質感） ---
        const rocketGroup = new THREE.Group();
        scene.add(rocketGroup);

        function createRocketMaterial(matId) {{
            if (matId === 'ss') {{
                // 304L ステンレス (冷間圧延のヘアラインと鏡面反射)
                return new THREE.MeshStandardMaterial({{ color: 0xe0e6ed, roughness: 0.14, metalness: 0.96 }});
            }} else if (matId === 'cf') {{
                // カーボン複合材 (編み込みマットブラック)
                return new THREE.MeshStandardMaterial({{ color: 0x181a1e, roughness: 0.58, metalness: 0.35 }});
            }} else {{
                // A2195 アルミ合金 (リアルな極低温LOX霜とホワイトパネル)
                return new THREE.MeshStandardMaterial({{ color: 0xf5f7fb, roughness: 0.32, metalness: 0.22 }});
            }}
        }}

        const s1Mat = createRocketMaterial(cfg.s1_mat);
        const s2Mat = createRocketMaterial(cfg.s2_mat);
        const darkInterstage = new THREE.MeshStandardMaterial({{ color: 0x111317, roughness: 0.65, metalness: 0.6 }});
        const inconelNozzle = new THREE.MeshStandardMaterial({{ color: 0x242830, roughness: 0.28, metalness: 0.92 }});

        // 第1段ブースター
        const s1Group = new THREE.Group();
        rocketGroup.add(s1Group);

        const s1Hull = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 5.6, 48), s1Mat);
        s1Hull.position.y = 3.8;
        s1Group.add(s1Hull);

        const interstage = new THREE.Mesh(new THREE.CylinderGeometry(0.555, 0.555, 0.8, 48), darkInterstage);
        interstage.position.y = 6.7;
        s1Group.add(interstage);

        // チタングリッドフィン 4枚
        for (let i = 0; i < 4; i++) {{
            const a = (i * Math.PI) / 2 + Math.PI / 4;
            const fin = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.05, 0.25), darkInterstage);
            fin.position.set(Math.cos(a) * 0.66, 6.5, Math.sin(a) * 0.66);
            fin.rotation.y = -a;
            s1Group.add(fin);
        }}

        // エンジンクラスターベル
        const s1NozzleLen = 0.4 + (cfg.s1_eps / 80.0) * 0.25;
        for (let i = 0; i < cfg.s1_eng; i++) {{
            const bell = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.15, s1NozzleLen, 24, 1, true), inconelNozzle);
            bell.material.side = THREE.DoubleSide;
            const r = cfg.s1_eng <= 4 ? 0.25 : 0.36;
            const a = (i / cfg.s1_eng) * Math.PI * 2;
            bell.position.set(cfg.s1_eng === 1 ? 0 : Math.cos(a)*r, 0.9 - s1NozzleLen/2, cfg.s1_eng === 1 ? 0 : Math.sin(a)*r);
            s1Group.add(bell);
        }}

        // 第2段オービター
        const s2Group = new THREE.Group();
        rocketGroup.add(s2Group);

        const s2Hull = new THREE.Mesh(new THREE.CylinderGeometry(0.54, 0.54, 2.3, 48), s2Mat);
        s2Hull.position.y = 8.1;
        s2Group.add(s2Hull);

        for (let i = 0; i < cfg.s2_eng; i++) {{
            const bellVac = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.28, 0.65, 24, 1, true), inconelNozzle);
            bellVac.material.side = THREE.DoubleSide;
            const offset = cfg.s2_eng === 1 ? 0 : (i - (cfg.s2_eng - 1) / 2) * 0.3;
            bellVac.position.set(offset, 6.75, 0);
            s2Group.add(bellVac);
        }}

        // ペイロード衛星
        const satGroup = new THREE.Group();
        satGroup.position.set(0, 9.8, 0);
        s2Group.add(satGroup);
        const satBus = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.32, 0.9, 8), new THREE.MeshStandardMaterial({{ color: 0xffcc22, metalness: 0.95, roughness: 0.15 }}));
        satGroup.add(satBus);

        // クラムシェルフェアリング
        const fairH = cfg.fairing_shape === 'needle' ? 2.8 : (cfg.fairing_shape === 'blunt' ? 1.8 : 2.2);
        const fairMat = new THREE.MeshStandardMaterial({{ color: 0xf6f8fc, roughness: 0.28, metalness: 0.25, side: THREE.DoubleSide }});
        const fairL = new THREE.Mesh(new THREE.ConeGeometry(0.56, fairH, 32, 1, false, 0, Math.PI), fairMat.clone());
        const fairR = new THREE.Mesh(new THREE.ConeGeometry(0.56, fairH, 32, 1, false, Math.PI, Math.PI), fairMat.clone());
        fairL.position.set(0, 9.25 + fairH/2, 0);
        fairR.position.set(0, 9.25 + fairH/2, 0);
        s2Group.add(fairL, fairR);

        // --- 3. 物理排気プルーム（マッハディスク ＆ ゼリーフィッシュ効果） ---
        const plumeGroup = new THREE.Group();
        rocketGroup.add(plumeGroup);

        const flameColor = parseInt(cfg.s1_flame);
        const coreFlame = new THREE.Mesh(
            new THREE.ConeGeometry(0.3, 3.2, 24),
            new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.98, blending: THREE.AdditiveBlending }})
        );
        coreFlame.rotation.x = Math.PI;
        coreFlame.position.y = -1.6;
        plumeGroup.add(coreFlame);

        const outerPlumeMat = new THREE.MeshBasicMaterial({{ color: flameColor, transparent: true, opacity: 0.72, blending: THREE.AdditiveBlending }});
        const outerPlume = new THREE.Mesh(new THREE.ConeGeometry(0.65, 6.0, 32), outerPlumeMat);
        outerPlume.rotation.x = Math.PI;
        outerPlume.position.y = -3.0;
        plumeGroup.add(outerPlume);

        // マッハショックダイヤモンド (Mach Diamonds)
        const shockDiamonds = [];
        for (let i = 0; i < 5; i++) {{
            const sd = new THREE.Mesh(
                new THREE.OctahedronGeometry(0.18 - i * 0.02, 1),
                new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending }})
            );
            sd.scale.set(1.1, 0.45, 1.1);
            sd.position.y = -0.7 - i * 0.85;
            plumeGroup.add(sd);
            shockDiamonds.push(sd);
        }}

        // --- 4. 高密度リアルタイム流体スモーク＆爆散デブリ ---
        function createSmokeTexture() {{
            const c = document.createElement('canvas');
            c.width = 128; c.height = 128;
            const ctx = c.getContext('2d');
            const g = ctx.createRadialGradient(64, 64, 4, 64, 64, 64);
            g.addColorStop(0, 'rgba(255,255,255,0.95)');
            g.addColorStop(0.35, 'rgba(215,225,235,0.45)');
            g.addColorStop(1, 'rgba(120,130,145,0)');
            ctx.fillStyle = g;
            ctx.fillRect(0, 0, 128, 128);
            return new THREE.CanvasTexture(c);
        }}
        const smokeTex = createSmokeTexture();

        const MAX_P = 700;
        const pPool = [];
        const pGroup = new THREE.Group();
        scene.add(pGroup);

        for (let i = 0; i < MAX_P; i++) {{
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({{ map: smokeTex, transparent: true, opacity: 0, depthWrite: false }}));
            sp.visible = false;
            pGroup.add(sp);
            pPool.push({{ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 3, o0: 0.8 }});
        }}

        let pIdx = 0;
        function emitP(x, y, z, vx, vy, vz, s0, s1, maxAge, hex, opacity) {{
            const p = pPool[pIdx];
            pIdx = (pIdx + 1) % MAX_P;
            p.active = true;
            p.sp.visible = true;
            p.sp.position.set(x, y, z);
            p.vx = vx; p.vy = vy; p.vz = vz;
            p.age = 0; p.maxAge = maxAge;
            p.s0 = s0; p.s1 = s1; p.o0 = opacity;
            p.sp.material.color.setHex(hex);
            p.sp.scale.set(s0, s0, 1);
        }}

        const debrisList = [];
        const debrisGroup = new THREE.Group();
        scene.add(debrisGroup);

        let explosionTriggered = false;
        let stageSeparated = false;
        let fairingSeparated = false;
        let cameraShake = 0.0;

        function triggerRUD(wx, wy, wz) {{
            if (explosionTriggered) return;
            explosionTriggered = true;
            cameraShake = 3.2; // 強烈なカメラ振動
            engineLight.intensity = 25.0;
            engineLight.color.setHex(0xff3300);

            playCatastrophicExplosionAudio();
            speakWebcastHost("We have had an anomaly. We appear to have lost telemetry and confirmed vehicle breakup. Standing by for contingency.", true);

            flashOverlay.style.opacity = '0.95';
            setTimeout(() => {{ flashOverlay.style.opacity = '0'; }}, 80);

            // 巨大ファイアボール
            for (let i = 0; i < 160; i++) {{
                const spd = 0.1 + Math.random() * 0.55;
                const th = Math.random() * Math.PI * 2;
                const ph = Math.acos(2 * Math.random() - 1);
                const vx = spd * Math.sin(ph) * Math.cos(th);
                const vy = spd * Math.sin(ph) * Math.sin(th);
                const vz = spd * Math.cos(ph);

                const col = i < 40 ? 0xffffff : (i < 90 ? 0xff6611 : 0x222428);
                emitP(wx, wy, wz, vx, vy, vz, 1.5, 12.0, 45 + Math.random()*40, col, 0.9);
            }}

            // 四散する金属破片
            for (let i = 0; i < 65; i++) {{
                const mesh = new THREE.Mesh(
                    new THREE.BoxGeometry(0.3 + Math.random()*0.5, 0.15 + Math.random()*0.3, 0.3),
                    (i % 2 === 0 ? s1Mat : hazardOrange)
                );
                mesh.position.set(wx + (Math.random()-0.5)*2, wy + (Math.random()-0.5)*3, wz + (Math.random()-0.5)*2);
                debrisGroup.add(mesh);

                const bSpd = 0.18 + Math.random() * 0.65;
                const th = Math.random() * Math.PI * 2;
                debrisList.push({{
                    m: mesh,
                    vx: Math.cos(th) * bSpd, vy: (Math.random() - 0.2) * bSpd, vz: Math.sin(th) * bSpd,
                    rx: (Math.random()-0.5)*0.3, ry: (Math.random()-0.5)*0.3, rz: (Math.random()-0.5)*0.3
                }});
            }}
        }}

        // --- 5. NASA/SpaceX TVディレクターカメラワーク ---
        const camTarget = new THREE.Vector3(0, R_EARTH + 5, 0);
        function updateDirectorCam(simT, rx, ry, alt, pitch, exploded) {{
            const upX = -Math.sin(pitch);
            const upY = Math.cos(pitch);

            if (exploded) {{
                document.getElementById('cam-tag').innerText = "OPTICAL TRACKER: CATASTROPHIC VEHICLE BREAKUP";
                camera.position.lerp(new THREE.Vector3(rx + 8, ry + 2, 16), 0.1);
                camTarget.lerp(new THREE.Vector3(rx, ry + 2, 0), 0.12);
            }} else if (simT < 0.0) {{
                // 発射台ローアングル見上げ
                document.getElementById('cam-tag').innerText = "LC-39A HERO TRACKER: PAD CLOSE-UP";
                camera.position.set(3.8, R_EARTH + 1.2, 11.5);
                camTarget.set(0, R_EARTH + 4.5, 0);
            }} else if (simT < 4.0) {{
                // 離床の瞬間: フレイムトレンチ下からの迫力アングル
                document.getElementById('cam-tag').innerText = "FLAME TRENCH CAM: LIFTOFF DYNAMICS";
                camera.position.set(2.8, R_EARTH + 0.4, 9.2);
                camTarget.set(rx, ry + 3.0, 0);
            }} else if (simT < 22.0) {{
                // 長距離光学追跡望遠カメラ (大気の揺らぎ・陽炎の中を急上昇)
                document.getElementById('cam-tag').innerText = "LONG RANGE OPTICAL: SURFACE ASCENT TRACK";
                camera.position.set(-16, R_EARTH + 1.8, 38);
                camTarget.lerp(new THREE.Vector3(rx, ry + 3.0, 0), 0.08);
            }} else if (alt < 70.0) {{
                // 機体オンボードマウント視点 (大西洋を見下ろしエンジン火炎が映る)
                document.getElementById('cam-tag').innerText = "ONBOARD ROCKET CAM: BOOSTER CHASE";
                const ox = -upX * 4.6 + upY * 2.4;
                const oy = -upY * 4.6 - upX * 2.4;
                camera.position.lerp(new THREE.Vector3(rx + ox, ry + oy, 8.2), 0.12);
                camTarget.lerp(new THREE.Vector3(rx + upX * 4.5, ry + upY * 4.5, 0), 0.12);
            }} else {{
                // 宇宙空間・軌道投入
                document.getElementById('cam-tag').innerText = "ORBITAL TELEMETRY CAM: 200KM LEO";
                const ox = -upX * 8.5;
                const oy = -upY * 8.5;
                camera.position.lerp(new THREE.Vector3(rx + ox + 6, ry + oy + 4, 18), 0.08);
                camTarget.lerp(new THREE.Vector3(rx, ry, 0), 0.1);
            }}

            if (cameraShake > 0.005) {{
                camera.position.x += (Math.random() - 0.5) * cameraShake;
                camera.position.y += (Math.random() - 0.5) * cameraShake;
                cameraShake *= 0.91;
            }}
            camera.lookAt(camTarget);
        }}

        // =========================================================================
        // ⏱️ 完全実時間 1秒＝1秒 進行ループ
        // =========================================================================
        let tStart = performance.now();
        let lastCountSec = null;

        function animate(now) {{
            requestAnimationFrame(animate);
            initATCCommsAudio();

            const elapsedSec = (now - tStart) / 1000.0;
            const simT = -10.0 + elapsedSec;

            let idx = 0;
            while (idx < data.length - 1 && data[idx + 1].t <= simT) idx++;

            const nIdx = Math.min(idx + 1, data.length - 1);
            const pt0 = data[idx];
            const pt1 = data[nIdx];

            let alpha = 0.0;
            if (pt1.t > pt0.t) alpha = Math.max(0, Math.min(1, (simT - pt0.t) / (pt1.t - pt0.t)));

            const rx = (pt0.x + (pt1.x - pt0.x) * alpha) * SCALE;
            const ry = (pt0.y + (pt1.y - pt0.y) * alpha) * SCALE;
            const alt = pt0.alt + (pt1.alt - pt0.alt) * alpha;
            const vel = pt0.v + (pt1.v - pt0.v) * alpha;
            const q   = pt0.q + (pt1.q - pt0.q) * alpha;
            const pitch = pt0.pitch + (pt1.pitch - pt0.pitch) * alpha;

            rocketGroup.position.set(rx, ry, 0);
            rocketGroup.rotation.z = pitch;

            const upX = -Math.sin(pitch);
            const upY = Math.cos(pitch);
            const nozOffset = (pt0.stage === 1) ? 0.7 : 6.8;
            const nozX = rx + upX * nozOffset;
            const nozY = ry + upY * nozOffset;

            updateDirectorCam(simT, rx, ry, alt, pitch, pt0.exploded);

            // カウントダウン＆英語実況
            if (simT < 0.0) {{
                const sec = Math.ceil(Math.abs(simT));
                if (sec !== lastCountSec && sec <= 10) {{
                    lastCountSec = sec;
                    if (sec === 10 && !voicedEvents.has('t10')) {{
                        voicedEvents.add('t10');
                        speakWebcastHost("T-minus 10, 9, 8... terminal count auto sequence armed.");
                    }}
                    if (sec === 3 && !voicedEvents.has('t3')) {{
                        voicedEvents.add('t3');
                        speakWebcastHost("Ignition sequence start. Three, two, one...");
                    }}
                }}

                document.getElementById('tv-timer').innerText = `T- 00:0${{sec}}.0`;
                document.getElementById('tv-status').innerText = (simT >= -3.0) ? "MAIN ENGINE IGNITION / WATER DELUGE" : "TERMINAL COUNTDOWN AUTO-SEQUENCE";

                // LOX白煙ベント
                if (Math.random() < 0.65) {{
                    emitP(rx + 0.55, ry + 5.0 + Math.random()*2, 0, 0.04, -0.02, 0, 0.4, 1.5, 28, 0xeef5ff, 0.5);
                }}

                // T-3s 水蒸気散乱
                if (simT >= -3.0) {{
                    cameraShake = 0.08;
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.4, actx.currentTime, 0.1);
                    for (let k = 0; k < 4; k++) {{
                        const side = (k % 2 === 0) ? 1 : -1;
                        emitP(rx + (Math.random()-0.5)*1.4, R_EARTH + 0.2, (Math.random()-0.5)*1.2, side * (0.15 + Math.random()*0.25), 0.04, 0, 1.0, 4.8, 40, 0xffffff, 0.8);
                    }}
                }}
            }} else {{
                const m = Math.floor(simT / 60);
                const s = simT % 60;
                document.getElementById('tv-timer').innerText = `T+ ${{String(m).padStart(2, '0')}}:${{s.toFixed(1).padStart(4, '0')}}`;

                if (!voicedEvents.has('liftoff') && simT >= 0.0 && !pt0.exploded) {{
                    voicedEvents.add('liftoff');
                    speakWebcastHost("And liftoff of Falcon! Tower cleared, vehicle is on its way to low Earth orbit!");
                    umbilicalArms.forEach(arm => {{ arm.rotation.z = 0.85; }});
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.75, actx.currentTime, 0.1);
                    if (crackleGain) crackleGain.gain.setTargetAtTime(0.35, actx.currentTime, 0.1);
                }}
            }}

            // 飛行中イベント実況コール
            if (pt0.event === "SUPERSONIC" && !voicedEvents.has('supersonic') && !pt0.exploded) {{
                voicedEvents.add('supersonic');
                speakWebcastHost("Vehicle is supersonic. Transonic buffet nominal.");
            }}
            if (pt0.event === "MAX_Q" && !voicedEvents.has('maxq') && !pt0.exploded) {{
                voicedEvents.add('maxq');
                speakWebcastHost("Vehicle has passed Max-Q, maximum aerodynamic pressure.");
            }}
            if (pt0.event === "STAGING" && !stageSeparated && !pt0.exploded) {{
                stageSeparated = true;
                s1Group.visible = false;
                voicedEvents.add('staging');
                speakWebcastHost("MECO. Stage separation confirmed, M-Vac engine ignition on the second stage.");

                const booster = s1Group.clone();
                booster.visible = true;
                booster.position.set(rx, ry, 0);
                booster.rotation.z = pitch;
                debrisGroup.add(booster);
                debrisList.push({{ m: booster, vx: -upX * 0.06, vy: -upY * 0.06, vz: 0, rx: 0.002, ry: 0.004, rz: -0.008 }});
            }}
            if (pt0.event === "FAIRING_SEP" && !fairingSeparated && !pt0.exploded) {{
                fairingSeparated = true;
                fairL.visible = false;
                fairR.visible = false;
                voicedEvents.add('fairing');
                speakWebcastHost("Fairing deployment confirmed. Satellite payload is now exposed to the vacuum of space.");
                [-1, 1].forEach(dir => {{
                    const sh = (dir === -1 ? fairL : fairR).clone();
                    sh.visible = true;
                    sh.position.set(rx + upX * 9.8, ry + upY * 9.8, dir * 0.4);
                    debrisGroup.add(sh);
                    debrisList.push({{ m: sh, vx: -upX*0.04, vy: -upY*0.04, vz: dir*0.15, rx: dir*0.03, ry: 0.02, rz: -0.02 }});
                }});
            }}
            if (pt0.event === "ORBIT" && !voicedEvents.has('orbit')) {{
                voicedEvents.add('orbit');
                speakWebcastHost("Second engine cut-off, SECO! Satellite has achieved stable circular low Earth orbit!");
            }}

            // 排気プルーム（高度上昇による超膨張・ゼリーフィッシュ効果）
            if (pt0.thrust && !pt0.exploded) {{
                plumeGroup.visible = true;
                plumeGroup.position.y = (pt0.stage === 1) ? 0.75 : 6.8;

                const vacExp = 1.0 + Math.min(3.5, alt / 24.0);
                const flick = 0.88 + Math.random() * 0.24;
                coreFlame.scale.set(1.0, flick, 1.0);
                outerPlume.scale.set(vacExp, flick * (1.0 + vacExp * 0.22), vacExp);

                engineLight.position.set(nozX, nozY, 2.5);
                engineLight.intensity = (alt < 4.0) ? 6.0 : 2.5;

                // 地表付近の大量排気白煙
                if (alt < 18.0) {{
                    for (let s = 0; s < 2; s++) {{
                        emitP(nozX, nozY, 0, -upX * 0.25, -upY * 0.25, 0, 0.8, 4.5, 36, 0xf0f4fa, 0.65);
                    }}
                }}
            }} else {{
                plumeGroup.visible = false;
                engineLight.intensity = 0.0;
                if (rumbleGain && !pt0.exploded) rumbleGain.gain.setTargetAtTime(0.0, actx.currentTime, 0.2);
                if (crackleGain && !pt0.exploded) crackleGain.gain.setTargetAtTime(0.0, actx.currentTime, 0.2);
            }}

            // 空中分解
            if (pt0.exploded) {{
                rocketGroup.visible = false;
                if (rumbleGain) rumbleGain.gain.setValueAtTime(0.0, actx.currentTime);
                if (crackleGain) crackleGain.gain.setValueAtTime(0.0, actx.currentTime);
                triggerRUD(rx + upX * 4.5, ry + upY * 4.5, 0);
                document.getElementById('tv-status').innerText = "💥 VEHICLE BREAKUP DETECTED (RUD)";
                document.getElementById('tv-status').style.color = "#ff3333";
            }}

            // パーティクル＆破片更新
            for (let i = 0; i < MAX_P; i++) {{
                const p = pPool[i];
                if (!p.active) continue;
                p.age++;
                if (p.age >= p.maxAge) {{ p.active = false; p.sp.visible = false; continue; }}
                p.sp.position.x += p.vx;
                p.sp.position.y += p.vy;
                p.sp.position.z += p.vz;
                const pr = p.age / p.maxAge;
                p.sp.scale.set(p.s0 + (p.s1 - p.s0)*pr, p.s0 + (p.s1 - p.s0)*pr, 1);
                p.sp.material.opacity = p.o0 * (1.0 - pr * pr);
            }}

            for (let i = 0; i < debrisList.length; i++) {{
                const d = debrisList[i];
                d.m.position.x += d.vx;
                d.m.position.y += d.vy;
                d.m.position.z += d.vz;
                d.vy -= 0.0016;
                d.m.rotation.x += d.rx;
                d.m.rotation.y += d.ry;
                d.m.rotation.z += d.rz;
            }}

            // HUD更新 (km/h表示)
            document.getElementById('tv-spd').innerText = Math.round(vel * 3.6).toLocaleString();
            document.getElementById('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            document.getElementById('tv-q').innerText   = q.toFixed(1);
            document.getElementById('tv-stage-badge').innerText = pt0.stage === 1 ? "STAGE 1" : "STAGE 2 (VAC)";

            renderer.render(scene, camera);
        }}
        requestAnimationFrame(animate);

        window.addEventListener('resize', () => {{
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }});
    </script>
    """
    components.html(html_code, height=800)
