from typing import Literal, Any
import datetime
import logging


def iso_timestamp_now() -> str:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    iso_now = now.isoformat()
    return iso_now

class Logger:
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.handler = logging.StreamHandler()
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.logger.propagate = False
    
    def info(self, msg: str, *values: object):
        self.logger.info(msg, *values)
    
    def warning(self, msg: str, *values: object):
        self.logger.warning(msg, *values)
    
    def error(self, msg: str, *values: object):
        self.logger.error(msg, *values)
    
    def debug(self, msg: str, *values: object):
        self.logger.debug(msg, *values)
    
    def critical(self, msg: str, *values: object):
        self.logger.critical(msg, *values)
    
    def exception(self, msg: str, *values: object):
        self.logger.exception(msg, *values)

    
