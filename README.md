# engebreth.com

Personal portfolio website built with Astro and deployed to AWS using CDK.

## Architecture

- **Frontend**: Astro static site → S3 + CloudFront
- **Backend**: Lambda (Python 3.14) + DynamoDB (on-demand) + API Gateway
- **DNS**: Route53 + ACM
- **Email**: Cloudflare Email Routing
- **CI/CD**: GitHub Actions with OIDC authentication
- **IaC**: AWS CDK (TypeScript)

## Project Structure

```
├── bin/
│   └── engebreth.ts        # CDK app entrypoint
├── lib/
│   ├── stacks/             # CDK stacks
│   └── constructs/         # CDK constructs
├── src/
│   └── functions/          # Lambda functions (Python)
│       └── visitor_counter/
├── website/                # Astro frontend
│   ├── src/
│   │   ├── layouts/
│   │   └── pages/
│   └── public/
├── tests/                  # Python tests (pytest)
└── config/                 # Environment config YAML files
```

## Quick Start

```bash
make install        # install Python + Node dependencies
make test           # run tests
make lint           # ruff check + format check
make deploy         # build website + cdk deploy
```

For local website development: `cd website && npm run dev`

## Detailed Setup

See [docs/setup.md](docs/setup.md) for first-time setup, CI/CD configuration, and deployment instructions.

## Tooling

- Python 3.14 / Node 24 (managed via `.tool-versions`)
- Linting/Formatting: ruff
- Pre-commit: ruff, bandit, detect-secrets
- Package management: uv (`uv sync --extra dev`)
- Environment: mise (`.tool-versions` + `.mise.toml`)
