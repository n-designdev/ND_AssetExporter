# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
#------------------------------------
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key,'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\','/')
    if path in sys.path: continue
    sys.path.append(path)
#------------------------------------
#Shotgunのスクリプトキーを取得
import exporter_lib.sg_scriptkey as sg_scriptkey
sg = sg_scriptkey.scriptKey()
#------------------------------------
#shotgun_api3
#https://github.com/shotgunsoftware/python-api
import exporter_lib.shotgun_api3.shotgun as shotgun

"""
Shotgunから情報を取得する
"""
def get_shotgun_page(project, entity_name):
    filters = [["project", "is", project], ["name", "is", entity_name]]
    fields = ["name", "entity_type", "folder"]

    return sg.find_one("Page", filters, fields)

def sg_find(entity, filters, fields):
    orders = [{'field_name':'Id', 'direction':'asc'}]
    try:
        return sg.find(entity, filters, fields, order=orders)
    except:
        return False

def sg_find_one(entity, filters, fields):
    try:
        return sg.find_one(entity, filters, fields)
    except Exception as error_mes:
        print(error_mes)
        return False
def get_current_context():
    try:
        import sgtk

        # get the current engine (e.g. tk-maya)

        current_engine = sgtk.platform.current_engine()
        return current_engine.context
    except error_mes:
        print("get CurrentContext Error:%s" % error_mes)
        return None

'''
ユーザー情報（HumanUser）の取得
'''
def get_user(login, active=False, add_fields=[]):
    #ログインIDを渡すとHumanUserEntityの値を返却する
    if active:
        filters = [['login', 'is', login], ["sg_status_list", "is", "act"]]
    else:
        filters = [['login', 'is', login]]
    fields = ['name', 'firstname', 'lastname', 'login', 'permission_rule_set', "sg_position"]
    if add_fields:
        fields += add_fields
    userList = sg.find('HumanUser', filters, fields)

    #loginは被らないという前提(改良の余地あり)
    if len(userList):
        return userList[0]
    else:
        return False

def get_users(active=False, filters=[], add_filters=[]):
    #HumanUserEntityのリストを返す
    #activeがTrueならアクティブユーザーのみ
    if not len(filters):
        if active:
            filters = [["sg_status_list", "is", "act"], ["name", "is_not", "Shotgun Support"]]
        else:
            filters = [["name", "is_not", "Shotgun Support"]]

    if len(add_filters):
        for add_filter in add_filters:
            filters.append(add_filter)

    fields = ['name', 'firstname', 'lastname', 'login', 'permission_rule_set', "sg_position"]
    userList = sg.find('HumanUser', filters, fields)

    return userList

def get_assigned_users(project):
    filters = [['projects', 'in', project]]
    fields = ['name', 'firstname', 'lastname', 'login', 'permission_rule_set', "sg_position"]
    return sg.find('HumanUser', filters, fields)

'''
グループ情報（Group）の取得
'''
def get_groups(filters=[]):
    if not len(filters):
        filters = [["code", "is_not", "Shotgun"]]

    fields = ["code", "users", "sg_grouptype", "sg_project"]
    groupList = sg.find('Group', filters, fields)

    return groupList

'''
プロジェクト情報（Project）の取得
'''
def get_project(name=None, active=True, all=False):
    #project 情報を取得
    #name プロジェクト名（文字列）を受け取って該当するEntity情報を返す
    #------------------
    if active:
        if name:
            filters = [['is_template', 'is', False],['sg_status', 'is', 'Active'],['name', 'is', name], ["name", "is_not", "Other"]]
        else:
            if all:
                filters = [['is_template', 'is', False],['sg_status', 'is', 'Active']]
            else:
                filters = [['is_template', 'is', False],['sg_status', 'is', 'Active'], ["name", "is_not", "Other"]]
    else:
        if name:
            filters = [['is_template', 'is', False], ['name', 'is', name], ["name", "is_not", "Other"]]
        else:
            if all:
                filters = [['is_template', 'is', False]]
            else:
                filters = [['is_template', 'is', False], ["name", "is_not", "Other"]]

    fields = ['name']
    projList = sg.find('Project', filters, fields)

    return projList

