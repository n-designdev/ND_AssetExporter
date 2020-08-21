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

def spsymbol_remover(litteral):
    litteral = re.sub(':|\'|,|{|}', '', litteral)
    return litteral

def strdict_parse(original_string):
    parsed_dic = {}
    original_string_iter = iter(original_string)
    for key, item in zip(original_string_iter, original_string_iter):
        key = spsymbol_remover(key)
        item = spsymbol_remover(item)
        parsed_dic[key] = item
    return parsed_dic

def back_starter(**kwargs):
    argsdic = kwargs

    inputpath = argsdic['inputpath']
    project = argsdic['project']

    charaName = argsdic['chara']
    nsChara = argsdic['namespace']
    exporttype = argsdic['exporttype']
    exportitem = argsdic['exportitem']
    topnode = argsdic['topnode']
    assetpath = argsdic['assetpath']

    stepValue = argsdic['stepValue']
    env_load = argsdic['env_load']
    framerange_output = argsdic['framgerange_output']

    testmode = argsdic['testmode']

    opc = util.outputPathConf(inputpath, isAnim=True, test=testmode)
    opc.createOutputDir(charaName)

    # abcOutput = opc.publishfullabcpath + '/' + charaName + '.abc'
    charaOutput = opc.publishfullpath + '/' + charaName + '.abc'

    output = opc.publishfullanimpath

    import pdb;pdb.set_trace()

    batch.animExport(
        output, exporttype,
        nsChara, exportitem,
        inputpath, env_load,
        project, framerange_output)

    animFiles = os.listdir(opc.publishfullanimpath)

    if len(animFiles) == 0:
        opc.removeDir()
        return

    for animFile in animFiles:
        ns = animFile.replace('anim_', '').replace('.ma', '')
        animOutput = opc.publishfullanimpath + '/' + animFile
        charaOutput = opc.publishfullpath + '/' + ns + '.ma'
        batch.animAttach(
            assetpath, ns, animOutput,
            charaOutput , env_load, project)

    opc.makeCurrentDir()

    for animFile in animFiles:
        if animFile[:5] != 'anim_':continue
        if animFile[-3:] != '.ma':continue
        ns = animFile.replace('anim_', '').replace('.ma', '')
        batch.animReplace(
            ns,
            opc.publishcurrentpath + '/anim/' + animFile,
            opc.publishcurrentpath + '/' + ns + '.ma',
            env_load,
            project)

    print '=================END==================='

    return 0

if __name__ == '__main__':
    argslist = sys.argv[:]
    argslist.pop(0) # 先頭はpyファイルなので
    argsdict = strdict_parse(argslist)
    back_starter(**argsdict)

