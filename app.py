import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbital Architect Pro: Starship級 超精密ロケット工学シミュレーター", layout="wide")

st.title("🚀 Orbital Architect Pro - 次世代ロケット工学＆公式4K生中継")
st.markdown("NASA / SpaceX公式Webcast体験。1:1リアルタイム物理シミュレーション、実機スケール3Dグラフィックス、超音速ヴェイパーコーン、ホットステージング、管制無線ATC完全連動。")

# --- ロケット推進・構造データベース ---
PROPELLANTS = {
    "LCH4 / LOX [メタン・液体酸素 / Raptor仕様]": {"base_isp_sl": 327, "base_isp_vac": 363, "base_thrust": 2300, "density": 0.82, "temp_factor": 1.1, "flame_color": "0x33aaff"},
    "RP-1 / LOX [ケロシン・液体酸素 / Merlin仕様]": {"base_isp_sl": 285, "base_isp_vac": 313, "base_thrust": 845, "density": 1.02, "temp_factor": 1.0, "flame_color": "0xff9922"},
    "LH2 / LOX [水素・液体酸素 / 極限高比推力]": {"base_isp_sl": 366, "base_isp_vac": 452, "base_thrust": 1150, "density": 0.32, "temp_factor": 0.9, "flame_color": "0xff6622"}
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [Raptor同等・超高圧]": {"isp_mod": 1.05, "thrust_mod": 1.35, "mass_mod": 1.25, "max_pressure_limit": 350},
    "二段燃焼サイクル (SC) [高出力・高信頼]": {"isp_mod": 1.02, "thrust_mod": 1.15, "mass_mod": 1.18, "max_pressure_limit": 250},
    "ガス発生器サイクル (GG) [標準的構造]": {"isp_mod": 0.96, "thrust_mod": 0.95, "mass_mod": 0.85, "max_pressure_limit": 150}
}

MATERIALS = {
    "304L 冷間圧延ステンレス鋼 [Starship鏡面仕様]": {"base_dry_ratio": 0.088, "max_q_base": 90.0, "max_g_base": 10.0, "mat_id": "ss"},
    "A2195 アルミリチウム合金 [Falcon 9ホワイト塗装]": {"base_dry_ratio": 0.062, "max_q_base": 48.0, "max_g_base": 6.2, "mat_id": "al"},
    "東レ製 炭素繊維複合材 (CFRP) [軽量マットブラック]": {"base_dry_ratio": 0.040, "max_q_base": 36.0, "max_g_base": 5.4, "mat_id": "cf"}
}

FAIRINGS = {
    "Starship型 一体型ノーズコーン (再突入耐熱タイル仕様)": {"mass": 3.2, "cd": 0.26, "heat_limit": 2600, "shape_id": "starship"},
    "標準オジーブ・クラムシェル (耐熱1,800K)": {"mass": 1.8, "cd": 0.32, "heat_limit": 1800, "shape_id": "ogive"},
    "高空力ニードルノーズ (低抵抗・極超音速特化)": {"mass": 1.4, "cd": 0.22, "heat_limit": 1450, "shape_id": "needle"}
}

PRESSURIZATION = {
    "自己加圧方式 (Autogenous / 極低温ガス還流)": {"mass_penalty": 0.002, "g_bonus": 0.92},
    "高圧ヘリウムCOPVボトル加圧": {"mass_penalty": 0.008, "g_bonus": 1.18}
}

