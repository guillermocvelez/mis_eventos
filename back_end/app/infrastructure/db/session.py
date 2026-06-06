from sqlmodel import create_engine, Session
from app.infrastructure.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=True,        
    pool_pre_ping=True,  
)


def get_db():
    """Dependencia FastAPI que provee una sesión de BD por request."""
    with Session(engine) as session:
        yield session