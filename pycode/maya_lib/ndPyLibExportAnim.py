# coding:utf-8
from __future__ import print_function
import maya.cmds as cmds
import ndPyLibAnimIOExportContain
import os
import sys
import re
import glob
sys.path.append(r"Y:\users\env\maya\scripts\Python\site-packages")
sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter_test\pycode")
sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter_test\pycode\maya")
sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter_test\pycode\maya_lib")

try:
    from importlib import reload
except:
    pass
reload(ndPyLibAnimIOExportContain)


def eulerfilter(attr_list):
    for attr in attr_list:
        anim_cv = map(lambda x: x.rstrip('.output'), attr)
        try:
            anim_cv = filter(lambda x: cmds.nodeType(x) in [
                             'animCurveTL', 'animCurveTU', 'animCurveTA', 'animCurveTT'], anim_cv)
            cmds.filterCurve(anim_cv, f='euler')
        except:
            continue


def get_reference_file(obj):
    return cmds.referenceQuery(obj, f=True)


def reference_ma(ma, ns):
    # cmds.file(ma, reference=True, ns=ns, force=False, pmt=True)
    cmds.file(ma, i=True, ns=ns, force=True)


def get_scene_ns_list():
    namespaces = cmds.namespaceInfo(lon=True)
    _nestedNS = []
    for ns in namespaces:
        try:
            nestedNS = cmds.namespaceInfo(ns, lon=True)
            if nestedNS != None:
                _nestedNS += nestedNS
        except:
            continue
    namespaces += _nestedNS
    try:
        namespaces.remove('UI')
        namespaces.remove('shared')
    except:
        pass
    return namespaces


def get_tg_ns_list(scene_ns_list, input_ns_list):
    tg_ns_list = []
    for scene_ns in scene_ns_list:
        for input_ns in input_ns_list:
            match = re.match(input_ns+'$', scene_ns)
            print(input_ns, scene_ns, match)
            if match != None:
                tg_ns_list.append(scene_ns)
    return tg_ns_list


def get_rec_sets(set):
    set_items = cmds.sets(set, q=True)
    result = []
    for set_item in set_items:
        if cmds.objectType(set_item) == 'objectSet':
            result.extend(get_rec_sets(set_item))
        else:
            result.append(set_item)
    return result


def get_tg_nodes(ns_list, regex_list):
    short_nodes = []
    all_objs = cmds.ls('*:*')
    for ns in ns_list:
        nodes = []
        for regex in regex_list:
            nodes.extend([i for i in all_objs[:] if re.search(
                r"{}:{}".format(ns, regex), i) != None])
        nodes = list(set(nodes))
        for node in nodes[:]:
            if cmds.objectType(node) == 'objectSet':
                nodes.extend(get_rec_sets(node))
        for node in nodes:
            short_nodes.append(node.split('|')[-1])
    return short_nodes


def getConstraintAttributes(nodes):
    attrs = []
    for n in nodes:
        const = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='constraint')
        if const is None:
            continue
        for i in range(0, len(const), 2):
            attrs.append(const[i])
    return attrs


def getPairBlendAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='pairBlend')
        if pairblend is None:
            continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
            const = cmds.listConnections(
                pairblend, s=True, d=False, p=False, c=True, t='constraint')
            if const is None:
                continue
            for i in range(0, len(const), 2):
                attrs.append(const[i])
    return attrs


def getMotionPathAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='motionPath')
        if pairblend is None:
            continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs


def getAddDoubleLinearAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='addDoubleLinear')
        if pairblend is None:
            continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs


def getTransformConnectionAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='transform')
        if pairblend is None:
            continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs


def getAnimLayerConnectionAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='animLayer')
        if pairblend is None:
            continue
        for i in range(0, len(pairblend), 2):
            attrs.append(pairblend[i])
    return attrs


