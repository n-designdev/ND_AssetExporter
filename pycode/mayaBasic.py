# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.mel as mel
import os

def newScene ():
    mc.file(new=True)

def saveAs (outputPath):
    ext = os.path.splitext(outputPath)[1]
    mc.file(rn=outputPath)
    if ext == '.ma':
        mc.file(f=True, s=True, type='mayaAscii')
    else:
        mc.file(f=True, s=True, type='mayaBinary')

def save ():
    print 'save!!!'*10
    mc.file(s=True, f=True)

def replaceAsset (assetPath, namespace):
    mc.warning( 'replace start ')
    print assetPath, namespace
    refs = mc.ls(type='reference')
    try:
        print refs
        refs.remove('sharedReferenceNode')
    except:
        pass
    try:
        refs.remove(namespace.replace('_anim','')+':_UNKNOWN_REF_NODE_')
    except:
        pass
    tgtRN = ''
    for r in refs:
        ns = mel.eval('referenceQuery -ns ' + r)[1:]
        if namespace == ns:
            tgtRN = r
            break
        else:
            if len(refs) == 2:
                if "_animRN" in refs[0]:
                    tgtRN = r
                    break 
            else:
                print r+' can not replace'
    try:
        mc.file(assetPath, loadReference=tgtRN)
    except Exception as e:
        print e
        print "replace not done..." 
        return
    mc.warning('replace end')


def exportFile (outputPath, topNode):
    mc.warning('export start')
    mc.select(topNode)
    mc.file(outputPath, typ='mayaAscii', f=True, es=True, pr=True)
    mc.warning('export end')

def loadAsset (assetPath, namespace):
    mc.file(assetPath, r=True, namespace=namespace, mergeNamespacesOnClash=False, ignoreVersion=True)

def attachABC (abcPath,namespace,hierarchyList):
    if not mc.pluginInfo('AbcImport', q=True, l=True):
        mc.loadPlugin('AbcImport')
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

            mc.setAttr(namespace+':pgYetiMaya'+namespace+'Shape.cacheFileName', inyeticasch.rstrip('\n'), type='string')
            mc.setAttr(namespace+':pgYetiMaya'+namespace+'Shape.outputCacheFileName', outyeticasch.rstrip('\n'), type='string')
    except:
        pass
        # setAttr - type "string" _LXM:pgYetiMaya_LXMShape.cacheFileName "a"
        # setAttr - type "string" _LXM:pgYetiMaya_LXMShape.outputCacheFileName "b"

def replaceABCPath (repAbcPath):
    abcNodes = mc.ls(type='AlembicNode')
    if len(abcNodes) != 0:
        mc.setAttr(abcNodes[0]+'.abc_File', repAbcPath, type='string')
    print 'x' * 20

def delUnknownNode ():
    unknownNodes = mc.ls(type='unknown')
    if len(unknownNodes) != 0:
        mc.delete(unknownNodes)

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

    selHierarchy = mc.ls(namespace+':'+topNode, dag=True)
    attachABC(abcPath, selHierarchy)
