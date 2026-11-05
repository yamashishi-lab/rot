import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect Extreme: Ultra-Real 4K Cinema", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect Extreme - 4K実写映画級 航空宇宙・弾道学シミュレーター")
st.caption("※ 完全拡張仕様：実機時間スケール・破片終息後RUD判定・広域PBR海洋ランドスケープ・4象限RCS・超低音音響合成")

# =========================================================================
# 🔬 推進剤・サイクル・素材・空力パーツ・ブースター・先端部 データベース
# =========================================================================
PROPELLANTS = {
    "超高密度サブクール・メタロックス (CH4 / LOX) [Starship / Raptor 3]": {
        "base_isp_sl": 338, "base_isp_vac": 382, "base_thrust": 2800, "density": 0.85, 
        "flame_hex": 0x38bdf8, "outer_hex": 0x1d4ed8, "spark_hex": 0x93c5fd, "risk": 0.005, "type": "methalox"
    },
    "高精製ロケットグレードケロシン (RP-1 / LOX) [Falcon 9 / Merlin 1D]": {
        "base_isp_sl": 282, "base_isp_vac": 311, "base_thrust": 845, "density": 1.03, 
        "flame_hex": 0xfef08a, "outer_hex": 0xea580c, "spark_hex": 0xfde047, "risk": 0.002, "type": "rp1"
    },
    "Saturn V 伝統 F-1 ケロシン (巨大ノズル煤煙仕様)": {
        "base_isp_sl": 263, "base_isp_vac": 304, "base_thrust": 6770, "density": 1.02, 
        "flame_hex": 0xffd166, "outer_hex": 0xc84b16, "spark_hex": 0xf4a261, "risk": 0.008, "type": "rp1_heavy"
    },
    "超極低温スラッシュ・ハイドロロックス (LH2 / LOX) [H3 / SLS / RS-25]": {
        "base_isp_sl": 366, "base_isp_vac": 452, "base_thrust": 2279, "density": 0.32, 
        "flame_hex": 0xfbcfe8, "outer_hex": 0xbe185d, "spark_hex": 0xffffff, "risk": 0.025, "type": "hydro"
    },
    "【軍用猛毒】四酸化二窒素 ＋ UDMH (N2O4 / UDMH) [Proton / ICBM]": {
        "base_isp_sl": 285, "base_isp_vac": 320, "base_thrust": 1850, "density": 1.25, 
        "flame_hex": 0xf5d0fe, "outer_hex": 0x9333ea, "spark_hex": 0xfab1a0, "risk": 0.04, "type": "hypergolic"
    },
    "【固体推進】高エネルギーHTPB/アルミ粉末コンポジット [軍用ICBM / SRB]": {
        "base_isp_sl": 250, "base_isp_vac": 282, "base_thrust": 3400, "density": 1.78, 
        "flame_hex": 0xffedd5, "outer_hex": 0x9a3412, "spark_hex": 0xffffff, "risk": 0.015, "type": "solid"
    },
    "【核熱】固体炉心型原子力サーマルロケット (NERVA / LH2)": {
        "base_isp_sl": 450, "base_isp_vac": 925, "base_thrust": 2500, "density": 0.30, 
        "flame_hex": 0x86efac, "outer_hex": 0x14532d, "spark_hex": 0x4ade80, "risk": 0.12, "type": "nuclear"
    },
    "【ジョーク・ネタ枠】超濃縮コーラ ＋ メントス高圧スラリ噴射": {
        "base_isp_sl": 42, "base_isp_vac": 48, "base_thrust": 160, "density": 1.15, 
        "flame_hex": 0x78350f, "outer_hex": 0x451a03, "spark_hex": 0xfbbf24, "risk": 0.35, "type": "joke_mentos"
    }
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [極限高圧・Starship仕様]": {"isp_mod": 1.07, "thrust_mod": 1.35, "mass_mod": 1.22, "max_pressure_limit": 380, "cyc_id": "ffsc"},
    "酸化剤リッチ二段燃焼 (ORSC) [RD-180 / 高出力ロシア仕様]": {"isp_mod": 1.04, "thrust_mod": 1.25, "mass_mod": 1.18, "max_pressure_limit": 310, "cyc_id": "sc"},
    "ガス発生器サイクル (GG) [Merlin 1D / F-1 煤煙ダクト]": {"isp_mod": 0.96, "thrust_mod": 1.00, "mass_mod": 0.85, "max_pressure_limit": 195, "cyc_id": "gg"},
    "エキスパンダーブリードサイクル (EB) [LE-9 / H3仕様 高信頼]": {"isp_mod": 1.02, "thrust_mod": 0.92, "mass_mod": 0.95, "max_pressure_limit": 180, "cyc_id": "eb"},
    "固体ロケットモーター穀燃焼 (Grain Direct)": {"isp_mod": 0.92, "thrust_mod": 1.45, "mass_mod": 0.75, "max_pressure_limit": 220, "cyc_id": "solid_grain"},
    "リニアエアロスパイク方式 [全高度最適膨張]": {"isp_mod": 1.09, "thrust_mod": 1.10, "mass_mod": 1.32, "max_pressure_limit": 250, "cyc_id": "aerospike"},
    "手動手押しダイヤフラムポンプ [ジョーク]": {"isp_mod": 0.35, "thrust_mod": 0.20, "mass_mod": 0.50, "max_pressure_limit": 45, "cyc_id": "joke_pump"}
}

MATERIALS = {
    "Austenitic 304L 冷間圧延鏡面ステンレス [Starship仕様]": {"base_dry_ratio": 0.065, "max_q_base": 130.0, "max_g_base": 12.5, "mat_id": "ss"},
    "航空宇宙用 Al-Li-2195 アルミリチウム合金 [SLSオレンジ防熱塗工]": {"base_dry_ratio": 0.050, "max_q_base": 82.0, "max_g_base": 9.0, "mat_id": "al"},
    "Falcon 9 伝統 ホワイト＆黒インターセクション特殊耐火塗工": {"base_dry_ratio": 0.048, "max_q_base": 90.0, "max_g_base": 10.0, "mat_id": "f9_white"},
    "Saturn V 伝統 白黒ロールチェック塗工 [ハイコントラスト]": {"base_dry_ratio": 0.054, "max_q_base": 88.0, "max_g_base": 9.5, "mat_id": "saturn"},
    "高弾性トレカ炭素繊維複合材 (CFRP) [軽量・低抗力マットブラック]": {"base_dry_ratio": 0.034, "max_q_base": 65.0, "max_g_base": 7.5, "mat_id": "cf"},
    "軍用高張力チタン・マルエージング鋼耐熱装甲 [ICBM仕様]": {"base_dry_ratio": 0.095, "max_q_base": 180.0, "max_g_base": 18.0, "mat_id": "icbm_steel"},
    "段ボール紙＆ガムテープ巻き [ジョーク・超低強度]": {"base_dry_ratio": 0.018, "max_q_base": 14.0, "max_g_base": 2.2, "mat_id": "cardboard"}
}

STRAPON_BOOSTERS = {
    "なし (単段スリムコア構成)": {"count": 0, "thrust_add": 0.0, "mass_add": 0.0, "fuel_add": 0.0, "isp_sl": 0, "type": "none"},
    "Falcon Heavy風 液体LRB × 2基 (再突入グリッドフィン付き)": {"count": 2, "thrust_add": 15000.0, "mass_add": 55.0, "fuel_add": 840.0, "isp_sl": 282, "type": "lrb"},
    "Soyuz R-7風 テーパー液体ブースター × 4基 (コロリョフクロス専用)": {"count": 4, "thrust_add": 3950.0, "mass_add": 38.0, "fuel_add": 480.0, "isp_sl": 257, "type": "soyuz"},
    "SLS / スペースシャトル風 巨大SRB × 2基 (白塗装＆黒ジョイント)": {"count": 2, "thrust_add": 28000.0, "mass_add": 120.0, "fuel_add": 1250.0, "isp_sl": 269, "type": "srb"},
    "極秘核分裂ブースターポッド × 2基 [危険]": {"count": 2, "thrust_add": 9500.0, "mass_add": 42.0, "fuel_add": 220.0, "isp_sl": 680, "type": "nuclear_strap"}
}

AERO_WINGS = {
    "チタン鍛造極超音速グリッドフィン × 4基 (Falcon 9 / RTLS帰還用)": {"lift_coeff": 0.15, "drag_penalty": 1.06, "mass": 1.4, "flutter_mach": 99.0, "wing_id": "grid"},
    "Starship風 空力エルロンボディフラップ × 4枚 (ベリーフロップ制御)": {"lift_coeff": 0.38, "drag_penalty": 1.15, "mass": 3.2, "flutter_mach": 99.0, "wing_id": "starship_flap"},
    "なし (軸対称弾道ロケット・ミサイル姿勢制御)": {"lift_coeff": 0.0, "drag_penalty": 1.0, "mass": 0.0, "flutter_mach": 99.0, "wing_id": "none"},
    "軍用ICBM 先進高機動デルタスタビライザー翼 × 4枚": {"lift_coeff": 0.45, "drag_penalty": 1.08, "mass": 1.1, "flutter_mach": 12.0, "wing_id": "icbm_fin"},
    "竹とんぼ風 巨大プロペラ翼 [ジョーク]": {"lift_coeff": 1.60, "drag_penalty": 3.20, "mass": 4.5, "flutter_mach": 0.85, "wing_id": "joke_prop"}
}

FAIRINGS = {
    "バイコニカル炭素複合材クラムシェル (金箔大型通信衛星内蔵)": {"mass": 2.2, "cd": 0.18, "heat_limit": 2600, "shape_id": "biconic", "is_weapon": False},
    "有人カプセル ＋ レスキューアボートタワー (LESエスケープ付)": {"mass": 7.4, "cd": 0.35, "heat_limit": 3200, "shape_id": "abort_tower", "is_weapon": False},
    "Starship風 窓付き有人クルーノーズコーン (大型キャビン)": {"mass": 5.2, "cd": 0.22, "heat_limit": 2900, "shape_id": "starship_crew", "is_weapon": False},
    "【軍用弾道弾】MIRV多弾頭 MIRV熱シールド再突入コーン": {"mass": 3.8, "cd": 0.12, "heat_limit": 4800, "shape_id": "mirv_cone", "is_weapon": True},
    "【超音速滑空兵器】極超音速グライドウェポン (HGV)": {"mass": 2.9, "cd": 0.14, "heat_limit": 5500, "shape_id": "hgv_waverider", "is_weapon": True},
    "超巨大ゴールデンメガホン [ジョーク]": {"mass": 1.5, "cd": 0.65, "heat_limit": 800, "shape_id": "joke_cone", "is_weapon": False}
}

