"""FastAPI dependencies — JWT authentication."""

import uuid

import jwt
from fastapi import Header, HTTPException

from config import JWT_SECRET_KEY
from db import get_pool


async def get_current_user(authorization: str | None = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.removeprefix("Bearer ")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email, name, picture_url, credits FROM public.users WHERE id = $1",
            uuid.UUID(user_id),
        )

    if not row:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "id": str(row["id"]),
        "email": row["email"],
        "name": row["name"],
        "picture_url": row["picture_url"],
        "credits": row["credits"],
    }
