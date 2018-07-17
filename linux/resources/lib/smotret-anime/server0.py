# -*- coding: utf-8 -*-
import sys
import struct
import os
from multiprocessing.dummy import Process, Event
import time
import requests
import re
import subprocess
import platform
import psutil

try:
	import urllib.request as ur
except ImportError:
	import urllib2 as ur

try:
	# Python 3
	from http.server import HTTPServer, SimpleHTTPRequestHandler
except ImportError:
	# Python 2
	from BaseHTTPServer import HTTPServer
	from SimpleHTTPServer import SimpleHTTPRequestHandler

try:
	from urllib.parse import unquote_plus as uq
except ImportError:
	from urllib import unquote_plus as uq

abspath = os.path.abspath(__file__)

class PopenHandler:
	"""Затычка для проверки статуса Popen"""


	def poll(self):
		return False
	def kill(self):
		pass


class PartsHandler:
	"""For temporary data"""


	parts = []  # список частей видео с информацией об оных
	part = int()  # текущая обрабатываемая часть
	popen = PopenHandler()  # subprocess.Popen


def video_part_info_builder(
	hosting, url='', mvhd=None, idx=0, duration=0, start=0):
	"""
	Генератор данных для куска видео.
	"""

	scale = struct.unpack(">I", mvhd[20:24])[0] if mvhd else None
	duration = duration or (struct.unpack(
		">I", mvhd[24:28])[0] / scale if scale else None)
	idx = idx
	start = start
	url = url
	data = b''
	size = 0
	start_numbering = 0

	if platform.system() == 'Windows':
		ffmpeg = abspath
	elif platform.system == 'Linux':
		ffmpeg = 'ffmpeg'

	if hosting == 'google':
		cmd = ['ffmpeg', '-i', url, \
			'-acodec', 'copy', '-vcodec', 'copy', \
			'-muxdelay', '0', '-muxpreload', '0', \
			'-f', 'mpegts', '-']
	elif hosting == 'big-sword':
		cmd = ['ffmpeg', '-i', '-', \
			'-acodec', 'copy', '-vcodec', 'copy', \
			'-muxdelay', '0', '-muxpreload', '0', \
			'-f', 'mpegts', '-']

	part_info = {
		'scale': scale,
		'duration': duration,
		'idx': idx,
		'start': start,
		'url': url,
		'data': data,
		'cmd': cmd,
		'size': size,
		'hosting': hosting}

	return part_info


def get_video_info(urls, hosting):
	"""
	Получает шапки частей видео. Сохраняет информацию о частях в
	список.
	"""

	with requests.Session() as s:
		s.headers.update({'Range': 'bytes=0-250'})
		mvhds = []
		for url in urls:
			r = s.get(url)
			print(r.status_code)
			print('URL IS:', r.url)
			print('ШАПКА', len(r.content))
			head = r.content
			pos = head.find(b'mvhd')
			size = struct.unpack(">I", head[pos-4:pos])[0]
			mvhd = head[pos-4:pos+size]
			mvhds.append(mvhd)

	parts = []
	for idx, url in enumerate(urls):
		video_part_info = video_part_info_builder(
			hosting, url=urls[idx], mvhd=mvhds[idx], idx=idx, start=sum(
			part['duration'] for part in parts))
		parts.append(video_part_info)

	return parts


def build_playlist(parts):
	"""Построение m3u8 плейлиста"""

	total_parts = len(PartsHandler.parts)
	playlist = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-PLAYLIST-TYPE:VOD\n" \
		"#EXT-X-TARGETDURATION:250"
	for part in parts:
		playlist += "\n#EXTINF:{},\nhttp://127.0.0.1:8900/p{}.ts".format(
			part['duration'], part['idx'])

	if total_parts and len(parts) >= total_parts:
		playlist += "\n#EXT-X-ENDLIST\n"
	return playlist


