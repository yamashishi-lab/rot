import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components
from renderer import get_html_content

st.set_page_config(
    page_title="Orbital Architect Extreme: Ultra Realistic Edition", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect Extreme - 4K実写航空宇宙シミュレーター")
st.caption("※ 厳格航空力学・破壊判定・自動実況・大地/海洋PBR・多段分離物理・実機志向プリセット完全搭載")

# =========================================================================
# 🔬 推進剤・材料・空力パーツ・ブースター・ジョーク部品データベース
# =========================================================================
PROPELLANTS = {
    "超高密度サブクール・メタロックス (CH4 / LOX) [Starship王道]": {
        "base_isp_sl": 338, "base_isp_vac": 382, "base_thrust": 2800, "density": 0.85, 
        "flame_hex": 0x60a5fa, "outer_hex": 0x1d4ed8, "spark_hex": 0x93c5fd, "risk": 0.01, "type": "methalox"
    },
    "高精製ロケットグレードケロシン (RP-1 / LOX) [Saturn V / Falcon 9]": {
        "base_isp_sl": 302, "base_isp_vac": 335, "base_thrust": 1950, "density": 1.03, 
        "flame_hex": 0xfef08a, "outer_hex": 0xea580c, "spark_hex": 0xfde047, "risk": 0.005, "type": "rp1"
    },
    "超極低温スラッシュ・ハイドロロックス (LH2 / LOX) [H3 / SLS / Shuttle]": {
        "base_isp_sl": 385, "base_isp_vac": 468, "base_thrust": 1450, "density": 0.34, 
        "flame_hex": 0xfbcfe8, "outer_hex": 0xbe185d, "spark_hex": 0xffffff, "risk": 0.03, "type": "hydro"
    },
    "猛毒ハイパーゴリック (N2O4 / UDMH) [Proton / ICBM Titan II]": {
        "base_isp_sl": 288, "base_isp_vac": 322, "base_thrust": 2100, "density": 1.26, 
        "flame_hex": 0xf5d0fe, "outer_hex": 0x9333ea, "spark_hex": 0xfab1a0, "risk": 0.05, "type": "hypergolic"
    },
    "HTPB高エネルギー固体推進薬 (アルミニウム粉末添加) [SRB / 固体弾道ミサイル]": {
        "base_isp_sl": 268, "base_isp_vac": 295, "base_thrust": 3400, "density": 1.78,
        "flame_hex": 0xffedd5, "outer_hex": 0xf97316, "spark_hex": 0xffffff, "risk": 0.02, "type": "solid"
    },
    "【核熱】固体炉心型原子力サーマルロケット (NERVA / LH2)": {
        "base_isp_sl": 450, "base_isp_vac": 925, "base_thrust": 2500, "density": 0.30, 
        "flame_hex": 0x86efac, "outer_hex": 0x14532d, "spark_hex": 0x4ade80, "risk": 0.12, "type": "nuclear"
    },
    "【ジョーク】メントス ＆ ダイエットコーラ特大加圧タンク": {
        "base_isp_sl": 45, "base_isp_vac": 52, "base_thrust": 180, "density": 1.05, 
        "flame_hex": 0xe2e8f0, "outer_hex": 0x64748b, "spark_hex": 0x38bdf8, "risk": 0.45, "type": "cola"
    },
    "【ジョーク】激辛ペヤング獄激辛麻婆ソース直接噴射": {
        "base_isp_sl": 190, "base_isp_vac": 215, "base_thrust": 950, "density": 1.15, 
        "flame_hex": 0xdc2626, "outer_hex": 0x7f1d1d, "spark_hex": 0xf87171, "risk": 0.60, "type": "spicy"
    }
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [極限高圧・Starship Raptor]": {"isp_mod": 1.07, "thrust_mod": 1.42, "mass_mod": 1.22, "max_pressure_limit": 380, "cyc_id": "ffsc"},
    "酸化剤リッチ二段燃焼 (ORSC) [高出力信頼性・RD-180]": {"isp_mod": 1.03, "thrust_mod": 1.25, "mass_mod": 1.18, "max_pressure_limit": 310, "cyc_id": "sc"},
    "ガス発生器サイクル (GG) [煤排気・Merlin 1D / F-1]": {"isp_mod": 0.96, "thrust_mod": 0.98, "mass_mod": 0.84, "max_pressure_limit": 195, "cyc_id": "gg"},
    "エキスパンダーブリードサイクル [極限高信頼・LE-9 / H3]": {"isp_mod": 1.01, "thrust_mod": 0.88, "mass_mod": 0.78, "max_pressure_limit": 150, "cyc_id": "expander"},
    "リニアエアロスパイク方式 [全高度最適膨張]": {"isp_mod": 1.09, "thrust_mod": 1.10, "mass_mod": 1.32, "max_pressure_limit": 250, "cyc_id": "aerospike"},
    "【ジョーク】手回し手動クランク駆動ターボポンプ": {"isp_mod": 0.25, "thrust_mod": 0.15, "mass_mod": 0.50, "max_pressure_limit": 45, "cyc_id": "crank"}
}

MATERIALS = {
    "Austenitic 304L 冷間圧延鏡面ステンレス [Starship仕様]": {"base_dry_ratio": 0.065, "max_q_base": 130.0, "max_g_base": 12.5, "mat_id": "ss"},
    "航空宇宙用 Al-Li-2195 アルミリチウム合金 [SLSオレンジ塗装]": {"base_dry_ratio": 0.050, "max_q_base": 82.0, "max_g_base": 9.0, "mat_id": "al"},
    "Saturn V 伝統 ホワイト＆ブラック・ロールチェック塗工": {"base_dry_ratio": 0.054, "max_q_base": 88.0, "max_g_base": 9.5, "mat_id": "saturn"},
    "高弾性トレカ炭素繊維複合材 (CFRP) [Falcon 9 / Neutron]": {"base_dry_ratio": 0.036, "max_q_base": 65.0, "max_g_base": 7.5, "mat_id": "cf"},
    "超耐熱インコネル718 モノコック [重装甲チタン調]": {"base_dry_ratio": 0.092, "max_q_base": 195.0, "max_g_base": 16.5, "mat_id": "inconel"},
    "ICBM迷彩マットオリーブドラブ [ロシア・Topol-M風]": {"base_dry_ratio": 0.048, "max_q_base": 110.0, "max_g_base": 14.0, "mat_id": "camo"},
    "【ジョーク】段ボール＋布ガムテープ補強構造": {"base_dry_ratio": 0.020, "max_q_base": 12.0, "max_g_base": 1.8, "mat_id": "cardboard"}
}

STRAPON_BOOSTERS = {
    "なし (単段スリムコア構成)": {"count": 0, "thrust_add": 0.0, "mass_add": 0.0, "fuel_add": 0.0, "isp_sl": 0, "type": "none"},
    "Falcon Heavy風 液体LRB × 2基 (着陸脚＆グリッドフィン付)": {"count": 2, "thrust_add": 5800.0, "mass_add": 52.0, "fuel_add": 840.0, "isp_sl": 315, "type": "lrb"},
    "Soyuz R-7風 テーパー液体ブースター × 4基 (コロリョフクロス専用)": {"count": 4, "thrust_add": 4200.0, "mass_add": 38.0, "fuel_add": 520.0, "isp_sl": 308, "type": "soyuz"},
    "SLS風 5セグメント超巨大SRB × 2基 (白塗装＆黒ジョイントリング)": {"count": 2, "thrust_add": 8800.0, "mass_add": 68.0, "fuel_add": 950.0, "isp_sl": 278, "type": "srb"},
    "ICBM用 クイックスタート小型固体ロケットブースター × 2基": {"count": 2, "thrust_add": 3200.0, "mass_add": 22.0, "fuel_add": 280.0, "isp_sl": 265, "type": "icbm_srb"},
    "【ジョーク】巨大花火「飛翔龍」× 8本掛け": {"count": 8, "thrust_add": 450.0, "mass_add": 6.0, "fuel_add": 40.0, "isp_sl": 180, "type": "firework"}
}

AERO_WINGS = {
    "チタン鍛造極超音速グリッドフィン × 4基": {"lift_coeff": 0.12, "drag_penalty": 1.05, "mass": 1.2, "flutter_mach": 99.0, "wing_id": "grid"},
    "Starship風 空力エルロンボディフラップ × 4枚": {"lift_coeff": 0.35, "drag_penalty": 1.12, "mass": 2.8, "flutter_mach": 99.0, "wing_id": "starship_flap"},
    "なし (純粋な軸対称弾道ロケット / ICBM)": {"lift_coeff": 0.0, "drag_penalty": 1.0, "mass": 0.0, "flutter_mach": 99.0, "wing_id": "none"},
    "デルタ制御翼 (超音速スタビライザー)": {"lift_coeff": 0.55, "drag_penalty": 1.25, "mass": 3.2, "flutter_mach": 4.5, "wing_id": "delta_wing"},
    "【ジョーク】タケコプター型天頂小型プロペラ": {"lift_coeff": 0.05, "drag_penalty": 2.20, "mass": 0.4, "flutter_mach": 0.65, "wing_id": "bamboo"}
}

FAIRINGS = {
    "バイコニカル炭素複合材クラムシェル (金箔通信衛星内蔵)": {"mass": 2.1, "cd": 0.18, "heat_limit": 2600, "shape_id": "biconic"},
    "有人カプセル ＋ レスキューアボートタワー (LES付)": {"mass": 6.8, "cd": 0.32, "heat_limit": 3200, "shape_id": "abort_tower"},
    "Starship風 窓付き有人クルーノーズコーン": {"mass": 4.2, "cd": 0.22, "heat_limit": 2900, "shape_id": "starship_crew"},
    "MIRV 多弾頭再突入体 コーン型ノーズ (ICBM仕様)": {"mass": 3.8, "cd": 0.14, "heat_limit": 4200, "shape_id": "mirv"},
    "【ジョーク】巨大アヒル型ノーズキャップ": {"mass": 1.5, "cd": 0.68, "heat_limit": 600, "shape_id": "duck"}
}

# =========================================================================
# 🎯 マニア向け実機プリセットセレクター
# =========================================================================
st.subheader("🎯 実機・実弾道・マニアックプリセット")
preset_choice = st.selectbox(
    "標準プリセットをロード (選択すると最適パラメータが自動反映されます)",
    [
        "カスタム設計 (完全マニュアル)",
        "SpaceX Falcon Heavy (3基コア液体・高推力)",
        "NASA SLS Block 1 (LH2/LOX + 巨大SRB2基)",
        "ロシア Soyuz 2.1b (ケロシン＋テーパーブースター・コロリョフクロス)",
        "大陸間弾道ミサイル (ICBM: 超高加速度・高耐熱MIRV)",
        "SpaceX Starship 完全体 (フルフローステージド・メタン)",
        "【危険】超高圧限界突破・自爆確定セッティング",
        "【爆笑】段ボールコークロケット (即座に空中圧壊)"
    ],
    index=0
)

# プリセット初期化
p_defaults = {
    "s1_prop": 0, "s1_cycle": 0, "s1_eng": 9, "s1_pc": 290, "s1_eps": 24, "s1_fuel": 1100.0, "s1_mat": 0, "s1_thick": 4.2,
    "strap": 2, "s2_prop": 0, "s2_cycle": 0, "s2_eng": 3, "s2_fuel": 280.0, "s2_mat": 0, "s2_thick": 3.0,
    "fairing": 0, "wing": 0, "flow": 250, "ign_lead": 3.8, "turn_start": 1.8, "turn_end": 120.0, "max_g": 5.0
}

if preset_choice == "SpaceX Falcon Heavy (3基コア液体・高推力)":
    p_defaults.update({"s1_prop": 1, "s1_cycle": 2, "s1_eng": 9, "s1_pc": 97, "s1_fuel": 1300.0, "s1_mat": 3, "strap": 1, "wing": 0, "s2_prop": 1, "s2_fuel": 320.0})
elif preset_choice == "NASA SLS Block 1 (LH2/LOX + 巨大SRB2基)":
    p_defaults.update({"s1_prop": 2, "s1_cycle": 1, "s1_eng": 4, "s1_pc": 204, "s1_fuel": 2100.0, "s1_mat": 1, "strap": 3, "s2_prop": 2, "s2_fuel": 240.0, "fairing": 1})
elif preset_choice == "ロシア Soyuz 2.1b (ケロシン＋テーパーブースター・コロリョフクロス)":
    p_defaults.update({"s1_prop": 1, "s1_cycle": 1, "s1_eng": 4, "s1_pc": 160, "s1_fuel": 950.0, "s1_mat": 2, "strap": 2, "s2_prop": 1, "s2_fuel": 190.0})
elif preset_choice == "大陸間弾道ミサイル (ICBM: 超高加速度・高耐熱MIRV)":
    p_defaults.update({"s1_prop": 4, "s1_cycle": 1, "s1_eng": 1, "s1_pc": 180, "s1_fuel": 650.0, "s1_mat": 5, "strap": 4, "wing": 2, "fairing": 3, "max_g": 11.5, "turn_start": 0.4, "turn_end": 70.0})
elif preset_choice == "SpaceX Starship 完全体 (フルフローステージド・メタン)":
    p_defaults.update({"s1_prop": 0, "s1_cycle": 0, "s1_eng": 33, "s1_pc": 350, "s1_fuel": 3400.0, "s1_mat": 0, "strap": 0, "wing": 1, "fairing": 2, "s2_prop": 0, "s2_fuel": 1200.0})
elif preset_choice == "【危険】超高圧限界突破・自爆確定セッティング":
    p_defaults.update({"s1_prop": 0, "s1_cycle": 2, "s1_pc": 410, "s1_thick": 1.0, "max_g": 12.0})
elif preset_choice == "【爆笑】段ボールコークロケット (即座に空中圧壊)":
    p_defaults.update({"s1_prop": 6, "s1_cycle": 5, "s1_mat": 6, "strap": 5, "wing": 4, "fairing": 4, "s1_thick": 1.0})

# =========================================================================
# 🎛️ パラメータ設定タブ
# =========================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 第1段 (推進・燃焼・構造)", 
    "🚀 外部ブースター & 分離機構",
    "🛩️ 空力翼 & RCS姿勢制御系", 
    "🛰️ 第2段 (オービター) & 先端部", 
    "🌊 発射台水冷デリュージ & ガイダンス"
])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=p_defaults["s1_prop"])
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", list(PUMP_CYCLES.keys()), index=p_defaults["s1_cycle"])
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, p_defaults["s1_eng"])
    with c2:
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 20, 420, p_defaults["s1_pc"], step=5)
        s1_eps = st.slider("海面膨張比 (ε: ノズル径連動)", 6, 70, p_defaults["s1_eps"], step=1)
        combustion_stability = st.slider("燃焼室音響ダンパー設計 (安定性マージン)", 0.5, 1.5, 1.0, step=0.05)
    with c3:
        s1_fuel = st.slider("第1段 推進剤充填量 (トン: 胴体長連動)", 50.0, 4500.0, p_defaults["s1_fuel"], step=50.0)
        s1_mat = st.selectbox("第1段 構造素材", list(MATERIALS.keys()), index=p_defaults["s1_mat"])
        s1_thick = st.slider("外殻等価板厚 (mm)", 0.5, 15.0, p_defaults["s1_thick"], step=0.1)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        strapon_opt = st.selectbox("ブースター種別クラスタ", list(STRAPON_BOOSTERS.keys()), index=p_defaults["strap"])
    with c2:
        sep_thrust_factor = st.slider("分離パイロ・プッシャー推力倍率 (分離間隔連動)", 0.2, 3.0, 0.85, step=0.05)
        booster_jettison_delay = st.slider("MECO後 ブースター切り離し遅延 (秒)", 0.0, 4.0, 0.4, step=0.1)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 空力パーツ", list(AERO_WINGS.keys()), index=p_defaults["wing"])
        angle_of_attack = st.slider("固定取り付け迎角 AoA (deg)", -5.0, 15.0, 0.2, step=0.1)
    with c2:
        rcs_deadband = st.slider("RCS 姿勢制御デッドバンド角 (deg)", 0.1, 5.0, 0.8, step=0.1)
        gimbal_rate_limit = st.slider("ジンバル応答角速度 (°/sec)", 5.0, 30.0, 15.0, step=1.0)

