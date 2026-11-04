import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbital Architect: ロケット開発管制室", layout="wide")

st.title("🚀 Orbital Architect - 超シビア軌道投入シミュレーター")
st.markdown("部品と燃料比、打ち上げ角度をミリ単位で調整し、地球低軌道（高度200km / 第一宇宙速度 7.8km/s）へペイロードを投入せよ。")

# --- パーツデータベース ---
ENGINES = {
    "Merlin-1D (ケロシン/大気圏向)": {"thrust_sl": 845, "thrust_vac": 914, "isp_sl": 282, "isp_vac": 311, "mass": 0.47, "type": "RP1"},
    "Raptor-2 (メタン/高出力)": {"thrust_sl": 2250, "thrust_vac": 2500, "isp_sl": 327, "isp_vac": 350, "mass": 1.6, "type": "CH4"},
    "LE-9 (液体水素/高燃費・重)": {"thrust_sl": 1200, "thrust_vac": 1471, "isp_sl": 330, "isp_vac": 425, "mass": 2.4, "type": "LH2"},
    "RL-10 (真空専用・大気圏内破損リスク)": {"thrust_sl": 40, "thrust_vac": 110, "isp_sl": 150, "isp_vac": 465, "mass": 0.3, "type": "LH2_VAC"}
}

MATERIALS = {
    "アルミ・リチウム合金 (標準)": {"dry_ratio": 0.07, "max_q_limit": 45.0, "max_g": 6.0},
    "カーボン複合材 (超軽量・熱に弱い)": {"dry_ratio": 0.045, "max_q_limit": 32.0, "max_g": 5.0},
    "高強度ステンレス (激重・超頑丈)": {"dry_ratio": 0.11, "max_q_limit": 80.0, "max_g": 9.0}
}

# --- UI: 設計パート ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔧 第1段（ブースター）設計")
    s1_engine = st.selectbox("第1段エンジン", list(ENGINES.keys()), index=1)
    s1_eng_count = st.slider("第1段エンジン基数", 1, 9, 3)
    s1_fuel = st.slider("第1段 推進剤質量 (トン)", 20.0, 400.0, 180.0, step=5.0)
    s1_mat = st.selectbox("第1段 タンク材質", list(MATERIALS.keys()), index=0)

with col2:
    st.subheader("🛰️ 第2段（オービター）＆衛星")
    s2_engine = st.selectbox("第2段エンジン", list(ENGINES.keys()), index=3)
    s2_eng_count = st.slider("第2段エンジン基数", 1, 3, 1)
    s2_fuel = st.slider("第2段 推進剤質量 (トン)", 5.0, 100.0, 35.0, step=1.0)
    s2_mat = st.selectbox("第2段 タンク材質", list(MATERIALS.keys()), index=1)
    payload_mass = st.slider("ペイロード（人工衛星）質量 (トン)", 0.5, 20.0, 3.0, step=0.5)

with col3:
    st.subheader("📐 飛行プログラム（誘導制御）")
    turn_start_alt = st.slider("重力ターン開始高度 (km)", 1.0, 20.0, 5.0, step=0.5)
    turn_end_alt = st.slider("水平飛行移行高度 (km)", 50.0, 180.0, 110.0, step=5.0)
    throttle_maxq = st.slider("Max-Q通過時のスロットル絞り (%)", 40, 100, 75)
    
    # 簡易スペック計算表示
    e1 = ENGINES[s1_engine]
    e2 = ENGINES[s2_engine]
    m1_dry = s1_fuel * MATERIALS[s1_mat]["dry_ratio"] + (e1["mass"] * s1_eng_count)
    m2_dry = s2_fuel * MATERIALS[s2_mat]["dry_ratio"] + (e2["mass"] * s2_eng_count)
    
    total_mass_s2 = s2_fuel + m2_dry + payload_mass
    total_mass_s1 = s1_fuel + m1_dry + total_mass_s2
    
    twr_s1 = (e1["thrust_sl"] * s1_eng_count) / (total_mass_s1 * 9.80665)
    dv_s1 = e1["isp_sl"] * 9.80665 * np.log(total_mass_s1 / (total_mass_s1 - s1_fuel))
    dv_s2 = e2["isp_vac"] * 9.80665 * np.log(total_mass_s2 / (total_mass_s2 - s2_fuel))
    total_dv = dv_s1 + dv_s2

    st.markdown("---")
    st.metric("総質量 / 初期TWR (1.2〜1.6推奨)", f"{total_mass_s1:.1f} t", f"TWR: {twr_s1:.2f}")
    st.metric("理論総 ΔV (目標: 9,300 m/s以上)", f"{total_dv:.0f} m/s", f"1段:{dv_s1:.0f} / 2段:{dv_s2:.0f}")

