# 독립 검증: 파이썬으로 같은 규칙을 따로 구현해 무작위 입력의 기대값을 만들고,
# index.html의 계산 엔진(CostCalc)을 담은 시험 페이지를 생성한다.
import json, random, re, sys

APP, OUT = sys.argv[1], sys.argv[2]
random.seed(20261112)
S = dict(rateMin=0.05, amtMin=300000, amtMax=2000000, unexplRatio=0.5, unexplMin=300000, staleMonths=6,
         kindUnitUp=0.05, kindMarginDrop=0.05)

def mi(m): y, mo = m.split('-'); return int(y) * 12 + int(mo) - 1
def mf(i): return f"{i // 12}-{i % 12 + 1:02d}"

MONTHS = [mf(mi('2025-01') + k) for k in range(18)]

def rand_project(n):
    base = random.choice(MONTHS[:10]); done = mf(mi(base) + random.randint(0, 9))
    mats, idx = [], {}
    for j in range(random.randint(1, 4)):
        if random.random() < 0.65:
            sq = round(random.uniform(5, 1500), random.choice([0, 1, 2]))
            sp = random.choice([random.randint(800, 30000), round(random.uniform(800, 30000), 1)])
            aq = round(sq * random.uniform(0.85, 1.2), random.choice([0, 1, 2]))
            ap = round(sp * random.uniform(0.8, 1.4), random.choice([0, 1]))
            name = None
            if random.random() < 0.7:
                name = f"IDX{n}_{j}"
                i0 = random.randint(1000, 25000); i1 = round(i0 * random.uniform(0.85, 1.3))
                idx[name] = {base: i0, done: i1}
                if random.random() < 0.1: del idx[name][done]       # 한 달 지표 없음 → 가정 없음
            mats.append(dict(code=f"M{j}", name=f"재료{j}", type="split", sq=sq, sp=sp, aq=aq, ap=ap, index=name))
        else:
            pre = random.randint(50000, 9000000)
            post = round(pre * random.uniform(0.8, 1.3))
            mats.append(dict(code=f"T{j}", name=f"총액{j}", type="total", pre=pre, post=post))
    # 경계값 근처 프로젝트 섞기: 총액 하나로 차이를 기준 바로 위/아래로
    if random.random() < 0.25:
        pre = random.randint(3_000_000, 50_000_000)
        target = random.choice([S['amtMin'], S['amtMax'], pre * S['rateMin']]) + random.choice([-1, -0.5, 0, 0.5, 1])
        mats = [dict(code="T0", name="총액", type="total", pre=pre, post=pre + target * random.choice([1, -1]))]
        idx = {}
    return dict(id=f"R{n}", kind="TEST", qty=random.randint(1, 50), price=0, baseMonth=base, doneMonth=done, materials=mats), idx

def expect_project(p, idx):
    t = dict(pre=0, post=0, use=0, indexShare=0, unexpl=0, undivided=0, other=0, absSplit=0, absTotal=0, absUnexpl=0, absPriceIdx=0)
    for m in p['materials']:
        if m['type'] == 'split':
            pre, post = m['sq'] * m['sp'], m['aq'] * m['ap']
            use, price = (m['aq'] - m['sq']) * m['sp'], (m['ap'] - m['sp']) * m['aq']
            t['pre'] += pre; t['post'] += post; t['use'] += use; t['absSplit'] += abs(post - pre)
            tbl = idx.get(m['index']) if m['index'] else None
            i0 = tbl.get(p['baseMonth']) if tbl else None; i1 = tbl.get(p['doneMonth']) if tbl else None
            if i0 is not None and i1 is not None:
                share = m['aq'] * (i1 - i0); un = price - share
                t['indexShare'] += share; t['unexpl'] += un; t['absUnexpl'] += abs(un); t['absPriceIdx'] += abs(price)
            else:
                t['undivided'] += price
        else:
            d = m['post'] - m['pre']
            t['pre'] += m['pre']; t['post'] += m['post']; t['other'] += d; t['absTotal'] += abs(d)
    t['diff'] = t['post'] - t['pre']
    t['rate'] = t['diff'] / t['pre'] if t['pre'] else None
    den = t['absSplit'] + t['absTotal']; t['coverage'] = t['absSplit'] / den if den > 0 else None
    t['elapsed'] = mi(p['doneMonth']) - mi(p['baseMonth'])
    f, ad = [], abs(t['diff'])
    if t['rate'] is not None and abs(t['rate']) >= S['rateMin'] and ad >= S['amtMin']: f.append(1)
    if ad >= S['amtMax']: f.append(2)
    if t['absPriceIdx'] > 0 and t['absUnexpl'] >= t['absPriceIdx'] * S['unexplRatio'] and t['absUnexpl'] >= S['unexplMin']: f.append(3)
    if t['elapsed'] >= S['staleMonths']: f.append(4)
    t['flags'] = ",".join(map(str, f))
    for k in ('absSplit', 'absTotal'): t.pop(k)
    return t

