# -*- coding: utf-8 -*-

import difflib
import json
import os

_TYPE_STR = type(str())
_TYPE_BYTES = type(bytes())
_TYPE_DICT = type(dict())
_TYPE_LIST = type(list())

def _is_str(inputData):
    """
    note   : Return if input data is a instance of "str".
    param  :
        inputData   : Input data.
    return : The conclusion.
    """
    typeInput = type(inputData)
    return typeInput == _TYPE_STR or typeInput == _TYPE_BYTES


def _is_list(inputData):
    """
    note   : Return if input data is a instance of "list".
    param  :
        inputData   : Input data.
    return : The conclusion.
    """
    return type(inputData) == _TYPE_LIST


def _is_dict(inputData):
    """
    note   : Return if input data is a instance of "dict".
    param  :
        inputData   : Input data.
    return : The conclusion.
    """
    return type(inputData) == _TYPE_DICT


def _stringlize_list(inputList):
    """
    note   : Stringlize a input list.
    param  :
        inputData   : Input list.
    return : Stringlized list.
    """
    result = ""

    if not inputList:
        return result

    for e in inputList:
        if _is_list(e):
            s = _stringlize_list(e)
        elif _is_dict(e):
            s = _stringlize_dict(e)
        else:
            s = str(e)

        result = result + s

    return result


def _stringlize_dict(inputDict):
    """
    note   : Stringlize input dict.
    param  :
        inputData   : Input dict.
    return : Stringlized dict.
    """
    result = ""

    if not inputDict:
        return result

    for k in sorted(inputDict.keys()):
        v = inputDict[k]
        if _is_list(v):
            s = _stringlize_list(v)
        elif _is_dict(v):
            s = _stringlize_dict(v)
        elif _is_str(v):
            # It seems got a problem that it depend the input data. 
            # Recommend to trans data in ensure_ascii=False
            #s = v.encode('utf-8')
            s = v
        else:
            s = str(v)

        result = result + s

    return result


def _get_sort_key(inputData):
    """
    note   : Stringlize input data.
    param  :
        inputData   : Input data.
    return : Stringlized data.
    """
    if _is_list(inputData):
        result = _stringlize_list(inputData)
    elif _is_dict(inputData):
        result = _stringlize_dict(inputData)
    else:
        result = str(inputData)

    return result


def _sort_list(inputList):
    """
    note   : Sort input list.
    param  :
        inputData   : Input list.
    return : Sorted list(copy).
    """
    length = len(inputList)
    tmpList_A = []
    midMap = {}
    for i in range(length):
        tmpList_A.append(_sort_list_in_data(inputList[i]))
        midMap[i] = _get_sort_key(tmpList_A[i])

    sortedIndex = sorted(\
            midMap.items(), \
            key = lambda x:x[1], \
            reverse = False)
    tmpList_B = []
    for pair in sortedIndex:
        tmpList_B.append(tmpList_A[pair[0]])

    return tmpList_B


def _sort_dict(inputDict):
    """
    note   : Sort input dict.
    param  :
        inputData   : Input dict.
    return : Sorted dict(copy).
    """
    tmpDict = {}
    for key, value in inputDict.items():
        if _is_list(value):
            sortedValue = _sort_list(value)
        elif _is_dict(value):
            sortedValue = _sort_dict(value)
        else:
            sortedValue = value

        tmpDict[key] = sortedValue

    return tmpDict


def _sort_list_in_data(inputData):
    """
    note   : Sort input data.
    param  :
        inputData   : Input data.
    return : Sorted data(copy).
    """
    if _is_list(inputData):
        return _sort_list(inputData)
    elif _is_dict(inputData):
        return _sort_dict(inputData)
    else:
        return inputData


def compare_data(inData_A, inData_B, diffFilePrefix):
    """
    note   : Sort and compre if inData_A equals to inData_B.
    param  :
        inData_A   : Input data.
        inData_B   : Another input data.
        diffFilePrefix  : Output diff file prefix.
    return :
        True    : inData_A equals to inData_B.
        False   : inData_A does NOT equals to inData_B.
    """

    dict_A = _sort_list_in_data(inData_A)
    dict_B = _sort_list_in_data(inData_B)

    str_A = json.dumps(dict_A, indent = 4, sort_keys=True, ensure_ascii=False)
    str_B = json.dumps(dict_B, indent = 4, sort_keys=True, ensure_ascii=False)

    if str_A == str_B:
        return True

    fileName = "{}_1.data".format(diffFilePrefix)
    with open(fileName, "w") as f:
        f.write(str_A)

    fileName = "{}_2.data".format(diffFilePrefix)
    with open(fileName, "w") as f:
        f.write(str_B)

    return False


def show_stringlized_dict_diff(strA, strB):
    """
    note   : Show the diff of two stringlized dicts as style of "diff".
    param  :
        strA    : one stringlized dict
        strB    : another stringlized dict
    """

    if (not strA) or (not strB):
        return

    if strA == strB:
        print("Inputs are equivalent.")
        return True

    d = difflib.Differ()
    diff = d.compare(strA.split(","), strB.split(","))
    print("".join(list(diff)))


def show_dict_diff(inDataA, inDataB):
    """
    note   : Show the diff of two dicts as style of "diff".
    param  :
        strA    : one dict
        strB    : another dict
    """
    dictA = _sort_list_in_data(inDataA)
    dictB = _sort_list_in_data(inDataB)

    strA = json.dumps(dictA, indent = 4, sort_keys=True)
    strB = json.dumps(dictB, indent = 4, sort_keys=True)

    show_stringlized_dict_diff(strA, strB)


def compare_data_json(jsonFileA, jsonFileB):
    """
    Compare two json files.
    """
    dictA = {}
    dictB = {}

    with open(jsonFileA, "r") as f:
        try:
            dictA = json.load(f, encoding = 'utf-8')
        except Exception as e:
            print("Error orrcured while decoding {}.".format(jsonFileA))

    with open(jsonFileB, "r") as f:
        try:
            dictB = json.load(f, encoding = 'utf-8')
        except Exception as e:
            print("Error orrcured while decoding {}.".format(jsonFileB))

    return compare_data(dictA, dictB, "diff_")

