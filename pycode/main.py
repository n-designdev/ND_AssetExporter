# -*- coding: utf-8 -*-
import os,sys
import time
# ------------------------------
__version__ = '2.1'
__author__ = "Kei Ueda"
# ------------------------------
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')

for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)
# ------------------------------------

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtUiTools import QUiLoader

import ND_lib.shotgun.sg_scriptkey as sg_scriptkey
import util
import subprocess
import datetime
import threading

import main_util
import shotgun_mod
try:
    import ND_Submitter.env as util_env
    # import ND_Submitter2.env as util_env
except Exception as e:
    DeadlineMode = False
else:
    DeadlineMode = True

sg = sg_scriptkey.scriptKey()

qtSignal = Signal
qtSlot = Slot

onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
class GUI(QMainWindow):
    WINDOW = 'ND_AssetExporter'
    def __init__(self, parent=None, qApp=None):
        super(self.__class__, self).__init__(parent)
        self.ui_path = '.\\Exp_gui.ui'
        self.ui = QUiLoader().load(self.ui_path)
        self.ui.DD_area.installEventFilter(self)
        self.setCentralWidget(self.ui)
        self.setGeometry(500, 200, 1000, 800)
        self.debug = False
        debug = ''
        if self.debug:debug = '__debug__'
        self.setWindowTitle('%s %s %s' % (self.WINDOW, __version__, debug))
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.headers_item = [
            "Asset name", "Name space",
            "Export Type", "Export Item",
            "Top Node", "Asset Path"]
        self.asset_fields = [
            "code", "sg_namespace", "sg_export_type",
            "sg_top_node", "sg_abc_export_list",
            "sg_anim_export_list", "sg_asset_path",
            "sequences"]
        self.shot_fields = ["code", "assets"]
        self.base_fields = [
            "code", "assets",
            "sg_namespace", "sg_export_type",
            "sg_top_node", "sg_abc_export_list",
            "sg_anim_export_list", "sg_asset_path",
            "sequences"]
        self.convert_dic = {
            "Asset name": "code",
            "Name space": "sg_namespace",
            "Export Type": "sg_export_type",
            "Top Node": "sg_top_node",
            "Asset Path": "sg_asset_path"}
        self.headers = [""] + (self.headers_item)
        self.input_path = ''
        self.camera_rig_export = False
        self.tabledata = []
        self.check_row = []
        self.executed_row = []
        self.priority = 50
        self.group = '16gb'
        self.selected_item = None

        self.ui.overrideValue_LineEdit.setEnabled(False)
        self.ui.Change_Area.setCurrentIndex(0)

        self.ui.cameraScaleOverride_CheckBox.stateChanged.connect(self.overrideValue_LineEdit_stateChange)
        self.ui.check_button.clicked.connect(self.check_button_clicked)
        self.ui.uncheck_button.clicked.connect(self.uncheck_button_clicked)
        self.ui.allcheck_button.clicked.connect(self.allcheck_button_clicked)
        self.ui.alluncheck_button.clicked.connect(self.alluncheck_button_clicked)
        self.ui.start_button.clicked.connect(self.start_button_clicked)
        self.ui.start_submit_button.clicked.connect(self.start_submit_button_clicked)
        self.ui.stepValue_CheckBox.stateChanged.connect(self.stepValue_clicked)

        self.ui.main_table.clicked.connect(self.main_table_clicked)
        self.ui.main_table.doubleClicked.connect(self.main_table_doubleclicked)
        self.ui.debug_CheckBox.stateChanged.connect(self.debug_clicked)

        self.ui.framerangecustom_checkbox.clicked.connect(self.framerangecustom_checkbox)
        self.ui.framehundle_checkbox.clicked.connect(self.framehundle_checkbox_clicked)
        self.ui.open_log_button.clicked.connect(self.open_log_button_clicked)
        self.ui.current_refresh_button.clicked.connect(self.current_refresh_button_clicked)
        self.ui.open_publish_dir_button.clicked.connect(self.open_publish_dir_button_clicked)
        self.ui.help_button.clicked.connect(self.help_button_clicked)
