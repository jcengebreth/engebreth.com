import aws_cdk.aws_apigateway as apigateway
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_route53 as route53
import aws_cdk.aws_route53_targets as route53_targets
from aws_cdk import RemovalPolicy, Stack
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
            website_index_document="index.html",
            website_error_document="error.html",
        )

        # ACM import certificate for engebreth.com
        certificate_arn = self.node.try_get_context(config["dns"]["certificate_arn"])
        domain_cert = Certificate.from_certificate_arn(
            self,
            "domainCert",
            certificate_arn,
        )

        # R53 hosted zone
        hosted_zone = route53.HostedZone(
            self,
            "EngebrethWebsiteZone",
            zone_name="engebreth.com",
        )

        # Cloudfront distribution
        distribution = cloudfront.Distribution(
            self,
            "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(uiBucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=["engebreth.com", "www.engebreth.com"],
            certificate=domain_cert,
        )

        # Define an OAI (Origin Access Identity)
        oai = cloudfront.OriginAccessIdentity(
            self,
            "WebsiteOAI",
            comment="OAI for UI S3 bucket",
        )

        # Restrict access to the S3 bucket through the OAI
        uiBucket.grant_read(oai)

        # Grant CloudFront distribution permissions to access the S3 bucket
        uiBucket.grant_read(distribution)

        # Define Route 53 DNS records
        route53.ARecord(
            self,
            "WebsiteAliasRecord",
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(distribution),
            ),
            zone=hosted_zone,
            record_name="engebreth.com",
        )

        route53.ARecord(
            self,
            "WebsiteWWWAliasRecord",
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(distribution),
            ),
            zone=hosted_zone,
            record_name="www.engebreth.com",
        )

        # DynamoDB table to hold counter

        dynamodb_table = dynamodb.Table(
            self,
            "WebsiteTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING,
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Lambda function for iterating counter

        lambda_function = _lambda.Function(
            self,
            "VisitorCounterFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset("src/funcs/visitor_counter"),
            environment={"TABLE_NAME": dynamodb_table.table_name},
        )

        # Grant Lambda permissions to read/write from/to DynamoDB
        dynamodb_table.grant_read_write_data(lambda_function)

        # Create an API Gateway REST API
        api = apigateway.RestApi(
            self,
            "WebsiteApi",
            rest_api_name="Website API",
            description="API for your website",
        )

        # Create a Lambda integration for the API
        lambda_integration = apigateway.LambdaIntegration(
            lambda_function,
            integration_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Content-Type": "text/html",
                    },
                },
            ],
        )

        # Create a resource and method for the Lambda function in the API
        api_resource = api.root.add_resource("lambda")
        api_resource.add_method("GET", lambda_integration)
