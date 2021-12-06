# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess

from importlib import import_module

env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key,'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\','/')
    if path in sys.path: continue
    sys.path.append(path)
#------------------------------------
import ND_lib.util.path as util_path

def getFiles (path):
    fileDirs = os.listdir(path)
    files = [os.path.join(path,fileDir).replace("\\", "/") for fileDir in fileDirs if os.path.isfile(os.path.join(path, fileDir).replace('\\', '/'))]
    return files


def getDirs (path):
    fileDirs = os.listdir(path)
    dirs = [fileDir for fileDir in fileDirs if os.path.isdir(os.path.join(path, fileDir).replace('\\', '/'))]
    return dirs


def getCharList(charsetpath):
    charsetpath = charsetpath.replace("\\", "/")
    if not os.path.exists(charsetpath):
        raise ValueError('char is not exported')
    charlist = getDirs(charsetpath)
    return charlist


def getCurrentFilesList(charsetpath, mode="ma"):
    charsetpath = charsetpath.replace("\\", "/")
    charList = getCharList(charsetpath)
    currentFiles = []
    if mode=="ma":
        for char in charList:
            if "non_connection_" in char:
                continue
            currentFile = getFiles(os.path.join(charsetpath, char, "current"))
            currentFiles.extend(currentFile)
    elif mode=="anim":
        for char in charList:
            currentFile = getFiles(os.path.join(charsetpath, char, "current", "anim"))
            currentFiles.extend(currentFile)
    return currentFiles


def getCamFilesList(camsetpath):
    camsetpath = os.path.join(camsetpath.replace("\\", "/"), "current", "cam")
    print camsetpath
    if not os.path.exists(camsetpath):
        raise ValueError('camera is not exported')
    print camsetpath
    print os.listdir(camsetpath)
    camFiles = [os.path.join(camsetpath,file_name) for file_name in os.listdir(camsetpath) if str(file_name).split(".")[-1] in ["ma", "mb"]]
    return camFiles


def open_folder(path):
    subprocess.call("explorer {}".format(path.replace("/", "\\")))


class CharSetDirConf(object):
    def __init__ (self, input_path):
        self.input_path = input_path
        path_dic = util_path.get_path_dic(input_path)
        shot_flag = False
        for k, v in path_dic.items():
            print k, v
            if k == 'project_name':
                pro_name = v
            elif k == 'shot':
                shot = v
                shot_flag = True
            elif k == 'sequence':
                sequence = v
            elif k == 'roll':
                roll = v
        
        # shot_flag = False
        shotpath = ''
        for parse_path in input_path.split('/'):
            if shot_flag == True:
                if parse_path == shot:
                    shotpath = shotpath + '/' + parse_path
                    break
                else:
                    shotpath = shotpath + '/' + parse_path
            else:
                if parse_path == sequence:
                    shotpath = shotpath + '/' + parse_path
                    break
                else:
                    shotpath = shotpath + '/' + parse_path               

        shotpath = shotpath.strip('/')
        self.project = pro_name
        self.sequence = sequence
        self.shot = shot
        self.shotpath  = shotpath
        self.roll = roll

        self.charsetpath = os.path.join(self.shotpath, 'publish', 'charSet').replace('\\', '/')
