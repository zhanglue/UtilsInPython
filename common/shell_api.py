# -*- coding: utf-8 -*-

import os
import psutil
import sys

def get_env_var(varName, isInt=False):
    """
    Get shell environment var.
    """
    result = None

    if varName not in os.environ:
        return result

    result = os.environ[varName]

    if isInt:
        result = int(result)

    return result


def kill_process_by_name(procName):
    """
    Kill processes by name.
    """
    if not procName:
        return

    for proc in psutil.process_iter():
        if proc.name() != procName:
            continue
        try:
            proc.kill()
        except:
            return


def kill_process_by_cmd(cmd, strict=True, onceFlag=True):
    """
    Kill processes by start cmd.
    """
    if not cmd:
        return

    cmd = cmd.strip()
    for proc in psutil.process_iter():
        cmdTmp = " ".join(proc.cmdline()).strip()

        result = False
        if strict:
            result = cmd == cmdTmp
        else:
            result = cmd in cmdTmp

        if not result:
            continue

        proc.kill()
        if onceFlag:
            break


def is_cmd_alive(cmdList):
    """
    Return if process of cmd alive.
    """
    for proc in psutil.process_iter():
        if cmdList == ''.join(proc.cmdline()):
            return True

    return False


def is_cmdline_alive(cmdList):
    """
    Return if process of cmdList alive.
    """
    for proc in psutil.process_iter():
        try:
            if cmdList == proc.cmdline():
                return True
        except NoSuchProcess:
            continue

    return False

