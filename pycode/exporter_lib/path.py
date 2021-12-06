# -*- coding: utf-8 -*-
'''
複数のツールで使用する共通の処理
'''
import os
import sys

import re
import glob

#------------------------------------
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key,'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\','/')
    if path in sys.path: continue
    sys.path.append(path)
#------------------------------------
import exporter_lib.env as util_env
import ND_lib.util.json_io as util_json
import ND_appEnv as appenv

def path_exists(path):
    return os.path.exists(path)

def get_project(path):
    project = None
    root_path = util_env.root_path
    path = path.replace('\\', '/')
    if not path.startswith(root_path):
        # print 'error : The entered path is not "P:/Project/" path. %s' % path
        pass
    else:
        project = path.strip(root_path).split('/')[0]
    return project

def get_project_path(project):
    """
    受け取ったプロジェクト名からプロジェクトのルートパスを返す
    存在しないパスの場合、空白("")を返す
    return:str(exists==True)
    """
    project_path = "%s/%s" % (util_env.root_path, project)
    if os.path.exists(project_path):
        return project_path
    else:
        return ""

def get_replace_char(item):
    _flg = 0
    replace_char = ""
    for char in item:
        if not "{" == char and not _flg:
            continue

        replace_char += char

        if "{" == char:
            _flg = 1

        elif "}" == char:
            _flg = 0
            return replace_char


    return replace_char


def search_type(path, root_path, project_name, type_root, full_path=True):
    template_path = "%s/%s/%s" % (root_path, project_name, type_root)
    _path = []

    template_path_count = len(template_path.split("/"))

    for item in template_path.split("/"):
        if len(_path) >= template_path_count:
            break
        if "{" in item and "}" in item:
            replaced_item = item
            while "{" in replaced_item and "}" in replaced_item:
                replace_char = get_replace_char(replaced_item)

                replaced_item = replaced_item.replace(replace_char, ".+")
            _path.append(replaced_item)
        else:
            _path.append(item)


    pattern = "/".join(_path)
    return re.search(pattern, path)

def get_project_root_path(project_name):
    import exporter_lib.sg_util as sg_util
    import exporter_lib.sgtk_util as sgtk_util
    root_dic = sgtk_util.get_project_root_dic(project_name)

    if 1 >= len(root_dic.keys()):
        root_path = root_dic["primary"]["windows_path"]
    else:
        root_path = root_dic["secondary"]["windows_path"]

    return root_path

