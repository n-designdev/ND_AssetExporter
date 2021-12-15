# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import yaml

onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

def maya_cmd_maker(unique_order, mayafile=None, mayaBatch=None):
    maya_cmd = (
        "import sys;"
        "sys.path.append(\'{}/maya\');".format(onpath)
    )
    maya_cmd = maya_cmd + unique_order
    cmd = [mayaBatch]
    cmd.append('-command')
    cmd.append('python(\"{}\")'.format(maya_cmd.replace(';', '\;').replace('\'', '\\\'')))
    if mayafile is not None:
        cmd.append('-file')
        cmd.append(mayafile)
    return cmd


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
    data = yaml.safe_load(f)
    f.close()

    for dcc in dcc_tools:
        for version in data["launch_%s" % dcc]["versions"]:
            args = data["launch_%s" % dcc]["windows_args"]
            if dcc == 'maya':
               renderinfo = version.replace('(','').split(')')

    ryear = renderinfo[0]
    # return  'C:\\Program Files\\Autodesk\\Maya2019'+'\\bin\\mayabatch.exe'
    return  'C:\\Program Files\\Autodesk\\Maya'+ryear+'\\bin\\mayabatch.exe'


def animExport(**kwargs):
    env_load(kwargs['project'])
    mayaBatch = maya_version(kwargs['project'])
    unique_order = (
        # 'from mayaBasic import *;'
        'from ndPyLibExportAnim import ndPyLibExportAnim_caller;'
        'ndPyLibExportAnim_caller({})'.format(kwargs)
    )
    cmd = maya_cmd_maker(unique_order, kwargs['input_path'], mayaBatch)
    print(cmd)
    # import pdb;pdb.set_trace()
    subprocess.run(cmd)


def animAttach(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    file_name_space = kwargs['file_name_space']
    
    ma_ver_path = kwargs['ma_ver_path']
    anim_ver_path = kwargs['anim_ver_path']

    asset_path = kwargs['asset_path']
    unique_order = (
        'from mayaBasic import *;'
        'import maya.cmds as cmds;'
        'saveAs(\'{}\');'.format(ma_ver_path) +
        'loadAsset(\'{}\', \'{}\');'.format(asset_path, file_name_space) +
        'loadAsset(\'{}\', \'{}_anim\');'.format(anim_ver_path, file_name_space) +
        'saveAs(\'{}\')'.format(ma_ver_path))
    cmd = maya_cmd_maker(unique_order, None, mayaBatch)
    subprocess.run(cmd)


def animReplace(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    ma_current_path = argsdic['ma_current_path']
    anim_current_path = argsdic['anim_current_path']
    file_name_space = argsdic['file_name_space']
    unique_order = (
        'from mayaBasic import *;'
        'replaceAsset(\'{}\', \'{}_anim\');'.format(anim_current_path, file_name_space) +
        'save();'
    )
    cmd = maya_cmd_maker(unique_order, ma_current_path, mayaBatch)
    subprocess.run(cmd)


def abcExport(**kwargs):
    env_load(kwargs['project'])
    mayaBatch = maya_version(kwargs['project'])
    unique_order = (
            'from ndPyLibExportAbc import ndPyLibExportAbc2;'
            'ndPyLibExportAbc2({})'.format(yaml.safe_dump(kwargs)))
    cmd = maya_cmd_maker(unique_order, mayafile=kwargs['input_path'], mayaBatch=mayaBatch)
    subprocess.run(cmd)


def abcAttach(**kwargs):
    env_load(kwargs['project'])
    mayaBatch = maya_version(kwargs['project'])
    asset_path = kwargs['asset_path']
    namespace = kwargs['scene_ns']
    topnode = namespace + ':' + kwargs['topnode']
    outputPath = kwargs['attachPath']
    abcOutput = kwargs['abcOutput']###ここの名前を合わせる

    unique_order = (
            'from mayaBasic import *;'
            'import maya.cmds as cmds;'
            'saveAs(\'{}\');'.format(outputPath) +
            'loadAsset(\'{}\', \'{}\');'.format(asset_path, namespace) +
            'selHierarchy=cmds.ls(\'{}\', dag=True);'.format(topnode) +
            'attachABC(\'{}\', \'{}\', selHierarchy);'.format(abcOutput, namespace) +
            'saveAs(\'{}\')'.format(outputPath))
    cmd = maya_cmd_maker(unique_order, mayafile=None, mayaBatch=mayaBatch)
    subprocess.run(cmd)


def repABC(**kwargs):
    scenepath = argsdic['charaOutput']
    repAbcPath = argsdic['abcOutput'].replace("\\","/")
    env_load(argsdic['project'])
    mayaBatch = maya_version(argsdic['project'])
    unique_order = (
            'from mayaBasic import *;'
            'replaceABCPath(\'{}\');'.format(repAbcPath) +
            'save();')
    cmd = maya_cmd_maker(unique_order, scenepath, mayaBatch)
    subprocess.run(cmd)


def camExport(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    unique_order = (
        'from ndPyLibExportCam import ndPyLibExportCam2;'
        'ndPyLibExportCam2({})'.format(yaml.safe_dump(argsdic))
    )
    cmd = maya_cmd_maker(unique_order, kwargs['input_path'], mayaBatch)
    subprocess.run(cmd)