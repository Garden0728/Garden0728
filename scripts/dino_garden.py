#!/usr/bin/env python3
"""
Jurassic Garden — 내 GitHub 잔디 위에서 공룡들이 노는 애니메이션 SVG 생성기.

usage:
  GITHUB_TOKEN=xxx python scripts/dino_garden.py Garden0728 assets/dino-garden.svg
  python scripts/dino_garden.py --sample assets/dino-garden.svg   # 샘플 데이터로 미리보기
표준 라이브러리만 사용합니다.
"""
import json
import os
import random
import re
import sys
import urllib.request

# ---------------------------------------------------------------- data
def fetch_graphql(user, token):
    q = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
      totalContributions weeks{contributionDays{date contributionCount contributionLevel weekday}}}}}}"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"u": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    lv = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    weeks = []
    for w in cal["weeks"]:
        col = [None] * 7
        for d in w["contributionDays"]:
            col[d["weekday"]] = lv[d["contributionLevel"]]
        weeks.append(col)
    return weeks, cal["totalContributions"]


def fetch_html(user):
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions",
                                 headers={"User-Agent": "jurassic-garden"})
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    cells = re.findall(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*?data-level="(\d)"', html)
    import datetime as dt
    cells.sort()
    weeks, col = [], [None] * 7
    for ds, lvl in cells:
        wd = (dt.date.fromisoformat(ds).weekday() + 1) % 7  # Sun=0
        if wd == 0 and any(c is not None for c in col):
            weeks.append(col); col = [None] * 7
        col[wd] = int(lvl)
    weeks.append(col)
    m = re.search(r"([\d,]+)\s+contributions?", html)
    total = int(m.group(1).replace(",", "")) if m else 0
    return weeks, total


def sample():
    rnd = random.Random(728)
    weeks = []
    for w in range(53):
        hot = 0.35 + 0.45 * abs(((w % 18) - 9) / 9)
        weeks.append([min(4, int(rnd.random() ** (1.6 - hot) * 5)) if rnd.random() < hot + 0.2 else 0
                      for _ in range(7)])
    weeks[-1] = weeks[-1][:3] + [None] * 4
    return weeks, sum((c or 0) * 3 for col in weeks for c in col)

# ---------------------------------------------------------------- sprites (오른쪽을 바라봄)
SPRITES = {
    "rex": [
        "...........gggggg.",
        "..........ggwkgggg",
        "..........gggggggg",
        "..........ggggt.t.",
        "..........gggggg..",
        "g........ggggg....",
        "g.......ggggggd...",
        "gg.....ggggggg.d..",
        "ggg...gggggggg....",
        ".gggggggggggggg...",
        "..ggggssssgggg....",
        "...gggssssggg.....",
        "....ggggggggg.....",
    ],
    "rex_a": [".....gg...gg......", ".....g.....g......", ".....gg....gg....."],
    "rex_b": ["......gg.gg.......", "......g..g........", ".....gg..gg......."],

    "tri": [
        "..............h...h.",
        ".............hh..hh.",
        "...........yyyggg...",
        "..........yyyyggwgg.",
        "..ssss....yyyyggggh.",
        ".ggggggggggyyyggggg.",
        "gggggggggggggggggg..",
        "gggggggggggggggg....",
        ".ggggggggggggggg....",
        "..bbbbbbbbbbbbb.....",
    ],
    "tri_a": ["..gg..gg...gg..gg...", "..gg..gg...gg..gg..."],
    "tri_b": ["...gg..gg...gg..gg..", "..gg..gg...gg..gg..."],

    "rap": [
        "...........ggg..",
        "..........ggwgg.",
        "..........gggggg",
        "..........ggg.t.",
        "g........ggg....",
        ".gg....gggggd...",
        "..ggggggsggg.d..",
        "....ggggggg.....",
    ],
    "rap_a": [".....g...g......", "....g.....g.....", "...gg....gg....."],
    "rap_b": ["......g.g.......", "......g.g.......", ".....gg.gg......"],

    "ptero_a": [
        "gg..............gg",
        ".ggg..........ggg.",
        "..gggg......gggg..",
        "...ggggg..ggggg...",
        "....gggggggggwkgg.",
        ".......gggg....gg.",
    ],
    "ptero_b": [
        "..................",
        "..................",
        "....gggggggggwkgg.",
        "...ggggggggggg..gg",
        "..gggg..gggg......",
        ".ggg........ggg...",
    ],
    "egg": ["..www..", ".wwwww.", "wwswwww", "wwwwsww", "wswwwww", ".wwwww.", "..www.."],
}

PALETTES = {
    "rex":  {"g": "#7c9a3d", "s": "#a9c46a", "w": "#fff7d6", "k": "#111", "t": "#fffbe8", "d": "#5e7a2b"},
    "tri":  {"g": "#d0813a", "y": "#e8b24a", "h": "#fff1c9", "w": "#fff7d6", "s": "#9e5a22", "b": "#f0b979"},
    "rap":  {"g": "#3aa6a0", "s": "#7fd6cf", "w": "#fff7d6", "k": "#111", "t": "#fffbe8", "d": "#2b7d78"},
    "rap2": {"g": "#8a6ad6", "s": "#b9a3f0", "w": "#fff7d6", "k": "#111", "t": "#fffbe8", "d": "#6a4fb0"},
    "ptero": {"g": "#c25b6e", "w": "#fff7d6", "k": "#111"},
    "egg":  {"w": "#f3ead2", "s": "#c9a86a"},
}
PALETTES["rap"]["k"] = PALETTES["rap2"]["k"] = "#111"
for p in ("rex", "rap", "rap2"):  # eye pupil = 'k' right after 'w'
    PALETTES[p].setdefault("k", "#111")


def sprite_rects(rows, pal, px, ox=0, oy=0):
    w = max(len(r) for r in rows)
    out = []
    for y, row in enumerate(rows):
        row = row.ljust(w, ".")
        x = 0
        while x < w:
            ch = row[x]
            if ch == ".":
                x += 1; continue
            run = 1
            while x + run < w and row[x + run] == ch:
                run += 1
            out.append(f'<rect x="{ox + x*px}" y="{oy + y*px}" width="{run*px}" height="{px}" fill="{pal.get(ch, "#000")}"/>')
            x += run
    return "".join(out)


def walker(kind, pal, px):
    """몸통 + 2프레임 다리. 원점 = 발바닥 중앙."""
    body = SPRITES[kind]
    la, lb = SPRITES[kind + "_a"], SPRITES[kind + "_b"]
    w = max(len(r) for r in body + la)
    h = len(body) + len(la)
    ox, oy = -w * px / 2, -h * px
    legs_y = oy + len(body) * px
    return (sprite_rects(body, pal, px, ox, oy)
            + f'<g>{sprite_rects(la, pal, px, ox, legs_y)}'
              f'<animate attributeName="opacity" values="1;0" dur="0.5s" calcMode="discrete" repeatCount="indefinite"/></g>'
            + f'<g opacity="0">{sprite_rects(lb, pal, px, ox, legs_y)}'
              f'<animate attributeName="opacity" values="0;1" dur="0.5s" calcMode="discrete" repeatCount="indefinite"/></g>'), w * px, h * px

# ---------------------------------------------------------------- render
LEVEL = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
SOIL = "#2a1f14"


def render(weeks, total, user):
    CELL, PITCH, PX = 11, 14, 2
    W = len(weeks)
    L, TOP = 24, 92
    width = L * 2 + W * PITCH - (PITCH - CELL)
    gh = 7 * PITCH - (PITCH - CELL)
    height = TOP + gh + 46
    T = 24.0  # loop seconds

    def cx(c): return L + c * PITCH + CELL / 2
    def ry(r): return TOP + r * PITCH  # top of row

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" shape-rendering="crispEdges">',
             '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#1a1030"/><stop offset=".55" stop-color="#3a1f2a"/><stop offset="1" stop-color="#0d1117"/></linearGradient>'
             '<radialGradient id="lava" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffcf5a"/><stop offset="1" stop-color="#ff5a1f" stop-opacity="0"/></radialGradient></defs>',
             f'<rect width="{width}" height="{height}" rx="10" fill="#0d1117"/>',
             f'<rect width="{width}" height="{TOP - 6}" rx="10" fill="url(#sky)"/>']

    # 별
    rnd = random.Random(7)
    for _ in range(28):
        x, y = rnd.uniform(10, width - 10), rnd.uniform(6, TOP - 40)
        d = rnd.uniform(2, 5)
        parts.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="2" height="2" fill="#fff3c4">'
                     f'<animate attributeName="opacity" values="1;.2;1" dur="{d:.1f}s" repeatCount="indefinite"/></rect>')

    # 화산 + 연기
    vx, vb = width - 120, TOP - 6
    parts.append(f'<circle cx="{vx}" cy="{vb - 46}" r="26" fill="url(#lava)" opacity=".7">'
                 f'<animate attributeName="opacity" values=".4;.9;.4" dur="3s" repeatCount="indefinite"/></circle>')
    parts.append(f'<path d="M{vx-70} {vb} L{vx-12} {vb-46} L{vx+12} {vb-46} L{vx+70} {vb} Z" fill="#241826"/>')
    parts.append(f'<path d="M{vx-12} {vb-46} L{vx+12} {vb-46} L{vx+6} {vb-38} L{vx} {vb-42} L{vx-6} {vb-36} Z" fill="#ff7a2e"/>')
    for i in range(4):
        parts.append(f'<circle cx="{vx}" cy="{vb-50}" r="5" fill="#6b5a6e" opacity="0">'
                     f'<animate attributeName="cy" values="{vb-50};{vb-88}" dur="4s" begin="{i}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="cx" values="{vx};{vx+18}" dur="4s" begin="{i}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="r" values="4;12" dur="4s" begin="{i}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values=".8;0" dur="4s" begin="{i}s" repeatCount="indefinite"/></circle>')

    # 정글 실루엣 (지평선)
    hills = f'M0 {TOP-6} '
    for i in range(0, width + 40, 40):
        hills += f'Q{i+20} {TOP-6-rnd.uniform(8,20):.0f} {i+40} {TOP-6} '
    parts.append(f'<path d="{hills} L{width} {TOP-6} Z" fill="#132a1c"/>')
    for x in (60, 190, width - 260):
        parts.append(palm(x, TOP - 6, rnd.uniform(.8, 1.1)))

    # ---- 초식공룡(트리케라톱스)이 지나간 칸은 뜯어먹혔다가 다시 자람
    tri_row = 3
    tri_a, tri_b = cx(2), cx(W - 3)
    mouth = 18
    eaten = {}
    for c in range(W):
        lvl = weeks[c][tri_row]
        if not lvl:
            continue
        x = cx(c)
        times = []
        if tri_a + mouth <= x <= tri_b + mouth:
            times.append((x - mouth - tri_a) / (tri_b - tri_a) * T / 2)
        if tri_a - mouth <= x <= tri_b - mouth:
            times.append(T / 2 + (tri_b - (x + mouth)) / (tri_b - tri_a) * T / 2)
        if times:
            eaten[c] = sorted(times)

    def regrow_anim(lvl, times):
        regrow = 5.0
        kt, vals = [0.0], [LEVEL[lvl]]
        for t in times:
            seq = [(t, LEVEL[lvl]), (t + .05, SOIL)]
            steps = list(range(1, lvl + 1))
            for i, s in enumerate(steps):
                seq.append((t + .05 + regrow * (i + 1) / len(steps), LEVEL[s]))
            for tt, v in seq:
                tt = min(max(tt, kt[-1] + .001), T)
                kt.append(tt); vals.append(v)
        if kt[-1] < T:
            kt.append(T); vals.append(LEVEL[lvl])
        kts = ";".join(f"{k / T:.4f}" for k in kt)
        kts = kts[: kts.rfind(";")] + ";1"
        return (f'<animate attributeName="fill" values="{";".join(vals)}" keyTimes="{kts}" '
                f'dur="{T}s" calcMode="discrete" repeatCount="indefinite"/>')

    for c, col in enumerate(weeks):
        for r, lvl in enumerate(col):
            if lvl is None:
                continue
            x, y = L + c * PITCH, ry(r)
            anim = regrow_anim(lvl, eaten[c]) if (r == tri_row and c in eaten) else ""
            parts.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LEVEL[lvl]}">{anim}</rect>')
            if lvl == 4 and r != tri_row and (c * 7 + r) % 3 == 0:  # 무성한 풀
                parts.append(f'<path d="M{x+2} {y+3} l1 -4 l1 4 M{x+6} {y+3} l1 -5 l1 5" stroke="#5be37a" stroke-width="1" fill="none"/>')

    # 알 (가끔 흔들림)
    ex, ey = L - 4, ry(7) + 8
    parts.append(f'<g transform="translate({ex} {ey})"><g>'
                 f'{sprite_rects(SPRITES["egg"], PALETTES["egg"], 2, -7, -14)}'
                 f'<animateTransform attributeName="transform" type="rotate" values="0;0;-12;12;-8;0;0" '
                 f'keyTimes="0;.7;.75;.8;.85;.9;1" dur="6s" repeatCount="indefinite"/></g></g>')

    # ---- 공룡들
    def patrol(svg_body, x0, x1, y, dur, begin=0.0, extra=""):
        flip = "1 1;-1 1" if x1 > x0 else "-1 1;1 1"
        return (f'<g><g>{svg_body}'
                f'<animateTransform attributeName="transform" type="scale" values="{flip}" keyTimes="0;.5" '
                f'calcMode="discrete" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></g>{extra}'
                f'<animateMotion path="M{x0} {y} L{x1} {y} L{x0} {y}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></g>')

    tri, _, _ = walker("tri", PALETTES["tri"], PX)
    parts.append(patrol(tri, tri_a, tri_b, ry(tri_row) + CELL + 1, T))

    rex, rw, rh = walker("rex", PALETTES["rex"], PX)
    roar = (f'<g opacity="0"><rect x="-22" y="{-rh-22}" width="44" height="16" rx="4" fill="#fff3c4"/>'
            f'<path d="M-2 {-rh-6} l4 0 l-2 5 z" fill="#fff3c4"/>'
            f'<text x="0" y="{-rh-10}" text-anchor="middle" font-family="monospace" font-weight="700" font-size="10" fill="#3a1f2a">RAWR!</text>'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0;1;1;0" keyTimes="0;.2;.21;.3;.31;.7;.71;.8;1" '
            f'calcMode="discrete" dur="{T*1.5}s" repeatCount="indefinite"/></g>')
    parts.append(patrol(rex, cx(W - 6), cx(8), ry(6) + CELL + 1, T * 1.5, 0, roar))

    rap1, _, _ = walker("rap", PALETTES["rap"], PX)
    rap2, _, _ = walker("rap", PALETTES["rap2"], PX)
    parts.append(patrol(rap1, cx(1), cx(W - 2), ry(1) + CELL + 1, 9))
    parts.append(patrol(rap2, cx(1), cx(W - 2), ry(1) + CELL + 1, 9, -0.9))

    pa = sprite_rects(SPRITES["ptero_a"], PALETTES["ptero"], PX, -18, -12)
    pb = sprite_rects(SPRITES["ptero_b"], PALETTES["ptero"], PX, -18, -12)
    flap = lambda s, v: (f'<g opacity="{v[0]}">{s}<animate attributeName="opacity" values="{v}" dur=".6s" '
                         f'calcMode="discrete" repeatCount="indefinite"/></g>')
    fy = 34
    wave = " ".join(f"L{x} {fy + (8 if i % 2 else -8)}" for i, x in enumerate(range(-40, width + 80, 60)))
    parts.append(f'<g>{flap(pa, "1;0")}{flap(pb, "0;1")}'
                 f'<animateMotion path="M-40 {fy} {wave}" dur="14s" repeatCount="indefinite"/></g>')

    # 캡션
    parts.append(f'<text x="{L}" y="{height - 16}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12" fill="#8b949e">'
                 f'<tspan fill="#f2b134" font-weight="700">{total}</tspan> contributions in the last year · {user}\'s Jurassic Garden</text>')
    lx = width - L - 5 * 15 - 60
    parts.append(f'<text x="{lx}" y="{height - 16}" font-family="ui-monospace,monospace" font-size="11" fill="#8b949e">Less</text>')
    for i, col in enumerate(LEVEL):
        parts.append(f'<rect x="{lx + 30 + i*15}" y="{height - 26}" width="11" height="11" rx="2" fill="{col}"/>')
    parts.append(f'<text x="{lx + 30 + 5*15 + 3}" y="{height - 16}" font-family="ui-monospace,monospace" font-size="11" fill="#8b949e">More</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def palm(x, base, s):
    h = 52 * s
    top = (x + 10 * s, base - h)
    fronds = "".join(
        f'<path d="M{top[0]:.0f} {top[1]:.0f} q{dx*s*.5:.0f} {-14*s:.0f} {dx*s:.0f} {dy*s:.0f}" stroke="#0f2318" stroke-width="{4*s:.1f}" fill="none" stroke-linecap="round"/>'
        for dx, dy in ((-30, 10), (-22, 18), (30, 10), (22, 18), (2, -6), (-10, 22), (12, 22)))
    return (f'<path d="M{x} {base} q{4*s:.0f} {-h/2:.0f} {10*s:.0f} {-h:.0f}" stroke="#0f2318" stroke-width="{4*s:.1f}" fill="none"/>'
            + fronds)


def main():
    args = sys.argv[1:]
    if args and args[0] == "--sample":
        weeks, total = sample(); user = "Garden0728"; out = args[1]
    else:
        user, out = args[0], args[1]
        token = os.environ.get("GITHUB_TOKEN")
        try:
            weeks, total = fetch_graphql(user, token) if token else fetch_html(user)
        except Exception as e:  # noqa
            print("graphql failed, falling back to html:", e)
            weeks, total = fetch_html(user)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(weeks, total, user))
    print("wrote", out, "weeks:", len(weeks), "total:", total)


if __name__ == "__main__":
    main()
