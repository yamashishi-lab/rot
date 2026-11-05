import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect Pro: 超精密物理演算＆公式4K中継", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect Pro - 極限リアル航空宇宙シミュレーター")
st.markdown("NASA/SpaceX公式Webcast仕様。実写衛星光学パイプライン、超望遠ディレクターカメラ、厳密軌道力学＆破壊力学。")

# =========================================================================
# 🔬 推進剤・材料・空力パーツ データベース
# =========================================================================
PROPELLANTS = {
    "超高密度メタロックス (CH4 / LOX) [王道FFSC]": {
        "base_isp_sl": 335, "base_isp_vac": 380, "base_thrust": 2750, "density": 0.83, 
        "flame_hex": 0x38bdf8, "outer_hex": 0x0284c7, "risk": 0.0, "type": "methalox"
    },
    "高精製ケロシン (RP-1 / LOX) [ヘビーリフト]": {
        "base_isp_sl": 295, "base_isp_vac": 325, "base_thrust": 1300, "density": 1.02, 
        "flame_hex": 0xfb923c, "outer_hex": 0xc2410c, "risk": 0.0, "type": "rp1"
    },
    "超極低温ハイドロロックス (LH2 / LOX) [究極真空比推力]": {
        "base_isp_sl": 375, "base_isp_vac": 465, "base_thrust": 1400, "density": 0.32, 
        "flame_hex": 0xf472b6, "outer_hex": 0xdb2777, "risk": 0.02, "type": "hydro"
    },
    "【猛毒】赤煙硝酸 ＋ UDMH [即自発火ハイパーゴリック]": {
        "base_isp_sl": 285, "base_isp_vac": 318, "base_thrust": 1950, "density": 1.25, 
        "flame_hex": 0xc026d3, "outer_hex": 0x7e22ce, "risk": 0.05, "type": "hypergolic"
    },
    "【オカルト】怪しい常温核融合エナジードリンク水": {
        "base_isp_sl": 430, "base_isp_vac": 530, "base_thrust": 3500, "density": 0.65, 
        "flame_hex": 0x22c55e, "outer_hex": 0x15803d, "risk": 0.25, "type": "energy"
    },
    "【禁忌】ダークマター濃縮スラリー [不安定特異点]": {
        "base_isp_sl": 880, "base_isp_vac": 1250, "base_thrust": 6800, "density": 1.85, 
        "flame_hex": 0xa855f7, "outer_hex": 0x6b21a8, "risk": 0.50, "type": "darkmatter"
    }
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [極限高圧]": {"isp_mod": 1.06, "thrust_mod": 1.40, "mass_mod": 1.25, "max_pressure_limit": 360},
    "二段燃焼サイクル (SC) [高出力信頼性]": {"isp_mod": 1.02, "thrust_mod": 1.15, "mass_mod": 1.18, "max_pressure_limit": 285},
    "ガス発生器サイクル (GG) [軽量堅牢]": {"isp_mod": 0.96, "thrust_mod": 0.95, "mass_mod": 0.85, "max_pressure_limit": 185},
    "【手動】人力足漕ぎペダル式タービン [超軽量・推力激減]": {"isp_mod": 0.30, "thrust_mod": 0.15, "mass_mod": 0.20, "max_pressure_limit": 80}
}

MATERIALS = {
    "Austenitic 300系 圧延鏡面ステンレス [極低温・耐熱]": {"base_dry_ratio": 0.068, "max_q_base": 125.0, "max_g_base": 12.0, "mat_id": "ss"},
    "航空宇宙用 Al-Li アルミリチウム合金 [高比強度白塗装]": {"base_dry_ratio": 0.052, "max_q_base": 70.0, "max_g_base": 8.0, "mat_id": "al"},
    "高弾性炭素繊維複合材 (CFRP) [マットブラック]": {"base_dry_ratio": 0.038, "max_q_base": 55.0, "max_g_base": 6.5, "mat_id": "cf"},
    "【節約】家庭用極薄アルミホイル [耐久皆無]": {"base_dry_ratio": 0.015, "max_q_base": 8.0, "max_g_base": 2.0, "mat_id": "foil"},
    "【DIY】防腐処理済み米松ツーバイフォー材 [超重量]": {"base_dry_ratio": 0.165, "max_q_base": 40.0, "max_g_base": 4.5, "mat_id": "wood"}
}

AERO_WINGS = {
    "なし (純粋な弾道弾体・グリッドフィンのみ)": {"lift_coeff": 0.0, "drag_penalty": 1.0, "mass": 0.0, "flutter_mach": 99.0, "wing_id": "none"},
    "ジャンボ旅客機の主翼 (B747流用・巨大アスペクト比)": {"lift_coeff": 2.4, "drag_penalty": 3.6, "mass": 19.5, "flutter_mach": 0.88, "wing_id": "airliner"},
    "超音速デルタ翼 (コンコルド風・高速揚力型)": {"lift_coeff": 0.85, "drag_penalty": 1.5, "mass": 8.8, "flutter_mach": 2.85, "wing_id": "delta"},
    "ダンボール製ハンドメイド補助翼 (セロテープ留め)": {"lift_coeff": 0.35, "drag_penalty": 1.35, "mass": 0.25, "flutter_mach": 0.42, "wing_id": "cardboard"}
}

FAIRINGS = {
    "低抵抗バイコニカル複合材カウル (耐熱2,600K)": {"mass": 2.2, "cd": 0.18, "heat_limit": 2600, "shape_id": "biconic"},
    "高音速オジーブ・クラムシェル (耐熱1,900K)": {"mass": 1.8, "cd": 0.25, "heat_limit": 1900, "shape_id": "ogive"},
    "極超音速ペネトレーターニードル (超低ドラッグ)": {"mass": 1.4, "cd": 0.15, "heat_limit": 1500, "shape_id": "needle"},
    "【即席】巨大タコさんウインナー型ノーズコーン": {"mass": 4.8, "cd": 0.98, "heat_limit": 550, "shape_id": "octopus"}
}

PRESSURIZATION = {
    "自己加圧方式 (Autogenous / 高効率)": {"mass_penalty": 0.002, "g_bonus": 0.95},
    "高圧He COPV複合材ボトル加圧 (高圧安定)": {"mass_penalty": 0.008, "g_bonus": 1.20},
    "自転車用手動空気入れ (気合いポンピング)": {"mass_penalty": 0.001, "g_bonus": 0.40}
}

