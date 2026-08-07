import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.capture import Capture
from app.models.workspace import Workspace
from app.schemas.capture import CaptureCreate, CaptureRead


router = APIRouter(
    prefix="/v1/workspaces/{workspace_id}",
    tags=["captures"],
)


@router.post(
    "/captures",
    response_model=CaptureRead,
    status_code=status.HTTP_201_CREATED,
)
def create_capture(
    workspace_id: uuid.UUID,
    payload: CaptureCreate,
    db: Session = Depends(get_db),
) -> Capture:
    """在指定生活空间中创建一条原始生活记录。"""

    # 1.1 验证 URL 中指定的生活空间存在。
    workspace = db.scalar(
        select(Workspace).where(Workspace.id == workspace_id)
    )

    # 1.2 阻止向不存在的生活空间写入记录。
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="生活空间不存在。",
        )

    # 2.1 使用已校验的请求数据构造原始 Capture。
    capture = Capture(
        workspace_id=workspace_id,
        content=payload.content,
        occurred_at=payload.occurred_at,
        visibility=payload.visibility,
        allow_ai_processing=payload.allow_ai_processing,
    )

    # 2.2 写入记录；是否分享给好友仍由 visibility 明确控制。
    db.add(capture)
    db.commit()

    # 3.1 刷新对象以获取数据库生成的字段。
    db.refresh(capture)

    # 3.2 返回新建的原始生活记录。
    return capture