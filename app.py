import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect Extreme: 4K Dual Photoreal Engine", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect Extreme - 4K実写デュアル中継＆航空宇宙物理シミュレーター")
st.caption("※ 外部通信ブロック完全対策済み自律レンダリングエンジン・圧縮GN2流体RCS・ケープカナベラルPBRランドスケープ・2画面同時中継")

# =========================================================================
# 🔬 推進剤・材料・空力パーツ・ブースターデータベース
# =========================================================================
PROPELLANTS = {
    "超高密度サブクール・メタロックス (CH4 / LOX) [Starship王道]": {
        "base_isp_sl": 338, "base_isp_vac": 382, "base_thrust": 2800, "density": 0.85, 
        "flame_hex": 0x38bdf8, "outer_hex": 0x1d4ed8, "spark_hex": 0x93c5fd, "risk": 0.0, "type": "methalox"
    },
    "高精製ケロシン (RP-1 / LOX) [Saturn V / Falcon]": {
        "base_isp_sl": 302, "base_isp_vac": 335, "base_thrust": 1950, "density": 1.03, 
        "flame_hex": 0xfde047, "outer_hex": 0xea580c, "spark_hex": 0xfbbf24, "risk": 0.0, "type": "rp1"
    },
    "超極低温ハイドロロックス (LH2 / LOX) [H3 / SLS]": {
        "base_isp_sl": 385, "base_isp_vac": 468, "base_thrust": 1450, "density": 0.34, 
        "flame_hex": 0xfbcfe8, "outer_hex": 0xbe185d, "spark_hex": 0xffffff, "risk": 0.01, "type": "hydro"
    },
    "【猛毒】四酸化二窒素 ＋ UDMH (N2O4 / UDMH) [Proton]": {
        "base_isp_sl": 288, "base_isp_vac": 322, "base_thrust": 2100, "density": 1.26, 
        "flame_hex": 0xf5d0fe, "outer_hex": 0x9333ea, "spark_hex": 0xfab1a0, "risk": 0.05, "type": "hypergolic"
    },
    "【核熱】固体炉心型原子力サーマルロケット (NERVA / LH2)": {
        "base_isp_sl": 450, "base_isp_vac": 925, "base_thrust": 2500, "density": 0.30, 
        "flame_hex": 0x86efac, "outer_hex": 0x14532d, "spark_hex": 0x4ade80, "risk": 0.12, "type": "nuclear"
    }
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [極限高圧]": {"isp_mod": 1.07, "thrust_mod": 1.42, "mass_mod": 1.22, "max_pressure_limit": 380, "cyc_id": "ffsc"},
    "酸化剤リッチ二段燃焼 (ORSC) [高出力信頼性]": {"isp_mod": 1.03, "thrust_mod": 1.25, "mass_mod": 1.18, "max_pressure_limit": 310, "cyc_id": "sc"},
    "ガス発生器サイクル (GG) [煤排気ダクト付]": {"isp_mod": 0.96, "thrust_mod": 0.98, "mass_mod": 0.84, "max_pressure_limit": 195, "cyc_id": "gg"},
    "リニアエアロスパイク方式 [全高度最適膨張]": {"isp_mod": 1.09, "thrust_mod": 1.10, "mass_mod": 1.32, "max_pressure_limit": 250, "cyc_id": "aerospike"}
}

MATERIALS = {
    "Austenitic 304L 冷間圧延鏡面ステンレス [Starship仕様]": {"base_dry_ratio": 0.065, "max_q_base": 130.0, "max_g_base": 12.5, "mat_id": "ss"},
    "航空宇宙用 Al-Li-2195 アルミリチウム合金 [SLSオレンジ塗装]": {"base_dry_ratio": 0.050, "max_q_base": 82.0, "max_g_base": 9.0, "mat_id": "al"},
    "Saturn V 伝統 ホワイト＆ブラック・ロールチェック塗工": {"base_dry_ratio": 0.054, "max_q_base": 88.0, "max_g_base": 9.5, "mat_id": "saturn"},
    "高弾性トレカ炭素繊維複合材 (CFRP) [マットブラック]": {"base_dry_ratio": 0.036, "max_q_base": 65.0, "max_g_base": 7.5, "mat_id": "cf"},
    "超耐熱インコネル718 モノコック [重装甲チタン調]": {"base_dry_ratio": 0.092, "max_q_base": 195.0, "max_g_base": 16.5, "mat_id": "inconel"}
}

STRAPON_BOOSTERS = {
    "なし (単段スリムコア構成)": {"count": 0, "thrust_add": 0.0, "mass_add": 0.0, "fuel_add": 0.0, "isp_sl": 0, "type": "none"},
    "Falcon Heavy風 液体LRB × 2基 (グリッドフィン付)": {"count": 2, "thrust_add": 5800.0, "mass_add": 50.0, "fuel_add": 820.0, "isp_sl": 315, "type": "lrb"},
    "Soyuz R-7風 テーパー液体ブースター × 4基 (コロリョフクロス専用)": {"count": 4, "thrust_add": 4200.0, "mass_add": 38.0, "fuel_add": 520.0, "isp_sl": 308, "type": "soyuz"},
    "SLS風 5セグメント超巨大SRB × 2基 (白塗装＆黒ジョイントリング)": {"count": 2, "thrust_add": 8800.0, "mass_add": 68.0, "fuel_add": 950.0, "isp_sl": 278, "type": "srb"}
}

AERO_WINGS = {
    "チタン鍛造極超音速グリッドフィン × 4基": {"lift_coeff": 0.12, "drag_penalty": 1.05, "mass": 1.2, "flutter_mach": 99.0, "wing_id": "grid"},
    "Starship風 空力エルロンボディフラップ × 4枚": {"lift_coeff": 0.35, "drag_penalty": 1.12, "mass": 2.8, "flutter_mach": 99.0, "wing_id": "starship_flap"},
    "なし (純粋な軸対称弾道ロケット)": {"lift_coeff": 0.0, "drag_penalty": 1.0, "mass": 0.0, "flutter_mach": 99.0, "wing_id": "none"},
    "コンコルド風 ダブルデルタ超音速後退翼": {"lift_coeff": 0.95, "drag_penalty": 1.45, "mass": 7.5, "flutter_mach": 3.8, "wing_id": "delta_wing"}
}

FAIRINGS = {
    "バイコニカル炭素複合材クラムシェル (金箔通信衛星内蔵)": {"mass": 2.1, "cd": 0.18, "heat_limit": 2600, "shape_id": "biconic"},
    "有人カプセル ＋ レスキューアボートタワー (LES付)": {"mass": 6.8, "cd": 0.32, "heat_limit": 3200, "shape_id": "abort_tower"},
    "Starship風 窓付き有人クルーノーズコーン": {"mass": 4.2, "cd": 0.22, "heat_limit": 2900, "shape_id": "starship_crew"}
}

# =========================================================================
# 🎛️ パラメータ設定タブ
# =========================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 第1段 & 外部ブースター", 
    "🛩️ 空力フィン & 姿勢制御", 
    "🛰️ 第2段 & フェアリング", 
    "📐 カウントダウン & 軌道投入プロファイル"
])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=0)
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", list(PUMP_CYCLES.keys()), index=0)
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, 9)
    with c2:
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, 290, step=10)
        s1_eps = st.slider("海面膨張比 (ε: ノズル径連動)", 8, 70, 24, step=1)
        strapon_opt = st.selectbox("外部追加ブースター", list(STRAPON_BOOSTERS.keys()), index=2)
    with c3:
        s1_fuel = st.slider("第1段 推進剤充填量 (トン: 胴体長連動)", 100.0, 4500.0, 1100.0, step=50.0)
        s1_mat = st.selectbox("第1段 構造素材", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("外殻等価板厚 (mm)", 1.0, 12.0, 4.2, step=0.1)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 空力パーツ", list(AERO_WINGS.keys()), index=0)
        angle_of_attack = st.slider("固定取り付け迎角 AoA (deg)", -3.0, 12.0, 0.5, step=0.5)
    with c2:
        sep_thrust_factor = st.slider("ブースター分離パイロ推力倍率 (スローモーション連動)", 0.5, 3.0, 1.2, step=0.1)
        st.info("💡 **自律型4K描画**: 外部接続不要なプロシージャルテクスチャ生成エンジンを採用し、ブラウザのCORS制限によるブラックアウトを根本対策しました。")

with tab3:
    c1, c2, c3 = st.columns(3)
    with c1:
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=0)
        s2_cycle = st.selectbox("第2段 ポンプ方式", list(PUMP_CYCLES.keys()), index=0)
        s2_eng_count = st.slider("真空ノズル基数", 1, 9, 3)
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 30, 280, 150, step=5)
    with c2:
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 20.0, 1200.0, 280.0, step=10.0)
        s2_mat = st.selectbox("第2段 構造素材", list(MATERIALS.keys()), index=0)
    with c3:
        fairing_type = st.selectbox("先端空力カウル / ペイロード", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 40.0, 180.0, 75.0, step=5.0)
        payload_mass = st.slider("投入衛星質量 (トン)", 0.5, 120.0, 22.0, step=1.0)

