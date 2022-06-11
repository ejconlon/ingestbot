import json
import os.path
from argparse import ArgumentParser
from dataclasses import dataclass

from aws_cdk import App, DefaultStackSynthesizer, Stack, StackSynthesizer
from aws_cdk.aws_apigateway import LambdaRestApi
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_lambda import Code, Function, Runtime
from ibot_prelude.parser import CustomArgumentParser


@dataclass
class Context:
    env: str


def title(dashed: str) -> str:
    return dashed.title().replace('-', '')


def prefix_dash(ctx: Context) -> str:
    return f'ibot-{ctx.env}'


def qualify_dash(ctx: Context, name: str) -> str:
    return f'{prefix_dash(ctx)}-{name}'


def qualify_title(ctx: Context, name: str) -> str:
    return title(qualify_dash(ctx, name))


def code(name: str) -> Code:
    rel_path = f'../../.build/ibot_{name}.zip'
    path = os.path.abspath(rel_path)
    return Code.from_asset(path)


def handler(name: str) -> str:
    return f'ibot_{name}.handler.handler'


def build_synth(ctx: Context) -> StackSynthesizer:
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


def build_app(ctx: Context) -> App:
    app = App()
    synth = build_synth(ctx)
    stack = Stack(app, qualify_title(ctx, 'stack'), synthesizer=synth)
    vpc = Vpc(
        stack,
        qualify_title(ctx, 'vpc'),
        vpc_name=qualify_dash(ctx, 'vpc'),
        max_azs=1,
        nat_gateways=None
    )
    api_lambda = Function(
        stack,
        qualify_title(ctx, 'api-lambda'),
        function_name=qualify_dash(ctx, 'api-lambda'),
        runtime=Runtime.PYTHON_3_9,
        handler=handler('api'),
        code=code('api'),
        vpc=vpc
    )
    api_gateway = LambdaRestApi(
        stack,
        qualify_title(ctx, 'api-gateway'),
        rest_api_name=qualify_dash(ctx, 'api-gateway'),
        handler=api_lambda
    )
    return app


def build_parser() -> ArgumentParser:
    parser = CustomArgumentParser(prog='ibot_cdk')
    parser.add_argument('--env', metavar='IBOT_ENV', required=True)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    ctx = Context(env=args.env)
    app = build_app(ctx)
    app.synth()


if __name__ == '__main__':
    main()
