import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import aws_cdk.aws_route53 as route53
from aws_cdk import Stack
from aws_cdk.aws_certificatemanager import Certificate
from aws_cdk.aws_s3 import Bucket, BucketEncryption
from constructs import Construct


class EngebrethWebsiteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import context set by app.py
        config = self.node.try_get_context("config")

        # Set domain name to config value
        self.node.try_get_context(config["dns"]["fqdn"])

        # S3 bucket for UI assets

        uiBucket = Bucket(
            self,
            bucket_name="engebreth-website-ui",
            enforce_ssl=True,
            block_public_access=True,
            encryption=BucketEncryption.S3_MANAGED,
        )

        # ACM import certificate for engebreth.com

        certificate_arn = self.node.try_get_context(config["dns"]["certificate_arn"])
        Certificate.from_certificate_arn(self, "domainCert", certificate_arn)

        # Cloudfront distribution and OAI

        cf_dist = cloudfront.Distribution(
            self,
            "myDist",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(uiBucket),
            ),
        )

        # R53 hosted zone

        route53.HostedZone(self, "MyZone", zone_name=cf_dist.domain_name)

        # DynamoDB table to hold counter

        # Lambda function for iterating counter
