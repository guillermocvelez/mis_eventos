from fastapi import FastAPI
from app.infrastructure.web.routers.auth import router as auth_router

app = FastAPI(title="Mis Eventos API")

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Mis Eventos API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
