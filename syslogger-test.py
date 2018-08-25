import unittest
from io import StringIO

import logging
from syslogger import Syslogger, SyslogFilter, SYSLOG_LEVELS

class SysloggerTestCase(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.logger = Syslogger(name='test', stream=self.stream)

    def tearDown(self):
        self.stream.close()

    def level_stoi(self, s):
        """ Convert string level name to syslog number
        """
        return SYSLOG_LEVELS.get(logging.getLevelName(s.upper()))

    def test_message_prepender_debug(self):
        self.logger.debug('hello')
        logged = self.stream.getvalue()
        self.assertEqual(logged, '<%s> hello\n' % SYSLOG_LEVELS.get(logging.DEBUG))

    def test_message_prepender_info(self):
        self.logger.info('hello')
        logged = self.stream.getvalue()
        self.assertEqual(logged, '<%s> hello\n' % SYSLOG_LEVELS.get(logging.INFO))

    def test_message_prepender_warning(self):
        self.logger.warning('hello')
        logged = self.stream.getvalue()
        self.assertEqual(logged, '<%s> hello\n' % SYSLOG_LEVELS.get(logging.WARNING))

    def test_message_prepender_error(self):
        self.logger.error('hello')
        logged = self.stream.getvalue()
        self.assertEqual(logged, '<%s> hello\n' % SYSLOG_LEVELS.get(logging.ERROR))

    def test_message_prepender_critical(self):
        self.logger.critical('hello')
        logged = self.stream.getvalue()
        self.assertEqual(logged, '<%s> hello\n' % SYSLOG_LEVELS.get(logging.CRITICAL))

    def test_passes_level_kwarg_to_base_logger(self):
        self.logger = Syslogger(name='test-custom', stream=self.stream, level=logging.CRITICAL)
        self.logger.info('Hello world!')
        logged = self.stream.getvalue().strip()
        self.assertEqual(logged, '')

