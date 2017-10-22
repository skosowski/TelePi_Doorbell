import RPi.GPIO as GPIO
import sys
import time
import random
import datetime
import telepot
import configparser
import signal
import picamera
import logging
import subprocess
import os.path
from logging.handlers import RotatingFileHandler
import requests

config = configparser.ConfigParser()
basepath = os.path.abspath(sys.argv[1])
config.read(os.path.join(basepath,'telepi.ini'))
allowed_chatid =  config['DEFAULT']['allowed_chatid']
telegramAPIKey =  config['DEFAULT']['telegramAPIKey']
config_loglevel = config['DEFAULT']['loglevel']
GPIO_PIN		= int(config['DEFAULT']['GPIO_PIN'])
PhotoRes_X		= int(config['DEFAULT']['PhotoRes_X'])
PhotoRes_Y		= int(config['DEFAULT']['PhotoRes_Y'])
logsizeBytes	= int(config['DEFAULT']['logsizeBytes'])
howManyLogFiles = int(config['DEFAULT']['howManyLogFiles'])
logrelativepath = config['DEFAULT']['logrelativepath']
photofile = config['DEFAULT']['photofile']
healthcheckURL = config['DEFAULT']['healthcheckURL']
mybouncetime_ms = int(config['DEFAULT']['mybouncetime_ms'])
please_call_mp3 = config['DEFAULT']['please_call_mp3']
please_wait_mp3 = config['DEFAULT']['please_wait_mp3']
mplayer_path = config['DEFAULT']['mplayer_path']

mplayer_path
photopath = os.path.join(basepath,photofile)
mappingDict = {
				"DEBUG"		:	logging.DEBUG,
				"INFO"		:	logging.INFO,
				"WARNING"	:	logging.WARNING,
				"ERROR"		:	logging.ERROR,
				"CRITICAL"	:	logging.CRITICAL
			}

loglevel = mappingDict[config_loglevel]			

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN,GPIO.IN, pull_up_down=GPIO.PUD_UP)

def signal_handler(signal, frame):
    logger.info("exiting gracefully")
    GPIO.cleanup()
    sys.exit(0)

def takepicture(path):
    with picamera.PiCamera() as picam:
        picam.capture(path, resize=(PhotoRes_X,PhotoRes_Y))
        picam.close()

def mycallback(channel):
    logger.debug('someone is calling')
    bot.sendMessage(allowed_chatid, 'someone is calling!')
    takepicture(photopath)
    with open(photopath,'rb') as file:
        bot.sendPhoto(allowed_chatid,file)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    logger.debug(str(content_type) + " " + str(chat_type) + " " + str(chat_id))
    if str(chat_id) != allowed_chatid:
        logger.warn("unknown chatid: " + str(chat_id))
    if content_type == 'text' and chat_type == 'supergroup' and str(chat_id) == allowed_chatid:
        command = msg['text']
        command=command.split("@")[0]
        logger.debug('Got command: %s' % command)

        if command == '/h':
            bot.sendMessage(chat_id, 'available commands:\n /h - help \n \n /p - take picture \n\n /wait - play please wait msg \n\n /callme - play please call me back msg')
        if command == '/p':
            takepicture(photopath)
            with open(os.path.join(basepath,photofile),'rb') as file:
                bot.sendPhoto(allowed_chatid,file)
        if command == '/reboot':
            try:
                subprocess.run("sudo reboot", shell=True, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(e)
        if command == '/poweroff':
            try:
                subprocess.run("sudo poweroff", shell=True, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(e)
        if command == '/wait':
            try:
                subprocess.run([mplayer_path, os.path.join(basepath,please_wait_mp3)], shell=False, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(e)
        if command == '/callme':
            try:
                subprocess.run([mplayer_path, os.path.join(basepath,please_call_mp3)], shell=False, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(e)
                   
#adding bounctime for depressed key = mybouncetime_ms (i.e. shortest keypress interval ismybouncetime_ms - see .ini file)
GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=mycallback, bouncetime=mybouncetime_ms)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

bot = telepot.Bot(telegramAPIKey)
bot.message_loop(handle)

logger = logging.getLogger('Bot logger')
logger.setLevel(loglevel)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
loghandler = logging.handlers.RotatingFileHandler(os.path.join(basepath,logrelativepath),mode='a',maxBytes=logsizeBytes, backupCount=howManyLogFiles, encoding=None, delay=False)
loghandler.setFormatter(formatter)
logger.addHandler(loghandler)


logger.info('I am listening...')

while 1:
	try:
		requests.get(healthcheckURL)
	except requests.exceptions.RequestException as e:
		logger.warn(e)
	time.sleep(300)
