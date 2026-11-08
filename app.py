import json
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect Ultra",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("🚀 Orbital Architect Ultra")
st.caption(
    "※ 4K実写級：IFT-5タワーキャッチ・精密光学長焦点追従・推進剤別多層プルーム・4段階RUD完全再現版"
)

# =========================================================================
# 🔬 推進剤・材料・空力パーツ・ブースターデータベース
# =========================================================================
PROPELLANTS = {
    "超高密度サブクール・メタロックス (CH4 / LOX) [Starship王道]": {
        "base_isp_sl": 338,
        "base_isp_vac": 382,
        "base_thrust": 2800,
        "density": 0.85,
        "flame_hex": 0x60A5FA,
        "outer_hex": 0x1D4ED8,
        "spark_hex": 0x93C5FD,
        "risk": 0.0,
        "type": "methalox",
    },
    "高精製ロケットグレードケロシン (RP-1 / LOX) [Saturn V / Falcon]": {
        "base_isp_sl": 302,
        "base_isp_vac": 335,
        "base_thrust": 1950,
        "density": 1.03,
        "flame_hex": 0xFEF08A,
        "outer_hex": 0xEA580C,
        "spark_hex": 0xFDE047,
        "risk": 0.0,
        "type": "rp1",
    },
    "超極低温スラッシュ・ハイドロロックス (LH2 / LOX) [H3 / SLS]": {
        "base_isp_sl": 385,
        "base_isp_vac": 468,
        "base_thrust": 1450,
        "density": 0.34,
        "flame_hex": 0xFBCFE8,
        "outer_hex": 0xBE185D,
        "spark_hex": 0xFFFFFF,
        "risk": 0.01,
        "type": "hydro",
    },
    "【猛毒】四酸化二窒素 ＋ UDMH (N2O4 / UDMH) [Proton / ICBM]": {
        "base_isp_sl": 288,
        "base_isp_vac": 322,
        "base_thrust": 2100,
        "density": 1.26,
        "flame_hex": 0xF5D0FE,
        "outer_hex": 0x9333EA,
        "spark_hex": 0xFAB1A0,
        "risk": 0.05,
        "type": "hypergolic",
    },
    "【核熱】固体炉心型原子力サーマルロケット (NERVA / LH2)": {
        "base_isp_sl": 450,
        "base_isp_vac": 925,
        "base_thrust": 2500,
        "density": 0.30,
        "flame_hex": 0x86EFAC,
        "outer_hex": 0x14532D,
        "spark_hex": 0x4ADE80,
        "risk": 0.12,
        "type": "nuclear",
    },
    "【超高カロリー】発酵イースト＆濃厚バター (Baguette Fuel)": {
        "base_isp_sl": 310,
        "base_isp_vac": 360,
        "base_thrust": 2200,
        "density": 0.92,
        "flame_hex": 0xFEF08A,
        "outer_hex": 0xD97706,
        "spark_hex": 0xFFEDD5,
        "risk": 0.0,
        "type": "rp1",
    },
    "【高密度黒鉛】最高級ハイユニグラファイト固体燃料": {
        "base_isp_sl": 295,
        "base_isp_vac": 330,
        "base_thrust": 2600,
        "density": 1.15,
        "flame_hex": 0xFDE047,
        "outer_hex": 0xB45309,
        "spark_hex": 0xFFFFFF,
        "risk": 0.0,
        "type": "solid",
    },
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [極限高圧]": {
        "isp_mod": 1.07,
        "thrust_mod": 1.42,
        "mass_mod": 1.22,
        "max_pressure_limit": 380,
        "cyc_id": "ffsc",
    },
    "酸化剤リッチ二段燃焼 (ORSC) [高出力信頼性]": {
        "isp_mod": 1.03,
        "thrust_mod": 1.25,
        "mass_mod": 1.18,
        "max_pressure_limit": 310,
        "cyc_id": "sc",
    },
    "ガス発生器サイクル (GG) [煤排気ダクト付]": {
        "isp_mod": 0.96,
        "thrust_mod": 0.98,
        "mass_mod": 0.84,
        "max_pressure_limit": 195,
        "cyc_id": "gg",
    },
    "リニアエアロスパイク方式 [全高度最適膨張]": {
        "isp_mod": 1.09,
        "thrust_mod": 1.10,
        "mass_mod": 1.32,
        "max_pressure_limit": 250,
        "cyc_id": "aerospike",
    },
}

MATERIALS = {
    "Austenitic 304L 冷間圧延鏡面ステンレス [Starship仕様]": {
        "base_dry_ratio": 0.065,
        "max_q_base": 58.0,
        "max_g_base": 8.5,
        "mat_id": "ss",
    },
    "航空宇宙用 Al-Li-2195 アルミリチウム合金 [SLSオレンジ塗装]": {
        "base_dry_ratio": 0.050,
        "max_q_base": 42.0,
        "max_g_base": 6.0,
        "mat_id": "al",
    },
    "Saturn V 伝統 ホワイト＆ブラック・ロールチェック塗工": {
        "base_dry_ratio": 0.054,
        "max_q_base": 45.0,
        "max_g_base": 6.5,
        "mat_id": "saturn",
    },
    "高弾性トレカ炭素繊維複合材 (CFRP) [マットブラック]": {
        "base_dry_ratio": 0.036,
        "max_q_base": 36.0,
        "max_g_base": 5.5,
        "mat_id": "cf",
    },
    "軍用オリーブドラブ重装甲鋼板 [ICBM サルマト仕様]": {
        "base_dry_ratio": 0.088,
        "max_q_base": 95.0,
        "max_g_base": 14.0,
        "mat_id": "military",
    },
    "焼きたて小麦粉クラスト [超軽量パリパリ仕様]": {
        "base_dry_ratio": 0.040,
        "max_q_base": 24.0,
        "max_g_base": 4.2,
        "mat_id": "baguette",
    },
    "天然ヒノキ材＆消しゴムラバー [HB鉛筆仕様]": {
        "base_dry_ratio": 0.048,
        "max_q_base": 32.0,
        "max_g_base": 5.0,
        "mat_id": "pencil",
    },
    "超耐熱インコネル718 モノコック [重装甲チタン調]": {
        "base_dry_ratio": 0.092,
        "max_q_base": 110.0,
        "max_g_base": 12.0,
        "mat_id": "inconel",
    },
}

STRAPON_BOOSTERS = {
    "なし (単段スリムコア構成)": {
        "count": 0,
        "thrust_add": 0.0,
        "mass_add": 0.0,
        "fuel_add": 0.0,
        "isp_sl": 0,
        "type": "none",
    },
    "Falcon Heavy風 液体LRB × 2基 (グリッドフィン付)": {
        "count": 2,
        "thrust_add": 5800.0,
        "mass_add": 50.0,
        "fuel_add": 820.0,
        "isp_sl": 315,
        "type": "lrb",
    },
    "Soyuz R-7風 テーパー液体ブースター × 4基 (コロリョフクロス専用)": {
        "count": 4,
        "thrust_add": 4200.0,
        "mass_add": 38.0,
        "fuel_add": 520.0,
        "isp_sl": 308,
        "type": "soyuz",
    },
    "SLS / H3風 巨大SRB × 2基 (白塗装＆黒ジョイントリング)": {
        "count": 2,
        "thrust_add": 8800.0,
        "mass_add": 68.0,
        "fuel_add": 950.0,
        "isp_sl": 278,
        "type": "srb",
    },
}

AERO_WINGS = {
    "チタン鍛造極超音速グリッドフィン × 4基 (SpaceX回収仕様)": {
        "lift_coeff": 0.12,
        "drag_penalty": 1.05,
        "mass": 1.2,
        "flutter_mach": 99.0,
        "wing_id": "grid",
    },
    "Starship風 空力エルロンボディフラップ × 4枚": {
        "lift_coeff": 0.35,
        "drag_penalty": 1.12,
        "mass": 2.8,
        "flutter_mach": 99.0,
        "wing_id": "starship_flap",
    },
    "なし (純粋な軸対称弾道ロケット)": {
        "lift_coeff": 0.0,
        "drag_penalty": 1.0,
        "mass": 0.0,
        "flutter_mach": 99.0,
        "wing_id": "none",
    },
    "軍用ミサイル制御小翼 (グリッド＆デルタ)": {
        "lift_coeff": 0.45,
        "drag_penalty": 1.15,
        "mass": 1.5,
        "flutter_mach": 99.0,
        "wing_id": "missile_fin",
    },
    "コンコルド風 ダブルデルタ超音速後退翼": {
        "lift_coeff": 0.95,
        "drag_penalty": 1.45,
        "mass": 7.5,
        "flutter_mach": 3.8,
        "wing_id": "delta_wing",
    },
}

FAIRINGS = {
    "Starship風 窓付き有人クルーノーズコーン (片面黒耐熱タイル)": {
        "mass": 4.2,
        "cd": 0.22,
        "heat_limit": 2900,
        "shape_id": "starship_crew",
    },
    "バイコニカル炭素複合材クラムシェル (金箔通信衛星内蔵)": {
        "mass": 2.1,
        "cd": 0.18,
        "heat_limit": 2600,
        "shape_id": "biconic",
    },
    "ICBM MIRV 多弾頭再突入カプセルノーズコーン": {
        "mass": 3.5,
        "cd": 0.14,
        "heat_limit": 3800,
        "shape_id": "icbm_warhead",
    },
    "有人カプセル ＋ レスキューアボートタワー (LES付)": {
        "mass": 6.8,
        "cd": 0.32,
        "heat_limit": 3200,
        "shape_id": "abort_tower",
    },
    "フランスパン 先端クープカウル": {
        "mass": 1.5,
        "cd": 0.24,
        "heat_limit": 2200,
        "shape_id": "baguette_tip",
    },
    "削りたて鉛筆芯ノーズコーン (黒鉛高硬度)": {
        "mass": 1.2,
        "cd": 0.20,
        "heat_limit": 3000,
        "shape_id": "pencil_tip",
    },
}

PRESETS = {
    "🌟 カスタム構成 (自由設定)": None,
    "🚀 SpaceX Starship & Super Heavy (IFT-5 タワーキャッチ仕様)": {
        "s1_prop": 0,
        "s1_cycle": 0,
        "s1_eng": 33,
        "s1_pc": 300,
        "s1_eps": 24,
        "s1_fuel": 3400.0,
        "s1_mat": 0,
        "s1_thick": 4.2,
        "strapon": 0,
        "spacex_rtls": True,
        "wings": 0,
        "aoa": 0.5,
        "rcs": 0.8,
        "s2_prop": 0,
        "s2_cycle": 0,
        "s2_eng": 6,
        "s2_eps": 150,
        "s2_fuel": 1200.0,
        "s2_mat": 0,
        "s2_thick": 3.0,
        "fairing": 0,
        "payload": 50.0,
        "water": 300,
        "turn_exp": 0.62,
    },
    "🌕 NASA Saturn V (アポロ月面着陸ロケット)": {
        "s1_prop": 1,
        "s1_cycle": 2,
        "s1_eng": 5,
        "s1_pc": 70,
        "s1_eps": 16,
        "s1_fuel": 2150.0,
        "s1_mat": 2,
        "s1_thick": 5.5,
        "strapon": 0,
        "spacex_rtls": False,
        "wings": 2,
        "aoa": 0.0,
        "rcs": 1.2,
        "s2_prop": 2,
        "s2_cycle": 2,
        "s2_eng": 5,
        "s2_eps": 40,
        "s2_fuel": 450.0,
        "s2_mat": 2,
        "s2_thick": 3.8,
        "fairing": 3,
        "payload": 45.0,
        "water": 200,
        "turn_exp": 0.70,
    },
    "🇯🇵 JAXA H3ロケット 22S (固体ブースター2基構成)": {
        "s1_prop": 2,
        "s1_cycle": 1,
        "s1_eng": 2,
        "s1_pc": 120,
        "s1_eps": 35,
        "s1_fuel": 250.0,
        "s1_mat": 1,
        "s1_thick": 3.2,
        "strapon": 3,
        "spacex_rtls": False,
        "wings": 2,
        "aoa": 0.0,
        "rcs": 1.0,
        "s2_prop": 2,
        "s2_cycle": 1,
        "s2_eng": 1,
        "s2_eps": 180,
        "s2_fuel": 32.0,
        "s2_mat": 1,
        "s2_thick": 2.2,
        "fairing": 1,
        "payload": 6.5,
        "water": 250,
        "turn_exp": 0.65,
    },
    "☢️ 大陸間弾道ミサイル ICBM「RS-28 サルマト (Sarmat)」": {
        "s1_prop": 3,
        "s1_cycle": 1,
        "s1_eng": 4,
        "s1_pc": 210,
        "s1_eps": 22,
        "s1_fuel": 180.0,
        "s1_mat": 4,
        "s1_thick": 6.5,
        "strapon": 0,
        "spacex_rtls": False,
        "wings": 3,
        "aoa": 0.0,
        "rcs": 0.4,
        "s2_prop": 3,
        "s2_cycle": 1,
        "s2_eng": 1,
        "s2_eps": 60,
        "s2_fuel": 35.0,
        "s2_mat": 4,
        "s2_thick": 4.5,
        "fairing": 2,
        "payload": 10.0,
        "water": 80,
        "turn_exp": 0.48,
    },
    "⚡ 極超音速滑空ミサイル「ダークイーグル (Dark Eagle LRHW)」": {
        "s1_prop": 3,
        "s1_cycle": 0,
        "s1_eng": 1,
        "s1_pc": 280,
        "s1_eps": 18,
        "s1_fuel": 120.0,
        "s1_mat": 3,
        "s1_thick": 4.0,
        "strapon": 0,
        "spacex_rtls": False,
        "wings": 3,
        "aoa": 2.0,
        "rcs": 0.3,
        "s2_prop": 3,
        "s2_cycle": 0,
        "s2_eng": 1,
        "s2_eps": 70,
        "s2_fuel": 25.0,
        "s2_mat": 3,
        "s2_thick": 2.5,
        "fairing": 2,
        "payload": 2.5,
        "water": 100,
        "turn_exp": 0.38,
    },
    "🥖 【ジョーク】超音速フランスパン「バゲット・V2 (Baguette)」": {
        "s1_prop": 5,
        "s1_cycle": 2,
        "s1_eng": 7,
        "s1_pc": 160,
        "s1_eps": 20,
        "s1_fuel": 450.0,
        "s1_mat": 5,
        "s1_thick": 2.5,
        "strapon": 0,
        "spacex_rtls": False,
        "wings": 2,
        "aoa": 0.0,
        "rcs": 1.5,
        "s2_prop": 5,
        "s2_cycle": 2,
        "s2_eng": 1,
        "s2_eps": 90,
        "s2_fuel": 90.0,
        "s2_mat": 5,
        "s2_thick": 1.8,
        "fairing": 4,
        "payload": 4.0,
        "water": 120,
        "turn_exp": 0.60,
    },
    "✏️ 【ジョーク】本当に鉛筆ロケット「三菱ハイユニ HB-9000」": {
        "s1_prop": 6,
        "s1_cycle": 2,
        "s1_eng": 1,
        "s1_pc": 190,
        "s1_eps": 18,
        "s1_fuel": 320.0,
        "s1_mat": 6,
        "s1_thick": 3.0,
        "strapon": 0,
        "spacex_rtls": False,
        "wings": 2,
        "aoa": 0.0,
        "rcs": 1.0,
        "s2_prop": 6,
        "s2_cycle": 2,
        "s2_eng": 1,
        "s2_eps": 80,
        "s2_fuel": 60.0,
        "s2_mat": 6,
        "s2_thick": 2.0,
        "fairing": 5,
        "payload": 2.0,
        "water": 90,
        "turn_exp": 0.55,
    },
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
    on_change=on_preset_change,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 第1段 (推進・燃焼・構造)",
    "🚀 外部ブースター & SpaceXキャッチ機構",
    "🛩️ 空力翼 & 4象限RCS姿勢制御",
    "🛰️ 第2段 (オービター) & 先端部",
    "🌊 発射台水冷デリュージ & ガイダンス",
])

with tab1:
  c1, c2, c3 = st.columns(3)
  with c1:
    s1_prop = st.selectbox("第1段 推進剤", prop_keys, key="k_s1_prop")
    s1_cycle = st.selectbox("ターボポンプ駆動サイクル", cyc_keys, key="k_s1_cycle")
    s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, key="k_s1_eng")
  with c2:
    s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, step=10, key="k_s1_pc")
    s1_eps = st.slider(
        "海面膨張比 (ε: ノズル径連動)", 8, 70, step=1, key="k_s1_eps"
    )
  with c3:
    s1_fuel = st.slider(
        "第1段 推進剤充填量 (トン: 胴体長連動)",
        50.0,
        4500.0,
        step=25.0,
        key="k_s1_fuel",
    )
    s1_mat = st.selectbox("第1段 構造素材", mat_keys, key="k_s1_mat")
    s1_thick = st.slider(
        "外殻等価板厚 (mm)", 1.0, 12.0, step=0.1, key="k_s1_thick"
    )

with tab2:
  c1, c2 = st.columns(2)
  with c1:
    strapon_opt = st.selectbox("ブースター種別クラスタ", strap_keys, key="k_strapon")
    sep_thrust_factor = st.slider(
        "分離パイロモーター推力倍率",
        0.5,
        3.0,
        1.2,
        step=0.1,
        key="k_sep_thrust",
    )
  with c2:
    spacex_return_mode = st.checkbox(
        "🔄 SpaceX型 ブースターRTLS帰還 ＆ チョップスティック・タワーキャッチ"
        " (IFT-5再現)",
        key="k_spacex_rtls",
    )
    st.caption(
        "※ ONの場合：第2段軌道投入＆第1段タワーキャッチの両方成功でミッション完了。OFFの場合：軌道投入のみでミッション完了。"
    )

with tab3:
  c1, c2 = st.columns(2)
  with c1:
    wing_type = st.selectbox("機体外部 空力パーツ", wing_keys, key="k_wings")
    angle_of_attack = st.slider(
        "固定取り付け迎角 AoA (deg)", -3.0, 12.0, step=0.5, key="k_aoa"
    )
  with c2:
    rcs_deadband = st.slider(
        "4象限RCS デッドバンド感度 (deg)", 0.2, 5.0, step=0.1, key="k_rcs"
    )
    st.caption(
        "※ 姿勢制御要求が発生した瞬間だけ冷ガス窒素(GN2)が一瞬パルス噴射されます。"
    )

with tab4:
  c1, c2, c3 = st.columns(3)
  with c1:
    s2_prop = st.selectbox("第2段 推進剤", prop_keys, key="k_s2_prop")
    s2_cycle = st.selectbox("第2段 ポンプ方式", cyc_keys, key="k_s2_cycle")
    s2_eng_count = st.slider("真空ノズル基数", 1, 9, key="k_s2_eng")
    s2_eps = st.slider(
        "第2段 真空膨張比 (ε)", 30, 280, step=5, key="k_s2_eps"
    )
  with c2:
    s2_fuel = st.slider(
        "第2段 推進剤充填量 (トン)", 10.0, 1500.0, step=10.0, key="k_s2_fuel"
    )
    s2_mat = st.selectbox("第2段 構造素材", mat_keys, key="k_s2_mat")
    s2_thick = st.slider(
        "第2段 壁厚 (mm)", 0.8, 8.0, step=0.1, key="k_s2_thick"
    )
  with c3:
    fairing_type = st.selectbox(
        "先端空力カウル / 弾頭 / ペイロード", fair_keys, key="k_fairing"
    )
    fairing_sep_alt = st.slider(
        "フェアリング分離高度 (km)",
        30.0,
        180.0,
        75.0,
        step=5.0,
        key="k_fairing_sep",
    )
    payload_mass = st.slider(
        "投入衛星 / 弾頭質量 (トン)", 0.2, 120.0, step=0.5, key="k_payload"
    )

with tab5:
  c1, c2 = st.columns(2)
  with c1:
    water_flow_rate = st.slider(
        "消音注水デリュージ流量 (トン/秒)", 50, 450, step=25, key="k_water"
    )
    ignition_lead_time = st.slider(
        "エンジン先行点火開始 (T-マイナス秒)",
        2.5,
        6.0,
        3.8,
        step=0.1,
        key="k_ign_lead",
    )
  with c2:
    turn_start_alt = st.slider(
        "ピッチオーバー開始高度 (km)", 0.3, 15.0, 1.8, step=0.1, key="k_turn_start"
    )
    turn_end_alt = st.slider(
        "水平重力ターン完了高度 (km)",
        50.0,
        250.0,
        120.0,
        step=5.0,
        key="k_turn_end",
    )
    turn_exponent = st.slider(
        "ターン曲率指数", 0.3, 2.0, step=0.02, key="k_turn_exp"
    )
    throttle_maxq = st.slider(
        "Max-Q 領域 推力抑制 (%)", 30, 100, 75, key="k_maxq_thr"
    )
    max_g_limit_cut = st.slider(
        "最大加速度リミッター (G)", 2.5, 18.0, 5.0, step=0.2, key="k_max_g"
    )


def calc_stage_specs(
    prop_key, cycle_key, pc, eps, eng_count, fuel_mass, mat_key, thick
):
  prop = PROPELLANTS[prop_key]
  cyc = PUMP_CYCLES[cycle_key]
  mat = MATERIALS[mat_key]

  pc_factor = 1.0 + (pc - 100.0) * 0.0006
  eps_vac_bonus = 1.0 + np.log10(eps / 25.0) * 0.08
  overexpansion_penalty = max(0.0, (eps - 35.0) * 0.006)

  isp_sl = (
      prop["base_isp_sl"]
      * cyc["isp_mod"]
      * pc_factor
      * (1.0 - overexpansion_penalty)
  )
  isp_vac = prop["base_isp_vac"] * cyc["isp_mod"] * pc_factor * eps_vac_bonus

  thrust_vac_per_eng = (
      prop["base_thrust"] * cyc["thrust_mod"] * ((pc / 150.0) ** 0.65)
  )
  thrust_sl_per_eng = thrust_vac_per_eng * (isp_sl / isp_vac)

  density_penalty = (1.0 / prop["density"]) ** 0.35
  thick_factor = thick / 3.0
  dry_ratio = mat["base_dry_ratio"] * density_penalty * thick_factor + 0.005
  eng_mass = (
      (thrust_vac_per_eng / 750.0)
      * cyc["mass_mod"]
      * (1.0 + eps * 0.002)
      * eng_count
  )
  dry_mass = fuel_mass * dry_ratio + eng_mass

  return {
      "isp_sl": float(isp_sl),
      "isp_vac": float(isp_vac),
      "thrust_sl": float(thrust_sl_per_eng * eng_count),
      "thrust_vac": float(thrust_vac_per_eng * eng_count),
      "dry_mass": float(dry_mass),
      "max_q": float(mat["max_q_base"] * (thick_factor**1.1)),
      "max_g": float(mat["max_g_base"] * (thick_factor**0.85)),
      "pc": pc,
      "eps": eps,
      "cd_mod": density_penalty,
      "mat_id": mat["mat_id"],
      "cyc_id": cyc["cyc_id"],
      "flame_hex": prop["flame_hex"],
      "outer_hex": prop["outer_hex"],
      "spark_hex": prop["spark_hex"],
      "prop_type": prop["type"],
      "eng_count": eng_count,
  }


