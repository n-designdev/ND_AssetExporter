# -*- coding: utf-8 -*-

import os
import re, glob

import maya.cmds as mc
import maya.mel as mel

from ndPyLibAnimIOExportContain import *

def _getNamespace ():
    print '_getNamespace'
    print mc.namespaceInfo(lon=True)
    namespaces = mc.namespaceInfo(lon=True)
    _nestedNS = []
    for ns in namespaces:
        nestedNS = mc.namespaceInfo(ns, lon=True)
        print ns, nestedNS
        if nestedNS != None:
            _nestedNS += nestedNS
    namespaces += _nestedNS
    namespaces.remove('UI')
    namespaces.remove('shared')
    print namespaces
    return namespaces

def _getAllNodes (namespace, regexArgs):
    if len(regexArgs) == 0:
        regexArgs = ['*']

    nodes = []
    for regex in regexArgs:
        regexN = ''
        if namespace != '':
            regexN += namespace + ':'
        regexN = regexN + regex
        print 'regexN:   ' + regexN
        objs = mc.ls(regexN, type='transform')
        objs += mc.ls(regexN, type='locator')
        print 'objs:'
        print objs

        try:
            objSets = mc.sets(regexN, q=True)
            print 'objSets:   '
            print  objSets

            if len(objs) != 0:
                nodes += objs
            if len(objSets) != 0:
                nodes += objSets
        except:
            pass
        #############################################
        print '@@@@@@@@@@@@@@@@@@@@@@@@'
        print mc.ls('*',type='transform')
        print mc.ls('*:root',type='transform')
        print objs
        ###########################################
        if len(objs) != 0:
            nodes += objs

    nodeShort = []

    for node in nodes:
        nodeShort.append(node.split('|')[-1])

    return nodeShort

def _getConstraintAttributes (nodes):
    attrs = []
    for n in nodes:
        const = mc.listConnections(n, s=True, d=False, p=False, c=True, t='constraint')
        print n, const
        if const is None: continue
        for i in range(0, len(const), 2):
            attrs.append(const[i])
    return attrs

def _getPairBlendAttributes (nodes):
    attrs = []
    for n in nodes:
        pairblend = mc.listConnections(n, s=True, d=False, p=False, c=True, t='pairBlend')
        if pairblend is None: continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs

def _getNoKeyAttributes (nodes):
    attrs = []
    for n in nodes:
        gAttrs = mc.listAttr(n, keyable=True)
        print n, gAttrs
        if gAttrs is None: continue
        for attr in gAttrs:
            if '.' not in attr:
                if mc.listConnections(n+'.'+attr, s=True, d=False) is None:
                    attrs.append(n+'.'+attr)
                    print 'find no key attribute : ' + n + '.' + attr
    return attrs


def _exportAnim (publishpath, oFilename, namespaceList, regexArgs, isFilter):
    outputfiles = []
    sframe = mc.playbackOptions(q=True, min=True)
    eframe = mc.playbackOptions(q=True, max=True)
    ###
    sframe -= 10
    eframe += 10

    namespaces = _getNamespace()

    allNodes = []

    print '***********'
    print namespaces
    print namespaceList
    print '***********'

    for ns in namespaces:
        for _nsList in namespaceList:##ketel
            print _nsList
            print ns
            print regexArgs
            match = re.match(_nsList, ns)
            print match
            if match != None:
                allNodes += _getAllNodes(ns, regexArgs)

    print allNodes
    print '==========================='

    characterSet = mc.ls(type='character')
    if len(characterSet) == 0:
        mc.delete(characterSet)

    mc.select(allNodes)
    baseAnimationLayer = mc.animLayer(q=True, r=True)

    if baseAnimationLayer!=None:
        animLayers = mc.ls(type='animLayer')
        for al in animLayers:
            mc.animLayer(al, e=True, sel=False)
        mc.animLayer(baseAnimationLayer, e=True, sel=True)
        mc.bakeResults(t=(sframe, eframe), sb=True, ral=True)
        print 'merge animation layers'
    mc.select(cl=True)

    attrs = _getNoKeyAttributes(allNodes)
    if len(attrs) != 0:
        mc.setKeyframe(attrs, t=sframe, insertBlend=False)

    attrs = _getConstraintAttributes(allNodes)
    attrs += _getPairBlendAttributes(allNodes)
    if len(attrs)!=0:
        mc.bakeResults(attrs, t=(sframe, eframe), sb=True)

    for ns in namespaces:
        pickNodes = []
        for n in allNodes:
            if ns+':' in n:
                pickNodes.append(n)
        print pickNodes
        if len(pickNodes) != 0:

            outputfiles.append(publishpath+oFilename+'_'+ns+'.ma')
            # ndPyLibAnimIOExportContain(isFilter, ['3', ''], publishpath, x+'_'+ns, pickNodes, 0, 0)
            ndPyLibAnimIOExportContain(isFilter, ['3', ''], publishpath, oFilename+'_'+ns, pickNodes, 0, 0)

    return outputfiles


def ndPyLibExportAnim (regexArgs, isFilter):
    if mc.file(q=True, modified=True):
        mc.warning('please save scene file...')
    return

    filepath = mc.file(q=True, sceneName=True)
    filename = os.path.basename(filepath)

    match = re.match('(P:/Project/[a-zA-Z0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)', filepath)
    if match is None:
        mc.warning('directory structure is not n-design format')
        return

    project  = match.group(1)
    roll     = match.group(3)
    sequence = match.group(4)
    shot     = match.group(5)

    shotpath = os.path.join(project, 'shots', roll, sequence, shot)

    animOutDir = 'Anim'
    publishpath = os.path.join(shotpath, 'publish', animOutDir, filename)

    oFilename = sequence + shot + '_anim'

    if not os.path.exists(shotpath):
        mc.warning('no exist folder...')
        return

def ndPyLibExportAnim2(outputPath,oFilename,namespaceList, regexArgs, isFilter):
    print 'x'*20
    print regexArgs
    print namespaceList
    print outputPath
    _exportAnim(outputPath,oFilename,namespaceList, regexArgs, isFilter)
