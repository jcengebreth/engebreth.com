import * as cdk from "aws-cdk-lib";
import { Match, Template } from "aws-cdk-lib/assertions";
import { GitHubOidc } from "../../lib/constructs/github-oidc";

describe("GitHubOidc", () => {
	let template: Template;

	beforeAll(() => {
		const app = new cdk.App();
		const stack = new cdk.Stack(app, "TestStack", {
			env: { account: "123456789012", region: "us-east-1" },
		});
		new GitHubOidc(stack, "Oidc", {
			githubOrg: "jcengebreth",
			githubRepo: "engebreth.com",
			stackName: "prod-engebreth-website",
		});
		template = Template.fromStack(stack);
	});

	test("creates GitHub OIDC provider without placeholder thumbprints", () => {
		template.hasResourceProperties("Custom::AWSCDKOpenIdConnectProvider", {
			Url: "https://token.actions.githubusercontent.com",
			ClientIDList: ["sts.amazonaws.com"],
			// ThumbprintList intentionally absent — AWS validates GitHub automatically
			ThumbprintList: Match.absent(),
		});
	});

	test("deploy role trust policy is scoped to main branch only", () => {
		template.hasResourceProperties("AWS::IAM::Role", {
			AssumeRolePolicyDocument: Match.objectLike({
				Statement: Match.arrayWith([
					Match.objectLike({
						Condition: Match.objectLike({
							StringLike: {
								"token.actions.githubusercontent.com:sub":
									"repo:jcengebreth/engebreth.com:ref:refs/heads/main",
							},
						}),
					}),
				]),
			}),
		});
	});

	test("deploy role has no AdministratorAccess managed policy", () => {
		template.hasResourceProperties("AWS::IAM::Role", {
			ManagedPolicyArns: Match.absent(),
		});
	});

	test("CloudFormation permissions are scoped to the stack", () => {
		template.hasResourceProperties("AWS::IAM::Role", {
			Description: "GitHub Actions deployment role for engebreth.com",
			Policies: Match.arrayWith([
				Match.objectLike({
					PolicyDocument: Match.objectLike({
						Statement: Match.arrayWith([
							Match.objectLike({
								Action: "cloudformation:*",
								Resource: Match.arrayWith([
									Match.stringLikeRegexp("prod-engebreth-website"),
								]),
							}),
						]),
					}),
				}),
			]),
		});
	});

	test("IAM permissions are scoped to stack-prefixed roles", () => {
		template.hasResourceProperties("AWS::IAM::Role", {
			Description: "GitHub Actions deployment role for engebreth.com",
			Policies: Match.arrayWith([
				Match.objectLike({
					PolicyDocument: Match.objectLike({
						Statement: Match.arrayWith([
							Match.objectLike({
								// Single-action statements serialize as strings in CloudFormation
								Action: "iam:*",
								Resource: Match.arrayWith([
									Match.stringLikeRegexp("prod-engebreth-website"),
								]),
							}),
						]),
					}),
				}),
			]),
		});
	});
});
