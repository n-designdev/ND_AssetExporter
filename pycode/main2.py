# -*- coding: utf-8 -*-

#------------------------------
__version__ = '0.6.13'
__author__ = "Yoshihisa Okano"
#------------------------------


import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import ND_lib.shotgun.shotgun_api3.shotgun as shotgun
import ND_lib.shotgun.sg_scriptkey as sg_scriptkey
import ND_lib.shotgun.sg_util as sg_util
import ND_lib.util.path as util_path
import sys
import os
import shutil

import util
import batch
from importlib import import_module
import subprocess
import back_starter

# import ninaSetup
# import hikalSetup
# import ikkaSetup

#------------------------------------

env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)
#------------------------------------

#Shotgunのスクリプトキーを取得

#------------------------------------
#shotgun_api3
#https://github.com/shotgunsoftware/python-api

reload(shotgun)
sg_scriptkey.scriptKey()

pythonBatch = 'C:\\Program Files\\Shotgun\\Python\\python.exe'

#------------------------------------


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
testRun = True


class GUI (QMainWindow):
    WINDOW = 'mem chara export'

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.ui_path = '.\\gui.ui'

        self.check_row = []  # エクスポート対象
        self.executed_row = []
        self.quantity = 0  # 行数
        self.tableData0 = []  # リスト
        self.inputpath = ''
        self.stepValue = 1.0

        self.yeti = False

        self.headers = [" ", "Asset name", "Name space",
                        "Export List", "Top Node", "Asset list", "Asset Path"]
        self.asset_fields = ["code", "sg_namespace", "sg_export_type",
                             "sg_top_node", "sg_abc_export_list", "sg_anim_export_list", "sg_asset_path"]

        self.shot_fields = ["sg_assets"]

        self.ui = QUiLoader().load(self.ui_path)
        self.setCentralWidget(self.ui)

        debug = ''

        if testRun:
            debug = '__debug__'
        self.setWindowTitle('%s %s %s' % (self.WINDOW, __version__, debug))
        self.setGeometry(500, 200, 1000, 800)
        self.exportTgtList = []

        self.ui.groupBox.installEventFilter(self)
        self.ui.group_box.installEventFilter(self)

        self.ui.overrideValue_LineEdit.setEnabled(False)
        self.ui.cameraScaleOverride_CheckBox.stateChanged.connect(
            self.overrideValue_LineEdit_stateChange)
        self.ui.yeti_CheckBox.stateChanged.connect(self.yeti_checker)

        self.ui.Change_Area.setCurrentIndex(0)
        self.ui.check_button.clicked.connect(self.check_button_clicked)
        self.ui.uncheck_button.clicked.connect(self.uncheck_button_clicked)
        self.ui.allcheck_button.clicked.connect(self.allcheck_button_clicked)
        self.ui.alluncheck_button.clicked.connect(
            self.alluncheck_button_clicked)

        self.ui.start_button.clicked.connect(self.start_button_clicked)

    def eventFilter(self, object, event):
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

    def drop_act(self, event):  # D&D時に実行される
        self.quantity = 0
        self.tableData0 = []
        mimedata = event.mimeData()
        a = mimedata.urls()
        self.inputpath = a[0].toString().replace("file:///", "")

        self.ui.path_line.setText(self.inputpath)
        self.ui.Change_Area.setCurrentIndex(1)

        pro_name = self.inputpath.split('/')[2]
        print pro_name
        # pro_name = 'ND_RnD'

        sg = sg_scriptkey.scriptKey()
        project = sg_util.get_project(pro_name)

        filters = [["project", "is", project]]
        asset_fields = self.asset_fields
        shot_fields = self.shot_fields

        asset_list = dict()
        asset_list = sg.find('Asset', filters, asset_fields)

        shot_list = dict()
        shot_list = sg.find('Shot', filters, shot_fields)

        exporttype_list = sg.find('Asset', filters, ["sg_abc_export_list"])
        print exporttype_list

        count = 0
        for item in asset_list:
            y = []
            y.append('')
            for z in asset_fields:
                if item[z] is None:
                    print z + " is none"
                else:
                    if z == "sg_export_type":
                        if item[z] == 'abc':
                            y.append(
                                exporttype_list[count]["sg_abc_export_list"])
                            # y.append("ABCset")
                        elif item[z] == 'anim':
                            y.append(
                                exporttype_list[count]["sg_anim_export_list"])
                        else:
                            print "export type must \"abc\" or \"anim\" "
                    elif z == "sg_abc_export_list" or z == "sg_anim_export_list":
                        pass
                    else:
                        y.append(item[z])
            count = count + 1

        for item in shot_list:
            x = []
            for z in shot_fields:
                if type(item[z]) is list:
                    x.append(item[z][0]["name"])
                else:
                    x.append(item[z])
            for z in x:
                y.insert(-1, z)

            # print y

            self.tableData0.append(y)
            self.quantity = self.quantity + 1

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

        self.ui.plan_num.setText((str(len(self.check_row))))

        model = TableModelMaker(self.tableData0, self.headers, self.check_row)

        self.ui.main_table.setModel(model)

    def allcheck_button_clicked(self):
        y = self.ui.main_table.selectedIndexes()
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

        count = 0

        for x in self.tableData0:
            print x
            if count in self.executed_row:
                pass
            else:
                if count in self.check_row:
                    self.executed_row.append(count)

                    assetname = x[1]  # assetname
                    namespace_origin = x[2]  # namespace
                    exporttype = x[3]  # exporttype
                    topnode = x[4]  # top_node
                    assetpath = x[6]  # Asset Path

                    namespace = namespace_origin
                    print x

                    print '_______________________'

                    y = assetpath.split("assets")[1]
                    z = y.split("/")[1]

                    chara = z
                    print chara

                    camScale = -1

                    if self.ui.cameraScaleOverride_CheckBox.isChecked():
                        camScale = float(self.ui.overrideValue_LineEdit.text())
                    else:
                        camScale = -1

                    if chara == 'char':
                        self.execExportAnim(
                            chara, self.inputpath, namespace, exporttype, topnode)

                    elif chara == 'BG':
                        self.execExportAnim(
                            bg, self.inputpath, namespace, exporttype, topnode)

                    elif chara == 'Cam':
                        self.execExportCam(self.inputpath, camScale)

                    elif chara in ['LgtSetAddCoreA', 'LgtSetCORin']:
                        self.execExportAnim(chara, self.inputpath)

                    else:
                        self.execExport(chara, self.inputpath, namespace, exporttype,
                                        topnode, assetpath, testRun, self.yeti, self.stepValue)

                    util.addTimeLog(chara, self.inputpath, test=testRun)

                else:
                    pass
            count = count + 1

        self.executed_row = list(set(self.executed_row))
        model = TableModelMaker(
            self.tableData0, self.headers, self.check_row, self.executed_row)

    def execExport(self, charaName, inputpath, namespace, exporttype, topnode, assetpath, test, yeti, stepValue):
        args = 'C:\\Program Files\\Shotgun\\Python\\python.exe back_starter.py '
        args = args + str(charaName)+' '+str(inputpath)+' '+str(namespace)+' '+str(exporttype) + \
            ' ' + str(topnode)+' '+str(assetpath)+' ' + \
            str(test)+' '+str(yeti)+' '+str(stepValue)

        print args

        a = subprocess.Popen(args)

        # back_starter.back_starter('a', charaName, inputpath, namespace,exporttype, topnode, assetpath, test, yeti, stepValue)

    def execExportAnim(self, charaName, inputpath, namespace, exporttype, topnode):
        opc = util.outputPathConf(inputpath, True, test=testRun)
        opc.createOutputDir(charaName)

        abcOutput = opc.publishfullabcpath + '/' + charaName + '.abc'
        charaOutput = opc.publishfullpath + '/' + charaName + '.abc'

        # charaSetup = import_module('setting.'+charaName+'Setup')

        abcSet = ['ABCset']
        nsChara = namespace
        regex = []

        output = opc.publishfullanimpath
        regex = ','.join(regex)
        batch.animExport(output, 'anim', nsChara, regex, inputpath)

        animFiles = os.listdir(opc.publishfullanimpath)
        if len(animFiles) == 0:
            opc.removeDir()
            return
        for animFile in animFiles:
            ns = animFile.replace('anim_', '').replace('.ma', '')
            animOutput = opc.publishfullanimpath + '/' + animFile
            charaOutput = opc.publishfullpath + '/' + ns + '.ma'
            batch.animAttach(assetChara, ns, animOutput, charaOutput)
        opc.makeCurrentDir()

        for animFile in animFiles:
            if animFile[:5] != 'anim_':
                continue
            if animFile[-3:] != '.ma':
                continue
            ns = animFile.replace('anim_', '').replace('.ma', '')
            batch.animReplace(ns, opc.publishcurrentpath + '/anim/' +
                              animFile, opc.publishcurrentpath + '/'+ns+'.ma')

    def execExportCam(self, inputpath, camScale):
        opc = util.outputPathConf(inputpath, test=testRun)
        opc.createCamOutputDir()

        batch.camExport(opc.publishfullpath, opc.sequence +
                        opc.shot+'_cam', camScale, inputpath)
        camFiles = os.listdir(opc.publishfullpath)
        for camFile in camFiles:
            srcFile = os.path.join(opc.publishfullpath, camFile)
            dstDir = os.path.join(opc.publishfullpath, '..')
            try:
                shutil.copy(srcFile, dstDir)
            except:
                pass


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
        row = index.row()
        column = index.column()

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
                return QtGui.QColor("#888888")
            else:
                if row in self.check_row:
                    return QtGui.QColor("#22FFFF")
                else:
                    return QtGui.QColor("#FFFFFF")

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


def run(*argv):
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


if __name__ == '__main__':
    run(sys.argv[1:])
