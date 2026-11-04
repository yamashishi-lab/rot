import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbital Architect Pro: ロケット設計＆軌道管制", layout="wide")

st.title("🚀 Orbital Architect Pro - 限界設計・軌道投入シミュレーター")
st.markdown("エンジン内部サイクル、ノズル膨張比、タンク肉厚、フェアリング投棄高度まで緻密にチューニングし、高度200km・第一宇宙速度（7,800m/s）の楕円・円軌道へ投入せよ。")

# --- 詳細パーツデータベース ---
PROPELLANTS = {
    "RP-1 (ケロシン) / LOX [高密度・大気圏向]": {"base_isp_sl": 285, "base_isp_vac": 312, "base_thrust": 900, "density": 1.02, "temp_factor": 1.0, "flame_color": "0xffaa22"},
    "LCH4 (液体メタン) / LOX [次世代バランス]": {"base_isp_sl": 325, "base_isp_vac": 360, "base_thrust": 1800, "density": 0.82, "temp_factor": 1.1, "flame_color": "0x55aaff"},
    "LH2 (液体水素) / LOX [最高燃費・極低温・巨大タンク]": {"base_isp_sl": 340, "base_isp_vac": 445, "base_thrust": 1100, "density": 0.32, "temp_factor": 0.9, "flame_color": "0xff8844"}
}

PUMP_CYCLES = {
    "ガス発生器サイクル (GG) [軽量・高信頼・燃費微減]": {"isp_mod": 0.96, "thrust_mod": 0.95, "mass_mod": 0.85, "max_pressure_limit": 140},
    "エキスパンダーサイクル [上段向き・高効率・低推力]": {"isp_mod": 1.03, "thrust_mod": 0.65, "mass_mod": 1.0, "max_pressure_limit": 100},
    "二段燃焼サイクル (SC) [高出力・高圧・重]": {"isp_mod": 1.02, "thrust_mod": 1.15, "mass_mod": 1.20, "max_pressure_limit": 240},
    "フルフロー二段燃焼 (FFSC) [究極性能・超高圧制御シビア]": {"isp_mod": 1.05, "thrust_mod": 1.35, "mass_mod": 1.30, "max_pressure_limit": 300}
}

MATERIALS = {
    "A2195 アルミ・リチウム合金 (標準航空宇宙材)": {"base_dry_ratio": 0.065, "max_q_base": 45.0, "max_g_base": 6.0, "mat_id": "al"},
    "TORAYCA カーボン複合材 (超軽量・熱とせん断に弱い)": {"base_dry_ratio": 0.042, "max_q_base": 34.0, "max_g_base": 5.2, "mat_id": "cf"},
    "304L 高強度ステンレス (激重・超高耐熱・高剛性)": {"base_dry_ratio": 0.095, "max_q_base": 85.0, "max_g_base": 9.5, "mat_id": "ss"}
}

FAIRINGS = {
    "標準オジーブ型 (バランス・耐熱1,800K)": {"mass": 1.8, "cd": 0.32, "heat_limit": 1800, "shape_id": "ogive"},
    "超鋭角ニードル型 (低空気抵抗・先端加熱に弱い 1,450K)": {"mass": 1.4, "cd": 0.22, "heat_limit": 1450, "shape_id": "needle"},
    "鈍頭大型フェアリング (高耐熱2,400K・空気抵抗大)": {"mass": 2.6, "cd": 0.46, "heat_limit": 2400, "shape_id": "blunt"}
}

PRESSURIZATION = {
    "ヘリウム高圧ボトリング加圧 (安定・タンク重量増)": {"mass_penalty": 0.008, "g_bonus": 1.15},
    "自生加圧 (Autogenous) (軽量・高G時に座屈リスク)": {"mass_penalty": 0.002, "g_bonus": 0.90}
}

