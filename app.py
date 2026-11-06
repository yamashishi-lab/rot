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

preset_choice = st.selectbox("🎯 機体プリセット / 特殊兵器セレクター", list(PRESETS.keys()), index=1)
p_cfg = PRESETS[preset_choice]

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

prop_keys = list(PROPELLANTS.keys())
cyc_keys = list(PUMP_CYCLES.keys())
mat_keys = list(MATERIALS.keys())
strap_keys = list(STRAPON_BOOSTERS.keys())
wing_keys = list(AERO_WINGS.keys())
fair_keys = list(FAIRINGS.keys())

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        s1_prop = st.selectbox("第1段 推進剤", prop_keys, index=p_cfg["s1_prop"] if p_cfg else 0)
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", cyc_keys, index=p_cfg["s1_cycle"] if p_cfg else 0)
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, p_cfg["s1_eng"] if p_cfg else 33)
    with c2:
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, p_cfg["s1_pc"] if p_cfg else 300, step=10)
        s1_eps = st.slider("海面膨張比 (ε: ノズル径連動)", 8, 70, p_cfg["s1_eps"] if p_cfg else 24, step=1)
    with c3:
        s1_fuel = st.slider("第1段 推進剤充填量 (トン: 胴体長連動)", 50.0, 4500.0, p_cfg["s1_fuel"] if p_cfg else 3400.0, step=25.0)
        s1_mat = st.selectbox("第1段 構造素材", mat_keys, index=p_cfg["s1_mat"] if p_cfg else 0)
        s1_thick = st.slider("外殻等価板厚 (mm)", 1.0, 12.0, p_cfg["s1_thick"] if p_cfg else 4.2, step=0.1)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        strapon_opt = st.selectbox("ブースター種別クラスタ", strap_keys, index=p_cfg["strapon"] if p_cfg else 0)
        sep_thrust_factor = st.slider("分離パイロモーター推力倍率", 0.5, 3.0, 1.2, step=0.1)
    with c2:
        spacex_return_mode = st.checkbox("🔄 SpaceX型 ブースターRTLS帰還 ＆ チョップスティック・タワーキャッチ (IFT-5再現)", value=p_cfg["spacex_rtls"] if p_cfg else True)
        st.caption("※ ONの場合：第2段軌道投入＆第1段タワーキャッチの両方成功でミッション完了。OFFの場合：軌道投入のみでミッション完了。")

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 空力パーツ", wing_keys, index=p_cfg["wings"] if p_cfg else 0)
        angle_of_attack = st.slider("固定取り付け迎角 AoA (deg)", -3.0, 12.0, p_cfg["aoa"] if p_cfg else 0.5, step=0.5)
    with c2:
        rcs_deadband = st.slider("4象限RCS デッドバンド感度 (deg)", 0.2, 5.0, p_cfg["rcs"] if p_cfg else 0.8, step=0.1)
        st.caption("※ 姿勢制御要求が発生した瞬間だけ冷ガス窒素(GN2)が一瞬パルス噴射されます。")

with tab4:
    c1, c2, c3 = st.columns(3)
    with c1:
        s2_prop = st.selectbox("第2段 推進剤", prop_keys, index=p_cfg["s2_prop"] if p_cfg else 0)
        s2_cycle = st.selectbox("第2段 ポンプ方式", cyc_keys, index=p_cfg["s2_cycle"] if p_cfg else 0)
        s2_eng_count = st.slider("真空ノズル基数", 1, 9, p_cfg["s2_eng"] if p_cfg else 6)
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 30, 280, p_cfg["s2_eps"] if p_cfg else 150, step=5)
    with c2:
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 10.0, 1500.0, p_cfg["s2_fuel"] if p_cfg else 1200.0, step=10.0)
        s2_mat = st.selectbox("第2段 構造素材", mat_keys, index=p_cfg["s2_mat"] if p_cfg else 0)
        s2_thick = st.slider("第2段 壁厚 (mm)", 0.8, 8.0, p_cfg["s2_thick"] if p_cfg else 3.0, step=0.1)
    with c3:
        fairing_type = st.selectbox("先端空力カウル / 弾頭 / ペイロード", fair_keys, index=p_cfg["fairing"] if p_cfg else 0)
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 30.0, 180.0, 75.0, step=5.0)
        payload_mass = st.slider("投入衛星 / 弾頭質量 (トン)", 0.2, 120.0, p_cfg["payload"] if p_cfg else 50.0, step=0.5)

with tab5:
    c1, c2 = st.columns(2)
    with c1:
        water_flow_rate = st.slider("消音注水デリュージ流量 (トン/秒)", 50, 450, p_cfg["water"] if p_cfg else 300, step=25)
        ignition_lead_time = st.slider("エンジン先行点火開始 (T-マイナス秒)", 2.5, 6.0, 3.8, step=0.1)
    with c2:
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.3, 15.0, 1.8, step=0.1)
        turn_end_alt = st.slider("水平重力ターン完了高度 (km)", 50.0, 250.0, 120.0, step=5.0)
        turn_exponent = st.slider("ターン曲率指数", 0.3, 2.0, p_cfg["turn_exp"] if p_cfg else 0.62, step=0.02)
        throttle_maxq = st.slider("Max-Q 領域 推力抑制 (%)", 30, 100, 75)
        max_g_limit_cut = st.slider("最大加速度リミッター (G)", 2.5, 18.0, 5.0, step=0.2)

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
# 💥 物理シミュレーション
# =========================================================================
def run_simulation(preview_only=False):
    if preview_only:
        return [{
            "t": -10.0, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0, "stage": 1,
            "fairing": True, "wings": bool(wing_spec["wing_id"] != "none"), "strapon": bool(strapon_spec["count"] > 0),
            "exploded": False, "thrust": False, "pitch": 0.0, "mach": 0.0, "event": "PREVIEW", "rcs_cmd": 0.0,
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False
        }], None

    dt = 0.5
    g0 = 9.80665
    R_earth = 6371000.0
    x, y, vx, vy = 0.0, 0.0, 0.0, 0.0
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
    rcs_cooldown = 0.0

    for cd_step in range(21):
        t_cd = -10.0 + cd_step * 0.5
        history.append({
            "t": float(t_cd), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0, "stage": 1,
            "fairing": True, "wings": wings_attached, "strapon": strapon_attached, "exploded": False,
            "thrust": bool(t_cd >= -ignition_lead_time), "pitch": 0.0, "mach": 0.0, "event": "COUNTDOWN", "rcs_cmd": 0.0,
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False
        })

    maxq_passed, supersonic_called = False, False
    TARGET_ALT_KM, TARGET_ORBITAL_VX = 250.0, 7900.0

    for step in range(3500):
        t = float(step * dt)
        alt = float(y)
        alt_km = float(alt / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))
        mach = v / 340.0
        rho = float(1.225 * np.exp(-alt / 7400.0)) if alt < 140000 else 0.0
        q = float(0.5 * rho * (v**2) / 1000.0)

        if alt_km < turn_start_alt:
            target_pitch_deg = 90.0
        elif alt_km < 230.0:
            prog = (alt_km - turn_start_alt) / (230.0 - turn_start_alt)
            target_pitch_deg = 90.0 * (1.0 - (prog ** turn_exponent))
        else:
            target_pitch_deg = 0.0

        wing_lift_force = 0.0
        if wings_attached and alt_km < 50.0 and rho > 0.003:
            wing_lift_force = 0.5 * rho * (v**2) * (wing_spec["lift_coeff"] * 24.0) * np.sin(np.radians(angle_of_attack))
            target_pitch_deg -= (wing_lift_force / 12000.0) * (mach ** 1.3)

        pitch_deg = max(0.0, min(90.0, target_pitch_deg))
        pitch_rad = float(np.radians(pitch_deg))
        visual_pitch = float(np.radians(90.0 - pitch_deg))

        pitch_rate = (pitch_deg - prev_pitch_val) / dt
        prev_pitch_val = pitch_deg
        rcs_cmd = 0.0
        if rcs_cooldown > 0:
            rcs_cooldown -= dt
        elif (abs(pitch_rate) > 0.06 and alt_km > 0.8) or (alt_km >= 230.0 and pitch_deg > 0.1):
            rcs_cmd = -1.0 if pitch_rate > 0 else 1.0
            rcs_cooldown = 5.5

        cur_event = "FLIGHT"
        if v >= 340.0 and not supersonic_called:
            cur_event, supersonic_called = "SUPERSONIC", True
        elif alt_km > 11.0 and not maxq_passed:
            cur_event, maxq_passed = "MAX_Q", True

        if fairing_attached and alt_km >= fairing_sep_alt:
            fairing_attached, cur_event = False, "FAIRING_SEP"

        f_mass = (fair_spec["mass"] * 1000.0) if fairing_attached else 0.0
        w_mass = (wing_spec["mass"] * 1000.0) if wings_attached else 0.0
        strap_m = (strapon_spec["mass_add"] * 1000.0 + max(0.0, fuel_strapon_rem)) if strapon_attached else 0.0

        if stage == 1:
            if strapon_attached:
                if fuel_strapon_rem > 0 and (fuel_s1_rem > s1_fuel * 1000.0 * 0.28):
                    strap_thrust = strapon_spec["thrust_add"] * 1000.0
                    fuel_strapon_rem -= (strap_thrust / (strapon_spec["isp_sl"] * g0)) * dt * 1.3
                else:
                    strapon_attached, cur_event, strap_thrust = False, "BOOSTER_SEP", 0.0
            else:
                strap_thrust = 0.0

            meco_thresh = (s1_fuel * 1000.0 * 0.18) if spacex_return_mode else 0.0
            if fuel_s1_rem <= meco_thresh:
                stage, strapon_attached, cur_event, thrust = 2, False, "HOT_STAGING", 0.0
                if spacex_return_mode and not b_active:
                    b_active = True
                    b_x, b_y = x, y
                    b_vy = -45.0
                    b_vx = -(b_x / 55.0)
                    b_pitch = 0.20
            else:
                cur_mass = float((s1_spec["dry_mass"] + s2_fuel + s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + w_mass + strap_m + fuel_s1_rem)
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s1_spec["isp_vac"] - (s1_spec["isp_vac"] - s1_spec["isp_sl"]) * atm_factor)
                thrust_core = float((s1_spec["thrust_vac"] - (s1_spec["thrust_vac"] - s1_spec["thrust_sl"]) * atm_factor) * 1000.0)

                if t < 3.0: thrust_core *= (0.65 + (t / 3.0) * 0.35)
                if 8000 < alt < 17000: thrust_core *= (throttle_maxq / 100.0)

                thrust = thrust_core + strap_thrust
                if thrust / (cur_mass * g0) > max_g_limit_cut: thrust = max_g_limit_cut * cur_mass * g0
                fuel_s1_rem -= (thrust_core / (isp * g0)) * dt

        if stage == 2:
            strapon_attached = False
            cur_mass = float((s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_mass + max(0.0, fuel_s2_rem))
            if fuel_s2_rem <= 0:
                thrust = 0.0
            else:
                atm_factor = float(np.exp(-alt / 7400.0))
                isp = float(s2_spec["isp_vac"] - (s2_spec["isp_vac"] - s2_spec["isp_sl"]) * atm_factor)
                thrust_base = float((s2_spec["thrust_vac"] - (s2_spec["thrust_vac"] - s2_spec["thrust_sl"]) * atm_factor) * 1000.0)
                speed_error = TARGET_ORBITAL_VX - vx
                thrust = 0.0 if speed_error <= 0.0 else (thrust_base * max(0.05, speed_error / 400.0) if speed_error < 400.0 else thrust_base)
                if thrust / (cur_mass * g0) > max_g_limit_cut: thrust = max_g_limit_cut * cur_mass * g0
                fuel_s2_rem -= (thrust / (isp * g0)) * dt

        if b_active and not b_caught:
            b_alt = b_y
            b_rho = float(1.225 * np.exp(-b_alt / 7400.0)) if b_alt < 140000 else 0.0
            b_v = float(np.sqrt(b_vx**2 + b_vy**2))
            b_drag = 0.5 * b_rho * (b_v**2) * 18.0 * 0.85
            b_drag_y = -b_drag * (b_vy / b_v) if b_v > 0 else 0.0

            if b_alt > 35000 and b_fuel > s1_fuel * 1000 * 0.04:
                b_pitch, b_thrust = -1.57, True
                b_force = s1_spec["thrust_vac"] * 1000.0 * 0.95
                b_fuel -= (b_force / (s1_spec["isp_vac"] * g0)) * dt
                b_vx -= (b_force / (s1_spec["dry_mass"] * 1000.0)) * dt * 2.8
            elif 12000 < b_alt <= 28000 and b_vy < -400 and b_fuel > s1_fuel * 1000 * 0.015:
                b_pitch, b_thrust = np.clip(-b_vx * 0.0008, -0.2, 0.2), True
                b_force = s1_spec["thrust_vac"] * 1000.0 * 0.85
                b_fuel -= (b_force / (s1_spec["isp_vac"] * g0)) * dt
                b_vy += (b_force / (s1_spec["dry_mass"] * 1000.0)) * dt * 0.9
            elif b_alt <= (TOWER_PHYSICAL_CATCH_Y + 3600.0):
                rem_h = max(0.0, b_alt - TOWER_PHYSICAL_CATCH_Y)
                b_thrust = True
                b_x = rem_h * 0.16
                b_pitch = np.clip((rem_h / 3600.0) * 0.20, 0.0, 0.20)
                desired_vy = -max(2.2, rem_h * 0.24)
                b_vy += (desired_vy - b_vy) * 0.55
                b_vx = -b_x * 0.65
            else:
                b_pitch = np.clip((b_x / 4000.0) * 0.2, -0.25, 0.25)
                b_vx += (-b_x / 25.0 - b_vx) * 0.25
                b_thrust = False

            b_vy += (-g0 + b_drag_y / (s1_spec["dry_mass"] * 1000.0)) * dt
            b_x = max(0.0, b_x + b_vx * dt)
            b_y = max(TOWER_PHYSICAL_CATCH_Y, b_y + b_vy * dt)

            if b_y <= (TOWER_PHYSICAL_CATCH_Y + 12.0) and abs(b_x) < 40.0:
                b_caught, b_y, b_x, b_vx, b_vy, b_pitch, b_thrust = True, TOWER_PHYSICAL_CATCH_Y, 0.0, 0.0, 0.0, 0.0, False

        dir_x, dir_y = float(np.cos(pitch_rad)), float(np.sin(pitch_rad))
        drag_area = (13.0 * s1_spec["cd_mod"] * wing_spec["drag_penalty"]) if stage == 1 else (5.2 * s2_spec["cd_mod"])
        drag_force = float(0.5 * rho * (v**2) * fair_spec["cd"] * drag_area)
        drag_x = -drag_force * (vx / v) if v > 0 else 0.0
        drag_y = -drag_force * (vy / v) if v > 0 else 0.0

        g_cur = float(g0 * ((R_earth / (R_earth + alt)) ** 2))
        grav_y = -cur_mass * (g_cur - (vx ** 2) / (R_earth + alt))

        fx = thrust * dir_x + drag_x - wing_lift_force * dir_y
        fy = thrust * dir_y + drag_y + wing_lift_force * dir_x + grav_y

        if alt <= 0.0 and fy <= 0.0:
            ax, ay, vx, vy, acc_g = 0.0, 0.0, 0.0, 0.0, 1.0
        else:
            ax, ay = fx / cur_mass, fy / cur_mass
            acc_g = float(np.sqrt((thrust * dir_x + drag_x)**2 + (thrust * dir_y + drag_y)**2) / (cur_mass * g0))

        cur_spec = s1_spec if stage == 1 else s2_spec
        if q > cur_spec["max_q"]:
            fail_reason = f"Max-Q 構造圧壊: 動圧 {q:.1f} kPa が強度限界を超過。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "stage": int(stage),
                "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached, "exploded": True,
                "thrust": False, "pitch": visual_pitch, "mach": mach, "event": "RUD", "rcs_cmd": 0.0,
                "b_x": float(b_x), "b_y": float(b_y), "b_active": b_active, "b_pitch": float(b_pitch), "b_thrust": b_thrust, "b_caught": b_caught
            })
            break

        vx, vy = float(vx + ax * dt), float(vy + ay * dt)
        x, y = float(x + vx * dt), float(max(0.0, y + vy * dt))

        is_orbit_achieved = bool(alt_km >= 230.0 and vx >= 7850.0)

        history.append({
            "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g, "stage": int(stage),
            "fairing": bool(fairing_attached), "wings": bool(wings_attached), "strapon": bool(strapon_attached), "exploded": False,
            "thrust": bool(thrust > 0 and not is_orbit_achieved), "pitch": visual_pitch, "mach": mach,
            "event": "ORBIT" if is_orbit_achieved else cur_event, "rcs_cmd": rcs_cmd,
            "b_x": float(b_x), "b_y": float(b_y), "b_active": b_active, "b_pitch": float(b_pitch), "b_thrust": b_thrust, "b_caught": b_caught
        })

        if is_orbit_achieved and (not spacex_return_mode or b_caught):
            for orbit_step in range(25):
                history.append({
                    "t": t + (orbit_step + 1) * dt, "x": x + vx * (orbit_step + 1) * dt, "y": y, "alt": alt_km, "v": v,
                    "q": 0.0, "g": 0.0, "stage": 2, "fairing": False, "wings": wings_attached, "strapon": False, "exploded": False,
                    "thrust": False, "pitch": 1.5708, "mach": mach, "event": "ORBIT", "rcs_cmd": 0.0,
                    "b_x": float(b_x), "b_y": float(b_y), "b_active": b_active, "b_pitch": float(b_pitch), "b_thrust": False, "b_caught": True
                })
            break

    if not fail_reason and history[-1]["event"] != "ORBIT":
        fail_reason = f"軌道速度未達。高度: {alt_km:.1f} km, 横速度: {vx:.0f} m/s (目標: 7,900 m/s)"

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

