"""
HTML builders for the game UI. Every function returns a single-line HTML
string (rendered with st.markdown) so the animations defined in theme.py
can run without extra JavaScript.

All player-provided text goes through `esc()`.
"""

from __future__ import annotations

import html
import json

from components.visuals import svg_for

LETTERS = "ABCD"
DIFF_LABEL = {"easy": "Cadet", "medium": "Pilot", "hard": "Commander", "mixed": "Mixed"}
DIFF_CHIP = {"easy": "green", "medium": "cyan", "hard": "pink", "mixed": ""}


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def one_line(markup: str) -> str:
    return " ".join(markup.split())


# ------------------------------------------------------------------ HUD
def brand() -> str:
    return one_line("""
    <div class="hud-brand">
      <div class="hud-logo"><div class="ring"></div><div class="core"></div><div class="moon"></div></div>
      <div class="hud-name">ASTROQUIZ <span>ARENA</span></div>
    </div>""")


def loader(text: str) -> str:
    return one_line(f"""
    <div class="waiting"><div class="loader"><div class="c"></div><div class="m"></div><div class="m b"></div></div>
    <div>{text}</div></div>""")


def alert(text: str, kind: str = "") -> str:
    return f'<div class="alert {kind}">{esc(text)}</div>'


def section(title: str, sub: str = "") -> str:
    s = f'<div class="section-title">{esc(title)}</div>'
    if sub:
        s += f'<div class="section-sub">{esc(sub)}</div>'
    return s


# ------------------------------------------------------------------ hero
def hero(total_questions: int, categories: int) -> str:
    return one_line(f"""
    <div class="hero">
      <div>
        <h1>AstroQuiz<br/>Arena</h1>
        <p class="lede">A live multiplayer space quiz. Host a mission, share the code with your crew,
        and race your rockets to the top of the leaderboard — every move travels over RPC to one shared game server.</p>
        <div class="facts">
          <div><b>{total_questions}</b>space questions</div>
          <div><b>{categories}</b>mission types</div>
          <div><b>12</b>astronauts per room</div>
        </div>
      </div>
      <div class="planet-wrap" aria-hidden="true">
        <div class="orbit"><div class="moon"></div></div>
        <div class="orbit o2"><div class="moon"></div></div>
        <div class="planet-ring r2"></div>
        <div class="planet-ring"></div>
        <div class="planet"></div>
        <div class="planet-ring front"></div>
        <div class="astronaut">🧑‍🚀</div>
      </div>
    </div>""")


# ------------------------------------------------------------------ lobby
def code_display(code: str, sector: str) -> str:
    return one_line(f"""
    <div class="code-display">
      <div class="lbl">Mission code</div>
      <div class="code">{esc(code)}</div>
      <div class="sector">SECTOR {esc(sector)}</div>
    </div>""")


def crew_card(p: dict, me_id: str) -> str:
    cls = "crew-card"
    if p["id"] == me_id:
        cls += " me"
    if not p.get("online", True):
        cls += " off"
    tags = []
    if p.get("is_host"):
        tags.append('<span class="tag host">★ Mission host</span>')
    if p["id"] == me_id:
        tags.append('<span class="tag">You</span>')
    if not p.get("online", True):
        tags.append('<span class="tag">Signal lost</span>')
    if not tags:
        tags.append('<span class="tag">Ready for launch</span>')
    return one_line(f"""
    <div class="{cls}"><div class="av">{esc(p['avatar'])}</div>
      <div><div class="nm">{esc(p['name'])}</div>{' · '.join(tags)}</div></div>""")


def settings_chips(settings: dict, category_title: str, category_icon: str) -> str:
    diff = settings["difficulty"]
    return one_line(f"""
    <div class="chips">
      <span class="chip">{esc(category_icon)} {esc(category_title)}</span>
      <span class="chip {DIFF_CHIP.get(diff, '')}">{DIFF_LABEL.get(diff, diff)}</span>
      <span class="chip gold">{settings['num_questions']} questions</span>
      <span class="chip cyan">⏱ {settings['time_per_q']} s each</span>
    </div>""")


