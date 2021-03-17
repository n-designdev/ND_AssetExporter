# -*- coding: utf-8 -*-
import os
import sys

env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key, 'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path:
        continue
    sys.path.append(path)

import ND_lib.shotgun.shotgun_api3.shotgun as shotgun
import ND_lib.shotgun.sg_scriptkey as sg_scriptkey
import ND_lib.shotgun.sg_util as sg_util
import ND_lib.util.path as util_path

reload(shotgun)
sg = sg_scriptkey.scriptKey()
onpath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

class SGProjectClass(object):
    def __init__(self, project, field_codes):
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
        else:
            self.field_dict_list = field_dict
            return field_dict

    def sg_write(self, category, attribute_name, field_code, new_data):
        item_id = self.codekeyed_dict[attribute_name]['id']
        sg.update(category, item_id, {field_code: new_data})

    def get_keying_dict(self, priority_field):
        '''
        特定のコードをキーに格納
        '''
        two_fold_dict = {}
        for dict_piece in self.field_dict_list:
            pri_item = dict_piece[priority_field]
            two_fold_dict[pri_item] = dict_piece
        return two_fold_dict

    def get_keying_list(self, target_field, topic_item):
        '''
        特定のキー:アイテムのリストを返す(重複がありうるので)
        '''
        sp_ls = []
        for dict_piece in self.field_dict_list:
            pri_item = dict_piece[target_field]
            if pri_item == topic_item:
                sp_ls.append(dict_piece)
        return sp_ls


if __name__ == "__main__":
    # SGGen_Proj('mem2')
    asset_fieldcodes = ["code", "sg_namespace", "sg_export_type", "sg_top_node",
                        "sg_abc_export_list", "sg_anim_export_list", "sg_asset_path",
                        "sequences"]
    fa23_class = SGProjectClass("FA23", asset_fieldcodes)
    sg_dict = fa23_class.get_dict("Asset")
    shot_fieldcodes = ['code','shots', 'assets']
    sg_shot = SGProjectClass("FA23", shot_fieldcodes)
    x = sg_shot.get_dict("Shot")
    print x
    # .get_keying_dict("code")
    # print sg_asset.codekeyed_dict['ep0906_s005_c056']['assets']
    import pprint
    # pprint.pprint(x)
