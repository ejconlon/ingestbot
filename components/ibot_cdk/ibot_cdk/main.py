import json
import os.path
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass

import boto3
from aws_cdk import App, DefaultStackSynthesizer, Stack, StackSynthesizer
from aws_cdk.aws_apigateway import LambdaRestApi
from aws_cdk.aws_codebuild import Project, BuildEnvironment, BuildSpec, LinuxBuildImage
from aws_cdk.aws_codepipeline import Artifact, Pipeline
from aws_cdk.aws_codepipeline_actions import CodeBuildAction, GitHubSourceAction
from aws_cdk.aws_ec2 import SubnetConfiguration, SubnetType, Vpc
from aws_cdk.aws_iam import AccessKey, Policy, PolicyStatement, Role, User
from aws_cdk.aws_lambda import Code, Function, Runtime
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_secretsmanager import Secret
from ibot_prelude.parser import CustomArgumentParser


def lookup_account_id() -> str:
    """
    Resolves account id with boto3
    """
    return boto3.client('sts').get_caller_identity().get('Account')


@dataclass
class Params:
    """
    Parameters shared with the CDK bootstrap.
    """
    qualifier: str
    file_assets_bucket_name: str
    container_assets_repository_name: str


def load_params(env: str) -> Params:
    with open(f'ibot_cdk/bootstrap/params-{env}.json') as f:
        params_list = json.load(f)
    params_kv = {x['ParameterKey']: x['ParameterValue'] for x in params_list}
    return Params(
        qualifier=params_kv['Qualifier'],
        file_assets_bucket_name=params_kv['FileAssetsBucketName'],
        container_assets_repository_name=params_kv['ContainerAssetsRepositoryName']
    )


@dataclass
class Context:
    """
    Attributes here control the names and content of generated resources.
    We support named environments for multi-tenancy in the same account.
    """
    env: str
    region: str
    account_id: str
    params: Params


# Several name-generating functions follow. CloudFormation demands TitleCase
# for its resource names, but we use dash-case for other purposes.
# Generally, everything will be prefixed with `IbotDev` or `ibot-dev` for the `dev` env.


# TODO(ejconlon) Confirm that prefixing CF names is not required for multitenancy.
# If it is, then add it here with `qualify_dash`.
def title(dashed: str) -> str:
    return dashed.title().replace('-', '')


def prefix_dash(ctx: Context) -> str:
    return f'ibot-{ctx.env}'


def qualify_dash(ctx: Context, name: str) -> str:
    return f'{prefix_dash(ctx)}-{name}'


def code(name: str) -> Code:
    """
    Returns a reference to the built artifact of the given component name.
    """
    rel_path = f'../../.build/ibot_{name}.zip'
    path = os.path.abspath(rel_path)
    return Code.from_asset(path)


def handler(name: str) -> str:
    """
    Returns the default lambda handler name for the given component.
    """
    return f'ibot_{name}.handler.handler'


def cdk_role_name(ctx: Context, aspect: str) -> str:
    """
    Returns the bootstrapped role name.
    Aspect should be one of {deploy, file-publishing, lookup}
    """
    return f'cdk-{ctx.params.qualifier}-{aspect}-role-{ctx.account_id}-{ctx.region}'


def build_synth(ctx: Context) -> StackSynthesizer:
    """
    Constructs a stack synthesizer from our custom parameters (per-env).
    This allows us to share configuration with the bootstrap template and define
    custom bucket/repo names as well as custom asset prefixes.
    CDK requires that you build a synthesizer per stack, but each one will basically be identical.
    """
    cdk_prefix = 'cdk'
    return DefaultStackSynthesizer(
        qualifier=ctx.params.qualifier,
        file_assets_bucket_name=ctx.params.file_assets_bucket_name,
        bucket_prefix=f'{cdk_prefix}/',
        image_assets_repository_name=ctx.params.container_assets_repository_name,
        docker_tag_prefix=f'{cdk_prefix}-',
    )


def build_stack(ctx: Context, app: App, name: str) -> Stack:
    """
    Smart constructor for a stack with our custom synthesizer and naming scheme.
    """
    synth = build_synth(ctx)
    return Stack(app, title(f'{name}-stack'), synthesizer=synth)


