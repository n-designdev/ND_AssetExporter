#coding-utf8
import maya.cmds as cmds

def getKeyAttributes(nodes):
    attrs = []
    for n in nodes:
        # print n, nodes
        if '.' in n:
            n = n.split('.')[0]
        gAttrs = cmds.listAttr(n, keyable=True)
        if gAttrs is None:
            continue
        for _attr in gAttrs:
            if '.' not in _attr:
                if cmds.listConnections(n+'.'+_attr, s=True, d=False) is None:
                    pass
                else:
                    attrs.append(_attr)
    return attrs

# def bakeTimeWarp(objects,start,end,killWarp=True):
#     # for each frame between start and end, query time1.outTime and time1.unwarpedTime
#     # for each object, get each channel with at least one keyframe set
#     # for each channel:
#     #     get the value of the channel at outTime
#     #     set the channel to this value at unwarpedTime and set a keyframe
#     for i in objects:
#         dupe = cmds.duplicate(i,po=1)[0]
#         if not cmds.attributeQuery('bakeTimeWarpConnection',node=i,ex=1):
#             cmds.addAttr(i,ln='bakeTimeWarpConnection',at='message')
#         cmds.connectAttr(dupe+'.message',i+'.bakeTimeWarpConnection')
#     for x in range(start,end+1):
#         cmds.currentTime(x)
#         outTime = cmds.getAttr('time1.outTime')
#         unwarpedTime = cmds.getAttr('time1.unwarpedTime')
#         for i in objects:
#             # build a list of all keyed channels.
#             keyables = getKeyAttributes([i])
#             # keyedChans = [f for f in keyables if cmds.keyframe(i+'.'+f,q=1,n=1)]
#             dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
#             for chan in keyables:
#                 try:
#                     val = cmds.getAttr(i+'.'+chan,t=outTime)
#                     cmds.setAttr(dupe+'.'+chan,val)
#                     cmds.setKeyframe(dupe+'.'+chan,t=unwarpedTime)
#                 except Exception as e:
#                     pass
#     # now reconnect anim curves from the duplicate to the original. then delete the duplicates and finally remove the timewarp.
#     for i in objects:
#         dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
#         chans = [f for f in cmds.listAttr(dupe,k=1) if cmds.keyframe(dupe+'.'+f,q=1,n=1)]
#         for chan in chans:
#             animCurve = cmds.keyframe(dupe+'.'+chan,q=1,n=1)[0]
#             oldCurve = cmds.keyframe(i+'.'+chan,q=1,n=1)
#             cmds.connectAttr(animCurve+'.output',i+'.'+chan,f=1)
#             cmds.delete(oldCurve)
#         cmds.delete(dupe)
#         cmds.deleteAttr(i+'.bakeTimeWarpConnection')


def bakeTimeWarp(objects,start,end,killWarp=False):
    # for each frame between start and end, query time1.outTime and time1.unwarpedTime
    # for each object, get each channel with at least one keyframe set
    # for each channel:
    #     get the value of the channel at outTime
    #     set the channel to this value at unwarpedTime and set a keyframe
    for i in objects:
        dupe = cmds.duplicate(i,po=1)[0]
        if not cmds.attributeQuery('bakeTimeWarpConnection',node=i,ex=1):
            cmds.addAttr(i,ln='bakeTimeWarpConnection',at='message')
        cmds.connectAttr(dupe+'.message',i+'.bakeTimeWarpConnection')
    for x in range(start,end+1):
        cmds.currentTime(x)
        outTime = cmds.getAttr('time1.outTime')
        unwarpedTime = cmds.getAttr('time1.unwarpedTime')
        for i in objects:
            # build a list of all keyed channels.
            keyables = cmds.listAttr(i,k=1, u=True, cb=True)
            if keyables is None:
                continue
            keyedChans = [f for f in keyables if cmds.keyframe(i+'.'+f,q=1,n=1)]
            dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
            for chan in keyedChans:
                val = cmds.getAttr(i+'.'+chan,t=outTime)
                cmds.setAttr(dupe+'.'+chan,val)
                cmds.setKeyframe(dupe+'.'+chan,t=unwarpedTime)
    # now reconnect anim curves from the duplicate to the original. then delete the duplicates and finally remove the timewarp.
    for i in objects:
        if cmds.listConnections(i+'.bakeTimeWarpConnection') is None:
            continue
        dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
        if cmds.listAttr(dupe,k=1, u=True, cb=True) is not None:
            chans = [f for f in cmds.listAttr(dupe,k=1, u=True, cb=True) if cmds.keyframe(dupe+'.'+f,q=1,n=1)]
            for chan in chans:
                animCurve = cmds.keyframe(dupe+'.'+chan,q=1,n=1)[0]
                oldCurve = cmds.keyframe(i+'.'+chan,q=1,n=1)
                cmds.connectAttr(animCurve+'.output',i+'.'+chan,f=1)
                cmds.delete(oldCurve)
        cmds.delete(dupe)
        cmds.deleteAttr(i+'.bakeTimeWarpConnection')


def bakeTimeWarp_caller():
    all_objs = cmds.ls(dag=True)
    sframe =int(cmds.playbackOptions(q=True, min=True)) 
    eframe =int(cmds.playbackOptions(q=True, max=True)) 
    bakeTimeWarp(all_objs, sframe, eframe)

if __name__ == '__main__':
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode\maya_lib\on_maya")
    import scene_timewarp_script; reload(scene_timewarp_script)
    scene_timewarp_script.bakeTimeWarp_caller()

