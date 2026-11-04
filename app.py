import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbital Architect Pro: ロケット設計＆軌道管制", layout="wide")

st.title("🚀 Orbital Architect Pro - 限界設計・軌道投入シミュレーター")
st.markdown("エンジン内部サイクル、ノズル膨張比、タンク肉厚、フェアリング投棄高度まで緻密にチューニングし、高度200km・第一宇宙速度（7,800m/s）の楕円・円軌道へ投入せよ。")

# --- 詳細パーツデータベース ---
PROPELLANTS = {
    "RP-1 (ケロシン) / LOX [高密度・大気圏向]": {"base_isp_sl": 285, "base_isp_vac": 312, "base_thrust": 900, "density": 1.02, "temp_factor": 1.0},
    "LCH4 (液体メタン) / LOX [次世代バランス]": {"base_isp_sl": 325, "base_isp_vac": 360, "base_thrust": 1800, "density": 0.82, "temp_factor": 1.1},
    "LH2 (液体水素) / LOX [最高燃費・極低温・巨大タンク]": {"base_isp_sl": 340, "base_isp_vac": 445, "base_thrust": 1100, "density": 0.32, "temp_factor": 0.9}
}

PUMP_CYCLES = {
    "ガス発生器サイクル (GG) [軽量・高信頼・燃費微減]": {"isp_mod": 0.96, "thrust_mod": 0.95, "mass_mod": 0.85, "max_pressure_limit": 140},
    "エキスパンダーサイクル [上段向き・高効率・低推力]": {"isp_mod": 1.03, "thrust_mod": 0.65, "mass_mod": 1.0, "max_pressure_limit": 100},
    "二段燃焼サイクル (SC) [高出力・高圧・重]": {"isp_mod": 1.02, "thrust_mod": 1.15, "mass_mod": 1.20, "max_pressure_limit": 240},
    "フルフロー二段燃焼 (FFSC) [究極性能・超高圧制御シビア]": {"isp_mod": 1.05, "thrust_mod": 1.35, "mass_mod": 1.30, "max_pressure_limit": 300}
}

MATERIALS = {
    "A2195 アルミ・リチウム合金 (標準航空宇宙材)": {"base_dry_ratio": 0.065, "max_q_base": 45.0, "max_g_base": 6.0},
    "TORAYCA カーボン複合材 (超軽量・熱とせん断に弱い)": {"base_dry_ratio": 0.042, "max_q_base": 34.0, "max_g_base": 5.2},
    "304L 高強度ステンレス (激重・超高耐熱・高剛性)": {"base_dry_ratio": 0.095, "max_q_base": 85.0, "max_g_base": 9.5}
}

