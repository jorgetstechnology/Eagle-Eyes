import os
import sys
import time
import random
import msvcrt
from PIL import ImageFont, Image, ImageDraw, ImageOps
from colorama import Fore, Style


def set_module_ports(values):
	ports = []
	for value in values:
		try:
			port = int(value)
			if port > 65000 or port < 1000:
				raise Exception('Something went wrong')
			ports.append(port)
		except:
			ports.append(random.randint(1000, 65000))
	while True:
		if len(ports) < 5:
			ports.append(random.randint(1000, 65000))		
		else:
			break
	return ports


def set_username(value):
	if value is None:
		try:
			return os.environ['USERNAME'].capitalize()
		except:
			return 'Anonymous'
	elif len(value) < 15 and len(value) > 0:
		return value.capitalize()


def set_theme(value):
	if len(value) > 0:
		if value == 'light':
			return [Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, 'light'] 
		elif value == 'dark':
			return [Fore.BLACK, Fore.LIGHTRED_EX, Fore.LIGHTCYAN_EX, Fore.BLACK, Fore.LIGHTRED_EX, 'dark']
		elif value == 'shade':
			return [Fore.LIGHTBLACK_EX, Fore.RED, Fore.CYAN, Fore.LIGHTBLACK_EX, Fore.LIGHTRED_EX, 'shade']
		elif value == 'star':
			return [Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, 'star']
		elif value == 'diamond':
			return [Fore.LIGHTWHITE_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, 'diamond']
		elif value == 'blood':
			return [Fore.LIGHTWHITE_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, 'blood']
		elif value == 'sky':
			return [Fore.LIGHTWHITE_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, 'sky']
		elif value == 'hacker':
			return [Fore.LIGHTWHITE_EX, Fore.GREEN, Fore.GREEN, Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, 'hacker']


def set_encoding(value):
	if len(value) < 15 and len(value) > 0:
		return value


def set_bool(value):
	if value is True:
		return True
	else:
		return False


def set_email(value):
	self_email_list = []

	try:
		if value[0].lower() == 'true':
			self_email_list.append(True)
		else:
			raise Exception('Something went wrong.')
	except:
		self_email_list.append(False)

	try:
		if '@' in value[1]:
			self_email_list.append(value[1])
		else:
			raise Exception('Something went wrong.')
	except:
		self_email_list.append(None)

	try:
		if value[2] != '' and value[2] != 'None':
			self_email_list.append(value[2])
		else:
			raise Exception('Something went wrong.')
	except:
		self_email_list.append(None)
	
	try:
		if len(value) > 3:
			for email in value[3:]:
				if '@' in email:
					continue
				else:
					value.remove(email)
			self_email_list.append(value[3:])
		else:
			raise Exception('Something went wrong.')
	except:
		self_email_list.append([])

	return self_email_list


def setup_directory(directories):
	for directory in directories:
		if os.path.isdir(directory) is False:
			os.mkdir(directory)


def clear_screen():
	os.system('clear || cls')


def banner(theme):
	print(f'''{theme[2]}{' ' * 84}///,        ////{Style.RESET_ALL}
{theme[1]}{'_' * 35}Created by{'_' * 34}{' ' * 5}{Style.RESET_ALL}{theme[2]}\  /,      /  >.{Style.RESET_ALL}
{theme[2]}{' ' * 84} \  /,   _/  /.{Style.RESET_ALL}
{theme[2]}//       //        //{Style.RESET_ALL}{theme[3]}        // // //    // // //    // // //    //    // // //{Style.RESET_ALL}{theme[2]}       \_  /_/   /.
{theme[2]} //     // //     // {Style.RESET_ALL}{theme[3]}      //     //    //    //    //          //    //{Style.RESET_ALL}{theme[2]}               \__/_   <
{theme[2]}  //   //   //   //  {Style.RESET_ALL}{theme[3]}    // //// //    //    //    // // //    //    // // //{Style.RESET_ALL}{theme[2]}          /<<< \_\_
{theme[2]}   // //     // //   {Style.RESET_ALL}{theme[3]}  //       //    //    //          //    //    //{Style.RESET_ALL}{theme[2]}                /,)^>>_._ \\
{theme[2]}     //        //    {Style.RESET_ALL}{theme[3]}//        //    //    //    // // //    //    //  // //{Style.RESET_ALL}{theme[2]}          (/   \\\\ /\\\\\\
{theme[1]}{'_' * 79}{' ' * 12}{Style.RESET_ALL}{theme[2]}// ````{Style.RESET_ALL}
{theme[2]}{' ' * 90}((`{Style.RESET_ALL}''')


def timer():
	return time.strftime("%Y-%m-%d %H:%M")


def text_image(text):
	PIXEL_ON = 255
	PIXEL_OFF = 0

	grayscale = 'L'
	lines = tuple(l.rstrip() for l in text.split('\n'))

	large_font = 40
	font_path = 'cour.ttf'

	try:
		font = ImageFont.truetype(font_path, size=large_font)
	except IOError:
		font = ImageFont.load_default()

	pt2px = lambda pt: int(round(pt * 96.0 / 72))
	max_width_line = max(lines, key=lambda s: font.getsize(s)[0])
	test_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	max_height = pt2px(font.getsize(test_string)[1])
	max_width = pt2px(font.getsize(max_width_line)[0])
	height = max_height * len(lines)
	width = int(round(max_width + 40))
	image = Image.new(grayscale, (width, height), color=PIXEL_OFF)
	draw = ImageDraw.Draw(image)

	vertical_position = 5
	horizontal_position = 5
	line_spacing = int(round(max_height * 0.8))
	for line in lines:
		draw.text((horizontal_position, vertical_position), line, fill=PIXEL_ON, font=font)
		vertical_position += line_spacing
	c_box = ImageOps.invert(image).getbbox()
	image = image.crop(c_box)
	return image


def readInput(encoding, timeout):
	start_time = time.time()
	inputData = ''

	while True:
		if msvcrt.kbhit():
			character = msvcrt.getwch()

			if character == '\b' and len(inputData) == 0:
				continue
			elif chr(ord(character)) == 'à':
				sub = msvcrt.getwch()
				if sub == 'K' or sub == 'M' or sub == 'P' or sub == 'H':
					pass
				continue

			print(character, end='', flush=True)

			if character == '\r':
				break
			elif character == '\b':
				inputData = inputData[:-1]
				print(' \b', end='', flush=True)			
			else:
				inputData += character
		
		if timeout is True:
			pass
		elif len(inputData) == 0 and (time.time() - start_time) > timeout:
			break
		time.sleep(0.01)

	print()
	if len(inputData) > 0:
		return inputData
	else:
		raise TimeoutError('Timeout')