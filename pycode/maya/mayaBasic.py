# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
import os

def newScene ():
    cmds.file(new=True)

def saveAs (outputPath):
    ext = os.path.splitext(outputPath)[1]
    cmds.file(rn=outputPath)
    if ext == '.ma':
        cmds.file(f=True, s=True, type='mayaAscii')
    else:
        cmds.file(f=True, s=True, type='mayaBinary')

def save ():
    print 'save!!!'*10
    cmds.file(s=True, f=True)

def replaceAsset (assetPath, namespace):
    cmds.warning( 'replace start ')
    refs = cmds.ls(type='reference')
    try:
        refs.remove('sharedReferenceNode')
    except Exception as e:
        print e
    try:
        refs.remove(namespace.replace('_animRN','')+':_UNKNOWN_REF_NODE_')
    except Exception as e:
        print e
    tgtRN = ''
    for r in refs:
        ns = mel.eval('referenceQuery -ns ' + r)[1:]
        print ns, namespace, r
        if namespace == ns:
            tgtRN = r
            break
        else:
            print refs
            if len(refs) == 2:
                if "_animRN" in refs[0]:
                    tgtRN = r
                    break 
            else:
                print r+' can not replace'
    try:
        print assetPath, tgtRN
        cmds.file(assetPath, loadReference=tgtRN)
    except Exception as e:
        print e
        print "replace not done..." 
        return
    cmds.warning('replace end')


def exportFile (outputPath, topNode):
    cmds.warning('export start')
    cmds.select(topNode)
    cmds.file(outputPath, typ='mayaAscii', f=True, es=True, pr=True)
    cmds.warning('export end')

def loadAsset (assetPath, namespace):
    cmds.file(assetPath, r=True, namespace=namespace, mergeNamespacesOnClash=False, ignoreVersion=True)

def attachABC (abcPath,namespace,hierarchyList):
    if not cmds.pluginInfo('AbcImport', q=True, l=True):
        cmds.loadPlugin('AbcImport')
    hierarchy = ' '.join(hierarchyList)
    mel.eval('AbcImport -mode import -fitTimeRange -debug -connect ' + '\"' + hierarchy + '\" ' + '\"' + abcPath + '\"')

    outputFile = os.path.dirname(os.path.dirname(abcPath))+'/yetimem.txt'
    print "outputFile: {}".format(outputFile)
    print "namespace: {}".format(namespace)
    try:
        with open(outputFile, 'r') as fp:

            inyeticasch = fp.readline()
            outyeticasch = fp.readline()

            print inyeticasch.rstrip('\n')
            print outyeticasch.rstrip('\n')

            print namespace+':pgYetiMaya'+namespace+'Shape.cacheFileName'

            cmds.setAttr(namespace+':pgYetiMaya'+namespace+'Shape.cacheFileName', inyeticasch.rstrip('\n'), type='string')
            cmds.setAttr(namespace+':pgYetiMaya'+namespace+'Shape.outputCacheFileName', outyeticasch.rstrip('\n'), type='string')
    except:
        pass
        # setAttr - type "string" _LXM:pgYetiMaya_LXMShape.cacheFileName "a"
        # setAttr - type "string" _LXM:pgYetiMaya_LXMShape.outputCacheFileName "b"

def replaceABCPath (repAbcPath):
    abcNodes = cmds.ls(type='AlembicNode')
    if len(abcNodes) != 0:
        cmds.setAttr(abcNodes[0]+'.abc_File', repAbcPath, type='string')
    print 'x' * 20

def delUnknownNode ():
    unknownNodes = cmds.ls(type='unknown')
    if len(unknownNodes) != 0:
        cmds.delete(unknownNodes)

def setEnv ():
    os.environ['VRAY_FOR_MAYA2015_MAIN_X64'] = 'Y:\\users\\env\\vray\\maya2015_vray_adv_36004\\maya_vray'
    os.environ['VRAY_TOOLS_MAYA2015_X64'] = 'Y:\\users\\env\\vray\\maya2015_vray_adv_36004\\vray\\bin'
    os.environ['MAYA_PLUG_IN_PATH'] = 'Y:/users/env/vray/maya2015_vray_adv_36004/maya_vray/plug-ins;'+os.environ['MAYA_PLUG_IN_PATH']
    os.environ['VRAYPATH'] = 'Y:\\users\\env\\vray\\maya2015_vray_adv_36004'
    os.environ['VRAY_FOR_MAYA2015_PLUGINS_X64'] = 'Y:/users/env/vray/maya2015_vray_adv_36004/maya_vray/vrayplugins'
    os.environ['MAYA_SCRIPT_PATH'] = 'Y:/users/env/vray/maya2015_vray_adv_36004/maya_vray/scripts;'+os.environ['MAYA_SCRIPT_PATH']
    os.environ['VRAY_VER'] = '36004'
    os.environ['VRAY_AUTH_CLIENT_FILE_PATH'] = 'Y:\\users\\env\\maya\\lic'
    os.environ['VRAY_OSL_PATH_MAYA2015_X64'] = 'Y:\\users\\env\\vray\\maya2015_vray_adv_36004\\vray\\opensl'

    for k,v in os.environ.items():
        print k, v

if __name__ == '__main__':
    namespace = 'DDNinaNml'
    assetPath = 'P:/Project/mem2/assets/chara/DDNina/DDNinaNml/publish/model/RenderHigh/maya/current/DDNinaNml_mdlRH.mb'
    topNode = 'DDNinaNml'
    abcPath = 'P:/Project/mem2/shots/roll04/s116D/c009D/publish/animGeo/s116Dc009D_anm_v004.ma/s116Dc009D_animGeoCache_DDNinaNml.abc'

    loadAsset(assetPath, namespace)

    selHierarchy = cmds.ls(namespace+':'+topNode, dag=True)
    attachABC(abcPath, selHierarchy)
