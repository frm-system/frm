import os
import yaml

class ConfigItem(dict):

    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                self[a] = [ConfigItem(x) if isinstance(x, dict) else x for x in b]
            else:
                self[a] = ConfigItem(b) if isinstance(b, dict) else b

    def __getattribute__(self, key):
        if dict.has_key(self, key):
            return self[key]
        return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        if dict.has_key(self, key):
            return dict.__setitem__(self, key, value)
        return object.__setattr__(self, key, value)


class Configs(object):
    obj = None

    def __new__(cls, *args):
        if cls.obj is None:
            cls.obj = object.__new__(cls, *args)
        return cls.obj

    def __init__(self, defaults):
        self._defaults = defaults
        app_path = os.path.dirname(os.path.dirname(__file__))
        self.config_path = os.path.join(app_path, "configs")

        config_file = os.environ.get('CONFIG_FILE', 'dev.yaml')

        self.data = None # public property!

        self._current_dir = os.path.dirname(config_file) if os.path.abspath(config_file) else ""
        self.data = self._load_yaml_from_file(config_file)

        self._check_data(self.data)

        self.data = ConfigItem(self.data)

    def _find_path(self, path):
        if os.path.isabs(path):
            if not os.path.isfile(path):
                raise Exception("Can't find file: %s" % path)
            return path

        if self._current_dir:
            p = os.path.join(self._current_dir, path)
            if os.path.isfile(p):
                return p

        p = os.path.join(self.config_path, path)
        if os.path.isfile(p):
            return p
        raise Exception("Can't find file: %s" % path)


    def _load_yaml_from_file(self, path):
        path = self._find_path(path)
        data = yaml.load(open(path))

        result_data = {}

        for key, val in data.iteritems():
            if key == 'extends':
                if isinstance(val, str) or isinstance(val, unicode):
                    val = [val]
                if isinstance(val, list):
                    for item in val:
                        if not (isinstance(item, str) or isinstance(item, unicode)):
                            continue
                        include_data = self._load_yaml_from_file(item)
                        self._recursiveupdate(result_data, include_data)

        self._recursiveupdate(result_data, data)
        return result_data

    def _check_data(self, data, path = None):
        path = path or []
        if isinstance(data, dict):
            for key, val in data.iteritems():
                data[key] = self._check_data(val, path + [str(key)])
        elif isinstance(data, list):
            for key in range(len(data)):
                data[key] = self._check_data(data[key], path + [str(key)])
        elif isinstance(data, str) or isinstance(data, unicode):
            data = self._update_consts(data, path)

        return data

    def _path_to_str(self, path):
        def tostr(p):
            if isinstance(p, str):
                return "."+p
            else:
                return "[%s]" % (p,)

        l = (tostr(p) for p in path)
        s = "".join(l)
        if s[0] == ".":
            s = s[1:]
        return s


    def _update_consts(self, val, path):
        path = path or None
        for k, rep in self._defaults.iteritems():
            if k in val:
                val = val.replace(k, rep)
        if val == "__FIX_ME__":
            raise Exception("Mandatory parameter %s is not overridden" % (self._path_to_str(path)))
        return val

    def _recursiveupdate(self, a, b, path=None):
        if path is None:
            path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self._recursiveupdate(a[key], b[key], path + [str(key)])
                else:
                    a[key] = b[key]
            else:
                a[key] = b[key]
        return a