def get_path_dic(path, project_name=""):
    """
    パスから判定できる限りの情報をまとめる
    N-designのフォルダ構造に則ったパスのみ対応
    arg:str   return:dict
    """
    try:
        import exporter_lib.sg_util as sg_util
        import exporter_lib.sgtk_util as sgtk_util
    except Exception as e:
        print(e)
        return {}

    path_dic = {}
    dcc = ""
    ext = ""
    type = ""
    path_class = ""
    path = path.replace("\\", "/")

    if not os.path.isdir(path):
        ext = path.rsplit(".")[-1]
        dcc = util_env.extension_dic.get(ext, "").lower()
        dir_path = os.path.dirname(path)

    if not project_name:
        #ShotgunからActiveなプロジェクト一覧を取得してパスと照合する？
        sg_projects = sg_util.get_project(name=None, active=True)
        active_project_list = []
        for sg_project in sg_projects:
            _project_name = sg_project.get("name")
            if _project_name:
                active_project_list.append(_project_name)

        _match_active_project = False
        for sg_project_name in active_project_list:
            project_dir_name = sg_project_name
            if sg_project_name == "PR22":
                project_dir_name = "PR2022"
            if "/%s/" % project_dir_name in path:
                path_dic["project_name"] = sg_project_name
                _match_active_project = True
                break

        if not _match_active_project:
            return path_dic

    #path_envが取得出来たらShotgunTemplateも取得する
    if dcc:
        template_dic = sgtk_util.get_template_dic(sg_project_name, dcc)
    else:
        template_dic = sgtk_util.get_template_dic(sg_project_name)

    project_env = get_conf_dic(sg_project_name.lower())
    root_dic = sgtk_util.get_project_root_dic(sg_project_name)


    if 1 >= len(root_dic.keys()):
        root_path = root_dic["primary"]["windows_path"]
    else:
        root_path = root_dic["secondary"]["windows_path"]

    root_path = root_path.replace("\\", "/")
    project_root = "%s/%s" % (root_path, project_dir_name)
    path_dic["project_root"] = project_root


    #root_pathが取得出来なければ何も出来ないので空を返す
    if not root_path in path:
        return path_dic

    #pathからassetかshotかを判定する
    if search_type(path, root_path, project_dir_name, template_dic["asset"]["root"], full_path=False):
        type = "asset"
    elif search_type(path, root_path, project_dir_name, template_dic["shot"]["root"], full_path=False):
        type = "shot"
    else:
        type = ""

    if type:
        if search_type(path, root_path, project_dir_name, template_dic[type]["work"]):
            path_class = "work"
        elif search_type(path, root_path, project_dir_name, template_dic[type]["publish"]):
            path_class = "publish"


    elif dcc:
        #dccツール単位で特殊なフォルダ構成になっている場合にtypeを決め打ち取得
        if search_type(path, root_path, project_dir_name, template_dic["asset"]["work"]):
            type = "asset"
            path_class = "work"

        elif search_type(path, root_path, project_dir_name, template_dic["asset"]["publish"]):
            type = "asset"
            path_class = "publish"

        elif search_type(path, root_path, project_dir_name, template_dic["shot"]["work"]):
            type = "shot"
            path_class = "work"

        elif search_type(path, root_path, project_dir_name, template_dic["shot"]["publish"]):
            type = "shot"
            path_class = "publish"


    if not type:
        #typeが取得できない場合はtemplateからフォルダ構造を取得するのが困難のためここで終了
        return path_dic

    path_dic["path_type"] = type
    path_dic["path"] = path
    path_list = path.replace(project_root + "/", "").split("/")
    #print "test", path_list
    count = 0

    path_dic["template"] = template_dic

    if path_class:
        path_dic["class"] = path_class
        template_name = path_class
    else:
        template_name = "root"

    if not template_name == "root":
        template_list = template_dic[type][template_name].rsplit("/", 1)[0].split("/")
    else:
        template_list = template_dic[type][template_name].split("/")

    #print "test template_list", template_list

    for item in template_list:
        if not "{" in item:
            count += 1
            continue


        replaced_item = get_replace_char(item).replace("{", "").replace("}", "").lower()
        #print "test", replaced_item
        if replaced_item == "customentity07":
            replaced_item = "roll"
        path_dic[replaced_item] = path_list[count]
        count += 1

    if type == "shot":
        code = project_env.get("preferences", {}).get("shot_code", "{Sequence}{Shot}")
        #print "test", code
        #print "test", path_dic.get("roll", ""), path_dic.get("sequence", "test"), path_dic.get("shot", "test")
        path_dic["shot_code"] = code.replace("{Roll}", path_dic.get("roll", "")).replace("{Sequence}", path_dic.get("sequence", "")).replace("{Shot}", path_dic.get("shot", ""))

    try:
        current_context = sg_util.get_current_context() or None
        path_dic["task_name"] = current_context.task["name"]
    except:
        path_dic["task_name"] = None

    return path_dic

def get_point_path(point, path):
    split_path = path.split("/")
    work_path_list = []

    if not point in path:
        return path

    for i in range(split_path.index(point)):
        work_path_list.append(split_path[i])

    return "/".join(work_path_list)

def create_folders(path):
    '''
    pathの場所にフォルダーを作成する。
    作成するpathまでに存在しないフォルダ全てを作成する。
    '''
    os.makedirs(path)

def generateTargetPath(path, task_group):
    task = util_env.task_dic.get(task_group, 'None')
    # print 'execute generateTargetPath'
    pattern = '^(.*?)/work/'
    sceneName = os.path.basename(path)
    m = re.match(pattern,path)
    if m:
        outputPath = m.groups()[0]
        outputPath += '/publish/%s/' % task
    else:
        outputPath = path.rsplit('/',4)[0]
        outputPath += '/publish/%s' % task
        outputPath += '/%s' % str(sceneName.split('.','_'))

    return outputPath