# ------------------------------------------------------------------ game
def game_bar(state: dict) -> str:
    q = state.get("question") or {}
    qi, total = state["q_index"], state["total_q"]
    dots = []
    for i in range(total):
        if i < qi or (i == qi and state["phase"] == "reveal"):
            dots.append('<i class="done"></i>')
        elif i == qi:
            dots.append('<i class="now"></i>')
        else:
            dots.append("<i></i>")
    me = state["me"]
    streak = f'<span class="chip pink">🔥 {me["streak"]} streak</span>' if me["streak"] >= 2 else ""
    shield = '<span class="chip cyan">🛡️ Shield up</span>' if me.get("shield_active") else ""
    diff = q.get("difficulty", "")
    return one_line(f"""
    <div class="gbar">
      <div class="left">
        <span class="chip">{esc(q.get('category_icon', ''))} {esc(q.get('category_title', ''))}</span>
        <span class="chip {DIFF_CHIP.get(diff, '')}">{DIFF_LABEL.get(diff, diff)}</span>
        <span class="chip gold">Q {qi + 1} / {total}</span>
        <div class="qprog">{''.join(dots)}</div>
      </div>
      <div class="left">{shield}{streak}<span class="chip gold">★ {me['score']:,} pts</span></div>
    </div>""")


def question_card(state: dict) -> str:
    q = state["question"]
    tag = "div" if state["q_index"] % 2 == 0 else "section"  # new tag => fresh warp-in animation
    visual = svg_for(q.get("visual"))
    vis_html = f'<div class="q-visual">{visual}</div>' if visual else ""
    return one_line(f"""
    <{tag} class="q-card">
      <div class="q-text">{esc(q['text'])}</div>
      {vis_html}
    </{tag}>""")


def warp(q_index: int) -> str:
    tag = "div" if q_index % 2 == 0 else "section"
    return f'<{tag} class="warp" aria-hidden="true"></{tag}>'


def timer(q_index: int, duration: float, elapsed: float, warp_s: float) -> str:
    """Orbit-ring countdown, driven purely by CSS so it stays smooth between polls."""
    d = max(duration, 0.1)
    name = f"q{q_index}w{int(warp_s)}"
    amber = max(0.0, min(99.0, 100 * (d - 8) / d))
    red = max(0.0, min(99.5, 100 * (d - 5) / d))
    delay = -max(0.0, elapsed)
    return one_line(f"""
    <style>
      @keyframes arc_{name} {{ from {{ stroke-dashoffset: 0; }} to {{ stroke-dashoffset: 276.46; }} }}
      @keyframes col_{name} {{ 0% {{ stroke: #22D3EE; color: #22D3EE; }} {amber:.1f}% {{ stroke: #22D3EE; color: #22D3EE; }}
        {min(red, amber + 0.1):.1f}% {{ stroke: #FACC15; color: #FACC15; }} {red + 0.1:.1f}% {{ stroke: #F87171; color: #F87171; }}
        100% {{ stroke: #F87171; color: #F87171; }} }}
      @keyframes cnt_{name} {{ from {{ --tsec: {int(round(d))}; }} to {{ --tsec: 0; }} }}
      @keyframes sat_{name} {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(-360deg); }} }}
      .tm_{name} .arc {{ animation: arc_{name} {d:.2f}s linear {delay:.2f}s both, col_{name} {d:.2f}s linear {delay:.2f}s both; }}
      .tm_{name} .count {{ animation: cnt_{name} {d:.2f}s linear {delay:.2f}s both; }}
      .tm_{name} .sat {{ animation: sat_{name} {d:.2f}s linear {delay:.2f}s both; }}
    </style>
    <div class="timer tm_{name}">
      <svg viewBox="0 0 104 104"><circle class="track" cx="52" cy="52" r="44"/><circle class="arc" cx="52" cy="52" r="44"/></svg>
      <div class="sat"></div>
      <div class="num"><div><span class="count"></span><small>SECONDS</small></div></div>
    </div>""")


