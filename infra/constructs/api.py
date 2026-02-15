import aws_cdk.aws_apigateway as apigateway
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_lambda as _lambda
from aws_cdk import RemovalPolicy
from constructs import Construct


class VisitorCounterApi(Construct):
    """DynamoDB table, Lambda function, and API Gateway for the visitor counter."""

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        table = dynamodb.Table(
            self,
            "Table",
            partition_key=dynamodb.Attribute(
                name="site",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        function = _lambda.Function(
            self,
            "Function",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="index.handler",
            code=_lambda.Code.from_asset("functions/visitor_counter"),
            environment={"TABLE_NAME": table.table_name},
        )

        table.grant_read_write_data(function)

        self.api = apigateway.RestApi(
            self,
            "Api",
            rest_api_name="Visitor Counter API",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "OPTIONS"],
            ),
        )

        self.api.root.add_method(
            "GET",
            apigateway.LambdaIntegration(function),
        )
