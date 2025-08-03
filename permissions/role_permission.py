from fastapi import Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from middlewares.dbs import get_session
from auth.auth_bearer import JWTBearer
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.role import Role

async def get_current_user(
    token_data: dict = Depends(JWTBearer()),
    db: AsyncSession = Depends(get_session)
) -> User:
    username = token_data.get("sub")
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.role).selectinload(Role.permissions)
        )
        .where(User.username == username)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 权限校验依赖
def PermissionRequired(permission_name: str):
    async def checker(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)
    ):
        if not user.role:
            raise HTTPException(status_code=403, detail="No role assigned")

        # 查询权限
        await db.refresh(user.role)  # 刷新角色中的 permissions 关系
        permissions = [p.name for p in user.role.permissions]

        if permission_name not in permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission_name}' required"
            )
    return checker
