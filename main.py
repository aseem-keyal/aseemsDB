from typing import Optional
from recoll import recoll
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
    results = recoll_query(query, searchType, dir, sort, ascending, page)
    return templates.TemplateResponse("results.html", {"request": request, "results": results})

@app.get("/query")
async def run_query(query: str,
        searchType: Optional[int] = 1,
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = 0,
        page: Optional[int] = 1):
    return recoll_query(query, searchType, dir, sort, ascending, page)

# Helper methods
query_wraps = ["\"%s\"l", "\"ANSWER: %s\"", "%s"]

def recoll_query(query, searchType, dir, sort, ascending, page):
    db = recoll.connect()
    q = db.query()
    query = wrap_query(query, searchType)
    nres = q.execute(query)
    results = q.fetchmany(20)
    return results

def wrap_query(query, searchType):
    return query_wraps[searchType - 1] % query
