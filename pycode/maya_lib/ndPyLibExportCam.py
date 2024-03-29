# -*- coding: utf-8 -*-
from distutils.log import info
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


def search_cam():
    #  cacheをハイドしてみる
    cam_shapes = cmds.ls(ca=True)
    try:
        cam_shapes.remove('frontShape')
        cam_shapes.remove('perspShape')
        cam_shapes.remove('sideShape')
        cam_shapes.remove('topShape')
        cam_shapes.remove('leftShape')
        cam_shapes.remove('backShape')
        cam_shapes.remove('bottomShape')
        cam_shapes.remove('front1Shape')
        cam_shapes.remove('persp1Shape')
        cam_shapes.remove('side1Shape')
        cam_shapes.remove('top1Shape')
        cam_shapes.remove('persp2Shape')
        cam_shapes.remove('deformation_camShape')
    except ValueError:
        pass
    for camShape in cam_shapes[:]:
        if cmds.getAttr("{}.orthographic".format(camShape)):
            cam_shapes.remove(camShape)

    cams = cmds.listRelatives(cam_shapes, p=True, f=True)
    tg_cam_list = []
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
                ref_file = cmds.referenceQuery(cmds.referenceQuery(cams[i], rfn=True, tr=True), f=True)
                cmds.file(ref_file, importReference=True)
            except:
                pass
        tg_cam_list.append(cams[i])
        tg_cam_list.append(cam_shapes[i])

    return tg_cam_list


