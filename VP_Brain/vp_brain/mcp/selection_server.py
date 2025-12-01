from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

app = FastAPI(title="VisionPilot Selection Server")

SEGMENTS = {
    "cover": {
        "description": "Front cover of the magic book",
    },
    "page_1": {
        "description": "First AR page / intro scene",
    },
    "page_2": {
        "description": "Second AR page / volcano scene",
    },
    "page_3": {
        "description": "Third AR page / whatever",
    },
    "chapter_2": {
        "description": "Chapter 2 spread",
    },
}


class Selection(BaseModel):
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    source: str = "demo"
    segment_id: Optional[str] = None


class SelectionOut(BaseModel):
    x: float
    y: float
    source: str
    segment_id: Optional[str]
    ts: datetime


# Initial dummy value
latest_selection = SelectionOut(
    x=0.5,
    y=0.5,
    source="init",
    segment_id=None,
    ts=datetime.utcnow(),
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/selection", response_model=SelectionOut)
def get_selection():
    return latest_selection


@app.post("/selection", response_model=SelectionOut)
def set_selection(sel: Selection):
    global latest_selection

    latest_selection = SelectionOut(
        x=sel.x,
        y=sel.y,
        source=sel.source,
        segment_id=sel.segment_id,
        ts=datetime.utcnow(),
    )
    return latest_selection


if __name__ == "__main__":
    # Allow running directly or via `python -m vp_brain.mcp.selection_server`
    import sys
    import pathlib
    try:
        import uvicorn  # type: ignore
    except Exception as exc:
        raise SystemExit(
            "Uvicorn is required to run the server. Install with 'pip install uvicorn'"
        ) from exc

    # Ensure project root is on sys.path when running directly
    project_root = pathlib.Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    uvicorn.run(
        "vp_brain.mcp.selection_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )