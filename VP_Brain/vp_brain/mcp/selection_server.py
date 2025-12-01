# VP_Brain/selection_server.py
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Selection(BaseModel):
    x: float  # normalized 0–1
    y: float  # normalized 0–1

latest = Selection(x=-1.0, y=-1.0)

@app.post("/selection")
async def update_selection(sel: Selection):
    global latest
    latest = sel
    return {"status": "ok"}

@app.get("/selection")
async def get_selection():
    return latest

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # for public/on-network access change to:
    # uvicorn.run(app, host="0.0.0.0", port=8000)