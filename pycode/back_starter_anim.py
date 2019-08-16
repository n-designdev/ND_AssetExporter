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

def back_starter (a, charaName, inputpath, namespace, exporttype, topnode, assetpath, testRun, yeti,stepValue):

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

    # regex =["*_ctrl_L","*_ctrl_R","*_ctrl_FL","*_ctrl_OL","*_ctrl_BL","*_ctrl_IL","*_ctrl_FR","*_ctrl_OR","*_ctrl_BR", "*_ctrl_IR", "*_ctrl_B", "*_ctrl",
    #      "*_ctrl_UL", "*_ctrl_DL", "*_ctrl_UR", "*_ctrl_DR", "*_ctrl_ZipL", "*_ctrl_ZipR", "*_ctrl_C", "*_ctrl_OL", "*_ctrl_OR", "*_ctrl_U", "*_ctrl_D", "*_ctrl_Zip",
    #      "*_ctrl_UC", "*_ctrl_DC", "*_ctrl_ZipC", "*_ctrl_AL", "*_ctrl_BL", "*_ctrl_CL", "*_ctrl_AR", "*_ctrl_BR", "*_ctrl_CR", "*_ctrl_TL", "*_ctrl_TR",
    #      "*_fkCtrl_C", "*_ikCtrl_R", "*_ikCtrl", "*_fkCtrl_L", "*_fkCtrl", "*_fkCtrl_R", "*_ikCtrl_L", "*_ikCtrl_C",
    #      "*_twk_R", "*_twk_FR", "*_twk_BR", "*_ctrl_C1", "*_twk_BC", "*_twk_FC", "*_ctrl_FC", "*_twk_BL", "*_ctrl_F", "*_ctrl_BC", "*_twk_FL", "*_twk_L",
    #      "*_ctrl_R1", "*_ctrl_L1", "*root", "*root", "*", "root"]
    regex=[]
    regex.append(topnode)
    # batch.animExport(output, abcSet, nsChara, regex, inputpath)

    batch.animExport(output,'anim', nsChara, regex, inputpath,yeti)
    print opc.publishfullanimpath

    animFiles = os.listdir(opc.publishfullanimpath)

    if len(animFiles) == 0:
        opc.removeDir()
        return
    for animFile in animFiles:
        ns = animFile.replace('anim_', '').replace('.ma', '')
        animOutput = opc.publishfullanimpath + '/' + animFile
        charaOutput = opc.publishfullpath + '/' + ns + '.ma'
        batch.animAttach(assetpath, ns, animOutput, charaOutput)
    opc.makeCurrentDir()

    for animFile in animFiles:
        if animFile[:5] != 'anim_':
            continue
        if animFile[-3:] != '.ma':
            continue
        ns = animFile.replace('anim_', '').replace('.ma', '')
        batch.animReplace(ns, opc.publishcurrentpath + '/anim/' + animFile, opc.publishcurrentpath + '/'+ns+'.ma')

    print '=================END==================='

    return 0

if __name__ == '__main__':
    print sys.argv[:]
    back_starter(*sys.argv[:])
