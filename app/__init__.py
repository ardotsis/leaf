import logging.handlers
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
fmt = "[%(asctime)s] [%(levelname)s] %(message)s [%(name)s - %(funcName)s:%(lineno)d]"
stream_handler.setFormatter(logging.Formatter(fmt))
logger.addHandler(stream_handler)