def rand_kind_case(n):
    last = '2026-06'; lst = []
    for k in range(random.randint(0, 8)):
        m = mf(mi(last) - random.randint(0, 7))
        pre = random.randint(2_000_000, 40_000_000); post = round(pre * random.uniform(0.9, 1.2))
        price = round(pre * random.uniform(1.0, 1.35))
        lst.append(dict(id=f"K{n}_{k}", kind="KX", qty=random.randint(1, 40), price=price, baseMonth=m, doneMonth=m,
                        materials=[dict(code="T", name="총액", type="total", pre=pre, post=post)]))
    def win(a, b):
        w = dict(n=0, pre=0, post=0, qty=0, price=0)
        for p in lst:
            i = mi(p['doneMonth'])
            if mi(a) <= i <= mi(b):
                w['n'] += 1; w['pre'] += p['materials'][0]['pre']; w['post'] += p['materials'][0]['post']; w['qty'] += p['qty']; w['price'] += p['price']
        return w
    r = win(mf(mi(last) - 2), last); pv = win(mf(mi(last) - 5), mf(mi(last) - 3))
    e = {}
    if r['qty'] > 0 and pv['qty'] > 0:
        ch = (r['post'] / r['qty']) / (pv['post'] / pv['qty']) - 1
        e['unitChange'] = ch; e['unit'] = 'alert' if ch >= S['kindUnitUp'] else 'ok'
    else: e['unitChange'] = None; e['unit'] = 'unknown'
    if r['n'] > 0 and r['price'] > 0:
        g = (r['price'] - r['post']) / r['price'] - (r['price'] - r['pre']) / r['price']
        e['marginGap'] = g; e['margin'] = 'alert' if g <= -S['kindMarginDrop'] else 'ok'
    else: e['marginGap'] = None; e['margin'] = 'unknown'
    # 월별 개당 원가 (빈 달 null)
    months = []
    for i in range(mi('2026-01'), mi(last) + 1):
        w = win(mf(i), mf(i)); months.append(w['post'] / w['qty'] if w['qty'] > 0 else None)
    e['monthly'] = months
    return dict(list=lst, expect=e)

projects = []
for n in range(400):
    p, idx = rand_project(n); projects.append(dict(p=p, idx=idx, expect=expect_project(p, idx)))
kinds = [rand_kind_case(n) for n in range(150)]
# 정렬 기대값
sort_amount = [x['p']['id'] for x in sorted(projects, key=lambda x: -abs(x['expect']['diff']))]

src = open(APP, encoding='utf-8').read()
engine = re.search(r'<script>\s*(/\* =+\s*계산 엔진.*?)</script>', src, re.S).group(1)