def get_projList(name=None):
    #project 情報を取得
    #name プロジェクト名（文字列）を受け取って該当するEntity情報を返す
    #------------------
    if name:
        filters = [['is_template', 'is', False],['sg_status', 'is', 'Active'],['name', 'is', name]]
    fields = ['name']
    projList = sg.find('Project', filters, fields)

    return projList

def get_assigned_project(user, active=True):
    if active:
        filters = [['is_template', 'is', False], ['sg_status', 'is', 'Active'], ["name", "is_not", "Other"], ["users", "in", user]]
    else:
        filters = [['is_template', 'is', False], ["name", "is_not", "Other"], ["users", "in", user]]

    fields = ['name']
    return sg.find('Project', filters, fields)



'''
パブリッシュファイル情報（PublishedFile）の取得
'''
def get_published_files(project=None, filters=None):
    fields = ["code", "name", "path", "entity", "project"]
    if not filters:
        if not project:
            return []
        filters = [["project", "is", project]]
    return sg.find("PublishedFile", filters, fields)

'''
パイプラインコンフィグレーション情報（PipelineConfiguration）の取得
'''
def get_primary_pc(project):
    project_entity = get_project(project)[0]
    filters = [["project", "is", project_entity], ["code", "is", "Primary"]]
    fields = ["windows_path"]

    return sg.find_one("PipelineConfiguration", filters, fields)

'''
タスク情報（Task）の取得
'''
def get_task(filters):
    #filters = [['id', 'is', 24608]]
    fields = ['task_assignees', 'project', "sg_status_list"]
    task = sg.find('Task', filters, fields)
    return task

def get_tasks_from_assets(filters):
    fields = ['code', 'tasks']
    assets = sg.find('Asset', filters, fields)
    if not assets:
        return None
    for asset in assets:
        print(asset)

def get_status_entity(code):
    fields = ["name", "code"]
    filters = [["code", "is", code]]
    return sg.find("Status", filters, fields)

def get_step_number(step_name):
    """
    step名から番号を取得する
    名前に「_」が入っていない場合は命名規則違反の為、全タスク中最も大きい値で返す
    """
    if "_" in step_name:
        return int(step_name.split("_", 1)[0])
    else:
        return 9999

def get_assigneDict(proj, user):
    #プロジェクト名とユーザー名でタスクを絞り込んで返す
    filters = [['project', 'is', proj]]

    #タスクの取得
    fields = ['task_assignees', 'Id', 'content', 'step', 'project']
    orders = [{'field_name':'Id', 'direction':'asc'}]
    taskDict = sg.find('Task', filters, fields, order=orders)
    #取得結果の覚書（task）
    #{'content': 'AnimationHigh',
    #'task_assignees': [{'type': 'HumanUser', 'id': 149, 'name': 'shotgun-dev'}, {'type': 'HumanUser', 'id': 118, 'name': 'tatsuya sugano'}],
    #'step': {'type': 'Step', 'id': 26, 'name': 'Model'},
    #'type': 'Task', 'id': 18901}
    assigneDict = {}
    for task in taskDict:
        #1タスクにつき複数人がアサインされる為にtask_assigneesはリストで格納されている
        for assigned_to in task['task_assignees']:
            if assigned_to['name'] == user:
                assigneDict[task['id']] = {'content':task['content'],
                                          'assigned_to':assigned_to['name'],
                                          'step':task['step'],
                                          'user':assigned_to,
                                          'project':task['project']}

    return assigneDict