with tab4:
    c1, c2, c3 = st.columns(3)
    with c1:
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=p_defaults["s2_prop"])
        s2_cycle = st.selectbox("第2段 ポンプ方式", list(PUMP_CYCLES.keys()), index=p_defaults["s2_cycle"])
        s2_eng_count = st.slider("真空ノズル基数", 1, 9, p_defaults["s2_eng"])
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 30, 280, 160, step=5)
    with c2:
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 10.0, 1200.0, p_defaults["s2_fuel"], step=10.0)
        s2_mat = st.selectbox("第2段 構造素材", list(MATERIALS.keys()), index=p_defaults["s2_mat"])
        s2_thick = st.slider("第2段 壁厚 (mm)", 0.5, 8.0, p_defaults["s2_thick"], step=0.1)
    with c3:
        fairing_type = st.selectbox("先端空力カウル / ペイロード", list(FAIRINGS.keys()), index=p_defaults["fairing"])
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 30.0, 180.0, 85.0, step=5.0)
        payload_mass = st.slider("投入衛星・弾頭質量 (トン)", 0.1, 150.0, 18.0, step=0.5)

with tab5:
    c1, c2 = st.columns(2)
    with c1:
        water_flow_rate = st.slider("消音注水デリュージ流量 (トン/秒)", 0, 500, p_defaults["flow"], step=25)
        ignition_lead_time = st.slider("エンジン先行点火開始 (T-マイナス秒)", 1.5, 6.0, p_defaults["ign_lead"], step=0.1)
    with c2:
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.1, 15.0, p_defaults["turn_start"], step=0.1)
        turn_end_alt = st.slider("水平重力ターン完了高度 (km)", 40.0, 250.0, p_defaults["turn_end"], step=5.0)
        turn_exponent = st.slider("ターン曲率指数", 0.2, 2.0, 0.65, step=0.02)
        throttle_maxq = st.slider("Max-Q 領域 推力抑制 (%)", 20, 100, 75)
        max_g_limit_cut = st.slider("最大加速度リミッター (G)", 1.5, 15.0, p_defaults["max_g"], step=0.2)

