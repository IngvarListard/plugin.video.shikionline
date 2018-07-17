# -*- coding: utf-8 -*-
from operator import itemgetter
import sys
import ast
from urllib import urlencode
from urllib import quote_plus as qp
from urlparse import parse_qsl
import re
import middle
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from data import SearchFilters as sf

_url = sys.argv[0]
_handle = int(sys.argv[1])
# TODO: замена на свои значения
__settings__ = xbmcaddon.Addon(id='plugin.video.shikionline')
locale_type = __settings__.getSetting('locale')

teams_priority = [(i, __settings__.getSetting(
    'prior%s' % i).lower()) for i in range(1, 10)]


#######################################################################
def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively
    from the given set of keyword arguments.
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def alert(title, message):
    """Simple alert's handler."""

    xbmcgui.Dialog().ok(title, message)


def addDirItem(label, action, category, is_folder=True, **kwargs):
    """Adding directory item to a catalogue"""
    item = xbmcgui.ListItem(label=label)
    url = get_url(action=action, category=category, **kwargs)
    xbmcplugin.addDirectoryItem(_handle, url, item, is_folder)


def titlesListGenerator(titles):
    """
    Generator of titles item to a directory. Getting dict of titles.
    """
    # TODO: подкрутить имена, фанарты, прочее
    for title in titles:
        title_name = title['name_ru'].encode('utf-8') if title.get(
            'name_ru') else title['name_en']
        list_item = xbmcgui.ListItem(label=title_name)
        list_item.setArt({
            'thumb': title['poster'],
            'icon': title['poster'],
            'fanart': title['poster']})
        list_item.setInfo('video', {
            'title': title_name,
            'genre': title_name,
            'mediatype': 'video'})
        url = get_url(action='listing', category=title['id'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)


#######################################################################

#######################################################################
def home(page='1'):
    """
    Home page items generator.
    """
    xbmcplugin.setPluginCategory(_handle, 'Shikimori')
    xbmcplugin.setContent(_handle, 'videos')
    lu, isNextPage = middle.getLastUpdates(page=page)

    if page == '1':
        addDirItem('Поиск', 'search', '1')
        addDirItem('Расширенный поиск', 'full_search', 'Full Search')
        addDirItem('Избранное Shikimori', 'selected', 'Избранное')
        addDirItem('Избранное сообществом', 'community', \
                   'Избранное сообществом')

    titlesListGenerator(lu)

    if isNextPage:
        next_page = int(page) + 1
        addDirItem('---Далее---', 'home', '%s' % next_page)
    view_mode_id = 500
    xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)
    xbmcplugin.endOfDirectory(_handle, succeeded=True, updateListing=False, \
                              cacheToDisc=True)


#######################################################################

#######################################################################
def search(page='1', query=''):
    """Simple search by title's name"""
    filter_ = ''
    if int(page) == 1:
        xbmcplugin.setPluginCategory(_handle, 'Search result')
        xbmcplugin.setContent(_handle, 'videos')
        kb = xbmc.Keyboard()
        kb.setDefault('')
        kb.setHeading("Поиск")
        kb.doModal()
        if kb.isConfirmed():
            query = kb.getText()
            filter_ = middle.filter_(page=page, search=query)
    else:
        filter_ = middle.filter_(page=page, search=query)

    if filter_:
        serp, isNext = middle.search(filter_=filter_)
    else:
        return
    titlesListGenerator(serp)

    if isNext:
        next_page = int(page) + 1
        addDirItem('---Далее---', 'search', '%s' % next_page, query=query)

    xbmcplugin.endOfDirectory(_handle)


#######################################################################
######################## SEARCH WITH FILTERS ##########################
#######################################################################
class FiltersHandler(object):
    """Unpack filters from filters_info dict"""

    def __init__(self, filters_info):
        for f in filters_info:
            if filters_info[f] == '0':
                filters_info[f] = ''
        self.name = filters_info['name']
        self.type_ = filters_info['type']
        self.status = filters_info['status']
        self.season = filters_info['season']
        self.genre = filters_info['genre']
        self.score = filters_info['score']
        self.sort_by = filters_info['sort_by']