# --- UI: タブ分けされた本格設計画面 ---
tab1, tab2, tab3 = st.tabs(["🔥 第1段（ブースター）詳細設計", "🛰️ 第2段（オービター）＆フェアリング", "📐 飛行誘導＆ミッション管制"])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### エンジン・推進系")
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=1)
        s1_cycle = st.selectbox("第1段 ターボポンプ方式", list(PUMP_CYCLES.keys()), index=3)
        s1_eng_count = st.slider("第1段 エンジンクラスター基数", 1, 12, 4)
    with c2:
        st.markdown("#### 燃焼室・ノズル改造")
        s1_pc = st.slider("第1段 燃焼室圧力 (bar)", 50, 350, 230, step=10, help="高いほど推力と燃費が上がるが、サイクルの限界を超えるとタービンが爆散する")
        s1_eps = st.slider("第1段 ノズル開口膨張比 (ε)", 10, 80, 28, step=2, help="大気圏内は15〜35が適正。大きすぎると低高度で過膨張を起こしノズルが破損する")
        s1_tvc = st.slider("ジンバル（姿勢制御）最大舵角 (度)", 2, 15, 8)
    with c3:
        st.markdown("#### タンク構造・肉厚")
        s1_fuel = st.slider("第1段 推進剤質量 (トン)", 30.0, 500.0, 220.0, step=10.0)
        s1_mat = st.selectbox("第1段 タンク材質", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("第1段 タンク肉厚係数 (mm相当)", 1.5, 6.0, 3.0, step=0.2, help="薄くすると劇的に軽くなるが、Max-Qや高Gで空中分解する")
        s1_press = st.selectbox("第1段 タンク加圧システム", list(PRESSURIZATION.keys()), index=1)

with tab2:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 第2段 エンジン・推進系")
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=2)
        s2_cycle = st.selectbox("第2段 ターボポンプ方式", list(PUMP_CYCLES.keys()), index=1)
        s2_eng_count = st.slider("第2段 エンジン基数", 1, 4, 1)
        s2_pc = st.slider("第2段 燃焼室圧力 (bar)", 30, 250, 85, step=5)
        s2_eps = st.slider("第2段 真空ノズル膨張比 (ε)", 30, 200, 110, step=5, help="真空空間では80〜180の高膨張比が圧倒的な燃費を生む")
    with c2:
        st.markdown("#### 第2段 タンク構造")
        s2_fuel = st.slider("第2段 推進剤質量 (トン)", 5.0, 120.0, 42.0, step=1.0)
        s2_mat = st.selectbox("第2段 タンク材質", list(MATERIALS.keys()), index=1)
        s2_thick = st.slider("第2段 タンク肉厚係数 (mm相当)", 1.0, 5.0, 2.2, step=0.2)
    with c3:
        st.markdown("#### フェアリング＆ペイロード")
        fairing_type = st.selectbox("フェアリング空力形状", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("フェアリング投棄（分離）高度 (km)", 40.0, 150.0, 85.0, step=5.0, help="低すぎると衛星が空気摩擦熱で焼損、高すぎると重りで速度不足になる")
        payload_mass = st.slider("人工衛星（ペイロード）質量 (トン)", 0.5, 25.0, 4.5, step=0.5)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 誘導アルゴリズム（重力ターン・スロットル）")
        turn_start_alt = st.slider("ピッチオーバー（重力ターン）開始高度 (km)", 1.0, 20.0, 4.5, step=0.5)
        turn_end_alt = st.slider("水平加速移行高度 (km)", 60.0, 180.0, 115.0, step=5.0)
        turn_exponent = st.slider("重力ターン曲率係数 (小:急激に傾く / 大:緩やかに傾く)", 0.4, 1.5, 0.80, step=0.05)
    with c2:
        st.markdown("#### 推力リミッター制御")
        throttle_maxq = st.slider("Max-Q（最大動圧領域）通過時のスロットル絞り (%)", 40, 100, 72)
        max_g_limit_cut = st.slider("Gリミッター（加速度制限オートスロットル）(G)", 3.0, 10.0, 4.8, step=0.2, help="後半で機体が軽くなった際、構造破壊を防ぐため自動で推力を絞る")

# --- パーツパラメータからの詳細スペック算出関数 ---
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

# --- スペックサマリーバー ---
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("総打ち上げ質量 / 初期TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f} (1.2〜1.6推奨)")
m2.metric("理論総 ΔV (目標: 9,300 m/s以上)", f"{total_dv:.0f} m/s", f"1段:{dv_s1:.0f} / 2段:{dv_s2:.0f}")
m3.metric("第1段 耐動圧(Max-Q) / 耐G限界", f"{s1_spec['max_q']:.1f} kPa", f"耐G: {s1_spec['max_g']:.1f} G")
m4.metric("第1段 燃費(海面/真空) & 推力", f"{s1_spec['isp_sl']:.0f}s / {s1_spec['isp_vac']:.0f}s", f"離床推力: {s1_spec['thrust_sl']:.0f} kN")

# --- 物理シミュレーション計算 ---
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
    status = "飛行中"
    fail_reason = None

    # カウントダウン T-5.0s 〜 T-0.0s
    for cd_step in range(10):
        t_cd = -5.0 + cd_step * 0.5
        pre_ignition = bool(t_cd >= -2.5)
        history.append({
            "t": float(t_cd), "x": 0.0, "y": float(R_earth), "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "temp": 288.0, "stage": 1, "fairing": True,
            "exploded": False, "thrust": pre_ignition, "pitch": 0.0, "phase": "COUNTDOWN"
        })

    # 発射台でのハードウェア限界判定
    if s1_spec["pc"] > s1_spec["pc_limit"]:
        fail_reason = f"T+0.2秒: 第1段燃焼室圧力({s1_spec['pc']} bar)が限界({s1_spec['pc_limit']} bar)を超過！発射台上で大爆発！"
        history.append({
            "t": 0.2, "x": 0.0, "y": float(R_earth + 2.0), "alt": 0.002, "v": 2.0,
            "q": 0.0, "g": 0.0, "temp": 1800.0, "stage": 1, "fairing": True,
            "exploded": True, "thrust": False, "pitch": 0.0, "phase": "PAD_EXPLOSION"
        })
        return history, fail_reason

    if s1_spec["eps"] > 55:
        fail_reason = f"T+0.5秒: ノズル膨張比(ε={s1_spec['eps']})過大による過膨張振動でノズル粉砕！"
        history.append({
            "t": 0.5, "x": 0.0, "y": float(R_earth + 12.0), "alt": 0.012, "v": 8.0,
            "q": 0.1, "g": 1.2, "temp": 1600.0, "stage": 1, "fairing": True,
            "exploded": True, "thrust": False, "pitch": 0.0, "phase": "PAD_EXPLOSION"
        })
        return history, fail_reason

    if twr_init <= 1.02:
        fail_reason = f"推力重量比(TWR: {twr_init:.2f})不足のため浮上不能！"
        for stand_step in range(8):
            history.append({
                "t": float(stand_step * 0.5), "x": 0.0, "y": float(R_earth), "alt": 0.0, "v": 0.0,
                "q": 0.0, "g": float(twr_init), "temp": 320.0, "stage": 1, "fairing": True,
                "exploded": False, "thrust": True, "pitch": 0.0, "phase": "PAD_STALL"
            })
        return history, fail_reason

    for step in range(1800):
        t = float(step * dt)
        r = float(np.sqrt(x**2 + y**2))
        alt = float(r - R_earth)
        alt_km = float(alt / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))

        if alt < -10:
            status = "墜落"
            fail_reason = f"T+{t:.0f}秒: 推力または速度不足により海面へ激突。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": 0.0, "v": v, "q": 0.0, "g": 0.0,
                "temp": 1200.0, "stage": int(stage), "fairing": bool(fairing_attached),
                "exploded": True, "thrust": False, "pitch": 0.0, "phase": "CRASH"
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

        # フェアリング分離
        if fairing_attached and alt_km >= fairing_sep_alt:
            fairing_attached = False
            if aero_temp > 650.0 or q > 1.2:
                fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): フェアリング早期投棄による空気摩擦熱焼損！"
                history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp, "stage": int(stage), "fairing": False, "exploded": True, "thrust": False, "pitch": visual_pitch, "phase": "RUD"})
                break

        f_mass = fair_spec["mass"] * 1000.0 if fairing_attached else 0.0

        if stage == 1:
            if fuel_rem <= 0:
                stage = 2
                fuel_rem = float(s2_fuel * 1000.0)
                if s2_spec["pc"] > s2_spec["pc_limit"]:
                    fail_reason = f"T+{t:.0f}秒: 第2段点火時にポンプ限界超過爆発！"
                    history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp, "stage": 2, "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "phase": "RUD"})
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
                    fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): 低高度での高膨張比ノズル点火による過膨張粉砕！"
                    history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp, "stage": 2, "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "phase": "RUD"})
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
            fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): Max-Q動圧({q:.1f} kPa)超過による空中分解（RUD）！"
            history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp, "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "phase": "RUD"})
            break
        if acc_g > cur_spec["max_g"]:
            fail_reason = f"T+{t:.0f}秒: 加速度({acc_g:.1f} G)過大による構造圧壊！"
            history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp, "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "phase": "RUD"})
            break
        if fairing_attached and aero_temp > fair_spec["heat_limit"]:
            fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): 空力加熱({aero_temp:.0f} K)によるフェアリング融解・空中分解！"
            history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp, "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False, "pitch": visual_pitch, "phase": "RUD"})
            break

        vx = float(vx + ax * dt)
        vy = float(vy + ay * dt)
        x = float(x + vx * dt)
        y = float(y + vy * dt)

        if step < 40 or step % 2 == 0:
            history.append({
                "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp,
                "stage": int(stage), "fairing": bool(fairing_attached), "exploded": False, "thrust": bool(thrust > 0),
                "pitch": visual_pitch, "phase": "FLIGHT"
            })

        v_radial = float(vx * np.sin(theta) + vy * np.cos(theta))
        v_tangent = float(vx * np.cos(theta) - vy * np.sin(theta))
        if alt_km >= 180.0 and v_tangent >= 7750.0 and abs(v_radial) < 420.0:
            status = "軌道投入成功"
            history.append({
                "t": t + dt, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp,
                "stage": int(stage), "fairing": bool(fairing_attached), "exploded": False, "thrust": False,
                "pitch": visual_pitch, "phase": "ORBIT_INSERTION"
            })
            break

    if not fail_reason and status != "軌道投入成功":
        fail_reason = f"目標高度・速度に届かずサブオービタル落下。(最高速度: {v:.0f} m/s, 到達高度: {alt_km:.1f} km)"

    return history, fail_reason