def get_assigneDict_from_entity(proj, user, item):
    #プロジェクト名とユーザー名でタスクを絞り込んで返す
    filters = [['project', 'is', proj], ["entity", "is", item]]

    #タスクの取得
    fields = ['task_assignees', 'Id', 'content', 'step', 'project', "entity", "sg_status_list"]
    orders = [{'field_name':'Id', 'direction':'asc'}]
    taskDict = sg.find('Task', filters, fields, order=orders)
    #取得結果の覚書（task）
    #{'content': 'AnimationHigh',
    #'task_assignees': [{'type': 'HumanUser', 'id': 149, 'name': 'shotgun-dev'}, {'type': 'HumanUser', 'id': 118, 'name': 'tatsuya sugano'}],
    #'step': {'type': 'Step', 'id': 26, 'name': 'Model'},
    #'type': 'Task', 'id': 18901}
    assigneDict = {}
    for task in taskDict:
        #1タスクにつき複数人がアサインされる為にtask_assigneesはリストで格納されている
        for assigned_to in task['task_assignees']:
            if assigned_to['name'] == user:
                assigneDict[task['id']] = {'content':task['content'],
                                          'assigned_to':task["task_assignees"],
                                          'step':task['step'],
                                          'user':assigned_to,
                                          'project':task['project'],
                                          "entity": task["entity"],
                                          "status": task["sg_status_list"]}
    return assigneDict

def get_taskDict_from_entity(proj, item):
    #プロジェクト名とユーザー名でタスクを絞り込んで返す
    filters = [['project', 'is', proj], ["entity", "is", item]]

    #タスクの取得
    fields = ['task_assignees', 'Id', 'content', 'step', 'project', "entity", "sg_status_list"]
    orders = [{'field_name':'Id', 'direction':'asc'}]
    task_list = sg.find('Task', filters, fields, order=orders)
    #取得結果の覚書（task）
    #{'content': 'AnimationHigh',
    #'task_assignees': [{'type': 'HumanUser', 'id': 149, 'name': 'shotgun-dev'}, {'type': 'HumanUser', 'id': 118, 'name': 'tatsuya sugano'}],
    #'step': {'type': 'Step', 'id': 26, 'name': 'Model'},
    #'type': 'Task', 'id': 18901}

    task_dict = {}
    for task in task_list:
        #1タスクにつき複数人がアサインされる為にtask_assigneesはリストで格納されている
        #for assigned_to in task['task_assignees']:
        #    if assigned_to['name'] == user:
        task_dict[task['id']] = {'content':task['content'],
                                  'assigned_to':task["task_assignees"],
                                  'step':task['step'],
                                  'user':task["task_assignees"],
                                  'project':task['project'],
                                  "entity": task["entity"],
                                  "status": task["sg_status_list"]}

    return task_dict

def get_asset_code(taskDict, proj):
    filters = [['project', 'is', proj]]
    fields = ['code', 'tasks']
    orders = [{'field_name':'code', 'direction':'asc'}]
    assetDict = sg.find('Asset', filters, fields, order=orders)
    resultDict = {}

    for asset in assetDict:
        if asset['tasks'] and asset['code']:
            for task in asset['tasks']:
                assigned_to = taskDict.get(task['id'], None)
                if assigned_to:
                    resultDict[task['id']] = taskDict[task['id']]
                    resultDict[task['id']].update({'code':asset['code']})
                    resultDict[task['id']].update({'type':asset['type']})
                    resultDict[task['id']].update({'config':asset})

    return resultDict

def get_sequence_code(taskDict, proj):
    filters = [['project', 'is', proj]]
    fields = ['sg_sequence', 'tasks']
    orders = [{'field_name':'sg_sequence', 'direction':'asc'}]
    shotDict = sg.find('Shot', filters, fields, order=orders)
    resultDict = {}

    for shot in shotDict:
        if shot['tasks'] and shot['sg_sequence']:
            for task in shot['tasks']:
                assigned_to = taskDict.get(task['id'], None)
                #ShotのタスクIDが一致したものだけリストする
                if assigned_to:
                    resultDict[task['id']] = taskDict[task['id']]
                    resultDict[task['id']].update({'code':shot['sg_sequence']['name']})
                    resultDict[task['id']].update({'type':shot['type']})
                    resultDict[task['id']].update({'config':shot})
                #print shot['sg_sequence']['name'], task['name'], task['id']
    return resultDict
    #return assigneDict

