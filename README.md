# ingestbot

WIP - An example data processing + web frontend stack on AWS with

* A multi-component repo
* Dev/CI tasks in standardized Makefile targets
* Deployment to AWS with API Gateway + Lambda + whatever else
* CI with Github Actions

(Javascript to follow...)

## Development environment + project structure

This project assumes you have a recent `python3` installed along with the `cdk` and `awscli` utilities.

The subdirectories of the `components` directory are _libraries_ or _applications_. Libraries can be depended on by other components, and applications can be packaged for execution and deployment.

It is not expected that any two components share dependency graphs. In fact, they need not even share language or build system. One is expected to work in the component directory and manage installed dependencies for each. It is expected that they share a few `make` targets like `build`, `test`, `package`, etc.

For Python components `make build` will ensure a `venv` is created and kept up-to-date. `make test` runs several automated checks. `make package` assembles a zip file in the top level `.build` directory with an entrypoint shell script inside. Please be careful unzipping this file, as there is no single top-level folder (this is to get around AWS Lambda working-directory restrictions).

The `support/python` directory contains language support files for the Python components. Note that the `Makefiles` in the component directories define the component name and include the appropriate `Makefile.app` or `Makefile.lib` from the language support directory.

## Deployment

This project uses CDK to manage deployments and supports multi-tenancy through an "environment" parameter. Work in the `components/ibot_cdk` directory when invoking `cdk`. You may need to prepend the following commands with `AWS_REGION=... AWS_PROFILE=...` or ensure that you have the relevant settings already present in your shell. (In particular, `AWS_REGION` is necessary in the environment.)

To start deploying, you'll want to bootstrap your environment. You can do that for the `dev` environment with

    make bootstrap-create-dev

This applies the bootstrap template frozen as `ibot_cdk/bootstrap/template.yml` to your environment with parameters from `ibot_cdk/bootstrap/params-dev.json`. (The parameters in the JSON file will also be read in later to resolve asset buckets, container repos, and more.) Once you do this, you don't have to do it again for that particular environment.

To resolve the `aws-cdk-lib` dependency, you must invoke `make build` to ensure a virtual environment is created. Once that's done, you can invoke `cdk` to your heart's content; however, you may find that blindly running it sputters out, as we do still need to pass the environment parameter. So here's how to do it:

    IBOT_ENV=dev cdk synth

CDK will report that several stacks are present; simply pass the name of any one of them or `\*` to select them all:

    IBOT_ENV=dev cdk synth VpcStack
    IBOT_ENV=dev cdk synth \*

Use `cdk deploy` instead to create/update the resources, or `cdk destroy` to delete them.

## CI

This repo is setup to use Github Actions for CI. The workflows are in `.github/workflows` - those with the `root-` prefix are triggered on branch pushes and those with the `sub-` prefix are reusable workflows triggered by those roots.

The `root-integrate` workflow is run on every pull request and every merge to `master`. It basically runs `make build test` in each component subdirectory.

You can use `./scripts/push_deploy.sh dev` to trigger a CI deployment workflow (`root-deploy-dev`) through a push to the `deploy-dev` branch. Note that in this repository setup there is an environment with the appropriate AWS credentials to make this happen (specifically, `AWS_{REGION,ACCESS_KEY_ID,SECRET_ACCESS_KEY}`). The access key id and secret were obtained by first manually creating the CI user:

    IBOT_ENV=dev cdk deploy CiStack

Then querying Secrets Manager for the key from the description and the secret from the value:

    aws secretsmanager list-secrets
    aws secretsmanager get-secret-value --secret-id ibot-dev-ci-secret

(You would have to do this for each new environment you configured.)
