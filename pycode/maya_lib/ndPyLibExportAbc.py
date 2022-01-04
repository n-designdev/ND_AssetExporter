# -*- coding: utf-8 -*-

import os
import re

import maya.cmds as cmds
import maya.mel as mel


# def norefresh (func):
#     def _norefresh (*args):
#         try:
#             cmds.refresh(suspend=True)
#             return func(*args)
#         finally:
#             cmds.refresh(suspend=False)
#     return _norefresh


def getNamespace():
    namespaces = cmds.namespaceInfo(lon=True, r=True)
    namespaces.remove('UI')
    namespaces.remove('shared')
    return namespaces

def Euler_filter(obj_list):
    xyz = ['.rotateX', '.rotateY', '.rotateZ']
    for obj in obj_list:
        anim_cv = map(lambda x: cmds.connectionInfo(obj+x, sfd=True), xyz)
        anim_cv = map(lambda x: x.rstrip('.output'), anim_cv)
        try:
            anim_cv = filter(lambda x: cmds.nodeType(x) in ['animCurveTL', 'animCurveTU', 'animCurveTA', 'animCurveTT'], anim_cv)
            cmds.filterCurve(anim_cv, f='euler')
        except:
            print('# Euler FilterFailed: '+obj+' #')
            continue
        print('# Euler Filter Success: '+obj+' #')

def getAllNodes(namespace, _regexArgs):
    if len(_regexArgs) == 0:
        regexArgs = ['*']

    nodes = []
    regexArgs = _regexArgs.split(',')

    for regex in regexArgs:
        objs = []
        objSets = []
        regexN = ''
        if namespace != '':
            regexN += namespace + ':'
        regexN = regexN + regex
        try:
            objs = cmds.ls(regexN, type='transform')
            objSets = cmds.sets(regexN, q=True)
        except:
            continue
        if objs != None:
            if len(objs) != 0:
                nodes += objs
        if objSets != None:
            if len(objSets) != 0:
                nodes += objSets

    return nodes


