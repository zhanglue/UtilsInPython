# -*- coding: utf-8 -*-

import codecs
import json
import os

from file_api import is_file_existing
from utils import Logger

def json_load(jsonFile):
    """
    Convert json file to python data.
    """
    if not is_file_existing(jsonFile):
        Logger.error("Json file is not found: {}".format(jsonFile))
        return None

    with codecs.open(jsonFile, encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            Logger.error("Json load failed: {}".format(str(e)))
            return None


def json_loads(inputStr):
    """
    Load str to dict.
    """
    try:
        result = json.loads(inputStr)
    except Exception as e:
        Logger.error("Json load failed: {}".format(str(e)))
        return None

    return result


def json_dumps(inputData):
    """
    Dump json data.
    """
    if isinstance(inputData, str):
        return inputData

    try:
        formatedString = json.dumps(inputData,
                indent = 4, sort_keys = True, ensure_ascii = False)
    except Exception as e:
        Logger.error("Json dump failed: {}".format(str(e)))
        return None

    return formatedString


def pyData_to_json_file(inputData, outputFile, appendFlag=False):
    """
    Convert python data to json file.
    """
    openMode = "w"
    if appendFlag:
        openMode = "a"

    try:
        with open(outputFile, openMode) as f:
            f.write(json_dumps(inputData)+"\n")
    except Exception as e:
        Logger.error("Write data to json file failed: {}".format(str(e)))
        return False

    return True

