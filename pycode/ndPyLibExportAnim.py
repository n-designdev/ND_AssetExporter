# -*- coding: utf-8 -*-
import os, sys
import re, glob
import maya.cmds as cmds
sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode")
from ndPyLibAnimIOExportContain import ndPyLibAnimIOExportContain

def eulerfilter(attr_list):
    for attr in attr_list:
        # anim_cv = map(lambda x: cmds.connectionInfo(obj+x, sfd=True), xyz)
        anim_cv = map(lambda x: x.rstrip('.output'), attr)
        try:
            anim_cv = filter(lambda x: cmds.nodeType(x) in ['animCurveTL', 'animCurveTU', 'animCurveTA', 'animCurveTT'], anim_cv)
            cmds.filterCurve(anim_cv, f='euler')
        except:
            print '# Euler FilterFailed: '+attr+' #'
            continue
        print '# Euler Filter Success: '+attr+' #'
        
        
def get_reference_file(obj):
    return cmds.referenceQuery(obj, f=True)


def reference_ma(ma, ns):
    # cmds.file(ma, reference=True, ns=ns, force=False, pmt=True)
    cmds.file(ma, i=True, ns=ns)


def getNamespace():
    namespaces = cmds.namespaceInfo(lon=True)
    _nestedNS = []
    for ns in namespaces:
        nestedNS = cmds.namespaceInfo(ns, lon=True)
        if nestedNS != None:
            _nestedNS += nestedNS
    namespaces += _nestedNS
    namespaces.remove('UI')
    namespaces.remove('shared')
    return namespaces


def getAllNodes(namespace, regexArgs):
    if len(regexArgs) == 0:
        regexArgs = ['*']
    nodes = []
    for regex in regexArgs:
        if "[None]:" in regex:
            objs.extend(regex.split("[None]:")[-1])
            continue
        regex = regex.lstrip(":")
        if "*" in regex:
            ns_objs = cmds.ls(str(namespace)+":*")
            objs = []
            if regex[0]=="*":
                _regex = regex.replace("*", "")
                objs.extend([i for i in ns_objs[:] if re.search(r"[a-zA-Z0-9_:]{}".format(_regex), i) != None])
            elif regex[-1]=="*":
                _regex = regex.replace("*", "")
                print regex
                objs.extend([i for i in ns_objs[:] if re.search(r"{}:{}[a-zA-Z0-9_:]".format(namespace, regex), i)!= None])
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
    return nodeShort


def getConstraintAttributes(nodes):
    attrs = []
    for n in nodes:
        const = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='constraint')
        if const is None: continue
        for i in range(0, len(const), 2):
            attrs.append(const[i])
    return attrs


def getPairBlendAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='pairBlend')
        if pairblend is None: continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
            const = cmds.listConnections(pairblend, s=True, d=False, p=False, c=True, t='constraint')
            if const is None: continue
            for i in range(0, len(const), 2):
                attrs.append(const[i])
    return attrs


def getMotionPathAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='motionPath')
        if pairblend is None: continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs


def getAddDoubleLinearAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='addDoubleLinear')
        if pairblend is None: continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs


def getTransformConnectionAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='transform')
        if pairblend is None: continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs


def getAnimLayerConnectionAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='animLayer')
        if pairblend is None: continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs


def getAnimCurveAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='animCurveTL')
        if pairblend is not None:
            for i in range(0, len(pairblend), 2):
                attrs.append(pairblend[i])
                continue
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='animCurveTU')
        if pairblend is not None:
            for i in range(0, len(pairblend), 2):
                attrs.append(pairblend[i])
                continue
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='animCurveTA')
        if pairblend is not None:
            for i in range(0, len(pairblend), 2):
                attrs.append(pairblend[i])
                continue
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=True, t='animCurveTT')
        if pairblend is not None:
            for i in range(0, len(pairblend), 2):
                attrs.append(pairblend[i])
                continue
    return attrs


def getNoKeyAttributes(nodes):
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


def getKeyAttributes(nodes):
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
                    pass
                else:
                    attrs.append(n+'.'+attr)
    return attrs


