import pytest
from app.application.use_cases.auth import RegisterUser, LoginUser
from app.application.dtos.user_dto import UserDTO, TokenDTO
from app.domain.exceptions import AlreadyRegistered, Unauthorized
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_security import FakePasswordHasher, FakeTokenService


@pytest.fixture
def deps():
    return {
        "user_repo": FakeUserRepository(),
        "hasher": FakePasswordHasher(),
        "token_service": FakeTokenService(),
    }



class TestRegisterUser:

    def test_registro_exitoso(self, deps):
        use_case = RegisterUser(**deps)
        result = use_case.execute(email="user@test.com", password="1234")

        assert isinstance(result, UserDTO)
        assert result.email == "user@test.com"
        assert result.role == "attendee"

    def test_contrasena_se_hashea(self, deps):
        use_case = RegisterUser(**deps)
        use_case.execute(email="user@test.com", password="1234")

        saved = deps["user_repo"].find_by_email("user@test.com")
        assert saved.hashed_password == "hashed:1234"
        assert saved.hashed_password != "1234"

    def test_email_duplicado_lanza_excepcion(self, deps):
        use_case = RegisterUser(**deps)
        use_case.execute(email="user@test.com", password="1234")

        with pytest.raises(AlreadyRegistered):
            use_case.execute(email="user@test.com", password="otra")



class TestLoginUser:

    def _registrar(self, deps, email="user@test.com", password="1234"):
        RegisterUser(**deps).execute(email=email, password=password)

    def test_login_exitoso(self, deps):
        self._registrar(deps)
        use_case = LoginUser(**deps)
        result = use_case.execute(email="user@test.com", password="1234")

        assert isinstance(result, TokenDTO)
        assert result.token_type == "bearer"
        assert "token:" in result.access_token

    def test_email_inexistente_lanza_excepcion(self, deps):
        use_case = LoginUser(**deps)

        with pytest.raises(Unauthorized):
            use_case.execute(email="noexiste@test.com", password="1234")

    def test_contrasena_incorrecta_lanza_excepcion(self, deps):
        self._registrar(deps)
        use_case = LoginUser(**deps)

        with pytest.raises(Unauthorized):
            use_case.execute(email="user@test.com", password="incorrecta")