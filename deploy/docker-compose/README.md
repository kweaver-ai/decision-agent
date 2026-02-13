# Decision Agent Docker Compose 部署指南

本目录包含使用 Docker Compose 部署 Decision Agent 项目的配置文件。

## 服务说明

| 服务名 | 说明 | 端口映射 |
|--------|------|----------|
| mariadb | MariaDB 数据库 | 3306:3306 |
| redis | Redis 缓存 | 6379:6379 |
| agent-backend | 后端服务 (agent-factory, agent-executor, agent-memory) | 13020, 30778, 30790 |
| agent-web | 前端服务 (Nginx) | 1101:1101 |

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

## 快速开始

### 1. 配置环境变量（可选）

```bash
cp .env.example .env
# 根据需要修改 .env 文件中的配置
```

### 2. 构建并启动所有服务

```bash
# 在项目根目录执行
cd deploy/docker-compose
docker-compose up -d --build
```

### 3. 查看服务状态

```bash
docker-compose ps
```

### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f agent-backend
docker-compose logs -f agent-web
```

### 5. 停止服务

```bash
docker-compose down
```

### 6. 停止服务并删除数据卷

```bash
docker-compose down -v
```

## 数据库初始化

数据库会在首次启动时自动初始化，初始化脚本位于 `init.sql`，包括：

- 创建 `adp` 数据库
- 创建 `t_data_agent_memory_history` 表

## 访问服务

| 服务 | 访问地址 |
|------|----------|
| 前端 (Agent Web) | http://localhost:1101/agent-web/my-agents.html |
| 后端 API (Agent Factory) | http://localhost:13020 |
| Agent Executor | http://localhost:30778 |
| Agent Memory | http://localhost:30790 |

## 健康检查

所有服务都配置了健康检查：

```bash
# 检查服务健康状态
docker-compose ps

# 手动检查后端健康
curl http://localhost:13020/health/ready
curl http://localhost:30778/health/ready

# 检查前端健康
curl http://localhost:1101/probe
```

## 故障排查

### 服务无法启动

1. 检查端口是否被占用：
```bash
lsof -i :3306  # MariaDB
lsof -i :6379  # Redis
lsof -i :1101  # Agent Web
lsof -i :13020 # Agent Factory
lsof -i :30778 # Agent Executor
lsof -i :30790 # Agent Memory
```

2. 查看详细日志：
```bash
docker-compose logs [service-name]
```

### 数据库连接失败

确认数据库服务已启动并完成初始化：
```bash
docker-compose logs mariadb
```

### 前端构建失败

确认 `agent-web/dist` 目录存在或使用 Dockerfile 构建

## 开发模式

如需在开发模式下运行（挂载源代码），可以修改 `docker-compose.yaml` 添加 volume 挂载。

## 修改前端后端URL配置

### 1. 修改前端接口的后端 URL

编辑 `docker-compose.yaml`，找到 `agent-web` 服务的 `BACKEND_URL` 环境变量：

```yaml
agent-web:
  environment:
    # 前端请求后端的baseUrl地址
    BACKEND_URL: https://dip.aishu.cn
```

将值改为目标后端地址即可。nginx 会将所有 `/api/` 前缀的请求转发到该地址。

### 2. 修改后重启

> **注意**：不能使用 `docker compose restart`，它只会重启容器但不会重新读取修改后的环境变量。

必须使用 `up` 命令重新创建容器：

```bash
docker compose -f deploy/docker-compose/docker-compose.yaml up -d --no-deps agent-web
```

| 参数        | 说明                                   |
| ----------- | -------------------------------------- |
| `up -d`     | 检测配置变化并重新创建容器（后台运行） |
| `--no-deps` | 仅重启 `agent-web`，不影响其他服务     |

### 3. 验证修改是否生效

查看容器启动日志，确认 `BACKEND_URL` 的值已更新：

```bash
docker logs decision-agent-web --tail 5
```

预期输出：

```
==> BACKEND_URL: https://dip.aishu.cn
==> nginx 配置已生成，启动 nginx...
```

也可以进入容器查看生成的 nginx 配置：

```bash
docker exec decision-agent-web cat /etc/nginx/conf.d/default.conf
```

确认 `proxy_pass` 的值已变为新的地址。

### 4. 前端页面访问地址

前端采用 MPA（多页面应用）架构，每个页面对应一个独立的 HTML 入口。启动后通过 `http://localhost:1101/agent-web/` 前缀访问：

| 页面       | 地址                                                  |
| ---------- | ----------------------------------------------------- |
| 决策智能体 | `http://localhost:1101/agent-web/decision-agent.html` |
| 我的智能体 | `http://localhost:1101/agent-web/my-agents.html`      |
| 智能体模板 | `http://localhost:1101/agent-web/agent-template.html` |
| API 文档   | `http://localhost:1101/agent-web/api.html`            |

> **说明**：端口 `1101` 对应 `docker-compose.yaml` 中 `agent-web` 服务映射的宿主机端口。
