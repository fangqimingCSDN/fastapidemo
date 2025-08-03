from pydantic import BaseModel


class UserCreateReqSchema(BaseModel):
    email: str
    username: str
    password: str

class UserUpdateReqSchema(BaseModel):
    email: str | None = None
    username: str | None = None
    password: str | None = None

class UserRespSchema(BaseModel):
    id: int
    username: str
    email: str

class UserRegister(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    username: str
    password: str