PRESETS = {
    "カスタム手動設定": None,
    "Falcon 9 Full Thrust風 (第1段RTLS着陸帰還モード)": {
        "s1_prop": "高精製ロケットグレードケロシン (RP-1 / LOX) [Falcon 9 / Merlin 1D]",
        "s1_cycle": "ガス発生器サイクル (GG) [Merlin 1D / F-1 煤煙ダクト]",
        "s1_eng": 9, "s1_pc": 97, "s1_fuel": 418.0, "s1_mat": "Falcon 9 伝統 ホワイト＆黒インターセクション特殊耐火塗工",
        "s1_thick": 3.8, "strapon": "なし (単段スリムコア構成)", "wing": "チタン鍛造極超音速グリッドフィン × 4基 (Falcon 9 / RTLS帰還用)",
        "s2_prop": "高精製ロケットグレードケロシン (RP-1 / LOX) [Falcon 9 / Merlin 1D]", "s2_eng": 1, "s2_fuel": 92.0,
        "s2_mat": "Falcon 9 伝統 ホワイト＆黒インターセクション特殊耐火塗工", "s2_thick": 3.0,
        "fairing": "バイコニカル炭素複合材クラムシェル (金箔大型通信衛星内蔵)", "payload": 16.5,
        "return_mode": True, "turn_start": 1.2, "turn_end": 110.0, "turn_exp": 0.58
    },
    "Starship / Super Heavy風 (完全再使用巨大メタロックス)": {
        "s1_prop": "超高密度サブクール・メタロックス (CH4 / LOX) [Starship / Raptor 3]",
        "s1_cycle": "フルフローステージド燃焼 (FFSC) [極限高圧・Starship仕様]",
        "s1_eng": 33, "s1_pc": 350, "s1_fuel": 3400.0, "s1_mat": "Austenitic 304L 冷間圧延鏡面ステンレス [Starship仕様]",
        "s1_thick": 4.5, "strapon": "なし (単段スリムコア構成)", "wing": "Starship風 空力エルロンボディフラップ × 4枚 (ベリーフロップ制御)",
        "s2_prop": "超高密度サブクール・メタロックス (CH4 / LOX) [Starship / Raptor 3]", "s2_eng": 6, "s2_fuel": 1200.0,
        "s2_mat": "Austenitic 304L 冷間圧延鏡面ステンレス [Starship仕様]", "s2_thick": 4.0,
        "fairing": "Starship風 窓付き有人クルーノーズコーン (大型キャビン)", "payload": 100.0,
        "return_mode": False, "turn_start": 2.0, "turn_end": 130.0, "turn_exp": 0.65
    },
    "大陸間弾道ミサイル ICBM (重装甲・超高速MIRV弾頭)": {
        "s1_prop": "【固体推進】高エネルギーHTPB/アルミ粉末コンポジット [軍用ICBM / SRB]",
        "s1_cycle": "固体ロケットモーター穀燃焼 (Grain Direct)",
        "s1_eng": 4, "s1_pc": 180, "s1_fuel": 85.0, "s1_mat": "軍用高張力チタン・マルエージング鋼耐熱装甲 [ICBM仕様]",
        "s1_thick": 6.8, "strapon": "なし (単段スリムコア構成)", "wing": "軍用ICBM 先進高機動デルタスタビライザー翼 × 4枚",
        "s2_prop": "【固体推進】高エネルギーHTPB/アルミ粉末コンポジット [軍用ICBM / SRB]", "s2_eng": 1, "s2_fuel": 28.0,
        "s2_mat": "軍用高張力チタン・マルエージング鋼耐熱装甲 [ICBM仕様]", "s2_thick": 5.2,
        "fairing": "【軍用弾道弾】MIRV多弾頭 MIRV熱シールド再突入コーン", "payload": 3.5,
        "return_mode": False, "turn_start": 0.4, "turn_end": 80.0, "turn_exp": 0.45
    },
    "極限ネタ：コーラ＆メントス段ボールロケット [ほぼ確実に爆散]": {
        "s1_prop": "【ジョーク・ネタ枠】超濃縮コーラ ＋ メントス高圧スラリ噴射",
        "s1_cycle": "手動手押しダイヤフラムポンプ [ジョーク]",
        "s1_eng": 12, "s1_pc": 40, "s1_fuel": 120.0, "s1_mat": "段ボール紙＆ガムテープ巻き [ジョーク・超低強度]",
        "s1_thick": 1.2, "strapon": "なし (単段スリムコア構成)", "wing": "竹とんぼ風 巨大プロペラ翼 [ジョーク]",
        "s2_prop": "【ジョーク・ネタ枠】超濃縮コーラ ＋ メントス高圧スラリ噴射", "s2_eng": 2, "s2_fuel": 25.0,
        "s2_mat": "段ボール紙＆ガムテープ巻き [ジョーク・超低強度]", "s2_thick": 1.0,
        "fairing": "超巨大ゴールデンメガホン [ジョーク]", "payload": 0.8,
        "return_mode": False, "turn_start": 0.5, "turn_end": 60.0, "turn_exp": 0.70
    }
}

preset_choice = st.selectbox("⚡ クイック機体プリセット選択 (瞬時に構成展開)", list(PRESETS.keys()), index=0)
cur_p = PRESETS[preset_choice]

# =========================================================================
# 🎛️ パラメータ設定タブ
# =========================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 第1段 (推進・エンジン・構造)", 
    "🚀 外部ブースター & SpaceX帰還モード",
    "🛩️ 空力フィン & 4象限RCS姿勢制御", 
    "🛰️ 第2段 (上段) & ペイロード/弾頭", 
    "🌊 水冷デリュージ & 飛行ガイダンス"
])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=list(PROPELLANTS.keys()).index(cur_p["s1_prop"]) if cur_p else 0)
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", list(PUMP_CYCLES.keys()), index=list(PUMP_CYCLES.keys()).index(cur_p["s1_cycle"]) if cur_p else 0)
        s1_eng_count = st.slider("メインエンジン 基数", 1, 33, cur_p["s1_eng"] if cur_p else 9)
    with c2:
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 20, 420, cur_p["s1_pc"] if cur_p else 280, step=5)
        s1_eps = st.slider("海面膨張比 (ε: ノズル径・過膨張連動)", 8, 70, 24, step=1)
        s1_gimbal_limit = st.slider("ジンバル最大首振り角 (deg)", 1.0, 15.0, 6.0, step=0.5)
    with c3:
        s1_fuel = st.slider("第1段 推進剤充填量 (トン: 胴体長連動)", 30.0, 4500.0, float(cur_p["s1_fuel"]) if cur_p else 1100.0, step=25.0)
        s1_mat = st.selectbox("第1段 構造素材", list(MATERIALS.keys()), index=list(MATERIALS.keys()).index(cur_p["s1_mat"]) if cur_p else 0)
        s1_thick = st.slider("外殻等価板厚 (mm: 重量・耐圧・耐熱トレードオフ)", 0.8, 14.0, float(cur_p["s1_thick"]) if cur_p else 4.0, step=0.1)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        strapon_opt = st.selectbox("外部ブースター構成", list(STRAPON_BOOSTERS.keys()), index=list(STRAPON_BOOSTERS.keys()).index(cur_p["strapon"]) if cur_p else 2)
        sep_thrust_factor = st.slider("分離パイロモーター反発速度倍率", 0.2, 2.5, 0.85, step=0.05)
    with c2:
        rtls_enabled = st.checkbox("🔄 SpaceX型 ブースターRTLS帰還 (分離後反転・再突入燃焼・パッド逆噴射着陸)", value=cur_p.get("return_mode", False) if cur_p else False)
        st.info("💡 **物理挙動改善**: 切り離されたブースターは急激に加速離反せず、慣性と空気抵抗に従って自然に本体後方へ滞留・減速・落下します。")

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("外部 空力パーツ / フィン", list(AERO_WINGS.keys()), index=list(AERO_WINGS.keys()).index(cur_p["wing"]) if cur_p else 0)
        angle_of_attack = st.slider("固定取り付け迎角 AoA (deg)", -4.0, 15.0, 0.0, step=0.5)
    with c2:
        rcs_deadband = st.slider("4象限RCS デッドバンド感度 (deg)", 0.2, 5.0, 1.2, step=0.1)
        st.caption("※ 前後4箇所の独立ノズル(+Pitch/-Pitch/+Yaw/-Yaw)から、姿勢誤差を打ち消す方向のみ精密パルス噴射します。")

with tab4:
    c1, c2, c3 = st.columns(3)
    with c1:
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=list(PROPELLANTS.keys()).index(cur_p["s2_prop"]) if cur_p else 0)
        s2_cycle = st.selectbox("第2段 ポンプ方式", list(PUMP_CYCLES.keys()), index=0)
        s2_eng_count = st.slider("上段エンジン基数", 1, 9, cur_p["s2_eng"] if cur_p else 3)
        s2_eps = st.slider("上段 真空膨張比 (ε)", 30, 300, 160, step=5)
    with c2:
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 10.0, 1500.0, float(cur_p["s2_fuel"]) if cur_p else 280.0, step=10.0)
        s2_mat = st.selectbox("第2段 構造素材", list(MATERIALS.keys()), index=list(MATERIALS.keys()).index(cur_p["s2_mat"]) if cur_p else 0)
        s2_thick = st.slider("第2段 壁厚 (mm)", 0.6, 10.0, float(cur_p["s2_thick"]) if cur_p else 3.0, step=0.1)
    with c3:
        fairing_type = st.selectbox("先端空力カウル / ペイロード", list(FAIRINGS.keys()), index=list(FAIRINGS.keys()).index(cur_p["fairing"]) if cur_p else 0)
        fairing_sep_alt = st.slider("カウル分離高度 (km)", 35.0, 180.0, 75.0, step=5.0)
        payload_mass = st.slider("投入ペイロード/弾頭質量 (トン)", 0.1, 150.0, float(cur_p["payload"]) if cur_p else 22.0, step=0.5)

with tab5:
    c1, c2 = st.columns(2)
    with c1:
        water_flow_rate = st.slider("発射台 消音注水デリュージ流量 (トン/秒)", 50, 600, 320, step=25)
        ignition_lead_time = st.slider("エンジン先行点火開始 (T-マイナス秒)", 2.0, 6.0, 3.8, step=0.1)
        sound_suppression = st.checkbox("音響反射抑制プレート設置 (離床時の衝撃波減衰)", value=True)
    with c2:
        turn_start_alt = st.slider("重力ターン開始高度 (km)", 0.2, 20.0, float(cur_p["turn_start"]) if cur_p else 1.8, step=0.1)
        turn_end_alt = st.slider("水平重力ターン完了高度 (km)", 40.0, 260.0, float(cur_p["turn_end"]) if cur_p else 120.0, step=5.0)
        turn_exponent = st.slider("ターン曲率指数 (低いほど急旋回)", 0.25, 2.0, float(cur_p["turn_exp"]) if cur_p else 0.62, step=0.02)
        throttle_maxq = st.slider("Max-Q 領域 スロットル抑制率 (%)", 25, 100, 75, step=5)
        max_g_limit_cut = st.slider("最大過負荷リミッター (G)", 2.0, 15.0, 5.0, step=0.2)

# =========================================================================
# ⚙️ 航空宇宙物理演算 (過負荷・過膨張・実時間スケール積分)
# =========================================================================
def calc_stage_specs(prop_key, cycle_key, pc, eps, eng_count, fuel_mass, mat_key, thick):
    prop = PROPELLANTS[prop_key]
    cyc = PUMP_CYCLES[cycle_key]
    mat = MATERIALS[mat_key]

    pc_ratio = pc / 100.0
    pc_factor = 1.0 + (pc - 100.0) * 0.0006
    eps_vac_bonus = 1.0 + np.log10(eps / 25.0) * 0.09
    
    overexpansion_penalty = max(0.0, (eps - 36.0) * 0.008)

    isp_sl = max(10.0, prop["base_isp_sl"] * cyc["isp_mod"] * pc_factor * (1.0 - overexpansion_penalty))
    isp_vac = prop["base_isp_vac"] * cyc["isp_mod"] * pc_factor * eps_vac_bonus

    thrust_vac_per_eng = prop["base_thrust"] * cyc["thrust_mod"] * (pc_ratio ** 0.65)
    thrust_sl_per_eng = thrust_vac_per_eng * (isp_sl / isp_vac)

    density_penalty = (1.0 / prop["density"]) ** 0.35
    thick_factor = thick / 3.0
    dry_ratio = mat["base_dry_ratio"] * density_penalty * thick_factor + 0.004
    eng_mass = (thrust_vac_per_eng / 750.0) * cyc["mass_mod"] * (1.0 + eps * 0.002) * eng_count
    dry_mass = fuel_mass * dry_ratio + eng_mass

    max_q_resistance = mat["max_q_base"] * (thick_factor ** 1.15)
    max_g_resistance = mat["max_g_base"] * (thick_factor ** 0.90)

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

s1_spec = calc_stage_specs(s1_prop, s1_cycle, s1_pc, s1_eps, s1_eng_count, s1_fuel, s1_mat, s1_thick)
s2_spec = calc_stage_specs(s2_prop, s2_cycle, 220, s2_eps, s2_eng_count, s2_fuel, s2_mat, s2_thick)

total_s2_wet = s2_fuel + s2_spec["dry_mass"] + payload_mass + fair_spec["mass"]
total_s1_wet = s1_fuel + s1_spec["dry_mass"] + wing_spec["mass"] + strapon_spec["mass_add"] + strapon_spec["fuel_add"] + total_s2_wet

