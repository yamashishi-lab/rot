import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect Extreme: 4K Photorealistic Webcast", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect Extreme - 4K実写級航空宇宙シミュレーター")
st.markdown("PBR金属反射シェーダー、流体ボリューメトリック排気プルーム、Starbase/LC-39A級発射施設、高精細RUD破壊力学エンジン搭載。")

# =========================================================================
# 🔬 推進剤・材料・空力パーツ・魔改造データベース
# =========================================================================
PROPELLANTS = {
    "超高密度メタロックス (CH4 / LOX) [王道FFSC]": {
        "base_isp_sl": 335, "base_isp_vac": 380, "base_thrust": 2750, "density": 0.83, 
        "flame_hex": 0x38bdf8, "outer_hex": 0x0284c7, "risk": 0.0, "type": "methalox"
    },
    "高精製ケロシン (RP-1 / LOX) [ヘビーリフト]": {
        "base_isp_sl": 298, "base_isp_vac": 330, "base_thrust": 1450, "density": 1.02, 
        "flame_hex": 0xffedd5, "outer_hex": 0xea580c, "risk": 0.0, "type": "rp1"
    },
    "超極低温ハイドロロックス (LH2 / LOX) [究極真空比推力]": {
        "base_isp_sl": 380, "base_isp_vac": 470, "base_thrust": 1400, "density": 0.32, 
        "flame_hex": 0xfbcfe8, "outer_hex": 0xdb2777, "risk": 0.02, "type": "hydro"
    },
    "【猛毒】赤煙硝酸 ＋ UDMH [即自発火ハイパーゴリック]": {
        "base_isp_sl": 285, "base_isp_vac": 318, "base_thrust": 1950, "density": 1.25, 
        "flame_hex": 0xf5d0fe, "outer_hex": 0x9333ea, "risk": 0.05, "type": "hypergolic"
    },
    "【核熱】固体コア型原子力熱ロケット (NERVA / H2)": {
        "base_isp_sl": 420, "base_isp_vac": 900, "base_thrust": 2400, "density": 0.28, 
        "flame_hex": 0x86efac, "outer_hex": 0x16a34a, "risk": 0.15, "type": "nuclear"
    },
    "【禁忌】ダークマター濃縮スラリー [不安定特異点]": {
        "base_isp_sl": 880, "base_isp_vac": 1250, "base_thrust": 6800, "density": 1.85, 
        "flame_hex": 0xe9d5ff, "outer_hex": 0x6b21a8, "risk": 0.45, "type": "darkmatter"
    }
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [極限高圧]": {"isp_mod": 1.06, "thrust_mod": 1.40, "mass_mod": 1.25, "max_pressure_limit": 360},
    "二段燃焼サイクル (SC) [高出力信頼性]": {"isp_mod": 1.02, "thrust_mod": 1.15, "mass_mod": 1.18, "max_pressure_limit": 285},
    "ガス発生器サイクル (GG) [軽量堅牢]": {"isp_mod": 0.96, "thrust_mod": 0.95, "mass_mod": 0.85, "max_pressure_limit": 185},
    "リニアエアロスパイク方式 [全高度最適膨張]": {"isp_mod": 1.08, "thrust_mod": 1.05, "mass_mod": 1.35, "max_pressure_limit": 240},
    "【手動】人力足漕ぎペダル式タービン [超軽量・推力激減]": {"isp_mod": 0.30, "thrust_mod": 0.15, "mass_mod": 0.20, "max_pressure_limit": 80}
}

MATERIALS = {
    "Austenitic 304L 冷間圧延鏡面ステンレス": {"base_dry_ratio": 0.068, "max_q_base": 125.0, "max_g_base": 12.0, "mat_id": "ss"},
    "航空宇宙用 Al-Li-2195 アルミリチウム合金 [白色防熱塗工]": {"base_dry_ratio": 0.052, "max_q_base": 75.0, "max_g_base": 8.5, "mat_id": "al"},
    "高弾性トレカ炭素繊維複合材 (CFRP) [マットブラック]": {"base_dry_ratio": 0.038, "max_q_base": 60.0, "max_g_base": 7.0, "mat_id": "cf"},
    "超耐熱インコネル718 モノコック [重装甲]": {"base_dry_ratio": 0.095, "max_q_base": 180.0, "max_g_base": 16.0, "mat_id": "inconel"},
    "【DIY】防腐処理済み米松ツーバイフォー材 [超重量]": {"base_dry_ratio": 0.165, "max_q_base": 40.0, "max_g_base": 4.5, "mat_id": "wood"}
}

STRAPON_BOOSTERS = {
    "なし (単段コアブースター)": {"count": 0, "thrust_add": 0.0, "mass_add": 0.0, "fuel_add": 0.0, "isp_sl": 0, "type": "none"},
    "液体LRB × 2基 (Falcon Heavy風 サイドブースター)": {"count": 2, "thrust_add": 5500.0, "mass_add": 52.0, "fuel_add": 800.0, "isp_sl": 310, "type": "lrb"},
    "超巨大SRB × 4基 (SLS風 高推力固体ブースター)": {"count": 4, "thrust_add": 14000.0, "mass_add": 110.0, "fuel_add": 1400.0, "isp_sl": 275, "type": "srb"},
    "【危険】超高圧メガ花火ロケット × 8基クラスタ": {"count": 8, "thrust_add": 3200.0, "mass_add": 12.0, "fuel_add": 80.0, "isp_sl": 190, "type": "firework"}
}

AERO_WINGS = {
    "チタン鍛造極超音速グリッドフィン × 4基 (大気再突入姿勢制御)": {"lift_coeff": 0.12, "drag_penalty": 1.05, "mass": 1.2, "flutter_mach": 99.0, "wing_id": "grid"},
    "なし (純粋な軸対称弾道弾体)": {"lift_coeff": 0.0, "drag_penalty": 1.0, "mass": 0.0, "flutter_mach": 99.0, "wing_id": "none"},
    "超音速可変後退翼 (翼胴一体チタンウェッジ)": {"lift_coeff": 0.95, "drag_penalty": 1.45, "mass": 7.5, "flutter_mach": 3.4, "wing_id": "delta_wing"},
    "高アスペクト比カーボン製グライダー主翼": {"lift_coeff": 2.2, "drag_penalty": 3.2, "mass": 14.0, "flutter_mach": 0.85, "wing_id": "glider"}
}

FAIRINGS = {
    "バイコニカル炭素複合材クラムシェル (耐熱2,600K)": {"mass": 2.1, "cd": 0.18, "heat_limit": 2600, "shape_id": "biconic"},
    "有人カプセル ＋ 緊急脱出アボートタワー (LES)": {"mass": 6.8, "cd": 0.32, "heat_limit": 3000, "shape_id": "abort_tower"},
    "骨格露出型スケルトン・耐圧ケージ (内部ペイロード透視)": {"mass": 1.5, "cd": 0.45, "heat_limit": 1400, "shape_id": "skeleton"},
    "極超音速ペネトレーターニードル (超低ドラッグ)": {"mass": 1.3, "cd": 0.14, "heat_limit": 1900, "shape_id": "needle"}
}

# =========================================================================
# 🎛️ パラメータ設定タブ
# =========================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 第1段 (コア＆ブースター群)", 
    "🛩️ 空力フィン・魔改造アドオン", 
    "🛰️ 第2段 (オービター) & 先端部", 
    "📐 ガイダンス＆スロットル制御"
])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### コア推進系")
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=0)
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", list(PUMP_CYCLES.keys()), index=0)
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, 9)
    with c2:
        st.markdown("#### 燃焼室 & ノズル")
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, 290, step=10)
        s1_eps = st.slider("海面膨張比 (ε)", 8, 70, 24, step=1)
        strapon_opt = st.selectbox("外部追加ブースター (魔改造クラスタ)", list(STRAPON_BOOSTERS.keys()), index=0)
    with c3:
        st.markdown("#### タンク構造・素材")
        s1_fuel = st.slider("第1段 推進剤充填量 (トン)", 100.0, 4500.0, 1100.0, step=50.0)
        s1_mat = st.selectbox("第1段 構造素材", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("外殻等価板厚 (mm)", 1.0, 12.0, 4.2, step=0.1)

with tab2:
    st.markdown("#### 🚀 空力安定板・姿勢制御システム")
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 空力パーツ", list(AERO_WINGS.keys()), index=0)
        angle_of_attack = st.slider("固定取り付け角迎角 AoA (deg)", -3.0, 12.0, 0.5, step=0.5)
    with c2:
        st.info("💡 **リアル空力警告**: 高アスペクト比主翼や過大迎角設定は、超音速遷移域（Mach 0.8〜1.3）で急激な衝撃波剥離・曲げモーメント破綻を誘発します。チタングリッドフィンは超音速域でも極めて高い安定性を維持します。")

with tab3:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 第2段 真空推進系")
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=0)
        s2_cycle = st.selectbox("第2段 ポンプ方式", list(PUMP_CYCLES.keys()), index=0)
        s2_eng_count = st.slider("真空特化ノズル基数", 1, 6, 1)
        s2_pc = st.slider("第2段 燃焼室圧 (bar)", 20, 350, 220, step=10)
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 30, 280, 150, step=5)
    with c2:
        st.markdown("#### 第2段 構造・タンク")
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 20.0, 1200.0, 280.0, step=10.0)
        s2_mat = st.selectbox("第2段 構造素材", list(MATERIALS.keys()), index=0)
        s2_thick = st.slider("第2段 壁厚 (mm)", 0.8, 8.0, 3.0, step=0.1)
    with c3:
        st.markdown("#### 先端フェアリング & ペイロード")
        fairing_type = st.selectbox("先端空力カウル / フェアリング", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 40.0, 180.0, 95.0, step=5.0)
        payload_mass = st.slider("投入衛星ペイロード質量 (トン)", 0.5, 120.0, 22.0, step=1.0)

