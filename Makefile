.PHONY: all install synth deploy destroy lint format test website-dev website-build

all:
	@echo "Available targets: install, synth, deploy, destroy, lint, format, test, website-dev, website-build"

# Setup
install:
	uv sync --extra dev
	uv run pre-commit install
	npm install
	cd website && npm install

# CDK commands
synth:
	npx cdk synth --profile personal

deploy:
	@# Fetch API URL from existing stack (empty on first deploy —
	@# visitor counter won't work until the second deploy after initial setup).
	$(eval API_URL := $(shell aws cloudformation describe-stacks \
		--stack-name prod-engebreth-website \
		--query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
		--output text --profile personal 2>/dev/null || echo ""))
	@if [ -n "$(API_URL)" ]; then echo "PUBLIC_API_URL=$(API_URL)" > website/.env; fi
	cd website && npm run build
	npx cdk deploy --profile personal --require-approval never

destroy:
	npx cdk destroy --profile personal

# Python tooling
lint:
	uv run ruff check .
	uv run ruff format --check .
	npx biome check lib/ bin/

format:
	uv run ruff check --fix .
	uv run ruff format .
	npx biome check --write lib/ bin/

test:
	uv run pytest
	npm test

# Website
website-dev:
	@echo "Run 'npm run dev' in the website/ directory"

website-build:
	cd website && npm run build
