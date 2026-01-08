# data-retrieval

用于构建和运行 Decision Agent 数据获取工具的库。

[English](README.md)

## 快速开始

### 安装依赖

```bash
cd data-retrieval
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 启动服务

```bash
# 方式一：直接运行 tool_api_router.py
cd src/data_retrieval/tools
python tool_api_router.py

# 方式二：使用 uvicorn
uvicorn data_retrieval.tools.tool_api_router:DEFAULT_APP --host 0.0.0.0 --port 9100
```

服务启动后访问地址：`http://localhost:9100`

## 脚本工具

### 生成 API 文档

使用 `scripts/generate_api_docs.py` 可以在不启动服务的情况下生成 OpenAPI 3.0 规范的 API 文档。

```bash
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate   # Linux/Mac

# 使用默认参数生成（输出到 api.json，服务地址为 http://data-retrieval:9100）
python scripts/generate_api_docs.py

# 指定输出路径和服务地址
python scripts/generate_api_docs.py ./api.json http://localhost:9100
```

**参数说明：**
- `output_path`：输出文件路径，默认为 `api.json`
- `server_url`：API 文档中的服务地址，默认为 `http://data-retrieval:9100`
