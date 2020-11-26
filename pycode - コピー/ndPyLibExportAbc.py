# -*- coding: utf-8 -*-

import os
import re

import maya.cmds as mc
import maya.mel as mel


def norefresh (func):
    def _norefresh (*args):
        try:
            mc.refresh(suspend=True)
            return func(*args)
        finally:
            mc.refresh(suspend=False)
    return _norefresh


def _getNamespace ():
    namespaces = mc.namespaceInfo(lon=True, r=True)
    namespaces.remove('UI')
    namespaces.remove('shared')
    return namespaces

def _getAllNodes (outputPath, namespace, _regexArgs):

    if len(_regexArgs) == 0:
        regexArgs = ['*']

    nodes = []
    regexArgs = _regexArgs.split(',')

    for regex in regexArgs:

        objs = []
        objSets = []
        regexN = ''
        if namespace != '':
            regexN += namespace + ':'
        regexN = regexN + regex
        try:
            objs = mc.ls(regexN, type='transform')
            objSets = mc.sets(regexN, q=True)
        except:
            continue
        if objs != None:
            if len(objs) != 0:
                nodes += objs
        if objSets != None:
            if len(objSets) != 0:
                nodes += objSets
        yetiobjs = mc.ls(namespace+':yetiSet')
        if len(yetiobjs) != 0:
            dirname = os.path.dirname(outputPath)
            dirname = os.path.dirname(dirname)
            inyeticasch = mc.getAttr(namespace+":pgYetiMaya"+namespace+"Shape.cacheFileName")
            outyeticasch = mc.getAttr(namespace+":pgYetiMaya"+namespace+"Shape.outputCacheFileName")
            outputFile = os.path.join(dirname,'yetimem.txt')
            try:
                with open(outputFile, 'w') as fp:
                    fp.write(inyeticasch)
                    fp.write('\n')
                    fp.write(outyeticasch)
            except:
                pass
    return nodes


def _exportAbc2 (outputPath, _namespaceList, regexArgs, step_value, frameHundle, _frameRange):

    namespaceList = _namespaceList.split(',')
    for i, namespaceItem in enumerate(namespaceList):
        namespaceList[i] = '[a-zA-Z0-9_:]*{}$'.format(namespaceItem)
    sframe = mc.playbackOptions(q=True, min=True)
    eframe = mc.playbackOptions(q=True, max=True)

    if _frameRange != 'None':
        _frameRange = _frameRange.lstrip('u')
        frameRange = _frameRange.split(',')
        sframe = float(frameRange[0])
        eframe = float(frameRange[1])

    ###
    sframe -= float(frameHundle)
    eframe += float(frameHundle)

    allNamespaces = []
    if len(namespaceList) == 0:
        allNamespaces = _getNamespace()
    else:
        tmpNS = _getNamespace()
        for _nsList in namespaceList:
            for _ns in tmpNS:
                match = re.match(_nsList, _ns)
                if match != None:
                    allNamespaces.append(_ns)

    allNodes = {}

    for ns in allNamespaces:
        allNodes[ns] = _getAllNodes(outputPath, ns, regexArgs)

    if not mc.pluginInfo('AbcExport', q=True, l=True):
        mc.loadPlugin('AbcExport')

    for ns in allNamespaces:
        pickNodes = []
        pickNodes = allNodes[ns]
        if len(pickNodes) == 0: continue

        if ':' in ns:
            ns = ns.replace(':', '___')
        outputPath_ns = outputPath.replace('.abc', '_'+ns+'.abc')

        strAbc = ''
        strAbc = strAbc + '-frameRange '
        strAbc = strAbc + str(sframe) + ' '
        strAbc = strAbc + str(eframe) + ' '
        strAbc = strAbc + '-uvWrite '
        # strAbc = strAbc + '-worldSpace '
        strAbc = strAbc + '-writeVisibility '
        strAbc = strAbc + '-eulerFilter '
        strAbc = strAbc + '-dataFormat ogawa '
        strAbc = strAbc + '-step '
        strAbc = strAbc + str(step_value) + ' '
        for pn in pickNodes:
            strAbc = strAbc + '-root '
            strAbc = strAbc + pn + ' '
        strAbc = strAbc + '-file '
        strAbc = strAbc + outputPath_ns

        print 'AbcExport -j ' + strAbc
        mel.eval('AbcExport -verbose -j ' + '"' + strAbc + '"')

def ndPyLibExportAbc2 (args):
    argsdic = args
    outputPath = argsdic['abcOutput']
    namespaceList = argsdic['namespace']
    try:
        step_value = argsdic['step_value']
    except KeyError:
        step_value = 1.0
    frameHundle = argsdic['framehundle']
    frameRange = argsdic['framerange']
    regexArgs = argsdic['exportitem']
    _exportAbc2(
        outputPath, namespaceList,
        regexArgs, step_value,
        frameHundle, frameRange)


