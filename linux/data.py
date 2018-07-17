# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

__settings__ = xbmcaddon.Addon(id='plugin.video.shikionline')
smotret_anime_status = __settings__.getSetting('smotret-anime')
smotret_anime = True if smotret_anime_status == 'true' else False
print('SMOTRET-ANIME STATUS IS', smotret_anime)

class SearchFilters:

    types = {
        'Все': '',
        'Сериал': 'tv',
        'Фильм': 'movie',
        'OVA': 'ova',
        'ONA': 'ona',
        'Спешл': 'special'}

    seasons = {
        'Все': '',
        'Лето 2018': 'summer_2018',
        'Весна 2018': 'spring_2018',
        'Зима 2018': 'winter_2018',
        'Осень 2017': 'fall_2017',
        '2018': '2018',
        '2017': '2017',
        '2015-2016': '2015_2016',
        '2010-2014': '2010_2014',
        '2000-2009': '2000_2009',
        '199x': '199x',
        '198x': '198x',
        'Старше': 'ancient'}

    status = {
        'Все': '',
        'Онгоинг': 'ongoing',
        'Законченные': 'released',
        'Последние': 'latest'}

    genres = {
        'Все': '',
        'Сёнен': '27-Shounen',
        'Сёнен Ай': '28-Shounen-Ai',
        'Сейнен': '42-Seinen',
        'Сёдзё': '25-Shoujo',
        'Сёдзё Ай': '26-Shoujo-Ai',
        'Дзёсей': '43-Josei',
        'Комедия': '4-Comedy',
        'Романтика': '22-Romance',
        'Школа': '23-School',
        'Безумие': '5-Dementia',
        'Боевые искусства': '17-Martial-Arts',
        'Вампиры': '32-Vampire',
        'Военное': '38-Military',
        'Гарем': '35-Harem',
        'Демоны': '6-Demons',
        'Детектив': '7-Mystery',
        'Детское': '15-Kids',
        'Драма': '8-Drama',
        'Игры': '11-Game',
        'Исторический': '13-Historical',
        'Космос': '29-Space',
        'Магия': '16-Magic',
        'Машины': '3-Cars',
        'Меха': '18-Mecha',
        'Музыка': '19-Music',
        'Пародия': '20-Parody',
        'Слайс': '36-Slice-of-Life',
        'Полиция': '39-Police',
        'Приключения': '2-Adventure',
        'Психологическое': '40-Psychological',
        'Самураи': '21-Samurai',
        'Сверхъестественное': '37-Supernatural',
        'Спорт': '30-Sports',
        'Супер сила': '31-Super-Power',
        'Ужасы': '14-Horror',
        'Фантастика': '24-Sci-Fi',
        'Фэнтези': '10-Fantasy',
        'Экшн': '1-Action',
        'Эччи': '9-Ecchi',
        'Триллер': '41-Thriller',
        'Хентай': '12-Hentai',
        'Яой': '33-Yaoi',
        'Юри': '34-Yuri'}

    scores = {
        'Все': '',
        'Больше 8': '8',
        'Больше 7': '7',
        'Больше 6': '6'}

    sort_type = {
        'Рейтинг': '',
        'Популярность': 'popularity',
        'Алфавиту': 'name',
        'Дате выхода': 'aired_on'}


class PriorityDataList:

    dub_teams = [
    {'name': 'anidub', 'priority': 1},
    {'name': 'studioband', 'priority': 2},
    {'name': 'anilibria', 'priority': 3},
    {'name': 'shiza', 'priority': 4,},
    {'name': 'onibaku', 'priority': 5},
    {'name': 'anifilm', 'priority': 6},
    {'name': 'animedia', 'priority': 7},
    {'name': 'kansai', 'priority': 8},
    {'name': 'aniplay', 'priority': 9},
    {'name': 'sovetromantica', 'priority': 10}]

    hostings = [
    {'name': 'smotret-anime.ru', 'priority': 1},
    {'name': 'sibnet.ru', 'priority': 2},
    {'name': 'vk.com', 'priority': 3},
    {'name': 'rutube.ru', 'priority': 4},
    {'name': 'myvi.ru', 'priority': 5}]

    _dub_teams = [
    (1, 'anidub'),
    (2, 'studio band'),
    (3, 'anilibria'),
    (4, 'shiza'),
    (5, 'onibaku'),
    (6, 'anifilm'),
    (7, 'animedia'),
    (8, 'kansai'),
    (9, 'aniplay'),
    (10, 'sovetromantica')]

    if smotret_anime:
        _hostings = [
        (1, 'smotret-anime.ru'),
        (2, 'sibnet.ru'),
        (4, 'vk.com'),
        #(5, 'rutube.ru'),
        (3, 'sovetromantica.com')]
    else:
        _hostings = [
        (2, 'sibnet.ru'),
        (4, 'vk.com'),
        #(5, 'rutube.ru'),
        (3, 'sovetromantica.com')]


    if smotret_anime:
        _hostings_for_sub = [
        (1, 'smotret-anime.ru'),
        (3, 'sibnet.ru'),
        (4, 'vk.com'),
        #(5, 'rutube.ru'),
        (2, 'sovetromantica.com')]
    else:
        _hostings_for_sub = [
        (3, 'sibnet.ru'),
        (4, 'vk.com'),
        #(5, 'rutube.ru'),
        (2, 'sovetromantica.com')]

