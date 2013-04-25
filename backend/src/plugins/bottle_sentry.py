from bottle import HTTPError
from raven import Client

class SentryPlugin(object):
    name = 'sentry'

    def __init__(self, dsn, **kwargs):
        self.client = None
        self.kwargs = kwargs
        self.dsn = dsn

    def setup(self,app):
        for other in app.plugins:
            if not isinstance(other, SentryPlugin):
                continue
        if self.client is None:
            self.client = Client(self.dsn, **self.kwargs)

    def apply(self,callback,context):
        def wrapper(*args,**kwargs):
            try:
                rv = callback(*args, **kwargs)
            except Exception, e:
                if not isinstance(e, HTTPError):
                    self.client.captureException()
                raise
            return rv
        return wrapper

Plugin = SentryPlugin
