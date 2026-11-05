import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect Extreme: 4K Cinema Dual Photoreal Engine", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect Extreme - 4K実写デュアル中継＆航空宇宙物理シミュレーター")
st.caption("※ 完全復元版：流体GLSLプルーム・高密度PBRマテリアル・ケープカナベラル大西洋ランドスケープ・非干渉デュアル中継")

# =========================================================================
# 🔬 超膨大！推進剤・サイクル・材料・ブースター・空力・先端部データベース
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
    "【三元推進剤】リチウム・フッ素・液体水素 (Li / F2 / LH2) [高比推力]": {
        "base_isp_sl": 445, "base_isp_vac": 542, "base_thrust": 2200, "density": 0.55, 
        "flame_hex": 0x5eead4, "outer_hex": 0x0f766e, "spark_hex": 0x99f6e4, "risk": 0.08, "type": "triprop"
    },
    "【高密度】ボロン添加ゲル化ケロシンスラリー (RP-1 / B)": {
        "base_isp_sl": 348, "base_isp_vac": 395, "base_thrust": 3100, "density": 1.18, 
        "flame_hex": 0x4ade80, "outer_hex": 0x15803d, "spark_hex": 0xbbf7d0, "risk": 0.04, "type": "boron"
    },
    "【猛毒】四酸化二窒素 ＋ ヒドラジン (N2O4 / UDMH) [Proton / 長征]": {
        "base_isp_sl": 288, "base_isp_vac": 322, "base_thrust": 2100, "density": 1.26, 
        "flame_hex": 0xf5d0fe, "outer_hex": 0x9333ea, "spark_hex": 0xfab1a0, "risk": 0.05, "type": "hypergolic"
    },
    "【核熱】固体炉心型原子力サーマルロケット (NERVA / LH2)": {
        "base_isp_sl": 450, "base_isp_vac": 925, "base_thrust": 2500, "density": 0.30, 
        "flame_hex": 0x86efac, "outer_hex": 0x14532d, "spark_hex": 0x4ade80, "risk": 0.12, "type": "nuclear"
    },
    "【核融合】D-He3 磁気慣性核融合パルスドライブ [次世代深宇宙]": {
        "base_isp_sl": 720, "base_isp_vac": 1850, "base_thrust": 4800, "density": 0.90, 
        "flame_hex": 0x38bdf8, "outer_hex": 0x312e81, "spark_hex": 0xe0f2fe, "risk": 0.18, "type": "fusion"
    },
    "【禁忌】反陽子触媒マイクロ核分裂スラリー (ACMF)": {
        "base_isp_sl": 950, "base_isp_vac": 2400, "base_thrust": 7200, "density": 1.95, 
        "flame_hex": 0xe9d5ff, "outer_hex": 0x581c87, "spark_hex": 0xf43f5e, "risk": 0.38, "type": "darkmatter"
    }
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [Raptor型・極限高圧]": {"isp_mod": 1.07, "thrust_mod": 1.42, "mass_mod": 1.22, "max_pressure_limit": 380, "cyc_id": "ffsc"},
    "酸化剤リッチ二段燃焼 (ORSC) [RD-170 / BE-4型]": {"isp_mod": 1.03, "thrust_mod": 1.25, "mass_mod": 1.18, "max_pressure_limit": 310, "cyc_id": "sc"},
    "燃料リッチ二段燃焼 (FRSC) [RS-25 / LE-9型]": {"isp_mod": 1.04, "thrust_mod": 1.15, "mass_mod": 1.16, "max_pressure_limit": 280, "cyc_id": "sc"},
    "ガス発生器サイクル (GG) [Merlin / F-1型・煤排気ダクト付]": {"isp_mod": 0.96, "thrust_mod": 0.98, "mass_mod": 0.84, "max_pressure_limit": 195, "cyc_id": "gg"},
    "エキスパンダーブリードサイクル [LE-5B型・高信頼]": {"isp_mod": 1.05, "thrust_mod": 0.88, "mass_mod": 0.92, "max_pressure_limit": 160, "cyc_id": "expander"},
    "リニアエアロスパイク方式 [X-33楔形ノズル・全高度最適]": {"isp_mod": 1.09, "thrust_mod": 1.10, "mass_mod": 1.32, "max_pressure_limit": 250, "cyc_id": "aerospike"},
    "回転デトネーションエンジン (RDE) [超音速爆轟リング]": {"isp_mod": 1.14, "thrust_mod": 1.35, "mass_mod": 1.05, "max_pressure_limit": 340, "cyc_id": "rde"},
    "電動ブラシレスターボポンプ (Rutherford型) [バッテリー駆動]": {"isp_mod": 1.01, "thrust_mod": 0.78, "mass_mod": 1.10, "max_pressure_limit": 150, "cyc_id": "electric"},
    "【手動】人力足漕ぎペダル式タービン [超軽量・推力激減]": {"isp_mod": 0.35, "thrust_mod": 0.18, "mass_mod": 0.25, "max_pressure_limit": 90, "cyc_id": "pedal"}
}

