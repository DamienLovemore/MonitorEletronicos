import os, logging

from datetime import datetime

class Logger:
    def __init__(self, filename=None, logger_name=None, debug=None, rotation=None):
        time_now = datetime.now().strftime('%Y%m%d')

        dir = os.path.join("backend/logs")
        self.filename = "./{}/{}_{}.log".format(dir, time_now, filename)

        self.logger_name = logger_name if logger_name else filename
        self.logger = self.get_logger(rotation=rotation) if rotation else self.get_logger()
        self.debug = debug if debug else False

    def get_logger(self, rotation=False):
        logger = logging.getLogger(self.logger_name)
        filename = self.filename
        self.handler = logging.FileHandler(filename)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.handler.setFormatter(formatter)
        logger.addHandler(self.handler)
        logger.setLevel(logging.DEBUG)

        return logger

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)