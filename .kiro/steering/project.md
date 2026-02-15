# Project: engebreth.com

Personal portfolio website deployed to a personal AWS account.

## Architecture

- Static site (Astro) served via S3 + CloudFront
- Visitor counter: Lambda (Python 3.13) + DynamoDB (on-demand) + API Gateway
- DNS: Route53 + ACM
- Email: ImprovMX email forwarding (jerad@engebreth.com → Gmail)
- IaC: AWS CDK (Python)

## Project Structure

- `app.py` — CDK app entrypoint
- `infra/` — CDK infrastructure (stacks and constructs)
- `website/` — Astro frontend (build output goes to `website/dist/`)
- `functions/` — Lambda function code
- `config/` — Environment config YAML files (loaded by app.py)
- `tests/` — Python tests (pytest + moto)

## Key Decisions

- Cost-conscious: everything stays in free tier or near-zero cost
- No containers — static S3 + CloudFront is cheapest for a personal site
- DynamoDB on-demand (PAY_PER_REQUEST) not provisioned
- Config lives in `config/*.yaml`, not in `cdk.json` context
- Ruff for all Python linting/formatting (no black, flake8, isort)
- `.tool-versions` for runtime versions (asdf/mise), `.envrc` for direnv

## Commands

- `make install` — install all Python and Node dependencies
- `make lint` / `make format` — ruff check and format
- `make test` — pytest
- `make deploy` — build website + cdk deploy
- `cd website && npm run dev` — local Astro dev server
