import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import aws_cdk.aws_route53 as route53
import aws_cdk.aws_route53_targets as route53_targets
import aws_cdk.aws_s3_deployment as s3deploy
from aws_cdk import RemovalPolicy
from aws_cdk.aws_certificatemanager import ICertificate
from aws_cdk.aws_route53 import IHostedZone
from aws_cdk.aws_s3 import Bucket, BucketEncryption
from constructs import Construct


class StaticSite(Construct):
    """S3 bucket, CloudFront distribution, bucket deployment, and DNS A records."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domain_name: str,
        hosted_zone: IHostedZone,
        certificate: ICertificate,
    ) -> None:
        super().__init__(scope, construct_id)

        bucket = Bucket(
            self,
            "SiteBucket",
            bucket_name=domain_name,
            enforce_ssl=True,
            encryption=BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # CloudFront Function to rewrite URLs for clean paths
        # e.g. /resume → /resume/index.html
        url_rewrite_fn = cloudfront.Function(
            self,
            "UrlRewriteFunction",
            code=cloudfront.FunctionCode.from_inline(
                "function handler(event) {"
                "  var request = event.request;"
                "  var uri = request.uri;"
                "  if (uri.endsWith('/')) {"
                "    request.uri += 'index.html';"
                "  } else if (!uri.includes('.')) {"
                "    request.uri += '/index.html';"
                "  }"
                "  return request;"
                "}"
            ),
            runtime=cloudfront.FunctionRuntime.JS_2_0,
        )

        self.distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_root_object="index.html",
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                function_associations=[
                    cloudfront.FunctionAssociation(
                        function=url_rewrite_fn,
                        event_type=cloudfront.FunctionEventType.VIEWER_REQUEST,
                    ),
                ],
            ),
            domain_names=[domain_name, f"www.{domain_name}"],
            certificate=certificate,
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
        )

        s3deploy.BucketDeployment(
            self,
            "DeployWithInvalidation",
            sources=[s3deploy.Source.asset("website/dist")],
            destination_bucket=bucket,
            distribution=self.distribution,
            distribution_paths=["/*"],
        )

        # DNS A records for apex and www
        route53.ARecord(
            self,
            "ApexRecord",
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(self.distribution),
            ),
            zone=hosted_zone,
            record_name=domain_name,
        )

        route53.ARecord(
            self,
            "WwwRecord",
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(self.distribution),
            ),
            zone=hosted_zone,
            record_name=f"www.{domain_name}",
        )