def getAnimCurveAttributes(nodes):
    attrs = []
    for n in nodes:
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='animCurveTL')
        if pairblend is not None:
            for i in range(0, len(pairblend), 2):
                attrs.append(pairblend[i])
                continue
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='animCurveTU')
        if pairblend is not None:
            for i in range(0, len(pairblend), 2):
                attrs.append(pairblend[i])
                continue
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='animCurveTA')
        if pairblend is not None:
            for i in range(0, len(pairblend), 2):
                attrs.append(pairblend[i])
                continue
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=True, t='animCurveTT')
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
        if gAttrs is None:
            continue
        for attr in gAttrs:
            if '.' not in attr:
                if cmds.listConnections(n+'.'+attr, s=True, d=False) is None:
                    attrs.append(n+'.'+attr)
    return attrs


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


def getNodehasPairBlends(nodes):
    result_nodes = []
    for n in nodes:
        pairblend = cmds.listConnections(
            n, s=True, d=False, p=False, c=False, t='pairBlend')
        if pairblend is not None:
            result_nodes.append(n)
    return result_nodes


def getPairBlend(node):
    pairblends = cmds.listConnections(
        node, s=True, d=False, p=False, c=False, t='pairBlend')
    if pairblends is not None:
        for pairblend in pairblends:
            if "pairBlend" in pairblend:
                return pairblend
    return pairblend


def replacePairBlendstoLocator(nodes, sframe, eframe):
    for node in nodes:
        if "Constraint" in node:
            continue
        blend_attrs = ["outTranslateX", "outTranslateY",
                       "outTranslateZ", "outRotateX", "outRotateY", "outRotateZ"]
        nml_attrs = ["translateX", "translateY",
                     "translateZ", "rotateX", "rotateY", "rotateZ"]
        blend = getPairBlend(node)
        loc = cmds.spaceLocator(n="tmp")[0]
        for blend_attr, attr in zip(blend_attrs, nml_attrs):
            cmds.connectAttr("{}.{}".format(blend, blend_attr),
                             "{}.{}".format(loc, attr))
        cmds.bakeResults(loc, t=(sframe, eframe))
        cmds.delete(blend)
        connect_nodes = cmds.listConnections(node, p=True, s=True)
        for connect_node in connect_nodes:
            if connect_node.split(".")[-1] == "output":
                try:
                    cmds.delete(connect_node.split(".")[0])
                except:
                    pass
        for attr in nml_attrs:
            cmds.connectAttr("{}.{}".format(loc, attr),
                             "{}.{}".format(node, attr))
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


