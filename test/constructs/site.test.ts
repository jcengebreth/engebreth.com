import * as fs from "node:fs";
import * as path from "node:path";
import * as cdk from "aws-cdk-lib";
import { Match, Template } from "aws-cdk-lib/assertions";
import * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as route53 from "aws-cdk-lib/aws-route53";
import { StaticSite } from "../../lib/constructs/site";

describe("StaticSite", () => {
	const distPath = path.join(__dirname, "../../website/dist");
	let template: Template;

	beforeAll(() => {
		// CDK asset bundling requires website/dist to exist at synth time
		fs.mkdirSync(distPath, { recursive: true });
		fs.writeFileSync(path.join(distPath, "index.html"), "<html></html>");

		const app = new cdk.App();
		const stack = new cdk.Stack(app, "TestStack", {
			env: { account: "123456789012", region: "us-east-1" },
		});

		const zone = new route53.HostedZone(stack, "Zone", {
			zoneName: "example.com",
		});
		const cert = new acm.Certificate(stack, "Cert", {
			domainName: "example.com",
		});

		new StaticSite(stack, "Site", {
			domainName: "example.com",
			hostedZone: zone,
			certificate: cert,
		});

		template = Template.fromStack(stack);
	});

	afterAll(() => {
		fs.rmSync(distPath, { recursive: true, force: true });
	});

	test("creates an S3 bucket with SSL enforcement and encryption", () => {
		template.hasResourceProperties("AWS::S3::Bucket", {
			BucketName: "example.com",
			BucketEncryption: Match.objectLike({
				ServerSideEncryptionConfiguration: Match.anyValue(),
			}),
		});
	});

	test("CloudFront distribution redirects HTTP to HTTPS", () => {
		template.hasResourceProperties("AWS::CloudFront::Distribution", {
			DistributionConfig: Match.objectLike({
				DefaultCacheBehavior: Match.objectLike({
					ViewerProtocolPolicy: "redirect-to-https",
				}),
			}),
		});
	});

	test("CloudFront enforces TLS 1.2 minimum", () => {
		template.hasResourceProperties("AWS::CloudFront::Distribution", {
			DistributionConfig: Match.objectLike({
				ViewerCertificate: Match.objectLike({
					MinimumProtocolVersion: "TLSv1.2_2021",
				}),
			}),
		});
	});

	test("CloudFront uses PriceClass_100 to minimize cost", () => {
		template.hasResourceProperties("AWS::CloudFront::Distribution", {
			DistributionConfig: Match.objectLike({
				PriceClass: "PriceClass_100",
			}),
		});
	});

	test("CloudFront returns 200 index.html for 404 errors", () => {
		template.hasResourceProperties("AWS::CloudFront::Distribution", {
			DistributionConfig: Match.objectLike({
				CustomErrorResponses: Match.arrayWith([
					Match.objectLike({
						ErrorCode: 404,
						ResponseCode: 200,
						ResponsePagePath: "/index.html",
					}),
				]),
			}),
		});
	});

	test("CloudFront returns 200 index.html for 403 errors", () => {
		template.hasResourceProperties("AWS::CloudFront::Distribution", {
			DistributionConfig: Match.objectLike({
				CustomErrorResponses: Match.arrayWith([
					Match.objectLike({
						ErrorCode: 403,
						ResponseCode: 200,
						ResponsePagePath: "/index.html",
					}),
				]),
			}),
		});
	});

	test("creates apex A record", () => {
		template.hasResourceProperties("AWS::Route53::RecordSet", {
			Name: "example.com.",
			Type: "A",
		});
	});

	test("creates www A record", () => {
		template.hasResourceProperties("AWS::Route53::RecordSet", {
			Name: "www.example.com.",
			Type: "A",
		});
	});
});