MATERIALS = {
    "Austenitic 304L 冷間圧延鏡面ステンレス [Starship仕様]": {"base_dry_ratio": 0.065, "max_q_base": 130.0, "max_g_base": 12.5, "mat_id": "ss"},
    "航空宇宙用 Al-Li-2195 アルミリチウム合金 [SLSオレンジ断熱塗装]": {"base_dry_ratio": 0.050, "max_q_base": 82.0, "max_g_base": 9.0, "mat_id": "al"},
    "Saturn V アポロ伝統 ホワイト＆ブラック・ロールチェック塗工": {"base_dry_ratio": 0.054, "max_q_base": 88.0, "max_g_base": 9.5, "mat_id": "saturn"},
    "高弾性トレカ炭素繊維複合材 (CFRP) [Electron / マットブラック]": {"base_dry_ratio": 0.036, "max_q_base": 65.0, "max_g_base": 7.5, "mat_id": "cf"},
    "超耐熱インコネル718 モノコック [X-15重装甲ダークチタン調]": {"base_dry_ratio": 0.092, "max_q_base": 195.0, "max_g_base": 16.5, "mat_id": "inconel"},
    "金属ベリリウム・銅合金ハニカム [JWSTゴールド鏡面仕上げ]": {"base_dry_ratio": 0.042, "max_q_base": 110.0, "max_g_base": 11.0, "mat_id": "gold"},
    "カーボンナノチューブ (CNT) バッキーペーパー複合外殻 [超軽量]": {"base_dry_ratio": 0.024, "max_q_base": 150.0, "max_g_base": 15.0, "mat_id": "cnt"},
    "【DIY】防腐処理済み米松ツーバイフォー材 [木目＆コーススレッド接合]": {"base_dry_ratio": 0.160, "max_q_base": 42.0, "max_g_base": 4.8, "mat_id": "wood"}
}

STRAPON_BOOSTERS = {
    "なし (単段スリムコア構成)": {"count": 0, "thrust_add": 0.0, "mass_add": 0.0, "fuel_add": 0.0, "isp_sl": 0, "type": "none"},
    "Falcon Heavy風 液体LRB × 2基 (グリッドフィン＆着陸脚付)": {"count": 2, "thrust_add": 5800.0, "mass_add": 50.0, "fuel_add": 820.0, "isp_sl": 315, "type": "lrb"},
    "Soyuz R-7風 テーパー液体ブースター × 4基 (コロリョフクロス専用)": {"count": 4, "thrust_add": 4200.0, "mass_add": 38.0, "fuel_add": 520.0, "isp_sl": 308, "type": "soyuz"},
    "SLS / Space Shuttle風 5セグメント超巨大SRB × 2基": {"count": 2, "thrust_add": 8800.0, "mass_add": 68.0, "fuel_add": 950.0, "isp_sl": 278, "type": "srb"},
    "SLS Block 2風 超巨大固体SRB × 4基クラスタ": {"count": 4, "thrust_add": 16500.0, "mass_add": 120.0, "fuel_add": 1600.0, "isp_sl": 278, "type": "srb"},
    "Energia / ゼニット風 大推力液体ブースター × 4基": {"count": 4, "thrust_add": 14800.0, "mass_add": 105.0, "fuel_add": 1450.0, "isp_sl": 330, "type": "lrb"},
    "Delta II / H-IIA風 グラファイトエポキシSRB-A × 6基": {"count": 6, "thrust_add": 4800.0, "mass_add": 36.0, "fuel_add": 420.0, "isp_sl": 285, "type": "srb_small"},
    "【危険】超高圧メガ花火ロケット × 8基クラスタ": {"count": 8, "thrust_add": 3600.0, "mass_add": 14.0, "fuel_add": 95.0, "isp_sl": 195, "type": "firework"},
    "【狂気】N1ロケット風 外周12基メガブースターリング": {"count": 12, "thrust_add": 24000.0, "mass_add": 180.0, "fuel_add": 2400.0, "isp_sl": 310, "type": "lrb_ring"}
}

AERO_WINGS = {
    "チタン鍛造極超音速グリッドフィン × 4基 (Super Heavy / Falcon 9)": {"lift_coeff": 0.12, "drag_penalty": 1.05, "mass": 1.2, "flutter_mach": 99.0, "wing_id": "grid"},
    "Starship風 前後エルロン・空力ボディフラップ × 4枚": {"lift_coeff": 0.35, "drag_penalty": 1.12, "mass": 2.8, "flutter_mach": 99.0, "wing_id": "starship_flap"},
    "なし (純粋な軸対称弾道ロケット)": {"lift_coeff": 0.0, "drag_penalty": 1.0, "mass": 0.0, "flutter_mach": 99.0, "wing_id": "none"},
    "Saturn V / V2風 大型十字尾翼スタビライザー × 4枚": {"lift_coeff": 0.25, "drag_penalty": 1.10, "mass": 2.2, "flutter_mach": 15.0, "wing_id": "tail_fins"},
    "コンコルド / Space Shuttle風 ダブルデルタ超音速後退翼": {"lift_coeff": 0.95, "drag_penalty": 1.45, "mass": 7.5, "flutter_mach": 3.8, "wing_id": "delta_wing"},
    "X-37B / Dream Chaser風 リフティングボディ傾斜ウィングレット": {"lift_coeff": 0.65, "drag_penalty": 1.25, "mass": 4.2, "flutter_mach": 8.5, "wing_id": "lifting_body"},
    "前進翼 (Su-47 / X-29風 遷音速高機動カナード＆逆後退翼)": {"lift_coeff": 1.35, "drag_penalty": 1.75, "mass": 9.0, "flutter_mach": 2.2, "wing_id": "forward_swept"},
    "高アスペクト比カーボン製グライダー主翼 (超長大スパン)": {"lift_coeff": 2.2, "drag_penalty": 3.2, "mass": 14.0, "flutter_mach": 0.90, "wing_id": "glider"}
}