# --- 設定タブUI ---
tab1, tab2, tab3 = st.tabs(["🔥 第1段 (ブースター)", "🛰️ 第2段 (宇宙船/ペイロード)", "📐 飛行プロファイル & 軌道投入計画"])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### ブースター推進系")
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=0)
        s1_cycle = st.selectbox("ターボポンプサイクル", list(PUMP_CYCLES.keys()), index=0)
        s1_eng_count = st.slider("エンジンクラスター数", 1, 33, 9)
    with c2:
        st.markdown("#### 燃焼室 & ノズル")
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 50, 350, 280, step=10)
        s1_eps = st.slider("海面膨張比 (ε)", 10, 60, 24, step=2)
        s1_tvc = st.slider("ジンバル角 TVC (deg)", 2, 15, 8)
    with c3:
        st.markdown("#### タンク & 機体構造")
        s1_fuel = st.slider("第1段 推進剤積載量 (トン)", 100.0, 3400.0, 1200.0, step=50.0)
        s1_mat = st.selectbox("第1段 船体材質", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("タンク壁厚 (mm 相当)", 1.5, 8.0, 3.8, step=0.2)
        s1_press = st.selectbox("加圧システム", list(PRESSURIZATION.keys()), index=0)

with tab2:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 第2段 推進系")
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=0)
        s2_cycle = st.selectbox("第2段 ターボポンプ", list(PUMP_CYCLES.keys()), index=0)
        s2_eng_count = st.slider("真空エンジン基数", 1, 9, 6)
        s2_pc = st.slider("第2段 燃焼室圧力 (bar)", 30, 350, 240, step=10)
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 30, 250, 120, step=5)
    with c2:
        st.markdown("#### 第2段 構造")
        s2_fuel = st.slider("第2段 推進剤積載量 (トン)", 20.0, 1200.0, 450.0, step=25.0)
        s2_mat = st.selectbox("第2段 船体材質", list(MATERIALS.keys()), index=0)
        s2_thick = st.slider("第2段 壁厚 (mm)", 1.0, 6.0, 3.0, step=0.2)
    with c3:
        st.markdown("#### ノーズ & ペイロード")
        fairing_type = st.selectbox("先端空力カウル / フェアリング", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("フェアリング分離高度 (km / Starship型は分離無効)", 40.0, 150.0, 95.0, step=5.0)
        payload_mass = st.slider("ペイロード重量 (トン)", 0.5, 150.0, 25.0, step=2.5)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 重力ターン軌道")
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.8, 15.0, 2.5, step=0.5)
        turn_end_alt = st.slider("水平加速移行高度 (km)", 50.0, 200.0, 125.0, step=5.0)
        turn_exponent = st.slider("ターン曲率指数", 0.4, 1.5, 0.75, step=0.05)
    with c2:
        st.markdown("#### スロットル & 構造安全制限")
        throttle_maxq = st.slider("Max-Q 通過時 スロットルカット (%)", 40, 100, 70)
        max_g_limit_cut = st.slider("Gリミッター制限値 (G)", 3.0, 10.0, 5.2, step=0.2)

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

total_s2_wet = s2_fuel + s2_spec["dry_mass"] + payload_mass + (fair_spec["mass"] if fair_spec["shape_id"] != "starship" else 0.0)
total_s1_wet = s1_fuel + s1_spec["dry_mass"] + total_s2_wet

twr_init = s1_spec["thrust_sl"] / (total_s1_wet * 9.80665)
dv_s1 = s1_spec["isp_sl"] * 9.80665 * np.log(total_s1_wet / (total_s1_wet - s1_fuel))
dv_s2 = s2_spec["isp_vac"] * 9.80665 * np.log(total_s2_wet / (s2_spec["dry_mass"] + payload_mass))
total_dv = dv_s1 + dv_s2

# --- 設計性能概要 ---
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("総打上げ質量 / 離床TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f}")
m2.metric("総設計速度増分 (ΔV)", f"{total_dv:.0f} m/s", f"S1: {dv_s1:.0f} / S2: {dv_s2:.0f}")
m3.metric("許容動圧 Max-Q / 加速度限界", f"{s1_spec['max_q']:.1f} kPa", f"耐G: {s1_spec['max_g']:.1f} G")
m4.metric("離床海面総推力", f"{s1_spec['thrust_sl']:.0f} kN", f"Isp: {s1_spec['isp_sl']:.0f} s")

