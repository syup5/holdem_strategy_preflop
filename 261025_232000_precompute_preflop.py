# -*- coding: utf-8 -*-
"""
Preflop data precompute for the Hold'em preflop drill.

  python 261025_232000_precompute_preflop.py equity   # 169x169 all-in equity matrix (Monte Carlo, eval7)
  python 261025_232000_precompute_preflop.py nash     # chipEV Nash push/fold charts (BB ante)
  python 261025_232000_precompute_preflop.py inject <html>  # embed data JSON into the HTML file
  python 261025_232000_precompute_preflop.py pages <html> [index.html]  # standalone page for GitHub Pages

Hand index: h = i*13 + j on the 13x13 grid (rank index 0 = A ... 12 = 2).
  i == j -> pair, i < j -> suited (hi=i, lo=j), i > j -> offsuit (hi=j, lo=i)
"""
import sys, os, json, random, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EQ_NPY = os.path.join(HERE, '261025_232000_equity169.npy')
DATA_JSON = os.path.join(HERE, '261025_232000_preflop_data.json')

RANKS = 'AKQJT98765432'
SUITS = 'shdc'
SAMPLES_PER_MATCHUP = 12000


def hand_name(h):
    i, j = divmod(h, 13)
    if i == j:
        return RANKS[i] * 2
    if i < j:
        return RANKS[i] + RANKS[j] + 's'
    return RANKS[j] + RANKS[i] + 'o'


def class_combos(h):
    i, j = divmod(h, 13)
    if i == j:
        r = RANKS[i]
        return [(r + SUITS[a], r + SUITS[b]) for a in range(4) for b in range(a + 1, 4)]
    if i < j:
        hi, lo = RANKS[i], RANKS[j]
        return [(hi + s, lo + s) for s in SUITS]
    hi, lo = RANKS[j], RANKS[i]
    return [(hi + a, lo + b) for a in SUITS for b in SUITS if a != b]


def compat_matrix():
    """W[h][v] = number of combos of class v that share no card with a fixed combo of class h."""
    W = np.zeros((169, 169))
    for h in range(169):
        rep = set(class_combos(h)[0])
        for v in range(169):
            W[h, v] = sum(1 for c in class_combos(v) if not (set(c) & rep))
    return W


