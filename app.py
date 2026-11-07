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
st.caption("※ 4K実写級：IFT-5タワーキャッチ・精密RCS制御・機体別発射台・雲海＆大気環境・高臨場感音響版")

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
    "【猛毒】四酸化二窒素 ＋ UDMH (N2O4 / UDMH) [Proton / ICBM]": {
        "base_isp_sl": 288, "base_isp_vac": 322, "base_thrust": 2100, "density": 1.26, 
        "flame_hex": 0xf5d0fe, "outer_hex": 0x9333ea, "spark_hex": 0xfab1a0, "risk": 0.05, "type": "hypergolic"
    },
    "【核熱】固体炉心型原子力サーマルロケット (NERVA / LH2)": {
        "base_isp_sl": 450, "base_isp_vac": 925, "base_thrust": 2500, "density": 0.30, 
        "flame_hex": 0x86efac, "outer_hex": 0x14532d, "spark_hex": 0x4ade80, "risk": 0.12, "type": "nuclear"
    },
    "【超高カロリー】発酵イースト＆濃厚バター (Baguette Fuel)": {
        "base_isp_sl": 310, "base_isp_vac": 360, "base_thrust": 2200, "density": 0.92,
        "flame_hex": 0xfef08a, "outer_hex": 0xd97706, "spark_hex": 0xffedd5, "risk": 0.0, "type": "rp1"
    },
    "【高密度黒鉛】最高級ハイユニグラファイト固体燃料": {
        "base_isp_sl": 295, "base_isp_vac": 330, "base_thrust": 2600, "density": 1.15,
        "flame_hex": 0xfde047, "outer_hex": 0xb45309, "spark_hex": 0xffffff, "risk": 0.0, "type": "solid"
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
    "軍用オリーブドラブ重装甲鋼板 [ICBM サルマト仕様]": {"base_dry_ratio": 0.088, "max_q_base": 180.0, "max_g_base": 18.0, "mat_id": "military"},
    "焼きたて小麦粉クラスト [超軽量パリパリ仕様]": {"base_dry_ratio": 0.040, "max_q_base": 70.0, "max_g_base": 8.0, "mat_id": "baguette"},
    "天然ヒノキ材＆消しゴムラバー [HB鉛筆仕様]": {"base_dry_ratio": 0.048, "max_q_base": 85.0, "max_g_base": 10.0, "mat_id": "pencil"},
    "超耐熱インコネル718 モノコック [重装甲チタン調]": {"base_dry_ratio": 0.092, "max_q_base": 195.0, "max_g_base": 16.5, "mat_id": "inconel"}
}

STRAPON_BOOSTERS = {
    "なし (単段スリムコア構成)": {"count": 0, "thrust_add": 0.0, "mass_add": 0.0, "fuel_add": 0.0, "isp_sl": 0, "type": "none"},
    "Falcon Heavy風 液体LRB × 2基 (グリッドフィン付)": {"count": 2, "thrust_add": 5800.0, "mass_add": 50.0, "fuel_add": 820.0, "isp_sl": 315, "type": "lrb"},
    "Soyuz R-7風 テーパー液体ブースター × 4基 (コロリョフクロス専用)": {"count": 4, "thrust_add": 4200.0, "mass_add": 38.0, "fuel_add": 520.0, "isp_sl": 308, "type": "soyuz"},
    "SLS / H3風 巨大SRB × 2基 (白塗装＆黒ジョイントリング)": {"count": 2, "thrust_add": 8800.0, "mass_add": 68.0, "fuel_add": 950.0, "isp_sl": 278, "type": "srb"}
}

AERO_WINGS = {
    "チタン鍛造極超音速グリッドフィン × 4基 (SpaceX回収仕様)": {"lift_coeff": 0.12, "drag_penalty": 1.05, "mass": 1.2, "flutter_mach": 99.0, "wing_id": "grid"},
    "Starship風 空力エルロンボディフラップ × 4枚": {"lift_coeff": 0.35, "drag_penalty": 1.12, "mass": 2.8, "flutter_mach": 99.0, "wing_id": "starship_flap"},
    "なし (純粋な軸対称弾道ロケット)": {"lift_coeff": 0.0, "drag_penalty": 1.0, "mass": 0.0, "flutter_mach": 99.0, "wing_id": "none"},
    "軍用ミサイル制御小翼 (グリッド＆デルタ)": {"lift_coeff": 0.45, "drag_penalty": 1.15, "mass": 1.5, "flutter_mach": 99.0, "wing_id": "missile_fin"},
    "コンコルド風 ダブルデルタ超音速後退翼": {"lift_coeff": 0.95, "drag_penalty": 1.45, "mass": 7.5, "flutter_mach": 3.8, "wing_id": "delta_wing"}
}

FAIRINGS = {
    "Starship風 窓付き有人クルーノーズコーン (片面黒耐熱タイル)": {"mass": 4.2, "cd": 0.22, "heat_limit": 2900, "shape_id": "starship_crew"},
    "バイコニカル炭素複合材クラムシェル (金箔通信衛星内蔵)": {"mass": 2.1, "cd": 0.18, "heat_limit": 2600, "shape_id": "biconic"},
    "ICBM MIRV 多弾頭再突入カプセルノーズコーン": {"mass": 3.5, "cd": 0.14, "heat_limit": 3800, "shape_id": "icbm_warhead"},
    "有人カプセル ＋ レスキューアボートタワー (LES付)": {"mass": 6.8, "cd": 0.32, "heat_limit": 3200, "shape_id": "abort_tower"},
    "フランスパン 先端クープカウル": {"mass": 1.5, "cd": 0.24, "heat_limit": 2200, "shape_id": "baguette_tip"},
    "削りたて鉛筆芯ノーズコーン (黒鉛高硬度)": {"mass": 1.2, "cd": 0.20, "heat_limit": 3000, "shape_id": "pencil_tip"}
}