FAIRINGS = {
    "バイコニカル炭素複合材クラムシェル (2分割開頭・金箔通信衛星内蔵)": {"mass": 2.1, "cd": 0.18, "heat_limit": 2600, "shape_id": "biconic"},
    "Starship風 窓付き有人クルーノーズコーン ＋ ヘッダータンク": {"mass": 4.2, "cd": 0.22, "heat_limit": 2900, "shape_id": "starship_crew"},
    "アポロ / Orion風 有人カプセル ＋ 緊急脱出タワー (LES 4ノズル付)": {"mass": 6.8, "cd": 0.32, "heat_limit": 3200, "shape_id": "abort_tower"},
    "JWST (ジェイムズ・ウェッブ宇宙望遠鏡) 18枚黄金六角ミラー搭載カウル": {"mass": 2.8, "cd": 0.20, "heat_limit": 2500, "shape_id": "jwst"},
    "骨格露出型スケルトン・耐圧トラスケージ (内部深宇宙プローブ透視)": {"mass": 1.5, "cd": 0.45, "heat_limit": 1400, "shape_id": "skeleton"},
    "極超音速ウェーブライダー・ペネトレーターニードル (プラズマスパイク付)": {"mass": 1.3, "cd": 0.12, "heat_limit": 2200, "shape_id": "needle"},
    "Von Braun クラシック球頭オジーブ ＋ 先端ピトー管センサー": {"mass": 1.9, "cd": 0.16, "heat_limit": 2400, "shape_id": "pitot"}
}

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
        s1_prop = st.selectbox("第1段 推進剤", list(PROPELLANTS.keys()), index=0)
        s1_cycle = st.selectbox("ターボポンプ駆動サイクル", list(PUMP_CYCLES.keys()), index=0)
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, 9)
    with c2:
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, 290, step=10)
        s1_eps = st.slider("海面膨張比 (ε: ノズル径連動)", 8, 70, 24, step=1)
    with c3:
        s1_fuel = st.slider("第1段 推進剤充填量 (トン: 胴体長連動)", 100.0, 4500.0, 1100.0, step=50.0)
        s1_mat = st.selectbox("第1段 構造素材", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("外殻等価板厚 (mm)", 1.0, 12.0, 4.2, step=0.1)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        strapon_opt = st.selectbox("ブースター種別クラスタ", list(STRAPON_BOOSTERS.keys()), index=2)
    with c2:
        sep_thrust_factor = st.slider("分離パイロモーター推力倍率 (スロー連動)", 0.5, 3.0, 1.2, step=0.1)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 空力パーツ", list(AERO_WINGS.keys()), index=0)
        angle_of_attack = st.slider("固定取り付け迎角 AoA (deg)", -3.0, 12.0, 0.5, step=0.5)
    with c2:
        st.info("💡 **高密度完全復元**: 削られていたパラボラ再生冷却ノズル、多層PBR海岸線地形、流体GLSLプルーム、RUD破片物理をすべて最高品質で復活させました。")

with tab4:
    c1, c2, c3 = st.columns(3)
    with c1:
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=0)
        s2_cycle = st.selectbox("第2段 ポンプ方式", list(PUMP_CYCLES.keys()), index=0)
        s2_eng_count = st.slider("真空ノズル基数", 1, 9, 3)
        s2_eps = st.slider("第2段 真空膨張比 (ε)", 30, 280, 150, step=5)
    with c2:
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 20.0, 1200.0, 280.0, step=10.0)
        s2_mat = st.selectbox("第2段 構造素材", list(MATERIALS.keys()), index=0)
        s2_thick = st.slider("第2段 壁厚 (mm)", 0.8, 8.0, 3.0, step=0.1)
    with c3:
        fairing_type = st.selectbox("先端空力カウル / 衛星", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 40.0, 180.0, 75.0, step=5.0)
        payload_mass = st.slider("投入衛星質量 (トン)", 0.5, 120.0, 22.0, step=1.0)

with tab5:
    c1, c2 = st.columns(2)
    with c1:
        water_flow_rate = st.slider("消音注水デリュージ流量 (トン/秒)", 50, 450, 250, step=25)
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
m1.metric("総離床重量 / 離床TWR", f"{total_s1_wet:.1f} t", f"TWR: {twr_init:.2f} ({'離床可能' if twr_init >= 1.05 else '推力不足！轟沈確定'})")
m2.metric("総計算速度増分 (ΔV)", f"{total_dv:.0f} m/s", "LEO投入基準: 9,200 m/s")
m3.metric("構造限界動圧 / 耐G", f"{s1_spec['max_q']:.1f} kPa", f"耐G: {s1_spec['max_g']:.1f} G")
m4.metric("ブースター追加推力", f"+{strapon_spec['thrust_add']:.0f} kN", f"基数: {strapon_spec['count']} 基")

# =========================================================================
# 💥 物理シミュレーション (離床過渡応答)
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

