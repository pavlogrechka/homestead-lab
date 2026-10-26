import sys, json
from ortools.sat.python import cp_model
variant = sys.argv[1]; tlimit = float(sys.argv[2]); wcorr = sys.argv[3] == "corr"
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
# units: decimetres (0.1 m)
V = {
 'V1': dict(W=82, D=97, rooms={  # ext 9 x 10.5: separate kitchen/living, separate bath & toilet
   'hall':(88,100,23),'kit':(115,130,24),'liv':(161,168,32),'bed1':(92,102,25),'bed2':(92,102,25),
   'bath':(34,38,15),'toilet':(16,18,9),'tech':(30,34,14)}),
 'V2': dict(W=82, D=92, rooms={  # ext 9 x 10: open kitchen-living
   'hall':(88,100,23),'kitliv':(245,270,32),'bed1':(92,102,25),'bed2':(92,102,25),
   'bath':(34,38,15),'toilet':(16,18,9),'tech':(30,34,14),'store':(30,34,14)}),
 'V3': dict(W=82, D=92, rooms={  # ext 9 x 10: separate kitchen/living, combined bathroom
   'hall':(88,100,23),'kit':(115,130,24),'liv':(161,168,32),'bed1':(92,102,25),'bed2':(92,102,25),
   'bath':(50,54,17),'tech':(30,34,14)}),
 'V4': dict(W=82, D=92, rooms={  # ext 9 x 10: separate kitchen/living, combined bath, store
   'hall':(88,100,23),'kit':(115,130,24),'liv':(161,168,32),'bed1':(92,102,25),'bed2':(92,102,25),
   'bath':(50,54,17),'tech':(30,34,14),'store':(30,34,14)}),
 'V5': dict(W=82, D=97, rooms={  # ext 9 x 10.5: separate kitchen/living, separate bath & toilet, store
   'hall':(88,100,23),'kit':(115,130,24),'liv':(161,168,32),'bed1':(92,102,25),'bed2':(92,102,25),
   'bath':(34,38,15),'toilet':(16,18,9),'tech':(30,34,14),'store':(30,34,14)}),
 'V6': dict(W=82, D=92, rooms={  # A-type: ext 9 x 10, separate kitchen/living, combined bath, store; master 12+ and small 9
   'hall':(88,100,23),'kit':(115,130,24),'liv':(161,168,32),'bed1':(120,125,28),'bed2':(90,93,24),
   'bath':(50,54,17),'tech':(30,34,14),'store':(30,34,14)}),
 'V7': dict(W=82, D=97, rooms={  # B-type: ext 9 x 10.5, separate kitchen/living, separate bath+toilet, store
   'hall':(88,100,23),'kit':(115,130,24),'liv':(161,168,32),'bed1':(120,125,28),'bed2':(90,93,24),
   'bath':(34,38,15),'toilet':(16,18,9),'tech':(30,34,14),'store':(30,34,14)}),
 'V8': dict(W=82, D=92, rooms={  # C-type: ext 9 x 10, open kitchen-living, separate bath+toilet, store
   'hall':(88,100,23),'kitliv':(245,270,32),'bed1':(120,125,28),'bed2':(90,93,24),
   'bath':(34,38,15),'toilet':(16,18,9),'tech':(30,34,14),'store':(30,34,14)}),
}
cfg = V[variant]; W, D = cfg['W'], cfg['D']
R = {k: (a*10, t*10, d) for k, (a, t, d) in cfg['rooms'].items()}
if wcorr: R['corr'] = (300, 400, 15)
m = cp_model.CpModel()
X, Y, WW, HH, A = {}, {}, {}, {}, {}
ivx, ivy = [], []
for n, (amin, tgt, mind) in R.items():
    X[n] = m.NewIntVar(0, W, f'x_{n}'); Y[n] = m.NewIntVar(0, D, f'y_{n}')
    WW[n] = m.NewIntVar(mind, W, f'w_{n}'); HH[n] = m.NewIntVar(mind, D, f'h_{n}')
    m.Add(X[n] + WW[n] <= W); m.Add(Y[n] + HH[n] <= D)
    amax = int(tgt*1.35) if n not in ('hall','corr') else (1400 if n == 'hall' else 600)
    A[n] = m.NewIntVar(amin, amax, f'a_{n}')
    m.AddMultiplicationEquality(A[n], [WW[n], HH[n]])
    ex = m.NewIntVar(0, W, f'ex_{n}'); ey = m.NewIntVar(0, D, f'ey_{n}')
    m.Add(ex == X[n] + WW[n]); m.Add(ey == Y[n] + HH[n])
    ivx.append(m.NewIntervalVar(X[n], WW[n], ex, f'ix_{n}'))
    ivy.append(m.NewIntervalVar(Y[n], HH[n], ey, f'iy_{n}'))
    # aspect limit
    lim = 4 if n in ('hall', 'corr') else 2
    if n == 'corr': lim = 6
    if n in ('toilet',): lim = 2
    m.Add(WW[n] <= lim*HH[n]); m.Add(HH[n] <= lim*WW[n])
