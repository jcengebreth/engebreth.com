import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DnsConstruct } from '../constructs/dns';
import { StaticSite } from '../constructs/site';
import { VisitorCounterApi } from '../constructs/api';

export class EngebrethWebsiteStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const config = this.node.tryGetContext('config') as Record<string, any>;
    const domainName = config.dns.fqdn as string;

    const dns = new DnsConstruct(this, 'Dns', { domainName });

    const site = new StaticSite(this, 'Site', {
      domainName,
      hostedZone: dns.hostedZone,
      certificate: dns.certificate,
    });

    const api = new VisitorCounterApi(this, 'Api');

    new cdk.CfnOutput(this, 'ApiUrl', { value: api.api.url });
    new cdk.CfnOutput(this, 'DistributionDomainName', { value: site.distribution.distributionDomainName });
  }
}
