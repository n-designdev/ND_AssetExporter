# -*- coding: utf-8 -*-

#------------------------------
__version__ = "0.0.1"
__copyright__ = "Copyright (C) 2016, N-Design"
__author__ = "Masato Hirabayashi"
__credits__ = ["Masato Hirabayashi"]
#------------------------------

#HIRA-----------------------------------
# expandvars from Python/Lib/ntpath.py
#HIRA-----------------------------------

import os

# Expand paths containing shell variable substitutions.
# The following rules apply:
#       - no expansion within single quotes
#       - '$$' is translated into '$'
#       - '%%' is translated into '%' if '%%' are not seen in %var1%%var2%
#       - ${varname} is accepted.
#       - $varname is accepted.
#       - %varname% is accepted.
#       - varnames can be made out of letters, digits and the characters '_-'
#         (though is not verified in the ${varname} and %varname% cases)
# XXX With COMMAND.COM you can use any characters in a variable name,
# XXX except '^|<>='.

def expandvars(path, env=None):
    """Expand shell variables of the forms $var, ${var} and %var%.

    Unknown variables are left unchanged."""

    #HIRA-----------------------------------
    if env is None:
        env = os.environ.copy()
    #HIRA-----------------------------------

    if '$' not in path and '%' not in path:
        return path
    import string
    varchars = string.ascii_letters + string.digits + '_-'
    res = ''
    index = 0
    pathlen = len(path)
    while index < pathlen:
        c = path[index]
        if c == '\'':   # no expansion within single quotes
            path = path[index + 1:]
            pathlen = len(path)
            try:
                index = path.index('\'')
                res = res + '\'' + path[:index + 1]
            except ValueError:
                res = res + path
                index = pathlen - 1
        elif c == '%':  # variable or '%'
            if path[index + 1:index + 2] == '%':
                res = res + c
                index = index + 1
            else:
                path = path[index+1:]
                pathlen = len(path)
                try:
                    index = path.index('%')
                except ValueError:
                    res = res + '%' + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    #HIRA-----------------------------------
                    if var in env:
                        res = res + env[var]
                    else:
                        res = res + '%' + var + '%'
                    #HIRA-----------------------------------
        elif c == '$':  # variable or '$$'
            if path[index + 1:index + 2] == '$':
                res = res + c
                index = index + 1
            elif path[index + 1:index + 2] == '{':
                path = path[index+2:]
                pathlen = len(path)
                try:
                    index = path.index('}')
                    var = path[:index]
                    #HIRA-----------------------------------
                    if var in env:
                        res = res + env[var]
                    else:
                        res = res + '${' + var + '}'
                    #HIRA-----------------------------------
                except ValueError:
                    res = res + '${' + path
                    index = pathlen - 1
            else:
                var = ''
                index = index + 1
                c = path[index:index + 1]
                while c != '' and c in varchars:
                    var = var + c
                    index = index + 1
                    c = path[index:index + 1]
                    #HIRA-----------------------------------
                if var in env:
                    res = res + env[var]
                else:
                    res = res + '$' + var
                    #HIRA-----------------------------------
                if c != '':
                    index = index - 1
        else:
            res = res + c
        index = index + 1
    return res
