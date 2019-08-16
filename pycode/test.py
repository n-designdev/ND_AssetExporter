


import util
import batch


# scenePath = 'P:\\Project\\mem2\\shots\\roll05\\s139T\\c059\\work\\okano\\tknTest.ma'
scenePath = 'P:\\Project\\mem2\\shots\\roll05\\s139T\\GEN\\work\\okano\\50_FX\\maya\\scenes\\aaa.mb'
opc = util.outputPathConf(scenePath)
opc.createOutputDir('TKN')

output = opc.publishfullpath
regex = ["*_Cntrl","*_Cntrl_01","*_Cntrl_02","*_Cntrl_03","*_Cntrl_04","*Attr_CntrlShape","*Wire","*All_Grp","*_ctrl"]
regex = ','.join(regex)
batch.animExport(output, 'anim', regex, scenePath)