# =========================================================================
# 🎛️ パラメータ設定タブ
# =========================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 第1段 (ブースター)", 
    "🛩️ 空力・主翼・怪しいアドオン", 
    "🛰️ 第2段 (オービター) & 先端部", 
    "📐 軌道投入ガイダンス & スロットル"
])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### ブースター推進系")
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=0)
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", list(PUMP_CYCLES.keys()), index=0)
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 42, 9)
    with c2:
        st.markdown("#### 燃焼室 & ノズル")
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, 280, step=10, help="限界を超えるとターボポンプが爆発します")
        s1_eps = st.slider("海面膨張比 (ε)", 8, 70, 24, step=1)
        s1_tvc = st.slider("TVC ジンバル最大角 (deg)", 1, 20, 8)
    with c3:
        st.markdown("#### タンク構造・加圧")
        s1_fuel = st.slider("第1段 推進剤充填量 (トン)", 50.0, 4500.0, 950.0, step=50.0)
        s1_mat = st.selectbox("第1段 構造素材", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("外殻等価板厚 (mm)", 0.5, 12.0, 3.8, step=0.1)
        s1_press = st.selectbox("タンク加圧方式", list(PRESSURIZATION.keys()), index=0)

with tab2:
    st.markdown("#### 🚀 空力実験アドオン（ロケットに巨大翼をつけたらどうなるか？）")
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 主翼アドオン", list(AERO_WINGS.keys()), index=0)
        angle_of_attack = st.slider("主翼 固定取り付け角迎角 AoA (deg)", -5.0, 15.0, 1.5, step=0.5)
    with c2:
        st.info("💡 **航空力学警告**: ロケットに主翼を付けると急激な動圧上昇で凄まじい揚力モーメントが発生し、音速手前でフラッター崩壊するか、横転して空中分解（RUD）します。")

with tab3:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 第2段 真空推進系")
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=0)
        s2_cycle = st.selectbox("第2段 ポンプ方式", list(PUMP_CYCLES.keys()), index=0)
        s2_eng_count = st.slider("真空特化ノズル基数", 1, 9, 3)
        s2_pc = st.slider("第2段 燃焼室圧 (bar)", 20, 350, 220, step=10)
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 30, 280, 130, step=5)
    with c2:
        st.markdown("#### 第2段 構造・タンク")
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 10.0, 1500.0, 320.0, step=10.0)
        s2_mat = st.selectbox("第2段 構造素材", list(MATERIALS.keys()), index=0)
        s2_thick = st.slider("第2段 壁厚 (mm)", 0.5, 8.0, 2.8, step=0.1)
    with c3:
        st.markdown("#### 先端部 & ペイロード")
        fairing_type = st.selectbox("先端空力カウル / フェアリング", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 30.0, 160.0, 85.0, step=5.0)
        payload_mass = st.slider("投入衛星ペイロード質量 (トン)", 0.1, 150.0, 15.0, step=1.0)

with tab4:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 重力ターン 軌道投入プロファイル")
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.2, 20.0, 1.8, step=0.1)
        turn_end_alt = st.slider("水平重力ターン完了高度 (km)", 40.0, 250.0, 115.0, step=5.0)
        turn_exponent = st.slider("ターン曲率プロファイル指数", 0.3, 2.0, 0.65, step=0.02)
    with c2:
        st.markdown("#### フライトスロットル & 加速度リミッター")
        throttle_maxq = st.slider("Max-Q 領域 推力抑制 (%)", 20, 100, 75)
        max_g_limit_cut = st.slider("最大加速度リミッター (G)", 2.0, 14.0, 5.5, step=0.2)

# =========================================================================
# ⚙️ 物理性能演算 (Physics Breakdown)
# =========================================================================
def calc_stage_specs(prop_key, cycle_key, pc, eps, eng_count, fuel_mass, mat_key, thick, press_key=None):
    prop = PROPELLANTS[prop_key]
    cyc = PUMP_CYCLES[cycle_key]
    mat = MATERIALS[mat_key]

    pc_factor = 1.0 + (pc - 100.0) * 0.0006
    eps_vac_bonus = 1.0 + np.log10(eps / 25.0) * 0.08
    overexpansion_penalty = max(0.0, (eps - 35.0) * 0.006)

    isp_sl = prop["base_isp_sl"] * cyc["isp_mod"] * pc_factor * (1.0 - overexpansion_penalty)
    isp_vac = prop["base_isp_vac"] * cyc["isp_mod"] * pc_factor * eps_vac_bonus

    thrust_vac_per_eng = prop["base_thrust"] * cyc["thrust_mod"] * ((pc / 150.0) ** 0.65)
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
        "flame_hex": prop["flame_hex"],
        "outer_hex": prop["outer_hex"],
        "eng_count": eng_count,
        "fuel_risk": prop["risk"],
        "prop_type": prop["type"]
    }

wing_spec = AERO_WINGS[wing_type]
fair_spec = FAIRINGS[fairing_type]

s1_spec = calc_stage_specs(s1_prop, s1_cycle, s1_pc, s1_eps, s1_eng_count, s1_fuel, s1_mat, s1_thick, s1_press)
s2_spec = calc_stage_specs(s2_prop, s2_cycle, s2_pc, s2_eps, s2_eng_count, s2_fuel, s2_mat, s2_thick)

total_s2_wet = s2_fuel + s2_spec["dry_mass"] + payload_mass + fair_spec["mass"]
total_s1_wet = s1_fuel + s1_spec["dry_mass"] + wing_spec["mass"] + total_s2_wet

twr_init = s1_spec["thrust_sl"] / (total_s1_wet * 9.80665)
dv_s1 = s1_spec["isp_sl"] * 9.80665 * np.log(total_s1_wet / (total_s1_wet - s1_fuel))
dv_s2 = s2_spec["isp_vac"] * 9.80665 * np.log(total_s2_wet / (s2_spec["dry_mass"] + payload_mass))
total_dv = dv_s1 + dv_s2

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("総離床重量 / 離床TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f} ({'離床可能' if twr_init >= 1.05 else '推力不足！墜落確定'})")
m2.metric("総計算速度増分 (ΔV)", f"{total_dv:.0f} m/s", "軌道投入基準: 9,200 m/s")
m3.metric("構造限界動圧 / 耐G", f"{s1_spec['max_q']:.1f} kPa", f"耐G: {s1_spec['max_g']:.1f} G")
m4.metric("主翼アドオン重量 / 抗力倍率", f"+{wing_spec['mass']:.1f} t", f"抗力 ×{wing_spec['drag_penalty']:.1f}")

