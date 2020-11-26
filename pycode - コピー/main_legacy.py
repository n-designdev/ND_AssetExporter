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
sg_scriptkey.scriptKey()


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
testRun = True



class GUI (QMainWindow):
    WINDOW = 'mem chara export'
    def __init__ (self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.ui_path = '.\\gui.ui'

        self.check_row = []#エクスポート対象
        self.quantity = 0 #行数
        self.tableData0 = [] #リスト
        self.inputpath = ''
        self.stepValue = 1.0

        self.yeti = False

        self.headers = [" ", "Asset name", "Name space", "Export Type", "Top Node","Asset list", "Asset Path"]
        self.asset_fields = ["code", "sg_namespace", "sg_export_type",
                             "sg_top_node", "sg_abc_export_list", "sg_anim_export_list", "sg_asset_path"]

        self.shot_fields = ["sg_assets"]

        self.ui = QUiLoader().load(self.ui_path)
        self.setCentralWidget(self.ui)

        debug = ''

        if testRun:
            debug = '__debug__'
        self.setWindowTitle('%s %s %s' % (self.WINDOW, __version__, debug))
        self.setGeometry(500, 200,1000,800)
        self.exportTgtList = []

        self.ui.groupBox.installEventFilter(self)
        self.ui.main_table.installEventFilter(self)

        self.ui.overrideValue_LineEdit.setEnabled(False)
        self.ui.cameraScaleOverride_CheckBox.stateChanged.connect(self.overrideValue_LineEdit_stateChange)
        self.ui.yeti_CheckBox.stateChanged.connect(self.yeti_checker)

        self.ui.Change_Area.setCurrentIndex(0)
        self.ui.check_button.clicked.connect(self.check_button_clicked)
        self.ui.uncheck_button.clicked.connect(self.uncheck_button_clicked)
        self.ui.allcheck_button.clicked.connect(self.allcheck_button_clicked)
        self.ui.alluncheck_button.clicked.connect(self.alluncheck_button_clicked)



        self.ui.start_button.clicked.connect(self.start_button_clicked)

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

    def drop_act(self,event):#D&D時に実行される
        mimedata = event.mimeData()
        a = mimedata.urls()
        self.inputpath = a[0].toString().replace("file:///", "")

        self.ui.path_line.setText(self.inputpath)
        self.ui.Change_Area.setCurrentIndex(1)

        # pro_name = self.inputpath.split('/')[2]
        pro_name = 'ND_RnD'

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
        # print b["sg_abc_export_list"]

        count = 0
        for item in asset_list:
            y =  []
            y.append('')
            for z in asset_fields:
                if item[z] is None:
                    print z + " is none"
                else:
                    if z == "sg_export_type":
                        if item[z]=='abc':
                            y.append(exporttype_list[count]["sg_abc_export_list"])
                        elif item[z]=='anim':
                            y.append(exporttype_list[count]["sg_anim_export_list"])
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
                y.insert(-1,z)

            # print y

            self.tableData0.append(y)
            self.quantity = self.quantity + 1

        self.tableData0[0][0] = ""
        self.ui.all_num.setText(str(self.quantity))

        model = TableModelMaker(self.tableData0, self.headers, self.check_row)

        self.ui.main_table.setModel(model)
        self.ui.main_table.setColumnWidth(0,25)
        self.ui.start_button.setEnabled(True)

        return True

    def check_button_clicked(self):
        y = self.ui.main_table.selectedIndexes()
        z = self.check_row

        for x in y:
            z.append(x.row())

        self.check_row = list(set(z))

        self.ui.plan_num.setText((str(len(self.check_row))))

        model = TableModelMaker(self.tableData0, self.headers, self.check_row)

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

        model = TableModelMaker(self.tableData0, self.headers, self.check_row)

        self.ui.main_table.setModel(model)

        self.ui.plan_num.setText(str(self.quantity))

    def alluncheck_button_clicked(self):

        self.check_row = []
        model = TableModelMaker(self.tableData0, self.headers, self.check_row)

        self.ui.main_table.setModel(model)

        self.ui.plan_num.setText(str(0))

    def tableClicked(self, indexClicked):#Tableクリック時
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
            if count in self.check_row:
                assetname = x[1] #assetname
                namespace_origin = x[2] #namespace
                exporttype = x[3] #exporttype
                topnode = x[4] #top_node
                assetpath = x[6] #Asset Path

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

                if chara == 'char':#######################################あとでcharaになおす
                    self.execExportAnim(chara, self.inputpath, namespace, exporttype, topnode)

                elif chara == 'BG':
                    self.execExportAnim(bg, self.inputpath, namespace, exporttype,topnode)

                elif chara == 'Cam':
                    self.execExportCam(self.inputpath, camScale)

                elif chara in ['LgtSetAddCoreA', 'LgtSetCORin']:
                    self.execExportAnim(chara, self.inputpath)

                else:
                    self.execExport(chara, self.inputpath, namespace, exporttype, topnode, assetpath)

                util.addTimeLog(chara, self.inputpath, test=testRun)

            else:
                pass
            count = count + 1


    def execExport(self, charaName, inputpath, namespace, exporttype, topnode, assetpath):
        opc = util.outputPathConf(inputpath, test=testRun)
        opc.createOutputDir(charaName)

        abcOutput = opc.publishfullabcpath + '/' + charaName + '.abc'
        charaOutput = opc.publishfullpath + '/' + charaName + '.abc'

        abcSet = ['ABCset']
        nsChara = namespace
        batch.abcExport(nsChara, abcSet,
                        abcOutput, inputpath, self.yeti, self.stepValue)

        abcFiles = os.listdir(opc.publishfullabcpath)
        if len(abcFiles) == 0:
            opc.removeDir()
            return
        print abcFiles
        allOutput = []
        for abc in abcFiles:
            ns = abc.replace(charaName+'_', '').replace('.abc', '')
            if '___' in ns:
                ns = ns.replace('___', ':')

            abcOutput = opc.publishfullabcpath + '/' + abc
            charaOutput = opc.publishfullpath + '/' + abc.replace('abc', 'ma')
            batch.abcAttach(assetpath, ns, ns+':' +
                            topnode, abcOutput, charaOutput)
            allOutput.append([abc.replace('abc', 'ma'), abc])
        opc.makeCurrentDir()

        for output in allOutput:
            print '#' * 20
            print output
            charaOutput = opc.publishcurrentpath + '/' + output[0]
            abcOutput = opc.publishcurrentpath + '/abc/' + output[1]
            batch.repABC(charaOutput, abcOutput)

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
            batch.animAttach(assetChara, ns,animOutput, charaOutput)
        opc.makeCurrentDir()

        for animFile in animFiles:
            if animFile[:5] != 'anim_':
                continue
            if animFile[-3:] != '.ma':
                continue
            ns = animFile.replace('anim_', '').replace('.ma', '')
            batch.animReplace(ns, opc.publishcurrentpath + '/anim/' + animFile, opc.publishcurrentpath + '/'+ns+'.ma')

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

    def __init__(self, list, headers = [], check_row = [], parent = None):
        self.check_row = check_row
        QAbstractTableModel.__init__(self, parent)
        self.list = list
        self.headers = headers

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

            if column == 0 and row in self.check_row:
                x = "◎"
                t = x.decode("utf-8",errors="ignore")
                value = t
            else:
                value = self.list[row][column]

            return value

        elif role == QtCore.Qt.BackgroundRole:

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

if __name__ == '__main__':
    run(sys.argv[1:])
