# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- Restructured project: `cdk/` → `infra/`, `src/funcs/` → `functions/`, `src/ui/` → `website/` (Astro)
- Split monolithic CDK stack into composable constructs (DnsConstruct, StaticSite, VisitorCounterApi)
- Replaced black, flake8, isort, pyupgrade with ruff
- Replaced `requirements.txt` / `requirements-dev.txt` with `pyproject.toml`
- Replaced `.python-version` and `.node-version` with `.tool-versions` (Python 3.13, Node 24)
- Added `.envrc` for direnv support
- Upgraded Lambda runtime from Python 3.9 to Python 3.13
- Switched DynamoDB from provisioned capacity to on-demand (PAY_PER_REQUEST)
- Switched CloudFront from OAI to OAC (Origin Access Control)
- Switched email forwarding from Cloudflare to ImprovMX
- Updated Google Fonts from HTTP to HTTPS
- Updated GitHub Actions workflow to use OIDC auth and two-phase CDK deploy
- Updated pre-commit hooks to latest versions
- Updated headshot image
- Fixed visitor counter test (broken import, deprecated moto decorator)
- Fixed visitor counter to only count once per session (sessionStorage)
- Fixed CloudFront URL routing for Astro pages (CloudFront Function rewrite)
- Removed hardcoded region from Lambda function
- Renamed stage from `dev` to `prod`
- Config-driven stage naming (from `config/*.yaml`, not `cdk.json`)
- API URL injected at build time from stack outputs, not committed

### Added

- Astro-based frontend with splash page, resume page, and projects page
- Shared layout with navigation and footer
- Visitor counter in site footer (once per session)
- CloudFront Function for clean URL routing (`/resume` → `/resume/index.html`)
- CDK stack outputs for API URL and CloudFront domain
- CORS configuration at API Gateway level
- ImprovMX email forwarding DNS records (MX + SPF)
- Email link on splash page (jerad@engebreth.com)
- Amazon Bedrock AgentCore Samples contribution on projects page
- CHANGELOG.md
- Setup docs (`docs/setup.md`) with OIDC and deployment instructions
- Kiro steering files for project conventions
- Root `package.json` for CDK CLI

### Removed

- Old single-page HTML resume
- IE conditional shim
- Hardcoded API Gateway URL in frontend
- `.flake8` config
- `source.bat`
- Unused Lambda layer directory
- Phone number from public site
- Cloudflare Email Routing (replaced by ImprovMX)
