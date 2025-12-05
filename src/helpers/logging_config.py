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
    console_handler = LogtailHandler(source_token="Nrpmoa8MJeRg3gh7Zdv2fH21")
    File_handler = logging.FileHandler("logs/request.log")

    #set the format of the handler
    console_handler.setFormatter(formatter)
    File_handler.setFormatter(formatter)
    # add to handlers
    logger.handlers = [console_handler, File_handler]

    #set logger level
    logger.setLevel(logging.INFO)
    
    return logger