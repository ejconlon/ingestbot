# ingestbot

WIP - An example data processing + web frontend stack on AWS with

* multi-component repo
* dev/CI tasks in standardized Makefile targets
* deployment to AWS with API Gateway + Lambda + whatever else
* CI with Github Actions

(Javascript to follow...)

## Development environment + project structure

This project assumes you have a recent `python3` installed along with the `cdk` and `awscli` utilities.

The subdirectories of the `components` directory are _libraries_ or _applications_. Libraries can be depended on by other components, and applications can be packaged for execution and deployment.

It is not expected that any two components share dependency graphs. In fact, they need not even share language or build system. One is expected to work in the component directory and manage installed dependencies for each. For Python components `make build` will ensure a `venv` is created and kept up-to-date. `make test` runs several automated checks.

`make package` assembles a zip file in the top level `.build` directory with an entrypoint shell script inside. Do be careful unzipping this file, as there is no single top-level folder (thank AWS Lambda for this).
