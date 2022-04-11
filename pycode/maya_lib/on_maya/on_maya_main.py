import sys, os
import yaml
import maya.cmds as cmds
sys.path.append(r"Y:\tool\ND_Tools\DCC")
sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter_dev\pycode")
sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter_dev\pycode\maya")
import ND_AssetExporter_dev.pycode.shell_lib.util_exporter as util_exporter; reload(util_exporter)
try:
    from import_lib import *
except:
    pass


def ls_asset_code(AssetClass_list):
    result_list = []
    for asset_ins in AssetClass_list:
        result_list.append(asset_ins.regular_asset_name)
    return result_list
    
class AssetClass():
    def __init__(self, scene_asset_name_list, regular_asset_name=None, sg_aaset=None):
        self.scene_asset_name_list = scene_asset_name_list
        self.regular_asset_name = regular_asset_name
        self.sg_asset = sg_aaset

    def export_asset(self, debug="True", override_shotpath=None, override_exptype=None, add_attr=None):
        if override_exptype is not None:
            export_type = override_exptype
        else:
            export_type = self.sg_asset['sg_export_type']

        if override_shotpath == None:
            scene_path = cmds.file(q=True, sn=True)
            opc = util_exporter.outputPathConf(scene_path, export_type=export_type)
            publish_ver_anim_path = opc.publish_ver_anim_path
            publish_ver_abc_path = opc.publsh_ver_abc_path
        else:
            publish_ver_anim_path = override_shotpath.replace(os.path.sep, '/')
            publish_ver_abc_path = override_shotpath.replace(os.path.sep, '/')
    
        argsdic = {
                    'publish_ver_anim_path': publish_ver_anim_path,
                    'publish_ver_abc_path': publish_ver_abc_path,
                    'anim_item': self.sg_asset["sg_anim_export_list"],
                    'abc_item': self.sg_asset['sg_abc_export_list'],
                    'namespace': self.sg_asset['sg_namespace'],
                    'top_node': self.sg_asset['sg_top_node'],
                    'asset_path': self.sg_asset['sg_asset_path'],
                    'step_value': 1.0,
                    'frame_range': False,
                    'frame_handle': 0,
                    'scene_timewarp': False}
        
        if add_attr is not None:
            argsdic['add_attr'] = add_attr

        if export_type=='anim':
            from maya_lib.ndPyLibExportAnim import export_anim_main
            # reload(export_anim_main)
            export_anim_main(**argsdic)
        if export_type=='abc':
            # from maya_lib.ndPyLibExportAbc import export_abc_main
            import maya_lib.ndPyLibExportAbc as ndPyLibExportAbc
            reload(ndPyLibExportAbc)
            ndPyLibExportAbc.export_abc_main(**argsdic)

def ls_asset_class():
    import shotgun_mod
    import maya_mod; reload(maya_mod)
    PathClass = util_exporter.outputPathConf(cmds.file(q=True,sceneName=True))
    
    project = PathClass.pro_name
    base_fieldcodes = ["code", "sg_namespace", "sg_export_type",
                        "sg_top_node", "sg_abc_export_list",
                        "sg_anim_export_list", "sg_asset_path",
                        "sequences", "shots", "assets"]
    ProSGClass = util_exporter.SGProjectClass(project, base_fieldcodes)
    AssetSG_list = ProSGClass.get_dict("Asset")
    asset_list = []
    for sg_asset in AssetSG_list:
        if sg_asset["sg_namespace"] is not None:
            asset_list.append(sg_asset)
    #ls scene_space
    import re
    scene_namespaces = maya_mod.getNamespace()
    class_list = []

    for sg_asset in asset_list:
        found_namespaces = []
        sg_namespace = sg_asset["sg_namespace"]
        for scene_namespace in scene_namespaces:
            if re.match(sg_namespace, scene_namespace) is not None:
                found_namespaces.append(sg_asset["code"])
        if len(found_namespaces) != 0:
            # for ProSG_dict in ProSG_list:
            class_list.append(AssetClass(found_namespaces, sg_asset["code"], sg_asset))
    return class_list

def get_asset_class_dict():
    import shotgun_mod
    import maya_mod; reload(maya_mod)
    PathClass = util_exporter.outputPathConf(cmds.file(q=True,sceneName=True))
    
    project = PathClass.pro_name
    base_fieldcodes = ["code", "sg_namespace", "sg_export_type",
                        "sg_top_node", "sg_abc_export_list",
                        "sg_anim_export_list", "sg_asset_path",
                        "sequences", "shots", "assets"]
    ProSGClass = util_exporter.SGProjectClass(project, base_fieldcodes)
    AssetSG_list = ProSGClass.get_dict("Asset")
    asset_list = []
    for sg_asset in AssetSG_list:
        if sg_asset["sg_namespace"] is not None:
            asset_list.append(sg_asset)
    #ls scene_space
    import re
    scene_namespaces = maya_mod.getNamespace()
    class_dict = {}

    for sg_asset in asset_list:
        found_namespaces = []
        sg_namespace = sg_asset["sg_namespace"]
        for scene_namespace in scene_namespaces:
            if re.match(sg_namespace, scene_namespace) is not None:
                found_namespaces.append(sg_asset["code"])
        if len(found_namespaces) != 0:
            # for ProSG_dict in ProSG_list:
            class_dict[sg_asset['code']] = AssetClass(found_namespaces, sg_asset["code"], sg_asset)
    return class_dict


if __name__ == "__main__":
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter_dev\pycode")
    import maya_lib.on_maya.on_maya_main as on_maya_main; reload(on_maya_main)
    # AssetClass_list = on_maya_main.ls_asset_class()

    asset_code_list = on_maya_main.ls_asset_code(on_maya_main.ls_asset_class())
    AssetClass_dict = on_maya_main.get_asset_class_dict()
    import pprint
    pprint.pprint(AssetClass_dict)
    # export_path = "C:/Users/k_ueda/Desktop/work"
    export_path = 'P:/Project/RAM1/shots/ep022/s2227/c008/publish/cache/alembic/s2227c008_anm_v004_old_asset'
    # AssetClass_list[0].export_asset(mode="Local", override_shotpath=None, override_exptype="abc", add_attr="shop_materialpath")
    # AssetClass_list[0].export_asset(override_shotpath=export_path, override_exptype="abc", add_attr="shop_materialpath")

    AssetClass_dict['NursedesseiDragon'].export_asset(override_shotpath=export_path, override_exptype="abc", add_attr="shop_materialpath")

    # print AssetClass.get_asset_list() ->['gutsFalconFighter', 'vernierNml', 'vulcanNml', 'vulcanDual']
