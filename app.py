import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbital Architect Ultra", layout="wide", initial_sidebar_state="collapsed")
st.title("🚀 Orbital Architect Ultra")
st.caption("※ 4K実写級：IFT-5タワーキャッチ・精密RCSコーン噴射・ノズル内包プルーム・2層爆風スチーム・重低音分離音響・実写大気シェーダー完全版")

PROPELLANTS = {
    "超高密度サブクール・メタロックス (CH4 / LOX) [Starship王道]": {"base_isp_sl": 338, "base_isp_vac": 382, "base_thrust": 2800, "density": 0.85, "flame_hex": 0x60a5fa, "outer_hex": 0x1d4ed8, "spark_hex": 0x93c5fd, "risk": 0.0, "type": "methalox"},
    "高精製ロケットグレードケロシン (RP-1 / LOX) [Saturn V / Falcon]": {"base_isp_sl": 302, "base_isp_vac": 335, "base_thrust": 1950, "density": 1.03, "flame_hex": 0xfef08a, "outer_hex": 0xea580c, "spark_hex": 0xfde047, "risk": 0.0, "type": "rp1"},
    "超極低温スラッシュ・ハイドロロックス (LH2 / LOX) [H3 / SLS]": {"base_isp_sl": 385, "base_isp_vac": 468, "base_thrust": 1450, "density": 0.34, "flame_hex": 0xfbcfe8, "outer_hex": 0xbe185d, "spark_hex": 0xffffff, "risk": 0.01, "type": "hydro"},
    "【猛毒】四酸化二窒素 ＋ UDMH (N2O4 / UDMH) [Proton / ICBM]": {"base_isp_sl": 288, "base_isp_vac": 322, "base_thrust": 2100, "density": 1.26, "flame_hex": 0xf5d0fe, "outer_hex": 0x9333ea, "spark_hex": 0xfab1a0, "risk": 0.05, "type": "hypergolic"},
    "【核熱】固体炉心型原子力サーマルロケット (NERVA / LH2)": {"base_isp_sl": 450, "base_isp_vac": 925, "base_thrust": 2500, "density": 0.30, "flame_hex": 0x86efac, "outer_hex": 0x14532d, "spark_hex": 0x4ade80, "risk": 0.12, "type": "nuclear"},
    "【超高カロリー】発酵イースト＆濃厚バター (Baguette Fuel)": {"base_isp_sl": 310, "base_isp_vac": 360, "base_thrust": 2200, "density": 0.92, "flame_hex": 0xfef08a, "outer_hex": 0xd97706, "spark_hex": 0xffedd5, "risk": 0.0, "type": "rp1"},
    "【高密度黒鉛】最高級ハイユニグラファイト固体燃料": {"base_isp_sl": 295, "base_isp_vac": 330, "base_thrust": 2600, "density": 1.15, "flame_hex": 0xfde047, "outer_hex": 0xb45309, "spark_hex": 0xffffff, "risk": 0.0, "type": "solid"}
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
    "🚀 SpaceX Starship & Super Heavy (IFT-5 タワーキャッチ仕様)": {"s1_prop": 0, "s1_cycle": 0, "s1_eng": 33, "s1_pc": 300, "s1_eps": 24, "s1_fuel": 3400.0, "s1_mat": 0, "s1_thick": 4.2, "strapon": 0, "spacex_rtls": True, "wings": 0, "aoa": 0.5, "rcs": 0.8, "s2_prop": 0, "s2_cycle": 0, "s2_eng": 6, "s2_eps": 150, "s2_fuel": 1200.0, "s2_mat": 0, "s2_thick": 3.0, "fairing": 0, "payload": 50.0, "water": 300, "turn_exp": 0.62},
    "🌕 NASA Saturn V (アポロ月面着陸ロケット)": {"s1_prop": 1, "s1_cycle": 2, "s1_eng": 5, "s1_pc": 70, "s1_eps": 16, "s1_fuel": 2150.0, "s1_mat": 2, "s1_thick": 5.5, "strapon": 0, "spacex_rtls": False, "wings": 2, "aoa": 0.0, "rcs": 1.2, "s2_prop": 2, "s2_cycle": 2, "s2_eng": 5, "s2_eps": 40, "s2_fuel": 450.0, "s2_mat": 2, "s2_thick": 3.8, "fairing": 3, "payload": 45.0, "water": 200, "turn_exp": 0.70},
    "🇯🇵 JAXA H3ロケット 22S (固体ブースター2基構成)": {"s1_prop": 2, "s1_cycle": 1, "s1_eng": 2, "s1_pc": 120, "s1_eps": 35, "s1_fuel": 250.0, "s1_mat": 1, "s1_thick": 3.2, "strapon": 3, "spacex_rtls": False, "wings": 2, "aoa": 0.0, "rcs": 1.0, "s2_prop": 2, "s2_cycle": 1, "s2_eng": 1, "s2_eps": 180, "s2_fuel": 32.0, "s2_mat": 1, "s2_thick": 2.2, "fairing": 1, "payload": 6.5, "water": 250, "turn_exp": 0.65},
    "☢️ 大陸間弾道ミサイル ICBM「RS-28 サルマト (Sarmat)」": {"s1_prop": 3, "s1_cycle": 1, "s1_eng": 4, "s1_pc": 210, "s1_eps": 22, "s1_fuel": 180.0, "s1_mat": 4, "s1_thick": 6.5, "strapon": 0, "spacex_rtls": False, "wings": 3, "aoa": 0.0, "rcs": 0.4, "s2_prop": 3, "s2_cycle": 1, "s2_eng": 1, "s2_eps": 60, "s2_fuel": 35.0, "s2_mat": 4, "s2_thick": 4.5, "fairing": 2, "payload": 10.0, "water": 80, "turn_exp": 0.48},
    "⚡ 極超音速滑空ミサイル「ダークイーグル (Dark Eagle LRHW)」": {"s1_prop": 3, "s1_cycle": 0, "s1_eng": 1, "s1_pc": 280, "s1_eps": 18, "s1_fuel": 120.0, "s1_mat": 3, "s1_thick": 4.0, "strapon": 0, "spacex_rtls": False, "wings": 3, "aoa": 2.0, "rcs": 0.3, "s2_prop": 3, "s2_cycle": 0, "s2_eng": 1, "s2_eps": 70, "s2_fuel": 25.0, "s2_mat": 3, "s2_thick": 2.5, "fairing": 2, "payload": 2.5, "water": 100, "turn_exp": 0.38},
    "🥖 【ジョーク】超音速フランスパン「バゲット・V2 (Baguette)」": {"s1_prop": 5, "s1_cycle": 2, "s1_eng": 7, "s1_pc": 160, "s1_eps": 20, "s1_fuel": 450.0, "s1_mat": 5, "s1_thick": 2.5, "strapon": 0, "spacex_rtls": False, "wings": 2, "aoa": 0.0, "rcs": 1.5, "s2_prop": 5, "s2_cycle": 2, "s2_eng": 1, "s2_eps": 90, "s2_fuel": 90.0, "s2_mat": 5, "s2_thick": 1.8, "fairing": 4, "payload": 4.0, "water": 120, "turn_exp": 0.60},
    "✏️ 【ジョーク】本当に鉛筆ロケット「三菱ハイユニ HB-9000」": {"s1_prop": 6, "s1_cycle": 2, "s1_eng": 1, "s1_pc": 190, "s1_eps": 18, "s1_fuel": 320.0, "s1_mat": 6, "s1_thick": 3.0, "strapon": 0, "spacex_rtls": False, "wings": 2, "aoa": 0.0, "rcs": 1.0, "s2_prop": 6, "s2_cycle": 2, "s2_eng": 1, "s2_eps": 80, "s2_fuel": 60.0, "s2_mat": 6, "s2_thick": 2.0, "fairing": 5, "payload": 2.0, "water": 90, "turn_exp": 0.55}
}

prop_keys, cyc_keys, mat_keys = list(PROPELLANTS), list(PUMP_CYCLES), list(MATERIALS)
strap_keys, wing_keys, fair_keys = list(STRAPON_BOOSTERS), list(AERO_WINGS), list(FAIRINGS)

def on_preset_change():
    c = PRESETS.get(st.session_state.get("preset_selector"))
    if not c: return
    mapping = {
        "k_s1_prop": prop_keys[c["s1_prop"]], "k_s1_cycle": cyc_keys[c["s1_cycle"]], "k_s1_eng": int(c["s1_eng"]),
        "k_s1_pc": int(c["s1_pc"]), "k_s1_eps": int(c["s1_eps"]), "k_s1_fuel": float(c["s1_fuel"]),
        "k_s1_mat": mat_keys[c["s1_mat"]], "k_s1_thick": float(c["s1_thick"]), "k_strapon": strap_keys[c["strapon"]],
        "k_spacex_rtls": bool(c["spacex_rtls"]), "k_wings": wing_keys[c["wings"]], "k_aoa": float(c["aoa"]),
        "k_rcs": float(c["rcs"]), "k_s2_prop": prop_keys[c["s2_prop"]], "k_s2_cycle": cyc_keys[c["s2_cycle"]],
        "k_s2_eng": int(c["s2_eng"]), "k_s2_eps": int(c["s2_eps"]), "k_s2_fuel": float(c["s2_fuel"]),
        "k_s2_mat": mat_keys[c["s2_mat"]], "k_s2_thick": float(c["s2_thick"]), "k_fairing": fair_keys[c["fairing"]],
        "k_payload": float(c["payload"]), "k_water": int(c["water"]), "k_turn_exp": float(c["turn_exp"])
    }
    st.session_state.update(mapping)

if "initialized_preset" not in st.session_state:
    st.session_state["preset_selector"] = list(PRESETS)[1]
    on_preset_change()
    st.session_state["initialized_preset"] = True

st.selectbox("🎯 機体プリセット / 特殊兵器セレクター", list(PRESETS), key="preset_selector", on_change=on_preset_change)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 第1段 (推進・燃焼・構造)", "🚀 外部ブースター & SpaceXキャッチ機構",
    "🛩️ 空力翼 & 4象限RCS姿勢制御", "🛰️ 第2段 (オービター) & 先端部", "🌊 発射台水冷デリュージ & ガイダンス"
])

with tab1:
    c1, c2, c3 = st.columns(3)
    s1_prop = c1.selectbox("第1段 推進剤", prop_keys, key="k_s1_prop")
    s1_cycle = c1.selectbox("ターボポンプ駆動サイクル", cyc_keys, key="k_s1_cycle")
    s1_eng_count = c1.slider("メインエンジン群 基数", 1, 33, key="k_s1_eng")
    s1_pc = c2.slider("燃焼室圧力 Pc (bar)", 30, 420, step=10, key="k_s1_pc")
    s1_eps = c2.slider("海面膨張比 (ε: ノズル径連動)", 8, 70, step=1, key="k_s1_eps")
    s1_fuel = c3.slider("第1段 推進剤充填量 (トン: 胴体長連動)", 50.0, 4500.0, step=25.0, key="k_s1_fuel")
    s1_mat = c3.selectbox("第1段 構造素材", mat_keys, key="k_s1_mat")
    s1_thick = c3.slider("外殻等価板厚 (mm)", 1.0, 12.0, step=0.1, key="k_s1_thick")

with tab2:
    c1, c2 = st.columns(2)
    strapon_opt = c1.selectbox("ブースター種別クラスタ", strap_keys, key="k_strapon")
    sep_thrust_factor = c1.slider("分離パイロモーター推力倍率", 0.5, 3.0, 1.2, step=0.1, key="k_sep_thrust")
    spacex_return_mode = c2.checkbox("🔄 SpaceX型 ブースターRTLS帰還 ＆ チョップスティック・タワーキャッチ (IFT-5再現)", key="k_spacex_rtls")
    c2.caption("※ ONの場合：第2段軌道投入＆第1段タワーキャッチの両方成功でミッション完了。OFFの場合：軌道投入のみでミッション完了。")

with tab3:
    c1, c2 = st.columns(2)
    wing_type = c1.selectbox("機体外部 空力パーツ", wing_keys, key="k_wings")
    angle_of_attack = c1.slider("固定取り付け迎角 AoA (deg)", -3.0, 12.0, step=0.5, key="k_aoa")
    rcs_deadband = c2.slider("4象限RCS デッドバンド感度 (deg)", 0.2, 5.0, step=0.1, key="k_rcs")
    c2.caption("※ 姿勢制御要求が発生した瞬間だけ冷ガス窒素(GN2)が一瞬パルス噴射されます。")

with tab4:
    c1, c2, c3 = st.columns(3)
    s2_prop = c1.selectbox("第2段 推進剤", prop_keys, key="k_s2_prop")
    s2_cycle = c1.selectbox("第2段 ポンプ方式", cyc_keys, key="k_s2_cycle")
    s2_eng_count = c1.slider("真空ノズル基数", 1, 9, key="k_s2_eng")
    s2_eps = c1.slider("第2段 真空膨張比 (ε)", 30, 280, step=5, key="k_s2_eps")
    s2_fuel = c2.slider("第2段 推進剤充填量 (トン)", 10.0, 1500.0, step=10.0, key="k_s2_fuel")
    s2_mat = c2.selectbox("第2段 構造素材", mat_keys, key="k_s2_mat")
    s2_thick = c2.slider("第2段 壁厚 (mm)", 0.8, 8.0, step=0.1, key="k_s2_thick")
    fairing_type = c3.selectbox("先端空力カウル / 弾頭 / ペイロード", fair_keys, key="k_fairing")
    fairing_sep_alt = c3.slider("フェアリング分離高度 (km)", 30.0, 180.0, 75.0, step=5.0, key="k_fairing_sep")
    payload_mass = c3.slider("投入衛星 / 弾頭質量 (トン)", 0.2, 120.0, step=0.5, key="k_payload")

with tab5:
    c1, c2 = st.columns(2)
    water_flow_rate = c1.slider("消音注水デリュージ流量 (トン/秒)", 50, 450, step=25, key="k_water")
    ignition_lead_time = c1.slider("エンジン先行点火開始 (T-マイナス秒)", 2.5, 6.0, 3.8, step=0.1, key="k_ign_lead")
    turn_start_alt = c2.slider("ピッチオーバー開始高度 (km)", 0.3, 15.0, 1.8, step=0.1, key="k_turn_start")
    turn_end_alt = c2.slider("水平重力ターン完了高度 (km)", 50.0, 250.0, 120.0, step=5.0, key="k_turn_end")
    turn_exponent = c2.slider("ターン曲率指数", 0.3, 2.0, step=0.02, key="k_turn_exp")
    throttle_maxq = c2.slider("Max-Q 領域 推力抑制 (%)", 30, 100, 75, key="k_maxq_thr")
    max_g_limit_cut = c2.slider("最大加速度リミッター (G)", 2.5, 18.0, 5.0, step=0.2, key="k_max_g")

def calc_stage_specs(p_k, c_k, pc, eps, eng_c, fuel_m, m_k, thick):
    p, cyc, mat = PROPELLANTS[p_k], PUMP_CYCLES[c_k], MATERIALS[m_k]
    pc_f = 1.0 + (pc - 100.0) * 0.0006
    eps_b = 1.0 + np.log10(eps / 25.0) * 0.08
    over_p = max(0.0, (eps - 35.0) * 0.006)
    isp_sl = p["base_isp_sl"] * cyc["isp_mod"] * pc_f * (1.0 - over_p)
    isp_vac = p["base_isp_vac"] * cyc["isp_mod"] * pc_f * eps_b
    th_vac = p["base_thrust"] * cyc["thrust_mod"] * ((pc / 150.0) ** 0.65)
    th_sl = th_vac * (isp_sl / isp_vac)
    den_p = (1.0 / p["density"]) ** 0.35
    thk_f = thick / 3.0
    dry_ratio = mat["base_dry_ratio"] * den_p * thk_f + 0.005
    eng_m = (th_vac / 750.0) * cyc["mass_mod"] * (1.0 + eps * 0.002) * eng_c
    return {
        "isp_sl": float(isp_sl), "isp_vac": float(isp_vac), "thrust_sl": float(th_sl * eng_c),
        "thrust_vac": float(th_vac * eng_c), "dry_mass": float(fuel_m * dry_ratio + eng_m),
        "max_q": float(mat["max_q_base"] * (thk_f ** 1.1)), "max_g": float(mat["max_g_base"] * (thk_f ** 0.85)),
        "pc": pc, "eps": eps, "cd_mod": den_p, "mat_id": mat["mat_id"], "cyc_id": cyc["cyc_id"],
        "flame_hex": p["flame_hex"], "outer_hex": p["outer_hex"], "spark_hex": p["spark_hex"], "eng_count": eng_c
    }

