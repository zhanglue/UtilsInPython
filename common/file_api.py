# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import tarfile
import tempfile

from utils import Logger

def path_join(*pathList):
    """
    Join path strings and return absolute path.
    """
    return get_abspath(os.path.join(*pathList))


def get_abspath(path):
    """
    Return absolute path.
    """
    return os.path.abspath(path)


def generate_temp_file():
    """
    Return a temp file.
    """
    return tempfile.mktemp()


def make_link(source, target, force=False):
    """
    Make soft link.
    """
    if os.path.exists(target):
        if not force:
            return
        os.remove(target)

    os.symlink(source, target)


def make_dir(dirPath, force=False):
    """
    Make directory.
    """
    if os.path.exists(dirPath):
        if not force:
            return
        remove_dir(dirPath)

    os.makedirs(dirPath)


def is_file_existing(fileToCheck):
    """
    Return if file is existing.
    """
    return isinstance(fileToCheck, str) and \
            len(fileToCheck) and \
            os.path.exists(fileToCheck) and \
            os.path.isfile(fileToCheck)


def is_dir_existing(dirToCheck):
    """
    Return if dir is existing.
    """
    return isinstance(dirToCheck, str) and \
            len(dirToCheck) and \
            os.path.exists(dirToCheck) and \
            os.path.isdir(dirToCheck)


def shell_ls(pathToLS, showFiles=True, showDirs=True, showHiden=False, absolutePath=True):
    """
    As shell ls.
    """
    results = []
    try:
        allItems = os.walk(pathToLS)
        for root, dirs, files in allItems:
            if showDirs:
                for d in dirs:
                    if d[0] != "." or showHiden:
                        if absolutePath:
                            r = path_join(root, d)
                        else:
                            r = d
                        results.append(r)
            if showFiles:
                for f in files:
                    if f[0] != "." or showHiden:
                        if absolutePath:
                            r = path_join(root, f)
                        else:
                            r = f
                        results.append(r)

            # Only show depth=1.
            break
    except Exception as e:
        Logger.error("Error occured while walk through: {}".format(str(e)))

    return results


def remove_file(fileToRemove):
    """
    Remove file.
    """
    if is_file_existing(fileToRemove):
        os.remove(fileToRemove)


def remove_file_list(fileList):
    """
    Remove file.
    """
    for f in fileList:
        remove_file(f)


def remove_dir(dirPath):
    """
    Remove directory.
    """
    shutil.rmtree(dirPath)


def shell_move(original, target):
    """
    As shell move.
    """
    shutil.move(original, target)


def shell_copy(original, target):
    """
    As shell copy.
    """
    try:
        if is_dir_existing(original):
            shutil.copytree(original, target, symlinks = True)
        else:
            shutil.copy(original, target)
    except Exception as e:
        Logger.error("Error orccured: {}".format(str(e)))
        return False

    return True


def substitute_str_in_file(inputFile, orgStr, tarStr, outputFile=None):
    """
    Substitute string in file.
    """
    if not is_file_existing(inputFile):
        Logger.error("Input file is not existing: {}".format(inputFile))
        return False

    tmpFile = generate_temp_file()
    proc = subprocess.Popen(["cp", inputFile, tmpFile])
    proc.wait()
    if proc.returncode:
        return False

    # TODO:
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Caution here for '/' in strings.
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    shellCmd = ["sed", 
            "-i", 
            "s/{}/{}/g".format(str(orgStr), str(tarStr)), 
            tmpFile]
    proc = subprocess.Popen(shellCmd)
    proc.wait()
    if proc.returncode:
        return False

    if not outputFile:
        outputFile = inputFile
    proc = subprocess.Popen(["cp", tmpFile, outputFile])
    proc.wait()
    if proc.returncode:
        return False

    return True


def tar_czf(target, *srcFiles):
    """
    Package files up like tar -czf.
    """
    tmpFile = generate_temp_file()
    tarHandler = tarfile.open(tmpFile, "w:gz")
    for srcFile in srcFiles:
        if is_file_existing(srcFile):
            tarHandler.add(srcFile)
        elif is_dir_existing(srcFile):
            for rootPath, dirs, files in os.walk(srcFile):
                tarHandler.add(rootPath)
                for f in files:
                    filePath = os.path.join(rootPath, f)
                    tarHandler.add(filePath)

    tarHandler.close()
    shell_move(tmpFile, target)


def tar_xzf(tarFile, targetPath):
    """
    Unackage files up like tar -xzf.
    """
    if not is_file_existing(tarFile):
        Logger.error("Unpackage tar file failed: file does not exist.")
        return False

    targetPath = get_abspath(targetPath)
    try:
        tarHandler = tarfile.open(tarFile)
        tarHandler.extractall(path = targetPath)
        tarHandler.close()
    except Exception as e:
        Logger.error("Unpackage tar file failed: " + str(e))
        return False

    return True


