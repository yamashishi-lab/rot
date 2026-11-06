import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect Ultra", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect Ultra")
st.caption("※ 4K実写級：IFT-5タワーキャッチ地上完全追尾・リアル霧状パルスRCS・黒線完全除去版")

# =========================================================================
# 🔬 推進剤・材料・空力パーツ・ブースターデータベース
# =========================================================================
PROPELLANTS = {
    "超高密度サブクール・メタロックス (CH4 / LOX) [Starship王道]": {
        "base_isp_sl": 338, "base_isp_vac": 382, "base_thrust": 2800, "density": 0.85, 
        "flame_hex": 0x60a5fa, "outer_hex": 0x1d4ed8, "spark_hex": 0x93c5fd, "risk": 0.0, "type": "methalox"
    },
    "高精製ロケットグレードケロシン (RP-1 / LOX) [Saturn V / Falcon]": {
        "base_isp_sl": 302, "base_isp_vac": 335, "base_thrust": 1950, "density": 1.03, 
        "flame_hex": 0xfef08a, "outer_hex": 0xea580c, "spark_hex": 0xfde047, "risk": 0.0, "type": "rp1"
    },
    "超極低温スラッシュ・ハイドロロックス (LH2 / LOX) [H3 / SLS]": {
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
    "チタン鍛造極超音速グリッドフィン × 4基 (SpaceX回収仕様)": {"lift_coeff": 0.12, "drag_penalty": 1.05, "mass": 1.2, "flutter_mach": 99.0, "wing_id": "grid"},
    "Starship風 空力エルロンボディフラップ × 4枚": {"lift_coeff": 0.35, "drag_penalty": 1.12, "mass": 2.8, "flutter_mach": 99.0, "wing_id": "starship_flap"},
    "なし (純粋な軸対称弾道ロケット)": {"lift_coeff": 0.0, "drag_penalty": 1.0, "mass": 0.0, "flutter_mach": 99.0, "wing_id": "none"},
    "コンコルド風 ダブルデルタ超音速後退翼": {"lift_coeff": 0.95, "drag_penalty": 1.45, "mass": 7.5, "flutter_mach": 3.8, "wing_id": "delta_wing"}
}

FAIRINGS = {
    "Starship風 窓付き有人クルーノーズコーン": {"mass": 4.2, "cd": 0.22, "heat_limit": 2900, "shape_id": "starship_crew"},
    "バイコニカル炭素複合材クラムシェル (金箔通信衛星内蔵)": {"mass": 2.1, "cd": 0.18, "heat_limit": 2600, "shape_id": "biconic"},
    "有人カプセル ＋ レスキューアボートタワー (LES付)": {"mass": 6.8, "cd": 0.32, "heat_limit": 3200, "shape_id": "abort_tower"}
}

# =========================================================================
# 🎛️ パラメータ設定タブ
# =========================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 第1段 (推進・燃焼・構造)", 
    "🚀 外部ブースター & SpaceXキャッチ機構",
    "🛩️ 空力翼 & 4象限RCS姿勢制御", 
    "🛰️ 第2段 (オービター) & 先端部", 
    "🌊 発射台水冷デリュージ & ガイダンス"
])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=0)
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", list(PUMP_CYCLES.keys()), index=0)
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, 33)
    with c2:
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, 300, step=10)
        s1_eps = st.slider("海面膨張比 (ε: ノズル径連動)", 8, 70, 24, step=1)
    with c3:
        s1_fuel = st.slider("第1段 推進剤充填量 (トン: 胴体長連動)", 100.0, 4500.0, 3400.0, step=50.0)
        s1_mat = st.selectbox("第1段 構造素材", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("外殻等価板厚 (mm)", 1.0, 12.0, 4.2, step=0.1)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        strapon_opt = st.selectbox("ブースター種別クラスタ", list(STRAPON_BOOSTERS.keys()), index=0)
        sep_thrust_factor = st.slider("分離パイロモーター推力倍率 (スロー連動)", 0.5, 3.0, 1.2, step=0.1)
    with c2:
        spacex_return_mode = st.checkbox("🔄 SpaceX型 ブースターRTLS帰還 ＆ チョップスティック・タワーキャッチ (IFT-5再現)", value=True)
        st.caption("※ 分離後、CAM 02が地上追尾局光学トラッカーへ自動切り替わり、着陸・タワーキャッチを完全捕捉。")

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 空力パーツ", list(AERO_WINGS.keys()), index=0)
        angle_of_attack = st.slider("固定取り付け迎角 AoA (deg)", -3.0, 12.0, 0.5, step=0.5)
    with c2:
        rcs_deadband = st.slider("4象限RCS デッドバンド感度 (deg)", 0.2, 5.0, 0.8, step=0.1)
        st.caption("※ 実機同様、姿勢誤差やモーメント要求が発生した瞬間だけ冷ガス窒素(GN2)が霧状パルス噴射されます。")

with tab4:
    c1, c2, c3 = st.columns(3)
    with c1:
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=0)
        s2_cycle = st.selectbox("第2段 ポンプ方式", list(PUMP_CYCLES.keys()), index=0)
        s2_eng_count = st.slider("真空ノズル基数", 1, 9, 6)
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 30, 280, 150, step=5)
    with c2:
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 20.0, 1500.0, 1200.0, step=10.0)
        s2_mat = st.selectbox("第2段 構造素材", list(MATERIALS.keys()), index=0)
        s2_thick = st.slider("第2段 壁厚 (mm)", 0.8, 8.0, 3.0, step=0.1)
    with c3:
        fairing_type = st.selectbox("先端空力カウル / 衛星", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 40.0, 180.0, 75.0, step=5.0)
        payload_mass = st.slider("投入衛星質量 (トン)", 0.5, 120.0, 50.0, step=1.0)

with tab5:
    c1, c2 = st.columns(2)
    with c1:
        water_flow_rate = st.slider("消音注水デリュージ流量 (トン/秒)", 50, 450, 300, step=25)
        ignition_lead_time = st.slider("エンジン先行点火開始 (T-マイナス秒)", 2.5, 6.0, 3.8, step=0.1)
    with c2:
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.3, 15.0, 1.8, step=0.1)
        turn_end_alt = st.slider("水平重力ターン完了高度 (km)", 50.0, 250.0, 120.0, step=5.0)
        turn_exponent = st.slider("ターン曲率指数", 0.3, 2.0, 0.62, step=0.02)
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
s2_spec = calc_stage_specs(s2_prop, s2_cycle, 220, s2_eps, s2_eng_count, s2_fuel, s2_mat, s2_thick)

total_s2_wet = s2_fuel + s2_spec["dry_mass"] + payload_mass + fair_spec["mass"]
total_s1_wet = s1_fuel + s1_spec["dry_mass"] + wing_spec["mass"] + strapon_spec["mass_add"] + strapon_spec["fuel_add"] + total_s2_wet

total_liftoff_thrust = s1_spec["thrust_sl"] + strapon_spec["thrust_add"]
twr_init = total_liftoff_thrust / (total_s1_wet * 9.80665)
dv_s1 = s1_spec["isp_sl"] * 9.80665 * np.log(total_s1_wet / (total_s1_wet - s1_fuel - strapon_spec["fuel_add"]))
dv_s2 = s2_spec["isp_vac"] * 9.80665 * np.log(total_s2_wet / (s2_spec["dry_mass"] + payload_mass))
total_dv = dv_s1 + dv_s2

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("総離床重量 / 離床TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f} ({'離床可能' if twr_init >= 1.05 else '推力不足！'})")
m2.metric("総計算速度増分 (ΔV)", f"{total_dv:.0f} m/s", "LEO投入基準: 9,200 m/s")
m3.metric("構造限界動圧 / 耐G", f"{s1_spec['max_q']:.1f} kPa", f"耐G: {s1_spec['max_g']:.1f} G")
m4.metric("ブースター追加推力", f"+{strapon_spec['thrust_add']:.0f} kN", f"基数: {strapon_spec['count']} 基")

