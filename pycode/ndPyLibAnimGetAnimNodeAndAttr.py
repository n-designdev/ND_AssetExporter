# -*- coding: utf-8 -*-


import maya.cmds as mc
from ndPyLibStrDeletePrefix import *


def ndPyLibAnimGetAnimNodeAndAttr (inForNodes, inMode, isCheckAnimCurve, isCheckConstraint):
    retNodes = []

    if (inMode >= 0 and inMode <= 3) and len(inForNodes)>0:
        retNodes = ndPyLibAnimGetAnimNodeAndAttrFunc(inForNodes, inMode, isCheckAnimCurve, isCheckConstraint)
    else:
        mc.confirmDialog(title='Error...', message='Please select the mode that 0-3 is correct or node is zero.')
        mc.error('[nd] Please select the mode that 0-3 is correct or node is zero.\n')
    return retNodes

def _GetAnimNodeAndAttrFunc (inNode, inMode):
    retNodes = []
    nodes = []
    nodeAttr = []
    animCurve = ['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU']
    count = flag = 0

    for l in animCurve:
        flag = 1
        nodes = []

        nodes = mc.listConnections(inNode, c=True, type=l)
        if nodes is not None:
            if inMode == 0 or inMode == 2:
                for k in range(0, len(nodes)):
                    if inMode == 0:
                        retNodes.append(nodes[k])
                    else:
                        if len(nodeAttr)>1:
                            print '[nd] ASSERT!!\n'
                            nodeAttr = nodes[k].split('.')
                            delPfxNode = ndPyLibStrDeletePrefix(nodeAttr[0])
                            retNodes[count] = delPfxNode + '.' + nodeAttr[1]
                        else:
                            delPfxNode = ndPyLibStrDeletePrefix(nodes[k])
                            retNodes[count] = delPfxNode
                    count+=1
            elif inMode == 1 or inMode == 3:
                for k in range(len(nodes)):
                    if flag == 1:
                        if inMode == 1:
                            retNodes[count] = nodes[k]
                        else:
                            nodeAttr = nodes[k].split('.')
                            delPfxNode = ndPyLibStrDeletePrefix(nodeAttr[0])
                            retNodes[count] = delPfxNode + '.' + nodeAttr[1]
                        
                        flag = 0
                        count+=1
                    else:
                        flag = 1
    return retNodes

def ndPyLibAnimGetAnimNodeAndAttrFunc (inForNodes, inMode, isCheckAnimCurve, isCheckConstraint):
    retNodesAll = []
    retNodes = []

    listNoAnimCurveNode = []
    listNoAnimCurveNodeCnt = 0
    listConstraintConnectNode = []
    listConstraintConnectNodeCnt = 0

    for j in range(len(inForNodes)):
        checkNode = inForNodes[j]

        if isCheckConstraint:
            print 'no implement'

        retNodes = _GetAnimNodeAndAttrFunc(checkNode, inMode)

        if isCheckAnimCurve and len(retNodes) <= 0:
            listNoAnimCurveNode.append(checkNode)
            listNoAnimCurveNodeCnt += 1
            mc.setKeyframe(checkNode, breakdown=0, hierarchy='none', controlPoints=0, shape=0)
            retNodes = _GetAnimNodeAndAttrFunc(checkNode, inMode)
            if len(retNodes) <= 0:
                print '[nd] Error No Animation Node.\n'

        retNodesAll += retNodes

        if isCheckAnimCurve or isCheckConstraint:
            message = ''
            if isCheckAnimCurve:
                if listNoAnimCurveNodeCnt>0:
                    message = '[No Animation Node(setKeyframe):] \n' + '\n'.join(listNoAnimCurveNode)
                else:
                    message = '[No Animation Node:] Nothing'
            else:
                message = '[No Animation Node:] No Check'
            message = message + '\n\n'
            
            if isCheckConstraint:
                if listConstraintConnectNodeCnt>0:
                    message = message + '[Constraint Connect Node:] \n' + '\n'.join(listConstraintConnectNode)
                else:
                    message = message + '[Constraint Connect Node:] Nothing'
            else:
                message = message + '[Constraint Connect Node:] No Check'
            message = message + '\n'

            ### result
    
    return retNodesAll
            