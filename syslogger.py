"""
This class enables proper syslog level logging to a journald enabled system
by prefixing all log lines with the syslog level.

See `man systemd.journal-fields` PRIORITY field for a brief description.
"""
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
    Prepends the syslog level corresponding to the python logging log level
    to all lines
    """
    def filter(self, record):
        record.sysloglevel = SYSLOG_LEVELS[record.levelno]
        return True


class Syslogger(logging.Logger):
    def __init__(self, name=__name__, stream=None, **kwargs):
        super().__init__(name, **kwargs)

        formatter = logging.Formatter('<%(sysloglevel)d> %(message)s')

        handler = logging.StreamHandler(stream=stream) # Allow mocking the output stream
        handler.setFormatter(formatter)

        self.addHandler(handler)
        self.addFilter(SyslogFilter())

