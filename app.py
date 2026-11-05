import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect")
st.caption("※ IFT-5 Starship / Super Heavy タワーキャッチ完全追従シミュレーター")

# =========================================================================
# 🔬 推進剤・材料・パーツデータベース
# =========================================================================
PROPELLANTS = {
    "超高密度サブクール・メタロックス (CH4 / LOX) [Starship王道]": {
        "base_isp_sl": 338, "base_isp_vac": 382, "base_thrust": 2800, "density": 0.85, 
        "flame_hex": 0x60a5fa, "outer_hex": 0x1d4ed8, "spark_hex": 0x93c5fd, "risk": 0.0, "type": "methalox"
    },
    "高精製ロケットグレードケロシン (RP-1 / LOX) [Falcon 9]": {
        "base_isp_sl": 302, "base_isp_vac": 335, "base_thrust": 1950, "density": 1.03, 
        "flame_hex": 0xfef08a, "outer_hex": 0xea580c, "spark_hex": 0xfde047, "risk": 0.0, "type": "rp1"
    }
}

PUMP_CYCLES = {
    "フルフローステージド燃焼 (FFSC) [極限高圧]": {"isp_mod": 1.07, "thrust_mod": 1.42, "mass_mod": 1.22, "max_pressure_limit": 380, "cyc_id": "ffsc"}
}

MATERIALS = {
    "Austenitic 304L 冷間圧延鏡面ステンレス [Starship仕様]": {"base_dry_ratio": 0.065, "max_q_base": 130.0, "max_g_base": 12.5, "mat_id": "ss"}
}

AERO_WINGS = {
    "チタン鍛造極超音速グリッドフィン × 4基 (回収仕様)": {"lift_coeff": 0.12, "drag_penalty": 1.05, "mass": 1.2, "wing_id": "grid"}
}

FAIRINGS = {
    "Starship風 窓付き有人クルーノーズコーン": {"mass": 4.2, "cd": 0.22, "heat_limit": 2900, "shape_id": "starship_crew"}
}

# =========================================================================
# 🎛️ パラメータ設定タブ
# =========================================================================
tab1, tab2, tab3 = st.tabs([
    "🔥 第1段 Super Heavy ＆ タワーキャッチ設定", 
    "🛰️ 第2段 Starship オービター", 
    "🌊 発射場 ＆ ガイダンス"
])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        s1_prop = st.selectbox("推進剤", list(PROPELLANTS.keys()), index=0)
        s1_eng_count = st.slider("Raptor エンジン基数", 1, 33, 33)
    with c2:
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, 300, step=10)
        s1_fuel = st.slider("推進剤充填量 (トン)", 500.0, 4500.0, 3400.0, step=50.0)
    with c3:
        spacex_catch_enabled = st.checkbox("🦾 Mechazilla チョップスティック・タワーキャッチ (IFT-5完全再現)", value=True)
        st.info("※ 有効時、切り離し後のSuper Heavyが反転・再突入し、発射タワーのアームに挟まれてキャッチされるまで望遠カメラが密着追尾します。")

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        s2_eng_count = st.slider("Starship 真空Raptor基数", 1, 9, 6)
        s2_fuel = st.slider("第2段 推進剤量 (トン)", 100.0, 1500.0, 1200.0, step=10.0)
    with c2:
        payload_mass = st.slider("ペイロード質量 (トン)", 0.5, 150.0, 50.0, step=1.0)
        rcs_deadband = st.slider("4象限RCS 制御感度 (deg)", 0.2, 5.0, 1.0, step=0.1)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        water_flow_rate = st.slider("水冷デリュージ流量 (トン/秒)", 50, 500, 350, step=25)
        ignition_lead = st.slider("エンジン先行点火 (T-マイナス秒)", 2.0, 6.0, 3.8, step=0.1)
    with c2:
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.5, 10.0, 1.5, step=0.1)
        turn_end_alt = st.slider("重力ターン完了高度 (km)", 50.0, 200.0, 110.0, step=5.0)

