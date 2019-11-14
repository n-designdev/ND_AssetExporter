# -*- coding: utf-8 -*-

import os,sys
import util
import batch

env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)


def back_starter(a, charaName, inputpath, namespace, exporttypelist, topnode, assetpath, test, yeti, stepValue, project, framerange_output):

    print '##############'*5

    print charaName
    print inputpath
    print namespace
    print exporttypelist
    print topnode
    print assetpath
    print test
    print yeti
    print stepValue
    print project
    print framerange_output

    print '##############'*5

    opc = util.outputPathConf(inputpath, test=test)
    opc.createOutputDir(charaName)

    abcOutput = opc.publishfullabcpath + '/' + charaName + '.abc'
    charaOutput = opc.publishfullpath + '/' + charaName + '.abc'

    abcSet = exporttypelist
    nsChara = namespace

    batch.abcExport(nsChara, abcSet,
                    abcOutput, inputpath, yeti, stepValue, project, framerange_output)

    abcFiles = os.listdir(opc.publishfullabcpath)

    if len(abcFiles) == 0:
        opc.removeDir()
        print 'abc not found'
        return
    print abcFiles
    allOutput = []
    for abc in abcFiles:
        ns = abc.replace(charaName + '_', '').replace('.abc', '')
        if '___' in ns:
            ns = ns.replace('___', ':')

        abcOutput = opc.publishfullabcpath + '/' + abc
        charaOutput = opc.publishfullpath + '/' + abc.replace('abc', 'ma')
        for x in exporttypelist
        batch.abcAttach(assetpath, ns, ns + ':' + topnode, abcOutput, charaOutput, yeti, project)
        allOutput.append([abc.replace('abc', 'ma'), abc])
    opc.makeCurrentDir()

    for output in allOutput:
        print '#' * 20
        print output
        charaOutput = opc.publishcurrentpath + '/' + output[0]
        abcOutput = opc.publishcurrentpath + '/abc/' + output[1]
        batch.repABC(charaOutput, abcOutput, project)

    return 0


if __name__ == '__main__':
    print sys.argv[:]
    back_starter(*sys.argv[:])