'''
バージョン情報（Version）の取得
'''
def get_version(filters, filter_operator="all"):
    #versions情報を取得
    fields = ['code',
              'sg_status_list',
              'sg_path_to_movie',
              'sg_path_to_frames',
              'sg_task.Task.id',
              'sg_task.Task.content',
              'sg_task.Task.sg_status_list',
              'project.Project.name',
              'user.HumanUser.name',
              'playlists']
    version = sg.find('Version', filters, fields, filter_operator=filter_operator)
    return version

def get_versions_from_playlists(name, status, project=None):
    version_list = []
    #playlist情報を取得
    playlists = get_playlists_at_filters(name, status, project)
    for playlist in playlists:
        versions = playlist.get('versions', None)
        for version in versions:
            _id = version.get('id')
            filters = [['id', 'is', _id]]
            version = get_version(filters)

            version_list.extend(version)

    return version_list

'''
プレイリスト情報（Playlist）の取得
'''
def get_playlists(filters):
    #playlist情報を取得
    fields = ['id', 'code', 'versions']
    playlistList = sg.find('Playlist', filters, fields)
    return playlistList

def get_playlists_at_filters(names, status, project=None):
    playlists = []
    if isinstance(names, list):
        for name in names:
            playlists.extend(get_versions_from_playlists(name, status))

    if status:
        filters = [['code', 'contains', names],
            ['versions.Version.sg_task.Task.sg_status_list', 'is', status]]
    else:
        filters = [['code', 'contains', names]]

    if not project is None:
        try:
            filters.extend([['project.Project.name', 'is', project]])
        except:
            print('Warnning:project name "%s" is does not exists' % project)

    playlists.extend(get_playlists(filters))

    return playlists

def get_playlist_template_name(date, project):
    """
    日付とプロジェクト名からプレイリスト名のテンプレートを作成する
    """
    _day = str(date).split("-")
    _year = _day[0]
    _month = _day[1]
    _day = _day[2]

    if isinstance(project, dict):
        project = project["name"]

    return "%s_%s%s_%s" % (_year, _month, _day, project.upper())

def get_versions_info_from_playlist(playlist):
    """
    受け取ったプレイリストに含まれるversionsにversion情報を付与して返す
    プレイリストにversionsが含まれない場合playlistをそのまま返す
    """
    if isinstance(playlist, list):
        for item in playlist:
            item = get_versions_info_from_playlist(item)

        return playlist

    versions = playlist.get('versions', [])

    if not versions:
        return playlist

    _new_versions = []
    for version in versions:
        _id = version.get('id')
        filters = [['id', 'is', _id]]
        _new_versions.extend(get_version(filters))

    playlist["versions"] = _new_versions

    return playlist

def get_playlists_backnumber(source_playlists, shotgun_playlists):
    """
    source_playlists:命名規則に則って生成された過去数日分のプレイリスト名の一部文字列のリスト
    shotgun_playlists:特定のプロジェクトに属するプレイリスト名のリスト

    shotgun_playlistsの中からsource_playlistsに格納される文字列と部分一致する文字列を取得する
    """
    import re
    match_list = []
    for _source in source_playlists:
        pattern = "^%s+" % _source
        for _shotgun in shotgun_playlists:
            m = re.search(pattern, _shotgun.get("code"))
            if not m:
                continue
            else:
                match_list.append(_shotgun)

    return match_list

def get_playlists_for_nd_tool(project, tool):
    """
    ND_toolで特定のToolを指定しているプレイリストのリストを取得する
    """
    filters = [["project", "is", project], ["sg_nd_tools.CustomNonProjectEntity02.code", "is", tool]]
    fields = ["code", "sg_nd_tool", 'versions']
    playlists = sg.find("Playlist", filters, fields)
    result = []
    for playlist in playlists:
        result.append(playlist)

    return result

