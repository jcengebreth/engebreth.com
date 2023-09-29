import unittest

import boto3
from moto import mock_dynamodb2

from src.funcs.visitor_counter.index import visitor_count


# Use moto decorator to ensure we don't use actual AWS services
@mock_dynamodb2
class TestUserCount(unittest.TestCase):
    def setUp(self):
        # Check to see if table already exists.
        # If it already exists then we are connected to a real AWS env and not mock/moto
        """
        try:
            dynamodb = boto3.resource('dynamodb')
            dynamodb.meta.client.describe_table(TableName='website-visits-count')
        except botocore.exceptions.ClientError:
            pass
        else:
            err = "{Table} should not exist.".format(Table = 'website-visits-count')
            raise EnvironmentError(err)
        """
        table_name = "website-visits-count"
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "site", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "site", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

    def event():
        pass

    def context():
        pass

    def test_updateUserCount(self):
        count1 = visitor_count.lambda_handler(self.event, self.context)

        self.assertTrue(count1["body"] > 0)
        self.assertEqual(count1["body"], 1)
        self.assertEqual(count1["statusCode"], 200)


if __name__ == "__main__":
    unittest.main()
