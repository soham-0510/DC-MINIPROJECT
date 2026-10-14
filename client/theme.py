"""
Visual system for AstroQuiz Arena: design tokens, the animated deep-space
background, and styling for Streamlit + shadcn components.
"""

from __future__ import annotations

import random

import streamlit as st


def _star_layer(count: int, size: int, seed: int, colors: list[str]) -> str:
    rnd = random.Random(seed)
    shadows = []
    for _ in range(count):
        x, y = rnd.randint(0, 2400), rnd.randint(0, 2400)
        shadows.append(f"{x}px {y}px {rnd.choice(colors)}")
    return ",".join(shadows)


STARS_S = _star_layer(260, 1, 7, ["#ffffff", "#dfe6ff", "#c9d4ff"])
STARS_M = _star_layer(90, 2, 11, ["#ffffff", "#bfe9ff", "#e9ddff"])
STARS_L = _star_layer(28, 3, 23, ["#ffffff", "#a5f3fc", "#fde68a", "#ddd6fe"])

CSS = """
@font-face { font-family: 'Orbitron'; font-style: normal; font-weight: 500; font-display: swap; src: url('app/static/fonts/orbitron-latin-500-normal.woff2') format('woff2'); }
@font-face { font-family: 'Orbitron'; font-style: normal; font-weight: 700; font-display: swap; src: url('app/static/fonts/orbitron-latin-700-normal.woff2') format('woff2'); }
@font-face { font-family: 'Orbitron'; font-style: normal; font-weight: 800; font-display: swap; src: url('app/static/fonts/orbitron-latin-800-normal.woff2') format('woff2'); }
@font-face { font-family: 'Orbitron'; font-style: normal; font-weight: 900; font-display: swap; src: url('app/static/fonts/orbitron-latin-900-normal.woff2') format('woff2'); }
@font-face { font-family: 'Space Grotesk'; font-style: normal; font-weight: 400; font-display: swap; src: url('app/static/fonts/space-grotesk-latin-400-normal.woff2') format('woff2'); }
@font-face { font-family: 'Space Grotesk'; font-style: normal; font-weight: 500; font-display: swap; src: url('app/static/fonts/space-grotesk-latin-500-normal.woff2') format('woff2'); }
@font-face { font-family: 'Space Grotesk'; font-style: normal; font-weight: 600; font-display: swap; src: url('app/static/fonts/space-grotesk-latin-600-normal.woff2') format('woff2'); }
@font-face { font-family: 'Space Grotesk'; font-style: normal; font-weight: 700; font-display: swap; src: url('app/static/fonts/space-grotesk-latin-700-normal.woff2') format('woff2'); }

:root {
  --space-950: #05070F;
  --space-900: #080B19;
  --space-800: #0E1330;
  --panel: rgba(17, 22, 50, 0.62);
  --panel-strong: rgba(22, 28, 64, 0.82);
  --line: rgba(160, 172, 255, 0.14);
  --line-strong: rgba(160, 172, 255, 0.28);
  --text: #E9ECFF;
  --muted: #8E96C2;
  --faint: #5D658F;
  --violet: #8B5CF6;
  --violet-soft: #A78BFA;
  --cyan: #22D3EE;
  --gold: #FACC15;
  --pink: #EC4899;
  --green: #34D399;
  --red: #F87171;
  --display: 'Orbitron', 'Space Grotesk', system-ui, sans-serif;
  --body: 'Space Grotesk', system-ui, -apple-system, 'Segoe UI', sans-serif;
  --r-lg: 22px;
  --r-md: 14px;
  --r-sm: 10px;
  --ease-out: cubic-bezier(.16, 1, .3, 1);
  --ease-spring: cubic-bezier(.34, 1.56, .64, 1);
}

/* ---------- App shell ---------- */
html, body, .stApp { background: var(--space-950) !important; }
.stApp {
  color: var(--text);
  font-family: var(--body);
  background:
    radial-gradient(1200px 700px at 85% -10%, rgba(139, 92, 246, .22), transparent 60%),
    radial-gradient(900px 600px at -10% 110%, rgba(34, 211, 238, .12), transparent 60%),
    radial-gradient(700px 500px at 50% 50%, rgba(236, 72, 153, .05), transparent 70%),
    var(--space-950) !important;
}
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp td, .stApp th { font-family: var(--body); }
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], footer, #MainMenu, [data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stAppViewContainer"] > .main, [data-testid="stMain"] { background: transparent !important; }
.block-container, [data-testid="stMainBlockContainer"] {
  max-width: 1180px !important; padding: 1.1rem 1.25rem 4rem !important; position: relative; z-index: 2;
}
/* Polling re-runs must not dim the screen */
[data-stale="true"], .stale-element, [data-testid="stElementContainer"][data-stale] { opacity: 1 !important; transition: none !important; }
[data-testid="stSkeleton"] { display: none !important; }
.stApp a { color: var(--cyan); }
::selection { background: rgba(139, 92, 246, .45); }

h1, h2, h3, h4 { font-family: var(--display) !important; letter-spacing: .02em; color: var(--text) !important; }
.stMarkdown p { color: var(--text); }
.muted { color: var(--muted) !important; }
.mono { font-family: ui-monospace, 'JetBrains Mono', Menlo, Consolas, monospace; }

/* ---------- Deep-space background ---------- */
.cosmos { position: fixed; inset: 0; z-index: -1; pointer-events: none; overflow: hidden; }
.cosmos .stars { position: absolute; top: 0; left: 0; border-radius: 50%; background: transparent; }
.cosmos .stars::after { content: ""; position: absolute; top: 2400px; left: 0; width: inherit; height: inherit;
  border-radius: 50%; box-shadow: inherit; }
.cosmos .s1 { width: 1px; height: 1px; box-shadow: __S1__; animation: drift 240s linear infinite; opacity: .75; }
.cosmos .s2 { width: 2px; height: 2px; box-shadow: __S2__; animation: drift 160s linear infinite, twinkle 5s ease-in-out infinite; }
.cosmos .s3 { width: 3px; height: 3px; box-shadow: __S3__; animation: drift 110s linear infinite, twinkle 3.6s ease-in-out infinite 1.2s;
  filter: drop-shadow(0 0 4px rgba(255,255,255,.7)); }
.cosmos .nebula { position: absolute; border-radius: 50%; filter: blur(70px); opacity: .5; }
.cosmos .n1 { width: 520px; height: 520px; right: -140px; top: 8%; background: radial-gradient(circle, rgba(139,92,246,.55), transparent 65%);
  animation: float 26s ease-in-out infinite; }
.cosmos .n2 { width: 460px; height: 460px; left: -160px; bottom: -80px; background: radial-gradient(circle, rgba(34,211,238,.35), transparent 65%);
  animation: float 32s ease-in-out infinite reverse; }
.cosmos .n3 { width: 300px; height: 300px; left: 40%; top: 55%; background: radial-gradient(circle, rgba(236,72,153,.22), transparent 70%);
  animation: float 38s ease-in-out infinite; }
.cosmos .shoot { position: absolute; height: 2px; width: 160px; border-radius: 2px; opacity: 0;
  background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.95)); transform: rotate(-28deg);
  filter: drop-shadow(0 0 6px rgba(165, 243, 252, .9)); }
.cosmos .sh1 { top: 12%; left: 62%; animation: shoot 11s ease-in infinite 2s; }
.cosmos .sh2 { top: 34%; left: 88%; animation: shoot 17s ease-in infinite 7s; }
.cosmos .sh3 { top: 6%; left: 30%; animation: shoot 23s ease-in infinite 13s; }

@keyframes drift { from { transform: translateY(0); } to { transform: translateY(-2400px); } }
@keyframes twinkle { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
@keyframes float { 0%, 100% { transform: translate(0, 0) scale(1); } 50% { transform: translate(-40px, 30px) scale(1.12); } }
@keyframes shoot {
  0% { opacity: 0; transform: rotate(-28deg) translateX(0); }
  2% { opacity: 1; }
  7% { opacity: 0; transform: rotate(-28deg) translateX(-520px); }
  100% { opacity: 0; transform: rotate(-28deg) translateX(-520px); }
}

/* ---------- Surfaces ---------- */
.panel {
  position: relative;
  background: linear-gradient(180deg, rgba(23, 29, 66, .66), rgba(11, 14, 34, .66));
  border: 1px solid var(--line); border-radius: var(--r-lg);
  backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 30px 60px -30px rgba(0,0,0,.7);
  padding: 22px 24px;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) { border-radius: var(--r-lg); }
div[class*="st-key-card"] {
  background: linear-gradient(180deg, rgba(23, 29, 66, .66), rgba(11, 14, 34, .66));
  border: 1px solid var(--line); border-radius: var(--r-lg);
  backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 30px 60px -30px rgba(0,0,0,.7);
  padding: 22px 24px 24px;
}
.section-title { font-family: var(--display); font-weight: 700; font-size: 1.02rem; letter-spacing: .04em; margin: 0 0 4px; color: var(--text); }
.section-sub { color: var(--muted); font-size: .92rem; margin: 0 0 14px; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stPopover"] > div > button, [data-testid="stPopoverButton"] {
  font-family: var(--body) !important; font-weight: 600 !important; letter-spacing: .01em;
  border-radius: var(--r-md) !important; border: 1px solid var(--line-strong) !important;
  background: rgba(22, 28, 64, .7) !important; color: var(--text) !important;
  min-height: 46px; transition: transform .18s var(--ease-out), box-shadow .25s, border-color .25s, background .25s !important;
}
.stButton > button:hover, [data-testid="stPopoverButton"]:hover {
  border-color: rgba(167, 139, 250, .7) !important; transform: translateY(-1px);
  box-shadow: 0 10px 30px -12px rgba(139, 92, 246, .7) !important;
}
.stButton > button:active { transform: translateY(1px) scale(.99); }
.stButton > button:focus-visible { outline: 2px solid var(--cyan) !important; outline-offset: 2px; }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, #7C3AED 0%, #8B5CF6 45%, #22D3EE 140%) !important;
  border: 1px solid rgba(196, 181, 253, .55) !important; color: #fff !important;
  box-shadow: 0 12px 34px -12px rgba(139, 92, 246, .9), inset 0 1px 0 rgba(255,255,255,.25) !important;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
  box-shadow: 0 16px 44px -10px rgba(139, 92, 246, 1), 0 0 0 4px rgba(139, 92, 246, .18) !important;
}
.stButton > button[kind="tertiary"], .stButton > button[data-testid="stBaseButton-tertiary"] {
  background: transparent !important; border-color: transparent !important; color: var(--muted) !important; min-height: 36px;
}
.stButton > button[kind="tertiary"]:hover { color: var(--text) !important; box-shadow: none !important; }
.stButton > button:disabled { opacity: .45 !important; transform: none !important; box-shadow: none !important; }
.stButton > button p { font-size: .98rem; }

/* big launch button */
div[class*="st-key-launch"] .stButton > button, div[class*="st-key-big"] .stButton > button { min-height: 58px; }
div[class*="st-key-launch"] .stButton > button p, div[class*="st-key-big"] .stButton > button p {
  font-family: var(--display) !important; font-size: 1.02rem !important; letter-spacing: .08em; }
div[class*="st-key-launch"] .stButton > button[kind="primary"] { animation: glowpulse 2.4s ease-in-out infinite; }
@keyframes glowpulse { 0%, 100% { box-shadow: 0 12px 34px -12px rgba(139,92,246,.9), 0 0 0 0 rgba(139,92,246,.45); }
  50% { box-shadow: 0 12px 34px -12px rgba(139,92,246,.9), 0 0 0 10px rgba(139,92,246,0); } }

/* ---------- Inputs & popovers ---------- */
.stTextInput input, .stNumberInput input {
  background: rgba(8, 11, 25, .7) !important; border-radius: var(--r-sm) !important; color: var(--text) !important;
  font-family: var(--body) !important;
}
.stTextInput [data-baseweb="input"], .stNumberInput [data-baseweb="input"] { border-radius: var(--r-sm) !important; border-color: var(--line-strong) !important; background: rgba(8, 11, 25, .7) !important; }
.stTextInput label p, .stNumberInput label p, .stToggle label p, .stPills label p { color: var(--muted) !important; font-size: .86rem !important; }
[data-testid="stPopoverBody"], div[data-baseweb="popover"] > div {
  background: rgba(14, 19, 48, .96) !important; border: 1px solid var(--line-strong) !important; border-radius: var(--r-md) !important;
  backdrop-filter: blur(16px);
}

/* avatar pills */
div[class*="st-key-avatar"] [data-testid="stButtonGroup"] { width: 100%; }
div[class*="st-key-avatar"] [data-testid="stButtonGroup"] div:has(> button) { display: grid !important; grid-template-columns: repeat(5, 1fr); gap: 10px; width: 100%; }
div[class*="st-key-avatar"] [data-testid="stPills"], div[class*="st-key-avatar"] .stPills { width: 100%; }
div[class*="st-key-avatar"] [data-testid="stButtonGroup"] button {
  width: 100%; height: 58px; border-radius: 16px !important; font-size: 1.7rem !important;
  background: rgba(8, 11, 25, .65) !important; border: 1px solid var(--line) !important;
  transition: transform .25s var(--ease-spring), border-color .2s, box-shadow .25s !important;
}
div[class*="st-key-avatar"] [data-testid="stButtonGroup"] button p { font-size: 1.7rem !important; line-height: 1; }
div[class*="st-key-avatar"] [data-testid="stButtonGroup"] button:hover { transform: translateY(-3px) scale(1.06); border-color: var(--violet-soft) !important; }
div[class*="st-key-avatar"] [data-testid="stButtonGroup"] button[data-selected="true"] {
  border-color: var(--cyan) !important; background: rgba(34, 211, 238, .12) !important;
  box-shadow: 0 0 0 3px rgba(34, 211, 238, .18), 0 10px 26px -8px rgba(34, 211, 238, .55) !important; transform: scale(1.08);
}

/* shadcn (streamlit-shadcn-ui) re-tinted to the AstroQuiz palette */
.stApp div[data-theme] {
  --background: #0B0F24; --foreground: #E9ECFF;
  --card: rgba(17, 22, 50, .72); --card-foreground: #E9ECFF;
  --popover: #10153A; --popover-foreground: #E9ECFF;
  --primary: #8B5CF6; --primary-foreground: #ffffff;
  --secondary: rgba(139, 92, 246, .16); --secondary-foreground: #E9ECFF;
  --muted: rgba(160, 172, 255, .10); --muted-foreground: #8E96C2;
  --accent: rgba(139, 92, 246, .22); --accent-foreground: #ffffff;
  --destructive: #F87171;
  --border: rgba(160, 172, 255, .16); --input: rgba(160, 172, 255, .22); --ring: #22D3EE;
  --radius: .85rem;
}

/* ---------- HUD ---------- */
.hud-brand { display: flex; align-items: center; gap: 12px; height: 46px; }
.hud-logo { width: 34px; height: 34px; position: relative; flex: none; }
.hud-logo .core { position: absolute; inset: 7px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #c4b5fd, #7c3aed 55%, #2e1065); box-shadow: 0 0 16px rgba(139,92,246,.8); }
.hud-logo .ring { position: absolute; inset: 0; border-radius: 50%; border: 1.5px solid rgba(34,211,238,.65);
  transform: rotateX(70deg); animation: spin 6s linear infinite; }
.hud-logo .moon { position: absolute; width: 6px; height: 6px; border-radius: 50%; background: #fde68a; top: 50%; left: 50%;
  margin: -3px; animation: orbit-sm 4s linear infinite; box-shadow: 0 0 8px #fde68a; }
.hud-name { font-family: var(--display); font-weight: 800; font-size: 1.05rem; letter-spacing: .08em; }
.hud-name span { color: var(--muted); font-weight: 500; }
.uplink { display: inline-flex; align-items: center; gap: 8px; height: 46px; padding: 0 14px; border-radius: 999px;
  border: 1px solid var(--line); background: rgba(8,11,25,.55); font-size: .85rem; color: var(--muted); white-space: nowrap; }
.uplink b { color: var(--text); font-weight: 600; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 0 0 rgba(52,211,153,.6); animation: ping 2s infinite; flex: none; }
.dot.off { background: var(--red); animation: none; box-shadow: 0 0 10px rgba(248,113,113,.8); }
@keyframes ping { 0% { box-shadow: 0 0 0 0 rgba(52,211,153,.55); } 80%, 100% { box-shadow: 0 0 0 9px rgba(52,211,153,0); } }
@keyframes spin { to { transform: rotateX(70deg) rotate(360deg); } }
@keyframes orbit-sm { from { transform: rotate(0) translateX(16px); } to { transform: rotate(360deg) translateX(16px); } }

/* ---------- Hero ---------- */
.hero { position: relative; display: grid; grid-template-columns: 1.15fr .85fr; align-items: center; gap: 24px; min-height: 360px; margin: 10px 0 18px; }
.hero h1 { font-size: clamp(2.4rem, 5.6vw, 4.6rem) !important; line-height: .98 !important; font-weight: 900 !important; margin: 0 0 18px !important;
  letter-spacing: .01em; padding: 0 !important;
  background: linear-gradient(180deg, #ffffff 30%, #b9b4ff 100%); -webkit-background-clip: text; background-clip: text; color: transparent !important;
  animation: rise 1s var(--ease-out) both; }
.hero p.lede { font-size: 1.12rem; color: var(--muted); max-width: 30rem; line-height: 1.6; margin: 0 0 18px; animation: rise 1s var(--ease-out) .15s both; }
.hero .facts { display: flex; gap: 22px; flex-wrap: wrap; animation: rise 1s var(--ease-out) .3s both; }
.hero .facts div { font-size: .88rem; color: var(--muted); }
.hero .facts b { display: block; font-family: var(--display); color: var(--text); font-size: 1.3rem; }
@keyframes rise { from { opacity: 0; transform: translateY(18px); filter: blur(6px); } to { opacity: 1; transform: none; filter: none; } }

.planet-wrap { position: relative; width: 340px; height: 340px; margin: 0 auto; animation: rise 1.2s var(--ease-out) .1s both; }
.planet { position: absolute; inset: 70px; border-radius: 50%;
  background:
    radial-gradient(circle at 32% 28%, rgba(255,255,255,.55), transparent 22%),
    repeating-linear-gradient(-18deg, rgba(255,255,255,.0) 0 18px, rgba(255,255,255,.06) 18px 26px),
    radial-gradient(circle at 38% 35%, #a78bfa 0%, #7c3aed 38%, #3b0764 72%, #12052b 100%);
  box-shadow: inset -30px -28px 60px rgba(5,7,15,.85), 0 0 80px rgba(139,92,246,.55), 0 0 160px rgba(139,92,246,.25);
  animation: bob 7s ease-in-out infinite; }
.planet-ring { position: absolute; left: 10px; right: 10px; top: 50%; height: 84px; margin-top: -42px; border-radius: 50%;
  border: 2px solid rgba(34, 211, 238, .55); transform: rotate(-16deg);
  box-shadow: 0 0 24px rgba(34,211,238,.35), inset 0 0 18px rgba(34,211,238,.25); animation: bob 7s ease-in-out infinite; }
.planet-ring.front { clip-path: inset(50% -10px -10px -10px); }
.planet-ring.r2 { left: -6px; right: -6px; height: 110px; margin-top: -55px; border-color: rgba(167,139,250,.35); border-width: 1px; }
.planet-ring::before { content: ""; position: absolute; inset: 0; border-radius: 50%; border-top: 2px solid rgba(5,7,15,.0); }
.orbit { position: absolute; inset: 0; border-radius: 50%; animation: spin2d 14s linear infinite; }
.orbit.o2 { inset: 30px; animation-duration: 9s; animation-direction: reverse; }
.orbit .moon { position: absolute; top: -9px; left: 50%; width: 18px; height: 18px; margin-left: -9px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #fff7cc, #facc15 60%, #a16207); box-shadow: 0 0 18px rgba(250,204,21,.8); }
.orbit.o2 .moon { width: 10px; height: 10px; margin-left: -5px; top: -5px; background: radial-gradient(circle at 35% 30%, #e0faff, #22d3ee 60%, #0e7490);
  box-shadow: 0 0 14px rgba(34,211,238,.9); }
.astronaut { position: absolute; right: 6px; bottom: 24px; font-size: 2.6rem; animation: drift-astro 9s ease-in-out infinite; filter: drop-shadow(0 6px 14px rgba(0,0,0,.6)); }
@keyframes spin2d { to { transform: rotate(360deg); } }
@keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
.planet-ring { animation: none; }
@keyframes drift-astro { 0%, 100% { transform: translate(0, 0) rotate(-8deg); } 50% { transform: translate(-14px, -18px) rotate(10deg); } }

/* ---------- Mission categories ---------- */
div[class*="st-key-cat"] .stButton > button {
  min-height: 112px; text-align: left; justify-content: flex-start; align-items: flex-start; padding: 16px 18px !important;
  background: linear-gradient(160deg, rgba(23,29,66,.75), rgba(10,13,32,.75)) !important; white-space: pre-line;
}
div[class*="st-key-cat"] .stButton > button p { text-align: left; font-size: .9rem; color: var(--muted); line-height: 1.45; }
div[class*="st-key-cat"] .stButton > button p strong { display: block; color: var(--text); font-size: 1.04rem; margin-bottom: 2px; font-weight: 700; }
div[class*="st-key-catsel_"] .stButton > button {
  border-color: var(--cyan) !important; background: linear-gradient(160deg, rgba(34,211,238,.16), rgba(139,92,246,.14)) !important;
  box-shadow: 0 0 0 3px rgba(34,211,238,.15), 0 18px 40px -18px rgba(34,211,238,.7) !important;
}

/* ---------- Lobby ---------- */
.code-display { text-align: center; padding: 8px 0 4px; }
.code-display .lbl { color: var(--muted); font-size: .9rem; }
.code-display .code { font-family: var(--display); font-weight: 900; font-size: clamp(2.4rem, 7vw, 4.2rem); letter-spacing: .28em;
  margin-right: -.28em; line-height: 1.15; color: #fff; text-shadow: 0 0 28px rgba(139,92,246,.85), 0 0 2px #fff; }
.code-display .sector { font-family: var(--display); color: var(--cyan); letter-spacing: .3em; font-size: .8rem; }
.crew-card { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: var(--r-md);
  background: rgba(8, 11, 25, .55); border: 1px solid var(--line); animation: beam .9s var(--ease-out) both; position: relative; overflow: hidden; }
.crew-card::after { content: ""; position: absolute; left: 0; right: 0; top: -100%; height: 100%;
  background: linear-gradient(180deg, transparent, rgba(34,211,238,.35), transparent); animation: beamscan 1.1s var(--ease-out) both; }
.crew-card .av { font-size: 1.8rem; width: 46px; height: 46px; display: grid; place-items: center; border-radius: 12px;
  background: radial-gradient(circle at 30% 25%, rgba(139,92,246,.45), rgba(8,11,25,.6)); flex: none; }
.crew-card .nm { font-weight: 600; font-size: 1rem; line-height: 1.2; }
.crew-card .tag { font-size: .78rem; color: var(--muted); }
.crew-card .tag.host { color: var(--gold); }
.crew-card.me { border-color: rgba(34,211,238,.45); }
.crew-card.off { opacity: .45; }
@keyframes beam { 0% { opacity: 0; transform: translateY(-14px) scale(.96); filter: brightness(2.2) blur(3px); }
  60% { opacity: 1; filter: brightness(1.4) blur(0); } 100% { opacity: 1; transform: none; filter: none; } }
@keyframes beamscan { to { top: 100%; } }
.waiting { display: flex; align-items: center; gap: 14px; color: var(--muted); }
.loader { position: relative; width: 44px; height: 44px; flex: none; }
.loader .c { position: absolute; inset: 14px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, #c4b5fd, #7c3aed); box-shadow: 0 0 12px rgba(139,92,246,.8); }
.loader .m { position: absolute; inset: 0; animation: spin2d 1.6s linear infinite; }
.loader .m::after { content: ""; position: absolute; top: 0; left: 50%; width: 7px; height: 7px; margin-left: -3.5px; border-radius: 50%; background: var(--cyan); box-shadow: 0 0 8px var(--cyan); }
.loader .m.b { inset: 6px; animation-duration: 2.6s; animation-direction: reverse; }
.loader .m.b::after { background: var(--gold); box-shadow: 0 0 8px var(--gold); width: 5px; height: 5px; margin-left: -2.5px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; font-size: .84rem;
  background: rgba(139,92,246,.12); border: 1px solid rgba(167,139,250,.28); color: #ddd6fe; }
.chip.cyan { background: rgba(34,211,238,.10); border-color: rgba(34,211,238,.3); color: #a5f3fc; }
.chip.gold { background: rgba(250,204,21,.10); border-color: rgba(250,204,21,.3); color: #fde68a; }
.chip.pink { background: rgba(236,72,153,.10); border-color: rgba(236,72,153,.3); color: #fbcfe8; }
.chip.green { background: rgba(52,211,153,.10); border-color: rgba(52,211,153,.3); color: #a7f3d0; }

/* copyable code (st.code) */
div[class*="st-key-copycode"] { max-width: 230px; margin: 0 auto; }
div[class*="st-key-copycode"] pre { background: rgba(8,11,25,.6) !important; border: 1px dashed var(--line-strong) !important; border-radius: 999px !important; padding: 8px 16px !important; text-align: center; }
div[class*="st-key-copycode"] pre code { font-family: var(--display) !important; letter-spacing: .3em; color: var(--muted) !important; font-size: .85rem !important; }
div[class*="st-key-copycode"] button { opacity: 1 !important; }

/* ---------- Game header ---------- */
.gbar { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; margin-bottom: 14px; }
.gbar .left { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.qprog { display: flex; gap: 6px; align-items: center; }
.qprog i { width: 22px; height: 6px; border-radius: 6px; background: rgba(160,172,255,.16); display: block; }
.qprog i.done { background: linear-gradient(90deg, var(--violet), var(--cyan)); }
.qprog i.now { background: var(--gold); box-shadow: 0 0 10px rgba(250,204,21,.8); animation: twinkle 1.4s ease-in-out infinite; }

/* ---------- Question deck ---------- */
.qwrap { display: grid; grid-template-columns: 1fr auto; gap: 18px; align-items: center; }
.q-card { position: relative; padding: 26px 28px; border-radius: var(--r-lg); overflow: hidden;
  background: linear-gradient(135deg, rgba(30, 37, 84, .82), rgba(11, 14, 34, .82));
  border: 1px solid var(--line-strong); animation: warpin .85s var(--ease-out) both;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06), 0 30px 70px -30px rgba(139,92,246,.55); }
.q-card::before { content: ""; position: absolute; inset: -1px; border-radius: inherit; padding: 1px;
  background: linear-gradient(120deg, rgba(139,92,246,.8), rgba(34,211,238,.25) 40%, transparent 60%, rgba(236,72,153,.5));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask-composite: exclude; pointer-events: none; }
.q-card .q-meta { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.q-card .q-text { font-size: clamp(1.25rem, 2.4vw, 1.7rem); font-weight: 600; line-height: 1.35; letter-spacing: -.005em; }
.q-card .q-visual { display: flex; justify-content: center; margin: 14px 0 2px; }
.q-card .q-visual svg { width: min(230px, 66%); max-height: 190px; height: auto; filter: drop-shadow(0 12px 30px rgba(0,0,0,.6)); }
@keyframes warpin { 0% { opacity: 0; transform: perspective(900px) translateZ(-260px) scale(.86); filter: blur(10px) brightness(1.8); }
  100% { opacity: 1; transform: none; filter: none; } }

.timer { position: relative; width: 104px; height: 104px; flex: none; }
.timer svg { width: 104px; height: 104px; transform: rotate(-90deg); }
.timer .track { fill: none; stroke: rgba(160,172,255,.14); stroke-width: 7; }
.timer .arc { fill: none; stroke-width: 7; stroke-linecap: round; stroke-dasharray: 276.46; filter: drop-shadow(0 0 6px currentColor); }
.timer .num { position: absolute; inset: 0; display: grid; place-items: center; font-family: var(--display); font-weight: 800; font-size: 1.9rem; }
.timer .num small { display: block; font-family: var(--body); font-size: .62rem; color: var(--muted); font-weight: 500; letter-spacing: .08em; margin-top: -4px; text-align: center; }
.timer .sat { position: absolute; inset: 0; }
.timer .sat::after { content: "🛰️"; position: absolute; top: -6px; left: 50%; margin-left: -9px; font-size: 16px; }
@property --tsec { syntax: '<integer>'; inherits: false; initial-value: 0; }
.timer .count { counter-reset: tsec var(--tsec); }
.timer .count::after { content: counter(tsec); }

/* answer options = Streamlit buttons, restyled */
div[class*="st-key-answers"] { counter-reset: opt; }
div[class*="st-key-opt"] { counter-increment: opt; }
div[class*="st-key-opt"] .stButton > button {
  min-height: 74px; justify-content: flex-start; text-align: left; padding: 14px 18px 14px 66px !important; position: relative;
  background: linear-gradient(150deg, rgba(23,29,66,.78), rgba(10,13,32,.78)) !important; border-radius: 18px !important;
  animation: optin .6s var(--ease-out) both; overflow: hidden;
}
div[class*="st-key-opt"] .stButton > button p { font-size: 1.06rem !important; font-weight: 600; text-align: left; }
div[class*="st-key-opt"] .stButton > button > div, div[class*="st-key-opt"] .stButton > button [data-testid="stMarkdownContainer"] { justify-content: flex-start !important; text-align: left; width: 100%; }
div[class*="st-key-opt"] .stButton > button::before {
  content: counter(opt, upper-alpha); position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
  width: 38px; height: 38px; border-radius: 12px; display: grid; place-items: center;
  font-family: var(--display); font-weight: 800; font-size: 1rem; color: #fff; background: var(--hue); box-shadow: 0 0 18px -2px var(--hue);
}
div[class*="st-key-opt"] .stButton > button::after {
  content: ""; position: absolute; inset: 0; background: radial-gradient(400px 120px at var(--mx, 20%) 50%, color-mix(in srgb, var(--hue) 22%, transparent), transparent 70%);
  opacity: 0; transition: opacity .3s; pointer-events: none;
}
div[class*="st-key-opt"] .stButton > button:hover { border-color: var(--hue) !important; box-shadow: 0 16px 40px -18px var(--hue) !important; transform: translateY(-2px); }
div[class*="st-key-opt"] .stButton > button:hover::after { opacity: 1; }
div[class*="st-key-opt0"] { --hue: #8B5CF6; } div[class*="st-key-opt0"] .stButton > button { animation-delay: .25s; }
div[class*="st-key-opt1"] { --hue: #06B6D4; } div[class*="st-key-opt1"] .stButton > button { animation-delay: .33s; }
div[class*="st-key-opt2"] { --hue: #EAB308; } div[class*="st-key-opt2"] .stButton > button { animation-delay: .41s; }
div[class*="st-key-opt3"] { --hue: #EC4899; } div[class*="st-key-opt3"] .stButton > button { animation-delay: .49s; }
div[class*="st-key-opt"] .stButton > button:disabled { opacity: .28 !important; text-decoration: line-through; filter: grayscale(.8); }
@keyframes optin { from { opacity: 0; transform: translateY(16px) scale(.97); } to { opacity: 1; transform: none; } }

/* option cards rendered as HTML (locked + reveal states) */
.opts { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.opt { position: relative; display: flex; align-items: center; gap: 14px; min-height: 74px; padding: 14px 18px; border-radius: 18px;
  background: linear-gradient(150deg, rgba(23,29,66,.78), rgba(10,13,32,.78)); border: 1px solid var(--line); font-weight: 600; font-size: 1.04rem; }
.opt .k { width: 38px; height: 38px; border-radius: 12px; flex: none; display: grid; place-items: center; font-family: var(--display); font-weight: 800; color: #fff; background: var(--hue); }
.opt .r { margin-left: auto; font-size: .85rem; color: var(--muted); font-weight: 500; display: flex; gap: 4px; }
.opt.dim { opacity: .38; }
.opt.gone { opacity: .18; text-decoration: line-through; }
.opt.locked { border-color: var(--cyan); box-shadow: 0 0 0 3px rgba(34,211,238,.18), 0 18px 40px -18px rgba(34,211,238,.8); animation: lockin .5s var(--ease-spring) both; }
.opt.locked .r { color: var(--cyan); }
.opt.correct { border-color: var(--green); background: linear-gradient(150deg, rgba(16,92,70,.55), rgba(10,13,32,.8));
  box-shadow: 0 0 0 3px rgba(52,211,153,.2), 0 0 40px -6px rgba(52,211,153,.7); animation: lockin .6s var(--ease-spring) both; }
.opt.correct::after { content: ""; position: absolute; left: 33px; top: 50%; width: 10px; height: 10px; margin: -5px; border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(52,211,153,.9); animation: nova 1.1s var(--ease-out) .15s both; }
.opt.wrong { border-color: var(--red); background: linear-gradient(150deg, rgba(110,24,24,.5), rgba(10,13,32,.8)); animation: impact .6s ease both; }
.opt.correct .r { color: var(--green); } .opt.wrong .r { color: var(--red); }
@keyframes lockin { 0% { transform: scale(.96); } 60% { transform: scale(1.025); } 100% { transform: scale(1); } }
@keyframes nova { 0% { box-shadow: 0 0 0 0 rgba(52,211,153,.9), 0 0 0 0 rgba(250,204,21,.7); } 100% { box-shadow: 0 0 0 160px rgba(52,211,153,0), 0 0 0 90px rgba(250,204,21,0); } }
@keyframes impact { 0%, 100% { transform: translateX(0); } 15% { transform: translateX(-10px) rotate(-.6deg); } 30% { transform: translateX(9px) rotate(.6deg); }
  45% { transform: translateX(-6px); } 60% { transform: translateX(4px); } 75% { transform: translateX(-2px); } }
.hue0 { --hue: #8B5CF6; } .hue1 { --hue: #06B6D4; } .hue2 { --hue: #EAB308; } .hue3 { --hue: #EC4899; }

/* power-ups */
div[class*="st-key-powerups"] { flex-wrap: nowrap !important; }
div[class*="st-key-pu_"] { flex: 1 1 0 !important; min-width: 0 !important; width: auto !important; }
div[class*="st-key-pu_"] .stButton > button { min-height: 52px; border-style: dashed !important; background: rgba(8,11,25,.5) !important; }
div[class*="st-key-pu_"] .stButton > button p { font-size: .9rem !important; }
div[class*="st-key-pu_"] .stButton > button:hover:not(:disabled) { border-color: var(--pink) !important; box-shadow: 0 10px 30px -12px rgba(236,72,153,.8) !important; }

/* result banner */
.banner { display: flex; align-items: center; gap: 16px; padding: 16px 20px; border-radius: var(--r-lg); border: 1px solid var(--line-strong);
  background: rgba(8, 11, 25, .6); animation: rise .6s var(--ease-out) both; }
.banner .big { font-size: 2.2rem; line-height: 1; }
.banner .t { font-family: var(--display); font-weight: 800; font-size: 1.15rem; letter-spacing: .03em; }
.banner .s { color: var(--muted); font-size: .92rem; }
.banner .pts { margin-left: auto; font-family: var(--display); font-weight: 900; font-size: 1.9rem; color: var(--gold); text-shadow: 0 0 20px rgba(250,204,21,.6); animation: popup .9s var(--ease-spring) .2s both; }
.banner.good { border-color: rgba(52,211,153,.55); background: linear-gradient(120deg, rgba(16,92,70,.35), rgba(8,11,25,.6)); }
.banner.bad { border-color: rgba(248,113,113,.45); background: linear-gradient(120deg, rgba(110,24,24,.3), rgba(8,11,25,.6)); }
@keyframes popup { 0% { opacity: 0; transform: translateY(18px) scale(.6); } 100% { opacity: 1; transform: none; } }
.fact { margin-top: 12px; padding: 14px 18px; border-radius: var(--r-md); border: 1px dashed rgba(250,204,21,.35); background: rgba(250,204,21,.05);
  color: #fef3c7; font-size: .97rem; line-height: 1.5; animation: rise .7s var(--ease-out) .25s both; }
.fact b { color: var(--gold); }
.nextbar { height: 4px; border-radius: 4px; background: rgba(160,172,255,.12); overflow: hidden; margin-top: 14px; }
.nextbar i { display: block; height: 100%; background: linear-gradient(90deg, var(--violet), var(--cyan)); transform-origin: left; animation: shrink linear forwards; }
@keyframes shrink { from { transform: scaleX(1); } to { transform: scaleX(0); } }

/* ---------- Rocket race leaderboard ---------- */
.race { display: flex; flex-direction: column; gap: 10px; }
.race-row { display: grid; grid-template-columns: 30px 1fr; gap: 8px; align-items: center; }
.race-row .pos { font-family: var(--display); font-weight: 800; color: var(--faint); font-size: .95rem; text-align: center; }
.race-row.p1 .pos { color: var(--gold); } .race-row.p2 .pos { color: #cbd5e1; } .race-row.p3 .pos { color: #f59e0b; }
.race-row .who { display: flex; justify-content: space-between; font-size: .88rem; margin-bottom: 4px; gap: 8px; }
.race-row .who .n { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.race-row .who .sc { font-family: var(--display); font-weight: 700; color: var(--text); }
.race-row.me .who .n { color: var(--cyan); font-weight: 600; }
.track { position: relative; height: 22px; border-radius: 12px; background: rgba(8,11,25,.6); border: 1px solid var(--line); }
.track .trail { position: absolute; left: 0; top: 50%; height: 3px; margin-top: -1.5px; border-radius: 3px;
  background: linear-gradient(90deg, transparent, rgba(139,92,246,.6), rgba(34,211,238,.9)); width: var(--to); }
.track .rkt { position: absolute; top: 50%; left: var(--to); transform: translate(-60%, -54%) rotate(45deg); font-size: 18px; line-height: 1; filter: drop-shadow(0 0 6px rgba(250,204,21,.8)); }
.track .flag { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); font-size: 11px; opacity: .55; }
.race.animate .trail { animation: grow 1.6s var(--ease-out) .35s both; }
.race.animate .rkt { animation: fly 1.6s var(--ease-out) .35s both; }
@keyframes grow { from { width: var(--from); } to { width: var(--to); } }
@keyframes fly { from { left: var(--from); } to { left: var(--to); } }
.sent { font-size: .72rem; color: var(--green); margin-left: 6px; animation: lockin .4s var(--ease-spring) both; }
.wait-dot { font-size: .72rem; color: var(--faint); margin-left: 6px; }

/* ---------- Launch overlay & warp ---------- */
.launch { position: fixed; inset: 0; z-index: 9999; display: grid; place-items: center; pointer-events: none;
  background: radial-gradient(circle at 50% 75%, rgba(124,58,237,.42), transparent 60%), rgba(5,7,15,.95); backdrop-filter: blur(8px); animation: launch-out 4s linear var(--lo, 0s) both; }
.launch .cd { position: absolute; top: 18%; left: 0; right: 0; text-align: center; font-family: var(--display); font-weight: 900; font-size: clamp(5rem, 16vw, 11rem); color: #fff; text-shadow: 0 0 40px rgba(139,92,246,.95); }
.launch .cd span { position: absolute; left: 0; right: 0; opacity: 0; animation: cdnum .95s var(--ease-out) both; }
.launch .cd span:nth-child(1) { animation-delay: calc(var(--lo, 0s) + 0s); }
.launch .cd span:nth-child(2) { animation-delay: calc(var(--lo, 0s) + .95s); }
.launch .cd span:nth-child(3) { animation-delay: calc(var(--lo, 0s) + 1.9s); }
.launch .cd span.go { font-size: .38em; letter-spacing: .2em; top: .9em; color: var(--gold); text-shadow: 0 0 30px rgba(250,204,21,.9); animation: cdgo 1.4s var(--ease-out) calc(var(--lo, 0s) + 2.85s) both; }
.launch .rocket { position: absolute; bottom: 8%; left: 50%; width: 90px; margin-left: -45px; animation: liftoff 4s cubic-bezier(.55, 0, .9, .4) var(--lo, 0s) both; }
.launch .rocket .flame { transform-origin: 50% 0; animation: flame .12s ease-in-out infinite alternate; }
.launch .smoke { position: absolute; bottom: 4%; left: 50%; width: 260px; height: 120px; margin-left: -130px; border-radius: 50%;
  background: radial-gradient(circle, rgba(226,232,240,.55), transparent 65%); filter: blur(14px); animation: smoke 4s ease-out var(--lo, 0s) both; }
.launch .shake { position: absolute; inset: 0; animation: rumble .1s linear infinite; }
@keyframes cdnum { 0% { opacity: 0; transform: scale(2.2); filter: blur(10px); } 25% { opacity: 1; transform: scale(1); filter: none; } 80% { opacity: 1; } 100% { opacity: 0; transform: scale(.6); } }
@keyframes cdgo { 0% { opacity: 0; transform: scale(.6); } 30% { opacity: 1; transform: scale(1.05); } 100% { opacity: 1; transform: scale(1); } }
@keyframes liftoff { 0%, 68% { transform: translateY(0); } 100% { transform: translateY(-115vh); } }
@keyframes flame { from { transform: scaleY(.85); opacity: .85; } to { transform: scaleY(1.25); opacity: 1; } }
@keyframes smoke { 0%, 60% { opacity: .2; transform: scale(.5); } 85% { opacity: 1; transform: scale(1.6); } 100% { opacity: 0; transform: scale(2.2); } }
@keyframes launch-out { 0%, 90% { opacity: 1; } 100% { opacity: 0; } }
@keyframes rumble { 0% { transform: translate(0,0); } 50% { transform: translate(1px,-1px); } 100% { transform: translate(-1px,1px); } }

.warp { position: fixed; inset: 0; z-index: 9998; pointer-events: none; animation: warpfade .95s ease-out both; }
.warp::before { content: ""; position: absolute; left: 50%; top: 45%; width: 220vmax; height: 220vmax; margin: -110vmax 0 0 -110vmax;
  background: repeating-conic-gradient(from 0deg, rgba(255,255,255,.0) 0deg 2.2deg, rgba(196,181,253,.55) 2.4deg 2.6deg, rgba(255,255,255,0) 2.8deg 7deg);
  -webkit-mask: radial-gradient(circle, transparent 6%, #000 30%, transparent 60%); mask: radial-gradient(circle, transparent 6%, #000 30%, transparent 60%);
  animation: warpzoom .95s cubic-bezier(.4, 0, .2, 1) both; }
@keyframes warpzoom { from { transform: scale(.2) rotate(0deg); } to { transform: scale(1.6) rotate(8deg); } }
@keyframes warpfade { 0% { opacity: 0; } 15% { opacity: 1; } 100% { opacity: 0; } }

/* ---------- Podium ---------- */
.podium { display: grid; grid-template-columns: repeat(3, 1fr); align-items: end; gap: 14px; max-width: 720px; margin: 10px auto 0; padding-top: 70px; }
.pod { text-align: center; position: relative; }
.pod .ava { font-size: 3rem; line-height: 1; animation: drop .9s var(--ease-spring) both; display: inline-block; filter: drop-shadow(0 10px 20px rgba(0,0,0,.6)); }
.pod .crown { position: absolute; left: 50%; top: -46px; transform: translateX(-50%); font-size: 1.8rem; animation: drop .9s var(--ease-spring) 2.1s both, bob 3s ease-in-out 3s infinite; }
.pod .pn { font-weight: 700; margin: 8px 0 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pod .ps { font-family: var(--display); font-weight: 800; color: var(--gold); margin-bottom: 10px; }
.pod .base { position: relative; border-radius: 18px 18px 6px 6px; display: grid; place-items: start center; padding-top: 14px; overflow: hidden;
  transform-origin: bottom; animation: risepod 1s var(--ease-out) both; border: 1px solid var(--line-strong);
  font-family: var(--display); font-weight: 900; font-size: 2.4rem; color: rgba(255,255,255,.9); }
.pod .base::before { content: ""; position: absolute; left: 50%; top: -60%; width: 160%; aspect-ratio: 1; transform: translateX(-50%); border-radius: 50%; opacity: .9; }
.pod .base span { position: relative; }
.pod.first .base { height: 200px; background: linear-gradient(180deg, rgba(250,204,21,.25), rgba(11,14,34,.9)); box-shadow: 0 0 60px -10px rgba(250,204,21,.6); }
.pod.first .base::before { background: radial-gradient(circle at 50% 80%, rgba(250,204,21,.55), transparent 55%); }
.pod.second .base { height: 150px; background: linear-gradient(180deg, rgba(167,139,250,.28), rgba(11,14,34,.9)); }
.pod.second .base::before { background: radial-gradient(circle at 50% 80%, rgba(167,139,250,.5), transparent 55%); }
.pod.third .base { height: 112px; background: linear-gradient(180deg, rgba(34,211,238,.22), rgba(11,14,34,.9)); }
.pod.third .base::before { background: radial-gradient(circle at 50% 80%, rgba(34,211,238,.45), transparent 55%); }
.pod.third .base { animation-delay: .2s; } .pod.third .ava { animation-delay: 1.1s; }
.pod.second .base { animation-delay: .5s; } .pod.second .ava { animation-delay: 1.4s; }
.pod.first .base { animation-delay: .8s; } .pod.first .ava { animation-delay: 1.8s; }
.pod.first .pn, .pod.first .ps { animation: rise .6s var(--ease-out) 1.9s both; }
.pod.second .pn, .pod.second .ps { animation: rise .6s var(--ease-out) 1.5s both; }
.pod.third .pn, .pod.third .ps { animation: rise .6s var(--ease-out) 1.2s both; }
.pod.empty { visibility: hidden; }
@keyframes risepod { from { transform: scaleY(0); opacity: 0; } to { transform: scaleY(1); opacity: 1; } }
@keyframes drop { 0% { opacity: 0; transform: translateY(-120px) scale(.6); } 100% { opacity: 1; transform: none; } }

.rank-card { text-align: center; padding: 22px; border-radius: var(--r-lg); border: 1px solid rgba(250,204,21,.4);
  background: radial-gradient(400px 160px at 50% 0%, rgba(250,204,21,.16), transparent 70%), rgba(8,11,25,.6);
  animation: rise .8s var(--ease-out) 2.3s both; }
.rank-card .e { font-size: 2.6rem; display: inline-block; animation: bob 3s ease-in-out infinite; }
.rank-card .ttl { font-family: var(--display); font-weight: 900; font-size: 1.5rem; letter-spacing: .05em; margin-top: 4px;
  background: linear-gradient(90deg, #fde68a, #fff, #a5f3fc); -webkit-background-clip: text; background-clip: text; color: transparent; }
.rank-card .sub { color: var(--muted); font-size: .9rem; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 14px; }
.stat { padding: 14px; border-radius: var(--r-md); background: rgba(8,11,25,.55); border: 1px solid var(--line); text-align: center; animation: rise .6s var(--ease-out) both; }
.stat b { display: block; font-family: var(--display); font-size: 1.35rem; color: var(--text); }
.stat span { color: var(--muted); font-size: .8rem; }
.stat:nth-child(1) { animation-delay: 2.5s; } .stat:nth-child(2) { animation-delay: 2.6s; } .stat:nth-child(3) { animation-delay: 2.7s; } .stat:nth-child(4) { animation-delay: 2.8s; }

.table { width: 100%; border-collapse: separate; border-spacing: 0 6px; font-size: .93rem; }
.table, .table tr, .table th, .table td { border: none !important; }
.table th { background: transparent !important; text-align: left; color: var(--muted); font-weight: 500; font-size: .8rem; padding: 0 12px; }
.table td { padding: 10px 12px; background: rgba(8,11,25,.5); border-top: 1px solid var(--line) !important; border-bottom: 1px solid var(--line) !important; }
.table td:first-child { border-left: 1px solid var(--line) !important; border-radius: 12px 0 0 12px; font-family: var(--display); font-weight: 800; color: var(--faint); }
.table td:last-child { border-right: 1px solid var(--line) !important; border-radius: 0 12px 12px 0; }
.table tr.me td { border-color: rgba(34,211,238,.45) !important; background: rgba(34,211,238,.06); }
.table td.num { font-family: var(--display); font-weight: 700; }

/* ---------- Ground station ---------- */
.gs-head { display: flex; align-items: end; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin: 6px 0 16px; }
.gs-head h2 { margin: 0 !important; padding: 0 !important; font-size: 1.7rem !important; }
.metric { padding: 16px 18px; border-radius: var(--r-md); background: rgba(8,11,25,.55); border: 1px solid var(--line); }
.metric b { display: block; font-family: var(--display); font-size: 1.7rem; font-weight: 800; }
.metric span { color: var(--muted); font-size: .84rem; }
.log { font-family: ui-monospace, 'JetBrains Mono', Menlo, Consolas, monospace; font-size: .8rem; line-height: 1.75; max-height: 420px; overflow: auto;
  padding: 14px 16px; border-radius: var(--r-md); background: rgba(3,5,12,.8); border: 1px solid var(--line); }
.log .ln { display: grid; grid-template-columns: 74px 128px 1fr 64px; gap: 10px; white-space: nowrap; }
.log .ln > * { overflow: hidden; text-overflow: ellipsis; }
.log .t { color: var(--faint); } .log .c { color: #93c5fd; } .log .ms { color: var(--muted); text-align: right; }
.log .m { color: var(--green); } .log .m.poll { color: var(--faint); } .log .m.err { color: var(--red); }
.log .ln.new { animation: logline .6s ease-out both; }
@keyframes logline { from { background: rgba(139,92,246,.25); } to { background: transparent; } }
.arch { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; align-items: center; gap: 10px; }
.arch .node { padding: 14px; border-radius: var(--r-md); border: 1px solid var(--line-strong); background: rgba(8,11,25,.55); text-align: center; font-size: .86rem; color: var(--muted); }
.arch .node b { display: block; color: var(--text); font-size: .95rem; margin-bottom: 2px; }
.arch .wire { position: relative; width: 70px; height: 2px; background: rgba(160,172,255,.2); overflow: hidden; }
.arch .wire::after { content: ""; position: absolute; top: 0; left: -30%; width: 30%; height: 100%; background: var(--cyan); box-shadow: 0 0 8px var(--cyan); animation: packet 1.4s linear infinite; }
@keyframes packet { to { left: 100%; } }

/* ---------- Alerts ---------- */
.alert { padding: 12px 16px; border-radius: var(--r-md); border: 1px solid rgba(248,113,113,.4); background: rgba(127,29,29,.25); color: #fecaca; font-size: .93rem; animation: impact .5s ease both; }
.alert.info { border-color: rgba(34,211,238,.35); background: rgba(8,51,68,.35); color: #cffafe; animation: rise .5s var(--ease-out) both; }

/* ---------- Responsive & motion preferences ---------- */
@media (max-width: 640px) {
  div[class*="st-key-hud_tools_live"] { display: none !important; }
  [data-testid="stHorizontalBlock"]:has(div[class*="st-key-hud_tools_live"]) { gap: 0 !important; }
  .hud-brand { justify-content: center; }
}
@media (max-width: 820px) {
  .hero { grid-template-columns: 1fr; text-align: left; min-height: 0; }
  .planet-wrap { width: 240px; height: 240px; order: -1; }
  .planet { inset: 50px; }
  .opts { grid-template-columns: 1fr; }
  .qwrap { grid-template-columns: 1fr; }
  .timer { margin: 0 auto; }
  .stats { grid-template-columns: repeat(2, 1fr); }
  .arch { grid-template-columns: 1fr; } .arch .wire { width: 2px; height: 26px; margin: 0 auto; }
  .log .ln { grid-template-columns: 64px 1fr 56px; } .log .ln .c { display: none; }
  div[class*="st-key-pu_"] .stButton > button { padding: 6px 4px !important; }
  div[class*="st-key-pu_"] .stButton > button p { font-size: .76rem !important; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
  .cosmos .shoot, .warp { display: none; }
}
"""


def inject_theme() -> None:
    css = (
        CSS.replace("__S1__", STARS_S)
        .replace("__S2__", STARS_M)
        .replace("__S3__", STARS_L)
    )
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


COSMOS_HTML = """
<div class="cosmos" aria-hidden="true">
  <div class="nebula n1"></div><div class="nebula n2"></div><div class="nebula n3"></div>
  <div class="stars s1"></div><div class="stars s2"></div><div class="stars s3"></div>
  <span class="shoot sh1"></span><span class="shoot sh2"></span><span class="shoot sh3"></span>
</div>
"""


def cosmos() -> None:
    st.markdown(COSMOS_HTML, unsafe_allow_html=True)
