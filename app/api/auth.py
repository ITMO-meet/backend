import re
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.utils.db import db_instance
from aiohttp import ClientSession
from hashlib import sha256
from base64 import urlsafe_b64encode
import os

router = APIRouter()

CLIENT_ID = "student-personal-cabinet"
REDIRECT_URI = "https://my.itmo.ru/login/callback"
PROVIDER_URL = "https://id.itmo.ru/auth/realms/itmo"

def generate_code_verifier():
    code_verifier = urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    return re.sub("[^a-zA-Z0-9]+", "", code_verifier)

def get_code_challenge(code_verifier: str):
    code_challenge_bytes = sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = urlsafe_b64encode(code_challenge_bytes).decode("utf-8")
    return code_challenge.replace("=", "")

code_verifier = generate_code_verifier()
code_challenge = get_code_challenge(code_verifier)

@router.get("/login")
async def login():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid profile",
        "state": "random_state",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{PROVIDER_URL}/protocol/openid-connect/auth?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(code: str):
    async with ClientSession() as session:
        token_url = f"{PROVIDER_URL}/protocol/openid-connect/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        }

        async with session.post(token_url, data=data) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail="Token exchange failed")

            token_data = await resp.json()
            access_token = token_data.get("access_token")

            user_info_url = f"{PROVIDER_URL}/protocol/openid-connect/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with session.get(user_info_url, headers=headers) as user_resp:
                if user_resp.status != 200:
                    raise HTTPException(status_code=user_resp.status, detail="User info retrieval failed")
                
                user_info = await user_resp.json()
                user_collection = db_instance.get_collection("users")
                
                existing_user = await user_collection.find_one({"username": user_info["preferred_username"]})
                
                if existing_user:
                    return RedirectResponse("/dashboard")
                
                return RedirectResponse("/register")

@router.get("/register")
async def register_stub():
    return {"message": "registration placeholder"}

@router.get("/dashboard")
async def dashboard_stub():
    return {"message": "dating dashboard placeholder"}
