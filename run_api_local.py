import os
import subprocess
import sys
from pathlib import Path


def load_local_environment(env_file: Path) -> None:
    """读取本地私有环境变量，并注入当前启动进程。"""

    # 1.1 确认本地环境变量文件存在。
    if not env_file.is_file():
        raise FileNotFoundError(
            f"未找到本地环境变量文件：{env_file}"
        )

    # 2.1 逐行读取配置，忽略空行和注释。
    for line in env_file.read_text(encoding="utf-8").splitlines():
        normalized_line = line.strip()

        if not normalized_line or normalized_line.startswith("#"):
            continue

        # 2.2 仅处理 KEY=VALUE 格式的环境变量。
        key, separator, value = normalized_line.partition("=")

        if separator:
            os.environ[key.strip()] = value.strip()

    # 3.1 阻止缺少数据库地址时错误启动 API。
    if not os.environ.get("DATABASE_URL"):
        raise ValueError(".env.local 中缺少 DATABASE_URL。")


def main() -> None:
    """加载开发配置后，使用当前虚拟环境启动 FastAPI。"""

    # 1.1 定位项目根目录和本地私密环境变量文件。
    project_root = Path(__file__).resolve().parent
    env_file = project_root / ".env.local"

    # 1.2 加载服务器 PostgreSQL 的连接地址。
    load_local_environment(env_file)

    # 2.1 使用运行当前脚本的解释器启动 Uvicorn。
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--port",
        "8000",
        "--app-dir",
        "apps/api",
    ]

    # 3.1 在项目根目录运行，并将进程退出码传递给系统。
    result = subprocess.run(
        command,
        cwd=project_root,
        env=os.environ.copy(),
        check=False,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()