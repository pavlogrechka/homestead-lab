import json, sys
cfg = json.load(open(sys.argv[1]))
W, H = cfg['W'], cfg['H']
F = cfg['furniture']
BED_W, BED_L = F['bed_w'], F['bed_l']
NS_W, NS_D = F['ns_w'], F['ns_d']
DESK_L, DESK_D, CHAIR = F['desk_l'], F['desk_d'], F['chair']
WD_D, WD_FRONT, WD_LENS = F['wd_d'], F['wd_front'], F['wd_lens']
EPS = 1e-9
def ov(a, b): return min(a[2], b[2]) - max(a[0], b[0]) > EPS and min(a[3], b[3]) - max(a[1], b[1]) > EPS
def inside(r): return r[0] > -EPS and r[1] > -EPS and r[2] < W + EPS and r[3] < H + EPS
def frange(lo, hi, step=0.1):
    n = int(round((hi - lo)/step)); return [round(lo + i*step, 2) for i in range(n+1)] if hi >= lo - EPS else []
def wall_len(w): return W if w in 'NS' else H
def band(wall, a0, a1, depth):
    if wall == 'W': return (0, a0, depth, a1)
    if wall == 'E': return (W-depth, a0, W, a1)
    if wall == 'N': return (a0, 0, a1, depth)
    return (a0, H-depth, a1, H)
door_c = cfg['door']['c']; door_wall = cfg['door']['wall']; DD = cfg['door']['depth']
WINDOWS = [(w['wall'], w['c']-w['w']/2, w['c']+w['w']/2) for w in cfg['windows']]
WIN_RECTS = [band(w, s0, s1, 0.6) for w, s0, s1 in WINDOWS]
def head_under_window(r):
    return any(ov(r, wr) for wr in WIN_RECTS)
def make_door(c): return band(door_wall, c-0.45, c+0.45, DD)
def bed_layouts(DOOR):
    out = []
    for wall in 'NSEW':
        L = wall_len(wall)
        for p in frange(NS_W, L - BED_W - NS_W):
            if wall == 'N': bed = (p, 0, p+BED_W, BED_L); ns = [(p-NS_W, 0, p, NS_D), (p+BED_W, 0, p+BED_W+NS_W, NS_D)]; sides = [(p-0.6, NS_D, p, BED_L), (p+BED_W, NS_D, p+BED_W+0.6, BED_L)]; foot = (p, BED_L, p+BED_W, BED_L+0.6)
            if wall == 'S': bed = (p, H-BED_L, p+BED_W, H); ns = [(p-NS_W, H-NS_D, p, H), (p+BED_W, H-NS_D, p+BED_W+NS_W, H)]; sides = [(p-0.6, H-BED_L, p, H-NS_D), (p+BED_W, H-BED_L, p+BED_W+0.6, H-NS_D)]; foot = (p, H-BED_L-0.6, p+BED_W, H-BED_L)
            if wall == 'E': bed = (W-BED_L, p, W, p+BED_W); ns = [(W-NS_D, p-NS_W, W, p), (W-NS_D, p+BED_W, W, p+BED_W+NS_W)]; sides = [(W-BED_L, p-0.6, W-NS_D, p), (W-BED_L, p+BED_W, W-NS_D, p+BED_W+0.6)]; foot = (W-BED_L-0.6, p, W-BED_L, p+BED_W)
            if wall == 'W': bed = (0, p, BED_L, p+BED_W); ns = [(0, p-NS_W, NS_D, p), (0, p+BED_W, NS_D, p+BED_W+NS_W)]; sides = [(NS_D, p-0.6, BED_L, p), (NS_D, p+BED_W, BED_L, p+BED_W+0.6)]; foot = (BED_L, p, BED_L+0.6, p+BED_W)
            items = [bed] + ns
            if not all(inside(r) for r in items): continue
            if any(ov(r, DOOR) for r in items): continue
            out.append(dict(wall=wall, p=p, bed=bed, ns=ns, sides=sides, foot=foot))
    return out
def desk_options(DOOR):
    out = []
    for wall in 'NSEW':
        for p in frange(0, wall_len(wall) - DESK_L):
            if wall == 'N': d = (p, 0, p+DESK_L, DESK_D); ch = (p, DESK_D, p+DESK_L, DESK_D+CHAIR)
            if wall == 'S': d = (p, H-DESK_D, p+DESK_L, H); ch = (p, H-DESK_D-CHAIR, p+DESK_L, H-DESK_D)
            if wall == 'E': d = (W-DESK_D, p, W, p+DESK_L); ch = (W-DESK_D-CHAIR, p, W-DESK_D, p+DESK_L)
            if wall == 'W': d = (0, p, DESK_D, p+DESK_L); ch = (DESK_D, p, DESK_D+CHAIR, p+DESK_L)
            if ov(d, DOOR) or ov(ch, DOOR) or not inside(ch): continue
            out.append(dict(wall=wall, p=p, rect=d, chair=ch))
    return out
