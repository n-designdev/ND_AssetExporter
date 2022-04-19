# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import yaml


onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

def maya_cmd_maker(unique_order, mayafile=None, mayaBatch=None):
    maya_cmd = (
        "import sys;"+
        "sys.path.append(\'{}/maya_lib\');".format(onpath)+
        "sys.path.append(\'{}\');".format(onpath)
    )
    maya_cmd = maya_cmd + unique_order
    cmd = [mayaBatch]
    cmd.append('-command')
    cmd.append('python(\"{}\")'.format(maya_cmd.replace(';', '\;').replace('\'', '\\\'')))
    if mayafile is not None:
        cmd.append('-file')
        cmd.append(mayafile)
    return cmd


def env_load(project, is_env_load):
    print('###env_load###')
    print(is_env_load)
    print('###env_load###')
    if is_env_load is True:
        ND_TOOL_PATH_default = "Y:/tool/ND_Tools/python"
        env_key = "ND_TOOL_PATH_PYTHON"
        ND_TOOL_PATH = os.environ.get(env_key, ND_TOOL_PATH_default)
        for path in ND_TOOL_PATH.split(';'):
            path = path.replace('\\', '/')
            if path in sys.path: continue
            sys.path.append(path)
        import shell_lib.env_loader
        shell_lib.env_loader.run(project, fork=True)


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
    # return  'C:\\Program Files\\Autodesk\\Maya'+ryear+'\\bin\\mayabatch.exe'
    return  'C:\\Program Files\\Autodesk\\Maya2020\\bin\\mayabatch.exe'


def animExport(**kwargs):
    env_load(kwargs['project'], kwargs['env_load'])
    mayaBatch = maya_version(kwargs['project'])
    unique_order = (
        # 'from maya_lib.mayaBasic import *;'
        'from ndPyLibExportAnim import export_anim_main;'
        'export_anim_main(**{})'.format(kwargs)
    )
    cmd = maya_cmd_maker(unique_order, mayafile=kwargs['input_path'], mayaBatch=mayaBatch)
    print(cmd)
    import pprint
    pprint.pprint(cmd)
    subprocess.call(cmd, shell=True)


def animAttach(**kwargs):
    env_load(kwargs['project'], kwargs['env_load'])
    mayaBatch = maya_version(kwargs['project'])
    argsdic = kwargs
    file_name_space = kwargs['file_name_space']
    
    ma_ver_path = kwargs['ma_ver_path']
    anim_ver_path = kwargs['anim_ver_path']

    asset_path = kwargs['asset_path']
    unique_order = (
        'from maya_lib.mayaBasic import *;'
        'import maya.cmds as cmds;'
        'saveAs(\'{}\');'.format(ma_ver_path) +
        'loadAsset(\'{}\', \'{}\');'.format(asset_path, file_name_space) +
        'loadAsset(\'{}\', \'{}_anim\');'.format(anim_ver_path, file_name_space) +
        'saveAs(\'{}\')'.format(ma_ver_path))
    cmd = maya_cmd_maker(unique_order, mayaBatch=mayaBatch)
    subprocess.call(cmd, shell=True)


def animReplace(**kwargs):
    env_load(kwargs['project'], kwargs['env_load'])
    mayaBatch = maya_version(kwargs['project'])
    argsdic = kwargs
    ma_current_path = argsdic['ma_current_path']
    publish_current_anim_path = argsdic['publish_current_anim_path']
    file_name_space = argsdic['file_name_space']
    unique_order = (
        'from maya_lib.mayaBasic import *;'
        'replaceAsset(\'{}\', \'{}_anim\');'.format(publish_current_anim_path, file_name_space) +
        'save();'
    )
    cmd = maya_cmd_maker(unique_order, mayafile=ma_current_path, mayaBatch=mayaBatch)
    print(cmd)
    subprocess.call(cmd, shell=True)


def abcExport(**kwargs):
    env_load(kwargs['project'], kwargs['env_load'])
    argsdic = kwargs
    mayaBatch = maya_version(kwargs['project'])
    unique_order = (
            'from ndPyLibExportAbc import ndPyLibExportAbc_caller;'
            'ndPyLibExportAbc_caller({})'.format(argsdic))
    cmd = maya_cmd_maker(unique_order, mayafile=kwargs['input_path'], mayaBatch=mayaBatch)
    subprocess.call(cmd,  shell=True)