# =========================================================================
# ⚙️ 物理演算 (Starship + Super Heavy タワーキャッチ軌道生成)
# =========================================================================
def run_simulation(preview_only=False):
    if preview_only:
        return [{
            "t": -10.0, "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0,
            "stage": 1, "exploded": False, "thrust": False, "pitch": 0.0, "mach": 0.0,
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False
        }], None

    dt = 0.5
    g0 = 9.80665
    history = []

    # カウントダウン
    for cd_step in range(21):
        t_cd = -10.0 + cd_step * 0.5
        history.append({
            "t": float(t_cd), "x": 0.0, "y": 0.0, "alt": 0.0, "v": 0.0, "q": 0.0, "g": 1.0,
            "stage": 1, "exploded": False, "thrust": bool(t_cd >= -ignition_lead),
            "pitch": 0.0, "mach": 0.0,
            "b_x": 0.0, "b_y": 0.0, "b_active": False, "b_pitch": 0.0, "b_thrust": False, "b_caught": False
        })

    x, y = 0.0, 0.0
    vx, vy = 0.0, 0.0
    stage = 1
    fuel_s1 = float(s1_fuel * 1000.0)
    fuel_s2 = float(s2_fuel * 1000.0)

    # ブースター（Super Heavy）独立運動変数
    b_x, b_y = 0.0, 0.0
    b_vx, b_vy = 0.0, 0.0
    b_active = False
    b_pitch = 0.0
    b_thrust = False
    b_caught = False

    for step in range(2400):
        t = float(step * dt)
        alt = float(y)
        alt_km = float(alt / 1000.0)
        v = float(np.sqrt(vx**2 + vy**2))
        mach = v / 340.0

        # 重力ターン
        if alt_km < turn_start_alt:
            target_pitch_deg = 90.0
        elif alt_km < turn_end_alt:
            prog = (alt_km - turn_start_alt) / (turn_end_alt - turn_start_alt)
            target_pitch_deg = 90.0 * (1.0 - (prog ** 0.62))
        else:
            target_pitch_deg = 0.0

        pitch_rad = float(np.radians(target_pitch_deg))
        visual_pitch = float(np.radians(90.0 - target_pitch_deg))

        # 第1段燃焼
        if stage == 1:
            thrust = 33 * 2800.0 * 1000.0 * 0.95
            total_mass = (s1_fuel + s2_fuel + 200.0 + payload_mass) * 1000.0
            fuel_s1 -= 12000.0 * dt

            # MECO ＆ ホットステージング
            if t >= 160.0 or fuel_s1 <= (s1_fuel * 1000.0 * 0.15):
                stage = 2
                thrust = 0.0
                if spacex_catch_enabled and not b_active:
                    b_active = True
                    b_x, b_y = float(x), float(y)
                    b_vx, b_vy = float(vx * 0.8), float(vy * 0.95)
                    b_pitch = visual_pitch

        # 第2段燃焼 (Starship)
        elif stage == 2:
            thrust = 6 * 2800.0 * 1000.0 * 0.95
            total_mass = (s2_fuel + 120.0 + payload_mass) * 1000.0
            fuel_s2 -= 3500.0 * dt
            if fuel_s2 <= 0:
                thrust = 0.0

        dir_x = float(np.cos(pitch_rad))
        dir_y = float(np.sin(pitch_rad))

        ax = (thrust * dir_x) / total_mass
        ay = (thrust * dir_y) / total_mass - g0

        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y = max(0.0, y + vy * dt)

        # 🦾 【重要】Super Heavy RTLS ＆ タワーキャッチ軌道計算
        if b_active and not b_caught:
            # 1. ブーストバック反転噴射 (高度65km以上で発射台へ逆噴射)
            if b_y > 60000.0 and b_vx > 0.0:
                b_pitch = 3.14159 # 180度反転
                b_thrust = True
                b_vx -= 28.0 * dt
                b_vy -= 4.0 * dt
            # 2. 空力降下 ＆ グリッドフィン操舵
            elif b_y > 3000.0:
                b_pitch = 3.14159 * 0.96
                b_thrust = False
                b_vy -= g0 * dt * 0.75 # 空気抵抗減速
                b_vx -= (b_vx * 0.03) * dt # 発射台(X=0)へ収束
            # 3. 着陸スイング燃焼 ＆ ホバリング (IFT-5実写通りの最終進入)
            elif b_y <= 3000.0 and b_y > 42.0:
                b_pitch = 3.14159 + np.clip(b_x / 800.0, -0.15, 0.15)
                b_thrust = True
                # アーム直前で速度をゼロにする急減速
                b_vy += 18.0 * dt
                b_vx *= 0.82
                b_x *= 0.94
            # 4. タワーキャッチ成立！(発射台高さ38mでピタリと保持)
            elif b_y <= 42.0:
                b_caught = True
                b_y = 38.0
                b_x = 0.0
                b_vx = 0.0
                b_vy = 0.0
                b_thrust = False
                b_pitch = 3.14159

            b_x += b_vx * dt
            b_y = max(38.0 if b_caught else 0.0, b_y + b_vy * dt)

        history.append({
            "t": t, "x": float(x), "y": float(y), "alt": float(y / 1000.0), "v": float(v),
            "q": float(0.5 * 1.225 * np.exp(-y/7400.0) * (v**2) / 1000.0) if y < 100000 else 0.0,
            "g": float(np.sqrt(ax**2 + (ay+g0)**2) / g0), "stage": int(stage), "exploded": False,
            "thrust": bool(thrust > 0), "pitch": float(visual_pitch), "mach": float(mach),
            "b_x": float(b_x), "b_y": float(b_y), "b_active": bool(b_active),
            "b_pitch": float(b_pitch), "b_thrust": bool(b_thrust), "b_caught": bool(b_caught)
        })

        if alt_km >= 160.0 and vx >= 7800.0:
            break

    return history, None