def wd_options(DOOR):
    out = []
    for wall in 'NSEW':
        for ln in WD_LENS:
            for p in frange(0, wall_len(wall) - ln):
                if wall == 'N': r = (p, 0, p+ln, WD_D); fr = (p, WD_D, p+ln, WD_D+WD_FRONT)
                if wall == 'S': r = (p, H-WD_D, p+ln, H); fr = (p, H-WD_D-WD_FRONT, p+ln, H-WD_D)
                if wall == 'E': r = (W-WD_D, p, W, p+ln); fr = (W-WD_D-WD_FRONT, p, W-WD_D, p+ln)
                if wall == 'W': r = (0, p, WD_D, p+ln); fr = (WD_D, p, WD_D+WD_FRONT, p+ln)
                if ov(r, DOOR) or ov(fr, DOOR) or not inside(fr): continue
                if any(ov(r, wr) for wr in WIN_RECTS): continue          # wardrobe must not block a window
                out.append(dict(wall=wall, p=p, ln=ln, rect=r, front=fr))
    return out
CELL = 0.05; NX, NY = int(round(W/CELL)), int(round(H/CELL)); RAD = 0.29
def reachable(obst, targets, DOOR, start):
    blocked = [[False]*NX for _ in range(NY)]
    for iy in range(NY):
        cy = (iy+0.5)*CELL
        for ix in range(NX):
            cx = (ix+0.5)*CELL
            if DOOR[0] <= cx <= DOOR[2] and DOOR[1] <= cy <= DOOR[3]: continue
            if cx < RAD or cx > W-RAD or cy < RAD or cy > H-RAD: blocked[iy][ix] = True; continue
            for r in obst:
                if r[0]-RAD < cx < r[2]+RAD and r[1]-RAD < cy < r[3]+RAD: blocked[iy][ix] = True; break
    sx, sy = min(NX-1, int(start[0]/CELL)), min(NY-1, int(start[1]/CELL))
    if blocked[sy][sx]: return False
    seen = {(sx, sy)}; st = [(sx, sy)]
    while st:
        x, y = st.pop()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < NX and 0 <= ny < NY and (nx, ny) not in seen and not blocked[ny][nx]:
                seen.add((nx, ny)); st.append((nx, ny))
    for (tx, ty) in targets:
        ix, iy = min(NX-1, int(tx/CELL)), min(NY-1, int(ty/CELL))
        if not any((jx, jy) in seen for jx in range(max(0, ix-3), min(NX, ix+4)) for jy in range(max(0, iy-3), min(NY, iy+4))): return False
    return True
def centre(r): return ((r[0]+r[2])/2, (r[1]+r[3])/2)
def door_start(c):
    if door_wall == 'N': return (c, DD/2)
    if door_wall == 'S': return (c, H-DD/2)
    if door_wall == 'W': return (DD/2, c)
    return (W-DD/2, c)
results = []
for c in cfg['door']['options']:
    DOOR = make_door(c)
    beds, desks, wds = bed_layouts(DOOR), desk_options(DOOR), wd_options(DOOR)
    for b in beds:
        bo = [b['bed']] + b['ns']
        free_sides = [s for s in b['sides'] if inside(s) and not any(ov(s, o) for o in bo) and not ov(s, DOOR)]
        foot_ok = inside(b['foot']) and not ov(b['foot'], DOOR)
        hu = head_under_window(b['bed'])
        for d in desks:
            if any(ov(d['rect'], o) or ov(d['chair'], o) for o in bo): continue
            for w in wds:
                if ov(w['rect'], d['rect']) or ov(w['rect'], d['chair']) or any(ov(w['rect'], o) for o in bo): continue
                if ov(w['front'], d['rect']) or any(ov(w['front'], o) for o in bo): continue
                if ov(d['chair'], w['rect']): continue
                fz = [s for s in free_sides if not ov(s, d['rect']) and not ov(s, w['rect'])]
                ft = foot_ok and not ov(b['foot'], d['rect']) and not ov(b['foot'], w['rect'])
                if not ft and not fz: continue
                score = 2*len(fz) + (2 if ft else 0)
                score += 0 if hu else 3
                score += 1 if any(ov(d['rect'], wr) or ov(d['chair'], wr) for wr in WIN_RECTS) else 0
                score += 0.5*(w['ln']-1.2)
                results.append((score, c, DOOR, b, d, w, fz, ft, bo + [d['rect'], w['rect']], hu))
results.sort(key=lambda t: -t[0])
print('candidates', len(results), file=sys.stderr)
out = []; seen_sig = set()
for score, c, DOOR, b, d, w, fz, ft, obst, hu in results[:15000]:
    sig = (b['wall'], d['wall'], w['wall'], w['ln'])
    if sum(1 for o_ in out if o_['bed_wall'] == b['wall']) >= 3: continue
    if sig in seen_sig: continue
    targets = [centre(d['chair']), centre(w['front'])]
    if ft: targets.append(centre(b['foot']))
    if fz: targets.append(centre(fz[0]))
    if not reachable(obst, targets, DOOR, door_start(c)): continue
    seen_sig.add(sig)
    out.append(dict(score=score, door_c=c, door=list(DOOR), head_under_window=hu, bed_wall=b['wall'], bed=list(b['bed']),
                    ns=[list(r) for r in b['ns']], free_sides=[list(s) for s in fz], foot=list(b['foot']) if ft else None,
                    desk=list(d['rect']), desk_wall=d['wall'], chair=list(d['chair']),
                    wd=list(w['rect']), wd_front=list(w['front']), wd_wall=w['wall'], wd_len=w['ln']))
    if len(out) >= 14: break
print(json.dumps(out, ensure_ascii=False))
