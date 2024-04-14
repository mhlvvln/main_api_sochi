from __future__ import annotations

import asyncio
import time
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from decode import verify_jwt_token


async def method_protected(token):
    return await verify_jwt_token(token)


async def method_for_role(token, role: str | list):
    user_info = await method_protected(token)
    user_role = user_info['role']
    if isinstance(role, str):
        if user_role == role:
            return user_info
    elif isinstance(role, list):
        if user_role in role:
            return user_info
    raise HTTPException(status_code=401, detail="Метод недоступен для этого пользователя")