def getNodehasPairBlends(nodes):
    result_nodes = []
    for n in nodes:
        pairblend = cmds.listConnections(n, s=True, d=False, p=False, c=False, t='pairBlend')
        if pairblend is not None:
            result_nodes.append(n)
    return result_nodes


def getPairBlend(node):
    pairblends = cmds.listConnections(node, s=True, d=False, p=False, c=False, t='pairBlend')
    if pairblends is not None:
        for pairblend in pairblends:
            if "pairBlend" in pairblend:
                return pairblend
    return pairblend


def replacePairBlendstoLocator(nodes, sframe, eframe):
    for node in nodes:
        print node
        if "Constraint" in node:
            continue
        blend_attrs = ["outTranslateX", "outTranslateY", "outTranslateZ", "outRotateX", "outRotateY", "outRotateZ"]
        nml_attrs = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
        blend = getPairBlend(node)
        loc = cmds.spaceLocator(n="tmp")[0]
        for blend_attr, attr in zip(blend_attrs, nml_attrs):
            cmds.connectAttr("{}.{}".format(blend, blend_attr),"{}.{}".format(loc, attr))
        cmds.bakeResults(loc, t=(sframe, eframe))
        cmds.delete(blend)
        connect_nodes = cmds.listConnections(node, p=True, s=True)
        for connect_node in connect_nodes:
            if connect_node.split(".")[-1] == "output":
                try:
                    cmds.delete(connect_node.split(".")[0])
                except:
                    pass
        print node, blend
        for attr in nml_attrs:
            cmds.connectAttr("{}.{}".format(loc, attr),"{}.{}".format(node, attr))
        cmds.bakeResults(node, t=(sframe, eframe))
        cmds.delete(loc)


def unlockAttributes(nodes):
    for node in nodes:
        if cmds.getAttr(node, lock=True):
            try:
                cmds.setAttr(node, lock=False)
            except Exception as e:
                pass
                

def unmuteAttributes(nodes):
    for node in nodes:
        try:
            cmds.mute("NursedesseiShip:root_ctrl", d=True)
        except Exception as e:   
            pass


