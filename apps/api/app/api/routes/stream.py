import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.capture import Capture
from app.models.workspace import Workspace
from app.schemas.capture import StreamRead


router = APIRouter(
    prefix="/v1/workspaces/{workspace_id}",
    tags=["stream"],
)


@router.get(
    "/stream",
    response_model=StreamRead,
)
def get_stream(
    workspace_id: uuid.UUID,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="一次最多返回的生活记录数量。",
    ),
    db: Session = Depends(get_db),
) -> StreamRead:
    """获取指定生活空间中按发生时间倒序排列的时间流。"""

    # 1.1 验证工作区存在，避免不存在的 ID 返回看似正常的空列表。
    workspace = db.scalar(
        select(Workspace).where(Workspace.id == workspace_id)
    )

    # 1.2 工作区不存在时终止查询。
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生活空间不存在。",
        )

    # 2.1 仅查询当前工作区且尚未软删除的原始记录。
    statement = (
        select(Capture)
        .where(
            Capture.workspace_id == workspace_id,
            Capture.deleted_at.is_(None),
        )
        .order_by(
            Capture.occurred_at.desc(),
            Capture.id.desc(),
        )
        .limit(limit)
    )

    # 2.2 获取按时间倒序排列的记录列表。
    captures = list(db.scalars(statement).all())

    # 3.1 返回时间流；游标分页在后续数据量增大后实现。
    return StreamRead(
        items=captures,
        next_cursor=None,
    )