def bake_cam(sframe, eframe, cam_scale):
    cams = search_cam()
    if cams is None:
        return
    shapeAttrs = ['fl','hfa','vfa','lsr','fs','fd','sa','coi','ncp','fcp']

    bake_cams = []
    from_cam = []
    to_cam = []

    for i in range(0, len(cams), 2):
        to_cam.extend(cmds.camera())
        from_cam.append(cams[i])
        from_cam.append(cams[i+1])

    # scene time warp
    if cmds.objExists('time1') == True:
        scene_time_warp = False
    else:
        scene_time_warp = False
    cmds.setAttr("time1.enableTimewarp", True)

    if scene_time_warp == True:
        print '%%%%%%%%%%%%%%'
        for i in range(0, len(cams), 2):

            time_set_list = []
            time_value_set_list = []

            for t in range(int(sframe),int(eframe+1)):
                cmds.currentTime(t)
                warp_time = cmds.getAttr("time1.outTime", time=t)
                time_set_list.append([t, warp_time])

            for time_set in time_set_list:
                t = time_set[0]
                warp_time = time_set[1]
                cmds.currentTime(warp_time)
                try:
                    attrsTrans = cmds.xform(from_cam[i],q=True,ws=True,t=True)
                    attrsRot = cmds.xform(from_cam[i],q=True,ws=True,ro=True)
                    time_value_set_list.append([t, attrsTrans, attrsRot])
                except Exception as e:
                    print e
            # cmds.setAttr("time1.enableTimewarp", 1)

            for time_list in time_value_set_list:
                frame = time_list[0]
                attrsTrans = time_list[1]
                attrsRot = time_list[2]
                cmds.currentTime(frame)
                cmds.setKeyframe(to_cam[int(i)],t=frame, v=attrsTrans[0], at='tx')
                cmds.setKeyframe(to_cam[int(i)],t=frame, v=attrsTrans[1], at='ty')
                cmds.setKeyframe(to_cam[int(i)],t=frame, v=attrsTrans[2], at='tz')
                cmds.setKeyframe(to_cam[int(i)],t=frame, v=attrsRot[0], at='rx')
                cmds.setKeyframe(to_cam[int(i)],t=frame, v=attrsRot[1], at='ry')
                cmds.setKeyframe(to_cam[int(i)],t=frame, v=attrsRot[2], at='rz')

    else:
        for t in range(int(sframe),int(eframe+1)):
            for i in range(0, len(cams), 2):
                cmds.currentTime(t)

                attrsTrans = cmds.xform(from_cam[i],q=True,ws=True,t=True)
                attrsRot = cmds.xform(from_cam[i],q=True,ws=True,ro=True)

                cmds.setKeyframe(to_cam[int(i)],t=cmds.currentTime(q=True), v=attrsTrans[0], at='tx')
                cmds.setKeyframe(to_cam[int(i)],t=cmds.currentTime(q=True), v=attrsTrans[1], at='ty')
                cmds.setKeyframe(to_cam[int(i)],t=cmds.currentTime(q=True), v=attrsTrans[2], at='tz')
                cmds.setKeyframe(to_cam[int(i)],t=cmds.currentTime(q=True), v=attrsRot[0], at='rx')
                cmds.setKeyframe(to_cam[int(i)],t=cmds.currentTime(q=True), v=attrsRot[1], at='ry')
                cmds.setKeyframe(to_cam[int(i)],t=cmds.currentTime(q=True), v=attrsRot[2], at='rz')

                # cmds.camera(cam, e=True, aspectRatio=cmds.getAttr('defaultResolution.deviceAspectRatio'))
                # cmds.camera(cam, e=True, filmFit=cmds.getAttr('{}.filmFit'.format(from_cam[i])))
                cmds.setAttr("{}.filmFit".format(to_cam[i]), cmds.getAttr('{}.filmFit'.format(from_cam[1])))
    for t in range(int(sframe),int(eframe+1)):
        for i in range(0, len(cams), 2):
            cmds.currentTime(t)
            if int(cam_scale) !=0:
                cmds.setKeyframe(to_cam[i+1],t=cmds.currentTime(q=True), v=float(cam_scale), at='.cs')
            else:
                camScale = cmds.getAttr(from_cam[i]+'.cameraScale')
                cmds.setKeyframe(to_cam[i+1],t=cmds.currentTime(q=True), v=camScale, at='.cs')

            for thisAttr in shapeAttrs:
                print from_cam[i], to_cam[i], cmds.getAttr(from_cam[i]+'.'+thisAttr)
                cmds.setKeyframe(to_cam[i],t=cmds.currentTime(q=True), v=cmds.getAttr(from_cam[i]+'.'+thisAttr), at='.'+thisAttr)
            # anim = cmds.listConnections(from_cam[i+1]+'.'+thisAttr)
            # if anim is not None and len(anim) > 0:

    for i in range(0, len(cams), 2):
        cmds.setAttr(to_cam[i]+'.'+thisAttr, cmds.getAttr(from_cam[i]+'.'+thisAttr))

    for i in range(0, len(cams), 2):

        cmds.setAttr(from_cam[i]+'.'+thisAttr, lock=False)

        cmds.setAttr(to_cam[i+1]+'.renderable', True)
        cmds.setAttr(to_cam[i+1]+'.renderable', lock=False)

        cmds.setAttr(to_cam[i]+'.rotateAxisX', cmds.getAttr(from_cam[i]+'.rotateAxisX'))
        cmds.setAttr(to_cam[i]+'.rotateAxisY', cmds.getAttr(from_cam[i]+'.rotateAxisY'))
        cmds.setAttr(to_cam[i]+'.rotateAxisZ', cmds.getAttr(from_cam[i]+'.rotateAxisZ'))
        cmds.setAttr(to_cam[i]+'.ro', cmds.getAttr(from_cam[i]+'.ro'))

        for thisAttr in shapeAttrs:
            cmds.setAttr(to_cam[i+1]+'.'+thisAttr,lock=True)

        # if cam_scale != -1:
        cmds.setAttr(to_cam[i+1]+'.cs',lock=True)

        cmds.setAttr(to_cam[i]+'.translate',lock=True)
        cmds.setAttr(to_cam[i]+'.rotate',lock=True)
        cmds.setAttr(to_cam[i]+'.scale',lock=True)
        cmds.setAttr(to_cam[i]+'.ro',lock=True)

        bake_cams.append(to_cam[i])
        bake_cams.append(from_cam[i])

        mel.eval('setAttr '+to_cam[i+1]+'.bestFitClippingPlanes true')
    Euler_filter(to_cam[0:len(to_cam):2])

    return bake_cams
#end of ndPylibExportCam_bakeCamera


def ndPyLibPlatform(text):
    prefix = 'nd'
    otsr = ''
    otsr = otsr+'['+prefix+']'+text+'\n'

    print(otsr)