56
    def contextMenu(self, point):
        print point

    def eventFilter(self, object, event):
        if event.type() == QEvent.DragEnter:
            event.acceptProposedAction()
        if event.type() == QEvent.Drop:
            mimedata = event.mimeData()
            urldata = mimedata.urls()
            self.drop_act(urldata)
        return True

    def debug_clicked(self):
        self.debug = self.ui.debug_CheckBox.isChecked()

    def stepValue_LineEdit_stateChange(self):
        currentState = self.ui.stepValue_CheckBox.isChecked()
        self.ui.stepValue_LineEdit.setEnabled(currentState)

    def stepValue_clicked(self):
        currentState = self.ui.stepValue_CheckBox.isChecked()
        self.ui.stepValue_lineEdit.setEnabled(currentState)

    def drop_act(self, urldata):
        self.check_row = []
        self.executed_row = []
        self.tabledata = []
        self.input_path = urldata[0].toString().replace("file:///", "")
        self.ui.path_line.setText(self.input_path)
        self.ui.Change_Area.setCurrentIndex(1)
        ProjectInfoClass = main_util.ProjectInfo(self.input_path)
        shot = ProjectInfoClass.shot
        sequence = ProjectInfoClass.sequence
        shot_code = ProjectInfoClass.shot_code
        self.ui.shot_line.setText(shot)
        self.ui.cut_line.setText(sequence)
        self.project = ProjectInfoClass.project_name
        self.ui.proj_line.setText(self.project)

        # カメラタイプの取得
        self.camera_rig_export = ProjectInfoClass.get_camera_rig_info()
        SGBaseClass = shotgun_mod.SGProjectClass(self.project, self.base_fields)
        SGBaseClass.get_dict("Asset")
        SGBaseClass.get_dict("Shot")
        target_asset_list = SGBaseClass.get_keying_dict("Shot", "code")[shot_code]['assets']
        all_asset_dics = SGBaseClass.get_keying_dict("Asset", "code")

        # GUI table作成
        target_asset_dics = []
        for target_asset_name in target_asset_list:
            target_asset_dics.append(
                all_asset_dics[target_asset_name['name']])
        if len(target_asset_list) == 0:  # ショットのアセット情報が存在しない場合、sequencesを見に行く
            seq_list = SGBaseClass.get_keying_list("Asset", "sequences", "sequence")
            for seq in seq_list:
                target_asset_list.append(seq['code'])
        tabledata = main_util.tabledata_maker(self.headers_item, self.convert_dic, target_asset_dics)
        tabledata = main_util.add_camera_row(self.headers_item, tabledata, self.camera_rig_export)

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

        if DeadlineMode is True:
            groups = util_env.deadline_group
            if type(groups) is str:
                groups = []
            groups.sort()
            pools = util_env.deadline_pool
            if type(pools) is str:
                pools = []
            pools.sort()
            _setComboBoxList(self.ui.grouplist, groups)
            _setComboBoxValue(self.ui.grouplist, "mem032")
            if main_util.check_arnold(self.project) is True:
                _setComboBoxValue(self.ui.grouplist, "mem064")
            _setComboBoxList(self.ui.poollist, pools)
            _setComboBoxValue(self.ui.poollist, self.project, 'normal')
        else:
            self.ui.start_submit_button.setDisabled(True)
            self.ui.start_submit_button.setHidden(True)
        model = main_util.TableModelMaker(tabledata, self.headers)
        self.ui.main_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.main_table.customContextMenuRequested.connect(self.main_table_rclicked)
        self.ui.main_table.setModel(model)
        self.ui.main_table.setColumnWidth(0, 25)
        self.ui.start_button.setEnabled(True)
        self.ui.start_submit_button.setEnabled(True)
        self.tabledata = tabledata
        self.output_user_info()
        return True

    def check_button_clicked(self):
        for selected_row in self.ui.main_table.selectedIndexes():
            self.check_row.append(selected_row.row())
        self.check_row = list(set(self.check_row))
        model = main_util.TableModelMaker(
            self.tabledata, self.headers,
            self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def uncheck_button_clicked(self):
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

    def allcheck_button_clicked(self):
        self.check_row = range(len(self.tabledata))
        model = main_util.TableModelMaker(
            self.tabledata, self.headers,
            self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def alluncheck_button_clicked(self):
        self.check_row = []
        model = main_util.TableModelMaker(
            self.tabledata, self.headers,
            self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def framehundle_checkbox_clicked(self):
        self.ui.framehundle_value.setEnabled(
            self.ui.framehundle_checkbox.isChecked())

    def framerangecustom_checkbox(self):
        fr_state = self.ui.framerangecustom_checkbox.isChecked()
        self.ui.sFrame.setEnabled(fr_state)
        self.ui.eFrame.setEnabled(fr_state)

    def overrideValue_LineEdit_stateChange(self):
        currentState = self.ui.cameraScaleOverride_CheckBox.isChecked()
        self.ui.overrideValue_LineEdit.setEnabled(currentState)

    def start_button_clicked(self):
        print 'Local'
        self.export_body(mode='Local')

    def start_submit_button_clicked(self):
        print 'Submit'
        self.export_body(mode='Submit')

    def open_log_button_clicked(self):
        sakura = r"C:\Program Files (x86)\sakura\sakura.exe"
        subprocess.Popen([sakura, self.output_file])

    def export_body(self, mode='Local'):
        if self.ui.cameraScaleOverride_CheckBox.isChecked():
            camScale = float(self.ui.overrideValue_LineEdit.text())
        else:
            camScale = -1

        if self.ui.stepValue_CheckBox.isChecked() == True:
            abcstep_override = float(self.ui.stepValue_lineEdit.text())
        else:
            abcstep_override = 1.0

        if self.ui.framehundle_checkbox.isChecked() == True:
            framehundle = float(self.ui.framehundle_value.text())
        else:
            framehundle = 0

        if self.ui.framerangecustom_checkbox.isChecked() == True:
            framerange = (self.ui.sFrame.text()) + ',' + (self.ui.eFrame.text())
        else:
            framerange = None

        if mode == 'Submit':
            file_number = 1
            jobFileslist = []

        self.ui.Change_Area.setCurrentIndex(2)
        self.ui.repaint()

        for count in range(len(self.tabledata)):
            if count in self.executed_row:
                pass
            elif count in self.check_row:
                tableItem = self.tabledata[count]
                self.executed_row.append(count)
                if len(tableItem)<7:
                    continue
                assetname = tableItem[1]
                namespace = tableItem[2]
                export_type = tableItem[3]
                export_item = tableItem[4]
                topnode = tableItem[5]
                assetpath = tableItem[6].replace("\\","/")
                chara = assetname
                execargs_ls = {
                    'chara': chara,
                    'namespace': namespace,
                    'export_item': export_item,
                    'topnode': topnode,
                    'assetpath': assetpath,
                    'debug_mode': self.debug,
                    'step_value': abcstep_override,
                    'framerange_output': True,
                    'export_type': export_type,
                    'project': self.project,
                    'framerange': framerange,
                    'framehundle': framehundle,
                    # 'input_path': self.input_path,
                    'input_path': self.input_path.encode('utf-8'),
                    'shot': self.ui.shot_line.text().encode(),
                    'sequence': self.ui.cut_line.text().encode(),
                    'env_load': self.ui.project_loader_checkbox.isChecked(),
                    'bake_anim': self.ui.bake_anim.isChecked(),
                    'scene_timeworp': self.ui.scene_timeworp_check.isChecked(),
                    'abc_check': self.ui.abc_cache_check.isChecked(),
                    'Priority': self.ui.priority.text(),
                    'Pool': self.ui.poollist.currentText(),
                    'Group': self.ui.grouplist.currentText()}

                for key, item in execargs_ls.items():
                    if type(item)==str:
                        new_item = item.rstrip(',')
                        if new_item == '':
                            new_item = None
                        if new_item!=None:
                            new_item = new_item.replace(", ", ",")
                        execargs_ls[key] = new_item
                if export_type == 'camera':
                    execargs_ls['camScale'] = camScale
                else:
                    pass
                if "{Empty!}" not in execargs_ls.values():
                    if mode == 'Submit':
                        DLclass = main_util.DeadlineMod(**execargs_ls)
                        jobFileslist.append(DLclass.make_submit_files(file_number))
                        file_number += 1
                    else:
                        now = datetime.datetime.now()
                        filename = "log_" + now.strftime('%Y%m%d_%H%M%S') + chara+ ".txt"
                        output_dir = "Y:\\users\\"+os.environ.get("USERNAME")+"\\DCC_log\\ND_AssetExporter"
                        output_file = output_dir + "\\" + filename
                        current_dir = "Y:\\tool\\ND_Tools\\DCC\\ND_AssetExporter\\pycode"
                        self.ui.Change_Area.setCurrentIndex(2)
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        export_thread = threading.Thread(target=thread_main, args=(str(execargs_ls), output_file, current_dir))
                        export_thread.start()
                        count = 0
                        t=0
                        while True:
                            if len(threading.enumerate())==1:
                                break
                            time.sleep(0.1)
                            t=t+0.1
                            if t>4:
                                count=count+1
                                t=0
                                if count==10:
                                    count = 0
                                self.ui.log_area.setPlainText("now working{}".format("."*count))
                                self.ui.repaint()
                            qApp.processEvents()
                        self.output_file = output_file
                        self.ui.open_log_button.setEnabled(True)
            else:
                pass
        if mode == 'Submit':
            main_util.submit_to_deadlineJobs(jobFileslist)
        self.ui.Change_Area.setCurrentIndex(1)
        self.executed_row = list(set(self.executed_row))
        main_util.TableModelMaker(
            self.tabledata, self.headers,
            self.check_row, self.executed_row)
        print "===============Export End=================="

    def main_table_clicked(self):
        if self.selected_item != None:
            self.ui.main_table.closePersistentEditor(self.selected_item)
            self.selected_item = None

    def main_table_doubleclicked(self):
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
        opc = util.outputPathConf(self.input_path)
        shot_path = opc.publishshotpath
        if self.debug:
            current_path = os.path.join(shot_path, "publish", "test_charSet")
        else:
            current_path = os.path.join(shot_path, "publish", "charSet")
        copy_main.copy_main(current_path)

    def open_publish_dir_button_clicked(self):
        import exporter_util
        opc = exporter_util.outputPathConf(self.input_path)
        shot_path = opc.publishshotpath
        publish_path = os.path.join(shot_path, "publish")
        subprocess.call("explorer {}".format(publish_path.replace("/", "\\")))

    def help_button_clicked(self):
        import webbrowser
        url = "Y:/tool/ND_Tools/DCC/ND_AssetExporter/pycode/help/help.html"
        webbrowser.open_new_tab(url)

    def load_user_info(self):
        filename = "user_info.py"
        output_dir = "Y:\\users\\"+os.environ.get("USERNAME")+"\\DCC_log\\ND_AssetExporter"
        output_file = output_dir + "\\" + filename
        if not os.path.exists(output_dir):
            return
        if os.path.exists(output_file):
            sys.path.append(output_dir)
            import user_info
            info = user_info.setting_info

    def output_user_info(self):
        filename = "user_info.py"
        output_dir = "Y:\\users\\"+os.environ.get("USERNAME")+"\\DCC_log\\ND_AssetExporter"
        output_file = output_dir + "\\" + filename
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_file) as f:
            f.write("setting_info{")
            f.write("    path = \"{}\"".format(self.input_path))
            f.write("}")

def thread_main(execargs_ls, output_path, current_dir):
    python = "Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe"
    py_path = "Y:\\tool\\ND_Tools\\DCC\\ND_AssetExporter\\pycode\\main_util.py"
    with open(output_path, "w+")as f:
        proc = subprocess.Popen([python, py_path,str(execargs_ls)], shell=True,stdout=f, cwd=current_dir)
        proc.wait()
    return


def runs(*argv):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    skin = "%s/skin.stylesheet" % onpath
    tx_o = open(skin, "r")
    tx_r = tx_o.read()
    tx_o.close()
    app.setStyleSheet(tx_r)
    ui = GUI(None, app)
    ui.show()
    app.exec_()
    sys.exit()

if __name__ == '__main__':
    print QtGui.__file__
    runs(sys.argv[1:])
