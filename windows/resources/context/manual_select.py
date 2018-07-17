# -*- coding: utf-8 -*-
# Скрипт контекстного меню для реализации ручного выбора типа
# локализации конкретного эпизода из предоставленного на сайте
# списка
import os
import sys
import inspect
try:
    from urllib.parse import unquote_plus as uq
except ImportError:
    from urllib import unquote_plus as uq
import xbmcgui
import xbmcplugin
import xbmc
import re
# добавление каталога для импорта нижеупомянутых модулей
current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
preparent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, preparent_dir)
import shiki
import middle
import data

args = sys.argv[1]
sh = shiki.Shikimori()

def alert(title, message):
    xbmcgui.Dialog().ok(title, message)

def manualSelect(args):
    args = uq(args)
    header, episode_link, handle_ = args.split('|')
    handle_ = int(handle_)
    raw_html = sh.getHTML(episode_link)
    dirty_links = sh.getDirtyEpisodeLinks(raw_html[0], type_='all')
    #hostings = ('sibnet.ru', 'smotret-anime.ru', 'vk.com', \
    #    'sovetromantica.com')
    pr_hosts = data.PriorityDataList
    hostings = [hosting[1] for hosting in pr_hosts._hostings]
    print('HOSTINGS IS', hostings)

    rel_vid_by_hostings = []
    for link in dirty_links:
        if link['hosting'] in hostings:
            rel_vid_by_hostings.append(link)

    f = lambda x: u'({}){}({})'.format(x['type'], x['author'], x['hosting'])
    video_headers = [f(i) for i in rel_vid_by_hostings]
    video_items = []
    for video in video_headers:
        item = xbmcgui.ListItem(label=video)
        item.setProperty('IsPlayeble', 'true')
        video_items.append(item)

    dialog = xbmcgui.Dialog()
    ret = dialog.select(header, video_items)
    selected = rel_vid_by_hostings[ret]
    direct_link = sh.getDirectEpisodeLink(selected['dirty_link'], \
        selected['hosting'])
    if direct_link:
        video, ass = direct_link
        to_play = video_items[ret]
        if ass:
            to_play.setSubtitles([ass])
        if video:
            to_play.setPath(path=video)
        else:
            alert('Что-то пошло не так', 'Невозможно воспроизвести это видео')
            return None

    else:
        alert('Что-то пошло не так', 'Невозможно воспроизвести это видео')
        return None

    xbmc.Player().play(video, listitem=to_play)
    if re.search(r'127\.0\.0\.1', video):
        xbmcgui.Dialog().notification('Перемотка не работает', \
            'Перемотка для этого видео не работает. См. xbmc.ru', \
            xbmcgui.NOTIFICATION_INFO, 5000)

manualSelect(args)
