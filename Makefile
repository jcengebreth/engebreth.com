# Set Env variables up here

# Make rules below

all:
	@echo at this time we do not use a full make

# CDK commands

synth:
	npx cdk synth --profile personal

deploy:
	npx cdk deploy --profile personal

destroy:
	npx cdk destroy --profile personal