wing_spec = AERO_WINGS[wing_type]
fair_spec = FAIRINGS[fairing_type]
strapon_spec = STRAPON_BOOSTERS[strapon_opt]

s1_spec = calc_stage_specs(
    s1_prop,
    s1_cycle,
    s1_pc,
    s1_eps,
    s1_eng_count,
    s1_fuel,
    s1_mat,
    s1_thick,
)
s2_spec = calc_stage_specs(
    s2_prop,
    s2_cycle,
    220,
    s2_eps,
    s2_eng_count,
    s2_fuel,
    s2_mat,
    s2_thick,
)

total_s2_wet = (
    s2_fuel + s2_spec["dry_mass"] + payload_mass + fair_spec["mass"]
)
total_s1_wet = (
    s1_fuel
    + s1_spec["dry_mass"]
    + wing_spec["mass"]
    + strapon_spec["mass_add"]
    + strapon_spec["fuel_add"]
    + total_s2_wet
)

total_liftoff_thrust = s1_spec["thrust_sl"] + strapon_spec["thrust_add"]
twr_init = total_liftoff_thrust / (total_s1_wet * 9.80665)
dv_s1 = (
    s1_spec["isp_sl"]
    * 9.80665
    * np.log(
        total_s1_wet
        / (total_s1_wet - s1_fuel - strapon_spec["fuel_add"])
    )
)
dv_s2 = (
    s2_spec["isp_vac"]
    * 9.80665
    * np.log(total_s2_wet / (s2_spec["dry_mass"] + payload_mass))
)
total_dv = dv_s1 + dv_s2

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric(
    "総離床重量 / 離床TWR",
    f"{total_s1_wet:.1f} t",
    f"TWR: {twr_init:.2f} ({'離床可能' if twr_init >= 1.05 else '推力不足！'})",
)
m2.metric(
    "総計算速度増分 (ΔV)",
    f"{total_dv:.0f} m/s",
    "LEO投入基準: 9,200 m/s",
)
m3.metric(
    "構造限界動圧 / 耐G",
    f"{s1_spec['max_q']:.1f} kPa",
    f"耐G: {s1_spec['max_g']:.1f} G",
)
m4.metric(
    "ブースター追加推力",
    f"+{strapon_spec['thrust_add']:.0f} kN",
    f"基数: {strapon_spec['count']} 基",
)

s1_len_scaled = float(
    np.clip(10.0 + (s1_fuel / 4500.0) * 16.0, 9.0, 26.0)
)
s2_len_scaled = float(
    np.clip(5.0 + (s2_fuel / 1200.0) * 8.0, 4.5, 13.0)
)

pin_offset_3d = s1_len_scaled - 2.2
target_bottom_y_3d = 68.6 - pin_offset_3d
TOWER_PHYSICAL_CATCH_Y = max(0.0, (target_bottom_y_3d - 6.0) * 10.0)


