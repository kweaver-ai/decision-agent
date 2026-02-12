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
| 前端 (Agent Web) | http://localhost:1101/agent-web |
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
