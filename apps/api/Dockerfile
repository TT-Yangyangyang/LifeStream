FROM python:3.12-slim

# 1.1 避免生成无用字节码，并让日志直接输出到容器标准输出。
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 2.1 统一容器内 API 的工作目录和导入根目录。
WORKDIR /app

# 3.1 先复制依赖清单，利用 Docker 构建缓存加快后续构建。
COPY requirements.txt ./

# 3.2 使用国内 PyPI 镜像安装 API 和数据库迁移依赖。
RUN pip install \
    --no-cache-dir \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    -r requirements.txt

# 4.1 复制 API 源码和数据库迁移配置。
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

# 5.1 声明 FastAPI 容器内部服务端口。
EXPOSE 8000

# 6.1 启动 API；生产容器不使用 --reload。
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]