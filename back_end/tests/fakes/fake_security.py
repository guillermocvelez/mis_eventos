from app.domain.ports.security import IPasswordHasher, ITokenService

class FakePasswordHasher(IPasswordHasher):
    def hash(self, plain: str) -> str:
        return f"hashed:{plain}"

    def verify(self, plain: str, hashed: str) -> bool:
        return hashed == f"hashed:{plain}"


class FakeTokenService(ITokenService):
    def create_token(self, payload: dict) -> str:
        return f"token:{payload.get('sub')}"

    def decode_token(self, token: str) -> dict:
        if not token.startswith("token:"):
            raise ValueError("Invalid token")
        return {"sub": token.removeprefix("token:")}