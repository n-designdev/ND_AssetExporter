# coding:utf-8
import subprocess
x = ['C:/Program Files/Autodesk/Maya2019/bin/mayabatch.exe',
'-command',
'python("import sys\\;sys.path.append(\'Y:/tool/ND_Tools/DCC/ND_AssetExporter_dev/pycode/maya_lib\')\\;sys.path.append(\'Y:/tool/ND_Tools/DCC/ND_AssetExporter_dev/pycode\')\\;from ndPyLibExportAnim import export_anim_main\\;export_anim_main(**{\'input_path\': \'P:/Project/RAM1/shots/AMA2_ep004/sB444/c007/work/k_ueda/sB444c007_lay_v005.ma\', \'sequence\': \'sB444\', \'export_type\': \'anim\', \'abc_check\': False, \'step_value\': 1.0, \'abc_item\': None, \'shot\': \'c007\', \'frame_range\': False, \'priority\': \'50\', \'group\': \'\', \'anim_item\': \'vernier_A_ctrl,vernier_ctrl\', \'publish_ver_anim_path\': \'P:/Project/RAM1/shots/AMA2_ep004/sB444/c007/publish/test_charSet/vernierNml/v006/anim\', \'namespace\': \'zzz\', \'top_node\': \'root\', \'publish_char_path\': \'P:/Project/RAM1/shots/AMA2_ep004/sB444/c007/publish/test_charSet/vernierNml\', \'scene_timewarp\': True, \'export_item\': {\'anim\': \'vernier_A_ctrl,vernier_ctrl\', \'abc\': None}, \'asset_name\': \'vernierNml\', \'frame_handle\': False, \'pool\': \'\', \'asset_path\': \'P:/Project/RAM1/assets/effect/vernier/vernierNml/publish/Setup/RH/maya/current/vernierNml_Rig_RH.mb\', \'cam_scale\': False, \'project\': \'RAM1\', \'debug\': True})")',
 '-file',
  'P:/Project/RAM1/shots/AMA2_ep004/sB444/c007/work/k_ueda/sB444c007_lay_v005.ma']
# proc = subprocess.run(x, shell=True)
import re
x = '[a-zA-Z0-9:_]*vernierNmlGF[A-Z0-9]*'
y = 'vernierNmlGF'

scene_ns_list = [u'GutsHawkNml', u'cameraGEMINI4K', u'cloudSea', u'gutsFalconFighter', u'skyNml', u'vernierNmlGF', u'vernierNmlGF1']
input_ns_list = ['[a-zA-Z0-9:_]*vernierNml[A-Z0-9]*', '[a-zA-Z0-9:_]*vernierNmlGF[A-Z0-9]*']
