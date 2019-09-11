# -*- coding: utf-8 -*-

# ------------------------------
__version__ = '0.1'
__author__ = "Yoshihisa Okano, Kei Ueda"

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

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import ND_lib.shotgun.shotgun_api3.shotgun as shotgun
import ND_lib.shotgun.sg_scriptkey as sg_scriptkey
import ND_lib.shotgun.sg_util as sg_util
import ND_lib.util.path as util_path
import util
import subprocess
from multiprocessing import Pool


reload(shotgun)

sg = sg_scriptkey.scriptKey()

pythonBatch = 'Y:\\tool\\MISC\\Python2710_amd64_vs2010\\python.exe'


try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtUiTools import QUiLoader
except:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtWidgets import *

qtSignal = Signal
qtSlot = Slot

onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

testRun = False


class GUI (QMainWindow):
    WINDOW = 'ND_AssetExporter'

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        ################
        self.ui_path = '.\\gui.ui'
        self.check_row = []  # エクスポート対象
        self.executed_row = []
        self.quantity = 0  # 行数
        self.tableData0 = []  # リスト
        self.inputpath = ''
        self.stepValue = 1.0
        self.export_type_list = []
        self.project = ''  # プロジェクト名
        self.camera_rig_export = False  # シーン内にあるカメラを使うか
        self.yeti = True  # shotgun環境を読むか
        self.process_list = []  # プロセスを格納 サブプロセスで使用
        self.framerange_output = True
        ################

        self.test = False

        debug = ''
        if testRun:
            debug = '__debug__'

        #### UI系変数####
        self.headers = [" ", "Asset name", "Name space",
                        "Export List", "Top Node", "Asset Path"]
        self.table_row = len(self.headers)
        self.setWindowTitle('%s %s %s' % (self.WINDOW, __version__, debug))
        self.setGeometry(500, 200, 1000, 800)
        self.exportTgtList = []
        ###############

        #### UI宣言系#####
        self.ui = QUiLoader().load(self.ui_path)
        self.setCentralWidget(self.ui)
        self.ui.groupBox.installEventFilter(self)
        self.ui.group_box.installEventFilter(self)
        ###############

        ####UIと関数#####
        self.ui.overrideValue_LineEdit.setEnabled(False)
        self.ui.yeti_CheckBox.stateChanged.connect(self.yeti_checker)
        self.ui.Change_Area.setCurrentIndex(0)

        self.ui.cameraScaleOverride_CheckBox.stateChanged.connect(
            self.overrideValue_LineEdit_stateChange)
        self.ui.check_button.clicked.connect(self.check_button_clicked)
        self.ui.uncheck_button.clicked.connect(self.uncheck_button_clicked)
        self.ui.allcheck_button.clicked.connect(self.allcheck_button_clicked)
        self.ui.alluncheck_button.clicked.connect(
            self.alluncheck_button_clicked)
        self.ui.start_button.clicked.connect(self.start_button_clicked)
        self.ui.pro_num_CheckBox.stateChanged.connect(self.pro_num_clicked)
        self.ui.framerange_CheckBox.stateChanged.connect(
            self.framerange_stateChange)

        self.ui.main_table.doubleClicked.connect(self.main_table_clicked)

        self.ui.debug_CheckBox.stateChanged.connect(self.debug_clicked)
        ###############

    def eventFilter(self, object, event):
        if event.type() == QEvent.DragEnter:
            event.acceptProposedAction()
            return True

        if event.type() == QEvent.Drop:
            self.drop_act(event)

            if self.ui.stepValue_CheckBox.isChecked():
                self.stepValue = float(
                    self.ui.stepValue_LineEdit.text())
            else:
                self.stepValue = 1.0

    def debug_clicked(self):
        self.test = self.ui.debug_CheckBox.isChecked()

    def stepValue_LineEdit_stateChange(self):
        currentState = self.ui.stepValue_CheckBox.isChecked()
        self.ui.stepValue_LineEdit.setEnabled(currentState)

    def framerange_stateChange(self):
        currentState = self.ui.framerange_CheckBox.isChecked()
        self.framerange_output = currentState

    def pro_num_clicked(self):
        currentState = self.ui.pro_num_CheckBox.isChecked()
        self.ui.pro_num.setEnabled(currentState)

    def drop_act(self, event):  ### D&D時に実行される
        self.check_row = []
        self.executed_row = []
        self.quantity = 0
        self.tableData0 = []
        self.inputpath = ''
        self.stepValue = 1.0

        mimedata = event.mimeData()
        a = mimedata.urls()
        self.inputpath = a[0].toString().replace("file:///", "")

        self.ui.path_line.setText(self.inputpath)
        self.ui.Change_Area.setCurrentIndex(1)

        ### ショットガン経由でプロジェクト名等を取得
        dic = util_path.get_path_dic(self.inputpath)

        print 'Input Path : '+self.inputpath
        print '__dic___'
        print dic
        print '________'

        for k, v in dic.items():
            print k, v
            if k == 'project_name':
                pro_name = v
            elif k == 'shot':
                shot = v
            elif k == 'sequence':
                sequence = v
            elif k == 'roll':
                roll = v

        shot_name = dic["shot_code"]
        ###

        self.ui.shot_line.setText(shot)
        self.ui.cut_line.setText(sequence)

        sg = sg_scriptkey.scriptKey()
        project = sg_util.get_project(pro_name)
        self.project = project[0]['name']

        ### カメラタイプの取得
        project_conf = util_path.get_conf_dic(self.project.lower())
        self.camera_rig_export = project_conf.get(
            "preferences", {}).get("camera_rig_export")

        ### ショットガン取得用変数
        filters = [["project", "is", project]]
        asset_fields = ["code", "sg_namespace", "sg_export_type", "sg_top_node",
                        "sg_abc_export_list", "sg_anim_export_list", "sg_asset_path", "sequences"]
        shot_fields = ["code", "assets"]

        self.ui.proj_line.setText(pro_name)
        print 'success'
        asset_list = dict()
        asset_list = sg.find('Asset', filters, asset_fields)

        shot_list = dict()
        shot_list = sg.find('Shot', filters, shot_fields)

        target_asset = []
        shot_list_flag = 0
        for x in shot_list:
            if x['code'] == shot_name:
                q = x
                if len(x['assets']) == 0:
                    break
                else:
                    shot_list_flag = 1
            else:
                pass
        same_seq = []
        if shot_list_flag == 0:  # ショットのアセット情報が存在しない場合、sequencesを見に行く
            for x in asset_list:
                if len(x["sequences"]) != 0:
                    if x["sequences"][0]["name"] == sequence:
                        same_seq.append(x)
        print '_______________________'

        ### 対象アセットの選定
        if shot_list_flag == 1:
            try:
                for x in q["assets"]:
                    target_asset.append(x['name'])
            except(UnboundLocalError):
                print 'aa'
        elif shot_list_flag == 0:
            for x in same_seq:
                target_asset.append(x['code'])
        print target_asset

        type_count = 0
        exporttype_abclist = sg.find('Asset', filters, ["sg_abc_export_list"])
        exporttype_animlist = sg.find(
            'Asset', filters, ["sg_anim_export_list"])

        ####asset#####
        for item in asset_list:
            if item['code'] in target_asset:
                y = []
                y.append('')
                for z in asset_fields:
                    if z == "sequences":
                        pass
                    else:
                        if item[z] is None:
                            if z == "sg_abc_export_list" or z == "sg_anim_export_list":
                                print '__'
                            elif z == "sg_export_type":
                                y.append('None')
                                self.export_type_list.append('None')
                            else:
                                y.append('None')
                        else:
                            if z == "sg_export_type":
                                try:
                                    if item[z] == 'abc':
                                        y.append(
                                            exporttype_abclist[type_count]["sg_abc_export_list"])
                                        self.export_type_list.append('abc')
                                    elif item[z] == 'anim':
                                        y.append(
                                            exporttype_animlist[type_count]["sg_anim_export_list"])
                                        self.export_type_list.append('anim')
                                except:
                                    y.append('None')
                                    self.export_type_list.append('None')
                                    print "export type must \"abc\" or \"anim\" "
                            elif z == "sg_abc_export_list" or z == "sg_anim_export_list":
                                pass
                            else:
                                y.append(item[z])

                x = []

                self.tableData0.append(y)
                self.quantity = self.quantity + 1
                type_count = type_count + 1
            else:
                type_count = type_count + 1

        ###camera###
        if self.camera_rig_export == 'True':
            pass
        else:
            y = []
            y.append("")
            y.append("Camera")
            y.append("")
            y.append("")
            y.append("")
            y.append("")

            self.quantity = self.quantity + 1
            self.tableData0.append(y)

        self.tableData0[0][0] = ""
        self.ui.all_num.setText(str(self.quantity))

        model = TableModelMaker(
            self.tableData0, self.headers, self.check_row, self.executed_row)

        self.ui.main_table.setModel(model)
        self.ui.main_table.setColumnWidth(0, 25)
        self.ui.start_button.setEnabled(True)

        return True

    def check_button_clicked(self):
        y = self.ui.main_table.selectedIndexes()
        z = self.check_row

        for x in y:
            z.append(x.row())

        self.check_row = list(set(z))
        self.ui.plan_num.setText((str(len(self.check_row))))

        model = TableModelMaker(
            self.tableData0, self.headers, self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)

    def uncheck_button_clicked(self):
        y = self.ui.main_table.selectedIndexes()
        z = []

        for x in y:
            z.append(x.row())

        z = list(set(z))
        for x in z:
            try:
                self.check_row.remove(x)
            except:
                pass

        model = TableModelMaker(self.tableData0, self.headers, self.check_row)
        self.ui.plan_num.setText((str(len(self.check_row))))
        self.ui.main_table.setModel(model)

    def allcheck_button_clicked(self):
        z = self.check_row

        for x in range(self.quantity):
            z.append(x)

        self.check_row = list(set(z))

        model = TableModelMaker(
            self.tableData0, self.headers, self.check_row, self.executed_row)

        self.ui.main_table.setModel(model)
        self.ui.plan_num.setText(str(self.quantity))

    def alluncheck_button_clicked(self):
        self.check_row = []
        model = TableModelMaker(
            self.tableData0, self.headers, self.check_row, self.executed_row)

        self.ui.main_table.setModel(model)
        self.ui.plan_num.setText(str(0))

    def tableClicked(self, indexClicked):  # Tableクリック時
        self.selectRow = indexClicked.row()

    def overrideValue_LineEdit_stateChange(self):
        currentState = self.ui.cameraScaleOverride_CheckBox.isChecked()
        self.ui.overrideValue_LineEdit.setEnabled(currentState)

    def yeti_checker(self):
        self.yeti = self.ui.yeti_CheckBox.isChecked()

    def start_button_clicked(self):

        testRun = self.test

        if self.ui.pro_num_CheckBox.isChecked:
            pro_num = self.ui.pro_num.value()
        else:
            pro_num = 1

        count = 0

        for tableItem in self.tableData0:
            if count in self.executed_row:
                pass
            else:
                if count in self.check_row:
                    self.executed_row.append(count)

                    assetname = tableItem[1]  # assetname
                    namespace = tableItem[2]  # namespace
                    exporttype = tableItem[4]  # exporttype
                    topnode = tableItem[3]  # top_node
                    assetpath = tableItem[5]  # Asset Path

                    self.camScale = -1

                    chara = assetname

                    if self.ui.cameraScaleOverride_CheckBox.isChecked():
                        self.camScale = float(
                            self.ui.overrideValue_LineEdit.text())
                    else:
                        self.camScale = -1

                    if self.export_type_list[count] == 'anim':
                        self.execExportAnim(chara, self.inputpath, namespace, exporttype, topnode,
                                            assetpath, testRun, self.yeti, self.stepValue, self.framerange_output)
                    elif self.export_type_list[count] == 'abc':
                        self.execExport(chara, self.inputpath, namespace, exporttype, topnode,
                                        assetpath, testRun, self.yeti, self.stepValue, self.framerange_output)

                    util.addTimeLog(chara, self.inputpath, test=testRun)

                else:
                    pass
            count = count + 1

        p = Pool(pro_num)  # 同時に実行するプロセス
        p.map(process_do, self.process_list)

        self.executed_row = list(set(self.executed_row))
        TableModelMaker(self.tableData0, self.headers,
                        self.check_row, self.executed_row)

        print "===============Export End=================="

    def execExport(self, charaName, inputpath, namespace,  topnode,exporttype, assetpath, test, yeti, stepValue, framerange_output):

        exporttypelist = '[' + exporttype +']'
        exporttypelist = exporttypelist.replace(' ','')
        args = pythonBatch + ' back_starter_abc.py '
        args = args + str(charaName)+' '+str(inputpath)+' '+str(namespace)+' '+str(exporttypelist)+' ' + str(topnode)+' '+str(
            assetpath)+' '+str(test)+' '+str(yeti)+' '+str(stepValue)+' '+str(self.project)+' '+str(framerange_output)
        self.process_list.append(args)

    def execExportAnim(self, charaName, inputpath, namespace,  topnode, exporttype, assetpath, test, yeti, stepValue, framerange_output):

        exporttypelist = '[' + exporttype +']'
        exporttypelist = exporttypelist.replace(' ','')

        print '#'*20
        args = pythonBatch + ' back_starter_anim.py '
        args = args + str(charaName)+' '+str(inputpath)+' '+str(namespace)+' '+str(exporttypelist)+' ' + str(topnode)+' '+str(
            assetpath)+' '+str(test)+' '+str(yeti)+' '+str(stepValue)+' '+str(self.project)+' '+str(framerange_output)
        self.process_list.append(args)

    def execExportCamera(self, inputpath, camScale, test):
        args = pythonBatch + ' back_starter_cam.py '
        args = args + str(inputpath) + ' ' + str(camScale) + \
            ' ' + str(test)+' '+str(self.project)
        self.process_list.append(args)

    def main_table_clicked(self):  # ダブルクリックされたとき
        clicked_row = self.ui.main_table.selectedIndexes()[0].row()
        z = self.check_row
        if clicked_row in z:
            z.remove(clicked_row)
        else:
            z.append(clicked_row)

        self.check_row = list(set(z))
        self.ui.plan_num.setText((str(len(self.check_row))))

        model = TableModelMaker(
            self.tableData0, self.headers, self.check_row, self.executed_row)
        self.ui.main_table.setModel(model)


class TableModelMaker(QAbstractTableModel):

    def __init__(self, list, headers=[], check_row=[], executed_row=[], parent=None):
        self.check_row = check_row
        QAbstractTableModel.__init__(self, parent)
        self.list = list
        self.headers = headers
        self.executed_row = executed_row

    def rowCount(self, parent):
        return len(self.list)

    def columnCount(self, parent):
        return len(self.list[0])

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.BackgroundRole):

        row = index.row()
        column = index.column()

        if role == Qt.EditRole:
            return self.list[row][column]

        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()

            if column == 0:
                if row in self.executed_row:
                    x = "✔"
                    t = x.decode("utf-8", errors="ignore")
                    value = t
                else:
                    if row in self.check_row:
                        x = "◎"
                        t = x.decode("utf-8", errors="ignore")
                        value = t
                    else:
                        value = self.list[row][column]
            else:
                value = self.list[row][column]

            return value

        elif role == QtCore.Qt.BackgroundRole:
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
            self.list[row][column] = value
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
####ここまでTableModel用 ###

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

### マルチプロセス用
def process_do(order):
    print order
    a = subprocess.call(order)


if __name__ == '__main__':
    runs(sys.argv[1:])
