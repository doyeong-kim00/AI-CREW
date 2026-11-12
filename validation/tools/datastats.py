# 가상 데이터 통계 페이지 생성: index.html의 엔진·데이터 스크립트만 꺼내 통계를 화면에 출력
import re, sys
APP, OUT = sys.argv[1], sys.argv[2]
src = open(APP, encoding='utf-8').read()
blocks = re.findall(r'<script>(.*?)</script>', src, re.S)
engine = [b for b in blocks if 'var CostCalc' in b][0]
demo = [b for b in blocks if 'var DemoData' in b][0]
runner = r"""
var C = CostCalc, D = DemoData.get(), out = [];
function p(s){ out.push(s); }
var P = D.projects;
var fl = {1:0,2:0,3:0,4:0}, none = 0, negUn = 0, posUn = 0, under = 0;
P.forEach(function(t){ if (!t.flags.length) none++; t.flags.forEach(function(f){ fl[f]++; });
  if (t.hasIndex){ if (t.unexpl < 0) negUn++; else posUn++; } if (t.diff < 0) under++; });
var rates = P.map(function(t){ return t.rate; }).sort(function(a,b){return a-b;});
var pres = P.map(function(t){ return t.pre; }).sort(function(a,b){return a-b;});
var cov = P.map(function(t){ return t.coverage; }).sort(function(a,b){return a-b;});
p("프로젝트 " + P.length + " · 확인 필요 있음 " + (P.length - none) + " · 없음 " + none);
p("사유 ①" + fl[1] + " ②" + fl[2] + " ③" + fl[3] + " ④" + fl[4]);
p("미분해 합 음수 " + negUn + " / 양수 " + posUn + " · 덜 든 프로젝트 " + under);
p("차이율 최소 " + C.pct(rates[0],1,true) + " 중앙 " + C.pct(rates[rates.length>>1],1,true) + " 최대 " + C.pct(rates[rates.length-1],1,true));
p("사전원가 최소 " + C.won(pres[0]) + " 중앙 " + C.won(pres[pres.length>>1]) + " 최대 " + C.won(pres[pres.length-1]));
p("분해 범위 최소 " + C.pct(cov[0],0) + " 중앙 " + C.pct(cov[cov.length>>1],0) + " 최대 " + C.pct(cov[cov.length-1],0));
var topList = C.sortProjects(P, "amount").slice(0,5).map(function(t){ return t.id + " " + t.kind + " " + C.won(t.diff,true) + " (" + C.pct(t.rate,1,true) + ") [" + t.flags.join(",") + "]"; });
p("금액 순 상위 5: <br>&nbsp;&nbsp;" + topList.join("<br>&nbsp;&nbsp;"));
D.kinds.forEach(function(k){
  var a = C.kindAlert(P, k, D.lastMonth), mo = C.kindMonthly(P, k, D.firstMonth, D.lastMonth);
  var gaps = mo.filter(function(r){ return r.unitPost === null; }).length;
  p(k + " · 개당원가 변화 " + C.pct(a.unitChange,1,true) + " [" + a.unit + "] · 이익률 차 " + (a.marginGap===null?"—":(a.marginGap*100).toFixed(1)+"%p") + " [" + a.margin + "] · 빈 달 " + gaps + " · 건수 " + mo.map(function(r){return r.n;}).join(""));
});
document.body.innerHTML = "<div style='font:15px/1.7 sans-serif;padding:16px'>" + out.join("<br>") + "</div>";
"""
html = "<!doctype html><html><head><meta charset='utf-8'></head><body><script>" + engine + "</script><script>" + demo + "</script><script>" + runner + "</script></body></html>"
open(OUT, 'w', encoding='utf-8').write(html)
print("ok")