def options_html(options: list[str], mode: str, chosen=None, answer=None, hidden=(), pick_counts=None) -> str:
    """mode: 'locked' (answered, waiting), 'timeout', or 'reveal'."""
    cards = []
    for i, text in enumerate(options):
        cls = f"opt hue{i}"
        right = ""
        if mode == "locked":
            if i == chosen:
                cls += " locked"
                right = "📡 Transmitted"
            elif i in hidden:
                cls += " gone"
            else:
                cls += " dim"
        elif mode == "timeout":
            cls += " gone" if i in hidden else " dim"
        elif mode == "reveal":
            if i == answer:
                cls += " correct"
                right = "✓ Correct"
            elif i == chosen:
                cls += " wrong"
                right = "✗ Your pick"
            else:
                cls += " dim"
            if pick_counts and pick_counts.get(i):
                right += f" &nbsp;👥 {pick_counts[i]}"
        cards.append(f'<div class="{cls}"><span class="k">{LETTERS[i]}</span><span>{esc(text)}</span><span class="r">{right}</span></div>')
    return f'<div class="opts">{"".join(cards)}</div>'


def race(players: list[dict], me_id: str, answered_ids=None, prev_scores=None, animate=False, deltas=None) -> str:
    top = max([p["score"] for p in players] + [1])
    rows = []
    for pos, p in enumerate(players, 1):
        to = 6 + 86 * p["score"] / top
        frm = to
        if prev_scores is not None:
            frm = 6 + 86 * prev_scores.get(p["id"], 0) / top
        cls = f"race-row p{pos}" + (" me" if p["id"] == me_id else "")
        status = ""
        if answered_ids is not None:
            status = '<span class="sent">✓ sent</span>' if p["id"] in answered_ids else '<span class="wait-dot">thinking…</span>'
        if deltas and deltas.get(p["id"]):
            status = f'<span class="sent" style="color:var(--gold)">+{deltas[p["id"]]}</span>'
        off = "" if p.get("online", True) else " 📴"
        rows.append(one_line(f"""
        <div class="{cls}"><div class="pos">{pos}</div><div>
          <div class="who"><span class="n">{esc(p['avatar'])} {esc(p['name'])}{off}{status}</span><span class="sc">{p['score']:,}</span></div>
          <div class="track" style="--from:{frm:.1f}%;--to:{to:.1f}%"><div class="trail"></div><span class="rkt">🚀</span><span class="flag">🏁</span></div>
        </div></div>"""))
    return f'<div class="race{" animate" if animate else ""}">{"".join(rows)}</div>'


def result_banner(mine: dict | None, answer_text: str, answer_letter: str, streak: int) -> str:
    if mine and mine.get("correct"):
        bonus = " · ×1.5 streak bonus" if streak >= 3 else ""
        t = f"{mine['time']:.1f}" if mine.get("time") is not None else "?"
        return one_line(f"""
        <div class="banner good"><div class="big">🎯</div><div><div class="t">Direct hit!</div>
        <div class="s">Answered in {t} s · streak {streak} 🔥{bonus}</div></div><div class="pts">+{mine['points']}</div></div>""")
    if mine and mine.get("option") is not None:
        shield = "🛡️ Your shield held — streak saved. " if mine.get("shielded") else ""
        return one_line(f"""
        <div class="banner bad"><div class="big">☄️</div><div><div class="t">Asteroid impact</div>
        <div class="s">{shield}The answer was {answer_letter} · {esc(answer_text)}</div></div><div class="pts" style="color:var(--faint);text-shadow:none">+0</div></div>""")
    shield = "🛡️ Shield held your streak. " if mine and mine.get("shielded") else ""
    return one_line(f"""
    <div class="banner bad"><div class="big">📡</div><div><div class="t">No transmission</div>
    <div class="s">{shield}Time ran out. The answer was {answer_letter} · {esc(answer_text)}</div></div><div class="pts" style="color:var(--faint);text-shadow:none">+0</div></div>""")


