# -*- coding: utf-8 -*-

import os, sys
import re, glob

import maya.cmds as cmds
import maya.mel as mel

from ndPyLibAnimIOExportContain import *

def spsymbol_remover(litteral, sp_check=None):
    listitem = ['exportitem']
    if sp_check in listitem:
        litteral = re.sub(':|\'|{|}', '', litteral)
    else:
        litteral = re.sub(':|\'|,|{|}', '', litteral)
    url_list = ['inputpath', 'assetpath']
    if sp_check in url_list:
        litteral = litteral.replace('/', ':/')
    return litteral


def strdict_parse(original_string):
    parsed_dic = {}
    original_string_iter = iter(original_string)
    for key, item in zip(original_string_iter, original_string_iter):
        key = spsymbol_remover(key)
        item = spsymbol_remover(item, key)
        parsed_dic[key] = item
    return parsed_dic


def _getNamespace():
    namespaces = cmds.namespaceInfo(lon=True)
    print namespaces
    _nestedNS = []
    for ns in namespaces:
        nestedNS = cmds.namespaceInfo(ns, lon=True)
        if nestedNS != None:
            _nestedNS += nestedNS
    namespaces += _nestedNS
    namespaces.remove('UI')
    namespaces.remove('shared')
    return namespaces


def _getAllNodes (namespace, regexArgs):
    if len(regexArgs) == 0:
        regexArgs = ['*']
    print regexArgs
    nodes = []
    for regex in regexArgs:
        if "*" in regex:
            ns_objs = cmds.ls(str(namespace)+":*")
            objs = []
            if regex[0]=="*":
                objs.extend([i for i in ns_objs[:] if re.search(r"[a-zA-Z0-9_:]{}".format(regex), i) != None])
            elif regex[-1]=="*":
                objs.extend([i for i in ns_objs[:] if re.search(r"{}:{}[a-zA-Z0-9_:]*".format(namespace, regex), i)!= None])
            nodes += objs
        else:
            regexN = ''
            if namespace != '':
                regexN += namespace + ':'
            regexN = regexN + regex
            print 'regexN:   ' + regexN
            objs = cmds.ls(regexN, type='transform')
            objs += cmds.ls(regexN, type='locator')
            objs += cmds.ls(regexN, type="joint")
            objs += cmds.ls(regexN, shapes=True)
            try:
                objSets = cmds.sets(regexN, q=True)
                objSets = cmds.sets(regexN, q=True)
            except:
                objSets = []
            if objSets is None:
                objSets = []
            print "objSets:{}".format(objSets)
            if len(objs) != 0:
                nodes += objs
            if len(objSets) != 0:
                nodes += objSets

    nodes = list(set(nodes))
    nodeShort = []

    for node in nodes:
        nodeShort.append(node.split('|')[-1])
    print "allNodes:", nodeShort
    return nodeShort


def _getConstraintAttributes (nodes):
    attrs = []
    for n in nodes:
        const = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='constraint')
        if const is None: continue
        for i in range(0, len(const), 2):
            attrs.append(const[i])
    return attrs


def _getPairBlendAttributes (nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='pairBlend')
        if pairblend is None: continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs


def _getNoKeyAttributes (nodes):
    attrs = []
    for n in nodes:
        if '.' in n:
            n = n.split('.')[0]
        gAttrs = cmds.listAttr(n, keyable=True)
        print n, gAttrs
        if gAttrs is None: continue
        for attr in gAttrs:
            if '.' not in attr:
                if cmds.listConnections(n+'.'+attr, s=True, d=False) is None:
                    attrs.append(n+'.'+attr)
                    print 'find no key attribute : ' + n + '.' + attr
    return attrs


