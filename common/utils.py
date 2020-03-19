# -*- coding: utf-8 -*-

import configparser
import logging
import logging.handlers
import os
import shutil
import sys

def try_exception(func):
    """
    A decorator.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            Logger.error(str(e))
            return None

    return wrapper


class Conf():
    """
    Config manager.
    """
    _conf = None
    _show_error = True

    def catch_exception(func):
        """
        A decorator.
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if Conf._show_error:
                    Logger.error("Get conf failed: {} {}".format(func, args))
                return None

        return wrapper

    @classmethod
    def switch_error_log(cls, b):
        """
        Switch error log.
        """
        cls._show_error = b

    @classmethod
    def initialize(cls, pathConfFile):
        """
        Initialization.
        """
        cls._conf = None
        try:
            config = configparser.ConfigParser()
            config.read(pathConfFile)
        except Exception as e:
            if cls._show_error:
                Logger.error("Parse config file failed: " + pathConfFile)
                Logger.error(e)
            cls._conf = None
            return False

        cls._conf = config
        return True

    @classmethod
    @catch_exception
    def get_section(cls, section):
        """
        """
        return cls._conf._sections[section]

    @classmethod
    @catch_exception
    def get(cls, *args, **kwargs):
        """
        """
        return cls._conf.get(*args, **kwargs)

    @classmethod
    @catch_exception
    def get_int(cls, *args, **kwargs):
        """
        """
        return cls._conf.getint(*args, **kwargs)

    @classmethod
    @catch_exception
    def get_float(cls, *args, **kwargs):
        """
        """
        return cls._conf.getfloat(*args, **kwargs)

    @classmethod
    @catch_exception
    def get_boolean(cls, *args, **kwargs):
        """
        """
        return cls._conf.getboolean(*args, **kwargs)


class Logger():
    """
    Static class.
    """
    _logger = None
    _conf = {
                "force_reset": True,
                "level": 1, # INFO
                "path": "",
                "prefix": "log",
                "remove_former": True,
                "log_level_sync": True,
                "forbidden_std_output": False,
                "forbidden_log_files": False,
                "independent_log_file_we": True,
            }

    @classmethod
    def set_conf_by_dict(cls, confDict):
        """
        Set conf by dict.
        """
        cls._conf.update(confDict)

    @classmethod
    def merge_confs(cls):
        """
        Merge configs between class and Conf.
        """
        Conf.switch_error_log(False)
        if Conf.get_section("log"):
            for item in [
                    "force_reset",
                    "remove_former",
                    "log_level_sync",
                    "forbidden_std_output",
                    "forbidden_log_files",
                    "independent_log_file_we",
                    ]:
                t = Conf.get_boolean("log", item)
                if t is None:
                    continue
                cls._conf[item] = t

            for item in [
                    "path",
                    "prefix",
                    ]:
                t = Conf.get("log", item)
                if t is None:
                    continue
                cls._conf[item] = t

            t = Conf.get_int("log", "level")
            if t is not None:
                if t < 0 or t > 3:
                    print("ERROR: log->level is invalid in conf file.")
                    sys.exit(1)
                else:
                    cls._conf["level"] = t

        Conf.switch_error_log(True)

        if "LOG_LEVEL" in os.environ:
            try:
                logLevelInShell = int(os.environ["LOG_LEVEL"])
            except Exception as e:
                print("ERROR: \"LOG_LEVEL\" is not a interger.")
                sys.exit(1)

            if logLevelInShell not in range(4):
                print("ERROR: \"LOG_LEVEL\" is out of range [0, 1, 2, 3].")
                sys.exit(1)

            cls._conf["level"] = logLevelInShell

        cls._conf["level"] = (cls._conf["level"] + 1) * 10

        return True

    @classmethod
    def initialize(cls):
        """
        Initialization.
        """
        cls.merge_confs()
        confDict = cls._conf

        if cls._logger:
            if not confDict["force_reset"]:
                return True
            logging.shutdown()
            importlib.reload(logging)

        # Generate base logger.
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")

        if not confDict["forbidden_std_output"]:
            # Set stream logger.
            streamHandler = logging.StreamHandler()
            streamHandler.setLevel(confDict["level"])
            streamHandler.setFormatter(formatter)
            logger.addHandler(streamHandler)

        if confDict["forbidden_log_files"] or not confDict["path"]:
            cls._logger = logger
            return True

        # Set file logger:
        # 1. There are two log files: regression.log.debug/regression.log.we
        # 2. Log files devide to 100MB for each log file.
        # 3. It keeps last 10 log files.

        try:
            if os.path.exists(confDict["path"]):
                if confDict["remove_former"] and os.path.exists(confDict["path"]):
                    shutil.rmtree(confDict["path"])
                    os.makedirs(confDict["path"])
            else:
                os.makedirs(confDict["path"])

            logFileName = "{}/{}".format(confDict["path"], confDict["prefix"])
            fileHandler = logging.handlers.RotatingFileHandler(
                    logFileName,
                    maxBytes = 100 * 1024 * 1024,
                    backupCount = 10)
            if confDict["log_level_sync"]:
                fileHandler.setLevel(confDict["level"])
            else:
                fileHandler.setLevel(logging.DEBUG)
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
        except IOError as e:
            logger.error("Genrate log file in {} failed.".format(confDict["path"]))
            logger.error(e)
            sys.exit(2)

        if not confDict["independent_log_file_we"]:
            cls._logger = logger
            return True

        try:
            logFileName = "{}/{}.we".format(confDict["path"], confDict["prefix"])
            fileHandler = logging.handlers.RotatingFileHandler(
                    logFileName,
                    maxBytes = 100 * 1024 * 1024,
                    backupCount = 10)
            fileHandler.setLevel(logging.WARNING)
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
        except IOError as e:
            logger.error("Genrate log file in {} failed.".format(confDict["path"]))
            logger.error(e)
            sys.exit(2)

        cls._logger = logger
        return True

    @classmethod
    def debug(cls, *msgs):
        """
        Log debug.
        """
        if not Logger._logger:
            Logger.initialize()
        cls._logger.debug("".join(map(str, msgs)))

    @classmethod
    def info(cls, *msgs):
        """
        Log info.
        """
        if not Logger._logger:
            Logger.initialize()
        cls._logger.info("".join(map(str, msgs)))

    @classmethod
    def warning(cls, *msgs):
        """
        Log warning.
        """
        if not Logger._logger:
            Logger.initialize()
        cls._logger.warning("".join(map(str, msgs)))

    @classmethod
    def error(cls, *msgs):
        """
        Log error.
        """
        if not Logger._logger:
            Logger.initialize()
        cls._logger.error("".join(map(str, msgs)))