PRESETS = {
    "🌟 カスタム構成 (自由設定)": None,
    "🚀 SpaceX Starship & Super Heavy (IFT-5 タワーキャッチ仕様)": {
        "s1_prop": 0, "s1_cycle": 0, "s1_eng": 33, "s1_pc": 300, "s1_eps": 24, "s1_fuel": 3400.0, "s1_mat": 0, "s1_thick": 4.2,
        "strapon": 0, "spacex_rtls": True, "wings": 0, "aoa": 0.5, "rcs": 0.8,
        "s2_prop": 0, "s2_cycle": 0, "s2_eng": 6, "s2_eps": 150, "s2_fuel": 1200.0, "s2_mat": 0, "s2_thick": 3.0,
        "fairing": 0, "payload": 50.0, "water": 300, "turn_exp": 0.62
    },
    "🌕 NASA Saturn V (アポロ月面着陸ロケット)": {
        "s1_prop": 1, "s1_cycle": 2, "s1_eng": 5, "s1_pc": 70, "s1_eps": 16, "s1_fuel": 2150.0, "s1_mat": 2, "s1_thick": 5.5,
        "strapon": 0, "spacex_rtls": False, "wings": 2, "aoa": 0.0, "rcs": 1.2,
        "s2_prop": 2, "s2_cycle": 2, "s2_eng": 5, "s2_eps": 40, "s2_fuel": 450.0, "s2_mat": 2, "s2_thick": 3.8,
        "fairing": 3, "payload": 45.0, "water": 200, "turn_exp": 0.70
    },
    "🇯🇵 JAXA H3ロケット 22S (固体ブースター2基構成)": {
        "s1_prop": 2, "s1_cycle": 1, "s1_eng": 2, "s1_pc": 120, "s1_eps": 35, "s1_fuel": 250.0, "s1_mat": 1, "s1_thick": 3.2,
        "strapon": 3, "spacex_rtls": False, "wings": 2, "aoa": 0.0, "rcs": 1.0,
        "s2_prop": 2, "s2_cycle": 1, "s2_eng": 1, "s2_eps": 180, "s2_fuel": 32.0, "s2_mat": 1, "s2_thick": 2.2,
        "fairing": 1, "payload": 6.5, "water": 250, "turn_exp": 0.65
    },
    "☢️ 大陸間弾道ミサイル ICBM「RS-28 サルマト (Sarmat)」": {
        "s1_prop": 3, "s1_cycle": 1, "s1_eng": 4, "s1_pc": 210, "s1_eps": 22, "s1_fuel": 180.0, "s1_mat": 4, "s1_thick": 6.5,
        "strapon": 0, "spacex_rtls": False, "wings": 3, "aoa": 0.0, "rcs": 0.4,
        "s2_prop": 3, "s2_cycle": 1, "s2_eng": 1, "s2_eps": 60, "s2_fuel": 35.0, "s2_mat": 4, "s2_thick": 4.5,
        "fairing": 2, "payload": 10.0, "water": 80, "turn_exp": 0.48
    },
    "⚡ 極超音速滑空ミサイル「ダークイーグル (Dark Eagle LRHW)」": {
        "s1_prop": 3, "s1_cycle": 0, "s1_eng": 1, "s1_pc": 280, "s1_eps": 18, "s1_fuel": 120.0, "s1_mat": 3, "s1_thick": 4.0,
        "strapon": 0, "spacex_rtls": False, "wings": 3, "aoa": 2.0, "rcs": 0.3,
        "s2_prop": 3, "s2_cycle": 0, "s2_eng": 1, "s2_eps": 70, "s2_fuel": 25.0, "s2_mat": 3, "s2_thick": 2.5,
        "fairing": 2, "payload": 2.5, "water": 100, "turn_exp": 0.38
    },
    "🥖 【ジョーク】超音速フランスパン「バゲット・V2 (Baguette)」": {
        "s1_prop": 5, "s1_cycle": 2, "s1_eng": 7, "s1_pc": 160, "s1_eps": 20, "s1_fuel": 450.0, "s1_mat": 5, "s1_thick": 2.5,
        "strapon": 0, "spacex_rtls": False, "wings": 2, "aoa": 0.0, "rcs": 1.5,
        "s2_prop": 5, "s2_cycle": 2, "s2_eng": 1, "s2_eps": 90, "s2_fuel": 90.0, "s2_mat": 5, "s2_thick": 1.8,
        "fairing": 4, "payload": 4.0, "water": 120, "turn_exp": 0.60
    },
    "✏️ 【ジョーク】本当に鉛筆ロケット「三菱ハイユニ HB-9000」": {
        "s1_prop": 6, "s1_cycle": 2, "s1_eng": 1, "s1_pc": 190, "s1_eps": 18, "s1_fuel": 320.0, "s1_mat": 6, "s1_thick": 3.0,
        "strapon": 0, "spacex_rtls": False, "wings": 2, "aoa": 0.0, "rcs": 1.0,
        "s2_prop": 6, "s2_cycle": 2, "s2_eng": 1, "s2_eps": 80, "s2_fuel": 60.0, "s2_mat": 6, "s2_thick": 2.0,
        "fairing": 5, "payload": 2.0, "water": 90, "turn_exp": 0.55
    }
}

prop_keys = list(PROPELLANTS.keys())
cyc_keys = list(PUMP_CYCLES.keys())
mat_keys = list(MATERIALS.keys())
strap_keys = list(STRAPON_BOOSTERS.keys())
wing_keys = list(AERO_WINGS.keys())
fair_keys = list(FAIRINGS.keys())

def on_preset_change():
    chosen = st.session_state.get("preset_selector")
    cfg = PRESETS.get(chosen)
    if cfg:
        st.session_state["k_s1_prop"] = prop_keys[cfg["s1_prop"]]
        st.session_state["k_s1_cycle"] = cyc_keys[cfg["s1_cycle"]]
        st.session_state["k_s1_eng"] = int(cfg["s1_eng"])
        st.session_state["k_s1_pc"] = int(cfg["s1_pc"])
        st.session_state["k_s1_eps"] = int(cfg["s1_eps"])
        st.session_state["k_s1_fuel"] = float(cfg["s1_fuel"])
        st.session_state["k_s1_mat"] = mat_keys[cfg["s1_mat"]]
        st.session_state["k_s1_thick"] = float(cfg["s1_thick"])

        st.session_state["k_strapon"] = strap_keys[cfg["strapon"]]
        st.session_state["k_spacex_rtls"] = bool(cfg["spacex_rtls"])

        st.session_state["k_wings"] = wing_keys[cfg["wings"]]
        st.session_state["k_aoa"] = float(cfg["aoa"])
        st.session_state["k_rcs"] = float(cfg["rcs"])

        st.session_state["k_s2_prop"] = prop_keys[cfg["s2_prop"]]
        st.session_state["k_s2_cycle"] = cyc_keys[cfg["s2_cycle"]]
        st.session_state["k_s2_eng"] = int(cfg["s2_eng"])
        st.session_state["k_s2_eps"] = int(cfg["s2_eps"])
        st.session_state["k_s2_fuel"] = float(cfg["s2_fuel"])
        st.session_state["k_s2_mat"] = mat_keys[cfg["s2_mat"]]
        st.session_state["k_s2_thick"] = float(cfg["s2_thick"])

        st.session_state["k_fairing"] = fair_keys[cfg["fairing"]]
        st.session_state["k_payload"] = float(cfg["payload"])
        st.session_state["k_water"] = int(cfg["water"])
        st.session_state["k_turn_exp"] = float(cfg["turn_exp"])

if "initialized_preset" not in st.session_state:
    st.session_state["preset_selector"] = list(PRESETS.keys())[1]
    on_preset_change()
    st.session_state["initialized_preset"] = True

