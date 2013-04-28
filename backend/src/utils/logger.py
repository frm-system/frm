# -*- coding: utf-8 -*-

import conf
import logging

_logging_levels = ["debug", "info", "warning", "error", "critical"]
_logger = None


def prepare_parameters(params):
    exception_words = [
        # 'password',
    ]
    mask_symbols = '*' * 8
    result = ["(%s=%s)" % (k, v if not k in exception_words else mask_symbols)
              for k, v in params.iteritems()]
    return ",".join(result)

def initLogger(name, force = False):
    global _logger
    if _logger is not None and not force:
        return

    from logging.config import dictConfig
    dictConfig(conf.logging)

    _logger = logging.getLogger(name)

    _levels = {}
    for x in _logging_levels:
        level = x.upper()
        __builtins__[level] = getattr(_logger, x)
        _levels[level] = getattr(logging, level)

    def log_enabled(level):
        l = _levels.get(level)
        if l is None:
            return False
        return _logger.isEnabledFor(l)

    __builtins__["LOG_ENABLED"] = log_enabled

def console(message, *args):
    if args:
        message = message % args
    print message

def initFakeMethods():
    for x in _logging_levels:
        level = x.upper()
        if level not in __builtins__:
            __builtins__[level] = console

initFakeMethods()
