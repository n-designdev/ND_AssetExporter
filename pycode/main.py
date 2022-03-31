# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import time
import importlib
import yaml
try:
    from importlib import reload
except:
    pass
# ------------------------------
__version__ = '2.2'
__author__ = 'Kei Ueda'
# ------------------------------
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = 'Y:/tool/ND_Tools/python;Y:/tool/ND_Tools/DCC/ND_AssetExport_test/pycode/exporter_lib'
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)
# ------------------------------
import datetime
import subprocess
import threading
import json

# import ND_lib.shotgun.sg_scriptkey as sg_scriptkey
# sg = sg_scriptkey.scriptKey()
try:
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGui
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide.QtUiTools import QUiLoader
except ModuleNotFoundError:
    import PySide6.QtCore as QtCore
    import PySide6.QtGui as QtGui
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
    from PySide6.QtUiTools import QUiLoader
# ------------------------------------

import main_util; reload(main_util)
import shotgun_mod; reload(shotgun_mod)
import util; reload(util)
try:
    import ND_Submitter.env as util_env
    # import ND_Submitter2.env as util_env
except Exception as e:
    print(e)
    NoDeadlineMode = True
else:
    NoDeadlineMode = False

# PYPATH = r'C:\Users\k_ueda\AppData\Local\Programs\Python\Python310\python.exe'
PYPATH = 'Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe'
onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
os.chdir(onpath)