def get_event_log(filters, fields):
    return sg.find("EventLogEntry", filters, fields)

def get_time_log(filters, fields):
    return sg.find("TimeLog", filters, fields)

'''
********************************
Shotgunの情報を更新する
********************************
'''
def update_entity(entity_type, update_item):
    if isinstance(update_item, list):
        for upload in update_item:
            update_entity(entity_type, upload)
    elif not isinstance(update_item, dict):
        return
    else:
        try:
            type_id = update_item.pop("id")
            result = sg.update(entity_type, type_id, update_item)
            print ("ShotgunEntity %s Update : Result : Complete! %s" % (entity_type, result))
            return result
        except Exception as error_mes:
            print ("ShotgunEntity %s Update : Result : eFailed.. %s" % (entity_type, str(error_mes)))
            return error_mes

def shotgun_entity_upload(type, type_id, upload_dic):
    #旧upload_entity (使っているツールが無くなれば削除)
    if isinstance(upload_dic, list):
        for upload in upload_dic:
            shotgun_entity_upload(type, type_id, upload)

    else:
        try:
            result = sg.update(type, type_id, upload_dic)
            print ("ShotgunEntity %s Update Result : UpdateComplete! %s" % (type, result))
            return result
        except Exception as error_mes:
            print ("ShotgunEntity %s Update Result : UpdateError %s" % (type, str(error_mes)))
            return error_mes

def update_task_status(task_id, status='pub'):
    #タスクIDを受け取ってステータスを書き換える
    #ステータスのデフォルト値はpub
    if status is None:
        print ('ShotgunTaskStatus Update Result : Error status is %s' % status)
        return ('ShotgunTaskStatus Update Result : Error status is %s' % status)
    if isinstance(task_id, int):
        try:
            result = sg.update('Task', task_id, {'sg_status_list':status})
            print ('ShotgunTaskStatus Update Result : UpdateComplete! %s' % result)
            return result
        except:
            print("ShotgunTaskStatus Update Result ：Error Update Failed")
            return "ShotgunTaskStatus Update Result ：Error Update Failed"

    else:
        print('ShotgunTaskStatus Update Result ：Error Task_id is not interger type')
        return 'ShotgunTaskStatus Update Result ：Error Tasks_id is not interger type'

"""
********************************
Shotgunの情報を登録する（新規作成）
********************************
"""
def create_entity(type, create_dic):
    if isinstance(create_dic, list):
        for create in create_dic:
            create_entity(type, create)
    else:
        return sg.create(type, create_dic)


def shotgun_entity_create(type, create_dic):
    #旧create_entity (使っているツールが無くなれば削除)
    if isinstance(create_dic, list):
        for create in create_dic:
            shotgun_entity_create(type, create)
    else:
        return sg.create(type, create_dic)

def register_timelog(dic, result_list=[]):
    #旧create_entity (使っているツールが無くなれば削除)
    for k, v in dic.items():
        result_list.append(k)

    result = sg.create('TimeLog', dic, result_list)
    return result

def create_note(upload_dic):
    create_result = sg.create("Note", upload_dic, [])
    return create_result

def create_version(upload_dic):
    created_result = sg.create("Version", upload_dic)
    return created_result