class SearchWithFilters(object):

    def headDirBuilder(self, params):
        """Head builder of 'search with filter's' catalogue"""

        if params:
            filters_info = ast.literal_eval(params['infostr'])
            fh = FiltersHandler(filters_info)
        else:
            filters_info = {
                'name': '0',
                'type': '0',
                'status': '0',
                'season': '0',
                'genre': '0',
                'score': '0',
                'sort_by': '0'}
            fh = FiltersHandler(filters_info)

        addDirItem('[COLOR green][B]Название:[/B][/COLOR] %s' % fh.name, \
            'dialogSelect', 'name', is_folder=False, infostr=filters_info)
        addDirItem('[COLOR green][B]Тип:[/B][/COLOR] %s' % (
            fh.type_ or 'Все'), 'dialogSelect', 'type', is_folder=False, \
            infostr=filters_info)
        addDirItem('[COLOR green][B]Статус:[/B][/COLOR] %s' % (
            fh.status or 'Все'), 'dialogSelect', 'status', is_folder=False, \
            infostr=filters_info)
        addDirItem('[COLOR green][B]Сезон, год:[/B][/COLOR] %s' % (
            fh.season or 'Все'), 'dialogSelect', 'season', is_folder=False, \
            infostr=filters_info)
        addDirItem('[COLOR green][B]Жанр:[/B][/COLOR] %s' % (
            fh.genre or 'Все'), 'dialogSelect', 'genre', is_folder=False, \
            infostr=filters_info)
        addDirItem('[COLOR green][B]Оценка:[/B][/COLOR] %s' % (
            fh.score or 'Все'), 'dialogSelect', 'score', is_folder=False, \
            infostr=filters_info)
        addDirItem('[COLOR green][B]Сортировать по:[/B][/COLOR] %s' % (
            fh.sort_by or 'По популярности'), 'dialogSelect', 'sort_by', \
            is_folder=False, infostr=filters_info)
        # TODO: func for dis
        addDirItem('[COLOR green][B]Искать[/B][/COLOR]', 'do_search', \
            '1', is_folder=True, infostr=filters_info)


    def filterInfoStrBuilder(self, params):
        """System URL builder for search with filters"""
        query = params['category']
        header = None
        filters_info = ast.literal_eval(params['infostr'])

        if query == 'type':
            header = 'Тип'
            list_items = list(sf.types)
        elif query == 'status':
            header = 'Статус'
            list_items = sf.status.keys()
        elif query == 'season':
            header = 'Сезон, год'
            list_items = sf.seasons.keys()
        elif query == 'genre':
            header = 'Жанр'
            list_items = sf.genres.keys()
            list_items.sort()
        elif query == 'score':
            header = 'Оценка'
            list_items = sf.scores.keys()
        elif query == 'sort_by':
            header = 'Сортировка'
            list_items = sf.sort_type.keys()
            # TODO: Посмотреть как реализуется пропуск рейтинга в shiki
        elif query == 'name':
            kb = xbmc.Keyboard()
            kb.setDefault('')
            kb.setHeading("Поиск по названию")
            kb.doModal()
            if kb.isConfirmed():
                text = kb.getText()
                filters_info[query] = text

        if header:
            dialog = xbmcgui.Dialog()
            dir_items = []
            ret = dialog.select(header, list_items)
            choosen = list_items[ret]
            filters_info[query] = choosen

        url = get_url(action='full_search_with_params', \
                      category='Расширенный поиск', infostr=filters_info)
        return url


def searchWithFilters(params=None, do_search=False):
    xbmcplugin.setPluginCategory(_handle, 'Расширенный поиск')
    xbmcplugin.setContent(_handle, 'videos')
    swf = SearchWithFilters()
    swf.headDirBuilder(params)  # добавление статичной части каталога

    if do_search:
        filters_info = ast.literal_eval(params['infostr'])
        fh = FiltersHandler(filters_info)

        kind = sf.types.get(fh.type_, '')
        status = sf.status.get(fh.status, '')
        season = sf.seasons.get(fh.season, '')
        genre = sf.genres.get(fh.genre, '')
        score = sf.scores.get(fh.score, '')
        sort_by = sf.sort_type.get(fh.sort_by, '')
        search = fh.name

        page = params['category']
        filter_ = middle.filter_(kind=kind, status=status, season=season, \
            genre=genre, score=score, order_by=sort_by, search=search, \
            page=page)
        serp, isNext = middle.search(filter_=filter_)
        titlesListGenerator(serp)
        if isNext:
            next_page = int(page) + 1
            addDirItem('---Далее---', 'do_search', '%s' % next_page, \
                       infostr=filters_info)

    xbmcplugin.endOfDirectory(_handle, succeeded=True, \
                              updateListing=True, cacheToDisc=True)
    xbmc.executebuiltin('Action(Select[3])')


def dialogSelect(params):
    """
    Select dialog for manual selection of episode type
    from context menu.
    """
    swf = SearchWithFilters()
    url = swf.filterInfoStrBuilder(params)
    xbmc.executebuiltin('Container.Update("%s")' % url)