def fact(text: str) -> str:
    return f'<div class="fact"><b>💡 Did you know?</b> {esc(text)}</div>' if text else ""


def next_bar(label: str, seconds: float, uid: str) -> str:
    tag = "div" if hash(uid) % 2 == 0 else "section"
    return one_line(f"""
    <{tag} style="margin-top:14px"><div class="section-sub" style="margin:0">{esc(label)}</div>
    <div class="nextbar"><i style="animation-duration:{max(seconds, .1):.2f}s"></i></div></{tag}>""")


# ------------------------------------------------------------------ launch
ROCKET_SVG = one_line("""
<svg viewBox="0 0 90 200" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="rk-b" x1="0" x2="1"><stop offset="0" stop-color="#cbd5e1"/><stop offset=".5" stop-color="#ffffff"/><stop offset="1" stop-color="#94a3b8"/></linearGradient>
 <linearGradient id="rk-f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff7d6"/><stop offset=".35" stop-color="#facc15"/><stop offset=".7" stop-color="#f97316"/><stop offset="1" stop-color="#ef4444" stop-opacity="0"/></linearGradient></defs>
 <g class="flame"><path d="M30 150 Q45 205 60 150 Z" fill="url(#rk-f)" transform="translate(0 0)"/></g>
 <path d="M45 6 C70 30 72 80 66 140 L24 140 C18 80 20 30 45 6 Z" fill="url(#rk-b)"/>
 <path d="M45 6 C55 16 61 28 64 40 L26 40 C29 28 35 16 45 6 Z" fill="#8b5cf6"/>
 <circle cx="45" cy="70" r="11" fill="#0e1330" stroke="#22d3ee" stroke-width="3"/>
 <path d="M24 110 L6 148 L24 140 Z" fill="#7c3aed"/><path d="M66 110 L84 148 L66 140 Z" fill="#7c3aed"/>
 <rect x="30" y="138" width="30" height="10" rx="3" fill="#475569"/>
</svg>""")


def launch_overlay(offset: float) -> str:
    return one_line(f"""
    <div class="launch" style="--lo:{-offset:.2f}s" aria-live="polite">
      <div class="shake"><div class="smoke"></div><div class="rocket">{ROCKET_SVG}</div></div>
      <div class="cd"><span>3</span><span>2</span><span>1</span><span class="go">LIFTOFF</span></div>
    </div>""")


# ------------------------------------------------------------------ results
def podium(final: list[dict]) -> str:
    top = {r["place"]: r for r in final[:3]}

    def slot(place: int, cls: str) -> str:
        r = top.get(place)
        if not r:
            return f'<div class="pod {cls} empty"><div class="base"></div></div>'
        crown = '<div class="crown">👑</div>' if place == 1 else ""
        return one_line(f"""
        <div class="pod {cls}">{crown}<div class="ava">{esc(r['avatar'])}</div>
          <div class="pn">{esc(r['name'])}</div><div class="ps">{r['score']:,}</div>
          <div class="base"><span>{place}</span></div></div>""")

    return f'<div class="podium">{slot(2, "second")}{slot(1, "first")}{slot(3, "third")}</div>'


def rank_card(me: dict) -> str:
    place = me["place"]
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(place if place < 20 else place % 10, "th")
    return one_line(f"""
    <div class="rank-card"><div class="e">{me['rank']['emoji']}</div>
      <div class="ttl">{esc(me['rank']['title'])}</div>
      <div class="sub">You finished {place}{suffix} with {me['correct']} of {me['total']} correct</div></div>""")


def stats(me: dict) -> str:
    avg = f"{me['avg_time']:.1f}s" if me.get("avg_time") is not None else "—"
    return one_line(f"""
    <div class="stats">
      <div class="stat"><b>{me['score']:,}</b><span>points</span></div>
      <div class="stat"><b>{me['accuracy']}%</b><span>accuracy</span></div>
      <div class="stat"><b>{avg}</b><span>avg answer time</span></div>
      <div class="stat"><b>{me['best_streak']}</b><span>best streak</span></div>
    </div>""")


