# -*- coding: utf-8 -*-

import os,sys
import re
import shutil
import util
import shutil

import batch

env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)

import ND_lib.deadline.common as common
import ND_lib.env as util_env

def spsymbol_remover(litteral, sp_check=None):
    listitem = ["exportitem", "framerange"]
    if sp_check in listitem:
        litteral = re.sub(':|\'|{|}', '', litteral)
        litteral = litteral.rstrip(',')
    elif sp_check == "namespace":
        litteral = re.sub('\'|{|}', '', litteral)
        litteral = litteral.rstrip(',')    
    else:
        litteral = re.sub(':|\'|,|{|}', '', litteral)
    url_list = ['inputpath', 'assetpath']
    if sp_check in url_list:
        litteral = litteral.replace('/', ':/', 1)
    return litteral


def strdict_parse(original_string):
    parsed_dic = {}
    original_string_iter = iter(original_string)
    for key, item in zip(original_string_iter, original_string_iter):
        key = spsymbol_remover(key)
        item = spsymbol_remover(item, key)
        parsed_dic[key] = item
    return parsed_dic


def back_starter(**kwargs):
    argsdic = kwargs
    inputpath = argsdic['inputpath']
    project = argsdic['project']
    charaName = argsdic['chara']
    exporttype = argsdic['exporttype']
    exportitem = argsdic['exportitem']
    topnode = argsdic['topnode']
    assetpath = argsdic['assetpath']
    stepValue = argsdic['stepValue']
    env_load = argsdic['env_load']
    testmode = argsdic['testmode']
    if exporttype == 'anim':
        isAnim = True
    else:
        isAnim = False

    opc = util.outputPathConf(inputpath, isAnim=isAnim, test=testmode)

    if exporttype == 'camera':
        opc.createCamOutputDir()
    else:
        opc.createOutputDir(charaName)
    abcOutput = opc.publishfullabcpath + '/' + charaName + '.abc'
    charaOutput = opc.publishfullpath + '/' + charaName + '.abc'
    argsdic['abcOutput'] = abcOutput
    argsdic['output'] = opc.publishfullanimpath

    if exporttype == 'anim':
        batch.animExport(**argsdic)
        animFiles = os.listdir(opc.publishfullanimpath)
        if charaName == "camera_base" or charaName == "camera_simple":
            os.rmdir(output)
            if len(os.listdir(os.path.dirname(output)))==0:
                os.rmdir(output)
                os.rmdir(os.path.dirname(output))
                if os.path.dirname(output).split("/")[-1]=="v001":
                    os.rmdir(os.path.dirname(os.path.dirname(output)))
            opc.makeCurrentDir()
            return
        print "##animFiles"
        import pprint
        pprint.pprint(animFiles)
        if len(animFiles)==0:
            opc.removeDir()
            return
        for animFile in animFiles:
            ns = animFile.replace('anim_', '').replace('.ma', '')
            animOutput = opc.publishfullanimpath + '/' + animFile
            charaOutput = opc.publishfullpath + '/' + ns + '.ma'
            argsdic['animOutput'] = animOutput
            argsdic['charaOutput'] = charaOutput
            # argsdic['ns'] = ns.replace("__", ":")
            argsdic['ns'] = ns
            batch.animAttach(**argsdic)

        opc.makeCurrentDir()

        for animFile in animFiles:
            if animFile[:5] != 'anim_':continue
            if animFile[-3:] != '.ma':continue
            ns = animFile.replace('anim_', '').replace('.ma', '')
            argsdic['ns'] = ns
            # argsdic['ns'] = ns.replace("_", ":")
            argsdic['animPath'] = (opc.publishcurrentpath + '/anim/' + animFile)
            argsdic['scene'] = (opc.publishcurrentpath + '/' + ns + '.ma')
            batch.animReplace(**argsdic)             

    elif exporttype == 'abc':
        # opc.createOutputDir(charaName)
        batch.abcExport(**argsdic)
        abcFiles = os.listdir(opc.publishfullabcpath)
        print opc.publishfullabcpath
        if len(abcFiles) == 0:
            opc.removeDir()
            print 'abc not found'
            return
        allOutput = []
        for abc in abcFiles:
            ns = abc.replace(charaName + '_', '').replace('.abc', '')
            if '___' in ns:
                ns = ns.replace('___', ':')
            abcOutput = opc.publishfullabcpath + '/' + abc
            charaOutput = opc.publishfullpath + '/' + abc.replace('abc', 'ma')
            argsdic['Ntopnode'] = ns + ':' + argsdic['topnode']
            argsdic['ns'] = ns
            argsdic['attachPath'] = charaOutput
            argsdic['abcOutput'] = abcOutput
            batch.abcAttach(**argsdic)
            allOutput.append([abc.replace('abc', 'ma'), abc])
        opc.makeCurrentDir()
        for output in allOutput:
            argsdic['charaOutput'] = opc.publishcurrentpath + '/' + output[0]
            argsdic['abcOutput'] = opc.publishcurrentpath + '/abc/' + output[1]
            batch.repABC(**argsdic)

    elif exporttype == 'camera':
        argsdic['publishPath'] = opc.publishfullpath #ディレクトリ名
        oFilename = opc.sequence + opc.shot + '_cam'
        argsdic['camOutput'] = '{}/{}.abc'.format(opc.publishfullcampath, oFilename) #フルパスとファイル名
        batch.camExport(**argsdic)
        camFiles = os.listdir(opc.publishfullcampath)
        if len(camFiles) == 0:
            print 'camera not found'
            return
        for camFile in camFiles:
            srcFile = os.path.join(opc.publishfullpath, camFile)
            if srcFile.split('.')[-1] == 'ma':
                dstDir = os.path.join(opc.publishfullpath, '..')
                try:
                    shutil.copy(srcFile, dstDir)
                except:
                    pass
        opc.makeCurrentDir()

    elif exporttype == 'abc_anim':
        batch.animExport(**argsdic)
        animFiles = os.listdir(opc.publishfullanimpath)
        if charaName == "camera_base" or charaName == "camera_simple":
            os.rmdir(output)
            if len(os.listdir(os.path.dirname(output)))==0:
                os.rmdir(output)
                os.rmdir(os.path.dirname(output))
                if os.path.dirname(output).split("/")[-1]=="v001":
                    os.rmdir(os.path.dirname(os.path.dirname(output)))
            opc.makeCurrentDir()
            return
        if len(animFiles)==0:
            opc.removeDir()
            return
        batch.abcExport(**argsdic)
        abcFiles = os.listdir(opc.publishfullabcpath)
        if len(abcFiles) == 0:
            opc.removeDir()
            print 'abc not found'
            return
        allOutput = []
        for abc in abcFiles:
            ns = abc.replace(charaName + '_', '').replace('.abc', '')
            if '___' in ns:
                ns = ns.replace('___', ':')
            abcOutput = opc.publishfullabcpath + '/' + abc
            charaOutput = opc.publishfullpath + '/' + abc.replace('abc', 'ma')
            argsdic['Ntopnode'] = ns + ':' + argsdic['topnode']
            argsdic['ns'] = ns
            argsdic['attachPath'] = charaOutput
            argsdic['abcOutput'] = abcOutput
            batch.abcAttach(**argsdic)
            allOutput.append([abc.replace('abc', 'ma'), abc])

        opc.makeCurrentDir()

        for animFile in animFiles:
            ns = animFile.replace('anim_', '').replace('.ma', '')
            animOutput = opc.publishfullanimpath + '/' + animFile
            charaOutput = opc.publishfullpath + '/' + ns + '.ma'
            argsdic['animOutput'] = animOutput
            argsdic['charaOutput'] = charaOutput
            argsdic['ns'] = ns
            batch.animAttach(**argsdic)

        for output in allOutput:
            argsdic['charaOutput'] = opc.publishcurrentpath + '/' + output[0]
            argsdic['abcOutput'] = opc.publishcurrentpath + '/abc/' + output[1]
            batch.repABC(**argsdic)


    print 'Output directry: {}'.format(opc.publishfullpath.replace('/','\\'))
    print '=================END==================='


if __name__ == '__main__':
    argslist = sys.argv[:]
    argslist.pop(0) # 先頭はpyファイルなので
    argsdict = strdict_parse(argslist)
    back_starter(**argsdict)