def create_platePath(project, roll_code, folder_name):
    root = util_env.root_path
    shot_root = os.path.join(root, project, 'shots')
    if folder_name.startswith('s'):
        seq_path = 0
        shot_path = (folder_name.find('c', 0))
        if not shot_path == -1:
            #seq_code = folder_name.strip(folder_name[shot_path:])
            seq_code = re.sub(folder_name[shot_path:], '', folder_name)
            shot_code = folder_name[shot_path:]
            return os.path.join(shot_root, roll_code, seq_code, shot_code, 'publish/plate').replace('\\', '/')

def get_itemDic(input_path, parent='{root}'):
    dic = {}
    parent_path = parent.replace('{root}', input_path)
    if not os.path.exists(parent_path):
        return dic
    for item in os.listdir(parent_path):
        item_dic = dic.setdefault(item, {})
        item_path = '/'.join([parent_path, item])
        item_dic['parent'] = parent
        if os.path.isdir(item_path):
            item_dic['type'] = 'folder'
            item_dic['contents'] = get_itemDic(input_path, item_path)
            app_flg = False
            for k, v in item_dic['contents'].items():
                if v.get('app', None):
                    app_flg = True
            if parent == '{root}' and not app_flg:
                item_dic['app'] = 'sequence'
                item_dic['copy_type'] = util_env.copy_type_dic.get('sequence', None)
                item_dic['collect_path'] = item_path
            total_size = 0
            for k, v in item_dic['contents'].items():
                total_size += int(v.get('size', 0))
            item_dic['size'] = total_size
            dic[item] = item_dic
            continue
        else:
            item_dic['type'] = 'item'
            item_dic['size'] = os.path.getsize(item_path)
            extension = item.rsplit('.', 1)[-1]
            app = util_env.extension_dic.get(extension, False)
            if app == False:
                continue
            item_dic['app'] = app
            item_dic['copy_type'] = util_env.copy_type_dic.get(app, None)
            if item_dic['copy_type'] == 'File':
                item_dic['collect_path'] = item_path
            else:
                item_dic['collect_path'] = parent_path
        dic[item] = item_dic
    return dic

def get_sourceDic(dic):
    collect_dic = {}
    for k, v in dic.items():
        if not v.get('collect_path'):
            if not v.get('contents'):
                continue
            result = get_sourceDic(v.get('contents'))
            if result:
                for rk, rv in result.items():
                    result[rk]['size'] = v.get('size', 0)
                collect_dic.update(result)
        else:
            item_dic = collect_dic.setdefault(k, {})
            item_dic['source_path'] = v.get('collect_path', None)
            item_dic['app'] = v.get('app', None)
            item_dic['copy_type'] = v.get('copy_type', None)
            item_dic['size'] = v.get('size', 0)
            collect_dic[k] = item_dic
    return collect_dic

'''
def get_scene_info_json_path(scene_path):
    """
    受け取ったシーンパスからルールに沿ったコンフィグファイル（json）のパスを返す
    """
    try:
        ext = scene_path.rsplit(".", 1)[1]
    except:
        ext = ""

    scene_path = scene_path.replace("\\", "/")
    scene_name = os.path.basename(scene_path)
    scene_name = scene_name.rsplit(".", 1)[0]

    if "/work/" in scene_path:
        split_work_list = scene_path.split("/work/")
        main_path = split_work_list[0] + "/work"
        user_name = split_work_list[1].split("/")[0]

        output_dir_path = "%s/%s/config" % (main_path, user_name)

    else:
        output_dir_path = os.path.dirname(scene_path)

    if not ext:
        json_path = "%s/%s.json" % (output_dir_path, scene_name)
    else:
        json_path = "%s/%s_%s.json" % (output_dir_path, scene_name, ext)

    return json_path
'''

