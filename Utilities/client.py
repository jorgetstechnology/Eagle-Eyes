import ctypes
import webbrowser


def show_message(title, text, style):
  if style == 1:
    style = 16
  elif style == 2:
    style = 32
  elif style == 3:
    style = 48
  elif style == 4:
    style = 64
  else:
    style = 0
  ctypes.windll.user32.MessageBoxW(0, text, title, style)


def open_browser(data):
  urls = data.split(',')
  
  for url in urls:
    if 'http://' in url or 'https://' in url:
      pass
    else:
      url = 'https://' + url
    webbrowser.open(url, new=2)