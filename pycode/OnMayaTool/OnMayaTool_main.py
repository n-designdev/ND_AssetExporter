import sys,os
# import maya.cmds as cmds
import ND_lib.maya.basic as basic
class AssetClass():
    def __init__(self, scene_asset_name_list, regular_asset_name=None, sg_aaset=None):
        self.scene_asset_name_list = scene_asset_name_list
        self.regular_asset_name = regular_asset_name
        self.sg_asset = sg_aaset

    def get_project_path(self):
        self.project_path = basic.get_project_path_fullName()

    def export_asset(self, debug=None):

        ProjectInfoClass = mu.ProjectInfo(self.inputpath)
        pro_name = ProjectInfoClass.project_name
        shot = ProjectInfoClass.shot
        sequence = ProjectInfoClass.sequence
        shot_code = ProjectInfoClass.shot_code
        execargs_ls = {
                    'chara': chara,
                    'namespace': namespace,
                    'exportitem': exportitem,
                    'topnode': topnode,
                    'assetpath': assetpath,
                    'testmode': debug,
                    # 'stepValue': abcstep_override,
                    'framerange_output': True,
                    'exporttype': exporttype,
                    'project': self.project,
                    'framerange': framerange,
                    'framehundle': framehundle,
                    'inputpath': self.inputpath.encode('utf-8'),
                    'shot': self.ui.shot_line.text().encode(),
                    'sequence': self.ui.cut_line.text().encode(),
                    'env_load': self.ui.project_loader_checkbox.isChecked(),
                    'bakeAnim': self.ui.bake_anim.isChecked(),
                    'sceneTimeworp': self.ui.scene_timeworp_check.isChecked(),
                    'Priority': self.ui.priority.text(),
                    'Pool': self.ui.poollist.currentText(),
                    'Group': self.ui.grouplist.currentText()}


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
            class_list.append(AssetClass(found_namespaces, sg_asset["code"]), sg_asset)
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
    import pprint
    pprint.pprint(AssetClass_list[0].sg_asset)

    # print AssetClass.get_asset_list() ->['gutsFalconFighter', 'vernierNml', 'vulcanNml', 'vulcanDual']