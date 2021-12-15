# -*- coding: utf-8 -*-

#------------------------------
__version__ = "0.0.1"
__copyright__ = "Copyright (C) 2016, N-Design"
__author__ = "Gou Hattori"
__maintainer__ = "Masato Hirabayashi"
__credits__ = ["Gou Hattori", "Masato Hirabayashi"]
#------------------------------

import sys
import os
import copy
import locale
import re

#------------------------------
ND_TOOL_PATH_default = "Y:/tool/ND_Tools/python"

env_key = "ND_TOOL_PATH_PYTHON"
ND_TOOL_PATH = os.environ.get(env_key, ND_TOOL_PATH_default)
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path: continue
    sys.path.append(path)

#-----------------------------------
import exporter_lib.json_io as util_json
import exporter_lib.custom_expandvars as custom_expandvars
from exporter_lib.custom_expandvars import expandvars

#-----------------------------------
# _encode
#-----------------------------------
#システム用の文字コードに変更
#-----------------------------------
def _encode(val):
    try:
        val = val.encode(locale.getpreferredencoding())
    except:
        pass
    return(val)

#-----------------------------------
# getConfPath
#-----------------------------------
#指定名の .json ファイルを探しフルパスを返す
#※.json ファイルを検索する対象フォルダについて今後拡張する場合に使用する
#-----------------------------------
def getConfPath(path, key, search_path='.'):

    if search_path == '.':
        path = '%s/%s.json' % (os.path.dirname(path), key)
        if os.path.exists(path):
            return (path)

    return (False)

#-----------------------------------
# getExpandedKey
#-----------------------------------
# / 区切りのキーワードを . = * と見立ててリストに変換する
#-----------------------------------
def getExpandedKey(keyStr, level=1):
    if not keyStr: return

    keyList = keyStr.split('/')[::-1] #reverse order
    for i in range(len(keyList) - level):
        if keyList[i] == '.': continue
        yield ('/'.join(keyList[::-1]))
        keyList[i] = '.'
    else: #break した場合は実行されない
        yield ('/'.join(keyList[::-1]))

# application/maya/version/2015/amd64/win
# =>
# application/maya/version/2015/amd64/win
# application/maya/version/2015/amd64/.
# application/maya/version/2015/./.
# application/maya/version/././.
# application/maya/./././.
# application/././././.

#-----------------------------------
# hitKey
#-----------------------------------
# キーの一致判定。ごちゃごちゃしているので後で見直したい
#-----------------------------------
def hitKey(key, value):
    keyList = key.split('/')
    valueList = value.split('/')
    for i in range(len(keyList)):
        k = keyList[i]
        if not (i < len(valueList)): return (True)
        v = valueList[i]
        if k == v: continue
        if k == '.': return(False)
        if re.match(v, k): continue
        return (False)
    return (True)

#-----------------------------------
# searchConf
#-----------------------------------
#dict からフィルタ文字にマッチするキーを持つ項目を取り出し配列にして返す
#-----------------------------------
def searchConf(envDict, filterStr, returnKeys=False):
    result = []

    for pat in getExpandedKey(filterStr):

        #dictList = envDict.get(pat, None)
        #-----------------------
        dictList = []
        for i in envDict:
            if not hitKey(pat, i): continue
            dictList += envDict.get(i)
            if returnKeys and i not in result:
                result += [i]
        #-----------------------
        if not dictList: continue

        if returnKeys:
            #result.insert(0, pat)
            pass
        else:
            dictList = copy.deepcopy(dictList)
            result.insert(0, dictList)

    return (result)

#-----------------------------------
# loadConf
#-----------------------------------
#json ファイルのパスから依存関係を辿りつつ環境変数配列を作成して返す
#-----------------------------------
def loadConf(basePath, **kwargs):
    '''
    loadConf

    basePath:
    name:
    appName [.]
    version [.]:
    osType [.]:
    osName [.]: ...
    searchPath [.]: ......
    '''
    name = kwargs.get("name")
    appName = kwargs.get("appName", ".")
    version = kwargs.get("version", ".")
    osType = kwargs.get("osType", ".")
    osName = kwargs.get("osName", ".")
    searchPath = kwargs.get("searchPath", ".")

    result = []

    path = getConfPath(basePath, name, searchPath)
    if not path or not os.path.exists(path):
        print ('[%s] not found' % path)
        return(result)

    filterStr = '/'.join(('application', appName, 'version', version, osType, osName))
    configDict = util_json._loadJson(path)
    result = searchConf(configDict.get('data', {}), filterStr)

    parentList = configDict.get('info', {}).get('parent', [])
    if not parentList:
        parentList = []
    if not isinstance(parentList, list):
        parentList = [parentList]

    parentResult = []
    for n in parentList:
        parentResult += loadConf(path, name=n,
            appName=appName, version=version, osType=osType, osName=osName,
            searchPath=searchPath,
        )

    return (parentResult + result)

#-----------------------------------
# _cleanup
#-----------------------------------
#重複する変数値の整理・削除を行う
#expand=True なら変数値の展開も行なう
#-----------------------------------
def _cleanup(valueStr, env=None, expand=True):
    if env is None:
        env = os.environ.copy()

    result = []
    for i in valueStr.split(';'):
        i = i.strip() #.replace('\\', '/')
        if expand:
            i = expandvars(i, env)
        if not i or i in result: continue

        result.append(i)

    return (result)

