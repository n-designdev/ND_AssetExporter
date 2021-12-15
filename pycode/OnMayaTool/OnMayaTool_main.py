import sys, os
import yaml
import maya.cmds as cmds
import back_starter

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

    def export_asset(self, mode="Submit", debug="True", override_shotpath=None, override_exptype=None, add_attr=None):
        import maya.cmds as cmds
        import main_util
        scene_path = cmds.file(q=True, sn=True)
        ProjectInfoClass = main_util.ProjectInfo(scene_path)
        pro_name = ProjectInfoClass.project_name
        shot = ProjectInfoClass.shot
        sequence = ProjectInfoClass.sequence
        if override_shotpath is not None:
            override_shotpath = override_shotpath + "/"
        execargs_ls = {
                    'chara': self.regular_asset_name,
                    'namespace': self.sg_asset["sg_namespace"],
                    'export_item': "anim: "+self.sg_asset["sg_anim_export_list"]+", abc: "+self.sg_asset["sg_abc_export_list"],
                    'topnode': self.sg_asset["sg_top_node"],
                    'assetpath': self.sg_asset["sg_asset_path"],
                    'debug_mode': debug,
                    'framerange_output': "True",
                    'export_type': self.sg_asset["sg_export_type"],
                    'project': pro_name,
                    'framerange': "None",
                    'framehundle': '0',
                    'framerange_output': 'True',
                    'input_path': str(scene_path),
                    'shot': shot,
                    'sequence': sequence,
                    'scene_timeworp': "False",
                    'env_load': "True",
                    'bake_anim': "True",
                    'abc_check': "False",
                    'Priority': '50',
                    'Pool': 'ram1',
                    'Group': 'mem064',
                    'override_shotpath': override_shotpath,
                    'add_attr': add_attr}

        for key, value in execargs_ls.items():
            print key, value

        if override_exptype is not None:
            execargs_ls["export_type"] = override_exptype
        for key, item in execargs_ls.items():
            if type(item)==str:
                new_item = item.rstrip(',')
                if new_item == '':
                    new_item = None
                if new_item!=None:
                    new_item = new_item.replace(", ", ",")
                    execargs_ls[key] = new_item
        if mode == 'Submit':
            from main_util import DeadlineMod
            DLclass = DeadlineMod(**execargs_ls)
            jobFileslist = [(DLclass.make_submit_files(0))]
            from main_util import submit_to_deadlineJobs
            submit_to_deadlineJobs(jobFileslist)
        else:
            import datetime
            now = datetime.datetime.now()
            filename = "log_" + now.strftime('%Y%m%d_%H%M%S') + self.regular_asset_name + ".txt"
            output_dir = "Y:\\users\\"+os.environ.get("USERNAME")+"\\DCC_log\\ND_AssetExporter"
            output_file = output_dir + "\\" + filename
            current_dir = "Y:\\tool\\ND_Tools\\DCC\\ND_AssetExporter\\pycode"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            thread_main(str(execargs_ls), output_file, current_dir)
            back_starter.back_starter(kwargs=yaml.safe_dump(execargs_ls))

def thread_main(execargs_ls, output_path, current_dir):
    import subprocess
    python = "Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe"
    py_path = "Y:\\tool\\ND_Tools\\DCC\\ND_AssetExporter\\pycode\\main_util.py"
    with open(output_path, "w+")as f:
        proc = subprocess.Popen([python, py_path,str(execargs_ls)], shell=False,stdout=f, cwd=current_dir)
        proc.wait()
    return


def ls_asset_class():
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode")
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode\OnMayaTool")
    import path_util
    import shotgun_mod
    import maya_mod; reload(maya_mod)
    PathClass = path_util.CharSetDirConf(cmds.file(q=True,sceneName=True))
    
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


if __name__ == "__main__":
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode\OnMayaTool")
    import OnMayaTool_main; reload(OnMayaTool_main)
    AssetClass_list = OnMayaTool_main.ls_asset_class()
    asset_code_list = OnMayaTool_main.ls_asset_code(AssetClass_list)
    # export_path = "C:/Users/k_ueda/Desktop/work"
    export_path = 'P:/Project/RAM1/shots/ep022/s2227/c008/publish/cache/alembic/s2227c008_anm_v004_old_asset'
    # AssetClass_list[0].export_asset(mode="Local", override_shotpath=None, override_exptype="abc", add_attr="shop_materialpath")
    AssetClass_list[0].export_asset(mode="Local", override_shotpath=export_path, override_exptype="abc", add_attr="shop_materialpath")

    # print AssetClass.get_asset_list() ->['gutsFalconFighter', 'vernierNml', 'vulcanNml', 'vulcanDual']
