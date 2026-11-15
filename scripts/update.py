#!/usr/bin/env python3
"""Build a source-attributed morning feed from Google News RSS search results.
No article bodies are scraped; descriptions are not treated as verified conclusions.
"""
import datetime as dt, email.utils, hashlib, json, os, pathlib, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parents[1]
KST=ZoneInfo('Asia/Seoul')
NOW=dt.datetime.now(KST)
SEARCHES={
 '재계': ['재계 기업 지배구조 투자 인수합병', '삼성 SK LG 현대차 롯데 한화 기업 투자'],
 '기업': ['한국 기업 실적 공시 수주 수출 산업', '배터리 전력기기 조선 석유화학 기업'],
 '에너지': ['한국 전력망 ESS 원전 LNG 에너지 정책', '전기요금 한전 가스공사 재생에너지'],
 '정치·정책': ['정부 국회 재계 산업 에너지 정책 규제 예산'],
 '국회·법안': ['국회 법안 상법 세법 기업 산업 에너지', '국회 발의 원자력 전력망 재생에너지 법률'],
 '국회 일정': ['국회 산업통상자원중소벤처기업위원회 회의 일정', '국회 재정경제위원회 법안심사소위원회 일정', '국회 에너지 산업 기업 토론회 개최 일정']
}
INCLUDE={
 '재계':r'기업|그룹|회장|총수|지배구조|투자|인수|합병|상공회의소|경제단체|삼성|SK|LG|롯데|한화|포스코',
 '기업':r'기업|실적|매출|영업이익|수출|수주|공시|배터리|반도체|조선|석유화학|전력기기|투자',
 '에너지':r'전력|에너지|ESS|원전|원자력|LNG|가스|재생|태양광|풍력|한전|전기|송전|배터리',
 '정치·정책':r'정부|국회|정책|규제|예산|지원|세제|산업|전력|에너지|기업',
 '국회·법안':r'법안|개정안|발의|법률|상법|세법|국회|입법|소위',
 '국회 일정':r'국회|토론회|상임위|소위|공청회|간담회|산자위|재경위|회의|발제'
}

def clean(s):return re.sub(r'\s+',' ',re.sub(r'<[^>]*>','',s or '')).strip()
def rss(q):
    url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q+' when:3d','hl':'ko','gl':'KR','ceid':'KR:ko'})
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 IndustryDesk/1.0 (RSS feed reader)'})
    with urllib.request.urlopen(req,timeout=18) as resp: body=resp.read(2_000_000)
    root=ET.fromstring(body)
    result=[]
    for item in root.findall('.//channel/item'):
        title=clean(item.findtext('title')); link=clean(item.findtext('link'))
        source=clean(item.findtext('source')) or 'Google News RSS'
        try: pub=email.utils.parsedate_to_datetime(item.findtext('pubDate')).astimezone(KST)
        except Exception: pub=None
        result.append({'title':title,'url':link,'source':source,'published_at':pub.isoformat() if pub else None})
    return result

def main():
    unique={}; errors=[]
    for cat, queries in SEARCHES.items():
        count=0
        for query in queries:
            try: found=rss(query)
            except Exception as exc:
                errors.append(f'{cat}: RSS 접근 실패 ({type(exc).__name__})');continue
            for r in found:
                if count>=12:break
                if not re.search(INCLUDE[cat],r['title'],re.I):continue
                key=re.sub(r'\s+','',re.sub(r'\s*[-–|]\s*[^-–|]+$','',r['title'])).lower()
                if key in unique:continue
                date=dt.datetime.fromisoformat(r['published_at']) if r['published_at'] else None
                if date and (NOW-date).total_seconds()>72*3600:continue
                r.update({'id':hashlib.sha1((r['title']+r['url']).encode()).hexdigest()[:14], 'category':cat,
                          'type':'news', 'summary':'제목 기반 수집 항목입니다. 원문에서 사실관계와 수치를 확인하세요.',
                          'impact':'기업 비용·투자·수익·규제 영향 추가 확인 필요',
                          'pitch':'기사 발제 가능성 검토', 'question':'정책 변화·기업별 영향·시행 시점·비용 수치를 취재원에게 확인',
                          'verified':False})
                if cat=='국회 일정':
                    r['type']='schedule_lead'
                    r['summary']='일정 관련 보도·공지 검색 결과입니다. 회의 개최 여부, 일시, 장소는 국회 공식 일정에서 재확인해야 합니다.'
                unique[key]=r;count+=1
            time.sleep(.25)
    # Only explicitly verified entries get displayed in confirmed schedule area.
    schedule_file=ROOT/'data'/'schedule_manual.json'
    try: schedules=json.loads(schedule_file.read_text(encoding='utf-8'))
    except Exception: schedules=[]
    confirmed=[]
    for i,s in enumerate(schedules):
        if not all(s.get(k) for k in ('title','starts_at','source_url','verified_on')):continue
        try:
            when=dt.datetime.fromisoformat(s['starts_at']);when=when.replace(tzinfo=KST) if when.tzinfo is None else when.astimezone(KST)
            if not (NOW-dt.timedelta(days=1)<=when<=NOW+dt.timedelta(days=14)):continue
        except Exception:continue
        confirmed.append({**s,'id':'manual-'+str(i),'category':'국회 일정','type':'verified_schedule','verified':True})
    feed={'generated_at':NOW.isoformat(),'timezone':'Asia/Seoul','status':'ok' if unique else 'unavailable',
          'source_method':'Google News RSS headline search (last 72 hours); confirmed schedules manually verified',
          'errors':errors,'items':list(unique.values()),'confirmed_schedules':confirmed}
    out=ROOT/'data'/'feed.json';out.write_text(json.dumps(feed,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Generated {len(unique)} news and {len(confirmed)} confirmed schedules; errors {len(errors)}')
if __name__=='__main__':main()