with tab4:
    c1, c2 = st.columns(2)
    with c1:
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.3, 15.0, 1.8, step=0.1)
        turn_end_alt = st.slider("水平重力ターン完了高度 (km)", 50.0, 250.0, 120.0, step=5.0)
        turn_exponent = st.slider("ターン曲率指数", 0.3, 2.0, 0.62, step=0.02)
    with c2:
        water_flow_rate = st.slider("消音注水デリュージ流量 (トン/秒)", 50, 450, 250, step=25)
        ignition_lead_time = st.slider("エンジン先行点火開始 (T-マイナス秒)", 2.5, 6.0, 3.8, step=0.1)
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
        "cyc_id": cyc["cyc_id"],
        "flame_hex": prop["flame_hex"],
        "outer_hex": prop["outer_hex"],
        "spark_hex": prop["spark_hex"],
        "eng_count": eng_count,
        "fuel_risk": prop["risk"],
        "prop_type": prop["type"]
    }

wing_spec = AERO_WINGS[wing_type]
fair_spec = FAIRINGS[fairing_type]
strapon_spec = STRAPON_BOOSTERS[strapon_opt]

s1_spec = calc_stage_specs(s1_prop, s1_cycle, s1_pc, 24, s1_eng_count, s1_fuel, s1_mat, s1_thick)
s2_spec = calc_stage_specs(s2_prop, s2_cycle, 220, s2_eps, s2_eng_count, s2_fuel, s2_mat, 3.0)

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
# 💥 物理シミュレーション (実時間軸カウントダウン・離床過渡応答)
# =========================================================================
def run_simulation(preview_only=False):
    if preview_only:
        return [{
            "t": -10.0, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "stage": 1, "fairing": True, "wings": bool(wing_spec["wing_id"] != "none"),
            "strapon": bool(strapon_spec["count"] > 0), "exploded": False, "explosion_type": "NONE",
            "thrust": False, "pitch": 0.0, "mach": 0.0, "event": "PREVIEW"
        }], None

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

    for cd_step in range(21):
        t_cd = -10.0 + cd_step * 0.5
        pre_ignition = bool(t_cd >= -ignition_lead_time)
        history.append({
            "t": float(t_cd), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "stage": 1, "fairing": True, "wings": wings_attached,
            "strapon": strapon_attached, "exploded": False, "explosion_type": "NONE",
            "thrust": pre_ignition, "pitch": 0.0, "mach": 0.0, "event": "COUNTDOWN"
        })

    maxq_passed = False
    supersonic_called = False

    if s1_spec["pc"] > s1_spec["pc_limit"]:
        fail_reason = f"ターボポンプ破裂: 燃焼室圧 {s1_spec['pc']} bar が限界 {s1_spec['pc_limit']} bar を超過。"
        history.append({
            "t": 0.1, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 0.0,
            "stage": 1, "fairing": True, "wings": wings_attached, "strapon": strapon_attached,
            "exploded": True, "explosion_type": "PAD_OVERPRESSURE", "thrust": False,
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
        strap_m = (strapon_spec["mass_add"] * 1000.0 + max(0.0, fuel_strapon_rem)) if strapon_attached else 0.0

        if stage == 1:
            if strapon_attached:
                if fuel_strapon_rem > 0 and (fuel_s1_rem > s1_fuel * 1000.0 * 0.28):
                    strap_thrust = strapon_spec["thrust_add"] * 1000.0
                    fuel_strapon_rem -= (strap_thrust / (strapon_spec["isp_sl"] * g0)) * dt * 1.3
                else:
                    strapon_attached = False
                    cur_event = "BOOSTER_SEP"
                    strap_thrust = 0.0
            else:
                strap_thrust = 0.0

            if fuel_s1_rem <= 0:
                stage = 2
                strapon_attached = False
                cur_event = "HOT_STAGING"
                thrust = 0.0
            else:
                cur_mass = float((s1_spec["dry_mass"] + s2_fuel + s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + w_mass + strap_m + fuel_s1_rem)
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s1_spec["isp_vac"] - (s1_spec["isp_vac"] - s1_spec["isp_sl"]) * atm_factor)
                thrust_core = float((s1_spec["thrust_vac"] - (s1_spec["thrust_vac"] - s1_spec["thrust_sl"]) * atm_factor) * 1000.0)

                if t < 3.0:
                    thrust_core *= (0.65 + (t / 3.0) * 0.35)

                if 8000 < alt < 17000:
                    thrust_core *= (throttle_maxq / 100.0)

                thrust = thrust_core + strap_thrust
                if thrust / (cur_mass * g0) > max_g_limit_cut:
                    thrust = max_g_limit_cut * cur_mass * g0

                mdot = thrust_core / (isp * g0)
                fuel_s1_rem -= mdot * dt

        if stage == 2:
            strapon_attached = False
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
            if t > 2.0:
                fail_reason = "推力不足 (TWR < 1.0): 自重を持ち上げられず発射台上で轟沈。"
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

        if q > cur_spec["max_q"]:
            fail_reason = f"Max-Q 構造圧壊: 動圧 {q:.1f} kPa が強度限界を超過。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached,
                "exploded": True, "explosion_type": "STRUCTURAL_COLLAPSE", "thrust": False, "pitch": visual_pitch,
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
        fail_reason = f"軌道速度未達（燃料枯渇・弾道落下）。高度: {alt_km:.1f} km, 速度: {vx:.0f} m/s"

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

cb1, cb2 = st.columns([3, 1])
with cb1:
    launch_clicked = st.button("🔴 4K 2画面中継 (近接追尾 ＆ 海岸線超望遠) ＆ 軌道投入シミュレーション開始", use_container_width=True, type="primary")
with cb2:
    st.caption("※ 上のタブで設定変更すると発射台上のロケットが即座に3D更新されます。")

traj_data, error_msg = run_simulation(preview_only=(not launch_clicked))

s1_len_scaled = float(np.clip(12.0 + (s1_fuel / 4500.0) * 15.0, 11.0, 27.0))
s2_len_scaled = float(np.clip(6.0 + (s2_fuel / 1200.0) * 8.0, 5.5, 14.0))

rocket_visual_cfg = {
    "is_preview": bool(not launch_clicked),
    "s1_mat": s1_spec["mat_id"],
    "s2_mat": s2_spec["mat_id"],
    "s1_cyc": s1_spec["cyc_id"],
    "s2_cyc": s2_spec["cyc_id"],
    "s1_eng": int(s1_eng_count),
    "s2_eng": int(s2_eng_count),
    "s1_eps": float(s1_eps),
    "s2_eps": float(s2_eps),
    "s1_len": s1_len_scaled,
    "s2_len": s2_len_scaled,
    "aoa": float(angle_of_attack),
    "flame_hex": s1_spec["flame_hex"],
    "outer_hex": s1_spec["outer_hex"],
    "spark_hex": s1_spec["spark_hex"],
    "s2_flame_hex": s2_spec["flame_hex"],
    "s2_outer_hex": s2_spec["outer_hex"],
    "s2_spark_hex": s2_spec["spark_hex"],
    "fairing_shape": fair_spec["shape_id"],
    "wing_id": wing_spec["wing_id"],
    "strapon_type": strapon_spec["type"],
    "strapon_count": int(strapon_spec["count"]),
    "water_flow": float(water_flow_rate),
    "ignition_lead": float(ignition_lead_time),
    "sep_thrust": float(sep_thrust_factor)
}

traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
cfg_json = json.dumps(rocket_visual_cfg)
fail_msg_clean = (error_msg or "").replace('"', '\\"').replace("'", "\\'")

html_code = f"""
<div id="broadcast-frame" style="position: relative; width: 100%; height: 950px; background: #000104; border-radius: 8px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none;">
    <script>
        if ({'false' if not launch_clicked else 'true'}) {{
            window.parent.document.getElementById('launch-viewport').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
    </script>

    <!-- メイン近接追尾キャンバス -->
    <div id="canvas-container" style="width: 100%; height: 100%; position: absolute; top: 0; left: 0;"></div>

    <!-- 🎥 サブ遠景PiPキャンバス (海岸線8.5km外定点ビュー) -->
    <div id="pip-container" style="position: absolute; top: 60px; right: 24px; width: 340px; height: 210px; background: #020617; border: 2px solid rgba(56, 189, 248, 0.5); border-radius: 6px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.85); z-index: 20;">
        <canvas id="pip-canvas" style="width: 100%; height: 100%; display: block;"></canvas>
        <div style="position: absolute; top: 8px; left: 10px; font-size: 10px; font-weight: 800; color: #fff; background: rgba(15, 23, 42, 0.85); padding: 2px 8px; border-radius: 3px; letter-spacing: 1px; font-family: monospace;">
            CAM 02: COASTAL TRACKER (8.5km OUT)
        </div>
        <div id="pip-hud-alt" style="position: absolute; bottom: 8px; right: 10px; font-size: 10px; font-family: monospace; color: #38bdf8; font-weight: 700; background: rgba(15, 23, 42, 0.85); padding: 2px 6px; border-radius: 3px;">
            ALT: 0.0 km
        </div>
    </div>

    <!-- 光学レンズ効果・レティクル -->
    <div style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; box-shadow: inset 0 0 140px rgba(0,0,0,0.88); z-index: 5;">
        <div style="position: absolute; top: 50%; left: 50%; width: 56px; height: 56px; transform: translate(-50%, -50%); border: 1px solid rgba(56, 189, 248, 0.22); border-radius: 50%;"></div>
        <div style="position: absolute; top: 50%; left: calc(50% - 40px); width: 20px; height: 1px; background: rgba(56, 189, 248, 0.35);"></div>
        <div style="position: absolute; top: 50%; left: calc(50% + 20px); width: 20px; height: 1px; background: rgba(56, 189, 248, 0.35);"></div>
    </div>

    <!-- 放送中継トップバナー -->
    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 48px; background: rgba(3, 7, 18, 0.9); backdrop-filter: blur(16px); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 10;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <span id="live-indicator" style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 12px #ef4444; animation: livePulse 1.4s infinite alternate;"></span>
            <span style="color: #ffffff; font-weight: 800; font-size: 13px; letter-spacing: 2px;">OFFICIAL 4K DUAL WEBCAST</span>
            <span style="color: rgba(255,255,255,0.2);">|</span>
            <span id="cam-tag" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; font-family: monospace;">CAM 01: PAD 39A HIGH-SPEED TRACKER</span>
        </div>
        <div style="display: flex; align-items: center; gap: 20px; font-family: monospace; font-size: 11px;">
            <span style="color: #94a3b8;">RCS FLUID JET: <strong id="hud-rcs" style="color: #38bdf8;">ACTIVE</strong></span>
            <span style="color: #94a3b8;">WATER DELUGE: <strong id="hud-deluge" style="color: #38bdf8;">STANDBY</strong></span>
            <span id="comm-status" style="color: #10b981;">TELEMETRY: LOCKED</span>
        </div>
    </div>

    <style>@keyframes livePulse {{ from {{ opacity: 0.35; }} to {{ opacity: 1.0; }} }}</style>

    <!-- 🛰️ 軌道フライト & 分離イベントログ HUD -->
    <div style="position: absolute; top: 280px; right: 24px; width: 340px; background: rgba(3, 7, 18, 0.88); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 4px; padding: 12px; z-index: 10; color: #fff;">
        <div style="font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 6px; display: flex; justify-content: space-between;">
            <span>DOWNRANGE TRAJECTORY</span>
            <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">0.0 km</span>
        </div>
        <canvas id="orbit-canvas" width="310" height="75" style="width: 100%; height: 75px; background: #01040d; border-radius: 2px;"></canvas>
        <div id="event-log" style="margin-top: 8px; font-family: monospace; font-size: 10px; color: #34d399; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
            > VEHICLE COUNTDOWN INITIALIZED
        </div>
    </div>

    <!-- 破壊アラート -->
    <div id="rud-banner" style="display: none; position: absolute; top: 170px; left: 50%; transform: translateX(-50%); background: rgba(120, 10, 10, 0.94); backdrop-filter: blur(16px); border: 2px solid #ef4444; border-radius: 4px; padding: 18px 32px; z-index: 25; text-align: center; box-shadow: 0 0 60px rgba(239, 68, 68, 0.7);">
        <div style="color: #fff; font-size: 18px; font-weight: 900; letter-spacing: 2.5px; font-family: monospace;">🚨 RAPID UNSCHEDULED DISASSEMBLY (RUD) 🚨</div>
        <div id="rud-desc" style="color: #fecaca; font-size: 13px; font-weight: 600; margin-top: 8px; max-width: 540px; line-height: 1.4;"></div>
    </div>

    <!-- 放送テレメトリー HUD -->
    <div style="position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(1, 3, 8, 0.98) 0%, rgba(2, 6, 14, 0.88) 75%, transparent 100%); padding: 28px 36px 20px 36px; box-sizing: border-box; display: flex; align-items: flex-end; justify-content: space-between; z-index: 10;">
        <div>
            <div id="tv-status" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 2px; margin-bottom: 2px;">COUNTDOWN SEQUENCE</div>
            <div id="tv-timer" style="color: #ffffff; font-size: 48px; font-weight: 900; font-family: 'Consolas', monospace; letter-spacing: 2px; text-shadow: 0 0 25px rgba(56, 189, 248, 0.4);">T- 00:10.0</div>
        </div>
        <div style="display: flex; gap: 36px; border-left: 1px solid rgba(255,255,255,0.15); padding-left: 32px;">
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
                <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">STAGE CONFIG</div>
                <div id="tv-stage-badge" style="color: #34d399; font-size: 20px; font-weight: 800; font-family: 'Consolas', monospace;">PAD INTEGRATION</div>
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
    const pipCanvas = document.getElementById('pip-canvas');
    const orbitCvs = document.getElementById('orbit-canvas');
    const octx = orbitCvs.getContext('2d');
    const flashOverlay = document.getElementById('flash-overlay');
    const rudBanner = document.getElementById('rud-banner');
    const rudDesc = document.getElementById('rud-desc');
    const eventLog = document.getElementById('event-log');

    // 音響合成エンジン
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    let actx = null, rumbleGain = null, crackleGain = null, hissGain = null;
    function initAudio() {{
        if (cfg.is_preview) return;
        if (!actx) {{
            actx = new AudioCtx();
            const buf = actx.createBuffer(1, actx.sampleRate * 2, actx.sampleRate);
            const d = buf.getChannelData(0);
            for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

            const rSrc = actx.createBufferSource(); rSrc.buffer = buf; rSrc.loop = true;
            const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 82;
            rumbleGain = actx.createGain(); rumbleGain.gain.value = 0;
            rSrc.connect(lp); lp.connect(rumbleGain); rumbleGain.connect(actx.destination);
            rSrc.start(0);

            const cSrc = actx.createBufferSource(); cSrc.buffer = buf; cSrc.loop = true;
            const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 640; bp.Q.value = 2.8;
            crackleGain = actx.createGain(); crackleGain.gain.value = 0;
            cSrc.connect(bp); bp.connect(crackleGain); crackleGain.connect(actx.destination);
            cSrc.start(0);

            const hSrc = actx.createBufferSource(); hSrc.buffer = buf; hSrc.loop = true;
            const hp = actx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 1800;
            hissGain = actx.createGain(); hissGain.gain.value = 0;
            hSrc.connect(hp); hp.connect(hissGain); hissGain.connect(actx.destination);
            hSrc.start(0);
        }}
        if (actx && actx.state === 'suspended') actx.resume();
    }}

    function playPyroSepSound() {{
        if (!actx) return;
        const osc = actx.createOscillator();
        const g = actx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(290, actx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(32, actx.currentTime + 0.45);
        g.gain.setValueAtTime(0.65, actx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.01, actx.currentTime + 0.45);
        osc.connect(g); g.connect(actx.destination);
        osc.start(); osc.stop(actx.currentTime + 0.45);
    }}

    function playExplosionSound() {{
        if (!actx) return;
        if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.0, actx.currentTime, 0.05);
        if (crackleGain) crackleGain.gain.setTargetAtTime(0.0, actx.currentTime, 0.05);
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
        if (cfg.is_preview || !('speechSynthesis' in window)) return;
        const u = new SpeechSynthesisUtterance(text);
        u.lang = 'en-US'; u.rate = 1.05; u.pitch = 0.92;
        window.speechSynthesis.speak(u);
    }}

    // =========================================================================
    // 🌍 Three.js シーン & デュアルカメラ構築
    // =========================================================================
    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(26, container.clientWidth / container.clientHeight, 0.5, 50000000);
    const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    container.appendChild(renderer.domElement);

    const pipCamera = new THREE.PerspectiveCamera(14, 340 / 210, 5.0, 50000000);
    pipCamera.position.set(-3200, 140, 4800);
    const pipRenderer = new THREE.WebGLRenderer({{ canvas: pipCanvas, antialias: true }});
    pipRenderer.setSize(340, 210);
    pipRenderer.setPixelRatio(1);
    pipRenderer.toneMapping = THREE.ACESFilmicToneMapping;
    pipRenderer.toneMappingExposure = 1.25;

    // 自律プロシージャルHDR環境マップ生成
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
    const sunGrad = ectx.createRadialGradient(380, 115, 2, 380, 115, 45);
    sunGrad.addColorStop(0, '#ffffff'); sunGrad.addColorStop(1, 'rgba(255,255,255,0)');
    ectx.fillStyle = sunGrad; ectx.fillRect(0, 0, 512, 256);

    const envTex = new THREE.CanvasTexture(envCanvas);
    envTex.mapping = THREE.EquirectangularReflectionMapping;
    scene.environment = pmremGenerator.fromEquirectangular(envTex).texture;

    const sunLight = new THREE.DirectionalLight(0xfff9f0, 4.2);
    sunLight.position.set(4000, 7500, 5000);
    scene.add(sunLight);
    scene.add(new THREE.HemisphereLight(0x7dd3fc, 0x1e293b, 0.75));

    const engineBounceLight = new THREE.PointLight(cfg.flame_hex, 0.0, 320, 1.6);
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
    const starMat = new THREE.PointsMaterial({{ size: 1.6, color: 0xe2e8f0, transparent: true, opacity: 0.15 }});
    scene.add(new THREE.Points(starGeo, starMat));

    // 自律プロシージャル地球生成 (外部CDN完全不使用)
    const earthCanvas = document.createElement('canvas'); earthCanvas.width = 1024; earthCanvas.height = 512;
    const gEctx = earthCanvas.getContext('2d');
    gEctx.fillStyle = '#0f3854'; gEctx.fillRect(0, 0, 1024, 512);
    // 大陸シェイプ
    gEctx.fillStyle = '#22543d';
    for(let i=0; i<42; i++) {{
        const cx = Math.random() * 1024, cy = 100 + Math.random() * 312;
        gEctx.beginPath(); gEctx.arc(cx, cy, 35 + Math.random()*70, 0, Math.PI * 2); gEctx.fill();
    }}
    // 雲シェイプ
    gEctx.fillStyle = 'rgba(255,255,255,0.45)';
    for(let i=0; i<65; i++) {{
        const cx = Math.random() * 1024, cy = 80 + Math.random() * 350;
        gEctx.beginPath(); gEctx.ellipse(cx, cy, 60 + Math.random()*90, 15 + Math.random()*25, 0.2, 0, Math.PI * 2); gEctx.fill();
    }}
    const earthTex = new THREE.CanvasTexture(earthCanvas);

    const R_EARTH = 6371.0;
    const earthMesh = new THREE.Mesh(
        new THREE.SphereGeometry(R_EARTH, 128, 96),
        new THREE.MeshStandardMaterial({{ map: earthTex, roughness: 0.7, metalness: 0.1 }})
    );
    earthMesh.position.set(0, -R_EARTH, 0);
    earthMesh.rotation.y = -Math.PI * 0.62;
    scene.add(earthMesh);

    // =========================================================================
    // 🏝️ ケープカナベラル PBR 海岸線ランドスケープ
    // =========================================================================
    const landscapeGroup = new THREE.Group();
    scene.add(landscapeGroup);

    const terrainCvs = document.createElement('canvas'); terrainCvs.width = 1024; terrainCvs.height = 1024;
    const tctx = terrainCvs.getContext('2d');
    tctx.fillStyle = '#082f49'; tctx.fillRect(0, 0, 1024, 1024);
    tctx.fillStyle = '#d4b996';
    tctx.beginPath(); tctx.moveTo(0, 0); tctx.lineTo(620, 0);
    tctx.bezierCurveTo(580, 300, 480, 700, 420, 1024); tctx.lineTo(0, 1024); tctx.closePath(); tctx.fill();
    tctx.fillStyle = '#3f6212';
    tctx.beginPath(); tctx.moveTo(0, 0); tctx.lineTo(540, 0);
    tctx.bezierCurveTo(500, 300, 420, 700, 360, 1024); tctx.lineTo(0, 1024); tctx.closePath(); tctx.fill();
    tctx.strokeStyle = '#78716c'; tctx.lineWidth = 14;
    tctx.beginPath(); tctx.moveTo(100, 512); tctx.lineTo(460, 512); tctx.stroke();

    const terrainTex = new THREE.CanvasTexture(terrainCvs);
    const terrainMat = new THREE.MeshStandardMaterial({{ map: terrainTex, roughness: 0.88, metalness: 0.08 }});
    const terrainMesh = new THREE.Mesh(new THREE.PlaneGeometry(16000, 16000), terrainMat);
    terrainMesh.rotation.x = -Math.PI / 2;
    terrainMesh.position.set(-1500, -1.2, 0);
    landscapeGroup.add(terrainMesh);

    const oceanMat = new THREE.MeshStandardMaterial({{ color: 0x0369a1, roughness: 0.12, metalness: 0.75, transparent: true, opacity: 0.88 }});
    const oceanMesh = new THREE.Mesh(new THREE.PlaneGeometry(24000, 24000), oceanMat);
    oceanMesh.rotation.x = -Math.PI / 2;
    oceanMesh.position.set(5000, -0.6, 0);
    landscapeGroup.add(oceanMesh);

    // NASA VAB組立棟
    const vabMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, roughness: 0.45 }});
    const vabMesh = new THREE.Mesh(new THREE.BoxGeometry(160, 150, 180), vabMat);
    vabMesh.position.set(-4200, 75, -1800);
    landscapeGroup.add(vabMesh);

    // =========================================================================
    // 🏗️ 発射複合施設 (OLM・タワー・デリュージ水冷プレート)
    // =========================================================================
    const pad = new THREE.Group();
    scene.add(pad);

    const darkSteelMat = new THREE.MeshStandardMaterial({{ color: 0x1e242b, metalness: 0.85, roughness: 0.35 }});
    const concreteMat = new THREE.MeshStandardMaterial({{ color: 0x374151, roughness: 0.9, metalness: 0.05 }});
    const pipeMat = new THREE.MeshStandardMaterial({{ color: 0xcbd5e1, metalness: 0.9, roughness: 0.22 }});
    const hazardMat = new THREE.MeshStandardMaterial({{ color: 0xeab308, roughness: 0.45, metalness: 0.35 }});
    const goldFoilMat = new THREE.MeshStandardMaterial({{ color: 0xf59e0b, metalness: 0.96, roughness: 0.16 }});

    const groundPlate = new THREE.Mesh(new THREE.CylinderGeometry(85, 95, 1.2, 64), concreteMat);
    groundPlate.position.y = -0.6; pad.add(groundPlate);

    const delugePlate = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 4.8, 0.4, 32), pipeMat);
    delugePlate.position.y = 0.2; pad.add(delugePlate);

    const olmRing = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 3.6, 1.8, 32), darkSteelMat);
    olmRing.position.y = 5.2; pad.add(olmRing);
    for(let i=0; i<12; i++) {{
        const ang = (i / 12) * Math.PI * 2;
        const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.38, 5.2, 12), darkSteelMat);
        leg.position.set(Math.cos(ang)*2.85, 2.6, Math.sin(ang)*2.85);
        pad.add(leg);
    }}

    const towerX = -9.2;
    const towerHeight = 56.0;
    for(let cx of [-2.2, 2.2]) {{
        for(let cz of [-2.2, 2.2]) {{
            const col = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.32, towerHeight, 12), darkSteelMat);
            col.position.set(towerX + cx, towerHeight/2, cz);
            pad.add(col);
        }}
    }}
    for(let h = 2; h < towerHeight; h += 3.8) {{
        const frame = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.25, 4.6), darkSteelMat);
        frame.position.set(towerX, h, 0); pad.add(frame);
    }}
    for(let zSide of [-1.4, 1.4]) {{
        const chopstick = new THREE.Mesh(new THREE.BoxGeometry(9.2, 0.55, 0.45), darkSteelMat);
        chopstick.position.set(towerX + 5.5, 6.0 + cfg.s1_len + 2.0, zSide);
        pad.add(chopstick);
    }}
    for(let mAng of [0.6, 2.4, 3.9, 5.5]) {{
        const lMast = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.45, 58.0, 8), hazardMat);
        lMast.position.set(Math.cos(mAng)*44, 29.0, Math.sin(mAng)*44); pad.add(lMast);
    }}

    // =========================================================================
    // 🎨 自律PBRテクスチャ生成エンジン (リベット・溶接ビード・TPS耐熱タイル)
    // =========================================================================
    function createMaterialSkin(matId, hasHeatshield) {{
        const w = 512, h = 1024;
        const diffCvs = document.createElement('canvas'); diffCvs.width = w; diffCvs.height = h;
        const dctx = diffCvs.getContext('2d');
        const bumpCvs = document.createElement('canvas'); bumpCvs.width = w; bumpCvs.height = h;
        const bctx = bumpCvs.getContext('2d');

        bctx.fillStyle = '#808080'; bctx.fillRect(0, 0, w, h);

        if (matId === 'ss') {{
            dctx.fillStyle = '#d1d5db'; dctx.fillRect(0, 0, w, h);
            for(let y = 0; y < h; y += 48) {{
                const s = (Math.random() - 0.5) * 20;
                dctx.fillStyle = `rgb(${{208+s}}, ${{213+s}}, ${{221+s}})`;
                dctx.fillRect(0, y, w, 46);
                dctx.fillStyle = 'rgba(80, 60, 40, 0.35)'; dctx.fillRect(0, y, w, 2);
                bctx.fillStyle = '#303030'; bctx.fillRect(0, y, w, 3);
            }}
        }} else if (matId === 'al') {{
            dctx.fillStyle = '#f8fafc'; dctx.fillRect(0, 0, w, h);
            dctx.fillStyle = '#d97706'; dctx.fillRect(0, h * 0.22, w, h * 0.56);
            for(let y=0; y<h; y+=48) {{ bctx.fillStyle = '#505050'; bctx.fillRect(0, y, w, 3); }}
        }} else if (matId === 'saturn') {{
            dctx.fillStyle = '#f8fafc'; dctx.fillRect(0, 0, w, h);
            dctx.fillStyle = '#0f172a';
            for(let i=0; i<8; i++) {{
                if (i%2===0) {{
                    dctx.fillRect(i*(w/8), h*0.12, w/8, h*0.18);
                    dctx.fillRect(i*(w/8), h*0.65, w/8, h*0.20);
                }}
            }}
        }} else if (matId === 'cf') {{
            dctx.fillStyle = '#141619'; dctx.fillRect(0, 0, w, h);
            dctx.fillStyle = '#27272a';
            for(let y = 0; y < h; y += 8) {{
                for(let x = 0; x < w; x += 8) {{
                    if ((x+y)%16 === 0) dctx.fillRect(x, y, 4, 4);
                }}
            }}
        }} else {{
            dctx.fillStyle = '#52525b'; dctx.fillRect(0, 0, w, h);
        }}

        for(let x = 0; x < w; x += 64) {{
            bctx.fillStyle = '#555555'; bctx.fillRect(x, 0, 2, h);
        }}

        if (hasHeatshield) {{
            dctx.fillStyle = '#0f1115'; dctx.fillRect(0, 0, w * 0.48, h);
            bctx.strokeStyle = '#18181b'; bctx.lineWidth = 2;
            for(let ty = 0; ty < h; ty += 16) {{
                for(let tx = 0; tx < w * 0.48; tx += 16) {{
                    bctx.strokeRect(tx + (ty%32===0?0:8), ty, 15, 15);
                }}
            }}
        }}

        const sootGrad = dctx.createLinearGradient(0, h * 0.78, 0, h);
        sootGrad.addColorStop(0, 'rgba(10,12,16,0)');
        sootGrad.addColorStop(1, 'rgba(10,12,16,0.75)');
        dctx.fillStyle = sootGrad; dctx.fillRect(0, h * 0.78, w, h * 0.22);

        return {{
            map: new THREE.CanvasTexture(diffCvs),
            bumpMap: new THREE.CanvasTexture(bumpCvs)
        }};
    }}

    // =========================================================================
    // 🔥 流体シェーダープルーム＆エンジンノズル
    // =========================================================================
    const plumeShaderMat = new THREE.ShaderMaterial({{
        transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
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
                float dist = 1.0 - uv.y;
                float bellExpand = pow(dist, 0.65) * (0.8 + uVacFactor * 3.8);
                float turb = sin(dist * 28.0 - uTime * 60.0) * 0.07 * dist;
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

                float waveFreq = 24.0 / (1.0 + uVacFactor * 1.5);
                float shockWave = pow(max(0.0, cos(distFromNozzle * waveFreq - uTime * 22.0)), 6.0);
                float shockFade = max(0.0, 1.0 - uVacFactor * 1.4) * exp(-distFromNozzle * 2.5);

                float coreMask = exp(-radial * radial * 8.5) * exp(-distFromNozzle * 1.6);
                float plumeBody = exp(-radial * radial * 3.0) * pow(1.0 - distFromNozzle, 1.3);
                float noise = 0.88 + 0.12 * sin(distFromNozzle * 45.0 - uTime * 75.0 + radial * 12.0);

                vec3 col = mix(uOuterColor, uMidColor, plumeBody);
                col = mix(col, uCoreColor, clamp(coreMask + shockWave * shockFade * 0.9, 0.0, 1.0));

                float tipFade = smoothstep(0.0, 0.015, distFromNozzle) * smoothstep(1.0, 0.12, distFromNozzle);
                float alpha = clamp((plumeBody * 0.95 + coreMask * 0.85) * tipFade * noise, 0.0, 1.0);

                gl_FragColor = vec4(col * 2.4, alpha);
            }}
        `
    }});

    function createNozzlePlumeMesh(jetWidth, jetLength) {{
        const jetGroup = new THREE.Group();
        for(let rAngle of [0, Math.PI / 2]) {{
            const pPlane = new THREE.Mesh(new THREE.PlaneGeometry(jetWidth, jetLength, 8, 32), plumeShaderMat);
            pPlane.position.y = -jetLength / 2;
            pPlane.rotation.y = rAngle;
            jetGroup.add(pPlane);
        }}
        return jetGroup;
    }}

    const s1NozzleTips = [];
    const s2NozzleTips = [];
    const boosterNozzleTips = [];

    const inconelNozzleMat = new THREE.MeshStandardMaterial({{ color: 0x3f3f46, metalness: 0.95, roughness: 0.22, side: THREE.DoubleSide }});

    function buildDetailedEngineCluster(parent, count, radius, basePosY, epsScale, cycId, tipArray, jetLen) {{
        const group = new THREE.Group();
        group.position.y = basePosY;
        const bellH = 1.15 * epsScale;
        const bellW = 0.24 * Math.pow(epsScale, 0.65);

        const nozzlePts = [];
        for(let i=0; i<=16; i++) {{
            const t = i / 16;
            nozzlePts.push(new THREE.Vector2(0.08 + bellW * Math.pow(t, 0.62), -t * bellH));
        }}
        const bellGeo = new THREE.LatheGeometry(nozzlePts, 24);
        const visualPlumeStep = Math.max(1, Math.floor(count / 6));

        for(let i=0; i<count; i++) {{
            const ang = (i / count) * Math.PI * 2;
            const r = (count === 1) ? 0 : (i < 3 && count > 6 ? radius * 0.38 : radius);
            const engUnit = new THREE.Group();
            engUnit.position.set(Math.cos(ang)*r, 0, Math.sin(ang)*r);

            const bell = new THREE.Mesh(bellGeo, inconelNozzleMat);
            engUnit.add(bell);

            const throatGlow = new THREE.Mesh(
                new THREE.CircleGeometry(bellW * 0.85, 16),
                new THREE.MeshBasicMaterial({{ color: 0xffffff, side: THREE.DoubleSide }})
            );
            throatGlow.rotation.x = Math.PI / 2;
            throatGlow.position.y = -bellH * 0.85;
            engUnit.add(throatGlow);

            if (i % visualPlumeStep === 0 || i === 0) {{
                const tipObj = new THREE.Object3D();
                tipObj.position.set(0, -bellH * 0.92, 0);
                const plumeMesh = createNozzlePlumeMesh(bellW * 6.5, jetLen);
                tipObj.add(plumeMesh);
                engUnit.add(tipObj);
                tipArray.push({{ node: tipObj, plume: plumeMesh }});
            }}
            group.add(engUnit);
        }}
        parent.add(group);
        return group;
    }}

    // =========================================================================
    // 🚀 ロケット本体＆パーツアセンブリ
    // =========================================================================
    const rocket = new THREE.Group();
    rocket.position.y = 6.0;
    scene.add(rocket);

    const s1Maps = createMaterialSkin(cfg.s1_mat, false);
    const s2Maps = createMaterialSkin(cfg.s2_mat, true);

    const s1Mat = new THREE.MeshStandardMaterial({{
        map: s1Maps.map, bumpMap: s1Maps.bumpMap, bumpScale: 0.04,
        metalness: (cfg.s1_mat === 'ss') ? 0.92 : 0.25,
        roughness: (cfg.s1_mat === 'ss') ? 0.16 : 0.42
    }});
    const s2Mat = new THREE.MeshStandardMaterial({{
        map: s2Maps.map, bumpMap: s2Maps.bumpMap, bumpScale: 0.045,
        metalness: (cfg.s2_mat === 'ss') ? 0.88 : 0.28,
        roughness: (cfg.s2_mat === 'ss') ? 0.18 : 0.45
    }});

    const s1Len = cfg.s1_len;
    const interLen = 2.2;
    const s2Len = cfg.s2_len;
    const s2BaseY = s1Len + interLen;
    const noseY = s2BaseY + s2Len;

    // 1. 第1段
    const s1Group = new THREE.Group();
    rocket.add(s1Group);

    const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, 48), s1Mat);
    s1Body.position.y = s1Len / 2; s1Group.add(s1Body);

    for(let side of [-1, 1]) {{
        const chine = new THREE.Mesh(new THREE.BoxGeometry(0.24, s1Len * 0.94, 0.32), s1Mat);
        chine.position.set(side * 1.12, s1Len * 0.48, 0); s1Group.add(chine);
    }}
    const skirtRing = new THREE.Mesh(new THREE.CylinderGeometry(1.18, 1.22, 1.8, 48), darkSteelMat);
    skirtRing.position.y = 0.9; s1Group.add(skirtRing);

    const interstage = new THREE.Group();
    interstage.position.y = s1Len + interLen / 2;
    s1Group.add(interstage);
    for(let i=0; i<16; i++) {{
        const a = (i / 16) * Math.PI * 2;
        const strut = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, interLen, 8), darkSteelMat);
        strut.position.set(Math.cos(a)*1.1, 0, Math.sin(a)*1.1);
        strut.rotation.z = (i%2 === 0) ? 0.18 : -0.18;
        interstage.add(strut);
    }}

    const s1EpsScale = 0.75 + (cfg.s1_eps / 70.0) * 0.75;
    const s1Engines = buildDetailedEngineCluster(s1Group, cfg.s1_eng, 0.78, 0.0, s1EpsScale, cfg.s1_cyc, s1NozzleTips, 32.0);

    const wingsGroup = new THREE.Group();
    s1Group.add(wingsGroup);
    const aoaRad = (cfg.aoa * Math.PI) / 180.0;

    if (cfg.wing_id === 'grid') {{
        for(let i=0; i<4; i++) {{
            const ang = (i / 4) * Math.PI * 2 + Math.PI / 4;
            const gridBox = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.14, 1.25), new THREE.MeshStandardMaterial({{ color: 0x94a3b8, metalness: 0.9, wireframe: true }}));
            gridBox.position.set(Math.cos(ang)*1.8, s1Len - 1.1, Math.sin(ang)*1.8);
            gridBox.rotation.y = -ang; gridBox.rotation.z = aoaRad;
            wingsGroup.add(gridBox);
        }}
    }} else if (cfg.wing_id === 'delta_wing') {{
        for(let side of [-1, 1]) {{
            const wing = new THREE.Mesh(new THREE.BoxGeometry(5.2, 6.2, 0.15), darkSteelMat);
            wing.position.set(side * 3.1, s1Len * 0.35, 0);
            wing.rotation.z = side * 0.45; wing.rotation.x = aoaRad;
            wingsGroup.add(wing);
        }}
    }}

    // 2. 外部ブースター群 (スローモーション分離物理対応)
    const boosterUnits = [];
    if (cfg.strapon_count > 0) {{
        const sCount = cfg.strapon_count;
        for(let i=0; i<sCount; i++) {{
            const angle = (i / sCount) * Math.PI * 2;
            const bx = Math.cos(angle) * 2.15, bz = Math.sin(angle) * 2.15;
            const bUnit = new THREE.Group();
            bUnit.position.set(bx, 0, bz);

            const bLen = s1Len * 0.82;
            const bBody = new THREE.Mesh(new THREE.CylinderGeometry(0.68, 0.68, bLen, 32), (cfg.strapon_type === 'srb') ? new THREE.MeshStandardMaterial({{ color: 0xf8fafc }}) : s1Mat);
            bBody.position.y = bLen / 2; bUnit.add(bBody);

            const bNose = new THREE.Mesh(new THREE.ConeGeometry(0.68, 1.9, 32), s1Mat);
            bNose.position.y = bLen + 0.95; bUnit.add(bNose);

            const localTips = [];
            buildDetailedEngineCluster(bUnit, 1, 0, 0, 1.0, 'sc', localTips, 26.0);
            localTips.forEach(t => boosterNozzleTips.push(t));

            rocket.add(bUnit);
            boosterUnits.push({{
                mesh: bUnit, angle: angle, baseX: bx, baseZ: bz,
                detached: false, vx: 0, vy: 0, vz: 0, rx: 0, rz: 0, tips: localTips
            }});
        }}
    }}

    // 3. 第2段オービター
    const s2Group = new THREE.Group();
    s2Group.position.y = s2BaseY;
    rocket.add(s2Group);

    const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, 48), s2Mat);
    s2Body.position.y = s2Len / 2; s2Group.add(s2Body);

    const s2EpsScale = 1.0 + (cfg.s2_eps / 280.0) * 1.1;
    const s2Engines = buildDetailedEngineCluster(s2Group, cfg.s2_eng, 0.55, 0.0, s2EpsScale, cfg.s2_cyc, s2NozzleTips, 34.0);
    s2NozzleTips.forEach(t => {{ t.plume.visible = false; }});

    // 内部衛星
    const satBus = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 2.4, 16), goldFoilMat);
    satBus.position.y = s2Len + 1.8;
    s2Group.add(satBus);

    // フェアリング
    const fairingHalves = [];
    const ogivePts = [];
    const noseH = 5.4;
    for(let i=0; i<=24; i++) {{
        const t = i / 24;
        ogivePts.push(new THREE.Vector2(Math.max(0.01, 1.12 * Math.pow(1.0 - Math.pow(t, 1.65), 0.72)), t * noseH));
    }}
    for(let side of [-1, 1]) {{
        const halfGeo = new THREE.LatheGeometry(ogivePts, 24, (side === 1) ? 0 : Math.PI, Math.PI);
        const halfMesh = new THREE.Mesh(halfGeo, s2Mat);
        halfMesh.position.y = s2Len;
        s2Group.add(halfMesh);
        fairingHalves.push({{ mesh: halfMesh, side: side, detached: false, vx: 0, vy: 0, rotZ: 0 }});
    }}

    // 4. RCSマウントノズル
    const rcsMountNodes = [];
    for(let side of [-1, 1]) {{
        const block = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.45, 0.25), darkSteelMat);
        block.position.set(side * 1.15, s2Len - 0.8, 0);
        s2Group.add(block);
        rcsMountNodes.push({{ node: block, side: side, isS1: false }});

        const s1Block = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.45, 0.25), darkSteelMat);
        s1Block.position.set(side * 1.15, s1Len - 0.6, 0);
        s1Group.add(s1Block);
        rcsMountNodes.push({{ node: s1Block, side: side, isS1: true }});
    }}

    // =========================================================================
    // ✨ パーティクルエンジン (自律生成スプライト)
    // =========================================================================
    function createCloudTexture() {{
        const c = document.createElement('canvas'); c.width = 64; c.height = 64;
        const ctx = c.getContext('2d');
        const g = ctx.createRadialGradient(32, 32, 4, 32, 32, 32);
        g.addColorStop(0, 'rgba(255,255,255,0.4)');
        g.addColorStop(0.5, 'rgba(225,232,240,0.18)');
        g.addColorStop(1, 'rgba(160,175,190,0)');
        ctx.fillStyle = g; ctx.fillRect(0,0,64,64);
        return new THREE.CanvasTexture(c);
    }}
    function createSparkTexture() {{
        const c = document.createElement('canvas'); c.width = 32; c.height = 32;
        const ctx = c.getContext('2d');
        const g = ctx.createRadialGradient(16,16,1, 16,16,15);
        g.addColorStop(0, 'rgba(255,255,255,1)');
        g.addColorStop(0.4, 'rgba(255,220,120,0.95)');
        g.addColorStop(1, 'rgba(255,40,0,0)');
        ctx.fillStyle = g; ctx.fillRect(0,0,32,32);
        return new THREE.CanvasTexture(c);
    }}

    const cloudTex = createCloudTexture();
    const sparkTex = createSparkTexture();

    const P_MAX = 1400;
    const pool = [];
    const pGroup = new THREE.Group(); scene.add(pGroup);
    for(let i=0; i<P_MAX; i++) {{
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({{ map: cloudTex, transparent: true, opacity: 0, depthWrite: false }}));
        sp.visible = false; pGroup.add(sp);
        pool.push({{ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 5, o: 0.8 }});
    }}
    let pIdx = 0;
    function emitParticle(x, y, z, vx, vy, vz, s0, s1, life, opacity, hexColor, additive) {{
        const p = pool[pIdx]; pIdx = (pIdx + 1) % P_MAX;
        p.active = true; p.sp.visible = true;
        p.sp.position.set(x, y, z);
        p.vx = vx; p.vy = vy; p.vz = vz;
        p.age = 0; p.maxAge = life; p.s0 = s0; p.s1 = s1; p.o = opacity;
        p.sp.material.color.setHex(hexColor);
        p.sp.material.blending = additive ? THREE.AdditiveBlending : THREE.NormalBlending;
    }}

    const SPARK_MAX = 400;
    const sparkPool = [];
    const sparkGroup = new THREE.Group(); scene.add(sparkGroup);
    for(let i=0; i<SPARK_MAX; i++) {{
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({{ map: sparkTex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }}));
        sp.visible = false; sparkGroup.add(sp);
        sparkPool.push({{ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, size: 0.5 }});
    }}
    let sIdx = 0;
    function emitNozzleSpark(x, y, z, vx, vy, vz, size, life, hexCol) {{
        const s = sparkPool[sIdx]; sIdx = (sIdx + 1) % SPARK_MAX;
        s.active = true; s.sp.visible = true;
        s.sp.position.set(x, y, z);
        s.vx = vx; s.vy = vy; s.vz = vz;
        s.age = 0; s.maxAge = life; s.size = size;
        s.sp.scale.set(size, size * 1.8, 1);
        s.sp.material.color.setHex(hexCol);
        s.sp.material.opacity = 1.0;
    }}

    function drawOrbitMap(altKm, dRangeKm, exploded) {{
        octx.clearRect(0, 0, 310, 75);
        octx.beginPath(); octx.arc(155, 210, 165, Math.PI, 0); octx.strokeStyle = '#1e293b'; octx.lineWidth = 3; octx.stroke();
        octx.beginPath(); octx.arc(155, 210, 195, Math.PI, 0); octx.strokeStyle = 'rgba(56, 189, 248, 0.25)'; octx.lineWidth = 1; octx.setLineDash([4, 4]); octx.stroke(); octx.setLineDash([]);

        const px = 20 + Math.min(270, (dRangeKm / 1200.0) * 270);
        const py = 65 - Math.min(55, (altKm / 200.0) * 55);

        octx.beginPath(); octx.moveTo(20, 65); octx.quadraticCurveTo(px * 0.5, 65, px, py);
        octx.strokeStyle = exploded ? '#ef4444' : '#38bdf8'; octx.lineWidth = 2; octx.stroke();
        octx.fillStyle = exploded ? '#dc2626' : '#38bdf8';
        octx.beginPath(); octx.arc(px, py, exploded ? 6 : 4, 0, Math.PI * 2); octx.fill();
    }}

    // =========================================================================
    // 🎥 デュアルカメラ・トラッキング制御 (見切れゼロ保証)
    // =========================================================================
    const smoothOffset = new THREE.Vector3(42.0, 14.0, 82.0);
    const activeFocusWorld = new THREE.Vector3();
    let camShake = 0.0;

    function updateDualCameraTracking(simT, elapsedSec, alt, pitch, stage, exploded) {{
        rocket.updateMatrixWorld(true);
        if (stage === 2) {{
            activeFocusWorld.set(0, s2Len * 0.45, 0);
            s2Group.localToWorld(activeFocusWorld);
        }} else {{
            activeFocusWorld.set(0, s1Len * 0.55, 0);
            rocket.localToWorld(activeFocusWorld);
        }}

        pipCamera.lookAt(activeFocusWorld);
        document.getElementById('pip-hud-alt').innerText = `ALT: ${{Math.max(0, alt).toFixed(1)}} km`;

        if (cfg.is_preview) {{
            document.getElementById('cam-tag').innerText = "PAD INSPECTION: LIVE 3D ORBITAL VIEW";
            const orbitAng = elapsedSec * 0.28;
            camera.position.set(Math.sin(orbitAng) * 72.0, 20.0 + Math.sin(elapsedSec * 0.4) * 8.0, Math.cos(orbitAng) * 72.0);
            camera.lookAt(0, 6.0 + (s1Len + s2Len) * 0.48, 0);
            return;
        }}

        const desiredOffset = new THREE.Vector3();
        if (exploded) {{
            document.getElementById('cam-tag').innerText = "CAM 01: HIGH-SPEED DEBRIS TRACKER";
            desiredOffset.set(55.0, 22.0, 130.0);
        }} else if (simT < 0.0) {{
            document.getElementById('cam-tag').innerText = "CAM 01: OLM TOWER TELEPHOTO";
            desiredOffset.set(38.0, -2.0, 76.0);
        }} else if (simT < 4.0) {{
            document.getElementById('cam-tag').innerText = "CAM 01: TOWER CLEARANCE TRACKER";
            desiredOffset.set(-42.0, 8.0, 95.0);
        }} else if (alt < 22.0) {{
            document.getElementById('cam-tag').innerText = "CAM 01: KINETO TRACKER (2400mm APO)";
            desiredOffset.set(-38.0, -14.0, 88.0);
        }} else if (alt < 85.0) {{
            document.getElementById('cam-tag').innerText = "CAM 01: WB-57 OPTICAL CHASE";
            desiredOffset.set(-35.0, -8.0, 82.0);
        }} else {{
            document.getElementById('cam-tag').innerText = "CAM 01: ORBITAL LONG-RANGE TELESCOPE";
            desiredOffset.set(-28.0, 10.0, 72.0);
        }}

        smoothOffset.lerp(desiredOffset, 0.08);
        camera.position.copy(activeFocusWorld).add(smoothOffset);

        if (camShake > 0.002) {{
            camera.position.x += (Math.random() - 0.5) * camShake;
            camera.position.y += (Math.random() - 0.5) * camShake;
            camShake *= 0.93;
        }}
        camera.lookAt(activeFocusWorld);
    }}

    // =========================================================================
    // ⏱️ アニメーション・メインループ
    // =========================================================================
    let tStart = performance.now();
    let explodedTriggered = false;
    let boosterDetached = false;
    let stage1Detached = false;
    let fairingDetached = false;
    let s1Vel = {{ vx: 0, vy: 0, rotVel: 0 }};
    let prevPitch = 0.0;
    const tempTipPos = new THREE.Vector3();

    function animate(now) {{
        requestAnimationFrame(animate);
        initAudio();

        const elapsedSec = (now - tStart) / 1000.0;
        const simT = cfg.is_preview ? -10.0 : (-10.0 + elapsedSec);
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
        rocket.updateMatrixWorld(true);

        starMat.opacity = Math.min(0.95, 0.1 + (alt / 45.0) * 0.85);

        const ux = Math.sin(pitch), uy = Math.cos(pitch);
        const perpX = Math.cos(pitch), perpY = -Math.sin(pitch);

        // 1. スローモーション・ブースター分離物理
        if (!p0.strapon && !boosterDetached && boosterUnits.length > 0 && !cfg.is_preview) {{
            boosterDetached = true;
            playPyroSepSound();
            eventLog.innerText = "> KOROLEV CROSS: BOOSTER SLOW-MOTION JETTISON";
            announceWebcast("Side boosters separated.");

            for(let b of boosterUnits) {{
                b.detached = true;
                b.tips.forEach(t => {{ t.plume.visible = false; }});
                scene.attach(b.mesh);
                const outX = Math.cos(b.angle);
                const outZ = Math.sin(b.angle);
                const sepP = cfg.sep_thrust;
                b.vx = ux * (vel * 0.068) + perpX * outX * (2.8 * sepP);
                b.vy = uy * (vel * 0.068) + perpY * outX * (2.8 * sepP) - 1.8;
                b.vz = outZ * (2.8 * sepP);
                b.rx = outZ * 0.42;
                b.rz = -outX * 0.42;

                b.mesh.getWorldPosition(tempTipPos);
                for(let k=0; k<8; k++) {{
                    emitParticle(tempTipPos.x, tempTipPos.y, tempTipPos.z, outX*0.6, 0.2, outZ*0.6, 2.8, 14.0, 45, 0.85, 0xffffff, false);
                }}
            }}
        }}
        if (boosterDetached) {{
            for(let b of boosterUnits) {{
                b.mesh.position.x += b.vx * 0.016;
                b.mesh.position.y += b.vy * 0.016;
                b.mesh.position.z += b.vz * 0.016;
                b.vy -= 9.8 * 0.016 * 0.8;
                b.mesh.rotation.x += b.rx * 0.016;
                b.mesh.rotation.z += b.rz * 0.016;
            }}
        }}

        // 2. 第1段ホットステージング
        if (p0.stage === 2 && !stage1Detached && !cfg.is_preview) {{
            stage1Detached = true;
            playPyroSepSound();
            eventLog.innerText = "> STAGE 1 SEPARATION & SECOND STAGE IGNITION";
            announceWebcast("Stage separation confirmed.");

            s1NozzleTips.forEach(t => {{ t.plume.visible = false; }});
            s2NozzleTips.forEach(t => {{ t.plume.visible = true; }});
            plumeShaderMat.uniforms.uMidColor.value.setHex(cfg.s2_flame_hex);
            plumeShaderMat.uniforms.uOuterColor.value.setHex(cfg.s2_outer_hex);

            scene.attach(s1Group);
            s1Vel.vx = ux * (vel * 0.068) - ux * 4.2;
            s1Vel.vy = uy * (vel * 0.068) - uy * 4.2;
            s1Vel.rotVel = 0.35;
        }}
        if (stage1Detached) {{
            s1Group.position.x += s1Vel.vx * 0.016;
            s1Group.position.y += s1Vel.vy * 0.016;
            s1Vel.vy -= 9.8 * 0.016 * 1.0;
            s1Group.rotation.z += s1Vel.rotVel * 0.016;
        }}

        // 3. フェアリング分離
        if (!p0.fairing && !fairingDetached && fairingHalves.length > 0 && !cfg.is_preview) {{
            fairingDetached = true;
            playPyroSepSound();
            eventLog.innerText = "> FAIRING JETTISON (PAYLOAD EXPOSED)";
            announceWebcast("Fairing separation confirmed.");
            for(let fh of fairingHalves) {{
                fh.detached = true;
                scene.attach(fh.mesh);
                fh.vx = ux * (vel * 0.072) + perpX * fh.side * 5.5;
                fh.vy = uy * (vel * 0.072) + perpY * fh.side * 5.5 - 1.5;
                fh.rotZ = -fh.side * 0.8;
            }}
        }}
        if (fairingDetached) {{
            for(let fh of fairingHalves) {{
                fh.mesh.position.x += fh.vx * 0.016;
                fh.mesh.position.y += fh.vy * 0.016;
                fh.vy -= 9.8 * 0.016 * 0.7;
                fh.mesh.rotation.z += fh.rotZ * 0.016;
            }}
        }}

        // 4. ノズル直結スパークシャワー＆エンジン排気
        if (p0.thrust && !p0.exploded && !cfg.is_preview) {{
            const vacFactor = Math.min(1.0, alt / 65.0);
            plumeShaderMat.uniforms.uVacFactor.value = vacFactor;

            const activeTips = (p0.stage === 1) ? [...s1NozzleTips] : [...s2NozzleTips];
            if (p0.stage === 1 && !boosterDetached) {{
                activeTips.push(...boosterNozzleTips);
            }}
            const curSparkHex = (p0.stage === 1) ? cfg.spark_hex : cfg.s2_spark_hex;

            for(let tObj of activeTips) {{
                tObj.plume.visible = true;
                tObj.node.getWorldPosition(tempTipPos);

                for(let spk=0; spk<2; spk++) {{
                    emitNozzleSpark(
                        tempTipPos.x + (Math.random()-0.5)*0.2,
                        tempTipPos.y + (Math.random()-0.5)*0.2,
                        tempTipPos.z + (Math.random()-0.5)*0.2,
                        -ux * (1.6 + Math.random()*1.8) + (Math.random()-0.5)*0.45,
                        -uy * (1.6 + Math.random()*1.8) + (Math.random()-0.5)*0.3,
                        (Math.random()-0.5)*0.45,
                        0.45 + Math.random()*0.45,
                        10 + Math.floor(Math.random()*12),
                        (Math.random() < 0.4) ? 0xffffff : curSparkHex
                    );
                }}

                if (alt < 32.0 && Math.random() < 0.45) {{
                    emitParticle(
                        tempTipPos.x - ux * 1.5, tempTipPos.y - uy * 1.5, tempTipPos.z,
                        -ux * 0.65 + (Math.random()-0.5)*0.22, -uy * 0.65, (Math.random()-0.5)*0.22,
                        2.8, 19.0, 50, 0.62, 0xf1f5f9, false
                    );
                }}
            }}

            engineBounceLight.intensity = Math.max(0.0, 6.0 - alt * 0.4);
            engineBounceLight.position.set(rx, ry + 3.0, 4.0);

            const gimbalAngle = Math.sin(now * 0.016) * 0.04;
            s1Engines.rotation.z = gimbalAngle;
            s2Engines.rotation.z = gimbalAngle;
        }} else {{
            s1NozzleTips.forEach(t => {{ t.plume.visible = false; }});
            s2NozzleTips.forEach(t => {{ t.plume.visible = false; }});
            boosterNozzleTips.forEach(t => {{ t.plume.visible = false; }});
            engineBounceLight.intensity = 0.0;
        }}

        // 5. 圧縮気体RCS噴射
        const pitchRate = Math.abs(pitch - prevPitch);
        prevPitch = pitch;
        let rcsFiring = false;

        for(let rcs of rcsMountNodes) {{
            const isPulse = (!cfg.is_preview && simT > 2.0 && (pitchRate > 0.0002 || alt > 35.0) && Math.sin(now * 0.025 + rcs.side) > 0.52);
            const isS1Active = (stage1Detached && rcs.isS1 && rcs.side === 1);

            if ((isPulse && !rcs.isS1) || isS1Active) {{
                rcsFiring = true;
                rcs.node.getWorldPosition(tempTipPos);
                const jetDirX = perpX * rcs.side;
                const jetDirY = perpY * rcs.side;
                emitParticle(
                    tempTipPos.x + jetDirX * 0.4, tempTipPos.y + jetDirY * 0.4, tempTipPos.z,
                    jetDirX * (2.2 + Math.random()*1.2), jetDirY * (2.2 + Math.random()*1.2), (Math.random()-0.5)*0.4,
                    0.45, 3.2, 18, 0.85, 0xf0f9ff, false
                );
            }}
        }}
        document.getElementById('hud-rcs').innerText = rcsFiring ? "EXPANDING JET (GN2)" : "NOMINAL";
        document.getElementById('hud-rcs').style.color = rcsFiring ? "#34d399" : "#38bdf8";

        updateDualCameraTracking(simT, elapsedSec, alt, pitch, p0.stage, p0.exploded);
        drawOrbitMap(alt, dRangeKm, p0.exploded);

        // 6. カウントダウン・注水水蒸気・離床
        if (simT < 0.0) {{
            const sec = Math.ceil(Math.abs(simT));
            document.getElementById('tv-timer').innerText = cfg.is_preview ? "PAD INSPECTION" : `T- 00:0${{sec}}.0`;

            // 極低温ベント
            emitParticle(rx + 1.25, ry + 6.0 + s1Len * 0.85, 0, 0.25, 0.04, 0, 0.9, 4.2, 45, 0.35, 0xffffff, false);

            if (simT >= -5.0 && !p0.exploded && !cfg.is_preview) {{
                document.getElementById('hud-deluge').innerText = "FLOWING (WATER DELUGE)";
                document.getElementById('hud-deluge').style.color = "#34d399";
                if (hissGain) hissGain.gain.setTargetAtTime(0.45, actx.currentTime, 0.2);
                for(let i=0; i<6; i++) {{
                    emitParticle(
                        rx + (Math.random()-0.5)*7, 0.8, (Math.random()-0.5)*7,
                        (Math.random()-0.5)*1.2, 0.2 + Math.random()*0.35, (Math.random()-0.5)*1.2,
                        4.5, 18.0, 55, 0.82, 0xf0f9ff, false
                    );
                }}
            }}

            if (simT >= -cfg.ignition_lead && !p0.exploded && !cfg.is_preview) {{
                eventLog.innerText = "> T-3.8s: MAIN ENGINE START SEQUENCE";
                for(let tObj of s1NozzleTips) {{
                    tObj.node.getWorldPosition(tempTipPos);
                    emitNozzleSpark(
                        tempTipPos.x, tempTipPos.y, tempTipPos.z,
                        (Math.random()-0.5)*1.1, -1.0 - Math.random()*1.5, (Math.random()-0.5)*1.1,
                        0.55, 15, 0xfde047
                    );
                }}
            }}

            if (simT >= -3.0 && !p0.exploded && !cfg.is_preview) {{
                camShake = 0.25;
                if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.72, actx.currentTime, 0.1);
                for(let i=0; i<8; i++) {{
                    const side = (i%2 === 0) ? 1 : -1;
                    emitParticle(
                        rx + (Math.random()-0.5)*5, 1.2, (Math.random()-0.5)*5,
                        side * (1.2 + Math.random()*2.2), 0.15 + Math.random()*0.4, (Math.random()-0.5)*1.0,
                        5.5, 32.0, 75, 0.88, 0xf8fafc, false
                    );
                }}
            }}
        }} else if (!p0.exploded) {{
            const m = Math.floor(simT / 60); const s = simT % 60;
            document.getElementById('tv-timer').innerText = `T+ ${{String(m).padStart(2,'0')}}:${{s.toFixed(1).padStart(4,'0')}}`;

            if (simT >= 0 && !voicedEvents.has('liftoff')) {{
                voicedEvents.add('liftoff');
                eventLog.innerText = "> T+0.0s: LIFTOFF OF ORBITAL ARCHITECT";
                announceWebcast("Liftoff. Tower cleared.");
                if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.95, actx.currentTime, 0.1);
                if (crackleGain) crackleGain.gain.setTargetAtTime(0.55, actx.currentTime, 0.1);
            }}

            if (simT < 5.0) {{
                for(let i=0; i<4; i++) {{
                    emitParticle(
                        rx + (Math.random()-0.5)*8, 2.0, (Math.random()-0.5)*8,
                        (Math.random()-0.5)*1.5, 0.2 + Math.random()*0.3, (Math.random()-0.5)*1.5,
                        6.0, 35.0, 70, 0.75, 0xf1f5f9, false
                    );
                }}
            }}
        }}

        // パーティクル更新
        for(let i=0; i<P_MAX; i++) {{
            const p = pool[i]; if (!p.active) continue;
            p.age++;
            if (p.age >= p.maxAge) {{ p.active = false; p.sp.visible = false; continue; }}
            p.sp.position.x += p.vx; p.sp.position.y += p.vy; p.sp.position.z += p.vz;
            const pr = p.age / p.maxAge;
            const curScale = p.s0 + (p.s1 - p.s0) * Math.pow(pr, 0.7);
            p.sp.scale.set(curScale, curScale, 1);
            p.sp.material.opacity = p.o * (1.0 - pr * pr);
        }}

        for(let i=0; i<SPARK_MAX; i++) {{
            const s = sparkPool[i]; if (!s.active) continue;
            s.age++;
            if (s.age >= s.maxAge) {{ s.active = false; s.sp.visible = false; continue; }}
            s.sp.position.x += s.vx; s.sp.position.y += s.vy; s.sp.position.z += s.vz;
            const pr = s.age / s.maxAge;
            s.sp.material.opacity = 1.0 - pr;
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
        if (!p0.exploded && !cfg.is_preview) {{
            document.getElementById('tv-stage-badge').innerText = p0.stage === 1 ? (p0.strapon ? "STAGE 1 + BOOSTERS" : "STAGE 1 CORE ONLY") : "STAGE 2 ORBITAL";
        }}

        // 🎥 2画面同時レンダリング
        renderer.render(scene, camera);
        pipRenderer.render(scene, pipCamera);
    }}
    requestAnimationFrame(animate);

    window.addEventListener('resize', () => {{
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }});
</script>
"""
components.html(html_code, height=980)

# =========================================================================
# 📊 フライト解析レポート
# =========================================================================
if launch_clicked:
    st.markdown("---")
    st.markdown("### 📋 フライトテレメトリ詳細レポート")
    if error_msg:
        st.error(f"⚠️ **ミッション異常終了 (RUD)**: {error_msg}")
    else:
        st.success("🎉 **ミッション完全成功 (SECO & LEO Insertion)**: 全段燃焼および分離シーケンスが正常に推移し、第2段オービターが低軌道投入条件に到達しました。")
