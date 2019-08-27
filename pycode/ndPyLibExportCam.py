# -*- coding: utf-8 -*-

import os
import re

import maya.cmds as cmds
import maya.mel as mel

import sys
import subprocess


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
    except ValueError:
        pass

    cams = cmds.listRelatives(camShapes, p=True)

    camAll = []

    for i in range(len(cams)):
        if cmds.referenceQuery(cams[i], inr=True):
            refFile = cmds.referenceQuery(cmds.referenceQuery(cams[i], rfn=True), f=True)
            cmds.file(refFile, importReference=True)
        camAll.append(cams[i])
        camAll.append(camShapes[i])

    return camAll

def ndPyLibExportCam_bakeCamera(frameHandle, CameraScale):

    sframe = cmds.playbackOptions(q=True, min=True) - frameHandle
    eframe = cmds.playbackOptions(q=True, max=True) + frameHandle

    ###
    sframe -= 10
    eframe += 10

    cams = ndPyLibExportCam_searchCamera()
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

            if CameraScale != -1:
                cmds.setKeyframe(toCam[i+1],t=cmds.currentTime(q=True), v=CameraScale, at='.cs')
            else:
                camScale = cmds.getAttr(fromCam[i+1]+'.cameraScale')
                cmds.setKeyframe(toCam[i+1],t=cmds.currentTime(q=True), v=camScale, at='.cs')

            for thisAttr in shapeAttrs:
                cmds.setKeyframe(toCam[i+1],t=cmds.currentTime(q=True), v=cmds.getAttr(fromCam[i+1]+'.'+thisAttr), at='.'+thisAttr)
                # anim = cmds.listConnections(fromCam[i+1]+'.'+thisAttr)
                # if anim is not None and len(anim) > 0:

    Euler_filter(toCam[0:len(toCam):2])

    for i in range(0, len(cams), 2):
        cmds.setAttr(toCam[1]+'.'+thisAttr, cmds.getAttr(fromCam[1]+'.'+thisAttr))

    for i in range(0, len(cams), 2):

        for thisAttr in shapeAttrs:
            cmds.setAttr(fromCam[i]+'.'+thisAttr, lock=False)

        cmds.setAttr(toCam[i+1]+'.renderable', True)
        cmds.setAttr(toCam[i+1]+'.renderable', lock=True)

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

    return bakeCams
#end of ndPylibExportCam_bakeCamera

def ndPyLibPlatform(text):

    prefix = 'nd'

    otsr = ''
    otsr = otsr+'['+prefix+']'+text+'\n'

    print(otsr)
#end of ndPyLibPlatform

