import decimal
import json

import boto3


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super().default(o)


### Create handler to execute function
def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("website-visits-count")
    response = table.update_item(
        Key={"site": "engebreth.com"},
        UpdateExpression="ADD numbCount :inc",
        ExpressionAttributeValues={":inc": 1},
        ReturnValues="UPDATED_NEW",
    )

    # Format dynamodb response into variable
    responseBody = json.dumps(
        int(float(response["Attributes"]["numbCount"])),
        cls=DecimalEncoder,
    )

    # Loads turns the JSON object into a Python dict
    responseBody_int = json.loads(responseBody)

    # API Response Object And Format To JSON
    apiResponse = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": responseBody_int,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
    }

    # Return API Response
    return apiResponse
