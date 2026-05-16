import * as cdk from "aws-cdk-lib";
import { Match, Template } from "aws-cdk-lib/assertions";
import { VisitorCounterApi } from "../../lib/constructs/api";

describe("VisitorCounterApi", () => {
	let template: Template;

	beforeAll(() => {
		const app = new cdk.App();
		const stack = new cdk.Stack(app, "TestStack");
		new VisitorCounterApi(stack, "Api");
		template = Template.fromStack(stack);
	});

	test("creates a DynamoDB table with on-demand billing", () => {
		template.hasResourceProperties("AWS::DynamoDB::Table", {
			BillingMode: "PAY_PER_REQUEST",
			KeySchema: [{ AttributeName: "site", KeyType: "HASH" }],
		});
	});

	test("creates a Lambda function with Python 3.14 runtime", () => {
		template.hasResourceProperties("AWS::Lambda::Function", {
			Runtime: "python3.14",
			Handler: "index.handler",
		});
	});

	test("Lambda receives TABLE_NAME environment variable", () => {
		template.hasResourceProperties("AWS::Lambda::Function", {
			Environment: {
				Variables: Match.objectLike({
					TABLE_NAME: Match.anyValue(),
				}),
			},
		});
	});

	test("creates an API Gateway REST API", () => {
		template.hasResourceProperties("AWS::ApiGateway::RestApi", {
			Name: "Visitor Counter API",
		});
	});

	test("API Gateway exposes a GET method", () => {
		template.hasResourceProperties("AWS::ApiGateway::Method", {
			HttpMethod: "GET",
			AuthorizationType: "NONE",
		});
	});

	test("API Gateway stage has throttling configured", () => {
		template.hasResourceProperties("AWS::ApiGateway::Stage", {
			MethodSettings: Match.arrayWith([
				Match.objectLike({
					ThrottlingRateLimit: 10,
					ThrottlingBurstLimit: 20,
				}),
			]),
		});
	});

	test("API Gateway CORS does not allow all origins", () => {
		// OPTIONS method mock integration response headers must not contain *
		const methods = template.findResources("AWS::ApiGateway::Method", {
			Properties: { HttpMethod: "OPTIONS" },
		});
		const bodies = JSON.stringify(methods);
		expect(bodies).not.toContain('"*"');
	});
});
