# 0.0.1

## shiki.Shikimori()

### getHTML(url)

Загружает ссылку через requests.get. Возвращает requests response object как список -- 

_Структура выходных данных_:
```python
[<Response 200>]
```
### getHTMLs(urls)

Принимает итерируемый объект с URL'ами внутри. Загружает ссылки через requests.get. Возвращает requests response object как список --

_Структура выходных данных_:

```python
[<Response 200>, <Response 200>, <Response 200>, ...]
```

### getLastUpdates(page):

На вход получает номер нужной страницы, возвращает ссылки на страницы.
*NOTE*
Одна страница для getLastUpdates это две страницы сайта shikimori. Т.е. на одной странице play.shikimori 8 тайтлов, а при запросе getLastUpdates(3) возвращаются ссылки две ссылки, на 6 и 7 страницы play.shikimori соответственно.

_Структура выходных данных_:
```python
(url_page_1, url_page_2)
```

### search(page=1, site='play.shikimori', filter_)

Принимает на вход параметры:
*page* - номер страницы (int);
*site* - сайт либо shikimori, либо play.shikimori(default). Лучше не трогать;
*filter_* - фильтры с выхода генератора запроса search_query_generator;

Возвращает сырой список response после requests.get. 

_Структура выходных данных_:
```python
[response]
```
или

```python
[response_1, response_2]
```

### getTooltipLinks(pages_list)

На вход принимает выхлоп shiki.search в виде списка response'ов, в котором либо 1 либо 2 элемента. Теоретически может быть больше.

Возвращает список тайтлов со страниц поиска. До 16 элементов.

NOTE: Работает быстро. Дальше полученных страниц не ходит. Возвращает _бедные_ данные.

Структура выходных данных:

```python
(title_list, isNext)

title_list:
[{
    'id': id_,
    'name_ru': name_ru,
    'name_en': name_en,
    'poster': poster_link,
    'year': year,
    'type': type_,
    'tooltip': tooltip_link,
    <...>
}]
```
isNext -- boolean  # сообщает, есть ли следующая страница у данного запроса

В будущем может быть добавится "необходимый минимум".

### getTitlesParams(titles_list)

На вход может принять либо список тайтлов, либо словарь с одним тайтлом, либо же строку со ссылкой на тултип. Обрабатывает tolltip'ы в тайтлах, по ним получает остальные данные, так что входными данными этого метода является выход предыдущей функции (_getTooltipLinks_).

_NOTE_:
Работает долго, т.к. для получения более подробной информации для каждого тайтла загружает его страницу.

Возвращает объект генератора.
Структура выходных данных:

```python
[{
    'title': 'имя тайтла',
    'name_en': 'same',
    'name_ru': 'same',
    'poster': poster link,
    'link': url title page on play.shikimori,
    'description': short description,
    'rating': rating,
    'genre': [genres],
    'year': year,
    'studio': studio,
    'type': title type(ova, movie, tv, etc)
},
    {<...>}
]
```

### searchQueryGenerator()
Возвращает запрос для адресной строки. За подробностями см. shikimori_query.md.

### getEpisodesLinks(title)
Принимает тайтл, достаёт либо прямую ссылку на страницу, либо ссылку на тултип, смотря что есть. Возвращает список ссылок на страницы серий.

Структура выходных данных:

```python
[
    {'episode_#': link},
    {'episode_#': link},
    {'episode_#': link},
    <...>
    {'episode_#': link}
]
```

### getDirtyEpsLinks(episode_url, type_='dub')
Принимает на вход ссылку на серию (выхлоп get_episodes_links, например) и тип нужного перевода:
- dub
- sub
- all

Возвращает список с доступными типами локализации, "грязными" ссылками на страницы с оными, имя хостинга и указывает авторство, если есть.

Структура возвращаемых данных:
```python
[{
    'author': author,
    'dirty_link': dirty link,
    'hosting': video hosting
},
    {<...>}
]
```

### getDirectEpisodeLink(episode_dirty_link)
Принимает прямую ссылку на страницу с плеером нужной локализации, возвращает прямую ссылку на видео если таковая имеется, либо None.
ass - Ссылка на файл субтитров. Нужна для сайта smotret-anime.ru. Если нет то None.
Структура выходных данных:

(ass_url, url)


