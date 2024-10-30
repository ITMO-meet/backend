import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import generate_code_verifier, get_code_challenge, fill_user_info
from app.utils.db import db_instance


client = TestClient(app)


@pytest.fixture
def mock_user_info():
    return {
        "isu": 386871,
        "preferred_username": "graevsky",
        "given_name": "Григорий",
        "family_name": "Раевский",
        "gender": "male",
        "birthdate": "2004-09-06",
        "groups": [{"faculty": {"name": "ФПИ и КТ"}}],
        "picture": "https://photo.itmo.su/avatar.jpg",
    }


def test_generate_code_verifier():
    verifier = generate_code_verifier()
    assert isinstance(verifier, str)
    assert len(verifier) > 0


def test_get_code_challenge():
    verifier = generate_code_verifier()
    challenge = get_code_challenge(verifier)
    assert isinstance(challenge, str)
    assert len(challenge) > 0



@pytest.mark.asyncio
async def test_fill_user_info(mock_user_info, monkeypatch):
    mock_insert_one = AsyncMock()
    monkeypatch.setattr(
        db_instance,
        "get_collection",
        lambda _: type("MockCollection", (object,), {"insert_one": mock_insert_one}),
    )

    await fill_user_info(mock_user_info)

    mock_insert_one.assert_called_once()
    insert_data = mock_insert_one.call_args[0][0] 
    assert insert_data["isu"] == mock_user_info["isu"]
    assert insert_data["username"] == mock_user_info["preferred_username"]
    assert insert_data["person_params"]["given_name"] == mock_user_info["given_name"]
    assert insert_data["photos"]["logo"] == mock_user_info["picture"]