def export_manual(info_dic):
    info_dic['ma_cam_path'] = '{}/{}.ma'.format(
        info_dic['outputdir'], info_dic['file_name'])
    # argsdic['anim_cam_path']= '{}/anim/{}_anim.ma'.format(opc.publish_ver_cam_path, oFilename)
    # フルパスとファイル名
    info_dic['abc_cam_path'] = '{}/{}.abc'.format(
        info_dic['outputdir'], info_dic['file_name'])
    # フルパスとファイル名
    info_dic['fbx_cam_path'] = '{}/{}.fbx'.format(
        info_dic['outputdir'], info_dic['file_name'])
    # export_cam_main(
    #     'ma_cam_path' = info_dic['ma_cam_path'],
    #     'abc_cam_path' = info_dic['abc_cam_path'],
    #     'fbx_cam_path' = info_dic['fbx_cam_path'],
    #     'cam_scale' = info_dic['cam_scale'],
    #     'frame_handle' = info_dic['frame_handle'],
    #     'frame_range' = info_dic['frame_range']
    # )
    export_cam_main(info_dic)

def export_cam_main(kwargs):
    top_nodes = cmds.ls(assemblies=True)
    cache_nodes = cmds.ls(type='cacheFile')
    hidden_objs = []
    # hidden_objs.extend(cmds.hide(top_nodes, rh=True))
    # hidden_objs.extend(cmds.hide(cache_nodes, rh=True))
    ignore_attrs = []
    if hidden_objs is not None:
        for obj in hidden_objs:
            ignore_attrs.append('{}Shape.visibility'.format(obj.lstrip('|')))
            ignore_attrs.append('{}.visibility'.format(obj.lstrip('|')))

    if kwargs['frame_range'] != False and kwargs['frame_range']!=None:
        sframe = float(kwargs['frame_range'].split(',')[0])
        eframe = float(kwargs['frame_range'].split(',')[1])
    else:
        sframe = cmds.playbackOptions(q=True, min=True)
        eframe = cmds.playbackOptions(q=True, max=True)

    sframe -= float(kwargs['frame_handle'])
    eframe += float(kwargs['frame_handle'])

    cams = bake_cam(sframe, eframe, kwargs['cam_scale'])
    if cams is None:
        return

    if cmds.objExists('cam_grp'):
        cmds.delete('cam_grp')

    cmds.group(em=True, n='cam_grp')
    for i in range(0, len(cams), 2):
        cmds.parent(cams[i],'cam_grp')
        cmds.rename(cams[i],cams[i+1].split("|")[-1])

    cmds.select('cam_grp')

    try:
        publish_ver_path = kwargs['publish_ver_path']
        if not os.path.exists(publish_ver_path):
            os.makedirs(publish_ver_path)
        sceneConfpath = os.path.join(publish_ver_path, '..', 'sceneConf.txt')
        with open(sceneConfpath, 'w') as f:
            f.write(str(sframe)+'\n')
            f.write(str(eframe)+'\n')
    except:
        pass

    cmds.file(kwargs['ma_cam_path'], force=True, options='v=0', typ='mayaAscii', pr=True, es=True)

    if cmds.pluginInfo('fbxmaya', q=True, l=True) == 0:
        cmds.loadPlugin('fbxmaya')
    cmds.file(kwargs['fbx_cam_path'], force=True, options='v=0', typ='FBX export', pr=True, es=True)

    if cmds.pluginInfo('AbcExport', q=True, l=True) == 0:
        cmds.loadPlugin('AbcExport')
    strAbc = ''
    strAbc = strAbc+'-frameRange '+str(sframe)+' '+str(eframe)+' '
    strAbc = strAbc+'-uvWrite '
    strAbc = strAbc+'-worldSpace '
    strAbc = strAbc+'-eulerFilter '
    strAbc = strAbc+'-dataFormat ogawa '
    strAbc = strAbc+ '-root cam_grp '
    strAbc = strAbc+ '-file '+ kwargs['abc_cam_path'] #abc
    print ('AbcExport -j ' + strAbc)
    mel.eval('AbcExport -verbose -j ' + '"' + strAbc + '"')
    cmds.file(kwargs['ma_cam_path'], force=True, options='v=0', typ='mayaAscii', pr=True, es=True)
    # cmds.showHidden(hidden_objs)


def ndPylibExportCam_caller(**kwargs):
    export_cam_main(kwargs)