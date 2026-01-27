#!/bin/bash
# 批量替换 o11y.Error 为 otelHelper.Errorf 的脚本

echo "开始批量替换 o11y.Error 调用..."

# 查找所有包含 o11y.Error 的 .go 文件(排除已经处理的chat.go和中间件)
find src -name "*.go" -type f ! -name "chat.go" ! -name "o11y_trace.go" ! -path "*/opentelemetry/*" | while read file; do
    if grep -q "o11y.Error" "$file"; then
        echo "处理文件: $file"

        # 备份原文件
        cp "$file" "${file}.backup"

        # 1. 替换 import 语句
        sed -i '/o11y "github.com\/kweaver-ai\/kweaver-go-lib\/observability"/d' "$file"
        # 在合适的位置添加新的 import
        sed -i '/^[[:space:]]*"github.com\/kweaver-ai\/kweaver-go-lib\/rest"/a\	otelHelper "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry"' "$file"

        # 2. 替换 o11y.Error(ctx, fmt.Sprintf(...)) 为 otelHelper.Errorf
        sed -i 's/o11y\.Error(\([^,]*\), fmt\.Sprintf(\([^)]*\)))/otelHelper.Errorf(\1, \2)/g' "$file"

        # 3. 替换 o11y.Error(ctx, "string") 为 otelHelper.Error
        sed -i 's/o11y\.Error(\([^,]*\), "\([^"]*\)")/otelHelper.Error(\1, "\2")/g' "$file"

        echo "✓ 完成处理: $file"
    fi
done

echo ""
echo "批量替换完成!"
echo "建议运行以下命令验证更改:"
echo "  make fmt"
echo "  make ciLint"
echo ""
echo "如果需要恢复,可以使用备份文件(*.backup)"