def abcAttach(**kwargs):
    env_load(kwargs['project'], kwargs['env_load'])
    mayaBatch = maya_version(kwargs['project'])
    mayaBatch = 'C:\\Program Files\\Autodesk\\Maya2020\\bin\\mayabatch.exe'
    asset_path = kwargs['asset_path']
    namespace = kwargs['file_namespace']
    top_node = namespace + ':' + kwargs['top_node']
    ma_ver_file = kwargs['ma_ver_file']
    abc_ver_file = kwargs['abc_ver_file']

    unique_order = (
            'from maya_lib.mayaBasic import *;'
            'import maya.cmds as cmds;'
            'saveAs(\'{}\');'.format(ma_ver_file) +
            'loadAsset(\'{}\', \'{}\');'.format(asset_path, namespace) +
            'selHierarchy=cmds.ls(\'{}\', dag=True);'.format(top_node) +
            'attachABC(\'{}\', \'{}\', selHierarchy);'.format(abc_ver_file, namespace) +
            'saveAs(\'{}\')'.format(ma_ver_file))
    cmd = maya_cmd_maker(unique_order, mayaBatch=mayaBatch)
    print(cmd)
    subprocess.call(cmd, shell=True)
    print(cmd)


def repABC(**kwargs):
    env_load(kwargs['project'], kwargs['env_load'])
    mayaBatch = maya_version(kwargs['project'])
    argsdic = kwargs
    ma_current_path = argsdic['ma_current_file']
    abc_current_path = argsdic['ma_current_file']
    mayaBatch = 'C:\\Program Files\\Autodesk\\Maya2020\\bin\\mayabatch.exe'
    unique_order = (
            'from maya_lib.mayaBasic import *;'
            'replaceABCPath(\'{}\');'.format(abc_current_path) +
            'save();')
    cmd = maya_cmd_maker(unique_order, mayafile=ma_current_path, mayaBatch=mayaBatch)
    print(cmd)
    subprocess.call(cmd, shell=True)


def camExport(**kwargs):
    argsdic = kwargs
    env_load(argsdic['project'], kwargs['env_load'])
    mayaBatch = 'C:\\Program Files\\Autodesk\\Maya2020\\bin\\mayabatch.exe'
    unique_order = (
        'from ndPyLibExportCam import ndPylibExportCam_caller;'
        'ndPylibExportCam_caller(**{})'.format(argsdic))
    cmd = maya_cmd_maker(unique_order, kwargs['input_path'], mayaBatch)
    subprocess.call(cmd, shell=True)


# x =['C:\\Program Files\\Autodesk\\Maya2020\\bin\\mayabatch.exe', '-command', 'python("import sys\\;sys.path.append(\\\'y:/tool/ND_Tools/DCC/ND_AssetExporter_dev/pycode/maya\\\')\\;from maya_lib.mayaBasic import *\\;import maya.cmds as cmds\\;saveAs(\\\'P:/Project/RAM1/shots/ep022/s2227/c008/publish/test_charSet/NursedesseiDragon/v015/NursedesseiDragon.ma\\\')\\;loadAsset(\\\'P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiDragon/publish/Setup/RH/maya/current/NursedesseiDragon_Rig_RH.mb\\\', \\\'NursedesseiDragon\\\')\\;selHierarchy=cmds.ls(\\\'NursedesseiDragon:root\\\', dag=True)\\;attachABC(\\\'P:/Project/RAM1/shots/ep022/s2227/c008/publish/test_charSet/NursedesseiDragon/v015/abc/NursedesseiDragon_abc.abc\\\', \\\'NursedesseiDragon\\\', selHierarchy)\\;saveAs(\\\'P:/Project/RAM1/shots/ep022/s2227/c008/publish/test_charSet/NursedesseiDragon/v015/NursedesseiDragon.ma\\\')")']

# import subprocess
# subprocess.call(x)