#######################################################################

#######################################################################
def selected():
    """Catalogue of shikimori's choosen titles."""
    xbmcplugin.setPluginCategory(_handle, 'Избранное')
    xbmcplugin.setContent(_handle, 'videos')
    selected_filter = middle.filter_(selected=True)
    selected, isNext = middle.search(filter_=selected_filter)
    titlesListGenerator(selected)
    xbmcplugin.endOfDirectory(_handle, succeeded=True, updateListing=False, \
                              cacheToDisc=True)


#######################################################################

#######################################################################
def communityChoosen():
    """Community choosen directory at home directory."""
    xbmcplugin.setPluginCategory(_handle, 'Избранное')
    xbmcplugin.setContent(_handle, 'videos')
    community_filter = middle.filter_(community_choosen=True)
    community_choosen, isNext = middle.search(filter_=community_filter)
    titlesListGenerator(community_choosen)
    xbmcplugin.endOfDirectory(_handle, succeeded=True, updateListing=False, \
                              cacheToDisc=True)


#######################################################################

#######################################################################
def listVideos(category):
    """
    Create the list of playable videos in the Kodi interface.
    """
    xbmcplugin.setPluginCategory(_handle, category)
    xbmcplugin.setContent(_handle, 'videos')
    eps_list = middle.getEpisodes(category, 'full')
    if eps_list:
        for ep in eps_list:
            item = xbmcgui.ListItem(label=ep['episode'])
            item.setProperty('IsPlayable', 'true')
            url = get_url(action='find_relevant', \
                          category=ep['episode'].encode('utf-8'), \
                          link=ep['episode_link'])

            # контекстное меню
            commands = []
            args = '{}|{}|{}'.format(
                ep['episode'].encode('utf-8'), ep['episode_link'], _handle)
            args = qp(args)
            script = "special://home/addons/plugin.video.shikionline/" \
                     "resources/context/manual_select.py"
            runner = 'XBMC.RunScript({}, {})'.format(script, args)
            name = "Выбрать вручную"
            commands.append((name, runner,))
            item.addContextMenuItems(commands)
            xbmcplugin.addDirectoryItem(_handle, url, item)

        xbmcplugin.endOfDirectory(
            _handle, succeeded=True, updateListing=False, cacheToDisc=True)
    else:
        alert('Упс!', 'Что-то пошло не так! Возможно до этого аниме ' \
                      'добрались правообладатели.')
        xbmcplugin.endOfDirectory(_handle)


#######################################################################

#######################################################################
def findRelevant(url):
    """Find relevant video to playback."""
    ass = None
    if locale_type == 'dub':
        video = middle.getRelevantVideo(url, teams_priority)
    elif locale_type == 'sub':
        vass = middle.getRelevantSubVideo(url)
        if vass:
            video, ass = vass
        else:
            video = None
    if not video:
        alert('Нет локализации', 'Для данной серии отсутствует ' \
            'выбранная локализация типа %s. Вы можете попробовать выбрать ' \
            'эпизод вручную из контекстного меню.' % locale_type)
    play_item = xbmcgui.ListItem(path=video)
    if ass:
        play_item.setSubtitles([ass])
    video = qp(video)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
    if re.search(r'127\.0\.0\.1', video):
        xbmcgui.Dialog().notification('Перемотка не работает', \
            'Для видео с сайта smotret-anime.ru перемотка не работает', \
            xbmcgui.NOTIFICATION_INFO, 5000)


#######################################################################

#######################################################################
def play_video(path):
    """
    Play a video by the provided path.
    """
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


#######################################################################

#######################################################################
def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    """
    params = dict(parse_qsl(paramstring))

    if params:
        if params['action'] == 'search':
            search(params['category'], query=params.get('query', ''))
        elif params['action'] == 'do_search':
            searchWithFilters(params, True)
        elif params['action'] == 'full_search':
            searchWithFilters()
        elif params['action'] == 'full_search_with_params':
            searchWithFilters(params)
        elif params['action'] == 'selected':
            selected()
        elif params['action'] == 'community':
            communityChoosen()
        elif params['action'] == 'listing':
            listVideos(params['category'])
        elif params['action'] == 'home':
            home(params['category'])
        elif params['action'] == 'find_relevant':
            findRelevant(params['link'])
        elif params['action'] == 'play':
            play_video(params['video'])
        elif params['action'] == 'dialogSelect':
            dialogSelect(params)
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        home()


#######################################################################

if __name__ == '__main__':
    router(sys.argv[2][1:])
