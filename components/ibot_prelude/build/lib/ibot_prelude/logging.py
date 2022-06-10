import logging
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