# 実行
traj_data, _ = run_simulation(preview_only=False)

cfg_json = json.dumps({
    "spacex_catch": bool(spacex_catch_enabled),
    "water_flow": float(water_flow_rate),
    "ignition_lead": float(ignition_lead),
    "rcs_deadband": float(rcs_deadband)
})
traj_json = json.dumps(traj_data)

# =========================================================================
# 📺 Three.js 4Kビューポート (チカチカ完全排除・タワーキャッチ密着追尾)
# =========================================================================
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        * {{ box-sizing: border-box; }}
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #020712; font-family: -apple-system, BlinkMacSystemFont, sans-serif; user-select: none; }}
        #canvas-main {{ width: 100vw; height: 100vh; display: block; position: absolute; top:0; left:0; z-index: 1; }}
        
        /* 🎥 望遠カメラ PiP 右上独立窓 (IFT-5 タワーキャッチ専任) */
        .pip-container {{ position: absolute; top: 52px; right: 20px; width: 350px; height: 210px; border: 2px solid #38bdf8; border-radius: 6px; z-index: 60; box-shadow: 0 10px 40px rgba(0,0,0,0.95); background: #01040a; overflow: hidden; }}
        #canvas-pip {{ width: 100%; height: 100%; display: block; }}
        .pip-tag {{ position: absolute; top: 6px; left: 8px; font-size: 9px; font-weight: 800; color: #fff; background: rgba(15, 23, 42, 0.9); padding: 3px 6px; border-radius: 2px; font-family: monospace; border-left: 2px solid #38bdf8; z-index: 65; }}
        .pip-alt {{ position: absolute; bottom: 6px; right: 8px; font-size: 10px; font-family: monospace; color: #38bdf8; font-weight: 700; background: rgba(15, 23, 42, 0.9); padding: 2px 6px; border-radius: 2px; z-index: 65; }}

        /* 🔝 トップバナー */
        .top-banner {{ position: absolute; top: 0; left: 0; width: 100%; height: 44px; background: rgba(2, 6, 16, 0.94); backdrop-filter: blur(16px); display: flex; align-items: center; justify-content: space-between; padding: 0 20px; border-bottom: 1px solid rgba(255,255,255,0.1); z-index: 20; color: #fff; font-family: monospace; font-size: 11px; }}
        
        /* 📊 ボトムテレメトリドック (下部バグ完全解消) */
        .hud-telemetry {{ position: absolute; bottom: 0; left: 0; width: 100%; height: 84px; background: linear-gradient(to top, rgba(2, 6, 16, 0.98) 0%, rgba(2, 6, 16, 0.85) 75%, transparent 100%); padding: 10px 24px; display: flex; align-items: center; justify-content: space-between; z-index: 20; color: #fff; }}
    </style>
</head>
<body>
    <canvas id="canvas-main"></canvas>

    <!-- 🎥 望遠カメラ PiP (Super Heavy 専用追尾) -->
    <div class="pip-container">
        <canvas id="canvas-pip"></canvas>
        <div id="pip-tag" class="pip-tag">CAM 02: TOWER TRACKER (IFT-5 CATCH)</div>
        <div id="pip-alt" class="pip-alt">BOOSTER: 0.0 km</div>
    </div>

    <div class="top-banner">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display:inline-block; width:8px; height:8px; background:#ef4444; border-radius:50%; box-shadow:0 0 10px #ef4444;"></span>
            <strong style="color:#fff; font-size:12px;">STARBASE LIVE 4K</strong> | <span id="cam-status" style="color:#38bdf8;">CAM 01: VEHICLE TRACKER</span>
        </div>
        <div>MECHAZILLA CATCH ARMS: <strong id="catch-status" style="color:#34d399;">READY & OPEN</strong></div>
    </div>

    <div class="hud-telemetry">
        <div>
            <div style="color:#38bdf8; font-size:10px; font-weight:700;">FLIGHT TIMER</div>
            <div id="tv-timer" style="font-size:28px; font-weight:900; font-family:monospace;">T- 00:10.0</div>
        </div>
        <div style="display:flex; gap:28px; border-left:1px solid rgba(255,255,255,0.15); padding-left:18px;">
            <div>
                <div style="font-size:9px; color:#94a3b8;">SPEED</div>
                <div id="tv-spd" style="font-size:16px; font-weight:800; font-family:monospace;">0 km/h</div>
            </div>
            <div>
                <div style="font-size:9px; color:#94a3b8;">ALTITUDE</div>
                <div id="tv-alt" style="font-size:16px; font-weight:800; font-family:monospace;">0.0 km</div>
            </div>
            <div>
                <div style="font-size:9px; color:#94a3b8;">SUPER HEAVY STATUS</div>
                <div id="tv-booster-status" style="font-size:14px; font-weight:800; font-family:monospace; color:#38bdf8;">ATTACHED TO CORE</div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const simData = {traj_json};
        const simCfg = {cfg_json};

        const canvasMain = document.getElementById('canvas-main');
        const canvasPip = document.getElementById('canvas-pip');

        // 音響
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null, rumble = null, crackle = null;
        function initSound() {{
            if (!actx) {{
                actx = new AudioCtx();
                const buf = actx.createBuffer(1, actx.sampleRate * 2, actx.sampleRate);
                const d = buf.getChannelData(0);
                for(let i=0; i<d.length; i++) d[i] = Math.random() * 2 - 1;

                const rSrc = actx.createBufferSource(); rSrc.buffer = buf; rSrc.loop = true;
                const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 55;
                rumble = actx.createGain(); rumble.gain.value = 0.001;
                rSrc.connect(lp); lp.connect(rumble); rumble.connect(actx.destination);
                rSrc.start(0);

                const cSrc = actx.createBufferSource(); cSrc.buffer = buf; cSrc.loop = true;
                const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 420; bp.Q.value = 3.5;
                crackle = actx.createGain(); crackle.gain.value = 0.001;
                cSrc.connect(bp); bp.connect(crackle); crackle.connect(actx.destination);
                cSrc.start(0);
            }}
            if (actx.state === 'suspended') actx.resume();
        }}
        ['click', 'touchstart', 'mousemove'].forEach(e => window.addEventListener(e, initSound, {{ once: true }}));

        // Three.js シーン
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x061121);

        // チラつき撲滅：logarithmicDepthBuffer 有効化
        const rendererMain = new THREE.WebGLRenderer({{ canvas: canvasMain, antialias: true, logarithmicDepthBuffer: true }});
        rendererMain.setSize(window.innerWidth, window.innerHeight);
        rendererMain.toneMapping = THREE.ACESFilmicToneMapping;
        rendererMain.toneMappingExposure = 1.35;

        const rendererPip = new THREE.WebGLRenderer({{ canvas: canvasPip, antialias: true, logarithmicDepthBuffer: true }});
        rendererPip.setSize(350, 210);
        rendererPip.toneMapping = THREE.ACESFilmicToneMapping;
        rendererPip.toneMappingExposure = 1.45;

        const cameraMain = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1.0, 500000);
        const cameraPip = new THREE.PerspectiveCamera(8.5, 350 / 210, 1.0, 500000);

        // ライティング
        const sun = new THREE.DirectionalLight(0xfffaed, 5.0);
        sun.position.set(5000, 9000, 6000);
        scene.add(sun);
        scene.add(new THREE.HemisphereLight(0x93c5fd, 0x1e293b, 1.2));

        // 大地・海面 (高度を明確に分離してZ-Fightingを完全防止)
        const ground = new THREE.Mesh(new THREE.PlaneGeometry(80000, 80000), new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.9 }}));
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = 0.0;
        scene.add(ground);

        const sea = new THREE.Mesh(new THREE.PlaneGeometry(120000, 120000), new THREE.MeshStandardMaterial({{ color: 0x072840, roughness: 0.1, metalness: 0.8 }}));
        sea.rotation.x = -Math.PI / 2;
        sea.position.set(15000, -2.0, 0);
        scene.add(sea);

        // =========================================================================
        // 🏗️ Mechazilla 発射台 ＆ チョップスティックアーム (実寸立体)
        // =========================================================================
        const towerGroup = new THREE.Group();
        towerGroup.position.set(-14.0, 0, 0);
        scene.add(towerGroup);

        const tower = new THREE.Mesh(new THREE.BoxGeometry(7.0, 145.0, 7.0), new THREE.MeshStandardMaterial({{ color: 0x1e242d, metalness: 0.9 }}));
        tower.position.y = 72.5;
        towerGroup.add(tower);

        // 🦾 チョップスティックアーム (キャッチ時に可動)
        const armLeft = new THREE.Mesh(new THREE.BoxGeometry(16.0, 2.2, 1.2), new THREE.MeshStandardMaterial({{ color: 0x334155, metalness: 0.9 }}));
        armLeft.position.set(8.0, 38.0, 3.8);
        towerGroup.add(armLeft);

        const armRight = new THREE.Mesh(new THREE.BoxGeometry(16.0, 2.2, 1.2), new THREE.MeshStandardMaterial({{ color: 0x334155, metalness: 0.9 }}));
        armRight.position.set(8.0, 38.0, -3.8);
        towerGroup.add(armRight);

        // =========================================================================
        // 🚀 ロケット本体 (Starship + Super Heavy)
        // =========================================================================
        const ssMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, metalness: 0.95, roughness: 0.15 }});
        const darkMat = new THREE.MeshStandardMaterial({{ color: 0x1f2937, metalness: 0.9 }});

        // 1. Starship (上段)
        const starship = new THREE.Group();
        const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 14.0, 36), ssMat);
        s2Body.position.y = 7.0; starship.add(s2Body);
        const nose = new THREE.Mesh(new THREE.ConeGeometry(1.2, 5.0, 36), ssMat);
        nose.position.y = 16.5; starship.add(nose);
        scene.add(starship);

        // 2. Super Heavy (第1段ブースター：完全に独立したオブジェクトとして配置)
        const booster = new THREE.Group();
        const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 22.0, 36), ssMat);
        s1Body.position.y = 11.0; booster.add(s1Body);

        // グリッドフィン × 4
        for(let i=0; i<4; i++) {{
            const gf = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.15, 1.2), darkMat);
            const a = (i/4) * Math.PI * 2;
            gf.position.set(Math.cos(a)*1.4, 20.5, Math.sin(a)*1.4);
            gf.rotation.y = -a;
            booster.add(gf);
        }}
        // キャッチ用受動ピン
        const catchPins = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 3.4, 16), darkMat);
        catchPins.rotation.z = Math.PI / 2;
        catchPins.position.set(0, 20.8, 0);
        booster.add(catchPins);

        // Raptor エンジンノズル群
        for(let i=0; i<9; i++) {{
            const r = (i === 0) ? 0 : 0.8;
            const a = (i/8) * Math.PI * 2;
            const n = new THREE.Mesh(new THREE.ConeGeometry(0.2, 1.0, 16), darkMat);
            n.position.set(Math.cos(a)*r, -0.5, Math.sin(a)*r);
            booster.add(n);
        }}
        scene.add(booster);

        // 火炎
        const flameGeo = new THREE.ConeGeometry(1.8, 16.0, 16);
        const flameMat = new THREE.MeshBasicMaterial({{ color: 0x60a5fa, transparent: true, opacity: 0.85 }});
        const boosterFlame = new THREE.Mesh(flameGeo, flameMat);
        boosterFlame.rotation.x = Math.PI;
        boosterFlame.position.y = -8.0;
        boosterFlame.visible = false;
        booster.add(boosterFlame);

        // 4象限RCSコールドガススラスター噴射口
        const rcsGroup = new THREE.Group();
        for(let a of [0, Math.PI/2, Math.PI, Math.PI*1.5]) {{
            const nozzle = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.3, 0.2), darkMat);
            nozzle.position.set(Math.cos(a)*1.25, 20.0, Math.sin(a)*1.25);
            rcsGroup.add(nozzle);
        }}
        booster.add(rcsGroup);

        // =========================================================================
        // ⏱️ アニメーション ＆ IFT-5タワーキャッチ密着カメラ追尾
        // =========================================================================
        const t0 = performance.now();
        const boosterWorldPos = new THREE.Vector3();

        function animate(now) {{
            requestAnimationFrame(animate);
            const t = (-10.0 + (now - t0) / 1000.0);

            let idx = 0;
            while(idx < simData.length - 1 && simData[idx + 1].t <= t) idx++;
            const p = simData[idx];

            // Starship 位置
            starship.position.set(p.x * 0.1, p.y * 0.1 + (p.stage === 1 ? 28.0 : 6.0), 0);
            starship.rotation.z = -p.pitch;

            // Super Heavy 位置 ＆ タワーキャッチ挙動
            if (!p.b_active) {{
                booster.position.set(p.x * 0.1, p.y * 0.1 + 6.0, 0);
                booster.rotation.z = -p.pitch;
                boosterFlame.visible = p.thrust;
            }} else {{
                // 【核心】独立した帰還座標で発射台へ進入
                booster.position.set(p.b_x * 0.1, p.b_y * 0.1 + 6.0, 0);
                booster.rotation.z = -p.b_pitch;
                boosterFlame.visible = p.b_thrust;
                boosterFlame.scale.set(1.0, p.b_y < 2000 ? 0.6 : 1.2, 1.0);

                // 🦾 チョップスティックアームが抱き込んでキャッチ！
                if (p.b_caught) {{
                    armLeft.rotation.y = 0.22;
                    armRight.rotation.y = -0.22;
                    document.getElementById('catch-status').innerText = "CAUGHT BY CHOPSTICKS!";
                    document.getElementById('catch-status').style.color = "#38bdf8";
                }}
            }}

            // 🎯 【重要】望遠カメラ (CAM 02) が帰還ブースターをタワーキャッチまで完全密着追尾
            if (p.b_active) {{
                booster.getWorldPosition(boosterWorldPos);
                cameraPip.lookAt(boosterWorldPos.x, boosterWorldPos.y + 10.0, boosterWorldPos.z);

                if (p.b_caught) {{
                    // キャッチ成立：タワー正面至近距離の映画級構図
                    cameraPip.position.set(38.0, 48.0, 52.0);
                    document.getElementById('pip-alt').innerText = "STATUS: CAUGHT";
                    document.getElementById('tv-booster-status').innerText = "MECHAZILLA CATCH SUCCESSFUL";
                    document.getElementById('tv-booster-status').style.color = "#38bdf8";
                }} else if (p.b_y < 3500) {{
                    // ホバリング・着陸進入：地上からの迫真見上げアングル
                    cameraPip.position.set(p.b_x * 0.1 + 75.0, Math.max(12.0, p.b_y * 0.1 + 18.0), 90.0);
                    document.getElementById('pip-alt').innerText = `BOOSTER: ${(p.b_y/1000).toFixed(2)} km`;
                    document.getElementById('tv-booster-status').innerText = "FINAL LANDING BURN & HOVER";
                }} else {{
                    // 再突入降下中
                    cameraPip.position.set(p.b_x * 0.1 - 250.0, p.b_y * 0.1 + 60.0, 350.0);
                    document.getElementById('pip-alt').innerText = `BOOSTER: ${(p.b_y/1000).toFixed(1)} km`;
                    document.getElementById('tv-booster-status').innerText = "RETURNING TO STARBASE";
                }}
            }} else {{
                // 打ち上げ時
                cameraPip.position.set(-1100, Math.max(70, p.y * 0.08 + 50), 1400);
                cameraPip.lookAt(p.x * 0.1, p.y * 0.1 + 15.0, 0);
                document.getElementById('pip-alt').innerText = `ALT: ${p.alt.toFixed(1)} km`;
            }}

            // メインカメラ追尾
            cameraMain.position.set(p.x * 0.1 - 65.0, p.y * 0.1 + 20.0, 120.0);
            cameraMain.lookAt(p.x * 0.1, p.y * 0.1 + 15.0, 0);

            // 音響コントロール
            if (actx && p.thrust) {{
                const atm = Math.exp(-p.y / 15000.0);
                rumble.gain.setTargetAtTime(0.85 * atm, actx.currentTime, 0.1);
                crackle.gain.setTargetAtTime(0.65 * atm, actx.currentTime, 0.1);
            }}

            // テレメトリ更新
            if (t < 0) {{
                document.getElementById('tv-timer').innerText = `T- 00:0${{Math.ceil(Math.abs(t))}}.0`;
            }} else {{
                const m = Math.floor(t / 60); const s = t % 60;
                document.getElementById('tv-timer').innerText = `T+ ${{String(m).padStart(2,'0')}}:${{s.toFixed(1).padStart(4,'0')}}`;
            }}
            document.getElementById('tv-spd').innerText = `${{Math.round(p.v * 3.6).toLocaleString()}} km/h`;
            document.getElementById('tv-alt').innerText = `${{p.alt.toFixed(1)}} km`;

            rendererMain.render(scene, cameraMain);
            rendererPip.render(scene, cameraPip);
        }}

        requestAnimationFrame(animate);

        window.addEventListener('resize', () => {{
            cameraMain.aspect = window.innerWidth / window.innerHeight;
            cameraMain.updateProjectionMatrix();
            rendererMain.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""

components.html(html_code, height=960)
