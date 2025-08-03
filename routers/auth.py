from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from middlewares.dbs import get_session
from models.users import User
from schemas.users import UserRegister, UserLogin
from auth.auth_handler import hash_password, verify_password, create_access_token
from sqlalchemy.future import select


router = APIRouter(prefix='/auth', tags=['auth'])

@router.post("/register")
async def register(user: UserRegister, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user = User(email=user.email, username=user.username, password=hash_password(user.password))
    db.add(db_user)
    await db.commit()
    return {"msg": "User created"}

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}
