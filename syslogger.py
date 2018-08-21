import logging

SYSLOG_LEVELS = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2,
    logging.FATAL: 1
}

class SyslogFilter(logging.Filter):
    """
    This filter prepends the syslog level corresponding with the python log level
    to all log messages
    """
    def filter(self, record):
        record.sysloglevel = SYSLOG_LEVELS[record.levelno]
        return True


class Syslogger(logging.Logger):
    def __init__(self, name=__name__, stream=None):
        super().__init__(name)

        log_handler = logging.StreamHandler(stream=stream)
        log_handler.setLevel(logging.NOTSET)
        log_formatter = logging.Formatter('<%(sysloglevel)d> %(message)s')
        log_handler.setFormatter(log_formatter)
        self.addHandler(log_handler)

        log_filter = SyslogFilter()
        self.addFilter(log_filter)

        # Send everything to syslog and leave filtering to other programs (e.g. journalctl -p <level>)
        self.setLevel(logging.NOTSET)


if __name__ == '__main__':
    logger = Syslogger('TestLogger')
    for levelname in SYSLOG_LEVELS.keys():
        print(levelname)
