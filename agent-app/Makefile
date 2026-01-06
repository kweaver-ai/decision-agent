.DEFAULT_GOAL := all

ciLint:
	golangci-lint run --out-format=colored-line-number ./...
	@echo "ciLint done"

ciLintFix:
	@golangci-lint run --out-format=colored-line-number ./... --fix
	@echo "ciLintFix done"

wsl:
	@wsl --fix ./... >/dev/null 2>&1 ||true
	@echo "wsl done"

fmt:
	@gofumpt -w .
	@goimports -w ./**/*.go
	@echo "fmt done"

all:
	$(MAKE) wsl
	$(MAKE) fmt
	#$(MAKE) ciLintFix

goGenerate:
	go generate ./...

goTest:
	go test -v ./...

add:
	goimports -w ./**/*.go
	git add .

pull:
	git pull origin $(shell git rev-parse --abbrev-ref HEAD)

push:
	git pull origin $(shell git rev-parse --abbrev-ref HEAD)
	git push origin $(shell git rev-parse --abbrev-ref HEAD)

# 文档相关命令
docs-serve:
	@echo "📖 启动文档服务器..."
	@echo "🌐 访问地址: http://0.0.0.0:30050"
	@echo "💡 按 Ctrl+C 停止服务器"
	@echo ""
	uv run mkdocs serve --dev-addr=0.0.0.0:30050