# --- 物理計算 ---
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

    for cd_step in range(20):
        t_cd = -10.0 + cd_step * 0.5
        pre_ignition = bool(t_cd >= -3.0)
        history.append({
            "t": float(t_cd), "x": 0.0, "y": float(R_earth), "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "stage": 1, "fairing": True,
            "exploded": False, "thrust": pre_ignition, "pitch": 0.0, "event": "COUNTDOWN"
        })

    if s1_spec["pc"] > s1_spec["pc_limit"]:
        fail_reason = "発射台上でターボポンプが許容圧力を超え破裂。"
        history.append({
            "t": 0.2, "x": 0.0, "y": float(R_earth + 2.0), "alt": 0.002, "v": 2.0,
            "q": 0.0, "g": 0.0, "stage": 1, "fairing": True,
            "exploded": True, "thrust": False, "pitch": 0.0, "event": "RUD_PAD"
        })
        return history, fail_reason

    if twr_init <= 1.02:
        fail_reason = "推力重量比 (TWR) 不足により発射台を離脱不能。"
        for stand_step in range(10):
            history.append({
                "t": float(stand_step * 0.5), "x": 0.0, "y": float(R_earth), "alt": 0.0, "v": 0.0,
                "q": 0.0, "g": float(twr_init), "stage": 1, "fairing": True,
                "exploded": False, "thrust": True, "pitch": 0.0, "event": "STALL"
            })
        return history, fail_reason

    maxq_passed = False
    supersonic_called = False
    hot_staging_done = False

    for step in range(1300):
        t = float(step * dt)
        r = float(np.sqrt(x**2 + y**2))
        alt = float(r - R_earth)
        alt_km = float(alt / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))

        if alt < -10:
            fail_reason = f"T+{t:.0f}s: 弾道軌道により海洋へ墜落。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": 0.0, "v": v, "q": 0.0, "g": 0.0,
                "stage": int(stage), "fairing": bool(fairing_attached),
                "exploded": True, "thrust": False, "pitch": 0.0, "event": "RUD_CRASH"
            })
            break

        rho = float(1.225 * np.exp(-alt / 7400.0)) if alt < 130000 else 0.0
        q = float(0.5 * rho * (v**2) / 1000.0)

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

        if fairing_attached and fair_spec["shape_id"] != "starship" and alt_km >= fairing_sep_alt:
            fairing_attached = False
            cur_event = "FAIRING_SEP"

        f_mass = (fair_spec["mass"] * 1000.0) if (fairing_attached and fair_spec["shape_id"] != "starship") else 0.0

        if stage == 1:
            if fuel_rem <= 0:
                stage = 2
                cur_event = "HOT_STAGING"
                hot_staging_done = True
                fuel_rem = float(s2_fuel * 1000.0)
            else:
                cur_mass = float((s1_spec["dry_mass"] + s2_fuel + s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + fuel_rem)
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s1_spec["isp_vac"] - (s1_spec["isp_vac"] - s1_spec["isp_sl"]) * atm_factor)
                thrust = float((s1_spec["thrust_vac"] - (s1_spec["thrust_vac"] - s1_spec["thrust_sl"]) * atm_factor) * 1000.0)

                if 8000 < alt < 16500:
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

        drag_area = (15.0 * s1_spec["cd_mod"]) if stage == 1 else (6.5 * s2_spec["cd_mod"])
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
            fail_reason = f"動圧限界超過: Max-Q動圧 {q:.1f} kPa により機体が空中分解。"
            history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "event": "RUD"})
            break

        vx = float(vx + ax * dt)
        vy = float(vy + ay * dt)
        x = float(x + vx * dt)
        y = float(y + vy * dt)

        history.append({
            "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g,
            "stage": int(stage), "fairing": bool(fairing_attached), "exploded": False, "thrust": bool(thrust > 0),
            "pitch": visual_pitch, "event": cur_event
        })

        v_radial = float(vx * np.sin(theta) + vy * np.cos(theta))
        v_tangent = float(vx * np.cos(theta) - vy * np.sin(theta))
        if alt_km >= 160.0 and v_tangent >= 7800.0 and abs(v_radial) < 400.0:
            history.append({
                "t": t + dt, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": 0.0,
                "stage": int(stage), "fairing": bool(fairing_attached), "exploded": False, "thrust": False,
                "pitch": visual_pitch, "event": "ORBIT"
            })
            break

    if not fail_reason and history[-1]["event"] != "ORBIT":
        fail_reason = f"軌道速度未達。到達最高高度: {alt_km:.1f} km, 最終速度: {v:.0f} m/s"

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

