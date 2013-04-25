import conf

import bottle
import json

from userapi import UserApi
from utils.logger import initLogger
from utils.request import add_routes, get, Api
from plugins.bottle_sentry import SentryPlugin
from plugins.bottle_request_log import RequestLogginingPlugin

initLogger("backend")

application = bottle.Bottle()

def default_error_handler(error):
    res = {"message": error.body or error.message, }
    if conf.debug and error.traceback:
        res["traceback"] = error.traceback

    if error.status_code == 405 and "Method not allowed" in error.body:
        INFO("Method %s %s is not allowed" % (bottle.request.method, bottle.request.path))
        if conf.debug:
            allow = ["%s %s" % (r.method, r.rule) for r in application.routes]
            DEBUG("List of allowed methods: %s" % "\n".join(allow))
            res["allowed_methods"] = allow

    from bottle import response
    response.content_type = 'application/json'
    response.body = json.dumps(res)
    return response

application.default_error_handler = default_error_handler

def find_last_created_file():
    import os
    from datetime import datetime
    path = os.path.dirname(__file__)
    t = 0
    for f in os.listdir(path):
        try:
            t = max(t, os.path.getmtime(f))
        except OSError:
            pass
    d = datetime.fromtimestamp(t)
    return d.strftime('%Y-%m-%d %H:%M:%S')

class OtherApi(Api):
    prefix  = ""

    @get("version/", no_version=True, no_prefix=True)
    def get_version(self):
        """
        Returns current version of the code

        :return str version: version of the code
        :return str date: date of release
        :return str build_number: the build number
        """
        date = getattr(conf, "release_date", None) or find_last_created_file()
        build_number = getattr(conf, "build_number", 0)
        return {"version": conf.version, "date": date, "build_number": build_number}

    @get("regions/", no_version=True, no_prefix=True)
    def get_regions(self):
        """
        Returns list of available regions

        :return list regions: List of available regions
        """
        return {"regions": conf.regions.keys()}

def init():
    add_routes(application, UserApi())
    add_routes(application, OtherApi())
    application.install(RequestLogginingPlugin())

init()

def main():
    sentry = SentryPlugin(**conf.sentry)
    application.install(sentry)
    bottle.run(app=application, host='localhost', port=8080, debug=conf.debug, reloader=conf.debug)

if __name__ == '__main__':
    main()

