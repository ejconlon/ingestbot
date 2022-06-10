COMPONENT_NAME=ibot_cdk
include ../../python/Makefile.base

# Freeze CDK bootstrap template (infrequent)
bootstrap-template:
	cdk bootstrap --show-template > ibot_cdk/bootstrap/template.yml

# Apply the bootstrap for the dev environment
bootstrap-create-dev:
	aws cloudformation create-stack --stack-name CDKToolkit --template-body file://./ibot_cdk/bootstrap/template.yml --parameters file://./ibot_cdk/bootstrap/params-dev.json --capabilities CAPABILITY_NAMED_IAM
