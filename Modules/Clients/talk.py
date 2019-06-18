import socket
import pickle
import zlib
import time
import pyaudio
import wave
from sys import exit
from Specific.encrypt import Encryption


def Talk(ip, port, encoding):
  try:
    headersize = 10
    new_msg = True
    msg_len = 0
    full_msg = b''
    msg = b'next'

    e = Encryption()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))


    CHUNK = 81920
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=False, output=True, frames_per_buffer=CHUNK)

    while True:
      try:
        talk_msg = s.recv(81920)

        if new_msg:
          msg_len = int(talk_msg[:headersize])
          new_msg = False

        full_msg += talk_msg

        if len(full_msg)-headersize == msg_len:
          data = e.do_decrypt(full_msg[headersize:])
          data = zlib.decompress(data)
          data = pickle.loads(data)

          stream.write(data)

          real_msg = pickle.dumps(msg)
          real_msg = zlib.compress(real_msg, 1)
          real_msg = e.do_encrypt(real_msg)
          final_msg = bytes(f'{len(msg):<{headersize}}', encoding) + msg
          s.send(final_msg)

          new_msg = True
          msg_len = 0
          full_msg = b''
      except:
        stream.stop_stream()
        stream.close()
        p.terminate()
        exit(0)
  except:
    exit(0)