if st.button("🔴 Starship Flight 5 スタイル 公式4K生中継を開始 (1:1 リアルタイム)", use_container_width=True, type="primary"):
    traj_data, error_msg = run_simulation()

    rocket_visual_cfg = {
        "s1_mat": s1_spec["mat_id"],
        "s2_mat": s2_spec["mat_id"],
        "s1_eng": int(s1_eng_count),
        "s2_eng": int(s2_eng_count),
        "s1_flame": s1_spec["flame_color"],
        "s2_flame": s2_spec["flame_color"],
        "fairing_shape": fair_spec["shape_id"]
    }

    traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
    cfg_json = json.dumps(rocket_visual_cfg)

    html_code = f"""
    <div id="broadcast-frame" style="position: relative; width: 100%; height: 820px; background: #000; border-radius: 6px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; user-select: none;">
        <script>
            window.parent.document.getElementById('launch-viewport').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        </script>

        <!-- 3D WebGL Canvas -->
        <div id="canvas-container" style="width: 100%; height: 100%; pointer-events: none;"></div>

        <!-- フィルムグレイン & 光学レンズ周辺減光 -->
        <div style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; background: radial-gradient(circle at center, transparent 55%, rgba(0,0,0,0.78) 100%); z-index: 2;"></div>

        <!-- SpaceX Flight 5 公式Webcast トップバー (英語表記) -->
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 48px; background: rgba(5,7,12,0.85); backdrop-filter: blur(10px); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 10;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <span style="display: inline-block; width: 9px; height: 9px; background: #ee1111; border-radius: 50%; box-shadow: 0 0 12px #ee1111; animation: liveBlink 1.2s infinite alternate;"></span>
                <span style="color: #ffffff; font-weight: 800; font-size: 13px; letter-spacing: 2px;">SPACEX LIVE</span>
                <span style="color: rgba(255,255,255,0.25); font-size: 12px;">|</span>
                <span id="cam-tag" style="color: #60a5fa; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">STARBASE OLIT-1 / HIGH BAY CAM</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="display: inline-block; width: 7px; height: 7px; background: #10b981; border-radius: 50%;"></span>
                <span style="color: #10b981; font-size: 12px; font-weight: 700; font-family: monospace; letter-spacing: 1px;">STARLINK HIGH-GAIN DOWNLINK: 4K 60FPS</span>
            </div>
        </div>

        <style>
            @keyframes liveBlink {{ from {{ opacity: 0.2; }} to {{ opacity: 1.0; }} }}
        </style>

        <!-- SpaceX Flight 5 公式 Webcast HUD (英語テレメトリー) -->
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(2,4,8,0.96) 0%, rgba(3,8,16,0.82) 75%, rgba(0,0,0,0) 100%); padding: 28px 36px 18px 36px; box-sizing: border-box; display: flex; align-items: flex-end; justify-content: space-between; z-index: 10;">
            <div>
                <div id="tv-status" style="color: #60a5fa; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 2px;">COUNTDOWN TERMINAL AUTO SEQUENCE</div>
                <div id="tv-timer" style="color: #ffffff; font-size: 48px; font-weight: 900; font-family: 'Consolas', 'Courier New', monospace; letter-spacing: 2px; text-shadow: 0 0 25px rgba(96,165,250,0.4);">T- 00:10.0</div>
            </div>

            <div style="display: flex; gap: 44px; border-left: 1px solid rgba(255,255,255,0.18); padding-left: 36px;">
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">SPEED</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-spd">0</span> <span style="font-size: 13px; font-weight: normal; color: #94a3b8;">km/h</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">ALTITUDE</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-alt">0.0</span> <span style="font-size: 13px; font-weight: normal; color: #94a3b8;">km</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">MAX-Q DYNAMIC</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-q">0.0</span> <span style="font-size: 13px; font-weight: normal; color: #94a3b8;">kPa</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">FLIGHT PHASE</div>
                    <div id="tv-stage-badge" style="color: #34d399; font-size: 22px; font-weight: 800; font-family: 'Consolas', monospace;">SUPER HEAVY</div>
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
        // 🎙️ SpaceX Flight 5 公式英語無線アナウンス ＆ 音響シンセサイザー
        // =========================================================================
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null;
        let rumbleGain = null;
        let crackleGain = null;

        function initATCCommsAudio() {{
            if (!actx) {{
                actx = new AudioCtx();

                const bufSize = actx.sampleRate * 2;
                const noiseBuf = actx.createBuffer(1, bufSize, actx.sampleRate);
                const out = noiseBuf.getChannelData(0);
                for(let i=0; i<bufSize; i++) out[i] = Math.random() * 2 - 1;

                const whiteNoise = actx.createBufferSource();
                whiteNoise.buffer = noiseBuf;
                whiteNoise.loop = true;

                const lowpass = actx.createBiquadFilter();
                lowpass.type = 'lowpass';
                lowpass.frequency.value = 120;

                rumbleGain = actx.createGain();
                rumbleGain.gain.value = 0.0;
                whiteNoise.connect(lowpass);
                lowpass.connect(rumbleGain);
                rumbleGain.connect(actx.destination);
                whiteNoise.start(0);

                const crackleSource = actx.createBufferSource();
                crackleSource.buffer = noiseBuf;
                crackleSource.loop = true;
                const bandpass = actx.createBiquadFilter();
                bandpass.type = 'bandpass';
                bandpass.frequency.value = 950;
                bandpass.Q.value = 2.5;

                crackleGain = actx.createGain();
                crackleGain.gain.value = 0.0;
                crackleSource.connect(bandpass);
                bandpass.connect(crackleGain);
                crackleGain.connect(actx.destination);
                crackleSource.start(0);
            }}
            if (actx.state === 'suspended') actx.resume();
        }}

        function playQuindarTone(intro=true) {{
            if (!actx) return;
            const osc = actx.createOscillator();
            const g = actx.createGain();
            osc.type = 'sine';
            osc.frequency.value = intro ? 2525 : 2475;
            g.gain.setValueAtTime(0.06, actx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + 0.1);
            osc.connect(g);
            g.connect(actx.destination);
            osc.start();
            osc.stop(actx.currentTime + 0.1);
        }}

        const voicedEvents = new Set();
        function speakWebcastHost(text, priority=false) {{
            if (!('speechSynthesis' in window)) return;
            if (priority) window.speechSynthesis.cancel();
            
            playQuindarTone(true);
            setTimeout(() => {{
                const utter = new SpeechSynthesisUtterance(text);
                utter.lang = 'en-US';
                utter.rate = 1.05;
                utter.pitch = 1.0;

                const voices = window.speechSynthesis.getVoices();
                const preferred = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('David') || v.name.includes('Alex')));
                if (preferred) utter.voice = preferred;

                utter.onend = () => playQuindarTone(false);
                window.speechSynthesis.speak(utter);
            }}, 120);
        }}

        // =========================================================================
        // 🌍 Starbase Boca Chica 級 リアルタイム 3D レンダリング
        // =========================================================================
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x1a2638, 0.00012);

        const camera = new THREE.PerspectiveCamera(36, container.clientWidth / container.clientHeight, 0.05, 1000000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.4;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        const SCALE = 0.0001;
        const R_EARTH = 6371000 * SCALE;

        // メキシコ湾のリアルな海面
        const seaGeo = new THREE.PlaneGeometry(1600, 1600, 32, 32);
        const seaMat = new THREE.MeshStandardMaterial({{
            color: 0x08182b,
            roughness: 0.18,
            metalness: 0.88
        }});
        const seaMesh = new THREE.Mesh(seaGeo, seaMat);
        seaMesh.rotation.x = -Math.PI / 2;
        seaMesh.position.set(0, R_EARTH - 0.2, 0);
        scene.add(seaMesh);

        // 朝焼けのテキサス・ボカチカ上空スカイドーム
        const skyGeo = new THREE.SphereGeometry(250000, 32, 32);
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
                    vec3 skyTop = vec3(0.015, 0.03, 0.06);
                    vec3 skyMid = vec3(0.14, 0.24, 0.42);
                    vec3 horizon = vec3(0.92, 0.52, 0.26);
                    vec3 col = mix(horizon, skyMid, smoothstep(0.0, 0.22, h));
                    col = mix(col, skyTop, smoothstep(0.22, 0.75, h));
                    gl_FragColor = vec4(col, 1.0);
                }}
            `
        }});
        scene.add(new THREE.Mesh(skyGeo, skyMat));

        const sun = new THREE.DirectionalLight(0xffeedd, 3.4);
        sun.position.set(800, 1200, 900);
        sun.castShadow = true;
        scene.add(sun);
        scene.add(new THREE.AmbientLight(0x2d3a4d, 0.9));

        const engineLight = new THREE.PointLight(0x55aaff, 0.0, 90);
        scene.add(engineLight);

        // --- 1. Starbase 発射タワー (Mechazilla Chopsticks & OLM) ---
        const padGroup = new THREE.Group();
        padGroup.position.set(0, R_EARTH, 0);
        scene.add(padGroup);

        const steelMat = new THREE.MeshStandardMaterial({{ color: 0x2e3540, roughness: 0.45, metalness: 0.9 }});
        const darkTruss = new THREE.MeshStandardMaterial({{ color: 0x4f5866, wireframe: true, metalness: 0.85 }});
        const chopstickMat = new THREE.MeshStandardMaterial({{ color: 0x1f2329, roughness: 0.35, metalness: 0.95 }});

        // 巨大な軌道発射台 (OLM: Orbital Launch Mount)
        const olmRing = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.8, 2.6, 24), steelMat);
        olmRing.position.set(0, 1.3, 0);
        padGroup.add(olmRing);

        // メカジラ・タワー (高層トラス)
        const towerH = 22.0;
        const towerCore = new THREE.Mesh(new THREE.BoxGeometry(3.0, towerH, 3.0), steelMat);
        towerCore.position.set(-4.5, towerH / 2, 0);
        padGroup.add(towerCore);

        const towerTruss = new THREE.Mesh(new THREE.BoxGeometry(3.2, towerH, 3.2), darkTruss);
        towerTruss.position.set(-4.5, towerH / 2, 0);
        padGroup.add(towerTruss);

        // チョップスティック・キャッチアーム (Mechazilla Arms)
        const armL = new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.6, 0.4), chopstickMat);
        armL.position.set(-1.8, 14.5, 1.2);
        padGroup.add(armL);
        const armR = new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.6, 0.4), chopstickMat);
        armR.position.set(-1.8, 14.5, -1.2);
        padGroup.add(armR);

        // --- 2. Starship & Super Heavy 機体モデル ---
        const rocketGroup = new THREE.Group();
        scene.add(rocketGroup);

        function createRocketMaterial(matId) {{
            if (matId === 'ss') {{
                return new THREE.MeshStandardMaterial({{ color: 0xdde4ec, roughness: 0.12, metalness: 0.98 }});
            }} else if (matId === 'cf') {{
                return new THREE.MeshStandardMaterial({{ color: 0x141619, roughness: 0.62, metalness: 0.3 }});
            }} else {{
                return new THREE.MeshStandardMaterial({{ color: 0xf5f7fb, roughness: 0.35, metalness: 0.2 }});
            }}
        }}

        const s1Mat = createRocketMaterial(cfg.s1_mat);
        const s2Mat = createRocketMaterial(cfg.s2_mat);
        const tileBlack = new THREE.MeshStandardMaterial({{ color: 0x0c0d10, roughness: 0.82, metalness: 0.15 }});
        const nozzleMat = new THREE.MeshStandardMaterial({{ color: 0x22262c, roughness: 0.25, metalness: 0.95 }});

        // 第1段 Super Heavy ブースター
        const s1Group = new THREE.Group();
        rocketGroup.add(s1Group);

        const s1Len = 8.2;
        const s1Hull = new THREE.Mesh(new THREE.CylinderGeometry(0.72, 0.72, s1Len, 48), s1Mat);
        s1Hull.position.y = s1Len / 2 + 1.2;
        s1Group.add(s1Hull);

        // グリッドフィン 4基
        for (let i = 0; i < 4; i++) {{
            const a = (i * Math.PI) / 2 + Math.PI / 4;
            const fin = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.08, 0.38), s1Mat);
            fin.position.set(Math.cos(a) * 0.9, s1Len + 0.6, Math.sin(a) * 0.9);
            fin.rotation.y = -a;
            s1Group.add(fin);
        }}

        // ホットステージング・リング (有孔スロット構造)
        const hotStageRing = new THREE.Mesh(new THREE.CylinderGeometry(0.725, 0.725, 0.9, 32, 1, true), darkTruss);
        hotStageRing.position.y = s1Len + 1.2 + 0.45;
        s1Group.add(hotStageRing);

        // Raptor エンジンクラスター
        const s1EngCount = Math.min(cfg.s1_eng, 33);
        for (let i = 0; i < s1EngCount; i++) {{
            const bell = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.11, 0.4, 16, 1, true), nozzleMat);
            bell.material.side = THREE.DoubleSide;
            const ringR = i < 3 ? 0.0 : (i < 13 ? 0.28 : 0.52);
            const a = (i / s1EngCount) * Math.PI * 2;
            bell.position.set(ringR === 0 ? 0 : Math.cos(a) * ringR, 1.2, ringR === 0 ? 0 : Math.sin(a) * ringR);
            s1Group.add(bell);
        }}

        // 第2段 Starship 宇宙船
        const s2Group = new THREE.Group();
        rocketGroup.add(s2Group);

        const s2BaseY = s1Len + 1.2 + 0.9;
        const s2Len = 4.8;
        const s2Hull = new THREE.Mesh(new THREE.CylinderGeometry(0.70, 0.70, s2Len, 48), s2Mat);
        s2Hull.position.y = s2BaseY + s2Len / 2;
        s2Group.add(s2Hull);

        // 耐熱シールドタイル (船体片面を覆うブラックタイル)
        const s2Tiles = new THREE.Mesh(new THREE.CylinderGeometry(0.705, 0.705, s2Len, 32, 1, false, 0, Math.PI), tileBlack);
        s2Tiles.position.y = s2BaseY + s2Len / 2;
        s2Group.add(s2Tiles);

        // Starship ノーズコーン
        const noseCone = new THREE.Mesh(new THREE.ConeGeometry(0.70, 2.4, 32), s2Mat);
        noseCone.position.y = s2BaseY + s2Len + 1.2;
        s2Group.add(noseCone);

        const noseTiles = new THREE.Mesh(new THREE.ConeGeometry(0.705, 2.4, 32, 1, false, 0, Math.PI), tileBlack);
        noseTiles.position.y = s2BaseY + s2Len + 1.2;
        s2Group.add(noseTiles);

        // アエロフラップ (前部2枚、後部2枚)
        const forwardFlapL = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.04, 0.35), tileBlack);
        forwardFlapL.position.set(-0.85, s2BaseY + s2Len + 0.4, 0);
        s2Group.add(forwardFlapL);
        const forwardFlapR = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.04, 0.35), s2Mat);
        forwardFlapR.position.set(0.85, s2BaseY + s2Len + 0.4, 0);
        s2Group.add(forwardFlapR);

        // --- 3. 超高密度排気プルーム ＆ マッハショックダイヤモンド ---
        const plumeGroup = new THREE.Group();
        rocketGroup.add(plumeGroup);

        const flameColorHex = parseInt(cfg.s1_flame);
        const coreFlame = new THREE.Mesh(
            new THREE.ConeGeometry(0.42, 4.5, 32),
            new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending }})
        );
        coreFlame.rotation.x = Math.PI;
        coreFlame.position.y = -2.25;
        plumeGroup.add(coreFlame);

        const outerPlumeMat = new THREE.MeshBasicMaterial({{ color: flameColorHex, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending }});
        const outerPlume = new THREE.Mesh(new THREE.ConeGeometry(0.9, 8.5, 32), outerPlumeMat);
        outerPlume.rotation.x = Math.PI;
        outerPlume.position.y = -4.25;
        plumeGroup.add(outerPlume);

        // マッハディスク
        const shockDiamonds = [];
        for (let i = 0; i < 6; i++) {{
            const sd = new THREE.Mesh(
                new THREE.OctahedronGeometry(0.24 - i * 0.025, 1),
                new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.92, blending: THREE.AdditiveBlending }})
            );
            sd.scale.set(1.2, 0.4, 1.2);
            sd.position.y = -0.8 - i * 0.95;
            plumeGroup.add(sd);
            shockDiamonds.push(sd);
        }}

        // --- 4. 超音速プラントル・グロワート凝縮コーン (Vapor Cone) ---
        const vaporConeGeo = new THREE.ConeGeometry(1.6, 2.2, 32, 1, true);
        const vaporConeMat = new THREE.MeshBasicMaterial({{
            color: 0xeef5ff,
            transparent: true,
            opacity: 0.0,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending
        }});
        const vaporCone = new THREE.Mesh(vaporConeGeo, vaporConeMat);
        vaporCone.rotation.x = Math.PI;
        vaporCone.position.y = s2BaseY;
        rocketGroup.add(vaporCone);

        // --- 5. ウォーターデリュージ蒸気 & 流体スモーク ---
        function createSmokeTexture() {{
            const c = document.createElement('canvas');
            c.width = 128; c.height = 128;
            const ctx = c.getContext('2d');
            const g = ctx.createRadialGradient(64, 64, 6, 64, 64, 64);
            g.addColorStop(0, 'rgba(255,255,255,0.92)');
            g.addColorStop(0.3, 'rgba(220,230,242,0.45)');
            g.addColorStop(1, 'rgba(100,110,125,0)');
            ctx.fillStyle = g;
            ctx.fillRect(0, 0, 128, 128);
            return new THREE.CanvasTexture(c);
        }}
        const smokeTex = createSmokeTexture();

        const MAX_P = 800;
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

        let cameraShake = 0.0;
        let stageSeparated = false;

        // --- 6. SpaceX公式ディレクターカメラワーク ---
        const camTarget = new THREE.Vector3(0, R_EARTH + 6, 0);
        function updateDirectorCam(simT, rx, ry, alt, pitch, exploded) {{
            const upX = -Math.sin(pitch);
            const upY = Math.cos(pitch);

            if (exploded) {{
                document.getElementById('cam-tag').innerText = "OPTICAL TRACKER: CATASTROPHIC VEHICLE BREAKUP";
                camera.position.lerp(new THREE.Vector3(rx + 9, ry + 3, 18), 0.1);
                camTarget.lerp(new THREE.Vector3(rx, ry + 2, 0), 0.12);
            }} else if (simT < 0.0) {{
                document.getElementById('cam-tag').innerText = "PAD CLOSE-UP: STARBASE OLIT-1";
                camera.position.set(3.5, R_EARTH + 1.8, 12.0);
                camTarget.set(0, R_EARTH + 5.5, 0);
            }} else if (simT < 3.5) {{
                document.getElementById('cam-tag').innerText = "TOWER TRACKER: LIFTOFF & MECHAZILLA CLEARANCE";
                camera.position.set(3.0, R_EARTH + 1.2, 9.8);
                camTarget.set(rx, ry + 4.0, 0);
            }} else if (simT < 26.0) {{
                document.getElementById('cam-tag').innerText = "LONG RANGE OPTICAL: BOCA CHICA TRACK";
                camera.position.set(-18, R_EARTH + 2.5, 42);
                camTarget.lerp(new THREE.Vector3(rx, ry + 3.5, 0), 0.08);
            }} else if (alt < 65.0) {{
                document.getElementById('cam-tag').innerText = "SUPER HEAVY ONBOARD: DOWNWARD FIN CHASE";
                const ox = -upX * 5.2 + upY * 2.8;
                const oy = -upY * 5.2 - upX * 2.8;
                camera.position.lerp(new THREE.Vector3(rx + ox, ry + oy, 8.8), 0.12);
                camTarget.lerp(new THREE.Vector3(rx + upX * 5.0, ry + upY * 5.0, 0), 0.12);
            }} else {{
                document.getElementById('cam-tag').innerText = "ORBITAL TELEMETRY CAM: STARSHIP SPACE TRACK";
                const ox = -upX * 10.0;
                const oy = -upY * 10.0;
                camera.position.lerp(new THREE.Vector3(rx + ox + 8, ry + oy + 5, 22), 0.08);
                camTarget.lerp(new THREE.Vector3(rx, ry, 0), 0.1);
            }}

            if (cameraShake > 0.005) {{
                camera.position.x += (Math.random() - 0.5) * cameraShake;
                camera.position.y += (Math.random() - 0.5) * cameraShake;
                cameraShake *= 0.92;
            }}
            camera.lookAt(camTarget);
        }}

        // =========================================================================
        // ⏱️ 1:1 実時間 進行メインループ
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

            updateDirectorCam(simT, rx, ry, alt, pitch, pt0.exploded);

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
                document.getElementById('tv-status').innerText = (simT >= -3.0) ? "RAPTOR IGNITION / WATER DELUGE ACTIVE" : "TERMINAL COUNTDOWN AUTO SEQUENCE";

                if (Math.random() < 0.65) {{
                    emitP(rx + 0.72, ry + 6.0 + Math.random()*2, 0, 0.05, -0.02, 0, 0.4, 1.6, 28, 0xedf4fc, 0.55);
                }}

                if (simT >= -3.0) {{
                    cameraShake = 0.12;
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.55, actx.currentTime, 0.1);
                    for (let k = 0; k < 6; k++) {{
                        const side = (k % 2 === 0) ? 1 : -1;
                        emitP(rx + (Math.random()-0.5)*1.8, R_EARTH + 0.4, (Math.random()-0.5)*1.5, side * (0.2 + Math.random()*0.35), 0.05, 0, 1.2, 5.5, 45, 0xffffff, 0.85);
                    }}
                }}
            }} else {{
                const m = Math.floor(simT / 60);
                const s = simT % 60;
                document.getElementById('tv-timer').innerText = `T+ ${{String(m).padStart(2, '0')}}:${{s.toFixed(1).padStart(4, '0')}}`;

                if (!voicedEvents.has('liftoff') && simT >= 0.0 && !pt0.exploded) {{
                    voicedEvents.add('liftoff');
                    speakWebcastHost("And liftoff of Starship Flight 5! Mechazilla tower cleared, vehicle is on its way to space!");
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.85, actx.currentTime, 0.1);
                    if (crackleGain) crackleGain.gain.setTargetAtTime(0.45, actx.currentTime, 0.1);
                }}
            }}

            if (vel > 310.0 && vel < 380.0) {{
                const vapInt = Math.sin(((vel - 310.0) / 70.0) * Math.PI);
                vaporConeMat.opacity = vapInt * 0.75;
                vaporCone.scale.set(1.0 + Math.random()*0.08, 1.0, 1.0 + Math.random()*0.08);
            }} else {{
                vaporConeMat.opacity = 0.0;
            }}

            if (pt0.event === "SUPERSONIC" && !voicedEvents.has('supersonic') && !pt0.exploded) {{
                voicedEvents.add('supersonic');
                speakWebcastHost("Vehicle is supersonic. Transonic buffet nominal.");
            }}
            if (pt0.event === "MAX_Q" && !voicedEvents.has('maxq') && !pt0.exploded) {{
                voicedEvents.add('maxq');
                speakWebcastHost("Vehicle has passed through Max-Q, maximum dynamic pressure.");
            }}
            if (pt0.event === "HOT_STAGING" && !stageSeparated && !pt0.exploded) {{
                stageSeparated = true;
                s1Group.visible = false;
                voicedEvents.add('hotstaging');
                speakWebcastHost("Hot-staging confirmed! Ship engines are lit, Super Heavy booster initiating boostback maneuver.");

                for (let k = 0; k < 40; k++) {{
                    const a = (k / 40) * Math.PI * 2;
                    emitP(rx, ry + 9.5, 0, Math.cos(a)*0.4, Math.sin(a)*0.4, 0, 0.8, 4.0, 30, 0x44bbff, 0.9);
                }}
            }}
            if (pt0.event === "ORBIT" && !voicedEvents.has('orbit')) {{
                voicedEvents.add('orbit');
                speakWebcastHost("Ship engine cutoff confirmed! Starship has reached orbital velocity and entered stable Earth orbit!");
            }}

            if (pt0.thrust && !pt0.exploded) {{
                plumeGroup.visible = true;
                plumeGroup.position.y = (pt0.stage === 1) ? 1.0 : s2BaseY;

                const vacExp = 1.0 + Math.min(4.8, alt / 20.0);
                const flick = 0.9 + Math.random() * 0.22;
                coreFlame.scale.set(1.0, flick, 1.0);
                outerPlume.scale.set(vacExp, flick * (1.0 + vacExp * 0.28), vacExp);

                engineLight.position.set(rx, ry + plumeGroup.position.y, 2.5);
                engineLight.intensity = (alt < 4.0) ? 7.5 : 3.0;

                if (alt < 18.0) {{
                    for (let s = 0; s < 2; s++) {{
                        emitP(rx, ry + 0.8, 0, -upX * 0.28, -upY * 0.28, 0, 0.9, 5.0, 38, 0xf0f4fa, 0.7);
                    }}
                }}
            }} else {{
                plumeGroup.visible = false;
                engineLight.intensity = 0.0;
            }}

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

            document.getElementById('tv-spd').innerText = Math.round(vel * 3.6).toLocaleString();
            document.getElementById('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            document.getElementById('tv-q').innerText   = q.toFixed(1);
            document.getElementById('tv-stage-badge').innerText = pt0.stage === 1 ? "SUPER HEAVY" : "STARSHIP";

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
    components.html(html_code, height=840)