m.AddNoOverlap2D(ivx, ivy)
m.Add(sum(A.values()) == W*D)          # exact tiling
_cache = {}
def adj(a, b, L=9):
    key = (min(a, b), max(a, b), L)
    if key in _cache: return _cache[key]
    # overlap along y and x
    oy = m.NewIntVar(-D, D, f'oy_{a}_{b}'); ox = m.NewIntVar(-W, W, f'ox_{a}_{b}')
    minY = m.NewIntVar(0, D, ''); maxY = m.NewIntVar(0, D, ''); minX = m.NewIntVar(0, W, ''); maxX = m.NewIntVar(0, W, '')
    ea, eb = m.NewIntVar(0, D, ''), m.NewIntVar(0, D, '')
    m.Add(ea == Y[a]+HH[a]); m.Add(eb == Y[b]+HH[b])
    m.AddMinEquality(minY, [ea, eb]); m.AddMaxEquality(maxY, [Y[a], Y[b]]); m.Add(oy == minY - maxY)
    fa, fb = m.NewIntVar(0, W, ''), m.NewIntVar(0, W, '')
    m.Add(fa == X[a]+WW[a]); m.Add(fb == X[b]+WW[b])
    m.AddMinEquality(minX, [fa, fb]); m.AddMaxEquality(maxX, [X[a], X[b]]); m.Add(ox == minX - maxX)
    def reif_eq(lhs, rhs, name):
        e = m.NewBoolVar(name)
        m.Add(lhs == rhs).OnlyEnforceIf(e); m.Add(lhs != rhs).OnlyEnforceIf(e.Not()); return e
    def reif_ge(var, val, name):
        o = m.NewBoolVar(name)
        m.Add(var >= val).OnlyEnforceIf(o); m.Add(var < val).OnlyEnforceIf(o.Not()); return o
    def conj(p, q, name):
        c_ = m.NewBoolVar(name); m.AddBoolAnd([p, q]).OnlyEnforceIf(c_); m.AddBoolOr([p.Not(), q.Not()]).OnlyEnforceIf(c_.Not()); return c_
    oy_ok = reif_ge(oy, L, f'oyok_{a}_{b}'); ox_ok = reif_ge(ox, L, f'oxok_{a}_{b}')
    e1 = reif_eq(fa, X[b], f'e1_{a}_{b}'); e2 = reif_eq(fb, X[a], f'e2_{a}_{b}')
    e3 = reif_eq(ea, Y[b], f'e3_{a}_{b}'); e4 = reif_eq(eb, Y[a], f'e4_{a}_{b}')
    cs = [conj(e1, oy_ok, f'c1_{a}_{b}'), conj(e2, oy_ok, f'c2_{a}_{b}'), conj(e3, ox_ok, f'c3_{a}_{b}'), conj(e4, ox_ok, f'c4_{a}_{b}')]
    b_ = m.NewBoolVar(f'adj_{a}_{b}')
    m.AddMaxEquality(b_, cs)
    _cache[key] = b_
    return b_
def perimeter(n):
    t = [m.NewBoolVar(f'p{k}_{n}') for k in range(4)]
    m.Add(X[n] == 0).OnlyEnforceIf(t[0]); m.Add(Y[n] == 0).OnlyEnforceIf(t[1])
    m.Add(X[n]+WW[n] == W).OnlyEnforceIf(t[2]); m.Add(Y[n]+HH[n] == D).OnlyEnforceIf(t[3])
    m.AddBoolOr(t)
# entry hall on front or west wall
t0, t1 = m.NewBoolVar('hf'), m.NewBoolVar('hw')
m.Add(Y['hall'] == 0).OnlyEnforceIf(t1); m.Add(X['hall'] == 0).OnlyEnforceIf(t0); m.AddBoolOr([t0, t1])
for n in ('kit', 'liv', 'kitliv', 'bed1', 'bed2'):
    if n in R: perimeter(n)
kit = 'kitliv' if 'kitliv' in R else 'kit'
circ = ['hall'] + (['corr'] if 'corr' in R else [])
m.Add(adj('hall', kit) == 1)
if 'corr' in R: m.Add(adj('corr', 'hall', 10) == 1)
for n in R:
    if n in ('hall', 'corr', 'kit', 'liv', 'kitliv'): continue
    m.AddBoolOr([adj(n, c, 8) for c in circ])
if 'liv' in R:
    m.AddBoolOr([adj('liv', 'hall', 8), adj('liv', 'kit', 9)])
# soft terms
pen = []
for k, (amin, tgt, mind) in R.items():
    d = m.NewIntVar(0, W*D, f'd_{k}'); m.AddAbsEquality(d, A[k] - tgt); pen.append(d)
for b in ('bed1', 'bed2'):
    m.Add(adj(b, kit, 3) == 0)
if 'liv' in R:
    pen.append(60*adj('liv', 'bed1', 5)); pen.append(60*adj('liv', 'bed2', 5))
if 'toilet' in R: pen.append(-30*adj('bath', 'toilet', 8))
pen.append(-25*adj('bath', 'tech', 8))
m.Minimize(sum(pen))
s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tlimit; s.parameters.num_workers = 8; s.parameters.random_seed = seed
st = s.Solve(m)
print(variant, 'corr' if wcorr else 'nocorr', s.StatusName(st), 'obj', s.ObjectiveValue() if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None, file=sys.stderr)
if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    out = {n: [s.Value(X[n])/10, s.Value(Y[n])/10, s.Value(WW[n])/10, s.Value(HH[n])/10] for n in R}
    print(json.dumps({'variant': variant, 'W': W/10, 'D': D/10, 'corr': wcorr, 'rooms': out}, ensure_ascii=False))
