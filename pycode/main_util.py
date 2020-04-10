# -*- coding: utf-8 -*-
import os,sys

# ------------------------------
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)
# ------------------------------------

# sys.path.append('C:/Users/k_ueda/Desktop/ND_AssetExporter_v03/pycode')  #ツールの場所

import ND_lib.shotgun.sg_util as sg_util
import ND_lib.util.path as util_path
import ND_lib.env as util_env
import shotgun_mod as sg_mod
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
from PySide.QtCore import Qt as Qt
from PySide.QtCore import QAbstractTableModel as QAbstractTableModel
import subprocess

pythonBatch = 'Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe'

class ProjectInfo():
    def __init__(self, url):
        import ND_lib.util.path as util_path
        url_parsedict = util_path.get_path_dic(url)
        import pprint
        pprint.pprint(url_parsedict.items())
        self.path = url_parsedict['path']
        self.path_type = url_parsedict['path_type']
        self.project_name = url_parsedict['project_name']
        # self.roll = url_parsedict['roll']
        self.shot = url_parsedict['shot']
        self.sequence = url_parsedict['sequence']
        self.shot_code = url_parsedict['shot_code']

    def get_camera_rig_info(self):
        project_conf = util_path.get_conf_dic(self.project_name.lower())
        self.camera_rig_export = (
            project_conf.get("preferences").get("camera_rig_export")
        )
        return self.camera_rig_export


class TableModelMaker(QAbstractTableModel):
    '''
        GUI.settableに入れるデータを作成するクラス
        テーブルデータ(二次元リスト),ヘッダー(list),
    '''
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

    def data(self, index, role=QtCore.Qt.BackgroundRole):
        row = index.row()
        column = index.column()

        if role == Qt.EditRole:
            return self.table_data[row][column]
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == 0:
                if row in self.executed_row:
                    x = "✔"
                    value = x.decode("utf-8", errors="ignore")
                else:
                    if row in self.check_row:
                        x = "◎"
                        value = x.decode("utf-8", errors="ignore")
                    else:
                        value = self.table_data[row][column]
            else:
                try:
                    value = self.table_data[row][column]
                except:
                    value = ""
            return value

        elif role == QtCore.Qt.BackgroundRole:
            if "{Empty!}" in self.table_data[row]:
                return QtGui.QColor("#AA0000")
            if row in self.executed_row:
                return QtGui.QColor("#BBBBBB")
            else:
                if row in self.check_row:
                    return QtGui.QColor("#226666")
                else:
                    return QtGui.QColor("#888888")

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
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
# ここまでTableModel用 ###


def tabledata_maker(headers, convert_dic, target_assets):
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
                    else:
                        td_row.append('{Empty!}')
                        td_row.append('{Empty!}')
                        break
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


def argsmaker(new_arg, args=None):
    if not args:
        return new_arg
    else:
        return args + ' ' + new_arg


def execExporter(**kwargs):
    progress = 5
    print("Progress: {}%".format(progress))

    args = argsmaker(pythonBatch)
    args = argsmaker('back_starter.py', args)
    args = argsmaker(str(kwargs), args)

    subprocess.call(args)

def spsymbol_remover(litteral, itemtype):
    import re
    if itemtype == 'key':
        litteral = re.sub(',| |:|\'|{|}', '', litteral)
        litteral = litteral.rstrip(',')
    elif itemtype == 'value':
        litteral = litteral.rstrip(',')
        litteral = re.sub(' |\'|{|}', '', litteral)
    return litteral

def dictlist_parse(dictlist):
    '''
    受け取ったdictだったリストを再度dictに変換
    '''
    argsdict = {}
    for dictparts in dictlist:
        if dictparts[-1] == ':':
            key = spsymbol_remover(dictparts, 'key')
        else:
            value = spsymbol_remover(dictparts, 'value')
            argsdict[key] = value
            print key, value
    return argsdict

class DeadlineMod():
    def __init__(self, **kwargs):
        #jobFile
        self.target_py = "Y:/users/env/Tools/ND_AssetExporter/pycode/main_util.py"

        #infoFile
        self.argsdict = kwargs

        self.executer = "Y:/tool/MISC/Python2710_amd64_vs2010/python.exe"
        self.stg_dir = "Y:/users/env/Tools/ND_AssetExporter/pycode"
        self.tmp_dir = os.environ.get('TEMP', 'E:/TEMP')

        self.job_dict = self.job_content()
        self.info_dict = self.info_content()

    def job_content(self):
        job_dict = {}
        job_dict["Frames"] = 1
        job_dict["Group"] = self.argsdict['Group']
        job_dict["MachineName"] = os.environ.get("COMPUTERNAME")
        job_dict["Name"] = "ND_AssetExporter_{Pool}_{shot}{sequence}_{chara}".format(**self.argsdict) # シーンの情報を入れる
        job_dict["OverrideTaskExtraInfoNames"] = False
        job_dict["Plugin"] = "CommandLine"
        job_dict["Pool"] = self.argsdict['Pool']
        job_dict["Priority"] = str(self.argsdict['Priority'])
        job_dict["SecondaryPool"] = "normal"
        job_dict["UserName"] = os.environ.get("USERNAME")
        # job_dict["Whitelist"] = "ws023"
        job_dict["BatchName"] = "Exporter_{Pool}_{shot}{sequence}".format(**self.argsdict)

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

        #numberを取得する必要がある？
        #numberは文字列

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
        '''
        使わない...?
        '''
        import subprocess

        job_file = self.file_maker('job', file_number)
        info_file = self.file_maker('info', file_number)

        if farm == "Deadline":
            deadline_cmd = r"{}\bin\deadlinecommand.exe".format(util_env.deadline_path)

        jobid = ""
        command = '{deadline_cmd} "{job_file}" "{info_file}"'.format(**vars())
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        lines_iterator = iter(process.stdout.readline, b"")
        print lines_iterator
        for line in lines_iterator:
            print(line)
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

if __name__ == '__main__':
    import sys
    import subprocess
    setting_bat = r"Y:\users\env\Tools\ND_AssetExporter\pycode\__env__.bat"
    subprocess.call(setting_bat)
    _strargv = sys.argv
    _strargv.pop(0)
    argsdict = dictlist_parse(_strargv)
    execExporter(**argsdict)
