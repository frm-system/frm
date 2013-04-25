# -*- coding: utf-8 -*-

import logging
import pycurl
import urllib
import cStringIO as StringIO
import json



class ClientException(Exception):
    def __init__(self, s, response):
        if response:
            s += "\n" + str(response)
        super(ClientException, self).__init__(s)
        self.response = response

class ConnectionException(ClientException):
    pass

class InvalidResponse(ClientException):
    pass

class InvalidStatus(InvalidResponse):
    pass

class AttributeNotFound(InvalidResponse):
    pass

class AuthorizationFailed(ClientException):
    pass

class UploadException(ClientException):
    pass

class DownloadException(ClientException):
    pass

class FountainClient(object):
    method_get = "GET"
    method_post = "POST"

    WITHOUT_VERSION = -1

    class SpecialResponse(object):
        def __init__(self, response):
            self.response = response

        def __str__(self):
            return str(self.response)

    def _init_logger(self):
        self.logger = logging.getLogger(self.logger_name or 'ServiceClient')
        if not len(self.logger.handlers):
            hdlr = logging.FileHandler('client.log')
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            hdlr.setFormatter(formatter)
            self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.DEBUG)


    def __init__(self, server_url, login, password, version = 0, pretty = False, logger_name = None):
        self.server_url = server_url
        if self.server_url[-1] != '/':
            self.server_url += '/'
        self._login = login
        self._password = password
        self.version = version
        self.pretty = pretty
        self.logger_name = logger_name

        self._init_logger()
        self.logger.info("FountainClient created")
        self.curl = None

        self.response_time = {}

        self.token = None
        self.__response = None


    def send(self, method, command, parameters = None, headers = None, version = None, expect_status = 200):
        """
        Send command to the API backend

        :param str method: HTTP method
        :param str command: API call name
        :param dict parameters: Request parameters. By default None
        :param dict headers: Request headers. By default None
        :param int version: Version of API. If presented used instead of default Client version. By default None
        """
        if version == self.WITHOUT_VERSION:
            path = "%s/" % command
        else:
            version = self.version if version is None else version
            path = "%d/%s/" % (version, command)

        url = self.server_url + path
        parameters = parameters or {}

        try:
            if self.curl is None:
                self.curl = pycurl.Curl()
                self.curl.setopt(pycurl.SSL_VERIFYHOST, False)
                self.curl.setopt(pycurl.SSL_VERIFYPEER, False)
                self.curl.setopt(pycurl.FOLLOWLOCATION, 1)

            if method == self.method_get:
                if parameters:
                    url += "?" + urllib.urlencode(parameters)
                self.curl.setopt(pycurl.POST, 0)
            else:
                self.curl.setopt(pycurl.POST, 1)
                p = urllib.urlencode(parameters)
                self.curl.setopt(pycurl.POSTFIELDS, p)

            if headers:
                self.curl.setopt(pycurl.HTTPHEADER, [str("%s: %s") % (urllib.quote(k), v) for k,v in headers.iteritems()])

            self.logger.info("Request: %s [%s] %s" % (method, url, parameters) )
            self.curl.setopt(pycurl.URL, url)
            buff=StringIO.StringIO()
            self.curl.setopt(pycurl.WRITEFUNCTION, buff.write)

            self.curl.perform()
            code = int(self.curl.getinfo(pycurl.RESPONSE_CODE)) #refer here http://curl.haxx.se/libcurl/c/curl_easy_getinfo.html
            response = buff.getvalue()

            response_to_print = response
            if self.pretty:
                try:
                    parsed = json.loads( response )
                    response_to_print = "".join(( "\n", json.dumps(parsed, sort_keys=True, indent=4) ))
                except ValueError:
                    response_to_print = response

            self.logger.info("Reply code %d: %s" % (code, response_to_print))
            if isinstance(expect_status, int):
                expect_status = [expect_status]

            if code not in expect_status:
                raise InvalidStatus("Status: %s, but expected on of: %s" % (code, expect_status), response)

            self.__response = response
            return response
        except pycurl.error, e:
            self.logger.error("curl exception: %s" % e)
            raise ConnectionException(str(e), None)


    def login(self):
        """ Get auth token """
        pass

    def user_send(self,method, command, parameters = None, **kwargs):
        if not self.token:
            self.login()

        parameters = parameters or {}
        if kwargs:
            parameters.update(kwargs)

        self._dict_remove_none(parameters)
        if "auth_token" not in parameters:
            parameters["auth_token"] = str(self.token)

        return self.send(method=method, command = command, parameters=parameters)

    def _dict_remove_none(self, d):
        for k in d.keys():
            v = d[k]
            if v is None:
                del d[k]

    def _dict_to_utf8(self, d):
        for k,v in d.iteritems():
            if isinstance(v, unicode):
                d[k] = v.encode("utf-8")


    # ===============================================================================
    def get_version(self):
        return self.send(self.method_get, "version", version=self.WITHOUT_VERSION)

    def auth(self, email, password, deviceid):
        """
        Call auth method
        :param str email: User's unique identifier
        :param str password: User's password
        :param str deviceid: Device unique id
        :return: token
        """
        params = {
            "email"    : email,
            "password" : password,
            "deviceid" : deviceid,
        }
        result = self.send(self.method_get, "auth", parameters=params)

    def create_user(self, email, password, display_name=None):
        """

        :param email:
        :param password:
        :param display_name:
        :return:
        """
        params = {
            "email"    : email,
            "password" : password
        }
        if display_name:
            params["display_name"] = display_name

        result = self.send(self.method_post, "user", parameters=params)
