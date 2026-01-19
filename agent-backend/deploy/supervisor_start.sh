#!/bin/bash
# Supervisor 启动脚本 - 启动所有 agent-backend 服务

set -e

echo "==================================="
echo "启动 agent-backend 服务"
echo "==================================="
echo ""
echo "服务列表:"
echo "  1. agent-executor (端口: 6483)"
echo "   2. agent-memory (端口: 6482)"
echo "  3. agent-factory (端口: 6481)"
echo ""
echo "使用 supervisor 管理所有服务进程"
echo ""

# 输出环境信息
echo "环境变量:"
echo "  UID: ${UID:-1000}"
echo "  GID: ${GID:-1000}"
echo ""

# 检查是否需要显示配置
if [ "${SHOW_CONFIG:-false}" = "true" ]; then
    echo "supervisor 配置文件: /etc/supervisor/conf.d/supervisord.conf"
    echo ""
    echo "服务配置:"
    supervisorctl -c /etc/supervisor/conf.d/supervisord.conf show agent-executor
    echo ""
    supervisorctl -c /etc/supervisor/conf.d/supervisord.conf show agent-memory
    echo ""
    supervisorctl -c /etc/supervisor/conf.d/supervisord.conf show agent-factory
    echo ""
fi

# 启动 supervisor
echo "启动 supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf -nodaemon
