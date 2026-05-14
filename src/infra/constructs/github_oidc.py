import aws_cdk.aws_iam as iam
from constructs import Construct


class GitHubOidc(Construct):
    """GitHub Actions OIDC provider and deployment role."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        github_org: str,
        github_repo: str,
    ) -> None:
        super().__init__(scope, construct_id)

        # Create the OIDC provider for GitHub Actions
        provider = iam.OpenIdConnectProvider(
            self,
            "GitHubProvider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
            thumbprints=["ffffffffffffffffffffffffffffffffffffffff"],
        )

        # IAM role that GitHub Actions assumes via OIDC
        self.role = iam.Role(
            self,
            "DeployRole",
            assumed_by=iam.WebIdentityPrincipal(
                provider.open_id_connect_provider_arn,
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": f"repo:{github_org}/{github_repo}:*",
                    },
                },
            ),
            description="GitHub Actions deployment role for engebreth.com",
            # CDK deploy needs broad permissions — scope down if you want tighter security
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"),
            ],
        )
