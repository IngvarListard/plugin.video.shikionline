# -*- coding: utf-8 -*-
import heapq
import re
import shiki
from data import PriorityDataList as prior_list

sh = shiki.Shikimori()  # shikimori crawler
#######################################################################
def filter_(**kwargs):
    """For more information about kwargs look
    shiki.Shikimori.searchQueryGenerator"""
    # Переопределение, чтобы не импортировать shiki в main
    return sh.searchQueryGenerator(**kwargs)
#######################################################################

#######################################################################
def getLastUpdates(mode='fast', page=1):
    """
    Returns last updated titles from play.shikimori.
    Full or fast. Full is providing more information, but generate
    lots of requests to the shikimori and take much more time.
    """
    urls = sh.getLastUpdates(page=page)
    raw_html = sh.getHTMLs(urls)
    if not raw_html[0] or not raw_html[1]:
        return None
    titles_tooltip, isNextPage = sh.getTooltipLinks(raw_html)
    if mode == 'fast':
        return titles_tooltip, isNextPage

    elif mode == 'full':
        if len(titles_tooltip) > 1:
            raw_htmls = sh.getHTMLs([i['tooltip'] for i in titles_tooltip])
            titles_params = list(sh.getTitlesParams(raw_htmls))
            for title in titles_tooltip:
                title.update(titles_params.pop(0))
            return titles_tooltip, isNextPage

        elif len(titles_tooltip) == 1:
            raw_html = sh.getHTML(titles_tooltip['tooltip'])
            titles_params = list(sh.getTitlesParams(raw_html))
            for title in titles_tooltip:
                title.update(titles_params.pop(0))
            return titles_tooltip, isNextPage
    else:
        raise ValueError('Wrong parameter mode or page')
#######################################################################

#######################################################################
def search(mode='fast', filter_=''):
    """
    Returns search result.
    Full or fast. 'Full' provides more information, but generate
    lots of requests to the shikimori and take much more time.
    """
    url = sh.search(filter_=filter_)
    raw_html = sh.getHTML(url)
    titles_tooltip, isNextPage = sh.getTooltipLinks(raw_html)

    if mode == 'fast':
        return titles_tooltip, isNextPage

    elif mode == 'full':
        if len(titles_tooltip) > 1:
            raw_htmls = sh.getHTMLs([i['tooltip'] for i in titles_tooltip])
            titles_params = list(sh.getTitlesParams(raw_htmls))
            for title in titles_tooltip:
                title.update(titles_params.pop(0))
            return titles_tooltip, isNextPage

        elif len(titles_tooltip) == 1:
            raw_html = sh.getHTML(titles_tooltip['tooltip'])
            titles_params = list(sh.getTitlesParams(raw_html))
            for title in titles_tooltip:
                title.update(titles_params.pop(0))
            return titles_tooltip, isNextPage
    else:
        raise ValueError('Wrong parameter mode or page')
#######################################################################

#######################################################################
def getEpisodes(id_, mode='fast'):
    """
    Gets title id, returns title's episodes as dict.
    Full or fast. 'Full' provides more information, but generate
    lots of requests to the shikimori and take much more time.
    """
    # TODO: full для тайтлов более 100 серий.
    # Сейчас работает некорректно
    title_url = sh.url + '/' + id_
    if mode == 'fast':
        raw_html = sh.getHTML(title_url)
        eps = sh.getEpisodesLinks(raw_html)
        return eps

    elif mode == 'full':
        title_mal = sh.mal_url + '/' + id_
        shiki_html, mal_html = sh.getHTMLs((title_url, title_mal))
        eps = sh.getEpisodesLinks([shiki_html])
        # тайтл может быть заблокирован на территории РФ, либо
        # попросту не иметь серий.
        if not eps:
            return None
        # если страница по каким-либо причинам не загрузилась
        if not mal_html:
            return eps
        names = sh.getEpisodesNames(mal_html, len(eps))
        # названий серий на MAL'e может не оказаться
        if names:
            for ep in eps:
                # или оказаться меньше, чем фактическое число серий
                # тогда names опустошится раньше окончания цикла
                if len(names) == 0:
                    break
                ep.update(names.pop(0))

        return eps
#######################################################################

#######################################################################
def getVideo(url, locale='dub'):
    dirty_links = sh.getDirtyEpisodeLinks(url, type_=locale)
    rep = dict()
    for ep in dirty_links:
        if re.search('anidub', ep['author'].lower()) and ep.get(
            'hosting') == 'sibnet.ru':
            rep = ep
    direct = sh.getDirectEpisodeLink(rep['dirty_link'], rep['hosting'])
    if direct:
        return direc[0]
    else:
        return direct
#######################################################################

