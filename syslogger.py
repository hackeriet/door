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
  This filter adds a key containing the syslog level corresponding with the python log level
  """
  def filter(self, record):
    record.sysloglevel = SYSLOG_LEVELS[record.levelno]
    return True

def getLogger(logger=None):
  """
  Traditional python logging logger with prefixed log level number to use with syslog or systemd journal
  """
  # Use passed in logger or create a default one
  if logger is None:
    logger = logging.getLogger(__name__)

  syslog_filter = SyslogFilter()
  logger.addFilter(syslog_filter)

  syslogFormat = logging.Formatter('<%(sysloglevel)d> %(message)s')
  handler = logging.StreamHandler()
  handler.setFormatter(syslogFormat)

  logger.addHandler(handler)
  # Send everything to syslog and leave filtering to other programs (e.g. journalctl -p <level>)
  logger.setLevel(logging.DEBUG)
  return logger