class GUI(QMainWindow):

    WINDOW = 'ND_AssetExporter'
    
    def __init__(self, parent=None, qApp=None):
        super(self.__class__, self).__init__(parent)
        self.debug = False
        self.ui_path = '.\\gui\\exporter_gui.ui'
        self.ui = QUiLoader().load(self.ui_path)
        self.setCentralWidget(self.ui)
        self.setGeometry(500, 200, 1000, 800)
        self.setWindowTitle('%s %s' % (self.WINDOW, __version__))

        self.input_path = ''
        #Shotgrid
        self.asset_fields = [
                'code', 'sg_namespace', 'sg_export_type',
                'sg_top_node', 'sg_abc_export_list',
                'sg_anim_export_list', 'sg_asset_path',
                'sequences']
        self.shot_fields = ['code', 'assets']
        self.base_fields = [
                'code', 'assets',
                'sg_namespace', 'sg_export_type',
                'sg_top_node', 'sg_abc_export_list',
                'sg_anim_export_list', 'sg_asset_path',
                'sequences']
        # GUI
        self.headers_item = [
                'Asset name', 'Name space', 
                'Export Type', 'Export Item',
                'Top Node', 'Asset Path']
        self.convert_dic = {
                'Asset name': 'code',
                'Name space': 'sg_namespace',
                'Export Type': 'sg_export_type',
                'Top Node': 'sg_top_node',
                'Asset Path': 'sg_asset_path'}
        self.headers = ['']
        self.headers.extend(self.headers_item)

        self.tabledata = []
        self.check_row = []
        self.executed_row = []

        self.priority = 50
        self.group = '16gb'

        self.selected_item = None

        self.ui.dd_area.installEventFilter(self)
        self.ui.main_table.clicked.connect(self.main_table_clicked)
        self.ui.main_table.doubleClicked.connect(self.main_table_doubleClicked)

        self.ui.debug_chk.stateChanged.connect(self.debug_chk_stateChange)

        self.ui.cam_scale_override_chk.stateChanged.connect(self.cam_scale_override_chk_stateChange)
        self.ui.abc_step_override_chk.stateChanged.connect(self.abc_step_override_chk_stateChange)

        self.ui.custom_frame_range_chk.clicked.connect(self.custom_frame_range_chk)
        self.ui.frame_handle_chk.clicked.connect(self.frame_handle_chk_clicked)

        self.ui.open_log_button.clicked.connect(self.open_log_button_clicked)
        self.ui.current_refresh_button.clicked.connect(self.current_refresh_button_clicked)
        self.ui.open_publish_dir_button.clicked.connect(self.open_publish_dir_button_clicked)
        self.ui.help_button.clicked.connect(self.help_button_clicked)
        self.ui.restore_last_file_button.clicked.connect(self.load_user_info)

        self.ui.check_selected_btn.clicked.connect(self.check_selected_btn_clicked)
        self.ui.uncheck_selected_btn.clicked.connect(self.uncheck_selected_btn_clicked)
        self.ui.allcheck_btn.clicked.connect(self.allcheck_btn_clicked)
        self.ui.alluncheck_btn.clicked.connect(self.alluncheck_btn_clicked)

        self.ui.export_local_btn.clicked.connect(self.export_local_btn_clicked)
        self.ui.export_submit_btn.clicked.connect(self.export_submit_btn_clicked)


    def debug_chk_stateChange(self):
        self.debug = self.ui.debug_chk.isChecked()

    def camscale_override_chk_stateChange(self):
        state = self.ui.abc_step_override_chk.isChecked()
        self.ui.stepValue_LineEdit.setEnabled(state)

    def abc_step_override_chk_stateChange(self):
        state = self.ui.abc_step_override_chk.isChecked()
        self.ui.stepValue_lineEdit.setEnabled(state)

    def check_selected_btn_clicked(self):
        for selected_row in self.ui.main_table.selectedIndexes():
            self.check_row.append(selected_row.row())
        self.check_row = list(set(self.check_row))
        model = main_util.TableModelMaker(
            self.tabledata, self.headers,
            self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def uncheck_selected_btn_clicked(self):
        selected_index = []
        for selected_row in self.ui.main_table.selectedIndexes():
            selected_index.append(selected_row.row())
        selected_index = list(set(selected_index))
        for _index in selected_index:
            try:
                self.check_row.remove(_index)
            except:
                pass
        model = main_util.TableModelMaker(
                self.tabledata, self.headers,
                self.check_row)
        self.ui.main_table.setModel(model)

    def allcheck_btn_clicked(self):
        self.check_row = list(range(len(self.tabledata)))
        model = main_util.TableModelMaker(
                self.tabledata, self.headers,
                self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def alluncheck_btn_clicked(self):
        self.check_row = []
        model = main_util.TableModelMaker(
                self.tabledata, self.headers,
                self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def frame_handle_chk_clicked(self):
        self.ui.frame_handle_value.setEnabled(
            self.ui.frame_handle_chk.isChecked())

    def custom_frame_range_chk(self):
        state = self.ui.custom_frame_range_chk.isChecked()
        self.ui.sFrame.setEnabled(state)
        self.ui.eFrame.setEnabled(state)

    def cam_scale_override_chk_stateChange(self):
        currentState = self.ui.camscale_override_chk.isChecked()
        self.ui.overrideValue_LineEdit.setEnabled(currentState)

    def export_local_btn_clicked(self):
        print('local')
        self.export_main(mode='Local')

    def export_submit_btn_clicked(self):
        print('Submit')
        self.export_main(mode='Submit')

    def open_log_button_clicked(self):
        sakura = r'C:\Program Files (x86)\sakura\sakura.exe'
        subprocess.Popen([sakura, self.last_log_path])

    def contextMenu(self, point):
        print(point)

    def eventFilter(self, object, event):
        if event.type() == QEvent.DragEnter:
            event.acceptProposedAction()
        if event.type() == QEvent.Drop:
            mimedata = event.mimeData()
            urldata = mimedata.urls()
            self.drop_func(urldata)
        return True


    def main_table_clicked(self):
        if self.selected_item != None:
            self.ui.main_table.closePersistentEditor(self.selected_item)
            self.selected_item = None

    def main_table_doubleClicked(self):
        clicked_row = self.ui.main_table.selectedIndexes()[0].row()
        check_rows = self.check_row
        if clicked_row in check_rows[:]:
            check_rows.remove(clicked_row)
        else:
            check_rows.append(clicked_row)
        self.check_row = list(set(check_rows))
        model = main_util.TableModelMaker(
            self.tabledata, self.headers, self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def main_table_rclicked(self):
        self.selected_item = self.ui.main_table.selectedIndexes()[0]
        _row = self.selected_item.row()
        _column = self.selected_item.column()
        newitem = self.selected_item.data()
        self.ui.main_table.openPersistentEditor(self.selected_item)

    def current_refresh_button_clicked(self):
        import copy_tool.copy_main as copy_main
        import exporter_util
        opc = exporter_util.outputPathConf(self.input_path)
        shot_path = opc.publishshotpath
        if self.debug:
            current_path = os.path.join(shot_path, 'publish', 'test_charSet')
        else:
            current_path = os.path.join(shot_path, 'publish', 'charSet')
        copy_main.copy_main(current_path)

    def open_publish_dir_button_clicked(self):
        import exporter_util
        opc = exporter_util.outputPathConf(self.input_path)
        shot_path = opc.shot_path
        publish_path = os.path.join(shot_path, 'publish')
        subprocess.call('explorer {}'.format(publish_path.replace('/', '\\')))

    def help_button_clicked(self):
        import webbrowser
        url = 'Y:/tool/ND_Tools/DCC/ND_AssetExporter/pycode/help/help.html'
        webbrowser.open_new_tab(url)

    def load_user_info(self):
        filename = 'user_info.py'
        output_dir = 'Y:\\users\\'+os.environ.get('USERNAME')+'\\DCC_log\\ND_AssetExporter'
        output_file = output_dir + '\\' + filename
        if not os.path.exists(output_dir):
            return
        if os.path.exists(output_file):
            sys.path.append(output_dir)
            import user_info
            print(user_info.path)
            self.drop_func(user_info.path)
        
    def output_user_info(self):
        filename = 'user_info.py'
        output_dir = 'Y:\\users\\'+os.environ.get('USERNAME')+'\\DCC_log\\ND_AssetExporter'
        output_file = output_dir + '\\' + filename
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_file, mode='w') as f:
            f.write('path =  \'{}\'\n'.format(self.input_path))

    def drop_func(self, urldata):
        self.check_row = []
        self.executed_row = []
        self.tabledata = []
        if type(urldata)==list:
            self.input_path = urldata[0].toString().replace('file:///', '')
        else:
            self.input_path = urldata
        self.ui.path_line.setText(self.input_path)
        self.ui.stack_area.setCurrentIndex(1)

        # shotgridからダウンロード
        ProjectInfoClass = main_util.ProjectInfo(self.input_path)
        self.ui.shot_line.setText(ProjectInfoClass.shot)
        self.ui.cut_line.setText(ProjectInfoClass.sequence)
        self.project = ProjectInfoClass.project_name
        self.ui.pro_line.setText(self.project)
        
        SGBaseClass = shotgun_mod.SGProjectClass(self.project, self.base_fields)
        SGBaseClass.get_dict('Asset')
        SGBaseClass.get_dict('Shot')
        shot_code = ProjectInfoClass.shot_code
        target_asset_list = SGBaseClass.get_keying_dict('Shot', 'code')[shot_code]['assets']
        all_asset_dics = SGBaseClass.get_keying_dict('Asset', 'code')

        # table data作成
        target_asset_dics = []
        for target_asset_name in target_asset_list:
            target_asset_dics.append(
                all_asset_dics[target_asset_name['name']])
        if len(target_asset_list) == 0:  # ショットのアセット情報が存在しない場合sequencesを見に行く
            seq_list = SGBaseClass.get_keying_list('Asset', 'sequences', 'sequence')
            for seq in seq_list:
                target_asset_list.append(seq['code'])
        is_cam_rig_export = ProjectInfoClass.get_camera_rig_info()
        self.tabledata = main_util.tabledata_maker(self.headers_item, self.convert_dic, target_asset_dics)
        self.tabledata = main_util.add_camera_row(self.headers_item, self.tabledata, is_cam_rig_export)

        def _setComboBoxList(qtcombobox, itemlist):
            qtcombobox.clear()
            qtcombobox.addItems(itemlist)

        def _setComboBoxValue(qtcombobox, value, subvalue=None):
            combo_index = qtcombobox.findText(value)
            if combo_index == -1:
                combo_index = qtcombobox.findText(value.lower())
                if combo_index == -1:
                    if subvalue != None:
                        combo_index = qtcombobox.findText(subvalue)
            qtcombobox.setCurrentIndex(combo_index)

        model = main_util.TableModelMaker(self.tabledata, self.headers)
        self.ui.main_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.main_table.customContextMenuRequested.connect(self.main_table_rclicked)
        self.ui.main_table.setModel(model)
        self.ui.main_table.setColumnWidth(0, 25)

        self.ui.export_local_btn.setEnabled(True)
        self.ui.export_submit_btn.setEnabled(True)
        self.output_user_info()

        # その他GUI        
        if NoDeadlineMode is False:
            groups = util_env.deadline_group
            pools = util_env.deadline_pool
            if type(groups) is str:
                groups = []
            if type(pools) is str:
                pools = []
            groups.sort()
            pools.sort()
            _setComboBoxList(self.ui.grouplist, groups)
            _setComboBoxValue(self.ui.grouplist, 'mem032')
            if main_util.is_arnold(self.project) is True:
                _setComboBoxValue(self.ui.grouplist, 'mem064')
            _setComboBoxList(self.ui.poollist, pools)
            _setComboBoxValue(self.ui.poollist, self.project, 'normal')
        elif NoDeadlineMode is True:
            self.ui.export_submit_btn.setDisabled(True)
            self.ui.export_submit_btn.setHidden(True)

        return True

    def export_main(self, mode):
        self.ui.stack_area.setCurrentIndex(2)
        self.ui.repaint()

        if self.ui.cam_scale_override_chk.isChecked():
            cam_scale = float(self.ui.cam_scale_override_velue_line.text())
        else:
            cam_scale = False

        if self.ui.abc_step_override_chk.isChecked() == True:
            abc_step_override = float(self.ui.abc_step_value_line.text())
        else:
            abc_step_override = 1.0

        if self.ui.frame_handle_chk.isChecked() == True:
            frame_handle = float(self.ui.frame_handle_value.text())
        else:
            frame_handle = False

        if self.ui.custom_frame_range_chk.isChecked() == True:
            frame_range = (self.ui.sFrame.text()) + '-' + (self.ui.eFrame.text())
        else:
            frame_range = False

        if mode == 'Submit':
            file_number = 1
            jobfiles_list = []

        for table_row in range(len(self.tabledata)):
            if table_row in self.executed_row:
                continue
            if table_row not in self.check_row:
                continue

            row_items = self.tabledata[table_row]

            if len(row_items)<7:
                self.executed_row.append(table_row)
                print('table data not qualified...')
                continue

            asset_name = row_items[1]
            namespace = row_items[2]
            export_type = row_items[3]
            export_item = row_items[4]
            top_node = row_items[5]
            asset_path = row_items[6].replace('\\','/')
            argsdic = {
                'asset_name': asset_name,
                # 'namespace': [yaml.safe_load(namespace.replace(':', '\:').replace('[', '\[').replace(']', '\]'))],
                'namespace': [namespace],
                # 'namespace': 'a',
                'export_item': yaml.safe_load(export_item),
                'top_node': top_node,
                'asset_path': asset_path,
                'debug': self.debug,
                'step_value': abc_step_override,
                'export_type': export_type,
                'project': self.project,
                'frame_range': frame_range,
                'frame_handle': frame_handle,
                'cam_scale': cam_scale,
                'input_path': str(self.input_path),
                'shot': str(self.ui.shot_line.text()),
                'sequence': str(self.ui.cut_line.text()),
                'scene_timewarp': self.ui.scene_timewarp_check.isChecked(),
                'abc_check': self.ui.abc_cache_check.isChecked(),
                'priority': str(self.ui.priority.text()),
                'pool': str(self.ui.poollist.currentText()),
                'group': str(self.ui.grouplist.currentText()),
                'env_load':self.ui.env_load_chk.isChecked()}

            if '{Empty!}' in argsdic.values():
                continue

            if mode == 'Local':
                log_name = 'log_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + asset_name+ '.txt'
                log_dir = 'Y:\\users\\'+os.environ.get('USERNAME')+'\\DCC_log\\ND_AssetExporter'
                log_path = log_dir + '\\' + log_name
                current_dir = r'Y:/tool/ND_Tools/DCC/ND_AssetExporter_test/pycode'
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                self.ui.stack_area.setCurrentIndex(2)
                thread_args = {}
                thread_args['argsdic']=argsdic
                thread_args['log_path']=log_path
                thread_args['current_dir']=current_dir
                export_thread = threading.Thread(target=thread_main, kwargs=thread_args)
                export_thread.start()

                count = 0
                timer=0

                while True:
                    if len(threading.enumerate())==1:
                        break
                    time.sleep(0.1)
                    timer=timer+0.1
                    if timer>4:
                        count=count+1
                        timer=0
                        if count==10:
                            count = 0
                        self.ui.log_area.setPlainText('now working{}'.format('.'*timer))
                        self.ui.repaint()
                    qApp.processEvents()
                self.last_log_path = log_path
                self.ui.open_log_button.setEnabled(True)
            elif mode == 'Submit':
                DLclass = main_util.DeadlineMod(**argsdic)
                jobfiles_list.append(DLclass.make_submit_files(file_number))
                file_number += 1
            self.executed_row.append(table_row)

        if mode == 'Submit':
            main_util.submit_to_deadlineJobs(jobfiles_list)

        self.ui.stack_area.setCurrentIndex(1)
        self.executed_row = list(set(self.executed_row))
        main_util.TableModelMaker(
                self.tabledata, self.headers,
                self.check_row, self.executed_row)
        print('===============Export End==================')


def thread_main(**kwargs):
    argsdic = json.dumps(kwargs['argsdic'], ensure_ascii=False)
    log_path = kwargs['log_path']
    current_dir = kwargs['current_dir']
    # python = 'Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe'
    python = PYPATH
    py_path = r'Y:\tool\ND_Tools\DCC\ND_AssetExporter_test\pycode\back_starter.py'
    with open(log_path, 'w+')as f:
        # proc = subprocess.run([python, py_path, argsdic], shell=True, stdout=f, cwd=current_dir)
        # print(python, py_path, argsdic)
        try:
            proc = subprocess.Popen([python, py_path, argsdic], shell=True, stdout=f, cwd=current_dir)

            # proc = subprocess.run([python, py_path, argsdic], shell=False, cwd=current_dir)
        # except:
            # proc = subprocess.Popen([python, py_path, argsdic], shell=True, cwd=current_dir)
            proc.wait()
        except:
            pass
    return


def runs(*argv):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    skin = '%s/skin.stylesheet' % onpath
    tx_o = open(skin, 'r')
    tx_r = tx_o.read()
    tx_o.close()
    app.setStyleSheet(tx_r)
    ui = GUI(None, app)
    ui.show()
    app.exec_()
    sys.exit()

if __name__ == '__main__':
    runs(sys.argv[1:])