def ExportAnim_body(publishpath, oFilename, strnamespaceList, strregexArgs, isFilter, bake_anim, strextra_dic, framehundle, framerange, scene_timeworp, top_node):
    regexArgsN = [] #regexArgs Normal
    regexArgsAttrs = [] #regexArgs Attribute用
    regexArgs = strregexArgs.split(',')
    namespaceList = strnamespaceList.split(',')
    _namespaceList = namespaceList[:]

    for regexArg in regexArgs:
        regexArg = regexArg.lstrip(":")
        if '.' in regexArg:
            regexArgsAttrs.append(regexArg)
        else:
            regexArgsN.append(regexArg)

    outputfiles = []
    namespaces = getNamespace()
    allNodes = []
    nodeAndAttrs = []

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
        for root in root_list:
            if 'camera_base' in root:
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
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(publishpath))), 'sceneConf.txt').replace('\\', '/'), 'w') as f:
        f.write(str(sframe)+'\n')
        f.write(str(eframe)+'\n')

    for a_ns in namespaces:
        for input_ns in namespaceList:
            match = re.match(input_ns, a_ns)
            if match != None:
                allNodes += getAllNodes(a_ns, regexArgsN)

    for a_ns in namespaceList:
        for regexArgsAttr in regexArgsAttrs:
            regexAttr = a_ns+':'+regexArgsAttr
            if cmds.objExists(regexAttr):
                nodeAndAttrs.append(regexAttr)

    characterSet = cmds.ls(type='character')
    if len(characterSet) == 0:
        cmds.delete(characterSet)
    print "##allNodes##"
    print allNodes
    # allNodes.append("pairBlend1")
    for node in allNodes:
        try:
            cmds.select(node, add=True)
        except:
            pass
    # cmds.select(allNodes)
    baseAnimationLayer = cmds.animLayer(q=True, r=True)

    if baseAnimationLayer!=None and len(cmds.ls(sl=True))!=0 :
        animLayers = cmds.ls(type='animLayer')
        for al in animLayers:
            cmds.animLayer(al, e=True, sel=False)
        cmds.animLayer(baseAnimationLayer, e=True, sel=True)
        cmds.bakeResults(t=(sframe, eframe), sb=True, ral=True, dic=True, pok=True, sm=True)
        # cmds.bakeResults(t=(sframe, eframe), sb=False, ral=False, dic=False, pok=False)
        print 'merge animation layers'
    cmds.select(cl=True)

    if strextra_dic != None:
        for extra_dicitem in strextra_dic:
            _key, item = extra_dicitem.split(':')
        for ns in namespaceList:
            for _nsList in namespaceList:
                _ns = ns.split('*')[1].rstrip('$')
                cmds.setAttr(_ns + ':' + _key, int(item))
                cmds.setKeyframe(_ns + ':' + _key, t=1)
    attrs = getNoKeyAttributes(allNodes)

    if len(nodeAndAttrs) !=0:
        attrs += getNoKeyAttributes(nodeAndAttrs)
    if len(attrs) != 0:
        cmds.setKeyframe(attrs, t=sframe, insertBlend=True)
    attrs = getConstraintAttributes(allNodes)
    # attrs += getPairBlendAttributes(allNodes)
    attrs += getMotionPathAttributes(allNodes)
    attrs += getAddDoubleLinearAttributes(allNodes)
    attrs += getTransformConnectionAttributes(allNodes)
    sub_attrs = []
    for node in allNodes:
        if cmds.listConnections(node, s=True, type="constraint") is not None:
            sub_attrs.extend(list(set(cmds.listConnections(node, s=True, type="constraint"))))
    if bake_anim == True:
        attrs += getNoKeyAttributes(allNodes)
        attrs += getKeyAttributes(allNodes)
        attrs += getAnimLayerConnectionAttributes(allNodes)
    unlockAttributes(attrs)
    unmuteAttributes(attrs)
    if scene_timeworp==True:
        bake_tg = attrs
        bake_tg.extend(sub_attrs)
        time_value_set_list = []
        ref_files = []
        ref_attrs = []
        sframe = cmds.playbackOptions(q=True, min=True)
        eframe = cmds.playbackOptions(q=True, max=True)
        #copy topobjs
        ignore_objs = ['persp','top', 'front', 'side', 'AllRoot']
        top_objs = cmds.ls(assemblies=True)
        top_objs = list(set(top_objs)-set(ignore_objs))
        for top_obj in top_objs:
            if cmds.referenceQuery(top_obj, inr=True):
                ns = top_obj.split(":")[0]
                for in_ns in namespaceList:
                    if re.match(in_ns, ns) != None:
                        ref_file = get_reference_file(top_obj)        
                        reference_ma(ref_file, "tmp_"+ns)
                        ref_files.append([ns, ref_file])
                        for obj in cmds.listRelatives(top_obj, ad=True):
                            try:
                                if cmds.listAttr(obj, keyable=True)!=None:
                                    for attr in cmds.listAttr(obj, keyable=True):
                                        ref_attrs.append(obj+"."+attr)
                            except:
                                pass
                        continue
        #store timewarp
        for t in range(int(sframe),int(eframe+1)):
            cmds.currentTime(t)
            warp_time = cmds.getAttr("time1.outTime", time=t)
            for attr in ref_attrs:
                obj = attr.split(".")[0]
                try:
                    if attr in attrs:           
                        value = cmds.getAttr(attr, time=warp_time)  
                        time_value_set_list.append([t, attr, value])
                except Exception as e:
                    pass
        for ref in ref_files:
            ns = ref[0]
            ref_file = ref[1]
            cmds.file(ref_file, rr=True)
        for ns_obj in cmds.ls("tmp_*:*"):
            try:
                cmds.rename(ns_obj, ns_obj.replace("tmp_", ":"))
            except:
                pass
        #restore timewarp
        cmds.setAttr("time1.enableTimewarp", 0)
        current_f = 0
        for time_list in time_value_set_list:
            frame = time_list[0]
            attr = time_list[1]
            value = time_list[2]
            if current_f !=frame:
                cmds.currentTime(frame)
                current_f = frame
            try:
                cmds.setAttr(attr, value)
                cmds.setKeyframe(attr)
            except:
                pass
    if len(attrs)!=0 and scene_timeworp !=True:
        bake_tg = attrs
        bake_tg.extend(sub_attrs)
        cmds.select(clear=True)
        for obj in bake_tg:
            if cmds.objExists(obj) == True:
                cmds.select(obj, add=True)
        cmds.bakeResults(t=(sframe, eframe), dic=True)
        eulerfilter(attrs)
    for ns in namespaces:
        pickNodes = []
        pickNodesAttr = []
        for n in allNodes:
            if ns+':' in n:
                pickNodes.append(n)
        for n in nodeAndAttrs:
            if ns+':' in n:
                pickNodesAttr.append(n)
        if len(pickNodes) != 0:
            outputfiles.append(publishpath+oFilename+'_'+ns+'.ma')
            ndPyLibAnimIOExportContain(isFilter, ['3', ''], publishpath, oFilename+'_'+ns, pickNodes, pickNodesAttr, 0, 0, frameRange, bake_anim, scene_timeworp)
    return outputfiles


