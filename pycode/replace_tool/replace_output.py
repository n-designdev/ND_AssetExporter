#coding:utf-8
import sys,os
import shutil
import re

def ref_main(file_name):
    if os.path.exists(file_name):
        dirname, basename = os.path.split(file_name)
        new_file_name = "{}\\test_{}".format(dirname, basename)
        with open(file_name, mode = "r") as f:
            read_lines = f.readlines()
        data_lines = []
        for read_line in read_lines[:]:
            data_lines.append(re.sub("connectAttr([a-zA-Z0-9_\'\" :;\s]*)", "// connectAttr\\1", read_line))
        with open(new_file_name, mode="w") as f:
            f.writelines(data_lines)
                
            
# if __name__ == '__main__':
#     file_name = "P:\\Project\\D55\\shots\\SR\\SR005\\SR005c009\\publish\\test_charSet\\KintaroNml\\current\\anim\\anim_KintaroNml.ma"
#     ref_main(file_name)