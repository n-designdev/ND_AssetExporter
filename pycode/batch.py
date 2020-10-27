# -*- coding: utf-8 -*-
import sys
import os
import subprocess

import yaml

# mayaBatch = 'C:/Program Files/Autodesk/Maya2017/bin/mayabatch.exe'
# pythonBatch = 'Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe'
pythonBatch = 'C:\\Program Files]\\Shotgun\\Python\\python.exe'
onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')


def mayacmd_maker(unique_order, file=None, mayaBatch=None):
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
    # cmd.append('-log')
    # cmd.append('C:/Users/k_ueda/Desktop/temp/maya_result.txt')

    if file is not None:
        cmd.append('-file')
        cmd.append(file)
    return cmd

def abcExport(**kwargs):

    argsdic = kwargs

    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    namespace = argsdic['namespace']
    outputPath = argsdic['abcOutput'] + '/' + namespace + 'abc'
    assetPath = argsdic['assetpath'].replace("\\","/")
    exportitem = argsdic['exportitem']

    original_litte = (
        'from ndPyLibExportAbc import ndPyLibExportAbc2;'
        'ndPyLibExportAbc2({})'.format(argsdic)
    )
    cmd = mayacmd_maker(original_litte, argsdic['inputpath'], mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\', '\\')
    subprocess.call(cmd)


def abcAttach(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    assetPath = argsdic['assetpath'].replace("\\","/")
    exportitem = argsdic['exportitem']
    namespace = argsdic['ns']
    topNode = argsdic['Ntopnode']
    outputPath = argsdic['attachPath']
    abcOutput = argsdic['abcOutput']###ここの名前を合わせる

    original_litte = (
        'from mayaBasic import *;'
        'import maya.cmds as cmds;'
        'saveAs(\'{}\');'.format(outputPath) +
        'loadAsset(\'{}\', \'{}\');'.format(assetPath, namespace) +
        'selHierarchy=cmds.ls(\'{}\', dag=True);'.format(topNode) +
        'attachABC(\'{}\', \'{}\', selHierarchy);'.format(abcOutput, namespace) +
        'saveAs(\'{}\')'.format(outputPath)
    )

    cmd = mayacmd_maker(original_litte, None, mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\', '\\')

    subprocess.call(cmd)


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
        'save();'
    )

    cmd = mayacmd_maker(original_litte, scenepath, mayaBatch)
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
        'from ndPyLibExportAnim import ndPyLibExportAnim2;'
        'ndPyLibExportAnim2({})'.format(str(argsdic))
    )
    cmd = mayacmd_maker(original_litte, argsdic['inputpath'], mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\','\\')
    print cmd
    p = subprocess.Popen(cmd, shell=True)
    p.wait()

def animAttach(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    outputPath = argsdic['charaOutput']
    assetPath = argsdic['assetpath'].replace("\\","/")
    animPath = argsdic['animOutput']
    namespace = argsdic['ns']
    print "#######"
    print "outputpath: ", outputPath
    print "assetPath: ", assetPath
    print "animPath: ", animPath
    print "namespace: ", namespace
    print "#######"

    original_litte = (
        'from mayaBasic import *;'
        'import maya.cmds as cmds;'
        'saveAs(\'{}\');'.format(outputPath) +
        'loadAsset(\'{}\', \'{}\');'.format(assetPath, namespace) +
        'loadAsset(\'{}\', \'{}_anim\');'.format(animPath, namespace) +
        'saveAs(\'{}\')'.format(outputPath)
    )
    cmd = mayacmd_maker(original_litte, None, mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\', '\\')

    subprocess.call(cmd)


def animReplace(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    animPath = argsdic['animPath'].replace("\\","/")
    namespace = argsdic['ns']
    scene = argsdic['scene']

    original_litte = (
        'from mayaBasic import *;'
        'replaceAsset(\'{}\', \'{}_anim\');'.format(animPath, namespace) +
        'save();'
    )
    cmd = mayacmd_maker(original_litte, scene, mayaBatch)
    cmd[2] = str(cmd[2]).replace('\\\\', '\\')
    subprocess.call(cmd)


def camExport(**kwargs):
    argsdic = kwargs
    if argsdic['env_load']:
        env_load(argsdic['project'])
        mayaBatch = maya_version(argsdic['project'])
    scene = argsdic['inputpath']
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

    import ND_lib.util.files as util_file
    import ND_lib.util.path as util_path

    toolkit_path = "Y:\\tool\\ND_Tools\\shotgun"
    app_launcher_path = "config\\env\\includes\\app_launchers.yml"
    dcc_tools = ["maya", "nuke", "nukex"]


    # プロジェクト名からShotgunの設定を取得する
    project_app_launcher = "%s\\ND_sgtoolkit_%s\\%s" % (toolkit_path, project.lower(), app_launcher_path)

    f = open(project_app_launcher, "r")
    data = yaml.load(f)
    f.close()

    for dcc in dcc_tools:
        for version in data["launch_%s" % dcc]["versions"]:
            #print version, type(version)
            args = data["launch_%s" % dcc]["windows_args"]

            if dcc == 'maya':
               renderinfo = version.replace('(','').split(')')

    ryear = renderinfo[0]
    # return  'C:\\Program Files\\Autodesk\\Maya2019'+'\\bin\\mayabatch.exe'
    return  'C:\\Program Files\\Autodesk\\Maya'+ryear+'\\bin\\mayabatch.exe'


# ['C:\\Program Files\\Autodesk\\Maya2018\\bin\\mayabatch.exe', '-command',
# 'python("import sys;sys.path.append(\'Y:/tool/ND_Tools/DCC/ND_AssetExporter/pycode\');
# from ndPyLibExportAnim import ndPyLibExportAnim2;
# ndPyLibExportAnim2({\\\'Group\\\': \\\'u16gb\\\', \\\'sequence\\\': \\\'s002\\\', \\\'exporttype\\\': \\\'anim\\\', \\\'env_load\\\': \\\'True\\\', \\\'Priority\\\': \\\'u50\\\', \\\'shot\\\': \\\'c001\\\', \\\'stepValue\\\': \\\'1.0\\\', \\\'namespace\\\': \\\'NBGNml_Rig_AH\\\', \\\'bakeAnim\\\': \\\'True\\\', \\\'abcOutput\\\': \\\'P:/Project/NW/shots/roll01/s002/c001/publish/test_charSet/NBGNml/v026/abc/NBGNml.abc\\\', \\\'framerange_output\\\': \\\'True\\\', \\\'inputpath\\\': \\\'P:/Project/NW/shots/roll01/s002/c001/work/kane/30_Anm/maya/scenes/s002c001_lay_v002.ma\\\', \\\'Pool\\\': \\\'unw\\\', \\\'assetpath\\\': \\\'P:/Project/NW/assets/chara/NBG/NBGNml/publish/Setup/AH/maya/current/NBGNml_Rig_AH.mb\\\', \\\'framerange\\\': \\\'None\\\', \\\'chara\\\': \\\'NBGNml\\\', \\\'topnode\\\': \\\'root\\\', \\\'framehundle\\\': \\\'0\\\', \\\'project\\\': \\\'NW\\\', \\\'testmode\\\': \\\'True\\\', \\\'output\\\': \\\'P:/Project/NW/shots/roll01/s002/c001/publish/test_charSet/NBGNml/v026/anim\\\', \\\'exportitem\\\': \\\'ctrl_sets\\\'});"
# )', '-file', 'P:/Project/NW/shots/roll01/s002/c001/work/kane/30_Anm/maya/scenes/s002c001_lay_v002.ma']