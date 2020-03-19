# -*- coding: utf-8 -*-

import os
import requests
import time

from json_api import json_load
from file_api import is_file_existing
from utils import Logger

def download_file_by_url(url, saveAs):
    """
    Download file by url.
    """
    Logger.debug("Url to download: {}".format(url))
    try:
        resp = requests.get(url)
        with open(saveAs, "wb") as f:
             f.write(resp.content)
    except Exception as e:
        Logger.error("Error orrcured while downloading file:")
        Logger.error(str(e))
        return False

    return True


class HttpClient():
    """
    A handler of http client to launch requests.
    """
    def __init__(self, doPost=True, headers={}, url=None, 
            host=None, port=None, path=None, data=None, name="httpClient"):
        """
        Initialization.
        """
        self.__doPost = doPost
        self.__headers = headers
        self.__url = url
        self.__host = host
        self.__port = port
        self.__path = path
        self.__reponse = None
        self.__data = data
        self.__name = name
        # TODO
        # add parameters
        # urlencoding

    @property
    def doPost(self):
        """
        Return doPost.
        """
        return self.__doPost

    @doPost.setter
    def doPost(self, value):
        """
        Set doPost.
        """
        if not isinstance(value, bool):
            Logger.error("Set doPost of http client failed.")
            return False

        self.__doPost = value
        return True

    @property
    def headers(self):
        """
        Return headers.
        """
        return self.__headers

    @headers.setter
    def headers(self, value):
        """
        Set headers.
        """
        if not isinstance(value, dict):
            Logger.error("Set headers of http client failed.")
            return False

        self.__headers = value
        return True

    @property
    def url(self):
        """
        Return url.
        """
        return self.__url

    @url.setter
    def url(self, value):
        """
        Set url.
        """
        if not isinstance(value, str):
            Logger.error("Set url of http client failed.")
            return False

        self.__url = value
        return True

    @property
    def host(self):
        """
        Return host.
        """
        return self.__host

    @host.setter
    def host(self, value):
        """
        Set host.
        """
        if not isinstance(value, str):
            Logger.error("Set host of http client failed.")
            return False

        self.__host = value.rstrip('/')
        return True

    @property
    def port(self):
        """
        Return port.
        """
        return self.__port

    @port.setter
    def port(self, value):
        """
        Set port.
        """
        if not isinstance(value, int) or value < 0 or value > 65535:
            Logger.error("Set port of http client failed.", value)
            return False

        self.__port = value
        return True

    @property
    def path(self):
        """
        Return path.
        """
        return self.__path

    @path.setter
    def path(self, value):
        """
        Set path.
        """
        if not isinstance(value, str):
            Logger.error("Set path of http client failed.")
            return False

        self.__path = value.lstrip('/')
        return True

    @property
    def data(self):
        """
        Return data.
        """
        return self.__data

    @data.setter
    def data(self, value):
        """
        Set data.
        """
        self.__data = value
        return True

    @property
    def name(self):
        """
        Return name.
        """
        return self.__name

    @name.setter
    def name(self, value):
        """
        Set name.
        """
        self.__name = value
        return True

    @property
    def response(self):
        """
        Return response.
        """
        return self.__response

    @property
    def respStatusCode(self):
        """
        Return response status code.
        """
        if self.__response is None:
            Logger.error("Launch request first.")
            return None

        return self.__response.status_code

    @property
    def respHeaders(self):
        """
        Return response headers.
        """
        if self.__response is None:
            Logger.error("Launch request first.")
            return None

        return self.__response.headers

    @property
    def respData(self):
        """
        Return response data.
        """
        if self.__response is None:
            Logger.error("Launch request first.")
            return None

        return self.__response.content

    def launch_request(self, waitTime=0):
        """
        Lauch request.
        """
        self.__response = None

        url = self.url
        if not url:
            url = "http://{}:{}/{}".format(self.host, self.port, self.path)

        Logger.debug("Launch request to: {}".format(url))
        if self.doPost:
            self.__response = requests.post(url, headers = self.headers, 
                    data = self.data)
        else:
            self.__response = requests.get(url, headers = self.headers)

        if waitTime:
            time.sleep(waitTime)

        # TODO
        # catch exception and set return

    def reset(self):
        """
        Reset internal vars.
        """
        self.__doPost = True
        self.__headers = {}
        self.__url = None
        self.__host = None
        self.__port = None
        self.__path = None
        self.__reponse = None
        self.__data = None

    def load_conf_file(self, confFile):
        """
        Load request configure file.
        """
        confData = json_load(confFile)
        return self.load_conf_data(confData)

    def load_conf_data(self, confData):
        """
        Load request configure.
        """
        self.reset()

        if confData is None:
            return False

        if "headers" in confData:
            self.headers = confData["headers"]

        if "url" in confData:
            self.url = confData["url"]

        if "host" in confData:
            self.host = confData["host"]

        if "port" in confData:
            self.port = confData["port"]

        if "path" in confData:
            self.path = confData["path"]

        return True

