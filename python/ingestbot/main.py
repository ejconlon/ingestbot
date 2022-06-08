"""
This is the development entrypoint that runs the webapp with the embedded
Flask server. For production, we will use API Gateway + Lambda and aws-wsgi.
If you want to deploy on ELB/ECS, use gunicorn with another entrypoint.
"""

from argparse import ArgumentParser
from flask import Flask
from ingestbot.app import build_app
from ingestbot.parser import parse_args_and_configure, parser_with_profile
from typing import Optional


def build_parser() -> ArgumentParser:
    parser = parser_with_profile(prog='ingestbot')
    parser.add_argument(
        '--default-name',
        default='traveler',
        help='example arg: default name to respond with'
    )
    return parser


def build_app_from_args(arg_str: Optional[str] = None) -> Flask:
    parser = build_parser()
    args = parse_args_and_configure(parser, arg_str)
    return build_app(default_name=args.default_name)


def main() -> None:
    app = build_app_from_args()
    app.run(debug=True)


if __name__ == '__main__':
    main()
