import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import CaptureVisibility


class CaptureCreate(BaseModel):
    """校验创建一条生活记录时提交的数据。"""

    content: str = Field(
        min_length=1,
        max_length=10_000,
        description="用户主动记录的原始文本内容。",
    )
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="生活记录实际发生的时间，未提供时使用当前 UTC 时间。",
    )
    visibility: CaptureVisibility = Field(
        default=CaptureVisibility.PRIVATE,
        description="记录可见范围，默认仅自己可见。",
    )
    allow_ai_processing: bool = Field(
        default=False,
        description="是否允许 AI 处理当前记录，默认不允许。",
    )

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        """清理生活记录文本，并拒绝空白内容。"""

        # 1.1 去除文本两侧的无意义空白。
        normalized_value = value.strip()

        # 2.1 阻止仅由空格或换行组成的记录。
        if not normalized_value:
            raise ValueError("生活记录内容不能为空。")

        # 3.1 返回清理后的原始记录文本。
        return normalized_value


class CaptureRead(BaseModel):
    """定义单条生活记录接口返回的数据结构。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    content: str
    occurred_at: datetime
    visibility: CaptureVisibility
    allow_ai_processing: bool
    created_at: datetime
    updated_at: datetime


class StreamRead(BaseModel):
    """定义时间流查询接口的分页响应结构。"""

    items: list[CaptureRead]
    next_cursor: None = None

# 目前 next_cursor 固定为 None，只是为后续游标分页预留接口结构。当前 limit 足够完成初始时间流。