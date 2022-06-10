"""
Some useful argparse extensions
"""

import argparse
import logging
import os
import shlex
from enum import Enum
from typing import Optional

DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d -- %(message)s'


def configure_logging(level: Optional[str] = None) -> None:
    if level is None:
        real_level = DEFAULT_LOG_LEVEL
    else:
        real_level = level.upper()
    logging.basicConfig(
        format=DEFAULT_LOG_FORMAT,
        level=real_level
    )


class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """ An argparse help formatter that includes metavars in output. """

    def _get_help_string(self, action):
        help = super()._get_help_string(action)
        if action.metavar is not None:
            help += ' [env: {}]'.format(action.metavar)
        return help


class CustomArgumentParser(argparse.ArgumentParser):
    """ `ArgumentParser` that can read environment variables declared as `metavar`s. """

    def __init__(self, *, formatter_class=CustomHelpFormatter, **kwargs):
        super().__init__(formatter_class=formatter_class, **kwargs)

    def _add_action(self, action):
        if action.metavar is not None:
            env_default = os.environ.get(action.metavar)
            if env_default is not None:
                action.default = env_default
                action.required = False
        return super()._add_action(action)


class EnumAction(argparse.Action):
    """
    Argparse action for handling Enums
    See https://stackoverflow.com/a/60750535
    """
    def __init__(self, **kwargs):
        # Pop off the type value
        enum = kwargs.pop("type", None)

        # Ensure an Enum subclass is provided
        if enum is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")
        if not issubclass(enum, Enum):
            raise TypeError("type must be an Enum when using EnumAction")

        # Generate choices from the Enum
        kwargs.setdefault("choices", tuple(e.name for e in enum))

        super(EnumAction, self).__init__(**kwargs)

        self._enum = enum

    def __call__(self, parser, namespace, values, option_string=None):
        # Convert value back into an Enum
        enum = self._enum[values]
        setattr(namespace, self.dest, enum)


def parser_with_profile(**kwargs) -> argparse.ArgumentParser:
    """ A `CustomArgumentParser` with `--profile` reading `AWS_PROFILE` from environment variables. """
    parser = CustomArgumentParser(**kwargs)
    parser.add_argument('--profile', metavar='AWS_PROFILE', help='optional AWS profile name')
    parser.add_argument('--log-level', metavar='LOG_LEVEL', help=f'log level (default: {DEFAULT_LOG_LEVEL})')
    return parser


def parse_args(parser: argparse.ArgumentParser, arg_str: Optional[str] = None) -> argparse.Namespace:
    """
    Parse args, optionally from a string.
    Useful from a gunicorn entrypoint.
    """
    if arg_str is not None:
        arg_list = shlex.split(arg_str)
        return parser.parse_args(arg_list)
    else:
        return parser.parse_args()


def parse_args_and_configure(parser: argparse.ArgumentParser, arg_str: Optional[str] = None) -> argparse.Namespace:
    """ Parse args and configure logging in one call. """
    args = parse_args(parser=parser, arg_str=arg_str)
    configure_logging(level=getattr(args, 'log_level', None))
    return args
