# -*- coding: utf-8 -*-
import os,sys
from imp import reload
import re
import yaml
import shutil
import distutils.dir_util
# ------------------------------
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)

import ND_lib.util.path as util_path
import ND_lib.env as util_env
import ND_lib.shotgun.sg_scriptkey as sg_scriptkey
import ND_lib.shotgun.shotgun_api3.shotgun as shotgun
import ND_lib.shotgun.sg_util as sg_util
sg = sg_scriptkey.scriptKey()
# ------------------------------
EXPORTER_PATH = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))).replace('\\', '/'))
if EXPORTER_PATH.split('/')[-1] == 'ND_AssetExporter':
    TOOLNAME = 'ND_AssetExporter'
if EXPORTER_PATH.split('/')[-1] == 'ND_AssetExporter_dev':
    TOOLNAME = 'ND_AssetExporter_dev'

# ND_TOOL_PATH = "Y:/tool/ND_Tools/DCC/ND_AssetExporter_dev/pycode"
try:
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGui
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide.QtUiTools import QUiLoader
except:
    # try:
    #     import PySide6.QtCore as QtCore
    #     import PySide6.QtGui as QtGui
    #     from PySide6.QtCore import *
    #     from PySide6.QtGui import *
    #     from PySide6.QtWidgets import *
    #     from PySide6.QtUiTools import QUiLoader
    # except Exception as e:
    import PySide2.QtCore as QtCore
    import PySide2.QtGui as QtGui
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2.QtUiTools import QUiLoader
        

import subprocess
# import shotgun_api3

def symlink(source, link_name):
    import os
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()
            
