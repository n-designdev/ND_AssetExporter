# -*- codicng: utf-8 -*-

import os,sys
import yaml
print(yaml.__file__)
import shutil

ND_TOOL_PATH = 'Y:/tool/ND_Tools/python;Y:/tool/ND_Tools/DCC/ND_AssetExport_test/pycode/exporter_lib;Y:/tool/ND_Tools/DCC/ND_AssetExport_test/pycode'
for path in ND_TOOL_PATH.split(";"):
    sys.path.append(path)
import exporter_util
import batch


def back_starter_main(**kwargs):
    # argsdic = yaml.safe_load(kwargs) #kwargsはポインタなので直接代入しない
    argsdic = kwargs
    input_path = argsdic['input_path']
    asset_name = argsdic['asset_name']
    export_type = argsdic['export_type']
    abc_check = argsdic['abc_check']
    debug = argsdic['debug']

    if export_type in ['anim', 'abc']:
        argsdic['anim_item'] = argsdic['export_item']['anim']
        argsdic['abc_item'] = argsdic["export_item"]['abc']

    if 'override_shotpath' in argsdic.keys():
        override = True
    else:
        override = False

    opc = exporter_util.outputPathConf(input_path, export_type=export_type, debug=debug)
    opc.set_char(asset_name)
        
    if export_type == 'anim':
        argsdic['publish_ver_anim_path'] = opc.publish_ver_anim_path
        batch.animExport(**argsdic)
        if override == True:
            return
        anim_files = os.listdir(opc._publish_ver_anim_path)
        if len(anim_files)==0:
            opc.remove_dir()
            return
        for anim_file_name in anim_files:
            file_name_space = anim_file_name.replace('anim_', '').replace('.ma', '')
            argsdic['file_name_space'] = file_name_space
            anim_ver_path = opc.publish_ver_anim_path + '/' + anim_file_name
            argsdic['anim_ver_path'] = anim_ver_path
            ma_ver_path = opc.publish_ver_path + '/' +  file_name_space + '.ma'
            argsdic['ma_ver_path'] = ma_ver_path
            batch.animAttach(**argsdic)

        opc.copy_ver2current()

        for anim_file in anim_files:
            if anim_file[:5] != 'anim_':continue
            if anim_file[-3:] != '.ma':continue
            file_name_space = anim_file_name.replace('anim_', '').replace('.ma', '')
            argsdic['file_name_space'] = file_name_space
            publish_current_anim_path = opc.publish_current_anim_path + '/' + anim_file_name
            argsdic['publish_current_anim_path'] = publish_current_anim_path
            ma_current_path = opc.publish_current_path + '/' + file_name_space + '.ma'
            argsdic['ma_current_path'] = ma_current_path
            batch.animReplace(**argsdic)
    if export_type == 'abc' or abc_check == 'True':
        if abc_check == 'True':
            # opc.setCache(asset_name) #opcからオーバーライドしたほうが良さそう
            pass
        argsdic["export_item"]=abc_item
        argsdic['abcOutput'] = opc._publish_ver_abcpath + "/" + asset_name + '.abc'
        argsdic['abcOutput'] = argsdic['abcOutput'].replace("\\", "/")
        try:
            os.makedirs(opc._publish_ver_abcpath)
        except:
            pass
        # batch.abcExport(**argsdic)
        if override == True:
            return
        abcFiles = os.listdir(opc._publish_ver_abcpath)
        if len(abcFiles) == 0:
            opc.remove_dir()
            print('abc not found')
            return
        allOutput = []
        for abc in abcFiles:
            scene_ns = abc.replace('_abc.abc', '')
            abcOutput = opc.publish_ver_abcpath+"/"+abc
            charaOutput = opc.publish_ver_path+"/"+abc.replace(".abc", ".ma")
            argsdic['scene_ns'] = scene_ns
            argsdic['attachPath'] = charaOutput #.ma
            argsdic['abcOutput'] = abcOutput #.abc
            batch.abcAttach(**argsdic)
            allOutput.append([abc.replace('.abc', '.ma'), abc])
        if override_shotpath == False:
            opc.makeCurrentDir()
            for output in allOutput:
                argsdic['charaOutput'] = opc.publishcurrentpath + '/' + output[0]
                argsdic['abcOutput'] = opc.publishcurrentpath + '/abc/' + output[1]
                batch.repABC(**argsdic)
    elif export_type == 'camera':
        opc.setChar(asset_name)
        argsdic['publishPath'] = opc.publish_ver_path
        oFilename = opc.sequence + opc.shot + '_cam'
        argsdic['camOutput'] = '{}/{}.abc'.format(opc.publish_ver_campath, oFilename) #フルパスとファイル名
        batch.camExport(**argsdic)
        camFiles = os.listdir(opc.publish_ver_campath)
        if len(camFiles) == 0:
            print('camera not found')
            return
        for camFile in camFiles:
            srcFile = os.path.join(opc.publish_ver_path, camFile)
            if srcFile.split('.')[-1] == 'ma':
                dstDir = os.path.join(opc.publish_ver_path, '..')
                try:
                    shutil.copy(srcFile, dstDir)
                except:
                    pass
        opc.makeCurrentDir()
    try:
        opc.addTimeLog()
    except Exception as e:
        print(e)
        
    print('Output directry: {}'.format(opc.publish_ver_path.replace('/','\\')))
    print('=================END===================')


# def strdict_parse(original_string):
#     parsed_dic = {}
#     original_string_iter = iter(original_string)
#     for key, item in zip(original_string_iter, original_string_iter):
#         key = spsymbol_remover(key)
#         item = spsymbol_remover(item, key)
#         parsed_dic[key] = item
#     return parsed_dic


# if __name__ == '__main__':
#     argslist = sys.argv[:]
#     argslist.pop(0) # 先頭はpyファイルなので
#     argsdic = yaml.safe_load(argslist[0])
#     back_starter_main(**argsdic)


argsdic_str = r'{"asset_name": "NursedesseiDragon", "namespace": "NursedesseiDragon[0-9]*$", "export_item": {"abc": "abc_Root", "anim": "ctrl_set, root"}, "top_node": "root", "asset_path": "P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiDragon/publish/Setup/RH/maya/current/NursedesseiDragon_Rig_RH.mb", "debug": true, "step_value": false, "export_type": "anim", "project": "RAM1", "frame_range": false, "frame_handle": false, "cam_scale": false, "input_path": "P:/Project/RAM1/shots/ep022/s2227/c008/work/k_ueda/s2227c008_anm_v006.ma", "shot": "c008", "sequence": "s2227", "scene_timewarp": false, "abc_check": false, "priority": "50", "pool": "", "group": ""}'
argsdic = yaml.safe_load(argsdic_str)
back_starter_main(**argsdic)
