import logging

def to_function(logger, level_str):
    levels = {"debug": logger.debug, "info": logger.info,
              "warning": logger.warning, "error": logger.error, "critical": logger.critical}
    return levels[level_str.lower()]

def to_level(level_str):
    levels = {"debug": logging.DEBUG, "info": logging.INFO,
              "warning": logging.WARNING, "error": logging.ERROR, "critical": logging.CRITICAL}
    return levels[level_str.lower()]


def create_logger(name, level, fh_name, fh_level=None,
                  format="%(name)s-%(levelname)s-%(message)s"):
    """
    Creates a logger with given name, level, fh_
    :param name:
    :param level:
    :param fh_name:
    :param fh_level:
    :param format:
    :return:
    """

    # temporary to simplify messages for debugging
    # format="%(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(to_level(level))

    # if no handler level supplied, use same as logger level
    fh_level = level if fh_level is None else fh_level

    handler = logging.FileHandler("dsDraw/" + fh_name)
    handler.setLevel(to_level(fh_level))

    formatter = logging.Formatter(format)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
