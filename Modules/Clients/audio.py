import socket
import pickle
import zlib
import time
import pyaudio
import wave
from sys import exit
from Specific.encrypt import Encryption


def Audio(ip, port, encoding):
  try:
    headersize = 10
    new_msg = True
    msg_len = 0
    full_msg = b''

    e = Encryption()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    CHUNK = 81920
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, as_loopback=True)

    while True:
      try:
        Audio_msg = s.recv(1024)

        if new_msg:
          msg_len = int(Audio_msg[:headersize])
          new_msg = False

        full_msg += Audio_msg

        if len(full_msg)-headersize == msg_len:
          frame = stream.read(CHUNK)

          frame = pickle.dumps(frame)
          frame = zlib.compress(frame, 1)
          frame = e.do_encrypt(frame)

          final_msg = bytes(f'{len(frame):<{headersize}}', encoding) + frame
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