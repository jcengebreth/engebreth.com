#!/usr/bin/env python3
import os

import aws_cdk as cdk
import yaml

from infra.stacks.engebreth_website_stack import EngebrethWebsiteStack

_env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
)

app: cdk.App = cdk.App()

# Config file is selected via context: -c config=prod
config_name: str = app.node.try_get_context("config") or "prod"

with open(f"config/{config_name}.yaml") as f:
    config = yaml.safe_load(f)

stage = config["metadata"]["stage"]
project_name = config["metadata"]["project_name"]

cdk.Tags.of(app).add("project", project_name)
app.node.set_context("config", config)

EngebrethWebsiteStack(
    scope=app,
    construct_id=f"{stage}-{project_name}",
    env=_env,
)

app.synth()
