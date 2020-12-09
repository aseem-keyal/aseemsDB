from typing import Optional
from recoll import recoll
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/results")
def read_item(query: str,
        searchType: Optional[int] = 1,
        dir: Optional[str] = "<all>",
        sort: Optional[str] = "url",
        ascending: Optional[int] = 0,
        page: Optional[int] = 1):
    db = recoll.connect()
    q = db.query()
    nres = q.execute(query)
    results = q.fetchmany(20)
    return results
