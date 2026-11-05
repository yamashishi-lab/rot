import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect Extreme: 4K Masterpiece Edition", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect Extreme - 4K実写級ロケット設計＆光学中継シミュレーター")
st.markdown("エンジンノズル直結スパークシャワー、ワールド座標完全分離物理（ブースター追従バグ完全解消）、見切れゼロ絶対重心ロックオンカメラ、超膨大パーツDB搭載。")

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
    "【三元推進剤】リチウム・フッ素・液体水素 (Li / F2 / LH2) [化学燃料最高Isp]": {
        "base_isp_sl": 445, "base_isp_vac": 542, "base_thrust": 2200, "density": 0.55, 
        "flame_hex": 0x5eead4, "outer_hex": 0x0f766e, "spark_hex": 0x99f6e4, "risk": 0.08, "type": "triprop"
    },
    "【高エネルギー】ボロン添加ゲル化ケロシンスラリー (RP-1 / B)": {
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
    "エキスパンダーブリードサイクル [LE-5B / LE-9型・高信頼]": {"isp_mod": 1.05, "thrust_mod": 0.88, "mass_mod": 0.92, "max_pressure_limit": 160, "cyc_id": "expander"},
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
# 🎛️ パラメータ設定タブ (全項目がリアルタイムで3Dハンガー＆フライトに連動)
# =========================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 第1段 (コア＆外部ブースター群)", 
    "🛩️ 空力フィン・フラップ・翼", 
    "🛰️ 第2段 (オービター) & 先端・衛星", 
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
        s1_eps = st.slider("海面膨張比 (ε: ノズルサイズ連動)", 8, 70, 24, step=1)
        strapon_opt = st.selectbox("外部追加ブースター (分離物理対応)", list(STRAPON_BOOSTERS.keys()), index=2)
    with c3:
        st.markdown("#### タンク構造・素材")
        s1_fuel = st.slider("第1段 推進剤充填量 (トン: 胴体長連動)", 100.0, 4500.0, 1100.0, step=50.0)
        s1_mat = st.selectbox("第1段 構造素材", list(MATERIALS.keys()), index=0)
        s1_thick = st.slider("外殻等価板厚 (mm)", 1.0, 12.0, 4.2, step=0.1)

with tab2:
    st.markdown("#### 🚀 空力安定板・姿勢制御システム")
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 空力パーツ", list(AERO_WINGS.keys()), index=0)
        angle_of_attack = st.slider("固定取り付け角迎角 AoA (deg: 翼角度連動)", -3.0, 12.0, 0.5, step=0.5)
    with c2:
        st.info("💡 **完全修正＆リアルタイム連動**: エンジンベル開口部から直接火花とジェットが噴き出し、外部ブースターは燃料枯渇時にワールド空間へ切り離されて後方へ落下します。")

with tab3:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 第2段 真空推進系")
        s2_prop = st.selectbox("第2段 推進剤", list(PROPELLANTS.keys()), index=0)
        s2_cycle = st.selectbox("第2段 ポンプ方式", list(PUMP_CYCLES.keys()), index=0)
        s2_eng_count = st.slider("真空特化ノズル基数", 1, 9, 3)
        s2_pc = st.slider("第2段 燃焼室圧 (bar)", 20, 350, 220, step=10)
        s2_eps = st.slider("第2段 真空膨張比 (ε: 真空ノズル巨大化)", 30, 280, 150, step=5)
    with c2:
        st.markdown("#### 第2段 構造・タンク")
        s2_fuel = st.slider("第2段 推進剤充填量 (トン: 2段目長連動)", 20.0, 1200.0, 280.0, step=10.0)
        s2_mat = st.selectbox("第2段 構造素材", list(MATERIALS.keys()), index=0)
        s2_thick = st.slider("第2段 壁厚 (mm)", 0.8, 8.0, 3.0, step=0.1)
    with c3:
        st.markdown("#### 先端フェアリング & ペイロード")
        fairing_type = st.selectbox("先端空力カウル / 衛星ペイロード", list(FAIRINGS.keys()), index=0)
        fairing_sep_alt = st.slider("フェアリング分離高度 (km)", 40.0, 180.0, 75.0, step=5.0)
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
# 💥 物理シミュレーション & 確実なブースター分離判定エンジン
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
        fail_reason = "特異点崩壊: 反陽子スラリーが臨界暴走。発射台ごと事象の地平線へ爆縮。"
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
        strap_m = (strapon_spec["mass_add"] * 1000.0 + max(0.0, fuel_strapon_rem)) if strapon_attached else 0.0

        if stage == 1:
            # 外部ブースターは燃料枯渇、または第1段残量35%以下で確実に分離させる
            if strapon_attached:
                if fuel_strapon_rem > 0 and (fuel_s1_rem > s1_fuel * 1000.0 * 0.25):
                    strap_thrust = strapon_spec["thrust_add"] * 1000.0
                    # ブースター燃焼速度を1.35倍に高め、第1段MECOより前に必ず分離させる
                    fuel_strapon_rem -= (strap_thrust / (strapon_spec["isp_sl"] * g0)) * dt * 1.35
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

cb1, cb2 = st.columns([3, 1])
with cb1:
    launch_clicked = st.button("🔴 4K 光学トラッキング実写中継 ＆ 軌道投入シミュレーション開始", use_container_width=True, type="primary")
with cb2:
    st.caption("※ タブで部品を変えると下の3Dハンガーのロケット形状が即座に変化します。")

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
    "strapon_count": int(strapon_spec["count"])
}

