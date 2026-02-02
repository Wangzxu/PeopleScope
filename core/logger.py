import logging
from logging.handlers import RotatingFileHandler
from core.config import LOG_PATH, LOG_LEVEL

def setup_logger(name="PeopleScope"):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] "
        "[%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
    )

    # 控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 文件日志
    file_handler = RotatingFileHandler(
        LOG_PATH / "people_scope.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # 错误日志
    error_handler = RotatingFileHandler(
        LOG_PATH / "error.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger
