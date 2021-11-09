#coding:utf-8
import maya.cmds as cmds

# testing #
objects = cmds.ls("*", type="transform")
objects.extend(cmds.ls("*:*", type="transform"))
# 指定は一つにすべし 
start = int(cmds.playbackOptions(q=1,min=1))
end = int(cmds.playbackOptions(q=1,max=1))
 
import maya.cmds as cmds

def bakeTimeWarp(objects=cmds.ls(sl=1),start=cmds.playbackOptions(q=1,min=1),end=cmds.playbackOptions(q=1,max=1),killWarp=False):
    # for each frame between start and end, query time1.outTime and time1.unwarpedTime
    # for each object, get each channel with at least one keyframe set
    # for each channel:
    #     get the value of the channel at outTime
    #     set the channel to this value at unwarpedTime and set a keyframe
    for i in objects:
        try:
            dupe = cmds.duplicate(i,po=1)[0]
            if not cmds.attributeQuery('bakeTimeWarpConnection',node=i,ex=1):
                cmds.addAttr(i,ln='bakeTimeWarpConnection',at='message')
            cmds.connectAttr(dupe+'.message',i+'.bakeTimeWarpConnection')
        except Exception as e:
            print e
    for x in range(int(start),int(end+1)):
        try:
            cmds.currentTime(x)
            outTime = cmds.getAttr('time1.outTime')
            unwarpedTime = cmds.getAttr('time1.unwarpedTime')
            for i in objects:
                # build a list of all keyed channels.
                keyables = cmds.listAttr(i,k=1)
                # keyedChans = [f for f in keyables if cmds.keyframe(i+'.'+f,q=1,n=1)]
                keyedChans = keyables
                dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
                for chan in keyedChans:
                    val = cmds.getAttr(i+'.'+chan,t=outTime)
                    cmds.setAttr(dupe+'.'+chan,val)
                    cmds.setKeyframe(dupe+'.'+chan,t=unwarpedTime)
        except Exception as e:
            print e

    # now reconnect anim curves from the duplicate to the original. then delete the duplicates and finally remove the timewarp.
    for i in objects:
        try:
            dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
            chans = [f for f in cmds.listAttr(dupe,k=1) if cmds.keyframe(dupe+'.'+f,q=1,n=1)]
            for chan in chans:
                animCurve = cmds.keyframe(dupe+'.'+chan,q=1,n=1)[0]
                oldCurve = cmds.keyframe(i+'.'+chan,q=1,n=1)
                cmds.connectAttr(animCurve+'.output',i+'.'+chan,f=1)
                cmds.delete(oldCurve)
            cmds.delete(dupe)
            cmds.deleteAttr(i+'.bakeTimeWarpConnection')
        except Exception as e:
            print e

    if killWarp:
        timeWarp = cmds.listConnections('time1.timewarpIn_Raw')[0]
        cmds.delete(timeWarp)
        
        
if __name__ == '__main__':
    bakeTimeWarp(objects=objects, start=start, end=end)
    # bakeTimeWarp(objects=["AllRoot"], start=start, end=end)
    # bakeTimeWarp(objects=["NursedesseiDragon:ctrl_allWorld"], start=start, end=end)