preset_choice = st.selectbox(
    "🎯 機体プリセット / 特殊兵器セレクター", 
    list(PRESETS.keys()), 
    key="preset_selector", 
    on_change=on_preset_change
)

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
        s1_prop = st.selectbox("第1段 推進剤", prop_keys, key="k_s1_prop")
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", cyc_keys, key="k_s1_cycle")
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, key="k_s1_eng")
    with c2:
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, step=10, key="k_s1_pc")
        s1_eps = st.slider("海面膨張比 (ε: ノズル径連動)", 8, 70, step=1, key="k_s1_eps")
    with c3:
        s1_fuel = st.slider("第1段 推進剤充填量 (トン: 胴体長連動)", 50.0, 4500.0, step=25.0, key="k_s1_fuel")
        s1_mat = st.selectbox("第1段 構造素材", mat_keys, key="k_s1_mat")
        s1_thick = st.slider("外殻等価板厚 (mm)", 1.0, 12.0, step=0.1, key="k_s1_thick")

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        strapon_opt = st.selectbox("ブースター種別クラスタ", strap_keys, key="k_strapon")
        sep_thrust_factor = st.slider("分離パイロモーター推力倍率", 0.5, 3.0, 1.2, step=0.1, key="k_sep_thrust")
    with c2:
        spacex_return_mode = st.checkbox("🔄 SpaceX型 ブースターRTLS帰還 ＆ チョップスティック・タワーキャッチ (IFT-5再現)", key="k_spacex_rtls")
        st.caption("※ ONの場合：第2段軌道投入＆第1段タワーキャッチの両方成功でミッション完了。OFFの場合：軌道投入のみでミッション完了。")

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 空力パーツ", wing_keys, key="k_wings")
        angle_of_attack = st.slider("固定取り付け迎角 AoA (deg)", -3.0, 12.0, step=0.5, key="k_aoa")
    with c2:
        rcs_deadband = st.slider("4象限RCS デッドバンド感度 (deg)", 0.2, 5.0, step=0.1, key="k_rcs")
        st.caption("※ 姿勢制御要求が発生した瞬間だけ冷ガス窒素(GN2)が一瞬パルス噴射されます。")

with tab4:
    c1, c2, c3 = st.columns(3)
    with c1:
        s2_prop = st.selectbox("第2段 推進剤", prop_keys, key="k_s2_prop")
        s2_cycle = st.selectbox("第2段 ポンプ方式", cyc_keys, key="k_s2_cycle")
        s2_eng_count = st.slider("真空ノズル基数", 1, 9, key="k_s2_eng")
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 30, 280, step=5, key="k_s2_eps")
    with c2:
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 10.0, 1500.0, step=10.0, key="k_s2_fuel")
        s2_mat = st.selectbox("第2段 構造素材", mat_keys, key="k_s2_mat")
        s2_thick = st.slider("第2段 壁厚 (mm)", 0.8, 8.0, step=0.1, key="k_s2_thick")
    with c3:
        fairing_type = st.selectbox("先端空力カウル / 弾頭 / ペイロード", fair_keys, key="k_fairing")
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 30.0, 180.0, 75.0, step=5.0, key="k_fairing_sep")
        payload_mass = st.slider("投入衛星 / 弾頭質量 (トン)", 0.2, 120.0, step=0.5, key="k_payload")

with tab5:
    c1, c2 = st.columns(2)
    with c1:
        water_flow_rate = st.slider("消音注水デリュージ流量 (トン/秒)", 50, 450, step=25, key="k_water")
        ignition_lead_time = st.slider("エンジン先行点火開始 (T-マイナス秒)", 2.5, 6.0, 3.8, step=0.1, key="k_ign_lead")
    with c2:
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.3, 15.0, 1.8, step=0.1, key="k_turn_start")
        turn_end_alt = st.slider("水平重力ターン完了高度 (km)", 50.0, 250.0, 120.0, step=5.0, key="k_turn_end")
        turn_exponent = st.slider("ターン曲率指数", 0.3, 2.0, step=0.02, key="k_turn_exp")
        throttle_maxq = st.slider("Max-Q 領域 推力抑制 (%)", 30, 100, 75, key="k_maxq_thr")
        max_g_limit_cut = st.slider("最大加速度リミッター (G)", 2.5, 18.0, 5.0, step=0.2, key="k_max_g")

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

    return {
        "isp_sl": float(isp_sl), "isp_vac": float(isp_vac),
        "thrust_sl": float(thrust_sl_per_eng * eng_count),
        "thrust_vac": float(thrust_vac_per_eng * eng_count),
        "dry_mass": float(dry_mass),
        "max_q": float(mat["max_q_base"] * (thick_factor ** 1.1)),
        "max_g": float(mat["max_g_base"] * (thick_factor ** 0.85)),
        "pc": pc, "eps": eps,
        "cd_mod": density_penalty,
        "mat_id": mat["mat_id"],
        "cyc_id": cyc["cyc_id"],
        "flame_hex": prop["flame_hex"],
        "outer_hex": prop["outer_hex"],
        "spark_hex": prop["spark_hex"],
        "eng_count": eng_count
    }

wing_spec = AERO_WINGS[wing_type]
fair_spec = FAIRINGS[fairing_type]
strapon_spec = STRAPON_BOOSTERS[strapon_opt]

s1_spec = calc_stage_specs(s1_prop, s1_cycle, s1_pc, s1_eps, s1_eng_count, s1_fuel, s1_mat, s1_thick)
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

s1_len_scaled = float(np.clip(10.0 + (s1_fuel / 4500.0) * 16.0, 9.0, 26.0))
s2_len_scaled = float(np.clip(5.0 + (s2_fuel / 1200.0) * 8.0, 4.5, 13.0))

pin_offset_3d = s1_len_scaled - 2.2
target_bottom_y_3d = 68.6 - pin_offset_3d
TOWER_PHYSICAL_CATCH_Y = max(0.0, (target_bottom_y_3d - 6.0) * 10.0)