# --- 物理シミュレーション計算 ---
def run_simulation():
    dt = 0.5  # 0.5秒刻み
    g0 = 9.80665
    R_earth = 6371000.0
    
    x, y = 0.0, R_earth  # 地球中心からの座標
    vx, vy = 0.0, 0.0
    stage = 1
    fuel_rem = s1_fuel * 1000.0
    
    history = []
    status = "飛行中"
    fail_reason = None

    # 第1段で真空用ノズルを使った場合のペナルティ判定
    if e1["type"] == "LH2_VAC":
        return [], "大気圏内で真空専用ノズルを使用したため、発射直後にノズルが過膨張で爆散しました！"
    if twr_s1 <= 1.02:
        return [], f"推力重量比(TWR: {twr_s1:.2f})が不足しており、発射台から浮上できません！"

    for step in range(1600): # 最大800秒
        t = step * dt
        r = np.sqrt(x**2 + y**2)
        alt = r - R_earth
        v = np.sqrt(vx**2 + vy**2)
        
        if alt < 0:
            status = "墜落"
            fail_reason = f"T+{t:.0f}秒: 推力または速度不足により高度0mへ墜落しました。"
            break

        # 大気密度モデル (指数減衰)
        rho = 1.225 * np.exp(-alt / 7500.0) if alt < 120000 else 0.0
        q = 0.5 * rho * (v**2) / 1000.0  # 動圧 (kPa)

        # ステージ管理と質量・推力計算
        if stage == 1:
            if fuel_rem <= 0:
                stage = 2
                fuel_rem = s2_fuel * 1000.0
            else:
                cur_mass = (m1_dry + total_mass_s2) * 1000.0 + fuel_rem
                # 高度によるIspと推力の補間
                atm_factor = np.exp(-alt / 7500.0)
                isp = e1["isp_vac"] - (e1["isp_vac"] - e1["isp_sl"]) * atm_factor
                thrust = (e1["thrust_vac"] - (e1["thrust_vac"] - e1["thrust_sl"]) * atm_factor) * s1_eng_count * 1000.0
                
                # Max-Q付近のスロットル制御
                if 8000 < alt < 16000:
                    thrust *= (throttle_maxq / 100.0)
                mdot = thrust / (isp * g0)
                fuel_rem -= mdot * dt

        if stage == 2:
            if fuel_rem <= 0:
                thrust = 0.0
                cur_mass = (m2_dry + payload_mass) * 1000.0
            else:
                cur_mass = (m2_dry + payload_mass) * 1000.0 + fuel_rem
                atm_factor = np.exp(-alt / 7500.0)
                isp = e2["isp_vac"] - (e2["isp_vac"] - e2["isp_sl"]) * atm_factor
                thrust = (e2["thrust_vac"] - (e2["thrust_vac"] - e2["thrust_sl"]) * atm_factor) * s2_eng_count * 1000.0
                mdot = thrust / (isp * g0)
                fuel_rem -= mdot * dt

        # ピッチ角（重力ターン）の計算: 局所水平線に対する角度
        alt_km = alt / 1000.0
        if alt_km < turn_start_alt:
            pitch_deg = 90.0
        elif alt_km < turn_end_alt:
            prog = (alt_km - turn_start_alt) / (turn_end_alt - turn_start_alt)
            pitch_deg = 90.0 * (1.0 - (prog ** 0.85))
        else:
            pitch_deg = 0.0

        # 地球中心からの角度
        theta = np.arctan2(x, y)
        # ロケットの推力方向ベクトル
        pitch_rad = np.radians(pitch_deg)
        dir_x = np.sin(theta) * np.sin(pitch_rad) + np.cos(theta) * np.cos(pitch_rad)
        dir_y = np.cos(theta) * np.sin(pitch_rad) - np.sin(theta) * np.cos(pitch_rad)

        # 空気抵抗
        drag_area = 12.0 if stage == 1 else 5.0
        drag_force = 0.5 * rho * (v**2) * 0.35 * drag_area
        if v > 0:
            drag_x = -drag_force * (vx / v)
            drag_y = -drag_force * (vy / v)
        else:
            drag_x, drag_y = 0.0, 0.0

        # 重力
        g_cur = g0 * ((R_earth / r) ** 2)
        grav_x = -cur_mass * g_cur * np.sin(theta)
        grav_y = -cur_mass * g_cur * np.cos(theta)

        # 合力と加速度
        fx = thrust * dir_x + drag_x + grav_x
        fy = thrust * dir_y + drag_y + grav_y
        ax = fx / cur_mass
        ay = fy / cur_mass
        acc_g = np.sqrt((thrust * dir_x + drag_x)**2 + (thrust * dir_y + drag_y)**2) / (cur_mass * g0)

        # 破壊判定（シビア要素）
        mat_limit_q = MATERIALS[s1_mat if stage == 1 else s2_mat]["max_q_limit"]
        mat_limit_g = MATERIALS[s1_mat if stage == 1 else s2_mat]["max_g"]

        if q > mat_limit_q:
            fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): 動圧({q:.1f} kPa)が機体構造限界({mat_limit_q} kPa)を超え、空中分解しました！"
            history.append({"t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g, "stage": stage, "exploded": True})
            break
        if acc_g > mat_limit_g:
            fail_reason = f"T+{t:.0f}秒: 過剰なG({acc_g:.1f} G)によりタンク隔壁が圧壊しました！(限界: {mat_limit_g} G)"
            history.append({"t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g, "stage": stage, "exploded": True})
            break
        if alt_km < 60 and v > 2600:
            fail_reason = f"T+{t:.0f}秒 (高度{alt_km:.1f}km): 低高度で加速しすぎたため、空力加熱によりフェアリングが融解しました！"
            history.append({"t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g, "stage": stage, "exploded": True})
            break

        # 位置と速度の更新
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt

        if step % 4 == 0: # 2秒おきに記録
            history.append({"t": t, "x": x, "y": y, "alt": alt_km, "v": v, "q": q, "g": acc_g, "stage": stage, "exploded": False, "thrust": thrust > 0})

        # 軌道投入成功判定 (高度180km以上、水平速度7750m/s以上、垂直速度が安定)
        v_radial = (vx * np.sin(theta) + vy * np.cos(theta))
        v_tangent = (vx * np.cos(theta) - vy * np.sin(theta))
        if alt_km >= 180.0 and v_tangent >= 7750.0 and abs(v_radial) < 400.0:
            status = "軌道投入成功"
            break

    if not fail_reason and status != "軌道投入成功":
        fail_reason = f"燃料切れ後、第一宇宙速度(7,800m/s)に達せず弾道飛行で終わりました。(最高到達速度: {v:.0f} m/s, 最終高度: {alt_km:.1f} km)"

    return history, fail_reason

# --- 発射ボタンと3Dビューワー ---
if st.button("🔥 イグニッション・発射シークエンス開始", use_container_width=True, type="primary"):
    traj_data, error_msg = run_simulation()
    
    if len(traj_data) == 0:
        st.error(f"❌ 発射失敗: {error_msg}")
    else:
        if error_msg:
            st.warning(f"⚠️ ミッション失敗: {error_msg}")
        else:
            st.success("🎉 ミッション成功！ペイロードは安定した地球低軌道（LEO）へ投入されました！")

        # Three.jsによる3D宇宙＆軌道ビジュアライザーの埋め込み
        traj_json = json.dumps(traj_data)
        html_code = f"""
        <div style="position: relative; width: 100%; height: 520px; background: #000; border-radius: 12px; overflow: hidden; font-family: monospace;">
            <div id="canvas-container" style="width: 100%; height: 100%;"></div>
            <div style="position: absolute; top: 15px; left: 15px; color: #00ffcc; background: rgba(0,20,40,0.8); padding: 12px; border: 1px solid #00ffcc; border-radius: 8px;">
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 6px;">TELEMETRY DATA</div>
                <div id="hud-time">T+ 0.0 s</div>
                <div id="hud-alt">ALTITUDE : 0.0 km</div>
                <div id="hud-vel">VELOCITY : 0 m/s</div>
                <div id="hud-q">MAX-Q    : 0.0 kPa</div>
                <div id="hud-g">G-LOAD   : 1.0 G</div>
                <div id="hud-stage" style="color: #ffcc00; margin-top:4px;">STAGE 1 BURN</div>
            </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            const data = {traj_json};
            const container = document.getElementById('canvas-container');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 10, 50000000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            // スケール変換 (1 unit = 10km)
            const SCALE = 0.0001;
            const R_EARTH = 6371000 * SCALE;

            // 地球と大気層の描画
            const earthGeo = new THREE.SphereGeometry(R_EARTH, 64, 64);
            const earthMat = new THREE.MeshPhongMaterial({{ color: 0x1a4b8c, emissive: 0x051525, specular: 0x333333, shininess: 15 }});
            const earth = new THREE.Mesh(earthGeo, earthMat);
            scene.add(earth);

            const atmosGeo = new THREE.SphereGeometry(R_EARTH + (100000 * SCALE), 64, 64);
            const atmosMat = new THREE.MeshBasicMaterial({{ color: 0x4da6ff, transparent: true, opacity: 0.18, wireframe: false }});
            const atmos = new THREE.Mesh(atmosGeo, atmosMat);
            scene.add(atmos);

            // 光源と星空
            const light = new THREE.DirectionalLight(0xffffff, 1.3);
            light.position.set(1000, 1000, 2000);
            scene.add(light);
            scene.add(new THREE.AmbientLight(0x333333));

            // ロケット本体と炎
            const rocketGroup = new THREE.Group();
            const bodyGeo = new THREE.ConeGeometry(4, 16, 16);
            const bodyMat = new THREE.MeshBasicMaterial({{ color: 0xffffff }});
            const rocketMesh = new THREE.Mesh(bodyGeo, bodyMat);
            rocketGroup.add(rocketMesh);

            const flameGeo = new THREE.ConeGeometry(3, 12, 16);
            flameGeo.rotateX(Math.PI);
            flameGeo.translate(0, -12, 0);
            const flameMat = new THREE.MeshBasicMaterial({{ color: 0xff5500 }});
            const flameMesh = new THREE.Mesh(flameGeo, flameMat);
            rocketGroup.add(flameMesh);
            scene.add(rocketGroup);

            // 軌跡ライン
            const points = [];
            const lineMat = new THREE.LineBasicMaterial({{ color: 0x00ffcc }});
            const lineGeo = new THREE.BufferGeometry();
            const trajectoryLine = new THREE.Line(lineGeo, lineMat);
            scene.add(trajectoryLine);

            let idx = 0;
            function animate() {{
                requestAnimationFrame(animate);
                if (idx < data.length) {{
                    const pt = data[idx];
                    const rx = pt.x * SCALE;
                    const ry = pt.y * SCALE;

                    rocketGroup.position.set(rx, ry, 0);
                    points.push(new THREE.Vector3(rx, ry, 0));
                    lineGeo.setFromPoints(points);

                    // 進行方向へロケットを向ける
                    if (idx > 0) {{
                        const prev = data[idx - 1];
                        const angle = Math.atan2(pt.y - prev.y, pt.x - prev.x);
                        rocketGroup.rotation.z = angle - Math.PI / 2;
                    }}

                    flameMesh.visible = pt.thrust && !pt.exploded;
                    if (pt.exploded) {{
                        bodyMat.color.setHex(0xff0000);
                        rocketGroup.scale.set(3, 3, 3);
                    }}

                    // カメラ追従
                    camera.position.set(rx * 0.7, ry * 0.7 + 50, 450);
                    camera.lookAt(rx, ry, 0);

                    // HUD更新
                    document.getElementById('hud-time').innerText = `T+ ${{pt.t.toFixed(1)}} s`;
                    document.getElementById('hud-alt').innerText = `ALTITUDE : ${{pt.alt.toFixed(1)}} km`;
                    document.getElementById('hud-vel').innerText = `VELOCITY : ${{pt.v.toFixed(0)}} m/s`;
                    document.getElementById('hud-q').innerText = `MAX-Q    : ${{pt.q.toFixed(1)}} kPa`;
                    document.getElementById('hud-g').innerText = `G-LOAD   : ${{pt.g.toFixed(2)}} G`;
                    document.getElementById('hud-stage').innerText = pt.exploded ? "💥 CRITICAL FAILURE (EXPLODED)" : (pt.stage === 1 ? "🔥 STAGE 1 BURN" : (pt.thrust ? "🚀 STAGE 2 ORBITAL INSERTION" : "🛰️ MECO / COASTING"));

                    idx++;
                }}
                renderer.render(scene, camera);
            }}
            animate();
        </script>
        """
        components.html(html_code, height=540)