# =========================================================================
# 💥 物理シミュレーション (ブースター連続降下プロファイル完全修正版)
# =========================================================================
def run_simulation(preview_only=False):
  if preview_only:
    return [{
        "t": -10.0,
        "x": 0.0,
        "y": 0.0,
        "alt": 0.0,
        "v": 0.0,
        "q": 0.0,
        "g": 1.0,
        "stage": 1,
        "fairing": True,
        "wings": bool(wing_spec["wing_id"] != "none"),
        "strapon": bool(strapon_spec["count"] > 0),
        "exploded": False,
        "thrust": False,
        "pitch": 0.0,
        "mach": 0.0,
        "event": "PREVIEW",
        "rcs_cmd": 0.0,
        "s1_prop_pct": 100.0,
        "s2_prop_pct": 100.0,
        "pitch_deg": 90.0,
        "apogee_km": 0.0,
        "chamber_p": 0.0,
        "b_x": 0.0,
        "b_y": 0.0,
        "b_active": False,
        "b_pitch": 0.0,
        "b_thrust": False,
        "b_caught": False,
        "b_rcs": 0.0,
        "b_vy": 0.0,
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
  b_rcs = 0.0
  b_sep_time = 0.0
  b_fuel = float(s1_fuel * 1000.0 * 0.18) if spacex_return_mode else 0.0

  history = []
  fail_reason = None
  prev_pitch_val = 90.0
  rcs_cooldown = 0.0

  for cd_step in range(21):
    t_cd = -10.0 + cd_step * 0.5
    history.append({
        "t": float(t_cd),
        "x": 0.0,
        "y": 0.0,
        "alt": 0.0,
        "v": 0.0,
        "q": 0.0,
        "g": 1.0,
        "stage": 1,
        "fairing": True,
        "wings": wings_attached,
        "strapon": strapon_attached,
        "exploded": False,
        "thrust": bool(t_cd >= -ignition_lead_time),
        "pitch": 0.0,
        "mach": 0.0,
        "event": "COUNTDOWN",
        "rcs_cmd": 0.0,
        "s1_prop_pct": 100.0,
        "s2_prop_pct": 100.0,
        "pitch_deg": 90.0,
        "apogee_km": 0.0,
        "chamber_p": float(s1_pc) if t_cd >= -ignition_lead_time else 0.0,
        "b_x": 0.0,
        "b_y": 0.0,
        "b_active": False,
        "b_pitch": 0.0,
        "b_thrust": False,
        "b_caught": False,
        "b_rcs": 0.0,
        "b_vy": 0.0,
    })

  maxq_passed, supersonic_called = False, False
  TARGET_ORBITAL_VX = 7900.0

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
      target_pitch_deg = 90.0 * (1.0 - (prog**turn_exponent))
    else:
      target_pitch_deg = 0.0

    wing_lift_force = 0.0
    if wings_attached and alt_km < 50.0 and rho > 0.003:
      wing_lift_force = (
          0.5
          * rho
          * (v**2)
          * (wing_spec["lift_coeff"] * 24.0)
          * np.sin(np.radians(angle_of_attack))
      )
      target_pitch_deg -= (wing_lift_force / 12000.0) * (mach**1.3)

    pitch_deg = max(0.0, min(90.0, target_pitch_deg))
    pitch_rad = float(np.radians(pitch_deg))
    visual_pitch = float(np.radians(90.0 - pitch_deg))

    pitch_rate = (pitch_deg - prev_pitch_val) / dt
    prev_pitch_val = pitch_deg
    rcs_cmd = 0.0
    if rcs_cooldown > 0:
      rcs_cooldown -= dt
    elif (abs(pitch_rate) > 0.15 and alt_km > 0.8) or (
        alt_km >= 230.0 and pitch_deg > 0.1
    ):
      rcs_cmd = -1.0 if pitch_rate > 0 else 1.0
      rcs_cooldown = 4.5

    cur_event = "FLIGHT"
    if v >= 340.0 and not supersonic_called:
      cur_event, supersonic_called = "SUPERSONIC", True
    elif alt_km > 11.0 and not maxq_passed:
      cur_event, maxq_passed = "MAX_Q", True

    if fairing_attached and alt_km >= fairing_sep_alt:
      fairing_attached, cur_event = False, "FAIRING_SEP"

    f_mass = (fair_spec["mass"] * 1000.0) if fairing_attached else 0.0
    w_mass = (wing_spec["mass"] * 1000.0) if wings_attached else 0.0
    strap_m = (
        (strapon_spec["mass_add"] * 1000.0 + max(0.0, fuel_strapon_rem))
        if strapon_attached
        else 0.0
    )

    current_pc = 0.0

    if stage == 1:
      if strapon_attached:
        if fuel_strapon_rem > 0 and (fuel_s1_rem > s1_fuel * 1000.0 * 0.28):
          strap_thrust = strapon_spec["thrust_add"] * 1000.0
          fuel_strapon_rem -= (
              (strap_thrust / (strapon_spec["isp_sl"] * g0)) * dt * 1.3
          )
        else:
          strapon_attached, cur_event, strap_thrust = (
              False,
              "BOOSTER_SEP",
              0.0,
          )
      else:
        strap_thrust = 0.0

      meco_thresh = (s1_fuel * 1000.0 * 0.18) if spacex_return_mode else 0.0
      if fuel_s1_rem <= meco_thresh:
        stage, strapon_attached, cur_event = 2, False, "HOT_STAGING"
        if not b_active:
          b_active = True
          b_sep_time = t
          b_x, b_y = x, y
          b_vx = vx * 0.45
          b_vy = -8.0 * sep_thrust_factor
          b_pitch = visual_pitch
      else:
        cur_mass = float(
            (
                s1_spec["dry_mass"]
                + s2_fuel
                + s2_spec["dry_mass"]
                + payload_mass
            )
            * 1000.0
            + f_mass
            + w_mass
            + strap_m
            + fuel_s1_rem
        )
        atm_factor = float(np.exp(-alt / 7400.0))
        isp = float(
            s1_spec["isp_vac"]
            - (s1_spec["isp_vac"] - s1_spec["isp_sl"]) * atm_factor
        )
        thrust_core = float(
            (
                s1_spec["thrust_vac"]
                - (s1_spec["thrust_vac"] - s1_spec["thrust_sl"]) * atm_factor
            )
            * 1000.0
        )

        t_throttle = 1.0
        if t < 3.0:
          t_throttle = 0.65 + (t / 3.0) * 0.35
          thrust_core *= t_throttle
        if 8000 < alt < 17000:
          t_throttle *= throttle_maxq / 100.0
          thrust_core *= throttle_maxq / 100.0

        thrust = thrust_core + strap_thrust
        if thrust / (cur_mass * g0) > max_g_limit_cut:
          thrust = max_g_limit_cut * cur_mass * g0
        fuel_s1_rem -= (thrust_core / (isp * g0)) * dt
        current_pc = s1_pc * t_throttle

    if stage == 2:
      strapon_attached = False
      cur_mass = float(
          (s2_spec["dry_mass"] + payload_mass) * 1000.0
          + f_mass
          + max(0.0, fuel_s2_rem)
      )
      if fuel_s2_rem <= 0:
        thrust = 0.0
        current_pc = 0.0
      else:
        atm_factor = float(np.exp(-alt / 7400.0))
        isp = float(
            s2_spec["isp_vac"]
            - (s2_spec["isp_vac"] - s2_spec["isp_sl"]) * atm_factor
        )
        thrust_base = float(
            (
                s2_spec["thrust_vac"]
                - (s2_spec["thrust_vac"] - s2_spec["thrust_sl"]) * atm_factor
            )
            * 1000.0
        )
        if b_active and (t - b_sep_time) < 2.0:
          thrust_base *= 1.0 + 0.15 * sep_thrust_factor
        speed_error = TARGET_ORBITAL_VX - vx
        thrust = (
            0.0
            if speed_error <= 0.0
            else (
                thrust_base * max(0.05, speed_error / 400.0)
                if speed_error < 400.0
                else thrust_base
            )
        )
        if thrust / (cur_mass * g0) > max_g_limit_cut:
          thrust = max_g_limit_cut * cur_mass * g0
        fuel_s2_rem -= (thrust / (isp * g0)) * dt
        current_pc = 220.0 * (
            thrust / thrust_base if thrust_base > 0 else 0.0
        )

    # =========================================================================
    # 🔄 【改善適用箇所】ブースター連続降下プロファイル（チャタリング・ワープ完全排除）
    # =========================================================================
    b_rcs = 0.0
    if b_active and not b_caught:
      b_alt = b_y
      rem_h = max(0.0, b_alt - TOWER_PHYSICAL_CATCH_Y)
      sep_elapsed = t - b_sep_time

      if not spacex_return_mode:
        b_thrust = False
        b_pitch += 0.05 * dt
        b_vx *= 0.992
        b_vy = max(-450.0, b_vy - g0 * 1.25 * dt)
        b_x = max(0.0, b_x + b_vx * dt)
        b_y = max(0.0, b_y + b_vy * dt)
      else:
        if sep_elapsed <= 4.0:
          # 【Phase 1】ホットステージング直後のフリップ反転（4秒間）
          b_thrust = False
          target_flip = -1.5708
          pitch_err = target_flip - b_pitch
          b_rcs = (
              1.0 if pitch_err < -0.05 else (-1.0 if pitch_err > 0.05 else 0.0)
          )
          b_pitch += np.clip(pitch_err * 0.45, -0.55, 0.55) * dt
          b_vx *= 0.92
          b_vy -= (g0 * 1.5) * dt
        elif sep_elapsed <= 18.0 and b_x > 1500.0:
          # 【Phase 2】ブーストバックバーン（水平速度をキャンセルし帰還軌道へ）
          b_pitch = -1.5708
          b_thrust = True
          b_rcs = 0.0
          b_vx = -b_x / max(12.0, (rem_h / 260.0))
          b_vy -= (g0 * 1.35) * dt
        elif rem_h > 3600.0:
          # 【Phase 3】大気圏グライド降下（チャタリングを完全排除し滑らかに減速）
          b_thrust = False
          target_bp = float(np.clip((b_x / 8000.0) * 0.18, -0.22, 0.22))
          b_rcs = 1.0 if abs(target_bp - b_pitch) > 0.02 else 0.0
          b_pitch += (target_bp - b_pitch) * 0.25
          glide_target_vy = -min(340.0, 95.0 + rem_h * 0.0055)
          b_vy += (glide_target_vy - b_vy) * 0.18
          time_to_landing = max(5.0, rem_h / max(10.0, abs(b_vy)))
          b_vx = -b_x / time_to_landing
        else:
          # 【Phase 4】ファイナル・ランディングバーン（高度3.6km以下〜キャッチまで連続比例減速）
          b_thrust = True
          ideal_landing_vy = -max(1.8, np.sqrt(2.0 * 14.5 * rem_h))
          b_vy += (ideal_landing_vy - b_vy) * 0.45
          time_to_catch = max(1.2, rem_h / max(2.0, abs(b_vy)))
          b_vx = -b_x / time_to_catch
          target_bp = float(np.clip((rem_h / 3600.0) * 0.16, 0.0, 0.16))
          b_rcs = -1.0 if abs(target_bp - b_pitch) > 0.015 else 0.0
          b_pitch += (target_bp - b_pitch) * 0.35

        # 座標更新（強制ワープなし）
        b_x = max(0.0, b_x + b_vx * dt)
        b_y = max(TOWER_PHYSICAL_CATCH_Y, b_y + b_vy * dt)

        # タワーキャッチ判定
        if rem_h <= 12.0 and abs(b_x) < 40.0:
          (
              b_caught,
              b_y,
              b_x,
              b_vx,
              b_vy,
              b_pitch,
              b_thrust,
              b_rcs,
          ) = (
              True,
              TOWER_PHYSICAL_CATCH_Y,
              0.0,
              0.0,
              0.0,
              0.0,
              False,
              0.0,
          )

    dir_x, dir_y = float(np.cos(pitch_rad)), float(np.sin(pitch_rad))
    drag_area = (
        (13.0 * s1_spec["cd_mod"] * wing_spec["drag_penalty"])
        if stage == 1
        else (5.2 * s2_spec["cd_mod"])
    )
    drag_force = float(0.5 * rho * (v**2) * fair_spec["cd"] * drag_area)
    drag_x = -drag_force * (vx / v) if v > 0 else 0.0
    drag_y = -drag_force * (vy / v) if v > 0 else 0.0

    g_cur = float(g0 * ((R_earth / (R_earth + alt)) ** 2))
    grav_y = -cur_mass * (g_cur - (vx**2) / (R_earth + alt))

    fx = thrust * dir_x + drag_x - wing_lift_force * dir_y
    fy = thrust * dir_y + drag_y + wing_lift_force * dir_x + grav_y

    cur_spec = s1_spec if stage == 1 else s2_spec
    s1_pct = max(0.0, (fuel_s1_rem / fuel_s1_init) * 100.0)
    s2_pct = max(0.0, (fuel_s2_rem / fuel_s2_init) * 100.0)
    apogee_val = alt_km + (max(0.0, vy) ** 2 / (2.0 * g0 * 1000.0))

    # 💥 0. 推力不足（TWR < 1.02）または失速落下による発射台転倒・激突爆発
    if (alt <= 5.0 and fy <= 0.0) or (t > 2.0 and alt < 150.0 and vy < -3.0):
      fail_reason = (
          f"【推力不足・発射台転倒大爆発】離床推力 (TWR: {twr_init:.2f})"
          " が機体重量に負け、ホールドダウン解放後に機体が傾いて発射台へ倒れ込み大爆発しました。"
      )
      tip_angle_rad = visual_pitch
      for tip_step in range(7):
        t_tip = t + tip_step * dt
        tip_angle_rad += 0.14 * (tip_step + 1) * dt
        history.append({
            "t": float(t_tip),
            "x": float(x + tip_step * 2.5),
            "y": 0.0,
            "alt": 0.0,
            "v": float(tip_step * 3.0),
            "q": 0.0,
            "g": 1.0,
            "stage": int(stage),
            "fairing": fairing_attached,
            "wings": wings_attached,
            "strapon": strapon_attached,
            "exploded": False,
            "thrust": True,
            "pitch": float(min(1.35, tip_angle_rad)),
            "mach": 0.0,
            "event": "FLIGHT",
            "rcs_cmd": 1.0,
            "s1_prop_pct": s1_pct,
            "s2_prop_pct": s2_pct,
            "pitch_deg": float(max(12.0, 90.0 - np.degrees(tip_angle_rad))),
            "apogee_km": 0.0,
            "chamber_p": current_pc,
            "b_x": 0.0,
            "b_y": 0.0,
            "b_active": False,
            "b_pitch": 0.0,
            "b_thrust": False,
            "b_caught": False,
            "b_rcs": 0.0,
            "b_vy": 0.0,
        })
      for rud_step in range(9):
        t_rud = t + (7 + rud_step) * dt
        history.append({
            "t": float(t_rud),
            "x": float(x + 18.0),
            "y": 0.0,
            "alt": 0.0,
            "v": 0.0,
            "q": 0.0,
            "g": 0.0,
            "stage": int(stage),
            "fairing": False,
            "wings": False,
            "strapon": False,
            "exploded": True,
            "thrust": False,
            "pitch": 1.35,
            "mach": 0.0,
            "event": "RUD",
            "rcs_cmd": 0.0,
            "s1_prop_pct": 0.0,
            "s2_prop_pct": 0.0,
            "pitch_deg": 12.0,
            "apogee_km": 0.0,
            "chamber_p": 0.0,
            "b_x": 0.0,
            "b_y": 0.0,
            "b_active": False,
            "b_pitch": 0.0,
            "b_thrust": False,
            "b_caught": False,
            "b_rcs": 0.0,
            "b_vy": 0.0,
        })
      break

    ax, ay = fx / cur_mass, fy / cur_mass
    acc_g = float(
        np.sqrt((thrust * dir_x + drag_x) ** 2 + (thrust * dir_y + drag_y) ** 2)
        / (cur_mass * g0)
    )

    # 💥 多項目RUD判定
    rud_triggered = False
    s1_cyc_spec = PUMP_CYCLES[s1_cycle]
    s2_cyc_spec = PUMP_CYCLES[s2_cycle]
    cur_prop_spec = PROPELLANTS[s1_prop if stage == 1 else s2_prop]

    # 1. 可燃性素材の排気熱引火・焼失爆発
    if cur_spec["mat_id"] in ["pencil", "baguette"] and thrust > 0 and t >= 1.5:
      mat_label = (
          "天然ヒノキ材＆消しゴム"
          if cur_spec["mat_id"] == "pencil"
          else "小麦粉クラスト(パン生地)"
      )
      fail_reason = (
          f"【機体引火・焼失爆発】{mat_label}の胴体が3,200Kのエンジン排気輻射熱と高温ガスで瞬時に引火・炭化し、燃料タンクが爆散しました。"
      )
      rud_triggered = True
    # 2. 消音注水デリュージ不足による発射台音響破壊
    elif (
        stage == 1
        and t >= 1.0
        and alt_km < 0.25
        and (s1_eng_count * 12.0) > (water_flow_rate * 1.35)
    ):
      fail_reason = (
          f"【発射台・音響過圧破壊】エンジン {s1_eng_count}"
          f" 基の猛烈な反射音響波に対し注水デリュージ流量 ({water_flow_rate} t/s)"
          " が不足し、音響振動で底部タンクが粉砕されました。"
      )
      rud_triggered = True
    # 3. CFRP × 極低温水素/核熱の熱衝撃クラック爆発
    elif (
        cur_spec["mat_id"] == "cf"
        and cur_prop_spec["type"] in ["hydro", "nuclear"]
        and t >= 3.0
    ):
      fail_reason = (
          "【極低温・熱衝撃タンク破断】CFRP複合材タンクが極低温水素(20K)/核熱の急激な熱収縮に耐えきれずマイクロクラックが発生、水素漏洩により大爆発しました。"
      )
      rud_triggered = True
    # 4. 第2段の推力不足失速
    elif stage == 2 and alt_km < 160.0 and vy < -25.0:
      fail_reason = (
          "【第2段・推力不足失速RUD】ブースター切り離し後の第2段推力が重量に対して不足し、軌道高度へ到達できず失速落下・大気圏再突入で空中分解しました。"
      )
      rud_triggered = True
    # 5. 動圧限界
    elif q > cur_spec["max_q"]:
      fail_reason = (
          f"【Max-Q 構造圧壊】動圧 {q:.1f} kPa が機体強度限界"
          f" ({cur_spec['max_q']:.1f} kPa)"
          " を超過。外殻板厚を上げるか推力抑制を強めてください。"
      )
      rud_triggered = True
    # 6. 過大迎角
    elif q > 10.0 and (q * abs(angle_of_attack)) > (cur_spec["max_q"] * 1.35):
      fail_reason = (
          f"【空力横曲げ座屈】高動圧領域 ({q:.1f} kPa) での迎角"
          f" ({angle_of_attack}°) が過大なため、機体が横風圧で折損しました。"
      )
      rud_triggered = True
    # 7. 軸方向G
    elif acc_g > cur_spec["max_g"]:
      fail_reason = (
          f"【過G 構造座屈】加速度 {acc_g:.1f} G が機体耐G限界"
          f" ({cur_spec['max_g']:.1f} G)"
          " を超過。最大加速度リミッターを下げてください。"
      )
      rud_triggered = True
    # 8. ポンプ限界
    elif (
        stage == 1
        and thrust > 0
        and s1_pc > s1_cyc_spec["max_pressure_limit"]
        and t > 1.5
    ):
      fail_reason = (
          f"【ターボポンプ爆裂】燃焼室圧力 ({s1_pc} bar) が {s1_cycle}"
          f" の設計耐圧限界 ({s1_cyc_spec['max_pressure_limit']} bar)"
          " を突破しエンジンが爆発しました。"
      )
      rud_triggered = True
    # 9. ノズル剥離
    elif stage == 1 and thrust > 0 and alt_km < 8.0 and s1_eps > 46 and t > 4.0:
      fail_reason = (
          f"【ノズル過膨張・剥離破壊】海面膨張比 (ε={s1_eps})"
          " が大きすぎるため低空大気圧で排気剥離(Flow"
          " Separation)が発生、激しい横振動でノズルが爆散しました。"
      )
      rud_triggered = True
    # 10. フラッター
    elif wings_attached and alt_km < 55.0 and mach > wing_spec["flutter_mach"]:
      fail_reason = (
          f"【超音速フラッター分解】速度 Mach {mach:.2f} が空力翼の限界速度 (Mach"
          f" {wing_spec['flutter_mach']})"
          " を超過し、主翼の共振剥離から機体が空中分解しました。"
      )
      rud_triggered = True
    # 11. 空力加熱・早期分離
    elif alt_km < 65.0 and mach > 4.0:
      stag_temp = 260.0 * (1.0 + 0.2 * (mach**2)) * np.exp(-alt_km / 42.0)
      if not fairing_attached and alt_km < 52.0 and q > 1.2:
        fail_reason = (
            f"【ペイロード空力焼損】高度 {alt_km:.1f} km"
            " でフェアリングを早期分離したため、むき出しの衛星が超音速気流と空力加熱に耐えきれず大破しました。"
        )
        rud_triggered = True
      elif stag_temp > fair_spec["heat_limit"]:
        fail_reason = (
            f"【ノーズコーン熱融解】空力加熱温度 ({stag_temp:.0f} K)"
            f" が先端カウルの耐熱限界 ({fair_spec['heat_limit']} K)"
            " を超え、先端部から融解・爆散しました。"
        )
        rud_triggered = True
    # 12. 推進剤リスク
    elif thrust > 0 and cur_prop_spec["risk"] > 0.0:
      step_fail_prob = (
          cur_prop_spec["risk"] * 0.012 * ((s1_pc / 200.0) ** 1.5)
      )
      if np.random.rand() < step_fail_prob:
        fail_reason = (
            "【推進剤・燃焼不安定爆発】高リスク推進剤の燃焼振動および配管腐食リークが発生し、推進系が連鎖爆発しました。"
        )
        rud_triggered = True

    if rud_triggered:
      for rud_step in range(9):
        t_rud = t + rud_step * dt
        vx *= 0.94
        vy -= g0 * dt * 1.2
        x += vx * dt
        y = max(0.0, y + vy * dt)
        history.append({
            "t": float(t_rud),
            "x": float(x),
            "y": float(y),
            "alt": float(y / 1000.0),
            "v": float(np.sqrt(vx**2 + vy**2)),
            "q": float(q),
            "g": float(acc_g),
            "stage": int(stage),
            "fairing": False,
            "wings": False,
            "strapon": False,
            "exploded": True,
            "thrust": False,
            "pitch": visual_pitch,
            "mach": mach,
            "event": "RUD",
            "rcs_cmd": 0.0,
            "s1_prop_pct": 0.0,
            "s2_prop_pct": 0.0,
            "pitch_deg": pitch_deg,
            "apogee_km": apogee_val,
            "chamber_p": 0.0,
            "b_x": float(b_x),
            "b_y": float(b_y),
            "b_active": b_active,
            "b_pitch": float(b_pitch),
            "b_thrust": False,
            "b_caught": False,
            "b_rcs": 0.0,
            "b_vy": float(b_vy),
        })
      break

    vx, vy = float(vx + ax * dt), float(vy + ay * dt)
    x, y = float(x + vx * dt), float(max(0.0, y + vy * dt))

    is_orbit_achieved = bool(alt_km >= 230.0 and vx >= 7850.0)

    history.append({
        "t": t,
        "x": x,
        "y": y,
        "alt": alt_km,
        "v": v,
        "q": q,
        "g": acc_g,
        "stage": int(stage),
        "fairing": bool(fairing_attached),
        "wings": bool(wings_attached),
        "strapon": bool(strapon_attached),
        "exploded": False,
        "thrust": bool(thrust > 0 and not is_orbit_achieved),
        "pitch": visual_pitch,
        "mach": mach,
        "event": "ORBIT" if is_orbit_achieved else cur_event,
        "rcs_cmd": rcs_cmd,
        "s1_prop_pct": s1_pct,
        "s2_prop_pct": s2_pct,
        "pitch_deg": pitch_deg,
        "apogee_km": apogee_val,
        "chamber_p": current_pc,
        "b_x": float(b_x),
        "b_y": float(b_y),
        "b_active": b_active,
        "b_pitch": float(b_pitch),
        "b_thrust": b_thrust,
        "b_caught": b_caught,
        "b_rcs": float(b_rcs),
        "b_vy": float(b_vy),
    })

    if is_orbit_achieved and (not spacex_return_mode or b_caught):
      for orbit_step in range(40):
        history.append({
            "t": t + (orbit_step + 1) * dt,
            "x": x + vx * (orbit_step + 1) * dt,
            "y": y,
            "alt": alt_km,
            "v": v,
            "q": 0.0,
            "g": 0.0,
            "stage": 2,
            "fairing": False,
            "wings": wings_attached,
            "strapon": False,
            "exploded": False,
            "thrust": False,
            "pitch": 1.5708,
            "mach": mach,
            "event": "ORBIT",
            "rcs_cmd": 0.0,
            "s1_prop_pct": 0.0,
            "s2_prop_pct": s2_pct,
            "pitch_deg": 0.0,
            "apogee_km": alt_km,
            "chamber_p": 0.0,
            "b_x": float(b_x),
            "b_y": float(b_y),
            "b_active": b_active,
            "b_pitch": float(b_pitch),
            "b_thrust": False,
            "b_caught": True,
            "b_rcs": 0.0,
            "b_vy": 0.0,
        })
      break

  if not fail_reason and history[-1]["event"] != "ORBIT":
    fail_reason = (
        f"軌道速度未達。高度: {alt_km:.1f} km, 横速度: {vx:.0f} m/s (目標:"
        " 7,900 m/s)"
    )

  return history, fail_reason


st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

cb1, cb2 = st.columns([3, 1])
with cb1:
  launch_clicked = st.button(
      "🔴 4K LIVE中継：ローンチ・シーケンス開始",
      use_container_width=True,
      type="primary",
  )
with cb2:
  st.caption("※ 設定変更すると発射台上の3Dモデルが即座に反映されます。")

traj_data, error_msg = run_simulation(preview_only=(not launch_clicked))

rocket_visual_cfg = {
    "is_preview": bool(not launch_clicked),
    "s1_mat": s1_spec["mat_id"],
    "s2_mat": s2_spec["mat_id"],
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
    "s1_prop_type": s1_spec["prop_type"],
    "s2_prop_type": s2_spec["prop_type"],
    "s1_cycle_id": s1_spec["cyc_id"],
    "fairing_shape": fair_spec["shape_id"],
    "wing_id": wing_spec["wing_id"],
    "strapon_type": strapon_spec["type"],
    "strapon_count": int(strapon_spec["count"]),
    "water_flow": float(water_flow_rate),
    "ignition_lead": float(ignition_lead_time),
    "sep_thrust": float(sep_thrust_factor),
    "spacex_return": bool(spacex_return_mode),
    "rcs_deadband": float(rcs_deadband),
}

traj_json = json.dumps(
    traj_data,
    default=lambda o: (
        float(o) if isinstance(o, (np.floating, np.integer)) else str(o)
    ),
)
cfg_json = json.dumps(rocket_visual_cfg)
fail_msg_clean = (error_msg or "").replace('"', '\\"').replace("'", "\\'")

# =========================================================================
# 📺 HTML / JS 描画テンプレート
# =========================================================================
html_template = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{box-sizing:border-box;}body,html{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#01040a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;user-select:none;}
#canvas-main{width:100%;height:100%;display:block;position:absolute;top:0;left:0;z-index:1;}
.vignette-overlay{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:5;background:radial-gradient(circle at center,transparent 65%,rgba(1,4,10,0.42) 100%);}
.top-banner{position:absolute;top:0;left:0;width:100%;min-height:42px;background:linear-gradient(180deg,rgba(2,6,16,0.96) 0%,rgba(3,10,24,0.92) 100%);border-bottom:1px solid rgba(56,189,248,0.22);display:flex;align-items:center;justify-content:space-between;padding:4px 14px;z-index:20;flex-wrap:wrap;gap:6px 12px;box-shadow:0 4px 20px rgba(0,0,0,0.7);overflow-x:hidden;}
.banner-group{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
.pip-container{position:absolute;top:48px;right:8px;width:410px;max-width:calc(100vw - 16px);height:235px;border:2px solid rgba(56,189,248,0.95);border-radius:6px;z-index:60;box-shadow:0 14px 45px rgba(0,0,0,0.98);background:#071526;overflow:hidden;cursor:pointer;transition:height 0.25s ease;}
#canvas-pip{width:100%;height:100%;display:block;transition:filter 0.15s ease-out;}
.pip-tag{position:absolute;top:6px;left:12px;font-size:10px;font-weight:800;color:#fff;background:rgba(15,23,42,0.94);padding:3px 8px;border-radius:2px;letter-spacing:1px;font-family:monospace;z-index:65;pointer-events:none;border-left:2px solid #38bdf8;}
.pip-alt{position:absolute;bottom:6px;right:12px;font-size:11px;font-family:monospace;color:#38bdf8;font-weight:700;background:rgba(15,23,42,0.94);padding:2px 8px;border-radius:2px;z-index:65;pointer-events:none;}
.pip-hint{position:absolute;top:6px;right:12px;font-size:9px;font-family:monospace;color:#94a3b8;background:rgba(15,23,42,0.94);padding:3px 6px;border-radius:2px;z-index:65;pointer-events:none;}
.hud-orbit{position:absolute;bottom:86px;left:24px;width:320px;background:#030712;border:1px solid rgba(255,255,255,0.16);border-radius:4px;padding:8px 12px;z-index:50;color:#fff;box-shadow:0 8px 32px rgba(0,0,0,0.85);}
#orbit-canvas{width:296px;height:64px;background:#020617;border-radius:2px;border:1px solid rgba(255,255,255,0.08);display:block;margin-top:4px;}
.hud-telemetry{position:absolute;bottom:0;left:0;width:100%;height:76px;background:#01040a;border-top:1px solid rgba(255,255,255,0.12);padding:8px 24px;display:flex;align-items:center;justify-content:space-between;z-index:20;pointer-events:none;}
.hud-telemetry>*{pointer-events:auto;}
.telemetry-row{display:flex;gap:clamp(14px,2.2vw,28px);align-items:center;flex-wrap:nowrap;overflow-x:auto;}
.telemetry-item{flex-shrink:0;}
.telemetry-label{font-size:9px;color:#94a3b8;letter-spacing:1px;}
.telemetry-val{color:#fff;font-size:clamp(13px,1.6vw,17px);font-weight:800;font-family:'Consolas',monospace;}
.rud-banner{display:none;position:absolute;top:160px;left:50%;transform:translateX(-50%);background:rgba(127,29,29,0.94);border:2px solid #ef4444;border-radius:6px;padding:20px 36px;z-index:75;text-align:center;box-shadow:0 0 70px rgba(239,68,68,0.85);animation:fadeInRUD 0.6s ease-out forwards;}
@keyframes fadeInRUD{from{opacity:0;transform:translate(-50%,-15px);}to{opacity:1;transform:translate(-50%,0);}}
.complete-banner{display:none;position:absolute;top:140px;left:50%;transform:translateX(-50%);background:rgba(6,78,59,0.95);border:2px solid #10b981;border-radius:6px;padding:20px 36px;z-index:70;text-align:center;box-shadow:0 0 70px rgba(16,185,129,0.7);}
</style>
</head>
<body>
<div class="vignette-overlay"></div>
<canvas id="canvas-main"></canvas>
<div id="pip-box" class="pip-container" title="クリックでCAM 02 (地上光学望遠) の表示/非表示を切り替え">
    <canvas id="canvas-pip"></canvas>
    <div id="pip-tag" class="pip-tag">CAM 02: GROUND OPTICAL TRACKER</div>
    <div id="pip-hud-alt" class="pip-alt">BOOSTER: 0.0 km</div>
    <div id="pip-hint" class="pip-hint">[CLICK TO TOGGLE]</div>
</div>
<div class="top-banner" id="top-banner-bar">
    <div class="banner-group">
        <span id="live-indicator" style="display:inline-block;width:8px;height:8px;background:#ef4444;border-radius:50%;box-shadow:0 0 10px #ef4444;flex-shrink:0;"></span>
        <span id="webcast-title" style="color:#ffffff;font-weight:800;font-size:11px;letter-spacing:1.5px;white-space:nowrap;">CAM 01: OPTICAL LONG TELEPHOTO</span>
        <span style="color:rgba(255,255,255,0.2);">|</span>
        <span style="color:#94a3b8;font-family:monospace;font-size:10px;">PITCH: <strong id="hud-pitch" style="color:#f8fafc;">90.0°</strong></span>
        <span style="color:#94a3b8;font-family:monospace;font-size:10px;">PRED APOGEE: <strong id="hud-apogee" style="color:#34d399;">0.0 km</strong></span>
    </div>
    <div class="banner-group" style="font-family:monospace;font-size:10px;">
        <span style="color:#94a3b8;">PROP S1: <strong id="hud-s1-prop" style="color:#38bdf8;">100%</strong></span>
        <span style="color:#94a3b8;">S2: <strong id="hud-s2-prop" style="color:#38bdf8;">100%</strong></span>
        <span style="color:#94a3b8;">Pc: <strong id="hud-pc" style="color:#f59e0b;">0 bar</strong></span>
        <span style="color:#94a3b8;">ATMOS: <strong id="hud-regime" style="color:#f8fafc;">TROPO</strong></span>
        <span style="color:#94a3b8;">ARM: <strong id="hud-arm" style="color:#f59e0b;">STOWED</strong></span>
        <span id="comm-status" style="color:#10b981;font-weight:700;">★ OPTICAL LOCK</span>
    </div>
</div>
<div class="hud-orbit" id="hud-orbit-box">
    <div style="font-size:9px;font-weight:800;color:#94a3b8;letter-spacing:1.2px;display:flex;justify-content:space-between;">
        <span>TRAJECTORY & GROUND TRACK</span>
        <span id="hud-downrange" style="color:#38bdf8;font-family:monospace;">DOWNRANGE: 0.0 km</span>
    </div>
    <canvas id="orbit-canvas" width="296" height="64"></canvas>
    <div id="event-log" style="margin-top:4px;font-family:monospace;font-size:9px;font-weight:800;color:#34d399;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">> [LD] GO FOR TERMINAL COUNTDOWN</div>
    <div id="sub-callout" style="font-family:monospace;font-size:8.5px;color:#93c5fd;margin-top:1px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">> Pad systems pressurized and ready</div>
</div>
<div id="complete-banner" class="complete-banner">
    <div style="color:#6ee7b7;font-size:18px;font-weight:900;letter-spacing:2px;font-family:monospace;">🎉 MISSION COMPLETE 🎉</div>
    <div id="complete-desc" style="color:#ecfdf5;font-size:13px;font-weight:700;margin-top:6px;">FIRST COSMIC VELOCITY (28,400 km/h) ACHIEVED</div>
    <div id="complete-sub" style="color:#a7f3d0;font-size:11px;margin-top:4px;font-family:monospace;">Vehicle safely established in circular orbit. Solar arrays deployed.</div>
</div>
<div id="rud-banner" class="rud-banner">
    <div style="color:#fff;font-size:16px;font-weight:900;letter-spacing:2px;font-family:monospace;">🚨 RAPID UNSCHEDULED DISASSEMBLY (RUD) 🚨</div>
    <div id="rud-desc" style="color:#fecaca;font-size:12px;margin-top:6px;font-weight:600;"></div>
</div>
<div class="hud-telemetry">
    <div>
        <div id="tv-status" style="color:#38bdf8;font-size:9px;font-weight:700;">COUNTDOWN SEQUENCE</div>
        <div id="tv-timer" style="color:#fff;font-size:clamp(20px,2.6vw,26px);font-weight:900;font-family:'Consolas',monospace;">T- 00:10.0</div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;margin:0 10px;">
        <div style="font-size:8px;color:#94a3b8;letter-spacing:1px;margin-bottom:2px;">ENGINE CLUSTER STATUS</div>
        <canvas id="engine-cluster-canvas" width="48" height="48" style="background:rgba(15,23,42,0.6);border-radius:50%;border:1px solid rgba(56,189,248,0.3);"></canvas>
    </div>
    <div class="telemetry-row">
        <div class="telemetry-item"><div class="telemetry-label">HORIZ VELOCITY</div><div class="telemetry-val"><span id="tv-mach">M 0.00</span> <span style="font-size:10px;color:#94a3b8;" id="tv-spd">(0 km/h)</span></div></div>
        <div class="telemetry-item"><div class="telemetry-label">ALTITUDE</div><div class="telemetry-val"><span id="tv-alt">0.0</span> <span style="font-size:10px;color:#94a3b8;">km</span></div></div>
        <div class="telemetry-item"><div class="telemetry-label">DYNAMIC PRESSURE</div><div class="telemetry-val"><span id="tv-q">0.0</span> <span style="font-size:10px;color:#94a3b8;">kPa</span></div></div>
        <div class="telemetry-item"><div class="telemetry-label">AXIAL LOAD</div><div class="telemetry-val"><span id="tv-g">1.0</span> <span style="font-size:10px;color:#94a3b8;">G</span></div></div>
        <div class="telemetry-item"><div class="telemetry-label">STAGE CONFIG</div><div id="tv-stage-badge" style="color:#34d399;font-size:clamp(11px,1.4vw,13px);font-weight:800;font-family:'Consolas',monospace;">PAD READY</div></div>
    </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
window.onerror=function(msg,url,line){const el=document.getElementById('event-log');if(el){el.innerText="🚨 SCRIPT ERROR (L"+line+"): "+msg;el.style.color="#ef4444";}};
window.addEventListener('DOMContentLoaded',()=>{
try{
const simData=__SIM_DATA__;const simCfg=__SIM_CFG__;const failMessage="__FAIL_MSG__";
const canvasMain=document.getElementById('canvas-main'),canvasPip=document.getElementById('canvas-pip');
const orbitCvs=document.getElementById('orbit-canvas'),octx=orbitCvs.getContext('2d');
const engineCvs=document.getElementById('engine-cluster-canvas'),ectx=engineCvs.getContext('2d');
const rudBanner=document.getElementById('rud-banner'),completeBanner=document.getElementById('complete-banner'),rudDesc=document.getElementById('rud-desc');
const eventLog=document.getElementById('event-log'),subCallout=document.getElementById('sub-callout'),pipBox=document.getElementById('pip-box'),topBannerBar=document.getElementById('top-banner-bar');
let isMissionEnded=false,catchPopPlayed=false,pipVisible=true,landingSonicBoomPlayed=false,hotStagingSparkTimer=0.0;
let pipBlurTriggered12k=false,pipBlurTriggeredCatch=false,cloudWakeTriggered=false,rudSequenceStarted=false,rudStartTime=0.0,is13to3CutoffTriggered=false,jsSepTime=0.0;

function updatePipPosition(){if(pipBox&&topBannerBar){const rect=topBannerBar.getBoundingClientRect();pipBox.style.top=Math.round(rect.bottom+4)+'px';}}
updatePipPosition();
function triggerPipAutoFocus(){if(!canvasPip)return;canvasPip.style.filter="blur(2.8px) brightness(1.28) contrast(1.15)";setTimeout(()=>{if(canvasPip)canvasPip.style.filter="blur(0px) brightness(1.0) contrast(1.0)";},320);}
function resizePipRenderer(){if(pipBox&&pipVisible){const w=pipBox.clientWidth||410,h=235;rendererPip.setSize(w,h,false);cameraPip.aspect=w/h;cameraPip.updateProjectionMatrix();}}
window.addEventListener('resize',()=>{updatePipPosition();resizePipRenderer();});

pipBox.addEventListener('click',()=>{
    pipVisible=!pipVisible;canvasPip.style.visibility=pipVisible?'visible':'hidden';
    document.getElementById('pip-tag').style.display=pipVisible?'block':'none';
    document.getElementById('pip-hud-alt').style.display=pipVisible?'block':'none';
    pipBox.style.height=pipVisible?'235px':'32px';
    document.getElementById('pip-hint').innerText=pipVisible?'[CLICK TO HIDE]':'[CLICK TO SHOW]';
    if(pipVisible){resizePipRenderer();rendererPip.render(scene,cameraPip);setTimeout(()=>{resizePipRenderer();rendererPip.render(scene,cameraPip);},260);}
});

function speakCallout(text){if(!window.speechSynthesis)return;try{window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.rate=1.15;u.pitch=0.95;u.lang='en-US';window.speechSynthesis.speak(u);}catch(e){}}

const calloutMilestones=[
    {t:-10.0,main:"> [LD] TERMINAL COUNTDOWN INITIATED",sub:"> Pad systems armed for flight",spoken:"Terminal countdown initiated"},
    {t:-simCfg.ignition_lead,main:"> [PROP] MAIN ENGINE IGNITION SEQUENCE START",sub:"> Deluge system at full pressure",spoken:"Ignition sequence start"},
    {t:0.0,main:"> [LIFTOFF] VEHICLE HAS CLEARED THE LAUNCH PAD",sub:"> Guidance active downrange",spoken:"Liftoff. Tower cleared"},
    {t:45.0,main:"> [AERO] VEHICLE PASSING MACH 1 - SUPERSONIC",sub:"> Transonic buffet optimal",spoken:"Vehicle is supersonic"},
    {t:65.0,main:"> [AERO] MAXIMUM DYNAMIC PRESSURE (MAX-Q)",sub:"> Main engine throttle bucket confirmed",spoken:"Max-Q"},
    {t:130.0,main:"> [PROP] BOOSTER MECO & SEPARATION",sub:"> Pneumatic pushers & pyros fired",spoken:"Booster separation"},
    {t:165.0,main:"> [STAGE] SECOND STAGE VACUUM IGNITION",sub:"> Staging confirmed",spoken:"Staging confirmed"},
    {t:230.0,main:"> [TOWER] CHOPSTICK ARMS EXTENDING FOR CATCH",sub:"> Mechazilla ready for capture",spoken:"Chopstick arms deployed"}
];

let calloutTrackIndex=0;
function updateFlightCallouts(simT){
    while(calloutTrackIndex<calloutMilestones.length&&simT>=calloutMilestones[calloutTrackIndex].t){
        const m=calloutMilestones[calloutTrackIndex];
        if(eventLog)eventLog.innerText=m.main;if(subCallout)subCallout.innerText=m.sub;speakCallout(m.spoken);calloutTrackIndex++;
    }
}

const AudioCtx=window.AudioContext||window.webkitAudioContext;
let actx=null,subRumble=null,shockCrackle=null,gasHiss=null,boosterRumble=null,boosterCrackle=null;
function ensureAudioActive(){
    if(!actx){
        actx=new AudioCtx();const buf=actx.createBuffer(1,actx.sampleRate*4,actx.sampleRate),d=buf.getChannelData(0);
        for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1;
        const rSrc=actx.createBufferSource();rSrc.buffer=buf;rSrc.loop=true;
        const lp=actx.createBiquadFilter();lp.type='lowpass';lp.frequency.value=45;lp.Q.value=5.2;
        subRumble=actx.createGain();subRumble.gain.value=0.0001;rSrc.connect(lp);lp.connect(subRumble);subRumble.connect(actx.destination);rSrc.start(0);
        const cSrc=actx.createBufferSource();cSrc.buffer=buf;cSrc.loop=true;const waveShaper=actx.createWaveShaper();
        const curve=new Float32Array(256);for(let i=0;i<256;i++){const x=(i*2)/256-1;curve[i]=Math.sign(x)*Math.pow(Math.abs(x),0.25);}
        waveShaper.curve=curve;const bp=actx.createBiquadFilter();bp.type='bandpass';bp.frequency.value=290;bp.Q.value=3.0;
        shockCrackle=actx.createGain();shockCrackle.gain.value=0.0001;cSrc.connect(bp);bp.connect(waveShaper);waveShaper.connect(shockCrackle);shockCrackle.connect(actx.destination);cSrc.start(0);
        const hSrc=actx.createBufferSource();hSrc.buffer=buf;hSrc.loop=true;const hp=actx.createBiquadFilter();hp.type='highpass';hp.frequency.value=2200;
        gasHiss=actx.createGain();gasHiss.gain.value=0.0001;hSrc.connect(hp);hp.connect(gasHiss);gasHiss.connect(actx.destination);hSrc.start(0);
        const bSrc=actx.createBufferSource();bSrc.buffer=buf;bSrc.loop=true;const bLp=actx.createBiquadFilter();bLp.type='lowpass';bLp.frequency.value=58;bLp.Q.value=4.8;
        boosterRumble=actx.createGain();boosterRumble.gain.value=0.0001;bSrc.connect(bLp);bLp.connect(boosterRumble);boosterRumble.connect(actx.destination);bSrc.start(0);
        const bcSrc=actx.createBufferSource();bcSrc.buffer=buf;bcSrc.loop=true;const bBp=actx.createBiquadFilter();bBp.type='bandpass';bBp.frequency.value=340;bBp.Q.value=2.5;
        boosterCrackle=actx.createGain();boosterCrackle.gain.value=0.0001;bcSrc.connect(bBp);bBp.connect(waveShaper);waveShaper.connect(boosterCrackle);boosterCrackle.connect(actx.destination);bcSrc.start(0);
    }
    if(actx&&actx.state==='suspended')actx.resume().catch(()=>{});
}
['click','touchstart','mousedown','keydown','pointerdown','mousemove'].forEach(evt=>{
    window.addEventListener(evt,ensureAudioActive,{once:false,passive:true});
    try{if(window.parent&&window.parent!==window)window.parent.addEventListener(evt,ensureAudioActive,{once:false,passive:true});}catch(e){}
});
ensureAudioActive();

function playExplosionDetonationSound(){
    ensureAudioActive();if(!actx)return;const now=actx.currentTime;
    const blastOsc=actx.createOscillator(),blastGain=actx.createGain();
    blastOsc.type='sawtooth';blastOsc.frequency.setValueAtTime(95,now);blastOsc.frequency.exponentialRampToValueAtTime(14,now+1.2);
    blastGain.gain.setValueAtTime(0.95,now);blastGain.gain.exponentialRampToValueAtTime(0.001,now+2.4);
    blastOsc.connect(blastGain);blastGain.connect(actx.destination);blastOsc.start(now);blastOsc.stop(now+2.5);
    const nBuf=actx.createBuffer(1,Math.floor(actx.sampleRate*2.2),actx.sampleRate),ndata=nBuf.getChannelData(0);
    for(let i=0;i<ndata.length;i++)ndata[i]=(Math.random()*2-1)*Math.exp(-i/(actx.sampleRate*0.42));
    const nSrc=actx.createBufferSource();nSrc.buffer=nBuf;const nFilt=actx.createBiquadFilter();nFilt.type='lowpass';nFilt.frequency.setValueAtTime(180,now);
    const nGain=actx.createGain();nGain.gain.setValueAtTime(1.0,now);nSrc.connect(nFilt);nFilt.connect(nGain);nGain.connect(actx.destination);nSrc.start(now);
}
function playLandingDoubleSonicBoom(){
    ensureAudioActive();if(!actx)return;const now=actx.currentTime;
    [0.0,0.12].forEach((offset,idx)=>{
        const boomOsc=actx.createOscillator(),boomGain=actx.createGain();
        boomOsc.type='triangle';boomOsc.frequency.setValueAtTime(idx===0?150:120,now+offset);boomOsc.frequency.exponentialRampToValueAtTime(20,now+offset+0.45);
        boomGain.gain.setValueAtTime(idx===0?0.75:0.55,now+offset);boomGain.gain.exponentialRampToValueAtTime(0.001,now+offset+0.5);
        boomOsc.connect(boomGain);boomGain.connect(actx.destination);boomOsc.start(now+offset);boomOsc.stop(now+offset+0.52);
    });
}
function playHeavySeparationSound(){
    ensureAudioActive();if(!actx)return;const now=actx.currentTime;
    const thudOsc=actx.createOscillator(),thudGain=actx.createGain();
    thudOsc.type='sine';thudOsc.frequency.setValueAtTime(135,now);thudOsc.frequency.exponentialRampToValueAtTime(24,now+0.26);
    thudGain.gain.setValueAtTime(0.48,now);thudGain.gain.exponentialRampToValueAtTime(0.001,now+0.34);
    thudOsc.connect(thudGain);thudGain.connect(actx.destination);thudOsc.start(now);thudOsc.stop(now+0.35);
    [0.0,0.038].forEach((offset,idx)=>{
        const clankBuf=actx.createBuffer(1,Math.floor(actx.sampleRate*0.065),actx.sampleRate),cdata=clankBuf.getChannelData(0);
        for(let i=0;i<cdata.length;i++)cdata[i]=(Math.random()*2-1)*Math.exp(-i/(actx.sampleRate*0.008));
        const clankSrc=actx.createBufferSource();clankSrc.buffer=clankBuf;const bp1=actx.createBiquadFilter();bp1.type='bandpass';
        bp1.frequency.setValueAtTime(idx===0?1180:2650,now+offset);bp1.Q.value=6.5;const clankG=actx.createGain();
        clankG.gain.setValueAtTime(0.28,now+offset);clankG.gain.exponentialRampToValueAtTime(0.01,now+offset+0.06);
        clankSrc.connect(bp1);bp1.connect(clankG);clankG.connect(actx.destination);clankSrc.start(now+offset);
    });
}
function playRcsPuffSound(){
    if(!actx)return;const now=actx.currentTime,dur=0.065,buf=actx.createBuffer(1,Math.floor(actx.sampleRate*dur),actx.sampleRate),data=buf.getChannelData(0);
    for(let i=0;i<data.length;i++)data[i]=(Math.random()*2-1)*Math.exp(-i/(actx.sampleRate*0.018));
    const src=actx.createBufferSource();src.buffer=buf;const bp=actx.createBiquadFilter();bp.type='bandpass';bp.frequency.setValueAtTime(1850,now);bp.Q.value=1.8;
    const g=actx.createGain();g.gain.setValueAtTime(0.045,now);g.gain.exponentialRampToValueAtTime(0.001,now+dur);src.connect(bp);bp.connect(g);g.connect(actx.destination);src.start(now);
}
function playFirecrackerSnapSound(){
    if(!actx)return;const now=actx.currentTime,osc=actx.createOscillator(),gain=actx.createGain();
    osc.type='square';osc.frequency.setValueAtTime(1200,now);osc.frequency.exponentialRampToValueAtTime(80,now+0.035);
    gain.gain.setValueAtTime(0.45,now);gain.gain.exponentialRampToValueAtTime(0.001,now+0.055);osc.connect(gain);gain.connect(actx.destination);osc.start(now);osc.stop(now+0.06);
}

const scene=new THREE.Scene();scene.fog=new THREE.FogExp2(0x4a769e,0.000028);
const initW=window.innerWidth||document.documentElement.clientWidth||1200,initH=window.innerHeight||document.documentElement.clientHeight||980;
const rendererMain=new THREE.WebGLRenderer({canvas:canvasMain,antialias:true,powerPreference:"high-performance"});
rendererMain.setPixelRatio(Math.min(window.devicePixelRatio,1.5));rendererMain.setSize(initW,initH);
rendererMain.toneMapping=THREE.ACESFilmicToneMapping;rendererMain.toneMappingExposure=1.32;rendererMain.shadowMap.enabled=true;rendererMain.shadowMap.type=THREE.PCFSoftShadowMap;

const rendererPip=new THREE.WebGLRenderer({canvas:canvasPip,antialias:true});
rendererPip.setSize(410,235);rendererPip.toneMapping=THREE.ACESFilmicToneMapping;rendererPip.toneMappingExposure=1.40;rendererPip.shadowMap.enabled=true;

const cameraMain=new THREE.PerspectiveCamera(16.0,initW/initH,2.0,95000);
const cameraPip=new THREE.PerspectiveCamera(20.0,410/235,2.0,95000);

const sunLight=new THREE.DirectionalLight(0xffedd5,4.8);sunLight.position.set(1800,2100,1500);sunLight.castShadow=true;sunLight.shadow.mapSize.width=2048;sunLight.shadow.mapSize.height=2048;sunLight.shadow.bias=-0.0003;scene.add(sunLight);
const skyAmbient=new THREE.HemisphereLight(0xdbeafe,0x1e293b,1.65);scene.add(skyAmbient);
const engineBounceLight=new THREE.PointLight(simCfg.flame_hex,0.0,650,1.8);scene.add(engineBounceLight);
const pipTrackingSpot=new THREE.DirectionalLight(0xffffff,2.5);scene.add(pipTrackingSpot);
const towerCatchLight=new THREE.PointLight(simCfg.flame_hex,0.0,95,2.0);towerCatchLight.position.set(-8.5,70.0,0);scene.add(towerCatchLight);

function generateEnvironmentMap(){
    const cvs=document.createElement('canvas');cvs.width=1024;cvs.height=512;const ctx=cvs.getContext('2d'),g=ctx.createLinearGradient(0,0,0,512);
    g.addColorStop(0.0,'#020817');g.addColorStop(0.28,'#153e75');g.addColorStop(0.44,'#568fc7');g.addColorStop(0.49,'#ffedd5');
    g.addColorStop(0.51,'#fed7aa');g.addColorStop(0.54,'#1e3a5f');g.addColorStop(0.75,'#0f2537');g.addColorStop(1.0,'#040d14');
    ctx.fillStyle=g;ctx.fillRect(0,0,1024,512);
    const sunG=ctx.createRadialGradient(720,210,4,720,210,95);sunG.addColorStop(0.0,'rgba(255,255,255,1.0)');sunG.addColorStop(0.3,'rgba(254,240,138,0.85)');sunG.addColorStop(1.0,'rgba(240,240,138,0.0)');
    ctx.fillStyle=sunG;ctx.fillRect(600,100,240,220);const envTex=new THREE.CanvasTexture(cvs);envTex.mapping=THREE.EquirectangularReflectionMapping;return envTex;
}
const proceduralEnvMap=generateEnvironmentMap();scene.environment=proceduralEnvMap;

function createSkyGradientTexture(){
    const cvs=document.createElement('canvas');cvs.width=256;cvs.height=512;const ctx=cvs.getContext('2d'),g=ctx.createLinearGradient(0,0,0,512);
    g.addColorStop(0.0,'#01040d');g.addColorStop(0.38,'#081c38');g.addColorStop(0.70,'#1d4f82');g.addColorStop(0.90,'#6ba3cc');g.addColorStop(0.97,'#dbeafe');g.addColorStop(1.0,'#fef3c7');
    ctx.fillStyle=g;ctx.fillRect(0,0,256,512);return new THREE.CanvasTexture(cvs);
}
const skyDomeGeo=new THREE.SphereGeometry(65000,32,24),skyDomeMat=new THREE.MeshBasicMaterial({map:createSkyGradientTexture(),side:THREE.BackSide,depthWrite:false});
const skyDome=new THREE.Mesh(skyDomeGeo,skyDomeMat);scene.add(skyDome);

const atmoLimbMat=new THREE.MeshBasicMaterial({color:0x38bdf8,transparent:true,opacity:0.0,side:THREE.BackSide,blending:THREE.AdditiveBlending,depthWrite:false});
const atmoLimbMesh=new THREE.Mesh(new THREE.SphereGeometry(58000,32,20),atmoLimbMat);scene.add(atmoLimbMesh);

const starGeo=new THREE.BufferGeometry(),starPos=new Float32Array(2200*3);
for(let i=0;i<6600;i+=3){const rad=54000,u=Math.random(),v=Math.random(),th=u*2*Math.PI,ph=Math.acos(2*v-1);starPos[i]=rad*Math.sin(ph)*Math.cos(th);starPos[i+1]=rad*Math.sin(ph)*Math.sin(th);starPos[i+2]=rad*Math.cos(ph);}
starGeo.setAttribute('position',new THREE.BufferAttribute(starPos,3));
const starMat=new THREE.PointsMaterial({size:3.8,color:0xffffff,transparent:true,opacity:0.15});
const starPoints=new THREE.Points(starGeo,starMat);scene.add(starPoints);

function createTerrainTexture(){
    const cvs=document.createElement('canvas');cvs.width=512;cvs.height=512;const ctx=cvs.getContext('2d');ctx.fillStyle='#1e2920';ctx.fillRect(0,0,512,512);
    for(let i=0;i<1800;i++){ctx.fillStyle=(Math.random()>0.45)?'rgba(42,58,40,0.35)':'rgba(68,64,52,0.28)';const rx=Math.random()*512,ry=Math.random()*512;ctx.fillRect(rx,ry,4+Math.random()*18,4+Math.random()*18);}
    const tex=new THREE.CanvasTexture(cvs);tex.wrapS=THREE.RepeatWrapping;tex.wrapT=THREE.RepeatWrapping;tex.repeat.set(40,40);return tex;
}
function createOceanNormalBump(){
    const cvs=document.createElement('canvas');cvs.width=256;cvs.height=256;const ctx=cvs.getContext('2d');ctx.fillStyle='#808080';ctx.fillRect(0,0,256,256);
    for(let i=0;i<900;i++){ctx.fillStyle=(i%2===0)?'rgba(220,220,220,0.35)':'rgba(30,30,30,0.35)';ctx.beginPath();ctx.ellipse(Math.random()*256,Math.random()*256,12+Math.random()*20,2+Math.random()*3,0.1,0,Math.PI*2);ctx.fill();}
    const tex=new THREE.CanvasTexture(cvs);tex.wrapS=THREE.RepeatWrapping;tex.wrapT=THREE.RepeatWrapping;tex.repeat.set(120,120);return tex;
}
const landscapeGroup=new THREE.Group();scene.add(landscapeGroup);
const coastPlane=new THREE.Mesh(new THREE.PlaneGeometry(35000,65000),new THREE.MeshStandardMaterial({map:createTerrainTexture(),roughness:0.92,metalness:0.05,envMap:proceduralEnvMap}));
coastPlane.rotation.x=-Math.PI/2;coastPlane.position.set(-17500,-2.5,0);coastPlane.receiveShadow=true;landscapeGroup.add(coastPlane);

const oceanBumpTex=createOceanNormalBump();
const oceanMesh=new THREE.Mesh(new THREE.PlaneGeometry(35000,65000),new THREE.MeshStandardMaterial({color:0x092c4c,roughness:0.12,metalness:0.90,bumpMap:oceanBumpTex,bumpScale:0.35,envMap:proceduralEnvMap}));
oceanMesh.rotation.x=-Math.PI/2;oceanMesh.position.set(17500,-8.0,0);oceanMesh.receiveShadow=true;landscapeGroup.add(oceanMesh);

const mountainMat=new THREE.MeshStandardMaterial({color:0x1e2f42,roughness:0.95,metalness:0.05});
for(let mi=0;mi<18;mi++){const mAng=Math.PI*0.55+(mi/18)*Math.PI*0.9,mDist=9500+(mi%3)*1800,mHeight=280+(mi*73%340),mCone=new THREE.Mesh(new THREE.ConeGeometry(900+(mi%4)*350,mHeight,7),mountainMat);mCone.position.set(Math.cos(mAng)*mDist,mHeight*0.45-5.0,Math.sin(mAng)*mDist);mCone.rotation.y=mi*1.1;landscapeGroup.add(mCone);}

const pad=new THREE.Group();scene.add(pad);
const darkSteelMat=new THREE.MeshStandardMaterial({color:0x222a36,metalness:0.85,roughness:0.35,envMap:proceduralEnvMap});
const concreteMat=new THREE.MeshStandardMaterial({color:0x3d4554,roughness:0.95});
const pipeMat=new THREE.MeshStandardMaterial({color:0x64748b,roughness:0.35,metalness:0.85,envMap:proceduralEnvMap});
let chopstickGroup=new THREE.Group(),armLeftPivot=new THREE.Group(),armRightPivot=new THREE.Group(),umbilicalArm=null;
const isStarshipPad=(simCfg.s1_mat==='ss'),isSaturnOrH3=(simCfg.s1_mat==='saturn'||simCfg.s1_mat==='al'),isMissilePad=(simCfg.s1_mat==='military'||simCfg.s1_mat==='cf'),isJokePad=(simCfg.s1_mat==='baguette'||simCfg.s1_mat==='pencil');

if(isStarshipPad){
    const groundPlate=new THREE.Mesh(new THREE.CylinderGeometry(110,125,3.0,32),concreteMat);groundPlate.position.y=0.5;groundPlate.receiveShadow=true;pad.add(groundPlate);
    const olmRing=new THREE.Mesh(new THREE.CylinderGeometry(3.6,4.2,2.2,24),darkSteelMat);olmRing.position.y=4.2;olmRing.castShadow=true;olmRing.receiveShadow=true;pad.add(olmRing);
    const clampMat=new THREE.MeshStandardMaterial({color:0xd97706,metalness:0.85,roughness:0.3});
    for(let i=0;i<20;i++){const ang=(i/20)*Math.PI*2,clamp=new THREE.Mesh(new THREE.BoxGeometry(0.35,0.8,0.4),clampMat);clamp.position.set(Math.cos(ang)*2.4,5.2,Math.sin(ang)*2.4);clamp.rotation.y=-ang;pad.add(clamp);}
    for(let i=0;i<6;i++){const ang=(i/6)*Math.PI*2,leg=new THREE.Mesh(new THREE.CylinderGeometry(0.42,0.52,3.8,12),darkSteelMat);leg.position.set(Math.cos(ang)*3.4,2.1,Math.sin(ang)*3.4);leg.castShadow=true;leg.receiveShadow=true;pad.add(leg);}
    const towerGroup=new THREE.Group();towerGroup.position.set(-11.5,0,0);pad.add(towerGroup);
    const towerMain=new THREE.Mesh(new THREE.BoxGeometry(6.2,145.0,6.2),darkSteelMat);towerMain.position.y=72.5;towerMain.castShadow=true;towerMain.receiveShadow=true;towerGroup.add(towerMain);
    const lightningRod=new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.35,18.0,8),darkSteelMat);lightningRod.position.y=154.0;towerGroup.add(lightningRod);
    umbilicalArm=new THREE.Group();umbilicalArm.position.set(3.1,18.0,0);const uPipe=new THREE.Mesh(new THREE.BoxGeometry(8.5,1.2,1.2),pipeMat);uPipe.position.x=4.2;umbilicalArm.add(uPipe);towerGroup.add(umbilicalArm);
    chopstickGroup.position.set(0,67.5,0);towerGroup.add(chopstickGroup);
    armLeftPivot.position.set(3.1,0,2.2);chopstickGroup.add(armLeftPivot);
    const armLeft=new THREE.Mesh(new THREE.BoxGeometry(16.0,2.2,1.3),darkSteelMat);armLeft.position.set(8.0,0,0);armLeft.castShadow=true;armLeftPivot.add(armLeft);
    armRightPivot.position.set(3.1,0,-2.2);chopstickGroup.add(armRightPivot);
    const armRight=new THREE.Mesh(new THREE.BoxGeometry(16.0,2.2,1.3),darkSteelMat);armRight.position.set(8.0,0,0);armRight.castShadow=true;armRightPivot.add(armRight);
    armLeftPivot.rotation.y=-0.75;armRightPivot.rotation.y=0.75;
}else if(isSaturnOrH3){
    const groundPlate=new THREE.Mesh(new THREE.BoxGeometry(70,8.0,70),concreteMat);groundPlate.position.y=0.5;groundPlate.receiveShadow=true;pad.add(groundPlate);
    const towerGroup=new THREE.Group();towerGroup.position.set(-12.5,0,0);pad.add(towerGroup);
    const redTower=new THREE.Mesh(new THREE.BoxGeometry(7.0,155.0,7.0),new THREE.MeshStandardMaterial({color:0xb91c1c,metalness:0.5,roughness:0.4,envMap:proceduralEnvMap}));
    redTower.position.y=77.5;redTower.castShadow=true;redTower.receiveShadow=true;towerGroup.add(redTower);
}else if(isMissilePad){
    const siloGround=new THREE.Mesh(new THREE.CylinderGeometry(35,40,2.5,16),new THREE.MeshStandardMaterial({color:0x272e25,roughness:0.9}));siloGround.position.y=-0.5;siloGround.receiveShadow=true;pad.add(siloGround);
    const hatchDoor=new THREE.Mesh(new THREE.BoxGeometry(7.5,1.2,7.5),new THREE.MeshStandardMaterial({color:0x3f4f38,metalness:0.6,roughness:0.4,envMap:proceduralEnvMap}));hatchDoor.position.set(-5.5,2.5,0);hatchDoor.rotation.z=0.95;hatchDoor.castShadow=true;pad.add(hatchDoor);
}else if(isJokePad){
    const boardColor=(simCfg.s1_mat==='baguette')?0x9a3412:0x0284c7;
    const jokePlate=new THREE.Mesh(new THREE.BoxGeometry(32,4.0,32),new THREE.MeshStandardMaterial({color:boardColor,roughness:0.7}));jokePlate.position.y=0.5;jokePlate.receiveShadow=true;pad.add(jokePlate);
}

function createSaturnRollPattern(){const cvs=document.createElement('canvas');cvs.width=512;cvs.height=512;const ctx=cvs.getContext('2d');ctx.fillStyle='#f8fafc';ctx.fillRect(0,0,512,512);ctx.fillStyle='#0f172a';ctx.fillRect(0,0,256,128);ctx.fillRect(256,128,256,128);ctx.fillRect(0,256,256,128);ctx.fillRect(256,384,256,128);ctx.fillStyle='#b91c1c';ctx.font='bold 36px sans-serif';ctx.fillText('USA',190,480);const tex=new THREE.CanvasTexture(cvs);tex.wrapS=THREE.RepeatWrapping;tex.wrapT=THREE.RepeatWrapping;return tex;}
function createBaguetteTexture(){const cvs=document.createElement('canvas');cvs.width=512;cvs.height=512;const ctx=cvs.getContext('2d');ctx.fillStyle='#c68a4c';ctx.fillRect(0,0,512,512);ctx.fillStyle='#e8b87d';for(let i=0;i<8;i++){ctx.save();ctx.translate(120+(i%3)*120,40+i*60);ctx.rotate(-0.35);ctx.beginPath();ctx.ellipse(0,0,75,14,0,0,Math.PI*2);ctx.fill();ctx.restore();}const imgData=ctx.getImageData(0,0,512,512);for(let k=0;k<imgData.data.length;k+=4){const noise=(Math.random()-0.5)*22;imgData.data[k]+=noise;imgData.data[k+1]+=noise;imgData.data[k+2]+=noise;}ctx.putImageData(imgData,0,0);return new THREE.CanvasTexture(cvs);}
function createPencilTexture(){const cvs=document.createElement('canvas');cvs.width=512;cvs.height=512;const ctx=cvs.getContext('2d');ctx.fillStyle='#155e3b';ctx.fillRect(0,0,512,512);ctx.fillStyle='#d97706';ctx.font='bold 32px serif';ctx.fillText('★ MITSUBISHI Hi-uni HB ★',60,260);ctx.fillStyle='#ca8a04';ctx.fillRect(0,470,512,42);return new THREE.CanvasTexture(cvs);}
function createHexTileTexture(){const cvs=document.createElement('canvas');cvs.width=256;cvs.height=256;const ctx=cvs.getContext('2d');ctx.fillStyle='#0f1216';ctx.fillRect(0,0,256,256);ctx.strokeStyle='#1e242d';ctx.lineWidth=1.5;for(let x=0;x<256;x+=16){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,256);ctx.stroke();}for(let y=0;y<256;y+=16){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(256,y);ctx.stroke();}return new THREE.CanvasTexture(cvs);}
function createWeldSeamTexture(){const cvs=document.createElement('canvas');cvs.width=512;cvs.height=512;const ctx=cvs.getContext('2d');ctx.fillStyle='#787878';ctx.fillRect(0,0,512,512);for(let y=16;y<512;y+=32){ctx.fillStyle='#a0a0a0';ctx.fillRect(0,y,512,2.5);ctx.fillStyle='#4a4a4a';ctx.fillRect(0,y+2.5,512,2.5);}for(let x=12;x<512;x+=24){ctx.fillStyle='#8e8e8e';ctx.fillRect(x,0,1.5,512);ctx.fillStyle='#525252';ctx.fillRect(x+1.5,0,1.5,512);}const imgData=ctx.getImageData(0,0,512,512);for(let k=0;k<imgData.data.length;k+=4){const n=(Math.random()-0.5)*16;imgData.data[k]+=n;imgData.data[k+1]+=n;imgData.data[k+2]+=n;}ctx.putImageData(imgData,0,0);const tex=new THREE.CanvasTexture(cvs);tex.wrapS=THREE.RepeatWrapping;tex.wrapT=THREE.RepeatWrapping;return tex;}
function createJellyfishTex(){const cvs=document.createElement('canvas');cvs.width=128;cvs.height=256;const ctx=cvs.getContext('2d'),g=ctx.createRadialGradient(64,40,10,64,120,110);g.addColorStop(0.0,'rgba(224,231,255,0.95)');g.addColorStop(0.35,'rgba(168,85,247,0.45)');g.addColorStop(0.75,'rgba(56,189,248,0.20)');g.addColorStop(1.0,'rgba(15,23,42,0.0)');ctx.fillStyle=g;ctx.fillRect(0,0,128,256);return new THREE.CanvasTexture(cvs);}

const saturnRollTex=createSaturnRollPattern(),baguetteTex=createBaguetteTexture(),pencilTex=createPencilTexture(),tileTex=createHexTileTexture(),weldSeamTex=createWeldSeamTexture(),jellyfishTex=createJellyfishTex();

function getRealisticMaterial(matId){
    if(matId==='saturn')return new THREE.MeshStandardMaterial({map:saturnRollTex,roughness:0.35,metalness:0.15,envMap:proceduralEnvMap,bumpMap:weldSeamTex,bumpScale:0.012});
    if(matId==='baguette')return new THREE.MeshStandardMaterial({map:baguetteTex,roughness:0.95,metalness:0.02});
    if(matId==='pencil')return new THREE.MeshStandardMaterial({map:pencilTex,roughness:0.45,metalness:0.25,envMap:proceduralEnvMap});
    if(matId==='ss')return new THREE.MeshStandardMaterial({color:0xf1f5f9,roughness:0.12,metalness:0.96,envMap:proceduralEnvMap,bumpMap:weldSeamTex,bumpScale:0.018,roughnessMap:weldSeamTex});
    if(matId==='al')return new THREE.MeshStandardMaterial({color:0xc2410c,roughness:0.70,metalness:0.15,bumpMap:weldSeamTex,bumpScale:0.010});
    if(matId==='cf')return new THREE.MeshStandardMaterial({color:0x111317,roughness:0.85,metalness:0.08,bumpMap:tileTex,bumpScale:0.025});
    if(matId==='military')return new THREE.MeshStandardMaterial({color:0x3f4f38,roughness:0.65,metalness:0.35,envMap:proceduralEnvMap,bumpMap:weldSeamTex,bumpScale:0.012});
    return new THREE.MeshStandardMaterial({color:0x3f3f46,roughness:0.32,metalness:0.85,envMap:proceduralEnvMap,bumpMap:weldSeamTex,bumpScale:0.012});
}
const blackTileMat=new THREE.MeshStandardMaterial({color:0x111317,roughness:0.88,metalness:0.1,bumpMap:tileTex,bumpScale:0.03});

const rocket=new THREE.Group();rocket.position.y=6.0;scene.add(rocket);
const s1Group=new THREE.Group();scene.add(s1Group);
const s1Len=simCfg.s1_len,s2Len=simCfg.s2_len,s1Mat=getRealisticMaterial(simCfg.s1_mat),s2Mat=getRealisticMaterial(simCfg.s2_mat);
const isPencilRocket=(simCfg.s1_mat==='pencil'),s1Segments=isPencilRocket?6:36;
const s1Body=new THREE.Mesh(new THREE.CylinderGeometry(1.12,1.12,s1Len,s1Segments),s1Mat);
s1Body.position.y=s1Len/2;s1Body.castShadow=true;s1Body.receiveShadow=true;s1Group.add(s1Body);

if(simCfg.s1_mat==='ss'){
    const skirtMesh=new THREE.Mesh(new THREE.CylinderGeometry(1.12,1.24,1.8,36,1,true),new THREE.MeshStandardMaterial({color:0x334155,metalness:0.92,roughness:0.35,envMap:proceduralEnvMap,side:THREE.DoubleSide}));
    skirtMesh.position.y=0.9;s1Group.add(skirtMesh);
    for(let i=0;i<6;i++){const ang=(i/6)*Math.PI*2,strut=new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,1.6,8),darkSteelMat);strut.position.set(Math.cos(ang)*0.85,0.8,Math.sin(ang)*0.85);strut.rotation.z=0.15;s1Group.add(strut);}
}
if(!isPencilRocket&&simCfg.s1_mat!=='baguette'){
    const raceway=new THREE.Mesh(new THREE.BoxGeometry(0.08,s1Len*0.94,0.18),darkSteelMat);raceway.position.set(0,s1Len*0.48,1.13);raceway.castShadow=true;s1Group.add(raceway);
    const copvMat=new THREE.MeshStandardMaterial({color:0x09090b,roughness:0.9,metalness:0.1});
    for(let ci=0;ci<4;ci++){const cang=(ci/4)*Math.PI*2,copv=new THREE.Mesh(new THREE.SphereGeometry(0.24,12,12),copvMat);copv.position.set(Math.cos(cang)*0.75,s1Len-0.6,Math.sin(cang)*0.75);s1Group.add(copv);}
    const feedPipe=new THREE.Mesh(new THREE.CylinderGeometry(0.065,0.065,s1Len*0.92,12),pipeMat);feedPipe.position.set(1.14,s1Len*0.48,0);feedPipe.castShadow=true;s1Group.add(feedPipe);
    const feedPipe2=new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,s1Len*0.85,12),pipeMat);feedPipe2.position.set(-1.14,s1Len*0.45,0);feedPipe2.castShadow=true;s1Group.add(feedPipe2);
    for(let ry=2.5;ry<s1Len;ry+=3.8){const ring=new THREE.Mesh(new THREE.TorusGeometry(1.125,0.015,6,24),darkSteelMat);ring.rotation.x=Math.PI/2;ring.position.y=ry;ring.castShadow=true;s1Group.add(ring);}
}

let frostMesh=null;const fullFrostHeight=s1Len*0.72;
if(simCfg.s1_mat==='ss'||simCfg.s1_mat==='saturn'){
    frostMesh=new THREE.Mesh(new THREE.CylinderGeometry(1.125,1.125,1.0,s1Segments),new THREE.MeshStandardMaterial({color:0xffffff,roughness:0.95,metalness:0.05,transparent:true,opacity:0.75,depthWrite:false}));
    frostMesh.scale.set(1.0,fullFrostHeight,1.0);frostMesh.position.y=s1Len*0.14+fullFrostHeight/2;s1Group.add(frostMesh);
}
let catchPinsMesh=null;
if(simCfg.spacex_return){
    catchPinsMesh=new THREE.Mesh(new THREE.CylinderGeometry(0.26,0.26,3.8,16),new THREE.MeshStandardMaterial({color:0xf59e0b,metalness:0.9,roughness:0.25,envMap:proceduralEnvMap}));
    catchPinsMesh.rotation.x=Math.PI/2;catchPinsMesh.position.set(0,s1Len-2.2,0);catchPinsMesh.castShadow=true;s1Group.add(catchPinsMesh);
}
const plasmaMesh=new THREE.Mesh(new THREE.CylinderGeometry(1.45,0.4,6.0,16,1,true),new THREE.MeshBasicMaterial({color:0xf43f5e,transparent:true,opacity:0.0,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,depthWrite:false,fog:false}));
plasmaMesh.position.y=-2.5;s1Group.add(plasmaMesh);

function createPlumeCoreTex(){
    const cvs=document.createElement('canvas');cvs.width=128;cvs.height=512;const ctx=cvs.getContext('2d');ctx.clearRect(0,0,128,512);
    const gY=ctx.createLinearGradient(0,0,0,512);gY.addColorStop(0.0,'rgba(255,255,255,1.0)');gY.addColorStop(0.08,'rgba(240,249,255,0.98)');gY.addColorStop(0.35,'rgba(147,197,253,0.75)');gY.addColorStop(0.70,'rgba(37,99,235,0.22)');gY.addColorStop(1.0,'rgba(0,0,0,0)');
    ctx.fillStyle=gY;ctx.fillRect(0,0,128,512);ctx.globalCompositeOperation='destination-in';
    const gX=ctx.createLinearGradient(0,0,128,0);gX.addColorStop(0.0,'rgba(0,0,0,0)');gX.addColorStop(0.35,'rgba(0,0,0,1)');gX.addColorStop(0.65,'rgba(0,0,0,1)');gX.addColorStop(1.0,'rgba(0,0,0,0)');
    ctx.fillStyle=gX;ctx.fillRect(0,0,128,512);return new THREE.CanvasTexture(cvs);
}
function createGlowPointTex(){
    const cvs=document.createElement('canvas');cvs.width=64;cvs.height=64;const ctx=cvs.getContext('2d');ctx.clearRect(0,0,64,64);
    const g=ctx.createRadialGradient(32,32,2,32,32,31);g.addColorStop(0.0,'rgba(255,255,255,1.0)');g.addColorStop(0.25,'rgba(147,197,253,0.85)');g.addColorStop(0.65,'rgba(37,99,235,0.2)');g.addColorStop(1.0,'rgba(0,0,0,0)');
    ctx.fillStyle=g;ctx.fillRect(0,0,64,64);return new THREE.CanvasTexture(cvs);
}
function createMachDiamondTex(){
    const cvs=document.createElement('canvas');cvs.width=64;cvs.height=128;const ctx=cvs.getContext('2d');ctx.clearRect(0,0,64,128);
    const g=ctx.createRadialGradient(32,64,2,32,64,55);g.addColorStop(0.0,'rgba(255,255,255,1.0)');g.addColorStop(0.25,'rgba(186,230,253,0.92)');g.addColorStop(0.65,'rgba(59,130,246,0.3)');g.addColorStop(1.0,'rgba(0,0,0,0)');
    ctx.fillStyle=g;ctx.beginPath();ctx.moveTo(32,4);ctx.lineTo(58,64);ctx.lineTo(32,124);ctx.lineTo(6,64);ctx.closePath();ctx.fill();return new THREE.CanvasTexture(cvs);
}
const plumeCoreTex=createPlumeCoreTex(),glowPointTex=createGlowPointTex(),machDiamondTex=createMachDiamondTex();
const s1NozzleTips=[],s2NozzleTips=[],boosterNozzleTips=[];
const s1InconelNozzleMat=new THREE.MeshStandardMaterial({color:0x1f242d,metalness:0.95,roughness:0.25,emissive:new THREE.Color(0xff4500),emissiveIntensity:0.0,side:THREE.DoubleSide,envMap:proceduralEnvMap});
const s2InconelNozzleMat=s1InconelNozzleMat.clone();
const s1EngineGimbalGroup=new THREE.Group();s1Group.add(s1EngineGimbalGroup);
const machConeGeo=new THREE.ConeGeometry(0.35,1.6,12,1,true);machConeGeo.rotateX(Math.PI);
const machConeMat=new THREE.MeshBasicMaterial({map:machDiamondTex,color:0xffffff,transparent:true,opacity:0.95,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false});

function buildFullDetailedEngineCluster(parent,count,basePosY,epsScale,tipArray,flameHex,nozzleMaterial){
    const group=new THREE.Group();group.position.y=basePosY;const bellH=1.2*epsScale,exitRadius=0.22*Math.pow(epsScale,0.65)*1.65;
    const nozzleGeo=new THREE.CylinderGeometry(0.11,exitRadius,bellH,16,1,true);nozzleGeo.translate(0,-bellH/2,0);
    const throatGeo=new THREE.SphereGeometry(0.12,8,8),throatMat=new THREE.MeshBasicMaterial({color:0xffffff,fog:false});
    const plumeLen=22.0,outerConeGeo=new THREE.CylinderGeometry(exitRadius*0.95,exitRadius*0.18,plumeLen,16,1,true);outerConeGeo.translate(0,-plumeLen/2,0);
    const outerConeMat=new THREE.MeshBasicMaterial({map:plumeCoreTex,color:flameHex,transparent:true,opacity:0.85,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false});
    const innerCoreGeo=new THREE.CylinderGeometry(exitRadius*0.45,exitRadius*0.05,plumeLen*0.75,12,1,true);innerCoreGeo.translate(0,-(plumeLen*0.75)/2,0);
    const innerCoreMat=new THREE.MeshBasicMaterial({map:plumeCoreTex,color:0xffffff,transparent:true,opacity:0.95,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false});
    const glowMat=new THREE.SpriteMaterial({map:glowPointTex,color:flameHex,blending:THREE.AdditiveBlending,depthWrite:false,fog:false});
    const enginePositions=[];
    if(count===33){
        for(let i=0;i<3;i++)enginePositions.push({x:Math.cos(i/3*Math.PI*2)*0.22,z:Math.sin(i/3*Math.PI*2)*0.22,isCenter:true,ring:0});
        for(let i=0;i<10;i++)enginePositions.push({x:Math.cos(i/10*Math.PI*2)*0.54,z:Math.sin(i/10*Math.PI*2)*0.54,isCenter:false,ring:1});
        for(let i=0;i<20;i++)enginePositions.push({x:Math.cos(i/20*Math.PI*2)*0.88,z:Math.sin(i/20*Math.PI*2)*0.88,isCenter:false,ring:2});
    }else if(count===1){enginePositions.push({x:0,z:0,isCenter:true,ring:0});}
    else{for(let i=0;i<count;i++)enginePositions.push({x:Math.cos(i/count*Math.PI*2)*0.68,z:Math.sin(i/count*Math.PI*2)*0.68,isCenter:(i<3),ring:1});}
    for(let pos of enginePositions){
        const engUnit=new THREE.Group();engUnit.position.set(pos.x,0,pos.z);
        const nMesh=new THREE.Mesh(nozzleGeo,nozzleMaterial);nMesh.castShadow=true;engUnit.add(nMesh);
        const throatMesh=new THREE.Mesh(throatGeo,throatMat);throatMesh.position.y=-0.05;engUnit.add(throatMesh);
        const tipObj=new THREE.Object3D();tipObj.position.set(0,-bellH*0.86,0);
        const glowSp=new THREE.Sprite(glowMat);glowSp.scale.set(exitRadius*1.5,exitRadius*1.5,1.0);glowSp.position.y=-0.25;glowSp.visible=false;tipObj.add(glowSp);
        const outerM=new THREE.Mesh(outerConeGeo,outerConeMat),innerM=new THREE.Mesh(innerCoreGeo,innerCoreMat);
        const plumeSubGroup=new THREE.Group();plumeSubGroup.add(outerM);plumeSubGroup.add(innerM);plumeSubGroup.visible=false;tipObj.add(plumeSubGroup);
        const diamonds=[];
        for(let k=1;k<=5;k++){
            const dCone=new THREE.Mesh(machConeGeo,machConeMat);dCone.position.y=-k*2.8;dCone.scale.set(exitRadius*1.8,1.0,exitRadius*1.8);dCone.visible=false;tipObj.add(dCone);diamonds.push(dCone);
        }
        engUnit.add(tipObj);tipArray.push({node:tipObj,isCenter:pos.isCenter,ring:pos.ring,glow:glowSp,plumeGroup:plumeSubGroup,diamonds:diamonds,firing:false,exitR:exitRadius,outerMat:outerConeMat,innerMat:innerCoreMat});
        group.add(engUnit);
    }
    parent.add(group);
}
const s1EpsScale=0.72+(simCfg.s1_eps/70.0)*0.65;
buildFullDetailedEngineCluster(s1EngineGimbalGroup,simCfg.s1_eng,0.0,s1EpsScale,s1NozzleTips,simCfg.flame_hex,s1InconelNozzleMat);

const mainCombinedPlumeMat=new THREE.MeshBasicMaterial({map:plumeCoreTex,color:simCfg.flame_hex,transparent:true,opacity:0.45,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false});
const mainCombinedPlumeGeo=new THREE.CylinderGeometry(0.85,2.8,38.0,20,1,true);mainCombinedPlumeGeo.translate(0,-19.0,0);
const mcpCone=new THREE.Mesh(mainCombinedPlumeGeo,mainCombinedPlumeMat);
const mainCombinedGroup=new THREE.Group();mainCombinedGroup.position.y=-0.85;mainCombinedGroup.add(mcpCone);mainCombinedGroup.visible=false;s1EngineGimbalGroup.add(mainCombinedGroup);

const spaceJellyGeo=new THREE.CylinderGeometry(0.8,14.0,48.0,24,1,true);spaceJellyGeo.translate(0,-24.0,0);
const spaceJellyMat=new THREE.MeshBasicMaterial({map:jellyfishTex,transparent:true,opacity:0.0,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,depthWrite:false,fog:false});
const spaceJellyMesh=new THREE.Mesh(spaceJellyGeo,spaceJellyMat);spaceJellyMesh.position.y=-2.0;rocket.add(spaceJellyMesh);

const underglowMat=new THREE.SpriteMaterial({map:glowPointTex,color:simCfg.flame_hex,blending:THREE.AdditiveBlending,depthWrite:false,opacity:0,fog:false});
const underglowSp=new THREE.Sprite(underglowMat);underglowSp.scale.set(95.0,95.0,1.0);scene.add(underglowSp);

const flareMat=new THREE.SpriteMaterial({map:glowPointTex,color:simCfg.flame_hex,blending:THREE.AdditiveBlending,depthWrite:false,opacity:0,fog:false});
const engineHaloGlow=new THREE.Sprite(flareMat);engineHaloGlow.scale.set(5.5,5.5,1.0);scene.add(engineHaloGlow);

const shockRingGeo=new THREE.RingGeometry(0.5,2.5,48);shockRingGeo.rotateX(-Math.PI/2);
const shockRingMat=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0.0,side:THREE.DoubleSide,depthWrite:false,fog:false});
const shockRingMesh=new THREE.Mesh(shockRingGeo,shockRingMat);shockRingMesh.position.set(0,3.0,0);scene.add(shockRingMesh);
let shockwaveFired=false;

const vaporMat=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0.0,side:THREE.DoubleSide,depthWrite:false,fog:false});
const vaporCone1=new THREE.Mesh(new THREE.ConeGeometry(2.6,4.2,32,1,true),vaporMat);vaporCone1.position.set(0,s1Len+s2Len+1.2,0);rocket.add(vaporCone1);
const vaporCone2=new THREE.Mesh(new THREE.ConeGeometry(3.1,4.8,32,1,true),vaporMat);vaporCone2.position.set(0,s1Len-0.5,0);s1Group.add(vaporCone2);

const wingsGroup=new THREE.Group();s1Group.add(wingsGroup);
const gridFinMat=darkSteelMat.clone(),aoaRad=(simCfg.aoa*Math.PI)/180.0;
if(simCfg.wing_id==='grid'){
    for(let i=0;i<4;i++){const ang=(i/4)*Math.PI*2+Math.PI/4,gfFrame=new THREE.Group();gfFrame.position.set(Math.cos(ang)*1.22,s1Len-1.1,Math.sin(ang)*1.22);gfFrame.rotation.y=-ang;gfFrame.rotation.z=aoaRad;const gridBox=new THREE.Mesh(new THREE.BoxGeometry(1.05,0.14,1.25),gridFinMat);gridBox.position.x=0.62;gridBox.castShadow=true;gfFrame.add(gridBox);wingsGroup.add(gfFrame);}
}else if(simCfg.wing_id==='starship_flap'){
    for(let side of [-1,1]){const flap=new THREE.Mesh(new THREE.BoxGeometry(1.6,4.2,0.12),darkSteelMat);flap.position.set(side*1.7,2.8,0);flap.rotation.z=side*0.15;flap.rotation.x=aoaRad;flap.castShadow=true;wingsGroup.add(flap);}
}else if(simCfg.wing_id==='missile_fin'){
    for(let i=0;i<4;i++){const ang=(i/4)*Math.PI*2,fin=new THREE.Mesh(new THREE.BoxGeometry(0.8,1.4,0.08),darkSteelMat);fin.position.set(Math.cos(ang)*1.4,1.6,Math.sin(ang)*1.4);fin.rotation.y=-ang;fin.castShadow=true;wingsGroup.add(fin);}
}else if(simCfg.wing_id==='delta_wing'){
    for(let side of [-1,1]){const s=new THREE.Shape();s.moveTo(0,0);s.lineTo(side*4.8,-1.8);s.lineTo(side*4.2,-6.5);s.lineTo(0,-5.2);const dm=new THREE.Mesh(new THREE.ShapeGeometry(s),s1Mat);dm.position.set(0,s1Len*0.45,0);dm.castShadow=true;wingsGroup.add(dm);}
}

const boosterUnits=[];
if(simCfg.strapon_count>0&&simCfg.strapon_type!=='none'){
    const isSRB=(simCfg.strapon_type==='srb'),isSoyuz=(simCfg.strapon_type==='soyuz'),bMat=isSRB?new THREE.MeshStandardMaterial({color:0xffffff,roughness:0.4}):s1Mat;
    for(let i=0;i<simCfg.strapon_count;i++){
        const ang=(i/simCfg.strapon_count)*Math.PI*2,distR=isSoyuz?2.3:2.15,bUnit=new THREE.Group();bUnit.position.set(Math.cos(ang)*distR,0,Math.sin(ang)*distR);
        const bLen=s1Len*(isSoyuz?0.75:0.84),topR=isSoyuz?0.42:0.68,botR=isSoyuz?0.78:0.68;
        const bBody=new THREE.Mesh(new THREE.CylinderGeometry(topR,botR,bLen,24),bMat);bBody.position.y=bLen/2;bBody.castShadow=true;bUnit.add(bBody);
        const bNose=new THREE.Mesh(new THREE.ConeGeometry(topR,2.2,24),bMat);bNose.position.y=bLen+1.1;bNose.castShadow=true;bUnit.add(bNose);
        const localTips=[];buildFullDetailedEngineCluster(bUnit,1,0,0.9,localTips,simCfg.flame_hex,s1InconelNozzleMat);localTips.forEach(t=>boosterNozzleTips.push(t));
        s1Group.add(bUnit);boosterUnits.push({mesh:bUnit,angle:ang,distR:distR,detached:false,tips:localTips,sepAge:0.0});
    }
}

const interStage=new THREE.Group();interStage.position.y=s1Len;s1Group.add(interStage);
const interStageMat=darkSteelMat.clone();
const interTruss=new THREE.Mesh(new THREE.CylinderGeometry(1.12,1.12,2.2,24,4,true),interStageMat);interTruss.position.y=1.1;interTruss.castShadow=true;interStage.add(interTruss);
const domeTop=new THREE.Mesh(new THREE.SphereGeometry(1.11,24,12,0,Math.PI*2,0,Math.PI/2),new THREE.MeshStandardMaterial({color:0xe2e8f0,metalness:0.95,roughness:0.15,envMap:proceduralEnvMap}));
domeTop.position.y=0.2;interStage.add(domeTop);

const flameDeflectorRingGeo=new THREE.RingGeometry(1.12,3.8,32);flameDeflectorRingGeo.rotateX(-Math.PI/2);
const flameDeflectorRingMat=new THREE.MeshBasicMaterial({color:simCfg.s2_flame_hex,transparent:true,opacity:0.0,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,depthWrite:false});
const flameDeflectorMesh=new THREE.Mesh(flameDeflectorRingGeo,flameDeflectorRingMat);flameDeflectorMesh.position.y=1.1;interStage.add(flameDeflectorMesh);

const s2Group=new THREE.Group();s2Group.position.y=s1Len+2.2;rocket.add(s2Group);
const s2Body=new THREE.Mesh(new THREE.CylinderGeometry(1.12,1.12,s2Len,s1Segments),s2Mat);s2Body.position.y=s2Len/2;s2Body.castShadow=true;s2Body.receiveShadow=true;s2Group.add(s2Body);
if(simCfg.s2_mat==='ss'){
    const heatShield=new THREE.Mesh(new THREE.CylinderGeometry(1.128,1.128,s2Len,24,1,true,0,Math.PI),blackTileMat);heatShield.position.y=s2Len/2;heatShield.castShadow=true;s2Group.add(heatShield);
    for(let side of [-1,1]){const hingeCover=new THREE.Mesh(new THREE.CylinderGeometry(0.14,0.14,0.6,12),darkSteelMat);hingeCover.position.set(side*1.15,0.6,0);s2Group.add(hingeCover);}
}
const s2EpsScale=0.95+(simCfg.s2_eps/280.0)*0.95;
buildFullDetailedEngineCluster(s2Group,simCfg.s2_eng,0.0,s2EpsScale,s2NozzleTips,simCfg.s2_flame_hex,s2InconelNozzleMat);

const payloadGroup=new THREE.Group();payloadGroup.position.y=s2Len+1.8;s2Group.add(payloadGroup);
const satBus=new THREE.Mesh(new THREE.CylinderGeometry(0.65,0.65,2.4,16),new THREE.MeshStandardMaterial({color:0xf59e0b,metalness:0.95,roughness:0.2,envMap:proceduralEnvMap}));
satBus.castShadow=true;payloadGroup.add(satBus);
const solarWingMat=new THREE.MeshStandardMaterial({color:0x0284c7,metalness:0.9,roughness:0.1,envMap:proceduralEnvMap});
const solarL=new THREE.Mesh(new THREE.BoxGeometry(3.5,0.8,0.05),solarWingMat);solarL.position.set(-2.4,0,0);solarL.scale.set(0.01,1,1);payloadGroup.add(solarL);
const solarR=new THREE.Mesh(new THREE.BoxGeometry(3.5,0.8,0.05),solarWingMat);solarR.position.set(2.4,0,0);solarR.scale.set(0.01,1,1);payloadGroup.add(solarR);

const fairingHalves=[];let abortTowerUnit=null;
if(simCfg.fairing_shape==='abort_tower'){
    abortTowerUnit=new THREE.Group();abortTowerUnit.position.y=s2Len;
    const cap=new THREE.Mesh(new THREE.ConeGeometry(1.14,2.8,24),s2Mat);cap.position.y=1.4;cap.castShadow=true;abortTowerUnit.add(cap);
    const spike=new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.14,3.8,12),darkSteelMat);spike.position.y=4.2;spike.castShadow=true;abortTowerUnit.add(spike);s2Group.add(abortTowerUnit);
}else if(simCfg.fairing_shape==='pencil_tip'){
    const wood=new THREE.Mesh(new THREE.ConeGeometry(1.12,3.8,6),new THREE.MeshStandardMaterial({color:0xd4a373,roughness:0.9}));wood.position.y=s2Len+1.9;wood.castShadow=true;s2Group.add(wood);
    const lead=new THREE.Mesh(new THREE.ConeGeometry(0.24,1.0,6),new THREE.MeshStandardMaterial({color:0x1a1a1a,roughness:0.4}));lead.position.y=s2Len+3.8;lead.castShadow=true;s2Group.add(lead);
}else{
    const ogivePts=[],noseH=(simCfg.fairing_shape==='icbm_warhead')?3.8:5.8;
    for(let i=0;i<=16;i++){const t=i/16;ogivePts.push(new THREE.Vector2(Math.max(0.01,1.12*Math.pow(1.0-Math.pow(t,1.65),0.72)),t*noseH));}
    for(let side of [-1,1]){
        const halfMesh=new THREE.Mesh(new THREE.LatheGeometry(ogivePts,16,(side===1)?0:Math.PI,Math.PI),s2Mat);halfMesh.position.y=s2Len;halfMesh.castShadow=true;s2Group.add(halfMesh);
        if(simCfg.fairing_shape==='starship_crew'&&side===1){
            const blackHalf=new THREE.Mesh(new THREE.LatheGeometry(ogivePts,16,0,Math.PI),blackTileMat);blackHalf.scale.set(1.006,1.0,1.006);blackHalf.castShadow=true;halfMesh.add(blackHalf);
        }
        fairingHalves.push({mesh:halfMesh,side:side,detached:false,vx:0,vy:0,rotZ:0,rotX:0});
    }
}

const rcsNozzles=[],rcsConeGeo=new THREE.CylinderGeometry(0.03,0.52,4.2,12,1,true);rcsConeGeo.translate(0,-2.1,0);rcsConeGeo.rotateZ(Math.PI/2);
const rcs8Dirs=[{id:"+X",dx:1,dy:0,dz:0,rotY:0},{id:"-X",dx:-1,dy:0,dz:0,rotY:Math.PI},{id:"+Z",dx:0,dy:0,dz:1,rotY:-Math.PI/2},{id:"-Z",dx:0,dy:0,dz:-1,rotY:Math.PI/2}];
function addFullRcsCluster(parent,yPos,isS1){
    for(let d of rcs8Dirs){
        const mount=new THREE.Mesh(new THREE.BoxGeometry(0.16,0.24,0.16),darkSteelMat);mount.position.set(d.dx*1.13,yPos,d.dz*1.13);
        const jetMat=new THREE.MeshBasicMaterial({map:plumeCoreTex,color:0xe0f2fe,transparent:true,opacity:0.0,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false});
        const jetCone=new THREE.Mesh(rcsConeGeo,jetMat);jetCone.rotation.y=d.rotY;mount.add(jetCone);parent.add(mount);
        rcsNozzles.push({mount:mount,jetCone:jetCone,jetMat:jetMat,dir:d,isS1:isS1,timer:0.0});
    }
}
addFullRcsCluster(s1Group,s1Len-0.85,true);addFullRcsCluster(s2Group,s2Len-0.75,false);

function createCloudTex(){
    const c=document.createElement('canvas');c.width=128;c.height=128;const ctx=c.getContext('2d');
    const puffs=[{x:64,y:64,r:58,a:0.95},{x:46,y:54,r:42,a:0.75},{x:82,y:58,r:40,a:0.75},{x:58,y:80,r:44,a:0.70},{x:74,y:46,r:36,a:0.65}];
    puffs.forEach(pf=>{const g=ctx.createRadialGradient(pf.x,pf.y,2,pf.x,pf.y,pf.r);g.addColorStop(0,`rgba(255,255,255,${pf.a})`);g.addColorStop(0.45,`rgba(241,245,249,${pf.a*0.65})`);g.addColorStop(0.8,`rgba(203,213,225,${pf.a*0.25})`);g.addColorStop(1,'rgba(180,200,220,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(pf.x,pf.y,pf.r,0,Math.PI*2);ctx.fill();});
    return new THREE.CanvasTexture(c);
}
function createSparkTex(){
    const c=document.createElement('canvas');c.width=32;c.height=32;const g=c.getContext('2d').createRadialGradient(16,16,1,16,16,15);
    g.addColorStop(0,'rgba(255,255,255,1)');g.addColorStop(0.4,'rgba(255,220,120,0.95)');g.addColorStop(1,'rgba(255,40,0,0)');c.getContext('2d').fillStyle=g;c.getContext('2d').fillRect(0,0,32,32);return new THREE.CanvasTexture(c);
}
const cloudTex=createCloudTex(),sparkTex=createSparkTex();
const cloudDeck=new THREE.Group();scene.add(cloudDeck);const cloudSprites=[];
for(let ci=0;ci<95;ci++){
    const cMat=new THREE.SpriteMaterial({map:cloudTex,color:0xdbeafe,transparent:true,opacity:0.22,depthWrite:false});const csp=new THREE.Sprite(cMat);
    let cx=(Math.random()-0.5)*4200.0,cz=(Math.random()-0.5)*4200.0;
    if(Math.hypot(cx,cz)<450.0){cx+=(cx>=0?450:-450);cz+=(cz>=0?450:-450);}
    const cy=135.0+(Math.random()-0.5)*35.0;csp.position.set(cx,cy,cz);const csc=95.0+Math.random()*130.0;csp.scale.set(csc*1.6,csc,1);cloudDeck.add(csp);cloudSprites.push(csp);
}

const pool=[];for(let i=0;i<800;i++){const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:cloudTex,transparent:true,opacity:0,depthWrite:false,fog:false}));sp.visible=false;scene.add(sp);pool.push({sp,active:false,vx:0,vy:0,vz:0,age:0,maxAge:1,s0:1,s1:5,o:0.8,drag:0.98,buoyancy:0.0,rotSpeed:0.0,lit:false});}
let pIdx=0;
function emitParticle(x,y,z,vx,vy,vz,s0,s1,life,opacity,hexColor=0xf8fafc,drag=0.985,buoyancy=0.015,litByFlame=false){
    const p=pool[pIdx];pIdx=(pIdx+1)%pool.length;p.active=true;p.sp.visible=true;p.sp.position.set(x,Math.max(2.2,y),z);p.vx=vx;p.vy=vy;p.vz=vz;p.age=0;p.maxAge=life;p.s0=s0;p.s1=s1;p.o=opacity;p.drag=drag;p.buoyancy=buoyancy;p.lit=litByFlame;p.rotSpeed=(Math.random()-0.5)*0.04;p.sp.material.rotation=Math.random()*Math.PI*2;p.sp.material.color.setHex(hexColor);
}

const sparks=[];for(let i=0;i<200;i++){const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:sparkTex,transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false,fog:false}));sp.visible=false;scene.add(sp);sparks.push({sp,active:false,vx:0,vy:0,vz:0,age:0,maxAge:1});}
let sIdx=0;
function emitSpark(x,y,z,vx,vy,vz,hexCol){
    const s=sparks[sIdx];sIdx=(sIdx+1)%sparks.length;s.active=true;s.sp.visible=true;s.sp.position.set(x,Math.max(2.5,y),z);s.vx=vx;s.vy=vy;s.vz=vz;s.age=0;s.maxAge=14;s.sp.material.color.setHex(hexCol);
}

const rudDebris=[],debrisGeo=new THREE.BoxGeometry(0.8,0.8,0.8);
for(let i=0;i<25;i++){const dMesh=new THREE.Mesh(debrisGeo,darkSteelMat);dMesh.visible=false;scene.add(dMesh);rudDebris.push({mesh:dMesh,active:false,vx:0,vy:0,vz:0,rx:0,ry:0,rz:0});}

const iceShards=[];for(let i=0;i<100;i++){const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:cloudTex,color:0xffffff,transparent:true,opacity:0,depthWrite:false,fog:false}));sp.visible=false;scene.add(sp);iceShards.push({sp,active:false,vx:0,vy:0,vz:0,age:0,maxAge:1});}
let iceIdx=0;
function emitIceShard(x,y,z,vx,vy,vz){
    const ic=iceShards[iceIdx];iceIdx=(iceIdx+1)%iceShards.length;ic.active=true;ic.sp.visible=true;ic.sp.position.set(x,y,z);ic.vx=vx;ic.vy=vy;ic.vz=vz;ic.age=0;ic.maxAge=35;ic.sp.scale.set(0.45,0.45,1);
}

