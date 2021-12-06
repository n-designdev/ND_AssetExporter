# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import yaml

onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

def mayacmd_maker(unique_order, mayafile=None, mayaBatch=None):
    batch_firstact = (
        "import sys;"
        "sys.path.append(\'{}\');".format(onpath)
        + unique_order.replace('\'', '\\\'')
    )
    if mayaBatch==None:
        mayaBatch = 'C:/Program Files/Autodesk/Maya2017/bin/mayabatch.exe'
    cmd = [mayaBatch]
    cmd.append('-command')
    cmd.append("python(\"{}\")".format(batch_firstact))
    if mayafile is not None:
        cmd.append('-file')
        cmd.append(mayafile)
    return cmd


def abcExport(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    original_litte = (
        'from ndPyLibExportAbc import ndPyLibExportAbc2;'
        'ndPyLibExportAbc2({})'.format(argsdic))
    cmd = mayacmd_maker(original_litte, argsdic['input_path'], mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\', '\\')
    subprocess.call(cmd)
    print cmd


def abcAttach(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    assetPath = argsdic['assetpath'].replace("\\","/")
    namespace = argsdic['scene_ns']
    topnode = namespace + ':' + argsdic['topnode']
    outputPath = argsdic['attachPath']
    abcOutput = argsdic['abcOutput']###ここの名前を合わせる

    original_litte = (
        'from mayaBasic import *;'
        'import maya.cmds as cmds;'
        'saveAs(\'{}\');'.format(outputPath) +
        'loadAsset(\'{}\', \'{}\');'.format(assetPath, namespace) +
        'selHierarchy=cmds.ls(\'{}\', dag=True);'.format(topnode) +
        'attachABC(\'{}\', \'{}\', selHierarchy);'.format(abcOutput, namespace) +
        'saveAs(\'{}\')'.format(outputPath))
    cmd = mayacmd_maker(original_litte, None, mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\', '\\')
    subprocess.call(cmd)
    print "##abcAttach"
    print cmd

def repABC(**kwargs):
    argsdic = kwargs
    scenepath = argsdic['charaOutput']
    repAbcPath = argsdic['abcOutput'].replace("\\","/")
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    original_litte = (
        'from mayaBasic import *;'
        'replaceABCPath(\'{}\');'.format(repAbcPath) +
        'save();')
    cmd = mayacmd_maker(original_litte, scenepath, mayaBatch)
    print "##repABC##"
    print cmd
    subprocess.call(cmd)


def animExport(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    else:
        mayaBatch = None
    original_litte = (
        'from mayaBasic import *;'
        'from ndPyLibExportAnim import ndPyLibExportAnim_caller;'
        'ndPyLibExportAnim_caller({})'.format(str(argsdic))
    )
    cmd = mayacmd_maker(original_litte, argsdic['input_path'], mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\','\\')
    subprocess.call(cmd)


def animAttach(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    outputPath = argsdic['charaOutput']
    assetPath = argsdic['assetpath'].replace("\\","/")
    animPath = argsdic['animOutput']
    scene_ns = argsdic['scene_ns']
    original_litte = (
        'from mayaBasic import *;'
        'import maya.cmds as cmds;'
        'saveAs(\'{}\');'.format(outputPath) +
        'loadAsset(\'{}\', \'{}\');'.format(assetPath, scene_ns) +
        'loadAsset(\'{}\', \'{}_anim\');'.format(animPath, scene_ns) +
        'saveAs(\'{}\')'.format(outputPath))
    cmd = mayacmd_maker(original_litte, None, mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\', '\\')
    subprocess.call(cmd)


def animReplace(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    anim_path = argsdic['animOutput']
    scene_ns = argsdic['scene_ns']
    scene_path = argsdic['scene_path']
    original_litte = (
        'from mayaBasic import *;'
        'replaceAsset(\'{}\', \'{}_anim\');'.format(anim_path, scene_ns) +
        'save();'
    )
    cmd = mayacmd_maker(original_litte, scene_path, mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\', '\\')
    print "##animReplace##"
    print cmd
    subprocess.call(cmd)


def camExport(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    scene = argsdic['input_path']
    original_litte = (
        'from ndPyLibExportCam import ndPyLibExportCam2;'
        'ndPyLibExportCam2({})'.format(str(argsdic))
    )
    cmd = mayacmd_maker(original_litte, scene, mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\', '\\')
    subprocess.call(cmd)


def env_load(project):
    ND_TOOL_PATH_default = "Y:/tool/ND_Tools/python"
    env_key = "ND_TOOL_PATH_PYTHON"
    ND_TOOL_PATH = os.environ.get(env_key, ND_TOOL_PATH_default)
    for path in ND_TOOL_PATH.split(';'):
        path = path.replace('\\', '/')
        if path in sys.path: continue
        sys.path.append(path)
    import env_loader
    env_loader.run(project, fork=True)


def maya_version(project):
    # ------------------------------------
    env_key = 'ND_TOOL_PATH_PYTHON'
    ND_TOOL_PATH = os.environ.get(env_key,'Y:/tool/ND_Tools/python')
    for path in ND_TOOL_PATH.split(';'):
        path = path.replace('\\','/')
        if path in sys.path: continue
        sys.path.append(path)
    #------------------------------------

    toolkit_path = "Y:\\tool\\ND_Tools\\shotgun"
    app_launcher_path = "config\\env\\includes\\app_launchers.yml"
    dcc_tools = ["maya", "nuke", "nukex"]
    project_app_launcher = "%s\\ND_sgtoolkit_%s\\%s" % (toolkit_path, project.lower(), app_launcher_path)

    f = open(project_app_launcher, "r")
    data = yaml.load(f)
    f.close()

    for dcc in dcc_tools:
        for version in data["launch_%s" % dcc]["versions"]:
            args = data["launch_%s" % dcc]["windows_args"]
            if dcc == 'maya':
               renderinfo = version.replace('(','').split(')')

    ryear = renderinfo[0]
    # return  'C:\\Program Files\\Autodesk\\Maya2019'+'\\bin\\mayabatch.exe'
    return  'C:\\Program Files\\Autodesk\\Maya'+ryear+'\\bin\\mayabatch.exe'