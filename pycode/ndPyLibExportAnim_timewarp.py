# -*- coding: utf-8 -*-
import os

import maya.cmds as cmds
import maya.mel as mel


def Euler_filter(obj_list):
    xyz = ['.rotateX', '.rotateY', '.rotateZ']
    for obj in obj_list:
        anim_cv = map(lambda x: cmds.connectionInfo(obj+x, sfd=True), xyz)
        anim_cv = map(lambda x: x.rstrip('.output'), anim_cv)
        try:
            anim_cv = filter(lambda x: cmds.nodeType(x) in ['animCurveTL', 'animCurveTU', 'animCurveTA', 'animCurveTT'], anim_cv)
            cmds.filterCurve(anim_cv, f='euler')
        except:
            print '# Euler FilterFailed: '+obj+' #'
            continue
        print '# Euler Filter Success: '+obj+' #'


def get_reference_file(obj):
    return cmds.referenceQuery(obj, f=True)


def reference_ma(ma):
    cmds.file(ma, reference=True, ns="{}_test")




def ndPyLibExportAnim_timewarp(publishpath, oFilename, strnamespaceList, strregexArgs, isFilter, bake_anim, strextra_dic, framehundle, framerange, scene_timeworp):
    ns = "NursedesseiDragon"
    top_node = "root"
    ref_ma = get_reference_file("{}:{}".format(ns, top_node))
    reference_ma(ref_ma, "{}_test".format(ns))

    regexArgsN = [] #regexArgs Normal
    regexArgsAttrs = [] #regexArgs Attribute用
    regexArgs = strregexArgs.split(',')
    namespaceList = strnamespaceList.split(',')

    for regexArg in regexArgs:
        regexArg = regexArg.lstrip(":")
        if '.' in regexArg:
            regexArgsAttrs.append(regexArg)
        else:
            regexArgsN.append(regexArg)

    outputfiles = []
    namespaces = _getNamespace()
    allNodes = []
    nodeAndAttrs = []

    frameHandle = framehundle
    if frameHandle == 'None':
        frameHandle = 0

    sframe = cmds.playbackOptions(q=True, min=True) - float(frameHandle)
    eframe = cmds.playbackOptions(q=True, max=True) + float(frameHandle)

    for a_ns in namespaces:
        for input_ns in namespaceList:
            match = re.match(input_ns, a_ns)
            if match != None:
                allNodes += _getAllNodes(a_ns, regexArgsN)

    for a_ns in namespaceList:
        for regexArgsAttr in regexArgsAttrs:
            regexAttr = a_ns+':'+regexArgsAttr
            if cmds.objExists(regexAttr):
                nodeAndAttrs.append(regexAttr)

    characterSet = cmds.ls(type='character')
    if len(characterSet) == 0:
        cmds.delete(characterSet)
    for node in allNodes:
        try:
            cmds.select(node, add=True)
        except:
            pass
    baseAnimationLayer = cmds.animLayer(q=True, r=True)

    if baseAnimationLayer!=None and len(cmds.ls(sl=True))!=0 :
        animLayers = cmds.ls(type='animLayer')
        for al in animLayers:
            cmds.animLayer(al, e=True, sel=False)
        cmds.animLayer(baseAnimationLayer, e=True, sel=True)
        cmds.bakeResults(t=(sframe, eframe), sb=True, ral=True, dic=True, pok=True, sm=True)
    cmds.select(cl=True)

    if strextra_dic != None:
        for extra_dicitem in strextra_dic:
            _key, item = extra_dicitem.split(':')
        for ns in namespaceList:
            for _nsList in namespaceList:
                _ns = ns.split('*')[1].rstrip('$')
                cmds.setAttr(_ns + ':' + _key, int(item))
                cmds.setKeyframe(_ns + ':' + _key, t=1)
    attrs = _getNoKeyAttributes(allNodes)

    if len(nodeAndAttrs) !=0:
        attrs += _getNoKeyAttributes(nodeAndAttrs)
    if len(attrs) != 0:
        cmds.setKeyframe(attrs, t=sframe, insertBlend=True)
    attrs = _getConstraintAttributes(allNodes)
    attrs += _getPairBlendAttributes(allNodes)
    attrs += _getMotionPathAttributes(allNodes)
    attrs += _getAddDoubleLinearAttributes(allNodes)
    attrs += _getTransformConnectionAttributes(allNodes)

    #ConstraintがあってBakeできないものの対応のテスト
    sub_attrs = []
    for node in allNodes:
        if cmds.listConnections(node, s=True, type="constraint") is not None:
            sub_attrs.extend(list(set(cmds.listConnections(node, s=True, type="constraint"))))

    # attrs += _getAnimCurveAttributes(allNodes)
    if bake_anim is True:
        attrs += _getNoKeyAttributes(allNodes)
        attrs += _getKeyAttributes(allNodes)
        attrs += _getAnimLayerConnectionAttributes(allNodes)

    for t in range(int(sframe),int(eframe+1)):
        cmds.currentTime(t)
        for attr in attrs:
            ns = attr.split(":")[0]
            tg_attr = attr.replace(ns, ns+"_test")

            cmds.setKetframe(tg_attr, t=t, v=cmds.getAttr(attr))

    if framerange != None:
        frameRange = [sframe, eframe]
    else:
        frameRange = framerange

    Euler_filter(attrs)
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
#end of ndPylibExportCam_bakeCamera


def ndPyLibPlatform(text):
    prefix = 'nd'
    otsr = ''
    otsr = otsr+'['+prefix+']'+text+'\n'

    print(otsr)
#end of ndPyLibPlatform