# ---------------------------------------------------------------- equity
def equity_row(h):
    import eval7
    rnd = random.Random(1000 + h)
    deck = {r + s: eval7.Card(r + s) for r in RANKS for s in SUITS}
    rep = class_combos(h)[0]
    hero = [deck[rep[0]], deck[rep[1]]]
    ev = eval7.evaluate
    row = np.zeros(169)
    for v in range(169):
        vc = [c for c in class_combos(v) if not (set(c) & set(rep))]
        if not vc:
            row[v] = np.nan
            continue
        per = max(1, SAMPLES_PER_MATCHUP // len(vc))
        win = 0.0
        n = 0
        for c in vc:
            vil = [deck[c[0]], deck[c[1]]]
            rest = [deck[k] for k in deck if k not in rep and k not in c]
            for _ in range(per):
                b = rnd.sample(rest, 5)
                a = ev(hero + b)
                o = ev(vil + b)
                win += 1.0 if a > o else (0.5 if a == o else 0.0)
            n += per
        row[v] = win / n
    return h, row


def run_equity():
    from multiprocessing import Pool
    t = time.time()
    E = np.zeros((169, 169))
    with Pool(8) as pool:
        for k, (h, row) in enumerate(pool.imap_unordered(equity_row, range(169))):
            E[h] = row
            if k % 20 == 0:
                print(f'  rows {k + 1}/169  {time.time() - t:.0f}s', flush=True)
    # average the two independent estimates of each matchup: E[a,b] and 1 - E[b,a]
    S = (E + (1.0 - E.T)) / 2.0
    S = np.nan_to_num(S, nan=0.5)
    np.save(EQ_NPY, S)
    print(f'equity done in {time.time() - t:.0f}s')
    idx = {hand_name(h): h for h in range(169)}
    for a, b in [('AA', 'KK'), ('AKs', 'QQ'), ('AKo', '22'), ('AA', '72o'), ('JTs', 'AKo'), ('22', 'AKo')]:
        print(f'  {a} vs {b}: {S[idx[a], idx[b]]:.4f}')


# ---------------------------------------------------------------- Nash push/fold
def solve_pushfold(E, Wn, k, S, ante, iters=400):
    """chipEV jam-or-fold equilibrium: one pusher with k players behind (all stacks = S bb).
    Callers act in order; once one calls, the rest fold (no overcalls). Card removal via Wn."""
    D = 1.5 + ante
    p0 = 0.5 if k == 1 else 0.0
    c0 = [1.0] if k == 1 else [0.0] * (k - 2) + [0.5, 1.0]
    pots = [2 * S + D - p0 - c for c in c0]
    WE = Wn * E

    def br_push(C):
        reach = np.ones(169)
        ev = np.zeros(169)
        for i in range(k):
            callp = Wn @ C[i]
            win = WE @ C[i]
            ev += reach * (win * pots[i] - callp * (S - p0))
            reach *= (1.0 - callp)
        ev += reach * D
        return (ev > 0).astype(float), ev

    def br_call(P, i):
        mass = Wn @ P
        win = WE @ P
        with np.errstate(invalid='ignore', divide='ignore'):
            eq = np.where(mass > 0, win / np.maximum(mass, 1e-12), 0.0)
        ev = eq * pots[i] - (S - c0[i])
        return (ev > 0).astype(float), ev

    P = np.ones(169) * 0.3
    C = [np.ones(169) * 0.2 for _ in range(k)]
    for t in range(iters):
        a = 1.0 / (t + 2)
        bp, _ = br_push(C)
        bcs = [br_call(P, i)[0] for i in range(k)]
        P += a * (bp - P)
        for i in range(k):
            C[i] += a * (bcs[i] - C[i])
    push, ev = br_push(C)
    calls = [br_call(P, i)[0] for i in range(k)]
    return push, ev, calls


def run_nash():
    E = np.load(EQ_NPY)
    W = compat_matrix()
    assert np.allclose(W.sum(1), 1225)
    Wn = W / 1225.0
    combos = np.array([len(class_combos(h)) for h in range(169)], dtype=float)
    names = [hand_name(h) for h in range(169)]
    grid = np.arange(1.0, 25.01, 0.5)
    out = {}
    t = time.time()
    for ante in (1.0, 0.0):
        tab = {}
        for k in range(1, 9):
            thr = np.zeros(169)
            for S in grid:
                push, _, _ = solve_pushfold(E, Wn, k, S, ante)
                thr = np.where(push > 0.5, S, thr)  # last (largest) stack at which the hand pushes
            tab[k] = thr
            pct = [(combos * (thr >= s)).sum() / 1326 * 100 for s in (5, 10, 15, 20)]
            print(f'  ante={ante:.0f} k={k}: push% @5/10/15/20bb = ' + ' / '.join(f'{p:.1f}' for p in pct), flush=True)
        out[ante] = tab
    print(f'nash done in {time.time() - t:.0f}s')

    # sanity: SB vs BB, no ante, 10bb
    push, _, calls = solve_pushfold(E, Wn, 1, 10.0, 0.0)
    print('  HU 10bb no ante: SB push %.1f%%, BB call %.1f%%' % (
        (combos * push).sum() / 13.26, (combos * calls[0]).sum() / 13.26))
    for nm in ('K2o', 'Q5o', 'J7o', 'T7o', '72o', '32o', 'A2o', '22'):
        h = names.index(nm)
        print(f'    {nm}: SB push max (no ante) = {out[0.0][1][h]:.1f}bb, (BB ante) = {out[1.0][1][h]:.1f}bb')

    def enc(arr):
        return [round(float(x), 1) for x in arr]

    data = {
        'hands': names,
        'eq': encode_eq(E),
        'nashGrid': [float(grid[0]), float(grid[-1]), 0.5],
        'nashPushBBAnte': {str(k): enc(out[1.0][k]) for k in range(1, 9)},
        'nashPushNoAnte': {str(k): enc(out[0.0][k]) for k in range(1, 9)},
        'meta': {
            'samplesPerMatchup': SAMPLES_PER_MATCHUP * 2,
            'model': 'chipEV jam-or-fold, equal stacks, no overcalls, card removal via combo compatibility',
        },
    }
    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print('wrote', DATA_JSON, os.path.getsize(DATA_JSON), 'bytes')


B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'


def encode_eq(E):
    """Each equity -> round(e*4095) -> 2 base64 chars, row-major 169x169."""
    s = []
    for x in E.flatten():
        n = int(round(float(np.clip(x, 0, 1)) * 4095))
        s.append(B64[n >> 6] + B64[n & 63])
    return ''.join(s)


# ---------------------------------------------------------------- inject
def run_inject(html_path):
    with open(DATA_JSON, encoding='utf-8') as f:
        data = f.read()
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    a = html.index('/*DATA_START*/')
    b = html.index('/*DATA_END*/')
    html = html[:a] + '/*DATA_START*/' + data + html[b:]
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('injected', len(data), 'bytes into', html_path)


# ---------------------------------------------------------------- GitHub Pages build
PAGE_DESC = '랜덤으로 생성되는 프리플랍 상황에서 폴드·콜·레이즈 사이즈를 고르고, 전략서 이론·레인지 차트·내쉬 푸시/폴드 EV로 해설을 받는 홀덤 연습 게임'


def run_pages(src_html, out_html):
    """Wrap the artifact page (body content only) into a standalone HTML document for GitHub Pages."""
    with open(src_html, encoding='utf-8') as f:
        src = f.read()
    cut = src.index('<div class="wrap" id="app">')
    head, body = src[:cut], src[cut:]
    head = head.replace('<meta charset="utf-8">\n', '').replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    base = ('<style>html{color-scheme:light}:root{padding-top:env(safe-area-inset-top,0px);'
            'padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}'
            '[hidden]{display:none!important}</style>\n')
    page = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<meta name="description" content="{PAGE_DESC}">\n'
            '<meta property="og:title" content="홀덤 프리플랍 드릴">\n'
            f'<meta property="og:description" content="{PAGE_DESC}">\n'
            '<meta property="og:type" content="website">\n'
            + base + head + '</head>\n<body>\n' + body.rstrip() + '\n</body>\n</html>\n')
    with open(out_html, 'w', encoding='utf-8', newline='\n') as f:
        f.write(page)
    print('wrote', out_html, len(page.encode('utf-8')), 'bytes')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'equity':
        run_equity()
    elif cmd == 'nash':
        run_nash()
    elif cmd == 'inject':
        run_inject(sys.argv[2])
    elif cmd == 'pages':
        run_pages(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, 'index.html'))
    else:
        print(__doc__)
