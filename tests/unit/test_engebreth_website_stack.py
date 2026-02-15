# CDK stack tests — uncomment and expand as needed
#
# import aws_cdk as core
# import aws_cdk.assertions as assertions
# from infra.stacks.engebreth_website_stack import EngebrethWebsiteStack
#
# def test_stack_creates_dynamodb_table():
#     app = core.App(context={
#         "stage": "dev",
#         "environment": "dev",
#         "config": {"dns": {"fqdn": "example.com"}, "metadata": {"project_name": "test"}},
#     })
#     stack = EngebrethWebsiteStack(app, "test-stack", env=core.Environment(account="123456789012", region="us-east-1"))
#     template = assertions.Template.from_stack(stack)
#     template.has_resource_properties("AWS::DynamoDB::Table", {
#         "BillingMode": "PAY_PER_REQUEST",
#     })