function drawPrecisionOrbitMap(curAltKm,curDRangeKm,exploded,isOrbit){
    if(!orbitCvs||!octx)return;octx.fillStyle='#020617';octx.fillRect(0,0,296,64);octx.strokeStyle='#1e293b';octx.lineWidth=1.5;octx.beginPath();octx.moveTo(10,52);octx.lineTo(286,52);octx.stroke();
    const curPx=20+Math.min(256,Math.max(0,(curDRangeKm/1400.0)*256)),curPy=52-Math.min(46,Math.max(0,(curAltKm/250.0)*42));
    octx.beginPath();octx.moveTo(20,52);octx.quadraticCurveTo(20+(curPx-20)*0.35,52,curPx,curPy);octx.strokeStyle=exploded?'#ef4444':(isOrbit?'#34d399':'#38bdf8');octx.lineWidth=2.0;octx.stroke();
    octx.fillStyle=exploded?'#dc2626':(isOrbit?'#10b981':'#38bdf8');octx.beginPath();octx.arc(curPx,curPy,3.5,0,Math.PI*2);octx.fill();
}

function drawEngineClusterGraphic(stage,isThrust,isExploded,bThrust,bCaught){
    if(!engineCvs||!ectx)return;ectx.clearRect(0,0,48,48);const cx=24,cy=24;
    if(stage===1&&!stage1Detached){
        const active=isThrust&&!isExploded;
        for(let i=0;i<20;i++){const ang=(i/20)*Math.PI*2;ectx.beginPath();ectx.arc(cx+Math.cos(ang)*19,cy+Math.sin(ang)*19,1.4,0,Math.PI*2);ectx.fillStyle=active?'#38bdf8':'#334155';ectx.fill();}
        for(let i=0;i<10;i++){const ang=(i/10)*Math.PI*2;ectx.beginPath();ectx.arc(cx+Math.cos(ang)*11.5,cy+Math.sin(ang)*11.5,1.5,0,Math.PI*2);ectx.fillStyle=active?'#60a5fa':'#334155';ectx.fill();}
        for(let i=0;i<3;i++){const ang=(i/3)*Math.PI*2;ectx.beginPath();ectx.arc(cx+Math.cos(ang)*4.8,cy+Math.sin(ang)*4.8,1.8,0,Math.PI*2);ectx.fillStyle=active?'#ffffff':'#334155';ectx.fill();}
    }else if(stage1Detached&&bThrust&&!bCaught){
        for(let i=0;i<3;i++){const ang=(i/3)*Math.PI*2;ectx.beginPath();ectx.arc(cx+Math.cos(ang)*5,cy+Math.sin(ang)*5,2.2,0,Math.PI*2);ectx.fillStyle='#ffffff';ectx.fill();}
    }else if(stage===2){
        for(let i=0;i<6;i++){const ang=(i/6)*Math.PI*2,r=(i%2===0)?14:7;ectx.beginPath();ectx.arc(cx+Math.cos(ang)*r,cy+Math.sin(ang)*r,2.5,0,Math.PI*2);ectx.fillStyle=isThrust?'#38bdf8':'#334155';ectx.fill();}
    }
}

