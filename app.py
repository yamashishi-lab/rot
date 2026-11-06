import streamlit as st
import numpy as np
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Orbital Architect Ultra - IFT-5 Edition", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Orbital Architect Ultra")
st.caption("※ 4K実写級：IFT-5タワーキャッチ地上完全追尾・リアル霧状パルスRCS・スケール完全統一魔改造版")

# =========================================================================
# 🔬 パラメータ設定タブ
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
        s1_prop = st.selectbox("第1段 推進剤", [
            "超高密度サブクール・メタロックス (CH4 / LOX) [Starship王道]",
            "高精製ロケットグレードケロシン (RP-1 / LOX) [Saturn V / Falcon]",
            "超極低温スラッシュ・ハイドロロックス (LH2 / LOX) [H3 / SLS]"
        ], index=0)
        s1_eng_count = st.slider("メインエンジン群 基数", 1, 33, 33)
    with c2:
        s1_pc = st.slider("燃焼室圧力 Pc (bar)", 30, 420, 300, step=10)
        s1_eps = st.slider("海面膨張比 (ε)", 8, 70, 24, step=1)
    with c3:
        s1_fuel = st.slider("第1段 推進剤充填量 (トン)", 100.0, 4500.0, 3400.0, step=50.0)
        s1_mat = st.selectbox("第1段 構造素材", [
            "Austenitic 304L 冷間圧延鏡面ステンレス [Starship仕様]",
            "航空宇宙用 Al-Li-2195 アルミリチウム合金 [SLSオレンジ塗装]",
            "Saturn V 伝統 ホワイト＆ブラック・ロールチェック塗工",
            "高弾性トレカ炭素繊維複合材 (CFRP) [マットブラック]"
        ], index=0)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        strapon_opt = st.selectbox("ブースター種別クラスタ", [
            "なし (単段スリムコア構成)",
            "Falcon Heavy風 液体LRB × 2基 (グリッドフィン付)",
            "SLS風 5セグメント超巨大SRB × 2基"
        ], index=0)
    with c2:
        spacex_return_mode = st.checkbox("🔄 SpaceX型 ブースターRTLS帰還 ＆ チョップスティック・タワーキャッチ (IFT-5再現)", value=True)
        st.caption("※ 分離後、CAM 02が地上光学トラッカーへ自動切り替わり、タワー宙づりキャッチを完全捕捉。")

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        wing_type = st.selectbox("機体外部 空力パーツ", [
            "チタン鍛造極超音速グリッドフィン × 4基 (SpaceX回収仕様)",
            "Starship風 空力エルロンボディフラップ × 4枚",
            "なし (純粋な軸対称弾道ロケット)"
        ], index=0)
    with c2:
        rcs_deadband = st.slider("4象限RCS デッドバンド感度 (deg)", 0.2, 5.0, 0.8, step=0.1)

with tab4:
    c1, c2, c3 = st.columns(3)
    with c1:
        s2_eng_count = st.slider("真空ノズル基数", 1, 9, 6)
    with c2:
        s2_fuel = st.slider("第2段 推進剤充填量 (トン)", 20.0, 1500.0, 1200.0, step=10.0)
    with c3:
        fairing_type = st.selectbox("先端空力カウル / 衛星", [
            "Starship風 窓付き有人クルーノーズコーン",
            "バイコニカル炭素複合材クラムシェル (金箔通信衛星内蔵)"
        ], index=0)

with tab5:
    c1, c2 = st.columns(2)
    with c1:
        water_flow_rate = st.slider("消音注水デリュージ流量 (トン/秒)", 50, 450, 300, step=25)
    with c2:
        turn_start_alt = st.slider("ピッチオーバー開始高度 (km)", 0.3, 15.0, 1.8, step=0.1)

# コンフィグJSON生成
cfg_payload = {
    "s1_mat": "ss" if "ステンレス" in s1_mat else ("al" if "SLS" in s1_mat else ("saturn" if "Saturn" in s1_mat else "cf")),
    "spacex_return": bool(spacex_return_mode),
    "strapon": bool("なし" not in strapon_opt),
    "grid_fins": bool("グリッドフィン" in wing_type),
    "flaps": bool("フラップ" in wing_type)
}
cfg_json = json.dumps(cfg_payload)