#######################################################################
def getRelevantVideo(url, teams_priority):
    """
    Returns relevant dub video, which selecting job based on
    teams_priority list.
    """

    episode_html = sh.getHTML(url)[0]
    if not episode_html:
        return None
    try:
        dirty_links = sh.getDirtyEpisodeLinks(episode_html, type_='dub')
    except ValueError:
        return None

    # TODO: тут должны быть динамические данные(когда-нибудь)
    dub_prior_heap = teams_priority[:]
    # приоритетная куча с командами озвучки
    heapq.heapify(dub_prior_heap)
    rel_eps = []
    # Поиск по приоритетным командам фандаба
    while len(dub_prior_heap) > 0:
        team = heapq.heappop(dub_prior_heap)
        dlinks_temp = dirty_links[:]
        while len(dlinks_temp) > 0:
            ep = dlinks_temp.pop(0)
            if re.search(team[1], ep['author'].lower()):
                rel_eps.append(ep)
        # Если в списке серий не найдена озвучка с наивысшим
        # приоритетом, тогда поиск ведётся по следующей по приоритету
        if len(rel_eps) == 0:
            continue
        else:
            break

    rel_video_link = str()
    hosting_prior_heap = prior_list._hostings[:]
    heapq.heapify(hosting_prior_heap)
    # Поиск по приоритетным хостингам
    while hosting_prior_heap:
        hosting = heapq.heappop(hosting_prior_heap)
        rel_eps_temp = rel_eps[:]
        while rel_eps_temp:
            ep = rel_eps_temp.pop(0)
            if re.search(hosting[1], ep['hosting']):
                rel_video_link = sh.getDirectEpisodeLink(
                    ep['dirty_link'], ep['hosting'])
            if not rel_video_link:
                continue
            else:
                return rel_video_link[0]

    # Если ничего не найдено, берёт первую попавшуюся с подходящим
    # хостингом
    if not rel_video_link:
        hosting_prior_heap = prior_list._hostings[:]
        heapq.heapify(hosting_prior_heap)
        while hosting_prior_heap:
            hosting = heapq.heappop(hosting_prior_heap)
            dlinks_temp = dirty_links[:]
            while dlinks_temp:
                ep = dlinks_temp.pop(0)
                if re.search(hosting[1], ep['hosting']):
                    rel_video_link = sh.getDirectEpisodeLink(
                        ep['dirty_link'], ep['hosting'])[0]
                    if rel_video_link:
                        return rel_video_link
#######################################################################

#######################################################################
def getRelevantSubVideo(url):
    """
    Returns relevant video with subtitles. Selection based on
    number of views of every localization type of an episode.
    """
    episode_html = sh.getHTML(url)[0]
    if not episode_html:
        return None
    try:
        dirty_links = sh.getDirtyEpisodeLinks(episode_html, type_='sub')
    except ValueError:
        return None

    rel_hostings_list = []
    # получение релевантных хостингов в порядке предпочтительности
    hosting_prior_heap = prior_list._hostings_for_sub[:]
    # создание кучи для приоретизации
    heapq.heapify(hosting_prior_heap)
    # Поиск среди ссылок релевантных хостингов
    while hosting_prior_heap:
        # берёт первый хостинг по приоритету
        hosting = heapq.heappop(hosting_prior_heap)
        dlinks_temp = dirty_links[:]
        while dlinks_temp:
            # сверяет хостинги из грязных ссылок с приоритетом
            # до тех пор пока не найдёт, либо не опустошатся переменные
            ep = dlinks_temp.pop(0)
            print('Checking relevant hosting')
            if re.search(hosting[1], ep['hosting']):
                rel_hostings_list.append(ep)

    # если релевантный хостинг не найден возвращает none
    if not rel_hostings_list:
        return None

    dlinks = [i['dirty_link'] for i in rel_hostings_list]
    raw_htmls = sh.getHTMLs(dlinks)
    n = 0
    # получение количества просмотров для каждого видео
    for video in rel_hostings_list:
        if not raw_htmls[n]:
            video['views'] = None
        views = sh.getEpisodeLocalePopularity(raw_htmls[n])
        video['views'] = views
        n += 1
    # сортировка по количеству просмотров
    for h in rel_hostings_list:
        rel_hostings_list.sort(key = lambda x: x['views'])
        direct_link = ''
    # пока не найдётся прямая ссылка или не истощится переменная
    while rel_hostings_list:
        rel_video = rel_hostings_list.pop()
        dilinks = sh.getDirectEpisodeLink(
            rel_video['dirty_link'], rel_video['hosting'])
        if dilinks:
            direct_link, ass = dilinks
        if direct_link:
            return direct_link, ass

    return None
#######################################################################