class CORSRequestHandler(SimpleHTTPRequestHandler):


	def do_GET(self):

		# отправка видео по запросу из плейлиста
		if re.match('.*p\d+\.ts', self.path):
			print('REQUEST', self.path)
			idx = int(re.match('.*p(\d).ts', self.path).groups()[0])
			self.send_response(200, 'OK')
			self.send_header('content-type', 'video/vnd.dlna.mpeg-tts')
			self.end_headers()
			parts = PartsHandler.parts
			popen = PartsHandler.popen

			if parts[idx]['hosting'] == 'google':
				# через ffmpeg кусок скачивается и преобразуется в .ts
				popen = subprocess.Popen(
					parts[idx]['cmd'], stdout=subprocess.PIPE)

				# выхлоп отправляется напрямую по запросу
				while True:
					line = popen.stdout.readline()
					if line:
						try:
							self.wfile.write(line)
						except Exception as e:
							print('EXCEPTION: ', e)
							popen.stdout.close()
							popen.kill()
					else:
						popen.stdout.close()
						popen.kill()
						print('ffmpeg killed')
						break

			elif parts[idx]['hosting'] == 'big-sword':

				# из-за особенностей сервера big-sword качать пришлось
				# отдельно, pipe'ить в ffmpeg, а оттуда уже отправлять

				# код с дополнительным процессом ниже необходим, т.к.
				# баг в Popen под windows
				ffmpeg = subprocess.Popen(parts[idx]['cmd'], \
					stdin=subprocess.PIPE, stdout=subprocess.PIPE)

				stop_event = Event()
				gvp = Process(target=self.get_video, args=(
					ffmpeg, parts[idx]['url'], stop_event))
				gvp.start()

				while True:
					line = ffmpeg.stdout.readline()
					if line:
						try:
							self.wfile.write(line)
						except Exception as e:
							print('Exception occured when sending ffmpeg ' \
								'output:\n', e)
							break
					else:
						break
				ffmpeg.stdout.close()
				ffmpeg.kill()
				stop_event.set()
				gvp.join()

		# генерация и отправка плейлистов, при получении
		# в запросе
		elif re.search(r'playlist\.m3u8', self.path):
			if re.search(r'http://lh3.googleusercontent', self.path):
				hosting = 'google'
			elif re.search(r'\.big-sword', self.path):
				hosting = 'big-sword'
			else:
				return
			print('PLAYLIST REQUEST:', self.path)
			paths = uq(self.path)
			self.urls = paths.lstrip('/playlist.m3u8?').split(' ')
			PartsHandler.parts = get_video_info(self.urls, hosting)
			playlist = build_playlist(PartsHandler.parts)
			self.send_response(200, 'OK')
			self.send_header('Content-Length', len(playlist))
			self.send_header('Content-Type', 'application/vnd.apple.mpegurl')
			self.end_headers()
			self.wfile.write(playlist.encode())


	def get_video(self, process, url, stop_event):
		"""
		Downloading video from big-sword in separate thread
		"""
		cl = 0  # request.content length
		while not stop_event.is_set():
			with requests.Session() as s:
				s.headers.update({'Connection': 'Keep-Alive'})
				s.headers.update({'Range': 'bytes={}-'.format(cl)})
				count = 0
				while count <= 5:  # переподключение при ошибке
					try:
						r = s.get(url)
						count = 0
						break
					except Exception as e:
						print('Exception occured when handling', \
							' requests.gets: ', e)
						print('Retry!')
						count += 1
						time.sleep(1)
				if count == 5:
					break

				if len(r.content) == 0 and r.status_code in (200, 206):
					process.stdin.close()
					break

				cl += len(r.content)

				if r.status_code in (400, 404):
					process.stdin.close()
					break
				if process.poll() != None:
					break
				try:
					process.stdin.write(r.content)
				except Exception as e:
					print('Exception when trying to write: ', e)
					process.stdin.close()
					break


def run(server_class=HTTPServer, handler_class=CORSRequestHandler, port=8900):

	server_address = ('127.0.0.1', port)
	httpd = server_class(server_address, handler_class)
	print('Starting httpd...')
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		httpd.server_close()


def exit():
	"""
	Windows only. Checking if process kodi is running.
	Initial exit if isn't.
	"""

	print('Exit daemon started')
	while True:
		kodi_process = False
		time.sleep(5)

		for process in list(psutil.process_iter()):
			if re.search('kodi', process.name().lower()):
				kodi_process = True
				break

		if kodi_process:
			continue
		else:
			break
	print('Kodi process not found')
	print('EXITING...')
	os._exit(1)


if __name__ == '__main__':

    check_exit = Process(target=exit)
    check_exit.daemon = True
    check_exit.start()

    run()
