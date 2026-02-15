from aws_cdk import CfnOutput, Stack
from constructs import Construct

from infra.constructs import DnsConstruct, StaticSite, VisitorCounterApi


class EngebrethWebsiteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = self.node.try_get_context("config")
        domain_name = config["dns"]["fqdn"]

        dns = DnsConstruct(self, "Dns", domain_name=domain_name)

        site = StaticSite(
            self,
            "Site",
            domain_name=domain_name,
            hosted_zone=dns.hosted_zone,
            certificate=dns.certificate,
        )

        api = VisitorCounterApi(self, "Api")

        CfnOutput(self, "ApiUrl", value=api.api.url)
        CfnOutput(self, "DistributionDomainName", value=site.distribution.distribution_domain_name)