# =========================================================================
# 💥 物理シミュレーション (慣性完全保存・滑らかな分離・正確な降下)
# =========================================================================
def run_simulation(preview_only=False):
    if preview_only:
        return [{
            "t": -10.0, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0, "stage": 1,
            "fairing": True, "wings": bool(wing_spec["wing_id"] != "none"), "strapon": bool(strapon_spec["count"] > 0),
            "exploded": False, "thrust": False, "pitch": 0.0, "mach": 0.0, "event": "PREVIEW", "rcs_cmd": 0.0,
            "s1_prop_pct": 100.0, "s2_prop_pct": 100.0, "pitch_deg": 90.0, "apogee_km": 0.0, "chamber_p": 0.0,
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False
        }], None

    dt = 0.5
    g0 = 9.80665
    R_earth = 6371000.0
    x, y, vx, vy = 0.0, 0.0, 0.0, 0.0
    stage = 1
    fuel_s1_init = float(s1_fuel * 1000.0)
    fuel_s2_init = float(s2_fuel * 1000.0)
    fuel_s1_rem = float(fuel_s1_init)
    fuel_strapon_rem = float(strapon_spec["fuel_add"] * 1000.0)
    fuel_s2_rem = float(fuel_s2_init)
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
    rcs_cooldown = 0.0

    for cd_step in range(21):
        t_cd = -10.0 + cd_step * 0.5
        history.append({
            "t": float(t_cd), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0, "stage": 1,
            "fairing": True, "wings": wings_attached, "strapon": strapon_attached, "exploded": False,
            "thrust": bool(t_cd >= -ignition_lead_time), "pitch": 0.0, "mach": 0.0, "event": "COUNTDOWN", "rcs_cmd": 0.0,
            "s1_prop_pct": 100.0, "s2_prop_pct": 100.0, "pitch_deg": 90.0, "apogee_km": 0.0,
            "chamber_p": float(s1_spec["pc"] if t_cd >= -ignition_lead_time else 0.0),
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False
        })

    t = 0.0
    step_limit = 1600
    while t < 800.0 and len(history) < step_limit:
        t += dt
        alt = max(0.0, y)
        r = R_earth + alt
        g_local = g0 * ((R_earth / r) ** 2)

        rho = 1.225 * np.exp(-alt / 8500.0) if alt < 120000.0 else 0.0
        v_sound = max(260.0, 340.0 - 0.004 * alt) if alt < 20000.0 else 295.0
        v_total = np.sqrt(vx**2 + vy**2)
        mach = v_total / v_sound
        dynamic_q = 0.5 * rho * (v_total ** 2) / 1000.0

        if fairing_attached and (alt >= fairing_sep_alt * 1000.0 or stage == 2):
            fairing_attached = False

        if strapon_attached and fuel_strapon_rem <= 0.0:
            strapon_attached = False

        if alt < turn_start_alt * 1000.0:
            pitch_deg = 90.0
        elif alt < turn_end_alt * 1000.0:
            fraction = (alt - turn_start_alt * 1000.0) / ((turn_end_alt - turn_start_alt) * 1000.0)
            pitch_deg = 90.0 - 90.0 * (fraction ** turn_exponent)
        else:
            pitch_deg = 0.0
        pitch_rad = np.radians(max(0.0, pitch_deg))

        thrust = 0.0
        isp_eff = 300.0
        m_dot = 0.0
        stage_current = stage

        if stage == 1:
            total_mass = (fuel_s1_rem + s1_spec["dry_mass"] + wing_spec["mass"] +
                          (strapon_spec["mass_add"] + fuel_strapon_rem if strapon_attached else 0.0) +
                          fuel_s2_rem + s2_spec["dry_mass"] + payload_mass +
                          (fair_spec["mass"] if fairing_attached else 0.0))
            if fuel_s1_rem > 0:
                alt_ratio = np.clip(alt / 45000.0, 0.0, 1.0)
                isp_eff = s1_spec["isp_sl"] + (s1_spec["isp_vac"] - s1_spec["isp_sl"]) * alt_ratio
                nominal_thrust = s1_spec["thrust_sl"] + (s1_spec["thrust_vac"] - s1_spec["thrust_sl"]) * alt_ratio
                if strapon_attached:
                    nominal_thrust += strapon_spec["thrust_add"]
                
                throttle = 1.0
                if dynamic_q > 25.0 and alt < 22000.0:
                    throttle = throttle_maxq / 100.0
                
                thrust = nominal_thrust * throttle * 1000.0
                m_dot = thrust / (isp_eff * g0)
                burned = m_dot * dt
                fuel_s1_rem = max(0.0, fuel_s1_rem - burned)
                if strapon_attached:
                    fuel_strapon_rem = max(0.0, fuel_strapon_rem - (strapon_spec["thrust_add"] * 1000.0 / (strapon_spec["isp_sl"] * g0)) * dt)
            else:
                stage = 2
                stage_current = 2
                # ブースター分離：本体の完全な速度・位置・姿勢をそのまま継承（慣性保存）
                b_active = True
                b_x = x
                b_y = y
                b_vx = vx - 1.5 * np.cos(pitch_rad) # スローモーションのようにゆっくり後落
                b_vy = vy - 1.5 * np.sin(pitch_rad)
                b_pitch = pitch_deg
        
        if stage == 2:
            total_mass = fuel_s2_rem + s2_spec["dry_mass"] + payload_mass + (fair_spec["mass"] if fairing_attached else 0.0)
            if fuel_s2_rem > 0:
                isp_eff = s2_spec["isp_vac"]
                nominal_thrust = s2_spec["thrust_vac"] * 1000.0
                accel_est = nominal_thrust / total_mass
                throttle = 1.0
                if accel_est > max_g_limit_cut * g0:
                    throttle = (max_g_limit_cut * g0 * total_mass) / nominal_thrust
                thrust = nominal_thrust * throttle
                m_dot = thrust / (isp_eff * g0)
                fuel_s2_rem = max(0.0, fuel_s2_rem - m_dot * dt)

        cd = (fair_spec["cd"] if fairing_attached else 0.32) * s1_spec["cd_mod"]
        if mach > 0.8 and mach < 1.3:
            cd *= 1.45
        drag = 0.5 * rho * (v_total ** 2) * cd * 12.0
        drag_x = drag * (vx / v_total) if v_total > 0 else 0.0
        drag_y = drag * (vy / v_total) if v_total > 0 else 0.0

        fx = thrust * np.cos(pitch_rad) - drag_x
        fy = thrust * np.sin(pitch_rad) - total_mass * g_local - drag_y

        ax = fx / total_mass
        ay = fy / total_mass
        total_g = np.sqrt(ax**2 + (ay + g_local)**2) / g0

        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt

        # ブースター精密ダイナミクス (分離後の滑らかな放物線 ＆ タワーキャッチ誘導)
        if b_active and not b_caught:
            b_alt = max(0.0, b_y)
            b_rho = 1.225 * np.exp(-b_alt / 8500.0) if b_alt < 120000.0 else 0.0
            b_v_tot = np.sqrt(b_vx**2 + b_vy**2)
            b_drag = 0.5 * b_rho * (b_v_tot**2) * 0.85 * 15.0
            b_dx = b_drag * (b_vx / b_v_tot) if b_v_tot > 0 else 0.0
            b_dy = b_drag * (b_vy / b_v_tot) if b_v_tot > 0 else 0.0

            b_thrust = False
            b_ax = -b_dx / s1_spec["dry_mass"]
            b_ay = -g0 - (b_dy / s1_spec["dry_mass"])

            if spacex_return_mode:
                # 姿勢制御：角速度をイーズインさせ滑らかにフリップ
                target_b_pitch = 180.0 if (b_vy > 0 and b_alt > 50000.0) else 90.0
                b_pitch += np.clip(target_b_pitch - b_pitch, -4.0, 4.0)
                
                # ブーストバック ＆ ランディングバーン
                if (b_vy > 50.0 and b_alt > 65000.0 and b_fuel > 0.0) or (b_vy < -40.0 and b_alt < 12000.0 and b_fuel > 0.0):
                    b_thrust = True
                    burn_f = s1_spec["thrust_sl"] * 0.65 * 1000.0
                    b_fuel -= (burn_f / (s1_spec["isp_sl"] * g0)) * dt
                    rad_bp = np.radians(b_pitch)
                    b_ax += (burn_f * np.cos(rad_bp)) / s1_spec["dry_mass"]
                    b_ay += (burn_f * np.sin(rad_bp)) / s1_spec["dry_mass"]

            b_vx += b_ax * dt
            b_vy += b_ay * dt
            b_x += b_vx * dt
            b_y += b_vy * dt

            if b_y <= TOWER_PHYSICAL_CATCH_Y:
                b_y = TOWER_PHYSICAL_CATCH_Y
                b_vy = 0.0
                b_vx = 0.0
                b_thrust = False
                if spacex_return_mode and abs(b_x) < 2000.0:
                    b_caught = True

        rcs_cmd = 0.0
        pitch_diff = abs(pitch_deg - prev_pitch_val)
        if pitch_diff > (rcs_deadband * 0.1):
            rcs_cmd = 1.0 if (pitch_deg < prev_pitch_val) else -1.0
        prev_pitch_val = pitch_deg

        event_str = "FLIGHT"
        if dynamic_q > s1_spec["max_q"]:
            fail_reason = f"Max-Q 構造限界超過により空中分解！ (動圧: {dynamic_q:.1f} kPa > 耐力: {s1_spec['max_q']:.1f} kPa)"
            break
        if total_g > s1_spec["max_g"]:
            fail_reason = f"最大許容加速度超過により機体圧壊！ (発生加速度: {total_g:.1f} G > 耐力: {s1_spec['max_g']:.1f} G)"
            break
        if y < -10.0:
            fail_reason = "推力不足またはピッチ操作失敗により地表墜落！"
            break
        if vx >= 7800.0 and alt >= 180000.0:
            event_str = "ORBIT REACHED"
            break

        history.append({
            "t": float(round(t, 2)), "x": float(x), "y": float(y), "alt": float(alt), "v": float(v_total),
            "q": float(dynamic_q), "g": float(total_g), "stage": int(stage_current),
            "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached, "exploded": False,
            "thrust": bool(thrust > 0.0), "pitch": float(90.0 - pitch_deg), "mach": float(mach), "event": event_str,
            "rcs_cmd": float(rcs_cmd), "s1_prop_pct": float(max(0.0, fuel_s1_rem / fuel_s1_init * 100.0)),
            "s2_prop_pct": float(max(0.0, fuel_s2_rem / fuel_s2_init * 100.0)), "pitch_deg": float(pitch_deg),
            "apogee_km": float((alt + (vy**2)/(2*g0))/1000.0) if vy > 0 else float(alt/1000.0),
            "chamber_p": float(s1_spec["pc"] if stage_current == 1 and thrust > 0 else (220.0 if stage_current == 2 and thrust > 0 else 0.0)),
            "b_x": float(b_x), "b_y": float(b_y), "b_active": bool(b_active), "b_pitch": float(90.0 - b_pitch),
            "b_thrust": bool(b_thrust), "b_caught": bool(b_caught)
        })

    return history, fail_reason

