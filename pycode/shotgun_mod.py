# -*- coding: utf-8 -*-
import os
import sys
try:
    from importlib import reload
except Exception as e:
    pass
    
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)

import exporter_lib.shotgun_api3.shotgun as shotgun
import exporter_lib.sg_scriptkey as sg_scriptkey
import exporter_lib.sg_util as sg_util
import exporter_lib.path as util_path

reload(shotgun)
sg = sg_scriptkey.scriptKey()
onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

class SGProjectClass(object):
    def __init__(self, project, field_codes):
        self.SGFieldDict = {} 
        self.project_name = project
        self.project_code = sg_util.get_project(project)
        self.filters = [["project", "is", self.project_code]]
        if field_codes == None:
            self.field_codes = ["code"]
        else:
            self.field_codes = field_codes

    def get_dict(self, category):
        try:
            field_dict = sg.find(category, self.filters, self.field_codes)
        except shotgun.Fault:
            raise ValueError('Coudn\'t get from Shotgun....')
        self.SGFieldDict[category] = field_dict
        return field_dict

    def sg_write(self, category, attribute_name, field_code, new_data):
        item_id = self.codekeyed_dict[attribute_name]['id']
        sg.update(category, item_id, {field_code: new_data})

    def get_keying_dict(self, category, priority_field):
        '''
        特定のコードをキーに格納
        '''
        two_fold_dict = {}
        for dict_piece in self.SGFieldDict[category]:
            pri_item = dict_piece[priority_field]
            two_fold_dict[pri_item] = dict_piece
        return two_fold_dict

    def get_keying_list(self, category, target_field, topic_item):
        '''
        特定のキー:アイテムのリストを返す(重複がありうるので)
        '''
        sp_ls = []
        for dict_piece in self.SGFieldDict[category]:
            pri_item = dict_piece[target_field]
            if pri_item == topic_item:
                sp_ls.append(dict_piece)
        return sp_ls