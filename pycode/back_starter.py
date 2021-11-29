# -*- coding: utf-8 -*-

import os,sys
import re
import shutil
import exporter_util; reload(exporter_util)
import batch

env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)

def spsymbol_remover(litteral, sp_check=None):
    listitem = ["export_item", "framerange"]
    if sp_check in listitem:
        litteral = re.sub('\'|{|}', '', litteral)
        litteral = litteral.rstrip(',')
    elif sp_check == "namespace":
        litteral = re.sub('\'|{|}', '', litteral)
        litteral = litteral.rstrip(',')
    else:
        litteral = re.sub(':|\'|,|{|}', '', litteral)
    url_list = ['input_path', 'assetpath']
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
    print "#####back_starter#######"
    if "kwargs" in kwargs.keys():
        argsdic = kwargs["kwargs"]
    else:
        argsdic = kwargs
        
    input_path = argsdic['input_path']
    charaName = argsdic['chara'].replace(".ma", "")
    export_type = argsdic['export_type']
    debug_mode = argsdic['debug_mode']
    abc_check = argsdic['abc_check']
    if export_type != 'camera':
        anim_item = argsdic["export_item"].split("anim", 1)[1:][0].split("abc", 1)[0].rstrip(",")
        abc_item = argsdic["export_item"].split("anim", 1)[1:][0].split("abc", 1)[1].rstrip(")")
    if export_type == 'anim':
        isAnim = True
    else:
        isAnim = False
    if 'override_shotpath' in argsdic.keys():
        if argsdic['override_shotpath'] is not None:
            override = True
            override_shotpath = argsdic['override_shotpath']
        else:
            override = False
            override_shotpath = None
    else:
        override = False
        override_shotpath = None
    opc = exporter_util.outputPathConf(input_path, isAnim=isAnim, test=debug_mode)
    if export_type != "camera":
        opc.createOutputDir(charaName)
    if override == True:
        opc.overrideShotpath(override_shotpath)
        opc.setChar(charaName, override=True)     
    if export_type == 'anim':
        # opc.createOutputDir(charaName)
        argsdic['animOutput'] = opc.publishfullanimpath
        argsdic["export_item"]=anim_item
        batch.animExport(**argsdic)
        animFiles = os.listdir(opc._publishfullanimpath)
        if charaName == "camera_base" or charaName == "camera_simple":
            opc.makeCurrentDir()
            return
        if len(animFiles)==0:
            opc.removeDir()
            return
        for animFile in animFiles:
            scene_ns = animFile.replace('anim_', '').replace('.ma', '')
            animOutput = opc.publishfullanimpath + '/' + animFile
            charaOutput = opc.publishfullpath + '/' + scene_ns + '.ma'
            argsdic['animOutput'] = animOutput
            argsdic['charaOutput'] = charaOutput
            argsdic['scene_ns'] = scene_ns
            batch.animAttach(**argsdic)
        if override == False:
            opc.makeCurrentDir()
            for animFile in animFiles:
                if animFile[:5] != 'anim_':continue
                if animFile[-3:] != '.ma':continue
                scene_ns = animFile.replace('anim_', '').replace('.ma', '')
                argsdic['animOutput'] = (opc.publishcurrentpath + '/anim/' + animFile)
                argsdic['scene_ns'] = scene_ns
                argsdic['scene_path'] = (opc.publishcurrentpath + '/' + scene_ns + '.ma')
                batch.animReplace(**argsdic)
    if export_type == 'abc' or abc_check == 'True':
        if abc_check == 'True':
            opc.setCache(charaName)
        argsdic["export_item"]=abc_item
        argsdic['abcOutput'] = opc._publishfullabcpath + "/" + charaName + '.abc'
        argsdic['abcOutput'] = argsdic['abcOutput'].replace("\\", "/")
        try:
            os.makedirs(opc._publishfullabcpath)
        except:
            pass
        batch.abcExport(**argsdic)
        abcFiles = os.listdir(opc._publishfullabcpath)
        if len(abcFiles) == 0:
            opc.removeDir()
            print 'abc not found'
            return
        allOutput = []
        for abc in abcFiles:
            scene_ns = abc.replace('_abc.abc', '')
            print "ns:", scene_ns
            print "abc:", abc
            print "publishfullabcpath", opc.publishfullabcpath
            abcOutput = opc.publishfullabcpath+"/"+abc
            charaOutput = opc.publishfullpath+"/"+abc.replace(".abc", ".ma")
            argsdic['scene_ns'] = scene_ns
            argsdic['attachPath'] = charaOutput #.ma
            argsdic['abcOutput'] = abcOutput #.abc
            batch.abcAttach(**argsdic)
            allOutput.append([abc.replace('.abc', '.ma'), abc])
        if override_shotpath == False:
            opc.makeCurrentDir()
            for output in allOutput:
                argsdic['charaOutput'] = opc.publishcurrentpath + '/' + output[0]
                argsdic['abcOutput'] = opc.publishcurrentpath + '/abc/' + output[1]
                batch.repABC(**argsdic)
    elif export_type == 'camera':
        opc.createCamOutputDir()
        opc.setChar(charaName)
        print opc.publishcurrentpath
        argsdic['publishPath'] = opc.publishfullpath
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
    
    try:
        exporter_util.addTimeLog(charaName, input_path, test=debug_mode)
    except Exception as e:
        print e
        

    print 'Output directry: {}'.format(opc.publishfullpath.replace('/','\\'))
    print '=================END==================='


if __name__ == '__main__':
    argslist = sys.argv[:]
    argslist.pop(0) # 先頭はpyファイルなので
    argsdict = strdict_parse(argslist)
    back_starter(**argsdict)
