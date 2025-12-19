from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base, engine
import app.models.models # Import models to register them with Base

# Create tables on startup (Simple approach for MVP)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
origins = [
    "http://localhost:5173", # Vite
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "survival_mode": "active"}

from app.api.routes import account, trades, journal

app.include_router(account.router, prefix=f"{settings.API_V1_STR}/account", tags=["account"])
app.include_router(trades.router, prefix=f"{settings.API_V1_STR}/trades", tags=["trades"])
app.include_router(journal.router, prefix=f"{settings.API_V1_STR}/journal", tags=["journal"])
