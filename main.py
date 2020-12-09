from typing import Optional
from recoll import recoll
from fastapi import FastAPI
from fastapi import FastAPI, Request
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
        searchType: Optional[int] = 1,
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = 0,
        page: Optional[int] = 1):
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
def recoll_query(query, searchType, dir, sort, ascending, page):
    db = recoll.connect()
    q = db.query()
    nres = q.execute(query)
    results = q.fetchmany(20)
    return results