def export_anim_main(**kwargs):
    import pprint
    pprint.pprint(kwargs)

    #  cacheをハイドしてみる
    top_nodes = cmds.ls(assemblies=True)
    cache_nodes = cmds.ls(type='cacheFile')
    hidden_objs = []
    hidden_objs.extend(cmds.hide(top_nodes, rh=True))
    hidden_objs.extend(cmds.hide(cache_nodes, rh=True))
    ignore_attrs = []
    if hidden_objs is not None:
        for obj in hidden_objs:
            ignore_attrs.append('{}Shape.visibility'.format(obj.lstrip('|')))
            ignore_attrs.append('{}.visibility'.format(obj.lstrip('|')))

    output_files = []
    all_nodes = []
    node_and_attrs = []

    frame_handle = kwargs['frame_handle']
    publish_ver_anim_path = kwargs['publish_ver_anim_path']

    sframe = cmds.playbackOptions(q=True, min=True) - float(frame_handle)
    eframe = cmds.playbackOptions(q=True, max=True) + float(frame_handle)

    if 'frame_range' in kwargs.keys():
        frame_range = kwargs['frame_range']
    else:
        frame_range = [sframe, eframe]
    if 'on_maya' in kwargs.keys():
        frame_range = [sframe, sframe+1]

    with open(os.path.dirname(os.path.dirname(os.path.dirname(publish_ver_anim_path))) + '/sceneConf.txt', 'w') as f:
        f.write(str(sframe)+'\n')
        f.write(str(eframe)+'\n')
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(publish_ver_anim_path))), "resolutionConf.txt"), "w") as f:
        f.write(str(cmds.getAttr("defaultResolution.width"))+"\n")
        f.write(str(cmds.getAttr("defaultResolution.height"))+"\n")

    input_ns_list = kwargs['namespace'][0].replace(
        ' ', '').rstrip(',').split(',')
    regex_list = [i for i in kwargs['export_item']['anim'].replace(
        ' ', '').split(',') if not '.' in i]  # 通常のエクスポート対象
    regex_attr_list = [i for i in kwargs['export_item']
                       ['anim'].split(',') if '.' in i]  # アトリビュートを直接指定

    scene_ns_list = get_scene_ns_list()
    tg_ns_list = get_tg_ns_list(scene_ns_list, input_ns_list)

    all_nodes += get_tg_nodes(tg_ns_list, regex_list)

    all_nodes = list(set(all_nodes))

    character_set = cmds.ls(type='character')
    if len(character_set) != 0:
        cmds.delete(character_set)

    for node in all_nodes:
        try:
            cmds.select(node, add=True)
        except Exception as e:
            print(e)
    baseAnimationLayer = cmds.animLayer(q=True, r=True)
    if baseAnimationLayer != None and len(cmds.ls(sl=True)) != 0:
        animLayers = cmds.ls(type='animLayer')
        for al in animLayers:
            cmds.animLayer(al, e=True, sel=False)
        cmds.animLayer(baseAnimationLayer, e=True, sel=True)
        cmds.bakeResults(t=(sframe, eframe), sb=True,
                         ral=True, dic=True, pok=True, sm=True)

    attrs = getNoKeyAttributes(all_nodes)
    if len(node_and_attrs) != 0:
        attrs.extend(getNoKeyAttributes(node_and_attrs))
    for tg_ns in tg_ns_list:
        for regex_obj_and_attr in regex_attr_list:
            obj_and_attr = tg_ns+':' + regex_obj_and_attr
            if cmds.objExists(obj_and_attr):
                attrs.append(obj_and_attr)

    if len(attrs) != 0:
        attrs = list(set(attrs)-set(ignore_attrs))
        print('#############')
        for attr in attrs:
            print(attr)
        cmds.setKeyframe(attrs, t=sframe, insertBlend=True)
        print('#############')

    attrs += getConstraintAttributes(all_nodes)
    attrs += getMotionPathAttributes(all_nodes)
    attrs += getAddDoubleLinearAttributes(all_nodes)
    attrs += getTransformConnectionAttributes(all_nodes)

    attrs += getKeyAttributes(all_nodes)
    attrs += getAnimLayerConnectionAttributes(all_nodes)
    # attrs += getPairBlendAttributes(all_nodes)
    attrs = list(set(attrs)-set(ignore_attrs))
    unlockAttributes(attrs)
    unmuteAttributes(attrs)

    '''
        関連するアトリビュートの追加
    '''
    for node in all_nodes:
        if cmds.listConnections(node, s=True, type="constraint") is not None:
            attrs.extend(
                list(set(cmds.listConnections(node, s=True, type="constraint"))))

    if kwargs['scene_timewarp'] == True:
        time_value_set_list = []
        ref_files = []
        ref_attrs = []
        for scene_ns in scene_ns_list:
            top_obj = '{}:root'.format(scene_ns)
            if not cmds.objExists(top_obj):
                continue
            if cmds.referenceQuery(top_obj, inr=True):
                ref_file = get_reference_file(top_obj)
                try:
                    reference_ma(ref_file, "tmp_"+scene_ns)
                    ref_files.append([scene_ns, ref_file])

                    for obj in cmds.listRelatives(top_obj, ad=True):
                        try:
                            if cmds.listAttr(obj, keyable=True) != None:
                                for attr in cmds.listAttr(obj, keyable=True):
                                    ref_attrs.append(obj+"."+attr)
                        except Exception as e:
                            print(e)

                except Exception as e:
                    print(e)
                # continue
        cmds.setAttr("time1.enableTimewarp", 0)
        # store timewarp
        for t in range(int(sframe), int(eframe+1)):
            cmds.currentTime(t)
            warp_time = cmds.getAttr("time1.outTime", time=t)
            for attr in ref_attrs:
                obj = attr.split(".")[0]
                try:
                    if attr in attrs:
                        value = cmds.getAttr(attr, time=warp_time)
                        time_value_set_list.append([t, attr, value])
                except Exception as e:
                    print(attr)
                    print(e)
        for ref in ref_files:
            ns = ref[0]
            ref_file = ref[1]
            # cmds.file(ref_file.replace('/', '\\'), rr=True)
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
    else:
        attrs = list(set(attrs)-set(ignore_attrs))
        for obj_and_attr in attrs:
            if cmds.objExists(obj_and_attr) == True:
                cmds.select(obj_and_attr, add=True)
        # cmds.select(attrs, add=True)
        print(sframe, eframe)
        cmds.bakeResults(at=attrs, t=(sframe, eframe), dic=True)
        eulerfilter(attrs)
    cmds.showHidden(hidden_objs)
    if 'on_maya' in kwargs.keys():
        return

    for ns in tg_ns_list:
        pick_nodes = []
        pick_node_and_attrs = []
        for node in all_nodes:
            if ns+':' in node:
                pick_nodes.append(node)
        for node in pick_node_and_attrs:
            if ns + ':' in node:
                pick_node_and_attrs.append(node)
        if len(pick_nodes) != 0 or len(pick_node_and_attrs) != 0:
            argsdic = {}
            argsdic['is_filter'] = True
            argsdic['inPfxInfo'] = ['3', '']
            argsdic['anim_file_name'] = 'anim_'+ns+'.ma'
            argsdic['publish_ver_anim_path'] = kwargs['publish_ver_anim_path']
            argsdic['pick_nodes'] = pick_nodes
            argsdic['pick_node_and_attrs'] = pick_node_and_attrs
            argsdic['frame_range'] = frame_range
            argsdic['scene_timewarp'] = kwargs['scene_timewarp']
            argsdic['is_check_constraint'] = True
            argsdic['is_check_anim_curve'] = True
            ndPyLibAnimIOExportContain.ndPyLibAnimIOExportContain_main(
                **argsdic)
    return output_files