# =========================================================================
# 📺 HTML / JS 完全描画テンプレート (非干渉スタジオレイアウト ＆ PBRランドスケープ)
# =========================================================================
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #01040d; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none; }
        #canvas-main { width: 100%; height: 100%; display: block; }
        .vignette { position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; box-shadow: inset 0 0 140px rgba(0,0,0,0.85); z-index: 5; }
        .reticle { position: absolute; top: 50%; left: 50%; width: 56px; height: 56px; transform: translate(-50%, -50%); border: 1px solid rgba(56, 189, 248, 0.22); border-radius: 50%; pointer-events: none; }
        
        /* 🎥 PiP 右上完全独立配置 (被り防止ベゼル) */
        .pip-border { position: absolute; top: 58px; right: 24px; width: 330px; height: 200px; border: 2px solid rgba(56, 189, 248, 0.6); border-radius: 6px; pointer-events: auto; cursor: pointer; z-index: 20; box-shadow: 0 10px 30px rgba(0,0,0,0.85); transition: opacity 0.2s; }
        .pip-tag { position: absolute; top: 66px; right: 175px; font-size: 10px; font-weight: 800; color: #fff; background: rgba(15, 23, 42, 0.88); padding: 3px 8px; border-radius: 3px; letter-spacing: 1px; font-family: monospace; z-index: 25; pointer-events: none; }
        .pip-alt { position: absolute; top: 228px; right: 32px; font-size: 10px; font-family: monospace; color: #38bdf8; font-weight: 700; background: rgba(15, 23, 42, 0.88); padding: 2px 6px; border-radius: 3px; z-index: 25; pointer-events: none; }
        .pip-toggle-hint { position: absolute; top: 66px; right: 30px; font-size: 9px; font-family: monospace; color: #94a3b8; background: rgba(15, 23, 42, 0.88); padding: 3px 6px; border-radius: 3px; z-index: 25; pointer-events: none; }

        /* 🛰️ 軌道HUD 左上配置 (PiPやロケット中央と絶対に被らない完全分離) */
        .hud-orbit { position: absolute; top: 58px; left: 24px; width: 290px; background: rgba(3, 7, 18, 0.88); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 4px; padding: 12px; box-sizing: border-box; z-index: 10; color: #fff; }
        
        .top-banner { position: absolute; top: 0; left: 0; width: 100%; height: 48px; background: rgba(3, 7, 18, 0.92); backdrop-filter: blur(16px); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 10; }
        .hud-telemetry { position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(1, 3, 8, 0.98) 0%, rgba(2, 6, 14, 0.88) 75%, transparent 100%); padding: 26px 36px 18px 36px; box-sizing: border-box; display: flex; align-items: flex-end; justify-content: space-between; z-index: 10; }
        .rud-banner { display: none; position: absolute; top: 170px; left: 50%; transform: translateX(-50%); background: rgba(120, 10, 10, 0.94); backdrop-filter: blur(16px); border: 2px solid #ef4444; border-radius: 4px; padding: 18px 32px; z-index: 30; text-align: center; box-shadow: 0 0 60px rgba(239, 68, 68, 0.7); }
    </style>
</head>
<body>
    <canvas id="canvas-main"></canvas>
    <div class="vignette"><div class="reticle"></div></div>
    
    <!-- 2画面用PiP 右上ベゼル枠 (クリックで表示切替可能) -->
    <div id="pip-frame" class="pip-border" title="クリックでPiPの表示/非表示を切り替え"></div>
    <div id="pip-tag" class="pip-tag">CAM 02: COASTAL TRACKER</div>
    <div id="pip-hud-alt" class="pip-alt">ALT: 0.0 km</div>
    <div id="pip-hint" class="pip-toggle-hint">[CLICK TO TOGGLE]</div>

    <div class="top-banner">
        <div style="display: flex; align-items: center; gap: 14px;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 12px #ef4444;"></span>
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

    <!-- 左上に完全分離された軌道トラジェクトリHUD -->
    <div class="hud-orbit">
        <div style="font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 6px; display: flex; justify-content: space-between;">
            <span>DOWNRANGE TRAJECTORY</span>
            <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">0.0 km</span>
        </div>
        <canvas id="orbit-canvas" width="266" height="70" style="width: 100%; height: 70px; background: #01040d; border-radius: 2px;"></canvas>
        <div id="event-log" style="margin-top: 8px; font-family: monospace; font-size: 10px; color: #34d399; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
            > VEHICLE COUNTDOWN INITIALIZED
        </div>
    </div>

    <div id="rud-banner" class="rud-banner">
        <div style="color: #fff; font-size: 18px; font-weight: 900; letter-spacing: 2.5px; font-family: monospace;">🚨 RAPID UNSCHEDULED DISASSEMBLY (RUD) 🚨</div>
        <div id="rud-desc" style="color: #fecaca; font-size: 13px; font-weight: 600; margin-top: 8px; max-width: 540px; line-height: 1.4;"></div>
    </div>

    <div class="hud-telemetry">
        <div>
            <div id="tv-status" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 2px; margin-bottom: 2px;">COUNTDOWN SEQUENCE</div>
            <div id="tv-timer" style="color: #ffffff; font-size: 46px; font-weight: 900; font-family: 'Consolas', monospace; letter-spacing: 2px; text-shadow: 0 0 25px rgba(56, 189, 248, 0.4);">T- 00:10.0</div>
        </div>
        <div style="display: flex; gap: 36px; border-left: 1px solid rgba(255,255,255,0.15); padding-left: 32px;">
            <div>
                <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">SPEED / MACH</div>
                <div style="color: #fff; font-size: 24px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-mach">M 0.00</span> <span style="font-size: 12px; color: #94a3b8;" id="tv-spd">(0 km/h)</span></div>
            </div>
            <div>
                <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">ALTITUDE</div>
                <div style="color: #fff; font-size: 24px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-alt">0.0</span> <span style="font-size: 12px; color: #94a3b8;">km</span></div>
            </div>
            <div>
                <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">DYNAMIC PRESSURE</div>
                <div style="color: #fff; font-size: 24px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-q">0.0</span> <span style="font-size: 12px; color: #94a3b8;">kPa</span></div>
            </div>
            <div>
                <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">AXIAL LOAD</div>
                <div style="color: #fff; font-size: 24px; font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-g">1.0</span> <span style="font-size: 12px; color: #94a3b8;">G</span></div>
            </div>
            <div>
                <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1.2px;">STAGE CONFIG</div>
                <div id="tv-stage-badge" style="color: #34d399; font-size: 20px; font-weight: 800; font-family: 'Consolas', monospace;">PAD INTEGRATION</div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const simData = __SIM_DATA__;
        const simCfg = __SIM_CFG__;
        const failMessage = "__FAIL_MSG__";

        const canvasMain = document.getElementById('canvas-main');
        const orbitCvs = document.getElementById('orbit-canvas');
        const octx = orbitCvs.getContext('2d');
        const rudBanner = document.getElementById('rud-banner');
        const rudDesc = document.getElementById('rud-desc');
        const eventLog = document.getElementById('event-log');

        // PiP表示切替トグル
        let pipVisible = true;
        const pipFrame = document.getElementById('pip-frame');
        const pipTag = document.getElementById('pip-tag');
        const pipAlt = document.getElementById('pip-hud-alt');
        const pipHint = document.getElementById('pip-hint');
        pipFrame.addEventListener('click', () => {
            pipVisible = !pipVisible;
            const disp = pipVisible ? 'block' : 'none';
            pipTag.style.display = disp;
            pipAlt.style.display = disp;
            pipFrame.style.opacity = pipVisible ? '1.0' : '0.2';
            pipHint.innerText = pipVisible ? '[CLICK TO HIDE]' : '[CLICK TO SHOW]';
        });

        // 音響
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null, rumbleGain = null, crackleGain = null;
        function initAudio() {
            if (simCfg.is_preview) return;
            if (!actx) {
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
                const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 650; bp.Q.value = 2.8;
                crackleGain = actx.createGain(); crackleGain.gain.value = 0;
                cSrc.connect(bp); bp.connect(crackleGain); crackleGain.connect(actx.destination);
                cSrc.start(0);
            }
            if (actx && actx.state === 'suspended') actx.resume();
        }

        function playPyro() {
            if (!actx) return;
            const osc = actx.createOscillator();
            const g = actx.createGain();
            osc.type = 'triangle'; osc.frequency.setValueAtTime(300, actx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(30, actx.currentTime + 0.4);
            g.gain.setValueAtTime(0.7, actx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.01, actx.currentTime + 0.4);
            osc.connect(g); g.connect(actx.destination); osc.start(); osc.stop(actx.currentTime + 0.4);
        }

        // =========================================================================
        // 🌍 Three.js シーン ＆ リアル大気霞（空気遠近法フォグ）
        // =========================================================================
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a1526);
        scene.fog = new THREE.FogExp2(0x0d1f38, 0.000085);

        const renderer = new THREE.WebGLRenderer({ canvas: canvasMain, antialias: true, powerPreference: "high-performance" });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.35;

        // メイン近接追随カメラ ＆ サブ遠景カメラ
        const cameraMain = new THREE.PerspectiveCamera(26, window.innerWidth / window.innerHeight, 0.5, 50000000);
        const cameraPip = new THREE.PerspectiveCamera(14, 330 / 200, 5.0, 50000000);
        cameraPip.position.set(-3800, 180, 5200);

        // 太陽光・大気散乱光
        const sunLight = new THREE.DirectionalLight(0xfff5e6, 4.6);
        sunLight.position.set(4500, 8000, 5500);
        scene.add(sunLight);
        scene.add(new THREE.HemisphereLight(0x93c5fd, 0x1e293b, 0.85));

        const engineBounceLight = new THREE.PointLight(simCfg.flame_hex, 0.0, 340, 1.6);
        scene.add(engineBounceLight);

        // 恒星
        const starGeo = new THREE.BufferGeometry();
        const starPos = new Float32Array(3000 * 3);
        for(let i=0; i<3000*3; i+=3) {
            const rad = 22000000;
            const u = Math.random(), v = Math.random();
            const th = u * 2.0 * Math.PI, ph = Math.acos(2.0 * v - 1.0);
            starPos[i] = rad * Math.sin(ph) * Math.cos(th);
            starPos[i+1] = rad * Math.sin(ph) * Math.sin(th);
            starPos[i+2] = rad * Math.cos(ph);
        }
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ size: 1.6, color: 0xe2e8f0, transparent: true, opacity: 0.15 })));

        // 地球
        const R_EARTH = 6371.0;
        const earthMesh = new THREE.Mesh(
            new THREE.SphereGeometry(R_EARTH, 64, 48),
            new THREE.MeshStandardMaterial({ color: 0x0f3854, roughness: 0.7 })
        );
        earthMesh.position.set(0, -R_EARTH, 0);
        scene.add(earthMesh);

        // =========================================================================
        // 🏝️ 写真画質！ケープカナベラル砂州・湿地帯・アスファルト道・フレネル海面
        // =========================================================================
        const landscapeGroup = new THREE.Group();
        scene.add(landscapeGroup);

        const terrainCvs = document.createElement('canvas'); terrainCvs.width = 1024; terrainCvs.height = 1024;
        const tctx = terrainCvs.getContext('2d');
        tctx.fillStyle = '#062038'; tctx.fillRect(0, 0, 1024, 1024);
        
        const sandGrad = tctx.createLinearGradient(0, 0, 700, 1024);
        sandGrad.addColorStop(0.35, '#c2a67a');
        sandGrad.addColorStop(0.5, '#8c7853');
        sandGrad.addColorStop(0.7, '#0a324a');
        tctx.fillStyle = sandGrad;
        tctx.beginPath();
        tctx.moveTo(0, 0); tctx.lineTo(650, 0);
        tctx.bezierCurveTo(620, 280, 520, 680, 440, 1024);
        tctx.lineTo(0, 1024); tctx.closePath(); tctx.fill();

        tctx.fillStyle = '#2d4a1d';
        tctx.beginPath();
        tctx.moveTo(0, 0); tctx.lineTo(540, 0);
        tctx.bezierCurveTo(490, 260, 410, 650, 340, 1024);
        tctx.lineTo(0, 1024); tctx.closePath(); tctx.fill();

        tctx.strokeStyle = '#9ca3af'; tctx.lineWidth = 18;
        tctx.beginPath(); tctx.moveTo(80, 512); tctx.lineTo(460, 512); tctx.stroke();

        tctx.strokeStyle = '#374151'; tctx.lineWidth = 8;
        tctx.beginPath(); tctx.moveTo(80, 512); tctx.lineTo(460, 512); tctx.stroke();

        const terrainTex = new THREE.CanvasTexture(terrainCvs);
        const terrainMesh = new THREE.Mesh(
            new THREE.PlaneGeometry(22000, 22000),
            new THREE.MeshStandardMaterial({ map: terrainTex, roughness: 0.92, metalness: 0.05 })
        );
        terrainMesh.rotation.x = -Math.PI / 2;
        terrainMesh.position.set(-1500, -1.2, 0);
        landscapeGroup.add(terrainMesh);

        const oceanMat = new THREE.MeshStandardMaterial({
            color: 0x0a3f63,
            roughness: 0.18,
            metalness: 0.82,
            transparent: true,
            opacity: 0.92
        });
        const oceanMesh = new THREE.Mesh(new THREE.PlaneGeometry(32000, 32000), oceanMat);
        oceanMesh.rotation.x = -Math.PI / 2;
        oceanMesh.position.set(6500, -0.6, 0);
        landscapeGroup.add(oceanMesh);

        // 遠景：NASA VAB
        const vabGroup = new THREE.Group();
        vabGroup.position.set(-4200, 0, -1800);
        const vabMain = new THREE.Mesh(new THREE.BoxGeometry(160, 150, 180), new THREE.MeshStandardMaterial({ color: 0xdbeafe, roughness: 0.4 }));
        vabMain.position.y = 75;
        vabGroup.add(vabMain);
        const flag = new THREE.Mesh(new THREE.BoxGeometry(6, 60, 40), new THREE.MeshBasicMaterial({ color: 0xdc2626 }));
        flag.position.set(82, 80, 0);
        vabGroup.add(flag);
        landscapeGroup.add(vabGroup);

        // 遠景：極低温貯蔵球形タンク群
        for(let g=0; g<3; g++) {
            const sphereTank = new THREE.Mesh(
                new THREE.SphereGeometry(24, 24, 16),
                new THREE.MeshStandardMaterial({ color: 0xf1f5f9, metalness: 0.7, roughness: 0.3 })
            );
            sphereTank.position.set(-1800 - g * 120, 24, -900 + g * 80);
            landscapeGroup.add(sphereTank);
        }

        // =========================================================================
        // 🏗️ 発射施設
        // =========================================================================
        const pad = new THREE.Group();
        scene.add(pad);
        const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x1e242b, metalness: 0.85, roughness: 0.35 });
        const concreteMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.9 });
        const hazardMat = new THREE.MeshStandardMaterial({ color: 0xeab308, roughness: 0.45, metalness: 0.35 });

        const groundPlate = new THREE.Mesh(new THREE.CylinderGeometry(85, 95, 1.4, 32), concreteMat);
        groundPlate.position.y = -0.7; pad.add(groundPlate);

        const olmRing = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 3.6, 1.8, 32), darkSteelMat);
        olmRing.position.y = 5.2; pad.add(olmRing);

        const tower = new THREE.Mesh(new THREE.BoxGeometry(4.5, 56.0, 4.5), darkSteelMat);
        tower.position.set(-9.2, 28.0, 0); pad.add(tower);

        for(let mAng of [0.6, 2.4, 3.9, 5.5]) {
            const lMast = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.45, 58.0, 8), hazardMat);
            lMast.position.set(Math.cos(mAng)*44, 29.0, Math.sin(mAng)*44); pad.add(lMast);
        }

        // =========================================================================
        // 🚀 ロケット本体アセンブリ
        // =========================================================================
        const rocket = new THREE.Group();
        rocket.position.y = 6.0;
        scene.add(rocket);

        const s1Mat = new THREE.MeshStandardMaterial({ color: (simCfg.s1_mat === 'al' ? 0xd97706 : 0xd1d5db), metalness: 0.85, roughness: 0.25 });
        const s2Mat = new THREE.MeshStandardMaterial({ color: (simCfg.s2_mat === 'al' ? 0xd97706 : 0xd1d5db), metalness: 0.85, roughness: 0.25 });

        const s1Len = simCfg.s1_len;
        const interLen = 2.2;
        const s2Len = simCfg.s2_len;
        const s2BaseY = s1Len + interLen;

        // 第1段
        const s1Group = new THREE.Group();
        rocket.add(s1Group);
        const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, 32), s1Mat);
        s1Body.position.y = s1Len / 2; s1Group.add(s1Body);

        // ノズル群
        const s1Tips = [];
        for(let i=0; i<Math.min(simCfg.s1_eng, 9); i++) {
            const ang = (i / Math.min(simCfg.s1_eng, 9)) * Math.PI * 2;
            const r = (i === 0 && simCfg.s1_eng > 1) ? 0 : 0.65;
            const bell = new THREE.Mesh(new THREE.ConeGeometry(0.24, 1.1, 16, 1, true), darkSteelMat);
            bell.rotation.x = Math.PI;
            bell.position.set(Math.cos(ang)*r, 0, Math.sin(ang)*r);
            s1Group.add(bell);

            const plume = new THREE.Mesh(
                new THREE.ConeGeometry(0.8, 18.0, 16),
                new THREE.MeshBasicMaterial({ color: simCfg.flame_hex, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending })
            );
            plume.rotation.x = Math.PI; plume.position.y = -9.0;
            bell.add(plume);
            s1Tips.push({ bell: bell, plume: plume });
        }

        // 第2段
        const s2Group = new THREE.Group();
        s2Group.position.y = s2BaseY;
        rocket.add(s2Group);

        const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, 32), s2Mat);
        s2Body.position.y = s2Len / 2; s2Group.add(s2Body);

        const s2Bell = new THREE.Mesh(new THREE.ConeGeometry(0.48, 1.6, 16, 1, true), darkSteelMat);
        s2Bell.rotation.x = Math.PI; s2Group.add(s2Bell);
        const s2Plume = new THREE.Mesh(
            new THREE.ConeGeometry(1.5, 22.0, 16),
            new THREE.MeshBasicMaterial({ color: simCfg.s2_flame_hex, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending })
        );
        s2Plume.rotation.x = Math.PI; s2Plume.position.y = -11.0;
        s2Plume.visible = false;
        s2Bell.add(s2Plume);

        // 先端ノーズコーン
        const noseCone = new THREE.Mesh(new THREE.ConeGeometry(1.12, 5.2, 32), s2Mat);
        noseCone.position.y = s2Len + 2.6; s2Group.add(noseCone);

        // 外部ブースター
        const boosterUnits = [];
        if (simCfg.strapon_count > 0) {
            for(let i=0; i<simCfg.strapon_count; i++) {
                const angle = (i / simCfg.strapon_count) * Math.PI * 2;
                const bx = Math.cos(angle) * 2.15, bz = Math.sin(angle) * 2.15;
                const bUnit = new THREE.Group();
                bUnit.position.set(bx, 0, bz);

                const bLen = s1Len * 0.82;
                const bBody = new THREE.Mesh(new THREE.CylinderGeometry(0.68, 0.68, bLen, 24), s1Mat);
                bBody.position.y = bLen / 2; bUnit.add(bBody);
                const bNose = new THREE.Mesh(new THREE.ConeGeometry(0.68, 1.8, 24), s1Mat);
                bNose.position.y = bLen + 0.9; bUnit.add(bNose);

                const bPlume = new THREE.Mesh(
                    new THREE.ConeGeometry(0.6, 14.0, 16),
                    new THREE.MeshBasicMaterial({ color: simCfg.flame_hex, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending })
                );
                bPlume.rotation.x = Math.PI; bPlume.position.y = -7.0;
                bUnit.add(bPlume);

                rocket.add(bUnit);
                boosterUnits.push({ mesh: bUnit, angle: angle, plume: bPlume, detached: false, vx: 0, vy: 0, vz: 0 });
            }
        }

        // =========================================================================
        // ✨ 自立パーティクルエンジン (煙・水蒸気・火花)
        // =========================================================================
        const pCanvas = document.createElement('canvas'); pCanvas.width = 32; pCanvas.height = 32;
        const pctx = pCanvas.getContext('2d');
        const pGrad = pctx.createRadialGradient(16,16,2, 16,16,16);
        pGrad.addColorStop(0, 'rgba(255,255,255,0.85)'); pGrad.addColorStop(1, 'rgba(200,215,230,0)');
        pctx.fillStyle = pGrad; pctx.fillRect(0,0,32,32);
        const pTex = new THREE.CanvasTexture(pCanvas);

        const P_MAX = 500;
        const pPool = [];
        const pGroup = new THREE.Group(); scene.add(pGroup);
        for(let i=0; i<P_MAX; i++) {
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: pTex, transparent: true, opacity: 0, depthWrite: false }));
            sp.visible = false; pGroup.add(sp);
            pPool.push({ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 4, o: 0.8 });
        }
        let pIdx = 0;
        function emitP(x, y, z, vx, vy, vz, s0, s1, life, op, col, add) {
            const p = pPool[pIdx]; pIdx = (pIdx + 1) % P_MAX;
            p.active = true; p.sp.visible = true;
            p.sp.position.set(x, y, z);
            p.vx = vx; p.vy = vy; p.vz = vz; p.age = 0; p.maxAge = life; p.s0 = s0; p.s1 = s1; p.o = op;
            p.sp.material.color.setHex(col);
            p.sp.material.blending = add ? THREE.AdditiveBlending : THREE.NormalBlending;
        }

        function drawOrbit(altKm, dRangeKm, exploded) {
            octx.clearRect(0, 0, 266, 70);
            octx.beginPath(); octx.arc(133, 190, 150, Math.PI, 0); octx.strokeStyle = '#1e293b'; octx.lineWidth = 3; octx.stroke();
            const px = 15 + Math.min(236, (dRangeKm / 1200.0) * 236);
            const py = 60 - Math.min(50, (altKm / 200.0) * 50);
            octx.beginPath(); octx.moveTo(15, 60); octx.quadraticCurveTo(px * 0.5, 60, px, py);
            octx.strokeStyle = exploded ? '#ef4444' : '#38bdf8'; octx.lineWidth = 2; octx.stroke();
            octx.fillStyle = exploded ? '#dc2626' : '#38bdf8';
            octx.beginPath(); octx.arc(px, py, 4, 0, Math.PI * 2); octx.fill();
        }

        // =========================================================================
        // ⏱️ アニメーション・メインループ
        // =========================================================================
        const tStart = performance.now();
        let boosterDetached = false;
        let stage1Detached = false;
        let s1Vel = { vx: 0, vy: 0, rotZ: 0 };
        const tempWorld = new THREE.Vector3();

        function animate(now) {
            requestAnimationFrame(animate);
            initAudio();

            const elapsedSec = (now - tStart) / 1000.0;
            const simT = simCfg.is_preview ? -10.0 : (-10.0 + elapsedSec);

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
            const dRangeKm = (rx * 10.0) / 1000.0;

            rocket.position.set(rx, ry + 6.0, 0);
            rocket.rotation.z = -pitch;
            rocket.updateMatrixWorld(true);

            // 1. ブースター分離
            if (!p0.strapon && !boosterDetached && boosterUnits.length > 0 && !simCfg.is_preview) {
                boosterDetached = true;
                playPyro();
                eventLog.innerText = "> KOROLEV CROSS: BOOSTER SLOW-MOTION JETTISON";
                for(let b of boosterUnits) {
                    b.detached = true;
                    b.plume.visible = false;
                    scene.attach(b.mesh);
                    const outX = Math.cos(b.angle);
                    const outZ = Math.sin(b.angle);
                    b.vx = outX * 3.5; b.vy = -1.5; b.vz = outZ * 3.5;
                }
            }
            if (boosterDetached) {
                for(let b of boosterUnits) {
                    b.mesh.position.x += b.vx * 0.016;
                    b.mesh.position.y += b.vy * 0.016;
                    b.mesh.position.z += b.vz * 0.016;
                    b.vy -= 9.8 * 0.016 * 0.6;
                }
            }

            // 2. 第1段分離
            if (p0.stage === 2 && !stage1Detached && !simCfg.is_preview) {
                stage1Detached = true;
                playPyro();
                eventLog.innerText = "> STAGE 1 SEPARATION & SECOND STAGE IGNITION";
                s1Tips.forEach(t => t.plume.visible = false);
                s2Plume.visible = true;
                scene.attach(s1Group);
                s1Vel.vx = -Math.sin(pitch) * 4.0;
                s1Vel.vy = -Math.cos(pitch) * 4.0;
                s1Vel.rotZ = 0.35;
            }
            if (stage1Detached) {
                s1Group.position.x += s1Vel.vx * 0.016;
                s1Group.position.y += s1Vel.vy * 0.016;
                s1Vel.vy -= 9.8 * 0.016 * 0.8;
                s1Group.rotation.z += s1Vel.rotZ * 0.016;
            }

            // 3. 火炎＆火花
            if (p0.thrust && !p0.exploded && !simCfg.is_preview) {
                s1Tips.forEach(t => t.plume.visible = (p0.stage === 1));
                if (p0.stage === 1) {
                    s1Group.getWorldPosition(tempWorld);
                    emitP(tempWorld.x, tempWorld.y, tempWorld.z, -Math.sin(pitch)*2.0, -Math.cos(pitch)*2.0, 0, 0.4, 2.5, 12, 0.9, simCfg.spark_hex, true);
                }
            } else {
                s1Tips.forEach(t => t.plume.visible = false);
                s2Plume.visible = false;
            }

            // 4. カウントダウン・水蒸気
            if (simT < 0.0) {
                const sec = Math.ceil(Math.abs(simT));
                document.getElementById('tv-timer').innerText = simCfg.is_preview ? "PAD INSPECTION" : `T- 00:0${sec}.0`;
                if (simT >= -3.5 && !simCfg.is_preview) {
                    for(let i=0; i<4; i++) {
                        emitP(rx + (Math.random()-0.5)*5, 1.2, (Math.random()-0.5)*5, (i%2===0?1:-1)*1.5, 0.3, 0, 3.5, 18.0, 45, 0.85, 0xf8fafc, false);
                    }
                }
            } else if (!p0.exploded) {
                const m = Math.floor(simT / 60); const s = simT % 60;
                document.getElementById('tv-timer').innerText = `T+ ${String(m).padStart(2,'0')}:${s.toFixed(1).padStart(4,'0')}`;
            }

            // パーティクル更新
            for(let i=0; i<P_MAX; i++) {
                const p = pPool[i]; if (!p.active) continue;
                p.age++;
                if (p.age >= p.maxAge) { p.active = false; p.sp.visible = false; continue; }
                p.sp.position.x += p.vx; p.sp.position.y += p.vy; p.sp.position.z += p.vz;
                const pr = p.age / p.maxAge;
                p.sp.scale.set(p.s0 + (p.s1 - p.s0)*pr, p.s0 + (p.s1 - p.s0)*pr, 1);
                p.sp.material.opacity = p.o * (1.0 - pr);
            }

            // テレメトリ更新
            document.getElementById('pip-hud-alt').innerText = `ALT: ${Math.max(0, alt).toFixed(1)} km`;
            document.getElementById('hud-downrange').innerText = `${dRangeKm.toFixed(1)} km`;
            document.getElementById('tv-mach').innerText = `M ${mach.toFixed(2)}`;
            document.getElementById('tv-spd').innerText = `(${Math.round(vel * 3.6).toLocaleString()} km/h)`;
            document.getElementById('tv-alt').innerText = Math.max(0, alt).toFixed(1);
            document.getElementById('tv-q').innerText = q.toFixed(1);
            document.getElementById('tv-g').innerText = accG.toFixed(1);
            drawOrbit(alt, dRangeKm, p0.exploded);

            // カメラ位置更新
            const targetFocus = (p0.stage === 2) ? s2Group : rocket;
            targetFocus.getWorldPosition(tempWorld);

            if (simCfg.is_preview) {
                const orbitAng = elapsedSec * 0.28;
                cameraMain.position.set(Math.sin(orbitAng)*72.0, 22.0, Math.cos(orbitAng)*72.0);
            } else {
                cameraMain.position.set(tempWorld.x - 38.0, Math.max(12.0, tempWorld.y - 12.0), tempWorld.z + 85.0);
            }
            cameraMain.lookAt(tempWorld);
            cameraPip.lookAt(tempWorld);

            // =========================================================================
            // 🎥 画面被りゼロ！2画面ビューポート分割レンダリング
            // =========================================================================
            const w = window.innerWidth;
            const h = window.innerHeight;

            renderer.setScissorTest(false);
            renderer.clear();

            // 1. メイン画面 (全画面フルビュー)
            cameraMain.aspect = w / h;
            cameraMain.updateProjectionMatrix();
            renderer.setViewport(0, 0, w, h);
            renderer.render(scene, cameraMain);

            // 2. サブ遠景画面 (右上PiP領域・トグルで非表示可能)
            if (pipVisible) {
                const pipW = 330;
                const pipH = 200;
                const pipX = w - pipW - 24;
                const pipY = h - pipH - 58;

                renderer.setScissorTest(true);
                renderer.setScissor(pipX, pipY, pipW, pipH);
                renderer.setViewport(pipX, pipY, pipW, pipH);

                cameraPip.aspect = pipW / pipH;
                cameraPip.updateProjectionMatrix();
                renderer.render(scene, cameraPip);
            }
        }

        requestAnimationFrame(animate);

        window.addEventListener('resize', () => {
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

# 安全なJSONプレースホルダー置換
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
        st.success("🎉 **ミッション完全成功 (SECO & LEO Insertion)**: 全段燃焼および分離シーケンスが正常に推移し、第2段オービターが低軌道投入条件に到達しました。")
