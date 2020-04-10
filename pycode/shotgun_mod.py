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


class SGGen_Proj(object):
    def __init__(self, project):
        self.project_name = project
        self.project_code = sg_util.get_project(project)
        self.filters = [["project", "is", self.project_code]]


class SGGen_Cate(SGGen_Proj):
    '''
    カテゴリーを絞ったショットガンの遣り取りをする関数
    フィールドがカテゴリーごとのため実質こちらを使う
    project名
    '''
    # TODO: フィールドを可変、更新を行えるようにする

    def __init__(self, project, category, FieldItems=None):
        super(SGGen_Cate, self).__init__(project)
        self.category = category  # e.g. "Assets"
        if FieldItems == None:
            self.field_codes = ["code"]
        else:
            self.field_codes = FieldItems
        self.field_dict_list = self.sg_get(self.field_codes)

    def sg_get(self, field_items):
        '''
        ショットガンからフィールドの中身を拾ってくる
        '''
        category = self.category
        filters = self.filters
        field_codes = self.field_codes
        try:
            sg_recieveditem = sg.find(category, filters, field_codes)
        except shotgun.Fault:
            raise ValueError('Coudn\'t get from Shotgun....')
        else:
            return sg_recieveditem

    def sg_write(self, attribute_name, field_code, field_data):
        '''
        ショットガンフィールドを書き換える
        新フィールドの対象コードと値のdictが引数
        '''
        category = self.category
        itemid = self.codekeyed_dict[attribute_name]['id']

        go_field_data = field_data
        sg.update(category, itemid, {field_code: go_field_data})

        return 0

    def make_nameddict(self, priority_field):
        '''
        特定のコードをキーに格納
        '''
        twofold_dict = {}
        for dict_piece in self.field_dict_list:
            pri_item = dict_piece[priority_field]
            twofold_dict[pri_item] = dict_piece
        return twofold_dict

    def get_topicitem(self, target_field, topic_item):
        '''
        特定のキー:アイテムのリストを返す(重複がありうるので)
        '''
        sp_ls = []
        for dict_piece in self.field_dict_list:
            pri_item = dict_piece[target_field]
            if pri_item == topic_item:
                sp_ls.append(dict_piece)
        return sp_ls



def printlist_singleline(cent):
    print cent

    ''''''


if __name__ == "__main__":
    # SGGen_Proj('mem2')
    asset_fieldcodes = ["code", "sg_namespace", "sg_export_type", "sg_top_node",
                                       "sg_abc_export_list", "sg_anim_export_list", "sg_asset_path",
                                       "sequences"]
    sg_asset = SGGen_Cate("mem2", "Asset", asset_fieldcodes)
    sg_dict = sg_asset.field_dict_list

    shot_fieldcodes = ['code','shots', 'assets']
    sg_shot = SGGen_Cate("MSTB4", "Shot", shot_fieldcodes)
    x = sg_shot.make_nameddict('code')
    print sg_shot.codekeyed_dict['ep0906_s005_c056']['assets']

