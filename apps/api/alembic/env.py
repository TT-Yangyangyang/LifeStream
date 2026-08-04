from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base
from app.models.capture import Capture
from app.models.workspace import Workspace

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url)

# 1.1 显式导入模型后，将已注册的表结构提供给 Alembic 比对。
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """使用数据库 URL 生成可审核的离线迁移 SQL。"""

    # 1.1 读取统一注入到 Alembic 配置中的数据库连接地址。
    url = config.get_main_option("sqlalchemy.url")

    # 2.1 配置目标元数据和 PostgreSQL 方言，生成内嵌参数的 SQL。
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "pyformat"},
        compare_type=True,
    )

    # 3.1 在迁移事务中输出迁移操作。
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """连接数据库并执行待应用的迁移版本。"""

    # 1.1 根据 Alembic 配置创建不复用连接的迁移引擎。
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 2.1 打开连接，并将数据库事务交给 Alembic 管理。
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        # 2.2 在单个事务中应用当前待执行的迁移脚本。
        with context.begin_transaction():
            context.run_migrations()

# 3.1 根据命令是否要求 SQL 输出，选择离线或在线迁移模式。
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