def _exportAnim (publishpath, oFilename, strnamespaceList, strregexArgs, isFilter, bakeAnim, strextra_dic, framehundle, framerange):

    regexArgsN = [] #regexArgs Normal
    regexArgsAttrs = [] #regexArgs Attribute用
    regexArgs = strregexArgs.split(',')
    namespaceList = strnamespaceList.split(',')
    _namespaceList = namespaceList[:]

    for regexArg in regexArgs:
        if '.' in regexArg:
            regexArgsAttrs.append(regexArg)
        else:
            regexArgsN.append(regexArg)

    outputfiles = []
    namespaces = _getNamespace()
    allNodes = []
    nodeAndAttrs = [] # ns+node+attr, ex:ketel_evo:wave8.minRadius

    frameHandle = framehundle
    if frameHandle == 'None':
        frameHandle = 0

    sframe = cmds.playbackOptions(q=True, min=True) - float(frameHandle)
    eframe = cmds.playbackOptions(q=True, max=True) + float(frameHandle)

    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(publishpath))), "resolutionConf.txt").replace("\\", "/"), "w") as f:
        f.write(str(cmds.getAttr("defaultResolution.width"))+"\n")
        f.write(str(cmds.getAttr("defaultResolution.height"))+"\n")

    if 'camera_base' in _namespaceList:
        root_list = cmds.ls("root", r=True)
        print root_list
        for root in root_list:
            if 'camera_base' in root:
                # for x in cmds.ls(root.split(":")[0]+":*"):
                try:
                    cam_objs = cmds.listRelatives(root, ad=True)
                    camera_name = root.split(":")[0]
                    cam_objs.remove(camera_name+":aim_jt1")
                    cam_objs.remove(camera_name+":aim_jt2")
                    cmds.bakeResults(cam_objs, t=(sframe, eframe), sb=1, simulation=True)
                    for x in cmds.listRelatives(root, ad=True):
                        if "Constraint" in cmds.objectType(x):
                            cmds.delete(x)
                    cmds.select(root)
                    _path = os.path.dirname(publishpath)+"/"+root.split(":")[0]
                    cmds.file(_path, f=True, es=True, typ="mayaAscii", ch=1, chn=1, exp=1, sh=0)
                    outputfiles.append(_path)
                except Exception as e:
                    print e

        return outputfiles

    if 'camera_simple' in _namespaceList:
        root_list = cmds.ls("camera", r=True)
        for root in root_list:
            if 'camera_simple' in root:
                try:
                    # for x in cmds.ls(root.split(":")[0]+":*"):
                    cam_objs = cmds.listRelatives(root, ad=True)
                    camera_name = root.split(":")[0]
                    cmds.bakeResults(cam_objs, hi='below', t=(sframe, eframe), simulation=True)
                    for x in cmds.listRelatives(root, ad=True):
                        if "Constraint" in cmds.objectType(x):
                            cmds.delete(x)
                    cmds.select(root)
                    _path = os.path.dirname(publishpath)+"/"+root.split(":")[0]
                    cmds.file(_path, f=True, es=True, typ="mayaAscii", ch=1, chn=1, exp=1, sh=0)
                    outputfiles.append(_path)
                except Exception as e:
                    print e
        return outputfiles

    if framerange != None:
        frameRange = [sframe, eframe]
    else:
        frameRange = framerange

    ### フレームレンジ書き込み ###
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(publishpath))), 'sceneConf.txt').replace('\\', '/'), 'w') as f:
        f.write(str(sframe)+'\n')
        f.write(str(eframe)+'\n')

    print "getting allNodes..."
    print "nanespaceList: {}".format(namespaceList)
    print "namespaces: {}".format(namespaces)
    for ns in namespaces:
        for _nsList in namespaceList:
            match = re.match(_nsList, ns)
            if match != None:
                print ns, regexArgsN
                allNodes += _getAllNodes(ns, regexArgsN)
    print "getting nodeAndAttrs"
    print "regexArgsAttrs:{}".format(regexArgsAttrs)
    for ns in namespaceList:
        for regexArgsAttr in regexArgsAttrs:
            regexAttr = ns+':'+regexArgsAttr
            if cmds.objExists(regexAttr):
                nodeAndAttrs.append(regexAttr)

    characterSet = cmds.ls(type='character')
    if len(characterSet) == 0:
        cmds.delete(characterSet)

    cmds.select(allNodes)
    baseAnimationLayer = cmds.animLayer(q=True, r=True)

    if baseAnimationLayer!=None and len(cmds.ls(sl=True))!=0 :
        animLayers = cmds.ls(type='animLayer')
        for al in animLayers:
            cmds.animLayer(al, e=True, sel=False)

        cmds.animLayer(baseAnimationLayer, e=True, sel=True)
        cmds.bakeResults(t=(sframe, eframe), sb=True, ral=True)
        print 'merge animation layers'
    cmds.select(cl=True)

    if strextra_dic != None:
        for extra_dicitem in strextra_dic:
            _key, item = extra_dicitem.split(':')
        for ns in namespaceList:
            for _nsList in namespaceList:
                _ns = ns.split('*')[1].rstrip('$')
                cmds.setAttr(_ns + ':' + _key, int(item)) # 整数限定
                cmds.setKeyframe(_ns + ':' + _key, t=1)

    attrs = _getNoKeyAttributes(allNodes)

    if len(nodeAndAttrs) !=0:
        attrs += _getNoKeyAttributes(nodeAndAttrs)
    if len(attrs) != 0:
        cmds.setKeyframe(attrs, t=sframe, insertBlend=False)

    attrs = _getConstraintAttributes(allNodes)
    attrs += _getPairBlendAttributes(allNodes)
    if len(attrs)!=0:
        cmds.bakeResults(attrs, t=(sframe, eframe), sb=True)

    for ns in namespaces:
        pickNodes = []
        pickNodesAttr = []
        for n in allNodes:
            # print ns, n
            if ns+':' in n:
                pickNodes.append(n)
        for n in nodeAndAttrs:
            if ns+':' in n:
                pickNodesAttr.append(n)
        if len(pickNodes) != 0:
            outputfiles.append(publishpath+oFilename+'_'+ns+'.ma')
            # ndPyLibAnimIOExportContain(isFilter, ['3', ''], publishpath, x+'_'+ns, pickNodes, 0, 0)
            ndPyLibAnimIOExportContain(isFilter, ['3', ''], publishpath, oFilename+'_'+ns, pickNodes, pickNodesAttr, 0, 0, frameRange, bakeAnim)

    return outputfiles


def ndPyLibExportAnim (regexArgs, isFilter):
    if cmds.file(q=True, modified=True):
        cmds.warning('please save scene file...')
    return

    filepath = cmds.file(q=True, sceneName=True)
    filename = os.path.basename(filepath)

    match = re.match('(P:/Project/[a-zA-Z0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)', filepath)
    if match is None:
        cmds.warning('directory structure is not n-design format')
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
        cmds.warning('no exist folder...')
        return

def ndPyLibExportAnim2(args):
    # argsdic = strdict_parse(args)
    # strdict_parse(args)
    argsdic = args
    outputPath = argsdic['output']
    oFilename = argsdic['exporttype']
    namespaceList = argsdic['namespace']
    regexArgs = argsdic['exportitem']
    bakeAnim = argsdic['bakeAnim']
    # extradic = argsdic['extra_dic']
    try:
        frameHundle = argsdic['framehundle']
    except KeyError:
        frameHundle = 0
    try:
        frameRange = argsdic['framerange']
    except KeyError:
        frameRange = None
    extra_dic = None
    isFilter = 1
    _exportAnim(outputPath, oFilename, namespaceList, regexArgs, isFilter, bakeAnim, extra_dic, frameHundle, frameRange)
    print "ndPylibExportAnim End"
    return