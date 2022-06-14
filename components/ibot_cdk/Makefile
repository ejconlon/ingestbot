COMPONENT_NAME=ibot_cdk
include ../../python/Makefile.app

# Package the application
.PHONY: package
package: pippackage
	cd ../../.build && cp ../components/$(COMPONENT_NAME)/entrypoint.sh $(COMPONENT_NAME)/entrypoint.sh
	cd ../../.build && chmod +x $(COMPONENT_NAME)/entrypoint.sh
	cd ../../.build && echo '{ "app": "python3 -m ibot_cdk.main" }' > $(COMPONENT_NAME)/cdk.json
	cd ../../.build/$(COMPONENT_NAME) && zip -rq ../$(COMPONENT_NAME).zip .
	cd ../../.build && unzip -l $(COMPONENT_NAME).zip

# Freeze CDK bootstrap template (infrequent)
.PHONY: bootstrap-template
bootstrap-template:
	cdk bootstrap --show-template > ibot_cdk/bootstrap/template.yml

# Apply the bootstrap for the dev environment
.PHONY: bootstrap-create-dev
bootstrap-create-dev:
	aws cloudformation create-stack --stack-name CDKToolkit --template-body file://./ibot_cdk/bootstrap/template.yml --parameters file://./ibot_cdk/bootstrap/params-dev.json --capabilities CAPABILITY_NAMED_IAM
