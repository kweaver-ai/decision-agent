# Docker Compose 部署指南

## 1. 修改前端接口的后端 URL

编辑 `docker-compose.yaml`，找到 `agent-web` 服务的 `BACKEND_URL` 环境变量：

```yaml
agent-web:
  environment:
    # 前端请求后端的baseUrl地址
    BACKEND_URL: https://dip.aishu.cn
```

将值改为目标后端地址即可。nginx 会将所有 `/api/` 前缀的请求转发到该地址。

## 2. 修改后重启

> **注意**：不能使用 `docker compose restart`，它只会重启容器但不会重新读取修改后的环境变量。

必须使用 `up` 命令重新创建容器：

```bash
docker compose -f deploy/docker-compose/docker-compose.yaml up -d --no-deps agent-web
```

| 参数        | 说明                                   |
| ----------- | -------------------------------------- |
| `up -d`     | 检测配置变化并重新创建容器（后台运行） |
| `--no-deps` | 仅重启 `agent-web`，不影响其他服务     |

## 3. 验证修改是否生效

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

## 4. 前端页面访问地址

前端采用 MPA（多页面应用）架构，每个页面对应一个独立的 HTML 入口。启动后通过 `http://localhost:1101/agent-web/` 前缀访问：

| 页面       | 地址                                                  |
| ---------- | ----------------------------------------------------- |
| 决策智能体 | `http://localhost:1101/agent-web/decision-agent.html` |
| 我的智能体 | `http://localhost:1101/agent-web/my-agents.html`      |
| 智能体模板 | `http://localhost:1101/agent-web/agent-template.html` |
| API 文档   | `http://localhost:1101/agent-web/api.html`            |

> **说明**：端口 `1101` 对应 `docker-compose.yaml` 中 `agent-web` 服务映射的宿主机端口。