class outputPathConf(object):
    def __init__(self, input_path, export_type=None, debug=False):
        self.input_path = input_path.replace('\\', '/')
        self.export_type = export_type
        self.debug = debug

        self.root_dir = "charSet"
        if self.export_type=="camera":
            self.root_dir = "Cam"
        if self.debug == True:
            self.root_dir = "test_" + self.root_dir
        dic = util_path.get_path_dic(self.input_path)
        self.pro_name = dic['project_name']
        self.shot = dic['shot']
        self.sequence = dic['sequence']
        self.shot_path = ''
        for path_parts in self.input_path.split('/'):
            self.shot_path = self.shot_path + path_parts+'/'
            if path_parts == self.shot:
                break

    def set_char(self, char):
        self._publish_char_path = os.path.join(self.shot_path, 'publish', self.root_dir, char)
        if self.export_type == "camera":
            self._publish_char_path = os.path.join(self.shot_path, 'publish', self.root_dir)
        if not os.path.exists(self.publish_current_path):
            os.makedirs(self.publish_current_path)
        vers = os.listdir(self.publish_char_path)
        if len(vers) == 1:
            self.current_ver = 'v001'
        else:
            vers.sort()
            current_ver = vers[-1]
            current_ver_num = int(current_ver[1:])
            self.current_ver = 'v' + str(current_ver_num).zfill(3)

    def ver_inc(self):
        vers = os.listdir(self.publish_char_path)
        if len(vers) == 1:
            self.current_ver = 'v001'
        else:
            vers.sort()
            current_ver = vers[-1]
            current_ver_num = int(current_ver[1:])
            next_ver_num = current_ver_num + 1
            next_ver = 'v' + str(next_ver_num).zfill(3)
            self.current_ver = next_ver
        try:
            if not os.path.isdir(self.publish_ver_path):
                os.makedirs(self.publish_ver_path)
                if self.export_type == "anim":
                    if not os.path.isdir(self.publish_ver_anim_path):
                        os.makedirs(self.publish_ver_anim_path)
                elif self.export_type == "abc":
                    if not os.path.isdir(self.publish_ver_abc_path):
                        os.makedirs(self.publish_ver_abc_path)
            # elif export_type == "cam":
            #     os.mkdir(self.publish_ver_cam_path)
        except Exception as e:
            print(e)

    def copy_ver2current(self):
        distutils.dir_util.copy_tree(self.publish_ver_path, self.publish_current_path)
        current_info = os.path.join(self.publish_current_path, 'current_info.txt')
        with open(current_info, 'w') as f:
            f.write("current ver:"+ str(self.current_ver)+"\n")


    def remove_dir(self):
        ver_files = os.listdir(self.publish_ver_path)  # 最新verの検索
        for f in ver_files:
            if '.ma' in f:
                return
        shutil.rmtree(self.publish_ver_path)
        # その後currentの空ならcharから削除
        current_files = os.listdir(self.publish_current_path)
        if len(current_files)==0:
            shutil.rmtree(self.publish_char_path)

    '''
    def set_cache(self, char):
        self.publish_char_path = os.path.join(self.shot_path, 'publish', 'cache', char)
        if os.path.exists(self.publish_char_path):
            self.inc_ver()
        else:
            try:
                os.makedirs(self.publish_char_path)
                self.inc_ver()
            except:
                pass
        try:
            vers = os.listdir(self.publish_char_path)
        except WindowsError as e:
            raise ValueError
        if len(vers) == 0:
            raise ValueError
        else:
            vers.sort()
            self.current_ver = vers[-1]
            if vers[0] > vers[-1]:
                self.current_ver = vers[0]
        self.publish_ver_path = os.path.join(self.publish_char_path, self.current_ver)
        self.publish_ver_abc_path = os.path.join(self.publish_ver_path, 'abc')
        self.publish_ver_anim_path = os.path.join(self.publish_ver_path, 'anim')
        self.publish_ver_cam_path = os.path.join(self.publish_ver_path, 'cam')
        self.publish_current_path = os.path.join(self.publish_char_path, 'current')      
    '''
        
    def overrideShotpath(self, shotpath):
        self.shot_path = shotpath.replace('\\', '/')

    @property
    def publish_char_path(self):
        return self._publish_char_path.replace(os.path.sep, '/')

    @property
    def publish_ver_path(self):
        self._publish_ver_path = os.path.join(self.publish_char_path, self.current_ver)
        return self._publish_ver_path.replace(os.path.sep, '/')

    @property
    def publish_ver_abc_path (self):
        self._publish_ver_abc_path = os.path.join(self.publish_ver_path, 'abc')
        return self._publish_ver_abc_path.replace(os.path.sep, '/')

    @property
    def publish_ver_anim_path (self):
        self._publish_ver_anim_path = os.path.join(self.publish_ver_path, 'anim')
        return self._publish_ver_anim_path.replace(os.path.sep, '/') 

    @property
    def publish_ver_cam_path (self):
        self._publish_ver_cam_path = os.path.join(self.publish_ver_path, 'cam')
        return self._publish_ver_cam_path.replace(os.path.sep, '/')

    @property
    def publish_current_path (self):
        self._publish_current_path = os.path.join(self.publish_char_path, 'current')
        return self._publish_current_path.replace(os.path.sep, '/')

    @property
    def publish_current_anim_path (self):
        self._publish_current_anim_path = os.path.join(self.publish_current_path, 'anim')
        return self._publish_current_anim_path.replace(os.path.sep, '/')

    @property
    def publish_current_abc_path (self):
        self._publish_current_abc_path = os.path.join(self.publish_current_path, 'abc')
        return self._publish_current_abc_path.replace(os.path.sep, '/')        

    @property
    def publish_current_cam_path(self):
        self.publish_current_cam_path = os.path.join(self.publish_current_path, 'cam')
        return self._publish_current_cam_path.replace(os.path.sep, '/')


    def addTimeLog(self):
        from datetime import datetime
        try:
            with open(os.path.join(self.publish_char_path, 'timelog.txt'), 'a') as f:
                f.write(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                f.write(' ' + self.current_ver)
                f.write(' ' + self.input_path)
                f.write(' ' + os.environ['USERNAME'])
                f.write('\n')
        except Exception as e:
            print(e)
    
    ''' 
        #publish_char_path         = ...publish/char_set/{char_name}
        #publish_ver_path          = ...publish/char_set/{char_name}/{ver}
        #publish_ver_abc_path      = ...publish/char_set/{char_name}/{ver}    /abc
        #publish_ver_anim_path     = ...publish/char_set/{char_name}/{ver}    /anim
        #publish_ver_cam_path      = ...publish/char_set/{char_name}/{ver}    /cam
        #publish_current_path      = ...publish/char_set/{char_name}/current
        #publish_current_abc_path  = ...publish/char_set/{char_name}/current  /abc
        #publish_current_anim_path = ...publish/char_set/{char_name}/current  /anim
        #publish_current_cam_path  = ...publish/char_set/{char_name}/current  /cam    
    '''

class ProjectInfo():
    def __init__(self, url):
        import ND_lib.util.path as util_path
        url_parsedict = util_path.get_path_dic(url)
        self.path = url_parsedict['path']
        self.path_type = url_parsedict['path_type']
        self.project_name = url_parsedict['project_name']
        self.shot = url_parsedict['shot']
        self.sequence = url_parsedict['sequence']
        self.shot_code = url_parsedict['shot_code']

    def get_camera_rig_info(self):
        project_conf = util_path.get_conf_dic(self.project_name.lower())
        try:
            self.camera_rig_export = (
                project_conf.get("preferences").get("camera_rig_export")
            )
        except AttributeError:
            self.camera_rig_export = False
        return self.camera_rig_export

class DeadlineMod():
    def __init__(self, **kwargs):
        #jobFile
        self.target_py = "Y:/tool/ND_Tools/DCC/{}/pycode/back_starter.py".format(TOOLNAME)
        #infoFile
        self.argsdict = kwargs
        # self.executer = r"C:\Users\k_ueda\AppData\Local\Programs\Python\Python310\python.exe"
        self.executer = 'Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe'
        self.stg_dir = "Y:/tool/ND_Tools/DCC/{}/pycode".format(TOOLNAME)
        self.tmp_dir = os.environ.get('TEMP', 'E:/TEMP')
        self.job_dict = self.job_content()
        self.info_dict = self.info_content()

    def job_content(self):
        job_dict = {}
        job_dict["Frames"] = 1
        job_dict["Group"] = self.argsdict['group']
        job_dict["MachineName"] = os.environ.get("COMPUTERNAME")
        job_dict["Name"] = "ND_AssetExporter_{pool}_{shot}{sequence}_{asset_name}".format(**self.argsdict) # シーンの情報を入れる
        job_dict["OverrideTaskExtraInfoNames"] = False
        job_dict["Plugin"] = "CommandLine"
        job_dict["Pool"] = self.argsdict['pool']
        job_dict["Priority"] = str(self.argsdict['priority'])
        job_dict["SecondaryPool"] = "normal"
        job_dict["UserName"] = os.environ.get("USERNAME")
        # job_dict["Whitelist"] = "ws023"
        job_dict["BatchName"] = "Exporter_{pool}_{shot}{sequence}".format(**self.argsdict)
        return job_dict

    def info_content(self):
        info_dict = {}
        info_dict["Arguments"] = self.target_py + ' ' + str(self.argsdict)
        info_dict["Executable"] = self.executer
        info_dict["Shell"] = "default"
        info_dict["ShellExecute"] = False
        info_dict["SingleFramesOnly"] = False
        info_dict["StartupDirectory"] = self.stg_dir

        return info_dict

    def file_maker(self, file_type, file_number):
        import codecs
        file_txt = ''
        target_dict = {}
        if file_type == 'job':
            target_dict = self.job_dict
        elif file_type == 'info':
            target_dict = self.info_dict
        for key,value in target_dict.items():
            file_txt += '{}={}\r'.format(key, value)
        deadline_tmpfile = r'{}\ND_AssetExporter_deadline_{}_{}.job'.format(self.tmp_dir, file_type, file_number)
        with codecs.open(deadline_tmpfile, 'w', 'utf-8') as output_file:
            output_file.write(file_txt)
        return deadline_tmpfile

    def make_submit_files(self, file_number, farm="Deadline", version="10"):
        job_file = self.file_maker('job', file_number)
        info_file = self.file_maker('info', file_number)
        tmp_dict = {}
        tmp_dict["job"] = job_file
        tmp_dict["info"] = info_file
        return tmp_dict

    def submit_to_deadlineJob(self, farm="Deadline", version="10", file_number=1):
        import subprocess
        job_file = self.file_maker('job', file_number)
        info_file = self.file_maker('info', file_number)
        if farm == "Deadline":
            deadline_cmd = r"{}\bin\deadlinecommand.exe".format(util_env.deadline_path)
        jobid = ""
        command = '{deadline_cmd} "{job_file}" "{info_file}"'.format(**vars())
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        lines_iterator = iter(process.stdout.readline, b"")
        for line in lines_iterator:
            if 'JobID' in line:
                jobid = line.replace('JobID=', '')
            sys.stdout.flush()
        return jobid


def submit_to_deadlineJobs(jobs, farm="Deadline", version="10"):
    arg_file_path = '{}/args.txt'.format(util_env.env_temp)
    submit_text = "-SubmitMultipleJobs"
    for job in jobs:
        submit_text = "{}\n-job\n{}\n{}".format(submit_text, job["job"], job["info"])
    f = open(arg_file_path, "w")
    f.write(submit_text)
    f.close()
    deadline_cmd = r"{}\bin\deadlinecommand.exe".format(util_env.deadline_path)
    command = '{deadline_cmd} {arg_file_path}'.format(**vars())
    devnull = open(os.devnull, "wb")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=devnull)
    lines_iterator = iter(process.stdout.readline, b"")
    return lines_iterator