# プレビュー用または実走行
sim_data, fail_msg = run_simulation(preview_only=False)
if fail_msg:
    st.error(f"⚠️ シミュレーション警告: {fail_msg}")

sim_json_str = json.dumps(sim_data)

# =========================================================================
# 🎨 4K実写級 Three.js & Web Audio API レンダラー
# =========================================================================
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin: 0; padding: 0; overflow: hidden; background: #000; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  #canvas-container {{ width: 100vw; height: 92vh; position: absolute; left: 0; top: 0; }}
  #hud {{
    position: absolute; top: 16px; left: 16px; color: #fff; z-index: 100;
    background: rgba(10, 15, 25, 0.78); backdrop-filter: blur(12px);
    padding: 18px 24px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5); pointer-events: none; min-width: 240px;
  }}
  .hud-val {{ font-size: 26px; font-weight: 800; font-family: "SF Pro Display", monospace; color: #38bdf8; }}
  .hud-sub {{ font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 2px; }}
  .hud-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; }}
  #controls {{
    position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%);
    z-index: 100; display: flex; gap: 12px; background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(14px); padding: 10px 20px; border-radius: 40px; border: 1px solid rgba(255,255,255,0.2);
  }}
  button {{
    background: #2563eb; color: #fff; border: none; padding: 10px 22px;
    border-radius: 20px; font-weight: 700; cursor: pointer; transition: all 0.2s;
    font-size: 13px; letter-spacing: 0.5px;
  }}
  button:hover {{ background: #1d4ed8; transform: scale(1.05); }}
  #audio-btn {{ background: #059669; }}
  #audio-btn:hover {{ background: #047857; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div id="canvas-container"></div>

<div id="hud">
  <div class="hud-sub">MISSION CLOCK</div>
  <div class="hud-val" id="hud-time">T-10.0 s</div>
  <div class="hud-grid">
    <div><div class="hud-sub">ALTITUDE</div><div style="font-size: 18px; font-weight: 700;" id="hud-alt">0.00 km</div></div>
    <div><div class="hud-sub">VELOCITY</div><div style="font-size: 18px; font-weight: 700;" id="hud-vel">0.0 m/s</div></div>
    <div><div class="hud-sub">MACH</div><div style="font-size: 18px; font-weight: 700;" id="hud-mach">M 0.00</div></div>
    <div><div class="hud-sub">DYNAMIC Q</div><div style="font-size: 18px; font-weight: 700;" id="hud-q">0.0 kPa</div></div>
  </div>
  <div style="margin-top: 10px; font-size: 11px; color: #38bdf8; font-weight: 600;" id="hud-status">STATUS: PRELAUNCH COUNTDOWN</div>
</div>

<div id="controls">
  <button id="play-btn">▶ LAUNCH</button>
  <button id="reset-btn">↺ RESET</button>
  <button id="cam-btn">🎥 CAM: GROUND TRACK</button>
  <button id="audio-btn">🔊 AUDIO ON</button>
</div>

<script>
const simData = {sim_json_str};
const flameColor = {hex(s1_spec['flame_hex'])};
const sparkColor = {hex(s1_spec['spark_hex'])};
const s1Len = {s1_len_scaled};
const s2Len = {s2_len_scaled};
const isStarship = {str(fair_spec["shape_id"] == "starship_crew").lower()};
const towerPhysicalCatchY = {TOWER_PHYSICAL_CATCH_Y};

let scene, camera, renderer, controls;
let rocketGroup, s1Mesh, s2Mesh, fairingMesh, nozzleGroup;
let flameCore, shockDiamonds = [], vaporCone;
let boosterGroup, boosterFlame;
let towerGroup, chopsticksMesh;
let cloudParticles = [], steamParticles = [], iceParticles = [], ventParticles = [];
let launchLight;
let isPlaying = false, simIdx = 0, clock = 0;
let camMode = 0; // 0: Ground Telephoto, 1: Onboard Rocket, 2: Tower/Booster Cam
let audioCtx = null, engineGain = null, rumbleFilter = null, hissNode = null;
let lastSeparation = false;

function initAudio() {{
  if (audioCtx) return;
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  
  // エンジン重低音
  const bufSize = audioCtx.sampleRate * 2;
  const noiseBuf = audioCtx.createBuffer(1, bufSize, audioCtx.sampleRate);
  const out = noiseBuf.getChannelData(0);
  let lastOut = 0.0;
  for (let i = 0; i < bufSize; i++) {{
    const white = Math.random() * 2 - 1;
    out[i] = (lastOut + 0.02 * white) / 1.02; // ブラウンノイズ
    lastOut = out[i];
  }}
  const noise = audioCtx.createBufferSource();
  noise.buffer = noiseBuf;
  noise.loop = true;
  
  rumbleFilter = audioCtx.createBiquadFilter();
  rumbleFilter.type = 'lowpass';
  rumbleFilter.frequency.value = 160;

  engineGain = audioCtx.createGain();
  engineGain.gain.value = 0.0;

  noise.connect(rumbleFilter);
  rumbleFilter.connect(engineGain);
  engineGain.connect(audioCtx.destination);
  noise.start(0);
}}

// 改善5: 複合多層ステージ分離音 (低音衝撃波 + メタルラッチ + 高圧ブロー)
function triggerSeparationSound() {{
  if (!audioCtx) return;
  const now = audioCtx.currentTime;

  // 1. パイロボルト低音打撃 (120Hz -> 30Hz)
  const osc = audioCtx.createOscillator();
  const oscGain = audioCtx.createGain();
  osc.type = 'triangle';
  osc.frequency.setValueAtTime(120, now);
  osc.frequency.exponentialRampToValueAtTime(30, now + 0.15);
  oscGain.gain.setValueAtTime(0.8, now);
  oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
  osc.connect(oscGain);
  oscGain.connect(audioCtx.destination);
  osc.start(now);
  osc.stop(now + 0.2);

  // 2. 金属クランプ解放音 (800〜1200Hz ガシャン)
  const bSize = audioCtx.sampleRate * 0.1;
  const mBuf = audioCtx.createBuffer(1, bSize, audioCtx.sampleRate);
  const mOut = mBuf.getChannelData(0);
  for (let i = 0; i < bSize; i++) mOut[i] = (Math.random() * 2 - 1);
  const mSrc = audioCtx.createBufferSource();
  mSrc.buffer = mBuf;
  const mFilter = audioCtx.createBiquadFilter();
  mFilter.type = 'bandpass';
  mFilter.frequency.value = 1100;
  mFilter.Q.value = 4.0;
  const mGain = audioCtx.createGain();
  mGain.gain.setValueAtTime(0.6, now);
  mGain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
  mSrc.connect(mFilter);
  mFilter.connect(mGain);
  mGain.connect(audioCtx.destination);
  mSrc.start(now);

  // 3. 高圧ガス＆ホットステージブロー音 (シュゴォォ)
  const pSize = audioCtx.sampleRate * 0.8;
  const pBuf = audioCtx.createBuffer(1, pSize, audioCtx.sampleRate);
  const pOut = pBuf.getChannelData(0);
  for (let i = 0; i < pSize; i++) pOut[i] = (Math.random() * 2 - 1);
  const pSrc = audioCtx.createBufferSource();
  pSrc.buffer = pBuf;
  const pFilter = audioCtx.createBiquadFilter();
  pFilter.type = 'lowpass';
  pFilter.frequency.value = 450;
  const pGain = audioCtx.createGain();
  pGain.gain.setValueAtTime(0.4, now);
  pGain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
  pSrc.connect(pFilter);
  pFilter.connect(pGain);
  pGain.connect(audioCtx.destination);
  pSrc.start(now);
}}

function initScene() {{
  const container = document.getElementById('canvas-container');
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0a101e, 0.00015);

  camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 0.5, 100000);
  camera.position.set(120, 25, 180);

  renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false, powerPreference: "high-performance" }});
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  container.appendChild(renderer.domElement);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.maxPolarAngle = Math.PI / 2 - 0.01;

  // ライティング
  const hemiLight = new THREE.HemisphereLight(0xdbeafe, 0x1e293b, 0.8);
  scene.add(hemiLight);
  const dirLight = new THREE.DirectionalLight(0xfff7ed, 1.8);
  dirLight.position.set(400, 600, 300);
  scene.add(dirLight);

  launchLight = new THREE.PointLight(0xff7700, 0.0, 500);
  launchLight.position.set(0, 5, 0);
  scene.add(launchLight);

  // 地形
  const groundGeo = new THREE.PlaneGeometry(8000, 8000, 64, 64);
  const groundMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.9, metalness: 0.1 }});
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.rotation.x = -Math.PI / 2;
  scene.add(ground);

  buildTower();
  buildRocket();
  buildSteamDelugeSystem();
  buildIceParticles();
  buildCryoVentSystem();

  window.addEventListener('resize', () => {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }});
}}

