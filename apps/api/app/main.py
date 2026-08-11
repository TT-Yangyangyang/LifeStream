from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.captures import router as captures_router
from app.api.routes.stream import router as stream_router
from app.api.routes.workspaces import router as workspaces_router
from app.core.config import settings


# 1.1 将逗号分隔的环境变量转换为允许跨域访问的来源列表。
allowed_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app = FastAPI(
    title="LifeStream API",
    version="0.1.0",
    description="LifeStream 的后端 API。",
)

# 2.1 允许本地 Next.js 开发服务器调用 FastAPI。
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# 3.1 注册当前 v0.1.0 的工作区、生活记录和时间流接口。
app.include_router(workspaces_router)
app.include_router(captures_router)
app.include_router(stream_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """返回 API 进程当前的基础健康状态。"""

    # 1.1 当前仅确认 API 可响应，后续增加数据库健康检查。
    return {"status": "ok"}