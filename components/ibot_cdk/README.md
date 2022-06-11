# ibot_cdk

Requires `cdk` installed and venv initialized with `make build`.

Synthesize:

    IBOT_ENV=dev cdk synth

Deploy:

    AWS_PROFILE=cic AWS_REGION=ca-central-1 IBOT_ENV=dev cdk deploy
