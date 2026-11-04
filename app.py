import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbital Architect Pro: 4K実写打ち上げ生中継", layout="wide")

st.title("🚀 Orbital Architect Pro - 次世代超重量級ロケット打ち上げシミュレーター")
st.markdown("航空宇宙管制センター公式4Kライブ中継。実写ブレンド光学パイプライン、完全自動ロストゼロ・ディレクターカメラ、1:1 リアルタイム軌道力学計算。")

# --- 推進剤・材料データベース ---
PROPELLANTS = {
    "超高密度メタロックス (CH4 / LOX) [次世代FFSC仕様]": {"base_isp_sl": 335, "base_isp_vac": 375, "base_thrust": 2700, "density": 0.83, "temp_factor": 1.1, "flame_color": "0x67e8f9"},
    "高精製ケロシン (RP-1 / LOX) [大気圏高密度高推力]": {"base_isp_sl": 290, "base_isp_vac": 320, "base_thrust": 1150, "density": 1.02, "temp_factor": 1.0, "flame_color": "0xf97316"},
    "超極低温ハイドロロックス (LH2 / LOX) [真空究極比推力]": {"base_isp_sl": 372, "base_isp_vac": 460, "base_thrust": 1350, "density": 0.32, "temp_factor": 0.9, "flame_color": "0xf43f5e"}
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [極限高圧・高効率]": {"isp_mod": 1.06, "thrust_mod": 1.40, "mass_mod": 1.25, "max_pressure_limit": 380},
    "二段燃焼サイクル (SC) [高出力・実証信頼性]": {"isp_mod": 1.02, "thrust_mod": 1.15, "mass_mod": 1.18, "max_pressure_limit": 280},
    "ガス発生器サイクル (GG) [堅牢・軽量設計]": {"isp_mod": 0.96, "thrust_mod": 0.95, "mass_mod": 0.85, "max_pressure_limit": 170}
}

MATERIALS = {
    "Austenitic 300系 圧延鏡面ステンレス [極低温・耐熱複合]": {"base_dry_ratio": 0.070, "max_q_base": 120.0, "max_g_base": 12.0, "mat_id": "ss"},
    "航空宇宙用 Al-Li アルミリチウム合金 [軽量断熱白塗装]": {"base_dry_ratio": 0.055, "max_q_base": 60.0, "max_g_base": 7.5, "mat_id": "al"},
    "高弾性炭素繊維複合材 (CFRP) [超軽量マットブラック]": {"base_dry_ratio": 0.038, "max_q_base": 45.0, "max_g_base": 6.0, "mat_id": "cf"}
}

FAIRINGS = {
    "低抵抗バイコニカル複合材カウル (耐熱2,600K)": {"mass": 2.2, "cd": 0.20, "heat_limit": 2600, "shape_id": "biconic"},
    "高音速オジーブ・クラムシェル (耐熱1,900K)": {"mass": 1.8, "cd": 0.28, "heat_limit": 1900, "shape_id": "ogive"},
    "極超音速ペネトレーターニードル (超低ドラッグ)": {"mass": 1.4, "cd": 0.18, "heat_limit": 1500, "shape_id": "needle"}
}

PRESSURIZATION = {
    "自己加圧方式 (Autogenous / 極低温排熱自己加圧)": {"mass_penalty": 0.002, "g_bonus": 0.95},
    "高圧He COPV複合材ボトル加圧": {"mass_penalty": 0.008, "g_bonus": 1.18}
}

# --- 設定タブUI ---
tab1, tab2, tab3 = st.tabs(["🔥 第1段 (ブースター)", "🛰️ 第2段 (オービター) & ペイロード", "📐 軌道投入ガイダンス & 安全マージン"])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### ブースター推進系")
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=0)
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", list(PUMP_CYCLES.keys()), index=0)
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, 9)
    with c2:
        st.markdown("#### 燃焼室 & ノズル")
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 50, 360, 290, step=10)
        s1_eps = st.slider("海面膨張比 (ε)", 10, 60, 24, step=1)
        s1_tvc = st.slider("TVC ジンバル最大角 (deg)", 2, 12, 8)
    with c3:
        st.markdown("#### タンク構造・加圧")
        s1_fuel = st.slider("第1段 推進剤充填量 (トン)", 100.0, 3000.0, 850.0, step=50.0)
        s1_mat = st.selectbox("第1段 構造素材", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("外殻等価板厚 (mm)", 1.5, 8.0, 3.8, step=0.2)
        s1_press = st.selectbox("タンク加圧方式", list(PRESSURIZATION.keys()), index=0)

with tab2:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 第2段 真空推進系")
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=0)
        s2_cycle = st.selectbox("第2段 ポンプ方式", list(PUMP_CYCLES.keys()), index=0)
        s2_eng_count = st.slider("真空特化ノズル基数", 1, 9, 3)
        s2_pc = st.slider("第2段 燃焼室圧 (bar)", 30, 320, 220, step=10)
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 40, 260, 130, step=5)
    with c2:
        st.markdown("#### 第2段 構造・タンク")
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 20.0, 900.0, 280.0, step=20.0)
        s2_mat = st.selectbox("第2段 構造素材", list(MATERIALS.keys()), index=0)
        s2_thick = st.slider("第2段 壁厚 (mm)", 1.0, 6.0, 2.8, step=0.2)
    with c3:
        st.markdown("#### 先端部 & ペイロード")
        fairing_type = st.selectbox("先端空力カウル / フェアリング", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 40.0, 150.0, 85.0, step=5.0)
        payload_mass = st.slider("投入衛星ペイロード質量 (トン)", 0.5, 120.0, 12.0, step=1.0)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 重力ターン 軌道投入プロファイル")
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.5, 12.0, 1.5, step=0.1)
        turn_end_alt = st.slider("水平重力ターン完了高度 (km)", 50.0, 200.0, 110.0, step=5.0)
        turn_exponent = st.slider("ターン曲率プロファイル指数", 0.4, 1.5, 0.68, step=0.02)
    with c2:
        st.markdown("#### フライトスロットル & 加速度リミッター")
        throttle_maxq = st.slider("Max-Q 領域 推力抑制 (%)", 40, 100, 78)
        max_g_limit_cut = st.slider("最大加速度リミッター (G)", 3.0, 9.0, 5.5, step=0.2)

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
    eng_mass = (thrust_vac_per_eng / 800.0) * cyc["mass_mod"] * (1.0 + eps * 0.002) * eng_count
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
dv_s2 = s2_spec["isp_vac"] * 9.80665 * np.log(total_s2_wet / (s2_spec["dry_mass"] + payload_mass))
total_dv = dv_s1 + dv_s2

