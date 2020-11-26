# -*- coding: utf-8 -*-

import maya.cmds as mc


def ndPyLibStrDeletePrefix (inStr):
    if mc.referenceQuery(inr=inStr)==1:
        pfxRN = mc.referenceQuery(rfn=inStr)
        pfx = pfxRN.replace('RN', '')
        pfxSize = len(pfx)
        inStrSize = len(inStr)
        ret = inStr[pfxSize+2:inStrSize]
    else:
        ret = inStr

    return ret
