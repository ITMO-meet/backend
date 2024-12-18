from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from app.api.auth import (
    CLIENT_ID,
    PROVIDER_URL,
    REDIRECT_URI,
    generate_code_verifier,
    get_code_challenge,
    login_with_password,
)


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


@pytest.fixture
def mock_dependencies():
    with patch("app.api.auth.generate_code_verifier") as mock_verifier, patch(
        "app.api.auth.get_code_challenge"
    ) as mock_challenge, patch("app.api.auth.ClientSession") as mock_session, patch(
        "app.utils.db.db_instance"
    ) as mock_db_instance, patch("app.api.auth.fill_user_info", new_callable=AsyncMock) as mock_fill_user_info, patch(
        "app.api.auth.PROVIDER_URL", PROVIDER_URL
    ), patch("app.api.auth.CLIENT_ID", CLIENT_ID), patch("app.api.auth.REDIRECT_URI", REDIRECT_URI):
        mock_verifier.return_value = "test_code_verifier"
        mock_challenge.return_value = "test_code_challenge"

        yield {
            "mock_verifier": mock_verifier,
            "mock_challenge": mock_challenge,
            "mock_session": mock_session,
            "mock_db_instance": mock_db_instance,
            "mock_fill_user_info": mock_fill_user_info,
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
async def test_login_with_password_success(mock_user_info, mock_dependencies):
    session_instance = AsyncMock()
    mock_dependencies["mock_session"].return_value.__aenter__.return_value = session_instance
    mock_dependencies["mock_session"].return_value.__aexit__.return_value = AsyncMock()

    auth_resp = AsyncMock()
    auth_resp.status = 200
    auth_resp.text.return_value = f'<form method="post" action="{PROVIDER_URL}"></form>'
    auth_resp.cookies = {"some_cookie": "cookie_value"}

    form_resp = AsyncMock()
    form_resp.status = 302
    form_resp.headers = {"Location": f"{REDIRECT_URI}?code=auth_code_value"}

    token_resp = AsyncMock()
    token_resp.status = 200
    token_resp.json.return_value = {"access_token": "test_access_token"}

    user_resp = AsyncMock()
    user_resp.status = 200
    user_resp.json.return_value = mock_user_info

    session_instance.get.side_effect = [auth_resp, user_resp]
    session_instance.post.side_effect = [form_resp, token_resp]

    user_collection_mock = AsyncMock()
    user_collection_mock.find_one.return_value = {
        "isu": mock_user_info["isu"],
        "username": mock_user_info["preferred_username"],
    }

    mock_dependencies["mock_db_instance"].get_collection.return_value = user_collection_mock

    response = await login_with_password("test_user", "test_password")

    assert isinstance(response, RedirectResponse)
    assert response.status_code == 307
    assert response.headers["location"] == "/auth/register/select_username"


@pytest.mark.asyncio
async def test_login_with_password_invalid_credentials(mock_user_info, mock_dependencies):
    mock_session = mock_dependencies["mock_session"]
    mock_fill_user_info = mock_dependencies["mock_fill_user_info"]

    session_instance = AsyncMock()
    mock_session.return_value.__aenter__.return_value = session_instance

    auth_resp = AsyncMock()
    auth_resp.status = 200
    auth_resp.text.return_value = f'<form method="post" action="{PROVIDER_URL}"></form>'
    auth_resp.cookies = {"some_cookie": "cookie_value"}

    form_resp = AsyncMock()
    form_resp.status = 401

    session_instance.get.side_effect = [auth_resp]
    session_instance.post.side_effect = [form_resp]

    with pytest.raises(HTTPException) as exc_info:
        await login_with_password("test_user", "wrong_password")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Login failed with provided credentials"

    mock_fill_user_info.assert_not_called()


@pytest.mark.asyncio
async def test_login_with_password_form_action_not_found(mock_user_info, mock_dependencies):
    mock_session = mock_dependencies["mock_session"]
    mock_fill_user_info = mock_dependencies["mock_fill_user_info"]

    session_instance = AsyncMock()
    mock_session.return_value.__aenter__.return_value = session_instance

    auth_resp = AsyncMock()
    auth_resp.status = 200
    auth_resp.text.return_value = "<html>No form here</html>"
    auth_resp.cookies = {"some_cookie": "cookie_value"}

    session_instance.get.side_effect = [auth_resp]

    with pytest.raises(HTTPException) as exc_info:
        await login_with_password("test_user", "test_password")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Failed to find form action for login"

    mock_fill_user_info.assert_not_called()
