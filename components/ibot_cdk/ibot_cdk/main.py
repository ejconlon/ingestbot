import json
import os.path
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass

from aws_cdk import App, DefaultStackSynthesizer, Stack, StackSynthesizer
from aws_cdk.aws_apigateway import LambdaRestApi
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_lambda import Code, Function, Runtime
from ibot_prelude.parser import CustomArgumentParser


@dataclass
class Context:
    """
    Parameters here control the names and content of generated resources.
    For now, we support named environments for multi-tenancy in the same account.
    """
    env: str


# Several name-generating functions follow. CloudFormation demands TitleCase
# for its resource names, but we use dash-case for other purposes.
# Generally, everything will be prefixed with `IbotDev` or `ibot-dev` for the `dev` env.


def title(dashed: str) -> str:
    return dashed.title().replace('-', '')


def prefix_dash(ctx: Context) -> str:
    return f'ibot-{ctx.env}'


def qualify_dash(ctx: Context, name: str) -> str:
    return f'{prefix_dash(ctx)}-{name}'


def qualify_title(ctx: Context, name: str) -> str:
    return title(qualify_dash(ctx, name))


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


def build_synth(ctx: Context) -> StackSynthesizer:
    """
    Constructs a stack synthesizer from our custom parameters (per-env).
    This allows us to share configuration with the bootstrap template and define
    custom bucket/repo names as well as custom asset prefixes.
    CDK requires that you build a synthesizer per stack, but each one will basically be identical.
    """
    with open(f'ibot_cdk/bootstrap/params-{ctx.env}.json') as f:
        params_list = json.load(f)
    params_kv = {x['ParameterKey']: x['ParameterValue'] for x in params_list}
    cdk_prefix = 'cdk'
    return DefaultStackSynthesizer(
        qualifier=params_kv.get('Qualifier'),
        file_assets_bucket_name=params_kv.get('FileAssetsBucketName'),
        bucket_prefix=f'{cdk_prefix}/',
        image_assets_repository_name=params_kv.get('ContainerAssetsRepositoryName'),
        docker_tag_prefix=f'{cdk_prefix}-',
    )


def build_stack(ctx: Context, app: App, name: str) -> Stack:
    """
    Smart constructor for a stack with our custom synthesizer and naming scheme.
    """
    synth = build_synth(ctx)
    return Stack(app, qualify_title(ctx, f'{name}-stack'), synthesizer=synth)


def build_app(ctx: Context) -> App:
    """
    Builds our multi-stack App.
    On the command line you will `cdk synth` and `cdk deploy` one or more sub-stacks at a time.
    """
    app = App()
    # VPC Stack
    vpc_stack = build_stack(ctx, app, 'vpc')
    vpc = Vpc(
        vpc_stack,
        qualify_title(ctx, 'vpc'),
        vpc_name=qualify_dash(ctx, 'vpc'),
        max_azs=1,
        nat_gateways=None
    )
    # API Stack
    api_stack = build_stack(ctx, app, 'api')
    api_lambda = Function(
        api_stack,
        qualify_title(ctx, 'api-lambda'),
        function_name=qualify_dash(ctx, 'api-lambda'),
        runtime=Runtime.PYTHON_3_9,
        handler=handler('api'),
        code=code('api'),
        vpc=vpc
    )
    api_gateway = LambdaRestApi(
        api_stack,
        qualify_title(ctx, 'api-gateway'),
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
    return parser


def build_context(args: Namespace) -> Context:
    """
    Builds a context from args.
    """
    return Context(env=args.env)


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
