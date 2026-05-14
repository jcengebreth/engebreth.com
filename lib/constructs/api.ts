import { RemovalPolicy } from "aws-cdk-lib";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";

export class VisitorCounterApi extends Construct {
	public readonly api: apigateway.RestApi;

	constructor(scope: Construct, id: string) {
		super(scope, id);

		const table = new dynamodb.Table(this, "Table", {
			partitionKey: { name: "site", type: dynamodb.AttributeType.STRING },
			billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
			removalPolicy: RemovalPolicy.DESTROY,
		});

		const fn = new lambda.Function(this, "Function", {
			runtime: lambda.Runtime.PYTHON_3_14,
			handler: "index.handler",
			code: lambda.Code.fromAsset("src/functions/visitor_counter"),
			environment: { TABLE_NAME: table.tableName },
		});

		table.grantReadWriteData(fn);

		this.api = new apigateway.RestApi(this, "Api", {
			restApiName: "Visitor Counter API",
			defaultCorsPreflightOptions: {
				allowOrigins: apigateway.Cors.ALL_ORIGINS,
				allowMethods: ["GET", "OPTIONS"],
			},
		});

		this.api.root.addMethod("GET", new apigateway.LambdaIntegration(fn));
	}
}
