# -*- coding: utf-8 -*-
import subprocess
import xbmc
import xbmcaddon
import os
import sys
import platform

reload(sys)
sys.setdefaultencoding('utf-8')
__addon__ = xbmcaddon.Addon('plugin.video.shikionline')
__addondir__ = __addon__.getAddonInfo('path')
if platform.system() == 'Windows':
    path = os.path.join(
        __addondir__, 'resources', 'lib', 'smotret-anime', 'server0.exe')
elif platform.system() == 'Linux':
    path = os.path.join(
        __addondir__, 'resources', 'lib', 'smotret-anime', './server0')
path = path.encode('utf-8')

if __name__ == '__main__':
    try:
        if platform.system() == 'Windows':
            p = subprocess.Popen(path.encode('mbcs'), shell=True)
        elif platform.system() == 'Linux':
            p = subprocess.Popen(path, shell=True)
    except Exception as e:
        print('Exception occured:', e)
        print('Killing server0 process...')
        p.kill()
