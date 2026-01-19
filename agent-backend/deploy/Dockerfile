ARG buildImage=acr.aishu.cn/dip/py.build:3.10.18:20250109211000
ARG baseImage=acr.aishu.cn/public/ubuntu:22.04.20241202
ARG goBuildImage=acr.aishu.cn/dip/go.build:1.21.9.3.8.2024120203

# ==================== 构建阶段：agent-executor ====================
FROM ${buildImage} AS builder-executor

WORKDIR /build

# 复制 agent-executor 的源代码和配置
COPY agent-executor/.netrc /root/.netrc
COPY agent-executor/id_rsa /root/.ssh/id_rsa
COPY agent-executor/agent-executor.spec /build/agent-executor.spec
COPY agent-executor/pyproject.toml /build/pyproject.toml
COPY agent-executor/app /build/app
COPY agent-executor/main.py /build/main.py
COPY agent-executor/mq-sdk-lib /build/mq-sdk-lib
COPY agent-executor/last_commit_info.txt /build/last_commit_info.txt

# 安装依赖并构建 agent-executor
RUN set -ex; \
    ssh-keyscan -t rsa devops.aishu.cn >> /root/.ssh/known_hosts; \
    cd /build; \
    uv sync; \
    uv run pyinstaller agent-executor.spec;

# ==================== 构建阶段：agent-memory ====================
FROM ${buildImage} AS builder-memory

WORKDIR /build

# 复制 agent-memory 的源代码和配置
COPY agent-memory/agent-memory.spec /build/agent-memory.spec
COPY agent-memory/requirements.txt /build/requirements.txt
COPY agent-memory/mem0 /build/mem0
COPY agent-memory/src /build/src

# 安装依赖并构建 agent-memory
RUN set -ex; \
    cd /build; \
    export PATH=/export/servers/python3.9/bin:$PATH; \
    python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade --no-cache-dir -r requirements.txt; \
    pyinstaller agent-memory.spec;

# ==================== 构建阶段：agent-factory (Go) ====================
FROM ${goBuildImage} AS builder-factory

WORKDIR /build

# 复制 agent-factory 的源代码和配置
COPY agent-factory/go.mod /build/
COPY agent-factory/go.sum /build/
COPY agent-factory/Makefile /build/
COPY agent-factory/main.go /build/

# 构建 agent-factory Go 二进制文件
RUN set -ex; \
    cd /build && \
    go build -o agent-factory . && \
    chmod +x agent-factory;

# ==================== 生产阶段：supervisor 管理三个服务 ====================
FROM ${baseImage} AS prod

ARG UID=1000
ARG GID=1000

# 安装 supervisor 和必要的工具
RUN apt-get update && apt-get install -y \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN groupadd -r -g $GID aishu && \
    useradd -r -u $UID -g $GID aishu

WORKDIR /app

# 从构建阶段复制已构建的二进制文件
COPY --from=builder-executor --chown=$UID:$GID /build/dist/agent-executor /app/agent-executor
COPY --from=builder-memory --chown=$UID:$GID /build/dist/agent-memory /app/agent-memory

# 设置权限
RUN chown -R $UID:$GID /app

# 复制 supervisor 配置文件
COPY --chown=$UID:$GID deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --chown=$UID:$GID deploy/supervisor_start.sh /app/supervisor_start.sh

# 切换到非 root 用户
USER $UID

# 暴露端口
# agent-executor: 6483
# agent-memory: 6482
EXPOSE 6483 6482

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:6483/api/agent-executor/v1/health/ready || exit 1

# 使用 supervisor 启动所有服务
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf", "-nodaemon"]
