import sys,os
import ND_lib.maya.basic as basic

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

    def get_project_path(self):
        self.project_path = basic.get_project_path_fullName()

    def export_asset(self, mode="Submit", debug="True"):
        import maya.cmds as cmds
        from main_util import ProjectInfo
        import threading
        scene_path = cmds.file(q=True, sn=True)
        ProjectInfoClass = ProjectInfo(scene_path)
        pro_name = ProjectInfoClass.project_name
        shot = ProjectInfoClass.shot
        sequence = ProjectInfoClass.sequence
        shot_code = ProjectInfoClass.shot_code
        execargs_ls = {
                    'chara': self.regular_asset_name,
                    'namespace': self.sg_asset["sg_namespace"],
                    'exportitem': "anim: "+self.sg_asset["sg_anim_export_list"]+", abc: "+self.sg_asset["sg_abc_export_list"],
                    'topnode': self.sg_asset["sg_top_node"],
                    'assetpath': self.sg_asset["sg_asset_path"],
                    'testmode': debug,
                    # 'stepValue': abcstep_override,
                    'framerange_output': "True",
                    'exporttype': self.sg_asset["sg_export_type"],
                    'project': pro_name,
                    'framerange': "None",
                    'framehundle': '0',
                    'framerange_output': 'True',
                    'inputpath': scene_path,
                    'shot': shot,
                    'sequence': sequence,
                    'sceneTimeworp': "False",
                    'env_load': "True",
                    'bakeAnim': "True",
                    'abcCheck': "False",
                    'Priority': '50',
                    'Pool': 'ram1',
                    'Group': 'mem064'}
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
            # thread1 = threading.Thread(target=thread_main, args=(str(execargs_ls), output_file, current_dir))
            # print output_file
            # thread1.start()
            # thread1.join()
            # import time
            # while True:
            #     print thread1
            #     time.sleep(1)
            #     if len(threading.enumerate())==1:
            #         break
            # thread_main(str(execargs_ls), output_file, current_dir)
            from main_util import execExporter_maya
            import ast
            import pprint
            pprint.pprint(execargs_ls)
            argsdict = ast.literal_eval(str(execargs_ls))
            execExporter_maya(kwargs=argsdict)            
                
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


if __name__ == "__main__":
    sys.path.append(r"Y:\tool\ND_Tools\DCC\ND_AssetExporter\pycode\OnMayaTool")
    import OnMayaTool_main; reload(OnMayaTool_main)
    AssetClass_list = OnMayaTool_main.ls_asset_class()
    asset_code_list = OnMayaTool_main.ls_asset_code(AssetClass_list)
    AssetClass_list[0].export_asset(mode="Local")

    # print AssetClass.get_asset_list() ->['gutsFalconFighter', 'vernierNml', 'vulcanNml', 'vulcanDual']