# --- 設計性能概要メトリクス ---
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("総離床重量 / 離床TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f}")
m2.metric("総計算速度増分 (ΔV)", f"{total_dv:.0f} m/s", f"S1: {dv_s1:.0f} / S2: {dv_s2:.0f}")
m3.metric("限界動圧 Max-Q / 加速度許容値", f"{s1_spec['max_q']:.1f} kPa", f"耐G: {s1_spec['max_g']:.1f} G")
m4.metric("海面総推力", f"{s1_spec['thrust_sl']:.0f} kN", f"Isp: {s1_spec['isp_sl']:.0f} s")

# --- 物理シミュレーション ---
def run_simulation():
    dt = 0.5
    g0 = 9.80665
    R_earth = 6371000.0

    x, y = 0.0, 0.0
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
            "t": float(t_cd), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "stage": 1, "fairing": True,
            "exploded": False, "thrust": pre_ignition, "pitch": 0.0, "event": "COUNTDOWN",
            "downrange_km": 0.0
        })

    maxq_passed = False
    supersonic_called = False

    for step in range(1400):
        t = float(step * dt)
        alt = float(y)
        alt_km = float(alt / 1000.0)
        downrange_km = float(x / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))

        rho = float(1.225 * np.exp(-alt / 7400.0)) if alt < 130000 else 0.0
        q = float(0.5 * rho * (v**2) / 1000.0)

        if alt_km < turn_start_alt:
            pitch_deg = 90.0
        elif alt_km < turn_end_alt:
            prog = (alt_km - turn_start_alt) / (turn_end_alt - turn_start_alt)
            pitch_deg = 90.0 * (1.0 - (prog ** turn_exponent))
        else:
            pitch_deg = 0.0

        pitch_rad = float(np.radians(pitch_deg))
        visual_pitch = float(np.radians(90.0 - pitch_deg))

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

        f_mass = (fair_spec["mass"] * 1000.0) if fairing_attached else 0.0

        if stage == 1:
            if fuel_rem <= 0:
                stage = 2
                cur_event = "HOT_STAGING"
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

        dir_x = float(np.cos(pitch_rad))
        dir_y = float(np.sin(pitch_rad))

        drag_area = (12.0 * s1_spec["cd_mod"]) if stage == 1 else (5.2 * s2_spec["cd_mod"])
        drag_force = float(0.5 * rho * (v**2) * fair_spec["cd"] * drag_area)
        drag_x = -drag_force * (vx / v) if v > 0 else 0.0
        drag_y = -drag_force * (vy / v) if v > 0 else 0.0

        g_cur = float(g0 * ((R_earth / (R_earth + alt)) ** 2))
        centrifugal_acc = (vx ** 2) / (R_earth + alt)
        grav_y = -cur_mass * (g_cur - centrifugal_acc)

        fx = thrust * dir_x + drag_x
        fy = thrust * dir_y + drag_y + grav_y

        if alt <= 0.0 and fy <= 0.0 and t < 0.5:
            ax, ay = 0.0, 0.0
            vx, vy = 0.0, 0.0
            acc_g = 1.0
        else:
            ax = fx / cur_mass
            ay = fy / cur_mass
            acc_g = float(np.sqrt((thrust * dir_x + drag_x)**2 + (thrust * dir_y + drag_y)**2) / (cur_mass * g0))

        cur_spec = s1_spec if stage == 1 else s2_spec
        if q > cur_spec["max_q"]:
            fail_reason = f"機体空中分解: Max-Q 動圧 {q:.1f} kPa が設計強度を超過。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False,
                "pitch": visual_pitch, "event": "RUD", "downrange_km": downrange_km
            })
            break

        vx = float(vx + ax * dt)
        vy = float(vy + ay * dt)
        x = float(x + vx * dt)
        y = float(max(0.0, y + vy * dt))

        history.append({
            "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g,
            "stage": int(stage), "fairing": bool(fairing_attached), "exploded": False, "thrust": bool(thrust > 0),
            "pitch": visual_pitch, "event": cur_event, "downrange_km": downrange_km
        })

        if alt_km >= 165.0 and vx >= 7780.0 and abs(vy) < 350.0:
            history.append({
                "t": t + dt, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": 0.0,
                "stage": int(stage), "fairing": bool(fairing_attached), "exploded": False, "thrust": False,
                "pitch": visual_pitch, "event": "ORBIT", "downrange_km": downrange_km
            })
            break

    if not fail_reason and history[-1]["event"] != "ORBIT":
        fail_reason = f"軌道速度未達。到達最高高度: {alt_km:.1f} km, 速度: {v:.0f} m/s"

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