class ExporterTableModel(QAbstractTableModel):
    def __init__(
            self, table_data, headers=[],
            check_row=[], executed_row=[],
            parent=None):

        QAbstractTableModel.__init__(self, parent)
        self.check_row = check_row
        self.table_data = table_data
        self.headers = headers
        self.executed_row = executed_row

    def rowCount(self, parent):
        return len(self.table_data)

    def columnCount(self, parent):
        return len(self.table_data[0])

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role=Qt.BackgroundRole):
        row = index.row()
        column = index.column()

        if role == Qt.EditRole:
            return self.table_data[row][column]
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == 0:
                if row in self.executed_row:
                    x = "◎"
                    try:
                        value = x.decode("utf-8", errors="ignore")
                    except:
                        value = x
                else:
                    if row in self.check_row:
                        x = "◎"
                        try:
                            value = x.decode("utf-8", errors="ignore")
                        except:
                            value = x
                    else:
                        value = self.table_data[row][column]
            else:
                try:
                    value = self.table_data[row][column]
                except:
                    value = ""
            return value

        elif role == Qt.BackgroundRole:
            if "{Empty!}" in self.table_data[row]:
                return QColor("#AA0000")
            if row in self.executed_row:
                return QColor("#BBBBBB")
            else:
                if row in self.check_row:
                    return QColor("#226666")
                else:
                    return QColor("#888888")

    def setData(self, index, value, role=Qt.DisplayRole):
        row = index.row()
        column = index.column()
        if role == Qt.EditRole:
            self.table_data[row][column] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.headers):
                    return self.headers[section]
                else:
                    return "not implemented"
            else:
                return "%d" % (section + 1)