def get_scene_info_json_path(scene_path):
    """
    受け取ったシーンパスからルールに沿ったコンフィグファイル（json）のパスを返す
    """
    scene_path = scene_path.replace("\\", "/")
    scene_name = os.path.basename(scene_path)
    scene_name = scene_name.rsplit(".", 1)[0]
    try:
        ext = scene_path.rsplit(".", 1)[1]
        scene_info_name = "%s_%s.json" % (scene_name, ext)
    except:
        ext = ""
        scene_info_name = "%s.json" % (scene_name)

    path_dic = get_path_dic(scene_path)
    project_root = path_dic.get("project_root", "")

    if not path_dic or not project_root in scene_path:
        # print "get_scene_info_json_path: Error: Failed to get project information."
        # print path_dic
        return "%s/%s" % (os.path.dirname(scene_path), scene_info_name)

    if not path_dic.has_key("path_type") or not path_dic.has_key("class"):
        return "%s/%s" % (os.path.dirname(scene_path), scene_info_name)

    path_type = path_dic["path_type"]
    path_class = path_dic["class"]

    path_template = path_dic["template"]
    scene_info_path = ""
    path_list = scene_path.replace(project_root + "/", "").split("/")
    count = 0
    if "{HumanUser}" in path_template[path_type][path_class]:
        try :
            for item in path_template[path_type][path_class].split("/"):
                scene_info_path += ("/%s" % path_list[count])
                count += 1
                if "{HumanUser}" in item:
                    break
        except Exception as err_mes:
            # print "get_scene_info_json_path: Error: %s" % str(err_mes)
            return "%s/%s" % (os.path.dirname(scene_path), scene_info_name)

    else:
        try:
            for item in path_template[path_type]["%s_root" % path_class].split("/"):
                scene_info_path += ("/%s" % path_list[count])
                count += 1
        except Exception as err_mes:
            # print "get_scene_info_json_path: Error: %s" % str(err_mes)
            return "%s/%s" % (os.path.dirname(scene_path), scene_info_name)

    return "%s%s/config/%s" % (project_root, scene_info_path, scene_info_name)


def get_byday_folder_path(project, date=None):
    import datetime
    name_date = ""
    if not date:
        date = str(datetime.date.today()).split("-")
    for item in date:
        if len(item) == 4:
            item = "%02d" % (int(item) % 100)
        name_date += str(item)

    return "%s/%s/review/byDay/%s" % (util_env.root_path, project, name_date)


def get_byday_output_path(project, date=None, item=None):
    byday_path = get_byday_folder_path(project, date)
    code = util_env.byday_folder_name
    if item:
        if isinstance(item, dict) and "code" in item:
            code = item.get("code", "")
    else:
        return byday_path

    byday_output_path = "%s/%s_[0-9]*/" % (byday_path, code)

    #print "byDay outputpath search : %s" % byday_path

    search_list = glob.glob(byday_output_path)

    if len(search_list) == 0:
        byday_path += "/%s_01" % code
    else:
        byday_id = sorted(search_list)[-1].replace("\\", "/").split("/")[-2].replace(code, "").replace("_", "")
        byday_id = int(byday_id) + 1
        byday_path += "/%s_%02d" % (code, int(byday_id))

    return byday_path

def get_lut_path_list(project):
    lut_extension_list = ["cube"]
    project_path = "%s/%s" % (util_env.root_path, project)
    lut_path = "%s/Library/LUT_shotgun" % project_path

    lut_list = []
    for lut_extension in lut_extension_list:
        lut_list.extend(glob.glob("%s/*/*.%s" % (lut_path, lut_extension)))
        lut_list.extend(glob.glob("%s/*.%s" % (lut_path, lut_extension)))
    lut_dic = {}
    for lut_path in lut_list:
        lut_path = lut_path.replace("\\", "/")
        lut_name = os.path.basename(lut_path)
        lut_dic[lut_name] = {"lut_name":lut_name, "lut_path":lut_path}

    return lut_dic

def get_conf_path(project):
    conf_path = "%s/projects/%s.json" % (os.path.dirname(appenv.__file__), project)
    conf_path = conf_path.replace("\\", "/")

    return conf_path

def get_conf_dic(project):
    conf_path = get_conf_path(project)
    if not os.path.exists(conf_path):
        return {}

    conf_dic = util_json._loadJson(conf_path)

    return conf_dic