const tStart=performance.now();
let boosterDetached=false,stage1Detached=false,fairingDetached=false,camShake=0.0,abortTowerDetached=false;
let prevRcsCmd=0.0,prevBoosterRcs=0.0,counterPulseTimer=0.0,counterDirSign=0.0;
const tempV=new THREE.Vector3(),activeFocusWorld=new THREE.Vector3(),smoothCamTarget=new THREE.Vector3(0,6.0,0);
const baseFlameColor=new THREE.Color(simCfg.flame_hex),seaLevelFlameColor=new THREE.Color(0xffedd5),raptorGreenColor=new THREE.Color(0x10b981),curDynamicFlameColor=new THREE.Color(),steamWhiteColor=new THREE.Color(0xf8fafc);
let catchStartTime=0.0;

function animate(now){
    if(isMissionEnded)return;requestAnimationFrame(animate);
    const elapsedSec=(now-tStart)/1000.0,simT=simCfg.is_preview?-10.0:(-10.0+elapsedSec);
    if(!simCfg.is_preview)updateFlightCallouts(simT);
    let idx=0;while(idx<simData.length-1&&simData[idx+1].t<=simT)idx++;
    const nIdx=Math.min(idx+1,simData.length-1),p0=simData[idx],p1=simData[nIdx];
    const a=(p1.t>p0.t)?Math.max(0,Math.min(1,(simT-p0.t)/(p1.t-p0.t))):0;
    const rx=(p0.x+(p1.x-p0.x)*a)*0.1,ry=(p0.y+(p1.y-p0.y)*a)*0.1,alt=p0.alt+(p1.alt-p0.alt)*a,vel=p0.v+(p1.v-p0.v)*a,q=p0.q+(p1.q-p0.q)*a,pitch=p0.pitch+(p1.pitch-p0.pitch)*a,mach=p0.mach+(p1.mach-p0.mach)*a,accG=p0.g+(p1.g-p0.g)*a,rcsCmd=p0.rcs_cmd+(p1.rcs_cmd-p0.rcs_cmd)*a;
    const s1PropVal=p0.s1_prop_pct+(p1.s1_prop_pct-p0.s1_prop_pct)*a,s2PropVal=p0.s2_prop_pct+(p1.s2_prop_pct-p0.s2_prop_pct)*a,pitchDegVal=p0.pitch_deg+(p1.pitch_deg-p0.pitch_deg)*a,apogeeVal=p0.apogee_km+(p1.apogee_km-p0.apogee_km)*a,pcVal=p0.chamber_p+(p1.chamber_p-p0.chamber_p)*a;
    const bX=p0.b_x+(p1.b_x-p0.b_x)*a,bY=p0.b_y+(p1.b_y-p0.b_y)*a,bPitch=p0.b_pitch+(p1.b_pitch-p0.b_pitch)*a,bRcsCmd=(p0.b_rcs!==undefined)?(p0.b_rcs+((p1.b_rcs||0)-p0.b_rcs)*a):0.0,bVyVal=(p0.b_vy!==undefined)?(p0.b_vy+((p1.b_vy||0)-p0.b_vy)*a):0.0;

    rocket.position.set(rx,ry+6.0,0);rocket.rotation.z=-pitch;rocket.updateMatrixWorld(true);
    oceanBumpTex.offset.x=(now*0.00004)%1.0;oceanBumpTex.offset.y=(now*0.00002)%1.0;

    if(umbilicalArm){
        if(simT>0.0){
            umbilicalArm.rotation.y=THREE.MathUtils.lerp(umbilicalArm.rotation.y,-1.2,0.08);
            if(simT<1.5&&Math.random()<0.4)emitParticle(-8.4,24.0,0,-0.6,0.2,0,0.2,1.2,12,0.5,0xffffff,0.95,0.01);
        }else{umbilicalArm.rotation.y=0.0;}
    }
    const targetGimbalAngle=(p0.stage===1&&!stage1Detached&&alt>0.5&&alt<60.0)?THREE.MathUtils.clamp((pitch-0.0)*0.045,-0.06,0.06):(stage1Detached&&p0.b_thrust?THREE.MathUtils.clamp(bPitch*0.25,-0.08,0.08):0.0);
    s1EngineGimbalGroup.rotation.z=THREE.MathUtils.lerp(s1EngineGimbalGroup.rotation.z,targetGimbalAngle,0.15);

    if(frostMesh){
        const propPct=(p0.stage===1?s1PropVal:0.0)/100.0,curFrostH=Math.max(0.1,fullFrostHeight*propPct);
        frostMesh.scale.y=curFrostH;frostMesh.position.y=s1Len*0.14+curFrostH/2;frostMesh.material.opacity=Math.max(0.0,(0.75*propPct)-(alt/45.0)*0.4);
    }
    const spaceFactor=Math.min(1.0,Math.max(0.0,(alt-12.0)/70.0));
    cloudSprites.forEach(csp=>{const cDist=cameraMain.position.distanceTo(csp.position);csp.material.opacity=THREE.MathUtils.clamp((cDist-120.0)/250.0,0.0,0.22);});
    const ux=Math.sin(pitch),uy=Math.cos(pitch),perpX=Math.cos(pitch),perpY=-Math.sin(pitch);

    if(alt>=1.2&&alt<=2.2&&!cloudWakeTriggered&&!simCfg.is_preview){
        cloudWakeTriggered=true;
        for(let i=0;i<16;i++){const ang=(i/16)*Math.PI*2;emitParticle(rx+Math.cos(ang)*3.5,ry+6.0,Math.sin(ang)*3.5,Math.cos(ang)*0.8,1.8+Math.random()*1.5,Math.sin(ang)*0.8,2.5,18.0,65,0.45,0xffffff,0.96,0.02,false);}
    }
    if(mach>=0.95&&mach<=1.18&&alt<18.0&&!simCfg.is_preview&&!p0.exploded){
        const vAlpha=Math.sin((mach-0.95)/0.23*Math.PI)*0.78;vaporMat.opacity=vAlpha;const jiggle=1.0+(Math.random()-0.5)*0.06;
        vaporCone1.scale.set(jiggle,1.0,jiggle);vaporCone2.scale.set(jiggle*1.08,1.0,jiggle*1.08);
    }else{vaporMat.opacity=0.0;}

    if(!simCfg.is_preview&&!p0.exploded){
        if(simT>0&&simT<12.0&&Math.random()<0.65){
            for(let k=0;k<2;k++){const h=Math.random()*s1Len,aAngle=Math.random()*Math.PI*2;emitIceShard(rx+Math.cos(aAngle)*1.18,ry+6.0+h,Math.sin(aAngle)*1.18,(Math.random()-0.5)*0.3,-0.6-Math.random()*0.5,(Math.random()-0.5)*0.3);}
        }else if(alt>=28.0&&alt<=85.0&&Math.random()<0.35){
            for(let k=0;k<2;k++){const aAngle=Math.random()*Math.PI*2;emitIceShard(rx+Math.cos(aAngle)*1.15,ry+6.0+(p0.stage===1?s1Len*0.6:s1Len+s2Len*0.5),Math.sin(aAngle)*1.15,-ux*2.5+(Math.random()-0.5)*0.8,-uy*2.5+(Math.random()-0.5)*0.8,(Math.random()-0.5)*0.8);}
        }
    }

    if(!p0.strapon&&!boosterDetached&&boosterUnits.length>0&&!simCfg.is_preview){
        boosterDetached=true;playHeavySeparationSound();camShake=0.18;
        for(let b of boosterUnits){b.detached=true;b.sepAge=0.0;b.tips.forEach(t=>{t.glow.visible=false;t.plumeGroup.visible=false;t.diamonds.forEach(d=>d.visible=false);});}
    }
    if(boosterDetached){
        for(let b of boosterUnits){
            b.sepAge+=0.016;const slowOut=Math.min(6.5,0.45*Math.pow(b.sepAge,1.35)),slowBack=0.35*Math.pow(b.sepAge,2.2),slowTilt=Math.min(0.65,0.08*Math.pow(b.sepAge,1.4));
            const outX=Math.cos(b.angle),outZ=Math.sin(b.angle);
            b.mesh.position.set(outX*(b.distR+slowOut),-slowBack,outZ*(b.distR+slowOut));b.mesh.rotation.z=-outX*slowTilt;b.mesh.rotation.x=outZ*slowTilt;
            if(b.sepAge<2.5&&Math.random()<0.6){b.mesh.getWorldPosition(tempV);emitParticle(tempV.x,tempV.y+s1Len*0.75,tempV.z,outX*0.5,0.15,outZ*0.5,0.2,1.4,14,0.55,0xffffff,0.94,0.0);}
        }
    }

    const isSeparated=(p0.stage===2||p0.b_active);
    if(isSeparated&&!stage1Detached&&!simCfg.is_preview){
        stage1Detached=true;hotStagingSparkTimer=2.6;jsSepTime=simT;playHeavySeparationSound();camShake=0.45;rendererMain.toneMappingExposure=2.3;mainCombinedGroup.visible=false;spaceJellyMesh.visible=false;
        if(abortTowerUnit&&!abortTowerDetached){abortTowerDetached=true;scene.attach(abortTowerUnit);}
        s1Group.localToWorld(tempV.set(0,s1Len,0));
        for(let i=0;i<36;i++){const ang=(i/36)*Math.PI*2;emitParticle(tempV.x+Math.cos(ang)*1.2,tempV.y,tempV.z+Math.sin(ang)*1.2,Math.cos(ang)*3.5,(Math.random()-0.5)*0.5,Math.sin(ang)*3.5,1.2,10.5,42,0.88,simCfg.s2_flame_hex,0.92,0.0);}
        if(s1Body&&s1Body.material){s1Body.material.roughness=0.42;s1Body.material.color.setRGB(0.72,0.74,0.78);}
    }
    if(abortTowerDetached&&abortTowerUnit){abortTowerUnit.position.x+=perpX*0.8;abortTowerUnit.position.y+=1.8;}

    if(hotStagingSparkTimer>0){
        hotStagingSparkTimer-=0.016;flameDeflectorRingMat.opacity=Math.min(0.85,hotStagingSparkTimer*0.35);flameDeflectorMesh.scale.set(1.0+(2.6-hotStagingSparkTimer)*0.5,1.0,1.0+(2.6-hotStagingSparkTimer)*0.5);interStageMat.emissive=new THREE.Color(0xf59e0b);interStageMat.emissiveIntensity=hotStagingSparkTimer*0.65;
        s1Group.localToWorld(tempV.set(0,s1Len,0));
        for(let k=0;k<5;k++){const hAngle=Math.random()*Math.PI*2,blastSpeed=2.5+Math.random()*2.2;emitSpark(tempV.x,tempV.y,tempV.z,Math.cos(hAngle)*blastSpeed,(Math.random()-0.5)*0.4,Math.sin(hAngle)*blastSpeed,0xfde047);}
    }else{flameDeflectorRingMat.opacity=0.0;interStageMat.emissiveIntensity=0.0;}

    const bY_scaled=(bY*0.1)+6.0;

    if(simCfg.spacex_return&&isStarshipPad){
        if(p0.b_caught){
            if(catchStartTime===0.0)catchStartTime=simT;const catchAge=simT-catchStartTime,damperDip=Math.sin(Math.min(Math.PI,catchAge*4.5))*1.5;
            chopstickGroup.position.y=67.5-damperDip;armLeftPivot.rotation.y=THREE.MathUtils.lerp(armLeftPivot.rotation.y,0.08,0.25);armRightPivot.rotation.y=THREE.MathUtils.lerp(armRightPivot.rotation.y,-0.08,0.25);
            document.getElementById('hud-arm').innerText="CATCH LOCKED (PIN SECURED)";document.getElementById('hud-arm').style.color="#10b981";
            if(catchAge<0.8&&Math.random()<0.7){emitParticle(-8.5,68.0,1.5,0.4,0.6,0.4,0.2,1.8,20,0.6,0xffffff,0.95,0.01);emitParticle(-8.5,68.0,-1.5,0.4,0.6,-0.4,0.2,1.8,20,0.6,0xffffff,0.95,0.01);}
        }else if(stage1Detached&&bY<=1500){
            chopstickGroup.position.y=67.5;armLeftPivot.rotation.y=THREE.MathUtils.lerp(armLeftPivot.rotation.y,0.05,0.12);armRightPivot.rotation.y=THREE.MathUtils.lerp(armRightPivot.rotation.y,-0.05,0.12);
            document.getElementById('hud-arm').innerText="CLOSING ARMS";document.getElementById('hud-arm').style.color="#38bdf8";
        }else if(stage1Detached&&bY<=4500){
            chopstickGroup.position.y=67.5;armLeftPivot.rotation.y=THREE.MathUtils.lerp(armLeftPivot.rotation.y,-0.16,0.08);armRightPivot.rotation.y=THREE.MathUtils.lerp(armRightPivot.rotation.y,0.16,0.08);
            document.getElementById('hud-arm').innerText="DEPLOYED (WIDE READY)";document.getElementById('hud-arm').style.color="#34d399";
        }else{
            chopstickGroup.position.y=67.5;armLeftPivot.rotation.y=THREE.MathUtils.lerp(armLeftPivot.rotation.y,-0.75,0.05);armRightPivot.rotation.y=THREE.MathUtils.lerp(armRightPivot.rotation.y,0.75,0.05);
            document.getElementById('hud-arm').innerText="STOWED CLEAR";document.getElementById('hud-arm').style.color="#f59e0b";
        }
    }

    if(stage1Detached&&bY>20000&&bY<65000&&p0.mach>2.5){
        const plasmaOp=Math.min(0.75,(p0.mach-2.5)*0.35);plasmaMesh.material.opacity=plasmaOp;plasmaMesh.rotation.y+=0.12;gridFinMat.emissive=new THREE.Color(0xff3300);gridFinMat.emissiveIntensity=plasmaOp*1.5;
        if(Math.random()<0.45){s1Group.localToWorld(tempV.set(0,s1Len-1.1,0));for(let gi=0;gi<2;gi++){const gfAngle=Math.random()*Math.PI*2;emitParticle(tempV.x+Math.cos(gfAngle)*1.3,tempV.y,tempV.z+Math.sin(gfAngle)*1.3,(Math.random()-0.5)*0.5,3.5+Math.random()*2.0,(Math.random()-0.5)*0.5,0.4,3.5,20,0.45,0xd946ef,0.94,0.0,false);}}
    }else{plasmaMesh.material.opacity=0.0;gridFinMat.emissiveIntensity=0.0;}

    if(stage1Detached){
        s1Group.visible=true;
        if(p0.b_caught){
            const catchAge=simT-catchStartTime,dampedSway=Math.sin(catchAge*6.5)*Math.exp(-catchAge*1.4)*0.06;
            s1Group.position.set(bX*0.1+dampedSway*2.5,bY_scaled,0);s1Group.rotation.set(0,0,-bPitch+dampedSway);
            if(catchAge<0.65&&catchPinsMesh){
                catchPinsMesh.getWorldPosition(tempV);
                for(let k=0;k<4;k++){emitSpark(tempV.x+(Math.random()-0.5)*1.8,tempV.y,tempV.z+(Math.random()-0.5)*1.8,(Math.random()-0.5)*3.5,1.2+Math.random()*2.0,(Math.random()-0.5)*3.5,0xf59e0b);emitParticle(tempV.x,tempV.y,tempV.z,(Math.random()-0.5)*0.8,0.4+Math.random()*0.5,(Math.random()-0.5)*0.8,0.4,2.5,25,0.4,0xffffff,0.94,0.02,false);}
            }
        }else{
            s1Group.position.set(bX*0.1,bY_scaled,0);s1Group.rotation.set(0,0,-bPitch);
        }
        s1Group.updateMatrixWorld(true);

        if(p0.b_thrust&&!landingSonicBoomPlayed&&bY<=3600){playLandingDoubleSonicBoom();landingSonicBoomPlayed=true;camShake=0.55;}
        if(actx&&boosterRumble&&boosterCrackle){
            if(p0.b_thrust&&!p0.b_caught&&bY<=3600){const is13Engines=(bY>1200);boosterRumble.gain.setTargetAtTime(is13Engines?1.4:0.95,actx.currentTime,0.08);boosterCrackle.gain.setTargetAtTime(is13Engines?1.1:0.65,actx.currentTime,0.08);}
            else{boosterRumble.gain.setTargetAtTime(0.0001,actx.currentTime,0.12);boosterCrackle.gain.setTargetAtTime(0.0001,actx.currentTime,0.12);}
        }

        if(p0.b_caught){
            if(!catchPopPlayed){
                playFirecrackerSnapSound();catchPopPlayed=true;camShake=0.45;s1Group.localToWorld(tempV.set(0,0,0));
                for(let i=0;i<28;i++){const ang=Math.random()*Math.PI*2,spd=1.2+Math.random()*2.8;emitParticle(tempV.x+Math.cos(ang)*1.5,tempV.y-1.0,tempV.z+Math.sin(ang)*1.5,Math.cos(ang)*spd,-0.5+Math.random()*1.8,Math.sin(ang)*spd,2.5,16.0,55,0.75,0xf8fafc,0.94,0.03,false);}
            }
            s1NozzleTips.forEach(t=>{t.glow.visible=false;t.plumeGroup.visible=false;t.diamonds.forEach(d=>d.visible=false);});
            mainCombinedGroup.visible=false;towerCatchLight.intensity=0.0;
            document.getElementById('tv-stage-badge').innerText="TOWER CATCH SUCCESS";document.getElementById('tv-stage-badge').style.color="#38bdf8";
            if(simT-catchStartTime<4.5&&Math.random()<0.75){s1Group.localToWorld(tempV.set(0,0,0));emitParticle(tempV.x+(Math.random()-0.5)*2.0,tempV.y-0.5,tempV.z+(Math.random()-0.5)*2.0,(Math.random()-0.5)*0.8,0.6+Math.random()*0.8,(Math.random()-0.5)*0.8,1.2,8.5,45,0.50,0xe2e8f0,0.96,0.025,true);}
        }else if(p0.b_thrust){
            mainCombinedGroup.visible=false;const isThreeOnly=(bY<=1200);
            towerCatchLight.intensity=(bY<=2500)?(8.5*(1.0-bY/2500.0)):0.0;
            if(isThreeOnly&&!is13to3CutoffTriggered){
                is13to3CutoffTriggered=true;
                s1NozzleTips.forEach((t,i)=>{if(!t.isCenter&&i<13){t.node.getWorldPosition(tempV);for(let k=0;k<4;k++)emitParticle(tempV.x,tempV.y,tempV.z,(Math.random()-0.5)*1.2,-1.0-Math.random(),(Math.random()-0.5)*1.2,0.8,4.5,30,0.65,0xfde047,0.95,0.01,true);}});
            }
            const isBoostback=(bY>28000);
            s1NozzleTips.forEach((t,i)=>{
                const active=isThreeOnly?t.isCenter:(i<13);t.glow.visible=active;t.plumeGroup.visible=active;
                const fLen=(isBoostback?1.4:0.68)+Math.random()*0.18;t.plumeGroup.scale.set(isBoostback?1.6:0.85,fLen,isBoostback?1.6:0.85);
                t.diamonds.forEach((d,k)=>{d.visible=active;d.position.y=-(k+1)*2.6*fLen;d.scale.set(t.exitR*(isBoostback?2.2:1.25),1.0,t.exitR*(isBoostback?2.2:1.25));});
            });
            if(bY<=2200.0){
                const groundRatio=Math.max(0.25,1.0-Math.max(0.0,bY-400.0)/1800.0),blastCount=Math.ceil(12*groundRatio);s1Group.localToWorld(tempV.set(0,0,0));
                for(let i=0;i<blastCount;i++){
                    const ang=Math.random()*Math.PI*2,spd=(2.5+Math.random()*4.5)*groundRatio,pType=Math.random(),col=(pType<0.35)?0xf59e0b:((pType<0.65)?0xfef08a:0xe2e8f0);
                    emitParticle(tempV.x+Math.cos(ang)*1.8,Math.max(3.0,tempV.y-4.0-Math.random()*10.0),tempV.z+Math.sin(ang)*1.8,Math.cos(ang)*spd*0.7,-1.2+Math.random()*2.2,Math.sin(ang)*spd*0.7,3.2,22.0*groundRatio+6.0,48,0.82,col,0.92,0.035,(pType<0.65));
                    if(bY<=1400.0&&i%2===0)emitParticle((bX*0.1)+Math.cos(ang)*3.5,3.5+Math.random()*2.5,Math.sin(ang)*3.5,Math.cos(ang)*spd*1.3,0.35+Math.random()*0.65,Math.sin(ang)*spd*1.3,4.5,30.0*groundRatio+10.0,58,0.85,0xcbd5e1,0.90,0.04,false);
                }
            }
        }else{
            s1NozzleTips.forEach(t=>{t.glow.visible=false;t.plumeGroup.visible=false;t.diamonds.forEach(d=>d.visible=false);});
            mainCombinedGroup.visible=false;towerCatchLight.intensity=0.0;
        }
    }else{
        s1Group.visible=!p0.exploded;s1Group.position.set(rx,ry+6.0,0);s1Group.rotation.z=-pitch;s1Group.updateMatrixWorld(true);
    }

    if(!p0.fairing&&!fairingDetached&&fairingHalves.length>0&&!simCfg.is_preview){
        fairingDetached=true;playHeavySeparationSound();
        for(let fh of fairingHalves){fh.detached=true;scene.attach(fh.mesh);fh.vx=perpX*fh.side*0.32;fh.vy=-0.18;fh.rotZ=-fh.side*0.018;fh.rotX=0.012;}
    }
    if(fairingDetached){
        for(let fh of fairingHalves){fh.mesh.position.x+=fh.vx;fh.mesh.position.y+=fh.vy;fh.vy-=0.018;fh.mesh.rotation.z+=fh.rotZ;fh.mesh.rotation.x+=fh.rotX;}
    }

    const isEngineFiring=(p0.thrust&&!p0.exploded&&!simCfg.is_preview);
    const s1TargetEmissive=(p0.stage===1&&isEngineFiring)?1.25:(p0.b_thrust&&!p0.b_caught?1.1:0.0);
    s1InconelNozzleMat.emissiveIntensity=THREE.MathUtils.lerp(s1InconelNozzleMat.emissiveIntensity,s1TargetEmissive,(p0.stage===1&&isEngineFiring)?0.06:0.018);
    const s2TargetEmissive=(p0.stage===2&&isEngineFiring)?(alt>80.0?1.85:1.35):0.0;
    s2InconelNozzleMat.emissive=new THREE.Color(alt>80.0?0xff2200:0xff4500);s2InconelNozzleMat.emissiveIntensity=THREE.MathUtils.lerp(s2InconelNozzleMat.emissiveIntensity,s2TargetEmissive,(p0.stage===2&&isEngineFiring)?0.08:0.015);

    if(isEngineFiring){
        const activeTips=(p0.stage===1)?s1NozzleTips:s2NozzleTips,inactiveTips=(p0.stage===1)?s2NozzleTips:(stage1Detached?[]:s1NozzleTips);
        const igniteElapsed=simT-(-simCfg.ignition_lead);
        if(igniteElapsed>=0&&igniteElapsed<0.42&&simCfg.s1_mat==='ss'){curDynamicFlameColor.copy(raptorGreenColor).lerp(baseFlameColor,igniteElapsed/0.42);}
        else{const colorShiftFactor=Math.min(1.0,alt/42.0);curDynamicFlameColor.copy(seaLevelFlameColor).lerp(baseFlameColor,colorShiftFactor);}
        const curFlameHexVal=curDynamicFlameColor.getHex();
        inactiveTips.forEach(t=>{t.glow.visible=false;t.plumeGroup.visible=false;t.diamonds.forEach(d=>d.visible=false);});
        if(!p0.strapon){boosterNozzleTips.forEach(t=>{t.glow.visible=false;t.plumeGroup.visible=false;t.diamonds.forEach(d=>d.visible=false);});}
        else{boosterNozzleTips.forEach(t=>{t.glow.visible=true;t.plumeGroup.visible=true;const bp=0.92+Math.random()*0.15;t.plumeGroup.scale.set(0.95,bp,0.95);t.diamonds.forEach((d,k)=>{d.visible=true;d.position.y=-(k+1)*2.6*bp;});});}

        if(p0.stage===1&&alt<35.0&&!stage1Detached){
            mainCombinedGroup.visible=true;mainCombinedPlumeMat.color.copy(curDynamicFlameColor);
            const pulse=0.94+Math.random()*0.12,atmExpansion=1.0+Math.min(0.20,Math.max(0.0,alt-5.0)/45.0);
            mainCombinedGroup.scale.set(atmExpansion,pulse,atmExpansion);mainCombinedPlumeMat.opacity=Math.max(0.35,0.65-(alt/60.0)*0.3);
        }else{mainCombinedGroup.visible=false;}

        if(alt>=38.0&&alt<=115.0&&p0.stage===1){
            spaceJellyMesh.visible=true;const jellyProgress=Math.sin(((alt-38.0)/77.0)*Math.PI);spaceJellyMat.opacity=jellyProgress*0.42;const jScale=1.0+jellyProgress*1.8;spaceJellyMesh.scale.set(jScale,1.0+jellyProgress*0.5,jScale);
        }else{spaceJellyMesh.visible=false;}

        const shockSpacingFactor=1.0+Math.min(1.8,alt/28.0);
        for(let tObj of activeTips){
            let isLit=true;if(simT<0.0){if(tObj.ring===1&&igniteElapsed<0.25)isLit=false;if(tObj.ring===2&&igniteElapsed<0.55)isLit=false;}
            tObj.glow.visible=isLit;tObj.plumeGroup.visible=isLit;if(tObj.outerMat)tObj.outerMat.color.copy(curDynamicFlameColor);
            const fPulse=0.92+Math.random()*0.16;tObj.plumeGroup.scale.set(1.0,fPulse*0.85,1.0);
            if(p0.stage===2&&alt>80.0){if(tObj.outerMat)tObj.outerMat.opacity=0.40;if(tObj.innerMat)tObj.innerMat.opacity=0.30;}
            else{if(tObj.outerMat)tObj.outerMat.opacity=0.85;if(tObj.innerMat)tObj.innerMat.opacity=0.95;}
            tObj.diamonds.forEach((d,k)=>{d.visible=(isLit&&alt<70.0);d.position.y=-(k+1)*2.8*fPulse*shockSpacingFactor;const diskW=tObj.exitR*(1.6-k*0.12)*Math.sqrt(shockSpacingFactor);d.scale.set(diskW,1.0,diskW);});
            if(simCfg.s1_cycle_id==="gg"&&p0.stage===1&&Math.random()<0.35){tObj.node.getWorldPosition(tempV);emitParticle(tempV.x+0.8,tempV.y-0.5,tempV.z,(Math.random()-0.5)*0.3,-1.8-Math.random(),(Math.random()-0.5)*0.3,0.4,3.2,28,0.50,0x18181b,0.96,0.01,false);}
            if(Math.random()<(alt>35.0?0.28:0.05)){
                tObj.node.getWorldPosition(tempV);const spread=(Math.random()-0.5)*2.0,isSpaceJelly=(alt>38.0),pLife=isSpaceJelly?42:22,pEndSize=isSpaceJelly?11.5:4.5,pAlpha=isSpaceJelly?0.20:0.12;
                emitParticle(tempV.x-ux*18.0,tempV.y-uy*18.0,tempV.z-5.0+spread,-ux*(3.2+Math.random()*2.0)+perpX*spread*0.35,-uy*(3.2+Math.random()*2.0)+perpY*spread*0.35,(Math.random()-0.5)*0.8,1.0,pEndSize,pLife,pAlpha,curFlameHexVal,0.98,0.0,false);
            }
        }
        rocket.localToWorld(tempV.set(0,(p0.stage===1?-2.2:s1Len+0.5),0));
        engineHaloGlow.position.copy(tempV);engineHaloGlow.material.opacity=THREE.MathUtils.lerp(engineHaloGlow.material.opacity,0.28+Math.random()*0.06,0.2);
        underglowSp.position.set(tempV.x-ux*10.0,tempV.y-uy*10.0,tempV.z);underglowSp.material.opacity=Math.max(0.0,(1.0-alt/25.0)*0.28);
        engineBounceLight.intensity=Math.max(0.0,8.5-alt*0.35);engineBounceLight.position.set(rx,ry+3.0,5.0);
        rendererMain.toneMappingExposure=THREE.MathUtils.lerp(rendererMain.toneMappingExposure,1.18,0.08);
    }else{
        if(!stage1Detached){s1NozzleTips.forEach(t=>{t.glow.visible=false;t.plumeGroup.visible=false;t.diamonds.forEach(d=>d.visible=false);});mainCombinedGroup.visible=false;}
        s2NozzleTips.forEach(t=>{t.glow.visible=false;t.plumeGroup.visible=false;t.diamonds.forEach(d=>d.visible=false);});
        boosterNozzleTips.forEach(t=>{t.glow.visible=false;t.plumeGroup.visible=false;t.diamonds.forEach(d=>d.visible=false);});
        spaceJellyMesh.visible=false;engineHaloGlow.material.opacity=THREE.MathUtils.lerp(engineHaloGlow.material.opacity,0.0,0.15);underglowSp.material.opacity=0.0;engineBounceLight.intensity=0.0;
        rendererMain.toneMappingExposure=THREE.MathUtils.lerp(rendererMain.toneMappingExposure,1.32,0.05);
    }

    if(p0.exploded&&!rudSequenceStarted){
        rudSequenceStarted=true;rudStartTime=simT;playExplosionDetonationSound();camShake=0.95;rocket.visible=false;s1Group.visible=false;
        shockRingMat.opacity=1.0;shockRingMesh.position.set(rx,ry+6.0+s1Len*0.5,0);shockRingMesh.scale.set(2.0,2.0,2.0);
        for(let i=0;i<45;i++){const ang=Math.random()*Math.PI*2,spd=2.0+Math.random()*5.0;emitParticle(rx+Math.cos(ang)*2.0,ry+6.0+s1Len*0.5,Math.sin(ang)*2.0,Math.cos(ang)*spd,(Math.random()-0.5)*4.0,Math.sin(ang)*spd,1.5,16.0,50,0.95,0xffffff,0.95,0.0);}
        rudDebris.forEach((d,di)=>{d.active=true;d.mesh.visible=true;d.mesh.position.set(rx+(Math.random()-0.5)*3.0,ry+6.0+(di/25.0)*s1Len,(Math.random()-0.5)*3.0);const ang=Math.random()*Math.PI*2,blast=1.8+Math.random()*4.2;d.vx=Math.cos(ang)*blast;d.vy=(Math.random()-0.2)*3.5;d.vz=Math.sin(ang)*blast;d.rx=(Math.random()-0.5)*0.2;d.ry=(Math.random()-0.5)*0.2;d.rz=(Math.random()-0.5)*0.2;});
    }
    if(rudSequenceStarted){
        const rudAge=simT-rudStartTime;
        if(rudAge>=0.15&&rudAge<=2.2){
            for(let i=0;i<6;i++){const ang=Math.random()*Math.PI*2,dist=Math.random()*4.5;emitParticle(rx+Math.cos(ang)*dist,ry+6.0+s1Len*0.5+(Math.random()-0.5)*4.0,Math.sin(ang)*dist,Math.cos(ang)*1.5,0.8+Math.random()*1.5,Math.sin(ang)*1.5,4.5,32.0,70,0.85,(Math.random()>0.4?0xea580c:0x7c2d12),0.94,0.035,true);}
        }
        rudDebris.forEach(d=>{
            if(!d.active)return;d.vy-=9.8*0.016*1.2;d.mesh.position.x+=d.vx*0.016*10.0;d.mesh.position.y+=d.vy*0.016*10.0;d.mesh.position.z+=d.vz*0.016*10.0;d.mesh.rotation.x+=d.rx;d.mesh.rotation.y+=d.ry;d.mesh.rotation.z+=d.rz;
            if(Math.random()<0.4)emitParticle(d.mesh.position.x,d.mesh.position.y,d.mesh.position.z,-d.vx*0.1,-d.vy*0.1,-d.vz*0.1,0.8,4.5,35,0.5,0x27272a,0.96,0.01,false);
        });
        if(rudAge>=3.0&&rudBanner.style.display!=='block'){
            rudBanner.style.display='block';rudDesc.innerText=failMessage||"機体過負荷による空中分解 (Structural Disassembly)";document.getElementById('tv-stage-badge').innerText="RUD - VEHICLE DESTROYED";document.getElementById('tv-stage-badge').style.color="#ef4444";
        }
    }

    const cmdFired=(Math.abs(rcsCmd)>0.2&&Math.abs(prevRcsCmd)<=0.2);if(cmdFired){counterDirSign=(rcsCmd>0)?-1.0:1.0;counterPulseTimer=0.26;}
    prevRcsCmd=rcsCmd;const boosterCmdFired=(stage1Detached&&!p0.b_caught&&(Math.abs(bRcsCmd)>0.2||(simT-jsSepTime<4.0&&Math.random()<0.35)));prevBoosterRcs=bRcsCmd;
    let isCounterBurst=false;if(counterPulseTimer>0){counterPulseTimer-=0.016;if(counterPulseTimer<=0)isCounterBurst=true;}
    let soundTriggeredThisFrame=false;
    for(let rcs of rcsNozzles){
        let triggerPulse=false;
        if(!simCfg.is_preview&&simT>0&&!p0.exploded){
            if(!rcs.isS1&&stage1Detached){if(cmdFired&&((rcs.dir.dx<-0.5&&rcsCmd>0)||(rcs.dir.dx>0.5&&rcsCmd<0)))triggerPulse=true;if(isCounterBurst&&((rcs.dir.dx<-0.5&&counterDirSign>0)||(rcs.dir.dx>0.5&&counterDirSign<0)))triggerPulse=true;}
            else if(rcs.isS1){if(!stage1Detached){if(cmdFired&&((rcs.dir.dx<-0.5&&rcsCmd>0)||(rcs.dir.dx>0.5&&rcsCmd<0)))triggerPulse=true;}else if(!p0.b_caught){if(boosterCmdFired)triggerPulse=true;}}
        }
        if(triggerPulse){
            rcs.timer=0.11;if(!soundTriggeredThisFrame){playRcsPuffSound();soundTriggeredThisFrame=true;}
            rcs.mount.getWorldPosition(tempV);const localJetDir=new THREE.Vector3(rcs.dir.dx,0,rcs.dir.dz).normalize(),parentQuat=new THREE.Quaternion();
            rcs.mount.parent.getWorldQuaternion(parentQuat);localJetDir.applyQuaternion(parentQuat);
            for(let k=0;k<2;k++){const spd=2.8+k*1.1;emitParticle(tempV.x+localJetDir.x*0.5,tempV.y+localJetDir.y*0.5,tempV.z+localJetDir.z*0.5,localJetDir.x*spd,localJetDir.y*spd,localJetDir.z*spd,0.18,0.95,6,0.55,0xe0f2fe,0.88,0.0,false);}
        }
        if(rcs.timer>0){rcs.timer-=0.016;rcs.jetMat.opacity=Math.min(0.92,(rcs.timer/0.11)*0.95);const lenScale=0.85+Math.random()*0.3;rcs.jetCone.scale.set(lenScale,1.0,1.0);}
        else{rcs.jetMat.opacity=0.0;}
    }

    if(simT<0.0){
        const sec=Math.ceil(Math.abs(simT));document.getElementById('tv-timer').innerText=simCfg.is_preview?"PAD INSPECTION":`T- 00:0${sec}.0`;
        emitParticle(rx+1.25,ry+6.0+s1Len*0.82,-1.5,0.18,-0.08,0,0.6,2.8,38,0.32,0xffffff,0.97,-0.005,false);
        if(!simCfg.is_preview&&actx){ensureAudioActive();if(gasHiss){const hissGain=(simT>=-5.0)?0.65:0.22;gasHiss.gain.setTargetAtTime(hissGain,actx.currentTime,0.2);}}
        if(simT>=-5.0&&!p0.exploded&&!simCfg.is_preview){
            const delugeRatio=simCfg.water_flow/300.0,countDeluge=Math.max(4,Math.floor(7*delugeRatio));
            for(let i=0;i<countDeluge;i++){const ang=Math.random()*Math.PI*2,rad=1.5+Math.random()*6.0;emitParticle(rx+Math.cos(ang)*rad,2.5,Math.sin(ang)*rad-2.0,Math.cos(ang)*(0.8+Math.random()*1.2),0.15+Math.random()*0.25,Math.sin(ang)*(0.8+Math.random()*1.2),2.2,14.0,52,0.48,0xe0f2fe,0.95,0.018,false);}
        }
        if(simT>=-simCfg.ignition_lead&&!p0.exploded&&!simCfg.is_preview){
            if(!shockwaveFired){shockwaveFired=true;shockRingMat.opacity=0.8;shockRingMesh.scale.set(1.0,1.0,1.0);rendererMain.toneMappingExposure=2.6;}
            if(actx){if(subRumble)subRumble.gain.setTargetAtTime(1.25,actx.currentTime,0.25);if(shockCrackle)shockCrackle.gain.setTargetAtTime(0.95,actx.currentTime,0.2);}
            camShake=0.32;for(let tObj of s1NozzleTips){tObj.node.getWorldPosition(tempV);emitSpark(tempV.x,tempV.y,tempV.z,(Math.random()-0.5)*1.5,-1.2-Math.random()*1.8,(Math.random()-0.5)*1.5,0xfde047);}
            for(let i=0;i<12;i++){const ang=Math.random()*Math.PI*2,spd=2.8+Math.random()*3.2,isInnerLit=(i<5);emitParticle(rx+Math.cos(ang)*2.2,2.4,Math.sin(ang)*2.2-2.5,Math.cos(ang)*spd,0.05+Math.random()*0.2,Math.sin(ang)*spd,2.8,22.0,58,isInnerLit?0.72:0.58,isInnerLit?0xffedd5:0xf8fafc,0.935,0.024,isInnerLit);}
            for(let i=0;i<6;i++){const side=(Math.random()>0.5?1:-1)*(10.0+Math.random()*22.0);emitParticle(rx+side,3.2,-5.0+(Math.random()-0.5)*16.0,side*0.04,0.45+Math.random()*0.55,(Math.random()-0.5)*0.4,6.5,34.0,75,0.52,0xf1f5f9,0.97,0.032,false);}
        }
    }else if(!p0.exploded){
        const m=Math.floor(simT/60),s=simT%60;document.getElementById('tv-timer').innerText=`T+ ${String(m).padStart(2,'0')}:${s.toFixed(1).padStart(4,'0')}`;
        if(actx){const atm=Math.exp(-alt/14.0);if(subRumble)subRumble.gain.setTargetAtTime(1.25*atm,actx.currentTime,0.15);if(shockCrackle)shockCrackle.gain.setTargetAtTime(0.95*atm,actx.currentTime,0.1);if(gasHiss)gasHiss.gain.setTargetAtTime(0.18*atm,actx.currentTime,1.0);}
        if(simT<6.5&&alt<0.45){
            camShake=Math.max(0.15,0.42*(1.0-simT/7.0));const intensity=Math.max(0.2,1.0-(alt/0.42)),surgeCount=Math.floor(14*intensity);
            for(let i=0;i<surgeCount;i++){const ang=Math.random()*Math.PI*2,spd=(3.0+Math.random()*3.5)*intensity,isLit=(i<5);emitParticle(rx+Math.cos(ang)*3.0,2.5,Math.sin(ang)*3.0-3.0,Math.cos(ang)*spd,0.08+Math.random()*0.25,Math.sin(ang)*spd,3.2,26.0,62,isLit?0.70:0.55,isLit?0xfef08a:0xf8fafc,0.93,0.026,isLit);}
            for(let i=0;i<Math.ceil(6*intensity);i++){const ang=Math.random()*Math.PI*2,dist=12.0+Math.random()*28.0;emitParticle(rx+Math.cos(ang)*dist,3.8,Math.sin(ang)*dist*0.6-6.0,Math.cos(ang)*0.6,0.5+Math.random()*0.65,Math.sin(ang)*0.4,7.0,38.0,80,0.50,0xf8fafc,0.965,0.035,false);}
        }
    }

    if(shockRingMat.opacity>0.005){shockRingMesh.scale.x+=1.8;shockRingMesh.scale.z+=1.8;shockRingMat.opacity*=0.91;}else{shockRingMesh.opacity=0.0;}

    for(let p of pool){
        if(!p.active)continue;p.age++;if(p.age>=p.maxAge){p.active=false;p.sp.visible=false;continue;}
        p.vx*=p.drag;p.vz*=p.drag;p.vy=p.vy*p.drag+p.buoyancy;p.sp.position.x+=p.vx;p.sp.position.y=Math.max(2.2,p.sp.position.y+p.vy);p.sp.position.z+=p.vz;p.sp.material.rotation+=p.rotSpeed;
        const pr=p.age/p.maxAge,sc=p.s0+(p.s1-p.s0)*Math.pow(pr,0.58);p.sp.scale.set(sc,sc,1);
        if(p.lit&&pr>0.15)p.sp.material.color.lerp(steamWhiteColor,0.08);
        const fadeIn=Math.min(1.0,p.age/5.0);p.sp.material.opacity=p.o*fadeIn*(1.0-Math.pow(pr,1.8));
    }
    for(let s of sparks){if(!s.active)continue;s.age++;if(s.age>=s.maxAge){s.active=false;s.sp.visible=false;continue;}s.sp.position.x+=s.vx;s.sp.position.y+=s.vy;s.sp.position.z+=s.vz;s.sp.material.opacity=1.0-(s.age/s.maxAge);}
    for(let ic of iceShards){if(!ic.active)continue;ic.age++;if(ic.age>=ic.maxAge){ic.active=false;ic.sp.visible=false;continue;}ic.sp.position.x+=ic.vx;ic.sp.position.y+=ic.vy;ic.sp.position.z+=ic.vz;ic.vy-=9.8*0.016*0.5;ic.sp.material.opacity=1.0-(ic.age/ic.maxAge);}

    if(p0.stage===2){activeFocusWorld.set(0,s2Len*0.45,0);s2Group.localToWorld(activeFocusWorld);}
    else{activeFocusWorld.set(0,s1Len*0.52,0);rocket.localToWorld(activeFocusWorld);}

    if(simCfg.is_preview){
        const ang=elapsedSec*0.22;cameraMain.position.set(Math.sin(ang)*280.0,42.0,Math.cos(ang)*280.0);
        smoothCamTarget.set(0,6.0+(s1Len+s2Len)*0.45,0);cameraMain.lookAt(smoothCamTarget);
    }else{
        cameraMain.position.set(activeFocusWorld.x-180.0,activeFocusWorld.y+35.0,activeFocusWorld.z+320.0);
        const heatHazeFactor=Math.max(0.0,1.0-alt/4.0),heatHazeX=Math.sin(now*0.018)*0.15*heatHazeFactor,heatHazeY=Math.cos(now*0.022)*0.18*heatHazeFactor;
        cameraMain.position.x+=heatHazeX;cameraMain.position.y+=heatHazeY;
        if(camShake>0.002){cameraMain.position.x+=(Math.random()-0.5)*camShake*2.5;cameraMain.position.y+=(Math.random()-0.5)*camShake*2.5;camShake*=0.94;}
        if(stage1Detached&&(simT-jsSepTime<5.0)){cameraMain.fov=THREE.MathUtils.lerp(cameraMain.fov,21.0,0.08);}else{cameraMain.fov=THREE.MathUtils.lerp(cameraMain.fov,16.0,0.05);}
        cameraMain.updateProjectionMatrix();
        const lookAim=new THREE.Vector3().copy(activeFocusWorld);lookAim.x+=Math.sin(now*0.002)*0.25;lookAim.y+=Math.cos(now*0.0017)*0.25;cameraMain.lookAt(lookAim);
    }

    if(p0.event==="ORBIT"){solarL.scale.x=THREE.MathUtils.lerp(solarL.scale.x,1.0,0.08);solarR.scale.x=THREE.MathUtils.lerp(solarR.scale.x,1.0,0.08);}

    // =========================================================================
    // 📺 CAM 02 (地上望遠) ＆ CAM 01 (メイン) 完全環境分離レンダリング
    // =========================================================================
    if(pipVisible){
        skyDome.position.copy(cameraPip.position);skyDomeMat.color.setRGB(1.0,1.0,1.0);starPoints.visible=false;
        atmoLimbMesh.visible=false;
        scene.fog.density=0.000028;scene.fog.color.setHex(0x4a769e);skyAmbient.intensity=1.65;sunLight.intensity=4.8;
        let targetPos=new THREE.Vector3();
        if(stage1Detached&&p0.b_active){
            targetPos.set(bX*0.1,bY_scaled+s1Len*0.55,0);cameraPip.position.set(240.0,22.0,260.0);
            if(bY<=14000&&bY>=10000&&!pipBlurTriggered12k){triggerPipAutoFocus();pipBlurTriggered12k=true;}
            if(bY<=3600&&!pipBlurTriggeredCatch){triggerPipAutoFocus();pipBlurTriggeredCatch=true;}
            const bSpdKmh=Math.round(Math.abs(bVyVal)*3.6),vArrow=(bVyVal<-5.0)?"▼":((bVyVal>5.0)?"▲":"━"),vColor=(bVyVal<-5.0)?"#34d399":"#38bdf8";
            if(p0.b_caught||bY_scaled<=90.0){
                cameraPip.fov=THREE.MathUtils.lerp(cameraPip.fov,16.0,0.1);document.getElementById('pip-tag').innerText="CAM 02: GROUND OPTICAL (TOWER CATCH)";document.getElementById('pip-hud-alt').innerText=p0.b_caught?"SUSPENDED (SECURED)":"FINAL TOUCHDOWN";
            }else{
                const targetFov=Math.max(8.0,Math.min(22.0,bY_scaled/35.0));cameraPip.fov=THREE.MathUtils.lerp(cameraPip.fov,targetFov,0.1);document.getElementById('pip-tag').innerText="CAM 02: GROUND OPTICAL TRACKER";
                document.getElementById('pip-hud-alt').innerHTML=`ALT: ${(bY*0.001).toFixed(1)} km <span style="color:${vColor};font-size:9.5px;margin-left:4px;">${vArrow} ${bSpdKmh.toLocaleString()} km/h</span>`;
            }
        }else{
            targetPos.copy(rocket.position);targetPos.y+=s1Len*0.5;cameraPip.position.set(240.0,22.0,260.0);
            cameraPip.fov=THREE.MathUtils.lerp(cameraPip.fov,Math.max(8.0,Math.min(24.0,rocket.position.y/24.0)),0.1);
            document.getElementById('pip-tag').innerText="CAM 02: GROUND OPTICAL (PAD 39A)";document.getElementById('pip-hud-alt').innerText=`ALT: ${(rocket.position.y*0.01).toFixed(1)} km`;
        }
        cameraPip.lookAt(targetPos);cameraPip.updateProjectionMatrix();
        pipTrackingSpot.position.set(targetPos.x+80,targetPos.y+100,targetPos.z+80);pipTrackingSpot.target.position.copy(targetPos);pipTrackingSpot.target.updateMatrixWorld();
        rendererPip.render(scene,cameraPip);
    }

    skyDome.position.copy(cameraMain.position);
    skyDomeMat.color.setRGB(1.0-spaceFactor*0.95,1.0-spaceFactor*0.92,1.0-spaceFactor*0.85);
    starPoints.visible=true;starMat.opacity=Math.min(0.95,Math.max(0.05,(alt-15.0)/55.0));
    scene.fog.density=THREE.MathUtils.lerp(0.000028,0.0,Math.min(1.0,alt/25.0));
    if(alt>20.0){atmoLimbMesh.visible=true;atmoLimbMat.opacity=Math.min(0.42,(alt-20.0)/55.0);}else{atmoLimbMesh.visible=false;atmoLimbMat.opacity=0.0;}
    atmoLimbMesh.position.set(cameraMain.position.x,-56000,cameraMain.position.z);
    rendererMain.render(scene,cameraMain);

    const dRangeKm=(rx*10.0)/1000.0;
    drawPrecisionOrbitMap(alt,dRangeKm,p0.exploded,(p0.event==="ORBIT"));
    drawEngineClusterGraphic(p0.stage,p0.thrust,p0.exploded,p0.b_thrust,p0.b_caught);

    let regime="TROPO";if(alt>=100.0)regime="THERMO (VAC)";else if(alt>=50.0)regime="MESO";else if(alt>=12.0)regime="STRATO";
    document.getElementById('hud-regime').innerText=regime;
    document.getElementById('hud-downrange').innerText=`DOWNRANGE: ${dRangeKm.toFixed(1)} km`;
    document.getElementById('hud-pitch').innerText=`${pitchDegVal.toFixed(1)}°`;
    document.getElementById('hud-apogee').innerText=`${apogeeVal.toFixed(1)} km`;
    document.getElementById('hud-s1-prop').innerText=`${Math.round(s1PropVal)}%`;
    document.getElementById('hud-s2-prop').innerText=`${Math.round(s2PropVal)}%`;
    document.getElementById('hud-pc').innerText=`${Math.round(pcVal)} bar`;
    document.getElementById('tv-mach').innerText=`M ${mach.toFixed(2)}`;
    document.getElementById('tv-spd').innerText=`(${Math.round(vel*3.6).toLocaleString()} km/h)`;
    document.getElementById('tv-alt').innerText=Math.max(0,alt).toFixed(1);
    document.getElementById('tv-q').innerText=q.toFixed(1);
    document.getElementById('tv-g').innerText=accG.toFixed(1);

    const isOrbit=(p0.event==="ORBIT"),canComplete=simCfg.spacex_return?(isOrbit&&p0.b_caught):isOrbit;
    if(canComplete&&!isMissionEnded){
        completeBanner.style.display='block';
        if(simCfg.spacex_return){
            document.getElementById('complete-desc').innerText="LEO INSERTION & SUPER HEAVY TOWER CATCH ACHIEVED";
            document.getElementById('complete-sub').innerText="Booster suspended on Mechazilla chopsticks. Orbiter in circular orbit. Solar arrays deployed.";
        }else{
            document.getElementById('complete-desc').innerText="FIRST COSMIC VELOCITY (28,400 km/h) NOMINAL INSERTION";
            document.getElementById('complete-sub').innerText="Vehicle has achieved stable orbital trajectory. Solar arrays deployed.";
        }
        document.getElementById('tv-stage-badge').innerText="MISSION SUCCESS - ALL OBJECTIVES ACHIEVED";document.getElementById('tv-stage-badge').style.color="#10b981";
        document.getElementById('live-indicator').style.background="#10b981";document.getElementById('webcast-title').innerText="CAM 01: MISSION COMPLETED";
        if(actx){
            if(subRumble)subRumble.gain.setTargetAtTime(0.0001,actx.currentTime,0.4);if(shockCrackle)shockCrackle.gain.setTargetAtTime(0.0001,actx.currentTime,0.4);
            if(gasHiss)gasHiss.gain.setTargetAtTime(0.0001,actx.currentTime,0.4);if(boosterRumble)boosterRumble.gain.setTargetAtTime(0.0001,actx.currentTime,0.2);if(boosterCrackle)boosterCrackle.gain.setTargetAtTime(0.0001,actx.currentTime,0.2);
        }
        setTimeout(()=>{isMissionEnded=true;},3600);
    }
}

