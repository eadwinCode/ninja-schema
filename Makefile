.PHONY: help docs
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Removing cached python compiled files
	find . -name \*pyc  | xargs  rm -fv
	find . -name \*pyo | xargs  rm -fv
	find . -name \*~  | xargs  rm -fv
	find . -name __pycache__  | xargs  rm -rfv
	find . -name .ruff_cache  | xargs  rm -rfv

install:clean ## Install dependencies
	flit install --deps develop --symlink
	pre-commit install -f

lint:fmt ## Run code linters
	ruff check ninja_schema tests
	mypy  ninja_schema

fmt format:clean ## Run code formatters
	ruff format ninja_schema tests
	ruff check --fix ninja_schema tests

test:clean ## Run tests
	pytest .

test-cov:clean ## Run tests with coverage
	pytest --cov=ninja_schema --cov-report term-missing tests
