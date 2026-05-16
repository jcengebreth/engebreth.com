import * as cdk from "aws-cdk-lib";
import * as iam from "aws-cdk-lib/aws-iam";
import { Construct } from "constructs";

export interface GitHubOidcProps {
	githubOrg: string;
	githubRepo: string;
	stackName: string;
}

export class GitHubOidc extends Construct {
	public readonly role: iam.Role;

	constructor(scope: Construct, id: string, props: GitHubOidcProps) {
		super(scope, id);

		const { githubOrg, githubRepo, stackName } = props;
		const account = cdk.Stack.of(this).account;
		const region = cdk.Stack.of(this).region;

		// AWS validates GitHub's OIDC provider automatically — thumbprints not required
		const provider = new iam.OpenIdConnectProvider(this, "GitHubProvider", {
			url: "https://token.actions.githubusercontent.com",
			clientIds: ["sts.amazonaws.com"],
		});

		this.role = new iam.Role(this, "DeployRole", {
			assumedBy: new iam.WebIdentityPrincipal(
				provider.openIdConnectProviderArn,
				{
					StringEquals: {
						"token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
					},
					StringLike: {
						"token.actions.githubusercontent.com:sub": `repo:${githubOrg}/${githubRepo}:ref:refs/heads/main`,
					},
				},
			),
			description: "GitHub Actions deployment role for engebreth.com",
			inlinePolicies: {
				DeployPolicy: new iam.PolicyDocument({
					statements: [
						// CloudFormation — scoped to this stack only
						new iam.PolicyStatement({
							actions: ["cloudformation:*"],
							resources: [
								`arn:aws:cloudformation:${region}:${account}:stack/${stackName}/*`,
								`arn:aws:cloudformation:${region}:${account}:stack/CDKToolkit/*`,
							],
						}),
						// CDK bootstrap bucket and site assets
						new iam.PolicyStatement({
							actions: ["s3:*"],
							resources: ["*"],
						}),
						// Services used by this stack
						new iam.PolicyStatement({
							actions: [
								"cloudfront:*",
								"lambda:*",
								"dynamodb:*",
								"apigateway:*",
								"route53:*",
								"acm:*",
								"logs:*",
							],
							resources: ["*"],
						}),
						// IAM — CDK creates execution roles for Lambda
						new iam.PolicyStatement({
							actions: ["iam:*"],
							resources: [
								`arn:aws:iam::${account}:role/${stackName}-*`,
								`arn:aws:iam::${account}:role/cdk-*`,
							],
						}),
						// SSM — CDK bootstrap parameters
						new iam.PolicyStatement({
							actions: [
								"ssm:GetParameter",
								"ssm:PutParameter",
								"ssm:DeleteParameter",
							],
							resources: [
								`arn:aws:ssm:${region}:${account}:parameter/cdk-bootstrap/*`,
							],
						}),
						// STS — CDK assumes bootstrap roles
						new iam.PolicyStatement({
							actions: ["sts:AssumeRole"],
							resources: [`arn:aws:iam::${account}:role/cdk-*`],
						}),
					],
				}),
			},
		});
	}
}
