# -*- coding: utf-8 -*-

from ndPyLibAnimGetAnimNodeAndAttr import *
import maya.cmds as cmds
import os

def ndPyLibAnimIOExportContain (isFilterCurve, inPfxInfo, inDirPath, inFileName, inForNodes, inForNodesAttr, isCheckAnimCurve, isCheckConstraint, frameRange, bakeAnim):
    print '================================================'
    print "isFilterCurve: {}".format(isFilterCurve)
    print "inPfxInfo: {}".format(inPfxInfo)
    print "inDirPath: {}:".format(inDirPath)
    print "inFileName: {}:".format(inFileName)
    print "inForNodes: {}".format(inForNodes)
    print "inForNodesAttr: {}".format(inForNodesAttr)  # Attr直指定
    print "isCheckAnimCurve: {}".format(isCheckAnimCurve)
    print "isCheckConstraint: {}".format(isCheckConstraint)
    print '================================================'
    retNodes = []
    addCmd = []

    pfxSw = int(inPfxInfo[0])
    NS = ['', '_', ':', '']

    tmpFile = 'ndExportAnimCurveTmp.ma'

    if pfxSw<3:
        retNodes = ndPyLibAnimGetAnimNodeAndAttr(inForNodes, 2, isCheckAnimCurve, isCheckConstraint)
        if len(inForNodesAttr)!=0:
            retNodes += ndPyLibAnimGetAnimNodeAndAttr(inForNodesAttr, 2, isCheckAnimCurve, isCheckConstraint)
    else:
        retNodes = ndPyLibAnimGetAnimNodeAndAttr(inForNodes, 0, isCheckAnimCurve, isCheckConstraint)
        if len(inForNodesAttr)!=0:
            retNodes += ndPyLibAnimGetAnimNodeAndAttr(inForNodesAttr, 0, isCheckAnimCurve, isCheckConstraint)

    if len(retNodes) <= 0:
        message = 'No Animation Nodes!\n' + 'Do you want to continue ?\n'
        resultStr = cmds.confirmDialog(title='Confirm', message=message,
            button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if resultStr == 'No':
            cmds.confirmDialog(title='Abort', message='Stop export.')
            return

    cmds.select(cl=True)
    count = 0
    for i in range(len(retNodes)/2):
        if cmds.objExists(retNodes[i*2+1]) == 1:
            buf = retNodes[i*2+1].split(':')
            if len(buf) == 2:
                rn = cmds.rename(retNodes[i*2+1], buf[1])
                retNodes[i*2+1] = rn
            cmds.select(retNodes[i*2+1], add=True)

    if bakeAnim:
        animNodes = retNodes[1:len(retNodes):2]
        bakeList = []
        for animNode in animNodes:
            bakeList += mc.listConnections(animNode+'.output', s=False, d=True, p=True)
        ### bakeResult cannot bake 'scene time warp' animation
        for t in range(int(frameRange[0]),int(frameRange[1]+1)):
            mc.currentTime(t)
            currentTime = mc.currentTime(q=True)
            print currentTime
            for bake in bakeList:
                obj, attr = bake.split('.')
                mc.setKeyframe(obj, t=currentTime, at=attr)

    if isFilterCurve:
        cmds.filterCurve()
    else:
        print '[nd] Not use filterCurve\n'

    inFileName = inFileName.replace(":","_")
    fileName = inFileName + '.ma'
    filePathName = inDirPath + '/' + fileName
    filePathNamex = os.path.dirname(filePathName)

    if not os.path.exists(filePathNamex):
        os.makedirs(filePathNamex)

    info = {}
    for i in range(len(retNodes)/2):
        if cmds.objExists(retNodes[i*2+1])==1:
            s = retNodes[i*2+1]
            sn = retNodes[i*2].split(':')[0]
            info['asset'] = sn
            info['ver'] = 'v0.0.0'
            info['tool'] = 'ND_AssetExporter'
            addInfoAttr(s, info)

    cmds.file(filePathName, f=True, es=True, typ='mayaAscii', ch=0, chn=0, exp=0, con=0, sh=0)

    for i in range(len(retNodes)/2):
        node = retNodes[i*2].split('|')[-1]
        # cmd = 'connectAttr \"' + retNodes[i*2+1] + '.output\" \":' + inPfxInfo[1] + NS[pfxSw] + retNodes[i*2] + '\";\n'
        cmd = 'connectAttr \"' + retNodes[i*2+1] + '.output\" \":' + inPfxInfo[1] + NS[pfxSw] + node + '\";\n'
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
    except Exception as e:
        print e
    finally:
        readFileID.close()
        writeFileID.close()
    org = inDirPath + '/' + fileName
    tmp = inDirPath + '/' + tmpFile

    print "org:{}".format(org)
    print "tmp:{}".format(tmp)
    os.remove(org)
    os.rename(tmp, org)


def addInfoAttr(node, info):
    for key in info.keys():
        try:
            cmds.getAttr(node+'.'+key)
        except:
            cmds.addAttr(node, ln=key, dt='string')
            cmds.setAttr(node+'.'+key, info[key], type='string')
