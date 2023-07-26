import socket

from colorama import init
init()
from colorama import Fore, Back, Style

from datetime import datetime

import os

import threading

import re

import urllib



class FTP(socket.socket):

	def __init__(self, ip, port, path):
		super().__init__()

		self.IP = [ip, port]

		self.ports = [self.IP[1], 433, 5000, 80, 8080]

		self._WORKING = True

		self.host = ''

		self.path = path

		self.sp_with_clints = {}


	def __print(self, data, time=False, status='log'):
		str_to_print = ''

		if time:
			str_to_print += f'[{str(datetime.now())[:-7]}] '

		str_to_print += str(data)

		if status == 'log':
			print(Fore.GREEN + f'[LOG] {str_to_print}')

		elif status == 'warning':
			print(Fore.YELLOW + f'[LOG] {str_to_print}')

		elif status == 'error':
			print(Fore.RED + f'[LOG] {str_to_print}')

		else:
			print(f'[INFO] {str_to_print}')


	def __exit(self):
		os.system('pause')

		self._WORKING = False

		exit()

	def __clear_console(self): os.system('cls')

	def __create_responce(self, data):
		return 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\n'.encode() + data.encode()

	def __decode_url(self, url):
		return urllib.parse.unquote(url)


	def _bind(self):
		for port in self.ports:
			self.IP[1] = port

			try:
				self.bind((self.IP[0], self.IP[1]))

				self.listen()

				self.__print(f'Server has been binded on {self.IP}')

				self.host = f'http://{self.IP[0]}:{self.IP[1]}'

				break
			except:
				self.__print(f'Server has not been binded, port <{self.IP[1]}> is bisy.', status='error')
		else:
			raise Exception(f'Server has not binded on {self.IP}. All ports are bisy now.')


	def get_info(self, path):
		str_of_resp = f'<h3>Path: {path}</h3><ul><li><a href="{self.host}/cd_back">..</a></li>'

		for obj in os.walk(path):
			for _path in obj[1]:
				str_of_resp += f'<li><a href="/cd/{_path}">{_path}</a></li>'

			str_of_resp += '<br><hr><br></ul>'

			str_of_resp += '<ul>'

			for _file in obj[2]:#href="#" download="{path}\\{file}"
				str_of_resp += f'<a href="{self.host}/show/{path}\\{_file}">{_file}</a><br>'

			str_of_resp += '</ul>'

			break

		return str_of_resp


	def send_file(self, path):
		pass


	def client_function(self, client, client_ip):
		data = client.recv(1024).decode('utf-8')

		self.__print(f'Data has been getted from client {client_ip}. Size: {len(data)}.', time=True)

		if data:
			data_list_line = data.split('\n')

			header = data_list_line[0].split(' ')

			method = header[0]

			url = self.host + header[1]

			if method == 'GET':
				self.__print(f'[GET] Url: {url}', time=True)

				if header[1] == '/':

					path = self.sp_with_clints[client_ip[0]]

					info_to_send = self.get_info(path)

					resp = self.__create_responce(info_to_send)
					client.send(resp)

					self.__print(f'Client moved to path: {self.sp_with_clints[client_ip[0]]};')
				elif header[1][:4] == '/cd/':
					self.sp_with_clints[client_ip[0]] = self.sp_with_clints[client_ip[0]] + f'\\{self.__decode_url(header[1][4:])}'

					if len(self.sp_with_clints[client_ip[0]].split('%20')):
						sp_with_part_of_path = self.sp_with_clints[client_ip[0]].split('%20')

						self.sp_with_clints[client_ip[0]] = ''
						for path in sp_with_part_of_path:
							self.sp_with_clints[client_ip[0]] += path
							self.sp_with_clints[client_ip[0]] += ' '
						self.sp_with_clints[client_ip[0]] = self.sp_with_clints[client_ip[0]][:-1]

					info_to_send = self.get_info(self.sp_with_clints[client_ip[0]])

					resp = self.__create_responce(info_to_send)
					client.send(resp)

					self.__print(f'Client moved to path: {self.sp_with_clints[client_ip[0]]};')
				elif header[1][:8] == '/cd_back':
					path_parts = self.sp_with_clints[client_ip[0]].split('\\')

					new_path = ''

					for pp in path_parts[:-1]:
						new_path += pp
						new_path += '\\'

					new_path = new_path[:-1]

					self.sp_with_clints[client_ip[0]] = new_path

					info_to_send = self.get_info(self.sp_with_clints[client_ip[0]])

					resp = self.__create_responce(info_to_send)
					client.send(resp)

					self.__print(f'Client moved to path: {self.sp_with_clints[client_ip[0]]};')
				elif header[1][:6] == '/show/':
					path_to_file = header[1][6:]

					try:
						file_data = '<br>'.join(open(path_to_file, 'rb').read().decode("utf-8").split('\n'))
					except:
						file_data = b'<br>'.join(open(path_to_file, 'rb').read().split(b'\n'))

					info_to_send = self.__create_responce(f'<h1>File: {path_to_file};</h1><p id="file_data">{file_data}</p>')

					client.send(info_to_send)
					self.__print(f'Client is looking a file: {path_to_file};')
				else:
					resp = self.__create_responce('<h1>[Error 404] Page has not found.</h1>')
	
					client.send(resp)
			elif method == 'POST':
				pass
			else:
				return 0




	def run(self):
		try:
			self._bind()
		except Exception as error:
			self.__print(error, status='error')

			self.__exit()
		else:
			self.__print(f'Server`s URL: {self.host}')
			self.__print(f'Server`s path: {self.path}')

			while self._WORKING:

				client, client_ip = self.accept()

				try:
					self.sp_with_clints[client_ip[0]]
				except:
					self.sp_with_clints[client_ip[0]] = self.path

				threading.Thread(target=self.client_function, args=(client, client_ip)).start()

		self.__exit()



def main():
	server = FTP('127.0.0.1', 5000, "C:\\Users\\admin\\Desktop")
	server.run()

if __name__ == '__main__':
	main()
