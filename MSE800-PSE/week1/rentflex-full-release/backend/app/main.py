from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import vehicles, auth ,booking, admin_booking, admin_vehicles
import asyncio


app = FastAPI()

# 添加CORS中间件，允许前端开发端口访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 在应用启动时自动创建数据库表结构（如果不存在）
# 注意：这种方法适合开发环境，生产环境建议使用Alembic管理数据库迁移
# 数据填充通过docker-compose中的init.sql完成
@app.on_event("startup")
async def startup_event():
    print("创建数据库表结构...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表结构创建完成！")
    
    # 等待几秒钟确保MySQL容器能够执行初始化脚本
    await asyncio.sleep(3)
    print("应用启动完成，可以接受请求")

# 包含各个路由模块
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(vehicles.router, prefix="/api", tags=["vehicles"])
app.include_router(booking.router, prefix="/api", tags=["booking"])
app.include_router(admin_booking.router, prefix="/api", tags=["admin"])
app.include_router(admin_vehicles.router, prefix="/api", tags=["admin"])

