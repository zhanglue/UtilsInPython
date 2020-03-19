# -*- coding: utf-8 -*-

from google.protobuf import text_format
from google.protobuf.descriptor import FieldDescriptor as FD
import os
import sys

from file_api import generate_temp_file
from file_api import is_file_existing
from file_api import remove_file
from shell_api import get_env_var
from json_api import pyData_to_json_file

# Import pb2 classes before using.
PB_FILES_ROOT = get_env_var("PB_FILES_ROOT")
if PB_FILES_ROOT:
    PB_FILES_ROOT = os.path.abspath(PB_FILES_ROOT)
    if PB_FILES_ROOT not in os.sys.path:
        os.sys.path.insert(0, PB_FILES_ROOT)
    PB_IMPORTING = get_env_var("PB_IMPORTING")
    if PB_IMPORTING:
        for i in PB_IMPORTING.split("\\n"):
            exec(i)

def _pyData_to_pbHandler(cls, pyData, strict=False):
    """
    Convert pyData to pbHandler of cls.
    "cls" here is "_concrete_class" but string.
    """
    # Declare pbHandler according to cls.
    pbHandler = cls()

    for field in pbHandler.DESCRIPTOR.fields:
        if field.label != field.LABEL_REQUIRED:
            continue
        if not field.has_default_value:
            continue
        if field.name not in pyData:
            msg = "Field \"{}\" missing from descriptor dictionary.".format(field.name)
            raise ConvertException(msg)

    field_names = set([field.name for field in pbHandler.DESCRIPTOR.fields])
    if strict:
        for key in pyData.keys():
            if key not in field_names:
                msg = "Key \"{}\" can not be mapped to field in {} class.".format\
                        (key, type(pbHandler)) 
                raise ConvertException(msg)

    for field in pbHandler.DESCRIPTOR.fields:
        if field.name not in pyData:
            continue

        msg_type = field.message_type
        if field.label == FD.LABEL_REPEATED:
            if field.type == FD.TYPE_MESSAGE:
                for sub_py in pyData[field.name]:
                    item = getattr(pbHandler, field.name).add()
                    item.CopyFrom(_pyData_to_pbHandler(msg_type._concrete_class, sub_py))
            else:
                for sub_py in pyData[field.name]:
                    getattr(pbHandler, field.name).append(sub_py)
        else:
            if field.type == FD.TYPE_MESSAGE:
                value = _pyData_to_pbHandler(msg_type._concrete_class, pyData[field.name])
                getattr(pbHandler, field.name).CopyFrom(value)
            elif field.type == FD.TYPE_BYTES:
                setattr(pbHandler, field.name, pyData[field.name].encode('utf8'))
            else:
                setattr(pbHandler, field.name, pyData[field.name])

    return pbHandler


def pyData_to_pbHandler(clsName, pyData, strict=False):
    """
    Convert pyData to pbHandler of clsName.
    "clsName" here is a string.
    """
    cls = eval(clsName)
    if not cls:
        return None

    return _pyData_to_pbHandler(cls, pyData, strict)


def pbHandler_to_pbString(pbHandler):
    """
    Convert pbHandler to pbString.
    """
    return pbHandler.SerializeToString()


def pbString_to_pbFile(pbString, fileName=None):
    """
    Write pbString to pbFile.
    If "fileName" was not specified, write to a temp file.
    """
    if not fileName:
        fileName = generate_temp_file()

    with open(fileName, "wb") as f:
        #f.write(pbString + "\n")
        f.write(pbString)

    return str(fileName)


def pyData_to_pbString(clsName, pyData, strict=False):
    """
    Convert pyData to pbString. 
    """
    pbHandler = pyData_to_pbHandler(clsName, pyData, strict)
    return pbHandler_to_pbString(pbHandler)


def pbHandler_to_pbFile(pbHandler, fileName=None):
    """
    Convert pbHandler to pbFile.
    """
    pbString = pbHandler_to_pbString(pbHandler)
    return pbString_to_pbFile(pbString, fileName)


def pyData_to_pbFile(clsName, pyData, fileName=None, strict=False):
    """
    Convert pyData to pbFile.
    """
    pbHandler = pyData_to_pbHandler(clsName, pyData, strict)
    pbString = pbHandler_to_pbString(pbHandler)
    return pbString_to_pbFile(pbString, fileName)


def pbFile_to_pbString(pbFile):
    """
    Convert pbFile to pbStrings.
    """
    if not is_file_existing(pbFile):
        return ""

    pbString = ""
    with open(pbFile, "r") as f:
        while True:
            lines = f.readlines(10000)
            if not lines:
                break
            else:
                for line in lines:
                    pbString += line

    if pbString:
        pbString = pbString[:-1]
    return pbString


def pbString_to_pbHandler(clsName, pbString):
    """
    Convert pbString to pbHandler.
    """
    try:
        pbHandler = eval(clsName + "()")
        pbHandler.ParseFromString(pbString)

        return pbHandler
    except:
        return None


