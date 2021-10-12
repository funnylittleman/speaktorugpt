from config import TOKEN, CHAT, NICKS
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import requests
import json
from random import choice
import sys
import time
import urllib.request

global TXT

def generate_text(text, net):
        if net == 'rugpt':
            url = 'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict'
            data = {"text": text}
            r = requests.post(url, verify=True, json=data)

            print('r\n', r)
            print('r.json()\n', r.json())
            r = r.json()['predictions']
            r = r[len(text):]
            print('len text\t', len(text))
            print('len r\t', len(r))
            print('len text+r\t', len(r) + len(text))
            print('r final\n', r)
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
            print('response\n', response)
            r = response.read()
            print('response.read()\n', r)
            r = r.decode('unicode_escape')
            print('r.decode\n', r)
            print(r)
            r = r.split('\"text\":\"')[1][:-2]
        return r


def generate_nickname(net):
    init = NICKS
    nick = generate_text(init, net)
    nick = nick.split('\n')[0]
    return nick


class speaker():
    def __init__(self, net='rugpt', initial='Диалог:\n', \
                    pre_user='Человек: «', post_user='»\n', \
                    pre_computer='Компьютер: «', post_computer='»\n', 
                    endpoint='»', max_len = 1850):
        self.net = net
        self.initial = initial
        self.text = initial
        self.pre_user = pre_user
        self.post_user = post_user
        self.pre_computer = pre_computer
        self.post_computer = post_computer
        self.endpoint = endpoint
        self.max_len = max_len

    def answer(self, text):
        self.listen(text)
        r = self.say()
        return r

    def say(self):
        self.text += f'{self.pre_computer}'
        if len(self.text) > self.max_len:
            self.text = self.text[-self.max_len:]
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
        if r.replace(' ', '') == '':
            r = '(молчит)'

        self.text += r + self.post_computer
        return r
        
        
    def listen(self, text):
        self.text += f'{self.pre_user}{text}{self.post_user}'

    def reset(self):
        self.text = self.initial
        

def main():
    bot = telegram.Bot(token=TOKEN)
    WAIT = 60*0.6
    initial = """Беседа:
Конфуций: «Вы что, не признаете правил хорошего тона?»
Лао-Цзы: «Если вам хочется сесть, садитесь, если вам хочется стоять — стойте. Я не вправе указывать вам на то, что делать. Я не вмешиваюсь в чужую жизнь. Вы свободный человек, но и я — свободный человек.»
Конфуций: «(потрясенный молчит)»
Лао-Цзы: «Я никогда не видел что-либо «высшее» или «низшее». Человек есть человек, точно так же как деревья есть деревья. Все участвуют в одном и том же существовании. Нет никого, кто был бы выше или ниже. Все это бессмыслица!»
Конфуций: «Что происходит с человеком после смерти?»
Лао-Цзы: «Вы живете, но можете ли вы сказать, что такое жизнь?»
Конфуций: «(смутился)»
Лао-Цзы: «Вы не знаете этой жизни и вместо того, чтобы познавать ее, вы беспокоитесь о той, запредельной.»
Беседа:
Морфиус: «Ты веришь в судьбу, Нео?»
Нео: «Нет.»
Морфиус: «Почему?»
Нео: «Неприятно думать, что тобой манипулируют.»
Беседа:
Диана: «Ты не становишься моложе, Марк. Мир меняется. Музыка меняется, даже наркотики меняются. Нельзя же сидеть целыми днями дома и мечтать о героине и Зигги Попе.»
Марк: «Игги Поп.»
Диана: «Без разницы. Все равно он уже умер.»
Марк: «Игги Поп не умер, в прошлом году Томми ходил на его концерт.»
Диана: «Ты должен найти для себя что-то новое.»
Беседа:
"""
    rugptname = generate_nickname('rugpt')
    yalmanme = generate_nickname('yalm')

    rugpt = speaker(net='rugpt', initial=initial, \
                    pre_user=f'{yalmanme}: «', post_user='»\n', \
                    pre_computer=f'{rugptname}: «', post_computer='»\n', 
                    endpoint='»', max_len = 1333)
    yalm = speaker(net='yalm', initial=initial, \
                    pre_user=f'{rugptname}: «', post_user='»\n', \
                    pre_computer=f'{yalmanme}: «', post_computer='»\n', 
                    endpoint='»', max_len = 1333)

    r2 = rugpt.say()
    while True:
        status = bot.send_message(chat_id=CHAT, text=f'<b>{rugptname}:</b>\n{r2}', parse_mode=telegram.ParseMode.HTML)
        # print(status)
        time.sleep(WAIT)
        r1 = yalm.answer(r2)
        status = bot.send_message(chat_id=CHAT, text=f'<b>{yalmanme}:</b>\n{r1}', parse_mode=telegram.ParseMode.HTML)
        # print(status)
        time.sleep(WAIT)
        r2 = rugpt.answer(r1)

if __name__ == '__main__':
    main()
