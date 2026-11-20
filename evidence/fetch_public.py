"""Fetch only explicitly reviewed public-domain/open-license sources.
Run from repo root: python evidence/fetch_public.py
Review the resulting snapshots, then git add/commit. No automatic push.
"""
import hashlib, json, pathlib, urllib.request, urllib.parse, datetime
ROOT=pathlib.Path(__file__).resolve().parent
SOURCES=[
 ("ADA-010","S02","https://api.parliament.uk/historic-hansard/commons/1832/feb/20/insurrection-in-jamaica","Open Parliament Licence v3.0","Contains Parliamentary information licensed under the Open Parliament Licence v3.0.","INSURRECTION IN JAMAICA"),
 ("ADA-002","BABBAGE-1864","https://www.gutenberg.org/files/57532/57532-h/57532-h.htm","US public domain historical work; retain Gutenberg notices","Charles Babbage, Passages from the Life of a Philosopher (1864), Project Gutenberg","Passages from the Life of a Philosopher")
]
def fetch(item):
    audit,sid,url,rights,credit,marker=item
    req=urllib.request.Request(url,headers={"User-Agent":"ADA-Public-Evidence/1.0 (historical research)"})
    with urllib.request.urlopen(req,timeout=30) as r:
        final=r.geturl()
        if urllib.parse.urlparse(final).hostname!=urllib.parse.urlparse(url).hostname: raise ValueError("unexpected host redirect")
        data=r.read(20_000_001)
        if r.status!=200 or len(data)>20_000_000 or marker.lower().encode() not in data.lower(): raise ValueError("unexpected response")
        if any(x in data[:10000].lower() for x in (b"verify that you're not a robot",b"captcha challenge",b"access denied")): raise ValueError("blocked response")
        content_type=r.headers.get("Content-Type")
    sha=hashlib.sha256(data).hexdigest()
    folder=ROOT/audit/"snapshots"/sid/sha
    folder.mkdir(parents=True,exist_ok=True)
    payload=folder/"source.html"
    if payload.exists() and payload.read_bytes()!=data: raise ValueError("digest collision or existing file altered")
    if not payload.exists(): payload.write_bytes(data)
    receipt=folder/"receipt.json"
    if not receipt.exists():
        receipt.write_text(json.dumps(dict(id=sid,source=url,final_url=final,sha256=sha,bytes=len(data),content_type=content_type,rights=rights,attribution=credit,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),review_pending=True),indent=2)+"\n")
    return str(folder)
if __name__=="__main__":
    failures=0
    for item in SOURCES:
        try: print(fetch(item))
        except Exception as e: failures+=1;print(item[0],item[1],"NOT ACQUIRED",str(e))
    raise SystemExit(bool(failures))