# --- 発射シークエンス＆シネマティックTV中継ビューワー ---
if st.button("🔴 LIVE BROADCAST: 発射中継開始 (自動カメラワーク)", use_container_width=True, type="primary"):
    traj_data, error_msg = run_simulation()

    if error_msg:
        st.warning(f"⚠️ ミッションテレメトリー速報: {error_msg}")
    else:
        st.success("🎉 ミッション完全成功！第一宇宙速度到達・軌道投入を確認しました！")

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

    traj_json = json.dumps(
        traj_data,
        default=lambda o: float(o) if isinstance(o, np.floating) else (int(o) if isinstance(o, np.integer) else (bool(o) if isinstance(o, np.bool_) else str(o)))
    )
    cfg_json = json.dumps(rocket_visual_cfg)

    html_code = f"""
    <div id="broadcast-frame" style="position: relative; width: 100%; height: 720px; background: #000; border-radius: 8px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; user-select: none;">
        <!-- 3DレンダリングCanvas（ユーザーのポインタ・ドラッグ操作を完全無効化） -->
        <div id="canvas-container" style="width: 100%; height: 100%; pointer-events: none;"></div>

        <!-- TV放送スタイル: 映画用2.39:1シネマスコープ黒帯 (上部) -->
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 42px; background: rgba(0,0,0,0.85); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 10;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="display: inline-block; width: 10px; height: 10px; background: #ff2222; border-radius: 50%; box-shadow: 0 0 8px #ff2222; animation: blink 1s infinite alternate;"></span>
                <span style="color: #fff; font-weight: 800; font-size: 13px; letter-spacing: 2px;">LIVE BROADCAST</span>
                <span style="color: rgba(255,255,255,0.4); font-size: 11px;">|</span>
                <span id="cam-indicator" style="color: #4da6ff; font-size: 11px; font-weight: 600; letter-spacing: 1px;">CAM 1: LAUNCH COMPLEX HERO</span>
            </div>
            <div id="top-msg" style="color: #00ffcc; font-size: 13px; font-weight: 700; letter-spacing: 1px;">STAGE 1 PROPULSION LOADED</div>
        </div>

        <style>
            @keyframes blink {{ from {{ opacity: 0.3; }} to {{ opacity: 1.0; }} }}
        </style>

        <!-- TV放送スタイル: 下部ミニマルティッカーHUD (映像を遮らないスリムバー) -->
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(0,0,0,0.92) 0%, rgba(5,10,20,0.82) 80%, rgba(0,0,0,0) 100%); padding: 18px 28px 12px 28px; box-sizing: border-box; display: flex; align-items: flex-end; justify-content: space-between; z-index: 10;">
            <!-- タイマー＆ステータス -->
            <div style="display: flex; flex-direction: column; gap: 4px;">
                <div id="tv-status" style="color: #ffaa00; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">PRE-LAUNCH ARMED</div>
                <div id="tv-timer" style="color: #ffffff; font-size: 38px; font-weight: 900; font-family: 'Courier New', monospace; letter-spacing: 1px; text-shadow: 0 0 15px rgba(255,255,255,0.4);">T- 05.0</div>
            </div>

            <!-- 横並びのテレメトリーストリーム -->
            <div style="display: flex; gap: 36px; border-left: 2px solid rgba(255,255,255,0.2); padding-left: 28px;">
                <div>
                    <div style="font-size: 11px; color: #8899aa; letter-spacing: 1px; margin-bottom: 2px;">SPEED</div>
                    <div style="color: #fff; font-size: 22px; font-weight: 800; font-family: 'Courier New', monospace;"><span id="tv-spd">0</span> <span style="font-size: 13px; font-weight: normal; color: #8899aa;">m/s</span></div>
                </div>
                <div>
                    <div style="font-size: 11px; color: #8899aa; letter-spacing: 1px; margin-bottom: 2px;">ALTITUDE</div>
                    <div style="color: #fff; font-size: 22px; font-weight: 800; font-family: 'Courier New', monospace;"><span id="tv-alt">0.0</span> <span style="font-size: 13px; font-weight: normal; color: #8899aa;">km</span></div>
                </div>
                <div>
                    <div style="font-size: 11px; color: #8899aa; letter-spacing: 1px; margin-bottom: 2px;">DYNAMIC PRESS</div>
                    <div style="color: #fff; font-size: 22px; font-weight: 800; font-family: 'Courier New', monospace;"><span id="tv-q">0.0</span> <span style="font-size: 13px; font-weight: normal; color: #8899aa;">kPa</span></div>
                </div>
                <div>
                    <div style="font-size: 11px; color: #8899aa; letter-spacing: 1px; margin-bottom: 2px;">NOSE TEMP</div>
                    <div style="color: #fff; font-size: 22px; font-weight: 800; font-family: 'Courier New', monospace;"><span id="tv-temp">288</span> <span style="font-size: 13px; font-weight: normal; color: #8899aa;">K</span></div>
                </div>
            </div>
        </div>

        <!-- 緊迫時のフルスクリーン閃光オーバーレイ -->
        <div id="flash-overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #ffffff; opacity: 0; pointer-events: none; transition: opacity 0.08s; z-index: 5;"></div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const data = {traj_json};
        const cfg = {cfg_json};
        const container = document.getElementById('canvas-container');
        const flashOverlay = document.getElementById('flash-overlay');

        const scene = new THREE.Scene();
        // TV映画用シネマティックカメラ (画角40度)
        const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.05, 700000);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.25;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        const SCALE = 0.0001;
        const R_EARTH = 6371000 * SCALE; // 637.1 units

        // --- パーティクル用グラデーションテクスチャ動的生成 ---
        function createRadialTexture(innerColor, midColor, outerColor) {{
            const c = document.createElement('canvas');
            c.width = 128; c.height = 128;
            const ctx = c.getContext('2d');
            const g = ctx.createRadialGradient(64, 64, 2, 64, 64, 64);
            g.addColorStop(0.0, innerColor);
            g.addColorStop(0.35, midColor);
            g.addColorStop(1.0, outerColor);
            ctx.fillStyle = g;
            ctx.fillRect(0, 0, 128, 128);
            return new THREE.CanvasTexture(c);
        }}

        const smokeTex = createRadialTexture('rgba(255,255,255,0.95)', 'rgba(215,225,235,0.5)', 'rgba(100,110,125,0.0)');
        const fireTex  = createRadialTexture('rgba(255,255,245,1.0)', 'rgba(255,140,25,0.85)', 'rgba(210,30,0,0.0)');

        // --- 星空背景 ---
        const starGeo = new THREE.BufferGeometry();
        const starCount = 5000;
        const starPos = new Float32Array(starCount * 3);
        for(let i = 0; i < starCount; i++) {{
            const r = 5000 + Math.random() * 8000;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            starPos[i*3] = r * Math.sin(phi) * Math.cos(theta);
            starPos[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
            starPos[i*3+2] = r * Math.cos(phi);
        }}
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({{ size: 2.0, color: 0xffffff, transparent: true, opacity: 0.85 }})));

        // --- プロシージャル地球＆大気層 ---
        const earthGroup = new THREE.Group();
        scene.add(earthGroup);

        const earthVertexShader = `
            varying vec3 vNormal;
            varying vec3 vPosition;
            void main() {{
                vNormal = normalize(normalMatrix * normal);
                vPosition = position;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }}
        `;
        const earthFragmentShader = `
            varying vec3 vNormal;
            varying vec3 vPosition;
            float hash(vec3 p) {{
                p = fract(p * 0.3183099 + .1);
                p *= 17.0;
                return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
            }}
            float noise(vec3 x) {{
                vec3 i = floor(x);
                vec3 f = fract(x);
                f = f * f * (3.0 - 2.0 * f);
                return mix(mix(mix(hash(i + vec3(0,0,0)), hash(i + vec3(1,0,0)), f.x),
                               mix(hash(i + vec3(0,1,0)), hash(i + vec3(1,1,0)), f.x), f.y),
                           mix(mix(hash(i + vec3(0,0,1)), hash(i + vec3(1,0,1)), f.x),
                               mix(hash(i + vec3(0,1,1)), hash(i + vec3(1,1,1)), f.x), f.y), f.z);
            }}
            void main() {{
                vec3 pos = vPosition * 0.012;
                float n = noise(pos) * 0.5 + noise(pos * 2.3) * 0.28 + noise(pos * 6.0) * 0.15;
                float clouds = smoothstep(0.55, 0.78, noise(pos * 3.2 + vec3(1.5, 0.8, 2.1)) * 0.65 + noise(pos * 8.5) * 0.35);
                
                vec3 deepOcean = vec3(0.02, 0.10, 0.25);
                vec3 landGreen = vec3(0.12, 0.28, 0.12);
                vec3 landDesert = vec3(0.38, 0.32, 0.20);
                
                vec3 surf = mix(deepOcean, mix(landGreen, landDesert, smoothstep(0.5, 0.7, n)), smoothstep(0.48, 0.52, n));
                surf = mix(surf, vec3(0.95, 0.98, 1.0), clouds * 0.8);

                vec3 lightDir = normalize(vec3(0.8, 0.55, 0.45));
                float diff = max(dot(vNormal, lightDir), 0.05);
                float rim = pow(1.0 - max(dot(vNormal, vec3(0.0, 0.0, 1.0)), 0.0), 3.2);
                vec3 atmos = vec3(0.25, 0.65, 1.0) * rim * 0.7;

                gl_FragColor = vec4(surf * diff + atmos, 1.0);
            }}
        `;
        const earthMesh = new THREE.Mesh(
            new THREE.SphereGeometry(R_EARTH, 128, 128),
            new THREE.ShaderMaterial({{ vertexShader: earthVertexShader, fragmentShader: earthFragmentShader }})
        );
        earthGroup.add(earthMesh);

        // 大気散乱ハロー
        earthGroup.add(new THREE.Mesh(
            new THREE.SphereGeometry(R_EARTH + 12.0, 96, 96),
            new THREE.MeshBasicMaterial({{ color: 0x3388ff, transparent: true, opacity: 0.14, side: THREE.BackSide, blending: THREE.AdditiveBlending }})
        ));

        // 目標軌道リング
        scene.add(new THREE.Mesh(
            new THREE.RingGeometry(R_EARTH + 20.0, R_EARTH + 20.25, 180),
            new THREE.MeshBasicMaterial({{ color: 0x00ff88, side: THREE.DoubleSide, transparent: true, opacity: 0.25 }})
        ));

        // 光源
        const sunLight = new THREE.DirectionalLight(0xfff8ee, 2.4);
        sunLight.position.set(800, 1400, 900);
        scene.add(sunLight);
        scene.add(new THREE.HemisphereLight(0x88bbff, 0x112233, 0.75));

        const engineLight = new THREE.PointLight(0xff7711, 0.0, 50);
        scene.add(engineLight);

        // --- 1. 発射台（Launch Complex）---
        const launchPadGroup = new THREE.Group();
        launchPadGroup.position.set(0, R_EARTH, 0);
        scene.add(launchPadGroup);

        const concreteMat = new THREE.MeshStandardMaterial({{ color: 0x555a60, roughness: 0.85, metalness: 0.1 }});
        const darkSteelMat = new THREE.MeshStandardMaterial({{ color: 0x252a32, roughness: 0.45, metalness: 0.8 }});
        const trussMat = new THREE.MeshStandardMaterial({{ color: 0x353d47, roughness: 0.5, metalness: 0.8, wireframe: true }});
        const hazardMat = new THREE.MeshStandardMaterial({{ color: 0xd45d0f, roughness: 0.4, metalness: 0.5 }});

        // パッドベース & ランチマウント
        const padBase = new THREE.Mesh(new THREE.BoxGeometry(10.0, 1.2, 8.0), concreteMat);
        padBase.position.set(0, -0.6, 0);
        launchPadGroup.add(padBase);

        const launchMount = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.5, 1.4, 16), darkSteelMat);
        launchMount.position.set(0, 0.7, 0);
        launchPadGroup.add(launchMount);

        // メインランチタワー
        const towerHeight = 11.5;
        const towerCore = new THREE.Mesh(new THREE.BoxGeometry(1.4, towerHeight, 1.4), darkSteelMat);
        towerCore.position.set(-2.4, towerHeight / 2, 0);
        launchPadGroup.add(towerCore);

        const towerTruss = new THREE.Mesh(new THREE.BoxGeometry(1.55, towerHeight, 1.55), trussMat);
        towerTruss.position.set(-2.4, towerHeight / 2, 0);
        launchPadGroup.add(towerTruss);

        // スイングバック可動式アンビリカルアーム
        const umbilicalArms = [];
        [3.2, 6.2, 8.8].forEach(h => {{
            const armPivot = new THREE.Group();
            armPivot.position.set(-1.7, h, 0);
            const armMesh = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.22, 0.35), hazardMat);
            armMesh.position.set(0.7, 0, 0);
            armPivot.add(armMesh);
            launchPadGroup.add(armPivot);
            umbilicalArms.push(armPivot);
        }});

        // 避雷針マスト
        [[-4.2, -3.2], [4.2, -3.2], [-4.2, 3.2], [4.2, 3.2]].forEach(([lx, lz]) => {{
            const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.22, 13.5, 8), concreteMat);
            mast.position.set(lx, 6.75, lz);
            launchPadGroup.add(mast);
        }});

        // --- 2. 設計スペック連動 PBRロケットモデル ---
        function getMaterialBySpec(matId) {{
            if (matId === 'ss') return new THREE.MeshStandardMaterial({{ color: 0xd8e0e8, metalness: 0.92, roughness: 0.16 }});
            if (matId === 'cf') return new THREE.MeshStandardMaterial({{ color: 0x1c2026, metalness: 0.35, roughness: 0.55 }});
            return new THREE.MeshStandardMaterial({{ color: 0xf2f4f8, metalness: 0.20, roughness: 0.38 }});
        }}

        const s1TankMat = getMaterialBySpec(cfg.s1_mat);
        const s2TankMat = getMaterialBySpec(cfg.s2_mat);
        const interstageMat = new THREE.MeshStandardMaterial({{ color: 0x181c22, metalness: 0.5, roughness: 0.6 }});
        const nozzleMat = new THREE.MeshStandardMaterial({{ color: 0x333842, metalness: 0.88, roughness: 0.28 }});

        const rocketGroup = new THREE.Group();
        scene.add(rocketGroup);

        // 第1段
        const s1Group = new THREE.Group();
        rocketGroup.add(s1Group);

        const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 5.2, 32), s1TankMat);
        s1Body.position.y = 3.6;
        s1Group.add(s1Body);

        const feedline = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 5.4, 12), s1TankMat);
        feedline.position.set(0.55, 3.6, 0);
        s1Group.add(feedline);

        const interstage = new THREE.Mesh(new THREE.CylinderGeometry(0.555, 0.555, 0.75, 32), interstageMat);
        interstage.position.y = 6.35;
        s1Group.add(interstage);

        // グリッドフィン
        for (let i = 0; i < 4; i++) {{
            const angle = (i * Math.PI) / 2 + Math.PI / 4;
            const gf = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.05, 0.22), darkSteelMat);
            gf.position.set(Math.cos(angle) * 0.65, 6.15, Math.sin(angle) * 0.65);
            gf.rotation.y = -angle;
            s1Group.add(gf);
        }}

        // 第1段エンジンノズル
        const s1NozzleLen = 0.35 + (cfg.s1_eps / 80.0) * 0.25;
        for (let i = 0; i < cfg.s1_eng; i++) {{
            const bell = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.14, s1NozzleLen, 16, 1, true), nozzleMat);
            bell.material.side = THREE.DoubleSide;
            if (cfg.s1_eng === 1) {{
                bell.position.set(0, 0.8 - s1NozzleLen / 2, 0);
            }} else {{
                const ringR = cfg.s1_eng <= 4 ? 0.24 : 0.34;
                const a = (i / cfg.s1_eng) * Math.PI * 2;
                bell.position.set(Math.cos(a) * ringR, 0.8 - s1NozzleLen / 2, Math.sin(a) * ringR);
            }}
            s1Group.add(bell);
        }}

        // 第2段
        const s2Group = new THREE.Group();
        rocketGroup.add(s2Group);

        const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(0.54, 0.54, 2.2, 32), s2TankMat);
        s2Body.position.y = 7.8;
        s2Group.add(s2Body);

        const s2NozzleLen = 0.55;
        for (let i = 0; i < cfg.s2_eng; i++) {{
            const bell2 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.26, s2NozzleLen, 20, 1, true), nozzleMat);
            bell2.material.side = THREE.DoubleSide;
            const offset = cfg.s2_eng === 1 ? 0 : (i - (cfg.s2_eng - 1) / 2) * 0.28;
            bell2.position.set(offset, 6.7 - s2NozzleLen / 2, 0);
            s2Group.add(bell2);
        }}

        // ペイロード（金箔衛星 + パネル）
        const payloadGroup = new THREE.Group();
        payloadGroup.position.set(0, 9.45, 0);
        s2Group.add(payloadGroup);

        const goldFoilMat = new THREE.MeshStandardMaterial({{ color: 0xffbb22, metalness: 0.9, roughness: 0.25 }});
        const satBus = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.32, 0.85, 8), goldFoilMat);
        payloadGroup.add(satBus);

        const panelL = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.03, 0.25), new THREE.MeshStandardMaterial({{ color: 0x113388, metalness: 0.8 }}));
        panelL.position.set(-0.45, 0, 0);
        const panelR = panelL.clone();
        panelR.position.set(0.45, 0, 0);
        payloadGroup.add(panelL, panelR);

        // 分離可能フェアリング
        const fairingHeight = cfg.fairing_shape === 'needle' ? 2.6 : (cfg.fairing_shape === 'blunt' ? 1.7 : 2.1);
        const fairingMat = new THREE.MeshStandardMaterial({{ color: 0xf5f7fa, metalness: 0.25, roughness: 0.35, side: THREE.DoubleSide }});
        const fairingLeft = new THREE.Mesh(new THREE.ConeGeometry(0.56, fairingHeight, 32, 1, false, 0, Math.PI), fairingMat.clone());
        const fairingRight = new THREE.Mesh(new THREE.ConeGeometry(0.56, fairingHeight, 32, 1, false, Math.PI, Math.PI), fairingMat.clone());
        fairingLeft.position.set(0, 8.9 + fairingHeight / 2, 0);
        fairingRight.position.set(0, 8.9 + fairingHeight / 2, 0);
        s2Group.add(fairingLeft, fairingRight);

        // ジェット噴射炎
        const plumeGroup = new THREE.Group();
        rocketGroup.add(plumeGroup);

        const coreCone = new THREE.Mesh(
            new THREE.ConeGeometry(0.32, 2.8, 20),
            new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending }})
        );
        coreCone.rotation.x = Math.PI;
        coreCone.position.y = -1.4;
        plumeGroup.add(coreCone);

        const outerFlameMat = new THREE.MeshBasicMaterial({{ color: parseInt(cfg.s1_flame), transparent: true, opacity: 0.65, blending: THREE.AdditiveBlending }});
        const outerCone = new THREE.Mesh(new THREE.ConeGeometry(0.58, 5.2, 24), outerFlameMat);
        outerCone.rotation.x = Math.PI;
        outerCone.position.y = -2.6;
        plumeGroup.add(outerCone);

        // --- 3. パーティクル＆空中分解物理デブリシステム ---
        const MAX_PARTICLES = 600;
        const particlePool = [];
        const particleGroup = new THREE.Group();
        scene.add(particleGroup);

        for (let i = 0; i < MAX_PARTICLES; i++) {{
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({{ map: smokeTex, transparent: true, opacity: 0, depthWrite: false }}));
            sp.visible = false;
            particleGroup.add(sp);
            particlePool.push({{ sprite: sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, startScale: 1, endScale: 3, baseOpacity: 0.8 }});
        }}

        let pCursor = 0;
        function spawnParticle(x, y, z, vx, vy, vz, startScale, endScale, maxAge, tex, colorHex, opacity, additive=false) {{
            const p = particlePool[pCursor];
            pCursor = (pCursor + 1) % MAX_PARTICLES;
            p.active = true;
            p.sprite.visible = true;
            p.sprite.position.set(x, y, z);
            p.vx = vx; p.vy = vy; p.vz = vz;
            p.age = 0; p.maxAge = maxAge;
            p.startScale = startScale; p.endScale = endScale;
            p.baseOpacity = opacity;
            p.sprite.material.map = tex;
            p.sprite.material.color.setHex(colorHex);
            p.sprite.material.blending = additive ? THREE.AdditiveBlending : THREE.NormalBlending;
            p.sprite.scale.set(startScale, startScale, 1);
        }}

        const debrisList = [];
        const debrisGroup = new THREE.Group();
        scene.add(debrisGroup);

        let explosionTriggered = false;
        let stageSeparated = false;
        let fairingSeparated = false;
        let cameraShakeIntensity = 0.0;

        function triggerCatastrophicExplosion(wx, wy, wz, baseVx, baseVy) {{
            if (explosionTriggered) return;
            explosionTriggered = true;
            cameraShakeIntensity = 2.4; // 強烈なカメラ振動
            engineLight.intensity = 15.0;
            engineLight.color.setHex(0xff3300);

            // 閃光白フラッシュ
            flashOverlay.style.opacity = '0.9';
            setTimeout(() => {{ flashOverlay.style.opacity = '0'; }}, 90);

            // 巨大ファイアボール
            for (let i = 0; i < 150; i++) {{
                const spd = 0.08 + Math.random() * 0.45;
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos(2 * Math.random() - 1);
                const dvx = baseVx + spd * Math.sin(phi) * Math.cos(theta);
                const dvy = baseVy + spd * Math.sin(phi) * Math.sin(theta);
                const dvz = spd * Math.cos(phi);

                if (i < 70) {{
                    const col = i < 20 ? 0xffffff : (i < 45 ? 0xff7711 : 0xcc2200);
                    spawnParticle(wx, wy, wz, dvx, dvy, dvz, 1.2, 8.5 + Math.random()*4, 38 + Math.random()*30, fireTex, col, 0.95, true);
                }} else {{
                    spawnParticle(wx, wy, wz, dvx * 0.7, dvy * 0.7, dvz * 0.7, 1.6, 12.0 + Math.random()*6, 70 + Math.random()*40, smokeTex, 0x22252a, 0.85, false);
                }}
            }}

            // 3D残骸・金属片が四散
            for (let i = 0; i < 60; i++) {{
                let geo = (Math.random() < 0.5)
                    ? new THREE.CylinderGeometry(0.5, 0.5, 0.3 + Math.random()*1.0, 8, 1, true, 0, 0.8)
                    : new THREE.BoxGeometry(0.2 + Math.random()*0.4, 0.1 + Math.random()*0.3, 0.2);
                
                const mesh = new THREE.Mesh(geo, (i % 2 === 0 ? s1TankMat : hazardMat));
                mesh.material.side = THREE.DoubleSide;
                mesh.position.set(wx + (Math.random()-0.5)*1.5, wy + (Math.random()-0.5)*3.0, wz + (Math.random()-0.5)*1.5);

                const burstSpeed = 0.15 + Math.random() * 0.65;
                const a1 = Math.random() * Math.PI * 2;
                const a2 = (Math.random() - 0.5) * Math.PI;

                debrisGroup.add(mesh);
                debrisList.push({{
                    mesh: mesh,
                    vx: baseVx + Math.cos(a1) * Math.cos(a2) * burstSpeed,
                    vy: baseVy + Math.sin(a1) * Math.cos(a2) * burstSpeed,
                    vz: Math.sin(a2) * burstSpeed,
                    rx: (Math.random() - 0.5) * 0.3,
                    ry: (Math.random() - 0.5) * 0.3,
                    rz: (Math.random() - 0.5) * 0.3,
                    smokeTrail: i < 22
                }});
            }}
        }}

        // --- 4. 自動シネマティック・ディレクター（TV中継カメラワーク） ---
        const camTarget = new THREE.Vector3(0, R_EARTH + 5, 0);
        let activeCamName = "CAM 1: LAUNCH COMPLEX HERO";

        function updateCinematicCamera(simT, rx, ry, alt, pitch, exploded) {{
            const upX = -Math.sin(pitch);
            const upY = Math.cos(pitch);

            if (exploded) {{
                // 💥 爆発時: 望遠トラッカーカメラが瞬時にズームインし爆散の全貌を捉える
                activeCamName = "OPTICAL TRACKER: VEHICLE LOSS BREAKUP";
                camera.position.lerp(new THREE.Vector3(rx + 6.0, ry + 2.0, 14.0), 0.12);
                camTarget.lerp(new THREE.Vector3(rx, ry + 2.0, 0), 0.15);
            }} else if (simT < 0.0) {{
                // ⏱️ カウントダウン: 発射台下から見上げるドラマチック・ローアングル
                activeCamName = "CAM 1: PAD TOWER LOWER DECK";
                camera.position.set(3.4, R_EARTH + 1.2, 11.2);
                camTarget.set(0, R_EARTH + 4.2, 0);
            }} else if (simT < 3.5) {{
                // 🚀 離床の瞬間: 火炎偏向溝（フレイムトレンチ）越しに見上げる迫力のアングル
                activeCamName = "CAM 2: FLAME TRENCH ANGLE";
                camera.position.set(2.8, R_EARTH + 0.6, 9.5);
                camTarget.set(rx, ry + 3.0, 0);
            }} else if (simT < 16.0) {{
                // 🔭 離床上昇: 望遠地上追尾カメラ（ロングレンジ・トラッカー）
                activeCamName = "CAM 3: LONG-RANGE OPTICAL TRACKER";
                const trackerX = -12.0;
                const trackerY = R_EARTH + 1.5;
                camera.position.set(trackerX, trackerY, 32.0);
                camTarget.lerp(new THREE.Vector3(rx, ry + 3.0, 0), 0.1);
            }} else if (alt < 65.0) {{
                // 🛰️ 大気圏突破〜Max-Q: 機体オンボードマウント視点（地球が遠ざかりエンジン火炎が映る）
                activeCamName = "CAM 4: ROCKET ONBOARD CHASE";
                // 機体後方上空から機首と地球を見下ろす視点
                const camOffX = -upX * 4.2 + upY * 2.2;
                const camOffY = -upY * 4.2 - upX * 2.2;
                camera.position.lerp(new THREE.Vector3(rx + camOffX, ry + camOffY, 7.5), 0.12);
                camTarget.lerp(new THREE.Vector3(rx + upX * 4.0, ry + upY * 4.0, 0), 0.12);
            }} else {{
                // 🌌 宇宙空間・軌道投入: 軌道追従シネマティックカメラ
                activeCamName = "CAM 5: ORBITAL WIDE TELEMETRY";
                const camOffX = -upX * 7.5;
                const camOffY = -upY * 7.5;
                camera.position.lerp(new THREE.Vector3(rx + camOffX + 5.0, ry + camOffY + 3.0, 16.0), 0.08);
                camTarget.lerp(new THREE.Vector3(rx, ry, 0), 0.1);
            }}

            // カメラ振動の合成
            if (cameraShakeIntensity > 0.005) {{
                camera.position.x += (Math.random() - 0.5) * cameraShakeIntensity;
                camera.position.y += (Math.random() - 0.5) * cameraShakeIntensity;
                cameraShakeIntensity *= 0.91;
            }}

            camera.lookAt(camTarget);
            document.getElementById('cam-indicator').innerText = activeCamName;
        }}

        // --- 5. メイン再生ループ ---
        let cursor = 0.0;
        const playSpeed = 0.9;

        function animate() {{
            requestAnimationFrame(animate);

            if (cursor < data.length - 1) {{
                const curPt = data[Math.floor(cursor)];
                // 発射の瞬間と爆発時はシネマティックにスローモーション化
                const timeScale = (curPt.t < 6.0 || curPt.exploded) ? 0.25 : 0.48;
                cursor = Math.min(cursor + playSpeed * timeScale, data.length - 1);
            }}

            const idx = Math.floor(cursor);
            const nextIdx = Math.min(idx + 1, data.length - 1);
            const alpha = cursor - idx;

            const pt0 = data[idx];
            const pt1 = data[nextIdx];

            const simT = pt0.t + (pt1.t - pt0.t) * alpha;
            const rx = (pt0.x + (pt1.x - pt0.x) * alpha) * SCALE;
            const ry = (pt0.y + (pt1.y - pt0.y) * alpha) * SCALE;
            const alt = pt0.alt + (pt1.alt - pt0.alt) * alpha;
            const vel = pt0.v + (pt1.v - pt0.v) * alpha;
            const q   = pt0.q + (pt1.q - pt0.q) * alpha;
            const temp = pt0.temp + (pt1.temp - pt0.temp) * alpha;
            const pitch = pt0.pitch + (pt1.pitch - pt0.pitch) * alpha;

            rocketGroup.position.set(rx, ry, 0);
            rocketGroup.rotation.z = pitch;

            const upX = -Math.sin(pitch);
            const upY = Math.cos(pitch);
            const nozzleOffset = (pt0.stage === 1) ? 0.6 : 6.4;
            const nozX = rx + upX * nozzleOffset;
            const nozY = ry + upY * nozzleOffset;

            // 自動カメラの更新
            updateCinematicCamera(simT, rx, ry, alt, pitch, pt0.exploded);

            // カウントダウン演出
            if (simT < 0.0) {{
                const sec = Math.ceil(Math.abs(simT));
                document.getElementById('tv-timer').innerText = `T- 0${{sec}}.0`;
                document.getElementById('tv-status').innerText = (simT >= -2.5) ? "IGNITION SEQUENCE START" : "AUTO-SEQUENCE COUNTDOWN";
                document.getElementById('tv-status').style.color = (simT >= -2.5) ? "#ff9900" : "#4da6ff";

                // LOX白煙ベント
                if (Math.random() < 0.65) {{
                    spawnParticle(rx + 0.55, ry + 4.8 + Math.random()*2.5, 0, 0.04, -0.02, 0, 0.35, 1.4, 28, smokeTex, 0xeef6ff, 0.5, false);
                }}

                // T-2.5s: エンジン点火＆ウォーターデリュージ
                if (simT >= -2.5) {{
                    cameraShakeIntensity = 0.10;
                    for (let k = 0; k < 5; k++) {{
                        const side = (k % 2 === 0) ? 1 : -1;
                        spawnParticle(rx + (Math.random()-0.5)*1.2, R_EARTH + 0.2, (Math.random()-0.5)*1.2, side * (0.12 + Math.random()*0.25), 0.04, 0, 0.9, 4.5, 42, smokeTex, 0xffffff, 0.75, false);
                    }}
                }}
            }} else {{
                document.getElementById('tv-timer').innerText = `T+ ${{simT.toFixed(1).padStart(4, '0')}}`;
                // T-0でアンビリカルアームがスイングバック
                umbilicalArms.forEach(arm => {{ arm.rotation.z = Math.min(0.85, arm.rotation.z + 0.08); }});
            }}

            // ステージ分離
            if (pt0.stage === 2 && !stageSeparated) {{
                stageSeparated = true;
                s1Group.visible = false;
                const sepBooster = s1Group.clone();
                sepBooster.visible = true;
                sepBooster.position.set(rx, ry, 0);
                sepBooster.rotation.z = pitch;
                debrisGroup.add(sepBooster);
                debrisList.push({{ mesh: sepBooster, vx: -upX * 0.06, vy: -upY * 0.06, vz: 0, rx: 0.002, ry: 0.004, rz: -0.008, smokeTrail: false }});
            }}

            // フェアリング分離
            if (!pt0.fairing && !fairingSeparated) {{
                fairingSeparated = true;
                fairingLeft.visible = false;
                fairingRight.visible = false;
                [-1, 1].forEach(dir => {{
                    const shell = (dir === -1 ? fairingLeft : fairingRight).clone();
                    shell.visible = true;
                    shell.position.set(rx + upX * 9.5, ry + upY * 9.5, dir * 0.4);
                    shell.rotation.z = pitch;
                    debrisGroup.add(shell);
                    debrisList.push({{ mesh: shell, vx: -upX * 0.04, vy: -upY * 0.04, vz: dir * 0.14, rx: dir * 0.03, ry: 0.02, rz: -0.02, smokeTrail: false }});
                }});
            }}

            // プルーム噴射炎
            if (pt0.thrust && !pt0.exploded) {{
                plumeGroup.visible = true;
                plumeGroup.position.y = (pt0.stage === 1) ? 0.65 : 6.45;
                const vacExpansion = 1.0 + Math.min(3.0, alt / 26.0);
                const flicker = 0.88 + Math.random() * 0.24;
                coreCone.scale.set(1.0, flicker, 1.0);
                outerCone.scale.set(vacExpansion, flicker * (1.0 + vacExpansion * 0.2), vacExpansion);
                outerFlameMat.color.setHex(parseInt(pt0.stage === 1 ? cfg.s1_flame : cfg.s2_flame));

                engineLight.position.set(nozX, nozY, 2.0);
                engineLight.intensity = (alt < 4.0) ? 5.0 : 2.2;

                if (alt < 20.0) {{
                    const smokeCount = (alt < 0.8) ? 6 : 2;
                    for (let s = 0; s < smokeCount; s++) {{
                        const spread = (alt < 0.25) ? 0.32 : 0.07;
                        spawnParticle(nozX, nozY, 0, -upX * 0.22 + (Math.random()-0.5)*spread, -upY * 0.22 + (Math.random()-0.5)*spread, (Math.random()-0.5)*spread, 0.7, 4.0, 38, smokeTex, 0xf2f4f8, 0.65, false);
                    }}
                }}
            }} else {{
                plumeGroup.visible = false;
                engineLight.intensity = Math.max(0, engineLight.intensity * 0.9);
            }}

            // 空中分解（RUD）
            if (pt0.exploded) {{
                rocketGroup.visible = false;
                const bvx = (pt0.x - data[Math.max(0, idx-1)].x) * SCALE * 0.25;
                const bvy = (pt0.y - data[Math.max(0, idx-1)].y) * SCALE * 0.25;
                triggerCatastrophicExplosion(rx + upX * 4.5, ry + upY * 4.5, 0, bvx, bvy);
                document.getElementById('tv-status').innerText = "💥 VEHICLE BREAKUP DETECTED (RUD)";
                document.getElementById('tv-status').style.color = "#ff3333";
                document.getElementById('top-msg').innerText = "MISSION ABORT - LOSS OF TELEMETRY";
                document.getElementById('top-msg').style.color = "#ff3333";
            }} else if (simT > 0) {{
                if (pt0.phase === 'ORBIT_INSERTION') {{
                    document.getElementById('tv-status').innerText = "🛰️ ORBIT INSERTION CONFIRMED (LEO)";
                    document.getElementById('tv-status').style.color = "#00ff88";
                    document.getElementById('top-msg').innerText = "SECO - PAYLOAD IN STABLE ORBIT";
                    document.getElementById('top-msg').style.color = "#00ff88";
                }} else if (pt0.stage === 1) {{
                    document.getElementById('tv-status').innerText = "STAGE 1 BOOST PHASE";
                    document.getElementById('tv-status').style.color = "#ffaa00";
                    document.getElementById('top-msg').innerText = (alt < 15.0) ? "MAX-Q REGION FLIGHT" : "MAIN ENGINE CUT-OFF (MECO) APPROACH";
                }} else if (pt0.thrust) {{
                    document.getElementById('tv-status').innerText = "STAGE 2 VACUUM ACCELERATION";
                    document.getElementById('tv-status').style.color = "#55ddff";
                    document.getElementById('top-msg').innerText = "ORBITAL VELOCITY BURN IN PROGRESS";
                }}
            }}

            // パーティクル＆破片更新
            for (let i = 0; i < MAX_PARTICLES; i++) {{
                const p = particlePool[i];
                if (!p.active) continue;
                p.age++;
                if (p.age >= p.maxAge) {{ p.active = false; p.sprite.visible = false; continue; }}
                p.sprite.position.x += p.vx;
                p.sprite.position.y += p.vy;
                p.sprite.position.z += p.vz;
                const prog = p.age / p.maxAge;
                const curScale = p.startScale + (p.endScale - p.startScale) * prog;
                p.sprite.scale.set(curScale, curScale, 1);
                p.sprite.material.opacity = p.baseOpacity * (1.0 - prog * prog);
            }}

            for (let i = 0; i < debrisList.length; i++) {{
                const d = debrisList[i];
                d.mesh.position.x += d.vx;
                d.mesh.position.y += d.vy;
                d.mesh.position.z += d.vz;
                d.vy -= 0.0016;
                d.mesh.rotation.x += d.rx;
                d.mesh.rotation.y += d.ry;
                d.mesh.rotation.z += d.rz;

                if (d.smokeTrail && Math.random() < 0.4) {{
                    spawnParticle(d.mesh.position.x, d.mesh.position.y, d.mesh.position.z, 0, 0, 0, 0.45, 2.2, 25, smokeTex, Math.random() < 0.3 ? 0xff6600 : 0x22252a, 0.7, false);
                }}
            }}

            // 下部ミニマルティッカーHUDの更新
            document.getElementById('tv-spd').innerText = Math.round(vel);
            document.getElementById('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            document.getElementById('tv-q').innerText   = q.toFixed(1);
            document.getElementById('tv-temp').innerText = Math.round(temp);

            renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }});
    </script>
    """
    components.html(html_code, height=740)
