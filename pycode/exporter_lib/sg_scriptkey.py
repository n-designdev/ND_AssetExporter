# -*- coding: utf-8 -*-

def scriptKey():
    import os
    import sys

#shotgun_api3
#https://github.com/shotgunsoftware/python-api

    import exporter_lib.shotgun_api3 as shotgun_api3

#------------------
    SERVER_URL = 'https://nd.shotgunstudio.com'
    SCRIPT_NAME = 'nd_util'
    SCRIPT_KEY = '4f5fcfa189a87921341d4ee21fe0e14a88d6066fa53b68e3703642760aac3294'


    return shotgun_api3.Shotgun(SERVER_URL, SCRIPT_NAME, SCRIPT_KEY)

