# Conventions

## Python

- Python 3.14, managed via `.tool-versions` (Lambda runtime: `PYTHON_3_14`)
- Use `pyproject.toml` for all config (no separate requirements.txt, setup.cfg, etc.)
- uv for package management (`uv sync --extra dev` to install, `uv run` to invoke tools)
- Ruff for linting and formatting (line-length 125)
- Tests use pytest + moto for AWS mocking

## CDK

- Constructs go in `infra/constructs/`, stacks in `infra/stacks/`
- Keep stacks thin — compose constructs, don't put resource definitions in stacks
- Config loaded from `config/{stage}.yaml`, not hardcoded
- Use `RemovalPolicy.DESTROY` for dev resources
- Prefer on-demand/serverless billing modes

## Frontend

- Astro static site in `website/`
- Styles scoped to components, global styles in the Base layout
- Static assets in `website/public/`
- `PUBLIC_API_URL` env var for the visitor counter API endpoint

## Git

- Conventional commits: `type(scope): description`
- Don't include AI attribution in commit messages
- Never force push or rewrite history

## CI/CD

- pre-commit runs bandit, detect-secrets, detect-private-key, and detect-aws-credentials on every deploy
- pre-commit is also available locally (`pip install pre-commit`)
