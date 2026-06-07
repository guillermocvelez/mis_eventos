from fastapi import FastAPI
from app.infrastructure.web.routers.auth import router as auth_router
from app.infrastructure.web.routers.events import router as events_router


app = FastAPI(title="Mis Eventos API")

app.include_router(auth_router)
app.include_router(events_router)


@app.get("/")
def read_root():
    return {"message": "Mis Eventos API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
