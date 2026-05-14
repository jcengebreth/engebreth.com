import * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as route53 from "aws-cdk-lib/aws-route53";
import { Construct } from "constructs";

export interface DnsConstructProps {
	domainName: string;
}

export class DnsConstruct extends Construct {
	public readonly hostedZone: route53.HostedZone;
	public readonly certificate: acm.Certificate;

	constructor(scope: Construct, id: string, props: DnsConstructProps) {
		super(scope, id);

		const { domainName } = props;

		this.hostedZone = new route53.HostedZone(this, "HostedZone", {
			zoneName: domainName,
		});

		this.certificate = new acm.Certificate(this, "Certificate", {
			domainName,
			validation: acm.CertificateValidation.fromDns(this.hostedZone),
			subjectAlternativeNames: [`*.${domainName}`],
		});

		new route53.MxRecord(this, "EmailMx", {
			zone: this.hostedZone,
			values: [
				{ hostName: "mx1.improvmx.com", priority: 10 },
				{ hostName: "mx2.improvmx.com", priority: 20 },
			],
		});

		new route53.TxtRecord(this, "EmailSpf", {
			zone: this.hostedZone,
			values: ["v=spf1 include:spf.improvmx.com ~all"],
		});
	}
}
