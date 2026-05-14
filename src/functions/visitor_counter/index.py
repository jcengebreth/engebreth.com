import json
import os
from decimal import Decimal

import boto3


class DecimalEncoder(json.JSONEncoder):
    """Handle DynamoDB Decimal types in JSON serialization."""

    def default(self, o):
        if isinstance(o, Decimal):
            return int(o) if o % 1 == 0 else float(o)
        return super().default(o)


def handler(event, context):
    """Increment and return the visitor count."""
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    response = table.update_item(
        Key={"site": "engebreth.com"},
        UpdateExpression="ADD numbCount :inc",
        ExpressionAttributeValues={":inc": 1},
        ReturnValues="UPDATED_NEW",
    )

    count = int(response["Attributes"]["numbCount"])

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": count,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
    }
