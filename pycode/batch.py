# -*- coding: utf-8 -*-
import sys
import os
import subprocess

# import psutil
# mayaBatch = 'C:\\Program Files\\Autodesk\\Maya2015\\bin\\mayabatch.exe'
mayaBatch = 'C:\\Program Files\\Autodesk\\Maya2018\\bin\\mayabatch.exe'
# mayaBatch =  'C:\\Program Files\\Autodesk\\Maya2018\\bin\\maya.exe'
pythonBatch = 'C:\\Program Files\\Shotgun\\Python\\python.exe'
onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

def abcExport (namespace, exportSet, outputPath, scene, yeti, step_value):
    if yeti==True:
        print '@@@@@@@@@@@@@@@@@@'
        print "load yeti"

    env_load()

    print '@@@@@@@@@@@@@@'
    print yeti
    nw_cmd = []
    nw_cmd.append(mayaBatch)
    nw_cmd.append('-command')
    nw_cmd.append('''python(\"import sys;sys.path.append('''+'\''+ onpath +'\''+ ''');from ndPyLibExportAbc import ndPyLibExportAbc2;ndPyLibExportAbc2(''' +str(namespace) + ''', ''' + str(exportSet) + ''',''' + "\'" + str(outputPath) + "\'" + ''',''' + "\'" + str(step_value) + "\'" + ''')\")''')
    nw_cmd.append('-file')
    nw_cmd.append(scene)

    print nw_cmd

    x = subprocess.call(nw_cmd)

def hairExport (assetPath, namespace, topNode, outputPath, scene):
    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from mayaBasic import *;replaceAsset(''' + "\'" +assetPath + "\'" + ',' + "\'" + namespace + "\'" + ''');exportFile(''' + "\'" + outputPath + "\'" + '''.''' + "\'" + topNode + "\'" + ''')\")''')
    cmd.append('-file')
    cmd.append(scene)
    print cmd
    ret = subprocess.call(cmd)

def abcAttach (assetPath, namespace,topNode, abcPath, outputPath):#Syntax Error
    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from mayaBasic import *;import maya.cmds as mc;saveAs(''' + "\'" + outputPath + "\'" + ''');loadAsset(''' + "\'" + assetPath + "\'" + ''',''' + "\'" + namespace + "\'"+''');selHierarchy=mc.ls(''' + "\'" + topNode + "\'"+''', dag=True);attachABC(''' + "\'" + abcPath + "\'" + ''','''+"\'"+namespace+"\'"+''',selHierarchy);saveAs(''' + "\'" + outputPath + "\'" + ''')\")''')
    print cmd
    ret = subprocess.call(cmd)

def animExport (outputPath, oFilename, namespace, regex, scene, yeti):
    print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
    print outputPath
    print oFilename
    print namespace
    print regex
    print scene
    print yeti
    print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
    if yeti==True:
        env_load()
        print 'CVCCCCCCCCCCCCCCC'
    else:
        env_load()

    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys; sys.path.append('''+'\'' + onpath + '\'' + ''');from ndPyLibExportAnim import ndPyLibExportAnim2;ndPyLibExportAnim2(''' +"\'" + outputPath + "\'" + ''',''' + "\'" + str(oFilename) + "\'"  + "," + str(namespace) + "," + str(regex) + ''', 0);\")''')
    cmd.append('-file')
    cmd.append(scene)
    print cmd
    subprocess.call(cmd)

def animAttach (assetPath, namespace, animPath, outputPath):

    print '++++++++++++++++++'
    print assetPath
    print namespace
    print animPath
    print outputPath
    print '++++++++++++++++++'

    x = assetPath
    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from mayaBasic import *;saveAs(''' + "\'" + outputPath + "\'" + ''');loadAsset(''' +  "\'"+x+"\'" + "," + "\'"+ namespace + "\'" +''');loadAsset(''' + "\'" + x + "\'" + "," +"\'"+ namespace +'_anim' + "\'" + ''');saveAs(''' + "\'" + outputPath + "\'" + ''');\")''')

    print cmd
    ret = subprocess.call(cmd)

def animReplace (namespace, animPath, scene):
    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from mayaBasic import *;replaceAsset(''' +"\'" + animPath + "\'" + "," + "\'" + namespace + '_anim' + "\'" + ''');save();\")''')
    cmd.append('-file')
    cmd.append(scene)
    print cmd
    subprocess.call(cmd)

def camExport (outputPath, oFilename, camScale, scene):

    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' + ''');from ndPyLibExportCam import ndPyLibExportCam2;ndPyLibExportCam2(''' +"\'" + outputPath + "\'" + "," + "\'" + oFilename + "\'" + "," + str(camScale) + ''');\")''')
    cmd.append('-file')
    cmd.append(scene)
    print cmd
    subprocess.call(cmd)

def repABC (scenePath, repAbcPath):
    cmd = []
    cmd.append(mayaBatch)
    cmd.append('-command')
    cmd.append('''python(\"import sys;sys.path.append('''+'\'' + onpath + '\'' +''');from mayaBasic import *;replaceABCPath(''' + "\'" + repAbcPath + "\'" + ''');save();\")''')
    cmd.append('-file')
    cmd.append(scenePath)
    print cmd
    subprocess.call(cmd)

def env_load():
    # os.environ["_TMP_VRAY_VER"]='36004'

    os.environ["_TMP_ARNOLD_VER"] = "2101"

    ND_TOOL_PATH_default = "Y:/tool/ND_Tools/python"

    env_key = "ND_TOOL_PATH_PYTHON"
    ND_TOOL_PATH = os.environ.get(env_key, ND_TOOL_PATH_default)
    for path in ND_TOOL_PATH.split(';'):
        path = path.replace('\\', '/')
        if path in sys.path: continue
        sys.path.append(path)
    import env_loader
    env_loader.run(sys.argv[:], fork=True)
