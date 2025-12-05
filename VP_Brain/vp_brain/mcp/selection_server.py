from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional
from .routes_voice import router as voice_router


class SegmentRequest(BaseModel):
    segment_group_id: str
    label: str | None = None


class AIResponse(BaseModel):
    segment_group_id: str
    intent: str
    action: str
    message: str
    emotion: str = "neutral"
    effects: Dict[str, bool] = Field(default_factory=dict)
    model_url: Optional[str] = None

app = FastAPI(title="VisionPilot Selection Server")
app.include_router(voice_router, prefix="/ai")

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


@app.post("/ai/segment", response_model=AIResponse)
async def handle_segment(req: SegmentRequest) -> AIResponse:
    sgid = req.segment_group_id

    # Special demo object
    if sgid == "plant_01":
        return AIResponse(
            segment_group_id=sgid,
            intent="educational_fact",
            action="speak_highlight_and_spawn_hologram",
            message="This is Peace Lily. It likes indirect light and moist soil.",
            emotion="friendly",
            effects={"highlight": True, "hologram": True},
            model_url="https://your-cdn-or-hyper3d-url/plant_01.glb",
        )

    # TEMP: simple hardcoded logic for demo
    if sgid.startswith("plant"):
        return AIResponse(
            segment_group_id=sgid,
            intent="educational_fact",
            action="speak_and_highlight",
            message=f"This is {req.label or 'a plant'}. It likes indirect light and moist soil.",
            emotion="friendly",
            effects={"highlight": True, "hologram": False},
        )

    if sgid.startswith("book"):
        return AIResponse(
            segment_group_id=sgid,
            intent="assistant_tip",
            action="speak",
            message="You were reading this last time. Do you want a quick summary?",
            emotion="neutral",
            effects={"highlight": False, "hologram": False},
        )

    # default fallback
    return AIResponse(
        segment_group_id=sgid,
        intent="smalltalk",
        action="speak",
        message="I see something interesting there. I’ll learn more about it next time.",
        emotion="casual",
        effects={"highlight": False, "hologram": False},
    )


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
