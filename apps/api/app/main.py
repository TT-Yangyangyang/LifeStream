from fastapi import FastAPI

from app.api.routes.captures import router as captures_router
from app.api.routes.stream import router as stream_router
from app.api.routes.workspaces import router as workspaces_router


app = FastAPI(
    title="LifeStream API",
    version="0.1.0",
    description="LifeStream 的后端 API。",
)

# 1.1 注册工作区、生活记录和时间流路由。
app.include_router(workspaces_router)
app.include_router(captures_router)
app.include_router(stream_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """返回 API 进程当前的基础健康状态。"""

    # 1.1 当前仅确认 API 可响应；后续可增加数据库健康检查。
    return {"status": "ok"}