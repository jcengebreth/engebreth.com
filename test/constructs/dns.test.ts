import * as cdk from "aws-cdk-lib";
import { Match, Template } from "aws-cdk-lib/assertions";
import { DnsConstruct } from "../../lib/constructs/dns";

describe("DnsConstruct", () => {
	let template: Template;
	const domainName = "test.example.com";

	beforeAll(() => {
		const app = new cdk.App();
		const stack = new cdk.Stack(app, "TestStack");
		new DnsConstruct(stack, "Dns", { domainName });
		template = Template.fromStack(stack);
	});

	test("creates a hosted zone for the domain", () => {
		template.hasResourceProperties("AWS::Route53::HostedZone", {
			Name: `${domainName}.`,
		});
	});

	test("creates a certificate with DNS validation and wildcard SAN", () => {
		template.hasResourceProperties("AWS::CertificateManager::Certificate", {
			DomainName: domainName,
			SubjectAlternativeNames: [`*.${domainName}`],
			ValidationMethod: "DNS",
		});
	});

	test("creates MX records pointing to ImprovMX", () => {
		template.hasResourceProperties("AWS::Route53::RecordSet", {
			Type: "MX",
			ResourceRecords: Match.arrayWith([
				Match.stringLikeRegexp("improvmx\\.com"),
			]),
		});
	});

	test("creates SPF TXT record for ImprovMX", () => {
		template.hasResourceProperties("AWS::Route53::RecordSet", {
			Type: "TXT",
			ResourceRecords: Match.arrayWith([
				Match.stringLikeRegexp("spf\\.improvmx\\.com"),
			]),
		});
	});
});