# =========================================================================
# 💥 物理シミュレーション & リアル破壊力学エンジン
# =========================================================================
def run_simulation():
    dt = 0.5
    g0 = 9.80665
    R_earth = 6371000.0

    x, y = 0.0, 0.0
    vx, vy = 0.0, 0.0
    stage = 1
    fuel_rem = float(s1_fuel * 1000.0)
    fairing_attached = True
    wings_attached = bool(wing_spec["wing_id"] != "none")

    history = []
    fail_reason = None

    # カウントダウン (T-10s)
    for cd_step in range(20):
        t_cd = -10.0 + cd_step * 0.5
        pre_ignition = bool(t_cd >= -3.0)
        history.append({
            "t": float(t_cd), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "stage": 1, "fairing": True, "wings": wings_attached,
            "exploded": False, "explosion_type": "NONE", "thrust": pre_ignition, "pitch": 0.0, "event": "COUNTDOWN"
        })

    maxq_passed = False
    supersonic_called = False

    # 1. 燃焼室過圧
    if s1_spec["pc"] > s1_spec["pc_limit"]:
        fail_reason = f"ターボポンプ破裂: 燃焼室圧 {s1_spec['pc']} bar が許容限界 {s1_spec['pc_limit']} bar を超過。"
        history.append({
            "t": 0.1, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 0.0,
            "stage": 1, "fairing": True, "wings": wings_attached, "exploded": True,
            "explosion_type": "PAD_OVERPRESSURE", "thrust": False, "pitch": 0.0, "event": "RUD"
        })
        return history, fail_reason

    # 2. 燃料リスク
    if s1_spec["fuel_risk"] > 0.3 and np.random.rand() < s1_spec["fuel_risk"]:
        fail_reason = "特異点崩壊: ダークマター濃縮スラリーが臨界に達し、発射台ごと事象の地平線へ消失。"
        history.append({
            "t": 0.2, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 0.0,
            "stage": 1, "fairing": True, "wings": wings_attached, "exploded": True,
            "explosion_type": "SINGULARITY", "thrust": False, "pitch": 0.0, "event": "RUD"
        })
        return history, fail_reason

    for step in range(1500):
        t = float(step * dt)
        alt = float(y)
        alt_km = float(alt / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))
        mach = v / 340.0

        rho = float(1.225 * np.exp(-alt / 7400.0)) if alt < 140000 else 0.0
        q = float(0.5 * rho * (v**2) / 1000.0)

        # 重力ターン角
        if alt_km < turn_start_alt:
            target_pitch_deg = 90.0
        elif alt_km < turn_end_alt:
            prog = (alt_km - turn_start_alt) / (turn_end_alt - turn_start_alt)
            target_pitch_deg = 90.0 * (1.0 - (prog ** turn_exponent))
        else:
            target_pitch_deg = 0.0

        # 主翼による異常空力モーメント
        extra_pitch_deflection = 0.0
        wing_lift_force = 0.0
        if wings_attached and alt_km < 45.0 and rho > 0.004:
            wing_lift_force = 0.5 * rho * (v**2) * (wing_spec["lift_coeff"] * 22.0) * np.sin(np.radians(angle_of_attack))
            extra_pitch_deflection = (wing_lift_force / 9000.0) * (mach ** 1.35)
            target_pitch_deg -= extra_pitch_deflection

        pitch_deg = max(-50.0, min(90.0, target_pitch_deg))
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
        w_mass = (wing_spec["mass"] * 1000.0) if wings_attached else 0.0

        # 推力演算
        if stage == 1:
            if fuel_rem <= 0:
                stage = 2
                cur_event = "HOT_STAGING"
                fuel_rem = float(s2_fuel * 1000.0)
                thrust = 0.0
            else:
                cur_mass = float((s1_spec["dry_mass"] + s2_fuel + s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + w_mass + fuel_rem)
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

        drag_area = (12.0 * s1_spec["cd_mod"] * wing_spec["drag_penalty"]) if stage == 1 else (5.2 * s2_spec["cd_mod"])
        drag_force = float(0.5 * rho * (v**2) * fair_spec["cd"] * drag_area)
        drag_x = -drag_force * (vx / v) if v > 0 else 0.0
        drag_y = -drag_force * (vy / v) if v > 0 else 0.0

        lift_x = -wing_lift_force * dir_y
        lift_y = wing_lift_force * dir_x

        g_cur = float(g0 * ((R_earth / (R_earth + alt)) ** 2))
        centrifugal_acc = (vx ** 2) / (R_earth + alt)
        grav_y = -cur_mass * (g_cur - centrifugal_acc)

        fx = thrust * dir_x + drag_x + lift_x
        fy = thrust * dir_y + drag_y + lift_y + grav_y

        if alt <= 0.0 and fy <= 0.0:
            if t > 1.0:
                fail_reason = "離床推力不足 (TWR < 1.0): 自重を持ち上げられず発射台上で轟沈・大爆発。"
                history.append({
                    "t": t, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0,
                    "stage": 1, "fairing": True, "wings": wings_attached, "exploded": True,
                    "explosion_type": "PAD_CRUSH", "thrust": False, "pitch": 0.0, "event": "RUD"
                })
                break
            ax, ay, vx, vy = 0.0, 0.0, 0.0, 0.0
            acc_g = 1.0
        else:
            ax = fx / cur_mass
            ay = fy / cur_mass
            acc_g = float(np.sqrt((thrust * dir_x + drag_x + lift_x)**2 + (thrust * dir_y + drag_y + lift_y)**2) / (cur_mass * g0))

        cur_spec = s1_spec if stage == 1 else s2_spec

        # 破壊判定
        if wings_attached and mach > wing_spec["flutter_mach"] and rho > 0.04:
            fail_reason = f"主翼遷音速フラッター破壊: マッハ {mach:.2f} の衝撃波干渉でもぎ取られた主翼がタンクを直撃破壊。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": False, "exploded": True,
                "explosion_type": "WING_TEAR", "thrust": False, "pitch": visual_pitch, "event": "RUD"
            })
            break

        if abs(extra_pitch_deflection) > 30.0 and q > 18.0:
            fail_reason = f"空力トリム破綻（ピッチ反転）: 主翼の巨大揚力により横滑りし、動圧 {q:.1f} kPa で機体真っ二つ。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "exploded": True,
                "explosion_type": "AERODYNAMIC_SNAP", "thrust": False, "pitch": visual_pitch, "event": "RUD"
            })
            break

        if q > cur_spec["max_q"]:
            fail_reason = f"Max-Q 構造圧壊: 動圧 {q:.1f} kPa が外殻等価強度 ({cur_spec['max_q']:.1f} kPa) を突破。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "exploded": True,
                "explosion_type": "STRUCTURAL_COLLAPSE", "thrust": False, "pitch": visual_pitch, "event": "RUD"
            })
            break

        if acc_g > cur_spec["max_g"]:
            fail_reason = f"過大加速度圧砕: 加速度 {acc_g:.1f} G が許容限界 ({cur_spec['max_g']:.1f} G) を超過。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "exploded": True,
                "explosion_type": "OVER_G", "thrust": False, "pitch": visual_pitch, "event": "RUD"
            })
            break

        vx = float(vx + ax * dt)
        vy = float(vy + ay * dt)
        x = float(x + vx * dt)
        y = float(max(0.0, y + vy * dt))

        history.append({
            "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g,
            "stage": int(stage), "fairing": bool(fairing_attached), "wings": bool(wings_attached),
            "exploded": False, "explosion_type": "NONE", "thrust": bool(thrust > 0),
            "pitch": visual_pitch, "event": cur_event
        })

        if alt_km >= 160.0 and vx >= 7780.0 and abs(vy) < 400.0:
            history.append({
                "t": t + dt, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": 0.0,
                "stage": int(stage), "fairing": bool(fairing_attached), "wings": bool(wings_attached),
                "exploded": False, "explosion_type": "NONE", "thrust": False,
                "pitch": visual_pitch, "event": "ORBIT"
            })
            break

    if not fail_reason and history[-1]["event"] != "ORBIT":
        fail_reason = f"軌道速度未達（燃料切れ弾道落下）。到達高度: {alt_km:.1f} km, 水平速度: {vx:.0f} m/s (必要: 7,780 m/s)"

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

