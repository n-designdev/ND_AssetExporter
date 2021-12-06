# -*- coding: utf-8 -*-
import os,sys
import ast
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
# ------------------------------------

# import ND_lib.shotgun.sg_util as sg_util
import exporter_lib.sg_util as sg_util
import exporter_lib.path as util_path
import exporter_lib.env as util_env
try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtWidgets import *
except:
    import PySide6.QtCore as QtCore
    import PySide6.QtGui as QtGui
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtUiTools import QUiLoader
import subprocess
# import shotgun_api3

pythonBatch = 'Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe'

class ProjectInfo():
    def __init__(self, url):
        import exporter_lib.path as util_path
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


class TableModelMaker(QAbstractTableModel):
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
                    x = "✔"
                    value = x
                else:
                    if row in self.check_row:
                        x = "◎"
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
                    elif target_asset[sg_code] == 'abc_anim':
                        td_row.append("abc_anim")
                        anim_item = target_asset["sg_anim_export_list"]
                        abc_item = target_asset["sg_abc_export_list"]
                        td_row.append("{{anim:{}, abc:{}}})".format(anim_item, abc_item))
                        continue
                    else:
                        td_row.append('{Empty!}')
                        td_row.append('{Empty!}')
                    anim_item = target_asset["sg_anim_export_list"]
                    abc_item = target_asset["sg_abc_export_list"]
                    td_row.append("{{anim:{}, abc:{}}})".format(anim_item, abc_item))
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


def argsmaker(new_arg, args=None):
    if not args:
        return new_arg
    else:
        return args + ' ' + new_arg


def execExporter(**kwargs):
    args = argsmaker(pythonBatch)
    args = argsmaker('back_starter.py', args)
    args = argsmaker(str(kwargs), args)
    subprocess.call(args, shell=True)


def execExporter_maya(**kwargs):
    import back_starter
    reload(back_starter)
    back_starter.back_starter(kwargs=kwargs["kwargs"])


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
    return argsdict


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

class DeadlineMod():
    def __init__(self, **kwargs):
        #jobFile
        self.target_py = "Y:/tool/ND_Tools/DCC/ND_AssetExporter/pycode/main_util.py"
        #infoFile
        self.argsdict = kwargs
        self.executer = "Y:/tool/MISC/Python2710_amd64_vs2010/python.exe"
        self.stg_dir = "Y:/tool/ND_Tools/DCC/ND_AssetExporter/pycode"
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