# =========================================================================
# 💥 物理シミュレーション (高度200km〜、秒速7.9km横向き投入 ＆ 超高速アームキャッチ)
# =========================================================================
def run_simulation(preview_only=False):
    if preview_only:
        return [{
            "t": -10.0, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "stage": 1, "fairing": True, "wings": bool(wing_spec["wing_id"] != "none"),
            "strapon": bool(strapon_spec["count"] > 0), "exploded": False, "explosion_type": "NONE",
            "thrust": False, "pitch": 0.0, "mach": 0.0, "event": "PREVIEW",
            "rcs_cmd": 0.0,
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False
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

    b_x, b_y = 0.0, 0.0
    b_vx, b_vy = 0.0, 0.0
    b_active = False
    b_pitch = 0.0
    b_thrust = False
    b_caught = False
    b_fuel = float(s1_fuel * 1000.0 * 0.18) if spacex_return_mode else 0.0

    history = []
    fail_reason = None
    prev_pitch_val = 90.0

    for cd_step in range(21):
        t_cd = -10.0 + cd_step * 0.5
        pre_ignition = bool(t_cd >= -ignition_lead_time)
        history.append({
            "t": float(t_cd), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0,
            "q": 0.0, "g": 1.0, "stage": 1, "fairing": True, "wings": wings_attached,
            "strapon": strapon_attached, "exploded": False, "explosion_type": "NONE",
            "thrust": pre_ignition, "pitch": 0.0, "mach": 0.0, "event": "COUNTDOWN",
            "rcs_cmd": 0.0,
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False
        })

    maxq_passed = False
    supersonic_called = False

    for step in range(3200):
        t = float(step * dt)
        alt = float(y)
        alt_km = float(alt / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))
        mach = v / 340.0

        rho = float(1.225 * np.exp(-alt / 7400.0)) if alt < 140000 else 0.0
        q = float(0.5 * rho * (v**2) / 1000.0)

        # 🎯 軌道プロファイル：垂直→斜め上昇、高度200km到達時にピッチ0度（完全水平・横向き）へ姿勢変更
        if alt_km < turn_start_alt:
            target_pitch_deg = 90.0
        elif alt_km < 200.0:
            prog = (alt_km - turn_start_alt) / (200.0 - turn_start_alt)
            target_pitch_deg = 90.0 * (1.0 - (prog ** turn_exponent))
        else:
            target_pitch_deg = 0.0 # 完全な横向き（水平加速モード）

        extra_pitch_deflection = 0.0
        wing_lift_force = 0.0
        if wings_attached and alt_km < 50.0 and rho > 0.003:
            wing_lift_force = 0.5 * rho * (v**2) * (wing_spec["lift_coeff"] * 24.0) * np.sin(np.radians(angle_of_attack))
            extra_pitch_deflection = (wing_lift_force / 12000.0) * (mach ** 1.3)
            target_pitch_deg -= extra_pitch_deflection

        pitch_deg = max(-5.0, min(90.0, target_pitch_deg))
        pitch_rad = float(np.radians(pitch_deg))
        visual_pitch = float(np.radians(90.0 - pitch_deg))

        pitch_rate = (pitch_deg - prev_pitch_val) / dt
        prev_pitch_val = pitch_deg
        rcs_cmd = float(np.clip(-pitch_rate * 0.45, -1.0, 1.0))

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

            meco_thresh = (s1_fuel * 1000.0 * 0.18) if spacex_return_mode else 0.0
            if fuel_s1_rem <= meco_thresh:
                stage = 2
                strapon_attached = False
                cur_event = "HOT_STAGING"
                thrust = 0.0
                if spacex_return_mode and not b_active:
                    b_active = True
                    b_x, b_y = x, y
                    # 超高速反転ブーストバック
                    b_vx, b_vy = vx * 0.35, vy * 0.70
                    b_pitch = visual_pitch
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

        # 🔄 SpaceX型 RTLS帰還（超高速帰還＆アーム高67.5mで突起ピンによる宙づり静止）
        if b_active and not b_caught:
            b_alt = b_y
            b_rho = float(1.225 * np.exp(-b_alt / 7400.0)) if b_alt < 140000 else 0.0
            b_v = float(np.sqrt(b_vx**2 + b_vy**2))
            b_drag = 0.5 * b_rho * (b_v**2) * 18.0 * 0.85
            b_drag_x = -b_drag * (b_vx / b_v) if b_v > 0 else 0.0
            b_drag_y = -b_drag * (b_vy / b_v) if b_v > 0 else 0.0

            b_thrust_force = 0.0
            b_thrust = False

            # 帰還時間を劇的に短縮する高速ガイダンス
            est_time_to_ground = max(3.5, b_alt / max(180.0, abs(b_vy) + 240.0))
            target_vx = -b_x / est_time_to_ground

            if b_alt > 35000 and b_vx > target_vx and b_fuel > s1_fuel * 1000 * 0.04:
                b_pitch = -1.50
                b_thrust_force = s1_spec["thrust_vac"] * 1000.0 * 1.05
                b_thrust = True
                b_fuel -= (b_thrust_force / (s1_spec["isp_vac"] * g0)) * dt
                b_vx -= (b_thrust_force / (s1_spec["dry_mass"] * 1000.0)) * dt * 3.5
                b_vy += (b_thrust_force / (s1_spec["dry_mass"] * 1000.0)) * dt * 0.05
            elif 14000 < b_alt <= 32000 and b_vy < -420 and b_fuel > s1_fuel * 1000 * 0.015:
                b_pitch = np.clip(-b_vx * 0.0008, -0.25, 0.25)
                b_thrust_force = s1_spec["thrust_vac"] * 1000.0 * 0.95
                b_thrust = True
                b_fuel -= (b_thrust_force / (s1_spec["isp_vac"] * g0)) * dt
                b_vx += (target_vx - b_vx) * 0.45
                b_vy += (b_thrust_force / (s1_spec["dry_mass"] * 1000.0)) * dt * 1.3
            elif b_alt <= 3500:
                b_pitch = np.clip((b_x / 180.0) * 0.12, -0.12, 0.12)
                b_thrust = True
                desired_vy = -max(5.0, (b_alt - 67.5) * 0.22)
                b_vy += (desired_vy - b_vy) * 0.55
                b_vx = -b_x * 0.55
            else:
                b_pitch = np.clip((b_x / 5000.0) * 0.25, -0.3, 0.3)
                b_vx += (target_vx - b_vx) * 0.22

            if not (b_alt <= 3500):
                b_ay = -g0 + b_drag_y / (s1_spec["dry_mass"] * 1000.0)
                b_vy += b_ay * dt

            b_x = max(0.0, b_x + b_vx * dt)
            b_y = max(67.5, b_y + b_vy * dt) # 絶対に67.5m未満（地面）には落ちない

            # アーム高さ（67.5m）到達かつタワー直近で確実にキャッチ＆宙づり静止
            if b_y <= 69.0 and abs(b_x) < 30.0:
                b_caught = True
                b_y = 67.5 # アームに頭部ピンが引っかかり完全に宙づり
                b_x = 0.0
                b_vx = 0.0
                b_vy = 0.0
                b_pitch = 0.0
                b_thrust = False

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
                "mach": mach, "event": "RUD", "rcs_cmd": 0.0,
                "b_x": float(b_x), "b_y": float(b_y), "b_active": b_active, "b_pitch": float(b_pitch), "b_thrust": b_thrust, "b_caught": b_caught
            })
            break

        vx = float(vx + ax * dt)
        vy = float(vy + ay * dt)
        x = float(x + vx * dt)
        y = float(max(0.0, y + vy * dt))

        # 🎯 軌道投入判定：高度200km以上かつ横速度7,900m/s（約28,400km/h）到達
        is_orbit_achieved = bool(alt_km >= 200.0 and vx >= 7900.0 and abs(vy) < 250.0)
        cur_event = "ORBIT" if is_orbit_achieved else cur_event

        history.append({
            "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g,
            "stage": int(stage), "fairing": bool(fairing_attached), "wings": bool(wings_attached),
            "strapon": bool(strapon_attached), "exploded": False, "explosion_type": "NONE",
            "thrust": bool(thrust > 0 and not is_orbit_achieved), "pitch": visual_pitch, "mach": mach, "event": cur_event,
            "rcs_cmd": rcs_cmd,
            "b_x": float(b_x), "b_y": float(b_y), "b_active": b_active, "b_pitch": float(b_pitch), "b_thrust": b_thrust, "b_caught": b_caught
        })

        # 軌道投入完了判定（SpaceX回収モード時はブースターキャッチ完了も確認）
        if is_orbit_achieved:
            if not spacex_return_mode or (spacex_return_mode and b_caught):
                for orbit_step in range(12):
                    t_orb = t + (orbit_step + 1) * dt
                    x_orb = x + vx * (orbit_step + 1) * dt
                    history.append({
                        "t": t_orb, "x": x_orb, "y": y, "alt": alt_km, "v": v, "q": 0.0, "g": 0.0,
                        "stage": 2, "fairing": False, "wings": wings_attached,
                        "strapon": False, "exploded": False, "explosion_type": "NONE", "thrust": False,
                        "pitch": visual_pitch, "mach": mach, "event": "ORBIT", "rcs_cmd": 0.0,
                        "b_x": float(b_x), "b_y": float(b_y), "b_active": b_active, "b_pitch": float(b_pitch), "b_thrust": False, "b_caught": True
                    })
                break

    if not fail_reason and history[-1]["event"] != "ORBIT":
        fail_reason = f"軌道速度未達（燃料枯渇・弾道落下）。高度: {alt_km:.1f} km, 横速度: {vx:.0f} m/s (目標: 7,900 m/s)"

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

btn_label = "🔴 4K中継：Starship & Super Heavy タワーキャッチ開始" if spacex_return_mode else "🔴 4K中継：軌道投入シミュレーション開始"

cb1, cb2 = st.columns([3, 1])
with cb1:
    launch_clicked = st.button(btn_label, use_container_width=True, type="primary")
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
    "sep_thrust": float(sep_thrust_factor),
    "spacex_return": bool(spacex_return_mode),
    "rcs_deadband": float(rcs_deadband)
}

traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
cfg_json = json.dumps(rocket_visual_cfg)
fail_msg_clean = (error_msg or "").replace('"', '\\"').replace("'", "\\'")