runner = r"""
var DATA = __DATA__;
var C = CostCalc, bad = [], n = 0;
function near(a, b, tol){ if (a === null || b === null) return a === b; return Math.abs(a - b) <= tol * Math.max(1, Math.abs(b)); }
DATA.projects.forEach(function(x){
  var t = C.project(x.p, x.idx), e = x.expect;
  ["pre","post","diff","use","indexShare","unexpl","undivided","other","absUnexpl","absPriceIdx"].forEach(function(k){
    n++; if (!near(t[k], e[k], 1e-9)) bad.push(x.p.id + " " + k + " " + t[k] + " vs " + e[k]); });
  ["rate","coverage"].forEach(function(k){ n++; if (!near(t[k], e[k], 1e-12)) bad.push(x.p.id + " " + k + " " + t[k] + " vs " + e[k]); });
  n++; if (t.elapsed !== e.elapsed) bad.push(x.p.id + " elapsed");
  n++; if (t.flags.join(",") !== e.flags) bad.push(x.p.id + " flags " + t.flags.join(",") + " vs " + e.flags);
  n++; if (Math.abs(t.check) >= 1e-6 * Math.max(1, Math.abs(t.diff))) bad.push(x.p.id + " check " + t.check);
});
var sorted = C.sortProjects(DATA.projects.map(function(x){ return C.project(x.p, x.idx); }), "amount").map(function(t){ return t.id; });
n++; if (sorted.join() !== DATA.sortAmount.join()) bad.push("sort amount mismatch");
DATA.kinds.forEach(function(k, i){
  var a = C.kindAlert(k.list.map(function(p){ return C.project(p, {}); }), "KX", "2026-06"), e = k.expect;
  n++; if (a.unit !== e.unit) bad.push("kind" + i + " unit " + a.unit + " vs " + e.unit);
  n++; if (a.margin !== e.margin) bad.push("kind" + i + " margin " + a.margin + " vs " + e.margin);
  n++; if (!near(a.unitChange, e.unitChange, 1e-12)) bad.push("kind" + i + " unitChange");
  n++; if (!near(a.marginGap, e.marginGap, 1e-12)) bad.push("kind" + i + " marginGap");
  var mo = C.kindMonthly(k.list.map(function(p){ return C.project(p, {}); }), "KX", "2026-01", "2026-06");
  mo.forEach(function(r, j){ n++; if (!near(r.unitPost, e.monthly[j], 1e-12)) bad.push("kind" + i + " month" + j); });
});
var flagsCount = {1:0,2:0,3:0,4:0,none:0};
DATA.projects.forEach(function(x){ var f = x.expect.flags; if (!f) flagsCount.none++; f.split(",").forEach(function(v){ if (v) flagsCount[v]++; }); });
var ku = {alert:0, ok:0, unknown:0}; DATA.kinds.forEach(function(k){ ku[k.expect.unit]++; });
document.body.innerHTML = "<h1 style='font:900 40px sans-serif;color:" + (bad.length ? "#d13b0e" : "#1a7f37") + "'>" +
  (bad.length ? "FAIL " : "PASS ") + (n - bad.length) + " / " + n + "</h1>" +
  "<p style='font:16px sans-serif'>무작위 프로젝트 " + DATA.projects.length + "개 · 기종 시나리오 " + DATA.kinds.length + "개</p>" +
  "<p style='font:16px sans-serif'>사유 분포(파이썬 기대값): ①" + flagsCount[1] + " ②" + flagsCount[2] + " ③" + flagsCount[3] + " ④" + flagsCount[4] + " 없음" + flagsCount.none +
  " · 기종①: 주의" + ku.alert + " 정상" + ku.ok + " 판단불가" + ku.unknown + "</p>" +
  "<pre style='font:13px monospace;color:#d13b0e'>" + bad.slice(0, 25).join("\n") + "</pre>";
"""
data = dict(projects=projects, kinds=kinds, sortAmount=sort_amount)
html = "<!doctype html><html><head><meta charset='utf-8'></head><body><script>" + engine + "</script><script>" + \
       runner.replace("__DATA__", json.dumps(data, ensure_ascii=False)) + "</script></body></html>"
open(OUT, 'w', encoding='utf-8').write(html)
print("projects", len(projects), "kinds", len(kinds), "engine chars", len(engine))
