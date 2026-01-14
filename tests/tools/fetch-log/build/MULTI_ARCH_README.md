# Fetch Log 工具 - 多架构版本

## 📦 版本说明

本目录包含三个不同架构的 fetch_log 二进制文件：

| 文件名 | 架构 | 平台 | 文件大小 | 说明 |
|--------|------|------|----------|------|
| `fetch_log` | x86_64 | Linux (当前系统) | 8.7M | 未优化，包含调试信息 |
| `fetch_log-linux-amd64` | x86_64 | Linux AMD64 | 6.0M | 优化版本，体积更小 |
| `fetch_log-linux-arm64` | ARM64 | Linux ARM64 | 5.7M | 优化版本，ARM 设备 |

## 🚀 快速开始

### 方法1：自动选择版本

```bash
# 检测系统架构并自动选择合适的版本
uname -m | grep -q "x86_64" && ./build/fetch_log-linux-amd64 --help || ./build/fetch_log-linux-arm64 --help
```

### 方法2：手动选择

#### 对于 AMD64 系统（Intel/AMD 处理器）

```bash
# 使用优化版本（推荐）
./build/fetch_log-linux-amd64 --help

# 收集日志
./build/fetch_log-linux-amd64 --svc_list agent-executor

# AI 分析
./build/fetch_log-linux-amd64 --ai
```

#### 对于 ARM64 系统（ARM 设备、树莓派等）

```bash
# 使用 ARM64 版本
./build/fetch_log-linux-arm64 --help

# 收集日志
./build/fetch_log-linux-arm64 --svc_list agent-executor

# AI 分析
./build/fetch_log-linux-arm64 --ai
```

## 📋 查看系统架构

### Linux 系统

```bash
# 查看系统架构
uname -m

# 输出示例：
# x86_64   - 使用 fetch_log-linux-amd64
# aarch64  - 使用 fetch_log-linux-arm64
# armv7l   - 使用 fetch_log-linux-arm64
```

### 详细系统信息

```bash
# 查看详细的 CPU 信息
lscpu | grep Architecture

# 查看更多系统信息
cat /proc/cpuinfo | grep "model name"
```

## 🛠️ 部署到不同平台

### 部署到 AMD64 服务器

```bash
# 复制文件
scp build/fetch_log-linux-amd64 user@server:/usr/local/bin/fetch_log

# SSH 登录服务器
ssh user@server

# 添加执行权限
chmod +x /usr/local/bin/fetch_log

# 测试
fetch_log --help
```

### 部署到 ARM64 设备（如树莓派）

```bash
# 复制文件
scp build/fetch_log-linux-arm64 pi@raspberrypi:/usr/local/bin/fetch_log

# SSH 登录
ssh pi@raspberrypi

# 添加执行权限
chmod +x /usr/local/bin/fetch_log

# 测试
fetch_log --help
```

## 📊 文件大小对比

| 版本 | 优化前 | 优化后 | 减小比例 |
|------|--------|--------|----------|
| AMD64 | 8.7M | 6.0M | 31% ↓ |
| ARM64 | - | 5.7M | - |

**优化说明**：
- 使用 `-ldflags="-s -w"` 去除调试信息和符号表
- 使用 `-trimpath` 去除文件路径信息
- 使用 `CGO_ENABLED=0` 禁用 CGO，生成静态链接

## ⚡ 性能说明

两个版本在功能上完全相同：
- ✅ 包含所有内置资源文件（模板、文档、知识库）
- ✅ 支持所有功能（日志收集、AI 分析、调试模式）
- ✅ AI 请求日志记录功能
- ✅ 完全独立的二进制文件，无需额外依赖

## 🧪 验证文件完整性

```bash
# 检查文件类型
file build/fetch_log-linux-amd64
file build/fetch_log-linux-arm64

# 验证文件完整性
md5sum build/fetch_log-linux-amd64
md5sum build/fetch_log-linux-arm64

# 测试运行
./build/fetch_log-linux-amd64 --help | head -5
```

## 🔧 重新编译（如需修改源码）

```bash
# 编译 AMD64 版本
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build \
  -ldflags="-s -w" \
  -trimpath \
  -o build/fetch_log-linux-amd64 \
  ./main.go

# 编译 ARM64 版本
GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build \
  -ldflags="-s -w" \
  -trimpath \
  -o build/fetch_log-linux-arm64 \
  ./main.go
```

## 📝 使用示例

### AMD64 系统示例

```bash
# 1. 收集默认服务日志
./build/fetch_log-linux-amd64

# 2. 收集指定服务并预览
./build/fetch_log-linux-amd64 --svc_list agent-executor --preview

# 3. 使用 AI 分析
./build/fetch_log-linux-amd64 --ai

# 4. 更新 Token
./build/fetch_log-linux-amd64 --ai --token "new_token"
```

### ARM64 系统示例

```bash
# 所有命令与 AMD64 相同，只需替换文件名
./build/fetch_log-linux-arm64 --svc_list agent-executor
./build/fetch_log-linux-arm64 --ai
```

## 🎯 推荐使用

- **生产环境**: 使用优化版本（`fetch_log-linux-amd64` 或 `fetch_log-linux-arm64`）
  - 体积更小，传输更快
  - 启动速度相同
  - 功能完全一致

- **开发调试**: 使用未优化版本（`fetch_log`）
  - 包含更多调试信息
  - 方便问题排查

## 💡 常见问题

### Q: 如何选择合适的版本？

```bash
# 自动检测并运行
ARCH=$(uname -m)
case "$ARCH" in
  x86_64|i686|i386)
    ./build/fetch_log-linux-amd64 "$@"
    ;;
  aarch64|armv*)
    ./build/fetch_log-linux-arm64 "$@"
    ;;
  *)
    echo "不支持的架构: $ARCH"
    exit 1
    ;;
esac
```

### Q: 为什么文件大小不同？

- 不同架构的机器码大小不同
- ARM64 指令集更紧凑，文件通常更小
- 优化级别相同，功能完全一致

### Q: 可以在 Windows 上运行吗？

不行，这些是 Linux 版本。Windows 版本需要使用：
```bash
GOOS=windows GOARCH=amd64 go build -o fetch_log.exe ./main.go
```

## 📞 支持

如有问题，请联系开发团队。
