from typing import Optional
from fastapi import FastAPI, Request, Query, Path, Response
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
import hashlib
import string
import json
import csv
import io

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
                                                        "snippets": 1,
                                                        "dirs": sorted_dirs(config["dirs"], config["dirdepth"])})


@app.get("/faq", response_class=HTMLResponse)
async def faq(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/preview/{resnum}", response_class=HTMLResponse)
async def preview(request: Request, 
        query: str,
        resnum: int = Path(..., title="The ID of the result to get", ge=0),
        searchtype: Optional[int] = Query(1, ge=1, le=3),
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = Query(0, ge=0, le=1),
        page: Optional[int] = Query(1, ge=1)):
    config = get_config()
    packet_text, filename = await recoll_packet_text(resnum, query, searchtype, dir, sort, ascending, page)
    return templates.TemplateResponse("preview.html", {"request": request, 
                                                        "filename": filename,
                                                        "packet_text": packet_text})

@app.get("/json")
async def get_json(request: Request, 
        response: Response,
        query: str,
        searchtype: Optional[int] = Query(1, ge=1, le=3),
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = Query(0, ge=0, le=1)):
    qs = build_query_string(wrap_query(query, searchtype), dir)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = 'attachment; filename=recoll-%s.json' % normalise_filename(qs)
    res, nres, time = await recoll_search(query, searchtype, dir, sort, ascending, 0, dosnippets=True)
    print(dict(request.query_params))
    return json.dumps({ 'query': dict(request.query_params), 'results': res })

@app.get("/csv")
async def get_csv(request: Request, 
        response: Response,
        query: str,
        searchtype: Optional[int] = Query(1, ge=1, le=3),
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = Query(0, ge=0, le=1)):
    qs = build_query_string(wrap_query(query, searchtype), dir)
    config = get_config()
    res, nres, time = await recoll_search(query, searchtype, dir, sort, ascending, 0, dosnippets=False)
    response.headers['Content-Disposition'] = 'attachment; filename=recoll-%s.csv' % normalise_filename(qs)
    
    si = io.StringIO()
    cw = csv.writer(si)
    fields = config['csvfields'].split()
    cw.writerow(fields)
    for doc in res:
        row = []
        for f in fields:
            row.append(doc[f])
        cw.writerow(row)
    data = si.getvalue().strip("\r\n")
    return data

@app.get("/results", response_class=HTMLResponse)
async def results(request: Request, 
        query: str,
        searchtype: Optional[int] = Query(1, ge=1, le=3),
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = Query(0, ge=0, le=1),
        snippets: Optional[bool] = False,
        page: Optional[int] = Query(1, ge=1)):
    config = get_config()
    results, nres, time = await recoll_search(query, searchtype, dir, sort, ascending, page, dosnippets=snippets)
    #results, nres, time = await recoll_search(query, searchtype, dir, sort, ascending, page)
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
                                                        "set_href": render_set_link,
                                                        "preview_href": render_preview_link,
                                                        "render_set_name": render_set_name,
                                                        "offset": calculate_offset(page, config['perpage']),
                                                        "sorts": SORTS,
                                                        "snippets": snippets,
                                                        "ascending": ascending,
                                                        "render_path": render_path,
                                                        "render_link_params": render_link_params,
                                                        "render_packet_name": render_packet_name,
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

def normalise_filename(fn):
    valid_chars = "_-%s%s" % (string.ascii_letters, string.digits)
    out = ""
    for i in range(0,len(fn)):
        if fn[i] in valid_chars:
            out += fn[i]
        else:
            out += "_"
    return out

def sorted_dirs(tops, depth):
    return filter(None, sorted(get_dirs(tops, depth), key=lambda p: (p.count(os.path.sep), p)))

class HlMeths:
    def startMatch(self, idx):
        return '<span class="search-result-highlight">'
    def endMatch(self):
        return '</span>'

def render_path(path):
    return replace_underscores(re.sub('.+/','', path))

def render_link_params(path, params):
    return path % urllib.parse.urlencode(params)

def render_preview_link(resnum, params):
    # TODO: extract 'preview' out into a string variable
    return render_link_params("./preview/" + str(resnum) + "?%s", params)

def replace_underscores(filename):
    return filename.replace("_", " ")

def replace_pdf_ext(filename):
    return filename.replace(".pdf", "")

def render_packet_name(filename):
    return replace_pdf_ext(replace_underscores(filename))

def render_page_link(query, page):
    q = dict(query)
    q['page'] = page
    # TODO: extract 'results' out into a string variable
    return './results?%s' % urllib.parse.urlencode(q)

def render_packet_link(filename, page=1):
    return "." + filename[filename.find('/static'):] + "#page=" + str(page)

def render_set_link(filename):
    q = {}
    q['dir'] = "/".join(filename.rsplit('/',3)[1:-1])
    q['query'] = "the"
    q['snippets'] = 1
    return './results?%s' % urllib.parse.urlencode(q)

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

def get_page_num(snippet):
    if len(re.findall(r'\d+', snippet)) > 0:
        return re.findall(r'\d+', snippet)[0]
    return 1

async def recoll_search(query, searchtype, dir, sort, ascending, page, dosnippets=True):
    config = get_config()
    query = wrap_query(query, searchtype)
    tstart = datetime.datetime.now()
    q = recoll_initsearch(query, dir, sort, ascending)
    nres = q.rowcount

    if config['maxresults'] == 0:
        config['maxresults'] = nres
    if nres > config['maxresults']:
        nres = config['maxresults']
    if config['perpage'] == 0 or page == 0:
        config['perpage'] = nres
        page = 1

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
            d['sha'] = hashlib.sha1((d['url']+d['ipath']).encode('utf-8')).hexdigest()
            if dosnippets:
                d['snippet'] = q.makedocabstract(doc, highlighter)
                d['page_num'] = get_page_num(d['snippet'])
                d['question_type'] = make_question_badge(d['snippet'])
            results.append(d)
        except:
            break
    q.close()
    tend = datetime.datetime.now()
    return results, nres, tend - tstart

async def recoll_packet_text(resnum, query, searchtype, dir, sort, ascending, page):
    if not hasrclextract:
        return 'Sorry, needs recoll version 1.19 or later'
    config = get_config()
    query = wrap_query(query, searchtype)
    q = recoll_initsearch(query, dir, sort, ascending)
    if resnum > q.rowcount - 1:
        return 'Bad result index %d' % resnum
    q.scroll(resnum)
    doc = q.fetchone()
    xt = rclextract.Extractor(doc)
    tdoc = xt.textextract(doc.ipath)
    return tdoc.text, render_packet_name(doc.filename)

def wrap_query(query, searchtype):
    return query_wraps[searchtype - 1] % query
