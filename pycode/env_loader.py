# -*- coding: utf-8 -*-

#------------------------------
__version__ = "0.0.1"
__copyright__ = "Copyright (C) 2016, N-Design"
__author__ = "Masato Hirabayashi"
__credits__ = ["Masato Hirabayashi"]
#------------------------------

import sys
import os
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
import ND_appEnv.lib.util.env_io as util_env
import ND_appEnv.env as env_param

reload(util_env)
reload(env_param)

#-----------------------------------
#-----------------------------------
def run(args, **kwargs):
    fork = kwargs.get('fork', True)
    values_ana = ['mem2/maya/2018/amd64/win']
    # values_ana = ['MSTB4/maya/2018/amd64/win']
    # values_ana = ['MST_NS/maya/2018/amd64/win']


    # name = args.pop(0)
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
    print envDict

    #-----------------------------------
    env = util_env.getEnvDict(envDict, env=os.environ, expand=True)
    print env

    # #-----------------------------------
    # import subprocess
    # if fork:
    #     args = [u'start', ''] + args

    # # proc = subprocess.Popen(args, shell=True, env=env, close_fds=True)
    # if fork:
    #     return (0)
    # else:
    #     proc.wait()
    #     return (proc.returncode)
    # time.sleep(5)

#-----------------------------------
#-----------------------------------
if __name__ == '__main__':
    run(sys.argv[:])
