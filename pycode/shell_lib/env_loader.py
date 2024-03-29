# -*- coding: utf-8 -*-

#------------------------------
import ND_appEnv.lib.util.env_io as util_env
__version__ = "0.0.1"
__copyright__ = "Copyright (C) 2016, N-Design"
__author__ = "Masato Hirabayashi"
__credits__ = ["Masato Hirabayashi"]
#------------------------------

import sys
import os
import yaml
import time

#------------------------------
ND_TOOL_PATH_default = "Y:/tool/ND_Tools/python"

env_key = "ND_TOOL_PATH_PYTHON"
ND_TOOL_PATH = os.environ.get(env_key, ND_TOOL_PATH_default)
for path in ND_TOOL_PATH.split(';'):
    path = path.replace('\\', '/')
    if path in sys.path: continue
    sys.path.append(path)

#------------------------------
import ND_appEnv.env as env_param


#-----------------------------------
#-----------------------------------
def run(args, **kwargs):
    fork = kwargs.get('fork', True)
    # values_ana = ['mem2/maya/2018/amd64/win']
    # values_ana = ['MSTB4/maya/2018/amd64/win']
    # values_ana = ['MST_NS/maya/2018/amd64/win']
    #------------------------------------
    env_key = 'ND_TOOL_PATH_PYTHON'
    ND_TOOL_PATH = os.environ.get(env_key,'Y:/tool/ND_Tools/python')
    for path in ND_TOOL_PATH.split(';'):
        path = path.replace('\\','/')
        if path in sys.path: continue
        sys.path.append(path)
    #------------------------------------

    toolkit_path = "Y:\\tool\\ND_Tools\\shotgun"
    app_launcher_path = "config\\env\\includes\\app_launchers.yml"
    dcc_tools = ["maya", "nuke", "nukex"]


    #プロジェクト名からShotgunの設定を取得する
    project_app_launcher = "%s\\ND_sgtoolkit_%s\\%s" % (toolkit_path, args.lower(), app_launcher_path)

    f = open(project_app_launcher, "r")
    data = yaml.safe_load(f)

    f.close()

    for dcc in dcc_tools:
        for version in data["launch_%s" % dcc]["versions"]:
            args = data["launch_%s" % dcc]["windows_args"]
            if dcc == 'maya':
                renderinfo = version.replace('(','').split(')')

    renderer = renderinfo[1].replace('_','').upper()
    rendver = renderinfo[2]
    ryear = renderinfo[0]
    oe = "_TMP_" + renderer + "_VER"
    os.environ[oe] = rendver

    argslist = args.split(' ')
    args = argslist[0].lower()

    values_ana = [args+'/maya/'+ryear+'/amd64/win']
    app_mode = values_ana.pop(0)
    #-----------------------------------
    filePath = '/'.join([env_param.data_path, "dummy.json"])
    #-----------------------------------
    keys = ["name", "appName", "version", "osType", "osName"]
    values = ["ndesign_base", ".", ".", ".", "."]
    options = app_mode.split('/')
    values[:len(options)] = options
    options = dict(zip(keys, values))

    #-----------------------------------
    envDict = util_env.loadConf(filePath, **options)
    # env = util_env.getEnvDict(envDict, env=os.environ, expand=True)

