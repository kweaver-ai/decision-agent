# Pre-commit hooks 管理
precommit-install:
	pre-commit install
	@echo "pre-commit hooks installed."

precommit-run-format:
	pre-commit run agent-factory-format-lint --all-files

precommit-run-ut:
	pre-commit run agent-factory-service-ut --all-files

precommit-run-all:
	pre-commit run --all-files

# Act 本地测试 GitHub Actions
act-lint:
	act push -j agent-factory-lint -W .github/workflows/agent-factory-code-check.yml

act-ut:
	act push -j agent-factory-ut -W .github/workflows/agent-factory-code-check.yml

act-all:
	act push -W .github/workflows/agent-factory-code-check.yml
