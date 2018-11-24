import logging
import logging.handlers

logfile = "log/finder.log"


def setupLogger():
    logger = logging.getLogger("admin-finder")
    logger.setLevel(logging.DEBUG)

    Formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
    LogHandler = logging.handlers.RotatingFileHandler(
        logfile,
        delay = 0,
        encoding = None,
        backupCount = 10,
        maxBytes = 50 * 1024 * 1024,
    )
    LogHandler.setFormatter(Formatter)

    StreamHandler = logging.StreamHandler()
    StreamHandler.setFormatter(Formatter)

    logger.addHandler(LogHandler)
    logger.addHandler(StreamHandler)
    return logger