def export_abc_main(**kwargs):
    # outputPath, _namespaceList, regexArgs, step_value, framehandle, _frameRange, add_attr):
    input_ns_list = kwargs['namespace'].split(',')
    frame_range = kwargs['frame_range']
    if frame_range != False:
        sframe = frame_range[0]
        eframe = frame_range[1]
    else:
        sframe = cmds.playbackOptions(q=True, min=True)
        eframe = cmds.playbackOptions(q=True, max=True)

    sframe -= float(kwargs['frame_handle'])
    eframe += float(kwargs['frame_handle'])

    tg_ns_list = []
    scene_ns_list = getNamespace()
    for scene_ns in scene_ns_list:
        for input_ns in input_ns_list:
            match = re.match(scene_ns, input_ns)
            if match != None:
                tg_ns_list.append(scene_ns)


    tg_nodes_dic = {}
    if 'add_attr' in kwargs.keys():
        import pymel.core as pm
        #キーがシェイプ名、値がそのシェイプのフェースアトリビュート値のリストのペアである辞書を宣言
        dictAttributes = {}
        context = "/mat/"
        for eachSG in pm.ls(type="shadingEngine"):
            if eachSG.split(':')[0] not in scene_ns_list:
                continue
            members = pm.sets(eachSG,q=True,nodesOnly=False)
            #SGにオブジェクト/コンポーネントが割り当てられていなければスキップする
            if len(members)==0:
                continue
            #SGにシェーダが割り当てられていなければスキップする。
            #SGのaiSurfaceShaderの入力コネクタがArnoldで優先されるサーフェスシェーダ。なければsurfaceShaderの入力コネクタのサーフェスシェーダが使用される。
            shader = (pm.listConnections(eachSG+".aiSurfaceShader",p=False,c=False,s=True,d=False) or [""])[0]
            if shader == "":
                shader = (pm.listConnections(eachSG+".surfaceShader",p=False,c=False,s=True,d=False) or [""])[0]
            if shader == "":
                continue
            shaderName = shader.name()
            #オブジェクトレベルの割り当てなのかコンポーネントレベルの割り当てなのかに基づいて処理を分岐させる。
            #オブジェクトレベルの場合は、すべてのフェースの数だけのサイズのリストを用意して、リストのすべてのアイテムにシェーダ名を書き込む
            #コンポーネントレベルの場合は、そのフェースのインデックスにシェーダ名の情報を書き込む
            for eachMember in members:
                #SGがオブジェクトに紐付けられている場合の処理
                if type(eachMember) == pm.nodetypes.Mesh:
                    dictAttributes[eachMember]={"shader":[],"rest":[]}
                    dictAttributes[eachMember]["shader"] = [context+eachSG]*eachMember.numFaces()
                    for vtxIndex in range(eachMember.numVertices()):
                        position = pm.pointPosition(eachMember+".vtx["+str(vtxIndex)+"]",world=True).get()
                        dictAttributes[eachMember]["rest"].append( [position[0],position[1],position[2]] )
                #SGがフェースに紐付けられている場合の処理
                elif eachMember._ComponentLabel__ == "f":
                    # listComponents = pm.ls(eachMember,flatten=True)
                    shape = eachMember._node
                    if shape not in dictAttributes:
                        dictAttributes[shape]={"shader":[],"rest":[]}
                        dictAttributes[shape]["shader"]= [""]*eachMember.totalSize()
                        for vtxIndex in range(shape.numVertices()):
                            dictAttributes[shape]["rest"].append( pm.pointPosition(shape+".vtx["+str(vtxIndex)+"]",world=True) )
                    #該当するリストのインデックスにシェーダ名を書き込む
                    for index in eachMember.indices():
                        dictAttributes[shape]["shader"][index] = context+eachSG#shaderName
        restAttributeName = "rest"
        shaderAttributeName = "shop_materialpath"
        for eachShape in dictAttributes:
            #Rest Positionアトリビュートを追加
            if not pm.attributeQuery(restAttributeName+"_AbcGeomScope",node=eachShape,exists=True):
                pm.addAttr(eachShape, dataType="string", longName=restAttributeName+"_AbcGeomScope")
            pm.setAttr(eachShape+"."+restAttributeName+"_AbcGeomScope", "var")
            if not pm.attributeQuery(restAttributeName,node=eachShape,exists=True):
                pm.addAttr(eachShape,dataType="vectorArray",longName=restAttributeName)
            pm.setAttr(eachShape+"."+restAttributeName,dictAttributes[eachShape]["rest"])
            #shop_materialpathアトリビュートを追加
            if not pm.attributeQuery(shaderAttributeName+"_AbcGeomScope",node=eachShape,exists=True):
                pm.addAttr(eachShape, dataType="string", longName=shaderAttributeName+"_AbcGeomScope")
            pm.setAttr(eachShape+"."+shaderAttributeName+"_AbcGeomScope", "uni")
            if not pm.attributeQuery(shaderAttributeName,node=eachShape,exists=True):
                pm.addAttr(eachShape,dataType="stringArray",longName=shaderAttributeName)
            pm.setAttr(eachShape+"."+shaderAttributeName,dictAttributes[eachShape]["shader"])
            

    for tg_ns in tg_ns_list:
        tg_nodes_dic[tg_ns] = getAllNodes(tg_ns, kwargs['abc_item'])
        yeti_objs = cmds.ls(tg_ns+':yetiSet')
        if len(yeti_objs) != 0:
            inyeticasch = cmds.getAttr(tg_ns+":pgYetiMaya"+tg_ns+"Shape.cacheFileName")
            outyeticasch = cmds.getAttr(tg_ns+":pgYetiMaya"+tg_ns+"Shape.outputCacheFileName")
            yeti_path = os.path.join(kwargs['publish_char_path'],'yetimem.txt')
            try:
                with open(yeti_path, 'w') as fp:
                    fp.write(inyeticasch)
                    fp.write('\n')
                    fp.write(outyeticasch)
            except:
                pass

    if not cmds.pluginInfo('AbcExport', q=True, l=True):
        if '_TMP_VER' in os.environ.keys():
            maya_ver = os.environ["_TMP_VER"]
        else:
            info = cmds.about(version=True)
            maya_ver = info.split(" ")[0]
            os.environ['_TMP_VER'] = maya_ver
        plugin_path = "C:/Program Files/Autodesk/Maya{}/bin/plug-ins".format(maya_ver)
        # os.environ["_TMP_VER"] = os.environ["_TMP_VER"]+";"+plugin_path
        cmds.loadPlugin('AbcExport')

    for tg_ns, tg_nodes in tg_nodes_dic.items():
        if len(tg_nodes) == 0:
            continue
        top_node =  tg_ns + ":" + kwargs['top_node']
        if not cmds.objExists(top_node):
            continue
        # abc_file_name = 'abc_'+tg_ns+'.abc'
        abc_file_name = tg_ns+'.abc'
        abc_file_path = kwargs['publish_ver_abc_path']+'/'+abc_file_name

        strAbc = ''
        strAbc = strAbc + '-frameRange '
        strAbc = strAbc + str(sframe) + ' '
        strAbc = strAbc + str(eframe) + ' '
        strAbc = strAbc + '-uvWrite '
        # strAbc = strAbc + '-worldSpace '
        strAbc = strAbc + '-writeVisibility '
        strAbc = strAbc + '-eulerFilter '
        strAbc = strAbc + '-dataFormat ogawa '
        strAbc = strAbc + '-step '
        strAbc = strAbc + str(kwargs['step_value']) + ' '
        strAbc = strAbc + '-root '
        # strAbc = strAbc + top_node + ' '
        for tg_node in tg_nodes:
            strAbc = strAbc  + tg_node + ' ' 
        strAbc = strAbc + '-file '
        strAbc = strAbc + abc_file_path
        if 'add_attr' in kwargs.keys():
            strAbc = strAbc + ' -attr ' + kwargs['add_attr']

        print('AbcExport -j {}'.format(strAbc))
        mel.eval('AbcExport -verbose -j \"{}\"'.format(strAbc))
        return


