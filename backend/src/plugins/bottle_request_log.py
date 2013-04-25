import conf
import time
import traceback
from bottle import HTTPResponse, request

class RequestLogginingPlugin(object):
    name = 'sentry'

    def __init__(self, **kwargs):
        self.logger = None

    def setup(self,app):
        for other in app.plugins:
            if not isinstance(other, RequestLogginingPlugin):
                continue
        if self.logger is None:
            import logging
            self.logger = logging.getLogger("api")

    def apply(self,callback,context):
        def wrapper(*args,**kwargs):
            lines = []
            lines.append(request.method)
            lines.append(request.path)
            s = ",".join("(%s=%s)" % kv for kv in request.GET.iterallitems())
            lines.append(s)
            s = ",".join("(%s=%s)" % kv for kv in request.POST.iterallitems())
            lines.append(s)

            start = time.time()
            status = 0
            body = ""
            try:
                rv = callback(*args, **kwargs)
                if isinstance(rv, dict):
                    status = 200
                    body = str(rv)
                elif isinstance(rv, HTTPResponse):
                    status = rv.status
                    body = rv.body
                else:
                    ERROR("Incorrect reply [%s] for request %s" % (rv, request))
                    body = str(rv)
            except HTTPResponse, e:
                status = e.status
                body = e.body or getattr(e, "message", "")
                raise
            except Exception,e:
                ERROR("Unhandled exception: %s", e)
                ex = traceback.format_exc()
                WARNING(ex)
                raise

            finally:
                lines.append(str(status))
                worktime = time.time() - start
                lines.append("%.2g" % worktime)
                body = body[:conf.logging.reply_size]
                lines.append(body)
                self.logger.info("|".join(lines))
            return rv
        return wrapper

Plugin = RequestLogginingPlugin
