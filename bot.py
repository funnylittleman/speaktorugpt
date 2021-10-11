
"""
Simple Bot to reply to Telegram messages taken from the python-telegram-bot examples.
Source: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
"""

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
import json
from random import choice
import sys
import ipywidgets as widgets
import time
import urllib.request



def generate_text(text, net = 'yalm'):
        if net is None:
            net = self.net
        if net == 'rugpt':
            url = 'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict'
            data = {"text": text}
            r = requests.post(url, json=data)
            r = r.json()['predictions']
            r = r[len(text):]
        if net == 'yalm':
            headers = {
                            'Content-Type': 'application/json',
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/605.1.15 '
                                        '(KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                            'Origin': 'https://yandex.ru',
                            'Referer': 'https://yandex.ru/',
                        }
            url = 'https://zeapi.yandex.net/lab/api/yalm/text3'
            payload = {"query": text, "intro": 0, "filter": 1}
            params = json.dumps(payload).encode('utf8')
            req = urllib.request.Request(url, data=params, headers=headers)
            response = urllib.request.urlopen(req)
            r = response.read()
            r = r.decode('unicode_escape')
            r = r.split('\"text\":\"')[1][:-2]
        return r


class dialog():
    def __init__(self, net='ruGPT', initial='Диалог:\n', \
                    pre_user='Человек: «', post_user='»\n', \
                    pre_computer='Компьютер: «', post_computer='»\n', 
                    endpoint='»'):
        self.net = net
        self.text = initial
    def answer(self, text):
        self.text += f'{self.pre_user}{text}{self.post_user}{self.pre_computer}'
        if len(text) > 1900:
            text = text[-1900:]
        r = generate_text(self.text, self.net)
            
        if self.endpoint == '»':
            q = 1
            for i in range(len(r)):
                if r[i] == '«':
                q += 1
                if r[i] == '»':
                q -= 1
                if q == 0:
                r = r[:i]
                break
        else:
            r = r.split(self.endpoint)[0]
        self.text += r + self.post_computer
        return r

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '2053623712:AAEXbNLC704BtLPps8Bh2TcHbkTncqX1Rxo'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
