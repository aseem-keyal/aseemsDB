from typing import Optional
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import datetime

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
@app.get("/results", response_class=HTMLResponse)
async def results(request: Request, 
        query: str,
        searchType: Optional[int] = Query(1, ge=1, le=3),
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = Query(0, ge=0, le=1),
        page: Optional[int] = Query(1, ge=1)):
    results, nres, time = recoll_search(query, searchType, dir, sort, ascending, page)
    return templates.TemplateResponse("results.html", {"request": request, 
                                                        "results": results,
                                                        "nres": nres})

# Helper methods
query_wraps = ["\"%s\"l", "\"ANSWER: %s\"", "%s"]
class HlMeths:
    def startMatch(self, idx):
        return '<span class="search-result-highlight">'
    def endMatch(self):
        return '</span>'

def calculate_offset(page, per_page):
    return (page - 1) * per_page

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

def recoll_search(query, searchType, dir, sort, ascending, page, dosnippets=True):
    query = wrap_query(query, searchType)
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
                d['snippet'] = q.makedocabstract(doc, highlighter).encode('utf-8')
            results.append(d)
        except:
            break
    q.close()
    tend = datetime.datetime.now()
    return results, nres, tend - tstart


def wrap_query(query, searchType):
    return query_wraps[searchType - 1] % query
