import * as cdk from "aws-cdk-lib";
import type { Construct } from "constructs";
import { VisitorCounterApi } from "../constructs/api";
import { DnsConstruct } from "../constructs/dns";
import { StaticSite } from "../constructs/site";
import type { AppConfig } from "../types";

export class EngebrethWebsiteStack extends cdk.Stack {
	constructor(scope: Construct, id: string, props?: cdk.StackProps) {
		super(scope, id, props);

		const config = this.node.tryGetContext("config") as AppConfig;
		const domainName = config.dns.fqdn;

		const dns = new DnsConstruct(this, "Dns", { domainName });

		const site = new StaticSite(this, "Site", {
			domainName,
			hostedZone: dns.hostedZone,
			certificate: dns.certificate,
		});

		const api = new VisitorCounterApi(this, "Api");

		new cdk.CfnOutput(this, "ApiUrl", { value: api.api.url });
		new cdk.CfnOutput(this, "DistributionDomainName", {
			value: site.distribution.distributionDomainName,
		});
	}
}