with tab4:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 重力ターン 軌道投入プロファイル")
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.3, 15.0, 1.6, step=0.1)
        turn_end_alt = st.slider("水平重力ターン完了高度 (km)", 50.0, 250.0, 120.0, step=5.0)
        turn_exponent = st.slider("ターン曲率指数", 0.3, 2.0, 0.62, step=0.02)
    with c2:
        st.markdown("#### スロットル & Gリミッター")
        throttle_maxq = st.slider("Max-Q 領域 推力抑制 (%)", 30, 100, 75)
        max_g_limit_cut = st.slider("最大加速度リミッター (G)", 2.5, 12.0, 5.0, step=0.2)

# =========================================================================
# ⚙️ 物理性能演算 (Physics Breakdown)
# =========================================================================
def calc_stage_specs(prop_key, cycle_key, pc, eps, eng_count, fuel_mass, mat_key, thick):
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
    dry_ratio = mat["base_dry_ratio"] * density_penalty * thick_factor + 0.005
    eng_mass = (thrust_vac_per_eng / 750.0) * cyc["mass_mod"] * (1.0 + eps * 0.002) * eng_count
    dry_mass = fuel_mass * dry_ratio + eng_mass

    max_q_resistance = mat["max_q_base"] * (thick_factor ** 1.1)
    max_g_resistance = mat["max_g_base"] * (thick_factor ** 0.85)

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
strapon_spec = STRAPON_BOOSTERS[strapon_opt]

s1_spec = calc_stage_specs(s1_prop, s1_cycle, s1_pc, s1_eps, s1_eng_count, s1_fuel, s1_mat, s1_thick)
s2_spec = calc_stage_specs(s2_prop, s2_cycle, s2_pc, s2_eps, s2_eng_count, s2_fuel, s2_mat, s2_thick)

total_s2_wet = s2_fuel + s2_spec["dry_mass"] + payload_mass + fair_spec["mass"]
total_s1_wet = s1_fuel + s1_spec["dry_mass"] + wing_spec["mass"] + strapon_spec["mass_add"] + strapon_spec["fuel_add"] + total_s2_wet

total_liftoff_thrust = s1_spec["thrust_sl"] + strapon_spec["thrust_add"]
twr_init = total_liftoff_thrust / (total_s1_wet * 9.80665)
dv_s1 = s1_spec["isp_sl"] * 9.80665 * np.log(total_s1_wet / (total_s1_wet - s1_fuel - strapon_spec["fuel_add"]))
dv_s2 = s2_spec["isp_vac"] * 9.80665 * np.log(total_s2_wet / (s2_spec["dry_mass"] + payload_mass))
total_dv = dv_s1 + dv_s2

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("総離床重量 / 離床TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f} ({'離床可能' if twr_init >= 1.05 else '推力不足！轟沈確定'})")
m2.metric("総計算速度増分 (ΔV)", f"{total_dv:.0f} m/s", "LEO投入基準: 9,200 m/s")
m3.metric("構造限界動圧 / 耐G", f"{s1_spec['max_q']:.1f} kPa", f"耐G: {s1_spec['max_g']:.1f} G")
m4.metric("ブースター追加推力", f"+{strapon_spec['thrust_add']:.0f} kN", f"基数: {strapon_spec['count']} 基")

# =========================================================================
# 💥 物理シミュレーション & 破壊力学エンジン
# =========================================================================
def run_simulation():
    dt = 0.5
    g0 = 9.80665
    R_earth = 6371000.0

    x, y = 0.0, 0.0
    vx, vy = 0.0, 0.0
    stage = 1
    fuel_s1_rem = float(s1_fuel * 1000.0)
    fuel_strapon_rem = float(strapon_spec["fuel_add"] * 1000.0)
    fuel_s2_rem = float(s2_fuel * 1000.0)
    fairing_attached = True
    wings_attached = bool(wing_spec["wing_id"] != "none")
    strapon_attached = bool(strapon_spec["count"] > 0)

    history = []
    fail_reason = None

    for cd_step in range(20):
        t_cd = -10.0 + cd_step * 0.5
        pre_ignition = bool(t_cd >= -3.0)
        history.append({
            "t": float(t_cd), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "stage": 1, "fairing": True, "wings": wings_attached,
            "strapon": strapon_attached, "exploded": False, "explosion_type": "NONE",
            "thrust": pre_ignition, "pitch": 0.0, "mach": 0.0, "event": "COUNTDOWN"
        })

    maxq_passed = False
    supersonic_called = False

    if s1_spec["pc"] > s1_spec["pc_limit"]:
        fail_reason = f"ターボポンプ高圧プリバーナー破裂: 燃焼室圧 {s1_spec['pc']} bar が構造限界 {s1_spec['pc_limit']} bar を超過。"
        history.append({
            "t": 0.1, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 0.0,
            "stage": 1, "fairing": True, "wings": wings_attached, "strapon": strapon_attached,
            "exploded": True, "explosion_type": "PAD_OVERPRESSURE", "thrust": False,
            "pitch": 0.0, "mach": 0.0, "event": "RUD"
        })
        return history, fail_reason

    if s1_spec["fuel_risk"] > 0.3 and np.random.rand() < s1_spec["fuel_risk"]:
        fail_reason = "特異点崩壊: ダークマター濃縮スラリーが臨界暴走。発射台ごと事象の地平線へ爆縮。"
        history.append({
            "t": 0.2, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 0.0,
            "stage": 1, "fairing": True, "wings": wings_attached, "strapon": strapon_attached,
            "exploded": True, "explosion_type": "SINGULARITY", "thrust": False,
            "pitch": 0.0, "mach": 0.0, "event": "RUD"
        })
        return history, fail_reason

    for step in range(1600):
        t = float(step * dt)
        alt = float(y)
        alt_km = float(alt / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))
        mach = v / 340.0

        rho = float(1.225 * np.exp(-alt / 7400.0)) if alt < 140000 else 0.0
        q = float(0.5 * rho * (v**2) / 1000.0)

        if alt_km < turn_start_alt:
            target_pitch_deg = 90.0
        elif alt_km < turn_end_alt:
            prog = (alt_km - turn_start_alt) / (turn_end_alt - turn_start_alt)
            target_pitch_deg = 90.0 * (1.0 - (prog ** turn_exponent))
        else:
            target_pitch_deg = 0.0

        extra_pitch_deflection = 0.0
        wing_lift_force = 0.0
        if wings_attached and alt_km < 50.0 and rho > 0.003:
            wing_lift_force = 0.5 * rho * (v**2) * (wing_spec["lift_coeff"] * 24.0) * np.sin(np.radians(angle_of_attack))
            extra_pitch_deflection = (wing_lift_force / 12000.0) * (mach ** 1.3)
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
        strap_m = (strapon_spec["mass_add"] * 1000.0 + fuel_strapon_rem) if strapon_attached else 0.0

        if stage == 1:
            if fuel_strapon_rem > 0 and strapon_attached:
                strap_thrust = strapon_spec["thrust_add"] * 1000.0
                fuel_strapon_rem -= (strap_thrust / (strapon_spec["isp_sl"] * g0)) * dt
            elif strapon_attached and fuel_strapon_rem <= 0:
                strapon_attached = False
                cur_event = "BOOSTER_SEP"
                strap_thrust = 0.0
            else:
                strap_thrust = 0.0

            if fuel_s1_rem <= 0:
                stage = 2
                cur_event = "HOT_STAGING"
                thrust = 0.0
            else:
                cur_mass = float((s1_spec["dry_mass"] + s2_fuel + s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + w_mass + strap_m + fuel_s1_rem)
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s1_spec["isp_vac"] - (s1_spec["isp_vac"] - s1_spec["isp_sl"]) * atm_factor)
                thrust_core = float((s1_spec["thrust_vac"] - (s1_spec["thrust_vac"] - s1_spec["thrust_sl"]) * atm_factor) * 1000.0)

                if 8000 < alt < 17000:
                    thrust_core *= (throttle_maxq / 100.0)

                thrust = thrust_core + strap_thrust
                if thrust / (cur_mass * g0) > max_g_limit_cut:
                    thrust = max_g_limit_cut * cur_mass * g0

                mdot = thrust_core / (isp * g0)
                fuel_s1_rem -= mdot * dt

        if stage == 2:
            if fuel_s2_rem <= 0:
                thrust = 0.0
                cur_mass = float((s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass)
            else:
                cur_mass = float((s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + fuel_s2_rem)
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s2_spec["isp_vac"] - (s2_spec["isp_vac"] - s2_spec["isp_sl"]) * atm_factor)
                thrust = float((s2_spec["thrust_vac"] - (s2_spec["thrust_vac"] - s2_spec["thrust_sl"]) * atm_factor) * 1000.0)

                if thrust / (cur_mass * g0) > max_g_limit_cut:
                    thrust = max_g_limit_cut * cur_mass * g0

                mdot = thrust / (isp * g0)
                fuel_s2_rem -= mdot * dt

        dir_x = float(np.cos(pitch_rad))
        dir_y = float(np.sin(pitch_rad))

        drag_area = (13.0 * s1_spec["cd_mod"] * wing_spec["drag_penalty"]) if stage == 1 else (5.2 * s2_spec["cd_mod"])
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
                fail_reason = "離床推力不足 (TWR < 1.0): 自重を支えきれずオービタルランチマウント上で座屈・大爆発。"
                history.append({
                    "t": t, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0,
                    "stage": 1, "fairing": True, "wings": wings_attached, "strapon": strapon_attached,
                    "exploded": True, "explosion_type": "PAD_CRUSH", "thrust": False, "pitch": 0.0,
                    "mach": 0.0, "event": "RUD"
                })
                break
            ax, ay, vx, vy = 0.0, 0.0, 0.0, 0.0
            acc_g = 1.0
        else:
            ax = fx / cur_mass
            ay = fy / cur_mass
            acc_g = float(np.sqrt((thrust * dir_x + drag_x + lift_x)**2 + (thrust * dir_y + drag_y + lift_y)**2) / (cur_mass * g0))

        cur_spec = s1_spec if stage == 1 else s2_spec

        if wings_attached and mach > wing_spec["flutter_mach"] and rho > 0.04:
            fail_reason = f"主翼遷音速フラッター崩壊: マッハ {mach:.2f} の衝撃波干渉で主翼が破断し、液体酸素タンク外壁を直撃貫通。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": False, "strapon": strapon_attached,
                "exploded": True, "explosion_type": "WING_TEAR", "thrust": False, "pitch": visual_pitch,
                "mach": mach, "event": "RUD"
            })
            break

        if abs(extra_pitch_deflection) > 28.0 and q > 18.0:
            fail_reason = f"空力トリム破綻（ピッチ反転）: 過大な揚力モーメントにより機体が横滑りし、動圧 {q:.1f} kPa の剪断応力で空中分解。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached,
                "exploded": True, "explosion_type": "AERODYNAMIC_SNAP", "thrust": False, "pitch": visual_pitch,
                "mach": mach, "event": "RUD"
            })
            break

        if q > cur_spec["max_q"]:
            fail_reason = f"Max-Q 構造圧壊: 空力動圧 {q:.1f} kPa が外殻許容座屈応力 ({cur_spec['max_q']:.1f} kPa) を突破。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached,
                "exploded": True, "explosion_type": "STRUCTURAL_COLLAPSE", "thrust": False, "pitch": visual_pitch,
                "mach": mach, "event": "RUD"
            })
            break

        if acc_g > cur_spec["max_g"]:
            fail_reason = f"過大軸方向G圧砕: 加速度 {acc_g:.1f} G によりドーム隔壁が破断 ({cur_spec['max_g']:.1f} G 限界)。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached,
                "exploded": True, "explosion_type": "OVER_G", "thrust": False, "pitch": visual_pitch,
                "mach": mach, "event": "RUD"
            })
            break

        vx = float(vx + ax * dt)
        vy = float(vy + ay * dt)
        x = float(x + vx * dt)
        y = float(max(0.0, y + vy * dt))

        history.append({
            "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g,
            "stage": int(stage), "fairing": bool(fairing_attached), "wings": bool(wings_attached),
            "strapon": bool(strapon_attached), "exploded": False, "explosion_type": "NONE",
            "thrust": bool(thrust > 0), "pitch": visual_pitch, "mach": mach, "event": cur_event
        })

        if alt_km >= 160.0 and vx >= 7780.0 and abs(vy) < 400.0:
            history.append({
                "t": t + dt, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": 0.0,
                "stage": int(stage), "fairing": bool(fairing_attached), "wings": bool(wings_attached),
                "strapon": False, "exploded": False, "explosion_type": "NONE", "thrust": False,
                "pitch": visual_pitch, "mach": mach, "event": "ORBIT"
            })
            break

    if not fail_reason and history[-1]["event"] != "ORBIT":
        fail_reason = f"軌道速度未達（推進剤枯渇・大気圏再突入落下）。到達高度: {alt_km:.1f} km, 水平速度: {vx:.0f} m/s"

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

