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

class outputPathConf (object):
    def __init__(self, inputPath, isAnim=False, test=False):
        self.inputPath = inputPath.replace('\\', '/')
        self.isAnim = isAnim
        self.outputRootDir = 'charSet'
        self.outputCamRootDir = 'Cam'
        if test == 'True':
            self.outputRootDir = 'test_charSet'
            self.outputCamRootDir = 'test_Cam'

        dic = util_path.get_path_dic(self.inputPath)

        self._pro_name = dic['project_name']
        self._shot = dic['shot']
        self._sequence = dic['sequence']
        self._shotpath = ''
        for path_parts in self.inputPath.split('/'):
            self._shotpath = self._shotpath + path_parts+'/'
            if path_parts == self._shot:
                break

    def createOutputDir (self, char):
        self._publishpath = os.path.join(self._shotpath+'publish', self.outputRootDir, char)
        print self._publishpath
        print 'createOutputDir'
        if os.path.exists(self._publishpath):
            self.verInc()
        else:
            try:
                os.makedirs(self._publishpath)
                self.verInc()
            except:
                pass

    def createCamOutputDir (self):
        self._publishpath = os.path.join(self._shotpath, 'publish', self.outputCamRootDir)
        if os.path.exists(self._publishpath):
            self.verInc(True)
        else:
            try:
                os.makedirs(self._publishpath)
                self.verInc(True)
            except:
                pass

    def verInc (self, isCam=False):
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
            print( isCam, self.isAnim)
            print e

    def makeCurrentDir (self):
        currentDir = os.path.join(self.publishpath, 'current')
        self._publishcurrentpath = currentDir
        distutils.dir_util.copy_tree(self._publishfullpath, currentDir)

    def removeDir (self):
        if os.path.exists(self._publishpath+'\\current'):
            files = os.listdir(self._publishpath+'\\current')
            for f in files:
                if '.ma' in f:
                    return
        shutil.rmtree(self._publishpath)

    def setChar (self, char):
        if char == 'Cam' or char == 'Camera':
            self._publishpath = os.path.join(self._shotpath, 'publish', self.outputCamRootDir, char).replace(os.path.sep, '/')
        else:
            self._publishpath = os.path.join(self._shotpath, 'publish', self.outputRootDir, char).replace(os.path.sep, '/')
            vers = []
        try:
            vers = os.listdir(self._publishpath)
        except WindowsError:
            raise ValueError
        if len(vers) == 0:
            raise ValueError
        vers.sort()
        self._currentVer = vers[-1]
        if vers[0] > vers[-1]:
            self._currentVer = vers[0]
        self._publishfullpath = os.path.join(self._publishpath, self._currentVer)
        self._publishfullabcpath = os.path.join(self._publishfullpath, 'abc')
        self._publishfullanimpath = os.path.join(self._publishfullpath, 'anim')
        self._publishfullcampath = os.path.join(self._publishfullpath, 'cam')
        self._publishcurrentpath = self._publishpath+'\\current'

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
    def currentVer (self):
        return self._currentVer


def addTimeLog (char, inputpath, test):
    from datetime import datetime
    opc = outputPathConf(inputpath, char, test)
    try:
        opc.setChar(char)
    except ValueError:
        return
    publishpath = opc.publishpath
    if test is True:
        publishpath.replace("char", "test_char")
        publishpath.replace("Cam", "test_Cam")
    with open(os.path.join(publishpath, 'timelog.txt').replace(os.path.sep, '/'), 'a') as f:
        f.write(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        f.write(' ' + opc.currentVer)
        f.write(' ' + inputpath)
        f.write(' ' + os.environ['USERNAME'])
        f.write('\n')