if st.button("🔴 AETHEL-9 ミッション 実写4K公式生中継を開始 (1:1 リアルタイム)", use_container_width=True, type="primary"):
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
    <div id="broadcast-frame" style="position: relative; width: 100%; height: 880px; background: #000; border-radius: 6px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none;">
        <script>
            window.parent.document.getElementById('launch-viewport').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        </script>

        <!-- 3D レンダリングキャンバス -->
        <div id="canvas-container" style="width: 100%; height: 100%;"></div>

        <!-- 実写光学レンズフィルムグレイン & アナモフィックフレア & ビネット -->
        <div style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; background: radial-gradient(circle at center, transparent 50%, rgba(0,3,8,0.85) 100%); z-index: 2;"></div>
        <div id="film-grain" style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; opacity:0.045; z-index:3;"></div>
        <div id="streak-flare" style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; opacity:0; z-index:4; mix-blend-mode: screen; background: linear-gradient(0deg, transparent 48%, rgba(100,200,255,0.25) 50%, transparent 52%); transition: opacity 0.08s;"></div>

        <!-- 放送中継トップバナー -->
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 42px; background: rgba(6,10,18,0.85); backdrop-filter: blur(12px); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 10;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 10px #ef4444; animation: liveBlink 1.4s infinite alternate;"></span>
                <span style="color: #ffffff; font-weight: 800; font-size: 12px; letter-spacing: 2px;">LIVE WEBCAST</span>
                <span style="color: rgba(255,255,255,0.25);">|</span>
                <span id="cam-tag" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">GROUND ULTRA-TRACKER: FULL VEHICLE 4K</span>
            </div>
            <div style="display: flex; align-items: center; gap: 14px;">
                <span style="display: inline-block; width: 6px; height: 6px; background: #10b981; border-radius: 50%;"></span>
                <span style="color: #10b981; font-size: 11px; font-weight: 700; font-family: monospace;">RAW FEED 60FPS</span>
            </div>
        </div>

        <style>
            @keyframes liveBlink {{ from {{ opacity: 0.2; }} to {{ opacity: 1.0; }} }}
        </style>

        <!-- 🛰️ フライトトラッカー (右上HUD: 映像と重ならないコンパクト設計) -->
        <div style="position: absolute; top: 52px; right: 20px; width: 250px; background: rgba(8,12,22,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; padding: 10px; z-index: 10;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="font-size: 9px; font-weight: 800; color: #38bdf8; letter-spacing: 1px;">TRAJECTORY TRACKER</span>
                <span id="region-tag" style="font-size: 8.5px; font-weight: 700; color: #34d399; font-family: monospace;">PAD LC-1</span>
            </div>
            <canvas id="map-canvas" width="230" height="75" style="width: 100%; height: 75px; background: #050914; border-radius: 4px; border: 1px solid rgba(255,255,255,0.06);"></canvas>
            <div style="display: flex; justify-content: space-between; font-size: 8px; color: #64748b; font-family: monospace; margin-top: 3px;">
                <span>0 km</span>
                <span id="map-downrange-txt">0.0 km</span>
                <span>2400 km</span>
            </div>
            <div style="margin-top: 6px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 5px;">
                <div style="display: flex; justify-content: space-between; font-size: 8.5px; color: #94a3b8; margin-bottom: 2px;">
                    <span>ORBITAL VELOCITY</span>
                    <span id="orbit-pct-txt" style="color: #38bdf8; font-weight: 700;">0%</span>
                </div>
                <div style="width: 100%; height: 3px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden;">
                    <div id="orbit-progress-bar" style="width: 0%; height: 100%; background: linear-gradient(90deg, #38bdf8, #10b981); transition: width 0.2s;"></div>
                </div>
            </div>
        </div>

        <!-- 放送テレメトリー HUD -->
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(2,4,8,0.95) 0%, rgba(3,6,12,0.75) 70%, rgba(0,0,0,0) 100%); padding: 22px 32px 16px 32px; box-sizing: border-box; display: flex; align-items: flex-end; justify-content: space-between; z-index: 10;">
            <div>
                <div id="tv-status" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 2px;">COUNTDOWN AUTO SEQUENCE INITIALIZED</div>
                <div id="tv-timer" style="color: #ffffff; font-size: 44px; font-weight: 900; font-family: 'Consolas', 'Courier New', monospace; letter-spacing: 2px; text-shadow: 0 0 25px rgba(56,189,248,0.35);">T- 00:10.0</div>
            </div>

            <div style="display: flex; gap: 36px; border-left: 1px solid rgba(255,255,255,0.16); padding-left: 30px;">
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">VELOCITY</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-spd">0</span> <span style="font-size: 12px; font-weight: normal; color: #94a3b8;">km/h</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">ALTITUDE</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-alt">0.0</span> <span style="font-size: 12px; font-weight: normal; color: #94a3b8;">km</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">DYNAMIC PRESSURE</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-q">0.0</span> <span style="font-size: 12px; font-weight: normal; color: #94a3b8;">kPa</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">STAGE</div>
                    <div id="tv-stage-badge" style="color: #34d399; font-size: 20px; font-weight: 800; font-family: 'Consolas', monospace;">STAGE 1</div>
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
        const streakFlare = document.getElementById('streak-flare');
        const mapCanvas = document.getElementById('map-canvas');
        const mapCtx = mapCanvas.getContext('2d');

        // 音響シンセサイザー
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
                for (let i = 0; i < bufSize; i++) out[i] = Math.random() * 2 - 1;

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

                const crackleSource = actx.createBufferSource();
                crackleSource.buffer = noiseBuf;
                crackleSource.loop = true;
                const bandpass = actx.createBiquadFilter();
                bandpass.type = 'bandpass';
                bandpass.frequency.value = 1100;
                bandpass.Q.value = 3.5;

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
                utter.pitch = 0.98;
                const voices = window.speechSynthesis.getVoices();
                const preferred = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('David')));
                if (preferred) utter.voice = preferred;
                utter.onend = () => playQuindarTone(false);
                window.speechSynthesis.speak(utter);
            }}, 120);
        }}

        // =========================================================================
        // 🌍 3D エンジン & 実写環境 (大気層・海岸地形・地球曲率)
        // =========================================================================
        const scene = new THREE.Scene();

        const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 4000000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.35;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        // 海岸線・大西洋グラウンドテクスチャ
        function createRealisticGroundTexture() {{
            const c = document.createElement('canvas');
            c.width = 2048; c.height = 2048;
            const ctx = c.getContext('2d');
            ctx.fillStyle = '#0a1726';
            ctx.fillRect(0, 0, 2048, 2048);

            // 沿岸部陸地
            ctx.fillStyle = '#1e2920';
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(820, 0);
            ctx.bezierCurveTo(780, 500, 640, 1000, 500, 2048);
            ctx.lineTo(0, 2048);
            ctx.fill();

            // 砂浜
            ctx.strokeStyle = '#a39068';
            ctx.lineWidth = 18;
            ctx.stroke();

            // 射場コンクリートパッド
            ctx.fillStyle = '#475569';
            ctx.fillRect(560, 940, 260, 200);

            return new THREE.CanvasTexture(c);
        }}

        const groundTex = createRealisticGroundTexture();
        const groundGeo = new THREE.PlaneGeometry(160000, 160000);
        const groundMat = new THREE.MeshStandardMaterial({{ map: groundTex, roughness: 0.7, metalness: 0.1 }});
        const groundMesh = new THREE.Mesh(groundGeo, groundMat);
        groundMesh.rotation.x = -Math.PI / 2;
        groundMesh.position.set(0, -0.2, 0);
        groundMesh.receiveShadow = true;
        scene.add(groundMesh);

        // 高度に応じたスカイドーム (低空: 青空/朝焼け、高空: 宇宙の星空と地球リム)
        const skyGeo = new THREE.SphereGeometry(1500000, 32, 32);
        const skyMat = new THREE.ShaderMaterial({{
            side: THREE.BackSide,
            uniforms: {{
                uCameraY: {{ value: 0.0 }}
            }},
            vertexShader: `
                varying vec3 vWorldPosition;
                void main() {{
                    vec4 wp = modelMatrix * vec4(position, 1.0);
                    vWorldPosition = wp.xyz;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }}
            `,
            fragmentShader: `
                uniform float uCameraY;
                varying vec3 vWorldPosition;
                void main() {{
                    vec3 dir = normalize(vWorldPosition);
                    float h = dir.y;
                    
                    float altRatio = clamp(uCameraY / 8000.0, 0.0, 1.0);
                    vec3 daySky = vec3(0.25, 0.48, 0.75);
                    vec3 horizon = vec3(0.92, 0.62, 0.38);
                    vec3 spaceSky = vec3(0.002, 0.003, 0.010);
                    
                    vec3 lowAtm = mix(horizon, daySky, smoothstep(0.0, 0.28, h));
                    vec3 sky = mix(lowAtm, spaceSky, altRatio);
                    
                    // 地球リム大気グロー
                    float rim = smoothstep(0.01, 0.08, h) * (1.0 - smoothstep(0.08, 0.24, h)) * altRatio;
                    sky += vec3(0.25, 0.65, 1.0) * rim * 2.5;

                    gl_FragColor = vec4(sky, 1.0);
                }}
            `
        }});
        const skySphere = new THREE.Mesh(skyGeo, skyMat);
        scene.add(skySphere);

        const sun = new THREE.DirectionalLight(0xfff5ea, 3.8);
        sun.position.set(1500, 2200, 1500);
        sun.castShadow = true;
        scene.add(sun);
        scene.add(new THREE.AmbientLight(0x334455, 0.85));

        const engineLight = new THREE.PointLight(0xff9933, 0.0, 350, 1.8);
        scene.add(engineLight);

        // 射場タワー施設
        const padGroup = new THREE.Group();
        scene.add(padGroup);

        const steelMat = new THREE.MeshStandardMaterial({{ color: 0x272c35, roughness: 0.45, metalness: 0.92 }});
        const darkTruss = new THREE.MeshStandardMaterial({{ color: 0x48515e, wireframe: true, metalness: 0.88 }});

        const launchMount = new THREE.Mesh(new THREE.CylinderGeometry(2.6, 3.4, 2.8, 32), steelMat);
        launchMount.position.set(0, 1.4, 0);
        padGroup.add(launchMount);

        const towerH = 28.0;
        const towerCore = new THREE.Mesh(new THREE.BoxGeometry(3.4, towerH, 3.4), steelMat);
        towerCore.position.set(-5.2, towerH / 2, 0);
        padGroup.add(towerCore);

        const towerTruss = new THREE.Mesh(new THREE.BoxGeometry(3.6, towerH, 3.6), darkTruss);
        towerTruss.position.set(-5.2, towerH / 2, 0);
        padGroup.add(towerTruss);

        const swingArms = [];
        [7.0, 14.0, 20.0].forEach(h => {{
            const arm = new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.45, 0.4), steelMat);
            arm.position.set(-2.4, h, 0);
            padGroup.add(arm);
            swingArms.push(arm);
        }});

        // --- ロケット本体 (Starship / Falcon風 高精細モデリング) ---
        const rocketGroup = new THREE.Group();
        scene.add(rocketGroup);

        function createPBRRocketMat(matId) {{
            if (matId === 'ss') {{
                return new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, roughness: 0.14, metalness: 0.98 }});
            }} else if (matId === 'cf') {{
                return new THREE.MeshStandardMaterial({{ color: 0x14171c, roughness: 0.65, metalness: 0.32 }});
            }} else {{
                return new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.35, metalness: 0.20 }});
            }}
        }}

        const s1Mat = createPBRRocketMat(cfg.s1_mat);
        const s2Mat = createPBRRocketMat(cfg.s2_mat);
        const nozzleMat = new THREE.MeshStandardMaterial({{ color: 0x181a1f, roughness: 0.28, metalness: 0.95 }});

        const s1Group = new THREE.Group();
        rocketGroup.add(s1Group);

        const s1Len = 8.6;
        const s1Hull = new THREE.Mesh(new THREE.CylinderGeometry(0.76, 0.76, s1Len, 48), s1Mat);
        s1Hull.position.y = s1Len / 2 + 1.4;
        s1Group.add(s1Hull);

        // グリッドフィン
        for (let i = 0; i < 4; i++) {{
            const a = (i * Math.PI) / 2 + Math.PI / 4;
            const fin = new THREE.Mesh(new THREE.BoxGeometry(0.56, 0.08, 0.42), nozzleMat);
            fin.position.set(Math.cos(a) * 0.94, s1Len + 0.8, Math.sin(a) * 0.94);
            fin.rotation.y = -a;
            s1Group.add(fin);
        }}

        const interstageMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.765, 0.765, 1.1, 32, 1, true), darkTruss);
        interstageMesh.position.y = s1Len + 1.4 + 0.55;
        s1Group.add(interstageMesh);

        // 第1段 エンジンノズル群
        const s1EngCount = Math.min(cfg.s1_eng, 33);
        for (let i = 0; i < s1EngCount; i++) {{
            const bell = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.12, 0.45, 16, 1, true), nozzleMat);
            bell.material.side = THREE.DoubleSide;
            const ringR = i < 3 ? 0.0 : (i < 13 ? 0.32 : 0.56);
            const a = (i / s1EngCount) * Math.PI * 2;
            bell.position.set(ringR === 0 ? 0 : Math.cos(a) * ringR, 1.4, ringR === 0 ? 0 : Math.sin(a) * ringR);
            s1Group.add(bell);
        }}

        // 第2段 オービター
        const s2Group = new THREE.Group();
        rocketGroup.add(s2Group);

        const s2BaseY = s1Len + 1.4 + 1.1;
        const s2Len = 5.2;
        const s2Hull = new THREE.Mesh(new THREE.CylinderGeometry(0.74, 0.74, s2Len, 48), s2Mat);
        s2Hull.position.y = s2BaseY + s2Len / 2;
        s2Group.add(s2Hull);

        const fairH = cfg.fairing_shape === 'needle' ? 3.0 : 2.5;
        const noseMesh = new THREE.Mesh(new THREE.ConeGeometry(0.74, fairH, 40), s2Mat);
        noseMesh.position.y = s2BaseY + s2Len + fairH / 2;
        s2Group.add(noseMesh);

        // =========================================================================
        // 🔥 実写YouTube級 火炎・ショックダイヤモンド・動的排気プルーム
        // =========================================================================
        const plumeGroup = new THREE.Group();
        rocketGroup.add(plumeGroup);

        const flameColorHex = parseInt(cfg.s1_flame);

        // 超高温中心コア炎 (純白の高輝度発光)
        const coreFlame = new THREE.Mesh(
            new THREE.ConeGeometry(0.55, 6.5, 32),
            new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.98, blending: THREE.AdditiveBlending }})
        );
        coreFlame.rotation.x = Math.PI;
        coreFlame.position.y = -3.25;
        plumeGroup.add(coreFlame);

        // 外周排気プルーム（高度＝真空度に応じて実写のように巨大化・半透明化）
        const outerPlumeMat = new THREE.MeshBasicMaterial({{
            color: flameColorHex, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending
        }});
        const outerPlume = new THREE.Mesh(new THREE.ConeGeometry(1.25, 12.0, 32), outerPlumeMat);
        outerPlume.rotation.x = Math.PI;
        outerPlume.position.y = -6.0;
        plumeGroup.add(outerPlume);

        // マッハショックダイヤモンド（低空大気圧縮時の衝撃波結節）
        const shockDiamonds = [];
        for (let i = 0; i < 7; i++) {{
            const sd = new THREE.Mesh(
                new THREE.OctahedronGeometry(0.24 - i * 0.02, 1),
                new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending }})
            );
            sd.scale.set(1.15, 0.40, 1.15);
            sd.position.y = -0.7 - i * 0.85;
            plumeGroup.add(sd);
            shockDiamonds.push(sd);
        }}

        // ベイパーコーン (遷音速水蒸気ショック凝縮)
        const vaporCone = new THREE.Mesh(
            new THREE.ConeGeometry(1.9, 2.6, 32, 1, true),
            new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.0, side: THREE.DoubleSide, blending: THREE.AdditiveBlending }})
        );
        vaporCone.rotation.x = Math.PI;
        vaporCone.position.y = s2BaseY;
        rocketGroup.add(vaporCone);

        // デリュージ白煙 & 排気スモークパーティクル
        function createSmokeTexture() {{
            const c = document.createElement('canvas');
            c.width = 128; c.height = 128;
            const ctx = c.getContext('2d');
            const g = ctx.createRadialGradient(64, 64, 4, 64, 64, 64);
            g.addColorStop(0, 'rgba(255,255,255,0.95)');
            g.addColorStop(0.3, 'rgba(220,230,245,0.5)');
            g.addColorStop(1, 'rgba(120,130,150,0)');
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
            pPool.push({{ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 4, o0: 0.8 }});
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

        // =========================================================================
        // 🗺️ フライトトラッカー (右上にすっきり分離配置)
        // =========================================================================
        function drawFlightTracker(downrangeKm, altKm, velocity) {{
            mapCtx.clearRect(0, 0, mapCanvas.width, mapCanvas.height);

            // 背景グリッド
            mapCtx.strokeStyle = 'rgba(255,255,255,0.06)';
            mapCtx.lineWidth = 1;
            for (let x = 20; x < mapCanvas.width; x += 40) {{
                mapCtx.beginPath(); mapCtx.moveTo(x, 0); mapCtx.lineTo(x, mapCanvas.height); mapCtx.stroke();
            }}
            for (let y = 15; y < mapCanvas.height; y += 25) {{
                mapCtx.beginPath(); mapCtx.moveTo(0, y); mapCtx.lineTo(mapCanvas.width, y); mapCtx.stroke();
            }}

            // 海岸線輪郭
            mapCtx.fillStyle = '#1e293b';
            mapCtx.beginPath();
            mapCtx.moveTo(0, 0);
            mapCtx.lineTo(40, 0);
            mapCtx.bezierCurveTo(35, 25, 25, 50, 15, 75);
            mapCtx.lineTo(0, 75);
            mapCtx.fill();

            // 予定軌道破線
            mapCtx.strokeStyle = 'rgba(56,189,248,0.25)';
            mapCtx.setLineDash([2, 3]);
            mapCtx.beginPath();
            mapCtx.moveTo(20, 50);
            mapCtx.quadraticCurveTo(110, 38, 220, 18);
            mapCtx.stroke();
            mapCtx.setLineDash([]);

            // 実飛行プロファイル
            const mapX = 20 + Math.min(200, (downrangeKm / 2400.0) * 200);
            const mapY = 50 - Math.min(32, (downrangeKm / 2400.0) * 32);

            mapCtx.strokeStyle = '#38bdf8';
            mapCtx.lineWidth = 2.0;
            mapCtx.beginPath();
            mapCtx.moveTo(20, 50);
            mapCtx.lineTo(mapX, mapY);
            mapCtx.stroke();

            // 現在位置ドット
            mapCtx.fillStyle = '#ef4444';
            mapCtx.beginPath();
            mapCtx.arc(mapX, mapY, 3, 0, Math.PI * 2);
            mapCtx.fill();
            mapCtx.strokeStyle = '#ffffff';
            mapCtx.lineWidth = 1;
            mapCtx.stroke();

            document.getElementById('map-downrange-txt').innerText = `${{downrangeKm.toFixed(0)}} km`;

            const regionElem = document.getElementById('region-tag');
            if (altKm < 1.0) {{
                regionElem.innerText = "PAD LC-1";
            }} else if (altKm < 50.0) {{
                regionElem.innerText = "ATLANTIC CORRIDOR";
            }} else if (altKm < 110.0) {{
                regionElem.innerText = "UPPER STRATOSPHERE";
            }} else {{
                regionElem.innerText = "LOW EARTH ORBIT";
            }}

            const progressPct = Math.min(100, (velocity / 7800.0) * 100);
            document.getElementById('orbit-progress-bar').style.width = `${{progressPct.toFixed(1)}}%`;
            document.getElementById('orbit-pct-txt').innerText = `${{Math.round(progressPct)}}%`;
        }}

        // =========================================================================
        // 🎥 ロストゼロ・常時機体全体捕捉 シネマティックカメラ
        // =========================================================================
        let cameraShake = 0.0;
        let stageSeparated = false;
        const totalRocketH = 16.5; // 全長 (単位)

        function updateFullRocketCamera(simT, rx, ry, alt, pitch, exploded) {{
            // ロケットの重心（中心点）: ノズルから約8m上
            const rCenterY = ry + (totalRocketH * 0.48);
            const lookTarget = new THREE.Vector3(rx, rCenterY, 0);

            if (exploded) {{
                document.getElementById('cam-tag').innerText = "OPTICAL: BREAKUP TRACKING";
                camera.position.lerp(new THREE.Vector3(rx + 25, rCenterY + 10, 45), 0.08);
            }} else if (simT < 0.0) {{
                // 【発射前 T-10s】発射台とタワー、ロケット全体が見上げる位置にすっぽり収まる画角
                document.getElementById('cam-tag').innerText = "LC-1 PAD TRACKER: FULL VEHICLE 4K";
                camera.position.set(6.0, 8.5, 28.0);
            }} else if (alt < 10.0) {{
                // 【初期上昇 0-10km】地上光学超望遠追従（機体全体＋排気炎＋タワーが画角に収まり続ける）
                document.getElementById('cam-tag').innerText = "OPTICAL TRACKER: SURFACE CHASE";
                // 距離を取りながらロケットの垂直上昇に追従
                const desiredDist = 32.0 + alt * 1.5;
                camera.position.lerp(new THREE.Vector3(rx - 8.0, rCenterY * 0.7 + 4.0, desiredDist), 0.12);
            }} else if (alt < 70.0) {{
                // 【重力ターン〜Max-Q 10-70km】機体全体の傾きと進行方向を見渡す望遠チェイス
                document.getElementById('cam-tag').innerText = "TRACKER 2: GRAVITY TURN & MAX-Q";
                const upX = Math.sin(pitch);
                const upY = Math.cos(pitch);
                // 機体の斜め後方・十分な距離から機体全体と排気炎を常に捉える
                const camX = rx - upX * 18.0 + upY * 8.0;
                const camY = rCenterY - upY * 18.0 - upX * 8.0;
                camera.position.lerp(new THREE.Vector3(camX, camY, 32.0), 0.14);
            }} else {{
                // 【成層圏・宇宙空間 70km〜】地球の青い円弧を背景に機体全体を捉えるオービタルビュー
                document.getElementById('cam-tag').innerText = "ORBITAL TELEMETRY: SPACE INSERTION";
                const upX = Math.sin(pitch);
                const upY = Math.cos(pitch);
                const camX = rx + upX * 14.0 + upY * 10.0;
                const camY = rCenterY + upY * 14.0 - upX * 10.0;
                camera.position.lerp(new THREE.Vector3(camX, camY, 36.0), 0.12);
            }}

            if (cameraShake > 0.005) {{
                camera.position.x += (Math.random() - 0.5) * cameraShake;
                camera.position.y += (Math.random() - 0.5) * cameraShake;
                cameraShake *= 0.92;
            }}

            // 常にロケットの中心点（全体）をフレームの真ん中にロック
            camera.lookAt(lookTarget);
            skyMat.uniforms.uCameraY.value = camera.position.y;
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

            // 10m = 1単位
            const rx = (pt0.x + (pt1.x - pt0.x) * alpha) * 0.1;
            const ry = (pt0.y + (pt1.y - pt0.y) * alpha) * 0.1;
            const alt = pt0.alt + (pt1.alt - pt0.alt) * alpha;
            const vel = pt0.v + (pt1.v - pt0.v) * alpha;
            const q   = pt0.q + (pt1.q - pt0.q) * alpha;
            const pitch = pt0.pitch + (pt1.pitch - pt0.pitch) * alpha;
            const downrange = pt0.downrange_km + (pt1.downrange_km - pt0.downrange_km) * alpha;

            rocketGroup.position.set(rx, ry, 0);
            rocketGroup.rotation.z = -pitch;

            const upX = Math.sin(pitch);
            const upY = Math.cos(pitch);

            updateFullRocketCamera(simT, rx, ry, alt, pitch, pt0.exploded);
            drawFlightTracker(downrange, alt, vel);

            // カウントダウン演出
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
                document.getElementById('tv-status').innerText = (simT >= -3.0) ? "MAIN ENGINE IGNITION / WATER DELUGE ACTIVE" : "TERMINAL COUNTDOWN AUTO SEQUENCE";

                // ベントガス白煙
                if (Math.random() < 0.6) {{
                    emitP(rx + 0.76, ry + 6.0 + Math.random()*2, 0, 0.06, -0.02, 0, 0.4, 1.8, 28, 0xedf4fc, 0.55);
                }}

                // T-3s デリュージ白煙爆発
                if (simT >= -3.0) {{
                    cameraShake = 0.14;
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.60, actx.currentTime, 0.1);
                    for (let k = 0; k < 6; k++) {{
                        const side = (k % 2 === 0) ? 1 : -1;
                        emitP(rx + (Math.random()-0.5)*2.0, 0.5, (Math.random()-0.5)*1.8, side * (0.25 + Math.random()*0.4), 0.06, 0, 1.4, 6.0, 48, 0xffffff, 0.88);
                    }}
                    streakFlare.style.opacity = "0.25";
                }}
            }} else {{
                const m = Math.floor(simT / 60);
                const s = simT % 60;
                document.getElementById('tv-timer').innerText = `T+ ${{String(m).padStart(2, '0')}}:${{s.toFixed(1).padStart(4, '0')}}`;

                if (!voicedEvents.has('liftoff') && simT >= 0.0 && !pt0.exploded) {{
                    voicedEvents.add('liftoff');
                    speakWebcastHost("And liftoff of AETHEL-9! Tower cleared, vehicle pitching downrange!");
                    swingArms.forEach(arm => {{ arm.rotation.z = 0.75; }});
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.85, actx.currentTime, 0.1);
                    if (crackleGain) crackleGain.gain.setTargetAtTime(0.45, actx.currentTime, 0.1);
                }}
            }}

            // 遷音速凝縮ベイパーコーン
            if (vel > 310.0 && vel < 380.0) {{
                const vapInt = Math.sin(((vel - 310.0) / 70.0) * Math.PI);
                vaporCone.material.opacity = vapInt * 0.75;
                vaporCone.scale.set(1.0 + Math.random()*0.08, 1.0, 1.0 + Math.random()*0.08);
            }} else {{
                vaporCone.material.opacity = 0.0;
            }}

            // アナウンス
            if (pt0.event === "SUPERSONIC" && !voicedEvents.has('supersonic') && !pt0.exploded) {{
                voicedEvents.add('supersonic');
                speakWebcastHost("Vehicle is supersonic. Transonic buffet nominal.");
            }}
            if (pt0.event === "MAX_Q" && !voicedEvents.has('maxq') && !pt0.exploded) {{
                voicedEvents.add('maxq');
                speakWebcastHost("Vehicle has passed through Max-Q, maximum aerodynamic stress.");
            }}
            if (pt0.event === "HOT_STAGING" && !stageSeparated && !pt0.exploded) {{
                stageSeparated = true;
                s1Group.visible = false;
                voicedEvents.add('hotstaging');
                speakWebcastHost("Hot-staging confirmed! Stage two engine ignition confirmed.");
                for (let k = 0; k < 45; k++) {{
                    const a = (k / 45) * Math.PI * 2;
                    emitP(rx, ry + 9.8, 0, Math.cos(a)*0.45, Math.sin(a)*0.45, 0, 0.8, 4.2, 32, flameColorHex, 0.9);
                }}
            }}
            if (pt0.event === "ORBIT" && !voicedEvents.has('orbit')) {{
                voicedEvents.add('orbit');
                speakWebcastHost("Engine cutoff confirmed! Spacecraft has achieved stable orbit!");
            }}

            // 火炎・プルーム制御 (実写排気物理)
            if (pt0.thrust && !pt0.exploded) {{
                plumeGroup.visible = true;
                plumeGroup.position.y = (pt0.stage === 1) ? 1.4 : s2BaseY;

                // 真空度によるクラゲ状排気プルームの膨張
                const vacExp = 1.0 + Math.min(5.5, alt / 18.0);
                const flick = 0.92 + Math.random() * 0.18;
                coreFlame.scale.set(1.0, flick, 1.0);
                outerPlume.scale.set(vacExp, flick * (1.0 + vacExp * 0.3), vacExp);

                // 低空時はショックダイヤモンドが明瞭
                shockDiamonds.forEach(sd => {{
                    sd.visible = (alt < 35.0);
                }});

                engineLight.position.set(rx, ry + plumeGroup.position.y, 2.5);
                engineLight.intensity = (alt < 4.0) ? 7.5 : 3.2;

                streakFlare.style.opacity = (Math.random() < 0.12) ? "0.38" : "0.22";

                // 低空スモークトレイル
                if (alt < 20.0) {{
                    for (let s = 0; s < 2; s++) {{
                        emitP(rx, ry + 1.0, 0, -upX * 0.28, -upY * 0.28, 0, 1.0, 5.2, 38, 0xf0f4fa, 0.72);
                    }}
                }}
            }} else {{
                plumeGroup.visible = false;
                engineLight.intensity = 0.0;
                streakFlare.style.opacity = "0";
            }}

            // パーティクル物理更新
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

            // テレメトリーHUD更新
            document.getElementById('tv-spd').innerText = Math.round(vel * 3.6).toLocaleString();
            document.getElementById('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            document.getElementById('tv-q').innerText   = q.toFixed(1);
            document.getElementById('tv-stage-badge').innerText = pt0.stage === 1 ? "STAGE 1" : "STAGE 2";

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
    components.html(html_code, height=900)