simulation_executed = False
traj_data = None
error_msg = None

if st.button("🔴 4K 光学トラッキング実写中継 ＆ 軌道投入シミュレーション開始", use_container_width=True, type="primary"):
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
        "wing_id": wing_spec["wing_id"],
        "strapon_type": strapon_spec["type"],
        "strapon_count": int(strapon_spec["count"])
    }

    traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
    cfg_json = json.dumps(rocket_visual_cfg)
    fail_msg_clean = (error_msg or "").replace('"', '\\"').replace("'", "\\'")

    html_code = f"""
    <div id="broadcast-frame" style="position: relative; width: 100%; height: 940px; background: #000104; border-radius: 8px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none;">
        <script>
            window.parent.document.getElementById('launch-viewport').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        </script>

        <div id="canvas-container" style="width: 100%; height: 100%; position: absolute; top: 0; left: 0;"></div>

        <!-- 光学フィルムグレイン＆ビネットオーバーレイ (実写望遠レンズ質感) -->
        <div style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; box-shadow: inset 0 0 130px rgba(0,0,0,0.85); z-index: 5;"></div>

        <!-- 放送中継トップバナー -->
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 48px; background: rgba(3, 7, 18, 0.88); backdrop-filter: blur(16px); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 10;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <span id="live-indicator" style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 12px #ef4444; animation: livePulse 1.4s infinite alternate;"></span>
                <span style="color: #ffffff; font-weight: 800; font-size: 13px; letter-spacing: 2px;">OFFICIAL 4K OPTICAL WEBCAST</span>
                <span style="color: rgba(255,255,255,0.2);">|</span>
                <span id="cam-tag" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; font-family: monospace;">OPTICS: LC-39A 2400mm LONG-RANGE TRACKER</span>
            </div>
            <div style="display: flex; align-items: center; gap: 20px; font-family: monospace; font-size: 11px;">
                <span style="color: #94a3b8;">REGIME: <strong id="hud-regime" style="color: #f8fafc;">SEA LEVEL</strong></span>
                <span id="comm-status" style="color: #10b981;">TELEMETRY: NOMINAL</span>
            </div>
        </div>

        <style>@keyframes livePulse {{ from {{ opacity: 0.35; }} to {{ opacity: 1.0; }} }}</style>

        <!-- 🛰️ 軌道フライト HUD -->
        <div style="position: absolute; top: 60px; right: 24px; width: 280px; background: rgba(3, 7, 18, 0.85); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 4px; padding: 14px; z-index: 10; color: #fff;">
            <div style="font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 8px; display: flex; justify-content: space-between;">
                <span>DOWNRANGE TRAJECTORY</span>
                <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">0.0 km</span>
            </div>
            <canvas id="orbit-canvas" width="250" height="90" style="width: 100%; height: 90px; background: #01040d; border-radius: 2px;"></canvas>
            <div style="display: flex; justify-content: space-between; font-size: 9px; color: #64748b; margin-top: 6px; font-family: monospace;">
                <span>LAUNCH PAD</span><span>MAX-Q</span><span>MECO</span><span>ORBIT</span>
            </div>
        </div>

        <!-- 破壊アラート -->
        <div id="rud-banner" style="display: none; position: absolute; top: 170px; left: 50%; transform: translateX(-50%); background: rgba(120, 10, 10, 0.92); backdrop-filter: blur(16px); border: 2px solid #ef4444; border-radius: 4px; padding: 18px 32px; z-index: 25; text-align: center; box-shadow: 0 0 60px rgba(239, 68, 68, 0.7);">
            <div style="color: #fff; font-size: 18px; font-weight: 900; letter-spacing: 2.5px; font-family: monospace;">🚨 RAPID UNSCHEDULED DISASSEMBLY (RUD) 🚨</div>
            <div id="rud-desc" style="color: #fecaca; font-size: 13px; font-weight: 600; margin-top: 8px; max-width: 540px; line-height: 1.4;"></div>
        </div>

        <!-- 放送テレメトリー HUD -->
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(1, 3, 8, 0.98) 0%, rgba(2, 6, 14, 0.88) 75%, transparent 100%); padding: 28px 36px 20px 36px; box-sizing: border-box; display: flex; align-items: flex-end; justify-content: space-between; z-index: 10;">
            <div>
                <div id="tv-status" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 2px; margin-bottom: 2px;">MISSION CLOCK</div>
                <div id="tv-timer" style="color: #ffffff; font-size: 48px; font-weight: 900; font-family: 'Consolas', monospace; letter-spacing: 2px; text-shadow: 0 0 25px rgba(56, 189, 248, 0.4);">T- 00:10.0</div>
            </div>
            <div style="display: flex; gap: 40px; border-left: 1px solid rgba(255,255,255,0.15); padding-left: 36px;">
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">SPEED / MACH</div>
                    <div style="color: #fff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-mach">M 0.00</span> <span style="font-size: 12px; color: #94a3b8;" id="tv-spd">(0 km/h)</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">ALTITUDE</div>
                    <div style="color: #fff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-alt">0.0</span> <span style="font-size: 12px; color: #94a3b8;">km</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">DYNAMIC PRESSURE</div>
                    <div style="color: #fff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-q">0.0</span> <span style="font-size: 12px; color: #94a3b8;">kPa</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">AXIAL LOAD</div>
                    <div style="color: #fff; font-size: 26px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-g">1.0</span> <span style="font-size: 12px; color: #94a3b8;">G</span></div>
                </div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">VEHICLE STATE</div>
                    <div id="tv-stage-badge" style="color: #34d399; font-size: 20px; font-weight: 800; font-family: 'Consolas', monospace;">BOOSTER IG-SEQ</div>
                </div>
            </div>
        </div>

        <div id="flash-overlay" style="position: absolute; top:0; left:0; width:100%; height:100%; background:#fff5e6; opacity:0; pointer-events:none; z-index:30; transition:opacity 0.12s;"></div>
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

        // 音響合成エンジン (重低音クラックルノイズ + 大爆発サブベース)
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null, rumbleGain = null, crackleGain = null;
        function initAudio() {{
            if (!actx) {{
                actx = new AudioCtx();
                const buf = actx.createBuffer(1, actx.sampleRate * 2, actx.sampleRate);
                const d = buf.getChannelData(0);
                for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

                const rSrc = actx.createBufferSource(); rSrc.buffer = buf; rSrc.loop = true;
                const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 85;
                rumbleGain = actx.createGain(); rumbleGain.gain.value = 0;
                rSrc.connect(lp); lp.connect(rumbleGain); rumbleGain.connect(actx.destination);
                rSrc.start(0);

                const cSrc = actx.createBufferSource(); cSrc.buffer = buf; cSrc.loop = true;
                const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 680; bp.Q.value = 2.8;
                crackleGain = actx.createGain(); crackleGain.gain.value = 0;
                cSrc.connect(bp); bp.connect(crackleGain); crackleGain.connect(actx.destination);
                cSrc.start(0);
            }}
            if (actx.state === 'suspended') actx.resume();
        }}

        function playExplosionSound() {{
            if (!actx) return;
            if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.0, actx.currentTime, 0.05);
            if (crackleGain) crackleGain.gain.setTargetAtTime(0.0, actx.currentTime, 0.05);
            // 衝撃波ドン音 + 破片轟音
            const osc = actx.createOscillator();
            const g = actx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(110, actx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(12, actx.currentTime + 3.2);
            g.gain.setValueAtTime(1.2, actx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + 4.2);
            osc.connect(g); g.connect(actx.destination);
            osc.start(); osc.stop(actx.currentTime + 4.2);
        }}

        const voicedEvents = new Set();
        function announceWebcast(text) {{
            if (!('speechSynthesis' in window)) return;
            const u = new SpeechSynthesisUtterance(text);
            u.lang = 'en-US'; u.rate = 1.06; u.pitch = 0.92;
            window.speechSynthesis.speak(u);
        }}

        // =========================================================================
        // 🌍 Three.js シーン & 実写PBR環境マップ構築 (金属鏡面反射の核心)
        // =========================================================================
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(24, container.clientWidth / container.clientHeight, 0.5, 50000000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.15;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        // プロシージャルHDR環境マップ生成（これがないと金属がプラスチックに見える）
        const pmremGenerator = new THREE.PMREMGenerator(renderer);
        pmremGenerator.compileEquirectangularShader();
        const envCanvas = document.createElement('canvas');
        envCanvas.width = 512; envCanvas.height = 256;
        const ectx = envCanvas.getContext('2d');
        const envGrad = ectx.createLinearGradient(0, 0, 0, 256);
        envGrad.addColorStop(0.0, '#020617');
        envGrad.addColorStop(0.42, '#1e3a8a');
        envGrad.addColorStop(0.49, '#bae6fd');
        envGrad.addColorStop(0.51, '#fde047');
        envGrad.addColorStop(0.55, '#334155');
        envGrad.addColorStop(1.0, '#090d16');
        ectx.fillStyle = envGrad; ectx.fillRect(0, 0, 512, 256);
        // 太陽ハイライトスポット
        const sunGrad = ectx.createRadialGradient(380, 115, 2, 380, 115, 45);
        sunGrad.addColorStop(0, '#ffffff');
        sunGrad.addColorStop(1, 'rgba(255,255,255,0)');
        ectx.fillStyle = sunGrad; ectx.fillRect(0, 0, 512, 256);

        const envTex = new THREE.CanvasTexture(envCanvas);
        envTex.mapping = THREE.EquirectangularReflectionMapping;
        scene.environment = pmremGenerator.fromEquirectangular(envTex).texture;

        // 太陽光＆点火照り返しライト
        const sunLight = new THREE.DirectionalLight(0xfff9f0, 3.8);
        sunLight.position.set(4000, 7500, 5000);
        sunLight.castShadow = true;
        scene.add(sunLight);
        scene.add(new THREE.HemisphereLight(0x7dd3fc, 0x1e293b, 0.65));

        const engineBounceLight = new THREE.PointLight(cfg.flame_hex, 0.0, 220, 1.6);
        scene.add(engineBounceLight);

        // 恒星フィールド
        const starGeo = new THREE.BufferGeometry();
        const starPos = new Float32Array(4500 * 3);
        for(let i=0; i<4500*3; i+=3) {{
            const rad = 22000000;
            const u = Math.random(), v = Math.random();
            const th = u * 2.0 * Math.PI, ph = Math.acos(2.0 * v - 1.0);
            starPos[i] = rad * Math.sin(ph) * Math.cos(th);
            starPos[i+1] = rad * Math.sin(ph) * Math.sin(th);
            starPos[i+2] = rad * Math.cos(ph);
        }}
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        const starMat = new THREE.PointsMaterial({{ size: 1.5, color: 0xe2e8f0, transparent: true, opacity: 0.15 }});
        const stars = new THREE.Points(starGeo, starMat);
        scene.add(stars);

        // 実写地球テクスチャ＆レイリー大気散乱ドーム
        const texLoader = new THREE.TextureLoader();
        const R_EARTH = 6371.0;
        const earthMesh = new THREE.Mesh(
            new THREE.SphereGeometry(R_EARTH, 160, 120),
            new THREE.MeshStandardMaterial({{
                map: texLoader.load('https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/planets/earth_atmos_2048.jpg'),
                normalMap: texLoader.load('https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/planets/earth_normal_2048.jpg'),
                roughness: 0.68, metalness: 0.12
            }})
        );
        earthMesh.position.set(0, -R_EARTH, 0);
        earthMesh.rotation.y = -Math.PI * 0.62;
        earthMesh.rotation.x = 0.28;
        scene.add(earthMesh);

        const cloudMesh = new THREE.Mesh(
            new THREE.SphereGeometry(R_EARTH + 4.2, 96, 72),
            new THREE.MeshStandardMaterial({{
                map: texLoader.load('https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/planets/earth_clouds_1024.png'),
                transparent: true, opacity: 0.78, depthWrite: false
            }})
        );
        cloudMesh.position.set(0, -R_EARTH, 0);
        cloudMesh.rotation.copy(earthMesh.rotation);
        scene.add(cloudMesh);

        const atmoMat = new THREE.ShaderMaterial({{
            side: THREE.BackSide, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
            vertexShader: `
                varying vec3 vNormal; varying vec3 vWorldPos;
                void main() {{
                    vNormal = normalize(normalMatrix * normal);
                    vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }}
            `,
            fragmentShader: `
                varying vec3 vNormal; varying vec3 vWorldPos;
                void main() {{
                    vec3 viewDir = normalize(cameraPosition - vWorldPos);
                    float rim = max(0.0, dot(viewDir, -vNormal));
                    float intensity = pow(1.0 - rim, 2.8);
                    vec3 col = mix(vec3(0.12, 0.48, 0.96), vec3(0.98, 0.55, 0.22), pow(intensity, 3.0));
                    gl_FragColor = vec4(col, intensity * 0.92);
                }}
            `
        }});
        const atmoMesh = new THREE.Mesh(new THREE.SphereGeometry(R_EARTH + 95.0, 96, 72), atmoMat);
        atmoMesh.position.set(0, -R_EARTH, 0);
        scene.add(atmoMesh);

        // =========================================================================
        // 🏗️ 超精密 Starbase / LC-39A 発射複合施設 (OLM・メカジラ・配管・避雷針塔)
        // =========================================================================
        const pad = new THREE.Group();
        scene.add(pad);

        const darkSteelMat = new THREE.MeshStandardMaterial({{ color: 0x1e242b, metalness: 0.85, roughness: 0.35 }});
        const concreteMat = new THREE.MeshStandardMaterial({{ color: 0x374151, roughness: 0.9, metalness: 0.05 }});
        const pipeMat = new THREE.MeshStandardMaterial({{ color: 0xcbd5e1, metalness: 0.9, roughness: 0.25 }});
        const hazardMat = new THREE.MeshStandardMaterial({{ color: 0xeab308, roughness: 0.5, metalness: 0.3 }});

        // 1. 広大コンクリートパッド面 & フレイムトレンチ導水路
        const groundPlate = new THREE.Mesh(new THREE.CylinderGeometry(85, 95, 1.2, 64), concreteMat);
        groundPlate.position.y = -0.6; pad.add(groundPlate);

        const flameDeflector = new THREE.Mesh(new THREE.ConeGeometry(8.5, 5.5, 4), new THREE.MeshStandardMaterial({{ color: 0x111827, roughness: 0.8 }}));
        flameDeflector.position.set(0, 1.2, 0); flameDeflector.rotation.y = Math.PI / 4; pad.add(flameDeflector);

        // 2. 20本脚 オービタル・ランチ・マウント (OLM)
        const olmRing = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 3.5, 1.8, 32), darkSteelMat);
        olmRing.position.y = 5.2; pad.add(olmRing);
        for(let i=0; i<12; i++) {{
            const ang = (i / 12) * Math.PI * 2;
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.38, 5.2, 12), darkSteelMat);
            leg.position.set(Math.cos(ang)*2.8, 2.6, Math.sin(ang)*2.8);
            pad.add(leg);
        }}

        // 3. 146m級 インテグレーションタワー (Mechazilla トラス構造)
        const towerX = -8.5;
        const towerHeight = 44.0;
        for(let cx of [-2.2, 2.2]) {{
            for(let cz of [-2.2, 2.2]) {{
                const col = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.32, towerHeight, 12), darkSteelMat);
                col.position.set(towerX + cx, towerHeight/2, cz);
                pad.add(col);
            }}
        }}
        // トラス斜材クロスブレース段重ね
        for(let h = 2; h < towerHeight; h += 3.8) {{
            const frame = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.25, 4.6), darkSteelMat);
            frame.position.set(towerX, h, 0); pad.add(frame);
            const diag = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 6.2, 8), darkSteelMat);
            diag.position.set(towerX, h + 1.9, 2.2); diag.rotation.z = 0.82; pad.add(diag);
            const diag2 = diag.clone(); diag2.rotation.z = -0.82; diag2.position.z = -2.2; pad.add(diag2);
        }}

        // 4. チョップスティック (キャッチアーム) ＆ クイックディスコネクト (QD) アンビリカルアーム
        for(let zSide of [-1.4, 1.4]) {{
            const chopstick = new THREE.Mesh(new THREE.BoxGeometry(8.5, 0.55, 0.45), darkSteelMat);
            chopstick.position.set(towerX + 5.2, 28.5, zSide);
            pad.add(chopstick);
        }}
        const qdArm = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 6.8, 12), pipeMat);
        qdArm.rotation.z = Math.PI / 2; qdArm.position.set(towerX + 4.2, 16.5, 0); pad.add(qdArm);

        // 5. 極低温LOX/CH4 タンクファーム ＆ 4基の避雷針マスト
        for(let tIdx = 0; tIdx < 4; tIdx++) {{
            const cryoTank = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 11.0, 32), pipeMat);
            cryoTank.position.set(-28 - tIdx * 6.5, 5.5, -18); pad.add(cryoTank);
            const dome = new THREE.Mesh(new THREE.SphereGeometry(2.2, 32, 16), pipeMat);
            dome.position.set(-28 - tIdx * 6.5, 11.0, -18); pad.add(dome);
        }}
        for(let mAng of [0.6, 2.4, 3.9, 5.5]) {{
            const lMast = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.45, 52.0, 8), hazardMat);
            lMast.position.set(Math.cos(mAng)*42, 26.0, Math.sin(mAng)*42); pad.add(lMast);
        }}

        // =========================================================================
        // 🚀 超高精細・実機ディテールロケット構築 (リベット・TPS耐熱タイル・配管・Raptorベル)
        // =========================================================================
        function createHighDetailRocketTextures(matId, hasHeatshield) {{
            const w = 1024, h = 2048;
            const diffCvs = document.createElement('canvas'); diffCvs.width = w; diffCvs.height = h;
            const dctx = diffCvs.getContext('2d');
            const bumpCvs = document.createElement('canvas'); bumpCvs.width = w; bumpCvs.height = h;
            const bctx = bumpCvs.getContext('2d');

            // ベースカラー
            if (matId === 'ss') dctx.fillStyle = '#cbd5e1';
            else if (matId === 'cf') dctx.fillStyle = '#18181b';
            else if (matId === 'inconel') dctx.fillStyle = '#64748b';
            else if (matId === 'wood') dctx.fillStyle = '#92400e';
            else dctx.fillStyle = '#f8fafc';
            dctx.fillRect(0, 0, w, h);

            bctx.fillStyle = '#808080'; bctx.fillRect(0, 0, w, h);

            // 溶接リングシーム & アルミリチウムパネルの微妙な個体差トーン
            for(let y = 0; y < h; y += 64) {{
                const shade = (Math.random() - 0.5) * 14;
                dctx.fillStyle = `rgba(${{shade>0?255:0}}, ${{shade>0?255:0}}, ${{shade>0?255:0}}, ${{Math.abs(shade)/255}})`;
                dctx.fillRect(0, y, w, 62);
                // 溶接ビード凹み
                bctx.fillStyle = '#404040'; bctx.fillRect(0, y, w, 3);
                bctx.fillStyle = '#b0b0b0'; bctx.fillRect(0, y+3, w, 2);
                dctx.fillStyle = 'rgba(0,0,0,0.32)'; dctx.fillRect(0, y, w, 2);
            }}

            // 縦方向ストリンガー & リベット列
            for(let x = 0; x < w; x += 64) {{
                bctx.fillStyle = '#606060'; bctx.fillRect(x, 0, 2, h);
                dctx.fillStyle = 'rgba(0,0,0,0.12)'; dctx.fillRect(x, 0, 2, h);
            }}

            // 第2段片側 六角形セラミック耐熱タイル (Starship風ブラックTPSシールド)
            if (hasHeatshield) {{
                dctx.fillStyle = '#111317';
                dctx.fillRect(0, 0, w * 0.48, h);
                bctx.strokeStyle = '#202020'; bctx.lineWidth = 2;
                for(let ty = 0; ty < h; ty += 16) {{
                    for(let tx = 0; tx < w * 0.48; tx += 16) {{
                        bctx.strokeRect(tx + (ty%32===0?0:8), ty, 15, 15);
                    }}
                }}
            }}

            // 下部エンジンスートの煤汚れグラデーション
            const sootGrad = dctx.createLinearGradient(0, h * 0.75, 0, h);
            sootGrad.addColorStop(0, 'rgba(15, 18, 22, 0)');
            sootGrad.addColorStop(1, 'rgba(10, 12, 16, 0.72)');
            dctx.fillStyle = sootGrad; dctx.fillRect(0, h * 0.75, w, h * 0.25);

            return {{
                map: new THREE.CanvasTexture(diffCvs),
                bumpMap: new THREE.CanvasTexture(bumpCvs)
            }};
        }}

        const rocket = new THREE.Group();
        rocket.position.y = 6.0;
        scene.add(rocket);

        const s1Maps = createHighDetailRocketTextures(cfg.s1_mat, false);
        const s2Maps = createHighDetailRocketTextures(cfg.s2_mat, true);

        const s1Mat = new THREE.MeshStandardMaterial({{
            map: s1Maps.map, bumpMap: s1Maps.bumpMap, bumpScale: 0.035,
            metalness: (cfg.s1_mat === 'ss' || cfg.s1_mat === 'inconel') ? 0.92 : 0.28,
            roughness: (cfg.s1_mat === 'ss') ? 0.18 : 0.42
        }});
        const s2Mat = new THREE.MeshStandardMaterial({{
            map: s2Maps.map, bumpMap: s2Maps.bumpMap, bumpScale: 0.04,
            metalness: (cfg.s2_mat === 'ss' || cfg.s2_mat === 'inconel') ? 0.88 : 0.30,
            roughness: (cfg.s2_mat === 'ss') ? 0.20 : 0.45
        }});

        // 1. 第1段コア胴体 + チャイン（空力フェアリングカバー）+ 外部LOXフィードライン配管
        const s1Len = 18.0;
        const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, 64), s1Mat);
        s1Body.position.y = s1Len / 2; rocket.add(s1Body);

        // 外部レースウェイ＆極低温フィードパイプ＆COPV高圧ヘリウムボトル群
        for(let side of [-1, 1]) {{
            const chine = new THREE.Mesh(new THREE.BoxGeometry(0.24, s1Len * 0.94, 0.32), s1Mat);
            chine.position.set(side * 1.12, s1Len * 0.48, 0); rocket.add(chine);

            const loxPipe = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, s1Len * 0.88, 16), pipeMat);
            loxPipe.position.set(0, s1Len * 0.46, side * 1.14); rocket.add(loxPipe);
        }}

        // エンジンセクション保護スカートリング & RCSコールドガススラスターポッド
        const skirtRing = new THREE.Mesh(new THREE.CylinderGeometry(1.18, 1.22, 1.8, 64), darkSteelMat);
        skirtRing.position.y = 0.9; rocket.add(skirtRing);

        // 2. ホットステージング・ベント付きインターステージ (精密メッシュスリット構造)
        const interLen = 2.2;
        const interstage = new THREE.Group();
        interstage.position.y = s1Len + interLen / 2;
        rocket.add(interstage);
        const interRingTop = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, 0.35, 64), darkSteelMat);
        interRingTop.position.y = interLen/2 - 0.17; interstage.add(interRingTop);
        const interRingBot = interRingTop.clone(); interRingBot.position.y = -interLen/2 + 0.17; interstage.add(interRingBot);
        for(let i=0; i<24; i++) {{
            const a = (i / 24) * Math.PI * 2;
            const strut = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, interLen, 8), darkSteelMat);
            strut.position.set(Math.cos(a)*1.1, 0, Math.sin(a)*1.1);
            strut.rotation.z = (i%2 === 0) ? 0.18 : -0.18;
            interstage.add(strut);
        }}

        // 3. 第2段オービター胴体
        const s2Len = 9.0;
        const s2BaseY = s1Len + interLen;
        const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, 64), s2Mat);
        s2Body.position.y = s2BaseY + s2Len / 2; rocket.add(s2Body);

        // 4. 旋盤加工(LatheGeometry)による流線型タンジェント・オジーブ・ノーズコーン
        const noseY = s2BaseY + s2Len;
        const fairingGroup = new THREE.Group();
        fairingGroup.position.y = noseY;
        rocket.add(fairingGroup);

        const ogivePts = [];
        const noseH = 5.4;
        for(let i=0; i<=30; i++) {{
            const t = i / 30;
            const y = t * noseH;
            const r = 1.12 * Math.pow(1.0 - Math.pow(t, 1.65), 0.72);
            ogivePts.push(new THREE.Vector2(Math.max(0.01, r), y));
        }}
        const ogiveGeo = new THREE.LatheGeometry(ogivePts, 64);

        if (cfg.fairing_shape === 'abort_tower') {{
            const capsule = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 1.12, 2.4, 48), s2Mat);
            capsule.position.y = 1.2; fairingGroup.add(capsule);
            const lesTower = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.22, 4.2, 24), new THREE.MeshStandardMaterial({{ color: 0xf8fafc, metalness: 0.5 }}));
            lesTower.position.y = 4.2; fairingGroup.add(lesTower);
            for(let k=0; k<4; k++) {{
                const a = (k/4)*Math.PI*2;
                const thr = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.7, 16), hazardMat);
                thr.position.set(Math.cos(a)*0.22, 5.2, Math.sin(a)*0.22); thr.rotation.z = Math.cos(a)*0.4;
                fairingGroup.add(thr);
            }}
        }} else {{
            const noseMesh = new THREE.Mesh(ogiveGeo, s2Mat);
            fairingGroup.add(noseMesh);
            // 前方フラップ（カナード）ディテール
            for(let side of [-1, 1]) {{
                const fwdFlap = new THREE.Mesh(new THREE.BoxGeometry(0.85, 2.1, 0.08), darkSteelMat);
                fwdFlap.position.set(side * 1.15, 2.2, 0);
                fwdFlap.rotation.z = side * 0.22;
                fairingGroup.add(fwdFlap);
            }}
        }}

        // 5. 再生冷却チャンネル付き リアル・パラボラ・エンジンベルノズル群
        const nozzlePts = [];
        for(let i=0; i<=16; i++) {{
            const t = i / 16;
            const ny = -t * 1.25;
            const nr = 0.09 + 0.24 * Math.pow(t, 0.65);
            nozzlePts.push(new THREE.Vector2(nr, ny));
        }}
        const realBellGeo = new THREE.LatheGeometry(nozzlePts, 32);
        const inconelNozzleMat = new THREE.MeshStandardMaterial({{
            color: 0x3f3f46, metalness: 0.95, roughness: 0.25, side: THREE.DoubleSide
        }});

        function buildRealEngineCluster(parent, count, radius, basePosY) {{
            const group = new THREE.Group();
            group.position.y = basePosY;
            for(let i=0; i<count; i++) {{
                const ang = (i / count) * Math.PI * 2;
                const r = (count === 1) ? 0 : (i < 3 && count > 6 ? radius * 0.38 : radius);
                const bell = new THREE.Mesh(realBellGeo, inconelNozzleMat);
                bell.position.set(Math.cos(ang)*r, 0, Math.sin(ang)*r);
                // ターボポンプマニホールドリング
                const manifold = new THREE.Mesh(new THREE.TorusGeometry(0.16, 0.035, 8, 20), pipeMat);
                manifold.rotation.x = Math.PI / 2; manifold.position.y = -0.25;
                bell.add(manifold);
                group.add(bell);
            }}
            parent.add(group);
        }}
        buildRealEngineCluster(rocket, cfg.s1_eng, 0.78, 0.0);

        // 6. 外部ストラップオンブースター
        const straponGroup = new THREE.Group();
        rocket.add(straponGroup);
        if (cfg.strapon_count > 0) {{
            const sCount = cfg.strapon_count;
            for(let i=0; i<sCount; i++) {{
                const angle = (i / sCount) * Math.PI * 2;
                const bx = Math.cos(angle) * 2.05, bz = Math.sin(angle) * 2.05;
                const bLen = 15.5;
                const bUnit = new THREE.Group();
                bUnit.position.set(bx, 0, bz);

                const bBody = new THREE.Mesh(new THREE.CylinderGeometry(0.72, 0.72, bLen, 48), s1Mat);
                bBody.position.y = bLen / 2; bUnit.add(bBody);

                const bNose = new THREE.Mesh(ogiveGeo, s1Mat);
                bNose.scale.set(0.64, 0.55, 0.64); bNose.position.y = bLen; bUnit.add(bNose);

                // ブースター結合ストラット
                const strutTop = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.2, 8), darkSteelMat);
                strutTop.rotation.z = Math.PI/2; strutTop.position.set(-Math.cos(angle)*0.6, bLen*0.8, -Math.sin(angle)*0.6);
                bUnit.add(strutTop);

                const bBell = new THREE.Mesh(realBellGeo, inconelNozzleMat);
                bBell.scale.set(1.5, 1.3, 1.5); bUnit.add(bBell);
                straponGroup.add(bUnit);
            }}
        }}

        // 7. チタン鍛造ワッフル・グリッドフィン ＆ 空力主翼
        const wingsGroup = new THREE.Group();
        rocket.add(wingsGroup);
        if (cfg.wing_id === 'grid') {{
            for(let i=0; i<4; i++) {{
                const ang = (i / 4) * Math.PI * 2 + Math.PI / 4;
                const gfFrame = new THREE.Group();
                gfFrame.position.set(Math.cos(ang)*1.22, s1Len - 1.1, Math.sin(ang)*1.22);
                gfFrame.rotation.y = -ang;
                // アクチュエータ基部マウント
                const mount = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.65, 0.35), darkSteelMat);
                gfFrame.add(mount);
                // チタン格子フィン本体
                const gridBox = new THREE.Mesh(new THREE.BoxGeometry(0.95, 0.12, 1.15), new THREE.MeshStandardMaterial({{ color: 0x64748b, metalness: 0.9, roughness: 0.35, wireframe: true }}));
                gridBox.position.x = 0.55;
                gfFrame.add(gridBox);
                wingsGroup.add(gfFrame);
            }}
        }} else if (cfg.wing_id === 'delta_wing') {{
            for(let side of [-1, 1]) {{
                const wing = new THREE.Mesh(new THREE.BoxGeometry(4.5, 5.5, 0.14), darkSteelMat);
                wing.position.set(side * 2.8, s1Len * 0.35, 0);
                wing.rotation.z = side * 0.42;
                wingsGroup.add(wing);
            }}
        }}

        // =========================================================================
        // 🔥 逆三角形ポリゴン完全撤廃！流体GLSLシェーダーによるリアル・ショックダイヤモンド＆排気プルーム
        // =========================================================================
        const plumeGroup = new THREE.Group();
        rocket.add(plumeGroup);

        const plumeShaderMat = new THREE.ShaderMaterial({{
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            side: THREE.DoubleSide,
            uniforms: {{
                uTime: {{ value: 0.0 }},
                uVacFactor: {{ value: 0.0 }},
                uCoreColor: {{ value: new THREE.Color(0xffffff) }},
                uMidColor: {{ value: new THREE.Color(cfg.flame_hex) }},
                uOuterColor: {{ value: new THREE.Color(cfg.outer_hex) }}
            }},
            vertexShader: `
                varying vec2 vUv;
                uniform float uTime;
                uniform float uVacFactor;
                void main() {{
                    vUv = uv;
                    vec3 pos = position;
                    // 下流に向かうほど真空膨張で自然なベル型に広がる（逆三角形にならない流体境界層）
                    float dist = 1.0 - uv.y;
                    float bellExpand = pow(dist, 0.65) * (1.0 + uVacFactor * 3.8);
                    float turb = sin(dist * 28.0 - uTime * 55.0) * 0.08 * dist;
                    pos.x *= (1.0 + bellExpand + turb);
                    pos.z *= (1.0 + bellExpand + turb);
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
                }}
            `,
            fragmentShader: `
                varying vec2 vUv;
                uniform float uTime;
                uniform float uVacFactor;
                uniform vec3 uCoreColor;
                uniform vec3 uMidColor;
                uniform vec3 uOuterColor;

                void main() {{
                    float distFromNozzle = 1.0 - vUv.y;
                    float radial = abs(vUv.x - 0.5) * 2.0;

                    // 超音速マッハ・ショックダイヤモンド定在波パターン
                    float waveFreq = 22.0 / (1.0 + uVacFactor * 1.5);
                    float shockWave = pow(max(0.0, cos(distFromNozzle * waveFreq - uTime * 18.0)), 6.0);
                    float shockFade = max(0.0, 1.0 - uVacFactor * 1.4) * exp(-distFromNozzle * 2.6);

                    // 中心軸の温度勾配（エッジのパキッとした境界を完全に消すガウシアン減衰）
                    float coreMask = exp(-radial * radial * 9.0) * exp(-distFromNozzle * 1.8);
                    float plumeBody = exp(-radial * radial * 3.2) * pow(1.0 - distFromNozzle, 1.35);

                    // 高速乱流ノイズ
                    float noise = 0.88 + 0.12 * sin(distFromNozzle * 45.0 - uTime * 70.0 + radial * 12.0);

                    vec3 col = mix(uOuterColor, uMidColor, plumeBody);
                    col = mix(col, uCoreColor, clamp(coreMask + shockWave * shockFade * 0.85, 0.0, 1.0));

                    // ノズル直下と末端の両方を滑らかにフェードアウト
                    float tipFade = smoothstep(0.0, 0.04, distFromNozzle) * smoothstep(1.0, 0.15, distFromNozzle);
                    float alpha = clamp((plumeBody * 0.95 + coreMask * 0.8) * tipFade * noise, 0.0, 1.0);

                    gl_FragColor = vec4(col * 2.2, alpha);
                }}
            `
        }});

        // 3枚の直交ボリュームプレーン＋オープンチューブで全角度から立体的な流体ジェットを描画
        const plumeLen = 36.0;
        for(let rAngle of [0, Math.PI / 3, (2 * Math.PI) / 3]) {{
            const pPlane = new THREE.Mesh(new THREE.PlaneGeometry(3.2, plumeLen, 16, 64), plumeShaderMat);
            pPlane.position.y = -plumeLen / 2;
            pPlane.rotation.y = rAngle;
            plumeGroup.add(pPlane);
        }}
        // ノズル出口の強烈なブリリアント・グレア・スプライト
        const glareCvs = document.createElement('canvas'); glareCvs.width = 128; glareCvs.height = 128;
        const gctx = glareCvs.getContext('2d');
        const gg = gctx.createRadialGradient(64,64,2, 64,64,64);
        gg.addColorStop(0, 'rgba(255,255,255,1)');
        gg.addColorStop(0.25, 'rgba(180,230,255,0.85)');
        gg.addColorStop(1, 'rgba(0,120,255,0)');
        gctx.fillStyle = gg; gctx.fillRect(0,0,128,128);
        const engineGlare = new THREE.Sprite(new THREE.SpriteMaterial({{
            map: new THREE.CanvasTexture(glareCvs), blending: THREE.AdditiveBlending, depthWrite: false
        }}));
        engineGlare.scale.set(11.0, 6.5, 1.0);
        engineGlare.position.y = -0.8;
        plumeGroup.add(engineGlare);

        // =========================================================================
        // 💨 ボリューメトリック・パーティクルエンジン (水蒸気・黒煙・白熱火球・衝撃波リング)
        // =========================================================================
        function createOrganicCloudTexture() {{
            const c = document.createElement('canvas'); c.width = 128; c.height = 128;
            const ctx = c.getContext('2d');
            for(let i=0; i<7; i++) {{
                const ox = 64 + (Math.random()-0.5)*28;
                const oy = 64 + (Math.random()-0.5)*28;
                const rad = 32 + Math.random()*22;
                const g = ctx.createRadialGradient(ox, oy, 2, ox, oy, rad);
                g.addColorStop(0, 'rgba(255,255,255,0.35)');
                g.addColorStop(0.5, 'rgba(225,232,240,0.18)');
                g.addColorStop(1, 'rgba(160,175,190,0)');
                ctx.fillStyle = g; ctx.fillRect(0,0,128,128);
            }}
            return new THREE.CanvasTexture(c);
        }}

        const cloudTex = createOrganicCloudTexture();
        const P_MAX = 2200;
        const pool = [];
        const pGroup = new THREE.Group(); scene.add(pGroup);

        for(let i=0; i<P_MAX; i++) {{
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({{
                map: cloudTex, transparent: true, opacity: 0, depthWrite: false
            }}));
            sp.visible = false; pGroup.add(sp);
            pool.push({{
                sp, active: false, vx: 0, vy: 0, vz: 0,
                age: 0, maxAge: 1, s0: 1, s1: 5, o: 0.8, rotSpd: 0, mode: 'smoke'
            }});
        }}
        let pIdx = 0;

        function emitParticle(x, y, z, vx, vy, vz, s0, s1, life, opacity, hexColor, additive) {{
            const p = pool[pIdx]; pIdx = (pIdx + 1) % P_MAX;
            p.active = true; p.sp.visible = true;
            p.sp.position.set(x, y, z);
            p.vx = vx; p.vy = vy; p.vz = vz;
            p.age = 0; p.maxAge = life; p.s0 = s0; p.s1 = s1; p.o = opacity;
            p.rotSpd = (Math.random() - 0.5) * 0.06;
            p.sp.material.color.setHex(hexColor);
            p.sp.material.blending = additive ? THREE.AdditiveBlending : THREE.NormalBlending;
        }}

        // =========================================================================
        // 💥 超リアル RUD 爆発力学エンジン (衝撃波コンデンセーションリング + 多層火球 + 燃焼デブリ軌跡)
        // =========================================================================
        const shockwaveRing = new THREE.Mesh(
            new THREE.RingGeometry(0.8, 1.35, 64),
            new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.0, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false }})
        );
        shockwaveRing.visible = false;
        scene.add(shockwaveRing);

        const DEBRIS_MAX = 260;
        const debrisPool = [];
        const debrisGroup = new THREE.Group(); scene.add(debrisGroup);
        const debGeos = [
            new THREE.CylinderGeometry(0.6, 0.8, 1.6, 12, 1, true),
            new THREE.BoxGeometry(1.5, 0.12, 1.1),
            realBellGeo,
            new THREE.BoxGeometry(0.25, 2.4, 0.25)
        ];

        for(let i=0; i<DEBRIS_MAX; i++) {{
            const deb = new THREE.Mesh(debGeos[i % debGeos.length], (i%3===0) ? s1Mat : darkSteelMat);
            deb.visible = false; debrisGroup.add(deb);
            debrisPool.push({{ mesh: deb, active: false, vx: 0, vy: 0, vz: 0, rx: 0, ry: 0, rz: 0, isBurning: (i % 2 === 0) }});
        }}

        let shockwaveAge = 0;
        function triggerPhotorealRUD(x, y, vxBase, vyBase) {{
            // 1. 超音速膨張コンデンセーション・ショックウェーブリング起動
            shockwaveRing.visible = true;
            shockwaveRing.position.set(x, y + 8.0, 0);
            shockwaveRing.scale.set(1, 1, 1);
            shockwaveRing.material.opacity = 0.95;
            shockwaveAge = 1;

            // 2. 中心核の3,200K 白熱フラッシュ＆推進剤ハイパーゴリック火球 (Additive)
            for(let k=0; k<95; k++) {{
                const ang = Math.random() * Math.PI * 2;
                const phi = (Math.random() - 0.5) * Math.PI;
                const spd = 0.4 + Math.random() * 2.8;
                const col = (k < 25) ? 0xffffff : (k < 65 ? 0xff7700 : 0xdc2626);
                emitParticle(
                    x + (Math.random()-0.5)*5, y + 8 + (Math.random()-0.5)*10, (Math.random()-0.5)*5,
                    vxBase*0.02 + Math.cos(ang)*Math.cos(phi)*spd,
                    vyBase*0.02 + Math.sin(phi)*spd + 0.15,
                    Math.sin(ang)*Math.cos(phi)*spd,
                    8.0, 68.0, 55 + Math.random()*35, 0.95, col, true
                );
            }}

            // 3. 外周の極低温LOX気化白煙＆炭素スート黒煙クラウド (NormalBlending)
            for(let k=0; k<120; k++) {{
                const ang = Math.random() * Math.PI * 2;
                const spd = 0.5 + Math.random() * 3.4;
                const isSoot = (k % 2 === 0);
                emitParticle(
                    x + (Math.random()-0.5)*8, y + 8 + (Math.random()-0.5)*14, (Math.random()-0.5)*8,
                    vxBase*0.02 + Math.cos(ang)*spd,
                    vyBase*0.02 + (Math.random()-0.3)*spd,
                    (Math.random()-0.5)*spd,
                    12.0, 95.0, 110 + Math.random()*50, isSoot ? 0.88 : 0.75,
                    isSoot ? 0x18181b : 0xf1f5f9, false
                );
            }}

            // 4. 260個の構造破片＆白煙ストリーマー放出
            for(let i=0; i<DEBRIS_MAX; i++) {{
                const d = debrisPool[i];
                d.active = true; d.mesh.visible = true;
                d.mesh.position.set(x + (Math.random()-0.5)*4, y + 8 + (Math.random()-0.5)*14, (Math.random()-0.5)*4);
                const angle = Math.random() * Math.PI * 2;
                const spd = 6.0 + Math.random() * 28.0;
                d.vx = (vxBase * 0.04) + Math.cos(angle) * spd;
                d.vy = (vyBase * 0.04) + Math.sin(angle) * spd;
                d.vz = (Math.random() - 0.5) * spd * 1.6;
                d.rx = (Math.random()-0.5)*0.5; d.ry = (Math.random()-0.5)*0.5; d.rz = (Math.random()-0.5)*0.5;
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
        // 🎥 光学トラッキング望遠カメラ制御
        // =========================================================================
        const currentTargetPos = new THREE.Vector3(0, 18, 0);
        let camShake = 0.0;

        function updateGimbalTracker(simT, rx, ry, alt, pitch, exploded) {{
            const upX = Math.sin(pitch), upY = Math.cos(pitch);
            const targetX = rx + upX * 16.0;
            const targetY = ry + 6.0 + upY * 16.0;
            currentTargetPos.lerp(new THREE.Vector3(targetX, targetY, 0), 0.18);

            if (exploded) {{
                document.getElementById('cam-tag').innerText = "OPTICS: HIGH-SPEED DEBRIS TRACKING LOCK";
                camera.position.lerp(new THREE.Vector3(rx + 65, ry + 28, 145), 0.05);
            }} else if (simT < 0.0) {{
                document.getElementById('cam-tag').innerText = "PAD CAM 01: OLM & MECHAZILLA TELEPHOTO";
                camera.position.set(38.0, 16.0, 78.0);
            }} else if (simT < 4.0) {{
                document.getElementById('cam-tag').innerText = "PAD PERIMETER: TOWER CLEARANCE TRACKER";
                camera.position.lerp(new THREE.Vector3(-55.0, 22.0, 115.0), 0.06);
            }} else if (alt < 18.0) {{
                document.getElementById('cam-tag').innerText = "COASTAL KINETO TRACKER (2400mm APO)";
                const camDist = 115.0 + alt * 5.0;
                camera.position.lerp(new THREE.Vector3(rx - camDist * 0.55, Math.max(12.0, ry * 0.55), camDist * 0.85), 0.08);
            }} else if (alt < 85.0) {{
                document.getElementById('cam-tag').innerText = "WB-57 HIGH-ALTITUDE OPTICAL CHASE";
                const camDist = 195.0;
                camera.position.lerp(new THREE.Vector3(rx - camDist * 0.5, ry - 15.0, camDist * 0.85), 0.08);
            }} else {{
                document.getElementById('cam-tag').innerText = "ORBITAL INSERTION LONG-RANGE TELESCOPE";
                camera.position.lerp(new THREE.Vector3(rx - upX * 110.0, ry - upY * 110.0 + 15.0, 185.0), 0.09);
            }}

            if (camShake > 0.002) {{
                camera.position.x += (Math.random() - 0.5) * camShake;
                camera.position.y += (Math.random() - 0.5) * camShake;
                camShake *= 0.93;
            }}
            camera.lookAt(currentTargetPos);
        }}

        // =========================================================================
        // ⏱️ メインレンダリングループ
        // =========================================================================
        let tStart = performance.now();
        let explodedTriggered = false;

        function animate(now) {{
            requestAnimationFrame(animate);
            initAudio();

            const elapsedSec = (now - tStart) / 1000.0;
            const simT = -10.0 + elapsedSec;
            plumeShaderMat.uniforms.uTime.value = elapsedSec;

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
            const mach = p0.mach + (p1.mach - p0.mach) * a;
            const accG = p0.g + (p1.g - p0.g) * a;
            const dRangeKm = (rx * 10.0) / 1000.0;

            rocket.position.set(rx, ry + 6.0, 0);
            rocket.rotation.z = -pitch;

            // 高度に応じた星空の露出と第1段分離
            starMat.opacity = Math.min(0.95, 0.1 + (alt / 45.0) * 0.85);
            if (p0.strapon === false) straponGroup.visible = false;
            if (p0.stage === 2) {{
                s1Body.visible = false; skirtRing.visible = false; wingsGroup.visible = false;
            }}

            updateGimbalTracker(simT, rx, ry, alt, pitch, p0.exploded);
            drawOrbitMap(alt, dRangeKm, p0.exploded);

            // 💥 RUD 爆発トリガー
            if (p0.exploded && !explodedTriggered) {{
                explodedTriggered = true;
                rocket.visible = false;
                plumeGroup.visible = false;
                camShake = 2.4;
                flashOverlay.style.opacity = '0.95';
                setTimeout(() => {{ flashOverlay.style.opacity = '0.0'; }}, 140);

                playExplosionSound();
                triggerPhotorealRUD(rx, ry, p0.v * Math.cos(p0.pitch), p0.v * Math.sin(p0.pitch));

                rudBanner.style.display = 'block';
                rudDesc.innerText = failMessage;
                announceWebcast("Anomaly detected on the vehicle. Loss of telemetry.");
                document.getElementById('tv-stage-badge').innerText = "VEHICLE LOSS (RUD)";
                document.getElementById('tv-stage-badge').style.color = "#ef4444";
                document.getElementById('comm-status').innerText = "SIGNAL LOST";
                document.getElementById('comm-status').style.color = "#ef4444";
            }}

            // 衝撃波リングと燃焼デブリの物理更新
            if (explodedTriggered) {{
                if (shockwaveAge > 0 && shockwaveAge < 70) {{
                    shockwaveAge++;
                    const sScale = 1.0 + shockwaveAge * 2.2;
                    shockwaveRing.scale.set(sScale, sScale, 1);
                    shockwaveRing.lookAt(camera.position);
                    shockwaveRing.material.opacity = Math.max(0, 0.95 * (1.0 - shockwaveAge / 70.0));
                }} else {{
                    shockwaveRing.visible = false;
                }}

                for(let i=0; i<DEBRIS_MAX; i++) {{
                    const d = debrisPool[i]; if (!d.active) continue;
                    d.mesh.position.x += d.vx * 0.016;
                    d.mesh.position.y += d.vy * 0.016;
                    d.mesh.position.z += d.vz * 0.016;
                    d.vy -= 9.8 * 0.016 * 0.12;
                    d.mesh.rotation.x += d.rx; d.mesh.rotation.y += d.ry;
                    // デブリの炎＆白煙ストリーマー
                    if (Math.random() < 0.42) {{
                        emitParticle(
                            d.mesh.position.x, d.mesh.position.y, d.mesh.position.z,
                            (Math.random()-0.5)*0.08, (Math.random()-0.5)*0.08, (Math.random()-0.5)*0.08,
                            d.isBurning ? 1.5 : 2.2, d.isBurning ? 6.5 : 11.0, 35,
                            d.isBurning ? 0.75 : 0.45,
                            d.isBurning ? 0xf97316 : 0xe2e8f0, d.isBurning
                        );
                    }}
                }}
            }}

            // カウントダウン極低温ベント ＆ デリュージ水蒸気システム
            if (simT < 0.0) {{
                const sec = Math.ceil(Math.abs(simT));
                document.getElementById('tv-timer').innerText = `T- 00:0${{sec}}.0`;
                emitParticle(rx + 1.25, ry + 20.0, 0, 0.25, 0.04, 0, 0.9, 4.2, 45, 0.35, 0xffffff, false);

                if (simT >= -3.0 && !p0.exploded) {{
                    camShake = 0.25;
                    engineBounceLight.intensity = 6.0;
                    engineBounceLight.position.set(rx, ry + 3.0, 4.0);
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.7, actx.currentTime, 0.1);
                    for(let i=0; i<10; i++) {{
                        const side = (i%2 === 0) ? 1 : -1;
                        emitParticle(
                            rx + (Math.random()-0.5)*4, 1.5, (Math.random()-0.5)*4,
                            side * (1.1 + Math.random()*1.6), 0.12 + Math.random()*0.28, (Math.random()-0.5)*0.8,
                            4.5, 28.0, 68, 0.85, 0xf8fafc, false
                        );
                    }}
                }}
            }} else if (!p0.exploded) {{
                const m = Math.floor(simT / 60); const s = simT % 60;
                document.getElementById('tv-timer').innerText = `T+ ${{String(m).padStart(2,'0')}}:${{s.toFixed(1).padStart(4,'0')}}`;
                if (simT >= 0 && !voicedEvents.has('liftoff')) {{
                    voicedEvents.add('liftoff');
                    announceWebcast("Liftoff. Tower cleared.");
                    if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.95, actx.currentTime, 0.1);
                    if (crackleGain) crackleGain.gain.setTargetAtTime(0.55, actx.currentTime, 0.1);
                }}
            }}

            // 流体シェーダープルーム更新
            if (p0.thrust && !p0.exploded) {{
                plumeGroup.visible = true;
                const vacFactor = Math.min(1.0, alt / 65.0);
                plumeShaderMat.uniforms.uVacFactor.value = vacFactor;
                engineGlare.scale.set(11.0 + Math.sin(now*0.05)*1.8, 6.5, 1.0);
                engineBounceLight.intensity = Math.max(0.0, 5.5 - alt * 0.4);
                engineBounceLight.position.set(rx, ry + 2.0, 4.0);

                if (alt < 28.0) {{
                    const ux = Math.sin(pitch), uy = Math.cos(pitch);
                    emitParticle(
                        rx - ux * 6.0, ry + 6.0 - uy * 6.0, 0,
                        -ux * 0.55 + (Math.random()-0.5)*0.18, -uy * 0.55, (Math.random()-0.5)*0.18,
                        3.5, 22.0, 55, 0.65, 0xf1f5f9, false
                    );
                }}
            }} else if (!p0.exploded) {{
                plumeGroup.visible = false;
                engineBounceLight.intensity = 0.0;
            }}

            // パーティクル物理・回転・フェード更新
            for(let i=0; i<P_MAX; i++) {{
                const p = pool[i]; if (!p.active) continue;
                p.age++;
                if (p.age >= p.maxAge) {{ p.active = false; p.sp.visible = false; continue; }}
                p.sp.position.x += p.vx; p.sp.position.y += p.vy; p.sp.position.z += p.vz;
                p.sp.material.rotation += p.rotSpd;
                const pr = p.age / p.maxAge;
                const curScale = p.s0 + (p.s1 - p.s0) * Math.pow(pr, 0.7);
                p.sp.scale.set(curScale, curScale, 1);
                p.sp.material.opacity = p.o * (1.0 - pr * pr);
            }}

            let regime = "TROPOSPHERE";
            if (alt >= 100.0) regime = "THERMOSPHERE (VACUUM)";
            else if (alt >= 50.0) regime = "MESOSPHERE";
            else if (alt >= 12.0) regime = "STRATOSPHERE";
            document.getElementById('hud-regime').innerText = regime;
            document.getElementById('hud-downrange').innerText = `${{dRangeKm.toFixed(1)}} km`;

            document.getElementById('tv-mach').innerText = `M ${{mach.toFixed(2)}}`;
            document.getElementById('tv-spd').innerText = `(${{Math.round(vel * 3.6).toLocaleString()}} km/h)`;
            document.getElementById('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            document.getElementById('tv-q').innerText   = q.toFixed(1);
            document.getElementById('tv-g').innerText   = accG.toFixed(1);
            if (!p0.exploded) {{
                document.getElementById('tv-stage-badge').innerText = p0.stage === 1 ? (p0.strapon ? "STAGE 1 + BOOSTERS" : "STAGE 1 ASCENT") : "STAGE 2 ORBITAL";
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
    components.html(html_code, height=960)

# =========================================================================
# 📊 フライト解析レポート
# =========================================================================
if simulation_executed:
    st.markdown("---")
    st.markdown("### 📋 フライトテレメトリ詳細レポート")
    if error_msg:
        st.error(f"⚠️ **ミッション異常終了 (RUD)**: {error_msg}")
    else:
        st.success("🎉 **ミッション完全成功 (SECO & LEO Insertion)**: 全段燃焼および分離シーケンスが正常に推移し、第2段オービターが低軌道投入条件に到達しました。")
