import json
import logging
import sys
from datetime import datetime
from typing import Optional


class Logger:
    def __init__(self,
                 level: Optional[int] = logging.INFO,
                 handler: Optional[logging.Handler] = None,
                 formatter: Optional[logging.Formatter] = None,
                 ):
        self.__level = level
        if not handler:
            handler = logging.StreamHandler(sys.stdout)
        if not formatter:
            formatter = logging.Formatter(
                fmt='%(asctime)s [%(levelname)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        handler.setFormatter(formatter)

        self.__logger = logging.getLogger("custom_logger")
        self.__logger.setLevel(level)

        self.__logger.handlers.clear()
        self.__logger.addHandler(handler)

        self.__logger.propagate = False

    def debug(self, message: str, **kwargs) -> None:
        extra = {"data": kwargs, "timestamp": datetime.now().isoformat()}
        return self.__logger.debug(message, extra=extra)

    def info(self, message: str, **kwargs) -> None:
        extra = {"data": kwargs, "timestamp": datetime.now().isoformat()}
        return self.__logger.info(message, extra=extra)

    def warn(self, message: str, **kwargs) -> None:
        extra = {"data": kwargs, "timestamp": datetime.now().isoformat()}
        self.__logger.warning(message, extra=extra)

    def error(self, message: str, **kwargs) -> None:
        extra = {"data": kwargs, "timestamp": datetime.now().isoformat()}
        return self.__logger.error(message, extra=extra)


class JSONCustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%dT%H:%M:%S')

        data = {
            "level": record.levelname,
            "timestamp": timestamp,
            "message": record.getMessage(),
        }

        if hasattr(record, 'data'):
            data.update(**record.data)

        if record.exc_info:
            data.update({
                "exception": self.formatException(record.exc_info),
            })

        return json.dumps(data)


class TextCustomFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

        log_message = f"{timestamp} | {record.levelname:8} | {record.getMessage()}"

        if hasattr(record, 'data') and record.data:
            pairs = ', '.join(f"{key}={value}" for key, value in record.data.items())
            log_message += f" | {pairs}"

        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"

        return log_message


