# -*- coding: utf-8 -*-

from ndPyLibAnimGetAnimNodeAndAttr import *
import maya.cmds as cmds
import os

def ndPyLibAnimIOExportContain_main(**kwargs):
    #isFilterCurve, inPfxInfo, inDirPath, inFileName, inForNodes, inForNodesAttr, isCheckAnimCurve, isCheckConstraint, frameRange, bake_anim, scene_timewarp):
    print('================================================')
    isFilterCurve = kwargs['is_filter'] 
    inPfxInfo = kwargs['inPfxInfo'] 
    inDirPath = kwargs['publish_ver_anim_path'] 
    inFileName = kwargs['anim_file_name'] 
    inForNodes = kwargs['pick_nodes'] 
    inForNodesAttr = kwargs['pick_node_and_attrs']
    isCheckAnimCurve = kwargs['is_check_anim_curve'] 
    isCheckConstraint = kwargs['is_check_constraint'] 
    print('================================================')
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
        return

    cmds.select(cl=True)
    for i in range(len(retNodes)/2):
        if cmds.objExists(retNodes[i*2+1]) == 1:
            buf = retNodes[i*2+1].split(':')
            if len(buf) == 2:
                # print retNodes[i*2], buf[1]
                try:
                    rn = cmds.rename(retNodes[i*2+1], buf[1])
                except:
                    rn = retNodes[i*2+1]
                retNodes[i*2+1] = rn
            cmds.select(retNodes[i*2+1], add=True)

    if isFilterCurve:
        cmds.filterCurve()
    else:
        # print '[nd] Not use filterCurve\n'
        pass

    # inFileName = inFileName.replace(":","_")
    fileName = inFileName.split(":")[-1]
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
        print(retNodes[i*2], retNodes[i*2+1])
        cmd = 'connectAttr \"' + retNodes[i*2+1] + '.output\" \":' + inPfxInfo[1] + NS[pfxSw] + retNodes[i*2] + '\";\n'
        # cmd = 'connectAttr \"' + retNodes[i*2+1] + '.output\" \":' + inPfxInfo[1] + NS[pfxSw] + ":".join(node.split(":")[-2:]) + '\" -f ;\n'
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

    # print "org:{}".format(org)
    # print "tmp:{}".format(tmp)
    os.remove(org)
    os.rename(tmp, org)


def addInfoAttr(node, info):
    for key in info.keys():
        try:
            cmds.getAttr(node+'.'+key)
        except:
            cmds.addAttr(node, ln=key, dt='string')
            cmds.setAttr(node+'.'+key, info[key], type='string')
