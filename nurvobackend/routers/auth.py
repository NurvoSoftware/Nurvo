"""Google OAuth 2.0 login flow, email/password login, and JWT token endpoints."""

import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from pydantic import BaseModel

from config import (
    FRONTEND_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    JWT_EXPIRE_DAYS,
    JWT_SECRET_KEY,
)
from db import get_pool
from routers.deps import get_current_user

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class _LoginRequest(BaseModel):
    email: str
    password: str

router = APIRouter(prefix="/auth", tags=["auth"])

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@router.get("/google/login")
async def google_login() -> RedirectResponse:
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    return RedirectResponse(f"{_GOOGLE_AUTH_URL}?{urlencode(params)}")


@router.get("/google/callback")
async def google_callback(code: str = Query(...)) -> RedirectResponse:
    async with httpx.AsyncClient() as client:
        # Exchange authorization code for access token
        token_resp = await client.post(
            _GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code")

        access_token = token_resp.json().get("access_token")

        # Fetch user profile from Google
        user_resp = await client.get(
            _GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Google user info")

        user_info = user_resp.json()

    google_id: str = user_info["id"]
    email: str = user_info.get("email", "")
    name: str | None = user_info.get("name")
    picture_url: str | None = user_info.get("picture")

    # Upsert user — create on first login, update name/picture/last_login on return
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO public.users (id, email, name, picture_url, google_id, created_at, last_login_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            ON CONFLICT (google_id) DO UPDATE SET
                name           = EXCLUDED.name,
                picture_url    = EXCLUDED.picture_url,
                last_login_at  = NOW()
            RETURNING id, email
            """,
            uuid.uuid4(),
            email,
            name,
            picture_url,
            google_id,
        )

    user_id = str(row["id"])

    # Issue JWT
    exp = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    token = jwt.encode(
        {"sub": user_id, "email": email, "exp": exp},
        JWT_SECRET_KEY,
        algorithm="HS256",
    )

    # Redirect to frontend; token in hash so it is never sent to any server
    return RedirectResponse(f"{FRONTEND_URL}/auth/callback#token={token}")


@router.post("/login")
async def email_login(body: _LoginRequest) -> dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email, name, picture_url, password_hash FROM public.users WHERE email = $1",
            body.email,
        )

    if not row or not row["password_hash"]:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    if not _pwd_context.verify(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE public.users SET last_login_at = NOW() WHERE id = $1", row["id"]
        )

    user_id = str(row["id"])
    exp = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    token = jwt.encode(
        {"sub": user_id, "email": row["email"], "exp": exp},
        JWT_SECRET_KEY,
        algorithm="HS256",
    )
    return {"access_token": token}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user
