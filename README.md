# engebreth.com

Personal portfolio website built with Astro and deployed to AWS using CDK.

## Architecture

- **Frontend**: Astro static site → S3 + CloudFront
- **Backend**: Lambda (Python 3.13) + DynamoDB (on-demand) + API Gateway
- **DNS**: Route53 + ACM
- **Email**: Cloudflare Email Routing
- **CI/CD**: GitHub Actions with OIDC authentication
- **IaC**: AWS CDK (Python)

## Project Structure

```
├── app.py                  # CDK app entrypoint
├── infra/                  # CDK infrastructure code
│   ├── stacks/
│   └── constructs/
├── website/                # Astro frontend
│   ├── src/
│   │   ├── layouts/
│   │   └── pages/
│   └── public/
├── functions/              # Lambda functions
│   └── visitor_counter/
├── tests/
└── config/
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

- Python 3.13 / Node 24 (managed via `.tool-versions`)
- Linting/Formatting: ruff
- Pre-commit: ruff, bandit, detect-secrets
- Environment: direnv (`.envrc`)
