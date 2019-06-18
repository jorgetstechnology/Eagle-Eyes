import socket
import pickle
import zlib
import cv2
import time
from sys import exit
from ctypes import windll
user32 = windll.user32
user32.SetProcessDPIAware()

from Specific.grabber import Grabber
from Specific.encrypt import Encryption


def Stream(ip, port, encoding):
  try:
    headersize = 10
    new_msg = True
    msg_len = 0
    full_msg = b''

    e = Encryption()
    g = Grabber()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    while True:
      try:
        last_time = time.time()
        recv_msg = s.recv(1024)

        if new_msg:
          msg_len = int(recv_msg[:headersize])
          new_msg = False

        full_msg += recv_msg

        if len(full_msg)-headersize == msg_len:
          frame = g.grab()
          cv2.putText(frame, f'FPS: {1.0 / (time.time() - last_time):f}', (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

          frame = pickle.dumps(frame)
          frame = zlib.compress(frame, 1)
          frame = e.do_encrypt(frame)

          final_msg = bytes(f'{len(frame):<{headersize}}', encoding) + frame
          s.send(final_msg)

          new_msg = True
          msg_len = 0
          full_msg = b''
      except:
        cv2.destroyAllWindows()
        exit(0)
  except:
    exit(0)