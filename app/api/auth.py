import re
import html
import urllib.parse
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.utils.db import db_instance
from aiohttp import ClientSession
from hashlib import sha256
from base64 import urlsafe_b64encode
import os

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

@router.get("/login_with_password")
async def login_with_password(username: str, password: str):
    code_verifier = generate_code_verifier()
    code_challenge = get_code_challenge(code_verifier)

    async with ClientSession() as session:
        auth_resp = await session.get(
            f"{PROVIDER_URL}/protocol/openid-connect/auth",
            params={
                "protocol": "oauth2",
                "response_type": "code",
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "scope": "openid profile",
                "state": "im_not_a_browser",
                "code_challenge_method": "S256",
                "code_challenge": code_challenge,
            },
        )
        auth_resp.raise_for_status()
        
        form_action_match = re.search(r'<form\s+.*?\s+action="(?P<action>.*?)"', await auth_resp.text())
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
            raise HTTPException(status_code=form_resp.status, detail="Login failed with provided credentials")

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
        
        async with session.get(user_info_url, headers=headers) as user_resp:
            if user_resp.status != 200:
                raise HTTPException(status_code=user_resp.status, detail="User info retrieval failed")

            user_info = await user_resp.json()
            print(user_info)
            user_collection = db_instance.get_collection("users")
            
            existing_user = await user_collection.find_one({"username": user_info["preferred_username"]})
            
            if existing_user:
                return RedirectResponse("/auth/dashboard")
            else:
                return RedirectResponse("/auth/register")
@router.get("/dashboard")
async def dashboard_stub():
    return {"message": "Welcome to the dating service!"}

@router.get("/register")
async def register_stub():
    return {"message": "Complete your registration to start using the dating service."}
