import sys,os
# import maya.cmds as cmds
import ND_lib.maya.basic as basic
class AssetClass():
    def __init__(self, scene_asset_name_list, regular_asset_name=None):
        self.scene_asset_name_list = scene_asset_name_list
        self.regular_asset_name = regular_asset_name
    
    def export_asset(self):
        pass
    

def ls_asset_class():
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode")
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode\OnMayaTool")
    import path_util
    import shotgun_mod
    import maya_mod; reload(maya_mod)
    #ls download sg
    PathClass = path_util.CharSetDirConf(basic.get_project_path_fullName())
    project = PathClass.project
    base_fieldcodes = ["code", "sg_namespace", "sg_export_type",
                        "sg_top_node", "sg_abc_export_list", 
                        "sg_anim_export_list", "sg_asset_path",
                        "sequences", "shots", "assets"]
    ProSGClass = shotgun_mod.SGProjectClass(project, base_fieldcodes)
    AssetSGDict = ProSGClass.get_dict("Asset")    
    asset_list = []
    for sg_asset in AssetSGDict:
        if sg_asset["sg_namespace"] is not None:
            asset_list.append(sg_asset)
    #ls seane_space
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
            class_list.append(AssetClass(found_namespaces, sg_asset["code"]))
    return class_list
                    
                    
def ls_asset_code(AssetClass_list):
    result_list = []
    for asset_ins in AssetClass_list:
        result_list.append(asset_ins.regular_asset_name)
    return result_list
    
    
if __name__ == "__main__":
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode\OnMayaTool")
    import OnMayaTool_main; reload(OnMayaTool_main)
    AssetClass_list = OnMayaTool_main.ls_asset_class()
    asset_code_list = ls_asset_code(AssetClass_list)
    for code in asset_code_list:
        print code
        
    # print AssetClass.get_asset_list() ->['gutsFalconFighter', 'vernierNml', 'vulcanNml', 'vulcanDual']