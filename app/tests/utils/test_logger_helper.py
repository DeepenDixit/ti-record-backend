import logging
import sys

from app.utils.logger_helper import RequestIDFilter, current_request_id_ctx, get_logger


def test_get_logger():
    """Test get_logger function"""
    logger = get_logger()

    assert len(logger.handlers) == 2
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream == sys.stdout

    formatter = handler.formatter
    assert formatter._fmt == (  # pylint: disable=protected-access
        "%(asctime)s %(levelname)s [%(name)s, %(request_id)s] "
        "--- %(module)s::%(funcName)s::%(lineno)d : %(message)s"
    )

    filters = logger.filters
    assert len(filters) == 2
    assert isinstance(filters[0], RequestIDFilter)

    current_request_id_ctx.set("test_request_id")
    log_record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None,
    )
    logger.handle(log_record)
    assert log_record.request_id == "test_request_id"  # pylint: disable=no-member
