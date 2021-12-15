# -*- coding: utf-8 -*-

import sys,os
import re
import shutil
import distutils.dir_util
env_key = 'ND_TOOL_PATH_PYTHON'
ND_TOOL_PATH = os.environ.get(env_key,'Y:/tool/ND_Tools/python')
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\','/')
    if path in sys.path: continue
    sys.path.append(path)
#------------------------------------
import exporter_lib.path as util_path

def symlink(source, link_name):
    import os
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()
            
class outputPathConf(object):
    '''
        init時点ではキャラをセットしない
        setCharを行う必要がある
    '''
    def __init__(self, input_path, export_type=None, debug=False):
        self.input_path = input_path.replace('\\', '/')
        self.export_type = export_type
        self.debug = debug

        self.root_dir = "charSet"
        if self.export_type=="camera":
            self.root_dir = "Cam"
        if self.debug == True:
            self.root_dir = "test_" + self.root_dir

        dic = util_path.get_path_dic(self.input_path)
        self._pro_name = dic['project_name']
        self._shot = dic['shot']
        self._sequence = dic['sequence']
        self._shot_path = ''
        for path_parts in self.input_path.split('/'):
            self._shot_path = self._shot_path + path_parts+'/'
            if path_parts == self._shot:
                break


    def set_char(self, char):
        self._publish_char_path = os.path.join(self._shot_path, 'publish', self.root_dir, char)
        if self.export_type == "cam":
            self._publish_char_path = os.path.join(self._shot_path, 'publish', self.root_dir)

        self._publish_current_path = os.path.join(self._publish_char_path, 'current')
        self._publish_current_anim_path = os.path.join(self._publish_current_path, 'anim')
        self._publish_current_abc_path = os.path.join(self._publish_current_path, 'abc')
        try:
            os.makedirs(self._publish_current_path)
        except Exception as e:
            print(e)

        vers = os.listdir(self._publish_char_path)
        if len(vers) == 0:
            self._current_ver = 'v001'
        else:
            vers.sort()
            current_ver = vers[-1]
            current_ver_num = int(current_ver[1:])
            next_ver_num = current_ver_num + 1
            next_ver = 'v' + str(next_ver_num).zfill(3)
            self._current_ver = next_ver

        self._publish_ver_path = os.path.join(self._publish_char_path, self._current_ver)
        self._publish_ver_anim_path = os.path.join(self._publish_ver_path, 'anim')
        self._publish_ver_abc_path = os.path.join(self._publish_ver_path, 'abc')
        # self._publish_ver_cam_path = os.path.join(self._publish_ver_path,'cam')

        try:
            if not os.path.isdir(self.publish_ver_path):
                os.mkdir(self._publish_ver_path)
                if self.export_type == "anim":
                    if not os.path.isdir(self._publish_ver_anim_path):
                        os.makedirs(self._publish_ver_anim_path)
                elif self.export_type == "abc":
                    if not os.path.isdir(self._publish_ver_abc_path):
                        os.makedirs(self._publish_ver_abc_path)
            # elif export_type == "cam":
            #     os.mkdir(self._publish_ver_cam_path)
        except Exception as e:
            print(e)


    def copy_ver2current(self):
        distutils.dir_util.copy_tree(self._publish_ver_path, self._publish_current_path)
        current_info = os.path.join(self._publish_current_path, 'current_info.txt')
        with open(current_info, 'w') as f:
            f.write("current ver:"+ str(self._current_ver)+"\n")


    def remove_dir(self):
        # 最新verを見に行く
        ver_files = os.listdir(self._publish_ver_path)
        for f in ver_files:
            if '.ma' in f:
                return
        shutil.rmtree(self._publish_ver_path)
        # その後currentの空ならcharから削除
        current_files = os.listdir(self._publish_current_path)
        if len(current_files)==0:
            shutil.rmtree(self._publish_char_path)


    # def set_cache(self, char):
    #     self._publish_char_path = os.path.join(self._shot_path, 'publish', 'cache', char)
    #     if os.path.exists(self._publish_char_path):
    #         self.inc_ver()
    #     else:
    #         try:
    #             os.makedirs(self._publish_char_path)
    #             self.inc_ver()
    #         except:
    #             pass
    #     try:
    #         vers = os.listdir(self._publish_char_path)
    #     except WindowsError as e:
    #         raise ValueError
    #     if len(vers) == 0:
    #         raise ValueError
    #     else:
    #         vers.sort()
    #         self._current_ver = vers[-1]
    #         if vers[0] > vers[-1]:
    #             self._current_ver = vers[0]
    #     self._publish_ver_path = os.path.join(self._publish_char_path, self._current_ver)
    #     self._publish_ver_abc_path = os.path.join(self._publish_ver_path, 'abc')
    #     self._publish_ver_anim_path = os.path.join(self._publish_ver_path, 'anim')
    #     self._publish_ver_cam_path = os.path.join(self._publish_ver_path, 'cam')
    #     self._publish_current_path = os.path.join(self._publish_char_path, 'current')      
    
        
    def overrideShotpath(self, shotpath):
        self._shot_path = shotpath.replace('\\', '/')

    @property
    def sequence (self):
        return self._sequence

    @property
    def shot (self):
        return self._shot

    @property
    def publishpath (self):
        return self._publish_char_path.replace(os.path.sep, '/')

    @property
    def publish_ver_path (self):
        return self._publish_ver_path.replace(os.path.sep, '/')

    @property
    def publish_ver_abc_path (self):
        return self._publish_ver_abc_path.replace(os.path.sep, '/')

    @property
    def publish_ver_anim_path (self):
        return self._publish_ver_anim_path.replace(os.path.sep, '/')

    @property
    def publish_current_path (self):
        return self._publish_current_path.replace(os.path.sep, '/')

    @property
    def publish_ver_cam_path(self):
        return self._publish_ver_cam_path.replace(os.path.sep, '/')

    @property
    def publishshotpath(self):
        return self._shot_path.replace(os.path.sep, '/')

    @property
    def current_ver (self):
        return self._current_ver


def addTimeLog(char, input_path, test):
    from datetime import datetime
    opc = outputPathConf(input_path, char, test)
    try:
        opc.setChar(char)
    except ValueError:
        return
    publishpath = opc.publishpath
    if test is True:
        publishpath = publishpath.replace("char", "test_char")
        publishpath = publishpath.replace("Cam", "test_Cam")
    try:
        with open(os.path.join(publishpath, 'timelog.txt').replace(os.path.sep, '/'), 'a') as f:
            f.write(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
            f.write(' ' + opc.current_ver)
            f.write(' ' + input_path)
            f.write(' ' + os.environ['USERNAME'])
            f.write('\n')
    except Exception as e:
        print(e)
    
