from models import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(100), unique=True, index=True)
    username = Column(String(100), unique=True)
    password = Column(String(200))
    role_id = Column(Integer, ForeignKey("roles.id"))  # ⬅️ 外键
    role = relationship("Role", backref="users")  # ⬅️ 一对多


class UserExtension(Base):
    __tablename__ = 'user_extension'
    id = Column(Integer, primary_key=True, index=True)
    university = Column(String(100))

    user_id = Column(Integer, ForeignKey("user.id"))
    # 使用uselist=False，表示和User建立一对一的关系
    user = relationship(User, backref='extension', uselist=False)