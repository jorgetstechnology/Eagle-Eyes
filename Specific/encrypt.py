import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encryption:
  def __init__(self, password='ksxgyRuBRJLKxjFeHD4nmxbE', salt=b'v4CuHZFzmTedBY2EBGrLRXsm'):
    self.password = password
    self.salt = salt
    self.key = Fernet(self.generate_key())


  def generate_key(self):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self.salt, iterations=100000, backend=default_backend())
    return base64.urlsafe_b64encode(kdf.derive(self.password.encode()))


  def do_encrypt(self, message):
    return self.key.encrypt(message)


  def do_decrypt(self, ciphertext):
    return self.key.decrypt(ciphertext)