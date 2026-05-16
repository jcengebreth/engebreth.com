import { RemovalPolicy } from "aws-cdk-lib";
import type * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as route53 from "aws-cdk-lib/aws-route53";
import * as route53Targets from "aws-cdk-lib/aws-route53-targets";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import { Construct } from "constructs";

export interface StaticSiteProps {
	domainName: string;
	hostedZone: route53.IHostedZone;
	certificate: acm.ICertificate;
}

export class StaticSite extends Construct {
	public readonly distribution: cloudfront.Distribution;

	constructor(scope: Construct, id: string, props: StaticSiteProps) {
		super(scope, id);

		const { domainName, hostedZone, certificate } = props;

		const bucket = new s3.Bucket(this, "SiteBucket", {
			bucketName: domainName,
			enforceSSL: true,
			encryption: s3.BucketEncryption.S3_MANAGED,
			removalPolicy: RemovalPolicy.DESTROY,
			autoDeleteObjects: true,
		});

		const urlRewriteFn = new cloudfront.Function(this, "UrlRewriteFunction", {
			code: cloudfront.FunctionCode.fromInline(`
        function handler(event) {
          var request = event.request;
          var uri = request.uri;
          if (uri.endsWith('/')) {
            request.uri += 'index.html';
          } else if (!uri.includes('.')) {
            request.uri += '/index.html';
          }
          return request;
        }
      `),
			runtime: cloudfront.FunctionRuntime.JS_2_0,
		});

		this.distribution = new cloudfront.Distribution(this, "Distribution", {
			defaultRootObject: "index.html",
			minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
			priceClass: cloudfront.PriceClass.PRICE_CLASS_100,
			defaultBehavior: {
				origin: origins.S3BucketOrigin.withOriginAccessControl(bucket),
				viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
				allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
				cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
				functionAssociations: [
					{
						function: urlRewriteFn,
						eventType: cloudfront.FunctionEventType.VIEWER_REQUEST,
					},
				],
			},
			domainNames: [domainName, `www.${domainName}`],
			certificate,
			errorResponses: [
				{
					httpStatus: 404,
					responseHttpStatus: 200,
					responsePagePath: "/index.html",
				},
				{
					httpStatus: 403,
					responseHttpStatus: 200,
					responsePagePath: "/index.html",
				},
			],
		});

		new s3deploy.BucketDeployment(this, "DeployWithInvalidation", {
			sources: [s3deploy.Source.asset("website/dist")],
			destinationBucket: bucket,
			distribution: this.distribution,
			distributionPaths: ["/*"],
		});

		new route53.ARecord(this, "ApexRecord", {
			target: route53.RecordTarget.fromAlias(
				new route53Targets.CloudFrontTarget(this.distribution),
			),
			zone: hostedZone,
			recordName: domainName,
		});

		new route53.ARecord(this, "WwwRecord", {
			target: route53.RecordTarget.fromAlias(
				new route53Targets.CloudFrontTarget(this.distribution),
			),
			zone: hostedZone,
			recordName: `www.${domainName}`,
		});
	}
}
