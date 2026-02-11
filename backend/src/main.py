# backend/src/main.py
from fastapi import FastAPI

from src.routers.auth import router as auth_router
from src.routers.users import router as users_router
from src.routers.tx import router as tx_router
from src.routers.admin import router as admin_router

from fastapi.staticfiles import StaticFiles
from pathlib import Path




app = FastAPI(title="LORD Chain API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tx_router)
app.include_router(admin_router)


FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
@app.get("/health")
def health():
    return {"status": "ok"}
