import html
import os
import re
import urllib.parse
from base64 import urlsafe_b64encode
from hashlib import sha256

from aiohttp import ClientSession
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.setup_rollbar import rollbar_handler
from app.utils.db import db_instance

router = APIRouter()

CLIENT_ID = "student-personal-cabinet"
PROVIDER_URL = "https://id.itmo.ru/auth/realms/itmo"
REDIRECT_URI = "https://my.itmo.ru/login/callback"

class LoginRequest(BaseModel):
    username: str
    password: str

@rollbar_handler
def generate_code_verifier():
    code_verifier = urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    return re.sub("[^a-zA-Z0-9]+", "", code_verifier)


@rollbar_handler
def get_code_challenge(code_verifier: str):
    code_challenge_bytes = sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = urlsafe_b64encode(code_challenge_bytes).decode("utf-8")
    return code_challenge.replace("=", "")


@router.post("/login_with_password")
@rollbar_handler
async def login_with_password(payload: LoginRequest):
    username = payload.username
    password = payload.password

    # Test user shortcut
    if username == "999999" and password == "test":
        # Mock user info
        user_info = {
            "isu": 999999,  # some mock isu
            "gender": "other",
            "birthdate": "2000-01-01",
            "groups": [{"course": 4, "faculty": {"name": "Test Faculty"}}],
        }

        user_collection = db_instance.get_collection("users")
        existing_user = await user_collection.find_one({"isu": user_info["isu"]})

        if not existing_user:
            await fill_user_info(user_info)
        return {"redirect": "/auth/register/select_username", "isu": user_info["isu"]}

    # Actual Keycloak logic below:
    code_verifier = generate_code_verifier()
    code_challenge = get_code_challenge(code_verifier)

    async with ClientSession() as session:
        auth_resp = await session.get(
            f"{PROVIDER_URL}/protocol/openid-connect/auth",
            params={
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "response_type": "code",
                "scope": "openid profile",
                "state": "random_state",
                "code_challenge_method": "S256",
                "code_challenge": code_challenge,
            },
        )
        auth_resp.raise_for_status()
        resp_text = await auth_resp.text()

        form_regex = re.compile(r'<form\s+.*?\s+action="(?P<action>.*?)"', re.DOTALL)
        form_action_match = re.search(form_regex, resp_text)
        if not form_action_match:
            raise HTTPException(status_code=500, detail="Failed to find form action for login")

        form_action = html.unescape(form_action_match.group("action"))

        form_resp = await session.post(
            url=form_action,
            data={"username": username, "password": password},
            cookies=auth_resp.cookies,
            allow_redirects=False,
        )

        if form_resp.status != 302:
            raise HTTPException(
                status_code=form_resp.status,
                detail="Login failed with provided credentials",
            )

        redirect_url = form_resp.headers["Location"]
        query = urllib.parse.urlparse(redirect_url).query
        redirect_params = urllib.parse.parse_qs(query)
        auth_code = redirect_params.get("code")
        if not auth_code:
            raise HTTPException(status_code=500, detail="Authorization code not found after login")

        token_resp = await session.post(
            f"{PROVIDER_URL}/protocol/openid-connect/token",
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "code": auth_code[0],
                "code_verifier": code_verifier,
            },
        )
        token_resp.raise_for_status()

        token_data = await token_resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=500, detail="Failed to retrieve access token")

        user_info_url = f"{PROVIDER_URL}/protocol/openid-connect/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        user_resp = await session.get(user_info_url, headers=headers)

        if user_resp.status != 200:
            raise HTTPException(status_code=user_resp.status, detail="User info retrieval failed")

        user_info = await user_resp.json()
        user_collection = db_instance.get_collection("users")
        user_resp.close()

        existing_user = await user_collection.find_one({"isu": user_info["isu"]})

        if existing_user:
            # Возвращаем JSON с redirect
            return {"redirect": "/auth/dashboard", "isu": user_info["isu"]}
        else:
            await fill_user_info(user_info)
            return {"redirect": "/auth/register/select_username", "isu": user_info["isu"]}

@router.get("/dashboard")
@rollbar_handler
async def dashboard_stub():
    return {"message": "Welcome to the dating service!"}


@rollbar_handler
async def fill_user_info(user_info: dict):
    user_collection = db_instance.get_collection("users")

    selected_group = max(user_info.get("groups", []), key=lambda g: g.get("course", 0), default=None)
    course = selected_group.get("course", None) if selected_group else None
    faculty = selected_group.get("faculty", {}).get("name", "") if selected_group else ""

    new_user = {
        "isu": user_info["isu"],
        "username": "",
        "bio": "",
        "logo": "",
        "photos": [],
        "mainFeatures": [
            {"text": "", "icon": "height"},
            {"text": "", "icon": "zodiac_sign"},
            {"text": "", "icon": "weight"},
            {"text": user_info.get("gender", ""), "icon": "gender"},
            {"text": user_info.get("birthdate", ""), "icon": "birthdate"},
        ],
        "interests": [],
        "itmo": [
            {"text": faculty, "icon": "faculty"},
            {"text": str(course) if course else "", "icon": "course"},
        ],
        "gender_preferences": [],
        "relationship_preferences": [],
        "isStudent": True,
    }

    await user_collection.insert_one(new_user)