# =========================================================================
# ⚙️ 物理性能演算 (Physics Breakdown)
# =========================================================================
def calc_stage_specs(prop_key, cycle_key, pc, eps, eng_count, fuel_mass, mat_key, thick, stability=1.0):
    prop = PROPELLANTS[prop_key]
    cyc = PUMP_CYCLES[cycle_key]
    mat = MATERIALS[mat_key]

    pc_factor = 1.0 + (pc - 100.0) * 0.0006
    eps_vac_bonus = 1.0 + np.log10(eps / 25.0) * 0.08
    overexpansion_penalty = max(0.0, (eps - 35.0) * 0.006)

    isp_sl = max(10.0, prop["base_isp_sl"] * cyc["isp_mod"] * pc_factor * (1.0 - overexpansion_penalty))
    isp_vac = max(15.0, prop["base_isp_vac"] * cyc["isp_mod"] * pc_factor * eps_vac_bonus)

    thrust_vac_per_eng = prop["base_thrust"] * cyc["thrust_mod"] * ((pc / 150.0) ** 0.65)
    thrust_sl_per_eng = thrust_vac_per_eng * (isp_sl / isp_vac)

    density_penalty = (1.0 / max(0.1, prop["density"])) ** 0.35
    thick_factor = thick / 3.0
    dry_ratio = mat["base_dry_ratio"] * density_penalty * thick_factor + 0.004
    eng_mass = (thrust_vac_per_eng / 750.0) * cyc["mass_mod"] * (1.0 + eps * 0.002) * eng_count
    dry_mass = fuel_mass * dry_ratio + eng_mass

    max_q_resistance = mat["max_q_base"] * (thick_factor ** 1.15)
    max_g_resistance = mat["max_g_base"] * (thick_factor ** 0.85)

    is_overpressured = (pc > cyc["max_pressure_limit"] * 1.08)
    instability_risk = prop["risk"] * (1.2 / max(0.1, stability))

    return {
        "isp_sl": float(isp_sl), "isp_vac": float(isp_vac),
        "thrust_sl": float(thrust_sl_per_eng * eng_count),
        "thrust_vac": float(thrust_vac_per_eng * eng_count),
        "dry_mass": float(dry_mass),
        "max_q": float(max_q_resistance),
        "max_g": float(max_g_resistance),
        "pc": pc, "pc_limit": cyc["max_pressure_limit"],
        "is_overpressured": is_overpressured,
        "instability_risk": instability_risk,
        "cd_mod": density_penalty,
        "mat_id": mat["mat_id"],
        "cyc_id": cyc["cyc_id"],
        "flame_hex": prop["flame_hex"],
        "outer_hex": prop["outer_hex"],
        "spark_hex": prop["spark_hex"],
        "eng_count": eng_count,
        "prop_type": prop["type"]
    }

