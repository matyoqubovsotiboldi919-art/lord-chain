from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

from src.routers.auth import router as auth_router
from src.routers.users import router as users_router
from src.routers.tx import router as tx_router
from src.routers.explorer import router as explorer_router
from src.routers.admin import router as admin_router

app = FastAPI(title="LORD API")

# ✅ CORS: browser OPTIONS (preflight) 405 bo‘lmasin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # localda shunday; keyin deployda domen qo'yiladi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API routerlar
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tx_router)
app.include_router(explorer_router)
app.include_router(admin_router)

# ✅ Frontend /ui da (API bilan urishmaydi)
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/ui", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/")
