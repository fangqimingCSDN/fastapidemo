from fastapi.requests import Request
from models import AsyncSessionFactory


async def create_session_middleware(request: Request, call_next):
    # 1. 请求到达视图之前执行的
    session = AsyncSessionFactory()
    request.state.session = session
    # setattr(request.state, 'session', session)
    response = await call_next(request)
    # 2. 响应返回给浏览器之前执行的
    await session.close()
    return response


async def get_session():
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()