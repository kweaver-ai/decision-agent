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

ut:
	rm -rf coverage_report
	mkdir coverage_report
	go generate ./...
	go test -v -coverprofile=coverage_report/cover.out  ./... 2>&1 | go-junit-report > coverage_report/lint_report.xml
	gocov convert coverage_report/cover.out | gocov-xml > coverage_report/coverage.xml
	gocov convert coverage_report/cover.out | gocov-html > coverage_report/coverage.html

goGenerate:
	go generate ./...

goTest:
	go test -v $$(go list ./... | grep -vE '/[^/]*mock[^/]*($$|/)')

# Swagger 文档生成
gen-swag:
	swag init -g main.go -o docs --parseDependency

# 查看 Swagger 文档（需要先启动服务）
view-swag:
	@echo "Swagger UI: http://localhost:30777/swagger/index.html"

# 清理并重新生成 Swagger
clean-swag:
	rm -rf docs
	$(MAKE) gen-swag

add:
	goimports -w ./**/*.go
	git add .

pull:
	git pull origin $(shell git rev-parse --abbrev-ref HEAD)

push:
	git pull origin $(shell git rev-parse --abbrev-ref HEAD)
	git push origin $(shell git rev-parse --abbrev-ref HEAD)


