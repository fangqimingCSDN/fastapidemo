from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from middlewares.dbs import get_session
from permissions.role_permission import PermissionRequired
from models.role import Role, Permission
from models.users import User

router = APIRouter(prefix='/permission', tags=['permission'])

@router.get("/admin/data")
async def get_admin_data(
    _ = Depends(PermissionRequired("admin_access"))  # ⬅️ 权限限制
):
    return {"message": "You are an admin!"}



from sqlalchemy.future import select

async def assign_admin_role_to_user(session: AsyncSession, user_email: str):
    # 查用户
    result = await session.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    if not user:
        raise Exception("User not found")

    # 创建角色和权限
    role = Role(name="admin")
    perm = Permission(name="admin_access")

    # 关联权限到角色
    role.permissions.append(perm)

    # 关联角色到用户
    user.role = role

    # 添加到会话
    session.add_all([role, perm, user])

    # 提交事务
    await session.commit()

    return f"Assigned admin role to {user.email}"


@router.post("/assign-admin")
async def assign_admin(db: AsyncSession = Depends(get_session)):
    message = await assign_admin_role_to_user(db, "1017127423@qq.com")
    return {"message": message}
