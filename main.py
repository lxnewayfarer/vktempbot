# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import requests
from bs4 import BeautifulSoup
import urllib.request
from configs import *

class MessageHandler():
    def __init__(self):
        self.token = TOKEN
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, GROUP_ID)

    def getLink(self, text):
        url = 'https://yandex.ru/pogoda/search?request=' + text
        data = requests.get(url)
        dom = BeautifulSoup(data.text, "html.parser")
        a = dom.findAll("a", {"class": "link place-list__item-name i-bem"})
        cityNumber = a[0].get('href')
        link = 'https://yandex.ru/pogoda/'
        for x in cityNumber:
            if x.isdigit():
                link += x
        data = requests.get(link)
        dom = BeautifulSoup(data.text, "html.parser")
        text = dom.findAll("h1", {"class": "title title_level_1 header-title__title"})[0].get_text()
        return [link, text]

    def SendWeather(self, user_id, url, text):
        text = text.split()[-1]
        data = requests.get(url)
        dom = BeautifulSoup(data.text, "html.parser")
        temperature = dom.select('.fact__hour-temp')
        time_hour = dom.select('.fact__hour-label')
        rezult = 'Температура в ' + text + ' сегодня:\n'
        
        for i in range(10):
            rezult += time_hour[i].getText() + ' ' + temperature[i].getText() + '\n'
        rand_id = random.getrandbits(64)
        self.vk.messages.send(user_id = user_id, token = self.token, message = rezult, random_id = rand_id)
    
    def run(self):  
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                print('•  Для меня от: ', end='')
                user_id = event.obj.from_id
                print(user_id)
                text = event.obj.text
                print('Текст: ', text)
                try:
                    infoList = self.getLink(text)
                    self.SendWeather(user_id, infoList[0], infoList[1])
                except:
                    rand_id = random.getrandbits(64)
                    rezult = 'Ошибка. Вероятно такого города не существует'
                    self.vk.messages.send(user_id = user_id, token = self.token, message = rezult, random_id = rand_id)
                
def main():
    obj = MessageHandler()
    obj.run()
    

if __name__ == '__main__':
    main()