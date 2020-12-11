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
import shlex

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

DEFAULTS = {
    'context': 30,
    'stem': 1,
    'timefmt': '%c',
    'dirdepth': 3,
    'maxchars': 500,
    'maxresults': 0,
    'perpage': 25,
    'csvfields': 'filename title author size time mtype url',
    'title_link': 'download',
}

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
    config = get_config()
    return templates.TemplateResponse("main.html", {"request": request,
                                                        "sorts": SORTS,
                                                        "render_path": render_path,
                                                        "dirs": sorted_dirs(config["dirs"], config["dirdepth"])})

@app.get("/results", response_class=HTMLResponse)
async def results(request: Request, 
        query: str,
        searchtype: Optional[int] = Query(1, ge=1, le=3),
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = Query(0, ge=0, le=1),
        page: Optional[int] = Query(1, ge=1)):
    config = get_config()
    #results, nres, time = recoll_search(query, searchtype, dir, sort, ascending, page, dosnippets=False)
    results, nres, time = await recoll_search(query, searchtype, dir, sort, ascending, page)
    return templates.TemplateResponse("results.html", {"request": request, 
                                                        "results": results,
                                                        "nres": nres,
                                                        "time": round(time.total_seconds(), 2),
                                                        "searchtype": searchtype,
                                                        "page": page,
                                                        "qs": build_query_string(wrap_query(query, searchtype), dir),
                                                        "pages": calculate_pages(nres, config['perpage']),
                                                        "page_href": render_page_link,
                                                        "packet_href": render_packet_link,
                                                        "render_set_name": render_set_name,
                                                        "offset": calculate_offset(page, config['perpage']),
                                                        "sorts": SORTS,
                                                        "ascending": ascending,
                                                        "render_path": render_path,
                                                        "replace_underscores": replace_underscores,
                                                        "dirs": sorted_dirs(config['dirs'], config['dirdepth'])})

# Helper methods
query_wraps = ["\"%s\"l", "\"ANSWER: %s\"", "%s"]
tossup_keywords = ["for 10 points", "for ten points", "ftp"]
bonus_keywords = ["for 10 points each", "for ten points each", "ftpe"]

def get_config():
    config = {}
    # get useful things from recoll.conf
    rclconf = rclconfig.RclConfig()
    config['confdir'] = rclconf.getConfDir()
    config['dirs'] = [os.path.expanduser(d) for d in
                      shlex.split(rclconf.getConfParam('topdirs'))]
    config['stemlang'] = rclconf.getConfParam('indexstemminglanguages')
    # get config from cookies or defaults
    for k, v in DEFAULTS.items():
        #value = select([bottle.request.get_cookie(k), v])
        #config[k] = type(v)(value)
        config[k] = v
    # Fix csvfields: get rid of invalid ones to avoid needing tests in the dump function
    cf = config['csvfields'].split()
    ncf = [f for f in cf if f in FIELDS]
    config['csvfields'] = ' '.join(ncf)
    config['fields'] = ' '.join(FIELDS)
    # get mountpoints
    config['mounts'] = {}
    for d in config['dirs']:
    #    name = 'mount_%s' % urllib.parse.quote(d,'')
    #    config['mounts'][d] = select([bottle.request.get_cookie(name), 'aseemsdb.me%s' % d], [None, ''])
        config['mounts'][d] = 'aseemsdb.me%s' % d
    return config

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
    return replace_underscores(re.sub('.+/','', path))

def replace_underscores(filename):
    return filename.replace("_", " ")

def render_page_link(query, page):
    q = dict(query)
    q['page'] = page
    # TODO: extract 'results' out into a string variable
    return './results?%s' % urllib.parse.urlencode(q)

def render_packet_link(filename):
    return "." + filename[filename.find('/static'):]

def render_set_name(filename):
    return replace_underscores('/'.join(filename.rsplit('/',3)[1:-1]))

def calculate_offset(page, per_page):
    return (page - 1) * per_page

def calculate_pages(nres, per_page):
    return int(math.ceil(nres/float(per_page)))

def build_query_string(query, dir):
    # TODO: strip out ? modifier if not searchtype 3
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

def make_question_badge(snippet):
    bonus_badge = '<span class="label label-info">Bonus</span>'
    tossup_badge = '<span class="label label-primary">Tossup</span>'
    snippet = snippet.lower()
    if any(keyword in snippet for keyword in bonus_keywords):
        return bonus_badge
    elif any(keyword in snippet for keyword in tossup_keywords):
        return tossup_badge
    elif snippet.count(" [10] ") > 0:
        return bonus_badge
    else:
        return tossup_badge

async def recoll_search(query, searchtype, dir, sort, ascending, page, dosnippets=True):
    config = get_config()
    query = wrap_query(query, searchtype)
    tstart = datetime.datetime.now()
    q = recoll_initsearch(query, dir, sort, ascending)
    nres = q.rowcount

    offset = calculate_offset(page, config['perpage'])
    q = scroll_query(q, offset)
    highlighter = HlMeths()
    results = []
    for i in range(config['perpage']):
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
                d['question_type'] = make_question_badge(d['snippet'])
            results.append(d)
        except:
            break
    q.close()
    tend = datetime.datetime.now()
    return results, nres, tend - tstart


def wrap_query(query, searchtype):
    return query_wraps[searchtype - 1] % query
