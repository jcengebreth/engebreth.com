# Project: engebreth.com

Personal portfolio website deployed to a personal AWS account.

## Architecture

- Static site (Astro) served via S3 + CloudFront
- Visitor counter: Lambda (Python 3.14) + DynamoDB (on-demand) + API Gateway
- DNS: Route53 + ACM
- Email: ImprovMX email forwarding (jerad@engebreth.com → Gmail)
- IaC: AWS CDK (TypeScript)

## Project Structure

- `bin/engebreth.ts` — CDK app entrypoint
- `lib/stacks/` — CDK stacks (TypeScript)
- `lib/constructs/` — CDK constructs (TypeScript)
- `src/functions/` — Lambda function code (Python)
- `website/` — Astro frontend (build output goes to `website/dist/`)
- `config/` — Environment config YAML files (loaded by app.py)
- `tests/` — Python tests (pytest + moto)

## AWS

- Region: `us-east-1`
- Stack naming: `{stage}-engebreth-website` (e.g. `prod-engebreth-website`)
- Credentials via OIDC role assumption (`AWS_ROLE_ARN` secret in GitHub Actions)

## Key Decisions

- Cost-conscious: everything stays in free tier or near-zero cost
- No containers — static S3 + CloudFront is cheapest for a personal site
- DynamoDB on-demand (PAY_PER_REQUEST) not provisioned
- Config lives in `config/*.yaml`, not in `cdk.json` context
- Ruff for all Python linting/formatting (no black, flake8, isort)
- `.tool-versions` for runtime versions (mise), `.mise.toml` for mise settings (Python venv auto-creation)

## Commands

- `make install` — install all Python and Node dependencies
- `make lint` / `make format` — ruff check and format
- `make test` — pytest
- `make deploy` — build website + cdk deploy
- `cd website && npm run dev` — local Astro dev server