def build_app(ctx: Context) -> App:
    """
    Builds our multi-stack App.
    On the command line you will `cdk synth` and `cdk deploy` one or more sub-stacks at a time.
    """
    app = App()

    # VPC Stack - base VPC resources
    vpc_stack = build_stack(ctx, app, 'vpc')
    vpc = Vpc(
        vpc_stack,
        title('vpc'),
        vpc_name=qualify_dash(ctx, 'vpc'),
        max_azs=1,
        # Just allocate one public subnet and no NAT gateways
        nat_gateways=None,
        nat_gateway_provider=None,
        subnet_configuration=[
            SubnetConfiguration(
                name='public',
                subnet_type=SubnetType.PUBLIC
            )
        ]
    )

    # CI Stack - Resources for CI: user, access key, role permissions
    ci_stack = build_stack(ctx, app, 'ci')
    ci_deploy_role = Role.from_role_name(
        ci_stack,
        title('ci-deploy-role'),
        role_name=cdk_role_name(ctx, 'deploy')
    )
    ci_file_role = Role.from_role_name(
        ci_stack,
        title('ci-file-role'),
        role_name=cdk_role_name(ctx, 'file-publishing')
    )
    ci_lookup_role = Role.from_role_name(
        ci_stack,
        title('ci-lookup-role'),
        role_name=cdk_role_name(ctx, 'lookup')
    )
    ci_policy = Policy(
        ci_stack,
        title('ci-policy'),
        policy_name=qualify_dash(ctx, 'ci-policy'),
        statements=[
            PolicyStatement(
                actions=["sts:AssumeRole"],
                resources=[
                    ci_deploy_role.role_arn,
                    ci_file_role.role_arn,
                    ci_lookup_role.role_arn,
                ]
            )
        ]
    )
    ci_user_name = qualify_dash(ctx, 'ci-user')
    ci_user = User(
        ci_stack,
        title('ci-user'),
        user_name=ci_user_name
    )
    ci_user.attach_inline_policy(ci_policy)
    ci_key = AccessKey(
        ci_stack,
        title('ci-key'),
        user=ci_user
    )
    ci_secret_description = f'Secret access key for {ci_user_name} access key {ci_key.access_key_id}'
    ci_secret = Secret(
        ci_stack,
        title('ci-secret'),
        secret_name=qualify_dash(ctx, 'ci-secret'),
        description=ci_secret_description,
        secret_string_value=ci_key.secret_access_key
    )

    # Repo Stack - secret for Github repo access
    repo_stack = build_stack(ctx, app, 'repo')
    repo_secret = Secret(
        repo_stack,
        title('repo-secret'),
        secret_name=qualify_dash(ctx, 'repo-secret'),
        description='Github Access Token with repo and admin:repo_hook scopes'
    )

    # Pipeline Stack - AWS CodePipeline resources
    # See https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codepipeline_actions/README.html#github
    pl_stack = build_stack(ctx, app, 'pipeline')
    pl_artifact_bucket = Bucket.from_bucket_name(
        pl_stack,
        title('file-assets-bucket'),
        bucket_name=ctx.params.file_assets_bucket_name
    )
    pl_deploy_pipeline = Pipeline(
        pl_stack,
        title('deploy-pipeline'),
        pipeline_name=qualify_dash(ctx, 'deploy-pipeline'),
        artifact_bucket=pl_artifact_bucket,
    )
    pl_source_output = Artifact(artifact_name=qualify_dash(ctx, 'source-output'))
    pl_source_action = GitHubSourceAction(
        action_name=qualify_dash(ctx, 'source-action'),
        owner='ejconlon',
        repo='ingestbot',
        oauth_token=repo_secret.secret_value,
        output=pl_source_output,
        branch=f'deploy-aws-{ctx.env}'
    )
    # See https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html
    pl_build_project = Project(
        pl_stack,
        title('build-project'),
        environment=BuildEnvironment(
            build_image=LinuxBuildImage.from_docker_registry('python:3.9.13')
        ),
        build_spec=BuildSpec.from_object({
            "version": "0.2",
            "phases": {
                "install": {
                    "commands": [
                        "echo installing"
                    ]
                },
                "build": {
                    "commands": [
                        "echo building"
                    ]
                }
            },
            "artifacts": {
            }
        })
    )
    pl_build_action = CodeBuildAction(
        action_name=qualify_dash(ctx, 'build-action'),
        project=pl_build_project,
        input=pl_source_output,
    )
    pl_deploy_pipeline.add_stage(
        stage_name='Source',
        actions=[pl_source_action]
    )
    pl_deploy_pipeline.add_stage(
        stage_name='Build',
        actions=[pl_build_action]
    )

    # API Stack - resources to serve the web app
    api_stack = build_stack(ctx, app, 'api')
    api_lambda = Function(
        api_stack,
        title('api-lambda'),
        function_name=qualify_dash(ctx, 'api-lambda'),
        runtime=Runtime.PYTHON_3_9,
        handler=handler('api'),
        code=code('api'),
        vpc=vpc,
        # Confirm that we don't need to access the internet
        # Otherwise we need a NAT gateway in our VPC
        allow_public_subnet=True
    )
    api_gateway = LambdaRestApi(
        api_stack,
        title('api-gateway'),
        rest_api_name=qualify_dash(ctx, 'api-gateway'),
        handler=api_lambda
    )
    return app


def build_parser() -> ArgumentParser:
    """
    Builds an `ArgumentParser` that contains enough information to put together a `Context`.
    Note that the `CustomArgumentParser` we use supports assigning arguments through
    environment variables named the same as the `metavar` attribute, so one would assign
    `IBOT_ENV` like this: `$ IBOT_ENV=dev cdk synth`
    """
    parser = CustomArgumentParser(prog='ibot_cdk')
    parser.add_argument('--env', metavar='IBOT_ENV', required=True)
    parser.add_argument('--region', metavar='AWS_REGION', required=True)
    return parser


def build_context(args: Namespace) -> Context:
    """
    Builds a context from args.
    """
    account_id = lookup_account_id()
    params = load_params(args.env)
    return Context(
        env=args.env,
        region=args.region,
        account_id=account_id,
        params=params
    )


def main():
    """
    Parses arguments and synthesizes CF for our parameterized application.
    """
    parser = build_parser()
    args = parser.parse_args()
    ctx = build_context(args)
    app = build_app(ctx)
    app.synth()


if __name__ == '__main__':
    main()
