import logging
from .config import get_Settings
from logtail import LogtailHandler
import sys
def setup_logger():
    logger = logging.getLogger("request")

    # FORMATTER
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # CONSOLE HANDLER (always present)
    File_handler = logging.FileHandler("logs/request.log")

    #set the format of the handler
    File_handler.setFormatter(formatter)
    # add to handlers
    logger.handlers = [File_handler]

    #set logger level
    logger.setLevel(logging.INFO)
    
    return logger