wing_spec = AERO_WINGS[wing_type]
fair_spec = FAIRINGS[fairing_type]
strapon_spec = STRAPON_BOOSTERS[strapon_opt]

s1_spec = calc_stage_specs(s1_prop, s1_cycle, s1_pc, s1_eps, s1_eng_count, s1_fuel, s1_mat, s1_thick, combustion_stability)
s2_spec = calc_stage_specs(s2_prop, s2_cycle, 220, s2_eps, s2_eng_count, s2_fuel, s2_mat, s2_thick, 1.0)

total_s2_wet = s2_fuel + s2_spec["dry_mass"] + payload_mass + fair_spec["mass"]
total_s1_wet = s1_fuel + s1_spec["dry_mass"] + wing_spec["mass"] + strapon_spec["mass_add"] + strapon_spec["fuel_add"] + total_s2_wet

total_liftoff_thrust = s1_spec["thrust_sl"] + strapon_spec["thrust_add"]
twr_init = total_liftoff_thrust / max(1.0, (total_s1_wet * 9.80665))
dv_s1 = s1_spec["isp_sl"] * 9.80665 * np.log(max(1.01, total_s1_wet / max(1.0, (total_s1_wet - s1_fuel - strapon_spec["fuel_add"]))))
dv_s2 = s2_spec["isp_vac"] * 9.80665 * np.log(max(1.01, total_s2_wet / max(1.0, (s2_spec["dry_mass"] + payload_mass))))
total_dv = dv_s1 + dv_s2

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("総離床重量 / 離床TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f} ({'離床可能' if twr_init >= 1.02 else '推力不足！発射不能'})")
m2.metric("総計算速度増分 (ΔV)", f"{total_dv:.0f} m/s", "LEO投入目安: 9,200 m/s")
m3.metric("構造限界動圧 / 耐G", f"{s1_spec['max_q']:.1f} kPa", f"耐G: {s1_spec['max_g']:.1f} G")
m4.metric("ブースター追加推力", f"+{strapon_spec['thrust_add']:.0f} kN", f"基数: {strapon_spec['count']} 基")