#-----------------------------------
# getEnvDict
#-----------------------------------
#
#-----------------------------------
def getEnvDict(object, env=None, expand=True):
    if env is None:
        env = os.environ.copy()

    if isinstance(object, list):
        for i in object:
            getEnvDict(i, env=env, expand=expand)

    elif isinstance(object, dict):
        key = object.get('key', None)
        if key is None: return

        value = object.get('value', '')
        mode = object.get('mode', 'append')

        prev = _cleanup(env.get(key, ''), env=env, expand=expand)
        next = _cleanup(value, env=env, expand=expand)

        if mode == 'set':
            pass
        elif mode == 'prepend':
            next += prev
        else: #if mode == 'append':
            next = prev + next
        import pprint
        pprint.pprint([key,next])
        env[_encode(key)] = _encode(';'.join(next))

        del prev[:]
        del next[:]

    return (env)

#-----------------------------------
# setEnv
#-----------------------------------
#環境変数の dict を現在の値に反映
#-----------------------------------
def setEnv(dic, expand=False):
    getEnvDict(dic, env=os.environ, expand=expand)

#-----------------------------------
# printEnvBat
#-----------------------------------
#環境変数の dict を bat 形式でプリントする
#-----------------------------------
def printEnvBat(dic, env=None, sortByName=True, mode=1):
    if env is None:
        env = os.environ.copy()

    envDict = getEnvDict(dic, expand=True, env=env)

    keys = envDict.keys()
    if sortByName:
        keys = sorted(keys)

    if mode == 1:
        for k in keys:
            print ('set %s=%s' % (k, envDict[k]))
    else:
        for k in keys:
            print ('%s=%s' % (k, envDict[k]))

#-----------------------------------
# printContents
#-----------------------------------
#
#-----------------------------------
def printContents(basePath, **kwargs):
    '''
    loadConf

    basePath:
    name [ndesign_base]:
    appName [.]
    version [.]:
    osType [.]:
    osName [.]: ...
    searchPath [.]:

    sortByName [True]:
    indentStr [""]:
    recursive [True]:
    '''
    name = kwargs.get("name", "ndesign_base")
    appName = kwargs.get("appName", ".")
    version = kwargs.get("version", ".")
    osType = kwargs.get("osType", ".")
    osName = kwargs.get("osName", ".")
    searchPath = kwargs.get("searchPath", ".")

    sortByName = kwargs.get("sortByName", True)
    indentStr = kwargs.get("indentStr", "")
    recursive = kwargs.get("recursive", True)

    depth = kwargs.get("depth", 0)
    parentName = kwargs.get("parentName", "")

    path = getConfPath(basePath, name, searchPath)
    if not path or not os.path.exists(path):
        print ('[%s] not found' % path)
        return

    filterStr = '/'.join(('application', appName, 'version', version, osType, osName))
    configDict = util_json._loadJson(path)
    result = searchConf(configDict.get('data', {}), filterStr, returnKeys=True)
    if sortByName:
        result = sorted(result)

    parentList = configDict.get('info', {}).get('parent', [])
    if parentList and recursive:
        if not isinstance(parentList, list):
            parentList = [parentList]
        for n in parentList:
            printContents(path, name=n,
                appName = appName, version = version, osType = osType, osName = osName,
                searchPath = searchPath,
                sortByName = sortByName,
                indentStr = indentStr,
                recursive = recursive,
                depth=depth + 1,
                parentName = name,
            )

    if parentName:
        print ("[%s] usedBy [%s]" % (name, parentName))
    else:
        print ("[%s]" % (name))
    #print ("%s" % (path))
    #print
    for i in result:
        print ("%s%s" % (indentStr * depth, i))
    print

#-----------------------------------
#-----------------------------------
if __name__ == '__main__':
    #args = sys.argv[:]
    args = [r"Y:\tool\ND_Tools\python\ND_appEnv\nfork.py", r"TOUKI/maya/2015/amd64/win", r"C:\Program Files\Autodesk\Maya2015\bin\maya.exe", r'-script "Y:\tool\ND_Tools\batch\ND_launcher\app\setup/userSetup.mel"']
    print(args)

    if len(args) < 3:
        print ('python "%s" "proj/maya/2015/amd64/win" command options...' % (__file__))

    name = args.pop(0)
    app_mode = args.pop(0)

    #-----------------------------------
    filePath = '/'.join([ND_TOOL_PATH_default, "ND_appEnv/projects/dummy.json"])

    keys = ["name", "appName", "version", "osType", "osName"]
    values = ["ndesign_base", ".", ".", ".", "."]
    options = app_mode.split('/')
    values[:len(options)] = options
    options = dict(zip(keys, values))

    #-----------------------------------
    # print keys
    #-----------------------------------
    #printContents(filePath, **options)
    #printContents(filePath, recursive=False, **options)

    #-----------------------------------
    envDict = loadConf(filePath, **options)

    #-----------------------------------
    # print bat
    #-----------------------------------
    #printEnvBat(envDict)
    #printEnvBat(envDict, env={})

    import subprocess
    #env = getEnvDict(envDict, expand=True)
    #env = getEnvDict(envDict, env={}, expand=True)
    env = getEnvDict(envDict, env=os.environ, expand=True)

    fork = True
    if fork: args = [u'start', ''] + args
    print (args)

    proc = subprocess.Popen(args, shell=True, env=env, close_fds=True)
    if not fork:
        proc.wait()