def tabledata_builder(headers, convert_dic, target_assets):
    '''
    SGからきたasset_dicを表示用の二次元配列に直す
    convert_dic: ヘッダーとcodesの対応表
    target_asset: targetassetのdicのリスト
    '''
    tabledata = []
    for target_asset in target_assets:
        td_row = ['']
        for header in headers:
            if header != 'Export Item':
                sg_code = convert_dic[header]
                if sg_code == 'sg_export_type':
                    if target_asset[sg_code] == 'anim':
                        td_row.append("anim")
                        sg_code = 'sg_anim_export_list'
                    elif target_asset[sg_code] == 'abc':
                        td_row.append("abc")
                        sg_code = 'sg_abc_export_list'
                    elif target_asset[sg_code] == 'abc_anim':
                        td_row.append("abc_anim")
                        anim_item = target_asset["sg_anim_export_list"]
                        abc_item = target_asset["sg_abc_export_list"]
                        # td_row.append("{{anim:{}, abc:{}}})".format(anim_item, abc_item))
                        export_item_dic = {}
                        export_item_dic['anim']=anim_item
                        export_item_dic['abc'] =abc_item
                        td_row.append(yaml.safe_dump(export_item_dic))
                        continue
                    else:
                        td_row.append('{Empty!}')
                        # td_row.append('{Empty!}')
                    anim_item = target_asset["sg_anim_export_list"]
                    abc_item = target_asset["sg_abc_export_list"]
                    # td_row.append("{{anim:{}, abc:{}}})".format(anim_item, abc_item))
                    export_item_dic = {}
                    export_item_dic['anim']=anim_item
                    export_item_dic['abc'] =abc_item
                    td_row.append(yaml.safe_dump(export_item_dic))
                    # td_row.append("{{anim:{}, abc:{}}}".format(anim_item, abc_item))
                    continue
                if target_asset[sg_code] is None:
                    td_row.append("{Empty!}")
                else:
                    td_row.append(target_asset[sg_code].replace("\n", ""))

        tabledata.append(td_row)
    return tabledata

