from typing import Optional
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import re
import datetime
import glob
import os
import math
import urllib

try:
    from recoll import recoll
    from recoll import rclextract
    hasrclextract = True
except:
    import recoll
    hasrclextract = False
try:
    from recoll import rclconfig
except:
    import rclconfig

SORTS = [
    ("url", "Path"),
    ("relevancyrating", "Relevancy"),
    ("mtime", "Date",),
    ("filename", "Filename"),
    ("fbytes", "Size"),
    ("author", "Author"),
]

FIELDS = [
    # exposed by python api
    'ipath',
    'filename',
    'title',
    'author',
    'fbytes',
    'dbytes',
    'size',
    'fmtime',
    'dmtime',
    'mtime',
    'mtype',
    'origcharset',
    'sig',
    'relevancyrating',
    'url',
    'abstract',
    'keywords',
    # calculated
    'time',
    'snippet',
    'label',
]

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# API methods
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/results", response_class=HTMLResponse)
async def results(request: Request, 
        query: str,
        searchtype: Optional[int] = Query(1, ge=1, le=3),
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = Query(0, ge=0, le=1),
        page: Optional[int] = Query(1, ge=1)):
    results, nres, time = recoll_search(query, searchtype, dir, sort, ascending, page)
    return templates.TemplateResponse("results.html", {"request": request, 
                                                        "results": results,
                                                        "nres": nres,
                                                        "time": round(time.total_seconds(), 2),
                                                        "searchtype": searchtype,
                                                        "page": page,
                                                        "pages": calculate_pages(nres, 25),
                                                        "page_href": render_page_link,
                                                        "sorts": SORTS,
                                                        "render_path": render_path,
                                                        "dirs": sorted_dirs(["/home/aseem/Documents/aseemsDB/fastapi-rewrite/static/packet_archive/"], 2)})

# Helper methods
query_wraps = ["\"%s\"l", "\"ANSWER: %s\"", "%s"]
def get_dirs(tops, depth):
    v = []
    for top in tops:
        dirs = [top]
        for d in range(1, depth+1):
            dirs = dirs + glob.glob(top + '/*' * d)
        dirs = filter(lambda f: os.path.isdir(f), dirs)
        top_path = top.rsplit('/', 1)[0]
        dirs = [w.replace(top_path+'/', '', 1) for w in dirs]
        v = v + dirs
    return ['<all>'] + v

def sorted_dirs(tops, depth):
    return filter(None, sorted(get_dirs(tops, depth), key=lambda p: (p.count(os.path.sep), p)))

class HlMeths:
    def startMatch(self, idx):
        return '<span class="search-result-highlight">'
    def endMatch(self):
        return '</span>'

def render_path(path):
    return re.sub('.+/','', path).replace("_", " ")

def render_page_link(query, page):
    q = dict(query)
    q['page'] = page
    # TODO: extract 'results' out into a string variable
    return './results?%s' % urllib.parse.urlencode(q)

def calculate_offset(page, per_page):
    return (page - 1) * per_page

def calculate_pages(nres, per_page):
    return int(math.ceil(nres/float(per_page)))

def build_query_string(query, dir):
    qs = query
    qs = qs.replace("\\", "")
    qs = qs.replace("\'", " ")
    qs = qs.replace(".", "")
    if dir != '<all>':
        qs += " dir:\"%s\" " % dir 
    return qs

def recoll_initsearch(query, dir, sort, ascending):
    db = recoll.connect()
    db.setAbstractParams(200, 30)
    q = db.query()
    q.sortby(sort, ascending)
    qs = build_query_string(query, dir)
    nres = q.execute(qs)
    return q

def scroll_query(query, offset):
    if query.rowcount > 0:
        if type(query.next) == int:
            query.next = offset
        else:
            query.scroll(offset, mode='absolute')
    return query

def recoll_search(query, searchtype, dir, sort, ascending, page, dosnippets=True):
    query = wrap_query(query, searchtype)
    tstart = datetime.datetime.now()
    q = recoll_initsearch(query, dir, sort, ascending)
    nres = q.rowcount

    offset = calculate_offset(page, 25)
    q = scroll_query(q, offset)
    highlighter = HlMeths()
    results = []
    for i in range(25):
        try:
            doc = q.fetchone()
            d = {}
            for f in FIELDS:
                v = getattr(doc, f)
                if v is not None:
                    d[f] = v
                else:
                    d[f] = ''
            if dosnippets:
                d['snippet'] = q.makedocabstract(doc, highlighter)
            results.append(d)
        except:
            break
    q.close()
    tend = datetime.datetime.now()
    return results, nres, tend - tstart


def wrap_query(query, searchtype):
    return query_wraps[searchtype - 1] % query
