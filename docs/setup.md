# Setup Guide

## Prerequisites

- [asdf](https://asdf-vm.com/) or [mise](https://mise.jdx.dev/) for runtime management
- [direnv](https://direnv.net/) for environment management
- An AWS account with CLI access (SSO recommended)
- A GitHub account

## First-Time Setup

### 1. Install runtimes

```bash
# Using asdf
asdf install

# Or using mise
mise install
```

This installs Python 3.13 and Node 24 as defined in `.tool-versions`.

### 2. Allow direnv

```bash
direnv allow
```

### 3. Install dependencies

```bash
make install
```

### 4. Bootstrap CDK (first time only)

```bash
npx cdk bootstrap --profile personal
```

### 5. Deploy

```bash
make deploy
```

Note the outputs:
- `ApiUrl` — the visitor counter API endpoint
- `DistributionDomainName` — the CloudFront domain

### 6. Update nameservers

If the hosted zone was recreated, update the nameservers at Route53 → Registered domains → your domain → Name servers. Get the new NS records from the hosted zone.

### 7. Configure the visitor counter URL

Copy `website/.env.example` to `website/.env` and set `PUBLIC_API_URL` to the `ApiUrl` output. Redeploy to pick it up.

## CI/CD Setup (GitHub Actions + OIDC)

After the first local deploy, set up OIDC so GitHub Actions can deploy automatically. This only needs to be done once per AWS account.

### 1. Create the OIDC identity provider

In the AWS Console: IAM → Identity providers → Add provider

- Provider type: OpenID Connect
- Provider URL: `https://token.actions.githubusercontent.com`
- Audience: `sts.amazonaws.com`

Or via CLI:

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list ffffffffffffffffffffffffffffffffffffffff \
  --profile personal
```

### 2. Create the deploy role

Create a file `github-oidc-trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:jcengebreth/engebreth.com:*"
        }
      }
    }
  ]
}
```

Replace `ACCOUNT_ID` with your AWS account ID, then:

```bash
aws iam create-role \
  --role-name github-actions-deploy \
  --assume-role-policy-document file://github-oidc-trust-policy.json \
  --profile personal

aws iam attach-role-policy \
  --role-name github-actions-deploy \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess \
  --profile personal
```

Note the role ARN from the output.

### 3. Add the secret to GitHub

In your GitHub repo: Settings → Secrets and variables → Actions → New repository secret

- Name: `AWS_ROLE_ARN`
- Value: the role ARN from step 2 (e.g. `arn:aws:iam::123456789012:role/github-actions-deploy`)

### 4. Done

Pushes to `main` will now authenticate via OIDC and deploy automatically. The workflow runs lint, tests, builds the Astro site, then runs `cdk deploy`.

## Local Development

```bash
cd website && npm run dev    # Astro dev server at localhost:4321
make test                    # pytest
make lint                    # ruff check + format check
make format                  # auto-fix
make synth                   # synthesize CloudFormation template
make deploy                  # build + deploy
make destroy                 # tear down
```