FAIRINGS = {
    "標準オジーブ型 (バランス・耐熱1,800K)": {"mass": 1.8, "cd": 0.32, "heat_limit": 1800},
    "超鋭角ニードル型 (低空気抵抗・先端加熱に弱い 1,450K)": {"mass": 1.4, "cd": 0.22, "heat_limit": 1450},
    "鈍頭大型フェアリング (高耐熱2,400K・空気抵抗大)": {"mass": 2.6, "cd": 0.46, "heat_limit": 2400}
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
    
    # 燃焼室圧と膨張比によるIsp補正
    pc_factor = 1.0 + (pc - 100.0) * 0.0006
    eps_vac_bonus = 1.0 + np.log10(eps / 25.0) * 0.08
    # 海面では膨張比が大きすぎると過膨張で推力・Ispが低下する
    overexpansion_penalty = max(0.0, (eps - 35.0) * 0.006)
    
    isp_sl = prop["base_isp_sl"] * cyc["isp_mod"] * pc_factor * (1.0 - overexpansion_penalty)
    isp_vac = prop["base_isp_vac"] * cyc["isp_mod"] * pc_factor * eps_vac_bonus
    
    thrust_vac_per_eng = prop["base_thrust"] * cyc["thrust_mod"] * (pc / 150.0) ** 0.65
    thrust_sl_per_eng = thrust_vac_per_eng * (isp_sl / isp_vac)
    
    # 燃料密度が低い（LH2など）とタンク体積が膨らみ構造質量が増える
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
        "cd_mod": density_penalty
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

    # 発射前・離床直後のハードウェア限界チェック
    if s1_spec["pc"] > s1_spec["pc_limit"]:
        return [], f"第1段の燃焼室圧力({s1_spec['pc']} bar)がターボポンプの設計限界({s1_spec['pc_limit']} bar)を超過！イグニッション直後にタービンが爆散しました！"
    if s1_spec["eps"] > 55:
        return [], f"第1段のノズル膨張比(ε={s1_spec['eps']})が大気圏内に対して大きすぎます！強烈なフロウセパレーション（過膨張振動）が発生し、離床直後にノズルが破壊されました！"
    if twr_init <= 1.02:
        return [], f"推力重量比(TWR: {twr_init:.2f})が1.0以下のため、ロケットが重力に勝てず発射台から浮上できません！"

    for step in range(1800): # 最大900秒
        t = float(step * dt)
        r = float(np.sqrt(x**2 + y**2))
        alt = float(r - R_earth)
        alt_km = float(alt / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))
        
        if alt < -10:
            status = "墜落"
            fail_reason = f"T+{t:.0f}秒: 推力または軌道速度不足により地表（海面）へ墜落しました。"
            break

        # 大気密度と動圧・空力加熱温度の計算
        rho = float(1.225 * np.exp(-alt / 7400.0)) if alt < 130000 else 0.0
        q = float(0.5 * rho * (v**2) / 1000.0) # kPa
        # 簡易空力加熱モデル (スタグネーション温度近似)
        aero_temp = float(288.0 + 0.5 * (rho ** 0.38) * ((v / 100.0) ** 2.35) * 45.0)

        # フェアリング分離判定
        if fairing_attached and alt_km >= fairing_sep_alt:
            fairing_attached = False
            # まだ空気が濃い高度でフェアリングを捨てた場合、むき出しの衛星が焼損する
            if aero_temp > 650.0 or q > 1.2:
                fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): フェアリング投棄が早すぎます！大気摩擦熱({aero_temp:.0f}K)と風圧によりむき出しの人工衛星が破壊されました！"
                history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp, "stage": int(stage), "fairing": False, "exploded": True, "thrust": False})
                break

        f_mass = fair_spec["mass"] * 1000.0 if fairing_attached else 0.0

        # ステージ管理
        if stage == 1:
            if fuel_rem <= 0:
                stage = 2
                fuel_rem = float(s2_fuel * 1000.0)
                if s2_spec["pc"] > s2_spec["pc_limit"]:
                    fail_reason = f"T+{t:.0f}秒: 第2段エンジン点火時に燃焼室圧力({s2_spec['pc']} bar)がターボポンプ限界({s2_spec['pc_limit']} bar)を超え、軌道上で爆発しました！"
                    history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp, "stage": 2, "fairing": fairing_attached, "exploded": True, "thrust": False})
                    break
            else:
                cur_mass = float((s1_spec["dry_mass"] + s2_fuel + s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + fuel_rem)
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s1_spec["isp_vac"] - (s1_spec["isp_vac"] - s1_spec["isp_sl"]) * atm_factor)
                thrust = float((s1_spec["thrust_vac"] - (s1_spec["thrust_vac"] - s1_spec["thrust_sl"]) * atm_factor) * 1000.0)
                
                if 7000 < alt < 16500:
                    thrust *= (throttle_maxq / 100.0)
                
                # Gリミッター制御
                if thrust / (cur_mass * g0) > max_g_limit_cut:
                    thrust = max_g_limit_cut * cur_mass * g0

                mdot = thrust / (isp * g0)
                fuel_rem -= mdot * dt

        if stage == 2:
            if fuel_rem <= 0:
                thrust = 0.0
                cur_mass = float((s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass)
            else:
                # 低高度で高膨張比の第2段を点火すると過膨張破壊
                if alt_km < 35.0 and s2_spec["eps"] > 70:
                    fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): 大気が残る低高度で高膨張比(ε={s2_spec['eps']})の第2段エンジンを点火したため、ノズルが過膨張で粉砕されました！"
                    history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": 0.0, "temp": aero_temp, "stage": 2, "fairing": fairing_attached, "exploded": True, "thrust": False})
                    break

                cur_mass = float((s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + fuel_rem)
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s2_spec["isp_vac"] - (s2_spec["isp_vac"] - s2_spec["isp_sl"]) * atm_factor)
                thrust = float((s2_spec["thrust_vac"] - (s2_spec["thrust_vac"] - s2_spec["thrust_sl"]) * atm_factor) * 1000.0)
                
                if thrust / (cur_mass * g0) > max_g_limit_cut:
                    thrust = max_g_limit_cut * cur_mass * g0

                mdot = thrust / (isp * g0)
                fuel_rem -= mdot * dt

        # ピッチ角（重力ターン）
        if alt_km < turn_start_alt:
            pitch_deg = 90.0
        elif alt_km < turn_end_alt:
            prog = (alt_km - turn_start_alt) / (turn_end_alt - turn_start_alt)
            pitch_deg = 90.0 * (1.0 - (prog ** turn_exponent))
        else:
            pitch_deg = 0.0

        theta = float(np.arctan2(x, y))
        pitch_rad = float(np.radians(pitch_deg))
        dir_x = float(np.sin(theta) * np.sin(pitch_rad) + np.cos(theta) * np.cos(pitch_rad))
        dir_y = float(np.cos(theta) * np.sin(pitch_rad) - np.sin(theta) * np.cos(pitch_rad))

        # 空気抵抗
        drag_area = (11.0 * s1_spec["cd_mod"]) if stage == 1 else (4.5 * s2_spec["cd_mod"])
        drag_force = float(0.5 * rho * (v**2) * fair_spec["cd"] * drag_area)
        if v > 0:
            drag_x = -drag_force * (vx / v)
            drag_y = -drag_force * (vy / v)
        else:
            drag_x, drag_y = 0.0, 0.0

        # 重力
        g_cur = float(g0 * ((R_earth / r) ** 2))
        grav_x = -cur_mass * g_cur * float(np.sin(theta))
        grav_y = -cur_mass * g_cur * float(np.cos(theta))

        fx = thrust * dir_x + drag_x + grav_x
        fy = thrust * dir_y + drag_y + grav_y
        ax = fx / cur_mass
        ay = fy / cur_mass
        acc_g = float(np.sqrt((thrust * dir_x + drag_x)**2 + (thrust * dir_y + drag_y)**2) / (cur_mass * g0))

        # 構造限界・熱破壊チェック
        cur_spec = s1_spec if stage == 1 else s2_spec
        if q > cur_spec["max_q"]:
            fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): 動圧({q:.1f} kPa)がタンク構造限界({cur_spec['max_q']:.1f} kPa)を超過！Max-Qで機体が空中分解しました！"
            history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp, "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False})
            break
        if acc_g > cur_spec["max_g"]:
            fail_reason = f"T+{t:.0f}秒: 加速度({acc_g:.1f} G)が機体耐G限界({cur_spec['max_g']:.1f} G)を超過！タンク隔壁が座屈・圧壊しました！"
            history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp, "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False})
            break
        if fairing_attached and aero_temp > fair_spec["heat_limit"]:
            fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): 空力加熱({aero_temp:.0f} K)がフェアリング耐熱限界({fair_spec['heat_limit']} K)を超え、先端から融解・爆散しました！"
            history.append({"t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp, "stage": int(stage), "fairing": fairing_attached, "exploded": True, "thrust": False})
            break

        vx = float(vx + ax * dt)
        vy = float(vy + ay * dt)
        x = float(x + vx * dt)
        y = float(y + vy * dt)

        if step % 4 == 0:
            history.append({
                "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g, "temp": aero_temp,
                "stage": int(stage), "fairing": bool(fairing_attached), "exploded": False, "thrust": bool(thrust > 0),
                "pitch": float(theta - np.radians(90.0 - pitch_deg))
            })

        # 軌道投入判定
        v_radial = float(vx * np.sin(theta) + vy * np.cos(theta))
        v_tangent = float(vx * np.cos(theta) - vy * np.sin(theta))
        if alt_km >= 180.0 and v_tangent >= 7750.0 and abs(v_radial) < 420.0:
            status = "軌道投入成功"
            break

    if not fail_reason and status != "軌道投入成功":
        fail_reason = f"燃料消費完了後、第一宇宙速度(7,800m/s)または目標高度に届かずサブオービタル（弾道飛行）で終了しました。(最高速度: {v:.0f} m/s, 到達高度: {alt_km:.1f} km)"

    return history, fail_reason

# --- 発射シークエンス＆インタラクティブ3Dビューワー ---
if st.button("🔥 イグニッション・発射シークエンス開始", use_container_width=True, type="primary"):
    traj_data, error_msg = run_simulation()
    
    if len(traj_data) == 0:
        st.error(f"❌ 発射失敗: {error_msg}")
    else:
        if error_msg:
            st.warning(f"⚠️ ミッション失敗: {error_msg}")
        else:
            st.success("🎉 ミッション完全成功！ペイロードは安定した地球周回軌道（LEO）へ投入されました！")

        traj_json = json.dumps(
            traj_data,
            default=lambda o: float(o) if isinstance(o, np.floating) else (int(o) if isinstance(o, np.integer) else (bool(o) if isinstance(o, np.bool_) else str(o)))
        )
        
        html_code = f"""
        <div style="position: relative; width: 100%; height: 600px; background: #02040a; border-radius: 12px; overflow: hidden; font-family: 'Courier New', monospace; user-select: none;">
            <div id="canvas-container" style="width: 100%; height: 100%; cursor: grab;"></div>
            
            <!-- 左上: テレメトリーHUD -->
            <div style="position: absolute; top: 15px; left: 15px; color: #00ffcc; background: rgba(0, 15, 30, 0.85); padding: 14px; border: 1px solid #00ffcc; border-radius: 8px; width: 250px; pointer-events: none; box-shadow: 0 0 15px rgba(0,255,204,0.2);">
                <div style="font-size: 16px; font-weight: bold; border-bottom: 1px solid #00ffcc; padding-bottom: 4px; margin-bottom: 8px;">📡 LIVE TELEMETRY</div>
                <div id="hud-time">T+ 0.0 s</div>
                <div id="hud-alt">ALTITUDE : 0.0 km</div>
                <div id="hud-vel">VELOCITY : 0 m/s</div>
                <div id="hud-q">DYN PRESS: 0.0 kPa</div>
                <div id="hud-temp">NOSE TEMP: 288 K</div>
                <div id="hud-g">G-LOAD   : 1.00 G</div>
                <div id="hud-fairing" style="color: #66ccff; margin-top: 4px;">FAIRING  : ATTACHED</div>
                <div id="hud-stage" style="color: #ffcc00; font-weight: bold; margin-top: 6px;">🔥 STAGE 1 BURN</div>
            </div>

            <!-- 右上: カメラ＆再生コントロール -->
            <div style="position: absolute; top: 15px; right: 15px; display: flex; flex-direction: column; gap: 8px;">
                <div style="background: rgba(0, 15, 30, 0.85); padding: 10px; border: 1px solid #4da6ff; border-radius: 8px; color: #fff; font-size: 12px;">
                    <div style="font-weight: bold; color: #4da6ff; margin-bottom: 6px;">🎥 カメラ＆再生操作 (マウス回転/ズーム可)</div>
                    <div style="display: flex; gap: 6px; margin-bottom: 6px;">
                        <button id="btn-cam-rocket" style="flex:1; background:#0066cc; color:#fff; border:none; padding:6px 10px; border-radius:4px; cursor:pointer;">🚀 ロケット追従</button>
                        <button id="btn-cam-earth" style="flex:1; background:#223344; color:#fff; border:none; padding:6px 10px; border-radius:4px; cursor:pointer;">🌍 地球俯瞰</button>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <button id="btn-speed-1" style="flex:1; background:#008866; color:#fff; border:none; padding:5px; border-radius:4px; cursor:pointer;">▶ 1x</button>
                        <button id="btn-speed-3" style="flex:1; background:#223344; color:#fff; border:none; padding:5px; border-radius:4px; cursor:pointer;">⏩ 3x</button>
                        <button id="btn-replay" style="flex:1; background:#444; color:#fff; border:none; padding:5px; border-radius:4px; cursor:pointer;">🔄 リプレイ</button>
                    </div>
                </div>
            </div>

            <!-- 左下: 操作ガイド -->
            <div style="position: absolute; bottom: 12px; left: 15px; color: #aaa; font-size: 12px; background: rgba(0,0,0,0.6); padding: 6px 10px; border-radius: 4px; pointer-events: none;">
                🖱️ 左ドラッグ: 360°回転 ｜ ホイール/ピンチ: ズーム ｜ 右ドラッグ: 視点移動
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script>
            const data = {traj_json};
            const container = document.getElementById('canvas-container');
            const scene = new THREE.Scene();
            
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.5, 500000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            // OrbitControls の導入
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.08;
            controls.minDistance = 8;
            controls.maxDistance = 4000;

            const SCALE = 0.0001; // 1 unit = 10 km
            const R_EARTH = 6371000 * SCALE; // 637.1 units

            // 背景の星空パーティクル
            const starGeo = new THREE.BufferGeometry();
            const starCount = 3000;
            const starPos = new Float32Array(starCount * 3);
            for(let i = 0; i < starCount * 3; i++) {{
                starPos[i] = (Math.random() - 0.5) * 12000;
            }}
            starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
            const starMat = new THREE.PointsMaterial({{ color: 0xffffff, size: 2.0 }});
            scene.add(new THREE.Points(starGeo, starMat));

            // 地球と経緯度グリッド・大気層
            const earthGeo = new THREE.SphereGeometry(R_EARTH, 64, 64);
            const earthMat = new THREE.MeshPhongMaterial({{ color: 0x103565, emissive: 0x041020, specular: 0x224466, shininess: 20 }});
            const earth = new THREE.Mesh(earthGeo, earthMat);
            scene.add(earth);

            const wireGeo = new THREE.SphereGeometry(R_EARTH + 0.2, 32, 32);
            const wireMat = new THREE.MeshBasicMaterial({{ color: 0x225588, wireframe: true, transparent: true, opacity: 0.25 }});
            scene.add(new THREE.Mesh(wireGeo, wireMat));

            const atmosGeo = new THREE.SphereGeometry(R_EARTH + (100000 * SCALE), 64, 64);
            const atmosMat = new THREE.MeshBasicMaterial({{ color: 0x3399ff, transparent: true, opacity: 0.14 }});
            scene.add(new THREE.Mesh(atmosGeo, atmosMat));

            // 目標軌道リング (高度200km)
            const targetOrbitGeo = new THREE.RingGeometry(R_EARTH + 20.0, R_EARTH + 20.4, 128);
            const targetOrbitMat = new THREE.MeshBasicMaterial({{ color: 0x00ff66, side: THREE.DoubleSide, transparent: true, opacity: 0.35 }});
            scene.add(new THREE.Mesh(targetOrbitGeo, targetOrbitMat));

            // 光源
            const sunLight = new THREE.DirectionalLight(0xffffff, 1.4);
            sunLight.position.set(1500, 1200, 1000);
            scene.add(sunLight);
            scene.add(new THREE.AmbientLight(0x404050));

            // 多段ロケット3Dモデル構築
            const rocketGroup = new THREE.Group();
            
            // 第1段ブースター
            const s1Geo = new THREE.CylinderGeometry(1.2, 1.4, 8, 16);
            const s1Mat = new THREE.MeshPhongMaterial({{ color: 0xdddddd }});
            const s1Mesh = new THREE.Mesh(s1Geo, s1Mat);
            s1Mesh.position.y = -4;
            rocketGroup.add(s1Mesh);

            // 第2段オービター
            const s2Geo = new THREE.CylinderGeometry(1.2, 1.2, 5, 16);
            const s2Mat = new THREE.MeshPhongMaterial({{ color: 0xffffff }});
            const s2Mesh = new THREE.Mesh(s2Geo, s2Mat);
            s2Mesh.position.y = 2.5;
            rocketGroup.add(s2Mesh);

            // フェアリング (ノーズコーン)
            const fairGeo = new THREE.ConeGeometry(1.3, 4.5, 16);
            const fairMat = new THREE.MeshPhongMaterial({{ color: 0x00ccff }});
            const fairMesh = new THREE.Mesh(fairGeo, fairMat);
            fairMesh.position.y = 7.25;
            rocketGroup.add(fairMesh);

            // ペイロード衛星 (フェアリング内部)
            const satGeo = new THREE.OctahedronGeometry(0.9, 1);
            const satMat = new THREE.MeshPhongMaterial({{ color: 0xffcc00, emissive: 0x443300 }});
            const satMesh = new THREE.Mesh(satGeo, satMat);
            satMesh.position.y = 6.2;
            rocketGroup.add(satMesh);

            // ジェット噴射炎
            const flameGeo = new THREE.ConeGeometry(1.3, 7, 16);
            flameGeo.rotateX(Math.PI);
            const flameMat = new THREE.MeshBasicMaterial({{ color: 0xff6600 }});
            const flameMesh = new THREE.Mesh(flameGeo, flameMat);
            flameMesh.position.y = -11.5;
            rocketGroup.add(flameMesh);

            scene.add(rocketGroup);

            // 軌跡ライン
            const points = [];
            const lineMat = new THREE.LineBasicMaterial({{ color: 0x00ffcc, linewidth: 2 }});
            const lineGeo = new THREE.BufferGeometry();
            const trajectoryLine = new THREE.Line(lineGeo, lineMat);
            scene.add(trajectoryLine);

            // 初期カメラ位置
            camera.position.set(0, R_EARTH + 15, 85);
            controls.target.set(0, R_EARTH, 0);

            let followMode = true;
            let playSpeed = 1;
            let idx = 0;
            let frameTick = 0;

            // ボタンイベント
            const btnRocket = document.getElementById('btn-cam-rocket');
            const btnEarth = document.getElementById('btn-cam-earth');
            btnRocket.onclick = () => {{
                followMode = true;
                btnRocket.style.background = '#0066cc';
                btnEarth.style.background = '#223344';
            }};
            btnEarth.onclick = () => {{
                followMode = false;
                btnEarth.style.background = '#0066cc';
                btnRocket.style.background = '#223344';
                camera.position.set(0, R_EARTH * 0.6, 950);
                controls.target.set(0, R_EARTH * 0.6, 0);
            }};
            document.getElementById('btn-speed-1').onclick = () => {{
                playSpeed = 1;
                document.getElementById('btn-speed-1').style.background = '#008866';
                document.getElementById('btn-speed-3').style.background = '#223344';
            }};
            document.getElementById('btn-speed-3').onclick = () => {{
                playSpeed = 3;
                document.getElementById('btn-speed-3').style.background = '#008866';
                document.getElementById('btn-speed-1').style.background = '#223344';
            }};
            document.getElementById('btn-replay').onclick = () => {{
                idx = 0;
                points.length = 0;
                s1Mesh.visible = true;
                fairMesh.visible = true;
                s2Mat.color.setHex(0xffffff);
                rocketGroup.scale.set(1, 1, 1);
            }};

            function animate() {{
                requestAnimationFrame(animate);
                frameTick++;

                if (idx < data.length && (playSpeed === 3 || frameTick % 2 === 0)) {{
                    const stepAdvance = playSpeed === 3 ? 2 : 1;
                    idx = Math.min(idx + stepAdvance, data.length - 1);
                    const pt = data[idx];
                    const rx = pt.x * SCALE;
                    const ry = pt.y * SCALE;

                    const prevPos = rocketGroup.position.clone();
                    rocketGroup.position.set(rx, ry, 0);
                    points.push(new THREE.Vector3(rx, ry, 0));
                    lineGeo.setFromPoints(points);

                    // 進行方向へ機体を回転
                    if (idx > 0) {{
                        const prev = data[idx - 1];
                        const angle = Math.atan2(pt.y - prev.y, pt.x - prev.x);
                        rocketGroup.rotation.z = angle - Math.PI / 2;
                    }}

                    // ステージ分離・フェアリング分離の見た目反映
                    if (pt.stage === 2) {{
                        s1Mesh.visible = false;
                        flameMesh.position.y = -3.5;
                        flameMat.color.setHex(0x66ccff); // 第2段は青白い真空プラズマ炎
                    }} else {{
                        s1Mesh.visible = true;
                        flameMesh.position.y = -11.5;
                        flameMat.color.setHex(0xff6600);
                    }}

                    fairMesh.visible = pt.fairing;
                    flameMesh.visible = pt.thrust && !pt.exploded;
                    // 炎のゆらぎアニメーション
                    flameMesh.scale.y = 0.85 + Math.random() * 0.35;

                    if (pt.exploded) {{
                        s1Mat.color.setHex(0xff2200);
                        s2Mat.color.setHex(0xff2200);
                        rocketGroup.scale.set(3.5, 3.5, 3.5);
                    }}

                    // ロケット追従モード時のカメラ平行移動（マウス回転角度を維持したまま追従）
                    if (followMode) {{
                        const deltaX = rx - prevPos.x;
                        const deltaY = ry - prevPos.y;
                        camera.position.x += deltaX;
                        camera.position.y += deltaY;
                        controls.target.set(rx, ry, 0);
                    }}

                    // HUD更新
                    document.getElementById('hud-time').innerText = `T+ ${{pt.t.toFixed(1)}} s`;
                    document.getElementById('hud-alt').innerText = `ALTITUDE : ${{pt.alt.toFixed(1)}} km`;
                    document.getElementById('hud-vel').innerText = `VELOCITY : ${{pt.v.toFixed(0)}} m/s`;
                    document.getElementById('hud-q').innerText = `DYN PRESS: ${{pt.q.toFixed(1)}} kPa`;
                    document.getElementById('hud-temp').innerText = `NOSE TEMP: ${{pt.temp.toFixed(0)}} K`;
                    document.getElementById('hud-g').innerText = `G-LOAD   : ${{pt.g.toFixed(2)}} G`;
                    document.getElementById('hud-fairing').innerText = pt.fairing ? "FAIRING  : ATTACHED" : "FAIRING  : JETTISONED (分離済)";
                    document.getElementById('hud-stage').innerText = pt.exploded
                        ? "💥 CRITICAL FAILURE (EXPLODED)"
                        : (pt.stage === 1 ? "🔥 STAGE 1 BOOSTER BURN" : (pt.thrust ? "🚀 STAGE 2 VACUUM BURN" : "🛰️ MECO / ORBITAL COASTING"));
                }}

                controls.update();
                renderer.render(scene, camera);
            }}
            animate();
        </script>
        """
        components.html(html_code, height=620)