traj_json = json.dumps(traj_data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
cfg_json = json.dumps(rocket_visual_cfg)
fail_msg_clean = (error_msg or "").replace('"', '\\"').replace("'", "\\'")

html_code = f"""
<div id="broadcast-frame" style="position: relative; width: 100%; height: 940px; background: #000104; border-radius: 8px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none;">
    <script>
        if ({'false' if not launch_clicked else 'true'}) {{
            window.parent.document.getElementById('launch-viewport').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
    </script>

    <div id="canvas-container" style="width: 100%; height: 100%; position: absolute; top: 0; left: 0;"></div>

    <!-- 実写シネマ望遠レンズ・ビネット & 光学トラッキング・レティクル -->
    <div style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; box-shadow: inset 0 0 140px rgba(0,0,0,0.88); z-index: 5;">
        <div style="position: absolute; top: 50%; left: 50%; width: 56px; height: 56px; transform: translate(-50%, -50%); border: 1px solid rgba(56, 189, 248, 0.22); border-radius: 50%;"></div>
        <div style="position: absolute; top: 50%; left: calc(50% - 40px); width: 20px; height: 1px; background: rgba(56, 189, 248, 0.35);"></div>
        <div style="position: absolute; top: 50%; left: calc(50% + 20px); width: 20px; height: 1px; background: rgba(56, 189, 248, 0.35);"></div>
    </div>

    <!-- 放送中継トップバナー -->
    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 48px; background: rgba(3, 7, 18, 0.88); backdrop-filter: blur(16px); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 10;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <span id="live-indicator" style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 12px #ef4444; animation: livePulse 1.4s infinite alternate;"></span>
            <span style="color: #ffffff; font-weight: 800; font-size: 13px; letter-spacing: 2px;">OFFICIAL 4K OPTICAL WEBCAST</span>
            <span style="color: rgba(255,255,255,0.2);">|</span>
            <span id="cam-tag" style="color: #38bdf8; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; font-family: monospace;">OPTICS: PAD 39A HANGAR INSPECTION CAM</span>
        </div>
        <div style="display: flex; align-items: center; gap: 20px; font-family: monospace; font-size: 11px;">
            <span style="color: #94a3b8;">RCS THRUSTERS: <strong id="hud-rcs" style="color: #38bdf8;">STANDBY</strong></span>
            <span style="color: #94a3b8;">REGIME: <strong id="hud-regime" style="color: #f8fafc;">SEA LEVEL</strong></span>
            <span id="comm-status" style="color: #10b981;">TELEMETRY: LOCKED</span>
        </div>
    </div>

    <style>@keyframes livePulse {{ from {{ opacity: 0.35; }} to {{ opacity: 1.0; }} }}</style>

    <!-- 🛰️ 軌道フライト & 分離イベントログ HUD -->
    <div style="position: absolute; top: 60px; right: 24px; width: 295px; background: rgba(3, 7, 18, 0.85); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 4px; padding: 14px; z-index: 10; color: #fff;">
        <div style="font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 8px; display: flex; justify-content: space-between;">
            <span>DOWNRANGE TRAJECTORY</span>
            <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">0.0 km</span>
        </div>
        <canvas id="orbit-canvas" width="265" height="90" style="width: 100%; height: 90px; background: #01040d; border-radius: 2px;"></canvas>
        <div id="event-log" style="margin-top: 8px; font-family: monospace; font-size: 10px; color: #34d399; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
            > VEHICLE CONFIG SYNCED ON PAD
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
    const orbitCvs = document.getElementById('orbit-canvas');
    const octx = orbitCvs.getContext('2d');
    const flashOverlay = document.getElementById('flash-overlay');
    const rudBanner = document.getElementById('rud-banner');
    const rudDesc = document.getElementById('rud-desc');
    const eventLog = document.getElementById('event-log');

    // 音響エンジン
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    let actx = null, rumbleGain = null, crackleGain = null;
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
        u.lang = 'en-US'; u.rate = 1.06; u.pitch = 0.92;
        window.speechSynthesis.speak(u);
    }}

    // =========================================================================
    // 🌍 Three.js シーン & 実写PBR環境マップ構築
    // =========================================================================
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(26, container.clientWidth / container.clientHeight, 0.5, 50000000);
    const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

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

    const sunLight = new THREE.DirectionalLight(0xfff9f0, 4.0);
    sunLight.position.set(4000, 7500, 5000);
    scene.add(sunLight);
    scene.add(new THREE.HemisphereLight(0x7dd3fc, 0x1e293b, 0.68));

    const engineBounceLight = new THREE.PointLight(cfg.flame_hex, 0.0, 280, 1.5);
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

    // 実写地球テクスチャ＆大気散乱ドーム
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
    // 🏗️ Starbase / LC-39A 発射複合施設 (デリュージ水冷鋼板・ホールドダウンアーム付)
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

    // 水冷ビデシャワー鋼板 & OLM 20本脚
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
        const diag = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 6.2, 8), darkSteelMat);
        diag.position.set(towerX, h + 1.9, 2.2); diag.rotation.z = 0.82; pad.add(diag);
        const diag2 = diag.clone(); diag2.rotation.z = -0.82; diag2.position.z = -2.2; pad.add(diag2);
    }}
    for(let zSide of [-1.4, 1.4]) {{
        const chopstick = new THREE.Mesh(new THREE.BoxGeometry(9.2, 0.55, 0.45), darkSteelMat);
        chopstick.position.set(towerX + 5.5, 6.0 + cfg.s1_len + 2.0, zSide);
        pad.add(chopstick);
    }}
    for(let tIdx = 0; tIdx < 4; tIdx++) {{
        const cryoTank = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 11.0, 32), pipeMat);
        cryoTank.position.set(-28 - tIdx * 6.5, 5.5, -18); pad.add(cryoTank);
        const dome = new THREE.Mesh(new THREE.SphereGeometry(2.2, 32, 16), pipeMat);
        dome.position.set(-28 - tIdx * 6.5, 11.0, -18); pad.add(dome);
    }}
    for(let mAng of [0.6, 2.4, 3.9, 5.5]) {{
        const lMast = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.45, 58.0, 8), hazardMat);
        lMast.position.set(Math.cos(mAng)*44, 29.0, Math.sin(mAng)*44); pad.add(lMast);
    }}

    // =========================================================================
    // 🎨 素材別・超精細プロシージャルPBRテクスチャ生成
    // =========================================================================
    function createMaterialSkin(matId, hasHeatshield) {{
        const w = 1024, h = 2048;
        const diffCvs = document.createElement('canvas'); diffCvs.width = w; diffCvs.height = h;
        const dctx = diffCvs.getContext('2d');
        const bumpCvs = document.createElement('canvas'); bumpCvs.width = w; bumpCvs.height = h;
        const bctx = bumpCvs.getContext('2d');

        bctx.fillStyle = '#808080'; bctx.fillRect(0, 0, w, h);

        if (matId === 'ss') {{
            dctx.fillStyle = '#d1d5db'; dctx.fillRect(0, 0, w, h);
            for(let y = 0; y < h; y += 64) {{
                const s = (Math.random() - 0.5) * 20;
                dctx.fillStyle = `rgb(${{208+s}}, ${{213+s}}, ${{221+s}})`;
                dctx.fillRect(0, y, w, 62);
                dctx.fillStyle = 'rgba(80, 60, 40, 0.35)'; dctx.fillRect(0, y, w, 3);
                bctx.fillStyle = '#303030'; bctx.fillRect(0, y, w, 4);
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
        }} else if (matId === 'cf' || matId === 'cnt') {{
            dctx.fillStyle = (matId === 'cnt') ? '#090d16' : '#141619';
            dctx.fillRect(0, 0, w, h);
            dctx.fillStyle = '#27272a';
            for(let y = 0; y < h; y += 8) {{
                for(let x = 0; x < w; x += 8) {{
                    if ((x+y)%16 === 0) {{
                        dctx.fillRect(x, y, 4, 4);
                        bctx.fillStyle = '#b0b0b0'; bctx.fillRect(x, y, 4, 4);
                    }}
                }}
            }}
        }} else if (matId === 'gold') {{
            dctx.fillStyle = '#f59e0b'; dctx.fillRect(0, 0, w, h);
            for(let y = 0; y < h; y += 48) {{
                dctx.fillStyle = '#d97706'; dctx.fillRect(0, y, w, 4);
                bctx.fillStyle = '#404040'; bctx.fillRect(0, y, w, 4);
            }}
        }} else if (matId === 'wood') {{
            dctx.fillStyle = '#b45309'; dctx.fillRect(0, 0, w, h);
            for(let x = 0; x < w; x += 32) {{
                dctx.fillStyle = (x%64===0) ? '#92400e' : '#b45309';
                dctx.fillRect(x, 0, 30, h);
                bctx.fillStyle = '#303030'; bctx.fillRect(x, 0, 2, h);
            }}
        }} else {{
            dctx.fillStyle = '#52525b'; dctx.fillRect(0, 0, w, h);
            for(let y = 0; y < h; y += 48) {{
                dctx.fillStyle = '#27272a'; dctx.fillRect(0, y, w, 4);
                bctx.fillStyle = '#202020'; bctx.fillRect(0, y, w, 4);
            }}
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
    // 🔥 エンジンノズル直結プルーム＆スパークエミッター対応クラスター構築
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

                // ノズル開口部(distFromNozzle=0)にぴったり直結させ隙間をゼロにする
                float tipFade = smoothstep(0.0, 0.015, distFromNozzle) * smoothstep(1.0, 0.12, distFromNozzle);
                float alpha = clamp((plumeBody * 0.95 + coreMask * 0.85) * tipFade * noise, 0.0, 1.0);

                gl_FragColor = vec4(col * 2.4, alpha);
            }}
        `
    }});

    function createNozzlePlumeMesh(jetWidth, jetLength) {{
        const jetGroup = new THREE.Group();
        for(let rAngle of [0, Math.PI / 2]) {{
            const pPlane = new THREE.Mesh(new THREE.PlaneGeometry(jetWidth, jetLength, 12, 48), plumeShaderMat);
            pPlane.position.y = -jetLength / 2;
            pPlane.rotation.y = rAngle;
            jetGroup.add(pPlane);
        }}
        return jetGroup;
    }}

    // 各ステージのエンジンノズル先端（火花＆煙の発生源）を記録する配列
    const s1NozzleTips = [];
    const s2NozzleTips = [];
    const boosterNozzleTips = [];

    const inconelNozzleMat = new THREE.MeshStandardMaterial({{ color: 0x3f3f46, metalness: 0.95, roughness: 0.22, side: THREE.DoubleSide }});
    const copperLinerMat = new THREE.MeshStandardMaterial({{ color: 0xd97706, metalness: 0.92, roughness: 0.25, side: THREE.DoubleSide }});

    function buildDetailedEngineCluster(parent, count, radius, basePosY, epsScale, cycId, tipArray, jetLen) {{
        const group = new THREE.Group();
        group.position.y = basePosY;

        const bellH = 1.15 * epsScale;
        const bellW = 0.24 * Math.pow(epsScale, 0.65);

        if (cycId === 'aerospike') {{
            const ramp = new THREE.Mesh(new THREE.ConeGeometry(1.08, 2.2, 4), inconelNozzleMat);
            ramp.rotation.x = Math.PI; ramp.rotation.y = Math.PI / 4; ramp.position.y = -1.1;
            group.add(ramp);
            const tipObj = new THREE.Object3D();
            tipObj.position.set(0, -0.4, 0);
            const plumeMesh = createNozzlePlumeMesh(2.4, jetLen);
            tipObj.add(plumeMesh);
            group.add(tipObj);
            tipArray.push({{ node: tipObj, plume: plumeMesh }});
        }} else {{
            const nozzlePts = [];
            for(let i=0; i<=16; i++) {{
                const t = i / 16;
                nozzlePts.push(new THREE.Vector2(0.08 + bellW * Math.pow(t, 0.62), -t * bellH));
            }}
            const bellGeo = new THREE.LatheGeometry(nozzlePts, 28);

            // エンジン基数が多い場合でもノズルから直接出る代表ジェットとスパークエミッターを配置
            const visualPlumeStep = Math.max(1, Math.floor(count / 6));

            for(let i=0; i<count; i++) {{
                const ang = (i / count) * Math.PI * 2;
                const r = (count === 1) ? 0 : (i < 3 && count > 6 ? radius * 0.38 : radius);
                const engUnit = new THREE.Group();
                engUnit.position.set(Math.cos(ang)*r, 0, Math.sin(ang)*r);

                const bell = new THREE.Mesh(bellGeo, (cycId === 'rde') ? copperLinerMat : inconelNozzleMat);
                engUnit.add(bell);

                // ノズル内側の白熱スロート発光ディスク（下から覗いた時にエンジン内部が真っ赤/青白く光る）
                const throatGlow = new THREE.Mesh(
                    new THREE.CircleGeometry(bellW * 0.85, 16),
                    new THREE.MeshBasicMaterial({{ color: 0xffffff, side: THREE.DoubleSide }})
                );
                throatGlow.rotation.x = Math.PI / 2;
                throatGlow.position.y = -bellH * 0.85;
                engUnit.add(throatGlow);

                const manifold = new THREE.Mesh(new THREE.TorusGeometry(0.14 * epsScale, 0.03, 8, 16), pipeMat);
                manifold.rotation.x = Math.PI / 2; manifold.position.y = -0.22;
                engUnit.add(manifold);

                if (cycId === 'gg') {{
                    const dumpPipe = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.05, bellH * 0.9, 8), darkSteelMat);
                    dumpPipe.position.set(0.18 * epsScale, -bellH * 0.45, 0);
                    engUnit.add(dumpPipe);
                }} else if (cycId === 'pedal') {{
                    const gear = new THREE.Mesh(new THREE.TorusGeometry(0.25, 0.04, 8, 16), hazardMat);
                    gear.position.set(0, -0.35, 0.25); engUnit.add(gear);
                }}

                // ノズル開口部直下にエミッターノードを設置
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
        }}
        parent.add(group);
        return group;
    }}

    // =========================================================================
    // 🚀 宇宙機アセンブリ構築 (ワールド座標完全切り離し対応)
    // =========================================================================
    const rocket = new THREE.Group();
    rocket.position.y = 6.0;
    scene.add(rocket);

    const s1Maps = createMaterialSkin(cfg.s1_mat, false);
    const s2Maps = createMaterialSkin(cfg.s2_mat, true);

    const s1Mat = new THREE.MeshStandardMaterial({{
        map: s1Maps.map, bumpMap: s1Maps.bumpMap, bumpScale: 0.04,
        metalness: (cfg.s1_mat === 'ss' || cfg.s1_mat === 'inconel' || cfg.s1_mat === 'gold') ? 0.92 : (cfg.s1_mat === 'wood' ? 0.05 : 0.25),
        roughness: (cfg.s1_mat === 'ss' || cfg.s1_mat === 'gold') ? 0.16 : (cfg.s1_mat === 'wood' ? 0.85 : 0.42)
    }});
    const s2Mat = new THREE.MeshStandardMaterial({{
        map: s2Maps.map, bumpMap: s2Maps.bumpMap, bumpScale: 0.045,
        metalness: (cfg.s2_mat === 'ss' || cfg.s2_mat === 'inconel' || cfg.s2_mat === 'gold') ? 0.88 : (cfg.s2_mat === 'wood' ? 0.05 : 0.28),
        roughness: (cfg.s2_mat === 'ss' || cfg.s2_mat === 'gold') ? 0.18 : (cfg.s2_mat === 'wood' ? 0.85 : 0.45)
    }});

    const s1Len = cfg.s1_len;
    const interLen = 2.2;
    const s2Len = cfg.s2_len;
    const s2BaseY = s1Len + interLen;
    const noseY = s2BaseY + s2Len;

    // 1. 第1段コアグループ
    const s1Group = new THREE.Group();
    rocket.add(s1Group);

    const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, 64), s1Mat);
    s1Body.position.y = s1Len / 2; s1Group.add(s1Body);

    for(let side of [-1, 1]) {{
        const chine = new THREE.Mesh(new THREE.BoxGeometry(0.24, s1Len * 0.94, 0.32), s1Mat);
        chine.position.set(side * 1.12, s1Len * 0.48, 0); s1Group.add(chine);
        const loxPipe = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, s1Len * 0.88, 16), pipeMat);
        loxPipe.position.set(0, s1Len * 0.46, side * 1.14); s1Group.add(loxPipe);
    }}
    const skirtRing = new THREE.Mesh(new THREE.CylinderGeometry(1.18, 1.22, 1.8, 64), darkSteelMat);
    skirtRing.position.y = 0.9; s1Group.add(skirtRing);

    const interstage = new THREE.Group();
    interstage.position.y = s1Len + interLen / 2;
    s1Group.add(interstage);
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

    const s1EpsScale = 0.75 + (cfg.s1_eps / 70.0) * 0.75;
    const s1Engines = buildDetailedEngineCluster(s1Group, cfg.s1_eng, 0.78, 0.0, s1EpsScale, cfg.s1_cyc, s1NozzleTips, 32.0);

    // 空力翼・フィン（8種の豊富な造形）
    const wingsGroup = new THREE.Group();
    s1Group.add(wingsGroup);
    const aoaRad = (cfg.aoa * Math.PI) / 180.0;

    if (cfg.wing_id === 'grid') {{
        for(let i=0; i<4; i++) {{
            const ang = (i / 4) * Math.PI * 2 + Math.PI / 4;
            const gfFrame = new THREE.Group();
            gfFrame.position.set(Math.cos(ang)*1.22, s1Len - 1.1, Math.sin(ang)*1.22);
            gfFrame.rotation.y = -ang; gfFrame.rotation.z = aoaRad;
            const mount = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.65, 0.35), darkSteelMat);
            gfFrame.add(mount);
            const gridBox = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.14, 1.25), new THREE.MeshStandardMaterial({{ color: 0x94a3b8, metalness: 0.9, roughness: 0.3, wireframe: true }}));
            gridBox.position.x = 0.62; gfFrame.add(gridBox);
            wingsGroup.add(gfFrame);
        }}
    }} else if (cfg.wing_id === 'starship_flap') {{
        for(let side of [-1, 1]) {{
            const aftFlap = new THREE.Mesh(new THREE.BoxGeometry(1.6, 4.2, 0.12), darkSteelMat);
            aftFlap.position.set(side * 1.7, 2.8, 0); aftFlap.rotation.z = side * 0.15; aftFlap.rotation.x = aoaRad;
            wingsGroup.add(aftFlap);
        }}
    }} else if (cfg.wing_id === 'tail_fins') {{
        for(let i=0; i<4; i++) {{
            const ang = (i / 4) * Math.PI * 2;
            const fin = new THREE.Mesh(new THREE.BoxGeometry(1.8, 3.2, 0.12), s1Mat);
            fin.position.set(Math.cos(ang)*1.8, 2.0, Math.sin(ang)*1.8);
            fin.rotation.y = -ang; fin.rotation.z = 0.25;
            wingsGroup.add(fin);
        }}
    }} else if (cfg.wing_id === 'delta_wing' || cfg.wing_id === 'forward_swept') {{
        const sweepSign = (cfg.wing_id === 'forward_swept') ? -1 : 1;
        for(let side of [-1, 1]) {{
            const wing = new THREE.Mesh(new THREE.BoxGeometry(5.2, 6.2, 0.15), darkSteelMat);
            wing.position.set(side * 3.1, s1Len * 0.35, 0);
            wing.rotation.z = side * sweepSign * 0.45;
            wing.rotation.x = aoaRad;
            wingsGroup.add(wing);
        }}
    }} else if (cfg.wing_id === 'lifting_body') {{
        for(let side of [-1, 1]) {{
            const wBody = new THREE.Mesh(new THREE.BoxGeometry(2.8, 4.5, 0.18), darkSteelMat);
            wBody.position.set(side * 2.2, s1Len * 0.3, 0);
            wBody.rotation.y = side * 0.35; wBody.rotation.z = -side * 0.25;
            wingsGroup.add(wBody);
        }}
    }} else if (cfg.wing_id === 'glider') {{
        for(let side of [-1, 1]) {{
            const gWing = new THREE.Mesh(new THREE.BoxGeometry(12.0, 1.6, 0.14), new THREE.MeshStandardMaterial({{ color: 0x18181b, roughness: 0.2 }}));
            gWing.position.set(side * 6.6, s1Len * 0.52, 0);
            gWing.rotation.x = aoaRad;
            wingsGroup.add(gWing);
        }}
    }}

    // 2. 外部ストラップオンブースター群（全種類造形＆ワールド座標デタッチ対応）
    const boosterUnits = [];
    if (cfg.strapon_count > 0) {{
        const sCount = cfg.strapon_count;
        for(let i=0; i<sCount; i++) {{
            const angle = (i / sCount) * Math.PI * 2;
            const distR = (cfg.strapon_type === 'firework' || cfg.strapon_type === 'srb_small') ? 1.68 : 2.15;
            const bx = Math.cos(angle) * distR, bz = Math.sin(angle) * distR;
            const bUnit = new THREE.Group();
            bUnit.position.set(bx, 0, bz);

            let bLen = s1Len * 0.82;
            let bRadTop = 0.68, bRadBot = 0.68;
            let bMat = s1Mat;

            if (cfg.strapon_type === 'soyuz') {{
                // ソユーズ R-7 特有の円錐テーパーブースター
                bLen = s1Len * 0.68; bRadTop = 0.22; bRadBot = 0.88;
                bMat = new THREE.MeshStandardMaterial({{ color: 0x475569, metalness: 0.7, roughness: 0.35 }});
            }} else if (cfg.strapon_type === 'srb') {{
                bLen = s1Len * 0.92; bRadTop = 0.78; bRadBot = 0.78;
                bMat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.35 }});
                for(let seg=1; seg<=4; seg++) {{
                    const ring = new THREE.Mesh(new THREE.CylinderGeometry(0.80, 0.80, 0.22, 32), darkSteelMat);
                    ring.position.y = (bLen / 5) * seg; bUnit.add(ring);
                }}
            }} else if (cfg.strapon_type === 'srb_small') {{
                bLen = s1Len * 0.52; bRadTop = 0.42; bRadBot = 0.42;
                bMat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.35 }});
            }} else if (cfg.strapon_type === 'firework') {{
                bLen = s1Len * 0.55; bRadTop = 0.34; bRadBot = 0.34;
                bMat = new THREE.MeshStandardMaterial({{ color: (i%2===0) ? 0xdc2626 : 0xeab308, roughness: 0.4 }});
            }} else if (cfg.strapon_type === 'lrb_ring') {{
                bLen = s1Len * 0.75; bRadTop = 0.38; bRadBot = 0.38;
            }}

            const bBody = new THREE.Mesh(new THREE.CylinderGeometry(bRadTop, bRadBot, bLen, 36), bMat);
            bBody.position.y = bLen / 2; bUnit.add(bBody);

            const bNose = new THREE.Mesh(new THREE.ConeGeometry(bRadTop, bRadTop * 2.8, 36), (cfg.strapon_type === 'firework') ? hazardMat : bMat);
            bNose.position.y = bLen + bRadTop * 1.4; bUnit.add(bNose);

            const strut = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.9, 8), darkSteelMat);
            strut.rotation.z = Math.PI/2; strut.position.set(-Math.cos(angle)*0.5, bLen*0.75, -Math.sin(angle)*0.5);
            bUnit.add(strut);

            const localTips = [];
            buildDetailedEngineCluster(bUnit, 1, 0, 0, (cfg.strapon_type === 'srb') ? 1.3 : 0.8, 'sc', localTips, 26.0);
            localTips.forEach(t => boosterNozzleTips.push(t));

            rocket.add(bUnit);
            boosterUnits.push({{
                mesh: bUnit, angle: angle, baseX: bx, baseZ: bz,
                detached: false, vx: 0, vy: 0, vz: 0, rx: 0, rz: 0, tips: localTips
            }});
        }}
    }}

    // 3. 第2段オービター ＆ ペイロード ＆ フェアリング
    const s2Group = new THREE.Group();
    s2Group.position.y = s2BaseY;
    rocket.add(s2Group);

    const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, 64), s2Mat);
    s2Body.position.y = s2Len / 2; s2Group.add(s2Body);

    const s2EpsScale = 1.0 + (cfg.s2_eps / 280.0) * 1.1;
    const s2Engines = buildDetailedEngineCluster(s2Group, cfg.s2_eng, 0.55, 0.0, s2EpsScale, cfg.s2_cyc, s2NozzleTips, 34.0);
    // 第2段プルームは初期状態では非表示
    s2NozzleTips.forEach(t => {{ t.plume.visible = false; }});

    // 内部衛星ペイロード（JWSTミラーまたは金箔通信衛星）
    const payloadGroup = new THREE.Group();
    payloadGroup.position.y = s2Len + 1.8;
    s2Group.add(payloadGroup);

    if (cfg.fairing_shape === 'jwst') {{
        const mirrorWall = new THREE.Group();
        for(let mx=-1; mx<=1; mx++) {{
            for(let my=-1; my<=1; my++) {{
                const hexSeg = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.28, 0.08, 6), goldFoilMat);
                hexSeg.rotation.z = Math.PI / 2;
                hexSeg.position.set(0.35, my * 0.52, mx * 0.52);
                mirrorWall.add(hexSeg);
            }}
        }}
        payloadGroup.add(mirrorWall);
        const sunshield = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.08, 1.4), new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, metalness: 0.9, roughness: 0.2 }}));
        sunshield.position.y = -1.1; payloadGroup.add(sunshield);
    }} else {{
        const satBus = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 2.4, 16), goldFoilMat);
        payloadGroup.add(satBus);
        const satDish = new THREE.Mesh(new THREE.ConeGeometry(0.55, 0.35, 24, 1, true), pipeMat);
        satDish.rotation.x = Math.PI; satDish.position.y = 1.35; payloadGroup.add(satDish);
        for(let side of [-1, 1]) {{
            const solarWing = new THREE.Mesh(new THREE.BoxGeometry(0.15, 2.0, 0.75), new THREE.MeshStandardMaterial({{ color: 0x1d4ed8, metalness: 0.8, roughness: 0.2 }}));
            solarWing.position.set(side * 0.75, 0, 0); payloadGroup.add(solarWing);
        }}
    }}

    // 先端フェアリング・カプセル群（ワールド座標デタッチ対応）
    const fairingHalves = [];
    const ogivePts = [];
    const noseH = (cfg.fairing_shape === 'needle') ? 8.2 : 5.4;
    for(let i=0; i<=30; i++) {{
        const t = i / 30;
        const y = t * noseH;
        const r = (cfg.fairing_shape === 'needle') ? 1.12 * (1.0 - t) : 1.12 * Math.pow(1.0 - Math.pow(t, 1.65), 0.72);
        ogivePts.push(new THREE.Vector2(Math.max(0.01, r), y));
    }}

    if (cfg.fairing_shape === 'abort_tower') {{
        const lesGroup = new THREE.Group();
        lesGroup.position.y = s2Len;
        const capsule = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 1.12, 2.4, 48), s2Mat);
        capsule.position.y = 1.2; lesGroup.add(capsule);
        const lesTower = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.22, 4.2, 24), new THREE.MeshStandardMaterial({{ color: 0xf8fafc, metalness: 0.5 }}));
        lesTower.position.y = 4.2; lesGroup.add(lesTower);
        for(let k=0; k<4; k++) {{
            const a = (k/4)*Math.PI*2;
            const thr = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.7, 16), hazardMat);
            thr.position.set(Math.cos(a)*0.22, 5.2, Math.sin(a)*0.22); thr.rotation.z = Math.cos(a)*0.4;
            lesGroup.add(thr);
        }}
        s2Group.add(lesGroup);
        fairingHalves.push({{ mesh: lesGroup, side: 1, detached: false, vx: 0, vy: 0, rotZ: 0 }});
    }} else if (cfg.fairing_shape === 'starship_crew') {{
        const crewCone = new THREE.Mesh(new THREE.LatheGeometry(ogivePts, 64), s2Mat);
        crewCone.position.y = s2Len;
        // クルーキャビン発光ウィンドウ
        const winMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.88, 0.96, 0.65, 32, 1, true, -0.6, 1.2), new THREE.MeshBasicMaterial({{ color: 0xbae6fd, side: THREE.DoubleSide }}));
        winMesh.position.y = 2.0; crewCone.add(winMesh);
        for(let side of [-1, 1]) {{
            const canard = new THREE.Mesh(new THREE.BoxGeometry(0.85, 2.1, 0.08), darkSteelMat);
            canard.position.set(side * 1.05, 2.2, 0); canard.rotation.z = side * 0.22;
            crewCone.add(canard);
        }}
        s2Group.add(crewCone);
    }} else {{
        for(let side of [-1, 1]) {{
            const phiStart = (side === 1) ? 0 : Math.PI;
            const halfGeo = new THREE.LatheGeometry(ogivePts, 32, phiStart, Math.PI);
            const fMat = (cfg.fairing_shape === 'skeleton') ?
                new THREE.MeshStandardMaterial({{ color: 0x38bdf8, wireframe: true }}) : s2Mat;
            const halfMesh = new THREE.Mesh(halfGeo, fMat);
            halfMesh.position.y = s2Len;

            if ((cfg.fairing_shape === 'needle' || cfg.fairing_shape === 'pitot') && side === 1) {{
                const spike = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.07, 2.6, 12), pipeMat);
                spike.position.y = noseH + 1.3;
                halfMesh.add(spike);
            }}
            s2Group.add(halfMesh);
            fairingHalves.push({{ mesh: halfMesh, side: side, detached: false, vx: 0, vy: 0, rotZ: 0 }});
        }}
    }}

    // RCS コールドガス・パルススラスター
    const rcsCones = [];
    const rcsMat = new THREE.MeshBasicMaterial({{ color: 0xe0f2fe, transparent: true, opacity: 0.0, blending: THREE.AdditiveBlending, depthWrite: false }});
    for(let side of [-1, 1]) {{
        const rcsJet = new THREE.Mesh(new THREE.ConeGeometry(0.35, 2.8, 16), rcsMat.clone());
        rcsJet.rotation.z = side * (Math.PI / 2);
        rcsJet.position.set(side * 2.5, s2Len - 0.8, 0);
        s2Group.add(rcsJet);
        rcsCones.push({{ mesh: rcsJet, side: side, isS1: false }});

        const s1Rcs = new THREE.Mesh(new THREE.ConeGeometry(0.35, 2.8, 16), rcsMat.clone());
        s1Rcs.rotation.z = side * (Math.PI / 2);
        s1Rcs.position.set(side * 2.5, s1Len - 0.6, 0);
        s1Group.add(s1Rcs);
        rcsCones.push({{ mesh: s1Rcs, side: side, isS1: true }});
    }}

    // =========================================================================
    // ✨ エンジン噴出口直結・高輝度スパーク（火花）＆ 煙パーティクルエンジン
    // =========================================================================
    function createOrganicCloudTexture() {{
        const c = document.createElement('canvas'); c.width = 128; c.height = 128;
        const ctx = c.getContext('2d');
        for(let i=0; i<7; i++) {{
            const ox = 64 + (Math.random()-0.5)*28;
            const oy = 64 + (Math.random()-0.5)*28;
            const rad = 32 + Math.random()*22;
            const g = ctx.createRadialGradient(ox, oy, 2, ox, oy, rad);
            g.addColorStop(0, 'rgba(255,255,255,0.4)');
            g.addColorStop(0.5, 'rgba(225,232,240,0.18)');
            g.addColorStop(1, 'rgba(160,175,190,0)');
            ctx.fillStyle = g; ctx.fillRect(0,0,128,128);
        }}
        return new THREE.CanvasTexture(c);
    }}

    function createSparkStreakTexture() {{
        const c = document.createElement('canvas'); c.width = 64; c.height = 64;
        const ctx = c.getContext('2d');
        const g = ctx.createRadialGradient(32,32,1, 32,32,30);
        g.addColorStop(0, 'rgba(255,255,255,1)');
        g.addColorStop(0.35, 'rgba(255,220,120,0.95)');
        g.addColorStop(0.7, 'rgba(255,100,20,0.5)');
        g.addColorStop(1, 'rgba(255,40,0,0)');
        ctx.fillStyle = g; ctx.fillRect(0,0,64,64);
        return new THREE.CanvasTexture(c);
    }}

    const cloudTex = createOrganicCloudTexture();
    const sparkTex = createSparkStreakTexture();

    // 煙パーティクルプール
    const P_MAX = 1800;
    const pool = [];
    const pGroup = new THREE.Group(); scene.add(pGroup);
    for(let i=0; i<P_MAX; i++) {{
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({{ map: cloudTex, transparent: true, opacity: 0, depthWrite: false }}));
        sp.visible = false; pGroup.add(sp);
        pool.push({{ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 5, o: 0.8, rotSpd: 0 }});
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

    // 🔥 エンジン噴出口専用スパーク（火花）プール
    const SPARK_MAX = 700;
    const sparkPool = [];
    const sparkGroup = new THREE.Group(); scene.add(sparkGroup);
    for(let i=0; i<SPARK_MAX; i++) {{
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({{
            map: sparkTex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false
        }}));
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

    // RUD爆発エフェクト
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
        new THREE.ConeGeometry(0.35, 0.9, 16, 1, true),
        new THREE.BoxGeometry(0.25, 2.4, 0.25)
    ];

    for(let i=0; i<DEBRIS_MAX; i++) {{
        const deb = new THREE.Mesh(debGeos[i % debGeos.length], (i%3===0) ? s1Mat : darkSteelMat);
        deb.visible = false; debrisGroup.add(deb);
        debrisPool.push({{ mesh: deb, active: false, vx: 0, vy: 0, vz: 0, rx: 0, ry: 0, isBurning: (i % 2 === 0) }});
    }}

    let shockwaveAge = 0;
    function triggerPhotorealRUD(x, y, vxBase, vyBase) {{
        shockwaveRing.visible = true;
        shockwaveRing.position.set(x, y, 0);
        shockwaveRing.scale.set(1, 1, 1);
        shockwaveRing.material.opacity = 0.95;
        shockwaveAge = 1;

        for(let k=0; k<95; k++) {{
            const ang = Math.random() * Math.PI * 2;
            const phi = (Math.random() - 0.5) * Math.PI;
            const spd = 0.4 + Math.random() * 2.8;
            const col = (k < 25) ? 0xffffff : (k < 65 ? 0xff7700 : 0xdc2626);
            emitParticle(
                x + (Math.random()-0.5)*5, y + (Math.random()-0.5)*10, (Math.random()-0.5)*5,
                vxBase*0.02 + Math.cos(ang)*Math.cos(phi)*spd,
                vyBase*0.02 + Math.sin(phi)*spd + 0.15,
                Math.sin(ang)*Math.cos(phi)*spd,
                8.0, 68.0, 55 + Math.random()*35, 0.95, col, true
            );
        }}
        for(let k=0; k<120; k++) {{
            const ang = Math.random() * Math.PI * 2;
            const spd = 0.5 + Math.random() * 3.4;
            const isSoot = (k % 2 === 0);
            emitParticle(
                x + (Math.random()-0.5)*8, y + (Math.random()-0.5)*14, (Math.random()-0.5)*8,
                vxBase*0.02 + Math.cos(ang)*spd,
                vyBase*0.02 + (Math.random()-0.3)*spd,
                (Math.random()-0.5)*spd,
                12.0, 95.0, 110 + Math.random()*50, isSoot ? 0.88 : 0.75,
                isSoot ? 0x18181b : 0xf1f5f9, false
            );
        }}
        for(let i=0; i<DEBRIS_MAX; i++) {{
            const d = debrisPool[i];
            d.active = true; d.mesh.visible = true;
            d.mesh.position.set(x + (Math.random()-0.5)*4, y + (Math.random()-0.5)*14, (Math.random()-0.5)*4);
            const angle = Math.random() * Math.PI * 2;
            const spd = 6.0 + Math.random() * 28.0;
            d.vx = (vxBase * 0.04) + Math.cos(angle) * spd;
            d.vy = (vyBase * 0.04) + Math.sin(angle) * spd;
            d.vz = (Math.random() - 0.5) * spd * 1.6;
            d.rx = (Math.random()-0.5)*0.5; d.ry = (Math.random()-0.5)*0.5;
        }}
    }}

    function drawOrbitMap(altKm, dRangeKm, exploded) {{
        octx.clearRect(0, 0, 265, 90);
        octx.beginPath(); octx.arc(132, 240, 185, Math.PI, 0); octx.strokeStyle = '#1e293b'; octx.lineWidth = 3; octx.stroke();
        octx.beginPath(); octx.arc(132, 240, 215, Math.PI, 0); octx.strokeStyle = 'rgba(56, 189, 248, 0.25)'; octx.lineWidth = 1; octx.setLineDash([4, 4]); octx.stroke(); octx.setLineDash([]);

        const px = 20 + Math.min(225, (dRangeKm / 1200.0) * 225);
        const py = 76 - Math.min(65, (altKm / 200.0) * 65);

        octx.beginPath(); octx.moveTo(20, 76); octx.quadraticCurveTo(px * 0.5, 76, px, py);
        octx.strokeStyle = exploded ? '#ef4444' : '#38bdf8'; octx.lineWidth = 2; octx.stroke();
        octx.fillStyle = exploded ? '#dc2626' : '#38bdf8';
        octx.beginPath(); octx.arc(px, py, exploded ? 6 : 4, 0, Math.PI * 2); octx.fill();
    }}

    // =========================================================================
    // 🎥 見切れゼロ保証！絶対重心ハードロック・トラッキングカメラ制御
    // =========================================================================
    const smoothOffset = new THREE.Vector3(42.0, 14.0, 82.0);
    const activeFocusWorld = new THREE.Vector3();
    let camShake = 0.0;

    function updateGimbalTracker(simT, elapsedSec, alt, pitch, stage, exploded) {{
        if (cfg.is_preview) {{
            document.getElementById('cam-tag').innerText = "LIVE 3D BLUEPRINT PREVIEW: ORBITAL PAD INSPECTION";
            const orbitAng = elapsedSec * 0.28;
            const camR = 72.0;
            camera.position.set(Math.sin(orbitAng) * camR, 20.0 + Math.sin(elapsedSec * 0.4) * 8.0, Math.cos(orbitAng) * camR);
            camera.lookAt(0, 6.0 + (s1Len + s2Len) * 0.48, 0);
            return;
        }}

        // 飛行中のステージの正確な重心ワールド座標を取得（ラグゼロで絶対に見切れない）
        rocket.updateMatrixWorld(true);
        if (stage === 2) {{
            activeFocusWorld.set(0, s2Len * 0.45, 0);
            s2Group.localToWorld(activeFocusWorld);
        }} else {{
            activeFocusWorld.set(0, s1Len * 0.55, 0);
            rocket.localToWorld(activeFocusWorld);
        }}

        const desiredOffset = new THREE.Vector3();
        if (exploded) {{
            document.getElementById('cam-tag').innerText = "OPTICS: HIGH-SPEED DEBRIS TRACKING LOCK";
            desiredOffset.set(55.0, 22.0, 130.0);
        }} else if (simT < 0.0) {{
            document.getElementById('cam-tag').innerText = "PAD CAM 01: OLM & NOZZLE SPARK IGNITION TELEPHOTO";
            desiredOffset.set(36.0, -4.0, 74.0);
        }} else if (simT < 4.0) {{
            document.getElementById('cam-tag').innerText = "PAD PERIMETER: TOWER CLEARANCE TRACKER";
            desiredOffset.set(-42.0, 8.0, 95.0);
        }} else if (alt < 22.0) {{
            document.getElementById('cam-tag').innerText = "COASTAL KINETO TRACKER (2400mm APO)";
            desiredOffset.set(-38.0, -14.0, 88.0);
        }} else if (alt < 85.0) {{
            document.getElementById('cam-tag').innerText = "WB-57 HIGH-ALTITUDE OPTICAL CHASE";
            desiredOffset.set(-35.0, -8.0, 82.0);
        }} else {{
            document.getElementById('cam-tag').innerText = "ORBITAL INSERTION LONG-RANGE TELESCOPE";
            desiredOffset.set(-28.0, 10.0, 72.0);
        }}

        // オフセットのみを滑らかに補間し、ベース座標はactiveFocusWorldに完全固定（見切れゼロ）
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
    // ⏱️ メインレンダリング＆ワールド座標完全分離アニメーションループ
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

        // ---------------------------------------------------------------------
        // 1. 外部ブースター完全ワールド座標切り離し (scene.attach で絶対に追従しない！)
        // ---------------------------------------------------------------------
        if (!p0.strapon && !boosterDetached && boosterUnits.length > 0 && !cfg.is_preview) {{
            boosterDetached = true;
            playPyroSepSound();
            eventLog.innerText = "> SIDE BOOSTER JETTISON (WORLD DETACHMENT)";
            announceWebcast("Side boosters have separated.");

            for(let b of boosterUnits) {{
                b.detached = true;
                // ブースターのノズル火炎を即座に消灯
                b.tips.forEach(t => {{ t.plume.visible = false; }});
                // 親のrocketからscene直下へワールド座標を維持したまま完全デタッチ
                scene.attach(b.mesh);
                const outX = Math.cos(b.angle);
                const outZ = Math.sin(b.angle);
                // ロケット進行方向より少し遅い速度＋外側への分離推力を付与
                b.vx = ux * (vel * 0.065) + perpX * outX * 6.5;
                b.vy = uy * (vel * 0.065) + perpY * outX * 6.5 - 4.0;
                b.vz = outZ * 6.5;
                b.rx = outZ * 0.85;
                b.rz = -outX * 0.85;

                b.mesh.getWorldPosition(tempTipPos);
                for(let k=0; k<8; k++) {{
                    emitParticle(tempTipPos.x, tempTipPos.y, tempTipPos.z, outX*0.8, 0.2, outZ*0.8, 2.5, 11.0, 35, 0.85, 0xffffff, true);
                }}
            }}
        }}
        if (boosterDetached) {{
            for(let b of boosterUnits) {{
                b.mesh.position.x += b.vx * 0.016;
                b.mesh.position.y += b.vy * 0.016;
                b.mesh.position.z += b.vz * 0.016;
                b.vy -= 9.8 * 0.016 * 1.4;
                b.mesh.rotation.x += b.rx * 0.016;
                b.mesh.rotation.z += b.rz * 0.016;
            }}
        }}

        // ---------------------------------------------------------------------
        // 2. 第1段ホットステージング ＆ ワールド座標完全切り離し
        // ---------------------------------------------------------------------
        if (p0.stage === 2 && !stage1Detached && !cfg.is_preview) {{
            stage1Detached = true;
            playPyroSepSound();
            eventLog.innerText = "> STAGE 1 SEPARATION & STAGE 2 IGNITION";
            announceWebcast("Stage separation confirmed. Second stage ignition.");

            // 第1段エンジン火炎を消灯し、第2段エンジン火炎＆カラーを点灯
            s1NozzleTips.forEach(t => {{ t.plume.visible = false; }});
            s2NozzleTips.forEach(t => {{ t.plume.visible = true; }});
            plumeShaderMat.uniforms.uMidColor.value.setHex(cfg.s2_flame_hex);
            plumeShaderMat.uniforms.uOuterColor.value.setHex(cfg.s2_outer_hex);

            // 第1段をscene直下へ完全デタッチ
            scene.attach(s1Group);
            s1Vel.vx = ux * (vel * 0.068) - ux * 5.0;
            s1Vel.vy = uy * (vel * 0.068) - uy * 5.0;
            s1Vel.rotVel = 0.45;

            s2Group.getWorldPosition(tempTipPos);
            for(let k=0; k<28; k++) {{
                const ang = (k / 28) * Math.PI * 2;
                emitParticle(
                    tempTipPos.x, tempTipPos.y, tempTipPos.z,
                    Math.cos(ang)*1.6, (Math.random()-0.5)*0.4, Math.sin(ang)*1.6,
                    2.8, 16.0, 30, 0.9, cfg.s2_flame_hex, true
                );
            }}
        }}
        if (stage1Detached) {{
            s1Group.position.x += s1Vel.vx * 0.016;
            s1Group.position.y += s1Vel.vy * 0.016;
            s1Vel.vy -= 9.8 * 0.016 * 1.2;
            s1Group.rotation.z += s1Vel.rotVel * 0.016;
        }}

        // ---------------------------------------------------------------------
        // 3. フェアリング 2分割クラムシェル ワールド座標完全切り離し
        // ---------------------------------------------------------------------
        if (!p0.fairing && !fairingDetached && fairingHalves.length > 0 && !cfg.is_preview) {{
            fairingDetached = true;
            playPyroSepSound();
            eventLog.innerText = "> FAIRING JETTISON & PAYLOAD DEPLOYED";
            announceWebcast("Fairing separation confirmed.");
            for(let fh of fairingHalves) {{
                fh.detached = true;
                scene.attach(fh.mesh);
                fh.vx = ux * (vel * 0.072) + perpX * fh.side * 8.0;
                fh.vy = uy * (vel * 0.072) + perpY * fh.side * 8.0 - 2.0;
                fh.rotZ = -fh.side * 1.2;
            }}
        }}
        if (fairingDetached) {{
            for(let fh of fairingHalves) {{
                fh.mesh.position.x += fh.vx * 0.016;
                fh.mesh.position.y += fh.vy * 0.016;
                fh.vy -= 9.8 * 0.016 * 0.9;
                fh.mesh.rotation.z += fh.rotZ * 0.016;
            }}
        }}

        // ---------------------------------------------------------------------
        // 4. エンジンノズル開口部からの直接スパーク（火花）シャワー ＆ 排気煙放出
        // ---------------------------------------------------------------------
        if (p0.thrust && !p0.exploded && !cfg.is_preview) {{
            const vacFactor = Math.min(1.0, alt / 65.0);
            plumeShaderMat.uniforms.uVacFactor.value = vacFactor;

            // 現在燃焼中の全エンジンノズル開口部リストを集計
            const activeTips = (p0.stage === 1) ? [...s1NozzleTips] : [...s2NozzleTips];
            if (p0.stage === 1 && !boosterDetached) {{
                activeTips.push(...boosterNozzleTips);
            }}
            const curSparkHex = (p0.stage === 1) ? cfg.spark_hex : cfg.s2_spark_hex;

            for(let tObj of activeTips) {{
                tObj.plume.visible = true;
                tObj.node.getWorldPosition(tempTipPos);

                // 各エンジンノズル開口部から直接飛び散る高輝度スパークシャワー！
                for(let spk=0; spk<3; spk++) {{
                    const spreadX = (Math.random() - 0.5) * 0.45;
                    const spreadZ = (Math.random() - 0.5) * 0.45;
                    const jetSpd = 1.6 + Math.random() * 1.8;
                    emitNozzleSpark(
                        tempTipPos.x + (Math.random()-0.5)*0.2,
                        tempTipPos.y + (Math.random()-0.5)*0.2,
                        tempTipPos.z + (Math.random()-0.5)*0.2,
                        -ux * jetSpd + spreadX,
                        -uy * jetSpd + (Math.random()-0.5)*0.3,
                        spreadZ,
                        0.45 + Math.random()*0.45,
                        10 + Math.floor(Math.random()*12),
                        (Math.random() < 0.4) ? 0xffffff : curSparkHex
                    );
                }}

                // 大気圏内では各ノズル直下から直接ジェット白煙トレイルを放出
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

            // TVC ジンバル微細首振り
            const gimbalAngle = Math.sin(now * 0.016) * 0.04;
            s1Engines.rotation.z = gimbalAngle;
            s2Engines.rotation.z = gimbalAngle;
        }} else {{
            s1NozzleTips.forEach(t => {{ t.plume.visible = false; }});
            s2NozzleTips.forEach(t => {{ t.plume.visible = false; }});
            boosterNozzleTips.forEach(t => {{ t.plume.visible = false; }});
            engineBounceLight.intensity = 0.0;
        }}

        // RCS パルス噴射更新
        const pitchRate = Math.abs(pitch - prevPitch);
        prevPitch = pitch;
        let rcsFiring = false;
        for(let rcs of rcsCones) {{
            if (rcs.isS1) {{
                const activeS1Rcs = (stage1Detached && rcs.side === 1);
                rcs.mesh.material.opacity = activeS1Rcs ? (0.55 + Math.random()*0.35) : 0.0;
                if (activeS1Rcs) rcsFiring = true;
            }} else {{
                const pulseActive = (!cfg.is_preview && simT > 2.0 && (pitchRate > 0.0002 || alt > 35.0) && Math.sin(now * 0.025 + rcs.side) > 0.55);
                rcs.mesh.material.opacity = pulseActive ? (0.65 + Math.random()*0.3) : 0.0;
                if (pulseActive) rcsFiring = true;
            }}
        }}
        document.getElementById('hud-rcs').innerText = rcsFiring ? "PULSING (N2 GAS)" : "NOMINAL";
        document.getElementById('hud-rcs').style.color = rcsFiring ? "#34d399" : "#38bdf8";

        // カメラ追尾（見切れゼロ）
        updateGimbalTracker(simT, elapsedSec, alt, pitch, p0.stage, p0.exploded);
        drawOrbitMap(alt, dRangeKm, p0.exploded);

        // 💥 RUD 爆発トリガー
        if (p0.exploded && !explodedTriggered) {{
            explodedTriggered = true;
            rocket.visible = false;
            s1Group.visible = false;
            camShake = 2.5;
            flashOverlay.style.opacity = '0.95';
            setTimeout(() => {{ flashOverlay.style.opacity = '0.0'; }}, 140);

            playExplosionSound();
            triggerPhotorealRUD(activeFocusWorld.x, activeFocusWorld.y, p0.v * Math.cos(p0.pitch), p0.v * Math.sin(p0.pitch));

            rudBanner.style.display = 'block';
            rudDesc.innerText = failMessage;
            eventLog.innerText = "> CRITICAL ANOMALY: LOSS OF VEHICLE";
            eventLog.style.color = "#ef4444";
            announceWebcast("Anomaly detected on the vehicle. Loss of telemetry.");
            document.getElementById('tv-stage-badge').innerText = "VEHICLE LOSS (RUD)";
            document.getElementById('tv-stage-badge').style.color = "#ef4444";
            document.getElementById('comm-status').innerText = "SIGNAL LOST";
            document.getElementById('comm-status').style.color = "#ef4444";
        }}

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

        // カウントダウン極低温ボイルオフ蒸気 ＆ T-3秒エンジンROFI点火スパークシャワー
        if (simT < 0.0) {{
            const sec = Math.ceil(Math.abs(simT));
            document.getElementById('tv-timer').innerText = cfg.is_preview ? "PAD PREVIEW" : `T- 00:0${{sec}}.0`;
            emitParticle(rx + 1.25, ry + 6.0 + s1Len * 0.85, 0, 0.25, 0.04, 0, 0.9, 4.2, 45, 0.35, 0xffffff, false);

            // T-4.5秒からノズル直下でROFI点火イグナイター火花がバチバチ散り始める
            if (simT >= -4.5 && !p0.exploded && !cfg.is_preview) {{
                for(let tObj of s1NozzleTips) {{
                    tObj.node.getWorldPosition(tempTipPos);
                    for(let spk=0; spk<4; spk++) {{
                        emitNozzleSpark(
                            tempTipPos.x, tempTipPos.y, tempTipPos.z,
                            (Math.random()-0.5)*0.9, -0.8 - Math.random()*1.2, (Math.random()-0.5)*0.9,
                            0.5, 14, 0xfde047
                        );
                    }}
                }}
            }}

            if (simT >= -3.0 && !p0.exploded && !cfg.is_preview) {{
                camShake = 0.25;
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
                eventLog.innerText = "> LIFTOFF! TOWER CLEARED";
                announceWebcast("Liftoff. Tower cleared.");
                if (rumbleGain) rumbleGain.gain.setTargetAtTime(0.95, actx.currentTime, 0.1);
                if (crackleGain) crackleGain.gain.setTargetAtTime(0.55, actx.currentTime, 0.1);
            }}
        }}

        // 煙パーティクル更新
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

        // 火花スパーク更新
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
if launch_clicked:
    st.markdown("---")
    st.markdown("### 📋 フライトテレメトリ詳細レポート")
    if error_msg:
        st.error(f"⚠️ **ミッション異常終了 (RUD)**: {error_msg}")
    else:
        st.success("🎉 **ミッション完全成功 (SECO & LEO Insertion)**: 全段燃焼および分離シーケンスが正常に推移し、第2段オービターが低軌道投入条件に到達しました。")