def add_camera_row(headers_item, tabledata, camera_rig_export):
    if camera_rig_export == 'True':
        pass
    else:
        td_row = ['']
        for header in headers_item:
            if header == 'Asset name':
                td_row.append('Camera')
            elif header == 'Export Type':
                td_row.append('camera')
            else:
                td_row.append('')
        tabledata.append(td_row)
    return tabledata

def execExporter_maya(**kwargs):
    import back_starter
    reload(back_starter)
    back_starter.back_starter(kwargs=kwargs["kwargs"])

def is_arnold(project):
    import yaml
    project_name = project
    toolkit_path = "Y:\\tool\\ND_Tools\\shotgun"
    app_launcher_path = "config\\env\\includes\\app_launchers.yml"
    project_app_launcher = "%s\\ND_sgtoolkit_%s\\%s" % (toolkit_path, project_name, app_launcher_path)
    f = open(project_app_launcher, "r")
    data = yaml.load(f)
    f.close()
    for version in data["launch_maya"]["versions"]:
        if "(_MtoA_)" in version:
            return True
    return False


class SGProjectClass(object):
    def __init__(self, project, field_codes):
        self.SGFieldDict = {} 
        self.project_name = project
        self.project_code = sg_util.get_project(project)
        self.filters = [["project", "is", self.project_code]]
        if field_codes == None:
            self.field_codes = ["code"]
        else:
            self.field_codes = field_codes

    def get_dict(self, category):
        try:
            field_dict = sg.find(category, self.filters, self.field_codes)
        except shotgun.Fault:
            raise ValueError('Coudn\'t get from Shotgun....')
        self.SGFieldDict[category] = field_dict
        return field_dict

    def sg_write(self, category, attribute_name, field_code, new_data):
        item_id = self.codekeyed_dict[attribute_name]['id']
        sg.update(category, item_id, {field_code: new_data})

    def get_keying_dict(self, category, priority_field):
        '''
        特定のコードをキーに格納
        '''
        two_fold_dict = {}
        for dict_piece in self.SGFieldDict[category]:
            pri_item = dict_piece[priority_field]
            two_fold_dict[pri_item] = dict_piece
        return two_fold_dict

    def get_keying_list(self, category, target_field, topic_item):
        '''
        特定のキー:アイテムのリストを返す(重複がありうるので)
        '''
        sp_ls = []
        for dict_piece in self.SGFieldDict[category]:
            pri_item = dict_piece[target_field]
            if pri_item == topic_item:
                sp_ls.append(dict_piece)
        return sp_ls


if __name__ == '__main__':
    py_file = sys.argv[0] 
    argsdic = yaml.safe_load(sys.argv[1])
    execExporter(argsdic)
    sys.exit()