total_liftoff_thrust = s1_spec["thrust_sl"] + strapon_spec["thrust_add"]
twr_init = total_liftoff_thrust / (total_s1_wet * 9.80665)
dv_s1 = s1_spec["isp_sl"] * 9.80665 * np.log(total_s1_wet / max(1.0, total_s1_wet - s1_fuel - strapon_spec["fuel_add"]))
dv_s2 = s2_spec["isp_vac"] * 9.80665 * np.log(total_s2_wet / max(1.0, s2_spec["dry_mass"] + payload_mass))
total_dv = dv_s1 + dv_s2

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("総離床重量 / 離床TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f} ({'離床可' if twr_init >= 1.05 else '推力不足で浮上不可'})")
m2.metric("総計算速度増分 (ΔV)", f"{total_dv:.0f} m/s", "LEO投入: 9,200m/s / 弾道: 4,500m/s")
m3.metric("構造限界動圧 / 耐G", f"{s1_spec['max_q']:.1f} kPa", f"耐G: {s1_spec['max_g']:.1f} G")
m4.metric("ブースター追加推力", f"+{strapon_spec['thrust_add']:.0f} kN", f"基数: {strapon_spec['count']} 基")

# =========================================================================
# 💥 実機実時間タイムステップ・継続落下物理シミュレータ
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

    if s1_pc > s1_spec["pc_limit"]:
        fail_reason = f"ターボポンプ破裂: 燃焼室圧力 ({s1_pc} bar) が許容限界 ({s1_spec['pc_limit']} bar) を超過し発射台上でCatastrophic Explosion。"
        history[-1]["exploded"] = True
        history[-1]["explosion_type"] = "PAD_EXPLOSION"
        # 爆発後も破片落下と煙消滅までシミュレーション継続
        for pad_debris in range(80):
            t_deb = pad_debris * dt
            history.append({
                "t": float(t_deb), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0,
                "q": 0.0, "g": 0.0, "stage": 1, "fairing": False, "wings": False, "strapon": False,
                "exploded": True, "explosion_type": "PAD_EXPLOSION", "thrust": False, "pitch": 0.0,
                "mach": 0.0, "event": "RUD_FALL"
            })
        return history, fail_reason

    if twr_init < 1.0:
        fail_reason = f"推力重量比不足 (TWR: {twr_init:.2f} < 1.00): 機体重量が総推力を上回り、発射台を浮上できず火炎のなかで転倒炎上。"
        history[-1]["exploded"] = True
        history[-1]["explosion_type"] = "PAD_TWR_FAIL"
        for pad_debris in range(80):
            t_deb = pad_debris * dt
            history.append({
                "t": float(t_deb), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0,
                "q": 0.0, "g": 0.0, "stage": 1, "fairing": False, "wings": False, "strapon": False,
                "exploded": True, "explosion_type": "PAD_TWR_FAIL", "thrust": False, "pitch": 0.0,
                "mach": 0.0, "event": "RUD_FALL"
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
            ax, ay, vx, vy = 0.0, 0.0, 0.0, 0.0
            acc_g = 1.0
        else:
            ax = fx / cur_mass
            ay = fy / cur_mass
            acc_g = float(np.sqrt((thrust * dir_x + drag_x + lift_x)**2 + (thrust * dir_y + drag_y + lift_y)**2) / (cur_mass * g0))

        cur_spec = s1_spec if stage == 1 else s2_spec

        # 構造破壊判定 (Max-Q または 過負荷G)
        has_exploded = False
        if q > cur_spec["max_q"]:
            fail_reason = f"Max-Q 構造圧壊: 最大動圧 ({q:.1f} kPa) が外殻耐力 ({cur_spec['max_q']:.1f} kPa) を超えて空中分解。"
            has_exploded = True
        elif acc_g > cur_spec["max_g"]:
            fail_reason = f"過大G荷重による圧壊: 加速度 ({acc_g:.1f} G) が機体限界 ({cur_spec['max_g']:.1f} G) を超えて座屈破壊。"
            has_exploded = True

        if has_exploded:
            # 爆発瞬間を記録
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g,
                "stage": int(stage), "fairing": fairing_attached, "wings": wings_attached, "strapon": strapon_attached,
                "exploded": True, "explosion_type": "STRUCTURAL_COLLAPSE", "thrust": False, "pitch": visual_pitch,
                "mach": mach, "event": "RUD_START"
            })
            # 爆発後：残骸・破片が放物線を描いて地表・海面に落ちるまでシミュレーションを継続
            debris_vx = vx * 0.75
            debris_vy = vy * 0.75
            debris_x = x
            debris_y = y
            for deb_step in range(120):
                t_deb = t + (deb_step + 1) * dt
                debris_vy -= g0 * dt
                debris_vx *= 0.985
                debris_x += debris_vx * dt
                debris_y = max(0.0, debris_y + debris_vy * dt)
                deb_alt_km = debris_y / 1000.0
                history.append({
                    "t": t_deb, "x": float(debris_x), "y": float(debris_y), "alt": deb_alt_km, "v": float(np.sqrt(debris_vx**2 + debris_vy**2)),
                    "q": 0.0, "g": 0.0, "stage": int(stage), "fairing": False, "wings": False, "strapon": False,
                    "exploded": True, "explosion_type": "STRUCTURAL_COLLAPSE", "thrust": False, "pitch": visual_pitch,
                    "mach": 0.0, "event": "RUD_FALL" if debris_y > 0 else "RUD_FINISHED"
                })
                if debris_y <= 0:
                    break
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

    if not fail_reason and history[-1]["event"] not in ["ORBIT", "REENTRY"]:
        fail_reason = f"軌道速度未達（燃料枯渇・弾道落下）。到達高度: {alt_km:.1f} km, 水平速度: {vx:.0f} m/s (LEO目標: 7,800 m/s)"

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)

cb1, cb2 = st.columns([3, 1])
with cb1:
    launch_clicked = st.button("🔴 4K 2画面中継 (近接追尾 ＆ 海岸線超望遠) ＆ シミュレーション開始", use_container_width=True, type="primary")
with cb2:
    st.caption("※ 上のタブで設定変更すると発射台上のロケットが即座に3D更新されます。")

traj_data, error_msg = run_simulation(preview_only=(not launch_clicked))

s1_len_scaled = float(np.clip(12.0 + (s1_fuel / 4500.0) * 15.0, 10.0, 28.0))
s2_len_scaled = float(np.clip(5.0 + (s2_fuel / 1500.0) * 8.0, 5.0, 14.0))

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
    "rtls_mode": bool(rtls_enabled),
    "rcs_deadband": float(rcs_deadband)
}

traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
cfg_json = json.dumps(rocket_visual_cfg)
fail_msg_clean = (error_msg or "").replace('"', '\\"').replace("'", "\\'")