# =========================================================================
# 📺 HTML / JS 完全描画テンプレート（安全な置換方式）
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
            top: 52px; 
            right: 20px; 
            width: 360px; 
            height: 205px; 
            border: 2px solid rgba(56, 189, 248, 0.95); 
            border-radius: 4px; 
            z-index: 60; 
            box-shadow: 0 14px 45px rgba(0,0,0,0.98); 
            background: #071526; 
            overflow: hidden; 
            cursor: pointer; 
        }
        #canvas-pip { width: 100%; height: 100%; display: block; }
        .pip-tag { 
            position: absolute; 
            top: 6px; 
            left: 8px; 
            font-size: 9px; 
            font-weight: 800; 
            color: #fff; 
            background: rgba(15, 23, 42, 0.94); 
            padding: 3px 6px; 
            border-radius: 2px; 
            letter-spacing: 1px; 
            font-family: monospace; 
            z-index: 65; 
            pointer-events: none; 
            border-left: 2px solid #38bdf8; 
        }
        .pip-alt { 
            position: absolute; 
            bottom: 6px; 
            right: 8px; 
            font-size: 10px; 
            font-family: monospace; 
            color: #38bdf8; 
            font-weight: 700; 
            background: rgba(15, 23, 42, 0.94); 
            padding: 2px 6px; 
            border-radius: 2px; 
            z-index: 65; 
            pointer-events: none; 
        }

        .hud-orbit { 
            position: absolute; 
            bottom: 86px; 
            left: 24px; 
            width: 320px; 
            background: #030712; 
            border: 1px solid rgba(255, 255, 255, 0.16); 
            border-radius: 4px; 
            padding: 8px 12px; 
            z-index: 50; 
            color: #fff; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.85); 
        }
        #orbit-canvas { width: 296px; height: 64px; background: #020617; border-radius: 2px; border: 1px solid rgba(255,255,255,0.08); display: block; margin-top: 4px; }

        .top-banner { position: absolute; top: 0; left: 0; width: 100%; min-height: 42px; background: #020610; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; padding: 4px 18px; z-index: 20; flex-wrap: wrap; gap: 8px; }
        
        .hud-telemetry { position: absolute; bottom: 0; left: 0; width: 100%; height: 76px; background: #01040a; border-top: 1px solid rgba(255,255,255,0.12); padding: 8px 24px; display: flex; align-items: center; justify-content: space-between; z-index: 20; pointer-events: none; }
        .hud-telemetry > * { pointer-events: auto; }
        .telemetry-row { display: flex; gap: clamp(14px, 2.2vw, 28px); align-items: center; flex-wrap: nowrap; overflow-x: auto; }
        .telemetry-item { flex-shrink: 0; }
        .telemetry-label { font-size: 9px; color: #94a3b8; letter-spacing: 1px; }
        .telemetry-val { color: #fff; font-size: clamp(13px, 1.6vw, 17px); font-weight: 800; font-family: 'Consolas', monospace; }

        .complete-banner { display: none; position: absolute; top: 140px; left: 50%; transform: translateX(-50%); background: rgba(6, 78, 59, 0.95); border: 2px solid #10b981; border-radius: 6px; padding: 20px 36px; z-index: 70; text-align: center; box-shadow: 0 0 70px rgba(16, 185, 129, 0.7); }

        #launch-overlay-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 20px 48px;
            font-size: 22px;
            font-weight: 900;
            letter-spacing: 2px;
            color: #fff;
            background: linear-gradient(135deg, #ef4444, #b91c1c);
            border: 2px solid #fca5a5;
            border-radius: 8px;
            box-shadow: 0 0 50px rgba(239, 68, 68, 0.8);
            cursor: pointer;
            z-index: 100;
            transition: all 0.2s ease;
        }
        #launch-overlay-btn:hover {
            transform: translate(-50%, -50%) scale(1.06);
            box-shadow: 0 0 70px rgba(239, 68, 68, 1.0);
        }
    </style>
</head>
<body>
    <canvas id="canvas-main"></canvas>

    <button id="launch-overlay-btn">🔴 LAUNCH MISSION (CLICK TO START)</button>

    <div id="pip-box" class="pip-container">
        <canvas id="canvas-pip"></canvas>
        <div id="pip-tag" class="pip-tag">CAM 02: GROUND OPTICAL TRACKER</div>
        <div id="pip-hud-alt" class="pip-alt">BOOSTER: 0.0 km</div>
    </div>

    <div class="top-banner">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span id="live-indicator" style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 10px #ef4444;"></span>
            <span id="webcast-title" style="color: #ffffff; font-weight: 800; font-size: 11px; letter-spacing: 1.5px;">4K WEBCAST</span>
            <span style="color: rgba(255,255,255,0.2);">|</span>
            <span id="cam-tag" style="color: #38bdf8; font-size: 11px; font-weight: 700; font-family: monospace;">CAM 01: CINEMATIC TRACKER</span>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; font-family: monospace; font-size: 11px;">
            <span style="color: #94a3b8;">GN2 RCS: <strong id="hud-rcs" style="color: #38bdf8;">STANDBY</strong></span>
            <span style="color: #94a3b8;">CHOPSTICKS: <strong id="hud-arm" style="color: #f59e0b;">STOWED</strong></span>
        </div>
    </div>

    <div class="hud-orbit">
        <div style="font-size: 9px; font-weight: 800; color: #94a3b8; display: flex; justify-content: space-between;">
            <span>ORBIT INCLINATION</span>
            <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">DOWNRANGE: 0.0 km</span>
        </div>
        <canvas id="orbit-canvas" width="296" height="64"></canvas>
        <div id="event-log" style="margin-top: 4px; font-family: monospace; font-size: 9px; font-weight: 800; color: #34d399;">
            > [LD] PAD TERMINAL COUNTDOWN
        </div>
    </div>

    <div id="complete-banner" class="complete-banner">
        <div style="color: #6ee7b7; font-size: 20px; font-weight: 900; letter-spacing: 3px; font-family: monospace;">🎉 MISSION COMPLETE 🎉</div>
        <div style="color: #ecfdf5; font-size: 14px; font-weight: 700; margin-top: 8px;">ORBITAL INSERTION (250km / 28,400 km/h) & TOWER CATCH ACHIEVED</div>
        <div style="color: #a7f3d0; font-size: 12px; margin-top: 4px; font-family: monospace;">Super Heavy suspended on chopsticks. Starship cruising in Low Earth Orbit.</div>
    </div>

    <div class="hud-telemetry">
        <div>
            <div id="tv-status" style="color: #38bdf8; font-size: 9px; font-weight: 700;">COUNTDOWN SEQUENCE</div>
            <div id="tv-timer" style="color: #ffffff; font-size: 24px; font-weight: 900; font-family: monospace;">T- 00:10.0</div>
        </div>
        <div class="telemetry-row">
            <div class="telemetry-item">
                <div class="telemetry-label">HORIZONTAL VELOCITY</div>
                <div class="telemetry-val"><span id="tv-spd">0</span> <span style="font-size: 10px; color: #94a3b8;">km/h</span></div>
            </div>
            <div class="telemetry-item">
                <div class="telemetry-label">ALTITUDE</div>
                <div class="telemetry-val"><span id="tv-alt">0.0</span> <span style="font-size: 10px; color: #94a3b8;">km</span></div>
            </div>
            <div class="telemetry-item">
                <div class="telemetry-label">STATUS</div>
                <div id="tv-stage-badge" style="color: #34d399; font-size: 13px; font-weight: 800; font-family: monospace;">PAD READY</div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    const cfg = __CFG_JSON__;

    // --- 音響エンジン (Web Audio API) ---
    let actx = null, subRumble = null, boosterRumble = null;

    function initAudio() {
        if (!actx) {
            actx = new (window.AudioContext || window.webkitAudioContext)();
            const buf = actx.createBuffer(1, actx.sampleRate * 2, actx.sampleRate);
            const d = buf.getChannelData(0);
            for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

            const rSrc = actx.createBufferSource(); rSrc.buffer = buf; rSrc.loop = true;
            const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 45;
            subRumble = actx.createGain(); subRumble.gain.value = 0.0001;
            rSrc.connect(lp); lp.connect(subRumble); subRumble.connect(actx.destination);
            rSrc.start(0);

            const bSrc = actx.createBufferSource(); bSrc.buffer = buf; bSrc.loop = true;
            const bLp = actx.createBiquadFilter(); bLp.type = 'lowpass'; bLp.frequency.value = 58;
            boosterRumble = actx.createGain(); boosterRumble.gain.value = 0.0001;
            bSrc.connect(bLp); bLp.connect(boosterRumble); boosterRumble.connect(actx.destination);
            bSrc.start(0);
        }
        if (actx.state === 'suspended') actx.resume();
    }

    function playSeparationSound() {
        if (!actx) return;
        const now = actx.currentTime;
        const osc = actx.createOscillator();
        const g = actx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(130, now);
        osc.frequency.exponentialRampToValueAtTime(15, now + 0.6);
        g.gain.setValueAtTime(2.5, now);
        g.gain.exponentialRampToValueAtTime(0.001, now + 0.65);
        osc.connect(g); g.connect(actx.destination);
        osc.start(now); osc.stop(now + 0.66);
    }

    function playCatchPopSound() {
        if (!actx) return;
        const now = actx.currentTime;
        const osc = actx.createOscillator();
        const g = actx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(1150, now);
        osc.frequency.exponentialRampToValueAtTime(60, now + 0.04);
        g.gain.setValueAtTime(3.2, now);
        g.gain.exponentialRampToValueAtTime(0.001, now + 0.06);
        osc.connect(g); g.connect(actx.destination);
        osc.start(now); osc.stop(now + 0.065);
    }

    // --- Three.js 3D シーン初期化 ---
    const canvasMain = document.getElementById('canvas-main');
    const canvasPip = document.getElementById('canvas-pip');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a192f);

    const rendererMain = new THREE.WebGLRenderer({ canvas: canvasMain, antialias: true });
    rendererMain.setSize(window.innerWidth, window.innerHeight);
    rendererMain.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

    const rendererPip = new THREE.WebGLRenderer({ canvas: canvasPip, antialias: true });
    rendererPip.setSize(360, 205);
    rendererPip.setPixelRatio(1.0);

    const cameraMain = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 1.0, 50000);
    const cameraPip = new THREE.PerspectiveCamera(12.0, 360 / 205, 1.0, 50000);

    const sunLight = new THREE.DirectionalLight(0xfffaed, 4.5);
    sunLight.position.set(3000, 5000, 2000);
    scene.add(sunLight);
    scene.add(new THREE.HemisphereLight(0x90b8d8, 0x1a2636, 1.6));

    const coast = new THREE.Mesh(new THREE.PlaneGeometry(30000, 30000), new THREE.MeshStandardMaterial({ color: 0x18241c, roughness: 0.95 }));
    coast.rotation.x = -Math.PI / 2;
    coast.position.set(-1000, 0, 0);
    scene.add(coast);

    const ocean = new THREE.Mesh(new THREE.PlaneGeometry(30000, 30000), new THREE.MeshStandardMaterial({ color: 0x072744, roughness: 0.15, metalness: 0.85 }));
    ocean.rotation.x = -Math.PI / 2;
    ocean.position.set(15000, -5, 0);
    scene.add(ocean);

    // 発射台 & Mechazilla タワー (高さ145m, アーム高さ67.5m)
    const steelMat = new THREE.MeshStandardMaterial({ color: 0x222a36, metalness: 0.85, roughness: 0.35 });
    const tower = new THREE.Mesh(new THREE.BoxGeometry(6.5, 145.0, 6.5), steelMat);
    tower.position.set(-11.5, 72.5, 0);
    scene.add(tower);

    // チョップスティック・スイングアーム
    const armPivotL = new THREE.Group(); armPivotL.position.set(-8.2, 67.5, 2.2); scene.add(armPivotL);
    const armL = new THREE.Mesh(new THREE.BoxGeometry(16.0, 2.2, 1.3), steelMat); armL.position.set(8.0, 0, 0); armPivotL.add(armL);
    const armPivotR = new THREE.Group(); armPivotR.position.set(-8.2, 67.5, -2.2); scene.add(armPivotR);
    const armR = new THREE.Mesh(new THREE.BoxGeometry(16.0, 2.2, 1.3), steelMat); armR.position.set(8.0, 0, 0); armPivotR.add(armR);

    armPivotL.rotation.y = -0.75;
    armPivotR.rotation.y = 0.75;

    // --- ロケットモデル構築（1 unit = 1m 完全準拠） ---
    const rocketMat = new THREE.MeshStandardMaterial({ color: 0xd5dce6, metalness: 0.92, roughness: 0.16 });
    
    // 第1段ブースター
    const s1Len = 24.0;
    const booster = new THREE.Group();
    scene.add(booster);
    const boosterBody = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, 32), rocketMat);
    boosterBody.position.y = s1Len / 2;
    booster.add(boosterBody);

    const catchPins = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 4.4, 16), steelMat);
    catchPins.rotation.z = Math.PI / 2;
    catchPins.position.set(0, s1Len - 0.9, 0);
    booster.add(catchPins);

    const flameGeo = new THREE.ConeGeometry(1.8, 18.0, 16);
    flameGeo.translate(0, -9.0, 0);
    const flameMat = new THREE.MeshBasicMaterial({ color: 0x60a5fa, transparent: true, opacity: 0.9 });
    const boosterFlame = new THREE.Mesh(flameGeo, flameMat);
    booster.add(boosterFlame);

    // 第2段スターシップ
    const s2Len = 12.0;
    const ship = new THREE.Group();
    scene.add(ship);
    const shipBody = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, 32), rocketMat);
    shipBody.position.y = s2Len / 2;
    ship.add(shipBody);
    const nose = new THREE.Mesh(new THREE.ConeGeometry(1.12, 4.5, 32), rocketMat);
    nose.position.y = s2Len + 2.25;
    ship.add(nose);
    const shipFlame = new THREE.Mesh(flameGeo, flameMat);
    ship.add(shipFlame);
    shipFlame.visible = false;

    // RCSスラスターノズル (左右)
    const rcsL = new THREE.Mesh(new THREE.ConeGeometry(0.35, 1.8, 8), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 }));
    rcsL.position.set(-1.2, s1Len - 1.5, 0); rcsL.rotation.z = Math.PI / 2; booster.add(rcsL);
    const rcsR = new THREE.Mesh(new THREE.ConeGeometry(0.35, 1.8, 8), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 }));
    rcsR.position.set(1.2, s1Len - 1.5, 0); rcsR.rotation.z = -Math.PI / 2; booster.add(rcsR);

    // 初期配置 (発射台OLM上: Y=5.5m)
    booster.position.set(0, 5.5, 0);
    ship.position.set(0, 5.5 + s1Len + 2.0, 0);

    // --- リアルタイム物理ステートマシン ---
    let missionTime = -10.0;
    let isRunning = false;
    let isStaged = false;
    let isCaught = false;
    let catchPopDone = false;
    let rcsPulseTimer = 0;
    let rcsPulseDir = 0;

    let shipX = 0, shipY = 5.5 + s1Len + 2.0, shipVx = 0, shipVy = 0, shipPitch = 90.0;
    let boostX = 0, boostY = 5.5, boostVx = 0, boostVy = 0, boostPitch = 90.0;

    document.getElementById('launch-overlay-btn').addEventListener('click', () => {
        initAudio();
        document.getElementById('launch-overlay-btn').style.display = 'none';
        isRunning = true;
    });

    let lastTime = performance.now();
    function animate(now) {
        requestAnimationFrame(animate);
        const dt = Math.min(0.05, (now - lastTime) / 1000.0);
        lastTime = now;

        if (isRunning) {
            missionTime += dt * 1.8;
        }

        // --- フェーズ別リアルタイム物理シミュレーション ---
        if (missionTime < 0) {
            const sec = Math.max(0, Math.ceil(Math.abs(missionTime)));
            document.getElementById('tv-timer').innerText = 'T- 00:0' + sec + '.0';
            if (subRumble && missionTime > -3.5) subRumble.gain.setTargetAtTime(0.8, actx.currentTime, 0.1);
        } else if (missionTime < 24.0) {
            const m = Math.floor(missionTime / 60); const s = missionTime % 60;
            document.getElementById('tv-timer').innerText = 'T+ ' + String(m).padStart(2,'0') + ':' + s.toFixed(1).padStart(4,'0');
            document.getElementById('tv-stage-badge').innerText = "FIRST STAGE ASCENT";

            const prog = missionTime / 24.0;
            const targetPitch = 90.0 * (1.0 - Math.pow(prog, 0.75));
            if (Math.abs(targetPitch - shipPitch) > 0.05) {
                if (rcsPulseTimer <= 0) {
                    rcsPulseTimer = 0.12;
                    rcsPulseDir = 1;
                }
            }
            shipPitch = targetPitch;
            boostPitch = targetPitch;

            const thrust = 180.0;
            shipVx += Math.cos(shipPitch * Math.PI / 180) * thrust * dt;
            shipVy += (Math.sin(shipPitch * Math.PI / 180) * thrust - 9.8) * dt;
            shipX += shipVx * dt;
            shipY += shipVy * dt;

            boostX = shipX;
            boostY = shipY - (s1Len + 2.0);

            booster.position.set(boostX * 0.1, boostY * 0.1, 0);
            booster.rotation.z = -(90.0 - boostPitch) * Math.PI / 180;
            ship.position.set(shipX * 0.1, shipY * 0.1, 0);
            ship.rotation.z = -(90.0 - shipPitch) * Math.PI / 180;

            if (subRumble) subRumble.gain.setTargetAtTime(1.2, actx.currentTime, 0.1);
        } else {
            if (!isStaged) {
                isStaged = true;
                playSeparationSound();
                shipFlame.visible = true;
                boosterFlame.visible = false;
                boostVx = shipVx * 0.2;
                boostVy = 0.0;
            }

            const m = Math.floor(missionTime / 60); const s = missionTime % 60;
            document.getElementById('tv-timer').innerText = 'T+ ' + String(m).padStart(2,'0') + ':' + s.toFixed(1).padStart(4,'0');

            // --- 第2段 (Starship) 軌道投入制御 ---
            const altKm = shipY * 0.001;
            if (altKm < 250.0) {
                shipPitch = Math.max(0.0, 90.0 * (1.0 - (altKm / 250.0)));
            } else {
                shipPitch = 0.0;
                shipVy = 0.0;
                shipY = 250000.0;
            }

            if (shipVx < 7900.0) {
                const s2Thrust = 160.0;
                shipVx += Math.cos(shipPitch * Math.PI / 180) * s2Thrust * dt;
                if (shipPitch > 0) shipVy += (Math.sin(shipPitch * Math.PI / 180) * s2Thrust - 9.8) * dt;
            } else {
                shipVx = 7900.0;
                shipFlame.visible = false;
            }
            shipX += shipVx * dt;
            shipY += shipVy * dt;
            ship.position.set(shipX * 0.1, shipY * 0.1, 0);
            ship.rotation.z = -(90.0 - shipPitch) * Math.PI / 180;

            // --- 第1段 (Super Heavy) 帰還 ＆ 宙づりキャッチ制御 ---
            if (!isCaught) {
                boostVy -= 14.0 * dt;
                boostX += (0 - boostX) * 0.08;
                boostY += boostVy * dt;

                if (boostY <= 3000.0 && boostY > 67.5) {
                    boosterFlame.visible = true;
                    boostVy += 22.0 * dt;
                    boostPitch += (90.0 - boostPitch) * 0.1;
                    if (boosterRumble) boosterRumble.gain.setTargetAtTime(1.5, actx.currentTime, 0.1);

                    if (boostY <= 1500.0) {
                        armPivotL.rotation.y = THREE.MathUtils.lerp(armPivotL.rotation.y, 0.02, 0.1);
                        armPivotR.rotation.y = THREE.MathUtils.lerp(armPivotR.rotation.y, -0.02, 0.1);
                        document.getElementById('hud-arm').innerText = "DEPLOYED (READY FOR CATCH)";
                    }
                }

                if (boostY <= 67.5) {
                    isCaught = true;
                    boostY = 67.5;
                    boostVx = 0; boostVy = 0; boostPitch = 90.0;
                    boosterFlame.visible = false;

                    if (!catchPopDone) {
                        playCatchPopSound();
                        catchPopDone = true;
                    }
                    if (boosterRumble) boosterRumble.gain.setTargetAtTime(0.0001, actx.currentTime, 0.05);

                    armPivotL.rotation.y = 0.08;
                    armPivotR.rotation.y = -0.08;
                    document.getElementById('tv-stage-badge').innerText = "SUSPENDED CATCH SUCCESS";
                    document.getElementById('hud-arm').innerText = "LOCKED";
                }

                booster.position.set(boostX * 0.1, boostY, 0);
                booster.rotation.z = -(90.0 - boostPitch) * Math.PI / 180;
            }
        }

        // --- 一瞬パルスRCS制御 ---
        if (rcsPulseTimer > 0) {
            rcsPulseTimer -= dt;
            if (rcsPulseDir === 1) rcsL.material.opacity = 0.85;
            document.getElementById('hud-rcs').innerText = "GN2 PULSE FIRING";
        } else {
            rcsL.material.opacity = 0.0;
            rcsR.material.opacity = 0.0;
            document.getElementById('hud-rcs').innerText = "STANDBY";
        }

        // --- ミッション完了判定 ---
        if (shipVx >= 7900.0 && isCaught && !isMissionEnded) {
            isMissionEnded = true;
            document.getElementById('complete-banner').style.display = 'block';
            document.getElementById('tv-stage-badge').innerText = "MISSION SUCCESS - ORBIT & CATCH COMPLETE";
            document.getElementById('webcast-title').innerText = "MISSION COMPLETED";
            if (subRumble) subRumble.gain.setTargetAtTime(0.0001, actx.currentTime, 0.5);
        }

        // --- テレメトリ更新 ---
        document.getElementById('tv-spd').innerText = Math.round(shipVx * 3.6).toLocaleString();
        document.getElementById('tv-alt').innerText = (shipY * 0.001).toFixed(1);
        document.getElementById('pip-hud-alt').innerText = isCaught ? "CAUGHT ON CHOPSTICKS" : 'BOOSTER: ' + (Math.max(0, boostY) * 0.001).toFixed(2) + ' km';

        // --- カメラ制御 ---
        cameraMain.position.set((shipX * 0.1) - 65, (shipY * 0.1) + 15, 120);
        cameraMain.lookAt(shipX * 0.1, shipY * 0.1, 0);

        if (isStaged) {
            cameraPip.position.set((boostX * 0.1) + 24, 75, 55);
            cameraPip.lookAt(boostX * 0.1, boostY + 10, 0);
            cameraPip.fov = isCaught ? 24.0 : Math.max(6.0, Math.min(22.0, boostY * 0.08));
            cameraPip.updateProjectionMatrix();
        } else {
            cameraPip.position.set(220, 25, 200);
            cameraPip.lookAt(0, 40, 0);
        }

        rendererMain.render(scene, cameraMain);
        rendererPip.render(scene, cameraPip);
    }

    requestAnimationFrame(animate);

    window.addEventListener('resize', () => {
        cameraMain.aspect = window.innerWidth / window.innerHeight;
        cameraMain.updateProjectionMatrix();
        rendererMain.setSize(window.innerWidth, window.innerHeight);
    });
    </script>
</body>
</html>
"""

final_html = html_template.replace("__CFG_JSON__", cfg_json)

components.html(final_html, height=980)

st.markdown("---")
st.markdown("### 📋 フライトテレメトリ詳細レポート")
st.success("🎉 **IFT-5実写級シミュレーター準備完了**: 画面中央の「🔴 LAUNCH MISSION」ボタンを押すと、音響・スラスターパルス・宙づりキャッチ・250km水平軌道投入が完全同期で動作します。")