def ndPyLibExportCam(camOutput, CameraScale, frameHundle, _frameRange):
    camOutput = camOutput.replace("\\", "/")
    isImagePlane = 1
    outputfiles = []
    if _frameRange == 'None' or _frameRange == None:
        sframe = cmds.playbackOptions(q=True, min=True)#innner frame
        eframe = cmds.playbackOptions(q=True, max=True)
    else:
        _frameRange = _frameRange.lstrip('u')
        frameRange = _frameRange.split(',')
        sframe = float(frameRange[0])
        eframe = float(frameRange[1])
    sframe -= float(frameHundle)
    eframe += float(frameHundle)
    if isImagePlane !=1:
        if len(cmds.ls(type='imagePlane'))!=0:
            cmds.delete(cmds.ls(type='imagePlane'))
            cmds.warning('delete imagePlanes...')

    cams = ndPyLibExportCam_bakeCamera(sframe, eframe, CameraScale)
    if cams is None:
        return

    if cmds.objExists('cam_grp'):
        cmds.delete('cam_grp')

    cmds.group(em=True, n='cam_grp')
    toCam = []
    for i in range(0, len(cams), 3):
        toCam.append(cams[i])
        toCam.append(cams[i+1])
        toCam.append(cams[i+2])
        cmds.parent(toCam[i],'cam_grp')
        cmds.rename(toCam[i],toCam[i+2].split("|")[-1])

    cmds.select('cam_grp')
    publishdir = os.path.dirname(camOutput)

    if not os.path.exists(publishdir):
        os.mkdir(publishdir)
    camOutput_abc = camOutput.replace('.ma', '.abc')
    camOutput_ma = camOutput.replace('.abc', '.ma').replace('/abc/', '/')
    camOutput_fbx = camOutput_ma.replace('.ma', '.fbx')

    cmds.file(camOutput_ma, force=True, options='v=0', typ='mayaAscii', pr=True, es=True)

    sceneConfpath = os.path.join(publishdir, '..', 'sceneConf.txt')
    with open(sceneConfpath, 'w') as f:
        f.write(str(sframe)+'\n')
        f.write(str(eframe)+'\n')

    # if isFbx == 1:
    if cmds.pluginInfo('fbxmaya', q=True, l=True) == 0:
        cmds.loadPlugin('fbxmaya')
    cmds.file(camOutput_fbx, force=True, options='v=0', typ='FBX export', pr=True, es=True)
    # if isABC == 1:
    if cmds.pluginInfo('AbcExport', q=True, l=True) == 0:
        cmds.loadPlugin('AbcExport')
    strAbc = ''
    strAbc = strAbc+'-frameRange '+str(sframe)+' '+str(eframe)+' '
    strAbc = strAbc+'-uvWrite '
    strAbc = strAbc+'-worldSpace '
    strAbc = strAbc+'-eulerFilter '
    strAbc = strAbc+'-dataFormat ogawa '
    strAbc = strAbc+ '-root cam_grp '
    strAbc = strAbc+ '-file '+ camOutput_abc #abc
    print ('AbcExport -j ' + strAbc)
    mel.eval('AbcExport -verbose -j ' + '"' + strAbc + '"')
    cmds.file(camOutput_ma, force=True, options='v=0', typ='mayaAscii', pr=True, es=True)
    return outputfiles


def ndPyLibExportCam2(args):
    argsdic = args
    camOutput = argsdic['camOutput'] #ファイル名込み ..Cam/cam/ver**/**_cam.abc
    CameraScale = argsdic['camScale']
    frameHundle = argsdic['framehundle']
    frameRange = argsdic['framerange']
    ndPyLibExportCam(camOutput, CameraScale, frameHundle, frameRange)


def ndPyLibExportCam3(outputPath, cameraScale=-1, frameHundle=5, frameRange="None"):
    animFiles = ndPyLibExportCam(outputPath, cameraScale, frameHundle, frameRange)
    for animFile in animFiles:
        ns = animFile.replace('anim_', '').replace('.ma', '')
        animOutput = opc.publishfullanimpath + '/' + animFile
        charaOutput = opc.publishfullpath + '/' + ns + '.ma'
        argsdic['animOutput'] = animOutput
        argsdic['charaOutput'] = charaOutput
        argsdic['ns'] = ns
        batch.animAttach(**argsdic)



if __name__ == '__main__':
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode")
    import ndPyLibExportAnim_timewarp
    reload(ndPyLibExportAnim_timewarp)
    argsdic = {'shot': 'c001', 'sequence': 's646', 'export_type': 'anim',
    'env_load': 'True', 'Priority': 'u50', 'Group': 'u128gb', 'stepValue': '1.0',
    'namespace': 'NursedesseiDragon',
     'bake_anim': 'True', 'scene_timeworp': 'True',
     'animOutput': 'P:/Project/RAM1/shots/ep006/s646/c001/publish/test_charSet/NursedesseiShip/v003/anim/NursedesseiShip.ma',
     'framerange_output': 'True',
     'input_path': 'P:/Project/RAM1/shots/ep006/s646/c001/work/k_ueda/test.ma', 'Pool': 'uram1',
     'assetpath': 'P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiShip/publish/Setup/RH/maya/current/NursedesseiShip_Rig_RH.mb', 'framerange': 'None', 'chara': 'NursedesseiShip', 'topnode': 'root', 'framehundle': '0', 'project': 'RAM1',
     'testmode': 'True', 'output': 'P:/Project/RAM1/shots/ep006/s646/c001/publish/test_charSet/NursedesseiShip/v003/anim',
      'export_item': 'ctrl_set, root,ctrloffA_set, *ik*,*LOC*, *JNT*, leg_L_grp, leg_R_grp, *fk*'}
    # ndPyLibExportAnim.ndPyLibExportAnim_caller(argsdic)
    ndPyLibExportAnim_timewarp(argsdic)