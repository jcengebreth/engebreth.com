import aws_cdk.aws_route53 as route53
from aws_cdk.aws_certificatemanager import Certificate, CertificateValidation
from constructs import Construct


class DnsConstruct(Construct):
    """Hosted zone, ACM certificate, and email forwarding DNS records."""

    def __init__(self, scope: Construct, construct_id: str, *, domain_name: str) -> None:
        super().__init__(scope, construct_id)

        self.hosted_zone = route53.HostedZone(
            self,
            "HostedZone",
            zone_name=domain_name,
        )

        self.certificate = Certificate(
            self,
            "Certificate",
            domain_name=domain_name,
            validation=CertificateValidation.from_dns(hosted_zone=self.hosted_zone),
            subject_alternative_names=[f"*.{domain_name}"],
        )

        # ImprovMX email forwarding — MX records
        route53.MxRecord(
            self,
            "EmailMx",
            zone=self.hosted_zone,
            values=[
                route53.MxRecordValue(host_name="mx1.improvmx.com", priority=10),
                route53.MxRecordValue(host_name="mx2.improvmx.com", priority=20),
            ],
        )

        # SPF record for ImprovMX
        route53.TxtRecord(
            self,
            "EmailSpf",
            zone=self.hosted_zone,
            values=["v=spf1 include:spf.improvmx.com ~all"],
        )
