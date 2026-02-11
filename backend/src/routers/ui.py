from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter(tags=["ui"])

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

@router.get("/")
def ui_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