// 発射台＆IFT-5チョップスティックタワー
function buildTower() {{
  towerGroup = new THREE.Group();
  const towerGeo = new THREE.BoxGeometry(7, 140, 7);
  const towerMat = new THREE.MeshStandardMaterial({{ color: 0x475569, metalness: 0.8, roughness: 0.4 }});
  const tower = new THREE.Mesh(towerGeo, towerMat);
  tower.position.set(-15, 70, 0);
  towerGroup.add(tower);

  // キャッチアーム (Chopsticks)
  chopsticksMesh = new THREE.Group();
  const armGeo = new THREE.BoxGeometry(18, 2.5, 2);
  const armMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.9, roughness: 0.3 }});
  const arm1 = new THREE.Mesh(armGeo, armMat);
  arm1.position.set(6, 0, 4.5);
  const arm2 = new THREE.Mesh(armGeo, armMat);
  arm2.position.set(6, 0, -4.5);
  chopsticksMesh.add(arm1, arm2);
  chopsticksMesh.position.set(-15, 68.6, 0);
  towerGroup.add(chopsticksMesh);

  scene.add(towerGroup);
}}

// ロケット構造 (改善1: ピボット固定 / 改善8: PBR鏡面反射 / 改善6: ショックダイヤ / 改善7: ベイパーコーン)
function buildRocket() {{
  rocketGroup = new THREE.Group();

  // PBR鏡面マテリアル
  const s1Mat = new THREE.MeshStandardMaterial({{
    color: 0xd1d5db, metalness: 0.92, roughness: 0.18
  }});
  const s2Mat = new THREE.MeshStandardMaterial({{
    color: isStarship ? 0x111827 : 0xe5e7eb, metalness: 0.85, roughness: 0.25
  }});

  // 第1段 (ブースター)
  const s1Geo = new THREE.CylinderGeometry(2.4, 2.4, s1Len, 48);
  s1Geo.translate(0, s1Len / 2, 0);
  s1Mesh = new THREE.Mesh(s1Geo, s1Mat);
  rocketGroup.add(s1Mesh);

  // 第2段 (オービター)
  const s2Geo = new THREE.CylinderGeometry(2.35, 2.35, s2Len, 48);
  s2Geo.translate(0, s2Len / 2, 0);
  s2Mesh = new THREE.Mesh(s2Geo, s2Mat);
  s2Mesh.position.y = s1Len;
  rocketGroup.add(s2Mesh);

  // 先端カウル
  const fGeo = new THREE.ConeGeometry(2.35, 6.0, 48);
  fGeo.translate(0, 3.0, 0);
  fairingMesh = new THREE.Mesh(fGeo, s2Mat);
  fairingMesh.position.y = s1Len + s2Len;
  rocketGroup.add(fairingMesh);

  // 改善1: ノズルとピボットを完全にスカート内側へ格納固定
  nozzleGroup = new THREE.Group();
  nozzleGroup.position.set(0, 0.2, 0); // スカート内部に0.2mめり込ませる
  rocketGroup.add(nozzleGroup);

  // コアフレーム (原点をノズル出口に固定しはみ出しをゼロに)
  const flameGeo = new THREE.ConeGeometry(2.1, 14.0, 32, 1, true);
  flameGeo.translate(0, -7.0, 0); // 先端を原点に
  const flameMat = new THREE.MeshBasicMaterial({{
    color: flameColor, transparent: true, opacity: 0.88, depthWrite: false, blending: THREE.AdditiveBlending
  }});
  flameCore = new THREE.Mesh(flameGeo, flameMat);
  flameCore.visible = false;
  nozzleGroup.add(flameCore);

  // 改善6: マッハダイヤモンド (ショックコーン群)
  for (let i = 0; i < 4; i++) {{
    const diaGeo = new THREE.OctahedronGeometry(0.7 - i * 0.1, 0);
    diaGeo.scale(0.8, 2.2, 0.8);
    const diaMat = new THREE.MeshBasicMaterial({{
      color: sparkColor, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending
    }});
    const diaMesh = new THREE.Mesh(diaGeo, diaMat);
    diaMesh.position.y = -(2.0 + i * 2.4);
    flameCore.add(diaMesh);
    shockDiamonds.push(diaMesh);
  }}

  // 改善7: プラントル・グロージャート・ベイパーコーン (音速突破時の水蒸気傘)
  const coneGeo = new THREE.ConeGeometry(4.2, 3.5, 32, 1, true);
  coneGeo.translate(0, 1.75, 0);
  const coneMat = new THREE.MeshStandardMaterial({{
    color: 0xffffff, transparent: true, opacity: 0.0, roughness: 0.8, side: THREE.DoubleSide
  }});
  vaporCone = new THREE.Mesh(coneGeo, coneMat);
  vaporCone.position.y = s1Len * 0.7;
  rocketGroup.add(vaporCone);

  // 独立分離ブースターグループ
  boosterGroup = new THREE.Group();
  const bGeo = new THREE.CylinderGeometry(2.4, 2.4, s1Len, 48);
  bGeo.translate(0, s1Len / 2, 0);
  const bMesh = new THREE.Mesh(bGeo, s1Mat);
  boosterGroup.add(bMesh);

  const bFlameGeo = new THREE.ConeGeometry(2.1, 12.0, 32, 1, true);
  bFlameGeo.translate(0, -6.0, 0);
  boosterFlame = new THREE.Mesh(bFlameGeo, flameMat);
  boosterFlame.position.set(0, 0.2, 0);
  boosterFlame.visible = false;
  boosterGroup.add(boosterFlame);
  boosterGroup.visible = false;

  scene.add(rocketGroup);
  scene.add(boosterGroup);
}}

