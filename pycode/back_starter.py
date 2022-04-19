# coding: utf-8

import os,sys
import yaml
import shell_lib.util_exporter as util_exporter
import batch
# reload(util_exporter)
# reload(batch)
def back_starter_main(**kwargs):
    # argsdic = yaml.safe_load(kwargs) #kwargsはポインタなので直接代入しない
    argsdic = kwargs
    import pprint
    pprint.pprint(argsdic)
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

    opc = util_exporter.outputPathConf(input_path, export_type=export_type, debug=debug)
    opc.set_char(asset_name)
    opc.ver_inc()
    argsdic['publish_char_path'] = opc.publish_char_path
    print(export_type)
    if export_type == 'anim':
        argsdic['publish_ver_anim_path'] = opc.publish_ver_anim_path
        batch.animExport(**argsdic)
        if override == True:
            return
        anim_files = os.listdir(opc.publish_ver_anim_path)
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
            file_name_space = anim_file.replace('anim_', '').replace('.ma', '')
            ma_ver_path = opc.publish_ver_path + '/' +  file_name_space + '.ma'
            argsdic['ma_ver_path'] = ma_ver_path
            anim_ver_path = opc.publish_ver_anim_path + '/' + anim_file
            argsdic['anim_ver_path'] = anim_ver_path
            publish_current_anim_path = opc.publish_current_anim_path + '/' + anim_file
            argsdic['publish_current_anim_path'] = publish_current_anim_path
            argsdic['file_name_space'] = file_name_space
            ma_current_path = opc.publish_current_path + '/' + file_name_space + '.ma'
            argsdic['ma_current_path'] = ma_current_path
            batch.animReplace(**argsdic)
    if export_type == 'abc' or abc_check == 'True':
        if abc_check == 'True':
            # opc.setCache(asset_name) #opcからオーバーライドしたほうが良さそう
            pass
        argsdic['publish_ver_abc_path'] = opc.publish_ver_abc_path
        batch.abcExport(**argsdic)
        print(opc.publish_ver_abc_path)
        abc_files = os.listdir(opc.publish_ver_abc_path)
        if len(abc_files) == 0:
            opc.remove_dir()
            return
        output_set_list = []
        for abc_file_name in abc_files:
            file_name_space = abc_file_name.replace('.abc', '')
            abc_file = opc.publish_ver_abc_path+"/"+abc_file_name
            ma_file_name = abc_file_name.replace(".abc", ".ma")
            ma_file = opc.publish_ver_path+"/"+ma_file_name
            argsdic['file_namespace'] = file_name_space
            argsdic['ma_ver_file'] = ma_file #.ma
            argsdic['abc_ver_file'] = abc_file #.abc
            batch.abcAttach(**argsdic)
            output_set_list.append([ma_file_name, abc_file_name])
        opc.copy_ver2current()
        for output_set in output_set_list:
            argsdic['ma_current_file'] = opc.publish_current_path + '/' + output_set[0]
            argsdic['abc_file'] = opc.publish_current_abc_path + '/' + output_set[1]
            batch.repABC(**argsdic)
    elif export_type == 'camera':
        argsdic['publish_ver_path'] = opc.publish_ver_path
        oFilename = opc.sequence + opc.shot + '_cam'
        argsdic['ma_cam_path'] =  '{}/{}.ma'.format(opc.publish_ver_path, oFilename)
        # argsdic['anim_cam_path']= '{}/anim/{}_anim.ma'.format(opc.publish_ver_cam_path, oFilename)
        argsdic['abc_cam_path'] = '{}/{}.abc'.format(opc.publish_ver_path, oFilename) #フルパスとファイル名
        argsdic['fbx_cam_path'] = '{}/{}.fbx'.format(opc.publish_ver_path, oFilename) #フルパスとファイル名
        batch.camExport(**argsdic)

        # anim_files = os.listdir(argsdic['anim_cam_path'])
        # if len(anim_files) == 0:
        #     return
        # for anim_file in anim_files:
        #     if '_anim' in cam_file:
        #         file_ns = cam_file.replace('_anim', '').replace('.ma', '')
        #         argsdic['file_name_space'] = file_ns
        #         anim_ver_path = argsdic['anim_cam_path'] + '/' + anim_file_name
        #         argsdic['anim_ver_path'] = anim_ver_path
        #         ma_ver_path = opc.publish_ver_path + '/' +  file_name_space + '.ma'
        #         argsdic['ma_ver_path'] = ma_ver_path
        #         batch.abcAttach(**argsdic)
        #     srcFile = os.path.join(opc.publish_ver_path, cam_file)
            # if srcFile.split('.')[-1] == 'ma':
            #     dstDir = os.path.join(opc.publish_ver_path, '..')
            #     try:
            #         shutil.copy(srcFile, dstDir)
            #     except:
            #         pass
        opc.copy_ver2current()
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


if __name__ == '__main__':
    argslist = sys.argv[:]
    argslist.pop(0) # 先頭はpyファイルなので
    # argsdic = yaml.safe_load(argslist[0])
    str_dict = ''.join(argslist)
    import pprint
    pprint.pprint(yaml.load(str_dict))
    back_starter_main(**yaml.load(str_dict))


# argsdic_str = r'{"asset_name": "NursedesseiDragon", "namespace": "NursedesseiDragon[0-9]*$", "export_item": {"abc": "abc_Root", "anim": "ctrl_set, root, ctrl_allWorld"}, "top_node": "root", "asset_path": "P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiDragon/publish/Setup/RH/maya/current/NursedesseiDragon_Rig_RH.mb", "debug": true, "step_value": 1.0, "export_type": "anim", "project": "RAM1", "frame_range": False, "frame_handle": false, "cam_scale": false, "input_path": "P:/Project/RAM1/shots/ep022/s2227/c008/work/k_ueda/s2227c008_anm_v006.ma", "shot": "c008", "sequence": "s2227", "scene_timewarp": True, "abc_check": false, "priority": "50", "pool": "", "group": ""}'
# # argsdic_str = r'{"asset_name": "camera", "namespace": "False", "export_item": {"abc": "abc_Root", "anim": "ctrl_set, root"}, "top_node": "root", "asset_path": "P:/Project/RAM1/assets/chara/Nursedessei/NursedesseiDragon/publish/Setup/RH/maya/current/NursedesseiDragon_Rig_RH.mb", "debug": true, "step_value": 1.0, "export_type": "camera", "project": "RAM1", "frame_range": False, "frame_handle": false, "cam_scale": false, "input_path": "P:/Project/RAM1/shots/ep022/s2227/c008/work/k_ueda/s2227c008_anm_v006.ma", "shot": "c008", "sequence": "s2227", "scene_timewarp": false, "abc_check": false, "priority": "50", "pool": "", "group": ""}'
# argsdic = yaml.safe_load(argsdic_str)
# back_starter_main(**argsdic)
