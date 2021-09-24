# -*- coding: utf-8 -*-

import sys,os
import re
import shutil
import distutils.dir_util
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key,'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\','/')
    if path in sys.path: continue
    sys.path.append(path)
#------------------------------------
import ND_lib.util.path as util_path

def symlink(source, link_name):
    import os
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()
            
class outputPathConf(object):
    def __init__(self, input_path, isAnim=False, test=False):
        self.input_path = input_path.replace('\\', '/')
        self.isAnim = isAnim
        self.outputRootDir = 'charSet'
        self.outputCamRootDir = 'Cam'
        if test == 'True':
            self.outputRootDir = 'test_charSet'
            self.outputCamRootDir = 'test_Cam'
        dic = util_path.get_path_dic(self.input_path)
        self._pro_name = dic['project_name']
        self._shot = dic['shot']
        self._sequence = dic['sequence']
        self._shotpath = ''
        for path_parts in self.input_path.split('/'):
            self._shotpath = self._shotpath + path_parts+'/'
            if path_parts == self._shot:
                break

    def createOutputDir(self, char):
        self._publishpath = os.path.join(self._shotpath,'publish', self.outputRootDir, char)
        if os.path.exists(self._publishpath):
            self.verInc()
        else:
            try:
                os.makedirs(self._publishpath)
                self.verInc()
            except:
                pass

    def createCamOutputDir(self):
        self._publishpath = os.path.join(self._shotpath, 'publish', self.outputCamRootDir)
        if os.path.exists(self._publishpath):
            self.verInc(True)
        else:
            try:
                os.makedirs(self._publishpath)
                self.verInc(True)
            except:
                pass

    def verInc(self, isCam=False):
        vers = os.listdir(self._publishpath)
        if len(vers) == 0:
            self._currentVer = 'v001'
        else:
            vers.sort()
            currentVer = vers[-1]
            currentVerNum = int(currentVer[1:])
            nextVerNum = currentVerNum + 1
            nextVer = 'v' + str(nextVerNum).zfill(3)
            self._currentVer = nextVer
        print self._publishpath
        self._publishfullpath = os.path.join(self._publishpath, self._currentVer)
        self._publishfullabcpath = os.path.join(self._publishfullpath, 'abc')
        self._publishfullanimpath = os.path.join(self._publishfullpath, 'anim')
        self._publishfullcampath = os.path.join(self._publishfullpath,'cam')
        try:
            os.mkdir(self._publishfullpath)
            if isCam == True:
                os.mkdir(self._publishfullcampath)
            elif self.isAnim:
                os.mkdir(self._publishfullanimpath)
            else:
                os.mkdir(self._publishfullabcpath)
        except Exception as e:
            print(isCam, self.isAnim)
            print e

    def makeCurrentDir(self):
        currentDir = os.path.join(self.publishpath, 'current')
        self._publishcurrentpath = currentDir
        distutils.dir_util.copy_tree(self._publishfullpath, currentDir)
        current_info = os.path.join(currentDir, 'current_info.txt')
        with open(current_info, 'w') as f:
            f.write("current ver:"+ str(self._currentVer)+"\n")

    def removeDir(self):
        if os.path.exists(self._publishpath+'\\current'):
            files = os.listdir(self._publishpath+'\\current')
            for f in files:
                if '.ma' in f:
                    return
        shutil.rmtree(self._publishpath)

    def setChar(self, char):
        if char == 'Cam' or char == 'Camera':
            self._publishpath = os.path.join(self._shotpath, 'publish', self.outputCamRootDir).replace('/', '\\')
        else:
            self._publishpath = os.path.join(self._shotpath, 'publish', self.outputRootDir, char).replace('/', '\\')
        try:
            vers = os.listdir(self._publishpath)
        except WindowsError as e:
            raise ValueError
        if len(vers) == 0:
            self.currentVer = 0
        else:
            vers.sort()
            self._currentVer = vers[-1]
            if vers[0] > vers[-1]:
                self._currentVer = vers[0]
        self._publishfullpath = os.path.join(self._publishpath, self._currentVer)
        self._publishfullabcpath = os.path.join(self._publishfullpath, 'abc')
        self._publishfullanimpath = os.path.join(self._publishfullpath, 'anim')
        self._publishfullcampath = os.path.join(self._publishfullpath, 'cam')
        self._publishcurrentpath = self._publishpath+'\\current'

    def setCache(self, char):
        self._publishpath = os.path.join(self._shotpath, 'publish', 'cache', char).replace('/', '\\')
        if os.path.exists(self._publishpath):
            self.verInc()
        else:
            try:
                os.makedirs(self._publishpath)
                self.verInc()
            except:
                pass
        try:
            vers = os.listdir(self._publishpath)
        except WindowsError as e:
            raise ValueError
        if len(vers) == 0:
            raise ValueError
        else:
            vers.sort()
            self._currentVer = vers[-1]
            if vers[0] > vers[-1]:
                self._currentVer = vers[0]
        self._publishfullpath = os.path.join(self._publishpath, self._currentVer)
        self._publishfullabcpath = os.path.join(self._publishfullpath, 'abc')
        self._publishfullanimpath = os.path.join(self._publishfullpath, 'anim')
        self._publishfullcampath = os.path.join(self._publishfullpath, 'cam')
        self._publishcurrentpath = os.path.join(self._publishpath, 'current')      
    
    def setDebug(self):
        self._publishfullpath = self._publishfullpath.replace('charSet', 'test_charSet')
        self._publishfullabcpath = self._publishfullabcpath.replace('charSet', 'test_charSet')
        self._publishfullanimpath = self._publishfullanimpath.replace('charSet', 'test_charSet')
        self._publishfullcampath = self._publishfullcampath.replace('charSet', 'test_charSet')
        self._publishcurrentpath = self._publishcurrentpath.replace('charSet', 'test_charSet')
        
    def overrideShotpath(self, shotpath):
        self._shotpath = shotpath.replace('\\', '/')

    @property
    def sequence (self):
        return self._sequence

    @property
    def shot (self):
        return self._shot

    @property
    def publishpath (self):
        return self._publishpath.replace(os.path.sep, '/')

    @property
    def publishfullpath (self):
        return self._publishfullpath.replace(os.path.sep, '/')

    @property
    def publishfullabcpath (self):
        return self._publishfullabcpath.replace(os.path.sep, '/')

    @property
    def publishfullanimpath (self):
        return self._publishfullanimpath.replace(os.path.sep, '/')

    @property
    def publishcurrentpath (self):
        return self._publishcurrentpath.replace(os.path.sep, '/')

    @property
    def publishfullcampath(self):
        return self._publishfullcampath.replace(os.path.sep, '/')

    @property
    def publishshotpath(self):
        return self._shotpath.replace(os.path.sep, '/')

    @property
    def currentVer (self):
        return self._currentVer


def addTimeLog(char, input_path, test):
    from datetime import datetime
    opc = outputPathConf(input_path, char, test)
    print "#####addTimeLog#####"
    print "chara: {}".format(char)
    print "input_path: {}".format(input_path)
    print "test: {}".format(test)
    try:
        opc.setChar(char)
    except ValueError:
        print "AddTimeLog Error!!"
        return
    publishpath = opc.publishpath
    if test is True:
        publishpath = publishpath.replace("char", "test_char")
        publishpath = publishpath.replace("Cam", "test_Cam")
    with open(os.path.join(publishpath, 'timelog.txt').replace(os.path.sep, '/'), 'a') as f:
        f.write(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        f.write(' ' + opc.currentVer)
        f.write(' ' + input_path)
        f.write(' ' + os.environ['USERNAME'])
        f.write('\n')