class outputPathConf(object):
    def __init__(self, input_path, isAnim=False, debug=False):
        self.input_path = input_path.replace('\\', '/')
        self.isAnim = isAnim
        self.outputRootDir = 'charSet'
        self.outputCamRootDir = 'Cam'
        if debug == 'True':
            self.outputRootDir = 'test_charSet'
            self.outputCamRootDir = 'test_Cam'
        dic = util_path.get_path_dic(self.input_path)
        self._pro_name = dic['project_name']
        self._shot = dic['shot']
        self._sequence = dic['sequence']
        self._shotpath = ''
        for path_parts in self.input_path.split('/'):
            self._shotpath = self._shotpath + path_parts+'/'
            if path_parts == self._shot:
                break

    def createOutputDir(self, char):
        self._publishpath = os.path.join(self._shotpath+'publish', self.outputRootDir, char)
        if os.path.exists(self._publishpath):
            self.verInc()
        else:
            try:
                os.makedirs(self._publishpath)
                self.verInc()
            except:
                pass

    def createCamOutputDir(self):
        self._publishpath = os.path.join(self._shotpath, 'publish', self.outputCamRootDir)
        if os.path.exists(self._publishpath):
            self.verInc(True)
        else:
            try:
                os.makedirs(self._publishpath)
                self.verInc(True)
            except:
                pass

    def verInc(self, isCam=False):
        vers = os.listdir(self._publishpath)
        if len(vers) == 0:
            self._currentVer = 'v001'
        else:
            vers.sort()
            currentVer = vers[-1]
            currentVerNum = int(currentVer[1:])
            nextVerNum = currentVerNum + 1
            nextVer = 'v' + str(nextVerNum).zfill(3)
            self._currentVer = nextVer
        self._publishfullpath = os.path.join(self._publishpath, self._currentVer)
        self._publishfullabcpath = os.path.join(self._publishfullpath, 'abc')
        self._publishfullanimpath = os.path.join(self._publishfullpath, 'anim')
        self._publishfullcampath = os.path.join(self._publishfullpath,'cam')
        try:
            os.mkdir(self._publishfullpath)
            if isCam == True:
                os.mkdir(self._publishfullcampath)
            elif self.isAnim:
                os.mkdir(self._publishfullanimpath)
            else:
                os.mkdir(self._publishfullabcpath)
        except Exception as e:
            print(isCam, self.isAnim)
            print(e)

    def makeCurrentDir(self):
        currentDir = os.path.join(self.publishpath, 'current')
        self._publishcurrentpath = currentDir
        distutils.dir_util.copy_tree(self._publishfullpath, currentDir)
        current_info = os.path.join(currentDir, 'current_info.txt')
        with open(current_info, 'w') as f:
            f.write("current ver:"+ str(self._currentVer)+"\n")

    def removeDir(self):
        if os.path.exists(self._publishpath+'\\current'):
            files = os.listdir(self._publishpath+'\\current')
            for f in files:
                if '.ma' in f:
                    return
        shutil.rmtree(self._publishpath)

    def setChar(self, char):
        if char == 'Cam' or char == 'Camera':
            self._publishpath = os.path.join(self._shotpath, 'publish', self.outputCamRootDir).replace('/', '\\')
        else:
            self._publishpath = os.path.join(self._shotpath, 'publish', self.outputRootDir, char).replace('/', '\\')
        try:
            vers = os.listdir(self._publishpath)
        except WindowsError as e:
            raise ValueError
        if len(vers) == 0:
            raise ValueError
        vers.sort()
        self._currentVer = vers[-1]
        if vers[0] > vers[-1]:
            self._currentVer = vers[0]
        self._publishfullpath = os.path.join(self._publishpath, self._currentVer)
        self._publishfullabcpath = os.path.join(self._publishfullpath, 'abc')
        self._publishfullanimpath = os.path.join(self._publishfullpath, 'anim')
        self._publishfullcampath = os.path.join(self._publishfullpath, 'cam')
        self._publishcurrentpath = self._publishpath+'\\current'

    def setCache(self, char):
        self._publishpath = os.path.join(self._shotpath, 'publish', 'cache', char).replace('/', '\\')
        if os.path.exists(self._publishpath):
            self.verInc()
        else:
            try:
                os.makedirs(self._publishpath)
                self.verInc()
            except:
                pass
        try:
            vers = os.listdir(self._publishpath)
        except WindowsError as e:
            raise ValueError
        if len(vers) == 0:
            raise ValueError
        vers.sort()
        self._currentVer = vers[-1]
        if vers[0] > vers[-1]:
            self._currentVer = vers[0]
        self._publishfullpath = os.path.join(self._publishpath, self._currentVer)
        self._publishfullabcpath = os.path.join(self._publishfullpath, 'abc')
        self._publishfullanimpath = os.path.join(self._publishfullpath, 'anim')
        self._publishfullcampath = os.path.join(self._publishfullpath, 'cam')
        self._publishcurrentpath = os.path.join(self._publishpath, 'current')      

    
    def setDebug(self):
        self._publishfullpath = self._publishfullpath.replace('charSet', 'test_charSet')
        self._publishfullabcpath = self._publishfullabcpath.replace('charSet', 'test_charSet')
        self._publishfullanimpath = self._publishfullanimpath.replace('charSet', 'test_charSet')
        self._publishfullcampath = self._publishfullcampath.replace('charSet', 'test_charSet')
        self._publishcurrentpath = self._publishcurrentpath.replace('charSet', 'test_charSet')
        
    @property
    def sequence (self):
        return self._sequence

    @property
    def shot (self):
        return self._shot

    @property
    def publishpath (self):
        return self._publishpath.replace(os.path.sep, '/')

    @property
    def publishfullpath (self):
        return self._publishfullpath.replace(os.path.sep, '/')

    @property
    def publishfullabcpath (self):
        return self._publishfullabcpath.replace(os.path.sep, '/')

    @property
    def publishfullanimpath (self):
        return self._publishfullanimpath.replace(os.path.sep, '/')

    @property
    def publishcurrentpath (self):
        return self._publishcurrentpath.replace(os.path.sep, '/')

    @property
    def publishfullcampath(self):
        return self._publishfullcampath.replace(os.path.sep, '/')

    @property
    def publishshotpath(self):
        return self._shotpath.replace(os.path.sep, '/')

    @property
    def currentVer (self):
        return self._currentVer


def addTimeLog(char, input_path, debug):
    from datetime import datetime
    opc = outputPathConf(input_path, char, debug)
    print("#####addTimeLog#####")
    print("chara: {}".format(char))
    print("input_path: {}".format(input_path))
    try:
        opc.setChar(char)
    except ValueError:
        print("AddTimeLog Error!!")
        return
    publishpath = opc.publishpath
    if debug is True:
        publishpath = publishpath.replace("char", "test_char")
        publishpath = publishpath.replace("Cam", "test_Cam")
    with open(os.path.join(publishpath, 'timelog.txt').replace(os.path.sep, '/'), 'a') as f:
        f.write(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        f.write(' ' + opc.currentVer)
        f.write(' ' + input_path)
        f.write(' ' + os.environ['USERNAME'])
        f.write('\n')

if __name__ == '__main__':
    import sys
    import subprocess
    _strargv = sys.argv
    _strargv.pop(0)
    try:
        argsdict = ast.literal_eval(_strargv[0])
    except:
        argsdict = dictlist_parse(_strargv)
    execExporter(**argsdict)
    sys.exit()