cb1, cb2 = st.columns([3, 1])
with cb1:
    launch_clicked = st.button("🔴 4K LIVE中継：ローンチ・シーケンス開始", use_container_width=True, type="primary")
with cb2:
    st.caption("※ 設定変更すると発射台上の3Dモデルが即座に反映されます。")

traj_data, error_msg = run_simulation(preview_only=(not launch_clicked))

rocket_visual_cfg = {
    "is_preview": bool(not launch_clicked),
    "s1_mat": s1_spec["mat_id"], "s2_mat": s2_spec["mat_id"],
    "s1_eng": int(s1_eng_count), "s2_eng": int(s2_eng_count),
    "s1_eps": float(s1_eps), "s2_eps": float(s2_eps),
    "s1_len": s1_len_scaled, "s2_len": s2_len_scaled,
    "aoa": float(angle_of_attack),
    "flame_hex": s1_spec["flame_hex"], "outer_hex": s1_spec["outer_hex"], "spark_hex": s1_spec["spark_hex"],
    "s2_flame_hex": s2_spec["flame_hex"], "s2_outer_hex": s2_spec["outer_hex"], "s2_spark_hex": s2_spec["spark_hex"],
    "fairing_shape": fair_spec["shape_id"], "wing_id": wing_spec["wing_id"],
    "strapon_type": strapon_spec["type"], "strapon_count": int(strapon_spec["count"]),
    "water_flow": float(water_flow_rate), "ignition_lead": float(ignition_lead_time),
    "sep_thrust": float(sep_thrust_factor), "spacex_return": bool(spacex_return_mode),
    "rcs_deadband": float(rcs_deadband)
}

traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
cfg_json = json.dumps(rocket_visual_cfg)
fail_msg_clean = (error_msg or "").replace('"', '\\"').replace("'", "\\'")

