# -*- coding: utf-8 -*-
# ------------------------------
__version__ = '0.4'
__author__ = "Yoshihisa Okano, Kei Ueda"
# ------------------------------
import os,sys

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
import ND_lib.shotgun.shotgun_api3.shotgun as shotgun
import ND_lib.shotgun.sg_scriptkey as sg_scriptkey
import ND_lib.shotgun.sg_util as sg_util
import ND_lib.util.path as util_path
import util
import subprocess
from multiprocessing import Pool
from importlib import import_module

import main_util as mu
import shotgun_mod as sg_mod

import ND_Submitter.env as util_env

sg = sg_scriptkey.scriptKey()

pythonBatch = 'Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe'

from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtUiTools import QUiLoader


qtSignal = Signal
qtSlot = Slot

onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
class GUI (QMainWindow):
    WINDOW = 'ND_AssetExporter'

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.ui_path = '.\\gui.ui'
        self.ui = QUiLoader().load(self.ui_path)
        self.ui.groupBox.installEventFilter(self)
        self.ui.group_box.installEventFilter(self)
        self.setCentralWidget(self.ui)
        self.setGeometry(500, 200, 1000, 800)
        self.test = False
        debug = ''
        if self.test:debug = '__debug__'
        self.setWindowTitle('%s %s %s' % (self.WINDOW, __version__, debug))
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.headers_item = ["Asset name", "Name space", "Export Type", "Export Item","Top Node", "Asset Path"]
        self.asset_fields = ["code", "sg_namespace", "sg_export_type", "sg_top_node","sg_abc_export_list", "sg_anim_export_list", "sg_asset_path","sequences"]
        self.shot_fields = ["code", "assets"]
        self.convert_dic = {"Asset name": "code", "Name space": "sg_namespace","Export Type": "sg_export_type", "Top Node": "sg_top_node","Asset Path": "sg_asset_path"}
        self.headers = ["", self.headers_item]
        self.check_row = []
        self.executed_row = []
        self.camera_rig_export = False
        self.load_env = True
        self.priority = 50
        self.group = '16gb'
        self.slitem = None
        ###############


        #-----------------------------------------
        #UIと関数のコネクト
        #-----------------------------------------
        self.ui.overrideValue_LineEdit.setEnabled(False)
        self.ui.yeti_CheckBox.stateChanged.connect(self.load_env_checker)
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

        self.ui.FRCus_CheckBox.clicked.connect(self.FRCus_clicked)
        self.ui.FH_CheckBox.clicked.connect(self.FH_clicked)

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
        self.test = self.ui.debug_CheckBox.isChecked()

    def stepValue_LineEdit_stateChange(self):
        currentState = self.ui.stepValue_CheckBox.isChecked()
        self.ui.stepValue_LineEdit.setEnabled(currentState)

    def stepValue_clicked(self):
        currentState = self.ui.stepValue_CheckBox.isChecked()
        self.ui.stepValue_lineEdit.setEnabled(currentState)

    def pool_comboBox_stateChanged(self):
        self.pool = self.ui.poollist.currentText()

    def group_comboBox_stateChanged(self):
        self.group = self.ui.grouplist.currentText()

    def drop_act(self, urldata):
        self.inputpath = urldata[0].toString().replace("file:///", "")
        self.ui.path_line.setText(self.inputpath)
        self.ui.Change_Area.setCurrentIndex(1)

        ProjectInfoClass = mu.ProjectInfo(self.inputpath)
        pro_name = ProjectInfoClass.project_name
        shot = ProjectInfoClass.shot
        sequence = ProjectInfoClass.sequence
        shot_code = ProjectInfoClass.shot_code
        self.ui.shot_line.setText(shot)
        self.ui.cut_line.setText(sequence)
        self.ui.proj_line.setText(pro_name)
        self.project = pro_name

        # カメラタイプの取得
        self.camera_rig_export = ProjectInfoClass.get_camera_rig_info()
        SGAssetClass = sg_mod.SGGen_Cate(pro_name, 'Asset', self.asset_fields)
        SGShotClass = sg_mod.SGGen_Cate(pro_name, 'Shot', self.shot_fields)

        # target_assetの選定
        target_asset_list = (SGShotClass.make_nameddict('code')[shot_code]['assets'])
        all_asset_dics = (SGAssetClass.make_nameddict('code'))

        # target_asset_list内の名前をもとにAssetPageから取得
        target_asset_dics = []
        for target_asset_name in target_asset_list:
            target_asset_dics.append(
                all_asset_dics[target_asset_name['name']])

        if len(target_asset_list) == 0:  # ショットのアセット情報が存在しない場合、sequencesを見に行く
            seq_list = SGAssetClass.get_topicitem('sequences', sequence)
            for spseq in seq_list:
                target_asset_list.append(spseq['code'])

        self.tabledata = mu.tabledata_maker(self.headers_item, self.convert_dic, target_asset_dics)
        self.tabledata = mu.add_camera_row(self.headers_item, self.tabledata, self.camera_rig_export)

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

        deadline_groups = util_env.deadline_group #dictかも
        deadline_groups.sort()
        _setComboBoxList(self.ui.grouplist, deadline_groups)
        _setComboBoxValue(self.ui.grouplist, self.group)

        deadline_pools = util_env.deadline_pool
        deadline_pools.sort()
        _setComboBoxList(self.ui.poollist, deadline_pools)
        _setComboBoxValue(self.ui.poollist, self.project, 'normal')

        model = mu.TableModelMaker(self.tabledata, self.headers)

        self.ui.main_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.main_table.setModel(model)
        self.ui.main_table.setColumnWidth(0, 25)
        self.ui.start_button.setEnabled(True)
        self.ui.start_submit_button.setEnabled(True)

        return True

    def check_button_clicked(self):
        self.check_row = list(set([x.rows() for x in self.ui.main_table.selectedIndexes])]
        model = mu.TableModelMaker(self.tabledata, self.headers, self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def uncheck_button_clicked(self):
        selected_rows = [x.row() for x in self.ui.main_table.selectedIndexes]
        for row in selected_rows:
            try:
                self.check_row.remove(row)
            except:
                pass
        model = mu.TableModelMaker(self.tabledata, self.headers, self.check_row)
        self.ui.main_table.setModel(model)

    def allcheck_button_clicked(self):
        self.check_row = list(set(range(len(self.tabledata))))
        model = mu.TableModelMaker(self.tabledata, self.headers, self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def alluncheck_button_clicked(self):
        self.check_row = []
        model = mu.TableModelMaker(self.tabledata, self.headers, self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def FH_clicked(self):
        fh_state = self.ui.FH_CheckBox.isChecked()
        self.ui.FH_value.setEnabled(fh_state)

    def FRCus_clicked(self):
        fr_state = self.ui.FRCus_CheckBox.isChecked()
        self.ui.sFrame.setEnabled(fr_state)
        self.ui.eFrame.setEnabled(fr_state)

    def overrideValue_LineEdit_stateChange(self):
        currentState = self.ui.cameraScaleOverride_CheckBox.isChecked()
        self.ui.overrideValue_LineEdit.setEnabled(currentState)

    def load_env_checker(self):
        self.load_env = self.ui.yeti_CheckBox.isChecked()

    def start_button_clicked(self):
        self.export_body(mode="Local")

    def start_submit_button_clicked(self):
        self.export_body(mode="Submit")

    def export_body(self, mode):
        if self.ui.cameraScaleOverride_CheckBox.isChecked():
            camScale = float(self.ui.overrideValue_LineEdit.text())
        else:
            camScale = -1

        if self.ui.stepValue_CheckBox.isChecked() == True:
            abcstep_override = float(self.ui.stepValue_lineEdit.text())
        else:
            abcstep_override = 1.0

        if self.ui.FH_CheckBox.isChecked() == True:
            framehundle = float(self.ui.FH_value.text())
        else:
            framehundle = 0

        if self.ui.FRCus_CheckBox.isChecked() == True:
            framerange = (self.ui.sFrame.text()) + ',' + (self.ui.eFrame.text())
        else:
            framerange = None

        if mode == "Submit":
            file_number = 1
            jobFileslist = []

        for count in range(len(self.tabledata)):
            if count in self.executed_row:
                pass
            elif count in self.check_row:
                tableItem = self.tabledata[count]
                self.executed_row.append(count)
                if len(tableItem)<7:
                    continue
                assetname = tableItem[1]  # assetname
                namespace = tableItem[2]  # namespace
                exporttype = tableItem[3]  # exporttype
                exportitem = tableItem[4]  #exportitem
                topnode = tableItem[5]  # topnode
                assetpath = tableItem[6].replace("\\","/")  # Asset Path
                chara = assetname
                execargs_ls = {
                    'chara': chara,
                    'inputpath': self.inputpath.encode('utf-8'),
                    'namespace': namespace,
                    'exportitem': exportitem,
                    'topnode': topnode,
                    'assetpath': assetpath,
                    'testmode': self.test,
                    'env_load': self.load_env,
                    'stepValue': abcstep_override,
                    'framerange_output': True,
                    'exporttype': exporttype,
                    'project': self.project,
                    'shot': self.ui.shot_line.text().encode(),
                    'sequence': self.ui.cut_line.text().encode(),
                    'bakeAnim': self.ui.bake_anim.isChecked(),
                    'framerange': framerange,
                    'framehundle': framehundle,
                    'Priority': self.ui.priority.text(),
                    'Pool': self.ui.poollist.currentText(),
                    'Group': self.ui.grouplist.currentText()}

                for key, item in execargs_ls.items():
                    print key, item
                    if type(item)==str:
                        new_item = item.rstrip(',')
                        if new_item == '':
                            new_item = None
                        if new_item!=None:
                            new_item = new_item.replace(", ", ",")
                        execargs_ls[key] = new_item

                if exporttype == 'camera':
                    execargs_ls['camScale'] = camScale
                else:
                    pass
                if "{Empty!}" not in execargs_ls.values():
                    if mode == "Submit":
                        DLclass = mu.DeadlineMod(**execargs_ls)
                        jobFileslist.append(DLclass.make_submit_files(file_number))
                        file_number += 1
                    elif mode == "Local":
                        mu.execExporter(**execargs_ls)
                    util.addTimeLog(chara, self.inputpath, test=self.test)
            else:
                pass
        if mode == "Submit":
            mu.submit_to_deadlineJobs(jobFileslist)
        self.executed_row = list(set(self.executed_row))
        mu.TableModelMaker(self.tabledata, self.headers,self.check_row, self.executed_row)
        print "===============Export End=================="

    def main_table_clicked(self):
        if self.slitem != None:
            self.ui.main_table.closePersistentEditor(self.slitem)
            self.slitem = None


    def main_table_doubleclicked(self):
        clicked_row = self.ui.main_table.selectedIndexes()[0].row()
        if clicked_row in self.check_row:
            self.check_row.remove(clicked_row)
        else:
            self.check_row.append(clicked_row)
        self.check_row = list(set(self.check_row))
        model = mu.TableModelMaker(
            self.tabledata, self.headers, self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

def runs(*argv):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    skin = "%s/skin.stylesheet" % onpath
    tx_o = open(skin, "r")
    tx_r = tx_o.read()
    tx_o.close()
    app.setStyleSheet(tx_r)
    if argv[0][0] == '':
        ui = GUI()
    else:
        ui = GUI(mode=argv[0][0])
    ui.show()
    app.exec_()
    return True

if __name__ == '__main__':
    runs(sys.argv[1:])
