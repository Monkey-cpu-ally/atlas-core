/* ============================================================
   ATLAS CORE — CINEMATIC UPGRADE ENGINE
   Boot sequence + scroll reveals + micro-interactions
   ============================================================ */
(function() {
    'use strict';

    // ── Boot Sequence ──
    const BOOT_LINES = [
        ['[CORE]    Initializing ATLAS-PRIME kernel...', 600],
        ['[CORE]    Version 0.3.1 · Fingerprint 63310066', 400],
        ['[MEMORY]  Loading persona memory stores... <span class="ok">OK</span>', 350],
        ['[GUARD]   Safety kernel armed · Refusal engine online... <span class="ok">OK</span>', 400],
        ['[PERSONA] Ajani  (Tactical)  — <span class="ok">READY</span>', 250],
        ['[PERSONA] Minerva (Cultural) — <span class="ok">READY</span>', 250],
        ['[PERSONA] Hermes  (Systems)  — <span class="ok">READY</span>', 250],
        ['[FORGE]   Cauldron factory initialized... <span class="ok">OK</span>', 300],
        ['[DB]      PostgreSQL connection pool... <span class="ok">CONNECTED</span>', 350],
        ['[ROUTER]  Mounting 18 API routers... <span class="ok">OK</span>', 300],
        ['[TRI]     Trinity Counsel mode... <span class="ok">STANDING BY</span>', 350],
        ['[HUD]     Ring animation system... <span class="ok">LOADED</span>', 250],
        ['[SYSTEM]  All checks passed. Launching interface.', 500],
    ];

    function createBootOverlay() {
        if (sessionStorage.getItem('atlas-booted')) return null;

        const overlay = document.createElement('div');
        overlay.id = 'bootOverlay';

        overlay.innerHTML = `
            <div class="boot-logo">ATLAS-PRIME</div>
            <div class="boot-sub">AI PERSONA EDUCATIONAL SYSTEM</div>
            <div class="boot-terminal" id="bootTerminal"></div>
            <div class="boot-bar"><div class="boot-bar-fill" id="bootBarFill"></div></div>
        `;

        document.body.prepend(overlay);
        return overlay;
    }

    async function runBootSequence(overlay) {
        if (!overlay) return;

        await sleep(300);

        const logo = overlay.querySelector('.boot-logo');
        const sub = overlay.querySelector('.boot-sub');
        const terminal = document.getElementById('bootTerminal');
        const bar = overlay.querySelector('.boot-bar');
        const fill = document.getElementById('bootBarFill');

        logo.classList.add('visible');
        await sleep(600);
        sub.classList.add('visible');
        bar.classList.add('visible');
        await sleep(400);

        for (let i = 0; i < BOOT_LINES.length; i++) {
            const [text, delay] = BOOT_LINES[i];
            const line = document.createElement('div');
            line.className = 'boot-line';
            line.innerHTML = text;
            terminal.appendChild(line);
            await sleep(60);
            line.classList.add('visible');
            fill.style.width = ((i + 1) / BOOT_LINES.length * 100) + '%';
            await sleep(delay);
        }

        await sleep(400);
        overlay.classList.add('fade-out');
        await sleep(600);
        overlay.remove();
        sessionStorage.setItem('atlas-booted', '1');
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // ── Scroll Reveal ──
    function initScrollReveal() {
        const sections = document.querySelectorAll(
            '.dashboard-card, .persona-card, .field-card, ' +
            'h2, h3, .api-section, [class*="section"]'
        );

        sections.forEach(el => {
            if (!el.closest('#bootOverlay') && !el.closest('.hud-overlay') &&
                !el.closest('.modal-overlay') && !el.closest('script') &&
                !el.closest('style')) {
                el.classList.add('reveal-on-scroll');
            }
        });

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

        document.querySelectorAll('.reveal-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    // ── Stagger reveal for card groups ──
    function initStaggeredReveals() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const cards = entry.target.querySelectorAll('.reveal-on-scroll');
                    cards.forEach((card, i) => {
                        setTimeout(() => card.classList.add('revealed'), i * 80);
                    });
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.dashboard-grid, .field-carousel-track, .persona-cards')
            .forEach(container => observer.observe(container));
    }

    // ── Smooth hover tilt for cards ──
    function initCardTilt() {
        document.querySelectorAll('.persona-card, .dashboard-card').forEach(card => {
            card.addEventListener('mousemove', function(e) {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width - 0.5;
                const y = (e.clientY - rect.top) / rect.height - 0.5;
                card.style.transform = `translateY(-2px) perspective(600px) rotateX(${-y * 3}deg) rotateY(${x * 3}deg)`;
            });
            card.addEventListener('mouseleave', function() {
                card.style.transform = '';
            });
        });
    }

    // ── Init ──
    document.addEventListener('DOMContentLoaded', function() {
        const overlay = createBootOverlay();
        runBootSequence(overlay).then(() => {
            initScrollReveal();
            initStaggeredReveals();
            initCardTilt();
        });

        if (!overlay) {
            initScrollReveal();
            initStaggeredReveals();
            initCardTilt();
        }
    });
})();