def standings(final: list[dict], me_id: str) -> str:
    rows = []
    for r in final:
        avg = f"{r['avg_time']:.1f}s" if r.get("avg_time") is not None else "—"
        cls = ' class="me"' if r["id"] == me_id else ""
        rows.append(
            f"<tr{cls}><td>{r['place']}</td><td>{esc(r['avatar'])} {esc(r['name'])}</td>"
            f"<td>{r['rank']['emoji']} {esc(r['rank']['title'])}</td><td class='num'>{r['correct']}/{r['total']}</td>"
            f"<td class='num'>{avg}</td><td class='num'>{r['best_streak']}</td><td class='num' style='color:var(--gold)'>{r['score']:,}</td></tr>"
        )
    head = "<tr><th>#</th><th>Astronaut</th><th>Rank</th><th>Correct</th><th>Avg time</th><th>Streak</th><th>Score</th></tr>"
    return f'<div style="overflow-x:auto"><table class="table">{head}{"".join(rows)}</table></div>'


def confetti_script(key: str) -> str:
    """Star-shaped confetti drawn on a full-screen canvas (runs once per key)."""
    return """
<script>
(function () {
  const KEY = %s;
  window.__astroFx = window.__astroFx || {};
  if (window.__astroFx[KEY]) return;
  window.__astroFx[KEY] = true;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const doc = document;
  const c = doc.createElement('canvas');
  c.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:10000';
  doc.body.appendChild(c);
  const ctx = c.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const W = () => window.innerWidth, H = () => window.innerHeight;
  c.width = W() * dpr; c.height = H() * dpr; ctx.scale(dpr, dpr);
  const colors = ['#FACC15', '#22D3EE', '#A78BFA', '#EC4899', '#FFFFFF', '#34D399'];
  const P = [];
  function burst(x, y, n, spread) {
    for (let i = 0; i < n; i++) {
      const a = -Math.PI / 2 + (Math.random() - 0.5) * spread, s = 6 + Math.random() * 10;
      P.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s, r: 3 + Math.random() * 5, rot: Math.random() * 6,
               vr: (Math.random() - 0.5) * 0.3, c: colors[i %% colors.length], life: 1, star: Math.random() < 0.6 });
    }
  }
  function star(x, y, r, rot) {
    ctx.beginPath();
    for (let i = 0; i < 10; i++) {
      const rr = i %% 2 ? r * 0.45 : r, a = rot + i * Math.PI / 5;
      ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr);
    }
    ctx.closePath(); ctx.fill();
  }
  setTimeout(() => burst(W() / 2, H() * 0.42, 140, Math.PI * 1.6), 1900);
  setTimeout(() => { burst(W() * 0.2, H() * 0.75, 70, Math.PI * 0.9); burst(W() * 0.8, H() * 0.75, 70, Math.PI * 0.9); }, 2300);
  setTimeout(() => burst(W() / 2, H() * 0.6, 90, Math.PI * 2), 3000);
  const t0 = performance.now();
  (function frame(t) {
    ctx.clearRect(0, 0, W(), H());
    for (const p of P) {
      p.vy += 0.22; p.vx *= 0.985; p.vy *= 0.985; p.x += p.vx; p.y += p.vy; p.rot += p.vr; p.life -= 0.006;
      ctx.globalAlpha = Math.max(p.life, 0); ctx.fillStyle = p.c;
      if (p.star) star(p.x, p.y, p.r * 1.4, p.rot); else { ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rot); ctx.fillRect(-p.r, -p.r / 2, p.r * 2, p.r); ctx.restore(); }
    }
    for (let i = P.length - 1; i >= 0; i--) if (P[i].life <= 0 || P[i].y > H() + 40) P.splice(i, 1);
    if (t - t0 < 9000) requestAnimationFrame(frame); else c.remove();
  })(t0);
})();
</script>""" % json.dumps(key)