# =========================================================================
# 📺 HTML / JS 描画テンプレート
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
        
        .pip-container { 
            position: absolute; 
            top: 56px; 
            left: 18px; 
            right: 18px; 
            width: calc(100vw - 36px); 
            height: 295px; 
            border: 2px solid rgba(56, 189, 248, 0.95); 
            border-radius: 6px; 
            z-index: 60; 
            box-shadow: 0 14px 45px rgba(0,0,0,0.98); 
            background: #071526; 
            overflow: hidden; 
            cursor: pointer; 
            transition: height 0.25s ease;
        }
        #canvas-pip { width: 100%; height: 100%; display: block; }
        .pip-tag { position: absolute; top: 6px; left: 12px; font-size: 10px; font-weight: 800; color: #fff; background: rgba(15, 23, 42, 0.94); padding: 3px 8px; border-radius: 2px; letter-spacing: 1px; font-family: monospace; z-index: 65; pointer-events: none; border-left: 2px solid #38bdf8; }
        .pip-alt { position: absolute; bottom: 6px; right: 12px; font-size: 11px; font-family: monospace; color: #38bdf8; font-weight: 700; background: rgba(15, 23, 42, 0.94); padding: 2px 8px; border-radius: 2px; z-index: 65; pointer-events: none; }
        .pip-toggle-hint { position: absolute; top: 6px; right: 12px; font-size: 9px; font-family: monospace; color: #94a3b8; background: rgba(15, 23, 42, 0.94); padding: 3px 6px; border-radius: 2px; z-index: 65; pointer-events: none; }
        
        .hud-orbit { position: absolute; bottom: 86px; left: 24px; width: 320px; background: #030712; border: 1px solid rgba(255, 255, 255, 0.16); border-radius: 4px; padding: 8px 12px; z-index: 50; color: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.85); }
        #orbit-canvas { width: 296px; height: 64px; background: #020617; border-radius: 2px; border: 1px solid rgba(255,255,255,0.08); display: block; margin-top: 4px; }
        .top-banner { position: absolute; top: 0; left: 0; width: 100%; min-height: 44px; background: #020610; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; padding: 4px 18px; z-index: 20; flex-wrap: wrap; gap: 8px; }
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
            <span id="cam-tag" style="color: #38bdf8; font-size: clamp(9px, 1.1vw, 11px); font-weight: 700; font-family: monospace;">CAM 01: CINEMATIC WIDE CHASE</span>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; font-family: monospace; font-size: clamp(9px, 1.1vw, 11px);">
            <span style="color: #94a3b8;">ATMOS: <strong id="hud-regime" style="color: #f8fafc;">TROPOSPHERE</strong></span>
            <span style="color: #94a3b8;">GN2 RCS: <strong id="hud-rcs" style="color: #38bdf8;">STANDBY</strong></span>
            <span style="color: #94a3b8;">ARM: <strong id="hud-arm" style="color: #f59e0b;">STOWED</strong></span>
            <span id="comm-status" style="color: #10b981;">LOCKED</span>
        </div>
    </div>
    <div class="hud-orbit" id="hud-orbit-box">
        <div style="font-size: 9px; font-weight: 800; color: #94a3b8; letter-spacing: 1.2px; display: flex; justify-content: space-between;">
            <span>TRAJECTORY & GROUND TRACK</span>
            <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">DOWNRANGE: 0.0 km</span>
        </div>
        <canvas id="orbit-canvas" width="296" height="64"></canvas>
        <div id="event-log" style="margin-top: 4px; font-family: monospace; font-size: 9px; font-weight: 800; color: #34d399; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
            > [LD] GO FOR TERMINAL COUNTDOWN
        </div>
        <div id="sub-callout" style="font-family: monospace; font-size: 8.5px; color: #93c5fd; margin-top: 1px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
            > Pad systems pressurized and ready
        </div>
    </div>
    <div id="complete-banner" class="complete-banner">
        <div style="color: #6ee7b7; font-size: 18px; font-weight: 900; letter-spacing: 2px; font-family: monospace;">🎉 MISSION COMPLETE 🎉</div>
        <div id="complete-desc" style="color: #ecfdf5; font-size: 13px; font-weight: 700; margin-top: 6px;">FIRST COSMIC VELOCITY (28,400 km/h) ACHIEVED</div>
        <div id="complete-sub" style="color: #a7f3d0; font-size: 11px; margin-top: 4px; font-family: monospace;">Vehicle safely established in circular orbit.</div>
    </div>
    <div id="rud-banner" class="rud-banner">
        <div style="color: #fff; font-size: 16px; font-weight: 900; letter-spacing: 2px; font-family: monospace;">🚨 RAPID UNSCHEDULED DISASSEMBLY (RUD) 🚨</div>
        <div id="rud-desc" style="color: #fecaca; font-size: 12px; margin-top: 4px;"></div>
    </div>
    <div class="hud-telemetry">
        <div>
            <div id="tv-status" style="color: #38bdf8; font-size: 9px; font-weight: 700;">COUNTDOWN SEQUENCE</div>
            <div id="tv-timer" style="color: #fff; font-size: clamp(20px, 2.6vw, 26px); font-weight: 900; font-family: 'Consolas', monospace;">T- 00:10.0</div>
        </div>
        <div class="telemetry-row">
            <div class="telemetry-item"><div class="telemetry-label">HORIZ VELOCITY</div><div class="telemetry-val"><span id="tv-mach">M 0.00</span> <span style="font-size: 10px; color: #94a3b8;" id="tv-spd">(0 km/h)</span></div></div>
            <div class="telemetry-item"><div class="telemetry-label">ALTITUDE</div><div class="telemetry-val"><span id="tv-alt">0.0</span> <span style="font-size: 10px; color: #94a3b8;">km</span></div></div>
            <div class="telemetry-item"><div class="telemetry-label">DYNAMIC PRESSURE</div><div class="telemetry-val"><span id="tv-q">0.0</span> <span style="font-size: 10px; color: #94a3b8;">kPa</span></div></div>
            <div class="telemetry-item"><div class="telemetry-label">AXIAL LOAD</div><div class="telemetry-val"><span id="tv-g">1.0</span> <span style="font-size: 10px; color: #94a3b8;">G</span></div></div>
            <div class="telemetry-item"><div class="telemetry-label">STAGE CONFIG</div><div id="tv-stage-badge" style="color: #34d399; font-size: clamp(11px, 1.4vw, 13px); font-weight: 800; font-family: 'Consolas', monospace;">PAD READY</div></div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    window.addEventListener('DOMContentLoaded', () => {
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

            let isMissionEnded = false, catchPopPlayed = false, pipVisible = true;
            let landingSonicBoomPlayed = false;
            const pipBox = document.getElementById('pip-box');

            function resizePipRenderer() {
                if (pipBox && pipVisible) {
                    const w = pipBox.clientWidth || window.innerWidth - 36;
                    const h = pipBox.clientHeight || 295;
                    rendererPip.setSize(w, h);
                    cameraPip.aspect = w / h;
                    cameraPip.updateProjectionMatrix();
                }
            }
            window.addEventListener('resize', resizePipRenderer);

            pipBox.addEventListener('click', () => {
                pipVisible = !pipVisible;
                canvasPip.style.display = pipVisible ? 'block' : 'none';
                document.getElementById('pip-tag').style.display = pipVisible ? 'block' : 'none';
                document.getElementById('pip-hud-alt').style.display = pipVisible ? 'block' : 'none';
                pipBox.style.height = pipVisible ? '295px' : '32px';
                document.getElementById('pip-hint').innerText = pipVisible ? '[CLICK TO HIDE]' : '[CLICK TO SHOW]';
                setTimeout(resizePipRenderer, 50);
            });

            function speakCallout(text) {
                if (!window.speechSynthesis) return;
                try {
                    window.speechSynthesis.cancel();
                    const u = new SpeechSynthesisUtterance(text);
                    u.rate = 1.15; u.pitch = 0.95; u.lang = 'en-US';
                    window.speechSynthesis.speak(u);
                } catch(e) {}
            }

            const calloutMilestones = [
                { t: -10.0, main: "> [LD] TERMINAL COUNTDOWN INITIATED", sub: "> Pad systems armed for flight", spoken: "Terminal countdown initiated" },
                { t: -simCfg.ignition_lead, main: "> [PROP] MAIN ENGINE IGNITION SEQUENCE START", sub: "> Deluge system at full pressure", spoken: "Ignition sequence start" },
                { t: 0.0, main: "> [LIFTOFF] VEHICLE HAS CLEARED THE LAUNCH PAD", sub: "> Guidance active downrange", spoken: "Liftoff. Tower cleared" },
                { t: 45.0, main: "> [AERO] VEHICLE PASSING MACH 1 - SUPERSONIC", sub: "> Transonic buffet optimal", spoken: "Vehicle is supersonic" },
                { t: 65.0, main: "> [AERO] MAXIMUM DYNAMIC PRESSURE (MAX-Q)", sub: "> Main engine throttle bucket confirmed", spoken: "Max-Q" },
                { t: 130.0, main: "> [PROP] BOOSTER MECO & SEPARATION", sub: "> Separation pyros fired", spoken: "Booster separation" },
                { t: 165.0, main: "> [STAGE] SECOND STAGE VACUUM IGNITION", sub: "> Staging confirmed", spoken: "Staging confirmed" },
                { t: 230.0, main: "> [TOWER] CHOPSTICK ARMS EXTENDING FOR CATCH", sub: "> Mechazilla ready for capture", spoken: "Chopstick arms deployed" }
            ];

            let calloutTrackIndex = 0;
            function updateFlightCallouts(simT) {
                while (calloutTrackIndex < calloutMilestones.length && simT >= calloutMilestones[calloutTrackIndex].t) {
                    const m = calloutMilestones[calloutTrackIndex];
                    if (eventLog) eventLog.innerText = m.main;
                    if (subCallout) subCallout.innerText = m.sub;
                    speakCallout(m.spoken);
                    calloutTrackIndex++;
                }
            }

            // =========================================================================
            // 🔊 音響合成システム
            // =========================================================================
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            let actx = null, subRumble = null, shockCrackle = null, gasHiss = null, boosterRumble = null, boosterCrackle = null;

            function ensureAudioActive() {
                if (!actx) {
                    actx = new AudioCtx();
                    const buf = actx.createBuffer(1, actx.sampleRate * 4, actx.sampleRate);
                    const d = buf.getChannelData(0);
                    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

                    const rSrc = actx.createBufferSource(); rSrc.buffer = buf; rSrc.loop = true;
                    const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 42; lp.Q.value = 5.0;
                    subRumble = actx.createGain(); subRumble.gain.value = 0.0001;
                    rSrc.connect(lp); lp.connect(subRumble); subRumble.connect(actx.destination);
                    rSrc.start(0);

                    const cSrc = actx.createBufferSource(); cSrc.buffer = buf; cSrc.loop = true;
                    const waveShaper = actx.createWaveShaper();
                    const curve = new Float32Array(256);
                    for (let i = 0; i < 256; i++) {
                        const x = (i * 2) / 256 - 1;
                        curve[i] = Math.sign(x) * Math.pow(Math.abs(x), 0.28);
                    }
                    waveShaper.curve = curve;
                    const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 280; bp.Q.value = 3.2;
                    shockCrackle = actx.createGain(); shockCrackle.gain.value = 0.0001;
                    cSrc.connect(bp); bp.connect(waveShaper); waveShaper.connect(shockCrackle); shockCrackle.connect(actx.destination);
                    cSrc.start(0);

                    const hSrc = actx.createBufferSource(); hSrc.buffer = buf; hSrc.loop = true;
                    const hp = actx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 2400;
                    gasHiss = actx.createGain(); gasHiss.gain.value = 0.0001;
                    hSrc.connect(hp); hSrc.connect(gasHiss); gasHiss.connect(actx.destination);
                    hSrc.start(0);

                    const bSrc = actx.createBufferSource(); bSrc.buffer = buf; bSrc.loop = true;
                    const bLp = actx.createBiquadFilter(); bLp.type = 'lowpass'; bLp.frequency.value = 58; bLp.Q.value = 4.8;
                    boosterRumble = actx.createGain(); boosterRumble.gain.value = 0.0001;
                    bSrc.connect(bLp); bLp.connect(boosterRumble); boosterRumble.connect(actx.destination);
                    bSrc.start(0);

                    const bcSrc = actx.createBufferSource(); bcSrc.buffer = buf; bcSrc.loop = true;
                    const bBp = actx.createBiquadFilter(); bBp.type = 'bandpass'; bBp.frequency.value = 340; bBp.Q.value = 2.5;
                    boosterCrackle = actx.createGain(); boosterCrackle.gain.value = 0.0001;
                    bcSrc.connect(bBp); bBp.connect(waveShaper); waveShaper.connect(boosterCrackle); boosterCrackle.connect(actx.destination);
                    bcSrc.start(0);
                }
                if (actx && actx.state === 'suspended') actx.resume();
            }
            ['click', 'touchstart', 'mousedown', 'keydown'].forEach(evt => window.addEventListener(evt, ensureAudioActive));

            function playLandingIgnitionBoom() {
                ensureAudioActive();
                if (!actx) return;
                const now = actx.currentTime;
                const boomOsc = actx.createOscillator();
                const boomGain = actx.createGain();
                boomOsc.type = 'triangle';
                boomOsc.frequency.setValueAtTime(140, now);
                boomOsc.frequency.exponentialRampToValueAtTime(22, now + 0.6);
                boomGain.gain.setValueAtTime(4.5, now);
                boomGain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
                boomOsc.connect(boomGain); boomGain.connect(actx.destination);
                boomOsc.start(now); boomOsc.stop(now + 0.72);

                const noiseBuf = actx.createBuffer(1, Math.floor(actx.sampleRate * 0.4), actx.sampleRate);
                const nd = noiseBuf.getChannelData(0);
                for(let i=0; i<nd.length; i++) nd[i] = (Math.random() * 2 - 1) * Math.exp(-i / (actx.sampleRate * 0.08));
                const nSrc = actx.createBufferSource(); nSrc.buffer = noiseBuf;
                const nFilt = actx.createBiquadFilter(); nFilt.type = 'lowpass'; nFilt.frequency.value = 450;
                const nGain = actx.createGain(); nGain.gain.setValueAtTime(3.8, now);
                nGain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
                nSrc.connect(nFilt); nFilt.connect(nGain); nGain.connect(actx.destination);
                nSrc.start(now);
            }

            function playHeavySeparationSound() {
                ensureAudioActive();
                if (!actx) return;
                const now = actx.currentTime;
                const impBuf = actx.createBuffer(1, Math.floor(actx.sampleRate * 0.08), actx.sampleRate);
                const idata = impBuf.getChannelData(0);
                for (let i = 0; i < idata.length; i++) idata[i] = (Math.random() * 2 - 1) * Math.exp(-i / (actx.sampleRate * 0.007));
                const impSrc = actx.createBufferSource(); impSrc.buffer = impBuf;
                const impF = actx.createBiquadFilter(); impF.type = 'lowpass'; impF.frequency.setValueAtTime(850, now);
                const impG = actx.createGain(); impG.gain.setValueAtTime(4.2, now);
                impSrc.connect(impF); impF.connect(impG); impG.connect(actx.destination);
                impSrc.start(now);

                const osc = actx.createOscillator(); const oscG = actx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(95, now); osc.frequency.exponentialRampToValueAtTime(22, now + 0.38);
                oscG.gain.setValueAtTime(3.8, now); oscG.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
                osc.connect(oscG); oscG.connect(actx.destination);
                osc.start(now); osc.stop(now + 0.46);

                const pBuf = actx.createBuffer(1, Math.floor(actx.sampleRate * 0.6), actx.sampleRate);
                const pdata = pBuf.getChannelData(0);
                for (let i = 0; i < pdata.length; i++) pdata[i] = (Math.random() * 2 - 1) * Math.sin(i / pdata.length * Math.PI) * Math.exp(-i / (actx.sampleRate * 0.2));
                const pSrc = actx.createBufferSource(); pSrc.buffer = pBuf;
                const pF = actx.createBiquadFilter(); pF.type = 'bandpass'; pF.frequency.setValueAtTime(1400, now); pF.Q.value = 1.2;
                const pG = actx.createGain(); pG.gain.setValueAtTime(1.8, now);
                pSrc.connect(pF); pF.connect(pG); pG.connect(actx.destination);
                pSrc.start(now + 0.015);
            }

            function playRcsPuffSound() {
                if (!actx) return;
                const now = actx.currentTime, dur = 0.07;
                const buf = actx.createBuffer(1, Math.floor(actx.sampleRate * dur), actx.sampleRate);
                const data = buf.getChannelData(0);
                for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (actx.sampleRate * 0.02));
                const src = actx.createBufferSource(); src.buffer = buf;
                const hp = actx.createBiquadFilter(); hp.type = 'bandpass'; hp.frequency.setValueAtTime(3400, now); hp.Q.value = 1.4;
                const g = actx.createGain(); g.gain.setValueAtTime(0.16, now); g.gain.exponentialRampToValueAtTime(0.005, now + dur);
                src.connect(hp); src.connect(g); g.connect(actx.destination);
                src.start(now);
            }

            function playFirecrackerSnapSound() {
                if (!actx) return;
                const now = actx.currentTime;
                const osc = actx.createOscillator(); const gain = actx.createGain();
                osc.type = 'square'; osc.frequency.setValueAtTime(1200, now); osc.frequency.exponentialRampToValueAtTime(80, now + 0.035);
                gain.gain.setValueAtTime(3.4, now); gain.gain.exponentialRampToValueAtTime(0.001, now + 0.055);
                osc.connect(gain); gain.connect(actx.destination);
                osc.start(now); osc.stop(now + 0.06);
            }

            // =========================================================================
            // 🌍 Three.js シーン ＆ ライティング
            // =========================================================================
            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x1a334f, 0.000045);

            const rendererMain = new THREE.WebGLRenderer({ canvas: canvasMain, antialias: true, powerPreference: "high-performance" });
            rendererMain.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
            rendererMain.setSize(window.innerWidth, window.innerHeight);
            rendererMain.toneMapping = THREE.ACESFilmicToneMapping;
            rendererMain.toneMappingExposure = 1.35;

            const rendererPip = new THREE.WebGLRenderer({ canvas: canvasPip, antialias: true });
            rendererPip.setSize(520, 295);
            rendererPip.toneMapping = THREE.ACESFilmicToneMapping;
            rendererPip.toneMappingExposure = 1.45;

            const cameraMain = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 2.0, 75000);
            const cameraPip = new THREE.PerspectiveCamera(38.0, 520 / 295, 2.0, 75000);

            const sunLight = new THREE.DirectionalLight(0xfffaed, 5.0);
            sunLight.position.set(4000, 6000, 3000); scene.add(sunLight);
            const skyAmbient = new THREE.HemisphereLight(0x90b8d8, 0x1a2636, 1.8); scene.add(skyAmbient);
            const engineBounceLight = new THREE.PointLight(simCfg.flame_hex, 0.0, 500, 2.0); scene.add(engineBounceLight);
            const pipTrackingSpot = new THREE.DirectionalLight(0xffffff, 3.5); scene.add(pipTrackingSpot);

            function createSkyGradientTexture() {
                const cvs = document.createElement('canvas'); cvs.width = 128; cvs.height = 512;
                const ctx = cvs.getContext('2d');
                const g = ctx.createLinearGradient(0, 0, 0, 512);
                g.addColorStop(0.0, '#020612');
                g.addColorStop(0.45, '#071830');
                g.addColorStop(0.82, '#1e4877');
                g.addColorStop(1.0, '#5383aa');
                ctx.fillStyle = g; ctx.fillRect(0, 0, 128, 512);
                return new THREE.CanvasTexture(cvs);
            }
            const skyDomeGeo = new THREE.SphereGeometry(45000, 24, 16);
            const skyDomeMat = new THREE.MeshBasicMaterial({ map: createSkyGradientTexture(), side: THREE.BackSide, depthWrite: false });
            const skyDome = new THREE.Mesh(skyDomeGeo, skyDomeMat); scene.add(skyDome);

            const starGeo = new THREE.BufferGeometry();
            const starPos = new Float32Array(1500 * 3);
            for(let i=0; i<4500; i+=3) {
                const rad = 42000, u = Math.random(), v = Math.random();
                const th = u * 2 * Math.PI, ph = Math.acos(2 * v - 1);
                starPos[i] = rad * Math.sin(ph) * Math.cos(th);
                starPos[i+1] = rad * Math.sin(ph) * Math.sin(th);
                starPos[i+2] = rad * Math.cos(ph);
            }
            starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
            const starMat = new THREE.PointsMaterial({ size: 3.5, color: 0xffffff, transparent: true, opacity: 0.25 });
            scene.add(new THREE.Points(starGeo, starMat));

            const landscapeGroup = new THREE.Group(); scene.add(landscapeGroup);
            const coastPlane = new THREE.Mesh(new THREE.PlaneGeometry(35000, 35000), new THREE.MeshStandardMaterial({ color: 0x162319, roughness: 0.95 }));
            coastPlane.rotation.x = -Math.PI / 2; coastPlane.position.set(-1500, -3.0, 0); landscapeGroup.add(coastPlane);

            const oceanMesh = new THREE.Mesh(new THREE.PlaneGeometry(45000, 45000), new THREE.MeshStandardMaterial({ color: 0x07223b, roughness: 0.18, metalness: 0.85 }));
            oceanMesh.rotation.x = -Math.PI / 2; oceanMesh.position.set(12000, -12.0, 0); landscapeGroup.add(oceanMesh);

            // 発射台 ＆ スイングアーム
            const pad = new THREE.Group(); scene.add(pad);
            const isSaturnPad = (simCfg.s1_mat === 'saturn' || simCfg.s1_mat === 'al');
            const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x222a36, metalness: 0.85, roughness: 0.35 });
            const concreteMat = new THREE.MeshStandardMaterial({ color: 0x3d4554, roughness: 0.95 });
            const pipeMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.35, metalness: 0.85 });

            let chopstickGroup = new THREE.Group();
            let armLeftPivot = new THREE.Group();
            let armRightPivot = new THREE.Group();

            const isStarshipPad = (simCfg.s1_mat === 'ss');
            const isSaturnOrH3 = (simCfg.s1_mat === 'saturn' || simCfg.s1_mat === 'al');
            const isMissilePad = (simCfg.s1_mat === 'military' || simCfg.s1_mat === 'cf');
            const isJokePad = (simCfg.s1_mat === 'baguette' || simCfg.s1_mat === 'pencil');

            if (isStarshipPad) {
                const groundPlate = new THREE.Mesh(new THREE.CylinderGeometry(110, 125, 3.0, 32), concreteMat);
                groundPlate.position.y = 0.5; pad.add(groundPlate);

                const olmRing = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 4.2, 2.2, 24), darkSteelMat);
                olmRing.position.y = 4.2; pad.add(olmRing);
                for(let i=0; i<6; i++) {
                    const ang = (i/6)*Math.PI*2;
                    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.52, 3.8, 12), darkSteelMat);
                    leg.position.set(Math.cos(ang)*3.4, 2.1, Math.sin(ang)*3.4);
                    pad.add(leg);
                }

                const towerGroup = new THREE.Group(); towerGroup.position.set(-11.5, 0, 0); pad.add(towerGroup);
                const towerMain = new THREE.Mesh(new THREE.BoxGeometry(6.2, 145.0, 6.2), darkSteelMat);
                towerMain.position.y = 72.5; towerGroup.add(towerMain);

                chopstickGroup.position.set(0, 67.5, 0); towerGroup.add(chopstickGroup);
                armLeftPivot.position.set(3.1, 0, 2.2); chopstickGroup.add(armLeftPivot);
                const armLeft = new THREE.Mesh(new THREE.BoxGeometry(16.0, 2.2, 1.3), darkSteelMat);
                armLeft.position.set(8.0, 0, 0); armLeftPivot.add(armLeft);

                armRightPivot.position.set(3.1, 0, -2.2); chopstickGroup.add(armRightPivot);
                const armRight = new THREE.Mesh(new THREE.BoxGeometry(16.0, 2.2, 1.3), darkSteelMat);
                armRight.position.set(8.0, 0, 0); armRightPivot.add(armRight);
                armLeftPivot.rotation.y = -0.75; armRightPivot.rotation.y = 0.75;

                for(let ti=0; ti<6; ti++) {
                    const tk = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 4.2, 18.0, 16), new THREE.MeshStandardMaterial({ color: 0xdde4ec, metalness: 0.8, roughness: 0.2 }));
                    tk.position.set(-45.0 - (ti%3)*12.0, 9.0, -25.0 - Math.floor(ti/3)*14.0);
                    pad.add(tk);
                }
            } else if (isSaturnOrH3) {
                const groundPlate = new THREE.Mesh(new THREE.BoxGeometry(70, 8.0, 70), concreteMat);
                groundPlate.position.y = 0.5; pad.add(groundPlate);
                const towerGroup = new THREE.Group(); towerGroup.position.set(-12.5, 0, 0); pad.add(towerGroup);
                const redTower = new THREE.Mesh(new THREE.BoxGeometry(7.0, 155.0, 7.0), new THREE.MeshStandardMaterial({ color: 0xb91c1c, metalness: 0.5, roughness: 0.4 }));
                redTower.position.y = 77.5; towerGroup.add(redTower);
            } else if (isMissilePad) {
                const siloGround = new THREE.Mesh(new THREE.CylinderGeometry(35, 40, 2.5, 16), new THREE.MeshStandardMaterial({ color: 0x272e25, roughness: 0.9 }));
                siloGround.position.y = -0.5; pad.add(siloGround);
                const hatchDoor = new THREE.Mesh(new THREE.BoxGeometry(7.5, 1.2, 7.5), new THREE.MeshStandardMaterial({ color: 0x3f4f38, metalness: 0.6, roughness: 0.4 }));
                hatchDoor.position.set(-5.5, 2.5, 0); hatchDoor.rotation.z = 0.95; pad.add(hatchDoor);
            } else if (isJokePad) {
                const boardColor = (simCfg.s1_mat === 'baguette') ? 0x9a3412 : 0x0284c7;
                const jokePlate = new THREE.Mesh(new THREE.BoxGeometry(32, 4.0, 32), new THREE.MeshStandardMaterial({ color: boardColor, roughness: 0.7 }));
                jokePlate.position.y = 0.5; pad.add(jokePlate);
            }

            // ロケット構造構築
            function getRealisticMaterial(matId) {
                let col = 0xd5dce6, m = 0.92, r = 0.16;
                if (matId === 'al') { col = 0xc2410c; m = 0.15; r = 0.65; }
                else if (matId === 'saturn') { col = 0xf8fafc; m = 0.25; r = 0.35; }
                else if (matId === 'cf') { col = 0x111317; m = 0.08; r = 0.78; }
                else if (matId === 'military') { col = 0x3f4f38; m = 0.30; r = 0.60; }
                else if (matId === 'baguette') { col = 0xc68a4c; m = 0.02; r = 0.88; }
                else if (matId === 'pencil') { col = 0x155e3b; m = 0.10; r = 0.70; }
                else if (matId === 'inconel') { col = 0x3f3f46; m = 0.85; r = 0.32; }
                return new THREE.MeshStandardMaterial({ color: col, metalness: m, roughness: r });
            }

            const blackTileMat = new THREE.MeshStandardMaterial({ color: 0x111317, roughness: 0.85, metalness: 0.1 });

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

            const rocket = new THREE.Group(); rocket.position.y = 6.0; scene.add(rocket);
            const s1Group = new THREE.Group(); scene.add(s1Group);
            const s1Len = simCfg.s1_len, s2Len = simCfg.s2_len;
            const s1Mat = getRealisticMaterial(simCfg.s1_mat), s2Mat = getRealisticMaterial(simCfg.s2_mat);

            const isPencilRocket = (simCfg.s1_mat === 'pencil');
            const s1Segments = isPencilRocket ? 6 : 32;
            const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, s1Segments), s1Mat);
            s1Body.position.y = s1Len / 2; s1Group.add(s1Body);

            if (!isPencilRocket && simCfg.s1_mat !== 'baguette') {
                const feedPipe = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.065, s1Len * 0.92, 12), pipeMat);
                feedPipe.position.set(1.14, s1Len * 0.48, 0); s1Group.add(feedPipe);
                const feedPipe2 = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, s1Len * 0.85, 12), pipeMat);
                feedPipe2.position.set(-1.14, s1Len * 0.45, 0); s1Group.add(feedPipe2);

                for(let ry = 2.5; ry < s1Len; ry += 3.8) {
                    const ring = new THREE.Mesh(new THREE.TorusGeometry(1.125, 0.015, 6, 24), darkSteelMat);
                    ring.rotation.x = Math.PI / 2; ring.position.y = ry; s1Group.add(ring);
                }
            }

            const catchPins = new THREE.Mesh(
                new THREE.CylinderGeometry(0.26, 0.26, 3.8, 16),
                new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.9, roughness: 0.25 })
            );
            catchPins.rotation.x = Math.PI / 2;
            catchPins.position.set(0, s1Len - 2.2, 0);
            s1Group.add(catchPins);

            const s1NozzleTips = [], s2NozzleTips = [], boosterNozzleTips = [];
            const inconelNozzleMat = new THREE.MeshStandardMaterial({ color: 0x222730, metalness: 0.95, roughness: 0.25, side: THREE.DoubleSide });

            function buildFullDetailedEngineCluster(parent, count, basePosY, epsScale, tipArray, jetLen, flameHex) {
                const group = new THREE.Group(); group.position.y = basePosY;
                const bellH = 1.2 * epsScale, bellW = 0.22 * Math.pow(epsScale, 0.65);

                const nozzleGeo = new THREE.CylinderGeometry(0.1, bellW * 2.0, bellH, 12, 1, true);
                nozzleGeo.translate(0, -bellH / 2, 0);

                const flameMat = new THREE.MeshBasicMaterial({
                    map: sharedFlameTex, color: flameHex, transparent: true, opacity: 0.95,
                    blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide
                });
                const flameGeo = new THREE.ConeGeometry(bellW * 3.2, jetLen, 8, 1, true);
                flameGeo.translate(0, -jetLen / 2, 0);

                const enginePositions = [];
                if (count === 33) {
                    for(let i=0; i<3; i++) enginePositions.push({ x: Math.cos(i/3*Math.PI*2)*0.24, z: Math.sin(i/3*Math.PI*2)*0.24, isCenter: true });
                    for(let i=0; i<10; i++) enginePositions.push({ x: Math.cos(i/10*Math.PI*2)*0.58, z: Math.sin(i/10*Math.PI*2)*0.58, isCenter: false });
                    for(let i=0; i<20; i++) enginePositions.push({ x: Math.cos(i/20*Math.PI*2)*0.94, z: Math.sin(i/20*Math.PI*2)*0.94, isCenter: false });
                } else if (count === 1) {
                    enginePositions.push({ x: 0, z: 0, isCenter: true });
                } else {
                    for(let i=0; i<count; i++) enginePositions.push({ x: Math.cos(i/count*Math.PI*2)*0.75, z: Math.sin(i/count*Math.PI*2)*0.75, isCenter: (i < 3) });
                }

                for(let pos of enginePositions) {
                    const engUnit = new THREE.Group(); engUnit.position.set(pos.x, 0, pos.z);
                    engUnit.add(new THREE.Mesh(nozzleGeo, inconelNozzleMat));
                    const tipObj = new THREE.Object3D(); tipObj.position.set(0, -bellH, 0);
                    const flameMesh = new THREE.Mesh(flameGeo, flameMat);
                    tipObj.add(flameMesh); engUnit.add(tipObj);
                    tipArray.push({ node: tipObj, plume: flameMesh, isCenter: pos.isCenter });
                    group.add(engUnit);
                }
                parent.add(group);
            }

            const s1EpsScale = 0.75 + (simCfg.s1_eps / 70.0) * 0.75;
            buildFullDetailedEngineCluster(s1Group, simCfg.s1_eng, 0.0, s1EpsScale, s1NozzleTips, 28.0, simCfg.flame_hex);

            const wingsGroup = new THREE.Group(); s1Group.add(wingsGroup);
            const aoaRad = (simCfg.aoa * Math.PI) / 180.0;
            if (simCfg.wing_id === 'grid') {
                for(let i=0; i<4; i++) {
                    const ang = (i / 4) * Math.PI * 2 + Math.PI / 4;
                    const gfFrame = new THREE.Group();
                    gfFrame.position.set(Math.cos(ang)*1.22, s1Len - 1.1, Math.sin(ang)*1.22);
                    gfFrame.rotation.y = -ang; gfFrame.rotation.z = aoaRad;
                    const gridBox = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.14, 1.25), darkSteelMat);
                    gridBox.position.x = 0.62; gfFrame.add(gridBox); wingsGroup.add(gfFrame);
                }
            } else if (simCfg.wing_id === 'starship_flap') {
                for(let side of [-1, 1]) {
                    const flap = new THREE.Mesh(new THREE.BoxGeometry(1.6, 4.2, 0.12), darkSteelMat);
                    flap.position.set(side * 1.7, 2.8, 0); flap.rotation.z = side * 0.15; flap.rotation.x = aoaRad;
                    wingsGroup.add(flap);
                }
            } else if (simCfg.wing_id === 'missile_fin') {
                for(let i=0; i<4; i++) {
                    const ang = (i / 4) * Math.PI * 2;
                    const fin = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.4, 0.08), darkSteelMat);
                    fin.position.set(Math.cos(ang)*1.4, 1.6, Math.sin(ang)*1.4);
                    fin.rotation.y = -ang; wingsGroup.add(fin);
                }
            } else if (simCfg.wing_id === 'delta_wing') {
                for(let side of [-1, 1]) {
                    const s = new THREE.Shape(); s.moveTo(0,0); s.lineTo(side*4.8, -1.8); s.lineTo(side*4.2, -6.5); s.lineTo(0, -5.2);
                    const dm = new THREE.Mesh(new THREE.ShapeGeometry(s), s1Mat);
                    dm.position.set(0, s1Len * 0.45, 0); wingsGroup.add(dm);
                }
            }

            const boosterUnits = [];
            if (simCfg.strapon_count > 0 && simCfg.strapon_type !== 'none') {
                const isSRB = (simCfg.strapon_type === 'srb'), isSoyuz = (simCfg.strapon_type === 'soyuz');
                const bMat = isSRB ? new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4 }) : s1Mat;
                for(let i=0; i<simCfg.strapon_count; i++) {
                    const ang = (i / simCfg.strapon_count) * Math.PI * 2;
                    const distR = isSoyuz ? 2.3 : 2.15;
                    const bUnit = new THREE.Group(); bUnit.position.set(Math.cos(ang)*distR, 0, Math.sin(ang)*distR);
                    const bLen = s1Len * (isSoyuz ? 0.75 : 0.84);
                    const topR = isSoyuz ? 0.42 : 0.68, botR = isSoyuz ? 0.78 : 0.68;
                    const bBody = new THREE.Mesh(new THREE.CylinderGeometry(topR, botR, bLen, 24), bMat);
                    bBody.position.y = bLen / 2; bUnit.add(bBody);
                    const bNose = new THREE.Mesh(new THREE.ConeGeometry(topR, 2.2, 24), bMat);
                    bNose.position.y = bLen + 1.1; bUnit.add(bNose);

                    const localTips = [];
                    buildFullDetailedEngineCluster(bUnit, 1, 0, 1.0, localTips, 24.0, simCfg.flame_hex);
                    localTips.forEach(t => boosterNozzleTips.push(t));
                    s1Group.add(bUnit);
                    boosterUnits.push({ mesh: bUnit, angle: ang, detached: false, vx: 0, vy: 0, vz: 0, rx: 0, rz: 0, tips: localTips });
                }
            }

            const interStage = new THREE.Group(); interStage.position.y = s1Len; s1Group.add(interStage);
            const interTruss = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, 2.2, 24, 4, true), darkSteelMat);
            interTruss.position.y = 1.1; interStage.add(interTruss);

            const s2Group = new THREE.Group(); s2Group.position.y = s1Len + 2.2; rocket.add(s2Group);
            const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, s1Segments), s2Mat);
            s2Body.position.y = s2Len / 2; s2Group.add(s2Body);

            if (simCfg.s2_mat === 'ss') {
                const heatShield = new THREE.Mesh(new THREE.CylinderGeometry(1.128, 1.128, s2Len, 24, 1, true, 0, Math.PI), blackTileMat);
                heatShield.position.y = s2Len / 2; s2Group.add(heatShield);
            }

            const s2EpsScale = 1.0 + (simCfg.s2_eps / 280.0) * 1.1;
            buildFullDetailedEngineCluster(s2Group, simCfg.s2_eng, 0.0, s2EpsScale, s2NozzleTips, 32.0, simCfg.s2_flame_hex);
            s2NozzleTips.forEach(t => t.plume.visible = false);

            const payloadGroup = new THREE.Group(); payloadGroup.position.y = s2Len + 1.8; s2Group.add(payloadGroup);
            const satBus = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 2.4, 16), new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.95, roughness: 0.2 }));
            payloadGroup.add(satBus);

            const fairingHalves = [];
            if (simCfg.fairing_shape === 'abort_tower') {
                const cap = new THREE.Mesh(new THREE.ConeGeometry(1.14, 2.8, 24), s2Mat); cap.position.y = s2Len + 1.4; s2Group.add(cap);
                const spike = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.14, 3.8, 12), darkSteelMat); spike.position.y = s2Len + 4.2; s2Group.add(spike);
            } else if (simCfg.fairing_shape === 'pencil_tip') {
                const wood = new THREE.Mesh(new THREE.ConeGeometry(1.12, 3.8, 6), new THREE.MeshStandardMaterial({ color: 0xd4a373, roughness: 0.9 }));
                wood.position.y = s2Len + 1.9; s2Group.add(wood);
                const lead = new THREE.Mesh(new THREE.ConeGeometry(0.24, 1.0, 6), new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.4 }));
                lead.position.y = s2Len + 3.8; s2Group.add(lead);
            } else {
                const ogivePts = [];
                const noseH = (simCfg.fairing_shape === 'icbm_warhead') ? 3.8 : 5.8;
                for(let i=0; i<=16; i++) {
                    const t = i / 16;
                    ogivePts.push(new THREE.Vector2(Math.max(0.01, 1.12 * Math.pow(1.0 - Math.pow(t, 1.65), 0.72)), t * noseH));
                }
                for(let side of [-1, 1]) {
                    const halfMesh = new THREE.Mesh(new THREE.LatheGeometry(ogivePts, 16, (side === 1) ? 0 : Math.PI, Math.PI), s2Mat);
                    halfMesh.position.y = s2Len; s2Group.add(halfMesh);

                    if (simCfg.fairing_shape === 'starship_crew' && side === 1) {
                        const blackHalf = new THREE.Mesh(new THREE.LatheGeometry(ogivePts, 16, 0, Math.PI), blackTileMat);
                        blackHalf.scale.set(1.006, 1.0, 1.006); blackHalf.position.y = s2Len; s2Group.add(blackHalf);
                    }
                    fairingHalves.push({ mesh: halfMesh, side: side, detached: false, vx: 0, vy: 0, rotZ: 0 });
                }
            }

            // 8方向ローカル全方位パルスRCSスラスター
            const rcsNozzles = [];
            const rcs8Dirs = [
                { id: "+X", dx:  1, dy: 0, dz:  0 },
                { id: "-X", dx: -1, dy: 0, dz:  0 },
                { id: "+Z", dx:  0, dy: 0, dz:  1 },
                { id: "-Z", dx:  0, dy: 0, dz: -1 },
                { id: "+X+Z", dx:  0.707, dy: 0, dz:  0.707 },
                { id: "-X+Z", dx: -0.707, dy: 0, dz:  0.707 },
                { id: "+X-Z", dx:  0.707, dy: 0, dz: -0.707 },
                { id: "-X-Z", dx: -0.707, dy: 0, dz: -0.707 }
            ];

            function addFullRcsCluster(parent, yPos, isS1) {
                for(let d of rcs8Dirs) {
                    const mount = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.28, 0.18), darkSteelMat);
                    mount.position.set(d.dx * 1.15, yPos, d.dz * 1.15);
                    parent.add(mount);
                    rcsNozzles.push({ mount: mount, dir: d, isS1: isS1, intensity: 0.0 });
                }
            }
            addFullRcsCluster(s1Group, s1Len - 0.8, true);
            addFullRcsCluster(s2Group, s2Len - 0.7, false);

            // パーティクルプール ＆ 雲海
            function createCloudTex() {
                const c = document.createElement('canvas'); c.width = 128; c.height = 128;
                const g = c.getContext('2d').createRadialGradient(64,64,4, 64,64,64);
                g.addColorStop(0, 'rgba(255,255,255,0.95)'); g.addColorStop(0.35, 'rgba(240,248,255,0.7)');
                g.addColorStop(0.75, 'rgba(200,215,230,0.3)'); g.addColorStop(1, 'rgba(180,200,220,0)');
                c.getContext('2d').fillStyle = g; c.getContext('2d').fillRect(0,0,128,128);
                return new THREE.CanvasTexture(c);
            }
            function createSparkTex() {
                const c = document.createElement('canvas'); c.width = 32; c.height = 32;
                const g = c.getContext('2d').createRadialGradient(16,16,1, 16,16,15);
                g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.4, 'rgba(255,220,120,0.95)');
                g.addColorStop(1, 'rgba(255,40,0,0)');
                c.getContext('2d').fillStyle = g; c.getContext('2d').fillRect(0,0,32,32);
                return new THREE.CanvasTexture(c);
            }
            const cloudTex = createCloudTex(), sparkTex = createSparkTex();

            const cloudDeck = new THREE.Group(); scene.add(cloudDeck);
            for(let ci=0; ci<75; ci++) {
                const cMat = new THREE.SpriteMaterial({ map: cloudTex, transparent: true, opacity: 0.52, depthWrite: false });
                const csp = new THREE.Sprite(cMat);
                const cx = (Math.random() - 0.5) * 3600.0, cz = (Math.random() - 0.5) * 3600.0;
                const cy = 125.0 + (Math.random() - 0.5) * 30.0;
                csp.position.set(cx, cy, cz);
                const csc = 85.0 + Math.random() * 110.0;
                csp.scale.set(csc * 1.5, csc, 1);
                cloudDeck.add(csp);
            }

            const pool = [];
            for(let i=0; i<600; i++) {
                const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: cloudTex, transparent: true, opacity: 0, depthWrite: false }));
                sp.visible = false; scene.add(sp);
                pool.push({ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 5, o: 0.8 });
            }
            let pIdx = 0;
            function emitParticle(x, y, z, vx, vy, vz, s0, s1, life, opacity, hexColor=0xf1f5f9) {
                const p = pool[pIdx]; pIdx = (pIdx + 1) % pool.length;
                p.active = true; p.sp.visible = true;
                p.sp.position.set(x, Math.max(3.5, y), z);
                p.vx = vx; p.vy = vy; p.vz = vz;
                p.age = 0; p.maxAge = life; p.s0 = s0; p.s1 = s1; p.o = opacity;
                p.sp.material.color.setHex(hexColor);
            }

            const sparks = [];
            for(let i=0; i<150; i++) {
                const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: sparkTex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
                sp.visible = false; scene.add(sp);
                sparks.push({ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1 });
            }
            let sIdx = 0;
            function emitSpark(x, y, z, vx, vy, vz, hexCol) {
                const s = sparks[sIdx]; sIdx = (sIdx + 1) % sparks.length;
                s.active = true; s.sp.visible = true;
                s.sp.position.set(x, Math.max(3.5, y), z);
                s.vx = vx; s.vy = vy; s.vz = vz;
                s.age = 0; s.maxAge = 14;
                s.sp.material.color.setHex(hexCol);
            }

            function drawPrecisionOrbitMap(curAltKm, curDRangeKm, exploded, isOrbit) {
                if (!orbitCvs || !octx) return;
                octx.fillStyle = '#020617'; octx.fillRect(0, 0, 296, 64);
                octx.strokeStyle = '#1e293b'; octx.lineWidth = 1.5;
                octx.beginPath(); octx.moveTo(10, 52); octx.lineTo(286, 52); octx.stroke();

                const curPx = 20 + Math.min(256, Math.max(0, (curDRangeKm / 1400.0) * 256));
                const curPy = 52 - Math.min(46, Math.max(0, (curAltKm / 250.0) * 42));
                octx.beginPath(); octx.moveTo(20, 52);
                octx.quadraticCurveTo(20 + (curPx - 20) * 0.35, 52, curPx, curPy);
                octx.strokeStyle = exploded ? '#ef4444' : (isOrbit ? '#34d399' : '#38bdf8');
                octx.lineWidth = 2.0; octx.stroke();

                octx.fillStyle = exploded ? '#dc2626' : (isOrbit ? '#10b981' : '#38bdf8');
                octx.beginPath(); octx.arc(curPx, curPy, 3.5, 0, Math.PI * 2); octx.fill();
            }

            // =========================================================================
            // ⏱️ アニメーション・メインループ
            // =========================================================================
            const tStart = performance.now();
            let boosterDetached = false, stage1Detached = false, fairingDetached = false, camShake = 0.0;
            let prevRcsCmd = 0.0;
            const tempV = new THREE.Vector3();
            const activeFocusWorld = new THREE.Vector3();

            function animate(now) {
                if (isMissionEnded) return;
                requestAnimationFrame(animate);

                const elapsedSec = (now - tStart) / 1000.0;
                const simT = simCfg.is_preview ? -10.0 : (-10.0 + elapsedSec);

                if (!simCfg.is_preview) updateFlightCallouts(simT);

                let idx = 0;
                while (idx < simData.length - 1 && simData[idx + 1].t <= simT) idx++;
                const nIdx = Math.min(idx + 1, simData.length - 1);
                const p0 = simData[idx], p1 = simData[nIdx];
                const a = (p1.t > p0.t) ? Math.max(0, Math.min(1, (simT - p0.t) / (p1.t - p0.t))) : 0;

                const rx = (p0.x + (p1.x - p0.x) * a) * 0.1;
                const ry = (p0.y + (p1.y - p0.y) * a) * 0.1;
                const alt = p0.alt + (p1.alt - p0.alt) * a;
                const vel = p0.v + (p1.v - p0.v) * a;
                const q = p0.q + (p1.q - p0.q) * a;
                const pitch = p0.pitch + (p1.pitch - p0.pitch) * a;
                const mach = p0.mach + (p1.mach - p0.mach) * a;
                const accG = p0.g + (p1.g - p0.g) * a;
                const rcsCmd = p0.rcs_cmd + (p1.rcs_cmd - p0.rcs_cmd) * a;

                const bX = p0.b_x + (p1.b_x - p0.b_x) * a;
                const bY = p0.b_y + (p1.b_y - p0.b_y) * a;
                const bPitch = p0.b_pitch + (p1.b_pitch - p0.b_pitch) * a;

                rocket.position.set(rx, ry + 6.0, 0);
                rocket.rotation.z = -pitch;
                rocket.updateMatrixWorld(true);

                starMat.opacity = Math.min(0.95, Math.max(0.02, (alt - 15.0) / 60.0));
                skyDomeMat.color.setHex((alt > 65.0) ? 0x020815 : 0x0a1c30);

                const ux = Math.sin(pitch), uy = Math.cos(pitch);
                const perpX = Math.cos(pitch), perpY = -Math.sin(pitch);

                if (!p0.strapon && !boosterDetached && boosterUnits.length > 0 && !simCfg.is_preview) {
                    boosterDetached = true;
                    playHeavySeparationSound();
                    camShake = 0.25;
                    for(let b of boosterUnits) {
                        b.detached = true;
                        b.tips.forEach(t => t.plume.visible = false);
                        scene.attach(b.mesh);
                        const outX = Math.cos(b.angle), outZ = Math.sin(b.angle);
                        const sepP = simCfg.sep_thrust;
                        b.vx = perpX * outX * (1.2 * sepP);
                        b.vy = -2.5 * sepP;
                        b.vz = outZ * (1.2 * sepP);
                        b.rx = outZ * 0.18; b.rz = -outX * 0.18;
                    }
                }
                if (boosterDetached) {
                    for(let b of boosterUnits) {
                        b.mesh.position.x += b.vx * 0.016;
                        b.mesh.position.y += b.vy * 0.016;
                        b.mesh.position.z += b.vz * 0.016;
                        b.vy -= 1.8 * 0.016;
                        b.mesh.rotation.x += b.rx * 0.016;
                        b.mesh.rotation.z += b.rz * 0.016;
                    }
                }

                const isSeparated = (p0.stage === 2 || p0.b_active);
                if (isSeparated && !stage1Detached && !simCfg.is_preview) {
                    stage1Detached = true;
                    playHeavySeparationSound();
                    camShake = 0.65;
                    s1NozzleTips.forEach(t => t.plume.visible = false);
                    s2NozzleTips.forEach(t => t.plume.visible = true);
                    for(let i=0; i<36; i++) {
                        const ang = (i / 36) * Math.PI * 2;
                        emitParticle(
                            rx + Math.cos(ang) * 1.6, ry + 6.0 + s1Len, Math.sin(ang) * 1.6,
                            Math.cos(ang) * 16.0, -4.0, Math.sin(ang) * 16.0,
                            2.5, 18.0, 45, 0.92
                        );
                    }
                }

                const bY_scaled = (bY * 0.1) + 6.0;
                if (simCfg.spacex_return && isStarshipPad) {
                    if (p0.b_caught) {
                        armLeftPivot.rotation.y = THREE.MathUtils.lerp(armLeftPivot.rotation.y, 0.08, 0.25);
                        armRightPivot.rotation.y = THREE.MathUtils.lerp(armRightPivot.rotation.y, -0.08, 0.25);
                        document.getElementById('hud-arm').innerText = "CATCH LOCKED (PIN SECURED)";
                        document.getElementById('hud-arm').style.color = "#10b981";
                    } else if (stage1Detached && bY <= 1500) {
                        armLeftPivot.rotation.y = THREE.MathUtils.lerp(armLeftPivot.rotation.y, 0.05, 0.12);
                        armRightPivot.rotation.y = THREE.MathUtils.lerp(armRightPivot.rotation.y, -0.05, 0.12);
                        document.getElementById('hud-arm').innerText = "CLOSING ARMS";
                        document.getElementById('hud-arm').style.color = "#38bdf8";
                    } else if (stage1Detached && bY <= 4500) {
                        armLeftPivot.rotation.y = THREE.MathUtils.lerp(armLeftPivot.rotation.y, -0.16, 0.08);
                        armRightPivot.rotation.y = THREE.MathUtils.lerp(armRightPivot.rotation.y, 0.16, 0.08);
                        document.getElementById('hud-arm').innerText = "DEPLOYED (WIDE READY)";
                        document.getElementById('hud-arm').style.color = "#34d399";
                    } else {
                        armLeftPivot.rotation.y = THREE.MathUtils.lerp(armLeftPivot.rotation.y, -0.75, 0.05);
                        armRightPivot.rotation.y = THREE.MathUtils.lerp(armRightPivot.rotation.y, 0.75, 0.05);
                        document.getElementById('hud-arm').innerText = "STOWED CLEAR";
                        document.getElementById('hud-arm').style.color = "#f59e0b";
                    }
                }

                if (stage1Detached) {
                    s1Group.visible = true;
                    s1Group.position.set(bX * 0.1, bY_scaled, 0);
                    s1Group.rotation.set(0, 0, -bPitch);
                    s1Group.updateMatrixWorld(true);

                    if (p0.b_thrust && !landingSonicBoomPlayed && bY <= 3600) {
                        playLandingIgnitionBoom();
                        landingSonicBoomPlayed = true;
                        camShake = 0.55;
                    }

                    if (actx && boosterRumble && boosterCrackle) {
                        if (p0.b_thrust && !p0.b_caught && bY <= 3600) {
                            const is13Engines = (bY > 1200);
                            const rVol = is13Engines ? 3.8 : 2.4;
                            const cVol = is13Engines ? 2.6 : 1.4;
                            boosterRumble.gain.setTargetAtTime(rVol, actx.currentTime, 0.08);
                            boosterCrackle.gain.setTargetAtTime(cVol, actx.currentTime, 0.08);
                        } else {
                            boosterRumble.gain.setTargetAtTime(0.0001, actx.currentTime, 0.12);
                            boosterCrackle.gain.setTargetAtTime(0.0001, actx.currentTime, 0.12);
                        }
                    }

                    if (p0.b_caught) {
                        if (!catchPopPlayed) { playFirecrackerSnapSound(); catchPopPlayed = true; camShake = 0.45; }
                        s1NozzleTips.forEach(t => t.plume.visible = false);
                        document.getElementById('tv-stage-badge').innerText = "TOWER CATCH SUCCESS";
                        document.getElementById('tv-stage-badge').style.color = "#38bdf8";
                    } else if (p0.b_thrust) {
                        const isThreeOnly = (bY <= 1200);
                        s1NozzleTips.forEach((t, i) => {
                            t.plume.visible = isThreeOnly ? t.isCenter : (i < 13);
                        });
                        if (bY <= 1500 && Math.random() < 0.55) {
                            s1Group.localToWorld(tempV.set(0, 0, 0));
                            emitParticle(
                                tempV.x + (Math.random()-0.5)*3.5, tempV.y - 2, tempV.z + (Math.random()-0.5)*3.5,
                                (Math.random()-0.5)*3.0, 0.4, (Math.random()-0.5)*3.0,
                                4.0, 24.0, 40, 0.85
                            );
                        }
                    } else {
                        s1NozzleTips.forEach(t => t.plume.visible = false);
                    }
                } else {
                    s1Group.visible = true;
                    s1Group.position.set(rx, ry + 6.0, 0);
                    s1Group.rotation.z = -pitch;
                    s1Group.updateMatrixWorld(true);
                }

                // フェアリング分離
                if (!p0.fairing && !fairingDetached && fairingHalves.length > 0 && !simCfg.is_preview) {
                    fairingDetached = true;
                    playHeavySeparationSound();
                    for(let fh of fairingHalves) {
                        fh.detached = true; scene.attach(fh.mesh);
                        fh.vx = ux * (vel * 0.072) + perpX * fh.side * 7.0;
                        fh.vy = uy * (vel * 0.072) + perpY * fh.side * 7.0 - 2.0;
                        fh.rotZ = -fh.side * 1.1;
                    }
                }
                if (fairingDetached) {
                    for(let fh of fairingHalves) {
                        fh.mesh.position.x += fh.vx * 0.016; fh.mesh.position.y += fh.vy * 0.016;
                        fh.vy -= 9.8 * 0.016 * 0.7; fh.mesh.rotation.z += fh.rotZ * 0.016;
                    }
                }

                // メインエンジン火炎
                if (p0.thrust && !p0.exploded && !simCfg.is_preview) {
                    const tips = (p0.stage === 1) ? s1NozzleTips : s2NozzleTips;
                    if (p0.stage === 1 && !boosterDetached) tips.push(...boosterNozzleTips);
                    for(let tObj of tips) {
                        tObj.plume.visible = true;
                        if (Math.random() < 0.3) {
                            tObj.node.getWorldPosition(tempV);
                            emitSpark(tempV.x, tempV.y, tempV.z, -ux*2.2, -uy*2.2, (Math.random()-0.5)*0.5, simCfg.spark_hex);
                        }
                    }
                    engineBounceLight.intensity = Math.max(0.0, 6.0 - alt * 0.3);
                    engineBounceLight.position.set(rx, ry + 3.0, 4.0);
                } else {
                    if (!p0.b_active) s1NozzleTips.forEach(t => t.plume.visible = false);
                    s2NozzleTips.forEach(t => t.plume.visible = false);
                    boosterNozzleTips.forEach(t => t.plume.visible = false);
                    engineBounceLight.intensity = 0.0;
                }

                // RCS スラスター噴射制御
                let rcsActiveHUD = false;
                const cmdFired = (Math.abs(rcsCmd) > 0.2 && Math.abs(prevRcsCmd) <= 0.2);
                prevRcsCmd = rcsCmd;

                for(let rcs of rcsNozzles) {
                    let burst = false;
                    if (!simCfg.is_preview && simT > 0 && !p0.exploded) {
                        if (rcs.isS1 && stage1Detached && p0.b_caught) {
                            burst = false;
                        } else {
                            if (cmdFired) {
                                if (rcs.isS1 && !stage1Detached && ((rcs.dir.dx < -0.3 && rcsCmd > 0) || (rcs.dir.dx > 0.3 && rcsCmd < 0))) burst = true;
                                if (!rcs.isS1 && stage1Detached && ((rcs.dir.dx < -0.3 && rcsCmd > 0) || (rcs.dir.dx > 0.3 && rcsCmd < 0))) burst = true;
                            }
                            if (rcs.isS1 && stage1Detached && p0.b_active && !p0.b_caught && (bY <= 3000) && cmdFired) {
                                burst = true;
                            }
                        }
                    }

                    if (burst) {
                        playRcsPuffSound();
                        rcsActiveHUD = true;
                        rcs.mount.getWorldPosition(tempV);

                        const localJetDir = new THREE.Vector3(rcs.dir.dx, rcs.dir.dy, rcs.dir.dz).normalize();
                        const parentQuat = new THREE.Quaternion();
                        rcs.mount.parent.getWorldQuaternion(parentQuat);
                        localJetDir.applyQuaternion(parentQuat);

                        for(let k=0; k<3; k++) {
                            const spd = 1.6 + Math.random() * 2.0;
                            emitParticle(
                                tempV.x, tempV.y, tempV.z,
                                localJetDir.x * spd + (Math.random()-0.5)*0.2,
                                localJetDir.y * spd + (Math.random()-0.5)*0.2,
                                localJetDir.z * spd + (Math.random()-0.5)*0.2,
                                0.2, 3.2, 7, 0.65, 0xe0f2fe
                            );
                        }
                    }
                }
                document.getElementById('hud-rcs').innerText = rcsActiveHUD ? "PULSE FIRING (8-AXIS)" : "STANDBY";
                document.getElementById('hud-rcs').style.color = rcsActiveHUD ? "#34d399" : "#38bdf8";

                // 注水デリュージ・先行点火・排煙
                if (simT < 0.0) {
                    const sec = Math.ceil(Math.abs(simT));
                    document.getElementById('tv-timer').innerText = simCfg.is_preview ? "PAD INSPECTION" : `T- 00:0${sec}.0`;
                    emitParticle(rx + 1.25, ry + 6.0 + s1Len * 0.85, 0, 0.25, 0.05, 0, 0.9, 4.2, 45, 0.4, 0xffffff);

                    if (simT >= -5.0 && !p0.exploded && !simCfg.is_preview) {
                        if (gasHiss && actx) gasHiss.gain.setTargetAtTime(0.55, actx.currentTime, 0.2);
                        for(let i=0; i<8; i++) {
                            const side = (Math.random() - 0.5) * 18.0;
                            emitParticle(rx + side, 3.5, (Math.random()-0.5)*18.0, side*0.35, 0.4+Math.random()*0.8, (Math.random()-0.5)*2.0, 5.0, 32.0, 60, 0.85, 0xe0f2fe);
                        }
                    }

                    if (simT >= -simCfg.ignition_lead && !p0.exploded && !simCfg.is_preview) {
                        if (actx) {
                            if (subRumble) subRumble.gain.setTargetAtTime(1.1, actx.currentTime, 0.3);
                            if (shockCrackle) shockCrackle.gain.setTargetAtTime(0.85, actx.currentTime, 0.2);
                        }
                        for(let tObj of s1NozzleTips) {
                            tObj.node.getWorldPosition(tempV);
                            emitSpark(tempV.x, tempV.y, tempV.z, (Math.random()-0.5)*1.5, -1.0-Math.random()*1.8, (Math.random()-0.5)*1.5, 0xfde047);
                        }
                    }

                    if (simT >= -3.0 && !p0.exploded && !simCfg.is_preview) {
                        camShake = 0.28;
                        for(let i=0; i<10; i++) {
                            const ang = Math.random() * Math.PI * 2;
                            const dist = 3.0 + Math.random() * 8.0;
                            emitParticle(
                                rx + Math.cos(ang) * dist, 3.5, Math.sin(ang) * dist,
                                Math.cos(ang) * (4.0 + Math.random()*4.0), 0.5 + Math.random()*0.8, Math.sin(ang) * (4.0 + Math.random()*4.0),
                                8.0, 48.0, 85, 0.92, 0xf8fafc
                            );
                        }
                    }
                } else if (!p0.exploded) {
                    const m = Math.floor(simT / 60), s = simT % 60;
                    document.getElementById('tv-timer').innerText = `T+ ${String(m).padStart(2,'0')}:${s.toFixed(1).padStart(4,'0')}`;
                    if (actx) {
                        const atm = Math.exp(-alt / 14.0);
                        if (subRumble) subRumble.gain.setTargetAtTime(1.15 * atm, actx.currentTime, 0.15);
                        if (shockCrackle) shockCrackle.gain.setTargetAtTime(0.90 * atm, actx.currentTime, 0.1);
                        if (gasHiss) gasHiss.gain.setTargetAtTime(0.18 * atm, actx.currentTime, 1.0);
                    }

                    if (simT < 6.0) {
                        camShake = 0.38;
                        for(let i=0; i<8; i++) {
                            const ang = Math.random() * Math.PI * 2;
                            const dist = 4.0 + Math.random() * 10.0;
                            emitParticle(
                                rx + Math.cos(ang) * dist, 3.5, Math.sin(ang) * dist,
                                Math.cos(ang) * (4.8 + Math.random()*4.5), 0.3 + Math.random()*0.6, Math.sin(ang) * (4.8 + Math.random()*4.5),
                                9.0, 56.0, 85, 0.88, 0xf1f5f9
                            );
                        }
                    }
                }

                for(let p of pool) {
                    if (!p.active) continue;
                    p.age++;
                    if (p.age >= p.maxAge) { p.active = false; p.sp.visible = false; continue; }
                    p.sp.position.x += p.vx; p.sp.position.y += p.vy; p.sp.position.z += p.vz;
                    const pr = p.age / p.maxAge;
                    const sc = p.s0 + (p.s1 - p.s0) * Math.pow(pr, 0.65);
                    p.sp.scale.set(sc, sc, 1);
                    p.sp.material.opacity = p.o * (1.0 - pr * pr);
                }
                for(let s of sparks) {
                    if (!s.active) continue;
                    s.age++;
                    if (s.age >= s.maxAge) { s.active = false; s.sp.visible = false; continue; }
                    s.sp.position.x += s.vx; s.sp.position.y += s.vy; s.sp.position.z += s.vz;
                    s.sp.material.opacity = 1.0 - (s.age / s.maxAge);
                }

                if (p0.stage === 2) { activeFocusWorld.set(0, s2Len * 0.45, 0); s2Group.localToWorld(activeFocusWorld); }
                else { activeFocusWorld.set(0, s1Len * 0.52, 0); rocket.localToWorld(activeFocusWorld); }

                if (simCfg.is_preview) {
                    const ang = elapsedSec * 0.22;
                    cameraMain.position.set(Math.sin(ang) * 115.0, 28.0, Math.cos(ang) * 115.0);
                    cameraMain.lookAt(0, 6.0 + (s1Len + s2Len) * 0.45, 0);
                } else {
                    cameraMain.position.set(activeFocusWorld.x - 72.0, activeFocusWorld.y + 16.0, activeFocusWorld.z + 140.0);
                    if (camShake > 0.002) {
                        cameraMain.position.x += (Math.random() - 0.5) * camShake;
                        cameraMain.position.y += (Math.random() - 0.5) * camShake;
                        camShake *= 0.94;
                    }
                    cameraMain.lookAt(activeFocusWorld);
                }

                // CAM 02 地上固定追尾
                if (pipVisible) {
                    let targetPos = new THREE.Vector3();
                    if (stage1Detached && p0.b_active) {
                        targetPos.set(bX * 0.1, bY_scaled + s1Len * 0.55, 0);
                        cameraPip.position.set(160.0, 14.0, 180.0);

                        if (p0.b_caught || bY_scaled <= 90.0) {
                            cameraPip.fov = THREE.MathUtils.lerp(cameraPip.fov, 25.0, 0.1);
                            document.getElementById('pip-tag').innerText = "CAM 02: GROUND OPTICAL (TOWER CATCH)";
                            document.getElementById('pip-hud-alt').innerText = p0.b_caught ? "SUSPENDED (SECURED)" : "FINAL TOUCHDOWN";
                        } else {
                            const targetFov = Math.max(12.0, Math.min(32.0, bY_scaled / 28.0));
                            cameraPip.fov = THREE.MathUtils.lerp(cameraPip.fov, targetFov, 0.1);
                            document.getElementById('pip-tag').innerText = "CAM 02: GROUND OPTICAL TRACKER";
                            document.getElementById('pip-hud-alt').innerText = `BOOSTER ALT: ${(bY * 0.001).toFixed(1)} km`;
                        }
                    } else {
                        targetPos.copy(rocket.position);
                        targetPos.y += s1Len * 0.5;
                        cameraPip.position.set(160.0, 14.0, 180.0);
                        cameraPip.fov = THREE.MathUtils.lerp(cameraPip.fov, Math.max(12.0, Math.min(32.0, rocket.position.y / 18.0)), 0.1);
                        document.getElementById('pip-tag').innerText = "CAM 02: GROUND OPTICAL (PAD 39A)";
                        document.getElementById('pip-hud-alt').innerText = `ALT: ${(rocket.position.y * 0.01).toFixed(1)} km`;
                    }
                    cameraPip.lookAt(targetPos);
                    cameraPip.updateProjectionMatrix();
                    pipTrackingSpot.position.set(targetPos.x + 80, targetPos.y + 100, targetPos.z + 80);
                    pipTrackingSpot.target.position.copy(targetPos);
                    pipTrackingSpot.target.updateMatrixWorld();
                    rendererPip.render(scene, cameraPip);
                }

                const dRangeKm = (rx * 10.0) / 1000.0;
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

                const isOrbit = (p0.event === "ORBIT");
                const canComplete = simCfg.spacex_return ? (isOrbit && p0.b_caught) : isOrbit;

                if (canComplete && !isMissionEnded) {
                    completeBanner.style.display = 'block';
                    if (simCfg.spacex_return) {
                        document.getElementById('complete-desc').innerText = "LEO INSERTION & SUPER HEAVY TOWER CATCH ACHIEVED";
                        document.getElementById('complete-sub').innerText = "Booster suspended on Mechazilla chopsticks. Orbiter in circular orbit.";
                    } else {
                        document.getElementById('complete-desc').innerText = "FIRST COSMIC VELOCITY (28,400 km/h) NOMINAL INSERTION";
                        document.getElementById('complete-sub').innerText = "Vehicle has achieved stable orbital trajectory.";
                    }
                    document.getElementById('tv-stage-badge').innerText = "MISSION SUCCESS - ALL OBJECTIVES ACHIEVED";
                    document.getElementById('tv-stage-badge').style.color = "#10b981";
                    document.getElementById('live-indicator').style.background = "#10b981";
                    document.getElementById('webcast-title').innerText = "MISSION COMPLETED";

                    if (actx) {
                        if (subRumble) subRumble.gain.setTargetAtTime(0.0001, actx.currentTime, 0.4);
                        if (shockCrackle) shockCrackle.gain.setTargetAtTime(0.0001, actx.currentTime, 0.4);
                        if (gasHiss) gasHiss.gain.setTargetAtTime(0.0001, actx.currentTime, 0.4);
                        if (boosterRumble) boosterRumble.gain.setTargetAtTime(0.0001, actx.currentTime, 0.2);
                        if (boosterCrackle) boosterCrackle.gain.setTargetAtTime(0.0001, actx.currentTime, 0.2);
                    }
                    setTimeout(() => { isMissionEnded = true; }, 2800);
                }

                if (p0.exploded) {
                    rudBanner.style.display = 'block';
                    rudDesc.innerText = failMessage || "機体過負荷による空中分解";
                }
            }

            // 🎯 メインアニメーションループを確実に開始
            requestAnimationFrame(animate);

            window.addEventListener('resize', () => {
                cameraMain.aspect = window.innerWidth / window.innerHeight;
                cameraMain.updateProjectionMatrix();
                rendererMain.setSize(window.innerWidth, window.innerHeight);
                resizePipRenderer();
            });
        } catch(err) {
            console.error("Simulation Render Error:", err);
        }
    });
    </script>
</body>
</html>
"""

final_html = html_template.replace("__SIM_DATA__", traj_json).replace("__SIM_CFG__", cfg_json).replace("__FAIL_MSG__", fail_msg_clean)
components.html(final_html, height=980)

if launch_clicked:
    st.markdown("---")
    st.markdown("### 📋 フライトテレメトリ詳細レポート")
    if error_msg:
        st.error(f"⚠️ **ミッション異常終了 (RUD)**: {error_msg}")
    else:
        st.success("🎉 **ミッション完全成功**: 軌道投入および機体制御シーケンスが設計通り正常に完了しました。")
