#!/usr/bin/env python3
import os

import aws_cdk as cdk
import yaml

from cdk.stacks.engebreth_website_stack import EngebrethWebsiteStack

# ingest environment variables for AWS account ID and Default Region
_env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
)

# define the cdk app
app: cdk.App = cdk.App()

# stage is set in cdk.context.json
stage: str = app.node.try_get_context("stage")
environment: str = app.node.try_get_context("environment")

if not stage:
    cdk.Annotations.of(app).add_error("No Stage Attached")
if not environment:
    cdk.Annotations.of(app).add_error("No Environment Attached")

# import config values
with open(f"config/{stage}.yaml") as _config:
    config = yaml.safe_load(_config)

# cdk app tagging
cdk.Tags.of(app).add("project", f"{config['metadata']['project_name']}")
app.node.set_context("project_name", config["metadata"]["project_name"])

# set kwargs for cdk stack
website_stack_kwargs = {
    "scope": app,
    "id": f"{stage}-{config['metadata']['project_name']}",
    "env": _env,
}

website_stack: EngebrethWebsiteStack = EngebrethWebsiteStack(**website_stack_kwargs)

app.synth()
