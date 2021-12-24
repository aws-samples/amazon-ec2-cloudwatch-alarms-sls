# pylint: disable=logging-format-interpolation, redefined-outer-name, redefined-builtin, bad-option-value, import-error, missing-module-docstring, missing-function-docstring

import logging
import uuid


class Logger:
    """
    Custom logger
    """
    def __init__(self):
        log = logging.getLogger()
        for h in log.handlers:
            h.setFormatter(logging.Formatter("[%(levelname)s]:%(message)s"))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self._id = uuid.uuid4().hex

    def set_new_uuid(self):
        self._id = uuid.uuid4().hex

    def get_uuid(self):
        return self._id

    def set_uuid(self, logger_id):
        self._id = logger_id

    def error(self, msg):
        self.logger.error("{}: {}".format(self._id, msg))

    def info(self, msg):
        self.logger.info("{}: {}".format(self._id, msg))

    def warn(self, msg):
        self.logger.warning("{}: {}".format(self._id, msg))

    def debug(self, msg):
        self.logger.debug("{}: {}".format(self._id, msg))
