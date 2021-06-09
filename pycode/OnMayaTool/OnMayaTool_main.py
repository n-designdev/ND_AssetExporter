import sys,os
import maya.cmds as cmds
import ND_lib.maya.basic as basic

def OnMaya_main():
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode")
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode\OnMayaTool")
    import path_util
    import shotgun_mod
    import maya_mod; reload(maya_mod)
    #download sg
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
    #search namespace
    import re
    scene_namespaces = maya_mod.getNamespace()
    found_namespaces = []
    for sg_asset in asset_list:
        sg_namespace = sg_asset["sg_namespace"]
        for scene_namespace in scene_namespaces:
            if re.match(sg_namespace, scene_namespace) is not None:
                found_namespaces.append(sg_asset["code"])
                break
    return found_namespaces 

if __name__ == "__main__":
    print OnMaya_main()