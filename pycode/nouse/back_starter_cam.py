# -*- coding: utf-8 -*-

import os,sys
import re
import shutil
import util

import batch

env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)

def back_starter (a, inputpath, camScale,test):

    print '##############'*5
    print inputpath
    print camScale
    print '##############'*5

    opc = util.outputPathConf(inputpath, test=test)
    opc.createCamOutputDir()

    batch.camExport(opc.publishfullpath, opc.sequence +
                    opc.shot+'_cam', camScale, inputpath)
    camFiles = os.listdir(opc.publishfullpath)
    for camFile in camFiles:
        srcFile = os.path.join(opc.publishfullpath, camFile)
        dstDir = os.path.join(opc.publishfullpath, '..')
        try:
            shutil.copy(srcFile, dstDir)
        except:
            pass
    return 0


if __name__ == '__main__':
    print sys.argv[:]
    back_starter(*sys.argv[:])