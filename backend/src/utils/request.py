import functools
import inspect
from bottle import request, HTTPError
import threading

local_properties = threading.local()

class ValidateError(Exception):
    def __init__(self, error):
        super(ValidateError, self).__init__(error)

class Api(object):
    prefix = None
    version = 0

def check_params(all_parameters = False, **types):
    def decorate(f):
        farg, _, _, def_params = inspect.getargspec(f)
        if def_params is None: def_params = []
        farg = farg[:len(farg) - len(def_params)]

        param_info = [(par, ptype, par in farg) for par, ptype in types.iteritems()]

        def validate(kwargs):
            getparam = request.params.get
            for par, ptype, required in param_info:
                value = getparam(par)
                if not value: # None or empty str
                    if required:
                        error = "%s requires the parameter %s" % (wrapper.__name__, par)
                        raise HTTPError(status = 400, body = error)
                    continue
                try:
                    kwargs[par] = ptype(value)
                except ValidateError, e:
                    raise HTTPError(status = 400, body=str(e))
                except Exception:
                    error = "Cannot convert parameter %s to %s" % (par, ptype.__name__)
                    raise HTTPError(status = 400, body=str(error))

        @functools.wraps(f)
        def wrapper(*args, **kargs):
            validate(kargs)
            if all_parameters:
                return f(*args, all_parameters = kargs, **kargs)
            else:
                return f(*args, **kargs)

        return wrapper
    return decorate

def route(path, method='GET', no_version = False, no_prefix = False):
    def wrapper(f):
        f._path = path
        f._method = method
        f._no_version = no_version
        f._no_prefix = no_prefix
        return f
    return wrapper

def get(path, no_version = False, no_prefix = False):
    return route(path, "GET", no_version, no_prefix)

def post(path, no_version = False, no_prefix = False):
    return route(path, "POST", no_version, no_prefix)

def put(path, no_version = False, no_prefix = False):
    return route(path, "PUT", no_version, no_prefix)

def delete(path, no_version = False, no_prefix = False):
    return route(path, "DELETE", no_version, no_prefix)

def add_routes(app, obj):
    for k in dir(obj):
        if not k.startswith("_"):
            v = getattr(obj, k)
            if hasattr(v, '_path') and hasattr(v, '_method'):
                version = "%s/" % obj.version if not v._no_version else ""
                prefix    = "%s/" % obj.prefix if not v._no_prefix else ""
                path = "/%s%s%s" % (version, prefix, v._path)
                app.route(path, v._method)(v)
