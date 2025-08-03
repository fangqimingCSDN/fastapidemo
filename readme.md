# ✅ 方法二：使用 Alembic 进行版本管理（推荐）
    适合生产环境，你可以：

    pip install alembic

    alembic init alembic  # 初始化迁移配置
    修改 alembic/env.py 中：

    from models import Base  # 导入你的模型 Base
    target_metadata = Base.metadata
    然后执行：

    alembic revision --autogenerate -m "create user table"
    alembic upgrade head

# 注意事项--迁移数据  
    ##  Alembic 只支持同步驱动，例如 pymysql、mysqlclient，不支持异步驱动（如 asyncmy、aiomysql）。
    alembic.ini 中写了：

    sqlalchemy.url = mysql+pymysql://root:123456@127.0.0.1:3306/fastapi_sqlalchemy?charset=utf8mb4

    
    bash
    复制
    编辑
    alembic revision --autogenerate -m "create user table"
    如果没有报错，并且生成了迁移文件（.py），再运行：
    
    bash
    复制
    编辑
    alembic upgrade head

# sqlalchemy 文档
    https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html