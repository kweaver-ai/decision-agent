# 基础镜像参数，可通过 --build-arg BASE_IMAGE=xxx 指定
# FROM acr.aishu.cn/as/sailor-python:3.11-base
ARG BASE_IMAGE=python:3.11
FROM ${BASE_IMAGE}

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中
COPY ./ /data_retrieval

# 设置工作目录
WORKDIR /data_retrieval

# 安装Python依赖（合并为单层减少镜像体积）
RUN pip install --no-cache-dir ./tmp/sandbox_env-0.1.0-py3-none-any.whl && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 设置子目录为工作目录
WORKDIR /data_retrieval/src/data_retrieval/tools

# 使端口可用
EXPOSE 9100

# 在容器启动时运行应用
ENTRYPOINT ["uvicorn"]
CMD ["tool_api_router:DEFAULT_APP", "--host", "0.0.0.0", "--port", "9100"]
