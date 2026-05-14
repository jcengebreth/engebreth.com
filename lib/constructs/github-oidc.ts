import * as iam from "aws-cdk-lib/aws-iam";
import { Construct } from "constructs";

export interface GitHubOidcProps {
	githubOrg: string;
	githubRepo: string;
}

export class GitHubOidc extends Construct {
	public readonly role: iam.Role;

	constructor(scope: Construct, id: string, props: GitHubOidcProps) {
		super(scope, id);

		const { githubOrg, githubRepo } = props;

		const provider = new iam.OpenIdConnectProvider(this, "GitHubProvider", {
			url: "https://token.actions.githubusercontent.com",
			clientIds: ["sts.amazonaws.com"],
			thumbprints: ["ffffffffffffffffffffffffffffffffffffffff"],
		});

		this.role = new iam.Role(this, "DeployRole", {
			assumedBy: new iam.WebIdentityPrincipal(
				provider.openIdConnectProviderArn,
				{
					StringEquals: {
						"token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
					},
					StringLike: {
						"token.actions.githubusercontent.com:sub": `repo:${githubOrg}/${githubRepo}:*`,
					},
				},
			),
			description: "GitHub Actions deployment role for engebreth.com",
			managedPolicies: [
				iam.ManagedPolicy.fromAwsManagedPolicyName("AdministratorAccess"),
			],
		});
	}
}
