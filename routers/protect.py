# routers/protected.py
from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth.auth_bearer import JWTBearer
from models.users import User
from middlewares.dbs import get_session

router = APIRouter(prefix='/protect', tags=['protect'])

@router.get("/me")
async def get_current_user_info(
    token_data: dict = Security(JWTBearer()),  # 拿到 payload
    db: AsyncSession = Depends(get_session)
):
    # token_data 是解密后的 {"sub": username}
    username = token_data.get("sub")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    return {"error": "User not found"}
