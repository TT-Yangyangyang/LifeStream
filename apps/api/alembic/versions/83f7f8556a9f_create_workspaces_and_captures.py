"""Create workspaces and captures.

Revision ID: 83f7f8556a9f
Revises:
Create Date: 2026-08-05 11:30:14.120468
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# 1.1 标识当前迁移及其前置迁移版本。
revision: str = "83f7f8556a9f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 1.2 定义 Capture 可见范围枚举，供升级和降级操作复用。
capture_visibility = postgresql.ENUM(
    "private",
    "friends",
    name="capture_visibility",
    create_type=False,
)


def upgrade() -> None:
    """创建工作区和生活记录的初始数据库结构。"""

    # 1.1 在 PostgreSQL 中创建 Capture 的可见范围枚举类型。
    capture_visibility.create(op.get_bind(), checkfirst=True)

    # 2.1 创建工作区表，作为个人生活记录的数据隔离边界。
    op.create_table(
        "workspaces",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3.1 创建文本生活记录表，并通过外键归属到工作区。
    op.create_table(
        "captures",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "visibility",
            capture_visibility,
            server_default=sa.text("'private'::capture_visibility"),
            nullable=False,
        ),
        sa.Column(
            "allow_ai_processing",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 4.1 为按工作区查询个人时间流创建索引。
    op.create_index(
        op.f("ix_captures_workspace_id"),
        "captures",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    """按依赖顺序删除初始工作区和生活记录结构。"""

    # 1.1 先删除依赖于工作区的 Capture 查询索引和数据表。
    op.drop_index(
        op.f("ix_captures_workspace_id"),
        table_name="captures",
    )
    op.drop_table("captures")

    # 2.1 删除不再被 Capture 使用的工作区表。
    op.drop_table("workspaces")

    # 3.1 最后删除 PostgreSQL 可见范围枚举类型。
    capture_visibility.drop(op.get_bind(), checkfirst=True)