def upload_version(version_id, upload_dic):
    movie_path = upload_dic.get("sg_path_to_movie")
    movie_name = os.path.basename(movie_path)
    uploaded_result = sg.upload("Version", version_id, movie_path, "sg_uploaded_movie", movie_name)
    return uploaded_result
    '''
    def upload_version(upload_dic):
    """
    upload_dicの中身の例
    [
      {
        "code": "BAF1_0021_lay_v002",
        "entity": {
          "id": 19832,
          "name": "BAF1_0021",
          "type": "Shot"
        },
        "frame_count": 54,
        "frame_range": "1-54",
        "project": {
          "id": 171,
          "name": "magimajo",
          "type": "Project"
        },
        "sg_first_frame": 1,
        "sg_path_to_movie": "P:/Project/magimajo/shots/EP09/BAF1/0021/review/BAF1_0021_lay_v002/BAF1_0021_lay_v002.mov",
        "sg_task": {
          "id": 34592,
          "name": "shot",
          "type": "Task"
        },
        "type": "Version"
      }
    ]
    """
    created_result = sg.create("Version", upload_dic)
    created_id = created_result.get("id")
    movie_path = upload_dic.get("sg_path_to_movie")
    movie_name = os.path.basename(movie_path)
    #uploaded_result = sg.upload("Version", created_id, movie_path, field_name="sg_uploaded_movie", movie_name)
    uploaded_result = sg.upload("Version", created_id, movie_path, "sg_uploaded_movie", movie_name)
    return [created_result, uploaded_result]'''

def create_snapshot():
    try:
        import sgtk

        # get the current engine (e.g. tk-maya)
        current_engine = sgtk.platform.current_engine()
        if not current_engine:
            print("Shotgun integration is not available!")

        # find the current instance of the snapshot app:
        snapshot_app = current_engine.apps.get("tk-multi-snapshot")
        if not snapshot_app:
            print("The Shotgun Snapshot app is not available!")

        # call the public method on the app to show the snapshot dialog:
        #snapshot_app.show_snapshot_dlg()
        return snapshot_app.snapshot()

    except Exception as e:
        print("Failed to launch Shotgun snapshot! - %s" % e)

def launch_filesave():
    try:
        import sgtk

        # get the current engine (e.g. tk-maya)
        current_engine = sgtk.platform.current_engine()
        if not current_engine:
            print("Shotgun integration is not available!")

        # find the current instance of the snapshot app:
        workfiles_app = current_engine.apps.get("tk-multi-workfiles2")
        if not workfiles_app:
            print("The Shotgun WorkFiles2 app is not available!")

        workfiles_app.show_file_save_dlg()
        # call the public method on the app to show the snapshot dialog:
        #snapshot_app.show_snapshot_dlg()
        #return workfile_app.snapshot()

    except Exception as e:
        print("Failed to launch Shotgun FileSave! - %s" % e)

"""
********************************
Shotgunの情報を削除する
********************************
"""
def delete_entity(entity_type, delete_list):
    for delete_id in delete_list:
        sg.delete("TimeLog", delete_id)


#------------------
#disconnect
sg.close()

#------------------

#------------------------------
#------------------------------
if __name__ == "__main__":
    import ND_lib.util.json_io as json
    #user情報
    user = 'tatsuya sugano'
    #projList = get_proj('ajin')
    #filters = [['code', 'contains', '170329'], ['versions.Version.sg_task.Task.sg_status_list', 'is', 'pub']]


    version_list = get_versions_from_playlists('2017_0706', 'pub')
    print(version_list)
    json._saveJson('E:/temp/test.json', version_list)

    #filters = [['project.Project.name', 'is', 'Franken']]
    #get_tasks_from_assets(filters)
    #result = update_task_status(24608)
    #print result
    sys.exit()


    """
    #project 情報を取得
    #------------------
    filters = [['is_template', 'is', False],['sg_status','is','Active']]
    fields = ['name']
    projDict = sg.find('Project', filters, fields)

    for proj in projDict:
        print '---------------------------------'
        print 'project name', proj['name']
        print '---------------------------------'

        assigneDict = get_assigneDict(proj, user)


        '''
        何度もShotgunへアクセスするのは望ましくないので
        AssetとShotを一括で取得した後にmyTaskで照合する
        '''
        #Assetの処理
        #myTaskごとにAssetを表示する

        assigneDict = get_asset_code(assigneDict, proj)
        print '---------------------------------'

        #Shotの処理
        #myTaskごとにSequenceを表示する
        assigneDict = get_sequence_code(assigneDict, proj)

        for k, v in assigneDict.items():
            print k, v
        print '---------------------------------'
        """
