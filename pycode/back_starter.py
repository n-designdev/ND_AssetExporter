# -*- coding: utf-8 -*-

import os,sys
import re
import shutil
import exporter_util
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
        litteral = re.sub('\'|{|}', '', litteral)
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
    import pprint
    pprint.pprint(kwargs)
    if "kwargs" in kwargs.keys():
        argsdic = kwargs["kwargs"]
    else:
        argsdic = kwargs
    inputpath = argsdic['inputpath']
    charaName = argsdic['chara']
    exporttype = argsdic['exporttype']
    testmode = argsdic['testmode']
    abcCheck = argsdic['abcCheck']
    if exporttype != 'camera':
        print argsdic["exportitem"]
        anim_item = argsdic["exportitem"].split("anim", 1)[1:][0].split("abc", 1)[0].rstrip(",")
        abc_item = argsdic["exportitem"].split("anim", 1)[1:][0].split("abc", 1)[1].rstrip(")")
    if exporttype == 'anim':
        isAnim = True
    else:
        isAnim = False
    opc = exporter_util.outputPathConf(inputpath, isAnim=isAnim, test=testmode)

    if exporttype == 'camera':
        opc.createCamOutputDir()
    else:
        opc.createOutputDir(charaName)
    abcOutput = opc.publishfullabcpath + '/' + charaName + '.abc'
    charaOutput = opc.publishfullpath + '/' + charaName + '.abc'
    argsdic['abcOutput'] = abcOutput
    argsdic['output'] = opc.publishfullanimpath

    if exporttype == 'anim':
        argsdic["exportitem"]=anim_item
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
        for animFile in animFiles:
            ns = animFile.replace('anim_', '').replace('.ma', '')
            animOutput = opc.publishfullanimpath + '/' + animFile
            charaOutput = opc.publishfullpath + '/' + ns + '.ma'
            argsdic['animOutput'] = animOutput
            argsdic['charaOutput'] = charaOutput
            argsdic['ns'] = ns
            batch.animAttach(**argsdic)
        opc.makeCurrentDir()
        for animFile in animFiles:
            if animFile[:5] != 'anim_':continue
            if animFile[-3:] != '.ma':continue
            ns = animFile.replace('anim_', '').replace('.ma', '')
            argsdic['ns'] = ns
            argsdic['animPath'] = (opc.publishcurrentpath + '/anim/' + animFile)
            argsdic['scene'] = (opc.publishcurrentpath + '/' + ns + '.ma')
            batch.animReplace(**argsdic)             
    if exporttype == 'abc' or abcCheck == 'True':
        argsdic["exportitem"]=abc_item
        if abcCheck == 'True':
            opc._publishpath = opc._publishpath + '/cache'
            if testmode == "True" or testmode == True:
                opc._publishfullpath = opc._publishfullpath.replace("test_charSet", "cache")
                opc._publishfullabcpath = opc._publishfullabcpath.replace("test_charSet", "cache") 
            else:
                opc._publishfullpath = opc._publishfullpath.replace("charSet", "cache")
                opc._publishfullabcpath = opc._publishfullabcpath.replace("charSet", "cache")     
            argsdic['abcOutput'] = opc._publishfullabcpath + "/" + charaName + '.abc'
            argsdic['abcOutput'] = argsdic['abcOutput'].replace("\\", "/")
            try:
                os.makedirs(opc._publishfullabcpath.replace("\\", "/"))
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
            print "##abc##"
            for x in abc:
                print x
            ns = abc.replace('_abc.abc', '')
            print "ns:", ns
            print "abc:", abc
            print "publishfullabcpath", opc.publishfullabcpath
            abcOutput = opc.publishfullabcpath + '/' + abc
            charaOutput = opc.publishfullpath + '/' + abc.replace('abc', 'ma')
            if abcCheck == "True":
                if testmode == "True":
                    charaOutput = charaOutput.replace("test_charSet", "cache")
                else:
                    charaOutput = charaOutput.replace("charSet", "cache")
            argsdic['Ntopnode'] = ns + ':' + argsdic['topnode']
            argsdic['ns'] = ns
            argsdic['attachPath'] = charaOutput
            argsdic['abcOutput'] = abcOutput
            batch.abcAttach(**argsdic)
            allOutput.append([abc.replace('abc', 'ma'), abc])
        opc._publishcurrentpath = opc._publishpath + '/current'  
        for output in allOutput:
            argsdic['charaOutput'] = opc._publishcurrentpath + '/' + output[0]
            argsdic['abcOutput'] = opc.publishcurrentpath + '/abc/' + output[1]
            batch.repABC(**argsdic)
        import pprint
        pprint.pprint(argsdic)

    elif exporttype == 'camera':
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

    # elif exporttype == 'abc_anim':
    #     anim_item = argsdic["exportitem"].split("anim", 1)[1:][0].split("abc", 1)[0].rstrip(",")
    #     abc_item = argsdic["exportitem"].split("anim", 1)[1:][0].split("abc", 1)[1].rstrip(")")
    #     argsdic["exportitem"] = anim_item
    #     batch.animExport(**argsdic)
    #     animFiles = os.listdir(opc.publishfullanimpath)
    #     if charaName == "camera_base" or charaName == "camera_simple":
    #         os.rmdir(output)
    #         if len(os.listdir(os.path.dirname(output)))==0:
    #             os.rmdir(output)
    #             os.rmdir(os.path.dirname(output))
    #             if os.path.dirname(output).split("/")[-1]=="v001":
    #                 os.rmdir(os.path.dirname(os.path.dirname(output)))
    #         opc.makeCurrentDir()
    #         return
    #     if len(animFiles)==0:
    #         opc.removeDir()
    #         return
    #     argsdic["exportitem"] = abc_item
    #     batch.abcExport(**argsdic)
    #     abcFiles = os.listdir(opc.publishfullabcpath)
    #     if len(abcFiles) == 0:
    #         opc.removeDir()
    #         print 'abc not found'
    #         return
    #     allOutput = []
    #     for abc in abcFiles:
    #         ns = abc.replace(charaName + '_', '').replace('.abc', '')
    #         if '___' in ns:
    #             ns = ns.replace('___', ':')
    #         abcOutput = opc.publishfullabcpath + '/' + abc
    #         charaOutput = opc.publishfullpath + '/' + abc.replace('abc', 'ma')
    #         argsdic['Ntopnode'] = ns + ':' + argsdic['topnode']
    #         argsdic['ns'] = ns
    #         argsdic['attachPath'] = charaOutput
    #         argsdic['abcOutput'] = abcOutput
    #         batch.abcAttach(**argsdic)
    #         allOutput.append([abc.replace('abc', 'ma'), abc])

    #     opc.makeCurrentDir()

    #     for animFile in animFiles:
    #         ns = animFile.replace('anim_', '').replace('.ma', '')
    #         animOutput = opc.publishfullanimpath + '/' + animFile
    #         charaOutput = opc.publishfullpath + '/' + ns + '.ma'
    #         argsdic['animOutput'] = animOutput
    #         argsdic['charaOutput'] = charaOutput
    #         argsdic['ns'] = ns
    #         batch.animAttach(**argsdic)

    #     for output in allOutput:
    #         argsdic['charaOutput'] = opc.publishcurrentpath + '/' + output[0]
    #         argsdic['abcOutput'] = opc.publishcurrentpath + '/abc/' + output[1]
    #         batch.repABC(**argsdic)
    exporter_util.addTimeLog(charaName, inputpath, test=testmode)

    print 'Output directry: {}'.format(opc.publishfullpath.replace('/','\\'))
    print '=================END==================='


if __name__ == '__main__':
    argslist = sys.argv[:]
    argslist.pop(0) # 先頭はpyファイルなので
    argsdict = strdict_parse(argslist)
    back_starter(**argsdict)
