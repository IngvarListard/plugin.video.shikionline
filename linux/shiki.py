# -*- coding: utf-8 -*-
#from builtins import str
from bs4 import BeautifulSoup
import json
import pickle
import os
import re
import requests

try:
    import YDStreamExtractor
except ImportError:
    # for development needs
    import youtube_dl as YDStreamExtractor

try:
    import urllib.parse as urllib
except ImportError:
    import urllib

try:
    import xbmcaddon
    import xbmc
    __addon__ = xbmcaddon.Addon('plugin.video.shikionline')
    __profile__ = __addon__.getAddonInfo('profile')
    userdata = xbmc.translatePath(__profile__).decode('utf-8')
except ImportError:
    # for developpment needs
    __profile__ = os.path.abspath(__file__)

class Shikimori():

    url = 'https://play.shikimori.org/animes'
    url_ = 'https://shikimori.org/animes'
    mal_url = 'http://myanimelist.net/anime'
    headers = {u'User-Agent': u'Mozilla/5.0 (X11; Linux x86_64; rv:59.0) '
        'Gecko/20100101 Firefox/59.0'}
    selected = '/kakie-anime-postmotret'
    community_choosen = '/s/104346-spisok-otbornyh-i-vkusnyh-animeh'

    def getHTML(self, url):
        print('++++++'*5, '\nGetting HTML\n', '++++++'*5)
        try:
            r = requests.get(url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return None
        if r.status_code == 404:
            return None
        return [r]

    def getHTMLs(self, urls):
        print('++++++'*5, '\nGetting HTMLs\n', '++++++'*5)
        with requests.session() as s:
            s.headers.update(self.headers)
            raw = []
            for url in urls:
                try:
                    r = s.get(url)
                    if r.status_code == 404:
                        raw.append(None)
                    else:
                        raw.append(s.get(url))
                except:
                    raw.append(None)
        return raw

    def getLastUpdates(self, page=1):
        """Get las updates from play.shikimori. Asynchronously"""
        page_st = self.url.rstrip('/animes') + '/page/' + str(
            2 * int(page) - 1)
        page_nd = self.url.rstrip('/animes') + '/page/' + str(2 * int(page))
        pages_with_titles = (page_st, page_nd)
        return pages_with_titles


    def search(self, page=1, site='play.shikimori', filter_=str()):
        """Search."""
        # TODO мб стоит раскидать по папкам жанры выдачи community choosen
        if len(filter_) != 0:
            if filter_ in (self.selected, self.community_choosen):
                url = self.url_.rstrip('/animes') + filter_
            else:
                url = 'https://' + site + '.org/animes' + filter_
        else:
            url = 'https://' + site + '.org/animes/page/' + str(page)

        return url

    def getTooltipLinks(self, pages_list):
        """Gets list of htmls, returns list with titles tooltips."""
        titles_list = []
        # Если ответом поисковой выдачи является один тайтл,
        # то движок сайта автоматически перенаправляет на страницу
        # этого тайтла. Нижеследующая проверка написана в этой связи.

        if len(pages_list) == 1:
            final_url = pages_list[0].url.split('/')
            soup_ = BeautifulSoup(pages_list[0].text, 'html.parser')

            if len(final_url) > 0 and final_url[-1] == 'video_online':
                isNext = False
                names = soup_.find('header', {
                    'class': 'head'}).h2.text.split(' / ')
                name_ru = names[0] if len(names) > 1 else None
                name_en = names[0] if len(names) == 1 else names[1]
                year = None
                type_ = None
                try:
                    poster = soup.find('center').find('img').get('src')
                except:
                    poster = None
                middle_dict = {
                    'id': final_url[-2].split('-')[0],
                    'name_ru': name_ru,
                    'name_en': name_en,
                    'poster': poster,
                    'year': year,
                    'type': type_,
                    'tooltip': self.url_ + '/' + final_url[-2] + '/tooltip'}
                titles_list.append(middle_dict)
                return titles_list, isNext

            elif len(final_url) > 0 and soup_.find('div',
                class_='c-description') != None:
                isNext = Flase
                names = soup_.find(
                    'header', {'class': 'head'}).h1.text.split(' / ')
                name_ru = names[0] if len(names) > 1 else None
                name_en = names[0] if len(names) == 0 else names[1]
                year = None
                try:
                    type_ = soup_.find_all(
                        'div', {'class': 'key'})[0].parent.find(
                        'div', {'class': 'value'}).text
                except:
                    type_ = None
                try:
                    poster = soup_.find('img', title=True).get('src')
                except:
                    poster = None

                middle_dict = {
                    'id': final_url[-1].split('-')[0],
                    'name_ru': name_ru,
                    'name_en': name_en,
                    'poster': poster,
                    'year': year,
                    'type': type_,
                    'tooltip': self.url_+ '/' + final_url[-1] + '/tooltip'}
                titles_list.append(middle_dict)
                return titles_list, isNext

        for page in pages_list:
            soup = BeautifulSoup(page.text, 'html.parser')
            entries_list = soup.find_all('article', id=True)
            isNext = True if soup.find('a', {'class': 'next'}) else False

            for title in entries_list:
                try:
                    name_en = title.find('a', class_='name').get('title')
                except AttributeError:
                    try:
                        name_en = title.find('a', class_='name-en').text
                    except AttributeError:
                        name_en = title.find('a', class_='title')
                        name_en = name_en.text if name_en else 'unknown'

                name_ru = title.find('span', class_='name-ru')
                name_ru = name_ru.get('data-text') if name_ru \
                    != None else None
                try:
                    type_ = title.find('span', class_='misc').contents[1].text
                except IndexError:
                    type_ = None
                year = title.find('span', class_='right')
                year = year.text if year != None else None
                tooltip = title.find(class_='cover').get('data-tooltip_url')
                poster = re.sub(r' .+', '', title.find(class_='cover').find(
                    'img', alt=True).get('srcset'))

                middle_dict = {
                    'id': tooltip.split('/')[-2].split('-')[0],
                    'name_ru': name_ru,
                    'name_en': name_en,
                    'type': type_,
                    'poster': poster,
                    'tooltip': tooltip}
                titles_list.append(middle_dict)

        return titles_list, isNext

    def getTitlesParams(self, titles_list):
        """Gets list with tooltips, returns list with titles with params."""

        for title in titles_list:
            soup = BeautifulSoup(title.text, 'html.parser')
            short_descr = soup.find('div', class_='b-prgrph')
            short_descr = short_descr.text if short_descr != None else None
            link = soup.find(class_='data name').get('href')
            link = re.sub(r'//shikimori', r'//play.shikimori', link)
            rating = [i for i in soup.find('div', class_='rating').strings][0]
            title_name = soup.find(class_='data name').get('title')
            info = soup.find('div', {'class': 'inner offset'})
            type_nfo = info.find('div', class_='key', string='Тип:').parent
            title_type = type_nfo.find(
                'div', class_='value').contents[0].text
            year = info.find('div', class_='value').contents[1].text
            poster = re.sub(r' .+', '', soup.find('img', class_='image').get(
                'srcset'))

            try:
                name_ru = soup.find(class_='data name').contents[1]
                name_ru = name_ru.get('data-text') if name_ru \
                    != None else None
            except IndexError:
                name_ru = None
            try:
                name_en = soup.find(class_='data name').contents[0].text
            except AttributeError:
                name_en = name_en if name_en is str else None
            try:
                studio = info.find('div', class_='key', \
                    string='Студия:').parent.find('div', \
                    class_='value').text
            except AttributeError:
                studio = None
            try:
                genre = [i for i in info.find('div', class_='key', \
                    string='Жанры:').parent.find('div', \
                    class_='value').strings]
            except AttributeError:
                genre = [i for i in info.find('div', class_='key', \
                    string='Жанр:').parent.find('div', \
                    class_='value').strings]

            desc_n_rate = {
                'title': title_name,
                'name_en': name_en,
                'name_ru': name_ru,
                'poster': poster,
                'link': link,
                'description': short_descr,
                'rating': rating,
                'genre': genre,
                'year': year,
                'studio': studio,
                'type': title_type}
            yield desc_n_rate

    def searchQueryGenerator(self, kind='', status='', season='', genre='',
        duration='', rating='', score='', mylist='', order_by='', page='',
        search='', selected=False, community_choosen=False):
        """Gets search query params, returns filter's link."""

        if selected and community_choosen:
            raise ValueError('Selected and community_choosen are both True')
        elif selected:
            return self.selected
        elif community_choosen:
            return self.community_choosen
        else:
            kind = '/kind/%s' % kind if len(kind) != 0 else ''
            status = '/status/%s' % status if len(status) != 0 else ''
            season = '/season/%s' % season if len(season) != 0 else ''
            genre = '/genre/%s' % genre if len(genre) !=0 else ''
            duration = '/duration/%s' % duration if len(duration) !=0 else ''
            rating = '/rating/%s' % rating if len(rating) !=0 else ''
            score = '/score/%s' % score if len(score) !=0 else ''
            mylist = '/mylist/%s' % mylist if len(mylist) !=0 else ''
            order_by = '/order-by/%s' % order_by if len(order_by) !=0 else ''
            page = '/page/%s' % page if len(page) !=0 else ''
            search = '?search=' + urllib.quote(search) if len(
                search) != 0 else ''
            filter_ = '{0}{1}{2}{3}{4}{6}{7}{8}{9}{10}'.format(
                kind, status, season, genre, duration, rating, score, mylist,
                order_by, page, search)

            return filter_

    def getEpisodesLinks(self, raw_html):

        soup = BeautifulSoup(raw_html[0].text, 'html.parser')
        eps = soup.find('div', class_='c-anime_video_episodes')
        try:
            num_of_eps = len(eps.find_all(
                'div', class_='b-video_variant'))
        except AttributeError:
            return None

        eps_list = []
        for num in range(1, num_of_eps + 1):
            ep_link = self.url + '/' + raw_html[0].url.split('/')[-2] + \
                '/video_online/' + str(num)
            eps_list.append({
                'episode': 'episode %s' %num,
                'episode_link': ep_link})

        return eps_list

    def getEpisodesNames(self, raw_html, num_of_eps):
        """
        Gets MAL's raw_html of a title.
        Trying to crawl episodes names from it.
        """
        soup = BeautifulSoup(raw_html.text, 'html.parser')
        episodes = soup.find(string='Episodes')
        if episodes == None:
            return None
        elif episodes:
            episodes = episodes.parent.get('href')
        r = requests.get(episodes, headers=self.headers, allow_redirects=True)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            episodes_list = soup.find_all(
                'tr', class_='episode-list-data')[:num_of_eps]
            episodes_names_ = [i.find('td', \
                class_='episode-title').a.text for i in episodes_list]
        except IndexError:
            episodes_names_ = None

        episode_names = []
        num = 1
        for ep in episodes_names_:
            episode_names.append({'episode': '#%s' %num + ' ' + ep})
            num += 1

        return episode_names

    def getEpisodeLocalePopularity(self, raw_html):
        """
        Get html of a certain locale type of an episode,
        returns number of views of it.
        """
        soup = BeautifulSoup(raw_html.text, 'html.parser')
        views_search = soup.find('div', class_='views_count')
        views = views_search.text if views_search else None
        if views:
            views_int = int(views.split(' ')[0])
        else:
            return 0
        return views_int


    def getDirtyEpisodeLinks(self, episode_html, type_='dub'):
        """
        Returns dirty links for choosen type of translation.
        sub, dub, all
        """
        soup = BeautifulSoup(episode_html.text, 'html.parser')

        if type_ == 'all':
            links_list = soup.find('div', {
                'class': 'video-variant-group',
                'data-kind': 'all'})
        elif type_ == 'dub':
            links_list = soup.find('div', {
                'class': 'video-variant-group',
                'data-kind': 'fandub'})
        elif type_ == 'sub':
            links_list = soup.find('div', {
                'class': 'video-variant-group',
                'data-kind': 'subtitles'})

        if not links_list:
            raise ValueError('There is no episodes {} for {}'.format(type_, \
                episode_html.url))
        src_list = []

        for point in links_list:
            link = point.a.get('href')
            number = soup.find('input', {'data-href': True}).get('value')
            try:
                hosting = point.a.find('span', class_='video-hosting').text
            except:
                hosting = 'unknown'
            try:
                author = point.a.find('span', class_='video-author').text
            except:
                author = 'unknown'
            try:
                locale_type = point.a.find('span', class_='video-kind').text
            except:
                locale_type = 'unknown'

            episode_params = {
                    'author': author,
                    'dirty_link': link,
                    'type': locale_type,
                    'hosting': hosting}
            src_list.append(episode_params)

        return src_list

    def getDirectEpisodeLink(self, episode_dirty_link, hosting):
        """
        Gets a dirty link of an episode, returns direct link to
        a video and subtitle link if exist (for smotret-anime).
        """
        # TODO: выбор разрешения.
        with requests.Session() as s:
            s.headers.update(self.headers)
            r = s.get(episode_dirty_link)
            soup = BeautifulSoup(r.text, 'html.parser')
            player = soup.find('div', class_='video-link').a.get('href')

            # для smotret-anime нужны куки. Получение оных
            print('HOSTING IS', hosting)
            if hosting == 'smotret-anime.ru':
                try:
                    with open(os.path.join(
                        userdata, u'cookies.pickle'), 'rb') as f:
                        cookies = pickle.load(f)
                        cookies['ads-blocked'] = '0'
                        s.cookies['watchedPromoVideo'] = '1531058305789'
                        s.cookies['viboomShown2'] = '1531058284737'
                except Exception as e:
                    print('CANT OPEN FILE, EXCEPTION:', e)
                    r = s.get(player)
                    s.cookies['ads-blocked'] = '0'
                    s.cookies['watchedPromoVideo'] = '1531058305789'
                    s.cookies['viboomShown2'] = '1531058284737'
                    cookies = s.cookies
                r = s.get(player, cookies=cookies)
                print('COOKIES IS', cookies)
                print('PROFILE DIR IS:', userdata)
                with open(os.path.join(
                        userdata, u'cookies.pickle'), 'wb') as f:
                    pickle.dump(s.cookies, f)
            else:
                r = s.get(player)
            soup = BeautifulSoup(r.text, 'html.parser')

        if hosting == 'smotret-anime.ru':
            middle_serv = 'http://127.0.0.1:8900/playlist.m3u8?'
            page_url = soup.find('video', {
                'id':'main-video'}).get('data-page-url')
            try:
                srcs = soup.find('video', {'id':'main-video'})['data-sources']
            except TypeError:
                return None
            try:
                ass = soup.find('video', {
                    'id':'main-video'})['data-subtitles']
                ass = 'https://smotret-anime.ru/' + ass
            except TypeError:
                ass = None

            print('src is', srcs)
            srcs_json = json.loads(srcs)
            print('json_is', srcs_json)
            urls = srcs_json[0]['urls']  # 0 здесь значит лучшее кач-во
            if len(urls) > 1:  # если ссылок на эп. больше чем 1
                serv_request = middle_serv + '+'.join(urls)
                return serv_request, ass

            elif len(urls) == 1:
                if re.search(r'\.big\-sword', urls[0]):
                    #rpage = requests.get(page_url, headers=self.headers)
                    #sasoup = BeautifulSoup(rpage.text, 'html5lib')
                    #cards = sasoup.find('div', {
                    #    'class': 'card-content m-translation-view-download'})
                    #if cards:
                    #    url = cards.find_all('a')[0].get('href')
                    #    return url, ass
                    serv_request = middle_serv + urls[0]
                    return serv_request, ass
                return urls[0], ass

            else:
                return None

        elif hosting == 'vk.com':
            YDStreamExtractor.disableDASHVideo(True)
            vid = YDStreamExtractor.getVideoInfo(player, quality=1)
            if not vid:
                return None
            stream_url = vid.streamURL()
            print('RUTUBE STREAM URL', stream_url)
            return (stream_url, None)

        elif hosting == 'sibnet.ru':
            sibnet = 'http://video.sibnet.ru'
            script = soup.find('script', type='text/javascript',
                charset=None, src=None).text
            m3u8_link = re.findall(r',{src: "(.+.m3u8)", type', script)
            if not m3u8_link:
                return None
            surl = sibnet + m3u8_link[0]
            return (surl, None)

#        elif hosting == 'myvi.ru':
#            script = soup.find_all('script')[-1]
#            dirty_url = re.findall(r'v=(.+?)\\', script.text)[0]
#            murl = urllib.unquote(dirty_url)
#            return murl

        elif hosting == 'animedia.tv':
            # Как-нибудь в следующий раз
            return None

        elif hosting == 'mail.ru':
            return None

        elif hosting == 'sovetromantica.com':
            script = soup.body.script
            link = re.search(r'player\.src\(.+?\)', script.string)
            url = None
            if link:
                url = link.group()
                url = url.strip('player.src(\'').rstrip('\')')
            else:
                src = soup.body.video.source
                url = src.get('src') if src else None
            if not url:
                return None
            return (url, None)

        else:
            return None