wing_spec, fair_spec, strapon_spec = AERO_WINGS[wing_type], FAIRINGS[fairing_type], STRAPON_BOOSTERS[strapon_opt]
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
target_bottom_y_3d = 68.6 - (s1_len_scaled - 2.2)
TOWER_PHYSICAL_CATCH_Y = max(0.0, (target_bottom_y_3d - 6.0) * 10.0)

def run_simulation(preview_only=False):
    if preview_only:
        return [{
            "t": -10.0, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0, "stage": 1,
            "fairing": True, "wings": bool(wing_spec["wing_id"] != "none"), "strapon": bool(strapon_spec["count"] > 0),
            "exploded": False, "thrust": False, "pitch": 0.0, "mach": 0.0, "event": "PREVIEW", "rcs_cmd": 0.0,
            "s1_prop_pct": 100.0, "s2_prop_pct": 100.0, "pitch_deg": 90.0, "apogee_km": 0.0, "chamber_p": 0.0,
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False, "b_rcs": 0.0
        }], None

    dt, g0, R_earth = 0.5, 9.80665, 6371000.0
    x, y, vx, vy, stage = 0.0, 0.0, 0.0, 0.0, 1
    fuel_s1_init, fuel_s2_init = float(s1_fuel * 1000.0), float(s2_fuel * 1000.0)
    fuel_s1_rem, fuel_s2_rem = fuel_s1_init, fuel_s2_init
    fuel_strapon_rem = float(strapon_spec["fuel_add"] * 1000.0)
    fairing_att = True
    wings_att = bool(wing_spec["wing_id"] != "none")
    strapon_att = bool(strapon_spec["count"] > 0)
    b_x = b_y = b_vx = b_vy = b_pitch = b_rcs = b_sep_time = 0.0
    b_active = b_thrust = b_caught = False
    b_fuel = float(s1_fuel * 1000.0 * 0.18) if spacex_return_mode else 0.0
    history, fail_reason, prev_pitch, rcs_cd = [], None, 90.0, 0.0

    for cd_s in range(21):
        t_cd = -10.0 + cd_s * 0.5
        history.append({
            "t": float(t_cd), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0, "stage": 1,
            "fairing": True, "wings": wings_att, "strapon": strapon_att, "exploded": False,
            "thrust": bool(t_cd >= -ignition_lead_time), "pitch": 0.0, "mach": 0.0, "event": "COUNTDOWN", "rcs_cmd": 0.0,
            "s1_prop_pct": 100.0, "s2_prop_pct": 100.0, "pitch_deg": 90.0, "apogee_km": 0.0,
            "chamber_p": float(s1_pc) if t_cd >= -ignition_lead_time else 0.0,
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False, "b_rcs": 0.0
        })

    maxq_p, super_c = False, False
    for step in range(3500):
        t, alt = float(step * dt), float(y)
        alt_km, v = alt / 1000.0, float(np.hypot(vx, vy))
        mach = v / 340.0
        rho = float(1.225 * np.exp(-alt / 7400.0)) if alt < 140000 else 0.0
        q = float(0.5 * rho * (v**2) / 1000.0)

        t_pitch = 90.0 if alt_km < turn_start_alt else (90.0 * (1.0 - (((alt_km - turn_start_alt) / (230.0 - turn_start_alt)) ** turn_exponent)) if alt_km < 230.0 else 0.0)
        wing_l = 0.0
        if wings_att and alt_km < 50.0 and rho > 0.003:
            wing_l = 0.5 * rho * (v**2) * (wing_spec["lift_coeff"] * 24.0) * np.sin(np.radians(angle_of_attack))
            t_pitch -= (wing_l / 12000.0) * (mach ** 1.3)

        pitch_deg = max(0.0, min(90.0, t_pitch))
        pitch_rad, visual_pitch = np.radians(pitch_deg), np.radians(90.0 - pitch_deg)
        pitch_rate = (pitch_deg - prev_pitch) / dt
        prev_pitch = pitch_deg
        rcs_cmd = 0.0
        if rcs_cd > 0: rcs_cd -= dt
        elif (abs(pitch_rate) > 0.15 and alt_km > 0.8) or (alt_km >= 230.0 and pitch_deg > 0.1):
            rcs_cmd, rcs_cd = (-1.0 if pitch_rate > 0 else 1.0), 4.5

        cur_ev = "FLIGHT"
        if v >= 340.0 and not super_c: cur_ev, super_c = "SUPERSONIC", True
        elif alt_km > 11.0 and not maxq_p: cur_ev, maxq_p = "MAX_Q", True
        if fairing_att and alt_km >= fairing_sep_alt: fairing_att, cur_ev = False, "FAIRING_SEP"

        f_m = (fair_spec["mass"] * 1000.0) if fairing_att else 0.0
        w_m = (wing_spec["mass"] * 1000.0) if wings_att else 0.0
        s_m = (strapon_spec["mass_add"] * 1000.0 + max(0.0, fuel_strapon_rem)) if strapon_att else 0.0
        cur_pc = 0.0

        if stage == 1:
            if strapon_att:
                if fuel_strapon_rem > 0 and (fuel_s1_rem > s1_fuel * 1000.0 * 0.28):
                    st_thrust = strapon_spec["thrust_add"] * 1000.0
                    fuel_strapon_rem -= (st_thrust / (strapon_spec["isp_sl"] * g0)) * dt * 1.3
                else: strapon_att, cur_ev, st_thrust = False, "BOOSTER_SEP", 0.0
            else: st_thrust = 0.0

            meco_th = (s1_fuel * 1000.0 * 0.18) if spacex_return_mode else 0.0
            if fuel_s1_rem <= meco_th:
                stage, strapon_att, cur_ev, thrust = 2, False, "HOT_STAGING", 0.0
                if not b_active:
                    b_active, b_sep_time = True, t
                    b_x, b_y = x, y
                    b_vx, b_vy = vx - np.cos(pitch_rad) * 2.5, vy - np.sin(pitch_rad) * 2.5
                    b_pitch = visual_pitch
            else:
                cur_mass = float((s1_spec["dry_mass"] + s2_fuel + s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_m + w_m + s_m + fuel_s1_rem)
                atm_fac = float(np.exp(-alt / 7400.0))
                isp = float(s1_spec["isp_vac"] - (s1_spec["isp_vac"] - s1_spec["isp_sl"]) * atm_fac)
                th_c = float((s1_spec["thrust_vac"] - (s1_spec["thrust_vac"] - s1_spec["thrust_sl"]) * atm_fac) * 1000.0)
                t_thr = (0.65 + (t / 3.0) * 0.35) if t < 3.0 else 1.0
                if 8000 < alt < 17000: t_thr *= (throttle_maxq / 100.0)
                th_c *= t_thr
                thrust = th_c + st_thrust
                if thrust / (cur_mass * g0) > max_g_limit_cut: thrust = max_g_limit_cut * cur_mass * g0
                fuel_s1_rem -= (th_c / (isp * g0)) * dt
                cur_pc = s1_pc * t_thr
        else:
            strapon_att = False
            cur_mass = float((s2_spec["dry_mass"] + payload_mass) * 1000.0 + f_m + max(0.0, fuel_s2_rem))
            if fuel_s2_rem <= 0: thrust = cur_pc = 0.0
            else:
                atm_fac = float(np.exp(-alt / 7400.0))
                isp = float(s2_spec["isp_vac"] - (s2_spec["isp_vac"] - s2_spec["isp_sl"]) * atm_fac)
                th_b = float((s2_spec["thrust_vac"] - (s2_spec["thrust_vac"] - s2_spec["thrust_sl"]) * atm_fac) * 1000.0)
                sp_err = 7900.0 - vx
                thrust = 0.0 if sp_err <= 0 else (th_b * max(0.05, sp_err / 400.0) if sp_err < 400.0 else th_b)
                if thrust / (cur_mass * g0) > max_g_limit_cut: thrust = max_g_limit_cut * cur_mass * g0
                fuel_s2_rem -= (thrust / (isp * g0)) * dt
                cur_pc = 220.0 * (thrust / th_b if th_b > 0 else 0.0)

        b_rcs = 0.0
        if b_active and not b_caught:
            b_alt = b_y
            b_rho = float(1.225 * np.exp(-b_alt / 7400.0)) if b_alt < 140000 else 0.0
            b_v = float(np.hypot(b_vx, b_vy))
            b_drag = 0.5 * b_rho * (b_v**2) * 18.0 * 0.85
            b_drag_y = -b_drag * (b_vy / b_v) if b_v > 0 else 0.0
            b_drag_x = -b_drag * (b_vx / b_v) if b_v > 0 else 0.0
            sep_el = t - b_sep_time

            if not spacex_return_mode:
                b_thrust = False
                b_pitch += 0.04 * dt
                b_vx += (b_drag_x / (s1_spec["dry_mass"] * 1000.0)) * dt
                b_vy += (-g0 + b_drag_y / (s1_spec["dry_mass"] * 1000.0)) * dt
            else:
                if sep_el <= 4.5:
                    b_thrust, p_err = False, -1.57 - b_pitch
                    b_rcs = 1.0 if p_err < -0.05 else (-1.0 if p_err > 0.05 else 0.0)
                    b_pitch += np.clip(p_err * 0.35, -0.45, 0.45) * dt
                    b_vx -= 6.5 * dt
                    b_vy -= (g0 + 3.5) * dt
                elif b_alt > 35000 and b_fuel > s1_fuel * 1000 * 0.04 and b_vx > -650.0:
                    b_pitch += (-1.57 - b_pitch) * 0.35
                    b_thrust, b_rcs = True, (1.0 if abs(-1.57 - b_pitch) > 0.08 else 0.0)
                    b_f = s1_spec["thrust_vac"] * 1000.0 * 0.95
                    b_fuel -= (b_f / (s1_spec["isp_vac"] * g0)) * dt
                    b_vx -= (b_f / (s1_spec["dry_mass"] * 1000.0)) * dt * 2.8
                    b_vy += (-g0 + b_drag_y / (s1_spec["dry_mass"] * 1000.0)) * dt
                elif 12000 < b_alt <= 28000 and b_vy < -400 and b_fuel > s1_fuel * 1000 * 0.015:
                    t_bp = float(np.clip(-b_vx * 0.0008, -0.2, 0.2))
                    b_rcs = 1.0 if (t_bp - b_pitch) > 0.03 else (-1.0 if (t_bp - b_pitch) < -0.03 else 0.0)
                    b_pitch, b_thrust = t_bp, True
                    b_f = s1_spec["thrust_vac"] * 1000.0 * 0.85
                    b_fuel -= (b_f / (s1_spec["isp_vac"] * g0)) * dt
                    b_vy += (b_f / (s1_spec["dry_mass"] * 1000.0)) * dt * 0.9 + (-g0 + b_drag_y / (s1_spec["dry_mass"] * 1000.0)) * dt
                elif b_alt <= (TOWER_PHYSICAL_CATCH_Y + 3600.0):
                    rem_h = max(0.0, b_alt - TOWER_PHYSICAL_CATCH_Y)
                    b_thrust, b_x = True, rem_h * 0.16
                    t_bp = float(np.clip((rem_h / 3600.0) * 0.20, 0.0, 0.20))
                    b_rcs = -1.0 if abs(t_bp - b_pitch) > 0.015 else 0.0
                    b_pitch = t_bp
                    d_vy = -max(2.2, rem_h * 0.24)
                    b_vy += (d_vy - b_vy) * 0.55
                    b_vx = -b_x * 0.65
                    b_vy += (-g0 + b_drag_y / (s1_spec["dry_mass"] * 1000.0)) * dt
                else:
                    t_bp = float(np.clip((b_x / 4000.0) * 0.2, -0.25, 0.25))
                    b_rcs = 1.0 if (t_bp - b_pitch) > 0.02 else (-1.0 if (t_bp - b_pitch) < -0.02 else 0.0)
                    b_pitch += (t_bp - b_pitch) * 0.25
                    b_vx += (-b_x / 25.0 - b_vx) * 0.25
                    b_thrust = False
                    b_vy += (-g0 + b_drag_y / (s1_spec["dry_mass"] * 1000.0)) * dt

                if b_y <= (TOWER_PHYSICAL_CATCH_Y + 12.0) and abs(b_x) < 40.0:
                    b_caught, b_y, b_x, b_vx, b_vy, b_pitch, b_thrust, b_rcs = True, TOWER_PHYSICAL_CATCH_Y, 0.0, 0.0, 0.0, 0.0, False, 0.0
            b_x = max(0.0, b_x + b_vx * dt)
            b_y = max(TOWER_PHYSICAL_CATCH_Y if spacex_return_mode else 0.0, b_y + b_vy * dt)

        dir_x, dir_y = np.cos(pitch_rad), np.sin(pitch_rad)
        dr_area = (13.0 * s1_spec["cd_mod"] * wing_spec["drag_penalty"]) if stage == 1 else (5.2 * s2_spec["cd_mod"])
        dr_f = 0.5 * rho * (v**2) * fair_spec["cd"] * dr_area
        dr_x = -dr_f * (vx / v) if v > 0 else 0.0
        dr_y = -dr_f * (vy / v) if v > 0 else 0.0
        g_cur = g0 * ((R_earth / (R_earth + alt)) ** 2)
        grav_y = -cur_mass * (g_cur - (vx ** 2) / (R_earth + alt))

        fx = thrust * dir_x + dr_x - wing_l * dir_y
        fy = thrust * dir_y + dr_y + wing_l * dir_x + grav_y
        if alt <= 0.0 and fy <= 0.0: ax = ay = vx = vy = 0.0; acc_g = 1.0
        else:
            ax, ay = fx / cur_mass, fy / cur_mass
            acc_g = float(np.hypot(thrust * dir_x + dr_x, thrust * dir_y + dr_y) / (cur_mass * g0))

        cur_spec = s1_spec if stage == 1 else s2_spec
        s1_pct, s2_pct = max(0.0, (fuel_s1_rem / fuel_s1_init) * 100.0), max(0.0, (fuel_s2_rem / fuel_s2_init) * 100.0)
        ap_val = alt_km + (max(0.0, vy)**2 / (2.0 * g0 * 1000.0))

        if q > cur_spec["max_q"]:
            fail_reason = f"Max-Q 構造圧壊: 動圧 {q:.1f} kPa が強度限界を超過。"
            history.append({
                "t": t, "x": float(x), "y": float(y), "alt": alt_km, "v": v, "q": q, "g": acc_g, "stage": int(stage),
                "fairing": fairing_att, "wings": wings_att, "strapon": strapon_att, "exploded": True,
                "thrust": False, "pitch": visual_pitch, "mach": mach, "event": "RUD", "rcs_cmd": 0.0,
                "s1_prop_pct": s1_pct, "s2_prop_pct": s2_pct, "pitch_deg": pitch_deg, "apogee_km": ap_val, "chamber_p": 0.0,
                "b_x": float(b_x), "b_y": float(b_y), "b_active": b_active, "b_pitch": float(b_pitch), "b_thrust": b_thrust, "b_caught": b_caught, "b_rcs": float(b_rcs)
            })
            break

        vx, vy = vx + ax * dt, vy + ay * dt
        x, y = x + vx * dt, max(0.0, y + vy * dt)
        is_orbit = bool(alt_km >= 230.0 and vx >= 7850.0)

        history.append({
            "t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g, "stage": int(stage),
            "fairing": fairing_att, "wings": wings_att, "strapon": strapon_att, "exploded": False,
            "thrust": bool(thrust > 0 and not is_orbit), "pitch": visual_pitch, "mach": mach,
            "event": "ORBIT" if is_orbit else cur_ev, "rcs_cmd": rcs_cmd,
            "s1_prop_pct": s1_pct, "s2_prop_pct": s2_pct, "pitch_deg": pitch_deg, "apogee_km": ap_val, "chamber_p": cur_pc,
            "b_x": float(b_x), "b_y": float(b_y), "b_active": b_active, "b_pitch": float(b_pitch), "b_thrust": b_thrust, "b_caught": b_caught, "b_rcs": float(b_rcs)
        })

        if is_orbit and (not spacex_return_mode or b_caught):
            for os_i in range(25):
                history.append({
                    "t": t + (os_i + 1) * dt, "x": x + vx * (os_i + 1) * dt, "y": y, "alt": alt_km, "v": v,
                    "q": 0.0, "g": 0.0, "stage": 2, "fairing": False, "wings": wings_att, "strapon": False, "exploded": False,
                    "thrust": False, "pitch": 1.5708, "mach": mach, "event": "ORBIT", "rcs_cmd": 0.0,
                    "s1_prop_pct": 0.0, "s2_prop_pct": s2_pct, "pitch_deg": 0.0, "apogee_km": alt_km, "chamber_p": 0.0,
                    "b_x": float(b_x), "b_y": float(b_y), "b_active": b_active, "b_pitch": float(b_pitch), "b_thrust": False, "b_caught": True, "b_rcs": 0.0
                })
            break

    if not fail_reason and history[-1]["event"] != "ORBIT":
        fail_reason = f"軌道速度未達。高度: {alt_km:.1f} km, 横速度: {vx:.0f} m/s (目標: 7,900 m/s)"

    return history, fail_reason

st.markdown("<div id='launch-viewport'></div>", unsafe_allow_html=True)
cb1, cb2 = st.columns([3, 1])
launch_clicked = cb1.button("🔴 4K LIVE中継：ローンチ・シーケンス開始", use_container_width=True, type="primary")
cb2.caption("※ 設定変更すると発射台上の3Dモデルが即座に反映されます。")

traj_data, error_msg = run_simulation(preview_only=(not launch_clicked))

rocket_visual_cfg = {
    "is_preview": not launch_clicked,
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

html_template = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}body,html{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#01040a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;user-select:none}
#canvas-main{width:100%;height:100%;position:absolute;top:0;left:0;z-index:1}
.pip-container{position:absolute;top:78px;right:6px;width:420px;max-width:calc(100vw - 12px);height:240px;border:2px solid rgba(56,189,248,.95);border-radius:6px;z-index:60;box-shadow:0 14px 45px rgba(0,0,0,.98);background:#071526;overflow:hidden;cursor:pointer;transition:height .25s ease}
#canvas-pip{width:100%;height:100%;display:block;transition:filter .15s ease-out}
.pip-tag,.pip-alt,.pip-toggle-hint{position:absolute;background:rgba(15,23,42,.94);font-family:monospace;pointer-events:none;z-index:65}
.pip-tag{top:6px;left:12px;font-size:10px;font-weight:800;color:#fff;padding:3px 8px;border-radius:2px;letter-spacing:1px;border-left:2px solid #38bdf8}
.pip-alt{bottom:6px;right:12px;font-size:11px;color:#38bdf8;font-weight:700;padding:2px 8px;border-radius:2px}
.pip-toggle-hint{top:6px;right:12px;font-size:9px;color:#94a3b8;padding:3px 6px;border-radius:2px}
.hud-orbit{position:absolute;bottom:86px;left:24px;width:320px;background:#030712;border:1px solid rgba(255,255,255,.16);border-radius:4px;padding:8px 12px;z-index:50;color:#fff;box-shadow:0 8px 32px rgba(0,0,0,.85)}
#orbit-canvas{width:296px;height:64px;background:#020617;border-radius:2px;border:1px solid rgba(255,255,255,.08);margin-top:4px}
.top-banner{position:absolute;top:0;left:0;width:100%;min-height:48px;background:linear-gradient(180deg,rgba(2,6,16,.96) 0%,rgba(3,10,24,.92) 100%);border-bottom:1px solid rgba(56,189,248,.22);display:flex;align-items:center;justify-content:space-between;padding:4px 18px;z-index:20;flex-wrap:wrap;gap:12px;box-shadow:0 4px 20px rgba(0,0,0,.7)}
.banner-group{display:flex;align-items:center;gap:12px;flex-wrap:nowrap;overflow-x:auto}
.hud-telemetry{position:absolute;bottom:0;left:0;width:100%;height:76px;background:#01040a;border-top:1px solid rgba(255,255,255,.12);padding:8px 24px;display:flex;align-items:center;justify-content:space-between;z-index:20;pointer-events:none}
.hud-telemetry>*{pointer-events:auto}.telemetry-row{display:flex;gap:clamp(14px,2.2vw,28px);align-items:center;flex-wrap:nowrap;overflow-x:auto}.telemetry-item{flex-shrink:0}
.telemetry-label{font-size:9px;color:#94a3b8;letter-spacing:1px}.telemetry-val{color:#fff;font-size:clamp(13px,1.6vw,17px);font-weight:800;font-family:'Consolas',monospace}
.rud-banner,.complete-banner{display:none;position:absolute;left:50%;transform:translateX(-50%);border-radius:6px;z-index:70;text-align:center}
.rud-banner{top:150px;background:#7f1d1d;border:2px solid #ef4444;padding:16px 28px;box-shadow:0 0 60px rgba(239,68,68,.7)}
.complete-banner{top:140px;background:rgba(6,78,59,.95);border:2px solid #10b981;padding:20px 36px;box-shadow:0 0 70px rgba(16,185,129,.7)}
</style></head><body>
<canvas id="canvas-main"></canvas>
<div id="pip-box" class="pip-container" title="クリックでPiPの表示/非表示を切り替え">
    <canvas id="canvas-pip"></canvas>
    <div id="pip-tag" class="pip-tag">CAM 02: GROUND OPTICAL TRACKER</div>
    <div id="pip-hud-alt" class="pip-alt">BOOSTER: 0.0 km</div>
    <div id="pip-hint" class="pip-toggle-hint">[CLICK TO TOGGLE]</div>
</div>
<div class="top-banner">
    <div class="banner-group" style="min-width:0;flex-shrink:1">
        <span id="live-indicator" style="display:inline-block;width:8px;height:8px;background:#ef4444;border-radius:50%;box-shadow:0 0 10px #ef4444;flex-shrink:0"></span>
        <span id="webcast-title" style="color:#fff;font-weight:800;font-size:clamp(10px,1.2vw,12px);letter-spacing:1.5px;white-space:nowrap">4K WEBCAST</span>
        <span style="color:rgba(255,255,255,.2)">|</span>
        <span id="cam-tag" style="color:#38bdf8;font-size:clamp(9px,1.1vw,11px);font-weight:700;font-family:monospace">CAM 01: OPTICAL LONG TELEPHOTO</span>
        <span style="color:rgba(255,255,255,.2)">|</span>
        <span style="color:#94a3b8;font-family:monospace;font-size:10px">PITCH: <strong id="hud-pitch" style="color:#f8fafc">90.0°</strong></span>
        <span style="color:#94a3b8;font-family:monospace;font-size:10px">PRED APOGEE: <strong id="hud-apogee" style="color:#34d399">0.0 km</strong></span>
    </div>
    <div class="banner-group" style="font-family:monospace;font-size:clamp(9px,1.0vw,10.5px)">
        <span style="color:#94a3b8">PROP S1: <strong id="hud-s1-prop" style="color:#38bdf8">100%</strong></span>
        <span style="color:#94a3b8">S2: <strong id="hud-s2-prop" style="color:#38bdf8">100%</strong></span>
        <span style="color:#94a3b8">Pc: <strong id="hud-pc" style="color:#f59e0b">0 bar</strong></span>
        <span style="color:#94a3b8">ATMOS: <strong id="hud-regime" style="color:#f8fafc">TROPO</strong></span>
        <span style="color:#94a3b8">ARM: <strong id="hud-arm" style="color:#f59e0b">STOWED</strong></span>
        <span id="comm-status" style="color:#10b981;font-weight:700">★ LASER LOCK</span>
    </div>
</div>
<div class="hud-orbit" id="hud-orbit-box">
    <div style="font-size:9px;font-weight:800;color:#94a3b8;letter-spacing:1.2px;display:flex;justify-content:space-between">
        <span>TRAJECTORY & GROUND TRACK</span><span id="hud-downrange" style="color:#38bdf8;font-family:monospace">DOWNRANGE: 0.0 km</span>
    </div>
    <canvas id="orbit-canvas" width="296" height="64"></canvas>
    <div id="event-log" style="margin-top:4px;font-family:monospace;font-size:9px;font-weight:800;color:#34d399;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">> [LD] GO FOR TERMINAL COUNTDOWN</div>
    <div id="sub-callout" style="font-family:monospace;font-size:8.5px;color:#93c5fd;margin-top:1px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">> Pad systems pressurized and ready</div>
</div>
<div id="complete-banner" class="complete-banner">
    <div style="color:#6ee7b7;font-size:18px;font-weight:900;letter-spacing:2px;font-family:monospace">🎉 MISSION COMPLETE 🎉</div>
    <div id="complete-desc" style="color:#ecfdf5;font-size:13px;font-weight:700;margin-top:6px">FIRST COSMIC VELOCITY (28,400 km/h) ACHIEVED</div>
    <div id="complete-sub" style="color:#a7f3d0;font-size:11px;margin-top:4px;font-family:monospace">Vehicle safely established in circular orbit.</div>
</div>
<div id="rud-banner" class="rud-banner">
    <div style="color:#fff;font-size:16px;font-weight:900;letter-spacing:2px;font-family:monospace">🚨 RAPID UNSCHEDULED DISASSEMBLY (RUD) 🚨</div>
    <div id="rud-desc" style="color:#fecaca;font-size:12px;margin-top:4px"></div>
</div>
<div class="hud-telemetry">
    <div>
        <div id="tv-status" style="color:#38bdf8;font-size:9px;font-weight:700">COUNTDOWN SEQUENCE</div>
        <div id="tv-timer" style="color:#fff;font-size:clamp(20px,2.6vw,26px);font-weight:900;font-family:'Consolas',monospace">T- 00:10.0</div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;margin:0 10px">
        <div style="font-size:8px;color:#94a3b8;letter-spacing:1px;margin-bottom:2px">ENGINE CLUSTER STATUS</div>
        <canvas id="engine-cluster-canvas" width="48" height="48" style="background:rgba(15,23,42,.6);border-radius:50%;border:1px solid rgba(56,189,248,.3)"></canvas>
    </div>
    <div class="telemetry-row">
        <div class="telemetry-item"><div class="telemetry-label">HORIZ VELOCITY</div><div class="telemetry-val"><span id="tv-mach">M 0.00</span> <span style="font-size:10px;color:#94a3b8" id="tv-spd">(0 km/h)</span></div></div>
        <div class="telemetry-item"><div class="telemetry-label">ALTITUDE</div><div class="telemetry-val"><span id="tv-alt">0.0</span> <span style="font-size:10px;color:#94a3b8">km</span></div></div>
        <div class="telemetry-item"><div class="telemetry-label">DYNAMIC PRESSURE</div><div class="telemetry-val"><span id="tv-q">0.0</span> <span style="font-size:10px;color:#94a3b8">kPa</span></div></div>
        <div class="telemetry-item"><div class="telemetry-label">AXIAL LOAD</div><div class="telemetry-val"><span id="tv-g">1.0</span> <span style="font-size:10px;color:#94a3b8">G</span></div></div>
        <div class="telemetry-item"><div class="telemetry-label">STAGE CONFIG</div><div id="tv-stage-badge" style="color:#34d399;font-size:clamp(11px,1.4vw,13px);font-weight:800;font-family:'Consolas',monospace">PAD READY</div></div>
    </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
window.addEventListener('DOMContentLoaded', () => {
    try {
        const simData = __SIM_DATA__, simCfg = __SIM_CFG__, failMessage = "__FAIL_MSG__";
        const $ = id => document.getElementById(id);
        const canvasMain = $('canvas-main'), canvasPip = $('canvas-pip'), pipBox = $('pip-box');
        const octx = $('orbit-canvas').getContext('2d'), ectx = $('engine-cluster-canvas').getContext('2d');
        const rudBanner = $('rud-banner'), completeBanner = $('complete-banner'), rudDesc = $('rud-desc');
        const eventLog = $('event-log'), subCallout = $('sub-callout');

        let isMissionEnded = false, catchPopPlayed = false, pipVisible = true, landingSonicBoomPlayed = false;
        let hotStagingSparkTimer = 0.0, pipBlurTriggered12k = false, pipBlurTriggeredCatch = false;

        function triggerPipAutoFocus() {
            if (!canvasPip) return;
            canvasPip.style.filter = "blur(2.8px) brightness(1.28) contrast(1.15)";
            setTimeout(() => { if (canvasPip) canvasPip.style.filter = "blur(0px) brightness(1.0) contrast(1.0)"; }, 320);
        }

        function resizePipRenderer() {
            if (pipBox && pipVisible) {
                const w = pipBox.clientWidth || 420, h = 240;
                rendererPip.setSize(w, h, false);
                cameraPip.aspect = w / h;
                cameraPip.updateProjectionMatrix();
            }
        }
        window.addEventListener('resize', resizePipRenderer);

        pipBox.addEventListener('click', () => {
            pipVisible = !pipVisible;
            canvasPip.style.visibility = pipVisible ? 'visible' : 'hidden';
            $('pip-tag').style.display = $('pip-hud-alt').style.display = pipVisible ? 'block' : 'none';
            pipBox.style.height = pipVisible ? '240px' : '32px';
            $('pip-hint').innerText = pipVisible ? '[CLICK TO HIDE]' : '[CLICK TO SHOW]';
            if (pipVisible) {
                resizePipRenderer(); rendererPip.render(scene, cameraPip);
                setTimeout(() => { resizePipRenderer(); rendererPip.render(scene, cameraPip); }, 260);
            }
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
            { t: 130.0, main: "> [PROP] BOOSTER MECO & SEPARATION", sub: "> Pneumatic pushers & pyros fired", spoken: "Booster separation" },
            { t: 165.0, main: "> [STAGE] SECOND STAGE VACUUM IGNITION", sub: "> Staging confirmed", spoken: "Staging confirmed" },
            { t: 230.0, main: "> [TOWER] CHOPSTICK ARMS EXTENDING FOR CATCH", sub: "> Mechazilla ready for capture", spoken: "Chopstick arms deployed" }
        ];

        let calloutTrackIndex = 0;
        function updateFlightCallouts(simT) {
            while (calloutTrackIndex < calloutMilestones.length && simT >= calloutMilestones[calloutTrackIndex].t) {
                const m = calloutMilestones[calloutTrackIndex++];
                if (eventLog) eventLog.innerText = m.main;
                if (subCallout) subCallout.innerText = m.sub;
                speakCallout(m.spoken);
            }
        }

        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null, subRumble = null, shockCrackle = null, gasHiss = null, boosterRumble = null, boosterCrackle = null;

        function ensureAudioActive() {
            if (!actx) {
                actx = new AudioCtx();
                const buf = actx.createBuffer(1, actx.sampleRate * 4, actx.sampleRate), d = buf.getChannelData(0);
                for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

                const makeNode = (fType, freq, q, dest) => {
                    const s = actx.createBufferSource(); s.buffer = buf; s.loop = true;
                    const f = actx.createBiquadFilter(); f.type = fType; f.frequency.value = freq; if (q) f.Q.value = q;
                    const g = actx.createGain(); g.gain.value = 0.0001;
                    s.connect(f); if (dest) { f.connect(dest); dest.connect(g); } else f.connect(g);
                    g.connect(actx.destination); s.start(0);
                    return g;
                };

                subRumble = makeNode('lowpass', 45, 5.2);
                gasHiss = makeNode('highpass', 2200);
                boosterRumble = makeNode('lowpass', 58, 4.8);

                const ws = actx.createWaveShaper(), curve = new Float32Array(256);
                for (let i = 0; i < 256; i++) { const x = (i * 2) / 256 - 1; curve[i] = Math.sign(x) * Math.pow(Math.abs(x), 0.25); }
                ws.curve = curve;

                shockCrackle = makeNode('bandpass', 290, 3.0, ws);
                boosterCrackle = makeNode('bandpass', 340, 2.5, ws);
            }
            if (actx && actx.state === 'suspended') actx.resume();
        }
        ['click', 'touchstart', 'mousedown', 'keydown'].forEach(e => window.addEventListener(e, ensureAudioActive));

        function playLandingIgnitionBoom() {
            ensureAudioActive();
            if (!actx) return;
            const now = actx.currentTime, osc = actx.createOscillator(), g = actx.createGain();
            osc.type = 'triangle'; osc.frequency.setValueAtTime(140, now); osc.frequency.exponentialRampToValueAtTime(22, now + 0.6);
            g.gain.setValueAtTime(4.5, now); g.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
            osc.connect(g); g.connect(actx.destination); osc.start(now); osc.stop(now + 0.72);

            const nBuf = actx.createBuffer(1, Math.floor(actx.sampleRate * 0.4), actx.sampleRate), nd = nBuf.getChannelData(0);
            for(let i=0; i<nd.length; i++) nd[i] = (Math.random() * 2 - 1) * Math.exp(-i / (actx.sampleRate * 0.08));
            const nSrc = actx.createBufferSource(); nSrc.buffer = nBuf;
            const nF = actx.createBiquadFilter(); nF.type = 'lowpass'; nF.frequency.value = 450;
            const nG = actx.createGain(); nG.gain.setValueAtTime(3.8, now); nG.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
            nSrc.connect(nF); nF.connect(nG); nG.connect(actx.destination); nSrc.start(now);
        }

        function playHeavySeparationSound() {
            ensureAudioActive();
            if (!actx) return;
            const now = actx.currentTime, thudOsc = actx.createOscillator(), thudG = actx.createGain();
            thudOsc.type = 'sine'; thudOsc.frequency.setValueAtTime(135, now); thudOsc.frequency.exponentialRampToValueAtTime(24, now + 0.26);
            thudG.gain.setValueAtTime(4.8, now); thudG.gain.exponentialRampToValueAtTime(0.001, now + 0.34);
            thudOsc.connect(thudG); thudG.connect(actx.destination); thudOsc.start(now); thudOsc.stop(now + 0.35);

            [0.0, 0.038].forEach((offset, idx) => {
                const cBuf = actx.createBuffer(1, Math.floor(actx.sampleRate * 0.065), actx.sampleRate), cd = cBuf.getChannelData(0);
                for (let i = 0; i < cd.length; i++) cd[i] = (Math.random() * 2 - 1) * Math.exp(-i / (actx.sampleRate * 0.008));
                const cSrc = actx.createBufferSource(); cSrc.buffer = cBuf;
                const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.setValueAtTime(idx === 0 ? 1180 : 2650, now + offset); bp.Q.value = 6.5;
                const cG = actx.createGain(); cG.gain.setValueAtTime(3.2, now + offset); cG.gain.exponentialRampToValueAtTime(0.01, now + offset + 0.06);
                cSrc.connect(bp); bp.connect(cG); cG.connect(actx.destination); cSrc.start(now + offset);
            });

            const pBuf = actx.createBuffer(1, Math.floor(actx.sampleRate * 0.55), actx.sampleRate), pd = pBuf.getChannelData(0);
            for (let i = 0; i < pd.length; i++) pd[i] = (Math.random() * 2 - 1) * Math.sin(Math.min(1.0, i / (actx.sampleRate * 0.02)) * (Math.PI / 2)) * Math.exp(-i / (actx.sampleRate * 0.16));
            const pSrc = actx.createBufferSource(); pSrc.buffer = pBuf;
            const pF = actx.createBiquadFilter(); pF.type = 'bandpass'; pF.frequency.setValueAtTime(2200, now + 0.02); pF.Q.value = 1.4;
            const pG = actx.createGain(); pG.gain.setValueAtTime(1.6, now + 0.02);
            pSrc.connect(pF); pF.connect(pG); pG.connect(actx.destination); pSrc.start(now + 0.02);
        }

        function playRcsPuffSound() {
            if (!actx) return;
            const now = actx.currentTime, dur = 0.065, buf = actx.createBuffer(1, Math.floor(actx.sampleRate * dur), actx.sampleRate), d = buf.getChannelData(0);
            for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * Math.exp(-i / (actx.sampleRate * 0.018));
            const s = actx.createBufferSource(); s.buffer = buf;
            const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.setValueAtTime(1850, now); bp.Q.value = 1.8;
            const g = actx.createGain(); g.gain.setValueAtTime(0.045, now); g.gain.exponentialRampToValueAtTime(0.001, now + dur);
            s.connect(bp); bp.connect(g); g.connect(actx.destination); s.start(now);
        }

        function playFirecrackerSnapSound() {
            if (!actx) return;
            const now = actx.currentTime, osc = actx.createOscillator(), g = actx.createGain();
            osc.type = 'square'; osc.frequency.setValueAtTime(1200, now); osc.frequency.exponentialRampToValueAtTime(80, now + 0.035);
            g.gain.setValueAtTime(3.4, now); g.gain.exponentialRampToValueAtTime(0.001, now + 0.055);
            osc.connect(g); g.connect(actx.destination); osc.start(now); osc.stop(now + 0.06);
        }

        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x4a769e, 0.000028);

        const initRenderer = (canvas, exposure) => {
            const r = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
            r.toneMapping = THREE.ACESFilmicToneMapping;
            r.toneMappingExposure = exposure;
            r.shadowMap.enabled = true;
            return r;
        };

        const rendererMain = initRenderer(canvasMain, 1.32);
        rendererMain.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
        rendererMain.setSize(window.innerWidth, window.innerHeight);
        rendererMain.shadowMap.type = THREE.PCFSoftShadowMap;

        const rendererPip = initRenderer(canvasPip, 1.40);
        rendererPip.setSize(420, 240);

        const cameraMain = new THREE.PerspectiveCamera(16.0, window.innerWidth / window.innerHeight, 2.0, 95000);
        const cameraPip = new THREE.PerspectiveCamera(20.0, 420 / 240, 2.0, 95000);

        const sunLight = new THREE.DirectionalLight(0xfff6e5, 4.5);
        sunLight.position.set(1600, 2600, 1400); sunLight.castShadow = true;
        sunLight.shadow.mapSize.set(2048, 2048);
        sunLight.shadow.camera.near = 10; sunLight.shadow.camera.far = 7000;
        const d = 160;
        Object.assign(sunLight.shadow.camera, { left: -d, right: d, top: d, bottom: -d, bias: -0.0003 });
        scene.add(sunLight);

        const skyAmbient = new THREE.HemisphereLight(0xdbeafe, 0x1e293b, 1.65);
        const engineBounceLight = new THREE.PointLight(simCfg.flame_hex, 0.0, 650, 1.8);
        const pipTrackingSpot = new THREE.DirectionalLight(0xffffff, 2.5);
        scene.add(skyAmbient, engineBounceLight, pipTrackingSpot);

        function createCanvasTex(w, h, drawFn) {
            const c = document.createElement('canvas'); c.width = w; c.height = h;
            drawFn(c.getContext('2d'), c);
            return new THREE.CanvasTexture(c);
        }

        const proceduralEnvMap = createCanvasTex(1024, 512, (ctx) => {
            const g = ctx.createLinearGradient(0, 0, 0, 512);
            [[0,'#020817'],[.28,'#153e75'],[.44,'#568fc7'],[.49,'#ffedd5'],[.51,'#fed7aa'],[.54,'#1e3a5f'],[.75,'#0f2537'],[1,'#040d14']].forEach(s => g.addColorStop(...s));
            ctx.fillStyle = g; ctx.fillRect(0, 0, 1024, 512);
            const sg = ctx.createRadialGradient(720, 210, 4, 720, 210, 95);
            sg.addColorStop(0, 'rgba(255,255,255,1)'); sg.addColorStop(0.3, 'rgba(254,240,138,0.85)'); sg.addColorStop(1, 'rgba(254,240,138,0)');
            ctx.fillStyle = sg; ctx.fillRect(600, 100, 240, 220);
        });
        proceduralEnvMap.mapping = THREE.EquirectangularReflectionMapping;
        scene.environment = proceduralEnvMap;

        const skyDomeMat = new THREE.MeshBasicMaterial({
            map: createCanvasTex(256, 512, (ctx) => {
                const g = ctx.createLinearGradient(0, 0, 0, 512);
                [[0,'#01040d'],[.38,'#081c38'],[.70,'#1d4f82'],[.90,'#6ba3cc'],[.97,'#dbeafe'],[1,'#fef3c7']].forEach(s => g.addColorStop(...s));
                ctx.fillStyle = g; ctx.fillRect(0, 0, 256, 512);
            }),
            side: THREE.BackSide, depthWrite: false
        });
        const skyDome = new THREE.Mesh(new THREE.SphereGeometry(65000, 32, 24), skyDomeMat);
        scene.add(skyDome);

        const atmoLimbMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.0, side: THREE.BackSide, blending: THREE.AdditiveBlending, depthWrite: false });
        scene.add(new THREE.Mesh(new THREE.SphereGeometry(58000, 32, 20), atmoLimbMat));

        const starGeo = new THREE.BufferGeometry(), starPos = new Float32Array(2200 * 3);
        for(let i=0; i<6600; i+=3) {
            const u = Math.random(), v = Math.random(), th = u * 2 * Math.PI, ph = Math.acos(2 * v - 1);
            starPos[i] = 54000 * Math.sin(ph) * Math.cos(th);
            starPos[i+1] = 54000 * Math.sin(ph) * Math.sin(th);
            starPos[i+2] = 54000 * Math.cos(ph);
        }
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ size: 3.8, color: 0xffffff, transparent: true, opacity: 0.15 })));

        const landscapeGroup = new THREE.Group(); scene.add(landscapeGroup);
        const makeRepeatedTex = (w, h, repX, repY, drawFn) => {
            const tex = createCanvasTex(w, h, drawFn);
            tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
            tex.repeat.set(repX, repY);
            return tex;
        };

        const terrainTex = makeRepeatedTex(512, 512, 40, 40, (ctx) => {
            ctx.fillStyle = '#1e2920'; ctx.fillRect(0, 0, 512, 512);
            for(let i=0; i<1800; i++) {
                ctx.fillStyle = Math.random() > 0.45 ? 'rgba(42,58,40,0.35)' : 'rgba(68,64,52,0.28)';
                ctx.fillRect(Math.random()*512, Math.random()*512, 4 + Math.random()*18, 4 + Math.random()*18);
            }
        });
        const coastPlane = new THREE.Mesh(new THREE.PlaneGeometry(55000, 55000), new THREE.MeshStandardMaterial({ map: terrainTex, roughness: 0.92, metalness: 0.05, envMap: proceduralEnvMap }));
        coastPlane.rotation.x = -Math.PI / 2; coastPlane.position.set(-2500, -2.5, 0); coastPlane.receiveShadow = true;
        landscapeGroup.add(coastPlane);

        const oceanBumpTex = makeRepeatedTex(256, 256, 120, 120, (ctx) => {
            ctx.fillStyle = '#808080'; ctx.fillRect(0, 0, 256, 256);
            for(let i=0; i<900; i++) {
                ctx.fillStyle = (i % 2 === 0) ? 'rgba(220,220,220,0.35)' : 'rgba(30,30,30,0.35)';
                ctx.beginPath(); ctx.ellipse(Math.random()*256, Math.random()*256, 12 + Math.random()*20, 2 + Math.random()*3, 0.1, 0, Math.PI*2); ctx.fill();
            }
        });
        const oceanMesh = new THREE.Mesh(new THREE.PlaneGeometry(65000, 65000), new THREE.MeshStandardMaterial({ color: 0x092c4c, roughness: 0.12, metalness: 0.90, bumpMap: oceanBumpTex, bumpScale: 0.35, envMap: proceduralEnvMap }));
        oceanMesh.rotation.x = -Math.PI / 2; oceanMesh.position.set(14000, -8.0, 0); oceanMesh.receiveShadow = true;
        landscapeGroup.add(oceanMesh);

        const mountainMat = new THREE.MeshStandardMaterial({ color: 0x1e2f42, roughness: 0.95, metalness: 0.05 });
        for(let mi=0; mi<18; mi++) {
            const mAng = Math.PI * 0.55 + (mi / 18) * Math.PI * 0.9, mDist = 9500 + (mi % 3) * 1800, mH = 280 + (mi * 73 % 340);
            const mCone = new THREE.Mesh(new THREE.ConeGeometry(900 + (mi%4)*350, mH, 7), mountainMat);
            mCone.position.set(Math.cos(mAng) * mDist, mH * 0.45 - 5.0, Math.sin(mAng) * mDist);
            mCone.rotation.y = mi * 1.1; landscapeGroup.add(mCone);
        }

        const pad = new THREE.Group(); scene.add(pad);
        const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x222a36, metalness: 0.85, roughness: 0.35, envMap: proceduralEnvMap });
        const concreteMat = new THREE.MeshStandardMaterial({ color: 0x3d4554, roughness: 0.95 });
        const pipeMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.35, metalness: 0.85, envMap: proceduralEnvMap });

        let chopstickGroup = new THREE.Group(), armLeftPivot = new THREE.Group(), armRightPivot = new THREE.Group();
        const { s1_mat } = simCfg;
        const isStarshipPad = s1_mat === 'ss', isSaturnOrH3 = (s1_mat === 'saturn' || s1_mat === 'al');
        const isMissilePad = (s1_mat === 'military' || s1_mat === 'cf'), isJokePad = (s1_mat === 'baguette' || s1_mat === 'pencil');

        if (isStarshipPad) {
            const gp = new THREE.Mesh(new THREE.CylinderGeometry(110, 125, 3.0, 32), concreteMat);
            gp.position.y = 0.5; gp.receiveShadow = true; pad.add(gp);

            const olmRing = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 4.2, 2.2, 24), darkSteelMat);
            olmRing.position.y = 4.2; olmRing.castShadow = olmRing.receiveShadow = true; pad.add(olmRing);
            for(let i=0; i<6; i++) {
                const ang = (i/6)*Math.PI*2, leg = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.52, 3.8, 12), darkSteelMat);
                leg.position.set(Math.cos(ang)*3.4, 2.1, Math.sin(ang)*3.4);
                leg.castShadow = leg.receiveShadow = true; pad.add(leg);
            }

            const towerGroup = new THREE.Group(); towerGroup.position.set(-11.5, 0, 0); pad.add(towerGroup);
            const tm = new THREE.Mesh(new THREE.BoxGeometry(6.2, 145.0, 6.2), darkSteelMat);
            tm.position.y = 72.5; tm.castShadow = tm.receiveShadow = true; towerGroup.add(tm);

            const lr = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.35, 18.0, 8), darkSteelMat);
            lr.position.y = 154.0; towerGroup.add(lr);

            chopstickGroup.position.set(0, 67.5, 0); towerGroup.add(chopstickGroup);
            const makeArm = (pivot, zSign) => {
                pivot.position.set(3.1, 0, zSign * 2.2); chopstickGroup.add(pivot);
                const arm = new THREE.Mesh(new THREE.BoxGeometry(16.0, 2.2, 1.3), darkSteelMat);
                arm.position.set(8.0, 0, 0); arm.castShadow = true; pivot.add(arm);
            };
            makeArm(armLeftPivot, 1); makeArm(armRightPivot, -1);
            armLeftPivot.rotation.y = -0.75; armRightPivot.rotation.y = 0.75;

            const tkMat = new THREE.MeshStandardMaterial({ color: 0xdde4ec, metalness: 0.8, roughness: 0.2, envMap: proceduralEnvMap });
            for(let ti=0; ti<6; ti++) {
                const tk = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 4.2, 18.0, 16), tkMat);
                tk.position.set(-45.0 - (ti%3)*12.0, 9.0, -25.0 - Math.floor(ti/3)*14.0);
                tk.castShadow = tk.receiveShadow = true; pad.add(tk);
            }
        } else if (isSaturnOrH3) {
            const gp = new THREE.Mesh(new THREE.BoxGeometry(70, 8.0, 70), concreteMat);
            gp.position.y = 0.5; gp.receiveShadow = true; pad.add(gp);
            const tg = new THREE.Group(); tg.position.set(-12.5, 0, 0); pad.add(tg);
            const rt = new THREE.Mesh(new THREE.BoxGeometry(7.0, 155.0, 7.0), new THREE.MeshStandardMaterial({ color: 0xb91c1c, metalness: 0.5, roughness: 0.4, envMap: proceduralEnvMap }));
            rt.position.y = 77.5; rt.castShadow = rt.receiveShadow = true; tg.add(rt);
        } else if (isMissilePad) {
            const sg = new THREE.Mesh(new THREE.CylinderGeometry(35, 40, 2.5, 16), new THREE.MeshStandardMaterial({ color: 0x272e25, roughness: 0.9 }));
            sg.position.y = -0.5; sg.receiveShadow = true; pad.add(sg);
            const hd = new THREE.Mesh(new THREE.BoxGeometry(7.5, 1.2, 7.5), new THREE.MeshStandardMaterial({ color: 0x3f4f38, metalness: 0.6, roughness: 0.4, envMap: proceduralEnvMap }));
            hd.position.set(-5.5, 2.5, 0); hd.rotation.z = 0.95; hd.castShadow = true; pad.add(hd);
        } else if (isJokePad) {
            const jp = new THREE.Mesh(new THREE.BoxGeometry(32, 4.0, 32), new THREE.MeshStandardMaterial({ color: s1_mat === 'baguette' ? 0x9a3412 : 0x0284c7, roughness: 0.7 }));
            jp.position.y = 0.5; jp.receiveShadow = true; pad.add(jp);
        }

        const saturnRollTex = createCanvasTex(512, 512, ctx => {
            ctx.fillStyle = '#f8fafc'; ctx.fillRect(0, 0, 512, 512); ctx.fillStyle = '#0f172a';
            [[0,0],[256,128],[0,256],[256,384]].forEach(([x,y]) => ctx.fillRect(x, y, 256, 128));
            ctx.fillStyle = '#b91c1c'; ctx.font = 'bold 36px sans-serif'; ctx.fillText('USA', 190, 480);
        });

        const baguetteTex = createCanvasTex(512, 512, (ctx, cvs) => {
            ctx.fillStyle = '#c68a4c'; ctx.fillRect(0, 0, 512, 512); ctx.fillStyle = '#e8b87d';
            for(let i=0; i<8; i++) {
                ctx.save(); ctx.translate(120 + (i%3)*120, 40 + i*60); ctx.rotate(-0.35);
                ctx.beginPath(); ctx.ellipse(0, 0, 75, 14, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
            }
            const id = ctx.getImageData(0,0,512,512);
            for(let k=0; k<id.data.length; k+=4) { const n = (Math.random() - 0.5) * 22; id.data[k]+=n; id.data[k+1]+=n; id.data[k+2]+=n; }
            ctx.putImageData(id, 0, 0);
        });

        const pencilTex = createCanvasTex(512, 512, ctx => {
            ctx.fillStyle = '#155e3b'; ctx.fillRect(0, 0, 512, 512);
            ctx.fillStyle = '#d97706'; ctx.font = 'bold 32px serif'; ctx.fillText('★ MITSUBISHI Hi-uni HB ★', 60, 260);
            ctx.fillStyle = '#ca8a04'; ctx.fillRect(0, 470, 512, 42);
        });

        const tileTex = createCanvasTex(256, 256, ctx => {
            ctx.fillStyle = '#0f1216'; ctx.fillRect(0, 0, 256, 256);
            ctx.strokeStyle = '#1e242d'; ctx.lineWidth = 1.5;
            for(let x=0; x<256; x+=16) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 256); ctx.stroke(); }
            for(let y=0; y<256; y+=16) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(256, y); ctx.stroke(); }
        });

        const weldSeamTex = createCanvasTex(256, 512, ctx => {
            ctx.fillStyle = '#7f7f7f'; ctx.fillRect(0, 0, 256, 512);
            for(let y=32; y<512; y+=48) { ctx.fillStyle = '#9a9a9a'; ctx.fillRect(0, y, 256, 2); ctx.fillStyle = '#5c5c5c'; ctx.fillRect(0, y+2, 256, 2); }
            const id = ctx.getImageData(0,0,256,512);
            for(let k=0; k<id.data.length; k+=4) { const n = (Math.random() - 0.5) * 14; id.data[k]+=n; id.data[k+1]+=n; id.data[k+2]+=n; }
            ctx.putImageData(id, 0, 0);
        });
        [saturnRollTex, weldSeamTex].forEach(t => t.wrapS = t.wrapT = THREE.RepeatWrapping);

        function getRealisticMaterial(matId) {
            const presets = {
                saturn: { map: saturnRollTex, roughness: 0.35, metalness: 0.15, envMap: proceduralEnvMap, bumpMap: weldSeamTex, bumpScale: 0.008 },
                baguette: { map: baguetteTex, roughness: 0.95, metalness: 0.02 },
                pencil: { map: pencilTex, roughness: 0.45, metalness: 0.25, envMap: proceduralEnvMap },
                ss: { color: 0xf1f5f9, roughness: 0.14, metalness: 0.95, envMap: proceduralEnvMap, bumpMap: weldSeamTex, bumpScale: 0.012, roughnessMap: weldSeamTex },
                al: { color: 0xc2410c, roughness: 0.70, metalness: 0.15, bumpMap: weldSeamTex, bumpScale: 0.006 },
                cf: { color: 0x111317, roughness: 0.85, metalness: 0.08, bumpMap: tileTex, bumpScale: 0.02 },
                military: { color: 0x3f4f38, roughness: 0.65, metalness: 0.35, envMap: proceduralEnvMap, bumpMap: weldSeamTex, bumpScale: 0.008 }
            };
            return new THREE.MeshStandardMaterial(presets[matId] || { color: 0x3f3f46, roughness: 0.32, metalness: 0.85, envMap: proceduralEnvMap, bumpMap: weldSeamTex, bumpScale: 0.008 });
        }

        const blackTileMat = new THREE.MeshStandardMaterial({ color: 0x111317, roughness: 0.88, metalness: 0.1, bumpMap: tileTex, bumpScale: 0.03 });
        const rocket = new THREE.Group(); rocket.position.y = 6.0; scene.add(rocket);
        const s1Group = new THREE.Group(); scene.add(s1Group);
        const { s1_len: s1Len, s2_len: s2Len } = simCfg;
        const s1Mat = getRealisticMaterial(simCfg.s1_mat), s2Mat = getRealisticMaterial(simCfg.s2_mat);

        const isPencil = s1_mat === 'pencil';
        const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, isPencil ? 6 : 36), s1Mat);
        s1Body.position.y = s1Len / 2; s1Body.castShadow = s1Body.receiveShadow = true; s1Group.add(s1Body);

        let frostMesh = null;
        if (s1_mat === 'ss' || s1_mat === 'saturn') {
            frostMesh = new THREE.Mesh(new THREE.CylinderGeometry(1.124, 1.124, s1Len * 0.65, isPencil ? 6 : 36), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.95, metalness: 0.05, transparent: true, opacity: 0.72, depthWrite: false }));
            frostMesh.position.y = s1Len * 0.48; s1Group.add(frostMesh);
        }

        if (!isPencil && s1_mat !== 'baguette') {
            [[1.14, s1Len * 0.48, 0.065, 0.92], [-1.14, s1Len * 0.45, 0.05, 0.85]].forEach(([x, y, r, hRatio]) => {
                const fp = new THREE.Mesh(new THREE.CylinderGeometry(r, r, s1Len * hRatio, 12), pipeMat);
                fp.position.set(x, y, 0); fp.castShadow = true; s1Group.add(fp);
            });
            for(let ry = 2.5; ry < s1Len; ry += 3.8) {
                const ring = new THREE.Mesh(new THREE.TorusGeometry(1.125, 0.015, 6, 24), darkSteelMat);
                ring.rotation.x = Math.PI / 2; ring.position.y = ry; ring.castShadow = true; s1Group.add(ring);
            }
        }

        if (simCfg.spacex_return) {
            const cp = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 3.8, 16), new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.9, roughness: 0.25, envMap: proceduralEnvMap }));
            cp.rotation.x = Math.PI / 2; cp.position.set(0, s1Len - 2.2, 0); cp.castShadow = true; s1Group.add(cp);
        }

        const laserCoreTex = createCanvasTex(64, 256, (ctx) => {
            const gy = ctx.createLinearGradient(0, 0, 0, 256);
            [[0,'rgba(255,255,255,1)'],[.1,'rgba(224,242,254,0.98)'],[.35,'rgba(96,165,250,0.85)'],[.75,'rgba(29,78,216,0.22)'],[1,'rgba(0,0,0,0)']].forEach(s => gy.addColorStop(...s));
            ctx.fillStyle = gy; ctx.fillRect(0, 0, 64, 256);
            ctx.globalCompositeOperation = 'destination-in';
            const gx = ctx.createLinearGradient(0, 0, 64, 0);
            [[0,'rgba(0,0,0,0)'],[.28,'rgba(0,0,0,1)'],[.72,'rgba(0,0,0,1)'],[1,'rgba(0,0,0,0)']].forEach(s => gx.addColorStop(...s));
            ctx.fillStyle = gx; ctx.fillRect(0, 0, 64, 256);
        });

        const glowPointTex = createCanvasTex(64, 64, (ctx) => {
            const g = ctx.createRadialGradient(32, 32, 2, 32, 32, 31);
            [[0,'rgba(255,255,255,1)'],[.25,'rgba(147,197,253,0.85)'],[.65,'rgba(37,99,235,0.2)'],[1,'rgba(0,0,0,0)']].forEach(s => g.addColorStop(...s));
            ctx.fillStyle = g; ctx.fillRect(0, 0, 64, 64);
        });

        const diamondDiskTex = createCanvasTex(64, 64, (ctx) => {
            const g = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
            [[0,'rgba(255,255,255,1)'],[.35,'rgba(186,230,253,0.85)'],[.75,'rgba(59,130,246,0.3)'],[1,'rgba(0,0,0,0)']].forEach(s => g.addColorStop(...s));
            ctx.fillStyle = g; ctx.beginPath();
            ctx.moveTo(32, 4); ctx.lineTo(58, 32); ctx.lineTo(32, 60); ctx.lineTo(6, 32); ctx.closePath(); ctx.fill();
        });

        const s1NozzleTips = [], s2NozzleTips = [], boosterNozzleTips = [];
        const s1InconelNozzleMat = new THREE.MeshStandardMaterial({ color: 0x1f242d, metalness: 0.95, roughness: 0.25, emissive: new THREE.Color(0xff4500), emissiveIntensity: 0.0, side: THREE.DoubleSide, envMap: proceduralEnvMap });
        const s2InconelNozzleMat = s1InconelNozzleMat.clone();
        const s1EngineGimbalGroup = new THREE.Group(); s1Group.add(s1EngineGimbalGroup);

        function buildFullDetailedEngineCluster(parent, count, basePosY, epsScale, tipArray, flameHex, nozzleMaterial) {
            const group = new THREE.Group(); group.position.y = basePosY;
            const bellH = 1.2 * epsScale, exitRadius = 0.22 * Math.pow(epsScale, 0.65) * 1.65;
            const nozzleGeo = new THREE.CylinderGeometry(0.11, exitRadius, bellH, 16, 1, true);
            nozzleGeo.translate(0, -bellH / 2, 0);

            const plumeLen = 18.0;
            const innerConeGeo = new THREE.CylinderGeometry(exitRadius * 0.82, exitRadius * 0.15, plumeLen, 12, 1, true);
            innerConeGeo.translate(0, -plumeLen / 2, 0);
            const innerConeMat = new THREE.MeshBasicMaterial({ map: laserCoreTex, color: flameHex, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });

            const corePlaneGeo = new THREE.PlaneGeometry(exitRadius * 1.55, plumeLen);
            corePlaneGeo.translate(0, -plumeLen / 2, 0);
            const coreMat = new THREE.MeshBasicMaterial({ map: laserCoreTex, color: 0xffffff, transparent: true, opacity: 0.92, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });

            const glowMat = new THREE.SpriteMaterial({ map: glowPointTex, color: flameHex, blending: THREE.AdditiveBlending, depthWrite: false, fog: false });
            const diskMat = new THREE.SpriteMaterial({ map: diamondDiskTex, color: 0xffffff, blending: THREE.AdditiveBlending, depthWrite: false, fog: false });

            const enginePositions = [];
            if (count === 33) {
                for(let i=0; i<3; i++) enginePositions.push({ x: Math.cos(i/3*Math.PI*2)*0.22, z: Math.sin(i/3*Math.PI*2)*0.22, isCenter: true });
                for(let i=0; i<10; i++) enginePositions.push({ x: Math.cos(i/10*Math.PI*2)*0.54, z: Math.sin(i/10*Math.PI*2)*0.54, isCenter: false });
                for(let i=0; i<20; i++) enginePositions.push({ x: Math.cos(i/20*Math.PI*2)*0.88, z: Math.sin(i/20*Math.PI*2)*0.88, isCenter: false });
            } else if (count === 1) enginePositions.push({ x: 0, z: 0, isCenter: true });
            else {
                for(let i=0; i<count; i++) enginePositions.push({ x: Math.cos(i/count*Math.PI*2)*0.68, z: Math.sin(i/count*Math.PI*2)*0.68, isCenter: (i < 3) });
            }

            for(let pos of enginePositions) {
                const engUnit = new THREE.Group(); engUnit.position.set(pos.x, 0, pos.z);
                const nMesh = new THREE.Mesh(nozzleGeo, nozzleMaterial); nMesh.castShadow = true; engUnit.add(nMesh);

                const tipObj = new THREE.Object3D(); tipObj.position.set(0, -bellH * 0.86, 0);
                const glowSp = new THREE.Sprite(glowMat);
                glowSp.scale.set(exitRadius * 2.1, exitRadius * 2.1, 1.0); glowSp.position.y = -0.35; glowSp.visible = false;
                tipObj.add(glowSp);

                const crossGroup = new THREE.Group();
                const coneMesh = new THREE.Mesh(innerConeGeo, innerConeMat);
                const coreP1 = new THREE.Mesh(corePlaneGeo, coreMat);
                const coreP2 = new THREE.Mesh(corePlaneGeo, coreMat);
                coreP2.rotation.y = Math.PI / 2;
                crossGroup.add(coneMesh, coreP1, coreP2); crossGroup.visible = false;
                tipObj.add(crossGroup);

                const disks = [];
                for(let k=1; k<=5; k++) {
                    const mDisk = new THREE.Sprite(diskMat);
                    mDisk.position.y = -k * 2.6; mDisk.scale.set(exitRadius * 1.45, exitRadius * 0.85, 1.0); mDisk.visible = false;
                    tipObj.add(mDisk); disks.push(mDisk);
                }

                engUnit.add(tipObj);
                tipArray.push({ node: tipObj, isCenter: pos.isCenter, glow: glowSp, cross: crossGroup, disks: disks, firing: false, exitR: exitRadius });
                group.add(engUnit);
            }
            parent.add(group);
        }

        buildFullDetailedEngineCluster(s1EngineGimbalGroup, simCfg.s1_eng, 0.0, 0.72 + (simCfg.s1_eps / 70.0) * 0.65, s1NozzleTips, simCfg.flame_hex, s1InconelNozzleMat);

        const mainCombinedPlumeMat = new THREE.MeshBasicMaterial({ map: laserCoreTex, color: simCfg.flame_hex, transparent: true, opacity: 0.90, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });
        const mainCombinedPlumeGeo = new THREE.CylinderGeometry(0.95, 2.1, 40.0, 20, 1, true); mainCombinedPlumeGeo.translate(0, -20.0, 0);
        const innerBrightGeo = new THREE.CylinderGeometry(0.68, 0.25, 32.0, 16, 1, true); innerBrightGeo.translate(0, -16.0, 0);
        const innerBrightMat = new THREE.MeshBasicMaterial({ map: laserCoreTex, color: 0xffffff, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });

        const mainCombinedGroup = new THREE.Group();
        mainCombinedGroup.position.y = -0.85;
        mainCombinedGroup.add(new THREE.Mesh(mainCombinedPlumeGeo, mainCombinedPlumeMat), new THREE.Mesh(innerBrightGeo, innerBrightMat));
        mainCombinedGroup.visible = false;
        s1EngineGimbalGroup.add(mainCombinedGroup);

        const underglowSp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowPointTex, color: simCfg.flame_hex, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0, fog: false }));
        underglowSp.scale.set(95.0, 95.0, 1.0); scene.add(underglowSp);

        const engineHaloGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowPointTex, color: simCfg.flame_hex, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0, fog: false }));
        engineHaloGlow.scale.set(6.5, 6.5, 1.0); scene.add(engineHaloGlow);

        const vaporMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.0, side: THREE.DoubleSide, depthWrite: false, fog: false });
        const vaporCone = new THREE.Mesh(new THREE.ConeGeometry(2.8, 4.5, 32, 1, true), vaporMat);
        vaporCone.position.set(0, s1Len * 0.82, 0); rocket.add(vaporCone);

        const wingsGroup = new THREE.Group(); s1Group.add(wingsGroup);
        const aoaRad = (simCfg.aoa * Math.PI) / 180.0;
        if (simCfg.wing_id === 'grid') {
            for(let i=0; i<4; i++) {
                const ang = (i / 4) * Math.PI * 2 + Math.PI / 4, gf = new THREE.Group();
                gf.position.set(Math.cos(ang)*1.22, s1Len - 1.1, Math.sin(ang)*1.22);
                gf.rotation.y = -ang; gf.rotation.z = aoaRad;
                const gb = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.14, 1.25), darkSteelMat);
                gb.position.x = 0.62; gb.castShadow = true; gf.add(gb); wingsGroup.add(gf);
            }
        } else if (simCfg.wing_id === 'starship_flap') {
            [-1, 1].forEach(side => {
                const fl = new THREE.Mesh(new THREE.BoxGeometry(1.6, 4.2, 0.12), darkSteelMat);
                fl.position.set(side * 1.7, 2.8, 0); fl.rotation.z = side * 0.15; fl.rotation.x = aoaRad;
                fl.castShadow = true; wingsGroup.add(fl);
            });
        } else if (simCfg.wing_id === 'missile_fin') {
            for(let i=0; i<4; i++) {
                const ang = (i / 4) * Math.PI * 2, fin = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.4, 0.08), darkSteelMat);
                fin.position.set(Math.cos(ang)*1.4, 1.6, Math.sin(ang)*1.4); fin.rotation.y = -ang; fin.castShadow = true; wingsGroup.add(fin);
            }
        } else if (simCfg.wing_id === 'delta_wing') {
            [-1, 1].forEach(side => {
                const s = new THREE.Shape(); s.moveTo(0,0); s.lineTo(side*4.8, -1.8); s.lineTo(side*4.2, -6.5); s.lineTo(0, -5.2);
                const dm = new THREE.Mesh(new THREE.ShapeGeometry(s), s1Mat);
                dm.position.set(0, s1Len * 0.45, 0); dm.castShadow = true; wingsGroup.add(dm);
            });
        }

        const boosterUnits = [];
        if (simCfg.strapon_count > 0 && simCfg.strapon_type !== 'none') {
            const isSRB = simCfg.strapon_type === 'srb', isSoyuz = simCfg.strapon_type === 'soyuz';
            const bMat = isSRB ? new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4 }) : s1Mat;
            for(let i=0; i<simCfg.strapon_count; i++) {
                const ang = (i / simCfg.strapon_count) * Math.PI * 2, bUnit = new THREE.Group();
                bUnit.position.set(Math.cos(ang)*(isSoyuz ? 2.3 : 2.15), 0, Math.sin(ang)*(isSoyuz ? 2.3 : 2.15));
                const bLen = s1Len * (isSoyuz ? 0.75 : 0.84), topR = isSoyuz ? 0.42 : 0.68, botR = isSoyuz ? 0.78 : 0.68;
                const bBody = new THREE.Mesh(new THREE.CylinderGeometry(topR, botR, bLen, 24), bMat);
                bBody.position.y = bLen / 2; bBody.castShadow = true; bUnit.add(bBody);
                const bNose = new THREE.Mesh(new THREE.ConeGeometry(topR, 2.2, 24), bMat);
                bNose.position.y = bLen + 1.1; bNose.castShadow = true; bUnit.add(bNose);

                const localTips = [];
                buildFullDetailedEngineCluster(bUnit, 1, 0, 0.9, localTips, simCfg.flame_hex, s1InconelNozzleMat);
                localTips.forEach(t => boosterNozzleTips.push(t));
                s1Group.add(bUnit);
                boosterUnits.push({ mesh: bUnit, angle: ang, detached: false, vx: 0, vy: 0, vz: 0, rx: 0, rz: 0, tips: localTips, sepAge: 0 });
            }
        }

        const interStage = new THREE.Group(); interStage.position.y = s1Len; s1Group.add(interStage);
        const interTruss = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, 2.2, 24, 4, true), darkSteelMat);
        interTruss.position.y = 1.1; interTruss.castShadow = true; interStage.add(interTruss);

        const s2Group = new THREE.Group(); s2Group.position.y = s1Len + 2.2; rocket.add(s2Group);
        const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, isPencil ? 6 : 36), s2Mat);
        s2Body.position.y = s2Len / 2; s2Body.castShadow = s2Body.receiveShadow = true; s2Group.add(s2Body);

        if (simCfg.s2_mat === 'ss') {
            const hs = new THREE.Mesh(new THREE.CylinderGeometry(1.128, 1.128, s2Len, 24, 1, true, 0, Math.PI), blackTileMat);
            hs.position.y = s2Len / 2; hs.castShadow = true; s2Group.add(hs);
        }

        buildFullDetailedEngineCluster(s2Group, simCfg.s2_eng, 0.0, 0.95 + (simCfg.s2_eps / 280.0) * 0.95, s2NozzleTips, simCfg.s2_flame_hex, s2InconelNozzleMat);

        const payloadGroup = new THREE.Group(); payloadGroup.position.y = s2Len + 1.8; s2Group.add(payloadGroup);
        const satBus = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 2.4, 16), new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.95, roughness: 0.2, envMap: proceduralEnvMap }));
        satBus.castShadow = true; payloadGroup.add(satBus);

        const fairingHalves = [];
        if (simCfg.fairing_shape === 'abort_tower') {
            const cap = new THREE.Mesh(new THREE.ConeGeometry(1.14, 2.8, 24), s2Mat); cap.position.y = s2Len + 1.4; cap.castShadow = true;
            const spk = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.14, 3.8, 12), darkSteelMat); spk.position.y = s2Len + 4.2; spk.castShadow = true;
            s2Group.add(cap, spk);
        } else if (simCfg.fairing_shape === 'pencil_tip') {
            const wd = new THREE.Mesh(new THREE.ConeGeometry(1.12, 3.8, 6), new THREE.MeshStandardMaterial({ color: 0xd4a373, roughness: 0.9 }));
            wd.position.y = s2Len + 1.9; wd.castShadow = true;
            const ld = new THREE.Mesh(new THREE.ConeGeometry(0.24, 1.0, 6), new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.4 }));
            ld.position.y = s2Len + 3.8; ld.castShadow = true;
            s2Group.add(wd, ld);
        } else {
            const ogivePts = [], noseH = simCfg.fairing_shape === 'icbm_warhead' ? 3.8 : 5.8;
            for(let i=0; i<=16; i++) { const t = i / 16; ogivePts.push(new THREE.Vector2(Math.max(0.01, 1.12 * Math.pow(1.0 - Math.pow(t, 1.65), 0.72)), t * noseH)); }
            [-1, 1].forEach(side => {
                const hm = new THREE.Mesh(new THREE.LatheGeometry(ogivePts, 16, side === 1 ? 0 : Math.PI, Math.PI), s2Mat);
                hm.position.y = s2Len; hm.castShadow = true; s2Group.add(hm);
                if (simCfg.fairing_shape === 'starship_crew' && side === 1) {
                    const bh = new THREE.Mesh(new THREE.LatheGeometry(ogivePts, 16, 0, Math.PI), blackTileMat);
                    bh.scale.set(1.006, 1.0, 1.006); bh.position.y = s2Len; bh.castShadow = true; s2Group.add(bh);
                }
                fairingHalves.push({ mesh: hm, side: side, detached: false, vx: 0, vy: 0, rotZ: 0 });
            });
        }

        const rcsNozzles = [];
        const rcsConeGeo = new THREE.CylinderGeometry(0.03, 0.52, 4.2, 12, 1, true);
        rcsConeGeo.translate(0, -2.1, 0); rcsConeGeo.rotateZ(Math.PI / 2);

        const rcsDirs = [
            { id: "+X", dx: 1, dy: 0, dz: 0, rotY: 0 }, { id: "-X", dx: -1, dy: 0, dz: 0, rotY: Math.PI },
            { id: "+Z", dx: 0, dy: 0, dz: 1, rotY: -Math.PI / 2 }, { id: "-Z", dx: 0, dy: 0, dz: -1, rotY: Math.PI / 2 }
        ];

        function addFullRcsCluster(parent, yPos, isS1) {
            for(let d of rcsDirs) {
                const mount = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.24, 0.16), darkSteelMat);
                mount.position.set(d.dx * 1.13, yPos, d.dz * 1.13);
                const jMat = new THREE.MeshBasicMaterial({ map: laserCoreTex, color: 0xe0f2fe, transparent: true, opacity: 0.0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });
                const jc = new THREE.Mesh(rcsConeGeo, jMat); jc.rotation.y = d.rotY;
                mount.add(jc); parent.add(mount);
                rcsNozzles.push({ mount, jetCone: jc, jetMat: jMat, dir: d, isS1, timer: 0.0 });
            }
        }
        addFullRcsCluster(s1Group, s1Len - 0.85, true);
        addFullRcsCluster(s2Group, s2Len - 0.75, false);

        const cloudTex = createCanvasTex(128, 128, ctx => {
            [[64,64,58,.95],[46,54,42,.75],[82,58,40,.75],[58,80,44,.7],[74,46,36,.65]].forEach(([x,y,r,a]) => {
                const g = ctx.createRadialGradient(x, y, 2, x, y, r);
                [[0,`rgba(255,255,255,${a})`],[.45,`rgba(241,245,249,${a*.65})`],[.8,`rgba(203,213,225,${a*.25})`],[1,'rgba(180,200,220,0)']].forEach(s => g.addColorStop(...s));
                ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2); ctx.fill();
            });
        });

        const sparkTex = createCanvasTex(32, 32, ctx => {
            const g = ctx.createRadialGradient(16,16,1, 16,16,15);
            [[0,'rgba(255,255,255,1)'],[.4,'rgba(255,220,120,0.95)'],[1,'rgba(255,40,0,0)']].forEach(s => g.addColorStop(...s));
            ctx.fillStyle = g; ctx.fillRect(0,0,32,32);
        });

        const cloudDeck = new THREE.Group(); scene.add(cloudDeck);
        for(let ci=0; ci<95; ci++) {
            const csp = new THREE.Sprite(new THREE.SpriteMaterial({ map: cloudTex, transparent: true, opacity: 0.32, depthWrite: false }));
            let cx = (Math.random() - 0.5) * 4200.0, cz = (Math.random() - 0.5) * 4200.0;
            if (Math.abs(cx) < 190 && Math.abs(cz) < 190) { cx += (cx >= 0 ? 230 : -230); cz += (cz >= 0 ? 230 : -230); }
            csp.position.set(cx, 135.0 + (Math.random() - 0.5) * 35.0, cz);
            const csc = 95.0 + Math.random() * 130.0;
            csp.scale.set(csc * 1.6, csc, 1); cloudDeck.add(csp);
        }

        const createPool = (count, mat) => Array.from({length: count}, () => {
            const sp = new THREE.Sprite(mat.clone()); sp.visible = false; scene.add(sp);
            return { sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1 };
        });

        const pool = createPool(1300, new THREE.SpriteMaterial({ map: cloudTex, transparent: true, opacity: 0, depthWrite: false, fog: false }));
        let pIdx = 0;
        function emitParticle(x, y, z, vx, vy, vz, s0, s1, life, opacity, hexColor=0xf8fafc, drag=0.985, buoyancy=0.015, litByFlame=false) {
            const p = pool[pIdx]; pIdx = (pIdx + 1) % pool.length;
            p.active = p.sp.visible = true;
            p.sp.position.set(x, Math.max(2.2, y), z);
            Object.assign(p, { vx, vy, vz, age: 0, maxAge: life, s0, s1, o: opacity, drag, buoyancy, lit: litByFlame, rotSpeed: (Math.random() - 0.5) * 0.04 });
            p.sp.material.rotation = Math.random() * Math.PI * 2;
            p.sp.material.color.setHex(hexColor);
        }

        const sparks = createPool(300, new THREE.SpriteMaterial({ map: sparkTex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
        let sIdx = 0;
        function emitSpark(x, y, z, vx, vy, vz, hexCol) {
            const s = sparks[sIdx]; sIdx = (sIdx + 1) % sparks.length;
            s.active = s.sp.visible = true;
            s.sp.position.set(x, Math.max(2.5, y), z);
            Object.assign(s, { vx, vy, vz, age: 0, maxAge: 14 });
            s.sp.material.color.setHex(hexCol);
        }

        const iceShards = createPool(150, new THREE.SpriteMaterial({ map: cloudTex, color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, fog: false }));
        let iceIdx = 0;
        function emitIceShard(x, y, z, vx, vy, vz) {
            const ic = iceShards[iceIdx]; iceIdx = (iceIdx + 1) % iceShards.length;
            ic.active = ic.sp.visible = true;
            ic.sp.position.set(x, y, z);
            Object.assign(ic, { vx, vy, vz, age: 0, maxAge: 35 });
            ic.sp.scale.set(0.45, 0.45, 1);
        }

        function drawPrecisionOrbitMap(curAltKm, curDRangeKm, exploded, isOrbit) {
            if (!octx) return;
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

        function drawEngineClusterGraphic(stage, isThrust, isExploded, bThrust, bCaught) {
            if (!ectx) return;
            ectx.clearRect(0, 0, 48, 48);
            const cx = 24, cy = 24;
            const drawRings = (rings, active, activeColor) => {
                rings.forEach(([count, radius, size, col]) => {
                    for(let i=0; i<count; i++) {
                        const ang = (i / count) * Math.PI * 2;
                        ectx.beginPath(); ectx.arc(cx + Math.cos(ang)*radius, cy + Math.sin(ang)*radius, size, 0, Math.PI*2);
                        ectx.fillStyle = active ? (col || activeColor) : '#334155'; ectx.fill();
                    }
                });
            };

            if (stage === 1 && !stage1Detached) {
                drawRings([[20, 19, 1.4, '#38bdf8'], [10, 11.5, 1.5, '#60a5fa'], [3, 4.8, 1.8, '#ffffff']], isThrust && !isExploded);
            } else if (stage1Detached && bThrust && !bCaught) {
                drawRings([[3, 5, 2.2, '#ffffff']], true);
            } else if (stage === 2) {
                for(let i=0; i<6; i++) {
                    const ang = (i / 6) * Math.PI * 2;
                    ectx.beginPath(); ectx.arc(cx + Math.cos(ang)*(i % 2 === 0 ? 14 : 7), cy + Math.sin(ang)*(i % 2 === 0 ? 14 : 7), 2.5, 0, Math.PI*2);
                    ectx.fillStyle = isThrust ? '#38bdf8' : '#334155'; ectx.fill();
                }
            }
        }

        const tStart = performance.now();
        let boosterDetached = false, stage1Detached = false, fairingDetached = false, camShake = 0.0;
        let prevRcsCmd = 0.0, prevBoosterRcs = 0.0, counterPulseTimer = 0.0, counterDirSign = 0.0;
        const tempV = new THREE.Vector3(), activeFocusWorld = new THREE.Vector3(), smoothCamTarget = new THREE.Vector3(0, 6.0, 0);
        const baseFlameColor = new THREE.Color(simCfg.flame_hex), seaLevelFlameColor = new THREE.Color(0xffedd5), curDynamicFlameColor = new THREE.Color(), steamWhiteColor = new THREE.Color(0xf8fafc);

        function animate(now) {
            if (isMissionEnded) return;
            requestAnimationFrame(animate);

            const elapsedSec = (now - tStart) / 1000.0;
            const simT = simCfg.is_preview ? -10.0 : (-10.0 + elapsedSec);
            if (!simCfg.is_preview) updateFlightCallouts(simT);

            let idx = 0;
            while (idx < simData.length - 1 && simData[idx + 1].t <= simT) idx++;
            const nIdx = Math.min(idx + 1, simData.length - 1), p0 = simData[idx], p1 = simData[nIdx];
            const a = (p1.t > p0.t) ? Math.max(0, Math.min(1, (simT - p0.t) / (p1.t - p0.t))) : 0;
            const lerpProp = k => p0[k] + (p1[k] - p0[k]) * a;

            const rx = lerpProp('x') * 0.1, ry = lerpProp('y') * 0.1;
            const alt = lerpProp('alt'), vel = lerpProp('v'), q = lerpProp('q'), pitch = lerpProp('pitch'), mach = lerpProp('mach'), accG = lerpProp('g');
            const rcsCmd = lerpProp('rcs_cmd'), s1PropVal = lerpProp('s1_prop_pct'), s2PropVal = lerpProp('s2_prop_pct');
            const pitchDegVal = lerpProp('pitch_deg'), apogeeVal = lerpProp('apogee_km'), pcVal = lerpProp('chamber_p');
            const bX = lerpProp('b_x'), bY = lerpProp('b_y'), bPitch = lerpProp('b_pitch');
            const bRcsCmd = (p0.b_rcs !== undefined) ? (p0.b_rcs + ((p1.b_rcs || 0) - p0.b_rcs) * a) : 0.0;

            rocket.position.set(rx, ry + 6.0, 0); rocket.rotation.z = -pitch; rocket.updateMatrixWorld(true);

            oceanBumpTex.offset.x = (now * 0.00004) % 1.0; oceanBumpTex.offset.y = (now * 0.00002) % 1.0;

            const targetGimbal = (p0.stage === 1 && !stage1Detached && alt > 0.5 && alt < 60.0) 
                ? THREE.MathUtils.clamp(pitch * 0.045, -0.06, 0.06) 
                : (stage1Detached && p0.b_thrust ? THREE.MathUtils.clamp(bPitch * 0.25, -0.08, 0.08) : 0.0);
            s1EngineGimbalGroup.rotation.z = THREE.MathUtils.lerp(s1EngineGimbalGroup.rotation.z, targetGimbal, 0.15);

            if (frostMesh) frostMesh.material.opacity = Math.max(0.0, 0.72 - (alt / 35.0) * 0.72);

            starMat.opacity = Math.min(0.95, Math.max(0.05, (alt - 15.0) / 55.0));
            const sf = Math.min(1.0, Math.max(0.0, (alt - 12.0) / 70.0));
            skyDomeMat.color.setRGB(1.0 - sf * 0.95, 1.0 - sf * 0.92, 1.0 - sf * 0.85);
            atmoLimbMat.opacity = alt > 20.0 ? Math.min(0.42, (alt - 20.0) / 55.0) : 0.0;

            const ux = Math.sin(pitch), uy = Math.cos(pitch), perpX = Math.cos(pitch), perpY = -Math.sin(pitch);

            if (mach >= 0.96 && mach <= 1.22 && alt < 18.0 && !simCfg.is_preview) {
                vaporMat.opacity = Math.sin((mach - 0.96) / 0.26 * Math.PI) * 0.75;
                vaporCone.scale.set(1.0 + Math.random()*0.05, 1.0, 1.0 + Math.random()*0.05);
            } else vaporMat.opacity = 0.0;

            if (simT > 0 && simT < 12.0 && Math.random() < 0.65) {
                for(let k=0; k<2; k++) {
                    const h = Math.random() * s1Len, aAng = Math.random() * Math.PI * 2;
                    emitIceShard(rx + Math.cos(aAng)*1.18, ry + 6.0 + h, Math.sin(aAng)*1.18, (Math.random()-0.5)*0.3, -0.6 - Math.random()*0.5, (Math.random()-0.5)*0.3);
                }
            }

            if (!p0.strapon && !boosterDetached && boosterUnits.length > 0 && !simCfg.is_preview) {
                boosterDetached = true; playHeavySeparationSound(); camShake = 0.22;
                for(let b of boosterUnits) {
                    b.detached = true; b.sepAge = 0.0; scene.attach(b.mesh);
                    b.tips.forEach(t => { t.glow.visible = t.cross.visible = false; t.disks.forEach(d => d.visible = false); });
                    const outX = Math.cos(b.angle), outZ = Math.sin(b.angle), sepP = simCfg.sep_thrust;
                    b.vx = perpX * outX * (0.12 * sepP); b.vy = -0.15 * sepP; b.vz = outZ * (0.12 * sepP); b.rx = b.rz = 0.0;
                    b.mesh.getWorldPosition(tempV);
                    for(let k=0; k<6; k++) emitParticle(tempV.x, tempV.y + s1Len * 0.65, tempV.z, outX * (0.4 + Math.random()*0.4), (Math.random()-0.5)*0.3, outZ * (0.4 + Math.random()*0.4), 0.3, 2.2, 24, 0.55, 0xe0f2fe, 0.94, 0.0);
                }
            }
            if (boosterDetached) {
                for(let b of boosterUnits) {
                    b.sepAge += 0.016;
                    const outX = Math.cos(b.angle), outZ = Math.sin(b.angle);
                    if (b.sepAge < 1.8) { b.vx += perpX * outX * 0.018; b.vz += outZ * 0.018; b.rx += outZ * 0.0035; b.rz += -outX * 0.0035; }
                    b.vy -= (0.45 + Math.min(1.5, b.sepAge * 0.35)) * 0.016;
                    b.mesh.position.add(tempV.set(b.vx, b.vy, b.vz));
                    b.mesh.rotation.x += b.rx; b.mesh.rotation.z += b.rz;
                }
            }

            const isSeparated = (p0.stage === 2 || p0.b_active);
            if (isSeparated && !stage1Detached && !simCfg.is_preview) {
                stage1Detached = true; hotStagingSparkTimer = 2.6; playHeavySeparationSound(); camShake = 0.55;
                mainCombinedGroup.visible = false;
                s1Group.localToWorld(tempV.set(0, s1Len, 0));
                for(let i=0; i<36; i++) {
                    const ang = (i / 36) * Math.PI * 2;
                    emitParticle(tempV.x + Math.cos(ang)*1.2, tempV.y, tempV.z + Math.sin(ang)*1.2, Math.cos(ang)*2.8, (Math.random()-0.5)*0.5, Math.sin(ang)*2.8, 1.2, 9.5, 38, 0.85, simCfg.flame_hex, 0.92, 0.0);
                }
            }

            if (hotStagingSparkTimer > 0) {
                hotStagingSparkTimer -= 0.016;
                s1Group.localToWorld(tempV.set(0, s1Len, 0));
                for(let k=0; k<5; k++) {
                    const hAngle = Math.random() * Math.PI * 2, bSpd = 2.2 + Math.random() * 1.8;
                    emitSpark(tempV.x, tempV.y, tempV.z, Math.cos(hAngle) * bSpd, (Math.random()-0.5)*0.4, Math.sin(hAngle) * bSpd, 0xfde047);
                }
            }

            const bY_scaled = (bY * 0.1) + 6.0;
            if (simCfg.spacex_return && isStarshipPad) {
                const setArmState = (rot, text, col, speed) => {
                    armLeftPivot.rotation.y = THREE.MathUtils.lerp(armLeftPivot.rotation.y, rot, speed);
                    armRightPivot.rotation.y = THREE.MathUtils.lerp(armRightPivot.rotation.y, -rot, speed);
                    $('hud-arm').innerText = text; $('hud-arm').style.color = col;
                };
                if (p0.b_caught) setArmState(0.08, "CATCH LOCKED (PIN SECURED)", "#10b981", 0.25);
                else if (stage1Detached && bY <= 1500) setArmState(0.05, "CLOSING ARMS", "#38bdf8", 0.12);
                else if (stage1Detached && bY <= 4500) setArmState(-0.16, "DEPLOYED (WIDE READY)", "#34d399", 0.08);
                else setArmState(-0.75, "STOWED CLEAR", "#f59e0b", 0.05);
            }

            if (stage1Detached) {
                s1Group.visible = true; s1Group.position.set(bX * 0.1, bY_scaled, 0); s1Group.rotation.set(0, 0, -bPitch); s1Group.updateMatrixWorld(true);
                if (p0.b_thrust && !landingSonicBoomPlayed && bY <= 3600) { playLandingIgnitionBoom(); landingSonicBoomPlayed = true; camShake = 0.55; }

                if (actx && boosterRumble && boosterCrackle) {
                    if (p0.b_thrust && !p0.b_caught && bY <= 3600) {
                        const is13 = bY > 1200;
                        boosterRumble.gain.setTargetAtTime(is13 ? 3.8 : 2.4, actx.currentTime, 0.08);
                        boosterCrackle.gain.setTargetAtTime(is13 ? 2.6 : 1.4, actx.currentTime, 0.08);
                    } else {
                        boosterRumble.gain.setTargetAtTime(0.0001, actx.currentTime, 0.12);
                        boosterCrackle.gain.setTargetAtTime(0.0001, actx.currentTime, 0.12);
                    }
                }

                if (p0.b_caught) {
                    if (!catchPopPlayed) { playFirecrackerSnapSound(); catchPopPlayed = true; camShake = 0.45; }
                    s1NozzleTips.forEach(t => { t.glow.visible = t.cross.visible = false; t.disks.forEach(d => d.visible = false); });
                    mainCombinedGroup.visible = false;
                    $('tv-stage-badge').innerText = "TOWER CATCH SUCCESS"; $('tv-stage-badge').style.color = "#38bdf8";
                } else if (p0.b_thrust) {
                    mainCombinedGroup.visible = false;
                    const is3 = bY <= 1200;
                    s1NozzleTips.forEach((t, i) => {
                        const act = is3 ? t.isCenter : (i < 13);
                        t.glow.visible = t.cross.visible = act;
                        const fLen = 0.68 + Math.random() * 0.18;
                        t.cross.scale.set(0.85, fLen, 0.85);
                        t.disks.forEach((d, k) => { d.visible = act; d.position.y = -(k + 1) * 2.4 * fLen; d.scale.set(t.exitR * 1.35, t.exitR * 0.8, 1); });
                    });
                    if (bY <= 1200 && Math.random() < 0.5) {
                        s1Group.localToWorld(tempV.set(0, 0, 0));
                        emitParticle(tempV.x + (Math.random()-0.5)*2.5, tempV.y - 2, tempV.z - 4.0 + (Math.random()-0.5)*2.5, (Math.random()-0.5)*1.8, 0.3, (Math.random()-0.5)*1.8, 2.0, 10.0, 32, 0.38, 0xf8fafc, 0.95, 0.02, true);
                    }
                } else {
                    s1NozzleTips.forEach(t => { t.glow.visible = t.cross.visible = false; t.disks.forEach(d => d.visible = false); });
                    mainCombinedGroup.visible = false;
                }
            } else {
                s1Group.visible = true; s1Group.position.set(rx, ry + 6.0, 0); s1Group.rotation.z = -pitch; s1Group.updateMatrixWorld(true);
            }

            if (!p0.fairing && !fairingDetached && fairingHalves.length > 0 && !simCfg.is_preview) {
                fairingDetached = true; playHeavySeparationSound();
                for(let fh of fairingHalves) { fh.detached = true; scene.attach(fh.mesh); fh.vx = perpX * fh.side * 0.45; fh.vy = -0.25; fh.rotZ = -fh.side * 0.025; }
            }
            if (fairingDetached) {
                for(let fh of fairingHalves) { fh.mesh.position.x += fh.vx; fh.mesh.position.y += fh.vy; fh.vy -= 0.022; fh.mesh.rotation.z += fh.rotZ; }
            }

            const isEngineFiring = (p0.thrust && !p0.exploded && !simCfg.is_preview);
            s1InconelNozzleMat.emissiveIntensity = THREE.MathUtils.lerp(s1InconelNozzleMat.emissiveIntensity, (p0.stage === 1 && isEngineFiring) ? 1.25 : (p0.b_thrust && !p0.b_caught ? 1.1 : 0.0), (p0.stage === 1 && isEngineFiring) ? 0.06 : 0.018);
            s2InconelNozzleMat.emissiveIntensity = THREE.MathUtils.lerp(s2InconelNozzleMat.emissiveIntensity, (p0.stage === 2 && isEngineFiring) ? 1.35 : 0.0, (p0.stage === 2 && isEngineFiring) ? 0.08 : 0.015);

            if (isEngineFiring) {
                const activeTips = p0.stage === 1 ? s1NozzleTips : s2NozzleTips;
                const inactiveTips = p0.stage === 1 ? s2NozzleTips : (stage1Detached ? [] : s1NozzleTips);
                curDynamicFlameColor.copy(seaLevelFlameColor).lerp(baseFlameColor, Math.min(1.0, alt / 42.0));
                const curHex = curDynamicFlameColor.getHex();

                inactiveTips.forEach(t => { t.glow.visible = t.cross.visible = false; t.disks.forEach(d => d.visible = false); });
                boosterNozzleTips.forEach(t => {
                    t.glow.visible = t.cross.visible = Boolean(p0.strapon);
                    if (p0.strapon) {
                        const bp = 0.92 + Math.random()*0.15;
                        t.cross.scale.set(0.95, bp, 0.95);
                        t.disks.forEach((d, k) => { d.visible = true; d.position.y = -(k+1)*2.4*bp; });
                    } else t.disks.forEach(d => d.visible = false);
                });

                if (p0.stage === 1 && alt < 35.0 && !stage1Detached) {
                    mainCombinedGroup.visible = true; mainCombinedPlumeMat.color.copy(curDynamicFlameColor);
                    const atmExp = 1.0 + Math.min(0.16, Math.max(0.0, alt - 5.0) / 45.0);
                    mainCombinedGroup.scale.set(atmExp, 0.94 + Math.random() * 0.12, atmExp);
                    mainCombinedPlumeMat.opacity = Math.max(0.65, 0.92 - (alt / 60.0) * 0.3);
                } else mainCombinedGroup.visible = false;

                for(let tObj of activeTips) {
                    tObj.glow.visible = tObj.cross.visible = true;
                    const fPulse = 0.92 + Math.random() * 0.16;
                    tObj.cross.scale.set(1.0, fPulse * 0.85, 1.0);
                    tObj.disks.forEach((d, k) => { d.visible = alt < 70.0; d.position.y = -(k + 1) * 2.5 * fPulse; d.scale.set(tObj.exitR * (1.4 - k*0.12), tObj.exitR * 0.8, 1); });

                    if (Math.random() < (alt > 35.0 ? 0.28 : 0.05)) {
                        tObj.node.getWorldPosition(tempV);
                        const sprd = (Math.random() - 0.5) * 2.0, isJelly = alt > 38.0;
                        emitParticle(tempV.x - ux * 18.0, tempV.y - uy * 18.0, tempV.z - 5.0 + sprd, -ux * (3.2 + Math.random()*2.0) + perpX * sprd * 0.35, -uy * (3.2 + Math.random()*2.0) + perpY * sprd * 0.35, (Math.random() - 0.5) * 0.8, 1.0, isJelly ? 11.5 : 4.5, isJelly ? 42 : 22, isJelly ? 0.20 : 0.12, curHex, 0.98, 0.0, false);
                    }
                }

                rocket.localToWorld(tempV.set(0, p0.stage === 1 ? -2.2 : s1Len + 0.5, 0));
                engineHaloGlow.position.copy(tempV);
                engineHaloGlow.material.opacity = THREE.MathUtils.lerp(engineHaloGlow.material.opacity, 0.28 + Math.random()*0.06, 0.2);
                underglowSp.position.set(tempV.x - ux * 10.0, tempV.y - uy * 10.0, tempV.z);
                underglowSp.material.opacity = Math.max(0.0, (1.0 - alt / 25.0) * 0.28);
                engineBounceLight.intensity = Math.max(0.0, 8.5 - alt * 0.35);
                engineBounceLight.position.set(rx, ry + 3.0, 5.0);
                rendererMain.toneMappingExposure = THREE.MathUtils.lerp(rendererMain.toneMappingExposure, 1.18, 0.08);
            } else {
                [s1NozzleTips, s2NozzleTips, boosterNozzleTips].forEach(arr => arr.forEach(t => { t.glow.visible = t.cross.visible = false; t.disks.forEach(d => d.visible = false); }));
                mainCombinedGroup.visible = false;
                engineHaloGlow.material.opacity = THREE.MathUtils.lerp(engineHaloGlow.material.opacity, 0.0, 0.15);
                underglowSp.material.opacity = engineBounceLight.intensity = 0.0;
                rendererMain.toneMappingExposure = THREE.MathUtils.lerp(rendererMain.toneMappingExposure, 1.32, 0.05);
            }

            const cmdFired = Math.abs(rcsCmd) > 0.2 && Math.abs(prevRcsCmd) <= 0.2;
            if (cmdFired) { counterDirSign = rcsCmd > 0 ? -1.0 : 1.0; counterPulseTimer = 0.26; }
            prevRcsCmd = rcsCmd;
            const boosterCmdFired = stage1Detached && !p0.b_caught && Math.abs(bRcsCmd) > 0.2 && (Math.abs(prevBoosterRcs) <= 0.2 || Math.random() < 0.08);
            prevBoosterRcs = bRcsCmd;

            let isCounterBurst = false;
            if (counterPulseTimer > 0) { counterPulseTimer -= 0.016; if (counterPulseTimer <= 0) isCounterBurst = true; }

            let soundTriggeredThisFrame = false;
            for(let rcs of rcsNozzles) {
                let triggerPulse = false;
                if (!simCfg.is_preview && simT > 0 && !p0.exploded) {
                    if (!rcs.isS1 && stage1Detached) {
                        if (cmdFired && ((rcs.dir.dx < -0.5 && rcsCmd > 0) || (rcs.dir.dx > 0.5 && rcsCmd < 0))) triggerPulse = true;
                        if (isCounterBurst && ((rcs.dir.dx < -0.5 && counterDirSign > 0) || (rcs.dir.dx > 0.5 && counterDirSign < 0))) triggerPulse = true;
                    } else if (rcs.isS1) {
                        if (!stage1Detached && cmdFired && ((rcs.dir.dx < -0.5 && rcsCmd > 0) || (rcs.dir.dx > 0.5 && rcsCmd < 0))) triggerPulse = true;
                        else if (stage1Detached && !p0.b_caught && boosterCmdFired && ((rcs.dir.dx > 0.5 && bRcsCmd > 0) || (rcs.dir.dx < -0.5 && bRcsCmd < 0))) triggerPulse = true;
                    }
                }

                if (triggerPulse) {
                    rcs.timer = 0.11;
                    if (!soundTriggeredThisFrame) { playRcsPuffSound(); soundTriggeredThisFrame = true; }
                    rcs.mount.getWorldPosition(tempV);
                    const lDir = new THREE.Vector3(rcs.dir.dx, 0, rcs.dir.dz).normalize(), pQ = new THREE.Quaternion();
                    rcs.mount.parent.getWorldQuaternion(pQ); lDir.applyQuaternion(pQ);
                    for(let k=0; k<2; k++) {
                        const spd = 2.8 + k * 1.1;
                        emitParticle(tempV.x + lDir.x*0.5, tempV.y + lDir.y*0.5, tempV.z + lDir.z*0.5, lDir.x * spd, lDir.y * spd, lDir.z * spd, 0.18, 0.95, 6, 0.55, 0xe0f2fe, 0.88, 0.0, false);
                    }
                }

                if (rcs.timer > 0) {
                    rcs.timer -= 0.016;
                    rcs.jetMat.opacity = Math.min(0.92, (rcs.timer / 0.11) * 0.95);
                    rcs.jetCone.scale.set(0.85 + Math.random() * 0.3, 1.0, 1.0);
                } else rcs.jetMat.opacity = 0.0;
            }

            if (simT < 0.0) {
                const sec = Math.ceil(Math.abs(simT));
                $('tv-timer').innerText = simCfg.is_preview ? "PAD INSPECTION" : `T- 00:0${sec}.0`;
                emitParticle(rx + 1.25, ry + 6.0 + s1Len * 0.82, -1.5, 0.18, -0.08, 0, 0.6, 2.8, 38, 0.32, 0xffffff, 0.97, -0.005, false);

                if (simT >= -5.0 && !p0.exploded && !simCfg.is_preview) {
                    if (gasHiss && actx) gasHiss.gain.setTargetAtTime(0.65, actx.currentTime, 0.2);
                    const countDeluge = Math.max(4, Math.floor(7 * (simCfg.water_flow / 300.0)));
                    for(let i=0; i<countDeluge; i++) {
                        const ang = Math.random() * Math.PI * 2, rad = 1.5 + Math.random() * 6.0;
                        emitParticle(rx + Math.cos(ang)*rad, 2.5, Math.sin(ang)*rad - 2.0, Math.cos(ang)*(0.8 + Math.random()*1.2), 0.15 + Math.random()*0.25, Math.sin(ang)*(0.8 + Math.random()*1.2), 2.2, 14.0, 52, 0.48, 0xe0f2fe, 0.95, 0.018, false);
                    }
                }

                if (simT >= -simCfg.ignition_lead && !p0.exploded && !simCfg.is_preview) {
                    if (actx) {
                        if (subRumble) subRumble.gain.setTargetAtTime(1.25, actx.currentTime, 0.25);
                        if (shockCrackle) shockCrackle.gain.setTargetAtTime(0.95, actx.currentTime, 0.2);
                    }
                    camShake = 0.32;
                    for(let tObj of s1NozzleTips) {
                        tObj.node.getWorldPosition(tempV);
                        emitSpark(tempV.x, tempV.y, tempV.z, (Math.random()-0.5)*1.5, -1.2-Math.random()*1.8, (Math.random()-0.5)*1.5, 0xfde047);
                    }
                    for(let i=0; i<12; i++) {
                        const ang = Math.random() * Math.PI * 2, spd = 2.8 + Math.random() * 3.2, isLit = i < 5;
                        emitParticle(rx + Math.cos(ang)*2.2, 2.4, Math.sin(ang)*2.2 - 2.5, Math.cos(ang)*spd, 0.05 + Math.random()*0.2, Math.sin(ang)*spd, 2.8, 22.0, 58, isLit ? 0.72 : 0.58, isLit ? 0xffedd5 : 0xf8fafc, 0.935, 0.024, isLit);
                    }
                    for(let i=0; i<6; i++) {
                        const side = (Math.random() > 0.5 ? 1 : -1) * (10.0 + Math.random() * 22.0);
                        emitParticle(rx + side, 3.2, -5.0 + (Math.random()-0.5)*16.0, side * 0.04, 0.45 + Math.random()*0.55, (Math.random()-0.5)*0.4, 6.5, 34.0, 75, 0.52, 0xf1f5f9, 0.97, 0.032, false);
                    }
                }
            } else if (!p0.exploded) {
                const m = Math.floor(simT / 60), s = simT % 60;
                $('tv-timer').innerText = `T+ ${String(m).padStart(2,'0')}:${s.toFixed(1).padStart(4,'0')}`;
                if (actx) {
                    const atm = Math.exp(-alt / 14.0);
                    if (subRumble) subRumble.gain.setTargetAtTime(1.25 * atm, actx.currentTime, 0.15);
                    if (shockCrackle) shockCrackle.gain.setTargetAtTime(0.95 * atm, actx.currentTime, 0.1);
                    if (gasHiss) gasHiss.gain.setTargetAtTime(0.18 * atm, actx.currentTime, 1.0);
                }

                if (simT < 6.5 && alt < 0.45) {
                    camShake = Math.max(0.15, 0.42 * (1.0 - simT / 7.0));
                    const intensity = Math.max(0.2, 1.0 - (alt / 0.42));
                    for(let i=0; i<Math.floor(14 * intensity); i++) {
                        const ang = Math.random() * Math.PI * 2, spd = (3.0 + Math.random() * 3.5) * intensity, isLit = i < 5;
                        emitParticle(rx + Math.cos(ang)*3.0, 2.5, Math.sin(ang)*3.0 - 3.0, Math.cos(ang)*spd, 0.08 + Math.random()*0.25, Math.sin(ang)*spd, 3.2, 26.0, 62, isLit ? 0.70 : 0.55, isLit ? 0xfef08a : 0xf8fafc, 0.93, 0.026, isLit);
                    }
                    for(let i=0; i<Math.ceil(6 * intensity); i++) {
                        const ang = Math.random() * Math.PI * 2, dist = 12.0 + Math.random() * 28.0;
                        emitParticle(rx + Math.cos(ang)*dist, 3.8, Math.sin(ang)*dist * 0.6 - 6.0, Math.cos(ang)*0.6, 0.5 + Math.random()*0.65, Math.sin(ang)*0.4, 7.0, 38.0, 80, 0.50, 0xf8fafc, 0.965, 0.035, false);
                    }
                }
            }

            for(let p of pool) {
                if (!p.active) continue;
                if (++p.age >= p.maxAge) { p.active = p.sp.visible = false; continue; }
                p.vx *= p.drag; p.vz *= p.drag; p.vy = p.vy * p.drag + p.buoyancy;
                p.sp.position.x += p.vx; p.sp.position.y = Math.max(2.2, p.sp.position.y + p.vy); p.sp.position.z += p.vz;
                p.sp.material.rotation += p.rotSpeed;
                const pr = p.age / p.maxAge, sc = p.s0 + (p.s1 - p.s0) * Math.pow(pr, 0.58);
                p.sp.scale.set(sc, sc, 1);
                if (p.lit && pr > 0.15) p.sp.material.color.lerp(steamWhiteColor, 0.08);
                p.sp.material.opacity = p.o * Math.min(1.0, p.age / 5.0) * (1.0 - Math.pow(pr, 1.8));
            }

            const updateSubParticles = (arr, gMod) => {
                for(let item of arr) {
                    if (!item.active) continue;
                    if (++item.age >= item.maxAge) { item.active = item.sp.visible = false; continue; }
                    item.sp.position.add(tempV.set(item.vx, item.vy, item.vz));
                    if (gMod) item.vy -= 9.8 * 0.016 * 0.5;
                    item.sp.material.opacity = 1.0 - (item.age / item.maxAge);
                }
            };
            updateSubParticles(sparks, false); updateSubParticles(iceShards, true);

            if (p0.stage === 2) { activeFocusWorld.set(0, s2Len * 0.45, 0); s2Group.localToWorld(activeFocusWorld); }
            else { activeFocusWorld.set(0, s1Len * 0.52, 0); rocket.localToWorld(activeFocusWorld); }

            if (simCfg.is_preview) {
                const ang = elapsedSec * 0.22;
                cameraMain.position.set(Math.sin(ang) * 280.0, 42.0, Math.cos(ang) * 280.0);
                smoothCamTarget.set(0, 6.0 + (s1Len + s2Len) * 0.45, 0);
                cameraMain.lookAt(smoothCamTarget);
            } else {
                cameraMain.position.set(activeFocusWorld.x - 180.0 + Math.sin(now * 0.0018) * 0.42, activeFocusWorld.y + 35.0 + Math.cos(now * 0.0013) * 0.32, activeFocusWorld.z + 320.0);
                if (camShake > 0.002) {
                    cameraMain.position.x += (Math.random() - 0.5) * camShake * 2.5;
                    cameraMain.position.y += (Math.random() - 0.5) * camShake * 2.5;
                    camShake *= 0.94;
                }
                cameraMain.lookAt(activeFocusWorld);
            }
            skyDome.position.copy(cameraMain.position);
            atmoLimbMesh.position.set(cameraMain.position.x, -56000, cameraMain.position.z);

            if (pipVisible) {
                const targetPos = new THREE.Vector3();
                if (stage1Detached && p0.b_active) {
                    targetPos.set(bX * 0.1, bY_scaled + s1Len * 0.55, 0);
                    cameraPip.position.set(240.0, 22.0, 260.0);
                    if (bY <= 14000 && bY >= 10000 && !pipBlurTriggered12k) { triggerPipAutoFocus(); pipBlurTriggered12k = true; }
                    if (bY <= 3600 && !pipBlurTriggeredCatch) { triggerPipAutoFocus(); pipBlurTriggeredCatch = true; }

                    if (p0.b_caught || bY_scaled <= 90.0) {
                        cameraPip.fov = THREE.MathUtils.lerp(cameraPip.fov, 16.0, 0.1);
                        $('pip-tag').innerText = "CAM 02: GROUND OPTICAL (TOWER CATCH)";
                        $('pip-hud-alt').innerText = p0.b_caught ? "SUSPENDED (SECURED)" : "FINAL TOUCHDOWN";
                    } else {
                        cameraPip.fov = THREE.MathUtils.lerp(cameraPip.fov, Math.max(8.0, Math.min(22.0, bY_scaled / 35.0)), 0.1);
                        $('pip-tag').innerText = "CAM 02: GROUND OPTICAL TRACKER";
                        $('pip-hud-alt').innerText = `BOOSTER ALT: ${(bY * 0.001).toFixed(1)} km`;
                    }
                } else {
                    targetPos.copy(rocket.position); targetPos.y += s1Len * 0.5;
                    cameraPip.position.set(240.0, 22.0, 260.0);
                    cameraPip.fov = THREE.MathUtils.lerp(cameraPip.fov, Math.max(8.0, Math.min(24.0, rocket.position.y / 24.0)), 0.1);
                    $('pip-tag').innerText = "CAM 02: GROUND OPTICAL (PAD 39A)";
                    $('pip-hud-alt').innerText = `ALT: ${(rocket.position.y * 0.01).toFixed(1)} km`;
                }
                cameraPip.lookAt(targetPos); cameraPip.updateProjectionMatrix();
                pipTrackingSpot.position.set(targetPos.x + 80, targetPos.y + 100, targetPos.z + 80);
                pipTrackingSpot.target.position.copy(targetPos); pipTrackingSpot.target.updateMatrixWorld();
                rendererPip.render(scene, cameraPip);
            }

            rendererMain.render(scene, cameraMain);

            const dRangeKm = (rx * 10.0) / 1000.0;
            drawPrecisionOrbitMap(alt, dRangeKm, p0.exploded, p0.event === "ORBIT");
            drawEngineClusterGraphic(p0.stage, p0.thrust, p0.exploded, p0.b_thrust, p0.b_caught);

            $('hud-regime').innerText = alt >= 100.0 ? "THERMO (VAC)" : (alt >= 50.0 ? "MESO" : (alt >= 12.0 ? "STRATO" : "TROPO"));
            $('hud-downrange').innerText = `DOWNRANGE: ${dRangeKm.toFixed(1)} km`;
            $('hud-pitch').innerText = `${pitchDegVal.toFixed(1)}°`;
            $('hud-apogee').innerText = `${apogeeVal.toFixed(1)} km`;
            $('hud-s1-prop').innerText = `${Math.round(s1PropVal)}%`;
            $('hud-s2-prop').innerText = `${Math.round(s2PropVal)}%`;
            $('hud-pc').innerText = `${Math.round(pcVal)} bar`;

            $('tv-mach').innerText = `M ${mach.toFixed(2)}`;
            $('tv-spd').innerText = `(${Math.round(vel * 3.6).toLocaleString()} km/h)`;
            $('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            $('tv-q').innerText   = q.toFixed(1);
            $('tv-g').innerText   = accG.toFixed(1);

            const isOrbit = p0.event === "ORBIT";
            const canComplete = simCfg.spacex_return ? (isOrbit && p0.b_caught) : isOrbit;

            if (canComplete && !isMissionEnded) {
                completeBanner.style.display = 'block';
                if (simCfg.spacex_return) {
                    $('complete-desc').innerText = "LEO INSERTION & SUPER HEAVY TOWER CATCH ACHIEVED";
                    $('complete-sub').innerText = "Booster suspended on Mechazilla chopsticks. Orbiter in circular orbit.";
                } else {
                    $('complete-desc').innerText = "FIRST COSMIC VELOCITY (28,400 km/h) NOMINAL INSERTION";
                    $('complete-sub').innerText = "Vehicle has achieved stable orbital trajectory.";
                }
                $('tv-stage-badge').innerText = "MISSION SUCCESS - ALL OBJECTIVES ACHIEVED";
                $('tv-stage-badge').style.color = $('live-indicator').style.background = "#10b981";
                $('webcast-title').innerText = "MISSION COMPLETED";

                if (actx) [subRumble, shockCrackle, gasHiss, boosterRumble, boosterCrackle].forEach(n => n && n.gain.setTargetAtTime(0.0001, actx.currentTime, 0.3));
                setTimeout(() => { isMissionEnded = true; }, 2800);
            }

            if (p0.exploded) {
                rudBanner.style.display = 'block';
                rudDesc.innerText = failMessage || "機体過負荷による空中分解";
            }
        }

        rendererMain.setSize(window.innerWidth || 1200, window.innerHeight || 980);
        cameraMain.aspect = (window.innerWidth || 1200) / (window.innerHeight || 980);
        cameraMain.updateProjectionMatrix();
        resizePipRenderer();
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
</script></body></html>"""

final_html = html_template.replace("__SIM_DATA__", traj_json).replace("__SIM_CFG__", cfg_json).replace("__FAIL_MSG__", fail_msg_clean)
components.html(final_html, height=980)

if launch_clicked:
    st.markdown("---")
    st.markdown("### 📋 フライトテレメトリ詳細レポート")
    if error_msg:
        st.error(f"⚠️ **ミッション異常終了 (RUD)**: {error_msg}")
    else:
        st.success("🎉 **ミッション完全成功**: 軌道投入および機体制御シーケンスが設計通り正常に完了しました。")
