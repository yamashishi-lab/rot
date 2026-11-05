
def get_html_content(sim_data_json, sim_cfg_json, fail_msg):
    html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #01040a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; user-select: none; }}
        #canvas-main {{ width: 100%; height: 100%; display: block; }}
        .vignette {{ position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; box-shadow: inset 0 0 160px rgba(0,0,0,0.88); z-index: 5; }}
        .grain {{ position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index: 6; opacity: 0.035; background-image: radial-gradient(#fff 1px, transparent 1px); background-size: 3px 3px; }}
        
        /* 🎥 PiP 右上完全独立配置 (被り防止ベゼル ＆ 独立Canvas) */
        .pip-container {{ position: absolute; top: 52px; right: 20px; width: 340px; height: 195px; border: 2px solid rgba(56, 189, 248, 0.85); border-radius: 4px; z-index: 60; box-shadow: 0 14px 45px rgba(0,0,0,0.98); background: #01040a; overflow: hidden; cursor: pointer; }}
        #canvas-pip {{ width: 100%; height: 100%; display: block; }}
        .pip-tag {{ position: absolute; top: 6px; left: 8px; font-size: 9px; font-weight: 800; color: #fff; background: rgba(15, 23, 42, 0.92); padding: 3px 6px; border-radius: 2px; letter-spacing: 1px; font-family: monospace; z-index: 65; pointer-events: none; border-left: 2px solid #38bdf8; }}
        .pip-alt {{ position: absolute; bottom: 6px; right: 8px; font-size: 10px; font-family: monospace; color: #38bdf8; font-weight: 700; background: rgba(15, 23, 42, 0.92); padding: 2px 6px; border-radius: 2px; z-index: 65; pointer-events: none; }}
        .pip-toggle-hint {{ position: absolute; top: 6px; right: 8px; font-size: 9px; font-family: monospace; color: #94a3b8; background: rgba(15, 23, 42, 0.92); padding: 3px 6px; border-radius: 2px; z-index: 65; pointer-events: none; }}

        /* 🛰️ 軌道HUD 左上配置 (PiPと絶対に被らない完全独立座標) */
        .hud-orbit {{ position: absolute; top: 52px; left: 20px; width: 300px; max-width: calc(100vw - 390px); background: rgba(3, 7, 18, 0.82); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 4px; padding: 10px 12px; box-sizing: border-box; z-index: 25; color: #fff; }}
        .hud-orbit:hover {{ background: rgba(3, 7, 18, 0.94); }}
        
        /* 🔝 トップバナー */
        .top-banner {{ position: absolute; top: 0; left: 0; width: 100%; min-height: 44px; background: rgba(2, 6, 16, 0.94); backdrop-filter: blur(16px); display: flex; align-items: center; justify-content: space-between; padding: 4px 18px; box-sizing: border-box; border-bottom: 1px solid rgba(255,255,255,0.08); z-index: 20; flex-wrap: wrap; gap: 8px; }}
        
        /* 📊 ボトムテレメトリ */
        .hud-telemetry {{ position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(1, 3, 8, 0.98) 0%, rgba(2, 6, 14, 0.88) 75%, transparent 100%); padding: 14px 20px 10px 20px; box-sizing: border-box; display: flex; align-items: flex-end; justify-content: space-between; z-index: 20; pointer-events: none; flex-wrap: wrap; gap: 14px; }}
        .hud-telemetry > * {{ pointer-events: auto; }}
        .rud-banner {{ display: none; position: absolute; top: 150px; left: 50%; transform: translateX(-50%); background: rgba(120, 10, 10, 0.94); backdrop-filter: blur(16px); border: 2px solid #ef4444; border-radius: 4px; padding: 16px 28px; z-index: 70; text-align: center; box-shadow: 0 0 60px rgba(239, 68, 68, 0.7); }}
    </style>
</head>
<body>
    <canvas id="canvas-main"></canvas>
    <div class="vignette"></div>
    <div class="grain"></div>

    <!-- 2画面用PiP 右上ベゼル枠 (CAM 02: 独立描画Canvas) -->
    <div id="pip-box" class="pip-container" title="クリックでPiPの表示/非表示を切り替え">
        <canvas id="canvas-pip"></canvas>
        <div id="pip-tag" class="pip-tag">CAM 02: COASTAL TELEPHOTO (1200mm)</div>
        <div id="pip-hud-alt" class="pip-alt">ALT: 0.0 km</div>
        <div id="pip-hint" class="pip-toggle-hint">[CLICK TO TOGGLE]</div>
    </div>

    <!-- 🔝 トップバナー -->
    <div class="top-banner">
        <div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex-shrink: 1;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 10px #ef4444; flex-shrink: 0;"></span>
            <span style="color: #ffffff; font-weight: 800; font-size: clamp(10px, 1.2vw, 12px); letter-spacing: 1.5px; white-space: nowrap;">4K WEBCAST</span>
            <span style="color: rgba(255,255,255,0.2);">|</span>
            <span id="cam-tag" style="color: #38bdf8; font-size: clamp(9px, 1.1vw, 11px); font-weight: 700; letter-spacing: 1px; font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">CAM 01: CINEMATIC WIDE CHASE</span>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; font-family: monospace; font-size: clamp(9px, 1.1vw, 11px); flex-wrap: wrap;">
            <span style="color: #94a3b8; white-space: nowrap;">ATMOS: <strong id="hud-regime" style="color: #f8fafc;">TROPOSPHERE</strong></span>
            <span style="color: #94a3b8; white-space: nowrap;">RCS: <strong id="hud-rcs" style="color: #38bdf8;">ACTIVE</strong></span>
            <span style="color: #94a3b8; white-space: nowrap;">WATER: <strong id="hud-deluge" style="color: #38bdf8;">STANDBY</strong></span>
            <span id="comm-status" style="color: #10b981; white-space: nowrap;">LOCKED</span>
        </div>
    </div>

    <!-- 🛰️ 軌道トラジェクトリHUD ＆ 実況コールアウト (左上固定) -->
    <div class="hud-orbit" id="hud-orbit-box">
        <div style="font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 1.2px; margin-bottom: 4px; display: flex; justify-content: space-between;">
            <span>DOWNRANGE TRAJECTORY</span>
            <span id="hud-downrange" style="color: #38bdf8; font-family: monospace;">0.0 km</span>
        </div>
        <canvas id="orbit-canvas" width="276" height="54" style="width: 100%; height: 54px; background: #020617; border-radius: 2px; border: 1px solid rgba(255,255,255,0.08);"></canvas>
        <div id="event-log" style="margin-top: 6px; font-family: monospace; font-size: 10.5px; font-weight: 800; color: #34d399; border-top: 1px solid rgba(255,255,255,0.12); padding-top: 4px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
            > [LD] GO FOR TERMINAL COUNTDOWN
        </div>
        <div id="sub-callout" style="font-family: monospace; font-size: 9.5px; color: #93c5fd; margin-top: 2px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
            > Propellant tanks pressurized for flight
        </div>
    </div>

    <div id="rud-banner" class="rud-banner">
        <div style="color: #fff; font-size: 17px; font-weight: 900; letter-spacing: 2.5px; font-family: monospace;">🚨 RAPID UNSCHEDULED DISASSEMBLY (RUD) 🚨</div>
        <div id="rud-desc" style="color: #fecaca; font-size: 13px; font-weight: 600; margin-top: 6px; max-width: 520px; line-height: 1.4;"></div>
    </div>

    <!-- 📊 ボトムテレメトリドック -->
    <div class="hud-telemetry">
        <div style="flex-shrink: 0;">
            <div id="tv-status" style="color: #38bdf8; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 2px;">COUNTDOWN SEQUENCE</div>
            <div id="tv-timer" style="color: #ffffff; font-size: clamp(26px, 3.5vw, 36px); font-weight: 900; font-family: 'Consolas', monospace; letter-spacing: 2px; text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);">T- 00:10.0</div>
        </div>
        <div style="display: flex; gap: clamp(12px, 2vw, 24px); border-left: 1px solid rgba(255,255,255,0.15); padding-left: 14px; flex-wrap: wrap;">
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">SPEED / MACH</div>
                <div style="color: #fff; font-size: clamp(15px, 2vw, 19px); font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-mach">M 0.00</span> <span style="font-size: 10px; color: #94a3b8;" id="tv-spd">(0 km/h)</span></div>
            </div>
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">ALTITUDE</div>
                <div style="color: #fff; font-size: clamp(15px, 2vw, 19px); font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-alt">0.0</span> <span style="font-size: 10px; color: #94a3b8;">km</span></div>
            </div>
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">DYNAMIC PRESSURE</div>
                <div style="color: #fff; font-size: clamp(15px, 2vw, 19px); font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-q">0.0</span> <span style="font-size: 10px; color: #94a3b8;">kPa</span></div>
            </div>
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">AXIAL LOAD</div>
                <div style="color: #fff; font-size: clamp(15px, 2vw, 19px); font-weight: 800; font-family: 'Consolas', monospace;"><span id="tv-g">1.0</span> <span style="font-size: 10px; color: #94a3b8;">G</span></div>
            </div>
            <div>
                <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">STAGE CONFIG</div>
                <div id="tv-stage-badge" style="color: #34d399; font-size: clamp(13px, 1.8vw, 16px); font-weight: 800; font-family: 'Consolas', monospace; white-space: nowrap;">PAD READY</div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const simData = {sim_data_json};
        const simCfg = {sim_cfg_json};
        const failMessage = "{fail_msg}";

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
        pipBox.addEventListener('click', () => {{
            pipVisible = !pipVisible;
            canvasPip.style.display = pipVisible ? 'block' : 'none';
            document.getElementById('pip-tag').style.display = pipVisible ? 'block' : 'none';
            document.getElementById('pip-hud-alt').style.display = pipVisible ? 'block' : 'none';
            pipBox.style.height = pipVisible ? '195px' : '32px';
            pipHint.innerText = pipVisible ? '[CLICK TO HIDE]' : '[CLICK TO SHOW]';
        }});

        // =========================================================================
        // 🎙️ 完全自動音声合成（SpeechSynthesis）実況エンジン (ボタン不要・即時再生)
        // =========================================================================
        function speakCallout(text) {{
            if (!('speechSynthesis' in window)) return;
            try {{
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance(text);
                u.rate = 1.15;
                u.pitch = 0.95;
                u.volume = 1.0;
                u.lang = 'en-US';
                window.speechSynthesis.speak(u);
            }} catch(e) {{}}
        }}

        // 自動起動の試行
        window.addEventListener('load', () => {{
            speakCallout("System ready. Webcast feed connected.");
        }});

        const calloutMilestones = [
            {{ t: -10.0, main: "> [LD] TERMINAL COUNTDOWN INITIATED", sub: "> Final telemetry lock confirmed", spoken: "Ten. Nine. Eight. Seven. Terminal countdown initiated." }},
            {{ t: -5.0, main: "> [PAD] DELUGE WATER SYSTEM ACTIVATED", sub: "> Sound suppression water flowing at 250 t/s", spoken: "Sound suppression water active." }},
            {{ t: -simCfg.ignition_lead, main: "> [PROP] ENGINE IGNITION SEQUENCE START", sub: "> Turbopumps spin-up in progress", spoken: "Ignition sequence start. Three. Two. One." }},
            {{ t: 0.0, main: "> [LIFTOFF] VEHICLE HAS CLEARED PAD 39A", sub: "> Pitch and roll program active", spoken: "Liftoff. Tower cleared." }},
            {{ t: 15.0, main: "> [GUIDANCE] GRAVITY TURN TRAJECTORY NOMINAL", sub: "> Pitch over maneuver continuing downrange", spoken: "Pitch and roll program initiated. Trajectory nominal." }},
            {{ t: 45.0, main: "> [AERO] VEHICLE PASSING MACH 1 - SUPERSONIC", sub: "> Transonic buffet levels well within limits", spoken: "Vehicle is supersonic." }},
            {{ t: 65.0, main: "> [AERO] MAXIMUM DYNAMIC PRESSURE (MAX-Q)", sub: "> Main engine throttle bucket applied", spoken: "Vehicle passing Max-Q. Throttle bucket applied." }},
            {{ t: 130.0, main: "> [PROP] BOOSTER MECO & SEPARATION", sub: "> Korolev cross staging sequence complete", spoken: "Booster engine cutoff and stage separation confirmed." }},
            {{ t: 165.0, main: "> [STAGE] FIRST STAGE MECO & HOT STAGING", sub: "> Second stage vacuum ignition confirmed", spoken: "First stage MECO. Hot staging and second stage ignition." }},
            {{ t: 195.0, main: "> [AERO] PAYLOAD FAIRING JETTISON", sub: "> Exo-atmospheric telemetry optimal", spoken: "Fairing deployment confirmed. Clean separation." }},
            {{ t: 480.0, main: "> [ORBIT] SECO - NOMINAL ORBITAL INSERTION", sub: "> Spacecraft cruising in stable Low Earth Orbit", spoken: "Second engine cutoff. Spacecraft in nominal orbit." }}
        ];

        let calloutTrackIndex = 0;
        function updateFlightCallouts(simT) {{
            while (calloutTrackIndex < calloutMilestones.length && simT >= calloutMilestones[calloutTrackIndex].t) {{
                const milestone = calloutMilestones[calloutTrackIndex];
                if (eventLog) eventLog.innerText = milestone.main;
                if (subCallout) subCallout.innerText = milestone.sub;
                speakCallout(milestone.spoken);
                calloutTrackIndex++;
            }}
        }}

        // =========================================================================
        // 🔊 Web Audio 重低音ランブル＆パイロ爆薬音響合成
        // =========================================================================
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let actx = null, subRumble = null, shockCrackle = null, gasHiss = null;
        function initAudio() {{
            if (!actx) {{
                try {{
                    actx = new AudioCtx();
                    const buf = actx.createBuffer(1, actx.sampleRate * 3, actx.sampleRate);
                    const d = buf.getChannelData(0);
                    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

                    const rSrc = actx.createBufferSource(); rSrc.buffer = buf; rSrc.loop = true;
                    const lp = actx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 45;
                    subRumble = actx.createGain(); subRumble.gain.value = 0;
                    rSrc.connect(lp); lp.connect(subRumble); subRumble.connect(actx.destination);
                    rSrc.start(0);

                    const cSrc = actx.createBufferSource(); cSrc.buffer = buf; cSrc.loop = true;
                    const bp = actx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 420; bp.Q.value = 3.8;
                    shockCrackle = actx.createGain(); shockCrackle.gain.value = 0;
                    cSrc.connect(bp); bp.connect(shockCrackle); shockCrackle.connect(actx.destination);
                    cSrc.start(0);

                    const hSrc = actx.createBufferSource(); hSrc.buffer = buf; hSrc.loop = true;
                    const hp = actx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 1600;
                    gasHiss = actx.createGain(); gasHiss.gain.value = 0;
                    hSrc.connect(hp); hp.connect(gasHiss); gasHiss.connect(actx.destination);
                    hSrc.start(0);
                }} catch(e) {{}}
            }}
            if (actx && actx.state === 'suspended') actx.resume();
        }}

        window.addEventListener('click', () => {{ initAudio(); }}, {{ once: true }});
        window.addEventListener('touchstart', () => {{ initAudio(); }}, {{ once: true }});

        function playPyro() {{
            if (!actx) return;
            const now = actx.currentTime;
            const osc = actx.createOscillator();
            const g = actx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(80, now);
            osc.frequency.exponentialRampToValueAtTime(25, now + 0.35);
            g.gain.setValueAtTime(0.9, now);
            g.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
            osc.connect(g); g.connect(actx.destination);
            osc.start(now); osc.stop(now + 0.36);
        }}

        // =========================================================================
        // 🌍 Three.js シーン ＆ 2画面レンダラー
        // =========================================================================
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a1628);
        const sceneFog = new THREE.FogExp2(0x0e1e36, 0.000025);
        scene.fog = sceneFog;

        const rendererMain = new THREE.WebGLRenderer({{ canvas: canvasMain, antialias: true, powerPreference: "high-performance" }});
        rendererMain.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        rendererMain.setSize(window.innerWidth, window.innerHeight);
        rendererMain.toneMapping = THREE.ACESFilmicToneMapping;
        rendererMain.toneMappingExposure = 1.35;
        rendererMain.shadowMap.enabled = true;
        rendererMain.shadowMap.type = THREE.PCFSoftShadowMap;

        const rendererPip = new THREE.WebGLRenderer({{ canvas: canvasPip, antialias: true, powerPreference: "high-performance" }});
        rendererPip.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        rendererPip.setSize(340, 195);
        rendererPip.toneMapping = THREE.ACESFilmicToneMapping;
        rendererPip.toneMappingExposure = 1.45;

        const cameraMain = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 1.0, 50000000);
        const cameraPip = new THREE.PerspectiveCamera(4.8, 340 / 195, 2.0, 50000000);
        cameraPip.position.set(-1400, 85, 1800);

        const sunLight = new THREE.DirectionalLight(0xfffaed, 5.8);
        sunLight.position.set(7000, 11000, 8000);
        sunLight.castShadow = true;
        scene.add(sunLight);

        const skyAmbient = new THREE.HemisphereLight(0xa5c9eb, 0x1e2733, 1.15);
        scene.add(skyAmbient);

        const engineBounceLight = new THREE.PointLight(simCfg.flame_hex, 0.0, 600, 1.8);
        scene.add(engineBounceLight);

        // 恒星
        const starGeo = new THREE.BufferGeometry();
        const starPos = new Float32Array(3500 * 3);
        for(let i=0; i<3500*3; i+=3) {{
            const rad = 25000000;
            const u = Math.random(), v = Math.random();
            const th = u * 2.0 * Math.PI, ph = Math.acos(2.0 * v - 1.0);
            starPos[i] = rad * Math.sin(ph) * Math.cos(th);
            starPos[i+1] = rad * Math.sin(ph) * Math.sin(th);
            starPos[i+2] = rad * Math.cos(ph);
        }}
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
        const starMat = new THREE.PointsMaterial({{ size: 1.8, color: 0xe2e8f0, transparent: true, opacity: 0.12 }});
        scene.add(new THREE.Points(starGeo, starMat));

        // 地球本体
        const R_EARTH = 6371.0;
        const earthMesh = new THREE.Mesh(
            new THREE.SphereGeometry(R_EARTH, 64, 48),
            new THREE.MeshStandardMaterial({{ color: 0x0c314b, roughness: 0.8 }})
        );
        earthMesh.position.set(0, -R_EARTH, 0);
        scene.add(earthMesh);

        // =========================================================================
        // 🏝️ PBR実写級ケープカナベラル・ランドスケープ＆大西洋海洋マテリアル
        // =========================================================================
        const landscapeGroup = new THREE.Group();
        scene.add(landscapeGroup);

        const coastCvs = document.createElement('canvas'); coastCvs.width = 2048; coastCvs.height = 2048;
        const cctx = coastCvs.getContext('2d');
        cctx.fillStyle = '#061a2e'; cctx.fillRect(0, 0, 2048, 2048);
        
        const surfGrad = cctx.createLinearGradient(0, 0, 1400, 2048);
        surfGrad.addColorStop(0.35, '#0d3b5c');
        surfGrad.addColorStop(0.52, '#145c7a');
        surfGrad.addColorStop(0.58, '#d4b483');
        surfGrad.addColorStop(0.64, '#5d5038');
        surfGrad.addColorStop(0.70, '#2d3b24');
        cctx.fillStyle = surfGrad;
        cctx.beginPath();
        cctx.moveTo(0, 0); cctx.lineTo(1350, 0);
        cctx.bezierCurveTo(1260, 600, 1020, 1300, 880, 2048);
        cctx.lineTo(0, 2048); cctx.closePath(); cctx.fill();

        const coastTex = new THREE.CanvasTexture(coastCvs);
        const coastPlane = new THREE.Mesh(
            new THREE.PlaneGeometry(64000, 64000),
            new THREE.MeshStandardMaterial({{ map: coastTex, roughness: 0.94, metalness: 0.04 }})
        );
        coastPlane.rotation.x = -Math.PI / 2;
        coastPlane.position.set(-2500, -1.6, 0);
        coastPlane.receiveShadow = true;
        landscapeGroup.add(coastPlane);

        const oceanMat = new THREE.MeshStandardMaterial({{
            color: 0x072840, roughness: 0.14, metalness: 0.88, transparent: true, opacity: 0.94
        }});
        const oceanMesh = new THREE.Mesh(new THREE.PlaneGeometry(96000, 96000), oceanMat);
        oceanMesh.rotation.x = -Math.PI / 2;
        oceanMesh.position.set(16000, -1.0, 0);
        landscapeGroup.add(oceanMesh);

        // =========================================================================
        // 🏗️ 発射台 Pad 39A 精密立体構造 ＆ 火炎偏向トレンチ
        // =========================================================================
        const pad = new THREE.Group();
        scene.add(pad);
        const darkSteelMat = new THREE.MeshStandardMaterial({{ color: 0x1f242d, metalness: 0.92, roughness: 0.32 }});
        const concreteMat = new THREE.MeshStandardMaterial({{ color: 0x3d4552, roughness: 0.94 }});
        const pipeMat = new THREE.MeshStandardMaterial({{ color: 0xcbd5e1, metalness: 0.95, roughness: 0.18 }});

        const groundPlate = new THREE.Mesh(new THREE.CylinderGeometry(110, 125, 2.4, 48), concreteMat);
        groundPlate.position.y = -1.2;
        groundPlate.receiveShadow = true;
        pad.add(groundPlate);

        const flameTrench = new THREE.Mesh(new THREE.BoxGeometry(24, 12, 48), concreteMat);
        flameTrench.position.set(0, -6.0, 0);
        pad.add(flameTrench);

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

        // =========================================================================
        // 🔥 ノズル直結流体GLSLバーナー炎＆ショックダイヤモンド (地面貫通防止仕様)
        // =========================================================================
        const plumeShaderMat = new THREE.ShaderMaterial({{
            transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
            uniforms: {{
                uTime: {{ value: 0.0 }},
                uVacFactor: {{ value: 0.0 }},
                uLengthScale: {{ value: 1.0 }},
                uCoreColor: {{ value: new THREE.Color(0xffffff) }},
                uMidColor: {{ value: new THREE.Color(simCfg.flame_hex) }},
                uOuterColor: {{ value: new THREE.Color(simCfg.outer_hex) }}
            }},
            vertexShader: `
                varying vec2 vUv;
                uniform float uTime;
                uniform float uVacFactor;
                uniform float uLengthScale;
                void main() {{
                    vUv = uv;
                    vec3 pos = position;
                    pos.y *= uLengthScale;
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

                    float tipFade = smoothstep(0.0, 0.015, distFromNozzle) * smoothstep(1.0, 0.12, distFromNozzle);
                    float alpha = clamp((plumeBody * 0.95 + coreMask * 0.85) * tipFade * noise, 0.0, 1.0);

                    gl_FragColor = vec4(col * 2.4, alpha);
                }}
            `
        }});

        function createNozzlePlumeMesh(jetWidth, jetLength) {{
            const jetGroup = new THREE.Group();
            for(let rAngle of [0, Math.PI / 2]) {{
                const pPlane = new THREE.Mesh(new THREE.PlaneGeometry(jetWidth, jetLength, 8, 32), plumeShaderMat);
                pPlane.position.y = -jetLength / 2;
                pPlane.rotation.y = rAngle;
                jetGroup.add(pPlane);
            }}
            return jetGroup;
        }}

        const s1NozzleTips = [];
        const s2NozzleTips = [];
        const boosterNozzleTips = [];
        const inconelNozzleMat = new THREE.MeshStandardMaterial({{ color: 0x374151, metalness: 0.95, roughness: 0.22, side: THREE.DoubleSide }});

        function buildDetailedEngineCluster(parent, count, radius, basePosY, epsScale, cycId, tipArray, jetLen) {{
            const group = new THREE.Group();
            group.position.y = basePosY;
            const bellH = 1.15 * epsScale;
            const bellW = 0.24 * Math.pow(epsScale, 0.65);

            const nozzlePts = [];
            for(let i=0; i<=16; i++) {{
                const t = i / 16;
                nozzlePts.push(new THREE.Vector2(0.08 + bellW * Math.pow(t, 0.62), -t * bellH));
            }}
            const bellGeo = new THREE.LatheGeometry(nozzlePts, 24);
            const visualPlumeStep = Math.max(1, Math.floor(count / 6));

            for(let i=0; i<count; i++) {{
                const ang = (i / count) * Math.PI * 2;
                const r = (count === 1) ? 0 : (i < 3 && count > 6 ? radius * 0.38 : radius);
                const engUnit = new THREE.Group();
                engUnit.position.set(Math.cos(ang)*r, 0, Math.sin(ang)*r);

                const bell = new THREE.Mesh(bellGeo, inconelNozzleMat);
                bell.castShadow = true;
                engUnit.add(bell);

                if (i % visualPlumeStep === 0 || i === 0) {{
                    const tipObj = new THREE.Object3D();
                    tipObj.position.set(0, -bellH * 0.92, 0);
                    const plumeMesh = createNozzlePlumeMesh(bellW * 6.5, jetLen);
                    tipObj.add(plumeMesh);
                    engUnit.add(tipObj);
                    tipArray.push({{ node: tipObj, plume: plumeMesh, origLen: jetLen }});
                }}
                group.add(engUnit);
            }}
            parent.add(group);
            return group;
        }}

        // =========================================================================
        // 🚀 ロケット本体＆高精細マテリアル
        // =========================================================================
        const rocket = new THREE.Group();
        rocket.position.y = 6.0;
        scene.add(rocket);

        const s1Mat = new THREE.MeshStandardMaterial({{ color: (simCfg.s1_mat === 'ss') ? 0xd1d5db : 0xf8fafc, roughness: 0.3, metalness: 0.8 }});
        const s2Mat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.35, metalness: 0.5 }});

        const s1Len = simCfg.s1_len;
        const interLen = 2.2;
        const s2Len = simCfg.s2_len;
        const s2BaseY = s1Len + interLen;

        const s1Group = new THREE.Group();
        rocket.add(s1Group);

        const s1Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s1Len, 64), s1Mat);
        s1Body.position.y = s1Len / 2;
        s1Body.castShadow = true;
        s1Group.add(s1Body);

        const s1EpsScale = 0.75 + (simCfg.s1_eps / 70.0) * 0.75;
        const s1Engines = buildDetailedEngineCluster(s1Group, simCfg.s1_eng, 0.78, 0.0, s1EpsScale, simCfg.s1_cyc, s1NozzleTips, 32.0);

        // 外部ブースター群 (Korolev Cross 物理シミュレーター)
        const boosterUnits = [];
        if (simCfg.strapon_count > 0) {{
            const sCount = simCfg.strapon_count;
            for(let i=0; i<sCount; i++) {{
                const angle = (i / sCount) * Math.PI * 2;
                const bx = Math.cos(angle) * 2.15, bz = Math.sin(angle) * 2.15;
                const bUnit = new THREE.Group();
                bUnit.position.set(bx, 0, bz);

                const bLen = s1Len * 0.82;
                const bBody = new THREE.Mesh(new THREE.CylinderGeometry(0.68, 0.68, bLen, 36), s1Mat);
                bBody.position.y = bLen / 2;
                bUnit.add(bBody);

                const bNose = new THREE.Mesh(new THREE.ConeGeometry(0.68, 1.9, 36), s1Mat);
                bNose.position.y = bLen + 0.95; bUnit.add(bNose);

                const localTips = [];
                buildDetailedEngineCluster(bUnit, 1, 0, 0, 1.0, 'sc', localTips, 26.0);
                localTips.forEach(t => boosterNozzleTips.push(t));

                rocket.add(bUnit);
                boosterUnits.push({{
                    mesh: bUnit, angle: angle, baseX: bx, baseZ: bz,
                    detached: false, vx: 0, vy: 0, vz: 0, rx: 0, rz: 0, bLen: bLen, tips: localTips
                }});
            }}
        }}

        // 第2段オービター
        const s2Group = new THREE.Group();
        s2Group.position.y = s2BaseY;
        rocket.add(s2Group);

        const s2Body = new THREE.Mesh(new THREE.CylinderGeometry(1.12, 1.12, s2Len, 64), s2Mat);
        s2Body.position.y = s2Len / 2;
        s2Body.castShadow = true;
        s2Group.add(s2Body);

        const s2EpsScale = 1.0 + (simCfg.s2_eps / 280.0) * 1.1;
        const s2Engines = buildDetailedEngineCluster(s2Group, simCfg.s2_eng, 0.55, 0.0, s2EpsScale, simCfg.s2_cyc, s2NozzleTips, 34.0);
        s2NozzleTips.forEach(t => {{ t.plume.visible = false; }});

        const fairingHalves = [];
        const ogivePts = [];
        const noseH = 5.4;
        for(let i=0; i<=30; i++) {{
            const t = i / 30;
            ogivePts.push(new THREE.Vector2(Math.max(0.01, 1.12 * Math.pow(1.0 - Math.pow(t, 1.65), 0.72)), t * noseH));
        }}
        for(let side of [-1, 1]) {{
            const halfGeo = new THREE.LatheGeometry(ogivePts, 32, (side === 1) ? 0 : Math.PI, Math.PI);
            const halfMesh = new THREE.Mesh(halfGeo, s2Mat);
            halfMesh.position.y = s2Len;
            s2Group.add(halfMesh);
            fairingHalves.push({{ mesh: halfMesh, side: side, detached: false, vx: 0, vy: 0, rotZ: 0 }});
        }}

        // RCSマウントノズル (実機志向)
        const rcsMountNodes = [];
        for(let side of [-1, 1]) {{
            const block = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.45, 0.25), darkSteelMat);
            block.position.set(side * 1.15, s2Len - 0.8, 0);
            s2Group.add(block);
            rcsMountNodes.push({{ node: block, side: side, isS1: false }});
        }}

        // =========================================================================
        // ✨ 自律パーティクルエンジン (水冷水蒸気・煙・火花シャワー)
        // =========================================================================
        const P_MAX = 900;
        const pool = [];
        const pGroup = new THREE.Group(); scene.add(pGroup);
        for(let i=0; i<P_MAX; i++) {{
            const sp = new THREE.Sprite(new THREE.SpriteMaterial({{ transparent: true, opacity: 0, depthWrite: false }}));
            sp.visible = false; pGroup.add(sp);
            pool.push({{ sp, active: false, vx: 0, vy: 0, vz: 0, age: 0, maxAge: 1, s0: 1, s1: 5, o: 0.8 }});
        }}
        let pIdx = 0;
        function emitParticle(x, y, z, vx, vy, vz, s0, s1, life, opacity, hexColor, additive) {{
            const p = pool[pIdx]; pIdx = (pIdx + 1) % P_MAX;
            p.active = true; p.sp.visible = true;
            p.sp.position.set(x, y, z);
            p.vx = vx; p.vy = vy; p.vz = vz;
            p.age = 0; p.maxAge = life; p.s0 = s0; p.s1 = s1; p.o = opacity;
            p.sp.material.color.setHex(hexColor);
            p.sp.material.blending = additive ? THREE.AdditiveBlending : THREE.NormalBlending;
        }}

        function drawOrbitMap(altKm, dRangeKm, exploded) {{
            octx.clearRect(0, 0, 276, 54);
            octx.beginPath(); octx.arc(138, 145, 125, Math.PI, 0); octx.strokeStyle = '#1e293b'; octx.lineWidth = 2.5; octx.stroke();
            const px = 14 + Math.min(248, (dRangeKm / 1200.0) * 248);
            const py = 46 - Math.min(38, (altKm / 200.0) * 38);
            octx.beginPath(); octx.moveTo(14, 46); octx.quadraticCurveTo(px * 0.5, 46, px, py);
            octx.strokeStyle = exploded ? '#ef4444' : '#38bdf8'; octx.lineWidth = 1.8; octx.stroke();
            octx.fillStyle = exploded ? '#dc2626' : '#38bdf8';
            octx.beginPath(); octx.arc(px, py, 3.5, 0, Math.PI * 2); octx.fill();
        }}

        // =========================================================================
        // ⏱️ アニメーション・メインループ
        // =========================================================================
        const tStart = performance.now();
        let boosterDetached = false;
        let stage1Detached = false;
        let fairingDetached = false;
        let s1Vel = {{ vx: 0, vy: 0, rotZ: 0 }};
        let prevPitch = 0.0;
        const tempTipPos = new THREE.Vector3();
        const activeFocusWorld = new THREE.Vector3();
        const smoothOffset = new THREE.Vector3(75.0, 26.0, 145.0);

        function animate(now) {{
            requestAnimationFrame(animate);

            const elapsedSec = (now - tStart) / 1000.0;
            const simT = simCfg.is_preview ? -10.0 : (-10.0 + elapsedSec);
            plumeShaderMat.uniforms.uTime.value = elapsedSec;

            if (!simCfg.is_preview) {{
                updateFlightCallouts(simT);
            }}

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

            if (simT > simData[simData.length - 1].t) {{
                const overT = simT - simData[simData.length - 1].t;
                rx += vel * overT * 0.1;
                q = 0.0; accG = 0.0;
            }}

            const dRangeKm = (rx * 10.0) / 1000.0;

            rocket.position.set(rx, ry + 6.0, 0);
            rocket.rotation.z = -pitch;
            rocket.updateMatrixWorld(true);

            // 火炎の地面貫通防止（ロケット高度に応じて長さをスケール）
            const groundClearance = Math.max(0.05, Math.min(1.0, (ry + 6.0) / 30.0));
            plumeShaderMat.uniforms.uLengthScale.value = groundClearance;

            const ux = Math.sin(pitch), uy = Math.cos(pitch);
            const perpX = Math.cos(pitch), perpY = -Math.sin(pitch);

            // ブースター自然な分離物理 (ゆっくり放射状に離脱)
            if (!p0.strapon && !boosterDetached && boosterUnits.length > 0 && !simCfg.is_preview) {{
                boosterDetached = true;
                playPyro();

                for(let b of boosterUnits) {{
                    b.detached = true;
                    b.tips.forEach(t => {{ t.plume.visible = false; }});
                    scene.attach(b.mesh);
                    const outX = Math.cos(b.angle);
                    const outZ = Math.sin(b.angle);
                    const sepP = simCfg.sep_thrust * 0.45;
                    b.vx = ux * (vel * 0.068) + perpX * outX * (1.2 * sepP);
                    b.vy = uy * (vel * 0.068) + perpY * outX * (1.2 * sepP) - 0.4;
                    b.vz = outZ * (1.2 * sepP);
                    b.rx = outZ * 0.25;
                    b.rz = -outX * 0.25;
                }}
            }}
            if (boosterDetached) {{
                for(let b of boosterUnits) {{
                    b.mesh.position.x += b.vx * 0.016;
                    b.mesh.position.y += b.vy * 0.016;
                    b.mesh.position.z += b.vz * 0.016;
                    b.vy -= 9.8 * 0.016 * 0.35;
                    b.mesh.rotation.x += b.rx * 0.016;
                    b.mesh.rotation.z += b.rz * 0.016;
                }}
            }}

            // 第1段分離
            if (p0.stage === 2 && !stage1Detached && !simCfg.is_preview) {{
                stage1Detached = true;
                playPyro();
                s1NozzleTips.forEach(t => {{ t.plume.visible = false; }});
                s2NozzleTips.forEach(t => {{ t.plume.visible = true; }});
                plumeShaderMat.uniforms.uMidColor.value.setHex(simCfg.s2_flame_hex);
                scene.attach(s1Group);
                s1Vel.vx = ux * (vel * 0.068) - ux * 3.2;
                s1Vel.vy = uy * (vel * 0.068) - uy * 3.2;
                s1Vel.rotZ = 0.22;
            }}
            if (stage1Detached) {{
                s1Group.position.x += s1Vel.vx * 0.016;
                s1Group.position.y += s1Vel.vy * 0.016;
                s1Vel.vy -= 9.8 * 0.016 * 0.6;
                s1Group.rotation.z += s1Vel.rotZ * 0.016;
            }}

            // 火炎と煙
            if (p0.thrust && !p0.exploded && !simCfg.is_preview) {{
                const vacFactor = Math.min(1.0, alt / 65.0);
                plumeShaderMat.uniforms.uVacFactor.value = vacFactor;
                const activeTips = (p0.stage === 1) ? [...s1NozzleTips] : [...s2NozzleTips];
                if (p0.stage === 1 && !boosterDetached) activeTips.push(...boosterNozzleTips);

                for(let tObj of activeTips) {{
                    tObj.plume.visible = true;
                    tObj.node.getWorldPosition(tempTipPos);

                    if (alt < 30.0 && Math.random() < 0.35) {{
                        emitParticle(
                            tempTipPos.x - ux * 1.5, Math.max(0.2, tempTipPos.y - uy * 1.5), tempTipPos.z,
                            -ux * 0.5 + (Math.random()-0.5)*0.3, -uy * 0.5, (Math.random()-0.5)*0.3,
                            3.5, 24.0, 60, 0.65, 0xf1f5f9, false
                        );
                    }}
                }}
            }} else {{
                s1NozzleTips.forEach(t => {{ t.plume.visible = false; }});
                s2NozzleTips.forEach(t => {{ t.plume.visible = false; }});
                boosterNozzleTips.forEach(t => {{ t.plume.visible = false; }});
            }}

            // スラスター (実機姿勢制御挙動)
            const pitchRate = (pitch - prevPitch) / 0.016;
            prevPitch = pitch;
            let rcsFiring = false;
            const dampingNeeded = (Math.abs(pitchRate) > 0.005);
            const pulseClock = (now % 600) < 100;

            for(let rcs of rcsMountNodes) {{
                let shouldFire = false;
                if (!simCfg.is_preview && simT > 2.0 && pulseClock && !rcs.isS1) {{
                    if (dampingNeeded && pitchRate > 0 && rcs.side === 1) shouldFire = true;
                    if (dampingNeeded && pitchRate < 0 && rcs.side === -1) shouldFire = true;
                }}
                if (shouldFire) {{
                    rcsFiring = true;
                    rcs.node.getWorldPosition(tempTipPos);
                    emitParticle(
                        tempTipPos.x + perpX * rcs.side * 0.3, tempTipPos.y + perpY * rcs.side * 0.3, tempTipPos.z,
                        perpX * rcs.side * 3.5, perpY * rcs.side * 3.5, 0,
                        0.3, 2.0, 10, 0.9, 0xf0f9ff, false
                    );
                }}
            }}
            document.getElementById('hud-rcs').innerText = rcsFiring ? "PULSE FIRING (GN2)" : "STANDBY (DEADBAND OK)";
            document.getElementById('hud-rcs').style.color = rcsFiring ? "#34d399" : "#38bdf8";

            // カメラ追随
            rocket.updateMatrixWorld(true);
            activeFocusWorld.set(0, s1Len * 0.5, 0);
            rocket.localToWorld(activeFocusWorld);
            cameraPip.lookAt(activeFocusWorld);
            document.getElementById('pip-hud-alt').innerText = `ALT: ${{Math.max(0, alt).toFixed(1)}} km`;

            if (simCfg.is_preview) {{
                const orbitAng = elapsedSec * 0.2;
                cameraMain.position.set(Math.sin(orbitAng)*115.0, 28.0, Math.cos(orbitAng)*115.0);
            }} else {{
                smoothOffset.set(-70.0, -14.0, 140.0);
                cameraMain.position.copy(activeFocusWorld).add(smoothOffset);
            }}
            cameraMain.lookAt(activeFocusWorld);

            drawOrbitMap(alt, dRangeKm, p0.exploded);

            // カウントダウン表示
            if (simT < 0.0) {{
                const sec = Math.ceil(Math.abs(simT));
                document.getElementById('tv-timer').innerText = simCfg.is_preview ? "PAD INSPECTION" : `T- 00:0${{sec}}.0`;
            }} else {{
                const m = Math.floor(simT / 60); const s = simT % 60;
                document.getElementById('tv-timer').innerText = `T+ ${{String(m).padStart(2,'0')}}:${{s.toFixed(1).padStart(4,'0')}}`;
            }}

            // パーティクル更新
            for(let i=0; i<P_MAX; i++) {{
                const p = pool[i]; if (!p.active) continue;
                p.age++;
                if (p.age >= p.maxAge) {{ p.active = false; p.sp.visible = false; continue; }}
                p.sp.position.x += p.vx; p.sp.position.y += p.vy; p.sp.position.z += p.vz;
                const pr = p.age / p.maxAge;
                const curScale = p.s0 + (p.s1 - p.s0) * Math.pow(pr, 0.7);
                p.sp.scale.set(curScale, curScale, 1);
                p.sp.material.opacity = p.o * (1.0 - pr * pr);
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

            if (p0.exploded) {{
                rudBanner.style.display = 'block';
                rudDesc.innerText = failMessage || "機体過負荷による空中分解";
            }}

            cameraMain.aspect = window.innerWidth / window.innerHeight;
            cameraMain.updateProjectionMatrix();
            rendererMain.render(scene, cameraMain);

            if (pipVisible) {{
                cameraPip.aspect = 340 / 195;
                cameraPip.updateProjectionMatrix();
                rendererPip.render(scene, cameraPip);
            }}
        }}

        requestAnimationFrame(animate);

        window.addEventListener('resize', () => {{
            rendererMain.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""
    return html_code