_EXTENSION_CONTAINER = "___X"

_TYPE_CALLABLE_MAP = {
    FD.TYPE_DOUBLE: float,
    FD.TYPE_FLOAT: float,
    FD.TYPE_INT32: int,
    FD.TYPE_INT64: int,
    FD.TYPE_UINT32: int,
    FD.TYPE_UINT64: int,
    FD.TYPE_SINT32: int,
    FD.TYPE_SINT64: int,
    FD.TYPE_FIXED32: int,
    FD.TYPE_FIXED64: int,
    FD.TYPE_SFIXED32: int,
    FD.TYPE_SFIXED64: int,
    FD.TYPE_BOOL: bool,

    FD.TYPE_STRING: str,
    #FD.TYPE_STRING: lambda b: b.decode("string_escape"),
    #FD.TYPE_STRING: lambda b: b.encode("utf-8"),

    FD.TYPE_BYTES: str,
    #FD.TYPE_BYTES: lambda b: b.encode("base64"),
    #FD.TYPE_BYTES: lambda b: b.encode("utf-8"),
    #FD.TYPE_BYTES: lambda b: b.decode("string_escape"),

    FD.TYPE_ENUM: int,
}


def _repeated(type_callable):
    return lambda value_list: [type_callable(value) for value in value_list]


def _enum_label_name(field, value):
    return field.enum_type.values_by_number[int(value)].name


def _get_field_value_adaptor(
        pbHandler, 
        field, 
        typeCallableMap=_TYPE_CALLABLE_MAP, 
        useEnumEabels=False):
    """
    Get value of field.
    """
    if field.type == FD.TYPE_MESSAGE:
        # recursively encode protobuf sub-message
        return lambda pbHandler: pbHandler_to_pyData(
                pbHandler,
                typeCallableMap = typeCallableMap,
                useEnumEabels = useEnumEabels)

    if useEnumEabels and field.type == FD.TYPE_ENUM:
        return lambda value: _enum_label_name(field, value)

    if field.type in typeCallableMap:
        return typeCallableMap[field.type]

    raise TypeError("Field {}.{} has unrecognised type id {}".format(
        pbHandler.__class__.__name__, field.name, field.type))


def pbHandler_to_pyData(
        pbHandler, 
        typeCallableMap=_TYPE_CALLABLE_MAP, 
        useEnumEabels=False):
    """
    Convert pbHandler to pyData.
    """
    resultDict = {}
    extensions = {}
    for field, value in pbHandler.ListFields():
        typeCallable = _get_field_value_adaptor(
                pbHandler, 
                field, 
                typeCallableMap, 
                useEnumEabels)

        if field.label == FD.LABEL_REPEATED:
            typeCallable = _repeated(typeCallable)

        if field.is_extension:
            extensions[str(field.number)] = typeCallable(value)
            continue

        resultDict[field.name] = typeCallable(value)

    if extensions:
        resultDict[_EXTENSION_CONTAINER] = extensions

    return resultDict


def pbFile_to_pbHandler(clsName, pbFile):
    """
    Convert pbFile to pbHandler.
    """
    pbString = pbFile_to_pbString(pbFile)
    return pbString_to_pbHandler(clsName, pbString)


def pbString_to_pyData(clsName, pbString):
    """
    Convert pbString to pyData.
    """
    pbHandler = pbString_to_pbHandler(clsName, pbString)
    if not pbHandler:
        return None
    return pbHandler_to_pyData(pbHandler)


def pbFile_to_pyData(clsName, pbFile):
    """
    Convert pbFile to pyData.
    """
    pbString = pbFile_to_pbString(pbFile)
    pbHandler = pbString_to_pbHandler(clsName, pbString)
    if not pbHandler:
        return None
    return pbHandler_to_pyData(pbHandler)


def pbDebugFile_to_pbHandler(clsName, pbDebugFile):
    """
    Convert pbDebugFile to pbHandler.
    """
    result = None
    if not is_file_existing(pbDebugFile):
        return result

    with open(pbDebugFile, "r") as f:
        pbHandler = eval(clsName + "()")
        text_format.Parse(f.read().encode("utf-8"), pbHandler)

    return pbHandler


def pbDebugFile_to_pyData(clsName, pbDebugFile):
    """
    Convert pbDebugFile to pyData.
    """
    result = None

    pbHandler = pbDebugFile_to_pbHandler(clsName, pbDebugFile)
    if not pbHandler:
        return result

    return pbHandler_to_pyData(pbHandler)


def pbDebugFile_to_json_file(clsName, pbDebugFile, outputFile):
    """
    Convert pbDebugFile to json_file.
    """
    pyData = pbDebugFile_to_pyData(clsName, pbDebugFile)
    pyData_to_json_file(pyData, outputFile)

