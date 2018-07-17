# plugin.video.shikionline
#### Плагин для медиалплеера kodi, который позволяет воспроизводить видео с сайта play.shikimori.ru

Основной идеей создания этого плагина была простота и удобство запуска просмотра видео, без дополнительных, лишних телодвижений.
Выбрал тайтл -> Нажал -> Смотришь.

Умеет пока немного:

- автоматический выбор видео с озвучкой по приоритетному списку команд фандаба. Список можно редактировать вручную:

<img src="https://pp.userapi.com/c830209/v830209760/145a9c/bNKDDQmE2I8.jpg" alt="drawing" width="500px"/>

- автоматический выбор видео с субтитрами. Выбирается самое популярное видео (по количеству просмотров);
- выбор видео из контекстного меню вручную:

<img src="https://pp.userapi.com/c844724/v844724377/a12ff/lJwsmnZH2-k.jpg" alt="drawing" width="500px"/>

<img src="https://pp.userapi.com/c844724/v844724377/a1313/DFxb5fdq4j4.jpg" alt="drawing" width="500px"/>

- поиск как по названию тайтла, так и расширенный:

<img src="https://pp.userapi.com/c846524/v846524377/9d37d/IFVpyZfS8jg.jpg" alt="drawing" width="500px"/>

- домашняя страница -- последние обновления с сайта play.shikimori;
- избранное сообществом;
- избранное shikimori;
- названия серий если таковые есть в MAL (на английском, конечно же);

### Поддерживаемые хостинги:

- vk
- sibnet
- sovetromantica
- smotret-anime (частично)

__Частичная__ поддержка обуславливается невозможностью перематывать видео. Для аниме проблема весомая, ибо опенинги смотреть хочется далеко не всегда. Также для некоторых тайтлов не работают внешние субтитры (на сайте smotret-anime для некоторых видео субтитры идут отдельным ass файлом. 

### Установка
Скачать zip архив и установить стандартным способом в kodi. После переустановки желательно перезапустить kodi для запуска службы для сайта smotret-anime.ru.

Если после переустановки и перезапуска kodi при попытке появляется видео о невозможности перемотки, но видео не воспроизводится, то в настройках плагина нужно отключить поддержку воспроизведения видео с хостинга smotret-anime.ru.
Настройки -> Видео -> Поддержка хостинга smotret-anime.ru

__Windows__

[plugin.video.shikionline.windows.zip](https://github.com/IngvarListard/plugin.video.shikionline/blob/master/plugin.video.shikionline.windows.zip)

__Linux__

[plugin.video.shikionline.windows.zip](https://github.com/IngvarListard/plugin.video.shikionline/blob/master/plugin.video.shikionline.linux.zip)