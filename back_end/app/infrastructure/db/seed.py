from sqlmodel import Session
from app.infrastructure.db.session import engine
from app.infrastructure.orm.models import UserORM
from app.infrastructure.security.password_hasher import BcryptPasswordHasher

def seed():
    hasher = BcryptPasswordHasher()
    with Session(engine) as session:
        admin = UserORM(
            email="admin@miseventos.com",
            hashed_password=hasher.hash("admin123"),
            role="admin"
        )
        session.add(admin)
        session.commit()
        print("Admin creado")

if __name__ == "__main__":
    seed()