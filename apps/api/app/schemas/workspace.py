import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorkspaceCreate(BaseModel):
    """校验创建生活空间时提交的数据。"""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="生活空间名称。",
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """清理生活空间名称，并拒绝空白名称。"""

        # 1.1 去除用户输入名称两侧的空白字符。
        normalized_value = value.strip()

        # 2.1 阻止仅由空格组成的生活空间名称。
        if not normalized_value:
            raise ValueError("生活空间名称不能为空。")

        # 3.1 返回清理后的名称供路由保存。
        return normalized_value


class WorkspaceRead(BaseModel):
    """定义生活空间接口返回的数据结构。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime