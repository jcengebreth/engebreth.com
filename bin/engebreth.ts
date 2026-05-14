#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as fs from 'fs';
import * as yaml from 'js-yaml';
import { EngebrethWebsiteStack } from '../lib/stacks/engebreth-website-stack';

const app = new cdk.App();

const configName = (app.node.tryGetContext('config') as string) || 'prod';
const config = yaml.load(fs.readFileSync(`config/${configName}.yaml`, 'utf8')) as Record<string, any>;

const stage = config.metadata.stage as string;
const projectName = config.metadata.project_name as string;

cdk.Tags.of(app).add('project', projectName);
app.node.setContext('config', config);

new EngebrethWebsiteStack(app, `${stage}-${projectName}`, {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

app.synth();