// 改善4: 発射時消音デリュージ＆水蒸気爆散システム
function buildSteamDelugeSystem() {{
  const steamGeo = new THREE.SphereGeometry(1.5, 8, 8);
  const steamMat = new THREE.MeshStandardMaterial({{
    color: 0xf1f5f9, roughness: 0.9, transparent: true, opacity: 0.0, depthWrite: false
  }});
  for (let i = 0; i < 90; i++) {{
    const p = new THREE.Mesh(steamGeo, steamMat.clone());
    p.visible = false;
    scene.add(p);
    steamParticles.push({{
      mesh: p,
      vx: (Math.random() - 0.5) * 45.0,
      vz: (Math.random() - 0.5) * 45.0,
      vy: Math.random() * 8.0 + 1.0,
      life: 0.0,
      maxLife: 3.5 + Math.random() * 2.0
    }});
  }}
}}

// 改善6-4: 発射瞬間の氷の剥離 (Ice Shedding)
function buildIceParticles() {{
  const iceGeo = new THREE.BoxGeometry(0.2, 0.2, 0.2);
  const iceMat = new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.8 }});
  for (let i = 0; i < 60; i++) {{
    const p = new THREE.Mesh(iceGeo, iceMat);
    p.visible = false;
    scene.add(p);
    iceParticles.push({{ mesh: p, vy: 0, life: 0 }});
  }}
}}

// 改善6-3: カウントダウン中の極低温クライオベント (ボイルオフガス)
function buildCryoVentSystem() {{
  const ventGeo = new THREE.SphereGeometry(0.3, 6, 6);
  const ventMat = new THREE.MeshBasicMaterial({{ color: 0xe2e8f0, transparent: true, opacity: 0.35 }});
  for (let i = 0; i < 20; i++) {{
    const p = new THREE.Mesh(ventGeo, ventMat);
    p.visible = false;
    scene.add(p);
    ventParticles.push({{ mesh: p, life: 0 }});
  }}
}}

function triggerIceShedding(baseY) {{
  iceParticles.forEach(p => {{
    if (p.life <= 0) {{
      p.mesh.position.set((Math.random() - 0.5) * 4.8, baseY + Math.random() * s1Len, (Math.random() - 0.5) * 4.8);
      p.vy = -Math.random() * 8.0 - 4.0;
      p.life = 1.0;
      p.mesh.visible = true;
    }}
  }});
}}

// 改善3: 4象限RCSの精密パルス噴射表現
function triggerRCSPulse(direction, parentGroup, heightY) {{
  const rcsGeo = new THREE.ConeGeometry(0.3, 2.8, 8);
  rcsGeo.translate(0, 1.4, 0);
  const rcsMat = new THREE.MeshBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.85 }});
  const rcs = new THREE.Mesh(rcsGeo, rcsMat);
  rcs.rotation.z = direction > 0 ? Math.PI / 2 : -Math.PI / 2;
  rcs.position.set(direction > 0 ? -2.4 : 2.4, heightY, 0);
  parentGroup.add(rcs);
  setTimeout(() => {{ parentGroup.remove(rcs); }}, 120);
}}