def ndPyLibExportAnim_caller(args):
    export_anim_main(**args)
    import pprint
    pprint.pprint(args)
    print("ndPylibExportAnim End")


if __name__ == '__main__':
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter_test\pycode\maya")
    import ndPyLibExportAnim
    reload(ndPyLibExportAnim)
    # argsdic = {'input_path': 'P:/Project/RAM1/shots/ep022/s2227/c008/work/k_ueda/s2227c008_anm_v006.ma', 'sequence': 's2227', 'export_type': 'anim', 'abc_check': False, 'step_value': False, 'abc_item': 'abc_Root', 'shot': 'c008', 'group': '', 'anim_item': 'ctrl_set, root', 'namespace': 'NursedesseiDragon[0-9]*$', 'priority': '50', 'top_node': 'root', 'asset_path': 'P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiDragon/publish/Setup/RH/maya/current/NursedesseiDragon_Rig_RH.mb', 'export_item': {'anim': 'ctrl_set, root', 'abc': 'abc_Root'}, 'asset_name': 'NursedesseiDragon', 'frame_range': False, 'publish_ver_anim_path': 'P:/Project/RAM1/shots/ep022/s2227/c008/publish/test_charSet/NursedesseiDragon/v104/anim', 'pool': '', 'frame_handle': False, 'cam_scale': False, 'project': 'RAM1', 'debug': True, 'scene_timewarp': False}
    # ndPyLibExportAnim.ndPyLibExportAnim_caller(argsdic)

    argsdic = {'namespace': ['PR2022_BG_LO'],
               'anim_item': 'ctrl_set, root',
               'export_item': {'abc': 'abc_Root', 'anim': 'animSets, treeSet'},
               'frame_handle': False,
               'frame_range': False,
               'publish_ver_anim_path': 'C:/Users/k_ueda/Desktop/temp/v001/anim',
               'scene_timewarp': False,
               'step_value': False,
               'on_maya': True}
    # ndPyLibExportAnim.ndPyLibExportAnim_caller(argsdic)
