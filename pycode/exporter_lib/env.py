# -*- coding: utf-8 -*-
"""
プロジェクトに依存しない環境を定義する
"""
import sys
import os

dir_tool = os.path.dirname(__file__).replace('\\','/')

#N-DESIGNの基本的なプロジェクトルートパス
root_path = 'P:/Project'
element_path = "P:/Material/Element"

env_temp = os.environ.get('TEMP', 'E:/TEMP')
env_temp = env_temp.replace('\\','/')

"""
Shotgun
"""
shotgun_url = "https://nd.shotgunstudio.com"

"""
Deadline
"""
deadline_path = "C:/Program Files/Thinkbox/Deadline10"
deadlineRepository_path = "Z:/DeadlineRepository10x1"
deadline_bin = "C:/Program Files/Thinkbox/Deadline10/bin"

deadline_webServiceHost = "deadlineweb.win.nd.co.jp"
#deadline_webServiceHost = "\\\\win.nd.co.jp\SAN\Share\DeadlineRepository10"
deadline_webServicePort = 8083
deadline_pulseName = "deadline10pulse"
deadline_pulsePort = 40202

deadline_api = "Z:/DeadlineRepository10x1/api/python"

extension_dic = {'ma':'Maya', 'mb':'Maya', 'nk':'Nuke', 'aep':'AE', 'mov':'Qt', "json":"Json"}
copy_type_dic = {'sequence':'Folder', 'Maya':'Folder', 'Nuke':'File', 'AE':'Folder', 'Qt':'File'}
active_project = ["d49", "diner", "magical", "mash", "mem2", "miracle", "ningyo", "pgm5", "sgm4", "shotguntest"]
maya_renderer = {"mayaSoftware":"sw", "mentalRay":"mr", "vray":"vray", "mayaHardware2":"hw2", "arnold":"arnold", "redshift":"redshift"}

sequence_ext = ["dpx", "exr", "jpg", "png", "tiff", "tif"]
movie_ext = ["mov", "mp4"]


ext_dic = {}
for k, v in extension_dic.items():
    appli_list = ext_dic.setdefault(v, [])
    appli_list.append(k)

python_exe_path = "Y:/pub/Tools/Python27_amd64_vs2010/python.exe"

byday_folder_name = "edit"

ffmpeg_path = "Y:/tool/ND_Tools/utility/ffmpeg/bin/ffmpeg"

'''
sequence_char_patternsとは
commonは収集時に対象となる全てに共通する命名規則（名前<_ or .>4桁数字.拡張子)
収集時：existsが通らない記号が含まれたファイル名をcommonのパターンへ変換
リマップ時：commonのパターンから元のパターンへ再変換してからリマップさせる

pattern：そのノードタイプで使用されるファイルパスの基礎パターン（N_DESIGN規定）
char：そのノードタイプで使用されるファイルパスでフレームナンバーにあてがわれている文字
'''
sequence_char_patterns = {'common':{'pattern':'(.*?)[._]*\d\d\d\d+\.([^\.]+)$'},
                          'VRayVolumeGrid':{'pattern' : '(.*?)[._]*#+\.([^\.]+)$', 'char':'#'},
                          "pgYetiMaya":{'pattern':'(.*?)[._]*%\d\dd+\.([^\.]+)$'}}
