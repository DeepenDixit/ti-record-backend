import contextvars
import logging
import sys

from app.core.config import settings

current_request_id_ctx = contextvars.ContextVar(
    "request_id", default="No Request ID Found"
)


class RequestIDFilter(logging.Filter):
    """
    Request id filter
    """

    def filter(self, record):
        """
        Add request id to logs
        """
        record.request_id = current_request_id_ctx.get()
        return True


def get_console_handler(formatter) -> logging.Handler:
    """
    A console log handler to print logs in console
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    return console_handler


def get_logger():
    """
    Create logger for the application and returns the same
    """

    formatter_pattern = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s, %(request_id)s] "
        "--- %(module)s::%(funcName)s::%(lineno)d : %(message)s"
    )

    logger_obj = logging.getLogger(settings.APP_LOGGER_NAME)
    logger_obj.setLevel(settings.APP_LOG_LEVEL)
    logger_obj.propagate = False
    logger_obj.addHandler(get_console_handler(formatter_pattern))
    logger_obj.addFilter(RequestIDFilter())
    logging.getLogger("multipart.multipart").setLevel(settings.APP_LOG_LEVEL)

    return logger_obj


app_logger = get_logger()
