import conf
import time
import traceback
import logging
import json
from bottle import HTTPResponse, request, Response, response
from utils.request import local_properties
from utils.logger import prepare_parameters
from utils.network import get_client_address


class RequestLogginingPlugin(object):
    name = 'request_logging'
    logger = logging.getLogger("api")

    def setup(self,app):
        for other in app.plugins:
            if not isinstance(other, RequestLogginingPlugin):
                continue

    @classmethod
    def get_post_to_str(cls, request):
        gets = prepare_parameters(request.GET)
        try:
            posts = prepare_parameters(request.POST)
        except KeyError, e:
            WARNING("Post parameters extract failed: {}".format(e))
            posts = "<can't extract>"
        return gets, posts

    @classmethod
    def log(cls, request, rv, worktime, status=None, body=None):
        if isinstance(worktime, float):
            worktime = "%.2f" % worktime
        gets, posts = cls.get_post_to_str(request)

        lines = []
        try:
            if rv is not None:
                if isinstance(rv, dict):
                    status = 200
                    if conf.debug:
                        body = json.dumps(rv)
                        rv = json.dumps(rv, indent=4)
                    else:
                        body = rv = json.dumps(rv)
                    response.content_type = 'application/json'
                elif isinstance(rv, Response):
                    status = rv.status
                    body = rv.body or getattr(rv, "message", "")
                else:
                    ERROR("Incorrect response [%s] for request %s" %
                          (rv, cls.request_to_str(request)))
                    body = str(rv)
                    status = 200

            body = body[:conf.logging.reply_size]
            body = body.replace("\n", " ")
            user_token = None
            tokenid, role, email = "", "", ""
            if hasattr(local_properties, 'user_token'):
                user_token = getattr(local_properties, 'user_token', '')
                delattr(local_properties, 'user_token')
            # if user_token:
            #     tokenid, role, email = str(user_token.tokenid), User.roles[user_token.role], user_token.email

            ip = get_client_address(request.environ)
            lines = [ip,
                     role,
                     tokenid,
                     email,
                     request.method,
                     request.path, gets, posts, str(status),
                     worktime, body,
                     ]
            cls.logger.info("|".join(lines))
        except Exception, e:
            trace = traceback.format_exc()
            WARNING("Exception during logging '{}': {}".format(lines, trace))
            ERROR("Exception '%s' during logging api call: %s %s %s %s " %
                  (e, request.method, request.path, gets, posts))
        return rv

    @classmethod
    def request_to_str(cls, request):
        g, p = cls.get_post_to_str(request)
        return " ".join((request.method, request.path, g, p))

    def apply(self, callback, context):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                rv = callback(*args, **kwargs)
                rv = self.log(request, rv, time.time() - start)
                return rv
            except HTTPResponse:
                raise
            except Exception, e:
                WARNING("Unhandled exception: '%s' during processing %s" %
                        (e, self.request_to_str(request)))
                ex = traceback.format_exc()
                WARNING(ex)
                raise
        return wrapper

Plugin = RequestLogginingPlugin