# =========================================================================
# 📺 HTML / JS 完全描画テンプレート
# =========================================================================
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #01040a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none; }
        #canvas-main { width: 100%; height: 100%; display: block; }
        .vignette { position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; box-shadow: inset 0 0 160px rgba(0,0,0,0.85); z-index: 5; }
        .grain { position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index: 6; opacity: 0.032; background-image: radial-gradient(#fff 1px, transparent 1px); background-size: 3px 3px; }
        
        /* 🎥 PiP 右上独立窓 (CAM 02) */
        .pip-container { position: absolute; top: 52px; right: 20px; width: 340px; height: 195px; border: 2px solid rgba(56, 189, 248, 0.85); border-radius: 4px; z-index: 60; box-shadow: 0 14px 45px rgba(0,0,0,0.98); background: #01040a; overflow: hidden; cursor: pointer; }
        #canvas-pip { width: 100%; height: 100%; display: block; }
        .pip-tag { position: absolute; top: 6px; left: 8px; font-size: 9px; font-weight: 800; color: #fff; background: rgba(15, 23, 42, 0.92); padding: 3px 6px; border-radius: 2px; letter-spacing: 1px; font-family: monospace; z-index: 65; pointer-events: none; border-left: 2px solid #38bdf8; }
        .pip-alt { position: absolute; bottom: 6px; right: 8px; font-size: 10px; font-family: monospace; color: #38bdf8; font-weight: 700; background: rgba(15, 23, 42, 0.92); padding: 2px 6px; border-radius: 2px; z-index: 65; pointer-events: none; }
        .pip-toggle-hint { position: absolute; top: 6px; right: 8px; font-size: 9px; font-family: monospace; color: #94a3b8; background: rgba(15, 23, 42, 0.92); padding: 3px 6px; border-radius: 2px; z-index: 65; pointer-events: none; }

        /* 🛰️ 左上独立：軌道HUD */
        .hud-orbit { position: absolute; top: 52px; left: 20px; width: 320px; max-width: calc(100vw - 390px); background: rgba(3, 7, 18, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 4px; padding: 12px 14px; box-sizing: border-box; z-index: 25; color: #fff; }
        
        /* 🔝 トップバナー */
        .top-banner { position: absolute; top: 0; left: 0; width: 100%; min-height: 44px; background: rgba(2, 6, 16, 0.94); backdrop-filter: blur(16px); display: flex; align-items: center; justify-content: space-between; padding: 4px 18px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 20; flex-wrap: wrap; gap: 8px; }
        
        /* 📊 ボトムテレメトリドック (下部バグ完全解消：グラデーションバックドロップ) */
        .hud-telemetry { position: absolute; bottom: 0; left: 0; width: 100%; height: 90px; background: linear-gradient(to top, rgba(2, 6, 16, 0.96) 0%, rgba(2, 6, 16, 0.85) 60%, transparent 100%); padding: 12px 24px; box-sizing: border-box; display: flex; align-items: center; justify-content: space-between; z-index: 20; pointer-events: none; }
        .hud-telemetry > * { pointer-events: auto; }

        .rud-banner { display: none; position: absolute; top: 160px; left: 50%; transform: translateX(-50%); background: rgba(120, 10, 10, 0.94); backdrop-filter: blur(16px); border: 2px solid #ef4444; border-radius: 4px; padding: 16px 28px; z-index: 70; text-align: center; box-shadow: 0 0 60px rgba(239, 68, 68, 0.7); }
    </style>
</head>
<body>
    <canvas id="canvas-main"></canvas>
    <div class="vignette"></div>
    <div class="grain"></div>

    <!-- 🎥 望遠カメラ PiP 右上独立窓 -->
    <div id="pip-box" class="pip-container" title="クリックで表示切替">
        <canvas id="canvas-pip"></canvas>
        <div id="pip-tag" class="pip-tag">CAM 02: COASTAL TELEPHOTO (1800mm)</div>
        <div id="pip-hud-alt" class="pip-alt">ALT: 0.0 km</div>
        <div id="pip-hint" class="pip-toggle-hint">[CLICK TO TOGGLE]</div>
    </div>

    <!-- 🔝 レスポンシブトップバナー -->
    <div class="top-banner">
        <div style="display: flex; align-items: center; gap: 10px; min-width: 0;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 10px #ef4444; flex-shrink: 0;"></span>
            <span style="color: #ffffff; font-weight: 800; font-size: 11px; letter-spacing: 1.5px; white-space: nowrap;">LIVE 4K CINEMA MASTER</span>
            <span style="color: rgba(255,255,255,0.2);">|</span>
            <span id="cam-tag" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 1px; font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">CAM 01: TRACKING CINEMA CHASE</span>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; font-family: monospace; font-size: 11px; flex-wrap: wrap;">
            <span style="color: #94a3b8; white-space: nowrap;">ATMOS: <strong id="hud-regime" style="color: #f8fafc;">TROPOSPHERE</strong></span>
            <span style="color: #94a3b8; white-space: nowrap;">4-AXIS RCS: <strong id="hud-rcs" style="color: #38bdf8;">ACTIVE</strong></span>
            <span style="color: #94a3b8; white-space: nowrap;">WATER DELUGE: <strong id="hud-deluge" style="color: #38bdf8;">STANDBY</strong></span>
            <span id="comm-status" style="color: #10b981; white-space: nowrap;">TELEMETRY LOCKED</span>
        </div>
    </div>

    <!-- 🛰️ 左上独立：軌道トラジェクトリHUD ＆ 実況コールアウト -->
    <div class="hud-orbit" id="hud-orbit-box">
        <div style="font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 1.2px; margin-bottom: 4px; display: flex; justify-content: space-between;">
            <span>DOWNRANGE TRAJECTORY</span>
            <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">0.0 km</span>
        </div>
        <canvas id="orbit-canvas" width="290" height="58" style="width: 100%; height: 58px; background: #020617; border-radius: 2px; border: 1px solid rgba(255,255,255,0.08);"></canvas>
        <div id="event-log" style="margin-top: 6px; font-family: monospace; font-size: 11px; font-weight: 800; color: #34d399; border-top: 1px solid rgba(255,255,255,0.12); padding-top: 4px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
            > [LD] GO FOR TERMINAL COUNTDOWN
        </div>
        <div id="sub-callout" style="font-family: monospace; font-size: 9.5px; color: #93c5fd; margin-top: 2px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
            > Propellant tanks pressurized. Flight guidance autonomous.
        </div>
    </div>

    <div id="rud-banner" class="rud-banner">
        <div style="color: #fff; font-size: 17px; font-weight: 900; letter-spacing: 2px; font-family: monospace;">🚨 RAPID UNSCHEDULED DISASSEMBLY (RUD) 🚨</div>
        <div id="rud-desc" style="color: #fecaca; font-size: 13px; font-weight: 600; margin-top: 6px; max-width: 540px; line-height: 1.4;"></div>
    </div>

    <!-- 📊 ボトムテレメトリドック -->
    <div class="hud-telemetry">
        <div style="flex-shrink: 0;">
            <div id="tv-status" style="color: #38bdf8; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 2px;">COUNTDOWN TIMING</div>
            <div id="tv-timer" style="color: #ffffff; font-size: clamp(26px, 3.2vw, 34px); font-weight: 900; font-family: 'Consolas', monospace; letter-spacing: 2px; text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);">T- 00:10.0</div>
        </div>
        <div style="display: flex; gap: clamp(14px, 2.5vw, 32px); border-left: 1px solid rgba(255,255,255,0.15); padding-left: 18px; flex-wrap: wrap;">
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">VELOCITY / MACH</div>
                <div style="color: #fff; font-size: 17px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-mach">M 0.00</span> <span style="font-size: 10px; color: #94a3b8;" id="tv-spd">(0 km/h)</span></div>
            </div>
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">ALTITUDE</div>
                <div style="color: #fff; font-size: 17px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-alt">0.0</span> <span style="font-size: 10px; color: #94a3b8;">km</span></div>
            </div>
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">DYNAMIC PRESSURE</div>
                <div style="color: #fff; font-size: 17px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-q">0.0</span> <span style="font-size: 10px; color: #94a3b8;">kPa</span></div>
            </div>
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">ACCELERATION</div>
                <div style="color: #fff; font-size: 17px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-g">1.0</span> <span style="font-size: 10px; color: #94a3b8;">G</span></div>
            </div>
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">STAGE STATUS</div>
                <div id="tv-stage-badge" style="color: #34d399; font-size: 15px; font-weight: 800; font-family: 'Consolas', monospace; white-space: nowrap;">PAD VERIFIED</div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const simData = __SIM_DATA__;
        const simCfg = __SIM_CFG__;
        const failMessage = "__FAIL_MSG__";

        const canvasMain = document.getElementById('canvas-main');
        const canvasPip = document.getElementById('canvas-pip');
        const orbitCvs = document.getElementById('orbit-canvas');
        const octx = orbitCvs.getContext('2d');
        const rudBanner = document.getElementById('rud-banner');
        const rudDesc = document.getElementById('rud-desc');
        const eventLog = document.getElementById('event-log');
        const subCallout = document.getElementById('sub-callout');

        let pipVisible = true;
        const pipBox = document.getElementById('pip-box');
        const pipHint = document.getElementById('pip-hint');
        pipBox.addEventListener('click', () => {
            pipVisible = !pipVisible;
            canvasPip.style.display = pipVisible ? 'block' : 'none';
            document.getElementById('pip-tag').style.display = pipVisible ? 'block' : 'none';
            document.getElementById('pip-hud-alt').style.display = pipVisible ? 'block' : 'none';
            pipBox.style.height = pipVisible ? '195px' : '32px';
            pipHint.innerText = pipVisible ? '[CLICK TO HIDE]' : '[CLICK TO SHOW]';
        });

        // =========================================================================
        // 🎙️ 完全自動音声合成実況 (カウントダウンから自律稼働)
        // =========================================================================
        let voiceSynthesizer = window.speechSynthesis;
        function autoSpeak(text) {
            if (!voiceSynthesizer) return;
            try {
                voiceSynthesizer.cancel();
                const ut = new SpeechSynthesisUtterance(text);
                ut.rate = 1.18;
                ut.pitch = 0.95;
                ut.volume = 1.0;
                ut.lang = 'en-US';
                voiceSynthesizer.speak(ut);
            } catch(e) {}
        }

        window.addEventListener('DOMContentLoaded', () => { if (voiceSynthesizer) voiceSynthesizer.resume(); });
        window.addEventListener('mousemove', () => { if (voiceSynthesizer) voiceSynthesizer.resume(); }, { once: true });

        const flightMilestones = [
            { t: -10.0, main: "> [LD] TERMINAL COUNTDOWN INITIATED", sub: "> Tanks pressurized, autonomous flight lock", spoken: "Ten, nine, eight, seven" },
            { t: -simCfg.ignition_lead, main: "> [PROP] ENGINE IGNITION SEQUENCE START", sub: "> Turbopump spin-up nominal", spoken: "Ignition sequence start" },
            { t: 0.0, main: "> [LIFTOFF] VEHICLE HAS CLEARED PAD 39A", sub: "> Pitch and roll program initiated", spoken: "Liftoff. Tower cleared" },
            { t: 15.0, main: "> [GUIDANCE] GRAVITY TURN TRAJECTORY NOMINAL", sub: "> Downrange pitch sequence continuing", spoken: "Downrange trajectory nominal" },
            { t: 45.0, main: "> [AERO] VEHICLE PASSING MACH 1 - SUPERSONIC", sub: "> Transonic buffet levels nominal", spoken: "Vehicle is supersonic" },
            { t: 65.0, main: "> [AERO] MAXIMUM DYNAMIC PRESSURE (MAX-Q)", sub: "> Throttle bucket applied for stress relief", spoken: "Vehicle passing Max-Q" },
            { t: 130.0, main: "> [PROP] BOOSTER MECO & SEPARATION", sub: "> Boosters staging safely downrange", spoken: "Booster separation confirmed" },
            { t: 165.0, main: "> [STAGE] FIRST STAGE MECO & HOT STAGING", sub: "> Upper stage vacuum engine ignited", spoken: "Staging sequence complete" },
            { t: 195.0, main: "> [AERO] PAYLOAD FAIRING JETTISON", sub: "> Atmospheric exit verified", spoken: "Fairing separation" },
            { t: 480.0, main: "> [ORBIT] SECO - NOMINAL ORBITAL INSERTION", sub: "> Payload safely cruising in stable orbit", spoken: "Nominal orbital insertion confirmed" }
        ];

        let calloutTracker = 0;
        function processFlightVoice(simT) {
            while (calloutTracker < flightMilestones.length && simT >= flightMilestones[calloutTracker].t) {
                const item = flightMilestones[calloutTracker];
                if (eventLog) eventLog.innerText = item.main;
                if (subCallout) subCallout.innerText = item.sub;
                autoSpeak(item.spoken);
                calloutTracker++;
            }
        }

        // =========================================================================
        // 🔊 超重低音インフラサウンド＆音響衝撃波クラックル合成 (Web Audio API)
        // =========================================================================
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null, subRumble = null, shockCrackle = null, gasHiss = null;
        function startAudioEngine() {
            if (!actx) {
                actx = new AudioCtx();
                const buf = actx.createBuffer(1, actx.sampleRate * 4, actx.sampleRate);
                const d = buf.getChannelData(0);
                for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

                // 1. 大地を揺らす超重低音 (Sub-Rumble: 28Hz~48Hz)
                const rSrc = actx.createBufferSource(); rSrc.buffer = buf; rSrc.loop = true;
                const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 38;
                subRumble = actx.createGain(); subRumble.gain.value = 0;
                rSrc.connect(lp); lp.connect(subRumble); subRumble.connect(actx.destination);
                rSrc.start(0);

                // 2. 大気引き裂きクラックル衝撃波 (Acoustic Shockwave Crackle)
                const cSrc = actx.createBufferSource(); cSrc.buffer = buf; cSrc.loop = true;
                const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 320; bp.Q.value = 5.2;
                shockCrackle = actx.createGain(); shockCrackle.gain.value = 0;
                cSrc.connect(bp); bp.connect(shockCrackle); shockCrackle.connect(actx.destination);
                cSrc.start(0);

                // 3. 水冷デリュージ蒸気・超音速大気流風切り
                const hSrc = actx.createBufferSource(); hSrc.buffer = buf; hSrc.loop = true;
                const hp = actx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 1400;
                gasHiss = actx.createGain(); gasHiss.gain.value = 0;
                hSrc.connect(hp); hp.connect(gasHiss); gasHiss.connect(actx.destination);
                hSrc.start(0);
            }
            if (actx && actx.state === 'suspended') actx.resume();
        }
        window.addEventListener('click', startAudioEngine, { once: true });
        window.addEventListener('touchstart', startAudioEngine, { once: true });

        function playPyroBlast() {
            if (!actx) return;
            const now = actx.currentTime;
            const osc = actx.createOscillator();
            const g = actx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(85, now);
            osc.frequency.exponentialRampToValueAtTime(22, now + 0.45);
            g.gain.setValueAtTime(1.3, now);
            g.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
            osc.connect(g); g.connect(actx.destination);
            osc.start(now); osc.stop(now + 0.46);
        }

        // =========================================================================
        // 🌍 Three.js シーン ＆ 広域実写級PBR海洋・発射場環境
        // =========================================================================
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050c18);
        const sceneFog = new THREE.FogExp2(0x081426, 0.000018);
        scene.fog = sceneFog;

        const rendererMain = new THREE.WebGLRenderer({ canvas: canvasMain, antialias: true, powerPreference: "high-performance" });
        rendererMain.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        rendererMain.setSize(window.innerWidth, window.innerHeight);
        rendererMain.toneMapping = THREE.ACESFilmicToneMapping;
        rendererMain.toneMappingExposure = 1.35;
        rendererMain.shadowMap.enabled = true;
        rendererMain.shadowMap.type = THREE.PCFSoftShadowMap;

        const rendererPip = new THREE.WebGLRenderer({ canvas: canvasPip, antialias: true, powerPreference: "high-performance" });
        rendererPip.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        rendererPip.setSize(340, 195);
        rendererPip.toneMapping = THREE.ACESFilmicToneMapping;
        rendererPip.toneMappingExposure = 1.45;

        const cameraMain = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 1.0, 50000000);
        const cameraPip = new THREE.PerspectiveCamera(4.2, 340 / 195, 2.0, 50000000);
        cameraPip.position.set(-1800, 95, 2200);

        const sunLight = new THREE.DirectionalLight(0xfffaed, 5.8);
        sunLight.position.set(7500, 12000, 8500);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        scene.add(sunLight);

        const skyAmbient = new THREE.HemisphereLight(0xa5c9eb, 0x1e2733, 1.15);
        scene.add(skyAmbient);

        const engineBounceLight = new THREE.PointLight(simCfg.flame_hex, 0.0, 700, 2.0);
        scene.add(engineBounceLight);

        // 恒星
        const starGeo = new THREE.BufferGeometry();
        const starPos = new Float32Array(3500 * 3);
        for(let i=0; i<3500*3; i+=3) {
            const rad = 25000000;
            const u = Math.random(), v = Math.random();
            const th = u * 2.0 * Math.PI, ph = Math.acos(2.0 * v - 1.0);
            starPos[i] = rad * Math.sin(ph) * Math.cos(th);
            starPos[i+1] = rad * Math.sin(ph) * Math.sin(th);
            starPos[i+2] = rad * Math.cos(ph);
        }
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        const starMat = new THREE.PointsMaterial({ size: 1.8, color: 0xe2e8f0, transparent: true, opacity: 0.12 });
        scene.add(new THREE.Points(starGeo, starMat));

        // 地球本体
        const R_EARTH = 6371.0;
        const earthMesh = new THREE.Mesh(
            new THREE.SphereGeometry(R_EARTH, 64, 48),
            new THREE.MeshStandardMaterial({ color: 0x09283f, roughness: 0.82 })
        );
        earthMesh.position.set(0, -R_EARTH, 0);
        scene.add(earthMesh);

        // =========================================================================
        // 🏝️ PBR見渡す限りのリアル海洋・海岸線・複合施設群
        // =========================================================================
        const landscapeGroup = new THREE.Group();
        scene.add(landscapeGroup);

        const coastCvs = document.createElement('canvas'); coastCvs.width = 2048; coastCvs.height = 2048;
        const cctx = coastCvs.getContext('2d');
        cctx.fillStyle = '#051422'; cctx.fillRect(0, 0, 2048, 2048);
        
        const surfGrad = cctx.createLinearGradient(0, 0, 1400, 2048);
        surfGrad.addColorStop(0.35, '#07243a');
        surfGrad.addColorStop(0.52, '#0c3a50');
        surfGrad.addColorStop(0.58, '#a88a62');
        surfGrad.addColorStop(0.64, '#3f3624');
        surfGrad.addColorStop(0.70, '#1c2817');
        cctx.fillStyle = surfGrad;
        cctx.beginPath();
        cctx.moveTo(0, 0); cctx.lineTo(1380, 0);
        cctx.bezierCurveTo(1280, 600, 1040, 1300, 900, 2048);
        cctx.lineTo(0, 2048); cctx.closePath(); cctx.fill();

        cctx.fillStyle = '#141e11';
        cctx.beginPath();
        cctx.moveTo(0, 0); cctx.lineTo(1120, 0);
        cctx.bezierCurveTo(1020, 550, 860, 1250, 740, 2048);
        cctx.lineTo(0, 2048); cctx.closePath(); cctx.fill();

        const coastTex = new THREE.CanvasTexture(coastCvs);
        const coastPlane = new THREE.Mesh(
            new THREE.PlaneGeometry(80000, 80000),
            new THREE.MeshStandardMaterial({ map: coastTex, roughness: 0.92, metalness: 0.05 })
        );
        coastPlane.rotation.x = -Math.PI / 2;
        coastPlane.position.set(-2500, -1.6, 0);
        coastPlane.receiveShadow = true;
        landscapeGroup.add(coastPlane);

        const oceanMat = new THREE.MeshStandardMaterial({
            color: 0x041829, roughness: 0.10, metalness: 0.92, transparent: true, opacity: 0.97
        });
        const oceanMesh = new THREE.Mesh(new THREE.PlaneGeometry(120000, 120000), oceanMat);
        oceanMesh.rotation.x = -Math.PI / 2;
        oceanMesh.position.set(20000, -1.0, 0);
        landscapeGroup.add(oceanMesh);

        // VAB組立棟 ＆ 周辺タンクファーム群
        const vabGroup = new THREE.Group();
        vabGroup.position.set(-5800, 0, -2600);
        const vabMain = new THREE.Mesh(
            new THREE.BoxGeometry(220, 160, 240),
            new THREE.MeshStandardMaterial({ color: 0xcfdbe8, roughness: 0.45, metalness: 0.25 })
        );
        vabMain.position.y = 80;
        vabGroup.add(vabMain);
        landscapeGroup.add(vabGroup);

        for(let g=0; g<8; g++) {
            const sphereTank = new THREE.Mesh(
                new THREE.SphereGeometry(32, 32, 24),
                new THREE.MeshStandardMaterial({ color: 0xf1f5f9, metalness: 0.85, roughness: 0.25 })
            );
            sphereTank.position.set(-2400 - g * 160, 32, -1400 + g * 100);
            sphereTank.castShadow = true;
            landscapeGroup.add(sphereTank);
        }

        // =========================================================================
        // 🏗️ 発射台 Pad 39A ＆ 火炎偏向トレンチ
        // =========================================================================
        const pad = new THREE.Group();
        scene.add(pad);
        const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x1f242d, metalness: 0.92, roughness: 0.32 });
        const concreteMat = new THREE.MeshStandardMaterial({ color: 0x3d4552, roughness: 0.94 });
        const pipeMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1, metalness: 0.95, roughness: 0.18 });
        const goldFoilMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.96, roughness: 0.16 });

        const groundPlate = new THREE.Mesh(new THREE.CylinderGeometry(110, 125, 2.4, 48), concreteMat);
        groundPlate.position.y = -1.2;
        groundPlate.receiveShadow = true;
        pad.add(groundPlate);

        const flameTrench = new THREE.Mesh(new THREE.BoxGeometry(24, 12, 48), concreteMat);
        flameTrench.position.set(0, -3.0, 0);
        pad.add(flameTrench);

        const flameDeflector = new THREE.Mesh(
            new THREE.ConeGeometry(7.0, 6.0, 4),
            new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.85, metalness: 0.8 })
        );
        flameDeflector.rotation.y = Math.PI / 4;
        flameDeflector.position.set(0, 0.5, 0);
        pad.add(flameDeflector);

        const olmRing = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 4.2, 2.2, 32), darkSteelMat);
        olmRing.position.y = 5.2;
        olmRing.castShadow = true;
        pad.add(olmRing);

        const towerGroup = new THREE.Group();
        towerGroup.position.set(-11.5, 0, 0);
        pad.add(towerGroup);

        const towerMain = new THREE.Mesh(new THREE.BoxGeometry(5.2, 72.0, 5.2), darkSteelMat);
        towerMain.position.y = 36.0;
        towerMain.castShadow = true;
        towerGroup.add(towerMain);

        for(let ty = 6.0; ty < 70.0; ty += 8.0) {
            const platform = new THREE.Mesh(new THREE.BoxGeometry(7.5, 0.4, 7.5), darkSteelMat);
            platform.position.y = ty;
            towerGroup.add(platform);
        }

        const accessArm = new THREE.Mesh(new THREE.BoxGeometry(9.0, 2.4, 2.2), darkSteelMat);
        accessArm.position.set(-5.5, 52.0, 0);
        pad.add(accessArm);

        // =========================================================================
        // 🎨 高精細PBRテクスチャ生成
        // =========================================================================
        function createMaterialSkin(matId, hasHeatshield) {
            const w = 512, h = 1024;
            const diffCvs = document.createElement('canvas'); diffCvs.width = w; diffCvs.height = h;
            const dctx = diffCvs.getContext('2d');
            const bumpCvs = document.createElement('canvas'); bumpCvs.width = w; bumpCvs.height = h;
            const bctx = bumpCvs.getContext('2d');

            bctx.fillStyle = '#808080'; bctx.fillRect(0, 0, w, h);

            if (matId === 'ss') {
                dctx.fillStyle = '#d1d5db'; dctx.fillRect(0, 0, w, h);
                for(let y = 0; y < h; y += 44) {
                    const s = (Math.random() - 0.5) * 16;
                    dctx.fillStyle = `rgb(${210+s}, ${218+s}, ${228+s})`;
                    dctx.fillRect(0, y, w, 42);
                    dctx.fillStyle = 'rgba(70, 50, 30, 0.35)'; dctx.fillRect(0, y, w, 2);
                    bctx.fillStyle = '#303030'; bctx.fillRect(0, y, w, 3);
                }
            } else if (matId === 'f9_white') {
                dctx.fillStyle = '#f8fafc'; dctx.fillRect(0, 0, w, h);
                dctx.fillStyle = '#0f172a'; dctx.fillRect(0, h * 0.72, w, h * 0.08);
            } else if (matId === 'al') {
                dctx.fillStyle = '#f8fafc'; dctx.fillRect(0, 0, w, h);
                dctx.fillStyle = '#d97706'; dctx.fillRect(0, h * 0.22, w, h * 0.56);
            } else if (matId === 'saturn') {
                dctx.fillStyle = '#f8fafc'; dctx.fillRect(0, 0, w, h);
                dctx.fillStyle = '#0f172a';
                for(let i=0; i<8; i++) {
                    if (i%2===0) {
                        dctx.fillRect(i*(w/8), h*0.12, w/8, h*0.18);
                        dctx.fillRect(i*(w/8), h*0.65, w/8, h*0.20);
                    }
                }
            } else if (matId === 'cf') {
                dctx.fillStyle = '#111317'; dctx.fillRect(0, 0, w, h);
            } else if (matId === 'icbm_steel') {
                dctx.fillStyle = '#374151'; dctx.fillRect(0, 0, w, h);
                dctx.fillStyle = '#1f2937'; dctx.fillRect(0, 0, w, h * 0.15);
            } else if (matId === 'cardboard') {
                dctx.fillStyle = '#b45309'; dctx.fillRect(0, 0, w, h);
                dctx.fillStyle = '#f59e0b'; dctx.fillRect(0, h * 0.4, w, 30);
            } else {
                dctx.fillStyle = '#4b5563'; dctx.fillRect(0, 0, w, h);
            }

            for(let x = 0; x < w; x += 32) {
                bctx.fillStyle = '#555555'; bctx.fillRect(x, 0, 2, h);
                dctx.fillStyle = 'rgba(0,0,0,0.12)'; dctx.fillRect(x, 0, 2, h);
            }

            if (hasHeatshield) {
                dctx.fillStyle = '#0d0f12'; dctx.fillRect(0, 0, w * 0.48, h);
                bctx.strokeStyle = '#18181b'; bctx.lineWidth = 2;
                for(let ty = 0; ty < h; ty += 14) {
                    for(let tx = 0; tx < w * 0.48; tx += 14) {
                        bctx.strokeRect(tx + (ty%28===0?0:7), ty, 13, 13);
                    }
                }
            }

            const sootGrad = dctx.createLinearGradient(0, h * 0.78, 0, h);
            sootGrad.addColorStop(0, 'rgba(10,12,16,0)');
            sootGrad.addColorStop(1, 'rgba(10,12,16,0.75)');
            dctx.fillStyle = sootGrad; dctx.fillRect(0, h * 0.78, w, h * 0.22);

            return {
                map: new THREE.CanvasTexture(diffCvs),
                bumpMap: new THREE.CanvasTexture(bumpCvs)
            };
        }

        // =========================================================================
        // 🔥 ノズル直結 GLSL実写級バーナー炎
        // =========================================================================
        const plumeShaderMat = new THREE.ShaderMaterial({
            transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
            uniforms: {
                uTime: { value: 0.0 },
                uVacFactor: { value: 0.0 },
                uGroundCut: { value: 0.0 },
                uCoreColor: { value: new THREE.Color(0xffffff) },
                uMidColor: { value: new THREE.Color(simCfg.flame_hex) },
                uOuterColor: { value: new THREE.Color(simCfg.outer_hex) }
            },
            vertexShader: `
                varying vec2 vUv;
                uniform float uTime;
                uniform float uVacFactor;
                uniform float uGroundCut;
                void main() {
                    vUv = uv;
                    vec3 pos = position;
                    float dist = 1.0 - uv.y;
                    float deflect = uGroundCut * pow(dist, 1.8) * 3.5;
                    float bellExpand = pow(dist, 0.65) * (0.8 + uVacFactor * 4.2) + deflect;
                    float turb = sin(dist * 32.0 - uTime * 65.0) * 0.08 * dist;
                    pos.x *= (1.0 + bellExpand + turb);
                    pos.z *= (1.0 + bellExpand + turb);
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
                }
            `,
            fragmentShader: `
                varying vec2 vUv;
                uniform float uTime;
                uniform float uVacFactor;
                uniform float uGroundCut;
                uniform vec3 uCoreColor;
                uniform vec3 uMidColor;
                uniform vec3 uOuterColor;

                void main() {
                    float distFromNozzle = 1.0 - vUv.y;
                    float radial = abs(vUv.x - 0.5) * 2.0;

                    float waveFreq = 26.0 / (1.0 + uVacFactor * 1.5);
                    float shockWave = pow(max(0.0, cos(distFromNozzle * waveFreq - uTime * 25.0)), 6.0);
                    float shockFade = max(0.0, 1.0 - uVacFactor * 1.4) * exp(-distFromNozzle * 2.5);

                    float coreMask = exp(-radial * radial * 9.0) * exp(-distFromNozzle * 1.6);
                    float plumeBody = exp(-radial * radial * 3.2) * pow(1.0 - distFromNozzle, 1.2);
                    float noise = 0.88 + 0.12 * sin(distFromNozzle * 50.0 - uTime * 80.0 + radial * 14.0);

                    vec3 col = mix(uOuterColor, uMidColor, plumeBody);
                    col = mix(col, uCoreColor, clamp(coreMask + shockWave * shockFade * 0.95, 0.0, 1.0));

                    float groundFade = 1.0 - smoothstep(1.0 - uGroundCut * 0.45, 1.0, distFromNozzle);
                    float tipFade = smoothstep(0.0, 0.015, distFromNozzle) * smoothstep(1.0, 0.10, distFromNozzle);
                    float alpha = clamp((plumeBody * 0.95 + coreMask * 0.85) * tipFade * groundFade * noise, 0.0, 1.0);

                    gl_FragColor = vec4(col * 2.5, alpha);
                }
            `
        });

        function createNozzlePlumeMesh(jetWidth, jetLength) {
            const jetGroup = new THREE.Group();
            for(let rAngle of [0, Math.PI / 2]) {
                const pPlane = new THREE.Mesh(new THREE.PlaneGeometry(jetWidth, jetLength, 8, 32), plumeShaderMat);
                pPlane.position.y = -jetLength / 2;
                pPlane.rotation.y = rAngle;
                jetGroup.add(pPlane);
            }
            return jetGroup;
        }

        const s1NozzleTips = [];
        const s2NozzleTips = [];
        const boosterNozzleTips = [];

        const inconelNozzleMat = new THREE.MeshStandardMaterial({ color: 0x374151, metalness: 0.95, roughness: 0.22, side: THREE.DoubleSide });

        function buildEngineCluster(parent, count, radius, basePosY, epsScale, cycId, tipArray, jetLen) {
            const group = new THREE.Group();
            group.position.y = basePosY;
            const bellH = 1.15 * epsScale;
            const bellW = 0.24 * Math.pow(epsScale, 0.65);

            const nozzlePts = [];
            for(let i=0; i<=16; i++) {
                const t = i / 16;
                nozzlePts.push(new THREE.Vector2(0.08 + bellW * Math.pow(t, 0.62), -t * bellH));
            }
            const bellGeo = new THREE.LatheGeometry(nozzlePts, 24);
            const visualPlumeStep = Math.max(1, Math.floor(count / 6));

            for(let i=0; i<count; i++) {
                const ang = (i / count) * Math.PI * 2;
                const r = (count === 1) ? 0 : (i < 3 && count > 6 ? radius * 0.38 : radius);
                const engUnit = new THREE.Group();
                engUnit.position.set(Math.cos(ang)*r, 0, Math.sin(ang)*r);

                const bell = new THREE.Mesh(bellGeo, inconelNozzleMat);
                bell.castShadow = true;
                engUnit.add(bell);

                const manifold = new THREE.Mesh(new THREE.TorusGeometry(0.14 * epsScale, 0.03, 8, 16), pipeMat);
                manifold.rotation.x = Math.PI / 2; manifold.position.y = -0.22;
                engUnit.add(manifold);

                if (i % visualPlumeStep === 0 || i === 0) {
                    const tipObj = new THREE.Object3D();
                    tipObj.position.set(0, -bellH * 0.92, 0);
                    const plumeMesh = createNozzlePlumeMesh(bellW * 6.5, jetLen);
                    tipObj.add(plumeMesh);
                    engUnit.add(tipObj);
                    tipArray.push({ node: tipObj, plume: plumeMesh });
                }
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

        const s1Maps = createMaterialSkin(simCfg.s1_mat, false);
        const s2Maps = createMaterialSkin(simCfg.s2_mat, true);

        const s1Mat = new THREE.MeshStandardMaterial({
            map: s1Maps.map, bumpMap: s1Maps.bumpMap, bumpScale: 0.04,
            metalness: (simCfg.s1_mat === 'ss') ? 0.94 : 0.25,
            roughness: (simCfg.s1_mat === 'ss') ? 0.14 : 0.42
        });
        const s2Mat = new THREE.MeshStandardMaterial({
            map: s2Maps.map, bumpMap: s2Maps.bumpMap, bumpScale: 0.045,
            metalness: (simCfg.s2_mat === 'ss') ? 0.90 : 0.28,
            roughness: (simCfg.s2_mat === 'ss') ? 0.16 : 0.45
        });

        const s1Len = simCfg.s1_len;
        const interLen = 2.2;
        const s2Len = simCfg.s2_len;
        const s2BaseY = s1Len + interLen;

        const s1Group = new THREE.Group();
        rocket.add(s1Group);

        const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, 64), s1Mat);
        s1Body.position.y = s1Len / 2;
        s1Body.castShadow = true;
        s1Body.receiveShadow = true;
        s1Group.add(s1Body);

        for(let side of [-1, 1]) {
            const loxPipe = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, s1Len * 0.88, 16), pipeMat);
            loxPipe.position.set(0, s1Len * 0.46, side * 1.14); s1Group.add(loxPipe);
        }

        const interstage = new THREE.Group();
        interstage.position.y = s1Len + interLen / 2;
        s1Group.add(interstage);
        const interRingTop = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, 0.35, 64), darkSteelMat);
        interRingTop.position.y = interLen/2 - 0.17; interstage.add(interRingTop);
        const interRingBot = interRingTop.clone(); interRingBot.position.y = -interLen/2 + 0.17; interstage.add(interRingBot);

        const s1EpsScale = 0.75 + (simCfg.s1_eps / 70.0) * 0.75;
        const s1Engines = buildEngineCluster(s1Group, simCfg.s1_eng, 0.78, 0.0, s1EpsScale, simCfg.s1_cyc, s1NozzleTips, 32.0);

        // 空力フィン
        const wingsGroup = new THREE.Group();
        s1Group.add(wingsGroup);
        const aoaRad = (simCfg.aoa * Math.PI) / 180.0;

        if (simCfg.wing_id === 'grid') {
            for(let i=0; i<4; i++) {
                const ang = (i / 4) * Math.PI * 2 + Math.PI / 4;
                const gfFrame = new THREE.Group();
                gfFrame.position.set(Math.cos(ang)*1.22, s1Len - 1.1, Math.sin(ang)*1.22);
                gfFrame.rotation.y = -ang; gfFrame.rotation.z = aoaRad;
                const gridBox = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.14, 1.25), new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.3, wireframe: true }));
                gridBox.position.x = 0.62; gfFrame.add(gridBox);
                wingsGroup.add(gfFrame);
            }
        } else if (simCfg.wing_id === 'starship_flap') {
            for(let side of [-1, 1]) {
                const aftFlap = new THREE.Mesh(new THREE.BoxGeometry(1.6, 4.2, 0.12), darkSteelMat);
                aftFlap.position.set(side * 1.7, 2.8, 0); aftFlap.rotation.z = side * 0.15; aftFlap.rotation.x = aoaRad;
                wingsGroup.add(aftFlap);
            }
        } else if (simCfg.wing_id === 'icbm_fin') {
            for(let i=0; i<4; i++) {
                const ang = (i / 4) * Math.PI * 2;
                const fin = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2.2, 0.08), darkSteelMat);
                fin.position.set(Math.cos(ang)*1.4, 1.6, Math.sin(ang)*1.4);
                fin.rotation.y = -ang;
                wingsGroup.add(fin);
            }
        }

        // 外部ブースター群
        const boosterUnits = [];
        if (simCfg.strapon_count > 0) {
            const sCount = simCfg.strapon_count;
            for(let i=0; i<sCount; i++) {
                const angle = (i / sCount) * Math.PI * 2;
                const bx = Math.cos(angle) * 2.15, bz = Math.sin(angle) * 2.15;
                const bUnit = new THREE.Group();
                bUnit.position.set(bx, 0, bz);

                const bLen = s1Len * 0.82;
                let bMat = s1Mat;
                if (simCfg.strapon_type === 'srb') {
                    bMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.35 });
                }

                const bBody = new THREE.Mesh(new THREE.CylinderGeometry(0.68, 0.68, bLen, 36), bMat);
                bBody.position.y = bLen / 2;
                bBody.castShadow = true;
                bUnit.add(bBody);

                const bNose = new THREE.Mesh(new THREE.ConeGeometry(0.68, 1.9, 36), bMat);
                bNose.position.y = bLen + 0.95; bUnit.add(bNose);

                const localTips = [];
                buildEngineCluster(bUnit, 1, 0, 0, 1.0, 'sc', localTips, 26.0);
                localTips.forEach(t => boosterNozzleTips.push(t));

                rocket.add(bUnit);
                boosterUnits.push({
                    mesh: bUnit, angle: angle, baseX: bx, baseZ: bz,
                    detached: false, vx: 0, vy: 0, vz: 0, rx: 0, rz: 0, bLen: bLen, tips: localTips
                });
            }
        }

        // 第2段オービター
        const s2Group = new THREE.Group();
        s2Group.position.y = s2BaseY;
        rocket.add(s2Group);

        const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, 64), s2Mat);
        s2Body.position.y = s2Len / 2;
        s2Body.castShadow = true;
        s2Group.add(s2Body);

        const s2EpsScale = 1.0 + (simCfg.s2_eps / 280.0) * 1.1;
        const s2Engines = buildEngineCluster(s2Group, simCfg.s2_eng, 0.55, 0.0, s2EpsScale, simCfg.s2_cyc, s2NozzleTips, 34.0);
        s2NozzleTips.forEach(t => { t.plume.visible = false; });

        const payloadGroup = new THREE.Group();
        payloadGroup.position.y = s2Len + 1.8;
        s2Group.add(payloadGroup);
        const satBus = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 2.4, 16), goldFoilMat);
        payloadGroup.add(satBus);

        const fairingHalves = [];
        const ogivePts = [];
        const noseH = 5.4;
        for(let i=0; i<=30; i++) {
            const t = i / 30;
            ogivePts.push(new THREE.Vector2(Math.max(0.01, 1.12 * Math.pow(1.0 - Math.pow(t, 1.65), 0.72)), t * noseH));
        }
        for(let side of [-1, 1]) {
            const halfGeo = new THREE.LatheGeometry(ogivePts, 32, (side === 1) ? 0 : Math.PI, Math.PI);
            const halfMesh = new THREE.Mesh(halfGeo, s2Mat);
            halfMesh.position.y = s2Len;
            s2Group.add(halfMesh);
            fairingHalves.push({ mesh: halfMesh, side: side, detached: false, vx: 0, vy: 0, rotZ: 0 });
        }

        // =========================================================================
        // 🛰️ 実機クアッドポッド 4象限RCSスラスタ (+Pitch, -Pitch, +Yaw, -Yaw)
        // =========================================================================
        const rcsNozzles = [];
        const rcsDirs = [
            { id: "+Pitch", dx:  1, dy:  0, dz:  0 },
            { id: "-Pitch", dx: -1, dy:  0, dz:  0 },
            { id: "+Yaw",   dx:  0, dy:  0, dz:  1 },
            { id: "-Yaw",   dx:  0, dy:  0, dz: -1 }
        ];

        for(let d of rcsDirs) {
            const blockS2 = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.35, 0.2), darkSteelMat);
            blockS2.position.set(d.dx * 1.16, s2Len - 0.7, d.dz * 1.16);
            s2Group.add(blockS2);
            rcsNozzles.push({ node: blockS2, isS1: false, dir: d });

            const blockS1 = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.35, 0.2), darkSteelMat);
            blockS1.position.set(d.dx * 1.16, s1Len - 0.8, d.dz * 1.16);
            s1Group.add(blockS1);
            rcsNozzles.push({ node: blockS1, isS1: true, dir: d });
        }

        // =========================================================================
        // ✨ 実写級パーティクルシステム ＆ 破片物理オブジェクト群
        // =========================================================================
        function createCloudTexture() {
            const c = document.createElement('canvas'); c.width = 128; c.height = 128;
            const ctx = c.getContext('2d');
            const g = ctx.createRadialGradient(64, 64, 4, 64, 64, 64);
            g.addColorStop(0, 'rgba(255,255,255,0.75)');
            g.addColorStop(0.3, 'rgba(240,245,250,0.45)');
            g.addColorStop(0.7, 'rgba(180,195,210,0.15)');
            g.addColorStop(1, 'rgba(160,175,190,0)');
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

        const P_MAX = 950;
        const pool = [];
        const pGroup = new THREE.Group(); scene.add(pGroup);
        for(let i=0; i<P_MAX; i++) {
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: cloudTex, transparent: true, opacity: 0, depthWrite: false }));
            sp.visible = false; pGroup.add(sp);
            pool.push({ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 5, o: 0.8 });
        }
        let pIdx = 0;
        function emitParticle(x, y, z, vx, vy, vz, s0, s1, life, opacity, hexColor, additive) {
            const p = pool[pIdx]; pIdx = (pIdx + 1) % P_MAX;
            p.active = true; p.sp.visible = true;
            p.sp.position.set(x, y, z);
            p.vx = vx; p.vy = vy; p.vz = vz;
            p.age = 0; p.maxAge = life; p.s0 = s0; p.s1 = s1; p.o = opacity;
            p.sp.material.color.setHex(hexColor);
            p.sp.material.blending = additive ? THREE.AdditiveBlending : THREE.NormalBlending;
        }

        const SPARK_MAX = 400;
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
            s.sp.position.set(x, y, z);
            s.vx = vx; s.vy = vy; s.vz = vz;
            s.age = 0; s.maxAge = life; s.size = size;
            s.sp.scale.set(size, size * 1.8, 1);
            s.sp.material.color.setHex(hexCol);
            s.sp.material.opacity = 1.0;
        }

        // 💥 空中分解・爆発破片オブジェクト群
        const debrisMeshGroup = new THREE.Group();
        scene.add(debrisMeshGroup);
        const debrisPieces = [];
        for(let i=0; i<35; i++) {
            const dGeo = new THREE.BoxGeometry(0.8 + Math.random()*1.2, 0.4 + Math.random()*1.0, 0.2 + Math.random()*0.5);
            const dMesh = new THREE.Mesh(dGeo, darkSteelMat);
            dMesh.visible = false;
            debrisMeshGroup.add(dMesh);
            debrisPieces.push({ mesh: dMesh, active: false, vx: 0, vy: 0, vz: 0, rx: 0, ry: 0, rz: 0 });
        }

        function triggerDebrisExplosion(cx, cy, cz, baseVx, baseVy) {
            for(let p of debrisPieces) {
                p.active = true;
                p.mesh.visible = true;
                p.mesh.position.set(cx + (Math.random()-0.5)*3.0, cy + (Math.random()-0.5)*6.0, cz + (Math.random()-0.5)*3.0);
                p.vx = baseVx * 0.4 + (Math.random()-0.5) * 18.0;
                p.vy = baseVy * 0.4 + (Math.random()-0.2) * 16.0;
                p.vz = (Math.random()-0.5) * 18.0;
                p.rx = (Math.random()-0.5) * 0.2;
                p.ry = (Math.random()-0.5) * 0.2;
                p.rz = (Math.random()-0.5) * 0.2;
            }
        }

        function drawOrbitMap(altKm, dRangeKm, exploded) {
            octx.clearRect(0, 0, 290, 58);
            octx.beginPath(); octx.arc(145, 150, 130, Math.PI, 0); octx.strokeStyle = '#1e293b'; octx.lineWidth = 2.5; octx.stroke();
            const px = 14 + Math.min(262, (dRangeKm / 1200.0) * 262);
            const py = 50 - Math.min(42, (altKm / 200.0) * 42);
            octx.beginPath(); octx.moveTo(14, 50); octx.quadraticCurveTo(px * 0.5, 50, px, py);
            octx.strokeStyle = exploded ? '#ef4444' : '#38bdf8'; octx.lineWidth = 2.0; octx.stroke();
            octx.fillStyle = exploded ? '#dc2626' : '#38bdf8';
            octx.beginPath(); octx.arc(px, py, 3.5, 0, Math.PI * 2); octx.fill();
        }

        // =========================================================================
        // 🎥 カメラ追随制御
        // =========================================================================
        const smoothOffset = new THREE.Vector3(75.0, 26.0, 145.0);
        const activeFocusWorld = new THREE.Vector3();
        let camShake = 0.0;

        function updateDualCameraTracking(simT, elapsedSec, alt, pitch, stage, exploded, rudFinished) {
            rocket.updateMatrixWorld(true);
            if (stage === 2) {
                activeFocusWorld.set(0, s2Len * 0.45, 0);
                s2Group.localToWorld(activeFocusWorld);
            } else {
                activeFocusWorld.set(0, s1Len * 0.52, 0);
                rocket.localToWorld(activeFocusWorld);
            }

            cameraPip.lookAt(activeFocusWorld);
            document.getElementById('pip-hud-alt').innerText = `ALT: ${Math.max(0, alt).toFixed(1)} km`;

            if (simCfg.is_preview) {
                document.getElementById('cam-tag').innerText = "PAD INSPECTION: LIVE 3D CINEMA VIEW";
                const orbitAng = elapsedSec * 0.22;
                cameraMain.position.set(Math.sin(orbitAng) * 115.0, 28.0 + Math.sin(elapsedSec * 0.3) * 10.0, Math.cos(orbitAng) * 115.0);
                cameraMain.lookAt(0, 6.0 + (s1Len + s2Len) * 0.45, 0);
                return;
            }

            const desiredOffset = new THREE.Vector3();
            if (exploded) {
                document.getElementById('cam-tag').innerText = rudFinished ? "CAM 01: IMPACT SITE OPTICAL RADAR" : "CAM 01: HIGH-SPEED DEBRIS CHASE";
                desiredOffset.set(95.0, 42.0, 210.0);
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

        // =========================================================================
        // ⏱️ アニメーション・メインループ (破片落下継続・完全消滅後メッセージ表示)
        // =========================================================================
        const tStart = performance.now();
        let boosterDetached = false;
        let stage1Detached = false;
        let fairingDetached = false;
        let explosionTriggered = false;
        let rudFinished = false;
        let s1Vel = { vx: 0, vy: 0, rotZ: 0 };
        let prevPitch = 0.0;
        let prevSimT = -10.0;
        const tempTipPos = new THREE.Vector3();

        function animate(now) {
            requestAnimationFrame(animate);

            const elapsedSec = (now - tStart) / 1000.0;
            const simT = simCfg.is_preview ? -10.0 : (-10.0 + elapsedSec);
            plumeShaderMat.uniforms.uTime.value = elapsedSec;

            if (!simCfg.is_preview) {
                processFlightVoice(simT);
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

            if (p0.event === "RUD_FINISHED" || (p0.exploded && ry <= 0 && simT > p0.t + 4.0)) {
                rudFinished = true;
            }

            if (simT > simData[simData.length - 1].t) {
                const overT = simT - simData[simData.length - 1].t;
                if (!p0.exploded) {
                    rx += vel * overT * 0.1;
                    q = 0.0;
                    accG = 0.0;
                } else {
                    rudFinished = true;
                }
            }

            const dRangeKm = (rx * 10.0) / 1000.0;

            // 爆発時はロケット本体を非表示にし、破片モデルを散開
            if (p0.exploded) {
                rocket.visible = false;
                if (!explosionTriggered) {
                    explosionTriggered = true;
                    playPyroBlast();
                    camShake = 0.85;
                    triggerDebrisExplosion(rx, ry + 6.0, 0, (vel * 0.1) * Math.sin(pitch), (vel * 0.1) * Math.cos(pitch));

                    for(let expP=0; expP<30; expP++) {
                        emitParticle(
                            rx + (Math.random()-0.5)*4.0, ry + 6.0 + (Math.random()-0.5)*8.0, (Math.random()-0.5)*4.0,
                            (Math.random()-0.5)*24.0, (Math.random()-0.5)*24.0, (Math.random()-0.5)*24.0,
                            4.0, 48.0, 90, 0.95, 0xf97316, true
                        );
                    }
                }
            } else {
                rocket.position.set(rx, ry + 6.0, 0);
                rocket.rotation.z = -pitch;
                rocket.updateMatrixWorld(true);
            }

            // 破片の慣性・重力物理演算
            if (explosionTriggered) {
                for(let piece of debrisPieces) {
                    if (!piece.active) continue;
                    piece.mesh.position.x += piece.vx * 0.016;
                    piece.mesh.position.y += piece.vy * 0.016;
                    piece.mesh.position.z += piece.vz * 0.016;
                    piece.vy -= 9.8 * 0.016 * 1.1; // 重力落下
                    piece.vx *= 0.992; // 空気減速
                    piece.mesh.rotation.x += piece.rx;
                    piece.mesh.rotation.y += piece.ry;
                    piece.mesh.rotation.z += piece.rz;

                    // 落下中に白煙を曳く
                    if (piece.mesh.position.y > 0 && Math.random() < 0.35) {
                        emitParticle(
                            piece.mesh.position.x, piece.mesh.position.y, piece.mesh.position.z,
                            (Math.random()-0.5)*0.5, -0.2, (Math.random()-0.5)*0.5,
                            1.5, 12.0, 45, 0.45, 0xd1d5db, false
                        );
                    }
                    // 地面・海面に衝突したら停止
                    if (piece.mesh.position.y <= 0) {
                        piece.mesh.position.y = 0;
                        piece.vx = 0; piece.vy = 0; piece.vz = 0;
                    }
                }
            }

            starMat.opacity = Math.min(0.95, 0.12 + (alt / 45.0) * 0.85);
            const fogFactor = Math.max(0.0, 1.0 - (alt / 35.0));
            sceneFog.density = 0.000018 * fogFactor;

            const ux = Math.sin(pitch), uy = Math.cos(pitch);
            const perpX = Math.cos(pitch), perpY = -Math.sin(pitch);

            // 1. ブースター自然分離
            if (!p0.strapon && !boosterDetached && boosterUnits.length > 0 && !simCfg.is_preview) {
                boosterDetached = true;
                playPyroBlast();

                for(let b of boosterUnits) {
                    b.detached = true;
                    b.tips.forEach(t => { t.plume.visible = false; });
                    scene.attach(b.mesh);
                    const outX = Math.cos(b.angle);
                    const outZ = Math.sin(b.angle);
                    const sepP = simCfg.sep_thrust;
                    b.vx = ux * (vel * 0.065) + perpX * outX * (1.2 * sepP);
                    b.vy = uy * (vel * 0.065) + perpY * outX * (1.2 * sepP) - 0.4;
                    b.vz = outZ * (1.5 * sepP);
                    b.rx = outZ * 0.25;
                    b.rz = -outX * 0.25;
                }
            }
            if (boosterDetached) {
                for(let b of boosterUnits) {
                    b.mesh.position.x += b.vx * 0.016;
                    b.mesh.position.y += b.vy * 0.016;
                    b.mesh.position.z += b.vz * 0.016;
                    b.vx *= 0.992;
                    b.vy -= 9.8 * 0.016 * 0.85;
                    b.mesh.rotation.x += b.rx * 0.016;
                    b.mesh.rotation.z += b.rz * 0.016;

                    if (Math.random() < 0.20) {
                        emitParticle(
                            b.mesh.position.x, b.mesh.position.y, b.mesh.position.z,
                            (Math.random()-0.5)*0.3, -0.6, (Math.random()-0.5)*0.3,
                            2.5, 12.0, 30, 0.35, 0xd1d5db, false
                        );
                    }
                }
            }

            // 2. 第1段分離 ＆ RTLS帰還
            if (p0.stage === 2 && !stage1Detached && !simCfg.is_preview) {
                stage1Detached = true;
                playPyroBlast();

                s1NozzleTips.forEach(t => { t.plume.visible = false; });
                s2NozzleTips.forEach(t => { t.plume.visible = true; });
                plumeShaderMat.uniforms.uMidColor.value.setHex(simCfg.s2_flame_hex);
                plumeShaderMat.uniforms.uOuterColor.value.setHex(simCfg.s2_outer_hex);

                scene.attach(s1Group);
                s1Vel.vx = ux * (vel * 0.065) - ux * 4.2;
                s1Vel.vy = uy * (vel * 0.065) - uy * 4.2;
                s1Vel.rotZ = simCfg.rtls_mode ? -0.25 : 0.35;

                for(let k=0; k<14; k++) {
                    const ang = (k / 14) * Math.PI * 2;
                    emitParticle(
                        rx + Math.cos(ang)*2.2, ry + s1Len, Math.sin(ang)*2.2,
                        Math.cos(ang)*5.0, (Math.random()-0.5)*1.5, Math.sin(ang)*5.0,
                        3.0, 20.0, 35, 0.85, simCfg.s2_flame_hex, true
                    );
                }
            }
            if (stage1Detached) {
                s1Group.position.x += s1Vel.vx * 0.016;
                s1Group.position.y += s1Vel.vy * 0.016;
                
                if (simCfg.rtls_mode) {
                    s1Group.rotation.z += (Math.PI - s1Group.rotation.z) * 0.02;
                    s1Vel.vx *= 0.985;
                    s1Vel.vy -= 9.8 * 0.016 * 0.4;
                    if (s1Group.position.y < 350.0 && s1Group.position.y > 60.0 && Math.random() < 0.5) {
                        emitParticle(
                            s1Group.position.x, s1Group.position.y, s1Group.position.z,
                            0, -3.5, 0, 1.8, 14.0, 25, 0.75, 0xfde047, true
                        );
                    }
                } else {
                    s1Vel.vy -= 9.8 * 0.016 * 0.95;
                    s1Group.rotation.z += s1Vel.rotZ * 0.016;
                }
            }

            // 3. フェアリング分離
            if (!p0.fairing && !fairingDetached && fairingHalves.length > 0 && !simCfg.is_preview) {
                fairingDetached = true;
                playPyroBlast();
                for(let fh of fairingHalves) {
                    fh.detached = true;
                    scene.attach(fh.mesh);
                    fh.vx = ux * (vel * 0.068) + perpX * fh.side * 4.8;
                    fh.vy = uy * (vel * 0.068) + perpY * fh.side * 4.8 - 1.5;
                    fh.rotZ = -fh.side * 0.8;
                }
            }
            if (fairingDetached) {
                for(let fh of fairingHalves) {
                    fh.mesh.position.x += fh.vx * 0.016;
                    fh.mesh.position.y += fh.vy * 0.016;
                    fh.vy -= 9.8 * 0.016 * 0.75;
                    fh.mesh.rotation.z += fh.rotZ * 0.016;
                }
            }

            // 4. バーナー火炎
            if (p0.thrust && !p0.exploded && !simCfg.is_preview) {
                const vacFactor = Math.min(1.0, alt / 65.0);
                plumeShaderMat.uniforms.uVacFactor.value = vacFactor;

                const groundProximity = Math.max(0.0, Math.min(1.0, (18.0 - ry) / 18.0));
                plumeShaderMat.uniforms.uGroundCut.value = groundProximity;

                const activeTips = (p0.stage === 1) ? [...s1NozzleTips] : [...s2NozzleTips];
                if (p0.stage === 1 && !boosterDetached) {
                    activeTips.push(...boosterNozzleTips);
                }
                const curSparkHex = (p0.stage === 1) ? simCfg.spark_hex : simCfg.s2_spark_hex;

                for(let tObj of activeTips) {
                    tObj.plume.visible = true;
                    tObj.node.getWorldPosition(tempTipPos);

                    for(let spk=0; spk<2; spk++) {
                        emitNozzleSpark(
                            tempTipPos.x + (Math.random()-0.5)*0.2,
                            tempTipPos.y + (Math.random()-0.5)*0.2,
                            tempTipPos.z + (Math.random()-0.5)*0.2,
                            -ux * (1.6 + Math.random()*1.8),
                            -uy * (1.6 + Math.random()*1.8),
                            (Math.random()-0.5)*0.4,
                            0.45 + Math.random()*0.4,
                            12 + Math.floor(Math.random()*10),
                            (Math.random() < 0.4) ? 0xffffff : curSparkHex
                        );
                    }

                    if (ry < 15.0 && Math.random() < 0.6) {
                        const spreadSide = (Math.random() - 0.5) * 2.0;
                        emitParticle(
                            tempTipPos.x + spreadSide * 2.0, 1.0, (Math.random()-0.5)*4.0,
                            spreadSide * (3.5 + Math.random()*2.5), 0.2 + Math.random()*0.5, (Math.random()-0.5)*2.5,
                            3.5, 22.0, 45, 0.85, 0xf1f5f9, false
                        );
                    }
                }

                engineBounceLight.intensity = Math.max(0.0, 6.5 - alt * 0.35);
                engineBounceLight.position.set(rx, ry + 3.0, 4.0);

                const gimbalAngle = Math.sin(now * 0.016) * 0.035;
                s1Engines.rotation.z = gimbalAngle;
                s2Engines.rotation.z = gimbalAngle;
            } else {
                s1NozzleTips.forEach(t => { t.plume.visible = false; });
                s2NozzleTips.forEach(t => { t.plume.visible = false; });
                boosterNozzleTips.forEach(t => { t.plume.visible = false; });
                engineBounceLight.intensity = 0.0;
            }

            // =====================================================================
            // 🤖 5. 4象限RCSスラスタ実機パルス噴射 (+Pitch/-Pitch/+Yaw/-Yaw)
            // =========================================================================
            const dtReal = Math.max(0.001, simT - prevSimT);
            const pitchRate = (pitch - prevPitch) / dtReal;
            prevPitch = pitch;
            prevSimT = simT;
            let rcsFiring = false;

            const deadband = (simCfg.rcs_deadband * Math.PI) / 180.0;
            const targetPitchProg = (alt > 2.0 && alt < 120.0);
            const pitchError = targetPitchProg ? (pitch - Math.atan2(ux, uy)) : 0.0;
            const needsPitchUp = (pitchRate < -0.004) || (pitchError < -deadband);
            const needsPitchDown = (pitchRate > 0.004) || (pitchError > deadband);
            const pulseClock = (now % 650) < 110;

            for(let rcs of rcsNozzles) {
                let shouldFire = false;
                if (!simCfg.is_preview && simT > 2.0 && pulseClock && !rcs.isS1) {
                    if (rcs.dir.id === "+Pitch" && needsPitchUp) shouldFire = true;
                    if (rcs.dir.id === "-Pitch" && needsPitchDown) shouldFire = true;
                }
                if (stage1Detached && rcs.isS1 && rcs.dir.id === "+Pitch" && (now % 500) < 110) {
                    shouldFire = true;
                }

                if (shouldFire) {
                    rcsFiring = true;
                    rcs.node.getWorldPosition(tempTipPos);
                    const jetX = rcs.dir.dx * 3.8;
                    const jetZ = rcs.dir.dz * 3.8;
                    emitParticle(
                        tempTipPos.x + rcs.dir.dx * 0.35, tempTipPos.y, tempTipPos.z + rcs.dir.dz * 0.35,
                        jetX, 0.2, jetZ,
                        0.32, 2.4, 10, 0.92, 0xf0f9ff, false
                    );
                }
            }
            document.getElementById('hud-rcs').innerText = rcsFiring ? "QUAD PULSE (GN2)" : "STANDBY (DEADBAND OK)";
            document.getElementById('hud-rcs').style.color = rcsFiring ? "#34d399" : "#38bdf8";

            updateDualCameraTracking(simT, elapsedSec, alt, pitch, p0.stage, p0.exploded, rudFinished);
            drawOrbitMap(alt, dRangeKm, p0.exploded);

            // 6. カウントダウン・水冷注水・点火・離床
            if (simT < 0.0) {
                const sec = Math.ceil(Math.abs(simT));
                document.getElementById('tv-timer').innerText = simCfg.is_preview ? "PAD INSPECTION" : `T- 00:0${sec}.0`;

                emitParticle(rx + 1.25, ry + 6.0 + s1Len * 0.85, 0, 0.25, 0.04, 0, 0.9, 4.2, 45, 0.35, 0xffffff, false);

                if (simT >= -5.0 && !p0.exploded && !simCfg.is_preview) {
                    document.getElementById('hud-deluge').innerText = "WATER DELUGE ACTIVE";
                    document.getElementById('hud-deluge').style.color = "#34d399";
                    if (gasHiss && actx) gasHiss.gain.setTargetAtTime(0.55, actx.currentTime, 0.2);
                    for(let i=0; i<8; i++) {
                        emitParticle(
                            rx + (Math.random()-0.5)*8, 0.8, (Math.random()-0.5)*8,
                            (Math.random()-0.5)*1.4, 0.2 + Math.random()*0.4, (Math.random()-0.5)*1.4,
                            4.5, 22.0, 55, 0.85, 0xf0f9ff, false
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
                    camShake = 0.35;
                    for(let i=0; i<10; i++) {
                        const side = (i%2 === 0) ? 1 : -1;
                        emitParticle(
                            rx + (Math.random()-0.5)*6, 1.2, (Math.random()-0.5)*6,
                            side * (1.6 + Math.random()*2.8), 0.2 + Math.random()*0.5, (Math.random()-0.5)*1.2,
                            6.0, 38.0, 80, 0.92, 0xf8fafc, false
                        );
                    }
                }
            } else if (!p0.exploded) {
                const m = Math.floor(simT / 60); const s = simT % 60;
                document.getElementById('tv-timer').innerText = `T+ ${String(m).padStart(2,'0')}:${s.toFixed(1).padStart(4,'0')}`;

                if (actx) {
                    if (subRumble) subRumble.gain.setTargetAtTime(0.98, actx.currentTime, 0.15);
                    if (shockCrackle) shockCrackle.gain.setTargetAtTime(0.72, actx.currentTime, 0.1);
                    if (gasHiss) gasHiss.gain.setTargetAtTime(0.15, actx.currentTime, 2.0);
                }

                if (simT < 6.0) {
                    camShake = 0.45;
                    for(let i=0; i<6; i++) {
                        emitParticle(
                            rx + (Math.random()-0.5)*9, 2.2, (Math.random()-0.5)*9,
                            (Math.random()-0.5)*2.0, 0.25 + Math.random()*0.4, (Math.random()-0.5)*2.0,
                            7.0, 42.0, 75, 0.8, 0xf1f5f9, false
                        );
                    }
                }
            }

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

            let regime = "TROPOSPHERE";
            if (alt >= 100.0) regime = "THERMOSPHERE (VACUUM)";
            else if (alt >= 50.0) regime = "MESOSPHERE";
            else if (alt >= 12.0) regime = "STRATOSPHERE";
            document.getElementById('hud-regime').innerText = regime;
            document.getElementById('hud-downrange').innerText = `${dRangeKm.toFixed(1)} km`;

            document.getElementById('tv-mach').innerText = `M ${mach.toFixed(2)}`;
            document.getElementById('tv-spd').innerText = `(${Math.round(vel * 3.6).toLocaleString()} km/h)`;
            document.getElementById('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            document.getElementById('tv-q').innerText   = q.toFixed(1);
            document.getElementById('tv-g').innerText   = accG.toFixed(1);
            if (!p0.exploded && !simCfg.is_preview) {
                document.getElementById('tv-stage-badge').innerText = p0.stage === 1 ? (p0.strapon ? "STAGE 1 + BOOSTERS" : "STAGE 1 CORE ONLY") : "STAGE 2 ORBITAL";
            }

            // 破片が完全に消滅・着底した後に初めてメッセージを表示
            if (rudFinished) {
                rudBanner.style.display = 'block';
                rudDesc.innerText = failMessage || "機体過負荷による空中分解（全残骸落下確認）";
            }

            // 🎥 レンダリング
            scene.fog = sceneFog;
            cameraMain.aspect = window.innerWidth / window.innerHeight;
            cameraMain.updateProjectionMatrix();
            rendererMain.render(scene, cameraMain);

            if (pipVisible) {
                scene.fog = null;
                cameraPip.aspect = 340 / 195;
                cameraPip.updateProjectionMatrix();
                rendererPip.render(scene, cameraPip);
                scene.fog = sceneFog;
            }
        }

        requestAnimationFrame(animate);

        window.addEventListener('resize', () => {
            rendererMain.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

final_html = html_template.replace("__SIM_DATA__", traj_json)
final_html = final_html.replace("__SIM_CFG__", cfg_json)
final_html = final_html.replace("__FAIL_MSG__", fail_msg_clean)

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
        st.success("🎉 **ミッション完全成功 (SECO & LEO Insertion / Nominal Trajectory)**: 全段燃焼および分離シーケンスが設計通り正常に推移しました。")