def ndPyLibExportAnim_caller(args):
    argsdic = args
    print "###args###"
    print args
    # outputPath = argsdic['output']
    outputPath = argsdic['animOutput']
    oFilename = argsdic['export_type']
    namespaceList = argsdic['namespace']
    regexArgs = argsdic['export_item']
    bake_anim = argsdic['bake_anim']
    scene_timeworp = argsdic['scene_timeworp']
    top_node = argsdic['topnode']
    if bake_anim == "False" or bake_anim == False:
        bake_anim=False
    elif bake_anim == "True" or bake_anim == True:
        bake_anim=True
    if scene_timeworp == "False" or scene_timeworp == False:
        scene_timeworp=False
    elif scene_timeworp == "True" or scene_timeworp == True:
        scene_timeworp=True
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
    ExportAnim_body(outputPath, oFilename, namespaceList, regexArgs, isFilter, bake_anim, extra_dic, frameHundle, frameRange, scene_timeworp, top_node)
    print "ndPylibExportAnim End"

if __name__ == '__main__':
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode")
    import ndPyLibExportAnim
    reload(ndPyLibExportAnim)
    argsdic = {'shot': 'c001', 'sequence': 's646', 'export_type': 'anim',
    'env_load': 'True', 'Priority': 'u50', 'Group': 'u128gb', 'stepValue': '1.0',
    'namespace': 'NursedesseiDragon',
    'bake_anim': 'True', 'scene_timeworp': 'True',
    # 'animOutput': 'P:/Project/RAM1/shots/ep006/s646/c001/publish/test_charSet/NursedesseiShip/v003/anim/NursedesseiShip.ma',
    'animOutput': 'C:/Users/k_ueda/Desktop/work/NursedesseiDragon',
     'framerange_output': 'True',
     'input_path': 'P:/Project/RAM1/shots/ep006/s646/c001/work/k_ueda/test.ma', 'Pool': 'uram1',
    #  'assetpath': 'P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiShip/publish/Setup/RH/maya/current/NursedesseiShip_Rig_RH.mb',
     'assetpath': 'P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiDragon/publish/Setup/RH/maya/current/NursedesseiDragon_Rig_RH.mb',
      'framerange': 'None', 'chara': 'NursedesseiShip', 'topnode': 'root', 'framehundle': '0', 'project': 'RAM1',
     'testmode': 'True',
    #   'output': 'P:/Project/RAM1/shots/ep006/s646/c001/publish/test_charSet/NursedesseiShip/v003/anim',
      'output': 'C:\Users\k_ueda\Desktop\work',
      'export_item': 'ctrl_set'}
    ndPyLibExportAnim.ndPyLibExportAnim_caller(argsdic)