const finalW=window.innerWidth||1200,finalH=window.innerHeight||980;
rendererMain.setSize(finalW,finalH);cameraMain.aspect=finalW/finalH;cameraMain.updateProjectionMatrix();resizePipRenderer();
requestAnimationFrame(animate);

window.addEventListener('resize',()=>{
    updatePipPosition();resizePipRenderer();
    const rw=window.innerWidth||1200,rh=window.innerHeight||980;
    cameraMain.aspect=rw/rh;cameraMain.updateProjectionMatrix();rendererMain.setSize(rw,rh);
});
}catch(err){
    console.error("Simulation Render Error:",err);
    const el=document.getElementById('event-log');if(el){el.innerText="🚨 SIM RENDER ERROR: "+err.message;el.style.color="#ef4444";}
}
});
</script></body></html>"""

final_html = (
    html_template.replace("__SIM_DATA__", traj_json)
    .replace("__SIM_CFG__", cfg_json)
    .replace("__FAIL_MSG__", fail_msg_clean)
)
components.html(final_html, height=980)

if launch_clicked:
  st.markdown("---")
  st.markdown("### 📋 フライトテレメトリ詳細レポート")
  if error_msg:
    st.error(f"⚠️ **ミッション異常終了 (RUD)**: {error_msg}")
  else:
    st.success(
        "🎉 **ミッション完全成功**:"
        " 軌道投入および機体制御シーケンスが設計通り正常に完了しました。"
    )
