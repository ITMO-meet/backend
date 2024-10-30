import re
import html
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.utils.db import db_instance
from app.models.user import UserModel
from aiohttp import ClientSession
from hashlib import sha256
from base64 import urlsafe_b64encode
import os
import urllib.parse

router = APIRouter()

CLIENT_ID = "student-personal-cabinet"
PROVIDER_URL = "https://id.itmo.ru/auth/realms/itmo"
REDIRECT_URI = "https://my.itmo.ru/login/callback"


def generate_code_verifier():
    code_verifier = urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    return re.sub("[^a-zA-Z0-9]+", "", code_verifier)


def get_code_challenge(code_verifier: str):
    code_challenge_bytes = sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = urlsafe_b64encode(code_challenge_bytes).decode("utf-8")
    return code_challenge.replace("=", "")


code_verifier = generate_code_verifier()
code_challenge = get_code_challenge(code_verifier)


@router.get("/login_with_password")
async def login_with_password(username: str, password: str):
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

        form_action_match = re.search(
            r'<form\s+.*?\s+action="(?P<action>.*?)"', await auth_resp.text()
        )
        if not form_action_match:
            raise HTTPException(
                status_code=500, detail="Failed to find form action for login"
            )

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
            raise HTTPException(
                status_code=500, detail="Authorization code not found after login"
            )

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
            raise HTTPException(
                status_code=500, detail="Failed to retrieve access token"
            )

        user_info_url = f"{PROVIDER_URL}/protocol/openid-connect/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with session.get(user_info_url, headers=headers) as user_resp:
            if user_resp.status != 200:
                raise HTTPException(
                    status_code=user_resp.status, detail="User info retrieval failed"
                )

            user_info = await user_resp.json()
            user_collection = db_instance.get_collection("users")

            existing_user = await user_collection.find_one({"isu": user_info["isu"]})

            if existing_user:
                return RedirectResponse("/auth/dashboard")
            else:
                await fill_user_info(user_info)
                return RedirectResponse("/auth/register")


@router.get("/dashboard")
async def dashboard_stub():
    return {"message": "Welcome to the dating service!"}


async def fill_user_info(user_info: dict):
    user_collection = db_instance.get_collection("users")

    new_user = UserModel(
        isu=user_info["isu"],
        username=user_info["preferred_username"],
        person_params={
            "given_name": user_info.get("given_name"),
            "family_name": user_info.get("family_name"),
            "gender": user_info.get("gender"),
            "birthdate": user_info.get("birthdate"),
            "faculty": (
                user_info.get("groups")[0]["faculty"]["name"]
                if user_info.get("groups")
                else None
            ),
        },
        photos={"logo": user_info.get("picture")},
        bio="",
    )

    await user_collection.insert_one(new_user.dict(by_alias=True))


@router.get("/register")
async def registration_succes_stub():
    # user data (bio, tags, etc will be updated here)
    return {"message": "Registration successfull!"}