simulation_executed = False
traj_data = None
error_msg = None

if st.button("🔴 AETHEL-9 超精密実写中継 ＆ 軌道投入シミュレーション開始", use_container_width=True, type="primary"):
    simulation_executed = True
    traj_data, error_msg = run_simulation()

    rocket_visual_cfg = {
        "s1_mat": s1_spec["mat_id"],
        "s2_mat": s2_spec["mat_id"],
        "s1_eng": int(s1_eng_count),
        "s2_eng": int(s2_eng_count),
        "flame_hex": s1_spec["flame_hex"],
        "outer_hex": s1_spec["outer_hex"],
        "fairing_shape": fair_spec["shape_id"],
        "wing_id": wing_spec["wing_id"]
    }

    traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
    cfg_json = json.dumps(rocket_visual_cfg)
    fail_msg_clean = (error_msg or "").replace('"', '\\"').replace("'", "\\'")

    html_code = f"""
    <div id="broadcast-frame" style="position: relative; width: 100%; height: 900px; background: #000205; border-radius: 8px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none;">
        <script>
            window.parent.document.getElementById('launch-viewport').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        </script>

        <div id="canvas-container" style="width: 100%; height: 100%; position: absolute; top: 0; left: 0;"></div>

        <!-- 実写シネマティック光学フィルター (周辺光量落ち・アナモルフィック調・グレイン) -->
        <div style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; background: radial-gradient(ellipse at center, transparent 35%, rgba(0, 1, 5, 0.8) 100%); mix-blend-mode: multiply; z-index: 2;"></div>

        <!-- 放送中継トップバナー -->
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 48px; background: rgba(3, 7, 18, 0.82); backdrop-filter: blur(16px); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 10;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <span id="live-indicator" style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 12px #ef4444; animation: livePulse 1.4s infinite alternate;"></span>
                <span style="color: #ffffff; font-weight: 800; font-size: 13px; letter-spacing: 2px;">LIVE WEBCAST</span>
                <span style="color: rgba(255,255,255,0.2);">|</span>
                <span id="cam-tag" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; font-family: monospace;">TRACKER: PAD ULTRA-TELEPHOTO (600mm)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 20px; font-family: monospace; font-size: 11px;">
                <span style="color: #94a3b8;">ATMOSPHERE: <strong id="hud-regime" style="color: #f8fafc;">SEA LEVEL</strong></span>
                <span style="color: #10b981;">OPTICAL LOCK: 4K HDR NOMINAL</span>
            </div>
        </div>

        <style>
            @keyframes livePulse {{ from {{ opacity: 0.35; }} to {{ opacity: 1.0; }} }}
        </style>

        <!-- 🛰️ 軌道フライト HUD -->
        <div style="position: absolute; top: 60px; right: 24px; width: 280px; background: rgba(3, 7, 18, 0.85); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 4px; padding: 14px; z-index: 10; color: #fff;">
            <div style="font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 8px; display: flex; justify-content: space-between;">
                <span>DOWNRANGE TRAJECTORY</span>
                <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">0.0 km</span>
            </div>
            <canvas id="orbit-canvas" width="250" height="90" style="width: 100%; height: 90px; background: #01040d; border-radius: 2px;"></canvas>
            <div style="display: flex; justify-content: space-between; font-size: 9px; color: #64748b; margin-top: 6px; font-family: monospace;">
                <span>LC-1</span>
                <span>MAX-Q</span>
                <span>STAGE-1 SEP</span>
                <span>ORBIT</span>
            </div>
        </div>

        <!-- 破壊アラート -->
        <div id="rud-banner" style="display: none; position: absolute; top: 180px; left: 50%; transform: translateX(-50%); background: rgba(153, 27, 27, 0.95); backdrop-filter: blur(16px); border: 2px solid #ef4444; border-radius: 4px; padding: 18px 32px; z-index: 25; text-align: center; box-shadow: 0 0 50px rgba(239, 68, 68, 0.6);">
            <div style="color: #fff; font-size: 18px; font-weight: 900; letter-spacing: 2.5px; font-family: monospace;">🚨 CATASTROPHIC VEHICLE ANOMALY (RUD) 🚨</div>
            <div id="rud-desc" style="color: #fecaca; font-size: 13px; font-weight: 600; margin-top: 8px; max-width: 520px; line-height: 1.4;"></div>
        </div>

        <!-- 放送テレメトリー HUD -->
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(1, 3, 8, 0.98) 0%, rgba(2, 6, 14, 0.88) 75%, transparent 100%); padding: 28px 36px 20px 36px; box-sizing: border-box; display: flex; align-items: flex-end; justify-content: space-between; z-index: 10;">
            <div>
                <div id="tv-status" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 2px; margin-bottom: 2px;">COUNTDOWN SEQUENCE</div>
                <div id="tv-timer" style="color: #ffffff; font-size: 48px; font-weight: 900; font-family: 'Consolas', monospace; letter-spacing: 2px; text-shadow: 0 0 25px rgba(56, 189, 248, 0.4);">T- 00:10.0</div>
            </div>

            <div style="display: flex; gap: 40px; border-left: 1px solid rgba(255,255,255,0.15); padding-left: 36px;">
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px; text-transform: uppercase;">SPEED</div>
                    <div style="color: #fff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-spd">0</span> <span style="font-size: 12px; color: #94a3b8;">km/h</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px; text-transform: uppercase;">ALTITUDE</div>
                    <div style="color: #fff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-alt">0.0</span> <span style="font-size: 12px; color: #94a3b8;">km</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px; text-transform: uppercase;">DYNAMIC Q</div>
                    <div style="color: #fff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-q">0.0</span> <span style="font-size: 12px; color: #94a3b8;">kPa</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px; text-transform: uppercase;">VEHICLE STATUS</div>
                    <div id="tv-stage-badge" style="color: #34d399; font-size: 20px; font-weight: 800; font-family: 'Consolas', monospace;">STAGE 1 BOOSTER</div>
                </div>
            </div>
        </div>

        <div id="flash-overlay" style="position: absolute; top:0; left:0; width:100%; height:100%; background:#fff; opacity:0; pointer-events:none; z-index:30; transition:opacity 0.08s;"></div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const data = {traj_json};
        const cfg = {cfg_json};
        const failMessage = "{fail_msg_clean}";
        const container = document.getElementById('canvas-container');
        const orbitCvs = document.getElementById('orbit-canvas');
        const octx = orbitCvs.getContext('2d');
        const flashOverlay = document.getElementById('flash-overlay');
        const rudBanner = document.getElementById('rud-banner');
        const rudDesc = document.getElementById('rud-desc');

        // 音響合成エンジン
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null, rumbleGain = null, crackleGain = null;
        function initAudio() {{
            if (!actx) {{
                actx = new AudioCtx();
                const buf = actx.createBuffer(1, actx.sampleRate * 2, actx.sampleRate);
                const d = buf.getChannelData(0);
                for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

                const rSrc = actx.createBufferSource(); rSrc.buffer = buf; rSrc.loop = true;
                const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 110;
                rumbleGain = actx.createGain(); rumbleGain.gain.value = 0;
                rSrc.connect(lp); lp.connect(rumbleGain); rumbleGain.connect(actx.destination);
                rSrc.start(0);

                const cSrc = actx.createBufferSource(); cSrc.buffer = buf; cSrc.loop = true;
                const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 850; bp.Q.value = 2.4;
                crackleGain = actx.createGain(); crackleGain.gain.value = 0;
                cSrc.connect(bp); bp.connect(crackleGain); crackleGain.connect(actx.destination);
                cSrc.start(0);
            }}
            if (actx.state === 'suspended') actx.resume();
        }}

        function playExplosionSound() {{
            if (!actx) return;
            const osc = actx.createOscillator();
            const g = actx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(75, actx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(14, actx.currentTime + 1.6);
            g.gain.setValueAtTime(0.95, actx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + 3.0);
            osc.connect(g); g.connect(actx.destination);
            osc.start(); osc.stop(actx.currentTime + 3.0);
        }}

        const voicedEvents = new Set();
        function speak(text) {{
            if (!('speechSynthesis' in window)) return;
            const u = new SpeechSynthesisUtterance(text);
            u.lang = 'en-US'; u.rate = 1.05;
            window.speechSynthesis.speak(u);
        }}

        // =========================================================================
        // 🌍 Three.js 実写光学＆実在衛星写真パイプライン
        // =========================================================================
        const scene = new THREE.Scene();
        // 望遠感を出すためFOVを22度に設定（超望遠シネマティックレンズ）
        const camera = new THREE.PerspectiveCamera(22, container.clientWidth / container.clientHeight, 0.5, 50000000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.25;
        container.appendChild(renderer.domElement);

        // 恒星宇宙背景 (Starfield)
        const starGeo = new THREE.BufferGeometry();
        const starCount = 4500;
        const starPositions = new Float32Array(starCount * 3);
        const starColors = new Float32Array(starCount * 3);
        for(let i=0; i<starCount*3; i+=3) {{
            const rad = 25000000;
            const u = Math.random();
            const v = Math.random();
            const theta = u * 2.0 * Math.PI;
            const phi = Math.acos(2.0 * v - 1.0);
            starPositions[i] = rad * Math.sin(phi) * Math.cos(theta);
            starPositions[i+1] = rad * Math.sin(phi) * Math.sin(theta);
            starPositions[i+2] = rad * Math.cos(phi);
            const tint = 0.8 + Math.random() * 0.2;
            starColors[i] = tint; starColors[i+1] = tint * 0.95; starColors[i+2] = tint * 1.1;
        }}
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
        starGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3));
        const starMat = new THREE.PointsMaterial({{ size: 1.8, vertexColors: true, transparent: true, opacity: 0.9 }});
        scene.add(new THREE.Points(starGeo, starMat));

        // 🛰️ 実写地球テクスチャのロード (NASA Blue Marble / 高解像度衛星写真)
        const texLoader = new THREE.TextureLoader();
        // NASA実写テクスチャ (CORS対応オープンミラー)
        const earthMapTex = texLoader.load('https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/planets/earth_atmos_2048.jpg');
        const earthNormalTex = texLoader.load('https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/planets/earth_normal_2048.jpg');
        const earthSpecTex = texLoader.load('https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/planets/earth_specular_2048.jpg');
        const earthCloudsTex = texLoader.load('https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/planets/earth_clouds_1024.png');

        // 地球本体 (半径 6,371 km)
        const R_EARTH = 6371.0;
        const earthMat = new THREE.MeshStandardMaterial({{
            map: earthMapTex,
            normalMap: earthNormalTex,
            roughnessMap: earthSpecTex,
            roughness: 0.65,
            metalness: 0.1
        }});
        const earthMesh = new THREE.Mesh(new THREE.SphereGeometry(R_EARTH, 160, 120), earthMat);
        earthMesh.position.set(0, -R_EARTH, 0);
        // 発射台（ケネディ宇宙センター/海岸線）にカメラが正対するよう自転角調整
        earthMesh.rotation.y = -Math.PI * 0.62;
        earthMesh.rotation.x = 0.28;
        scene.add(earthMesh);

        // 実写雲海レイヤー (実写クラウドマップ)
        const cloudMesh = new THREE.Mesh(
            new THREE.SphereGeometry(R_EARTH + 4.5, 96, 72),
            new THREE.MeshStandardMaterial({{
                map: earthCloudsTex,
                transparent: true,
                opacity: 0.72,
                blending: THREE.NormalBlending,
                depthWrite: false
            }})
        );
        cloudMesh.position.set(0, -R_EARTH, 0);
        cloudMesh.rotation.copy(earthMesh.rotation);
        scene.add(cloudMesh);

        // 大気レイリー散乱リムグロー (青い大気のベール)
        const atmoMat = new THREE.ShaderMaterial({{
            side: THREE.BackSide,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            vertexShader: `
                varying vec3 vNormal;
                varying vec3 vWorldPosition;
                void main() {{
                    vNormal = normalize(normalMatrix * normal);
                    vec4 worldPos = modelMatrix * vec4(position, 1.0);
                    vWorldPosition = worldPos.xyz;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }}
            `,
            fragmentShader: `
                varying vec3 vNormal;
                varying vec3 vWorldPosition;
                void main() {{
                    vec3 viewDir = normalize(cameraPosition - vWorldPosition);
                    float rim = max(0.0, dot(viewDir, -vNormal));
                    float intensity = pow(1.0 - rim, 3.2);
                    vec3 skyBlue = vec3(0.18, 0.52, 0.98);
                    vec3 glowColor = vec3(0.95, 0.45, 0.15);
                    vec3 col = mix(skyBlue, glowColor, pow(intensity, 2.8));
                    gl_FragColor = vec4(col, intensity * 0.88);
                }}
            `
        }});
        const atmoMesh = new THREE.Mesh(new THREE.SphereGeometry(R_EARTH + 85.0, 96, 72), atmoMat);
        atmoMesh.position.set(0, -R_EARTH, 0);
        scene.add(atmoMesh);

        // 太陽光・環境ライティング
        const sunLight = new THREE.DirectionalLight(0xfff8ee, 4.2);
        sunLight.position.set(8000, 12000, 6000);
        scene.add(sunLight);
        scene.add(new THREE.AmbientLight(0x0a192f, 0.7));

        // 発射台 LC-39A 風ディテール
        const pad = new THREE.Group();
        const metalMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.35, metalness: 0.9 }});
        const towerMat = new THREE.MeshStandardMaterial({{ color: 0x475569, wireframe: true }});
        const tower = new THREE.Mesh(new THREE.BoxGeometry(5.0, 48, 5.0), towerMat);
        tower.position.set(-7.5, 24, 0); pad.add(tower);
        const mount = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 5.5, 3.5, 32), metalMat);
        mount.position.set(0, 1.75, 0); pad.add(mount);
        scene.add(pad);

        // ロケット本体
        const rocket = new THREE.Group();
        scene.add(rocket);

        const s1Mat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, roughness: 0.18, metalness: 0.94 }});
        const s2Mat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.22, metalness: 0.85 }});

        const s1Len = 15.0;
        const s1 = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0, s1Len, 64), s1Mat);
        s1.position.y = s1Len / 2 + 1.8;
        rocket.add(s1);

        const s2Len = 8.0;
        const s2 = new THREE.Mesh(new THREE.CylinderGeometry(0.98, 0.98, s2Len, 64), s2Mat);
        s2.position.y = s1Len + 1.8 + s2Len / 2;
        rocket.add(s2);

        const nose = new THREE.Mesh(new THREE.ConeGeometry(0.98, 3.6, 64), s2Mat);
        nose.position.y = s1Len + 1.8 + s2Len + 1.8;
        rocket.add(nose);

        // 主翼アドオン
        const wingsGroup = new THREE.Group();
        rocket.add(wingsGroup);
        if (cfg.wing_id === 'airliner') {{
            const wingGeo = new THREE.BoxGeometry(18.0, 0.24, 3.0);
            const wingMat = new THREE.MeshStandardMaterial({{ color: 0xf1f5f9, roughness: 0.4, metalness: 0.2 }});
            const airlinerWings = new THREE.Mesh(wingGeo, wingMat);
            airlinerWings.position.set(0, s1Len * 0.45, 0);
            wingsGroup.add(airlinerWings);
        }} else if (cfg.wing_id === 'delta') {{
            const deltaShape = new THREE.Shape();
            deltaShape.moveTo(-6.5, 0); deltaShape.lineTo(6.5, 0); deltaShape.lineTo(0, 8.5); deltaShape.closePath();
            const deltaGeo = new THREE.ExtrudeGeometry(deltaShape, {{ depth: 0.2, bevelEnabled: false }});
            const deltaMesh = new THREE.Mesh(deltaGeo, new THREE.MeshStandardMaterial({{ color: 0x334155, metalness: 0.85, roughness: 0.25 }}));
            deltaMesh.rotation.x = -Math.PI / 2;
            deltaMesh.position.set(0, s1Len * 0.65, 0);
            wingsGroup.add(deltaMesh);
        }}

        // =========================================================================
        // 🔥 実写ロケット排気噴射炎＆超巨大真空プルーム
        // =========================================================================
        const plume = new THREE.Group();
        rocket.add(plume);

        const fColor = cfg.flame_hex;
        const oColor = cfg.outer_hex;

        // 1. 中心部：超高温ホワイトコア
        const coreFlame = new THREE.Mesh(
            new THREE.ConeGeometry(0.65, 12.0, 32),
            new THREE.MeshBasicMaterial({{ color: 0xffffff, blending: THREE.AdditiveBlending }})
        );
        coreFlame.rotation.x = Math.PI; coreFlame.position.y = -6.0; plume.add(coreFlame);

        // 2. マッハダイヤモンド群 (実写の超音速ショックコーン)
        const shockDiamonds = [];
        for (let i = 0; i < 9; i++) {{
            const dia = new THREE.Mesh(
                new THREE.OctahedronGeometry(0.42 - i * 0.035, 1),
                new THREE.MeshBasicMaterial({{ color: 0xffffff, blending: THREE.AdditiveBlending }})
            );
            dia.scale.set(1.15, 0.4, 1.15);
            dia.position.y = -1.4 - i * 1.5;
            plume.add(dia);
            shockDiamonds.push(dia);
        }}

        // 3. メイン乱流炎
        const outerPlume = new THREE.Mesh(
            new THREE.ConeGeometry(2.2, 28.0, 32),
            new THREE.MeshBasicMaterial({{ color: fColor, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false }})
        );
        outerPlume.rotation.x = Math.PI; outerPlume.position.y = -14.0; plume.add(outerPlume);

        // 4. 真空巨大膨張クラゲプルーム (Jellyfish Effect: 高度40km以上で直径数百mに拡散)
        const jellyfishGeo = new THREE.SphereGeometry(18.0, 32, 32);
        const jellyfishMat = new THREE.MeshBasicMaterial({{
            color: oColor,
            transparent: true,
            opacity: 0.0,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        }});
        const jellyfishPlume = new THREE.Mesh(jellyfishGeo, jellyfishMat);
        jellyfishPlume.position.y = -22.0;
        plume.add(jellyfishPlume);

        // =========================================================================
        // 💨 実写スモークトレイル＆発射台消火蒸気
        // =========================================================================
        function createSmokeParticleTexture() {{
            const c = document.createElement('canvas'); c.width = 128; c.height = 128;
            const ctx = c.getContext('2d');
            const g = ctx.createRadialGradient(64,64,8, 64,64,64);
            g.addColorStop(0, 'rgba(255,255,255,0.95)');
            g.addColorStop(0.3, 'rgba(220,230,245,0.6)');
            g.addColorStop(0.7, 'rgba(160,175,195,0.2)');
            g.addColorStop(1, 'rgba(120,135,150,0)');
            ctx.fillStyle = g; ctx.fillRect(0,0,128,128);
            return new THREE.CanvasTexture(c);
        }}
        const smokeTex = createSmokeParticleTexture();
        const P_MAX = 1200;
        const pool = [];
        const pGroup = new THREE.Group(); scene.add(pGroup);
        for(let i=0; i<P_MAX; i++) {{
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({{ map: smokeTex, transparent: true, opacity: 0, depthWrite: false }}));
            sp.visible = false; pGroup.add(sp);
            pool.push({{ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 4, o: 0.8 }});
        }}
        let pIdx = 0;
        function emitSmoke(x, y, z, vx, vy, vz, s0, s1, life, opacity) {{
            const p = pool[pIdx]; pIdx = (pIdx + 1) % P_MAX;
            p.active = true; p.sp.visible = true; p.sp.position.set(x, y, z);
            p.vx = vx; p.vy = vy; p.vz = vz; p.age = 0; p.maxAge = life; p.s0 = s0; p.s1 = s1; p.o = opacity;
        }}

        // 破壊破片
        const DEBRIS_MAX = 160;
        const debrisPool = [];
        const debrisGroup = new THREE.Group(); scene.add(debrisGroup);
        for(let i=0; i<DEBRIS_MAX; i++) {{
            const deb = new THREE.Mesh(
                new THREE.BoxGeometry(0.8 + Math.random(), 0.3 + Math.random()*0.4, 0.4),
                new THREE.MeshStandardMaterial({{ color: (i%2===0)?0xe2e8f0:0x334155, metalness: 0.9, roughness: 0.25 }})
            );
            deb.visible = false; debrisGroup.add(deb);
            debrisPool.push({{ mesh: deb, active: false, vx: 0, vy: 0, vz: 0, rx: 0, ry: 0, rz: 0 }});
        }}

        function triggerDebrisExplosion(x, y, vBaseX, vBaseY) {{
            for(let i=0; i<DEBRIS_MAX; i++) {{
                const d = debrisPool[i];
                d.active = true; d.mesh.visible = true;
                d.mesh.position.set(x + (Math.random()-0.5)*4, y + (Math.random()-0.5)*10, (Math.random()-0.5)*4);
                const angle = Math.random() * Math.PI * 2;
                const spd = 3.0 + Math.random() * 12.0;
                d.vx = (vBaseX * 0.05) + Math.cos(angle) * spd;
                d.vy = (vBaseY * 0.05) + Math.sin(angle) * spd;
                d.vz = (Math.random()-0.5) * spd * 1.5;
                d.rx = Math.random()*0.4; d.ry = Math.random()*0.4; d.rz = Math.random()*0.4;
            }}
        }}

        function drawOrbitMap(altKm, dRangeKm, exploded) {{
            octx.clearRect(0, 0, 250, 90);
            octx.beginPath(); octx.arc(125, 240, 185, Math.PI, 0); octx.strokeStyle = '#1e293b'; octx.lineWidth = 3; octx.stroke();
            octx.beginPath(); octx.arc(125, 240, 215, Math.PI, 0); octx.strokeStyle = 'rgba(56, 189, 248, 0.25)'; octx.lineWidth = 1; octx.setLineDash([4, 4]); octx.stroke(); octx.setLineDash([]);

            const px = 20 + Math.min(210, (dRangeKm / 1200.0) * 210);
            const py = 76 - Math.min(65, (altKm / 200.0) * 65);

            octx.beginPath(); octx.moveTo(20, 76); octx.quadraticCurveTo(px * 0.5, 76, px, py);
            octx.strokeStyle = exploded ? '#ef4444' : '#38bdf8'; octx.lineWidth = 2; octx.stroke();

            octx.fillStyle = exploded ? '#dc2626' : '#38bdf8';
            octx.beginPath(); octx.arc(px, py, exploded ? 6 : 4, 0, Math.PI * 2); octx.fill();
        }}

        // =========================================================================
        // 🎥 超望遠（800mm〜1200mm相当）シネマティック・ディレクターカメラワーク
        // =========================================================================
        const camTarget = new THREE.Vector3(0, 12, 0);
        let camShake = 0.0;

        function updateCam(simT, rx, ry, alt, pitch, exploded) {{
            const upX = Math.sin(pitch), upY = Math.cos(pitch);

            if (exploded) {{
                document.getElementById('cam-tag').innerText = "TRACKER 1: CATASTROPHIC BREAKUP LONG-SHOT";
                camera.position.lerp(new THREE.Vector3(rx + 80, ry + 30, 140), 0.08);
                camTarget.lerp(new THREE.Vector3(rx, ry, 0), 0.12);
            }} else if (simT < 0.0) {{
                // 発射台点火前：海岸線越しの望遠
                document.getElementById('cam-tag').innerText = "TRACKER 1: PAD TELEPHOTO (400mm)";
                camera.position.set(38.0, 8.0, 75.0);
                camTarget.set(0, 12.0, 0);
            }} else if (simT < 4.0) {{
                // 発射直後：タワークリアランスを引いて全体を収める
                document.getElementById('cam-tag').innerText = "COASTAL TRACKER 1: LIFTOFF CLEARANCE";
                camera.position.set(-65.0, 18.0, 120.0);
                camTarget.set(rx, ry + 12.0, 0);
            }} else if (alt < 15.0) {{
                // 【低空〜音速突破】：数km離れた地上トラッカーから超ロング引き（機体全体＋長大な煙の柱を捉える）
                document.getElementById('cam-tag').innerText = "COASTAL SUPER-TELEPHOTO TRACKER (800mm)";
                const camDist = 280.0 + alt * 15.0;
                camera.position.lerp(new THREE.Vector3(-camDist * 0.7, 18.0 + alt * 0.5, camDist * 0.9), 0.05);
                // 画面上部にロケットを配置し、下部に伸びる巨大な排気煙トレイルを収める
                camTarget.lerp(new THREE.Vector3(rx + upX * 15.0, ry + upY * 15.0, 0), 0.12);
            }} else if (alt < 80.0) {{
                // 【成層圏・Max-Q】：高空追尾機からの超望遠シネマティック。湾曲する地球の地平線とロケット全体が完全にフレームイン
                document.getElementById('cam-tag').innerText = "AIRBORNE WB-57 CHASE TRACKER (WIDE HORIZON)";
                const camX = rx - 240.0;
                const camY = ry - 60.0;
                const camZ = 380.0 + (alt - 15.0) * 3.5;
                camera.position.lerp(new THREE.Vector3(camX, camY, camZ), 0.06);
                camTarget.lerp(new THREE.Vector3(rx + upX * 25.0, ry + upY * 25.0, 0), 0.1);
            }} else {{
                // 【宇宙空間・LEO投入】：漆黒の真空空間、広大な地球の青い円弧を背景にした超広角ロングショット
                document.getElementById('cam-tag').innerText = "ORBITAL TELEMETRY: ULTRA-WIDE VACUUM CAM";
                const ox = -upX * 350.0 + upY * 120.0;
                const oy = -upY * 350.0 - upX * 120.0;
                camera.position.lerp(new THREE.Vector3(rx + ox, ry + oy, 580.0), 0.08);
                camTarget.lerp(new THREE.Vector3(rx, ry, 0), 0.1);
            }}

            if (camShake > 0.002) {{
                camera.position.x += (Math.random() - 0.5) * camShake;
                camera.position.y += (Math.random() - 0.5) * camShake;
                camShake *= 0.92;
            }}
            camera.lookAt(camTarget);
        }}

        // =========================================================================
        // ⏱️ アニメーション・メインループ
        // =========================================================================
        let tStart = performance.now();
        let explodedTriggered = false;

        function animate(now) {{
            requestAnimationFrame(animate);
            initAudio();

            const simT = -10.0 + (now - tStart) / 1000.0;

            let idx = 0;
            while (idx < data.length - 1 && data[idx + 1].t <= simT) idx++;
            const nIdx = Math.min(idx + 1, data.length - 1);
            const p0 = data[idx], p1 = data[nIdx];
            const a = (p1.t > p0.t) ? Math.max(0, Math.min(1, (simT - p0.t) / (p1.t - p0.t))) : 0;

            const rx = (p0.x + (p1.x - p0.x) * a) * 0.1;
            const ry = (p0.y + (p1.y - p0.y) * a) * 0.1;
            const alt = p0.alt + (p1.alt - p0.alt) * a;
            const vel = p0.v + (p1.v - p0.v) * a;
            const q   = p0.q + (p1.q - p0.q) * a;
            const pitch = p0.pitch + (p1.pitch - p0.pitch) * a;
            const dRangeKm = (rx * 10.0) / 1000.0;

            rocket.position.set(rx, ry, 0);
            rocket.rotation.z = -pitch;

            // 地球の自転微動
            earthMesh.rotation.y = -Math.PI * 0.62 + (dRangeKm * 0.00003);
            cloudMesh.rotation.y = earthMesh.rotation.y + 0.00005;

            updateCam(simT, rx, ry, alt, pitch, p0.exploded);
            drawOrbitMap(alt, dRangeKm, p0.exploded);

            // 💥 爆発瞬間
            if (p0.exploded && !explodedTriggered) {{
                explodedTriggered = true;
                rocket.visible = false;
                plume.visible = false;
                camShake = 1.1;
                flashOverlay.style.opacity = '1.0';
                setTimeout(() => {{ flashOverlay.style.opacity = '0.0'; }}, 80);

                playExplosionSound();
                triggerDebrisExplosion(rx, ry, p0.v * Math.cos(p0.pitch), p0.v * Math.sin(p0.pitch));

                for(let k=0; k<90; k++) {{
                    const ang = Math.random()*Math.PI*2;
                    emitSmoke(rx, ry, 0, Math.cos(ang)*2.2, Math.sin(ang)*2.2, (Math.random()-0.5)*2.5, 5.0, 28.0, 70, 0.95);
                }}

                rudBanner.style.display = 'block';
                rudDesc.innerText = failMessage;
                speak("Vehicle breakup confirmed.");
                document.getElementById('tv-stage-badge').innerText = "VEHICLE DESTROYED";
                document.getElementById('tv-stage-badge').style.color = "#ef4444";
            }}

            if (explodedTriggered) {{
                for(let i=0; i<DEBRIS_MAX; i++) {{
                    const d = debrisPool[i]; if (!d.active) continue;
                    d.mesh.position.x += d.vx * 0.016;
                    d.mesh.position.y += d.vy * 0.016;
                    d.mesh.position.z += d.vz * 0.016;
                    d.vy -= 9.8 * 0.016 * 0.1;
                    d.mesh.rotation.x += d.rx; d.mesh.rotation.y += d.ry;
                }}
            }}

            let regime = "TROPOSPHERE (対流圏)";
            if (alt >= 100.0) regime = "THERMOSPHERE / ORBIT (宇宙空間)";
            else if (alt >= 50.0) regime = "MESOSPHERE (中間圏)";
            else if (alt >= 12.0) regime = "STRATOSPHERE (成層圏)";
            document.getElementById('hud-regime').innerText = regime;
            document.getElementById('hud-downrange').innerText = `${{dRangeKm.toFixed(1)}} km`;

            // カウントダウン＆点火時の巨大な発射台白煙
            if (simT < 0.0) {{
                const sec = Math.ceil(Math.abs(simT));
                document.getElementById('tv-timer').innerText = `T- 00:0${{sec}}.0`;
                if (simT >= -3.0 && !p0.exploded) {{
                    camShake = 0.22;
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.55, actx.currentTime, 0.1);
                    // 発射台横から吹き出す巨大な消火スチーム
                    for(let i=0; i<8; i++) {{
                        const side = (i%2 === 0)? 1 : -1;
                        emitSmoke(rx + (Math.random()-0.5)*3, 1.0, (Math.random()-0.5)*3, side * (0.6 + Math.random()*0.8), 0.1, (Math.random()-0.5)*0.3, 3.0, 16.0, 50, 0.9);
                    }}
                }}
            }} else if (!p0.exploded) {{
                const m = Math.floor(simT / 60); const s = simT % 60;
                document.getElementById('tv-timer').innerText = `T+ ${{String(m).padStart(2,'0')}}:${{s.toFixed(1).padStart(4,'0')}}`;
                if (simT >= 0 && !voicedEvents.has('liftoff')) {{
                    voicedEvents.add('liftoff');
                    speak("Liftoff of Aethel-9.");
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.9, actx.currentTime, 0.1);
                    if (crackleGain) crackleGain.gain.setTargetAtTime(0.48, actx.currentTime, 0.1);
                }}
            }}

            // 排気火炎・真空膨張・ショックダイヤモンド
            if (p0.thrust && !p0.exploded) {{
                plume.visible = true;
                const vacExp = 1.0 + Math.min(14.0, alt / 8.0);
                const flicker = 0.94 + Math.random() * 0.12;

                coreFlame.scale.set(1.0, flicker, 1.0);
                outerPlume.scale.set(vacExp * 0.7, flicker * (1.0 + vacExp * 0.35), vacExp * 0.7);

                // 高度によるマッハダイヤモンドの消失（大気圧低下に伴い拡散）
                const shockVis = Math.max(0.0, 1.0 - alt / 35.0);
                shockDiamonds.forEach(sd => {{ sd.visible = shockVis > 0.05; sd.material.opacity = shockVis; }});

                // 高度40km以上のクラゲ状真空光彩 (Jellyfish Plume)
                if (alt > 35.0 && alt < 130.0) {{
                    const jProg = Math.sin(((alt - 35.0) / 95.0) * Math.PI);
                    jellyfishPlume.material.opacity = jProg * 0.55;
                    jellyfishPlume.scale.set(vacExp * 1.6, vacExp * 2.8, vacExp * 1.6);
                }} else {{
                    jellyfishPlume.material.opacity = 0.0;
                }}

                // 上昇中のスモークトレイル（大気圏内での長大な航跡）
                if (alt < 35.0) {{
                    const ux = Math.sin(pitch), uy = Math.cos(pitch);
                    for(let k=0; k<2; k++) {{
                        emitSmoke(rx - ux * 2.0, ry - uy * 2.0, 0, -ux * 0.5 + (Math.random()-0.5)*0.2, -uy * 0.5, (Math.random()-0.5)*0.2, 2.5, 14.0, 48, 0.75);
                    }}
                }}
            }} else if (!p0.exploded) {{
                plume.visible = false;
            }}

            // スモーク更新
            for(let i=0; i<P_MAX; i++) {{
                const p = pool[i]; if (!p.active) continue;
                p.age++;
                if (p.age >= p.maxAge) {{ p.active = false; p.sp.visible = false; continue; }}
                p.sp.position.x += p.vx; p.sp.position.y += p.vy; p.sp.position.z += p.vz;
                const pr = p.age / p.maxAge;
                p.sp.scale.set(p.s0 + (p.s1 - p.s0)*pr, p.s0 + (p.s1 - p.s0)*pr, 1);
                p.sp.material.opacity = p.o * (1.0 - pr * pr);
            }}

            document.getElementById('tv-spd').innerText = Math.round(vel * 3.6).toLocaleString();
            document.getElementById('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            document.getElementById('tv-q').innerText   = q.toFixed(1);
            if (!p0.exploded) {{
                document.getElementById('tv-stage-badge').innerText = p0.stage === 1 ? "STAGE 1 BOOSTER" : "STAGE 2 VACUUM";
            }}

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
    components.html(html_code, height=920)

# =========================================================================
# 📊 フライト解析レポート
# =========================================================================
if simulation_executed:
    st.markdown("---")
    st.markdown("### 📋 フライトテレメトリ詳細レポート")
    if error_msg:
        st.error(f"⚠️ **ミッション失敗 (RUD / 異常事態)**: {error_msg}")
    else:
        st.success("🎉 **ミッション完全成功**: 全ステージの燃焼・分離シーケンスが完璧に推移し、第2段オービターが低軌道（LEO）投入に到達しました。")
