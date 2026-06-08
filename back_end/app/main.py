from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.web.routers.auth import router as auth_router
from app.infrastructure.web.routers.events import router as events_router
from app.infrastructure.web.routers.sessions import router as sessions_router
from app.infrastructure.web.routers.registrations import router as registrations_router
from app.infrastructure.web.routers.session_registrations import router as session_registrations_router
from app.infrastructure.web.routers.speakers import router as speakers_router



app = FastAPI(title="Mis Eventos API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(sessions_router)
app.include_router(registrations_router)
app.include_router(session_registrations_router)
app.include_router(speakers_router)





@app.get("/")
def read_root():
    return {"message": "Mis Eventos API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
