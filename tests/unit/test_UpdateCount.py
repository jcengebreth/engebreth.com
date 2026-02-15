import os
import unittest

import boto3
from moto import mock_aws

from functions.visitor_counter.index import handler


@mock_aws
class TestVisitorCount(unittest.TestCase):
    def setUp(self):
        # Set env vars the handler expects
        os.environ["TABLE_NAME"] = "test-visitor-count"
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="test-visitor-count",
            KeySchema=[
                {"AttributeName": "site", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "site", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

    def tearDown(self):
        os.environ.pop("TABLE_NAME", None)
        os.environ.pop("AWS_DEFAULT_REGION", None)

    def test_handler_increments_count(self):
        result = handler({}, {})

        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(result["body"], 1)

    def test_handler_increments_on_subsequent_calls(self):
        handler({}, {})
        result = handler({}, {})

        self.assertEqual(result["body"], 2)


if __name__ == "__main__":
    unittest.main()
