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

def back_starter (a, charaName, inputpath, namespace, exporttype, topnode, assetpath, testRun, yeti,stepValue, project, framerange_output):

    print '##############'*5

    print charaName
    print inputpath
    print namespace
    print exporttype
    print topnode
    print assetpath
    print testRun
    print yeti
    print stepValue
    print project
    print framerange_output

    print '##############'*5

    opc = util.outputPathConf(inputpath, test=testRun)
    print opc
    opc.createOutputDir(charaName)

    abcOutput = opc.publishfullabcpath + '/' + charaName + '.abc'
    charaOutput = opc.publishfullpath + '/' + charaName + '.abc'

    # charaSetup = import_module('setting.'+charaName+'Setup')

    abcSet = exporttype.split('@')
    nsChara = namespace.split('@')

    output =opc.publishfullanimpath

    regex=[]
    regex.append(topnode)


    batch.animExport(output,'anim', nsChara, regex, inputpath,yeti, project, framerange_output)
    print opc.publishfullanimpath

    animFiles = os.listdir(opc.publishfullanimpath)

    if len(animFiles) == 0:
        opc.removeDir()
        return
    for animFile in animFiles:
        ns = animFile.replace('anim_', '').replace('.ma', '')
        animOutput = opc.publishfullanimpath + '/' + animFile
        charaOutput = opc.publishfullpath + '/' + ns + '.ma'
        batch.animAttach(assetpath, ns, animOutput, charaOutput,yeti, project)
    opc.makeCurrentDir()

    for animFile in animFiles:
        if animFile[:5] != 'anim_':
            continue
        if animFile[-3:] != '.ma':
            continue
        ns = animFile.replace('anim_', '').replace('.ma', '')
        batch.animReplace(ns, opc.publishcurrentpath + '/anim/' + animFile, opc.publishcurrentpath + '/'+ns+'.ma', yeti,project)

    print '=================END==================='

    return 0

if __name__ == '__main__':
    print sys.argv[:]
    back_starter(*sys.argv[:])
