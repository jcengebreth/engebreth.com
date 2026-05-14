.PHONY: all install synth deploy destroy lint format test website-dev website-build

all:
	@echo "Available targets: install, synth, deploy, destroy, lint, format, test, website-dev, website-build"

# Setup
install:
	uv sync --extra dev
	npm install
	cd website && npm install

# CDK commands
synth:
	npx cdk synth --profile personal

deploy:
	@# First deploy to ensure infra exists and get API URL
	npx cdk deploy --profile personal --require-approval never --outputs-file cdk-outputs.json
	@# Extract API URL and build website with it
	$(eval API_URL := $(shell node -e "const d=require('./cdk-outputs.json'); console.log(Object.values(d)[0].ApiUrl)"))
	echo "PUBLIC_API_URL=$(API_URL)" > website/.env
	cd website && npm run build
	@# Redeploy to push updated site assets
	npx cdk deploy --profile personal --require-approval never
	rm -f cdk-outputs.json

destroy:
	npx cdk destroy --profile personal

# Python tooling
lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

# Website
website-dev:
	@echo "Run 'npm run dev' in the website/ directory"

website-build:
	cd website && npm run build
