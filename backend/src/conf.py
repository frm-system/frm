import copy
import os
from utils import yamlconfigs as conf
from utils.network import get_hostname

def _config_post_processing(data):
    data = _update_logging_section(data)
    return data

def _update_logging_section(d):
    logging = d["logging"]
    path     = _defaults["__LOGS_PATH__"]
    handlers = logging["handlers"]
    loggers  = logging["loggers"]
    formatters=logging["formatters"]
    failures_error_handler = "failures_error_handler"
    sentry_handler = "sentry"

    syslog = logging.get("syslog", False) and platform.system().lower() != "windows"
    if not syslog:
        if not os.path.exists(path):
            os.makedirs(path)
    enable_debug = logging.get("enable_debug", True) or d["debug"]

    for logger_name, prop in logging.get("__loggers", {}).iteritems():
        level, filename, formatter, params = prop
        handler_name = logger_name + "handler"
        # create formatter if syslog mode
        if syslog:
            f = copy.deepcopy(formatters[formatter])
            formatter = "%s_fmp" % logger_name
            f["format"] = "FNT%s %s" % (filename, f["format"]) # adding filename before format string
            formatters[formatter] = f

        # create handler
        if syslog:
            handler = copy.deepcopy(logging["default_handler_syslog"])
        else:
            handler = copy.deepcopy(logging["default_handler"])
            handler["filename"] = os.path.join(path, "%s.log" % filename)
            if params:
                handler.update(params)

        if level.upper() == "DEBUG" and not enable_debug:
            # change level to info if __enable_debug is false
            level = "INFO"
        handler["level"] = level
        handler["formatter"] = formatter
        handlers[handler_name] = handler
        handler_names = [handler_name]

        if logger_name == "failures":
            handler = copy.deepcopy(handler)
            handler["level"] = "WARNING"
            handlers[failures_error_handler] = handler
        else:
            handler_names.append(failures_error_handler)
            handler_names.append(sentry_handler)

        logger = {"handlers": handler_names, "level": level}
        loggers[logger_name] = logger

    return d

APPLICATION_PATH = os.path.dirname(__file__)

_defaults = {
    '__LOGS_PATH__': os.environ.get('LOGS_PATH', os.path.join(APPLICATION_PATH, 'log')),
    '__APPLICATION_PATH__': APPLICATION_PATH,
    '__HOST__': get_hostname(),
}

globals().update(_config_post_processing(conf.Configs(_defaults).data))


