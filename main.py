"""Offline transparent keyword triage of user-provided research metadata."""
import argparse, json, re
from datetime import date
from pathlib import Path

RULES={'time-series':['time-series','predictive maintenance','topology'],
       'semantic-twin':['ontology','semantic','unstructured'],
       'physics-hybrid':['physics','modeling','world models'],
       'agent-guard':['autonomous','agent','intervention']}
IDEAS={'time-series':'센서 관계 그래프를 포함한 예지보전 평가 파이프라인',
       'semantic-twin':'문서 근거와 장비 ID를 연결하는 검색·검증 도구',
       'physics-hybrid':'물리 기준선과 데이터 잔차를 비교하는 이상 탐지기',
       'agent-guard':'상태 버전·범위·인터록을 검사하는 제어 요청 검증기'}

def rank(papers,as_of):
    today=date.fromisoformat(as_of); result=[]; seen=set()
    for paper in papers:
        if paper['url'] in seen: continue
        seen.add(paper['url']); published=date.fromisoformat(paper['published'])
        if published>today: continue
        text=(paper['title']+' '+paper['summary']).lower()
        matches={category:[word for word in words if word in text] for category,words in RULES.items()}
        matches={k:v for k,v in matches.items() if v}
        if not matches: continue
        age=(today-published).days; score=sum(len(v) for v in matches.values())*10+max(0,30-age)/3
        result.append({**paper,'age_days':age,'score':round(score,2),'matched_terms':matches,
                       'prototype_ideas':[IDEAS[k] for k in matches]})
    return sorted(result,key=lambda p:(-p['score'],p['url']))

def report(papers,as_of):
    out=[f'# 디지털 트윈·AI 논문 → 구현 아이디어 ({as_of})',
         '규칙 기반 분석이며 LLM 요약이나 논문 성능 검증이 아닙니다. 점수는 키워드와 최근성의 합입니다.','']
    for p in rank(papers,as_of):
        out += [f"## {p['title']}",f"- 발표: {p['published']} / 상태: {p['status']}",
                f"- 원문: {p['url']}",f"- 점수: {p['score']} / 매칭 근거: {json.dumps(p['matched_terms'],ensure_ascii=False)}",
                f"- 등록한 요약: {p['summary']}",'- 구현 아이디어(개발자 해석): '+', '.join(p['prototype_ideas']),'']
    return '\n'.join(out)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input',default=str(Path(__file__).with_name('papers.json')))
    p.add_argument('--as-of',default='2026-10-08'); p.add_argument('--output'); a=p.parse_args()
    papers=json.loads(Path(a.input).read_text(encoding='utf-8')); value=report(papers,a.as_of)
    if a.output: Path(a.output).write_text(value,encoding='utf-8')
    else: print(value,end='')
