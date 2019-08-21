# -*- coding: utf-8 -*-

#------------------------------
__version__ = '0.6.13'
__author__ = "Yoshihisa Okano"
#------------------------------


import sys
import os
import shutil

import util
import batch
from importlib import import_module
import subprocess
import back_starter_anim
import back_starter_abc
from multiprocessing import Pool
from multiprocessing import Process

# import ninaSetup
# import hikalSetup
# import ikkaSetup

#------------------------------------

env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key,'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\','/')
    if path in sys.path: continue
    sys.path.append(path)
#------------------------------------
import ND_lib.util.path as util_path
import ND_lib.shotgun.sg_util as sg_util

#Shotgunのスクリプトキーを取得
import ND_lib.shotgun.sg_scriptkey as sg_scriptkey

#------------------------------------
#shotgun_api3
#https://github.com/shotgunsoftware/python-api

import ND_lib.shotgun.shotgun_api3.shotgun as shotgun
reload(shotgun)
sg = sg_scriptkey.scriptKey()

pythonBatch = 'C:\\Program Files\\Shotgun\\Python\\python.exe'

#------------------------------------

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

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

### debug mode

testRun = False

class GUI (QMainWindow):
    WINDOW = 'mem chara export'
    def __init__ (self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.ui_path = '.\\gui.ui'
        self.check_row = []#エクスポート対象
        self.executed_row = []
        self.quantity = 0 #行数
        self.tableData0 = [] #リスト
        self.inputpath = ''
        self.stepValue = 1.0
        self.export_type_list = []

        self.project = ''

        self.yeti = False

        self.process_list = [] ##プロセスを格納

        self.headers = [" ", "Asset name", "Name space", "Export List", "Top Node", "Asset Path"]
        self.table_row = len(self.headers)
        self.asset_fields = ["code", "sg_namespace", "sg_export_type","sg_top_node", "sg_abc_export_list", "sg_anim_export_list", "sg_asset_path"]

        self.shot_fields = ["code","sg_assets"]

        self.ui = QUiLoader().load(self.ui_path)
        self.setCentralWidget(self.ui)

        debug = ''

        if testRun:
            debug = '__debug__'
        self.setWindowTitle('%s %s %s' % (self.WINDOW, __version__, debug))
        self.setGeometry(500, 200,1000,800)
        self.exportTgtList = []

        self.ui.groupBox.installEventFilter(self)
        self.ui.group_box.installEventFilter(self)

        self.ui.overrideValue_LineEdit.setEnabled(False)
        self.ui.cameraScaleOverride_CheckBox.stateChanged.connect(self.overrideValue_LineEdit_stateChange)
        self.ui.yeti_CheckBox.stateChanged.connect(self.yeti_checker)

        self.ui.Change_Area.setCurrentIndex(0)
        self.ui.check_button.clicked.connect(self.check_button_clicked)
        self.ui.uncheck_button.clicked.connect(self.uncheck_button_clicked)
        self.ui.allcheck_button.clicked.connect(self.allcheck_button_clicked)
        self.ui.alluncheck_button.clicked.connect(self.alluncheck_button_clicked)

        self.ui.start_button.clicked.connect(self.start_button_clicked)
        self.ui.pro_num_CheckBox.stateChanged.connect(self.pro_num_clicked)

        self.ui.proj_comboBox.currentIndexChanged.connect(self.proj_comboBox_changed)

    def eventFilter (self, object, event):
        if event.type() == QEvent.DragEnter:
            event.acceptProposedAction()
            return True

        if event.type() == QEvent.Drop:
            self.drop_act(event)

            camScale = -1

            if self.ui.cameraScaleOverride_CheckBox.isChecked():
                camScale = float(self.ui.overrideValue_LineEdit.text())
            else:
                camScale = -1

            if self.ui.stepValue_CheckBox.isChecked():
                self.stepValue = float(
                    self.ui.stepValue_LineEdit.text())
            else:
                self.stepValue = 1.0


    def stepValue_LineEdit_stateChange(self):
        currentState = self.ui.stepValue_CheckBox.isChecked()
        self.ui.stepValue_LineEdit.setEnabled(currentState)

    def pro_num_clicked(self):
        currentState = self.ui.pro_num_CheckBox.isChecked()
        self.ui.pro_num.setEnabled(currentState)

    def drop_act(self,event):#D&D時に実行される
        self.check_row = []
        self.executed_row = []
        self.quantity = 0
        self.tableData0 = []
        self.inputpath = ''
        self.stepValue = 1.0

        mst = True###MST用

        mimedata = event.mimeData()
        a = mimedata.urls()
        self.inputpath = a[0].toString().replace("file:///", "")

        self.ui.path_line.setText(self.inputpath)
        self.ui.Change_Area.setCurrentIndex(1)

        pro_name = self.inputpath.split('/')[2]
        if mst:
            pro_name = self.inputpath.split('/')[1]

        shot = self.inputpath.split('/')[5]
        cut = self.inputpath.split('/')[6]


        shot_name = shot +'_'+ cut
        if mst:
            shot_name = self.inputpath.split('/')[4] + '_' + shot_name


        self.ui.shot_line.setText(shot)
        self.ui.cut_line.setText(cut)

        self.ui.proj_line.setText(pro_name)

        sg = sg_scriptkey.scriptKey()
        project = sg_util.get_project(pro_name)

        self.project = project[0]['name']

        filters = [["project", "is", project]]
        asset_fields = self.asset_fields
        shot_fields = self.shot_fields

        proj_list = self.set_proj_comboBox()
        if pro_name in proj_list:
            self.ui.proj_comboBox.setCurrentIndex(proj_list.index(pro_name))
            print 'success'
            asset_list = dict()
            asset_list = sg.find('Asset', filters, asset_fields)

            shot_list = dict()
            shot_list = sg.find('Shot', filters, shot_fields)

            count = 0

            target_asset = []
            for x in shot_list:
                if x['code']==shot_name:
                    q = x
                else:
                    pass
            for x in q["sg_assets"]:
                target_asset.append(x['name'])
            print target_asset
            if len(target_asset)>1:###ショットの中にアセットリストがない場合
                pass
            else:
                target_asset_prot_list = sg.find('Sequence',[["project","is", project]],["assets","code"])#ショットフィールド
                target_asset_prot = []#アセットリスト
                for a in target_asset_prot_list:
                    if a['code']==shot_name:
                        for b in a['assets']:
                            target_asset_prot.append('name')
                z = []
                for x in target_asset_prot:
                    if x["code"]==shot_name:
                        for y in x['assets']:
                            z.append(y['name'])
                    else:
                        pass

                target_asset = z

            type_count=0

            exporttype_abclist = sg.find('Asset', filters, ["sg_abc_export_list"])
            exporttype_animlist = sg.find('Asset', filters, ["sg_anim_export_list"])

            ####asset#####
            for item in asset_list:
                print target_asset
                print item['code']
                if item['code'] in target_asset:
                    y = []
                    y.append('')
                    for z in asset_fields:
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
                                    if item[z]=='abc':
                                        y.append(exporttype_abclist[type_count]["sg_abc_export_list"])
                                        self.export_type_list.append('abc')
                                        # y.append("ABCset")
                                    elif item[z]=='anim':
                                        y.append(exporttype_animlist[type_count]["sg_anim_export_list"])
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
                    count = count + 1
                    type_count = type_count + 1
                else:
                    type_count = type_count + 1


            ###asset####


            ###camera###
            y = []
            y.append("")
            y.append("Camera")
            y.append("")
            y.append("")
            y.append("")
            y.append("")

            self.quantity = self.quantity + 1
            count = count + 1
            self.tableData0.append(y)

            self.tableData0[0][0] = ""
            self.ui.all_num.setText(str(self.quantity))

            model = TableModelMaker(self.tableData0, self.headers, self.check_row, self.executed_row)

            self.ui.main_table.setModel(model)
            self.ui.main_table.setColumnWidth(0,25)
            self.ui.start_button.setEnabled(True)

        else:
            print 'Not Much Project_=List'

        return True

    def check_button_clicked(self):
        y = self.ui.main_table.selectedIndexes()
        z = self.check_row

        for x in y:
            z.append(x.row())

        self.check_row = list(set(z))

        self.ui.plan_num.setText((str(len(self.check_row))))

        model = TableModelMaker(self.tableData0, self.headers, self.check_row, self.executed_row)

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

        self.ui.plan_num.setText((str(len(self.check_row))))

        model = TableModelMaker(self.tableData0, self.headers, self.check_row)

        self.ui.main_table.setModel(model)


    def allcheck_button_clicked(self):
        y = self.ui.main_table.selectedIndexes()
        z = self.check_row

        for x in range(self.quantity):
            z.append(x)

        self.check_row = list(set(z))

        model = TableModelMaker(self.tableData0, self.headers, self.check_row, self.executed_row)

        self.ui.main_table.setModel(model)

        self.ui.plan_num.setText(str(self.quantity))

    def alluncheck_button_clicked(self):

        self.check_row = []
        model = TableModelMaker(self.tableData0, self.headers, self.check_row, self.executed_row)

        self.ui.main_table.setModel(model)

        self.ui.plan_num.setText(str(0))

    def proj_comboBox_changed(self):
        self.ui.proj_line.setText(self.ui.proj_comboBox.currentText())

    def tableClicked(self, indexClicked):#Tableクリック時
        self.selectRow = indexClicked.row()

    def overrideValue_LineEdit_stateChange(self):
        currentState = self.ui.cameraScaleOverride_CheckBox.isChecked()
        self.ui.overrideValue_LineEdit.setEnabled(currentState)

    def yeti_checker(self):
        self.yeti = self.ui.yeti_CheckBox.isChecked()

    def start_button_clicked(self):

        if self.ui.pro_num_CheckBox.isChecked:
             pro_num = self.ui.pro_num.value()
        else:
            pro_num = 1

        count = 0

        for x in self.tableData0:
            print x
            if count in self.executed_row:
                pass
            else:
                if count in self.check_row:
                    self.executed_row.append(count)

                    assetname = x[1] #assetname
                    namespace = x[2] #namespace
                    exporttype = x[4] #exporttype
                    topnode = x[3] #top_node
                    assetpath = x[5] #Asset Path

                    ##後で消す
                    # self.inputpath = 'X:/MSTB4/Data/60_SHOT/ep0906/s005/c066/work/k_ueda/layout/maya/scenes/ep0906_s005_c066_layout_v002_001.ma'
                    # assetname = 'ketel'
                    # namespace = 'ketel_evo' #namespace
                    # exporttype = 'basic' #exporttype
                    # topnode = 'root' #top_node
                    # assetpath = 'X:/MSTB4/Data/20_ASSETS/chara/ketel/maya/scenes/ketel_evo_rig_complete_v005.mb' #Asset Path

                    try:
                        y = assetpath.split("assets")[1]
                        z = y.split("/")[1]

                    except:
                        pass
                    self.camScale = -1

                    chara = assetname

                    if self.ui.cameraScaleOverride_CheckBox.isChecked():
                        self.camScale = float(self.ui.overrideValue_LineEdit.text())
                    else:
                        self.camScale = -1

                    # if assetname == 'Camera':
                    #     self.execExportCamera(self.inputpath,self.camScale,test=testRun)
                    # elif self.export_type_list[count] == 'abc':
                    #     self.execExport(chara, self.inputpath, namespace, exporttype,
                    #                     topnode, assetpath, testRun, self.yeti, self.stepValue)
                    # elif self.export_type_list[count] == 'anim':
                    #     self.execExportAnim(chara, self.inputpath, namespace, exporttype,topnode, assetpath, testRun, self.yeti, self.stepValue)

                    self.execExportAnim(chara, self.inputpath, namespace, exporttype,topnode, assetpath, testRun, self.yeti, self.stepValue)


                    util.addTimeLog(chara, self.inputpath, test=testRun)

                else:
                    pass
            count = count + 1

        p = Pool(pro_num)####同時に実行するプロセス
        p.map(process_do,self.process_list)

        self.executed_row = list(set(self.executed_row))
        model = TableModelMaker(self.tableData0, self.headers, self.check_row, self.executed_row)

        print "===============Export End=================="


    def execExport(self, charaName, inputpath, namespace, exporttype, topnode, assetpath, test, yeti, stepValue):
        args = 'C:\\Program Files\\Shotgun\\Python\\python.exe back_starter_abc.py '
        args = args + str(charaName)+' '+str(inputpath)+' '+str(namespace)+' '+str(exporttype)+' ' +str(topnode)+' '+str(assetpath)+' '+str(test)+' '+str(yeti)+' '+str(stepValue)+' '+str(self.project)

        self.process_list.append(args)

    def execExportAnim(self, charaName, inputpath, namespace, exporttype, topnode, assetpath, test, yeti, stepValue):

        args = 'C:\\Program Files\\Shotgun\\Python\\python.exe back_starter_anim.py '
        args = args + str(charaName)+' '+str(inputpath)+' '+str(namespace)+' '+str(exporttype)+' ' +str(topnode)+' '+str(assetpath)+' '+str(test)+' '+str(yeti)+' '+str(stepValue)+' '+str(self.project)

        self.process_list.append(args)

    def execExportCamera(self, inputpath, camScale, test):

        args = 'C:\\Program Files\\Shotgun\\Python\\python.exe back_starter_cam.py '
        args = args + str(inputpath) +' '+ str(camScale) +' '+ str(test)+' '+str(self.project)

        self.process_list.append(args)

    def set_proj_comboBox(self):
        #project 情報を取得してプルダウンメニューに登録
        filters = [['is_template', 'is', False],['sg_status','is','Active']]
        fields = ['name']
        projDict = sg.find('Project', filters, fields)
        projList = []
        self.projInfoDict = {}
        for proj in projDict:
            if proj['name'] == 'Shotgun_test3':
                continue
            projList.append(proj['name'])
            self.projInfoDict[proj['name']] = proj
        projList.sort()
        self.ui.proj_comboBox.addItems(projList)
        return projList

class TableModelMaker(QAbstractTableModel):

    def __init__(self, list, headers = [], check_row = [],executed_row=[], parent = None):
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
        row = index.row()
        column = index.column()


        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role = QtCore.Qt.BackgroundRole):

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
                        t = x.decode("utf-8",errors="ignore")
                        value = t
                    else:
                        value = self.list[row][column]
            else:
                value = self.list[row][column]

            return value

        elif role == QtCore.Qt.BackgroundRole:

            if row in self.executed_row:
                return QtGui.QColor("#888888")
            else:
                if row in self.check_row:
                    return QtGui.QColor("#22FFFF")
                else:
                    return QtGui.QColor("#FFFFFF")

    def setData(self, index, value, role = QtCore.Qt.DisplayRole):
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

def run (*argv):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setStyle('plastique')
    if argv[0][0] == '':
        ui = GUI()
    else:
        ui = GUI(mode=argv[0][0])
    ui.show()

    app.exec_()

def process_do(order):
    print order
    a = subprocess.call(order)

if __name__ == '__main__':
    run(sys.argv[1:])
