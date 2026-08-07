import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead


router = APIRouter(
    prefix="/v1/workspaces",
    tags=["workspaces"],
)


@router.post(
    "",
    response_model=WorkspaceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
) -> Workspace:
    """创建一个用于隔离个人生活数据的工作区。"""

    # 1.1 根据已校验的请求内容构造工作区实体。
    workspace = Workspace(name=payload.name)

    # 2.1 将新工作区写入当前数据库事务。
    db.add(workspace)
    db.commit()

    # 3.1 刷新对象以获取数据库生成的 ID 和时间字段。
    db.refresh(workspace)

    # 4.1 返回新建的生活空间。
    return workspace


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceRead,
)
def get_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Workspace:
    """按唯一 ID 获取一个生活空间。"""

    # 1.1 查询指定 ID 的工作区。
    workspace = db.scalar(
        select(Workspace).where(Workspace.id == workspace_id)
    )

    # 2.1 不存在时返回统一的资源不存在响应。
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生活空间不存在。",
        )

    # 3.1 返回当前工作区信息。
    return workspace