# =========================================================================
# 📺 HTML / JS 完全描画テンプレート（動的発射台・アーム開閉・破裂音・宙づり固定版）
# =========================================================================
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        * { box-sizing: border-box; }
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #01040a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none; }
        #canvas-main { width: 100%; height: 100%; display: block; position: absolute; top:0; left:0; z-index: 1; }
        
        /* 📱 CAM 02 (地上光学追尾局 PiPウィンドウ) */
        .pip-container { 
            position: absolute; 
            top: 52px; 
            right: 20px; 
            width: 360px; 
            height: 205px; 
            border: 2px solid rgba(56, 189, 248, 0.95); 
            border-radius: 4px; 
            z-index: 60; 
            box-shadow: 0 14px 45px rgba(0,0,0,0.98); 
            background: #071526; 
            overflow: hidden; 
            cursor: pointer; 
        }
        #canvas-pip { width: 100%; height: 100%; display: block; }
        .pip-tag { 
            position: absolute; 
            top: 6px; 
            left: 8px; 
            font-size: 9px; 
            font-weight: 800; 
            color: #fff; 
            background: rgba(15, 23, 42, 0.94); 
            padding: 3px 6px; 
            border-radius: 2px; 
            letter-spacing: 1px; 
            font-family: monospace; 
            z-index: 65; 
            pointer-events: none; 
            border-left: 2px solid #38bdf8; 
        }
        .pip-alt { 
            position: absolute; 
            bottom: 6px; 
            right: 8px; 
            font-size: 10px; 
            font-family: monospace; 
            color: #38bdf8; 
            font-weight: 700; 
            background: rgba(15, 23, 42, 0.94); 
            padding: 2px 6px; 
            border-radius: 2px; 
            z-index: 65; 
            pointer-events: none; 
        }
        .pip-toggle-hint { 
            position: absolute; 
            top: 6px; 
            right: 8px; 
            font-size: 9px; 
            font-family: monospace; 
            color: #94a3b8; 
            background: rgba(15, 23, 42, 0.94); 
            padding: 3px 6px; 
            border-radius: 2px; 
            z-index: 65; 
            pointer-events: none; 
        }

        /* 🗺️ 精密軌道マップ */
        .hud-orbit { 
            position: absolute; 
            bottom: 86px; 
            left: 24px; 
            width: 320px; 
            background: #030712; 
            border: 1px solid rgba(255, 255, 255, 0.16); 
            border-radius: 4px; 
            padding: 8px 12px; 
            z-index: 50; 
            color: #fff; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.85); 
        }
        #orbit-canvas { width: 296px; height: 64px; background: #020617; border-radius: 2px; border: 1px solid rgba(255,255,255,0.08); display: block; margin-top: 4px; }

        .top-banner { position: absolute; top: 0; left: 0; width: 100%; min-height: 42px; background: #020610; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; padding: 4px 18px; z-index: 20; flex-wrap: wrap; gap: 8px; }
        
        .hud-telemetry { position: absolute; bottom: 0; left: 0; width: 100%; height: 76px; background: #01040a; border-top: 1px solid rgba(255,255,255,0.12); padding: 8px 24px; display: flex; align-items: center; justify-content: space-between; z-index: 20; pointer-events: none; }
        .hud-telemetry > * { pointer-events: auto; }
        .telemetry-row { display: flex; gap: clamp(14px, 2.2vw, 28px); align-items: center; flex-wrap: nowrap; overflow-x: auto; }
        .telemetry-item { flex-shrink: 0; }
        .telemetry-label { font-size: 9px; color: #94a3b8; letter-spacing: 1px; }
        .telemetry-val { color: #fff; font-size: clamp(13px, 1.6vw, 17px); font-weight: 800; font-family: 'Consolas', monospace; }

        .rud-banner { display: none; position: absolute; top: 150px; left: 50%; transform: translateX(-50%); background: #7f1d1d; border: 2px solid #ef4444; border-radius: 4px; padding: 16px 28px; z-index: 70; text-align: center; box-shadow: 0 0 60px rgba(239, 68, 68, 0.7); }

        .complete-banner { display: none; position: absolute; top: 140px; left: 50%; transform: translateX(-50%); background: rgba(6, 78, 59, 0.95); border: 2px solid #10b981; border-radius: 6px; padding: 20px 36px; z-index: 70; text-align: center; box-shadow: 0 0 70px rgba(16, 185, 129, 0.7); }
    </style>
</head>
<body>
    <canvas id="canvas-main"></canvas>

    <!-- 📱 CAM 02 地上光学トラッカーPiP -->
    <div id="pip-box" class="pip-container" title="クリックでPiPの表示/非表示を切り替え">
        <canvas id="canvas-pip"></canvas>
        <div id="pip-tag" class="pip-tag">CAM 02: GROUND OPTICAL TRACKER</div>
        <div id="pip-hud-alt" class="pip-alt">BOOSTER: 0.0 km</div>
        <div id="pip-hint" class="pip-toggle-hint">[CLICK TO TOGGLE]</div>
    </div>

    <div class="top-banner">
        <div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex-shrink: 1;">
            <span id="live-indicator" style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 10px #ef4444; flex-shrink: 0;"></span>
            <span id="webcast-title" style="color: #ffffff; font-weight: 800; font-size: clamp(10px, 1.2vw, 12px); letter-spacing: 1.5px; white-space: nowrap;">4K WEBCAST</span>
            <span style="color: rgba(255,255,255,0.2);">|</span>
            <span id="cam-tag" style="color: #38bdf8; font-size: clamp(9px, 1.1vw, 11px); font-weight: 700; letter-spacing: 1px; font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">CAM 01: CINEMATIC WIDE CHASE</span>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; font-family: monospace; font-size: clamp(9px, 1.1vw, 11px); flex-wrap: wrap;">
            <span style="color: #94a3b8; white-space: nowrap;">ATMOS: <strong id="hud-regime" style="color: #f8fafc;">TROPOSPHERE</strong></span>
            <span style="color: #94a3b8; white-space: nowrap;">GN2 RCS: <strong id="hud-rcs" style="color: #38bdf8;">STANDBY</strong></span>
            <span style="color: #94a3b8; white-space: nowrap;">ARM STATUS: <strong id="hud-arm" style="color: #f59e0b;">STOWED</strong></span>
            <span id="comm-status" style="color: #10b981; white-space: nowrap;">LOCKED</span>
        </div>
    </div>

    <!-- 🗺️ 精密軌道マップ -->
    <div class="hud-orbit" id="hud-orbit-box">
        <div style="font-size: 9px; font-weight: 800; color: #94a3b8; letter-spacing: 1.2px; display: flex; justify-content: space-between;">
            <span>TRAJECTORY & GROUND TRACK</span>
            <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">DOWNRANGE: 0.0 km</span>
        </div>
        <canvas id="orbit-canvas" width="296" height="64"></canvas>
        <div id="event-log" style="margin-top: 4px; font-family: monospace; font-size: 9px; font-weight: 800; color: #34d399; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 3px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
            > [LD] GO FOR TERMINAL COUNTDOWN
        </div>
        <div id="sub-callout" style="font-family: monospace; font-size: 8.5px; color: #93c5fd; margin-top: 1px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
            > Propellant tanks pressurized for flight
        </div>
    </div>

    <!-- 🏁 ミッション完了バナー -->
    <div id="complete-banner" class="complete-banner">
        <div style="color: #6ee7b7; font-size: 20px; font-weight: 900; letter-spacing: 3px; font-family: monospace;">🎉 MISSION COMPLETE 🎉</div>
        <div style="color: #ecfdf5; font-size: 14px; font-weight: 700; margin-top: 8px;">ORBITAL INSERTION (28,400 km/h) & TOWER CATCH ACHIEVED</div>
        <div style="color: #a7f3d0; font-size: 12px; margin-top: 4px; font-family: monospace;">Super Heavy suspended on chopsticks. Starship cruising in Low Earth Orbit.</div>
    </div>

    <div id="rud-banner" class="rud-banner">
        <div style="color: #fff; font-size: 17px; font-weight: 900; letter-spacing: 2.5px; font-family: monospace;">🚨 RAPID UNSCHEDULED DISASSEMBLY (RUD) 🚨</div>
        <div id="rud-desc" style="color: #fecaca; font-size: 13px; font-weight: 600; margin-top: 6px; max-width: 520px; line-height: 1.4;"></div>
    </div>

    <!-- 📊 フロート式テレメトリバー -->
    <div class="hud-telemetry">
        <div style="flex-shrink: 0;">
            <div id="tv-status" style="color: #38bdf8; font-size: 9px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 2px;">COUNTDOWN SEQUENCE</div>
            <div id="tv-timer" style="color: #ffffff; font-size: clamp(20px, 2.6vw, 28px); font-weight: 900; font-family: 'Consolas', monospace; letter-spacing: 2px; text-shadow: 0 0 16px rgba(56, 189, 248, 0.4);">T- 00:10.0</div>
        </div>
        <div class="telemetry-row">
            <div class="telemetry-item">
                <div class="telemetry-label">HORIZ VELOCITY</div>
                <div class="telemetry-val"><span id="tv-mach">M 0.00</span> <span style="font-size: 10px; color: #94a3b8;" id="tv-spd">(0 km/h)</span></div>
            </div>
            <div class="telemetry-item">
                <div class="telemetry-label">ALTITUDE</div>
                <div class="telemetry-val"><span id="tv-alt">0.0</span> <span style="font-size: 10px; color: #94a3b8;">km</span></div>
            </div>
            <div class="telemetry-item">
                <div class="telemetry-label">DYNAMIC PRESSURE</div>
                <div class="telemetry-val"><span id="tv-q">0.0</span> <span style="font-size: 10px; color: #94a3b8;">kPa</span></div>
            </div>
            <div class="telemetry-item">
                <div class="telemetry-label">AXIAL LOAD</div>
                <div class="telemetry-val"><span id="tv-g">1.0</span> <span style="font-size: 10px; color: #94a3b8;">G</span></div>
            </div>
            <div class="telemetry-item">
                <div class="telemetry-label">STAGE CONFIG</div>
                <div id="tv-stage-badge" style="color: #34d399; font-size: clamp(11px, 1.4vw, 14px); font-weight: 800; font-family: 'Consolas', monospace; white-space: nowrap;">PAD READY</div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    try {
        const simData = __SIM_DATA__;
        const simCfg = __SIM_CFG__;
        const failMessage = "__FAIL_MSG__";

        const canvasMain = document.getElementById('canvas-main');
        const canvasPip = document.getElementById('canvas-pip');
        const orbitCvs = document.getElementById('orbit-canvas');
        const octx = orbitCvs.getContext('2d');
        const rudBanner = document.getElementById('rud-banner');
        const completeBanner = document.getElementById('complete-banner');
        const rudDesc = document.getElementById('rud-desc');
        const eventLog = document.getElementById('event-log');
        const subCallout = document.getElementById('sub-callout');

        let isMissionEnded = false;
        let catchPopPlayed = false;

        let pipVisible = true;
        const pipBox = document.getElementById('pip-box');
        const pipHint = document.getElementById('pip-hint');
        pipBox.addEventListener('click', () => {
            pipVisible = !pipVisible;
            canvasPip.style.display = pipVisible ? 'block' : 'none';
            document.getElementById('pip-tag').style.display = pipVisible ? 'block' : 'none';
            document.getElementById('pip-hud-alt').style.display = pipVisible ? 'block' : 'none';
            pipBox.style.height = pipVisible ? '205px' : '32px';
            pipHint.innerText = pipVisible ? '[CLICK TO HIDE]' : '[CLICK TO SHOW]';
        });

        let voiceSynthesizer = window.speechSynthesis;
        function speakCallout(text) {
            if (!voiceSynthesizer) return;
            try {
                voiceSynthesizer.cancel();
                const u = new SpeechSynthesisUtterance(text);
                u.rate = 1.15; u.pitch = 0.95; u.volume = 1.0; u.lang = 'en-US';
                voiceSynthesizer.speak(u);
            } catch(e) {}
        }

        const calloutMilestones = [
            { t: -10.0, main: "> [LD] TERMINAL COUNTDOWN INITIATED", sub: "> Swing arms retracted to pad clear position", spoken: "Terminal countdown initiated" },
            { t: -simCfg.ignition_lead, main: "> [PROP] ENGINE IGNITION SEQUENCE START", sub: "> Turbopumps spin-up in progress", spoken: "Ignition sequence start" },
            { t: 0.0, main: "> [LIFTOFF] VEHICLE HAS CLEARED PAD 39A", sub: "> Pitch and roll program active", spoken: "Liftoff. Tower cleared" },
            { t: 15.0, main: "> [GUIDANCE] GRAVITY TURN TRAJECTORY NOMINAL", sub: "> Pitch over maneuver continuing downrange", spoken: "Trajectory nominal" },
            { t: 45.0, main: "> [AERO] VEHICLE PASSING MACH 1 - SUPERSONIC", sub: "> Transonic buffet levels well within limits", spoken: "Vehicle is supersonic" },
            { t: 65.0, main: "> [AERO] MAXIMUM DYNAMIC PRESSURE (MAX-Q)", sub: "> Main engine throttle bucket applied", spoken: "Max-Q" },
            { t: 130.0, main: "> [PROP] BOOSTER MECO & SEPARATION", sub: "> Booster separation sequence complete", spoken: "Booster separation" },
            { t: 165.0, main: "> [STAGE] FIRST STAGE MECO & HOT STAGING", sub: "> Second stage vacuum ignition confirmed", spoken: "Staging confirmed" },
            { t: 195.0, main: "> [AERO] PAYLOAD FAIRING JETTISON", sub: "> Exo-atmospheric telemetry optimal", spoken: "Fairing separation" },
            { t: 230.0, main: "> [TOWER] CHOPSTICK ARMS EXTENDING FOR CATCH", sub: "> Mechazilla arms deployed to catch position", spoken: "Mechazilla arms deployed for catch" }
        ];

        let calloutTrackIndex = 0;
        function updateFlightCallouts(simT) {
            while (calloutTrackIndex < calloutMilestones.length && simT >= calloutMilestones[calloutTrackIndex].t) {
                const milestone = calloutMilestones[calloutTrackIndex];
                if (eventLog) eventLog.innerText = milestone.main;
                if (subCallout) subCallout.innerText = milestone.sub;
                speakCallout(milestone.spoken);
                calloutTrackIndex++;
            }
        }

        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null, subRumble = null, shockCrackle = null, gasHiss = null;
        function initAudio() {
            if (!actx) {
                actx = new AudioCtx();
                const buf = actx.createBuffer(1, actx.sampleRate * 4, actx.sampleRate);
                const d = buf.getChannelData(0);
                for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

                const rSrc = actx.createBufferSource(); rSrc.buffer = buf; rSrc.loop = true;
                const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 38; lp.Q.value = 5.0;
                subRumble = actx.createGain(); subRumble.gain.value = 0.001;
                rSrc.connect(lp); lp.connect(subRumble); subRumble.connect(actx.destination);
                rSrc.start(0);

                const cSrc = actx.createBufferSource(); cSrc.buffer = buf; cSrc.loop = true;
                const waveShaper = actx.createWaveShaper();
                const curve = new Float32Array(256);
                for (let i = 0; i < 256; i++) {
                    const x = (i * 2) / 256 - 1;
                    curve[i] = Math.sign(x) * Math.pow(Math.abs(x), 0.32);
                }
                waveShaper.curve = curve;
                const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 280; bp.Q.value = 2.8;
                shockCrackle = actx.createGain(); shockCrackle.gain.value = 0.001;
                cSrc.connect(bp); bp.connect(waveShaper); waveShaper.connect(shockCrackle); shockCrackle.connect(actx.destination);
                cSrc.start(0);

                const hSrc = actx.createBufferSource(); hSrc.buffer = buf; hSrc.loop = true;
                const hp = actx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 2400;
                gasHiss = actx.createGain(); gasHiss.gain.value = 0.001;
                hSrc.connect(hp); hp.connect(gasHiss); gasHiss.connect(actx.destination);
                hSrc.start(0);
            }
            if (actx && actx.state === 'suspended') actx.resume();
        }

        ['click', 'touchstart', 'mousemove', 'keydown'].forEach(evt => {
            window.addEventListener(evt, () => { initAudio(); }, { once: true });
        });

        function playHeavySeparationSound() {
            if (!actx) return;
            const now = actx.currentTime;
            const osc = actx.createOscillator();
            const oscGain = actx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(110, now);
            osc.frequency.exponentialRampToValueAtTime(16, now + 0.65);
            oscGain.gain.setValueAtTime(2.2, now);
            oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
            osc.connect(oscGain);
            oscGain.connect(actx.destination);
            osc.start(now);
            osc.stop(now + 0.71);
        }

        // 💥 【改修】爆竹が1個鳴った様な鋭い乾いた破裂音（Snap Firecracker Pop）
        function playFirecrackerSnapSound() {
            if (!actx) return;
            const now = actx.currentTime;

            // 鋭い高域インパクト（爆竹の最初のパチッ・バン音）
            const osc = actx.createOscillator();
            const gain = actx.createGain();
            osc.type = 'square';
            osc.frequency.setValueAtTime(950, now);
            osc.frequency.exponentialRampToValueAtTime(120, now + 0.04);
            gain.gain.setValueAtTime(2.8, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.06);
            osc.connect(gain); gain.connect(actx.destination);
            osc.start(now); osc.stop(now + 0.07);

            // 乾いたホワイトノイズ破裂（余韻なし）
            const noiseBuf = actx.createBuffer(1, Math.floor(actx.sampleRate * 0.12), actx.sampleRate);
            const nd = noiseBuf.getChannelData(0);
            for(let i=0; i<nd.length; i++) nd[i] = (Math.random() * 2 - 1) * Math.exp(-i / (actx.sampleRate * 0.015));
            const nSrc = actx.createBufferSource();
            nSrc.buffer = noiseBuf;
            const nFilter = actx.createBiquadFilter();
            nFilter.type = 'highpass';
            nFilter.frequency.setValueAtTime(800, now);
            const nGain = actx.createGain();
            nGain.gain.setValueAtTime(2.2, now);
            nGain.gain.exponentialRampToValueAtTime(0.001, now + 0.10);
            nSrc.connect(nFilter); nFilter.connect(nGain); nGain.connect(actx.destination);
            nSrc.start(now);
        }

        // =========================================================================
        // 🌍 Three.js シーン ＆ 環境ライティング
        // =========================================================================
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x020813);

        const rendererMain = new THREE.WebGLRenderer({ 
            canvas: canvasMain, antialias: true, powerPreference: "high-performance",
            logarithmicDepthBuffer: true
        });
        rendererMain.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
        rendererMain.setSize(window.innerWidth, window.innerHeight);
        rendererMain.toneMapping = THREE.ACESFilmicToneMapping;
        rendererMain.toneMappingExposure = 1.35;

        const rendererPip = new THREE.WebGLRenderer({ 
            canvas: canvasPip, antialias: true, powerPreference: "default",
            logarithmicDepthBuffer: true
        });
        rendererPip.setPixelRatio(1.0);
        rendererPip.setSize(360, 205);
        rendererPip.toneMapping = THREE.ACESFilmicToneMapping;
        rendererPip.toneMappingExposure = 1.45;

        const cameraMain = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 2.0, 200000);
        const cameraPip = new THREE.PerspectiveCamera(10.0, 360 / 205, 2.0, 200000);

        const sunLight = new THREE.DirectionalLight(0xfffaed, 5.8);
        sunLight.position.set(12000, 18000, 10000);
        scene.add(sunLight);

        const skyAmbient = new THREE.HemisphereLight(0x78a4c8, 0x0d141e, 1.4);
        scene.add(skyAmbient);

        const engineBounceLight = new THREE.PointLight(simCfg.flame_hex, 0.0, 800, 2.2);
        scene.add(engineBounceLight);

        const pipTrackingSpot = new THREE.DirectionalLight(0xffffff, 3.2);
        scene.add(pipTrackingSpot);

        // スカイドーム
        const skyDomeGeo = new THREE.SphereGeometry(180000, 24, 16);
        const skyDomeMat = new THREE.MeshBasicMaterial({ color: 0x0a1c30, side: THREE.BackSide, depthWrite: false });
        const skyDome = new THREE.Mesh(skyDomeGeo, skyDomeMat);
        scene.add(skyDome);

        const starGeo = new THREE.BufferGeometry();
        const starPos = new Float32Array(2000 * 3);
        for(let i=0; i<2000*3; i+=3) {
            const rad = 170000;
            const u = Math.random(), v = Math.random();
            const th = u * 2.0 * Math.PI, ph = Math.acos(2.0 * v - 1.0);
            starPos[i] = rad * Math.sin(ph) * Math.cos(th);
            starPos[i+1] = rad * Math.sin(ph) * Math.sin(th);
            starPos[i+2] = rad * Math.cos(ph);
        }
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        const starMat = new THREE.PointsMaterial({ size: 2.0, color: 0xffffff, transparent: true, opacity: 0.25 });
        scene.add(new THREE.Points(starGeo, starMat));

        // 沿岸ランドスケープ
        const landscapeGroup = new THREE.Group();
        scene.add(landscapeGroup);

        const coastPlane = new THREE.Mesh(
            new THREE.PlaneGeometry(60000, 60000),
            new THREE.MeshStandardMaterial({ color: 0x141f16, roughness: 0.95 })
        );
        coastPlane.rotation.x = -Math.PI / 2;
        coastPlane.position.set(-2500, -0.5, 0);
        landscapeGroup.add(coastPlane);

        const oceanMesh = new THREE.Mesh(
            new THREE.PlaneGeometry(80000, 80000), 
            new THREE.MeshStandardMaterial({ color: 0x031d33, roughness: 0.1, metalness: 0.9 })
        );
        oceanMesh.rotation.x = -Math.PI / 2;
        oceanMesh.position.set(22000, -12.0, 0);
        landscapeGroup.add(oceanMesh);

        // =========================================================================
        // 🏗️ 【ロケットごとに変化する動的発射台 ＆ スイングアーム機構】
        // =========================================================================
        const pad = new THREE.Group();
        scene.add(pad);

        const isStarshipPad = (simCfg.s1_mat === 'ss');
        const isSaturnPad = (simCfg.s1_mat === 'saturn' || simCfg.s1_mat === 'al');

        const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x181e28, metalness: 0.9, roughness: 0.3 });
        const concreteMat = new THREE.MeshStandardMaterial({ color: 0x333b47, roughness: 0.95 });
        const towerColorMat = isSaturnPad 
            ? new THREE.MeshStandardMaterial({ color: 0xb91c1c, metalness: 0.6, roughness: 0.4 }) // サターン/SLS赤トラス
            : darkSteelMat;

        const groundPlate = new THREE.Mesh(new THREE.CylinderGeometry(110, 125, 3.0, 32), concreteMat);
        groundPlate.position.y = 1.0;
        pad.add(groundPlate);

        const olmRing = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 4.2, 2.2, 24), darkSteelMat);
        olmRing.position.y = 5.2;
        pad.add(olmRing);

        const towerGroup = new THREE.Group();
        towerGroup.position.set(-11.5, 0, 0);
        pad.add(towerGroup);

        const towerHeight = isSaturnPad ? 160.0 : 145.0;
        const towerMain = new THREE.Mesh(new THREE.BoxGeometry(6.2, towerHeight, 6.2), towerColorMat);
        towerMain.position.y = towerHeight / 2;
        towerGroup.add(towerMain);

        // チョップスティック・スイングアーム機構（開閉ギミック）
        const chopstickGroup = new THREE.Group();
        chopstickGroup.position.set(0, 67.5, 0);
        towerGroup.add(chopstickGroup);

        const armLeftPivot = new THREE.Group();
        armLeftPivot.position.set(3.1, 0, 2.2);
        chopstickGroup.add(armLeftPivot);

        const armLeft = new THREE.Mesh(new THREE.BoxGeometry(16.0, 2.2, 1.3), darkSteelMat);
        armLeft.position.set(8.0, 0, 0);
        armLeftPivot.add(armLeft);

        const armRightPivot = new THREE.Group();
        armRightPivot.position.set(3.1, 0, -2.2);
        chopstickGroup.add(armRightPivot);

        const armRight = new THREE.Mesh(new THREE.BoxGeometry(16.0, 2.2, 1.3), darkSteelMat);
        armRight.position.set(8.0, 0, 0);
        armRightPivot.add(armRight);

        // 初期状態：打ち上げ前は発射台から外側に格納（オープン）
        armLeftPivot.rotation.y = -0.75;
        armRightPivot.rotation.y = 0.75;

        // =========================================================================
        // 🎨 素材別動的シェーダーマテリアル
        // =========================================================================
        function getRealisticMaterial(matId, hasHeatshield) {
            let color = 0xd5dce6;
            let metal = 0.92;
            let rough = 0.16;

            if (matId === 'al') {
                color = 0xc2410c; metal = 0.15; rough = 0.65;
            } else if (matId === 'saturn') {
                color = 0xf8fafc; metal = 0.25; rough = 0.35;
            } else if (matId === 'cf') {
                color = 0x111317; metal = 0.08; rough = 0.78;
            } else if (matId === 'inconel') {
                color = 0x3f3f46; metal = 0.85; rough = 0.32;
            }

            return new THREE.MeshStandardMaterial({
                color: color,
                metalness: metal,
                roughness: rough
            });
        }

        // =========================================================================
        // 🔥 ノズルバーナーコーン生成
        // =========================================================================
        function createFlameTexture() {
            const cvs = document.createElement('canvas'); cvs.width = 64; cvs.height = 256;
            const ctx = cvs.getContext('2d');
            const g = ctx.createLinearGradient(0, 0, 0, 256);
            g.addColorStop(0, 'rgba(255, 255, 255, 1.0)');
            g.addColorStop(0.15, 'rgba(255, 240, 180, 0.95)');
            g.addColorStop(0.5, 'rgba(56, 189, 248, 0.6)');
            g.addColorStop(0.85, 'rgba(29, 78, 216, 0.25)');
            g.addColorStop(1.0, 'rgba(0, 0, 0, 0.0)');
            ctx.fillStyle = g; ctx.fillRect(0, 0, 64, 256);
            return new THREE.CanvasTexture(cvs);
        }
        const sharedFlameTex = createFlameTexture();

        const s1NozzleTips = [];
        const s2NozzleTips = [];
        const boosterNozzleTips = [];

        const inconelNozzleMat = new THREE.MeshStandardMaterial({ 
            color: 0x222730, metalness: 0.95, roughness: 0.25, side: THREE.DoubleSide 
        });

        function buildFullDetailedEngineCluster(parent, count, basePosY, epsScale, tipArray, jetLen, flameHex) {
            const group = new THREE.Group();
            group.position.y = basePosY;
            const bellH = 1.2 * epsScale;
            const bellW = 0.22 * Math.pow(epsScale, 0.65);

            const nozzleGeo = new THREE.CylinderGeometry(0.1, bellW * 2.0, bellH, 12, 1, true);
            nozzleGeo.translate(0, -bellH / 2, 0);

            const flameMat = new THREE.MeshBasicMaterial({
                map: sharedFlameTex,
                color: flameHex,
                transparent: true,
                opacity: 0.95,
                blending: THREE.AdditiveBlending,
                depthWrite: false,
                side: THREE.DoubleSide
            });

            const flameGeo = new THREE.ConeGeometry(bellW * 3.2, jetLen, 8, 1, true);
            flameGeo.translate(0, -jetLen / 2, 0);

            const enginePositions = [];
            if (count === 33) {
                for(let i=0; i<3; i++) {
                    const a = (i / 3) * Math.PI * 2;
                    enginePositions.push({ x: Math.cos(a) * 0.24, z: Math.sin(a) * 0.24, isCenter: true });
                }
                for(let i=0; i<10; i++) {
                    const a = (i / 10) * Math.PI * 2;
                    enginePositions.push({ x: Math.cos(a) * 0.58, z: Math.sin(a) * 0.58, isCenter: false });
                }
                for(let i=0; i<20; i++) {
                    const a = (i / 20) * Math.PI * 2;
                    enginePositions.push({ x: Math.cos(a) * 0.94, z: Math.sin(a) * 0.94, isCenter: false });
                }
            } else if (count === 1) {
                enginePositions.push({ x: 0, z: 0, isCenter: true });
            } else {
                for(let i=0; i<count; i++) {
                    const r = (count > 6 && i < 3) ? 0.3 : 0.82;
                    const a = (i / count) * Math.PI * 2;
                    enginePositions.push({ x: Math.cos(a) * r, z: Math.sin(a) * r, isCenter: (i < 3) });
                }
            }

            for(let pos of enginePositions) {
                const engUnit = new THREE.Group();
                engUnit.position.set(pos.x, 0, pos.z);

                const bell = new THREE.Mesh(nozzleGeo, inconelNozzleMat);
                engUnit.add(bell);

                const tipObj = new THREE.Object3D();
                tipObj.position.set(0, -bellH, 0);

                const flameMesh = new THREE.Mesh(flameGeo, flameMat);
                tipObj.add(flameMesh);
                engUnit.add(tipObj);

                tipArray.push({ node: tipObj, plume: flameMesh, isCenter: pos.isCenter });
                group.add(engUnit);
            }
            parent.add(group);
            return group;
        }

        // =========================================================================
        // 🚀 ロケット本体モデル構築
        // =========================================================================
        const rocket = new THREE.Group();
        rocket.position.y = 6.0;
        scene.add(rocket);

        const s1Mat = getRealisticMaterial(simCfg.s1_mat, false);
        const s2Mat = getRealisticMaterial(simCfg.s2_mat, true);

        const s1Len = simCfg.s1_len;
        const interLen = 2.2;
        const s2Len = simCfg.s2_len;
        const s2BaseY = s1Len + interLen;

        const s1Group = new THREE.Group();
        rocket.add(s1Group);

        const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, 32), s1Mat);
        s1Body.position.y = s1Len / 2;
        s1Group.add(s1Body);

        for(let ry = 2.5; ry < s1Len; ry += 3.8) {
            const ring = new THREE.Mesh(new THREE.TorusGeometry(1.125, 0.015, 6, 24), darkSteelMat);
            ring.rotation.x = Math.PI / 2;
            ring.position.y = ry;
            s1Group.add(ring);
        }

        // 🎯 ブースター頭部のリフティング突起ピン（左右4.4m幅でアーム上に確実に引っかかる）
        const catchPins = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 4.4, 16), darkSteelMat);
        catchPins.rotation.z = Math.PI / 2;
        catchPins.position.set(0, s1Len - 0.9, 0);
        s1Group.add(catchPins);

        const s1EpsScale = 0.75 + (simCfg.s1_eps / 70.0) * 0.75;
        const s1Engines = buildFullDetailedEngineCluster(s1Group, simCfg.s1_eng, 0.0, s1EpsScale, s1NozzleTips, 28.0, simCfg.flame_hex);

        const wingsGroup = new THREE.Group();
        s1Group.add(wingsGroup);
        const aoaRad = (simCfg.aoa * Math.PI) / 180.0;

        if (simCfg.wing_id === 'grid') {
            for(let i=0; i<4; i++) {
                const ang = (i / 4) * Math.PI * 2 + Math.PI / 4;
                const gfFrame = new THREE.Group();
                gfFrame.position.set(Math.cos(ang)*1.22, s1Len - 1.1, Math.sin(ang)*1.22);
                gfFrame.rotation.y = -ang; gfFrame.rotation.z = aoaRad;
                const gridBox = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.14, 1.25), darkSteelMat);
                gridBox.position.x = 0.62; gfFrame.add(gridBox);
                wingsGroup.add(gfFrame);
            }
        } else if (simCfg.wing_id === 'starship_flap') {
            for(let side of [-1, 1]) {
                const aftFlap = new THREE.Mesh(new THREE.BoxGeometry(1.6, 4.2, 0.12), darkSteelMat);
                aftFlap.position.set(side * 1.7, 2.8, 0); aftFlap.rotation.z = side * 0.15; aftFlap.rotation.x = aoaRad;
                wingsGroup.add(aftFlap);
            }
        } else if (simCfg.wing_id === 'delta_wing') {
            for(let side of [-1, 1]) {
                const wingShape = new THREE.Shape();
                wingShape.moveTo(0, 0);
                wingShape.lineTo(side * 4.8, -1.8);
                wingShape.lineTo(side * 4.2, -6.5);
                wingShape.lineTo(0, -5.2);
                const deltaMesh = new THREE.Mesh(new THREE.ShapeGeometry(wingShape), s1Mat);
                deltaMesh.position.set(0, s1Len * 0.45, 0);
                wingsGroup.add(deltaMesh);
            }
        }

        const boosterUnits = [];
        if (simCfg.strapon_count > 0 && simCfg.strapon_type !== 'none') {
            const sCount = simCfg.strapon_count;
            const isSRB = (simCfg.strapon_type === 'srb');
            const isSoyuz = (simCfg.strapon_type === 'soyuz');
            const bMat = isSRB ? new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4 }) : s1Mat;

            for(let i=0; i<sCount; i++) {
                const angle = (i / sCount) * Math.PI * 2;
                const distR = isSoyuz ? 2.3 : 2.15;
                const bx = Math.cos(angle) * distR, bz = Math.sin(angle) * distR;
                const bUnit = new THREE.Group();
                bUnit.position.set(bx, 0, bz);
                const bLen = s1Len * (isSoyuz ? 0.75 : 0.84);
                
                const topR = isSoyuz ? 0.42 : 0.68;
                const botR = isSoyuz ? 0.78 : 0.68;
                const bBody = new THREE.Mesh(new THREE.CylinderGeometry(topR, botR, bLen, 24), bMat);
                bBody.position.y = bLen / 2;
                bUnit.add(bBody);

                const bNose = new THREE.Mesh(new THREE.ConeGeometry(topR, 2.2, 24), bMat);
                bNose.position.y = bLen + 1.1;
                bUnit.add(bNose);

                if (isSRB) {
                    for(let seg = 1; seg <= 4; seg++) {
                        const ring = new THREE.Mesh(new THREE.CylinderGeometry(0.70, 0.70, 0.18, 24), darkSteelMat);
                        ring.position.y = (bLen / 5) * seg;
                        bUnit.add(ring);
                    }
                }

                const localTips = [];
                buildFullDetailedEngineCluster(bUnit, 1, 0, 1.0, localTips, 24.0, simCfg.flame_hex);
                localTips.forEach(t => boosterNozzleTips.push(t));

                rocket.add(bUnit);
                boosterUnits.push({
                    mesh: bUnit, angle: angle, baseX: bx, baseZ: bz,
                    detached: false, vx: 0, vy: 0, vz: 0, rx: 0, rz: 0, bLen: bLen, tips: localTips
                });
            }
        }

        const s2Group = new THREE.Group();
        s2Group.position.y = s2BaseY;
        rocket.add(s2Group);

        const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, 32), s2Mat);
        s2Body.position.y = s2Len / 2;
        s2Group.add(s2Body);

        const s2EpsScale = 1.0 + (simCfg.s2_eps / 280.0) * 1.1;
        const s2Engines = buildFullDetailedEngineCluster(s2Group, simCfg.s2_eng, 0.0, s2EpsScale, s2NozzleTips, 32.0, simCfg.s2_flame_hex);
        s2NozzleTips.forEach(t => { t.plume.visible = false; });

        const payloadGroup = new THREE.Group();
        payloadGroup.position.y = s2Len + 1.8;
        s2Group.add(payloadGroup);
        const satBus = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 2.4, 16), goldFoilMat);
        payloadGroup.add(satBus);

        const fairingHalves = [];
        if (simCfg.fairing_shape === 'abort_tower') {
            const capMesh = new THREE.Mesh(new THREE.ConeGeometry(1.14, 2.8, 24), s2Mat);
            capMesh.position.y = s2Len + 1.4;
            s2Group.add(capMesh);

            const towerSpike = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.14, 3.8, 12), darkSteelMat);
            towerSpike.position.y = s2Len + 4.2;
            s2Group.add(towerSpike);
        } else {
            const ogivePts = [];
            const noseH = (simCfg.fairing_shape === 'biconic') ? 6.2 : 5.4;
            for(let i=0; i<=16; i++) {
                const t = i / 16;
                ogivePts.push(new THREE.Vector2(Math.max(0.01, 1.12 * Math.pow(1.0 - Math.pow(t, 1.65), 0.72)), t * noseH));
            }
            for(let side of [-1, 1]) {
                const halfGeo = new THREE.LatheGeometry(ogivePts, 16, (side === 1) ? 0 : Math.PI, Math.PI);
                const halfMesh = new THREE.Mesh(halfGeo, s2Mat);
                halfMesh.position.y = s2Len;
                s2Group.add(halfMesh);
                fairingHalves.push({ mesh: halfMesh, side: side, detached: false, vx: 0, vy: 0, rotZ: 0 });
            }
        }

        // =========================================================================
        // 🛰️ 4象限パルスRCSスラスター
        // =========================================================================
        const rcsNozzles = [];
        const rcsDirs = [
            { id: "+Pitch", dx: -1, dy:  0, dz:  0, rotZ:  Math.PI / 2 },
            { id: "-Pitch", dx:  1, dy:  0, dz:  0, rotZ: -Math.PI / 2 },
            { id: "+Yaw",   dx:  0, dy:  0, dz: -1, rotX: -Math.PI / 2 },
            { id: "-Yaw",   dx:  0, dy:  0, dz:  1, rotX:  Math.PI / 2 }
        ];

        const rcsConeGeo = new THREE.ConeGeometry(0.42, 2.6, 12, 1, true);
        rcsConeGeo.translate(0, 1.3, 0);

        function createRcsJetUnit(parent, posX, posY, posZ, dir, isS1) {
            const mount = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.38, 0.22), darkSteelMat);
            mount.position.set(posX, posY, posZ);
            parent.add(mount);

            const jetMat = new THREE.MeshBasicMaterial({
                color: 0xf0f9ff,
                transparent: true,
                opacity: 0.0,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });
            const jetMesh = new THREE.Mesh(rcsConeGeo, jetMat);
            if (dir.rotZ) jetMesh.rotation.z = dir.rotZ;
            if (dir.rotX) jetMesh.rotation.x = dir.rotX;
            mount.add(jetMesh);

            return { mount, jetMesh, jetMat, dir, isS1, intensity: 0.0 };
        }

        for(let d of rcsDirs) {
            rcsNozzles.push(createRcsJetUnit(s2Group, d.dx * 1.16, s2Len - 0.7, d.dz * 1.16, d, false));
            rcsNozzles.push(createRcsJetUnit(s1Group, d.dx * 1.16, s1Len - 0.8, d.dz * 1.16, d, true));
        }

        // =========================================================================
        // 💨 パーティクルプール
        // =========================================================================
        function createCloudTexture() {
            const c = document.createElement('canvas'); c.width = 128; c.height = 128;
            const ctx = c.getContext('2d');
            const g = ctx.createRadialGradient(64, 64, 4, 64, 64, 64);
            g.addColorStop(0, 'rgba(255,255,255,0.95)');
            g.addColorStop(0.35, 'rgba(240,248,255,0.7)');
            g.addColorStop(0.75, 'rgba(200,215,230,0.3)');
            g.addColorStop(1, 'rgba(180,200,220,0)');
            ctx.fillStyle = g; ctx.fillRect(0,0,128,128);
            return new THREE.CanvasTexture(c);
        }
        function createSparkTexture() {
            const c = document.createElement('canvas'); c.width = 32; c.height = 32;
            const ctx = c.getContext('2d');
            const g = ctx.createRadialGradient(16,16,1, 16,16,15);
            g.addColorStop(0, 'rgba(255,255,255,1)');
            g.addColorStop(0.4, 'rgba(255,220,120,0.95)');
            g.addColorStop(1, 'rgba(255,40,0,0)');
            ctx.fillStyle = g; ctx.fillRect(0,0,32,32);
            return new THREE.CanvasTexture(c);
        }

        const cloudTex = createCloudTexture();
        const sparkTex = createSparkTexture();

        const P_MAX = 500;
        const pool = [];
        const pGroup = new THREE.Group(); scene.add(pGroup);
        for(let i=0; i<P_MAX; i++) {
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: cloudTex, transparent: true, opacity: 0, depthWrite: false }));
            sp.visible = false; pGroup.add(sp);
            pool.push({ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 5, o: 0.8 });
        }
        let pIdx = 0;
        function emitParticle(x, y, z, vx, vy, vz, s0, s1, life, opacity, hexColor, additive=false) {
            const p = pool[pIdx]; pIdx = (pIdx + 1) % P_MAX;
            p.active = true; p.sp.visible = true;
            p.sp.position.set(x, Math.max(1.2, y), z);
            p.vx = vx; p.vy = vy; p.vz = vz;
            p.age = 0; p.maxAge = life; p.s0 = s0; p.s1 = s1; p.o = opacity;
            p.sp.material.color.setHex(hexColor);
            p.sp.material.blending = additive ? THREE.AdditiveBlending : THREE.NormalBlending;
        }

        const SPARK_MAX = 180;
        const sparkPool = [];
        const sparkGroup = new THREE.Group(); scene.add(sparkGroup);
        for(let i=0; i<SPARK_MAX; i++) {
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: sparkTex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
            sp.visible = false; sparkGroup.add(sp);
            sparkPool.push({ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, size: 0.5 });
        }
        let sIdx = 0;
        function emitNozzleSpark(x, y, z, vx, vy, vz, size, life, hexCol) {
            const s = sparkPool[sIdx]; sIdx = (sIdx + 1) % SPARK_MAX;
            s.active = true; s.sp.visible = true;
            s.sp.position.set(x, Math.max(1.2, y), z);
            s.vx = vx; s.vy = vy; s.vz = vz;
            s.age = 0; s.maxAge = life; s.size = size;
            s.sp.scale.set(size, size * 1.8, 1);
            s.sp.material.color.setHex(hexCol);
            s.sp.material.opacity = 1.0;
        }

        const tempTipPos = new THREE.Vector3();
        const tempRcsPos = new THREE.Vector3();

        // =========================================================================
        // 📊 精密リアルタイム軌道マップ
        // =========================================================================
        function drawPrecisionOrbitMap(curAltKm, curDRangeKm, exploded, isOrbit) {
            if (!orbitCvs || !octx) return;
            const w = 296, h = 64;
            octx.save();
            octx.setTransform(1, 0, 0, 1, 0, 0);
            octx.fillStyle = '#020617';
            octx.fillRect(0, 0, w, h);

            const groundY = 52.0;
            const startX = 20.0;

            octx.beginPath();
            octx.moveTo(startX - 10, groundY);
            octx.lineTo(w - 10, groundY);
            octx.strokeStyle = '#1e293b';
            octx.lineWidth = 1.5;
            octx.stroke();

            const karmanY = groundY - (100.0 / 220.0) * 42.0;
            octx.setLineDash([3, 4]);
            octx.beginPath();
            octx.moveTo(startX, karmanY);
            octx.lineTo(w - 10, karmanY);
            octx.strokeStyle = 'rgba(56, 189, 248, 0.25)';
            octx.lineWidth = 1.0;
            octx.stroke();
            octx.setLineDash([]);

            octx.fillStyle = '#10b981';
            octx.fillRect(startX - 2, groundY - 4, 4, 4);

            const maxDRange = 1400.0;
            const maxAlt = 220.0;
            const curPx = startX + Math.min(w - startX - 20, Math.max(0, (curDRangeKm / maxDRange) * (w - startX - 20)));
            const curPy = groundY - Math.min(46.0, Math.max(0, (curAltKm / maxAlt) * 42.0));

            octx.beginPath();
            octx.moveTo(startX, groundY);
            octx.quadraticCurveTo(startX + (curPx - startX) * 0.35, groundY, curPx, curPy);
            octx.strokeStyle = exploded ? '#ef4444' : (isOrbit ? '#34d399' : '#38bdf8');
            octx.lineWidth = 2.0;
            octx.stroke();

            octx.fillStyle = exploded ? '#dc2626' : (isOrbit ? '#10b981' : '#38bdf8');
            octx.beginPath();
            octx.arc(curPx, curPy, 3.5, 0, Math.PI * 2);
            octx.fill();

            octx.restore();
        }

        // =========================================================================
        // 🎥 CAM 02 地上固定光学トラッキング（アームキャッチ完全追従）
        // =========================================================================
        const groundTrackerStationPos = new THREE.Vector3(260.0, 14.0, 240.0);
        const towerCloseupPos = new THREE.Vector3(24.0, 70.0, 36.0);

        const currentPipCamPos = new THREE.Vector3().copy(groundTrackerStationPos);
        const currentPipLookTarget = new THREE.Vector3();

        function renderGroundOpticalTracker(isBoosterMode, bX, bY, bCaught, mainRocketPos) {
            let targetPos = new THREE.Vector3();
            let desiredCamPos = groundTrackerStationPos;
            let targetFov = 10.0;

            if (isBoosterMode) {
                targetPos.set(bX * 0.1, bY * 0.1 + s1Len * 0.85, 0);
                const dist = groundTrackerStationPos.distanceTo(targetPos);

                if (bCaught) {
                    desiredCamPos = towerCloseupPos;
                    targetFov = 28.0;
                    document.getElementById('pip-tag').innerText = "CAM 02: MECHAZILLA (CHOPSTICKS SECURED)";
                    document.getElementById('pip-hud-alt').innerText = "SUSPENDED ON ARMS (ENGINES OFF)";
                } else if (bY <= 4000) {
                    if (bY <= 300) {
                        const blend = Math.max(0.0, Math.min(1.0, (300.0 - bY) / 300.0));
                        desiredCamPos = new THREE.Vector3().lerpVectors(groundTrackerStationPos, towerCloseupPos, blend * 0.9);
                        targetFov = 18.0 + (bY / 300.0) * 8.0;
                    } else {
                        desiredCamPos = groundTrackerStationPos;
                        targetFov = Math.max(5.5, Math.min(22.0, (dist / 18.0)));
                    }
                    document.getElementById('pip-tag').innerText = "CAM 02: GROUND OPTICAL (TOWER APPROACH)";
                    document.getElementById('pip-hud-alt').innerText = `BOOSTER ALT: ${(bY / 1000.0).toFixed(2)} km`;
                } else {
                    desiredCamPos = groundTrackerStationPos;
                    targetFov = Math.max(1.8, Math.min(9.0, (dist / 130.0)));
                    document.getElementById('pip-tag').innerText = "CAM 02: KINETO TRACKER (SUPER HEAVY RTLS)";
                    document.getElementById('pip-hud-alt').innerText = `BOOSTER ALT: ${(bY / 1000.0).toFixed(1)} km`;
                }
            } else {
                targetPos.copy(mainRocketPos);
                targetPos.y += s1Len * 0.5;
                desiredCamPos = groundTrackerStationPos;
                const dist = groundTrackerStationPos.distanceTo(mainRocketPos);
                targetFov = Math.max(4.0, Math.min(26.0, (dist / 18.0)));
                document.getElementById('pip-tag').innerText = "CAM 02: GROUND OPTICAL (PAD 39A)";
                document.getElementById('pip-hud-alt').innerText = `ALT: ${(mainRocketPos.y * 0.01).toFixed(1)} km`;
            }

            currentPipCamPos.lerp(desiredCamPos, 0.14);
            currentPipLookTarget.lerp(targetPos, 0.28);

            cameraPip.position.copy(currentPipCamPos);
            cameraPip.lookAt(currentPipLookTarget);
            cameraPip.fov = cameraPip.fov + (targetFov - cameraPip.fov) * 0.14;
            cameraPip.updateProjectionMatrix();

            pipTrackingSpot.position.set(currentPipLookTarget.x + 80, currentPipLookTarget.y + 100, currentPipLookTarget.z + 80);
            pipTrackingSpot.target.position.copy(currentPipLookTarget);
            pipTrackingSpot.target.updateMatrixWorld();

            const prevSkyColor = skyDomeMat.color.getHex();
            const prevAmbientIntensity = skyAmbient.intensity;
            skyDomeMat.color.setHex(0x1a3a60);
            skyAmbient.intensity = 2.2;

            rendererPip.render(scene, cameraPip);

            skyDomeMat.color.setHex(prevSkyColor);
            skyAmbient.intensity = prevAmbientIntensity;
        }

        // =========================================================================
        // ⏱️ アニメーション・メインループ
        // =========================================================================
        const tStart = performance.now();
        let boosterDetached = false;
        let stage1Detached = false;
        let fairingDetached = false;
        let prevRcsCmdVal = 0.0;
        let camShake = 0.0;
        const activeFocusWorld = new THREE.Vector3();
        const smoothOffset = new THREE.Vector3(75.0, 26.0, 145.0);

        function animate(now) {
            if (isMissionEnded) return;

            requestAnimationFrame(animate);

            const elapsedSec = (now - tStart) / 1000.0;
            const simT = simCfg.is_preview ? -10.0 : (-10.0 + elapsedSec);

            if (!simCfg.is_preview) {
                updateFlightCallouts(simT);
            }

            let idx = 0;
            while (idx < simData.length - 1 && simData[idx + 1].t <= simT) idx++;
            const nIdx = Math.min(idx + 1, simData.length - 1);
            const p0 = simData[idx], p1 = simData[nIdx];
            const a = (p1.t > p0.t) ? Math.max(0, Math.min(1, (simT - p0.t) / (p1.t - p0.t))) : 0;

            let rx = (p0.x + (p1.x - p0.x) * a) * 0.1;
            let ry = (p0.y + (p1.y - p0.y) * a) * 0.1;
            let alt = p0.alt + (p1.alt - p0.alt) * a;
            let vel = p0.v + (p1.v - p0.v) * a;
            let q = p0.q + (p1.q - p0.q) * a;
            let pitch = p0.pitch + (p1.pitch - p0.pitch) * a;
            let mach = p0.mach + (p1.mach - p0.mach) * a;
            let accG = p0.g + (p1.g - p0.g) * a;
            let rcsCommand = p0.rcs_cmd + (p1.rcs_cmd - p0.rcs_cmd) * a;

            let bX = p0.b_x + (p1.b_x - p0.b_x) * a;
            let bY = p0.b_y + (p1.b_y - p0.b_y) * a;
            let bPitch = p0.b_pitch + (p1.b_pitch - p0.b_pitch) * a;

            const dRangeKm = (rx * 10.0) / 1000.0;

            rocket.position.set(rx, ry + 6.0, 0);
            rocket.rotation.z = -pitch;
            rocket.updateMatrixWorld(true);

            starMat.opacity = Math.min(0.95, Math.max(0.02, (alt - 15.0) / 60.0));
            skyDomeMat.color.setHex((alt > 65.0) ? 0x020815 : 0x0a1c30);

            const ux = Math.sin(pitch), uy = Math.cos(pitch);
            const perpX = Math.cos(pitch), perpY = -Math.sin(pitch);

            // 1. 外部ブースター分離
            if (!p0.strapon && !boosterDetached && boosterUnits.length > 0 && !simCfg.is_preview) {
                boosterDetached = true;
                playHeavySeparationSound();
                camShake = 0.25;

                for(let b of boosterUnits) {
                    b.detached = true;
                    b.tips.forEach(t => { t.plume.visible = false; });

                    const worldPos = new THREE.Vector3();
                    const worldQuat = new THREE.Quaternion();
                    b.mesh.getWorldPosition(worldPos);
                    b.mesh.getWorldQuaternion(worldQuat);

                    scene.attach(b.mesh);
                    b.mesh.position.copy(worldPos);
                    b.mesh.quaternion.copy(worldQuat);

                    const outX = Math.cos(b.angle);
                    const outZ = Math.sin(b.angle);
                    const sepP = simCfg.sep_thrust;

                    b.vx = ux * (vel * 0.088) + perpX * outX * (4.2 * sepP);
                    b.vy = uy * (vel * 0.088) + perpY * outX * (4.2 * sepP) - (1.5 * sepP);
                    b.vz = outZ * (4.2 * sepP);
                    b.rx = outZ * (0.85 * sepP);
                    b.rz = -outX * (0.85 * sepP);
                }
            }
            if (boosterDetached) {
                for(let b of boosterUnits) {
                    b.mesh.position.x += b.vx * 0.016;
                    b.mesh.position.y += b.vy * 0.016;
                    b.mesh.position.z += b.vz * 0.016;
                    b.vy -= 9.80665 * 0.016 * 0.85;
                    b.vx *= 0.998;
                    b.vz *= 0.998;
                    b.mesh.rotation.x += b.rx * 0.016;
                    b.mesh.rotation.z += b.rz * 0.016;
                }
            }

            // 2. 第1段分離 ＆ スイングアーム動的開閉キャッチ
            const isSeparated = (p0.stage === 2 || p0.b_active);
            if (isSeparated && !stage1Detached && !simCfg.is_preview) {
                stage1Detached = true;
                playHeavySeparationSound();
                camShake = 0.3;
                s1NozzleTips.forEach(t => { t.plume.visible = false; });
                s2NozzleTips.forEach(t => { t.plume.visible = true; });
                scene.attach(s1Group);
            }

            // 🎯 スイングアームのリアル開閉制御（打ち上げ前/飛行中は格納、接近時に展開キャッチ）
            if (simCfg.spacex_return) {
                if (stage1Detached && bY <= 2500) {
                    // ブースターが上空から接近：アームを前に出して挟み込み準備
                    armLeftPivot.rotation.y = THREE.MathUtils.lerp(armLeftPivot.rotation.y, 0.02, 0.08);
                    armRightPivot.rotation.y = THREE.MathUtils.lerp(armRightPivot.rotation.y, -0.02, 0.08);
                    document.getElementById('hud-arm').innerText = "DEPLOYED (READY FOR CATCH)";
                    document.getElementById('hud-arm').style.color = "#34d399";
                } else {
                    // 発射時や上空飛行中は格納（オープン退避）
                    armLeftPivot.rotation.y = THREE.MathUtils.lerp(armLeftPivot.rotation.y, -0.75, 0.05);
                    armRightPivot.rotation.y = THREE.MathUtils.lerp(armRightPivot.rotation.y, 0.75, 0.05);
                    document.getElementById('hud-arm').innerText = "STOWED CLEAR";
                    document.getElementById('hud-arm').style.color = "#f59e0b";
                }
            }

            if (stage1Detached) {
                // 🎯 ブースター頭部ピンがアーム上面（Y=67.5m）に引っかかるよう配置
                // s1Body下端ノズルは地面（Y=0）から約50m以上浮いた完全宙づり状態
                s1Group.position.set(bX * 0.1, (bY - s1Len + 1.2) * 0.1 + 6.0, 0);
                s1Group.rotation.set(0, 0, -bPitch);
                s1Group.updateMatrixWorld(true);

                // アームキャッチ成功の瞬間
                if (p0.b_caught) {
                    // アームが突起ピンを挟み込んでロック
                    armLeftPivot.rotation.y = 0.06;
                    armRightPivot.rotation.y = -0.06;
                    document.getElementById('tv-stage-badge').innerText = "SUSPENDED CATCH SUCCESS";
                    document.getElementById('tv-stage-badge').style.color = "#38bdf8";

                    // 💥 爆竹が1個鳴った様な「バンッ！」という乾いた破裂音
                    if (!catchPopPlayed) {
                        playFirecrackerSnapSound();
                        catchPopPlayed = true;
                        camShake = 0.25;
                    }
                    // エンジン即時完全遮断
                    s1NozzleTips.forEach(t => { t.plume.visible = false; });
                } else if (p0.b_thrust) {
                    const isLandingBurn = (bY <= 3500);
                    s1NozzleTips.forEach(t => {
                        t.plume.visible = isLandingBurn ? t.isCenter : true;
                    });
                    if (bY <= 1500 && Math.random() < 0.6) {
                        s1Group.localToWorld(tempTipPos.set(0, 0, 0));
                        emitParticle(
                            tempTipPos.x + (Math.random()-0.5)*4, tempTipPos.y - 4, tempTipPos.z + (Math.random()-0.5)*4,
                            (Math.random()-0.5)*3.5, 0.4, (Math.random()-0.5)*3.5,
                            4.0, 28.0, 45, 0.85, 0xf1f5f9
                        );
                    }
                } else {
                    s1NozzleTips.forEach(t => { t.plume.visible = false; });
                }
            }

            // 3. フェアリング分離
            if (!p0.fairing && !fairingDetached && fairingHalves.length > 0 && !simCfg.is_preview) {
                fairingDetached = true;
                playHeavySeparationSound();
                for(let fh of fairingHalves) {
                    fh.detached = true;
                    scene.attach(fh.mesh);
                    fh.vx = ux * (vel * 0.072) + perpX * fh.side * 7.2;
                    fh.vy = uy * (vel * 0.072) + perpY * fh.side * 7.2 - 2.2;
                    fh.rotZ = -fh.side * 1.1;
                }
            }
            if (fairingDetached) {
                for(let fh of fairingHalves) {
                    fh.mesh.position.x += fh.vx * 0.016;
                    fh.mesh.position.y += fh.vy * 0.016;
                    fh.vy -= 9.8 * 0.016 * 0.7;
                    fh.mesh.rotation.z += fh.rotZ * 0.016;
                }
            }

            // 4. メイン火炎
            if (p0.thrust && !p0.exploded && !simCfg.is_preview) {
                const activeTips = (p0.stage === 1) ? s1NozzleTips : s2NozzleTips;
                if (p0.stage === 1 && !boosterDetached) activeTips.push(...boosterNozzleTips);

                for(let tObj of activeTips) {
                    tObj.plume.visible = true;
                    tObj.node.getWorldPosition(tempTipPos);

                    if (Math.random() < 0.35) {
                        emitNozzleSpark(
                            tempTipPos.x, tempTipPos.y, tempTipPos.z,
                            -ux * (1.8 + Math.random()*2.2),
                            -uy * (1.8 + Math.random()*2.2),
                            (Math.random()-0.5)*0.5,
                            0.45 + Math.random()*0.35,
                            12 + Math.floor(Math.random()*10),
                            simCfg.spark_hex
                        );
                    }

                    if (ry < 35.0 && Math.random() < 0.25) {
                        emitParticle(
                            tempTipPos.x + (Math.random()-0.5)*3.0, tempTipPos.y - 2.0, tempTipPos.z + (Math.random()-0.5)*3.0,
                            -ux * 0.5 + (Math.random()-0.5)*1.5, -uy * 0.5, (Math.random()-0.5)*1.5,
                            4.5, 32.0, 65, 0.7, 0xf1f5f9
                        );
                    }
                }
                engineBounceLight.intensity = Math.max(0.0, 6.5 - alt * 0.35);
                engineBounceLight.position.set(rx, ry + 3.0, 4.0);
            } else {
                if (!p0.b_active) s1NozzleTips.forEach(t => { t.plume.visible = false; });
                s2NozzleTips.forEach(t => { t.plume.visible = false; });
                boosterNozzleTips.forEach(t => { t.plume.visible = false; });
                engineBounceLight.intensity = 0.0;
            }

            // 5. 【多方向微調整RCS】
            let rcsActiveHUD = false;
            const rcsDelta = Math.abs(rcsCommand - prevRcsCmdVal);
            prevRcsCmdVal = rcsCommand;

            const isCorrectingPitchPlus  = (rcsDelta > 0.03 && rcsCommand > 0.12);
            const isCorrectingPitchMinus = (rcsDelta > 0.03 && rcsCommand < -0.12);
            const boosterApproachTune = stage1Detached && p0.b_active && !p0.b_caught && (bY <= 3500);

            for(let rcs of rcsNozzles) {
                let firePulse = false;

                if (!simCfg.is_preview && simT > 0.5 && !p0.exploded) {
                    if (rcs.isS1 && !stage1Detached) {
                        if (rcs.dir.id === "+Pitch" && isCorrectingPitchPlus) firePulse = true;
                        if (rcs.dir.id === "-Pitch" && isCorrectingPitchMinus) firePulse = true;
                    } else if (!rcs.isS1 && stage1Detached) {
                        if (rcs.dir.id === "+Pitch" && isCorrectingPitchPlus) firePulse = true;
                        if (rcs.dir.id === "-Pitch" && isCorrectingPitchMinus) firePulse = true;
                    }
                }

                if (rcs.isS1 && boosterApproachTune && (Math.random() < 0.28)) {
                    firePulse = true;
                }

                if (firePulse) {
                    rcs.intensity = 1.0;
                    rcs.mount.getWorldPosition(tempRcsPos);
                    emitParticle(
                        tempRcsPos.x, tempRcsPos.y, tempRcsPos.z,
                        rcs.dir.dx * 2.4 + (Math.random()-0.5)*0.4,
                        rcs.dir.dy * 2.4 + (Math.random()-0.5)*0.4,
                        rcs.dir.dz * 2.4 + (Math.random()-0.5)*0.4,
                        0.5, 3.2, 14, 0.8, 0xf0f9ff, true
                    );
                } else {
                    rcs.intensity *= 0.65;
                }

                rcs.jetMat.opacity = rcs.intensity;
                if (rcs.intensity > 0.15) rcsActiveHUD = true;
            }

            document.getElementById('hud-rcs').innerText = rcsActiveHUD ? "GN2 ACTIVE (MULTI-AXIS TUNE)" : "STANDBY (DEADBAND OK)";
            document.getElementById('hud-rcs').style.color = rcsActiveHUD ? "#34d399" : "#38bdf8";

            // 6. 発射台消音注水デリュージ
            if (simT < 0.0) {
                const sec = Math.ceil(Math.abs(simT));
                document.getElementById('tv-timer').innerText = simCfg.is_preview ? "PAD INSPECTION" : `T- 00:0${sec}.0`;

                emitParticle(rx + 1.25, ry + 6.0 + s1Len * 0.85, 0, 0.25, 0.05, 0, 0.9, 4.2, 45, 0.4, 0xffffff);

                if (simT >= -5.0 && !p0.exploded && !simCfg.is_preview) {
                    if (gasHiss && actx) gasHiss.gain.setTargetAtTime(0.55, actx.currentTime, 0.2);

                    for(let i=0; i<6; i++) {
                        const side = (Math.random() - 0.5) * 16.0;
                        emitParticle(
                            rx + side, 1.2, (Math.random() - 0.5) * 16.0,
                            side * 0.25, 0.4 + Math.random()*0.8, (Math.random()-0.5)*1.8,
                            5.0, 32.0, 60, 0.85, 0xe0f2fe
                        );
                    }
                }

                if (simT >= -simCfg.ignition_lead && !p0.exploded && !simCfg.is_preview) {
                    for(let tObj of s1NozzleTips) {
                        tObj.node.getWorldPosition(tempTipPos);
                        emitNozzleSpark(
                            tempTipPos.x, tempTipPos.y, tempTipPos.z,
                            (Math.random()-0.5)*1.2, -1.0 - Math.random()*1.8, (Math.random()-0.5)*1.2,
                            0.65, 18, 0xfde047
                        );
                    }
                }

                if (simT >= -3.0 && !p0.exploded && !simCfg.is_preview) {
                    camShake = 0.25;
                    for(let i=0; i<8; i++) {
                        const ang = Math.random() * Math.PI * 2;
                        const dist = 3.0 + Math.random() * 8.0;
                        emitParticle(
                            rx + Math.cos(ang) * dist, 1.5, Math.sin(ang) * dist,
                            Math.cos(ang) * (3.5 + Math.random()*4.0), 0.5 + Math.random()*0.8, Math.sin(ang) * (3.5 + Math.random()*4.0),
                            8.0, 45.0, 85, 0.92, 0xf8fafc
                        );
                    }
                }
            } else if (!p0.exploded) {
                const m = Math.floor(simT / 60); const s = simT % 60;
                document.getElementById('tv-timer').innerText = `T+ ${String(m).padStart(2,'0')}:${s.toFixed(1).padStart(4,'0')}`;

                if (actx) {
                    const atm = Math.exp(-alt / 14.0);
                    if (subRumble) subRumble.gain.setTargetAtTime(1.1 * atm, actx.currentTime, 0.15);
                    if (shockCrackle) shockCrackle.gain.setTargetAtTime(0.85 * atm, actx.currentTime, 0.1);
                    if (gasHiss) gasHiss.gain.setTargetAtTime(0.18 * atm, actx.currentTime, 1.0);
                }

                if (simT < 6.0) {
                    camShake = 0.35;
                    for(let i=0; i<6; i++) {
                        const ang = Math.random() * Math.PI * 2;
                        const dist = 4.0 + Math.random() * 10.0;
                        emitParticle(
                            rx + Math.cos(ang) * dist, 2.2, Math.sin(ang) * dist,
                            Math.cos(ang) * (4.2 + Math.random()*4.5), 0.3 + Math.random()*0.6, Math.sin(ang) * (4.2 + Math.random()*4.5),
                            9.0, 52.0, 85, 0.88, 0xf1f5f9
                        );
                    }
                }
            }

            // パーティクル更新
            for(let i=0; i<P_MAX; i++) {
                const p = pool[i]; if (!p.active) continue;
                p.age++;
                if (p.age >= p.maxAge) { p.active = false; p.sp.visible = false; continue; }
                p.sp.position.x += p.vx; p.sp.position.y += p.vy; p.sp.position.z += p.vz;
                const pr = p.age / p.maxAge;
                const curScale = p.s0 + (p.s1 - p.s0) * Math.pow(pr, 0.7);
                p.sp.scale.set(curScale, curScale, 1);
                p.sp.material.opacity = p.o * (1.0 - pr * pr);
            }

            for(let i=0; i<SPARK_MAX; i++) {
                const s = sparkPool[i]; if (!s.active) continue;
                s.age++;
                if (s.age >= s.maxAge) { s.active = false; s.sp.visible = false; continue; }
                s.sp.position.x += s.vx; s.sp.position.y += s.vy; s.sp.position.z += s.vz;
                const pr = s.age / s.maxAge;
                s.sp.material.opacity = 1.0 - pr;
            }

            // メインカメラ追従
            if (p0.stage === 2) {
                activeFocusWorld.set(0, s2Len * 0.45, 0);
                s2Group.localToWorld(activeFocusWorld);
            } else {
                activeFocusWorld.set(0, s1Len * 0.52, 0);
                rocket.localToWorld(activeFocusWorld);
            }

            if (simCfg.is_preview) {
                document.getElementById('cam-tag').innerText = "PAD INSPECTION: LIVE 3D CINEMA VIEW";
                const orbitAng = elapsedSec * 0.22;
                cameraMain.position.set(Math.sin(orbitAng) * 115.0, 28.0 + Math.sin(elapsedSec * 0.3) * 10.0, Math.cos(orbitAng) * 115.0);
                cameraMain.lookAt(0, 6.0 + (s1Len + s2Len) * 0.45, 0);
            } else {
                const desiredOffset = new THREE.Vector3();
                if (p0.exploded) {
                    document.getElementById('cam-tag').innerText = "CAM 01: HIGH-SPEED DEBRIS TRACKER";
                    desiredOffset.set(85.0, 32.0, 185.0);
                } else if (simT < 0.0) {
                    document.getElementById('cam-tag').innerText = "CAM 01: PAD PERIMETER HIGH-SPEED WIDE";
                    desiredOffset.set(72.0, 8.0, 138.0);
                } else if (simT < 4.0) {
                    document.getElementById('cam-tag').innerText = "CAM 01: TOWER CLEARANCE TRACKER";
                    desiredOffset.set(-78.0, 18.0, 155.0);
                } else if (alt < 22.0) {
                    document.getElementById('cam-tag').innerText = "CAM 01: KINETO TRACKER (2400mm APO)";
                    desiredOffset.set(-72.0, -16.0, 145.0);
                } else if (alt < 85.0) {
                    document.getElementById('cam-tag').innerText = "CAM 01: NASA WB-57 OPTICAL CHASE";
                    desiredOffset.set(-65.0, -12.0, 135.0);
                } else {
                    document.getElementById('cam-tag').innerText = "CAM 01: ORBITAL LONG-RANGE TELESCOPE";
                    desiredOffset.set(-55.0, 14.0, 120.0);
                }

                smoothOffset.lerp(desiredOffset, 0.065);
                cameraMain.position.copy(activeFocusWorld).add(smoothOffset);

                if (camShake > 0.002) {
                    cameraMain.position.x += (Math.random() - 0.5) * camShake;
                    cameraMain.position.y += (Math.random() - 0.5) * camShake;
                    camShake *= 0.94;
                }
                cameraMain.lookAt(activeFocusWorld);
            }

            drawPrecisionOrbitMap(alt, dRangeKm, p0.exploded, (p0.event === "ORBIT"));

            let regime = "TROPOSPHERE";
            if (alt >= 100.0) regime = "THERMOSPHERE (VACUUM)";
            else if (alt >= 50.0) regime = "MESOSPHERE";
            else if (alt >= 12.0) regime = "STRATOSPHERE";
            document.getElementById('hud-regime').innerText = regime;
            document.getElementById('hud-downrange').innerText = `DOWNRANGE: ${dRangeKm.toFixed(1)} km`;

            document.getElementById('tv-mach').innerText = `M ${mach.toFixed(2)}`;
            document.getElementById('tv-spd').innerText = `(${Math.round(vel * 3.6).toLocaleString()} km/h)`;
            document.getElementById('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            document.getElementById('tv-q').innerText   = q.toFixed(1);
            document.getElementById('tv-g').innerText   = accG.toFixed(1);

            // 🏁 【改修】ミッション完了条件：軌道投入（28,400km/h以上）かつ ブースターアーム回収
            const isOrbitAchieved = (p0.event === "ORBIT");
            const isCatchComplete = p0.b_caught || (!simCfg.spacex_return);

            if (isOrbitAchieved && isCatchComplete && !isMissionEnded) {
                completeBanner.style.display = 'block';
                document.getElementById('tv-stage-badge').innerText = "MISSION SUCCESS - ALL OBJECTIVES NOMINAL";
                document.getElementById('tv-stage-badge').style.color = "#10b981";
                document.getElementById('live-indicator').style.background = "#10b981";
                document.getElementById('live-indicator').style.boxShadow = "0 0 10px #10b981";
                document.getElementById('webcast-title').innerText = "MISSION COMPLETED";

                if (actx) {
                    if (subRumble) subRumble.gain.setTargetAtTime(0.0001, actx.currentTime, 0.4);
                    if (shockCrackle) shockCrackle.gain.setTargetAtTime(0.0001, actx.currentTime, 0.4);
                    if (gasHiss) gasHiss.gain.setTargetAtTime(0.0001, actx.currentTime, 0.4);
                }

                setTimeout(() => {
                    isMissionEnded = true;
                }, 2800);
            }

            if (p0.exploded) {
                rudBanner.style.display = 'block';
                rudDesc.innerText = failMessage || "機体過負荷による空中分解";
            }

            rendererMain.render(scene, cameraMain);

            if (pipVisible) {
                const isBoosterTrackActive = simCfg.spacex_return && (stage1Detached || p0.b_active || p0.stage === 2);
                renderGroundOpticalTracker(isBoosterTrackActive, bX, bY, p0.b_caught, rocket.position);
            }
        }

        requestAnimationFrame(animate);

        window.addEventListener('resize', () => {
            cameraMain.aspect = window.innerWidth / window.innerHeight;
            cameraMain.updateProjectionMatrix();
            rendererMain.setSize(window.innerWidth, window.innerHeight);
        });
    } catch(err) {
        console.error("Simulation Render Error:", err);
    }
    </script>
</body>
</html>
"""

final_html = html_template.replace("__SIM_DATA__", traj_json)
final_html = final_html.replace("__SIM_CFG__", cfg_json)
final_html = final_html.replace("__FAIL_MSG__", fail_msg_clean)

components.html(final_html, height=980)

if launch_clicked:
    st.markdown("---")
    st.markdown("### 📋 フライトテレメトリ詳細レポート")
    if error_msg:
        st.error(f"⚠️ **ミッション異常終了 (RUD)**: {error_msg}")
    else:
        st.success("🎉 **ミッション完全成功 (Starship LEO Insertion & Super Heavy Mechazilla Catch)**: 第1段ブースターのタワーキャッチおよび第2段の軌道投入シーケンスが設計通り正常に推移しました。")