def ndPyLibExportCam_exportCamera(publishpath, oFilename, isImagePlane, isFbx, isABC, frameHandle, CameraScale=-1):

    outputfiles = []
    sframe = cmds.playbackOptions(q=True, min=True)-frameHandle
    eframe = cmds.playbackOptions(q=True, max=True)+frameHandle

    ###
    sframe_org = sframe
    eframe_org = eframe
    sframe -= 10
    eframe += 10

    if isImagePlane!=1:
        if len(cmds.ls(type='imagePlane'))!=0:
            cmds.delete(cmds.ls(type='imagePlane'))
            cmds.warning('delete imagePlanes...')

    #end of delete imageplane

    cams = ndPyLibExportCam_bakeCamera(frameHandle, CameraScale)

    if cmds.objExists('cam_grp'):
        cmds.delete('cam_grp')

    grp = cmds.group(em=True, n='cam_grp')
    toCam = []
    if(len(cams)==3):#カメラが一つの場合
        toCam.append(cams[0])
        cmds.parent(toCam[0],'cam_grp')
        cmds.rename(toCam[0],'rend_cam')
    else :#カメラが複数の場合
        for i in range(0, len(cams), 3):

            toCam.append(cams[i])
            toCam.append(cams[i+1])
            toCam.append(cams[i+2])

            cmds.parent(toCam[i],'cam_grp')
            cmds.rename(toCam[i],toCam[i+2]+'_rend_cam')

    cmds.select('cam_grp')

    if not os.path.exists(publishpath):
        os.mkdir(publishpath)

    cmds.file(os.path.join(publishpath, oFilename+'.ma').replace('\\', '/'), force=True, options='v=0', typ='mayaAscii', pr=True, es=True)

    with open(os.path.join(publishpath, '..', 'sceneConf.txt').replace('\\', '/'), 'w') as f:
        f.write(str(sframe_org)+'\n')
        f.write(str(eframe_org)+'\n')

    if isFbx == 1:
        if cmds.pluginInfo('fbxmaya', q=True, l=True) == 0:
            cmds.loadPlugin('fbxmaya')

        outputfiles.append(cmds.file(os.path.join(publishpath, oFilename+'.fbx').replace('\\', '/'), force=True, options='v=0', typ='FBX export', pr=True, es=True))

    if isABC == 1:
        if cmds.pluginInfo('AbcExport', q=True, l=True) == 0:
            cmds.loadPlugin('AbcExport')


        strAbc = ''
        strAbc = strAbc+'-frameRange '+str(sframe)+' '+str(eframe)+' '
        strAbc = strAbc+'-uvWrite '
        strAbc = strAbc+'-worldSpace '
        strAbc = strAbc+'-eulerFilter '
        strAbc = strAbc+'-dataFormat ogawa '
        strAbc = strAbc+ '-root cam_grp '
        strAbc = strAbc+ '-file '+ os.path.join(publishpath, oFilename+'.abc').replace('\\', '/')

        print ('AbcExport -j ' + strAbc)
        mel.eval('AbcExport -verbose -j ' + '"' + strAbc + '"')

        outputfiles.append(os.path.join(publishpath, oFilename + '.abc').replace('\\', '/'))

    outputfiles.append(cmds.file(os.path.join(publishpath, oFilename + '.ma').replace('\\', '/'), force=True, options='v=0', typ='mayaAscii', pr=True, es=True))

    return outputfiles

    #end of ndPythonLibExportCam_exportCamera

def ndPyLibExportCam(isImagePlane, isFbx, isAbc, frameHandle, CameraScale):
    if cmds.file(q=True, modified=True) == 1:
        ndPyLibPlatform('please save scene file...')
    else:
        filepath = cmds.file(q=True, sceneName=True)
        filename = os.basename(filepath)

        project = cmds.match('P:/Project/[a-zA-Z0-9]+/', filepath)
        roll = cmds.match('/roll[a-zA-Z0-9]+/', filepath)
        roll = cmds.match('roll[a-zA-Z0-9]+', roll)
        sequence = cmds.match('/s[0-9]+[a-zA-Z]*/', filepath)
        sequence = cmds.match('s[0-9]+[a-zA-Z]*/', filepath)
        shot = cmds.match('/c[0-9]+[a-zA-Z_]*/', filepath)
        shot = cmds.match('c[0-9]+[a-zA-Z_]*/', shot)

        shotpath = os.path.join(project, 'shots', roll, sequence, shot)
        publishpath = os.path.join(shotpath,'publish','Cam',filename)

        oFilename = os.path.join(sequence, shot, '_cam')

        ndPyLibPlatform('project : ' +project)
        ndPyLibPlatform('roll : ' +roll)
        ndPyLibPlatform('sequence : ' +sequence)
        ndPyLibPlatform('shot : ' +shot)
        ndPyLibPlatform('filename : '+filename)

        if os.exists(shotpath) != 1:
            ndPyLibPlatform('no exist folder...')
        else:
            if not os.exists(publishpath):
                os.mkdir(publishpath, md=True)

            outputfiles = ndPyLibExportCam_exportCamera(publishpath, oFilename, isImagePlane, isFbx, isAbc, frameHandle, CameraScale)

            for o in outputfiles:
                ndPyLibPlatform('output file : '+o)

            for o in outputfiles:
                destFile = os.path.dirname( os.path.dirname(o) )+'/'+os.path.basename(o, '')
                cmds.sysFile(o, copy=destFile)
#end of ndPyLibExportCam


def ndPyLibExportCam2 (publishPath, oFilename, CameraScale):
    FrameHandle = 0
    ndPyLibExportCam_exportCamera(publishPath, oFilename, 1, 1, 1, FrameHandle, CameraScale)