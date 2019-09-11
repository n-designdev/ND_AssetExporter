# -*- coding: utf-8 -*-
import sys
import os
import subprocess

print sys.version

import yaml


# import psutil
mayaBatch_def = 'C:\\Program Files\\Autodesk\\Maya2015\\bin\\mayabatch.exe'
# mayaBatch = 'C:\\Program Files\\Autodesk\\Maya2018\\bin\\mayabatch.exe'
# mayaBatch =  'C:\\Program Files\\Autodesk\\Maya2018\\bin\\maya.exe'
pythonBatch = 'Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe'
onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')


def abcExport(namespace, exportSet, outputPath, scene, yeti, step_value, project, framerange_output):
    mayaBatch = mayaBatch_def
    if yeti=='True':
        env_load(project)
        mayaBatch = maya_version(project)
    nw_cmd = []
    nw_cmd.append(mayaBatch)
    nw_cmd.append('-command')
    nw_cmd.append('''python(\"import sys;sys.path.append('''+'\''+ onpath +'\''+''');from ndPyLibExportAbc import ndPyLibExportAbc2;ndPyLibExportAbc2(''' +str(namespace) + ''', ''' + str(exportSet) + ''',''' + "\'" + str(outputPath) + "\'" + ''',''' + "\'" + str(step_value) + "\'" + ","  + str(framerange_output)  + ''')\")''')
    nw_cmd.append('-file')
    nw_cmd.append(scene)

    print nw_cmd

    subprocess.call(nw_cmd)


def hairExport(assetPath, namespace, topNode, outputPath, scene):

    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from mayaBasic import *;replaceAsset(''' + "\'" +assetPath + "\'" + ',' + "\'" + namespace + "\'" + ''');exportFile(''' + "\'" + outputPath + "\'" + '''.''' + "\'" + topNode + "\'" + ''')\")''')
    cmd.append('-file')
    cmd.append(scene)
    print cmd
    subprocess.call(cmd)


def abcAttach(assetPath, namespace, topNode, abcPath, outputPath, yeti, project):
    mayaBatch = mayaBatch_def

    if yeti == 'True':
        env_load(project)
        mayaBatch = maya_version(project)

    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from mayaBasic import *;import maya.cmds as mc;saveAs(''' + "\'" + outputPath + "\'" + ''');loadAsset(''' + "\'" + assetPath + "\'" + ''',''' + "\'" + namespace + "\'"+''');selHierarchy=mc.ls(''' + "\'" + topNode + "\'"+''', dag=True);attachABC(''' + "\'" + abcPath + "\'" + ''','''+"\'"+namespace+"\'"+''',selHierarchy);saveAs(''' + "\'" + outputPath + "\'" + ''')\")''')
    print cmd
    subprocess.call(cmd)


def animExport(outputPath, oFilename, namespace, regex, scene, yeti, project, framerange_output):
    # print '$$$$$$$$$animExport$$$$$$$$$$$$'
    # print 'outputPath: ' + outputPath
    # print 'oFilename: ' + oFilename
    # print 'namespace: ' + namespace
    # print 'regex: ' + regex
    # print 'scene: ' + scene
    # print 'yeti: ' + yeti
    # print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
    mayaBatch = mayaBatch_def
    if yeti == 'True':
        env_load(project)
        mayaBatch = maya_version(project)

    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys; sys.path.append('''+'\'' + onpath + '\'' + ''');from ndPyLibExportAnim import ndPyLibExportAnim2;ndPyLibExportAnim2(''' +"\'" + outputPath + "\'" + ''',''' + "\'" + str(oFilename) + "\'"  + "," + str(namespace) + "," + str(regex) + ","  + "0" + "," + str(framerange_output)  + ''');\")''')
    cmd.append('-file')
    cmd.append(scene)
    print cmd
    subprocess.call(cmd)


def animAttach(assetPath, namespace, animPath, outputPath, yeti, project):
    # print '+++++++animAttach+++++++++++'
    # print 'assetPath: ' + assetPath
    # print 'namespace: ' + namespace
    # print 'animPath: ' + animPath
    # print 'outputPath: ' + outputPath
    # print '++++++++++++++++++++++++++++'
    mayaBatch = mayaBatch_def
    if yeti == 'True':
        env_load(project)
        mayaBatch = maya_version(project)

    x = assetPath
    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from mayaBasic import *;saveAs(''' + "\'" + outputPath + "\'" + ''');loadAsset(''' +  "\'" + assetPath + "\'" + "," + "\'"+ namespace + "\'" +''');loadAsset(''' + "\'" + assetPath + "\'" + "," +"\'"+ namespace +'_anim' + "\'" + ''');saveAs(''' + "\'" + outputPath + "\'" + ''');\")''')
    print cmd
    subprocess.call(cmd)


def animReplace(namespace, animPath, scene, yeti, project):
    mayaBatch = mayaBatch_def
    if yeti == 'True':
        env_load(project)
        mayaBatch = maya_version(project)

    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from mayaBasic import *;replaceAsset(''' +"\'" + animPath + "\'" + "," + "\'" + namespace + '_anim' + "\'" + ''');save();\")''')
    cmd.append('-file')
    cmd.append(scene)
    print cmd
    subprocess.call(cmd)


def camExport(outputPath, oFilename, camScale, scene):
    mayaBatch = mayaBatch_def
    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from ndPyLibExportCam import ndPyLibExportCam2;ndPyLibExportCam2(''' +"\'" + outputPath + "\'" + "," + "\'" + oFilename + "\'" + "," + str(camScale) + ''');\")''')
    cmd.append('-file')
    cmd.append(scene)
    print cmd
    subprocess.call(cmd)


def repABC(scenePath, repAbcPath, yeti, project):
    mayaBatch = mayaBatch_def
    if yeti == 'True':
        env_load(project)
        mayaBatch = maya_version(project)

    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' +''');from mayaBasic import *;replaceABCPath(''' + "\'" + repAbcPath + "\'" + ''');save();\")''')
    cmd.append('-file')
    cmd.append(scenePath)
    print cmd
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

    f = open(project_app_launcher, "r+")
    data = yaml.load(f)

    f.close()

    for dcc in dcc_tools:
        for version in data["launch_%s" % dcc]["versions"]:
            #print version, type(version)
            args = data["launch_%s" % dcc]["windows_args"]

            if dcc == 'maya':

               renderinfo =  version.replace('(','').split(')')

    ryear = renderinfo[0]
    print ryear
    return  'C:\\Program Files\\Autodesk\\Maya'+ryear+'\\bin\\mayabatch.exe'
