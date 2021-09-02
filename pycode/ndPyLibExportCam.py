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


def ndPyLibExportCam_searchCamera():
    camShapes = cmds.ls(ca=True)
    try:
        camShapes.remove('frontShape')
        camShapes.remove('perspShape')
        camShapes.remove('sideShape')
        camShapes.remove('topShape')
        camShapes.remove('leftShape')
        camShapes.remove('backShape')
        camShapes.remove('bottomShape')
        camShapes.remove('front1Shape')
        camShapes.remove('persp1Shape')
        camShapes.remove('side1Shape')
        camShapes.remove('top1Shape')
        camShapes.remove('persp2Shape')
        camShapes.remove('deformation_camShape')
    except ValueError:
        pass
    for camShape in camShapes[:]:
        if cmds.getAttr("{}.orthographic".format(camShape)):
            camShapes.remove(camShape)

    cams = cmds.listRelatives(camShapes, p=True, f=True)
    camAll = []
    if cams is None:
        return
    for i in range(len(cams)):
        if cmds.referenceQuery(cams[i], inr=True):
            # try:
            #     refFile = cmds.referenceQuery(cmds.referenceQuery("anguirus:asset", rfn=True, tr=True), f=True)
            #     cmds.file(refFile, importReference=True)
            # except:
            #     pass
            try:
                refFile = cmds.referenceQuery(cmds.referenceQuery(cams[i], rfn=True, tr=True), f=True)
                cmds.file(refFile, importReference=True)
            except:
                pass
        camAll.append(cams[i])
        camAll.append(camShapes[i])

    return camAll


def ndPyLibExportCam_bakeCamera(sframe, eframe, CameraScale):
    cams = ndPyLibExportCam_searchCamera()
    if cams is None:
        return
    shapeAttrs = ['fl','hfa','vfa','lsr','fs','fd','sa','coi','ncp','fcp']

    bakeCams = []
    fromCam = []
    toCam = []

    for i in range(0, len(cams), 2):
        toCam.extend(cmds.camera())
        fromCam.append(cams[i])
        fromCam.append(cams[i+1])

    for t in range(int(sframe),int(eframe+1)):
        for i in range(0, len(cams), 2):
            cmds.currentTime(t)

            attrsTrans = cmds.xform(fromCam[i],q=True,ws=True,t=True)
            attrsRot = cmds.xform(fromCam[i],q=True,ws=True,ro=True)

            cmds.setKeyframe(toCam[int(i)],t=cmds.currentTime(q=True), v=attrsTrans[0], at='tx')
            cmds.setKeyframe(toCam[int(i)],t=cmds.currentTime(q=True), v=attrsTrans[1], at='ty')
            cmds.setKeyframe(toCam[int(i)],t=cmds.currentTime(q=True), v=attrsTrans[2], at='tz')
            cmds.setKeyframe(toCam[int(i)],t=cmds.currentTime(q=True), v=attrsRot[0], at='rx')
            cmds.setKeyframe(toCam[int(i)],t=cmds.currentTime(q=True), v=attrsRot[1], at='ry')
            cmds.setKeyframe(toCam[int(i)],t=cmds.currentTime(q=True), v=attrsRot[2], at='rz')

            # cmds.camera(cam, e=True, aspectRatio=cmds.getAttr('defaultResolution.deviceAspectRatio'))
            # cmds.camera(cam, e=True, filmFit=cmds.getAttr('{}.filmFit'.format(fromCam[i])))
            cmds.setAttr("{}.filmFit".format(toCam[i]), cmds.getAttr('{}.filmFit'.format(fromCam[1])))

            if int(CameraScale) !=-1:
                cmds.setKeyframe(toCam[i+1],t=cmds.currentTime(q=True), v=float(CameraScale), at='.cs')
            else:
                camScale = cmds.getAttr(fromCam[i+1]+'.cameraScale')
                cmds.setKeyframe(toCam[i+1],t=cmds.currentTime(q=True), v=camScale, at='.cs')

            for thisAttr in shapeAttrs:
                cmds.setKeyframe(toCam[i+1],t=cmds.currentTime(q=True), v=cmds.getAttr(fromCam[i+1]+'.'+thisAttr), at='.'+thisAttr)
                # anim = cmds.listConnections(fromCam[i+1]+'.'+thisAttr)
                # if anim is not None and len(anim) > 0:

    for i in range(0, len(cams), 2):
        cmds.setAttr(toCam[1]+'.'+thisAttr, cmds.getAttr(fromCam[1]+'.'+thisAttr))

    for i in range(0, len(cams), 2):

        for thisAttr in shapeAttrs:
            try:
                cmds.setAttr(fromCam[i]+'.'+thisAttr, lock=False)
            except:
                pass

        cmds.setAttr(toCam[i+1]+'.renderable', True)
        cmds.setAttr(toCam[i+1]+'.renderable', lock=False)

        cmds.setAttr(toCam[i]+'.rotateAxisX', cmds.getAttr(fromCam[i]+'.rotateAxisX'))
        cmds.setAttr(toCam[i]+'.rotateAxisY', cmds.getAttr(fromCam[i]+'.rotateAxisY'))
        cmds.setAttr(toCam[i]+'.rotateAxisZ', cmds.getAttr(fromCam[i]+'.rotateAxisZ'))
        cmds.setAttr(toCam[i]+'.ro', cmds.getAttr(fromCam[i]+'.ro'))

        for thisAttr in shapeAttrs:
            cmds.setAttr(toCam[i+1]+'.'+thisAttr,lock=True)

        # if CameraScale != -1:
        cmds.setAttr(toCam[i+1]+'.cs',lock=True)

        cmds.setAttr(toCam[i]+'.translate',lock=True)
        cmds.setAttr(toCam[i]+'.rotate',lock=True)
        cmds.setAttr(toCam[i]+'.scale',lock=True)
        cmds.setAttr(toCam[i]+'.ro',lock=True)

        bakeCams.append(toCam[i])
        bakeCams.append(toCam[i+1])
        bakeCams.append(cams[int(i)])

        mel.eval('setAttr '+toCam[i+1]+'.bestFitClippingPlanes true')
    Euler_filter(toCam[0:len(toCam):2])

    return bakeCams
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
    import sys
    sys.path.append("Y:\\tool\\ND_Tools\\DCC\\ND_AssetExporter\\pycode")
    import ndPyLibExportCam;reload(ndPyLibExportCam)
    outputpath = "C:/Users/k_ueda/Desktop/work/test1.ma"
    cameraScale = -1
    frameHundle = 5
    frameRange = None
    ndPyLibExportCam.ndPyLibExportCam3(outputpath, cameraScale, frameHundle, frameRange)
