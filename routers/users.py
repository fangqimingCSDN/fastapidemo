from fastapi import APIRouter
from models.users import User
from models import AsyncSessionFactory
from schemas.users import UserCreateReqSchema, UserRespSchema, UserUpdateReqSchema
from fastapi.exceptions import HTTPException
from models import AsyncSession
from fastapi import Depends
import sqlalchemy
from fastapi.requests import Request
from sqlalchemy import delete, select, update
from typing import List, Dict
from sqlalchemy import or_


router = APIRouter(prefix='/user', tags=['user'])


@router.post('/add', response_model=UserRespSchema)
async def add_user(user_data: UserCreateReqSchema):
    # 1. 不用异步上下文管理器
    # session = AsyncSessionFactory()
    #
    # # 以下代码，会自动创建一个事务
    # try:
    #     user = User(email=user_data.email, username=user_data.username, password=user_data.password)
    #     session.add(user)
    #     await session.commit()
    #     await session.refresh(user, attribute_names=['id'])
    # except sqlalchemy.exc.IntegrityError as e:
    #     await session.rollback()
    #     raise HTTPException(status_code=400, detail='用户名或邮箱已经存在！')
    # await session.close()
    # return user

    # 2. 用上下文管理器
    async with AsyncSessionFactory() as session:
        # try:
        #     user = User(email=user_data.email, username=user_data.username, password=user_data.password)
        #     session.add(user)
        #     await session.commit()
        # except sqlalchemy.exc.IntegrityError as e:
        #     await session.rollback()
        #     raise HTTPException(status_code=400, detail='用户名或邮箱已经存在！')

        try:
            # 手动开启事务，在上下文中，不需要写commit操作，退出上下文后，会自动执行commit
            async with session.begin():
                user = User(email=user_data.email, username=user_data.username, password=user_data.password)
                session.add(user)
        except Exception as e:
            # 如果抛出异常，异步上下文管理器就已经执行了回滚的操作
            raise HTTPException(status_code=400, detail='用户名或邮箱已经存在1111！')
    return user


async def get_session():
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()


@router.post('/add/depends', response_model=UserRespSchema)
async def add_user_depends(
        user_data: UserCreateReqSchema,
        session: AsyncSession=Depends(get_session)
):
    try:
        async with session.begin():
            user = User(email=user_data.email, username=user_data.username, password=user_data.password)
            session.add(user)
        return user
    except Exception:
        raise HTTPException(status_code=400, detail='用户名或邮箱已经存在222！')


@router.post('/add/middleware', response_model=UserRespSchema)
async def add_user_middleware(request: Request, user_data: UserCreateReqSchema):
    session = request.state.session
    try:
        async with session.begin():
            user = User(email=user_data.email, username=user_data.username, password=user_data.password)
            session.add(user)
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail='用户名或邮箱已经存在333！')


@router.delete('/delete/{user_id}')
async def delete_user(user_id: int, request: Request):
    session = request.state.session
    try:
        async with session.begin():
            sql = delete(User).where(User.id==user_id)
            await session.execute(sql)
        return {"message": "删除成功！"}
    except Exception as e:
        raise HTTPException(status_code=400, detail='删除失败！')

# 查找一条数据
# @router.get('/select/{user_id}')
@router.get('/select/{user_id}', response_model=UserRespSchema)
async def select_user_by_id(user_id: int, request: Request):
    session = request.state.session
    async with session.begin():
        stmt = select(User.id, User.username, User.email).where(User.id==user_id)
        query = await session.execute(stmt)
        row = query.one()
        # print(type(row))
        # print(row)
        # print(row._asdict())
        return row._asdict()

@router.get('/select', response_model=List[UserRespSchema])
async def select_user(request: Request, q: str):
    session = request.state.session
    async with session.begin():
        stmt = select(User.id, User.username, User.email).where(
            or_(User.username.contains(q), User.email.contains(q))
        ).offset(1).limit(2).order_by(User.id.desc())
        query = await session.execute(stmt)
        # rows = []
        # for row in query:
        #     rows.append(row._asdict())
        rows = [row._asdict() for row in query]
        return rows

@router.put('/update/{user_id}')
async def update_user(user_id: int, request: Request, user_data: UserUpdateReqSchema):
    session = request.state.session
    async with session.begin():
        fields: Dict = {}
        if user_data.email:
            fields['email'] = user_data.email
        if user_data.username:
            fields['username'] = user_data.username
        if user_data.password:
            fields['password'] = user_data.password
        stmt = update(User).where(User.id==user_id).values(**fields)
        await session.execute(stmt)
    return {"message": "数据更新成功！"}


@router.put('/update/cp/{user_id}', response_model=UserRespSchema)
async def update_cp_user(request: Request, user_id: int, user_data: UserUpdateReqSchema):
    session = request.state.session
    async with session.begin():
        # select(User)：会把满足条件的所有列都提取出来，形成一个User的ORM对象
        query = await session.execute(select(User).where(User.id==user_id))
        # [(User1, ), (User2, ), (User3, )]
        # scalars：将上面的结构，变为：[User1, User2, User3]
        user = query.scalars().first()
        user.email = user_data.email or user.email
        user.username = user_data.username or user.username
        # session.commit()
    return user
