# -*- coding: utf-8 -*-
"""
ShotgunToolkitに関連した処理
"""
import os
import sys

import yaml

#------------------------------------
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key,'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\','/')
    if path in sys.path: continue
    sys.path.append(path)
#------------------------------------
import ND_lib.shotgun.sg_util as sg_util

def append_sgtk_to_sys(project_name):
    """
    project_nameからN-design所定の位置を割り出してsys.pathに追加する
    """
    core_path = "Y:\\tool\\ND_Tools\\shotgun\\ND_sgtoolkit_%s\\install\\core\\python" % project_name
    if not core_path in sys.path:
        sys.path.append(core_path)

def get_project_sgtk_from_path(path):
    import sgtk
    return sgtk.sgtk_from_path(path)

def get_context_from_path(project_sgtk, path):
    import sgtk
    return project_sgtk.context_from_path(path)

def get_project_context_from_path(project_path, item_path):
    import sgtk
    project_sgtk = sgtk.sgtk_from_path(project_path)
    ctx = project_sgtk.context_from_path(item_path)

    return ctx, project_sgtk

"""
ShotgunToolkitのyamlに関連する処理
"""

"""
取得
"""
def get_sgtk_path(project):
    dic = sg_util.get_primary_pc(project)
    sgtk_path = dic["windows_path"].replace("\\", "/")
    return sgtk_path

def get_sgtk_template_path(sgtk_path):
    return "%s/config/core/templates.yml" % sgtk_path

def get_sgtk_roots_path(sgtk_path):
    roots_yaml_path = "%s/config/core/roots.yml" % sgtk_path
    return roots_yaml_path

def get_project_root_dic(project):
    sgtk_path = get_sgtk_path(project)
    roots_yaml_path = get_sgtk_roots_path(sgtk_path)

    roots_dic = {"Windows": "", "Mac": "", "Linux": ""}

    f = open(roots_yaml_path, "r")
    roots = yaml.safe_load(f)
    f.close()


    #roots_dic["Windows"] = roots["primary"]["windows_path"].replace("\\", "/")

    return roots


def get_template_dic(project, dcc=None):
    """
    ShotgunToolkitのTemplate.yamlから必要なパスを繋げて返却する
    """
    template_dic = {}

    sgtk_path = get_sgtk_path(project)
    template_path = get_sgtk_template_path(sgtk_path)

    f = open(template_path, "r")
    template = yaml.safe_load(f)
    f.close()

    #DCCツール単位にテンプレートを取得
    #DCC情報が無ければ一つ手前の階層を取得
    #QTは強制的にElseへ
    if dcc and not dcc == "qt":
        shot_root = template["paths"]["shot_root"]
        shot_work = template["paths"]["%s_shot_work" % (dcc.lower())]["definition"]
        shot_work_root = template["paths"]["shot_work_root"]
        shot_publish = template["paths"]["%s_shot_publish" % (dcc.lower())]["definition"]
        shot_publish_root = template["paths"]["shot_publish_root"]
        asset_root = template["paths"]["asset_root"]
        asset_work = template["paths"]["%s_asset_work" % (dcc.lower())]["definition"]
        asset_work_root = template["paths"]["asset_work_root"]
        asset_publish = template["paths"]["%s_asset_publish" % (dcc.lower())]["definition"]
        asset_publish_root = template["paths"]["asset_publish_root"]

    else:
        shot_root = template["paths"]["shot_root"]
        shot_work = template["paths"]["shot_work_root"]
        shot_work_root = template["paths"]["shot_work_root"]
        shot_publish = template["paths"]["shot_publish_root"]
        shot_publish_root = template["paths"]["shot_publish_root"]
        asset_root = template["paths"]["asset_root"]
        asset_work = template["paths"]["asset_work_root"]
        asset_work_root = template["paths"]["asset_work_root"]
        asset_publish = template["paths"]["asset_publish_root"]
        asset_publish_root = template["paths"]["asset_publish_root"]


    template_dic.setdefault("asset", {})
    template_dic["asset"]["root"] = get_keys_path(asset_root, template)
    template_dic["asset"]["work"] = get_keys_path(asset_work, template)
    template_dic["asset"]["work_root"] = get_keys_path(asset_work_root, template)
    template_dic["asset"]["publish"] = get_keys_path(asset_publish, template)
    template_dic["asset"]["publish_root"] = get_keys_path(asset_publish_root, template)
    template_dic.setdefault("shot", {})
    template_dic["shot"]["root"] = get_keys_path(shot_root, template)
    template_dic["shot"]["work"] = get_keys_path(shot_work, template)
    template_dic["shot"]["work_root"] = get_keys_path(shot_work_root, template)
    template_dic["shot"]["publish"] = get_keys_path(shot_publish, template)
    template_dic["shot"]["publish_root"] = get_keys_path(shot_publish_root, template)

    return  template_dic

def get_keys_path(path, template):
    split_path = path.split("/")

    for item in split_path:
        if "@" in item:
            key = item.replace("@", "")
            key_path = get_keys_path(template["paths"][key], template)

            path = path.replace(item, key_path)

    return path