function updateSimulation() {{
  if (!isPlaying || simIdx >= simData.length - 1) return;

  clock += 0.016;
  const cur = simData[simIdx];
  const next = simData[Math.min(simIdx + 1, simData.length - 1)];
  const alpha = 0.5;

  const curY = cur.alt;
  const curPitch = cur.pitch;
  const curStage = cur.stage;

  // 1. 機体位置と姿勢
  rocketGroup.position.set(cur.x * 0.1, curY, 0);
  rocketGroup.rotation.z = THREE.MathUtils.degToRad(-curPitch);

  // 2. エンジン炎とマッハダイヤ・高高度プルーム膨張
  if (cur.thrust) {{
    flameCore.visible = true;
    launchLight.intensity = Math.min(2.5, Math.max(0.2, 10.0 / (curY + 5.0)));

    // 改善6-2: 高度に応じたアンダーエクスパンション (横への広がり)
    const expansionRatio = 1.0 + Math.min(4.5, (curY / 30000.0) * 3.5);
    flameCore.scale.set(expansionRatio, 1.0 + Math.random() * 0.2, expansionRatio);

    // ショックダイヤの微振動
    shockDiamonds.forEach((d, i) => {{
      d.visible = curY < 25000.0;
      d.position.y = -(2.0 + i * 2.2) * (1.0 + Math.sin(clock * 30.0 + i) * 0.08);
    }});
  }} else {{
    flameCore.visible = false;
    launchLight.intensity = 0.0;
  }}

  // 3. 改善5: ステージ分離検知と音響
  if (curStage === 2 && !lastSeparation) {{
    lastSeparation = true;
    s1Mesh.visible = false; // ブースターが分離して独立動作へ移行
    triggerSeparationSound();
  }}

  // 4. 改善2: ブースターの滑らかで慣性を維持した帰還
  if (cur.b_active) {{
    boosterGroup.visible = true;
    boosterGroup.position.set(cur.b_x * 0.1, cur.b_y, 0);
    boosterGroup.rotation.z = THREE.MathUtils.degToRad(-cur.b_pitch);
    boosterFlame.visible = cur.b_thrust;
  }}

  // 改善10: チョップスティックの油圧ダンパー沈み込み
  if (cur.b_caught) {{
    chopsticksMesh.position.y = 68.6 - Math.sin(Math.min(Math.PI / 2, clock * 4.0)) * 1.5;
  }}

  // 5. 改善7: ベイパーコーン (Mach 0.95〜1.1)
  if (cur.mach >= 0.94 && cur.mach <= 1.08 && curY < 18000.0) {{
    vaporCone.material.opacity = Math.sin((cur.mach - 0.94) / 0.14 * Math.PI) * 0.55;
  }} else {{
    vaporCone.material.opacity = 0.0;
  }}

  // 6. 改善4: デリュージ水蒸気の水平爆散
  if (cur.t >= -2.0 && cur.t <= 6.0) {{
    steamParticles.forEach(p => {{
      if (p.life <= 0 && Math.random() < 0.25) {{
        p.life = 0.01;
        p.mesh.position.set(0, 1.5, 0);
        p.mesh.visible = true;
      }}
    }});
    if (cur.t >= 0 && cur.t <= 2.5) triggerIceShedding(curY);
  }}

  // 水蒸気物理シミュレーション (水平爆散 ＆ 上昇ドラッグ)
  steamParticles.forEach(p => {{
    if (p.life > 0) {{
      p.life += 0.016;
      p.mesh.position.x += p.vx * 0.016;
      p.mesh.position.z += p.vz * 0.016;
      p.mesh.position.y += p.vy * 0.016;
      p.vx *= 0.94; // 空気抵抗
      p.vz *= 0.94;
      p.vy += 0.08; // 浮力
      const progress = p.life / p.maxLife;
      const s = 1.0 + progress * 8.0;
      p.mesh.scale.set(s, s, s);
      p.mesh.material.opacity = Math.max(0.0, (1.0 - progress) * 0.45);
      if (progress >= 1.0) {{ p.life = 0; p.mesh.visible = false; }}
    }}
  }});

  // 氷パーティクル更新
  iceParticles.forEach(p => {{
    if (p.life > 0) {{
      p.mesh.position.y += p.vy * 0.016;
      p.life -= 0.016;
      if (p.mesh.position.y < 0) p.life = 0;
      if (p.life <= 0) p.mesh.visible = false;
    }}
  }});

  // クライオベント更新
  if (cur.t < 0) {{
    ventParticles.forEach((p, idx) => {{
      if (!p.mesh.visible || p.life <= 0) {{
        p.mesh.visible = true;
        p.mesh.position.set(2.4, s1Len * 0.85, 0);
        p.life = 1.0;
      }} else {{
        p.mesh.position.x += 0.05;
        p.mesh.position.y -= 0.08;
        p.life -= 0.02;
        if (p.life <= 0) p.mesh.visible = false;
      }}
    }});
  }}

  // 7. RCSパルス噴射
  if (cur.rcs_cmd !== 0 && Math.random() < 0.2) {{
    triggerRCSPulse(cur.rcs_cmd, curStage === 1 ? rocketGroup : s2Mesh, s1Len * 0.9);
  }}

  // 8. 改善9: 音響の距離減衰と高音ローパス吸収
  if (audioCtx && engineGain) {{
    if (cur.thrust) {{
      const dist = camera.position.distanceTo(rocketGroup.position);
      const targetGain = Math.min(1.0, 180.0 / (dist + 40.0));
      engineGain.gain.setTargetAtTime(targetGain, audioCtx.currentTime, 0.1);
      const targetCutoff = Math.max(80.0, 450.0 - (dist * 0.05));
      rumbleFilter.frequency.setTargetAtTime(targetCutoff, audioCtx.currentTime, 0.1);
    }} else {{
      engineGain.gain.setTargetAtTime(0.001, audioCtx.currentTime, 0.2);
    }}
  }}

  // HUD更新
  document.getElementById('hud-time').innerText = (cur.t < 0 ? 'T' : 'T+') + cur.t.toFixed(1) + ' s';
  document.getElementById('hud-alt').innerText = (cur.alt / 1000.0).toFixed(2) + ' km';
  document.getElementById('hud-vel').innerText = cur.v.toFixed(1) + ' m/s';
  document.getElementById('hud-mach').innerText = 'M ' + cur.mach.toFixed(2);
  document.getElementById('hud-q').innerText = cur.q.toFixed(1) + ' kPa';
  document.getElementById('hud-status').innerText = 'STATUS: ' + cur.event;

  // カメラ追尾 (改善6-5: 望遠圧縮と三脚手ブレ)
  if (camMode === 0) {{
    camera.lookAt(rocketGroup.position.x, rocketGroup.position.y + s1Len * 0.5, rocketGroup.position.z);
    const shake = cur.thrust ? (Math.sin(clock * 45.0) * 0.12 * Math.min(1.0, 50.0 / (curY + 10.0))) : 0.0;
    camera.position.x = 120 + shake;
    camera.position.y = 25 + (curY * 0.12);
  }} else if (camMode === 1) {{
    camera.position.set(rocketGroup.position.x + 8, rocketGroup.position.y + s1Len * 0.9, rocketGroup.position.z + 8);
    camera.lookAt(rocketGroup.position.x, rocketGroup.position.y - 10, rocketGroup.position.z);
  }} else if (camMode === 2) {{
    camera.position.set(towerGroup.position.x + 35, 80, towerGroup.position.z + 35);
    camera.lookAt(towerGroup.position.x, 70, towerGroup.position.z);
  }}

  simIdx++;
}}

function animate() {{
  requestAnimationFrame(animate);
  updateSimulation();
  controls.update();
  renderer.render(scene, camera);
}}

// UIイベントハンドラー
document.getElementById('play-btn').addEventListener('click', () => {{
  initAudio();
  isPlaying = !isPlaying;
  document.getElementById('play-btn').innerText = isPlaying ? '⏸ PAUSE' : '▶ LAUNCH';
}});

document.getElementById('reset-btn').addEventListener('click', () => {{
  isPlaying = false;
  simIdx = 0;
  clock = 0;
  lastSeparation = false;
  s1Mesh.visible = true;
  boosterGroup.visible = false;
  document.getElementById('play-btn').innerText = '▶ LAUNCH';
}});

document.getElementById('cam-btn').addEventListener('click', () => {{
  camMode = (camMode + 1) % 3;
  const labels = ['🎥 CAM: GROUND TELEPHOTO', '🎥 CAM: ONBOARD ROCKET', '🎥 CAM: TOWER CATCH'];
  document.getElementById('cam-btn').innerText = labels[camMode];
}});

document.getElementById('audio-btn').addEventListener('click', () => {{
  initAudio();
  document.getElementById('audio-btn').innerText = '🔊 AUDIO ACTIVE';
}});

window.onload = () => {{
  initScene();
  animate();
}};
</script>
</body>
</html>
"""

components.html(html_code, height=720, scrolling=False)
