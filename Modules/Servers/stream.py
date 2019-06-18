import socket
import pickle
import zlib
import time
import random
import cv2
from sys import exit
from Specific.encrypt import Encryption
from Utilities.db_queries import get_module_data


try:
	# Address
	info = get_module_data()
	# Settings
	stream_settings = []
	# Socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((info[1], int(info[3].split(',')[0])))
	s.listen()
except:
	exit(0)


def stream_info():
	info = '\n'
	
	for index, setting in enumerate(stream_settings):
		info += f'    - {setting[0]}[{index}]'
		if len(stream_settings) > 1 and index + 1 != len(stream_settings):
			info += '\n'
	
	if len(stream_settings) == 0:
		info = 'False'
		
	return info


def set_stream_settings(index):
	global stream_settings

	try:
		if index == '*':
			for stream_setting in stream_settings:
				stream_setting[1].close()
			return 'Streams closed!'
		else:
			stream_settings[int(index)][1].close()
			return 'Stream closed!'
	except:
		return 'Stream failed to close.'


def Stream(encoding, path, user):
	try:
		global stream_settings

		FRAMES = 5.0
		QUALITY = (1920, 1080)
		headersize = 10
		new_msg = True
		msg_len = 0
		full_msg = b''
		msg = b'next'

		r = random.randint(0, 1000000)
		e = Encryption()
		client, addr = s.accept()

		u = (user, client, addr)
		stream_settings.append(u)

		real_msg = pickle.dumps(msg)
		real_msg = zlib.compress(real_msg, 1)
		real_msg = e.do_encrypt(real_msg)
		final_msg = bytes(f'{len(msg):<{headersize}}', encoding) + msg
		client.send(final_msg)

		fourcc = cv2.VideoWriter_fourcc(*'XVID')
		out = cv2.VideoWriter(f'{path}/{time.strftime("%Y-%m-%d (%H-%M-%S")}.avi', fourcc, FRAMES, QUALITY)

		while True:
			try:
				client_msg = client.recv(81920)

				if new_msg:
					msg_len = int(client_msg[:headersize])
					new_msg = False

				full_msg += client_msg

				if len(full_msg)-headersize == msg_len:
					frame = e.do_decrypt(full_msg[headersize:])
					frame = zlib.decompress(frame)
					frame = pickle.loads(frame)

					cv2.namedWindow(f'{user}\'s live stream. {r}', cv2.WINDOW_NORMAL)
					cv2.imshow(f'{user}\'s live stream. {r}', frame)
					out.write(frame)

					if cv2.waitKey(1) == 27:
						client.close()
						break
				
					real_msg = pickle.dumps(msg)
					real_msg = zlib.compress(real_msg, 1)
					real_msg = e.do_encrypt(real_msg)
					final_msg = bytes(f'{len(real_msg):<{headersize}}', encoding) + real_msg
					client.send(final_msg)
					
					new_msg = True
					msg_len = 0
					full_msg = b''
			except:
				stream_settings.remove(u)
				out.release()
				exit(0)

		stream_settings.remove(u)
		out.release()
	except:
		exit(0)