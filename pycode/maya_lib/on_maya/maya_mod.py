import maya.cmds as cmds

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

def getKeyAttributes(nodes):
    attrs = []
    for n in nodes:
        if '.' in n:
            n = n.split('.')[0]
        gAttrs = cmds.listAttr(n, keyable=True)
        if gAttrs is None:
            continue
        for attr in gAttrs:
            if '.' not in attr:
                if cmds.listConnections(n+'.'+attr, s=True, d=False) is None:
                    pass
                else:
                    attrs.append(n+'.'+attr)
    return attrs

 
def bake_timewarp(objects):
    time_value_set_list = []
    cmds.setAttr("time1.enableTimewarp", 0)
    sframe = cmds.playbackOptions(q=True, min=True)
    eframe = cmds.playbackOptions(q=True, max=True)
    # store timewarp
    key_attrs = []
    for _obj in cmds.ls(ass=True):
        _attrs = getKeyAttributes(_obj)
        if _attrs is not None:
            key_attrs.extend(_attrs)
    for t in range(int(sframe), int(eframe+1)):
        cmds.currentTime(t)
        warp_time = cmds.getAttr("time1.outTime", time=t)
        for attr in key_attrs:
            value = cmds.getAttr(attr, time=warp_time)
            time_value_set_list.append([t, attr, value])
    for ref in ref_files:
        ns = ref[0]
        ref_file = ref[1]
        try:
            cmds.file(ref_file, rr=True)
        except:
            pass
    for ns_obj in cmds.ls("tmp_*:*"):
        try:
            cmds.rename(ns_obj, ns_obj.replace("tmp_", ":"))
        except:
            pass
    # restore timewarp
    cmds.setAttr("time1.enableTimewarp", 0)
    current_f = 0
    for time_list in time_value_set_list:
        frame = time_list[0]
        attr = time_list[1]
        value = time_list[2]
        if current_f != frame:
            cmds.currentTime(frame)
            current_f = frame
        try:
            cmds.setAttr(attr, value)
            cmds.setKeyframe(attr)
        except Exception as e:
            print(e)

    '''
    import sys
    sys.path.append(r'Y\tool\ND_Tools\DCC\ND_AssetExporter')
    import pycode.maya_lib.on_maya.maya_mod as maya_mod

    key_attrs = []

    for _obj in cmds.ls(ass=True):
        _attrs = getKeyAttributes()
        if _attrs is not None:
            key_attrs.extend(_attrs)

    maya_mod.bake_timewarp(key_attrs)
    '''

