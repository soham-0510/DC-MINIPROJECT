"""
Hand-drawn SVG illustrations for the Visual Round.

The server only sends a short key (e.g. "saturn"); the client turns it into
artwork. This keeps RPC messages tiny and needs no internet or image files.
"""

SVGS = {
"saturn": """
<svg viewBox="0 0 240 200" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <radialGradient id="sat-b" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#fff3cf"/><stop offset=".45" stop-color="#e9c97d"/><stop offset="1" stop-color="#6b4c1e"/></radialGradient>
  <linearGradient id="sat-r" x1="0" x2="1"><stop offset="0" stop-color="#b8955a" stop-opacity=".35"/><stop offset=".5" stop-color="#f6e4b5"/><stop offset="1" stop-color="#b8955a" stop-opacity=".35"/></linearGradient>
  <clipPath id="sat-c"><circle cx="120" cy="100" r="54"/></clipPath>
 </defs>
 <path d="M15.2 126.1 A108 26 -14 0 1 224.8 73.9" fill="none" stroke="url(#sat-r)" stroke-width="12" opacity=".75"/>
 <circle cx="120" cy="100" r="54" fill="url(#sat-b)"/>
 <g clip-path="url(#sat-c)" opacity=".3" fill="none" stroke="#8a6a32" stroke-width="6"><path d="M60 82 Q120 74 180 66"/><path d="M60 106 Q120 98 180 90"/><path d="M62 128 Q120 120 178 112"/></g>
 <path d="M15.2 126.1 A108 26 -14 0 0 224.8 73.9" fill="none" stroke="url(#sat-r)" stroke-width="12"/>
 <path d="M15.2 126.1 A108 26 -14 0 0 224.8 73.9" fill="none" stroke="#3b2a10" stroke-width="1.5" opacity=".5"/>
</svg>""",

"jupiter": """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <radialGradient id="jup-s" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>
  <clipPath id="jup-c"><circle cx="100" cy="100" r="80"/></clipPath>
 </defs>
 <g clip-path="url(#jup-c)">
  <rect x="0" y="0" width="200" height="200" fill="#e8d3b0"/>
  <rect x="0" y="30" width="200" height="16" fill="#b9825a"/><rect x="0" y="58" width="200" height="12" fill="#d9a877"/>
  <rect x="0" y="78" width="200" height="20" fill="#a86b44"/><rect x="0" y="108" width="200" height="10" fill="#f1e2c6"/>
  <rect x="0" y="124" width="200" height="18" fill="#b9825a"/><rect x="0" y="150" width="200" height="10" fill="#d9a877"/>
  <ellipse cx="128" cy="132" rx="17" ry="10" fill="#c4512f"/><ellipse cx="128" cy="132" rx="10" ry="5" fill="#de7a52"/>
  <rect x="0" y="0" width="200" height="200" fill="url(#jup-s)"/>
 </g>
</svg>""",

"mars": """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <radialGradient id="mar-b" cx="38%" cy="32%" r="78%"><stop offset="0" stop-color="#f6a173"/><stop offset=".5" stop-color="#c1440e"/><stop offset="1" stop-color="#4a1405"/></radialGradient>
  <clipPath id="mar-c"><circle cx="100" cy="100" r="76"/></clipPath>
 </defs>
 <circle cx="100" cy="100" r="76" fill="url(#mar-b)"/>
 <g clip-path="url(#mar-c)" fill="#7a2a0c" opacity=".55">
  <path d="M40 92 q30 -10 60 4 t70 -6 v16 q-40 10 -70 0 t-60 6z"/><ellipse cx="70" cy="130" rx="18" ry="8"/><ellipse cx="135" cy="70" rx="12" ry="6"/>
 </g>
 <ellipse cx="100" cy="30" rx="26" ry="8" fill="#fff" opacity=".9" clip-path="url(#mar-c)"/>
</svg>""",

"earth": """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <radialGradient id="ear-b" cx="38%" cy="32%" r="78%"><stop offset="0" stop-color="#7dd3fc"/><stop offset=".55" stop-color="#1d4ed8"/><stop offset="1" stop-color="#0b1a4a"/></radialGradient>
  <radialGradient id="ear-a" cx="50%" cy="50%" r="50%"><stop offset=".86" stop-color="#7dd3fc" stop-opacity="0"/><stop offset="1" stop-color="#7dd3fc" stop-opacity=".6"/></radialGradient>
  <clipPath id="ear-c"><circle cx="100" cy="100" r="74"/></clipPath>
 </defs>
 <circle cx="100" cy="100" r="84" fill="url(#ear-a)"/>
 <circle cx="100" cy="100" r="74" fill="url(#ear-b)"/>
 <g clip-path="url(#ear-c)" fill="#22a35a">
  <path d="M48 70 q14 -22 40 -14 q10 12 -4 22 q-6 16 6 30 q-6 14 -22 10 q-10 -18 -24 -20 q-8 -14 4 -28z"/>
  <path d="M112 56 q24 -8 44 8 q8 18 -8 26 q-16 -2 -20 10 q8 18 -4 30 q-14 6 -18 -10 q-6 -20 4 -34 q-10 -16 2 -30z"/>
 </g>
 <g clip-path="url(#ear-c)" fill="#fff" opacity=".75"><path d="M30 120 q30 -8 60 2 q20 6 40 -2 v6 q-24 8 -44 2 q-30 -8 -56 -2z"/><path d="M90 40 q20 -6 50 0 v5 q-24 -2 -50 2z"/></g>
</svg>""",

"uranus": """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 <defs><radialGradient id="ura-b" cx="38%" cy="32%" r="78%"><stop offset="0" stop-color="#e0fbff"/><stop offset=".5" stop-color="#7fdbe6"/><stop offset="1" stop-color="#1c5a66"/></radialGradient></defs>
 <ellipse cx="100" cy="100" rx="22" ry="92" fill="none" stroke="#cdeff3" stroke-opacity=".55" stroke-width="3" transform="rotate(8 100 100)"/>
 <circle cx="100" cy="100" r="62" fill="url(#ura-b)"/>
 <path d="M86 8 A22 92 8 0 1 115 37" fill="none" stroke="#cdeff3" stroke-opacity=".55" stroke-width="3"/>
</svg>""",

"neptune": """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 <defs><radialGradient id="nep-b" cx="38%" cy="32%" r="78%"><stop offset="0" stop-color="#93c5fd"/><stop offset=".5" stop-color="#2546c4"/><stop offset="1" stop-color="#0a1450"/></radialGradient>
 <clipPath id="nep-c"><circle cx="100" cy="100" r="74"/></clipPath></defs>
 <circle cx="100" cy="100" r="74" fill="url(#nep-b)"/>
 <g clip-path="url(#nep-c)"><path d="M26 80 Q100 70 174 82" stroke="#6b8cff" stroke-opacity=".35" stroke-width="6" fill="none"/>
 <path d="M26 124 Q100 116 174 128" stroke="#6b8cff" stroke-opacity=".3" stroke-width="5" fill="none"/>
 <ellipse cx="78" cy="104" rx="16" ry="9" fill="#0b1440" opacity=".8"/><path d="M60 98 q18 -6 34 0" stroke="#fff" stroke-opacity=".75" stroke-width="3" fill="none"/></g>
</svg>""",

"spiral_galaxy": """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 <defs><radialGradient id="gal-c" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff7d6"/><stop offset=".25" stop-color="#fde68a" stop-opacity=".9"/><stop offset="1" stop-color="#8b5cf6" stop-opacity="0"/></radialGradient></defs>
 <g transform="translate(100 100)">
  <g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="60s" repeatCount="indefinite"/>
  <path d="M0 0 C 30 -10 60 10 58 44 C 56 70 20 84 -10 80" fill="none" stroke="#a5b4fc" stroke-width="10" stroke-opacity=".55" stroke-linecap="round"/>
  <path d="M0 0 C -30 10 -60 -10 -58 -44 C -56 -70 -20 -84 10 -80" fill="none" stroke="#a5b4fc" stroke-width="10" stroke-opacity=".55" stroke-linecap="round"/>
  <path d="M0 0 C 30 -10 60 10 58 44 C 56 70 20 84 -10 80" fill="none" stroke="#67e8f9" stroke-width="3" stroke-opacity=".8"/>
  <path d="M0 0 C -30 10 -60 -10 -58 -44 C -56 -70 -20 -84 10 -80" fill="none" stroke="#67e8f9" stroke-width="3" stroke-opacity=".8"/>
  <g fill="#fff"><circle cx="52" cy="30" r="1.6"/><circle cx="40" cy="66" r="1.3"/><circle cx="-52" cy="-30" r="1.6"/><circle cx="-38" cy="-66" r="1.3"/><circle cx="20" cy="76" r="1.2"/><circle cx="-20" cy="-76" r="1.2"/><circle cx="60" cy="50" r="1"/><circle cx="-60" cy="-50" r="1"/></g>
  </g>
  <circle r="34" fill="url(#gal-c)"/>
 </g>
</svg>""",

"comet": """
<svg viewBox="0 0 240 180" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <linearGradient id="com-t" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#a5f3fc" stop-opacity=".95"/><stop offset="1" stop-color="#a5f3fc" stop-opacity="0"/></linearGradient>
  <linearGradient id="com-d" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fde68a" stop-opacity=".8"/><stop offset="1" stop-color="#fde68a" stop-opacity="0"/></linearGradient>
  <radialGradient id="com-sun"><stop offset="0" stop-color="#fff7d6"/><stop offset=".4" stop-color="#facc15"/><stop offset="1" stop-color="#f59e0b" stop-opacity="0"/></radialGradient>
 </defs>
 <circle cx="210" cy="40" r="34" fill="url(#com-sun)"/>
 <path d="M150 82 L20 40 L22 60 Z" fill="url(#com-t)"/>
 <path d="M150 84 Q80 96 18 128 L24 112 Q90 86 150 84Z" fill="url(#com-d)"/>
 <circle cx="152" cy="84" r="9" fill="#e0fbff"/><circle cx="152" cy="84" r="16" fill="#a5f3fc" opacity=".25"/>
</svg>""",

"orion": """
<svg viewBox="0 0 200 220" xmlns="http://www.w3.org/2000/svg">
 <g stroke="#a5b4fc" stroke-opacity=".45" stroke-width="1.6" fill="none">
  <path d="M62 40 L84 98 L100 104 L116 110 L140 46"/><path d="M84 98 L66 178"/><path d="M116 110 L144 184"/><path d="M62 40 L100 20 L140 46"/>
 </g>
 <g fill="#fff">
  <circle cx="62" cy="40" r="6" fill="#fb923c"><animate attributeName="opacity" values="1;.6;1" dur="3s" repeatCount="indefinite"/></circle>
  <circle cx="140" cy="46" r="4.2"/><circle cx="100" cy="20" r="2.8"/>
  <circle cx="84" cy="98" r="3.6"/><circle cx="100" cy="104" r="3.6"/><circle cx="116" cy="110" r="3.6"/>
  <circle cx="66" cy="178" r="3.6"/><circle cx="144" cy="184" r="5.6" fill="#bfdbfe"><animate attributeName="opacity" values="1;.65;1" dur="2.4s" repeatCount="indefinite"/></circle>
  <circle cx="102" cy="132" r="1.8" fill="#f9a8d4"/>
 </g>
</svg>""",

"big_dipper": """
<svg viewBox="0 0 240 170" xmlns="http://www.w3.org/2000/svg">
 <path d="M20 40 L66 54 L104 74 L138 96 L146 140 L206 146 L212 98 Z" stroke="#a5b4fc" stroke-opacity=".45" stroke-width="1.6" fill="none"/>
 <path d="M138 96 L212 98" stroke="#a5b4fc" stroke-opacity=".45" stroke-width="1.6"/>
 <g fill="#fff"><circle cx="20" cy="40" r="4"/><circle cx="66" cy="54" r="4"/><circle cx="104" cy="74" r="3.6"/><circle cx="138" cy="96" r="3.2"/>
 <circle cx="146" cy="140" r="4"/><circle cx="206" cy="146" r="4.2"/><circle cx="212" cy="98" r="4.4"><animate attributeName="opacity" values="1;.6;1" dur="2.8s" repeatCount="indefinite"/></circle></g>
</svg>""",

"cassiopeia": """
<svg viewBox="0 0 240 140" xmlns="http://www.w3.org/2000/svg">
 <path d="M20 40 L70 100 L118 58 L164 108 L220 46" stroke="#a5b4fc" stroke-opacity=".45" stroke-width="1.6" fill="none"/>
 <g fill="#fff"><circle cx="20" cy="40" r="4.2"/><circle cx="70" cy="100" r="4.6"/><circle cx="118" cy="58" r="5"><animate attributeName="opacity" values="1;.6;1" dur="2.6s" repeatCount="indefinite"/></circle><circle cx="164" cy="108" r="4"/><circle cx="220" cy="46" r="4"/></g>
</svg>""",

"black_hole": """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <radialGradient id="bh-r" cx="50%" cy="50%" r="50%"><stop offset=".42" stop-color="#000"/><stop offset=".5" stop-color="#ffd27a"/><stop offset=".62" stop-color="#f97316"/><stop offset=".8" stop-color="#7c2d12" stop-opacity=".6"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
 </defs>
 <circle cx="100" cy="100" r="90" fill="url(#bh-r)"><animate attributeName="r" values="88;92;88" dur="4s" repeatCount="indefinite"/></circle>
 <path d="M44 74 A60 60 0 0 1 156 74" stroke="#fff3c4" stroke-opacity=".75" stroke-width="5" fill="none" stroke-linecap="round"/>
 <circle cx="100" cy="100" r="37" fill="#000"/>
</svg>""",

"eclipse": """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 <defs><radialGradient id="ecl-c" cx="50%" cy="50%" r="50%"><stop offset=".38" stop-color="#ffffff"/><stop offset=".5" stop-color="#e0f2fe" stop-opacity=".8"/><stop offset="1" stop-color="#1e3a8a" stop-opacity="0"/></radialGradient></defs>
 <g transform="translate(100 100)"><g opacity=".7" stroke="#e0f2fe" stroke-width="2" stroke-linecap="round">
  <path d="M0 -50 L0 -86"/><path d="M0 50 L0 82"/><path d="M-50 0 L-90 0"/><path d="M50 0 L88 0"/><path d="M36 -36 L62 -60"/><path d="M-36 36 L-58 58"/><path d="M-36 -36 L-60 -62"/><path d="M36 36 L60 58"/>
  <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="90s" repeatCount="indefinite"/></g>
  <circle r="78" fill="url(#ecl-c)"/><circle r="40" fill="#05070f"/></g>
</svg>""",

"waxing_crescent": """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
 <defs><radialGradient id="moo-g" cx="60%" cy="40%" r="70%"><stop offset="0" stop-color="#fffbe6"/><stop offset="1" stop-color="#cbbf98"/></radialGradient>
 <mask id="moo-m"><rect width="200" height="200" fill="#000"/><circle cx="100" cy="100" r="66" fill="#fff"/><circle cx="72" cy="100" r="66" fill="#000"/></mask></defs>
 <circle cx="100" cy="100" r="66" fill="#1a1d33" opacity=".7"/>
 <circle cx="100" cy="100" r="66" fill="url(#moo-g)" mask="url(#moo-m)"/>
</svg>""",

"nebula": """
<svg viewBox="0 0 220 180" xmlns="http://www.w3.org/2000/svg">
 <defs>
  <filter id="neb-b" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
 </defs>
 <g filter="url(#neb-b)">
  <ellipse cx="90" cy="90" rx="62" ry="40" fill="#ec4899" opacity=".55"><animate attributeName="rx" values="62;68;62" dur="7s" repeatCount="indefinite"/></ellipse>
  <ellipse cx="130" cy="80" rx="54" ry="44" fill="#8b5cf6" opacity=".6"/>
  <ellipse cx="110" cy="110" rx="46" ry="26" fill="#22d3ee" opacity=".45"><animate attributeName="ry" values="26;32;26" dur="9s" repeatCount="indefinite"/></ellipse>
 </g>
 <g fill="#fff"><circle cx="110" cy="92" r="3"/><circle cx="70" cy="70" r="1.6"/><circle cx="150" cy="110" r="1.8"/><circle cx="160" cy="58" r="1.2"/><circle cx="56" cy="118" r="1.2"/></g>
</svg>""",
}


def svg_for(key: str | None) -> str:
    if not key:
        return ""
    # strip newlines so the SVG survives markdown rendering intact
    return " ".join(SVGS.get(key, "").split())
