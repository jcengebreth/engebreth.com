import aws_cdk.aws_apigateway as apigateway
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_route53 as route53
import aws_cdk.aws_route53_targets as route53_targets
import aws_cdk.aws_s3_deployment as s3deploy
from aws_cdk import RemovalPolicy, Stack
from aws_cdk.aws_certificatemanager import Certificate
from aws_cdk.aws_s3 import Bucket, BucketEncryption
from constructs import Construct


class EngebrethWebsiteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import context set by app.py
        config = self.node.try_get_context("config")
        print(config)

        # Set domain name to config value
        # domain_name = config["dns"]["fqdn"]

        # S3 bucket for UI assets
        uiBucket = Bucket(
            self,
            "engebreth.com",
            bucket_name="engebreth.com",
            enforce_ssl=True,
            encryption=BucketEncryption.S3_MANAGED,
            website_index_document="index.html",
            website_error_document="error.html",
            removal_policy=RemovalPolicy.DESTROY,
        )

        # ACM import certificate for engebreth.com
        certificate_arn = config["dns"]["certificate_arn"]
        print(certificate_arn)
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

        # Define an OAI (Origin Access Identity)
        oai = cloudfront.OriginAccessIdentity(
            self,
            "WebsiteOAI",
            comment="OAI for UI S3 bucket",
        )

        # Cloudfront distribution
        distribution = cloudfront.Distribution(
            self,
            "WebsiteDistribution",
            default_root_object="index.html",
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(uiBucket, origin_access_identity=oai),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
            ),
            domain_names=["engebreth.com", "www.engebreth.com"],
            certificate=domain_cert,
        )

        s3deploy.BucketDeployment(
            self,
            "DeployWithInvalidation",
            sources=[s3deploy.Source.asset("src/ui")],
            destination_bucket=uiBucket,
            distribution=distribution,
        )

        # Restrict access to the S3 bucket through the OAI
        uiBucket.grant_read(oai)

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

        visitor_count_table = dynamodb.Table(
            self,
            "VisitorCountTable",
            table_name="engebreth-website-visits-count",
            partition_key=dynamodb.Attribute(
                name="site",
                type=dynamodb.AttributeType.STRING,
            ),
            removal_policy=RemovalPolicy.DESTROY,  # Adjust removal policy as needed
            read_capacity=5,
            write_capacity=5,
        )

        # Lambda function for iterating counter

        lambda_function = _lambda.Function(
            self,
            "VisitorCounterFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset("src/funcs/visitor_counter"),
            environment={"TABLE_NAME": visitor_count_table.table_name},
        )

        # Grant Lambda permissions to read/write from/to DynamoDB
        visitor_count_table.grant_read_write_data(lambda_function)

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
                    "responseParameters": {},
                },
            ],
        )

        # Create a resource and method for the Lambda function in the API
        api_resource = api.root.add_resource("lambda")
        api_resource.add_method("GET", lambda_integration)
