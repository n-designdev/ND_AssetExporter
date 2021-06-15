import sys,os
# import maya.cmds as cmds
import ND_lib.maya.basic as basic
class AssetClass():
    def __init__(self, scene_asset_name_list, regular_asset_name=None, sg_aaset=None):
        self.scene_asset_name_list = scene_asset_name_list
        self.regular_asset_name = regular_asset_name
        self.sg_asset = sg_aaset #
        #{'sg_anim_export_list': 'ctrl_set, root, allWorld_ctrloffA', 'code': 'gutsFalconNml', 'assets': [], 'sg_asset_path': 'P:\\Project\\RAM1\\assets\\chara\\gutsFalcon\\gutsFalconNml\\publish\\Setup\\RH\\maya\\current\\gutsFalconNml_Rig_RH.mb', 'sg_export_type': 'anim', 'sg_namespace': 'gutsFalconNml', 'shots': [{'type': 'Shot', 'id': 35017, 'name': 's000c000'}, {'type': 'Shot', 'id': 37965, 'name': 's1021c002'}, {'type': 'Shot', 'id': 38545, 'name': 's1509c001'}, {'type': 'Shot', 'id': 38776, 'name': 's1740c001'}, {'type': 'Shot', 'id': 36007, 'name': 's217c003'}, {'type': 'Shot', 'id': 35806, 'name': 's218c005'}, {'type': 'Shot', 'id': 35807, 'name': 's221c001'}, {'type': 'Shot', 'id': 36008, 'name': 's246Ac001'}, {'type': 'Shot', 'id': 35808, 'name': 's247c001'}, {'type': 'Shot', 'id': 36011, 'name': 's301c000'}, {'type': 'Shot', 'id': 36015, 'name': 's314c003'}, {'type': 'Shot', 'id': 36016, 'name': 's314c004'}, {'type': 'Shot', 'id': 36018, 'name': 's315c004'}, {'type': 'Shot', 'id': 36019, 'name': 's320c002'}, {'type': 'Shot', 'id': 36020, 'name': 's320c003'}, {'type': 'Shot', 'id': 36021, 'name': 's320c005'}, {'type': 'Shot', 'id': 36022, 'name': 's320c006'}, {'type': 'Shot', 'id': 36023, 'name': 's320c007'}, {'type': 'Shot', 'id': 36025, 'name': 's325c002'}, {'type': 'Shot', 'id': 36029, 'name': 's331c020'}, {'type': 'Shot', 'id': 35872, 'name': 's411c002'}, {'type': 'Shot', 'id': 36033, 'name': 's413c001'}, {'type': 'Shot', 'id': 36037, 'name': 's504c002'}, {'type': 'Shot', 'id': 36038, 'name': 's504c003'}, {'type': 'Shot', 'id': 36040, 'name': 's508Ac001'}, {'type': 'Shot', 'id': 36041, 'name': 's523c002'}, {'type': 'Shot', 'id': 36042, 'name': 's523c004'}, {'type': 'Shot', 'id': 36043, 'name': 's525c010'}, {'type': 'Shot', 'id': 38388, 'name': 's600c122A'}, {'type': 'Shot', 'id': 36044, 'name': 's616c001'}, {'type': 'Shot', 'id': 36048, 'name': 's625c001'}, {'type': 'Shot', 'id': 36054, 'name': 's646Ac001'}, {'type': 'Shot', 'id': 36053, 'name': 's646c001'}, {'type': 'Shot', 'id': 37424, 'name': 'sOPc009'}], 'sequences': [], 'sg_abc_export_list': None, 'sg_top_node': 'root', 'type': 'Asset', 'id': 8477}


    def get_project_path(self):
        self.project_path = basic.get_project_path_fullName()

    # def export_asset(self, debug=None):

        ProjectInfoClass = mu.ProjectInfo(self.inputpath)
        pro_name = ProjectInfoClass.project_name
        shot = ProjectInfoClass.shot
        sequence = ProjectInfoClass.sequence
        shot_code = ProjectInfoClass.shot_code
        execargs_ls = {
                    'chara': self.regular_asset_name,
                    'namespace': self.sg_asset["sg_namespace"],
                    'exportitem': self.sg_asset["sg_anim_export_list"],
                    'topnode': self.sg_asset["sg_top_node"]
                    'assetpath': self.sg_asset["sg_asset_path"],
                    'testmode': debug,
                    # 'stepValue': abcstep_override,
                    'framerange_output': True,
                    'exporttype': self.sg_asset["sg_export_type"],
                    'project': pro_name,
                    'framerange': framerange,
                    'framehundle': framehundle,
                    'inputpath': self.inputpath.encode('utf-8'),
                    'shot': shot,
                    'sequence': sequence,
                    'env_load': True,
                    'bakeAnim': True,


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
    AssetSG_list = ProSGClass.get_dict("Asset")
    asset_list = []
    for sg_asset in AssetSG_list:
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
            # for ProSG_dict in ProSG_list:
            class_list.append(AssetClass(found_namespaces, sg_asset["code"], sg_asset))
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

    # print AssetClass.get_asset_list() ->['gutsFalconFighter', 'vernierNml', 'vulcanNml', 'vulcanDual']