# =========================================================================
# 💥 物理シミュレーション (破壊力学・重力ターン・空力崩壊判定)
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

    # 発射台での即座爆発判定（超高圧・音響破壊・極低消音水）
    if s1_spec["is_overpressured"]:
        fail_reason = f"燃焼室破壊爆発 (Chamber Overpressure RUD): 燃焼室圧力 {s1_pc} bar が限界値 {s1_spec['pc_limit']} bar を超過。"
        history.append({
            "t": 0.0, "x": 0.0, "y": 0.5, "alt": 0.0005, "v": 0.0, "q": 0.0, "g": 1.0,
            "stage": 1, "fairing": True, "wings": wings_attached, "strapon": strapon_attached,
            "exploded": True, "explosion_type": "CHAMBER_EXPLOSION", "thrust": False, "pitch": 0.0, "mach": 0.0, "event": "RUD"
        })
        return history, fail_reason

    if water_flow_rate < 30 and s1_eng_count > 6:
        fail_reason = "音響反射波による発射台爆沈: 水冷消音不足により反射衝撃波がエンジンノズルを破壊。"
        history.append({
            "t": 0.2, "x": 0.0, "y": 1.0, "alt": 0.001, "v": 0.0, "q": 0.0, "g": 1.0,
            "stage": 1, "fairing": True, "wings": wings_attached, "strapon": strapon_attached,
            "exploded": True, "explosion_type": "ACOUSTIC_COLLAPSE", "thrust": False, "pitch": 0.0, "mach": 0.0, "event": "RUD"
        })
        return history, fail_reason

    if twr_init < 1.0:
        fail_reason = f"離床推力不足 (TWR: {twr_init:.2f} < 1.00): 機体が自重を持ち上げられず発射台上で炎上・沈降。"
        history.append({
            "t": 1.5, "x": 0.0, "y": 0.2, "alt": 0.0002, "v": 0.0, "q": 0.0, "g": 1.0,
            "stage": 1, "fairing": True, "wings": wings_attached, "strapon": strapon_attached,
            "exploded": True, "explosion_type": "PAD_STALL", "thrust": True, "pitch": 0.0, "mach": 0.0, "event": "RUD"
        })
        return history, fail_reason

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

        # 重力ターン誘導計算
        if alt_km < turn_start_alt:
            target_pitch_deg = 90.0
        elif alt_km < turn_end_alt:
            prog = (alt_km - turn_start_alt) / (turn_end_alt - turn_start_alt)
            target_pitch_deg = 90.0 * (1.0 - (prog ** turn_exponent))
        else:
            target_pitch_deg = 0.0

        # 空力翼による追加揚力・ロールモーメント影響
        extra_pitch_deflection = 0.0
        wing_lift_force = 0.0
        if wings_attached and alt_km < 50.0 and rho > 0.002:
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
                    fuel_strapon_rem -= (strap_thrust / (max(10.0, strapon_spec["isp_sl"]) * g0)) * dt * 1.3
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

                mdot = thrust_core / (max(10.0, isp) * g0)
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

                mdot = thrust / (max(10.0, isp) * g0)
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
            ax, ay, vx, vy = 0.0, 0.0, 0.0, 0.0
            acc_g = 1.0
        else:
            ax = fx / max(1.0, cur_mass)
            ay = fy / max(1.0, cur_mass)
            acc_g = float(np.sqrt((thrust * dir_x + drag_x + lift_x)**2 + (thrust * dir_y + drag_y + lift_y)**2) / max(1.0, (cur_mass * g0)))

        cur_spec = s1_spec if stage == 1 else s2_spec

        # 構造破壊判定 (動圧超過 / 耐G超過 / 超音速フラッター)
        if q > cur_spec["max_q"]:
            fail_reason = f"Max-Q 空力圧壊 (Structural Disintegration): 動圧 {q:.1f} kPa が機体許容限界 {cur_spec['max_q']:.1f} kPa を超過。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached,
                "exploded": True, "explosion_type": "STRUCTURAL_COLLAPSE", "thrust": False, "pitch": visual_pitch,
                "mach": mach, "event": "RUD"
            })
            break

        if acc_g > cur_spec["max_g"]:
            fail_reason = f"過大加速度圧壊 (G-Force Structural Failure): 加速度 {acc_g:.1f} G が許容限界 {cur_spec['max_g']:.1f} G を超過。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached,
                "exploded": True, "explosion_type": "G_LIMIT_COLLAPSE", "thrust": False, "pitch": visual_pitch,
                "mach": mach, "event": "RUD"
            })
            break

        if mach > wing_spec["flutter_mach"]:
            fail_reason = f"空力翼フラッター空中分解: マッハ数 {mach:.2f} において空力翼が発散振動を起こし脱落。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached,
                "exploded": True, "explosion_type": "WING_FLUTTER", "thrust": False, "pitch": visual_pitch,
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

        # 軌道投入到達判定
        if alt_km >= 160.0 and vx >= 7780.0 and abs(vy) < 400.0:
            cur_event = "ORBIT"
            for orbit_step in range(1200):
                t_orb = t + (orbit_step + 1) * dt
                x_orb = x + vx * (orbit_step + 1) * dt
                history.append({
                    "t": t_orb, "x": x_orb, "y": y, "alt": alt_km, "v": v, "q": 0.0, "g": 0.0,
                    "stage": 2, "fairing": False, "wings": wings_attached,
                    "strapon": False, "exploded": False, "explosion_type": "NONE", "thrust": False,
                    "pitch": visual_pitch, "mach": mach, "event": "ORBIT"
                })
            break

    if not fail_reason and history[-1]["event"] != "ORBIT":
        fail_reason = f"軌道投入失敗（燃料枯渇・弾道落下）。高度: {alt_km:.1f} km, 速度: {vx:.0f} m/s"

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
    "rcs_deadband": float(rcs_deadband),
    "gimbal_rate": float(gimbal_rate_limit),
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
    "booster_delay": float(booster_jettison_delay)
}

traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
cfg_json = json.dumps(rocket_visual_cfg)
fail_msg_clean = (error_msg or "").replace('"', '\\"').replace("'", "\\'")

# HTML描画の呼び出し
final_html = get_html_content(traj_json, cfg_json, fail_msg_clean)
components.html(final_html, height=980)

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
