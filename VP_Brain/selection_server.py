from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class Selection(BaseModel):
    x: float  # normalized 0–1
    y: float  # normalized 0–1
    source: str = None
    segment_id: str = None

latest = Selection(x=-1.0, y=-1.0)

"""
DEPRECATED: Do not use this file.

The selection server lives under the package path:
  vp_brain/mcp/selection_server.py

Run it via:
  - uvicorn vp_brain.mcp.selection_server:app --reload
  - python -m vp_brain.mcp.selection_server
"""

raise SystemExit(
    "selection_server.py at project root is deprecated. "
    "Use 'uvicorn vp_brain.mcp.selection_server:app --reload' or "
    "'python -m vp_brain.mcp.selection_server' instead."
)
