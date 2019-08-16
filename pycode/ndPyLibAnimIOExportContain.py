# -*- coding: utf-8 -*-

from ndPyLibAnimGetAnimNodeAndAttr import *
import maya.cmds as mc
import os

def ndPyLibAnimIOExportContain (isFilterCurve, inPfxInfo, inDirPath, inFileName, inForNodes, isCheckAnimCurve, isCheckConstraint):
    retNodes = []
    addCmd = []

    pfxSw = int(inPfxInfo[0])
    NS = ['', '_', ':', '']

    tmpFile = 'ndExportAnimCurveTmp.ma'

    if pfxSw<3:
        retNodes = ndPyLibAnimGetAnimNodeAndAttr(inForNodes, 2, isCheckAnimCurve, isCheckConstraint)
    else:
        retNodes = ndPyLibAnimGetAnimNodeAndAttr(inForNodes, 0, isCheckAnimCurve, isCheckConstraint)

    if len(retNodes) <= 0:
        message = 'No Animation Nodes!\n' + 'Do you want to continue ?\n'
        resultStr = mc.confirmDialog(title='Confirm', message=message,
            button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if resultStr == 'No':
            mc.confirmDialog(title='Abort', message='Stop export.')
            return

    mc.select(cl=True)
    count = 0
    for i in range(len(retNodes)/2):
        if mc.objExists(retNodes[i*2+1]) == 1:
            buf = retNodes[i*2+1].split(':')
            if len(buf) == 2:
                rn = mc.rename(retNodes[i*2+1], buf[1])
                retNodes[i*2+1] = rn
            mc.select(retNodes[i*2+1], add=True)

    if isFilterCurve:
        mc.filterCurve()
    else:
        print '[nd] Not use filterCurve\n'

    inFileName = inFileName.replace(":","_")

    fileName = inFileName + '.ma'
    filePathName = inDirPath + '/' + fileName

    print '/////////////////////////'
    print inFileName

    print filePathName

    filePathNamex = os.path.dirname(filePathName)

    if not os.path.exists(filePathNamex):
        os.makedirs(filePathNamex)


    mc.file(filePathName, f=True, es=True, typ='mayaAscii', ch=0, chn=0, exp=0, con=0, sh=0) ######ここで止まる

    inc = 0
    # print retNodes
    for i in range(len(retNodes)/2):
        print retNodes[i*2+1], inPfxInfo, NS[pfxSw], retNodes[i*2]
        cmd = 'connectAttr \"' + retNodes[i*2+1] + '.output\" \":' + inPfxInfo[1] + NS[pfxSw] + retNodes[i*2] + '\";\n'
        addCmd.append(cmd)

    try:
        readFileID = open(inDirPath+'/'+fileName, 'r')
        writeFileID = open(inDirPath+'/'+tmpFile, 'w')
        line = readFileID.readline()

        while line:
            if line == '// End of ' + fileName + '\n':
                for c in addCmd:
                    writeFileID.write(c)
                writeFileID.write('// End of '+fileName+'\n')
            else:
                writeFileID.write(line)
            line = readFileID.readline()
    except:
        pass
    finally:
        readFileID.close()
        writeFileID.close()

    org = inDirPath + '/' + fileName
    tmp = inDirPath + '/' + tmpFile

    os.remove(org)
    os.rename(tmp, org)

    ###