def ndPyLibExportAbc_caller(args):
    export_abc_main(**args)
    print("ndPylibExportAbc End")

# def ndPyLibExportAbc2(args):
#     argsdic = args
#     outputPath = argsdic['abcOutput']
#     namespaceList = argsdic['namespace']
#     try:
#         step_value = argsdic['step_value']
#     except KeyError:
#         step_value = 1.0
#     framehandle = argsdic['framehandle']
#     frameRange = argsdic['framerange']
#     regexArgs = argsdic['export_item']
#     if "add_attr" in argsdic.keys():
#         add_attr = argsdic['add_attr']
#     else:
#         add_attr = None
#     _exportAbc2(
#         outputPath, namespaceList,
#         regexArgs, step_value,
#         framehandle, frameRange, add_attr)

'''
{'abc_check': False,
 'abc_item': 'abc_Root',
 'anim_item': 'ctrl_set, root',
 'asset_name': 'NursedesseiDragon',
 'asset_path': 'P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiDragon/publish/Setup/RH/maya/current/NursedesseiDragon_Rig_RH.mb',
 'cam_scale': False,
 'debug': True,
 'export_item': {'abc': 'abc_Root', 'anim': 'ctrl_set, root'},
 'export_type': 'abc',
 'frame_handle': False,
 'frame_range': False,
 'group': '',
 'input_path': 'P:/Project/RAM1/shots/ep022/s2227/c008/work/k_ueda/s2227c008_anm_v006.ma',
 'namespace': 'NursedesseiDragon[0-9]*$',
 'pool': '',
 'priority': '50',
 'project': 'RAM1',
 'scene_timewarp': False,
 'sequence': 's2227',
 'shot': 'c008',
 'step_value': False,
 'top_node': 'root'}
'''


