"""Public OLBG route discovery. Never a probability model or official-fixture feed."""
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,parse_qs,unquote
import re
from .config import SPORTS,SPORT_INDEX
from .http import FetchError

SPORT_ID_MAP={x[2]:x[0] for x in SPORTS}
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.active=None;self.words=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'):
            self.active=a['href'];self.words=[]
    def handle_data(self,data):
        if self.active is not None:self.words.append(data)
    def handle_endtag(self,tag):
        if tag=='a' and self.active is not None:
            self.links.append((self.active,' '.join(' '.join(self.words).split())))
            self.active=None


def event_link(url,base):
    absolute=urljoin(base,url);p=urlsplit(absolute)
    if p.scheme!='https' or p.hostname not in ('www.olbg.com','olbg.com'):return None
    m=re.fullmatch(r'/betting-tips/(?:[^/]+/)+(\d+)/?',p.path)
    if not m or int(m[1]) not in SPORT_ID_MAP:return None
    ids=parse_qs(p.query).get('event_id',[])
    if len(ids)!=1 or not re.fullmatch(r'\d+',ids[0]):return None
    sport=SPORT_ID_MAP[int(m[1])]
    return {'id':'olbg-'+str(int(m[1]))+'-'+ids[0],'event_id':ids[0],'sport':sport,'url':absolute,
            'official_source_url':SPORT_INDEX[sport]['official_url'],
            'verified_participant_a':None,'verified_participant_b':None,'verified_start_utc':None,
            'selection':None,'probability':None,'confidence':None,'verification':'unverified — discovery only'}


def crawl(fetcher,max_pages=24):
    queue=[x['olbg_url'] for x in SPORT_INDEX.values()];seen=set();events={};pages=[]
    while queue and len(seen)<max_pages:
        url=queue.pop(0)
        if url in seen:continue
        seen.add(url)
        try:
            response=fetcher.get(url,'olbg-page-'+str(len(seen)))
            parser=Links();parser.feed(response.body.decode('utf-8','replace'))
            for link,label in parser.links:
                ev=event_link(link,url)
                if ev:
                    ev.update(observed_label=label,observed_at=response.observed_before)
                    # Preserve a match label rather than overwrite with a selection label.
                    if ev['id'] not in events or len(label)>len(events[ev['id']]['observed_label']):events[ev['id']]=ev
                else:
                    candidate=urljoin(url,link);p=urlsplit(candidate)
                    # Follow only explicitly linked public pagination/competition pages.
                    if p.hostname=='www.olbg.com' and re.fullmatch(r'/betting-tips/[^/]+/(?:[^/]+/)*\d+',p.path):
                        sid=int(p.path.rstrip('/').split('/')[-1])
                        if sid in SPORT_ID_MAP and candidate not in seen and candidate not in queue:
                            queue.append(candidate)
            pages.append({'url':url,'status':'read','event_links':sum(bool(event_link(x,url)) for x,_ in parser.links)})
        except FetchError as e:
            pages.append({'url':url,'status':'unverified','reason':str(e)})
    return {'complete':False,'scope':'Bounded public linked-page crawl; not all competitions or hidden feeds.',
            'pages':pages,'unvisited_linked_pages':len(queue),'events':sorted(events.values(),key=lambda e:e['id']),
            'policy':'OLBG is authoritative only for its own displayed tips/route labels. Tip percentages are votes, NOT win probabilities; relative clocks have no inferred UTC date.'}
