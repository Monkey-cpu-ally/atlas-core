/* ============================================================
   HUD-FIRST LAYOUT ENGINE
   Makes the ring system the primary home screen.
   Content panels open from ring segment clicks.
   ============================================================ */
(function() {
    'use strict';

    const CX = 290, CY = 290;
    const DEG = Math.PI / 180;

    const COLORS = {
        ajani:   { primary: '#e84040', glow: 'rgba(232,64,64,' },
        minerva: { primary: '#00d4aa', glow: 'rgba(0,212,170,' },
        hermes:  { primary: '#d4d0c8', glow: 'rgba(212,208,200,' },
        counsel: { primary: '#9b7edb', glow: 'rgba(155,126,219,' },
    };

    const RING1 = {
        segments: ['ajani', 'minerva', 'hermes', 'counsel'],
        labels:   ['AJANI', 'MINERVA', 'HERMES', 'COUNCIL'],
        innerR: 65, outerR: 105, gap: 5
    };
    const RING2 = {
        segments: ['chat', 'memory', 'monitor', 'tools', 'settings', 'explore'],
        labels:   ['CHAT', 'MEMORY', 'MONITOR', 'TOOLS', 'SETTINGS', 'EXPLORE'],
        innerR: 120, outerR: 155, gap: 3
    };
    const RING3 = {
        segments: ['subjects', 'lab', 'projects', 'blueprints', 'forge', 'archive'],
        labels:   ['SUBJECTS', 'LAB', 'PROJECTS', 'BLUEPRINTS', 'FORGE', 'ARCHIVE'],
        innerR: 170, outerR: 210, gap: 3
    };

    let activePersona = 'ajani';
    let ring2Selected = null;
    let ring3Selected = null;

    function polarToCart(cx, cy, r, angleDeg) {
        const rad = (angleDeg - 90) * DEG;
        return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
    }

    function arcPath(innerR, outerR, startDeg, endDeg) {
        const s1 = polarToCart(CX, CY, outerR, startDeg);
        const e1 = polarToCart(CX, CY, outerR, endDeg);
        const s2 = polarToCart(CX, CY, innerR, endDeg);
        const e2 = polarToCart(CX, CY, innerR, startDeg);
        const large = (endDeg - startDeg) > 180 ? 1 : 0;
        return `M ${s1.x} ${s1.y} A ${outerR} ${outerR} 0 ${large} 1 ${e1.x} ${e1.y} L ${s2.x} ${s2.y} A ${innerR} ${innerR} 0 ${large} 0 ${e2.x} ${e2.y} Z`;
    }

    function labelPos(outerR, startDeg, endDeg) {
        const mid = (startDeg + endDeg) / 2;
        return polarToCart(CX, CY, outerR + 20, mid);
    }

    function buildHomeSVG() {
        const svg = document.getElementById('hudHomeSvg');
        const labelsDiv = document.getElementById('hudHomeLabels');
        if (!svg) return;

        let s = '';
        let labels = '';

        s += `<defs>
            <filter id="hGlow"><feGaussianBlur stdDeviation="4"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter>
            <filter id="hCoreGlow"><feGaussianBlur stdDeviation="8"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter>
            <filter id="hRing2Shadow" x="-10%" y="-10%" width="120%" height="130%">
                <feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="rgba(0,0,0,0.3)" flood-opacity="0.3"/>
            </filter>
            <filter id="hRing3Shadow" x="-10%" y="-10%" width="120%" height="130%">
                <feDropShadow dx="0" dy="5" stdDeviation="3" flood-color="rgba(0,0,0,0.35)" flood-opacity="0.35"/>
            </filter>
            <radialGradient id="hCoreBg"><stop offset="0%" stop-color="${COLORS.ajani.primary}" stop-opacity="0.12" class="h-core-grad"/><stop offset="100%" stop-color="transparent"/></radialGradient>
        </defs>`;

        // Guide circles
        [58, 115, 165].forEach(r => {
            s += `<circle cx="${CX}" cy="${CY}" r="${r}" fill="none" stroke="rgba(255,255,255,0.02)" stroke-width="0.5"/>`;
        });

        // Core
        s += `<circle cx="${CX}" cy="${CY}" r="50" fill="url(#hCoreBg)" filter="url(#hCoreGlow)" id="hCoreGlow"/>`;
        s += `<circle cx="${CX}" cy="${CY}" r="42" fill="rgba(8,8,14,0.95)" stroke="${COLORS.ajani.primary}" stroke-width="1.5" id="hCoreRing" style="cursor:pointer;transition:stroke 0.3s" onclick="window.HudLayout.openChat()"/>`;
        s += `<text x="${CX}" y="${CY-6}" text-anchor="middle" dominant-baseline="central" font-size="18" fill="${COLORS.ajani.primary}" id="hCoreIcon" style="pointer-events:none;transition:fill 0.3s">⬡</text>`;
        s += `<text x="${CX}" y="${CY+14}" text-anchor="middle" font-size="7" fill="rgba(200,200,220,0.3)" letter-spacing="2" style="pointer-events:none">SPEAK</text>`;

        // Ring 1
        s += `<g id="hRing1">`;
        const s1 = 360 / RING1.segments.length;
        RING1.segments.forEach((id, i) => {
            const start = i * s1 + RING1.gap / 2;
            const end = (i + 1) * s1 - RING1.gap / 2;
            const col = COLORS[id].primary;
            const op = i === 0 ? '0.7' : '0.15';
            s += `<path d="${arcPath(RING1.innerR, RING1.outerR, start, end)}" fill="${col}" opacity="${op}" stroke="${col}" stroke-width="0.8" stroke-opacity="0.4" style="cursor:pointer;transition:opacity 0.3s" data-ring="1" data-id="${id}" onclick="window.HudLayout.selectPersona('${id}')" filter="url(#hGlow)" id="h-r1-${id}"/>`;
            const lp = labelPos(RING1.outerR, start, end);
            labels += `<div class="hud-label ring1-label" id="h-l1-${id}" style="left:${lp.x}px;top:${lp.y}px">${RING1.labels[i]}</div>`;
        });
        s += `</g>`;

        // Ring 2 — slightly elevated
        s += `<g id="hRing2" filter="url(#hRing2Shadow)">`;
        const s2 = 360 / RING2.segments.length;
        RING2.segments.forEach((id, i) => {
            const start = i * s2 + RING2.gap / 2;
            const end = (i + 1) * s2 - RING2.gap / 2;
            s += `<path d="${arcPath(RING2.innerR, RING2.outerR, start, end)}" fill="rgba(100,140,180,0.08)" stroke="rgba(100,140,180,0.2)" stroke-width="0.6" style="cursor:pointer;transition:all 0.25s" data-ring="2" data-id="${id}" onclick="window.HudLayout.selectR2('${id}')" id="h-r2-${id}"/>`;
            for (let t = start + 3; t < end; t += 5) {
                const tp1 = polarToCart(CX, CY, RING2.innerR, t);
                const tp2 = polarToCart(CX, CY, RING2.innerR + 4, t);
                s += `<line x1="${tp1.x}" y1="${tp1.y}" x2="${tp2.x}" y2="${tp2.y}" stroke="rgba(100,140,180,0.08)" stroke-width="0.5"/>`;
            }
            const lp = labelPos(RING2.outerR, start, end);
            labels += `<div class="hud-label ring2-label" id="h-l2-${id}" style="left:${lp.x}px;top:${lp.y}px">${RING2.labels[i]}</div>`;
        });
        s += `</g>`;

        // Ring 3 — highest elevation in 2.5D
        s += `<g id="hRing3" filter="url(#hRing3Shadow)">`;
        const s3 = 360 / RING3.segments.length;
        RING3.segments.forEach((id, i) => {
            const start = i * s3 + RING3.gap / 2;
            const end = (i + 1) * s3 - RING3.gap / 2;
            s += `<path d="${arcPath(RING3.innerR, RING3.outerR, start, end)}" fill="rgba(120,180,140,0.06)" stroke="rgba(120,180,140,0.18)" stroke-width="0.6" style="cursor:pointer;transition:all 0.3s" data-ring="3" data-id="${id}" onclick="window.HudLayout.selectR3('${id}')" id="h-r3-${id}"/>`;
            const lp = labelPos(RING3.outerR, start, end);
            labels += `<div class="hud-label ring3-label" id="h-l3-${id}" style="left:${lp.x}px;top:${lp.y}px">${RING3.labels[i]}</div>`;
        });
        s += `</g>`;

        svg.innerHTML = s;
        if (labelsDiv) labelsDiv.innerHTML = labels;
    }

    // ── Persona selection ──
    function selectPersona(persona) {
        activePersona = persona;
        const col = COLORS[persona];
        if (!col) return;

        document.getElementById('hCoreRing')?.setAttribute('stroke', col.primary);
        document.getElementById('hCoreIcon')?.setAttribute('fill', col.primary);
        document.querySelector('.h-core-grad')?.setAttribute('stop-color', col.primary);

        RING1.segments.forEach(id => {
            const seg = document.getElementById(`h-r1-${id}`);
            const label = document.getElementById(`h-l1-${id}`);
            if (seg) seg.setAttribute('opacity', id === persona ? '0.7' : '0.12');
            if (label) {
                label.className = id === persona ? `hud-label ring1-label active active-${persona}` : 'hud-label ring1-label';
            }
        });

        const status = document.getElementById('hudHomeStatus');
        const names = { ajani: 'AJANI · TACTICAL', minerva: 'MINERVA · CULTURAL', hermes: 'HERMES · SYSTEMS', counsel: 'COUNCIL · TRI-CORE' };
        if (status) {
            status.textContent = `ATLAS-PRIME · ${names[persona]} · ACTIVE`;
            status.style.color = col.glow + '0.5)';
        }

        if (typeof window.selectPersona === 'function') {
            window.selectPersona(persona);
        }
    }

    // ── Ring 2 selection ──
    function selectR2(id) {
        ring2Selected = id;
        RING2.segments.forEach(sid => {
            const seg = document.getElementById(`h-r2-${sid}`);
            const label = document.getElementById(`h-l2-${sid}`);
            if (seg) {
                seg.setAttribute('fill', sid === id ? 'rgba(100,140,180,0.25)' : 'rgba(100,140,180,0.06)');
                seg.setAttribute('stroke-opacity', sid === id ? '0.6' : '0.15');
            }
            if (label) label.className = sid === id ? 'hud-label ring2-label active' : 'hud-label ring2-label';
        });

        if (id === 'chat') {
            openChat();
        } else {
            openContentPanel(RING2.labels[RING2.segments.indexOf(id)], getR2Content(id));
        }
    }

    // ── Ring 3 selection ──
    function selectR3(id) {
        ring3Selected = id;
        RING3.segments.forEach(sid => {
            const seg = document.getElementById(`h-r3-${sid}`);
            const label = document.getElementById(`h-l3-${sid}`);
            if (seg) {
                seg.setAttribute('fill', sid === id ? 'rgba(120,180,140,0.22)' : 'rgba(120,180,140,0.04)');
                seg.setAttribute('stroke-opacity', sid === id ? '0.5' : '0.12');
            }
            if (label) {
                label.className = sid === id ? 'hud-label ring3-label active' : 'hud-label ring3-label';
                if (sid === id) { label.style.color = 'rgba(120,220,160,0.9)'; label.style.textShadow = '0 0 8px rgba(120,180,140,0.4)'; }
                else { label.style.color = ''; label.style.textShadow = ''; }
            }
        });
        openContentPanel(RING3.labels[RING3.segments.indexOf(id)], getR3Content(id));
    }

    // ── Content panel ──
    function openContentPanel(title, html) {
        closeChatPanel();
        const panel = document.getElementById('hudContentPanel');
        document.getElementById('hudCPTitle').textContent = title;
        document.getElementById('hudCPBody').innerHTML = html;
        panel.classList.add('open');
        document.body.classList.add('panel-open');
    }

    function closeContentPanel() {
        document.getElementById('hudContentPanel')?.classList.remove('open');
        document.body.classList.remove('panel-open');
    }

    // ── Chat panel ──
    let chatMessages = [];

    function openChat() {
        closeContentPanel();
        const panel = document.getElementById('hudChatPanel');
        panel.classList.add('open');
        document.body.classList.add('panel-open');
        updateChatPersonaLabel();
        document.getElementById('hudChatInput')?.focus();
    }

    function closeChatPanel() {
        document.getElementById('hudChatPanel')?.classList.remove('open');
        document.body.classList.remove('panel-open');
    }

    function updateChatPersonaLabel() {
        const label = document.getElementById('hudChatPersonaLabel');
        const names = { ajani: 'Ajani', minerva: 'Minerva', hermes: 'Hermes', counsel: 'Trinity Counsel' };
        if (label) label.textContent = `CHAT · ${(names[activePersona] || 'AI').toUpperCase()}`;
    }

    function addChatMessage(role, text) {
        const container = document.getElementById('hudChatMessages');
        if (!container) return;
        const msg = document.createElement('div');
        msg.className = `hud-chat-msg ${role}`;
        if (role === 'ai') {
            const names = { ajani: 'AJANI', minerva: 'MINERVA', hermes: 'HERMES', counsel: 'COUNCIL' };
            msg.innerHTML = `<div class="persona-tag">${names[activePersona] || 'AI'}</div>${text}`;
        } else {
            msg.textContent = text;
        }
        container.appendChild(msg);
        container.scrollTop = container.scrollHeight;
    }

    async function sendChatMessage() {
        const input = document.getElementById('hudChatInput');
        if (!input) return;
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        addChatMessage('user', text);

        try {
            const endpoint = activePersona === 'counsel' ? '/counsel' : '/chat';
            const body = activePersona === 'counsel'
                ? { message: text }
                : { persona: activePersona, message: text };
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await res.json();
            const reply = data.response || data.message || data.text || JSON.stringify(data);
            addChatMessage('ai', reply);
        } catch (e) {
            addChatMessage('ai', 'Connection error. The AI service may need a valid API key.');
        }
    }

    // ── Content generators ──
    function getR2Content(id) {
        const map = {
            memory: `<h3>Memory Store</h3><p>Your conversation history, saved insights, and learning progress across all personas.</p><div id="r2MemoryContent"><p style="color:rgba(200,200,220,0.3)">Loading...</p></div>`,
            monitor: `<h3>System Monitor</h3><p>Real-time system health and API status.</p><div id="r2MonitorContent"><p style="color:rgba(200,200,220,0.3)">Loading...</p></div>`,
            tools: `<h3>Tools</h3><p>Calculator, code runner, and persona tools.</p><div id="r2ToolsContent"><p style="color:rgba(200,200,220,0.3)">Loading...</p></div>`,
            settings: `<h3>Settings</h3><p>Theme preferences, persona configuration, and UI customization.</p>`,
            explore: `<h3>Explore Mode</h3><p>Free exploration — discover new fields, hidden content, and experimental features.</p>`,
        };
        const html = map[id] || `<p>${id}</p>`;
        if (id === 'monitor') setTimeout(loadMonitorData, 100);
        if (id === 'tools') setTimeout(loadToolsData, 100);
        if (id === 'memory') setTimeout(loadMemoryData, 100);
        return html;
    }

    function getR3Content(id) {
        const map = {
            subjects: `<h3>Fields of Study</h3><p>Choose a domain to explore. Each persona brings a unique perspective.</p><div id="r3SubjectsContent"><p style="color:rgba(200,200,220,0.3)">Loading...</p></div>`,
            lab: `<h3>Lab</h3><p>Interactive experiments and simulations with real-time feedback.</p><div id="r3LabContent"><p style="color:rgba(200,200,220,0.3)">Loading...</p></div>`,
            projects: `<h3>Projects</h3><p>Your personal project tracker with LEGO-style build steps.</p><div id="r3ProjectsContent"><p style="color:rgba(200,200,220,0.3)">Loading...</p></div>`,
            blueprints: `<h3>Blueprints</h3><p>Engineering blueprints with 3D viewer and assembly instructions.</p><div id="r3BlueprintsContent"><p style="color:rgba(200,200,220,0.3)">Loading...</p></div>`,
            forge: `<h3>Forge</h3><p>Safety-first robotic blueprint templates.</p><div id="r3ForgeContent"><p style="color:rgba(200,200,220,0.3)">Loading...</p></div>`,
            archive: `<h3>Archive</h3><p>Past research, completed lessons, and exported materials.</p><div id="r3ArchiveContent"><p style="color:rgba(200,200,220,0.3)">Loading...</p></div>`,
        };
        const html = map[id] || `<p>${id}</p>`;
        if (id === 'subjects') setTimeout(loadSubjects, 100);
        if (id === 'projects') setTimeout(loadProjects, 100);
        if (id === 'forge') setTimeout(loadForge, 100);
        if (id === 'blueprints') setTimeout(loadBlueprints, 100);
        if (id === 'lab') setTimeout(loadLessons, 100);
        if (id === 'archive') setTimeout(loadArchive, 100);
        return html;
    }

    // ── Live data loaders ──
    async function loadMonitorData() {
        try {
            const [health, identity] = await Promise.all([
                fetch('/health').then(r => r.json()),
                fetch('/identity').then(r => r.json()),
            ]);
            const el = document.getElementById('r2MonitorContent');
            if (el) el.innerHTML = `
                <div style="margin-top:12px;font-family:monospace;font-size:0.75rem;line-height:2;color:rgba(200,200,220,0.5)">
                    <div>STATUS: <span style="color:rgba(90,154,138,0.9)">${health.ok ? 'ONLINE' : 'OFFLINE'}</span></div>
                    <div>VERSION: ${health.version}</div>
                    <div>CODENAME: ${identity.codename}</div>
                    <div>FINGERPRINT: ${identity.fingerprint}</div>
                    <div style="margin-top:8px;font-size:0.65rem;color:rgba(200,200,220,0.3)">PRINCIPLES:</div>
                    ${(identity.principles||[]).map(p => `<div style="font-size:0.65rem;color:rgba(200,200,220,0.3)">  ${p}</div>`).join('')}
                </div>`;
        } catch(e) { /* silent */ }
    }

    async function loadToolsData() {
        try {
            const data = await fetch('/tools').then(r => r.json());
            const el = document.getElementById('r2ToolsContent');
            if (el) el.innerHTML = (data.tools||[]).map(t =>
                `<div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.03)"><strong style="color:rgba(200,200,220,0.7)">${t.name}</strong><br><span style="font-size:0.75rem">${t.description||''}</span></div>`
            ).join('');
        } catch(e) { /* silent */ }
    }

    async function loadMemoryData() {
        try {
            const data = await fetch('/conversations').then(r => r.json());
            const el = document.getElementById('r2MemoryContent');
            if (el) el.innerHTML = (data.conversations||[]).length === 0
                ? '<p style="color:rgba(200,200,220,0.3)">No saved conversations yet.</p>'
                : (data.conversations||[]).map(c => `<div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.03)">${c.persona} · ${c.message_count} messages</div>`).join('');
        } catch(e) { /* silent */ }
    }

    async function loadSubjects() {
        try {
            const personas = ['ajani', 'minerva', 'hermes'];
            const results = await Promise.all(personas.map(p => fetch(`/lessons/${p}/fields`).then(r => r.json())));
            const el = document.getElementById('r3SubjectsContent');
            if (!el) return;
            let html = '';
            results.forEach((data, i) => {
                if (data.fields) {
                    html += `<div style="margin-top:12px;font-size:0.65rem;letter-spacing:2px;color:rgba(200,200,220,0.3);text-transform:uppercase">${personas[i]}</div>`;
                    data.fields.forEach(f => {
                        html += `<div style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.03);color:rgba(200,200,220,0.6);font-size:0.8rem">${f.name || f.id}</div>`;
                    });
                }
            });
            el.innerHTML = html || '<p>No fields found.</p>';
        } catch(e) { /* silent */ }
    }

    async function loadProjects() {
        try {
            const data = await fetch('/project-specs').then(r => r.json());
            const el = document.getElementById('r3ProjectsContent');
            if (el) el.innerHTML = (data.projects||[]).map(p =>
                `<div style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03)"><strong style="color:rgba(200,200,220,0.7)">${p.name||p.id}</strong><br><span style="font-size:0.75rem">${p.purpose||''}</span></div>`
            ).join('') || '<p>No projects found.</p>';
        } catch(e) { /* silent */ }
    }

    async function loadForge() {
        try {
            const data = await fetch('/forge/templates').then(r => r.json());
            const el = document.getElementById('r3ForgeContent');
            if (el) el.innerHTML = (data.templates||[]).map(t =>
                `<div style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03)"><strong style="color:rgba(200,200,220,0.7)">${t.name}</strong> <span style="font-size:0.7rem;color:rgba(90,154,138,0.5)">${t.biomimic}</span><br><span style="font-size:0.75rem">Task: ${t.task} · ${t.payload_kg}kg</span></div>`
            ).join('');
        } catch(e) { /* silent */ }
    }

    async function loadBlueprints() {
        try {
            const data = await fetch('/atlas/projects').then(r => r.json());
            const el = document.getElementById('r3BlueprintsContent');
            if (el) el.innerHTML = (data.projects||[]).map(p =>
                `<div style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03)"><strong style="color:rgba(200,200,220,0.7)">${p.versions?.[0]?.title || p.project_slug}</strong><br><span style="font-size:0.75rem">${p.versions?.[0]?.domain || ''} · ${p.versions?.[0]?.safety_tier || ''}</span></div>`
            ).join('') || '<p>No blueprints stored yet.</p>';
        } catch(e) { /* silent */ }
    }

    async function loadLessons() {
        try {
            const data = await fetch('/lego-lessons').then(r => r.json());
            const el = document.getElementById('r3LabContent');
            if (el) el.innerHTML = (data.lessons||[]).map(l =>
                `<div style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.03)"><strong style="color:rgba(200,200,220,0.7)">${l.title}</strong> <span style="font-size:0.7rem;color:rgba(90,154,138,0.5)">${l.persona}</span><br><span style="font-size:0.75rem">${l.goal} · ${l.steps_count} steps</span></div>`
            ).join('');
        } catch(e) { /* silent */ }
    }

    async function loadArchive() {
        try {
            const data = await fetch('/research').then(r => r.json());
            const el = document.getElementById('r3ArchiveContent');
            if (!el) return;
            let html = '';
            for (const [persona, info] of Object.entries(data)) {
                html += `<div style="margin-top:12px;font-size:0.65rem;letter-spacing:2px;color:rgba(200,200,220,0.3);text-transform:uppercase">${persona} · ${info.domain||''}</div>`;
                (info.projects||[]).forEach(p => {
                    html += `<div style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.03);color:rgba(200,200,220,0.6);font-size:0.8rem">${p.name} <span style="font-size:0.65rem;color:rgba(200,200,220,0.3)">${p.phase}</span></div>`;
                });
            }
            el.innerHTML = html;
        } catch(e) { /* silent */ }
    }

    // ── Layout mode toggle ──
    function switchToClassic() {
        document.body.classList.remove('hud-mode');
        closeContentPanel();
        closeChatPanel();
    }

    function switchToHUD() {
        document.body.classList.add('hud-mode');
    }

    // ── Keyboard ──
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (document.getElementById('hudChatPanel')?.classList.contains('open')) {
                closeChatPanel();
            } else if (document.getElementById('hudContentPanel')?.classList.contains('open')) {
                closeContentPanel();
            }
        }
    });

    // ── Public API ──
    window.HudLayout = {
        selectPersona: selectPersona,
        selectR2: selectR2,
        selectR3: selectR3,
        openChat: openChat,
        closeChat: closeChatPanel,
        closePanel: closeContentPanel,
        sendChat: sendChatMessage,
        switchToClassic: switchToClassic,
        switchToHUD: switchToHUD,
    };

    // ── Init ──
    document.addEventListener('DOMContentLoaded', function() {
        document.body.classList.add('hud-mode');
        buildHomeSVG();
        selectPersona('ajani');

        const chatInput = document.getElementById('hudChatInput');
        if (chatInput) {
            chatInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendChatMessage();
                }
            });
        }
    });
})();
