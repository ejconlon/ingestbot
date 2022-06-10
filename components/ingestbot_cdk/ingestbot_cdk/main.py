from argparse import ArgumentParser

from aws_cdk.core import App, Stack


def qualify(env: str, name: str) -> str:
    return f'ibot-{env}-{name}'


def build_app(env: str) -> App:
    app = App()
    stack = Stack(app, qualify(env, 'stack'))
    return app


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='ingestbot_cdk')
    parser.add_argument('--env', default='dev')
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    app = build_app(args.env)
    app.synth()


if __name__ == '__main__':
    main()
