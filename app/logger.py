import logging
from logging.handlers import RotatingFileHandler


def configure_logging(write_logger_level, stream_logger_level):
    form = '%(levelname)-8s [%(asctime)s] - %(filename)s:%(lineno)d - %(message)s'
    rothand = RotatingFileHandler(filename='logs/log.log', maxBytes=1000000, backupCount=10)
    rothand.setFormatter(logging.Formatter(fmt=form))
    rothand.setLevel(write_logger_level)
    stream = logging.StreamHandler()
    logging.basicConfig(level=stream_logger_level, format=form, handlers=[stream, rothand])
