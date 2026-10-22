"""Bounded, identifiable, robots-aware public-source reader (no access-control bypass).

Network failures are data gaps, not empty fixture lists. Redirects cannot leave
explicit publisher allowlists. No cookies, credentials, hidden APIs or UA rotation.
"""
from dataclasses import dataclass
from pathlib import Path
import threading
import time
from urllib import error, request, robotparser
from urllib.parse import urlsplit, urlunsplit
from .common import allowed_url, digest, iso, now_utc

USER_AGENT = 'OLBG1Research/1.0 (+https://github.com/buffedlizard55-lab/OLBG1; Python-urllib)'
MAX_BYTES = 10 * 1024 * 1024

class FetchError(Exception):
    pass

class SafeRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_url(newurl, discovery=True):
            raise FetchError('Redirect outside publisher allowlist')
        return super().redirect_request(req, fp, code, msg, headers, newurl)

@dataclass
class Response:
    url: str
    final_url: str
    body: bytes
    status: int
    content_type: str
    observed_after: str
    observed_before: str
    sha256: str

class Fetcher:
    def __init__(self, raw_dir, timeout=12, attempts=2, opener=None, delay=1.0):
        self.raw_dir=Path(raw_dir); self.raw_dir.mkdir(parents=True,exist_ok=True)
        self.timeout=timeout; self.attempts=attempts
        self.opener=opener or request.build_opener(SafeRedirect())
        self.robots={}; self.last={}; self.delay=delay
        self.lock=threading.Lock()
        self.log=[]

    def _raw(self, url):
        if not allowed_url(url,discovery=True):
            raise FetchError('URL outside explicit HTTPS publisher allowlist')
        host=urlsplit(url).hostname
        with self.lock:
            wait=self.delay-(time.monotonic()-self.last.get(host,0))
            if wait>0: time.sleep(wait)
            self.last[host]=time.monotonic()
        started=iso(now_utc())
        req=request.Request(url,headers={'User-Agent':USER_AGENT,'Accept':'application/json,text/html,application/xml,text/plain;q=0.9','Accept-Encoding':'identity'})
        with self.opener.open(req,timeout=self.timeout) as resp:
            body=resp.read(MAX_BYTES+1)
            if len(body)>MAX_BYTES: raise FetchError('Source body exceeds 10 MiB limit')
            final=resp.geturl()
            if not allowed_url(final,discovery=True): raise FetchError('Unapproved final source host')
            if resp.status!=200: raise FetchError('HTTP '+str(resp.status))
            result=Response(url,final,body,resp.status,resp.headers.get('Content-Type',''),started,iso(now_utc()),digest(body))
        return result

    def _robots_allowed(self,url):
        p=urlsplit(url); origin=urlunsplit((p.scheme,p.netloc,'','',''))
        if origin not in self.robots:
            try:
                r=self._raw(origin+'/robots.txt')
                text=r.body.decode('utf-8','replace')
                # An HTML bot challenge at /robots.txt is not an allow-all policy.
                if '<html' in text.lower() or '<!doctype' in text.lower():
                    raise FetchError('robots.txt returned HTML; policy unknown')
                rp=robotparser.RobotFileParser();rp.parse(text.splitlines())
                self.robots[origin]=rp
                self.log.append({'url':origin+'/robots.txt','status':'read','http_status':200,'at':r.observed_before})
            except error.HTTPError as e:
                if e.code in (404,410):
                    rp=robotparser.RobotFileParser();rp.parse(['User-agent: *','Allow: /']);self.robots[origin]=rp
                else:
                    self.robots[origin]=None
            except Exception:
                self.robots[origin]=None
        rp=self.robots[origin]
        if rp is None: raise FetchError('robots policy unavailable; request withheld')
        # Advertise and respect both our app identity and underlying library identity.
        if not rp.can_fetch(USER_AGENT,url) or not rp.can_fetch('Python-urllib',url):
            raise FetchError('robots.txt disallows this client/path; request withheld')
        delay=rp.crawl_delay(USER_AGENT)
        if delay and delay>self.delay:
            if delay>30: raise FetchError('Crawl delay exceeds bounded run budget')
            self.delay=float(delay)

    def get(self,url,source_id,robots=True):
        try:
            if robots: self._robots_allowed(url)
            for attempt in range(self.attempts):
                try:
                    result=self._raw(url)
                    path=self.raw_dir/(source_id+'.body')
                    path.write_bytes(result.body)
                    self.log.append({'url':url,'final_url':result.final_url,'source_id':source_id,'status':'read','http_status':result.status,
                                     'at':result.observed_before,'raw_sha256':result.sha256})
                    return result
                except error.HTTPError as e:
                    if e.code not in (408,429,500,502,503,504) or attempt==self.attempts-1: raise
                    # No repeated hammering after rate limiting.
                    if e.code==429: raise FetchError('Rate limited; retry on the next scheduled run') from e
                    time.sleep(1+attempt)
                except (error.URLError,TimeoutError,OSError):
                    if attempt==self.attempts-1: raise
                    time.sleep(1+attempt)
        except Exception as e:
            self.log.append({'url':url,'source_id':source_id,'status':'unverified','http_status':getattr(e,'code',None),
                             'at':iso(now_utc()),'error':str(e)[:350]})
            raise FetchError(str(e)) from e
