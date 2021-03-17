#coding:utf-8
import sys,os
import re
import maya.cmds as cmds
import pymel.core as pm

def search_anim(publish_path, test=False):
    if test:
        tg_dir = "test_charSet"
    else:
        tg_dir = "charSet"
    files = os.listdir(os.path.join(publish_path, tg_dir))
    char_dirs = [os.path.join(publish_path, tg_dir, f) for f in files if os.path.isdir(os.path.join(publish_path, tg_dir, f))]
    anim_dirs = [os.path.join(f, "current", "anim") for f in char_dirs if os.path.exists(os.path.join(f, "current", "anim"))]        
    anim_files = []
    for anim_dir in anim_dirs:
        anim_files.extend([os.path.join(anim_dir, f) for f in os.listdir(anim_dir) if os.path.splitext(f)[-1]==".ma"])
        
    file_name = anim_files[1]
    if os.path.exists(file_name):
        dirname, basename = os.path.split(file_name)
        new_file_name = "{}\\test_{}".format(dirname, basename)
        new_file_name = "{}\\test_{}".format(dirname, basename)
    
def load_modified_anim(file_name)
    with open(file_name, mode = "r") as f:
        read_lines = f.readlines()
    data_lines = []
    # data_lines = data_lines.replace("   ", "Google マップ ")
    for read_line in read_lines[:]:
        if re.match("// connectAttr[a-zA-Z0-9_\'\" :;\s]*", read_line):
            _text = read_line.lstrip("// connectAttr")
            source = _text.split(" ")[0].strip("\"")
            dest = _text.split(" ")[1].strip(":\n;\"\'").replace("\";", "")
            ns = dest.split(":")[0]
            print source
            print dest
            if "blendParent" in dest:
                continue
            cmds.connectAttr("{}_anim:{}".format(ns, source), dest)
        # connectAttr "frontHairKA_ctrl_R_rotateX.output" ":KintaroNml:frontHairKA_ctrl_R.rotateX";
        #     data_lines.append(re.sub("connectAttr([a-zA-Z0-9_\'\" :;\s]*)", "// connectAttr$1", read_line))
        #     # data_lines.append(re.sub("connectAttr[a-zA-Z0-9_\'\" :;]", "#connectAttr[a-zA-Z0-9_\'\" :;]", read_line))
        # with open(new_file_name, mode="w") as f:
        #     f.writelines(data_lines)
       
def all_replace(publish_path):
    refs = delete_anim_refs()
    for ref in refs:
       
if __name__ == '__main__':
    publish_path = "P:\\Project\\D55\\shots\\SR\\SR005\\SR005c009\\publish"
    search_anim(publish_path, test=True)
    