#coding:utf-8
import os
import distutils.dir_util

def getFiles (path):
    fileDirs = os.listdir(path)
    files = [os.path.join(path,fileDir).replace("\\", "/") for fileDir in fileDirs if os.path.isfile(os.path.join(path, fileDir).replace('\\', '/'))]
    return files


def getDirs (path):
    fileDirs = os.listdir(path)
    dirs = [fileDir for fileDir in fileDirs if os.path.isdir(os.path.join(path, fileDir).replace('\\', '/'))]
    return dirs


def getCharList(charsetpath):
    charsetpath = charsetpath.replace("\\", "/")
    if not os.path.exists(charsetpath):
        raise ValueError('char is not exported')
    charlist = getDirs(charsetpath)
    return charlist


def getCurrentFilesList(charsetpath, mode="ma"):
    charsetpath = charsetpath.replace("\\", "/")
    charList = getCharList(charsetpath)
    currentFiles = []
    if mode=="ma":
        for char in charList:
            if "non_connection_" in char:
                continue
            currentFile = getFiles(os.path.join(charsetpath, char, "current"))
            currentFiles.extend(currentFile)
    elif mode=="anim":
        for char in charList:
            currentFile = getFiles(os.path.join(charsetpath, char, "current", "anim"))
            currentFiles.extend(currentFile)
    return currentFiles


def getCamFilesList(camsetpath):
    camsetpath = os.path.join(camsetpath.replace("\\", "/"), "current", "cam")
    print camsetpath
    if not os.path.exists(camsetpath):
        raise ValueError('camera is not exported')
    print camsetpath
    print os.listdir(camsetpath)
    camFiles = [os.path.join(camsetpath,file_name) for file_name in os.listdir(camsetpath) if str(file_name).split(".")[-1] in ["ma", "mb"]]
    return camFiles


def open_folder(path):
    subprocess.call("explorer {}".format(path.replace("/", "\\")))

            
def check_newest_ver(info_file):
    char_dir = "/".join(info_file.split("/")[:-2])
    char_name = info_file.split("/")[-3]
    with open(info_file, 'r') as f:
        ver = int(str(f.readline().rstrip("\n")).split(":")[-1].lstrip("v"))
    next_ver = ver+1
    next_ver_str = str(next_ver).zfill(3)
    next_dir = char_dir + "/v" + next_ver_str
    if not os.path.exists(next_dir):
        return True
    while(1):
        next_ver = next_ver+1
        next_ver_str = str(next_ver).zfill(3)
        next_dir = char_dir + "/v" + next_ver_str        
        if not os.path.exists(next_dir):
            return next_ver-1
            
            
def copy_main(dir_path):    
    # dir_path = r"P:\Project\RAM1\shots\OP\sOP\c009\publish\test_charSet"
    charFiles = getCurrentFilesList(dir_path, mode="ma")
    info_files = []
    for _file in charFiles:
        if _file.split("/")[-1] == "current_info.txt":
            info_files.append(_file)
    for _file in info_files:
        newest_ver = check_newest_ver(_file)
        if newest_ver is True:
            char_name = _file.split("/")[-3]
            print "{}: is already latest.".format(char_name)
        else:
            newest_dir = os.path.join("/".join(_file.split("/")[:-2]), "v{}".format(str(newest_ver).zfill(3)))
            current_dir = os.path.join("/".join(_file.split("/")[:-2]), "current")
            distutils.dir_util.copy_tree(newest_dir, current_dir)
            with open(_file, 'w') as f:
                f.write("current ver:v{}\n".format(str(newest_ver).zfill(3)))
            char_name = _file.split("/")[-3]
            print "{}: -> ver:{}".format(char_name, str(newest_ver))
    print "=== copy finished. =="
        
