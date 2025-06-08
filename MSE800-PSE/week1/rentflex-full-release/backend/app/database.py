import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 加载 .env.dev 文件
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.dev'))
DATABASE_URL = (
    f"mysql+aiomysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
# 从环境变量中读取数据库 URL


engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# FastAPI 依赖，用来获取数据库会话
async def get_session():
    async with async_session() as session:
        yield session
