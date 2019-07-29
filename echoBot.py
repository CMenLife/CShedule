#!/usr/bin/python
# -*- coding: utf-8 -*-

import array as arr
import logging
from urllib.parse import urlparse

import requests
import telebot
from bs4 import BeautifulSoup
from telebot import types

API_TOKEN = '833271152:AAHl4v2jEh6R8qKTvUzKH2q8RrgRwMdJPbA'

bot = telebot.TeleBot(API_TOKEN)
chats = arr.array('I', [447680872])
groups = []

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


def upd_groups():
    groups.clear()
    url = "https://pmkedu.pro/schedules/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    main_content = soup.find('div', {'class': 'row mb-5'})
    global date
    date = soup.find('small', {'class': 'text-muted'}).text
    list_or_repos = main_content.findAll('div', {'class': 'col-12 col-xl-4 col-lg-6 col-md-6'})

    bot.send_message(447680872, "Список групп запрошен")

    for repo in list_or_repos:
        base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
        group = {'name': repo.a.string.strip(),
                 'link': base_url + repo.a.get('href')
                 }
        groups.append(group)


upd_groups()


@bot.message_handler(commands=['help', 'start'])
def send_start(message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    for group in groups:
        markup.add(group['name'])

    bot.send_message(message.chat.id, """\
Привет, я СSchedule бот.
Недоработки/предложения: @cmen_life
Какая у тебя группа?\
""", reply_markup=markup)


@bot.message_handler(commands=['groups'])
def send_groups(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for group in groups:
        markup.add(group['name'])

    bot.send_message(message.chat.id, """\
Список групп:
""", reply_markup=markup)


@bot.message_handler(commands=['upd'])
def cmd_upd_groups(message):
    upd_groups()


@bot.message_handler(commands=['sub'])
def debug_sub(message):
    chats.append(message.chat.id)
    bot.send_message(message.chat.id, chats)


@bot.message_handler(commands=['subs'])
def debug_subs(message):
    bot.send_message(message.chat.id, chats)


def group_isset(text):
    for group in groups:
        if group['name'] == text:
            return True


def group_link(text):
    for group in groups:
        if group['name'] == text:
            return group['link']


@bot.message_handler(func=lambda message: group_isset(message.text))
def command_text_hi(msg):
    url = group_link(msg.text)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    main_card = soup.find('div', {'class': 'card-body'})
    list_or_repos = main_card.find('div', {'class': 'card-text'}).findAll('div', {'class': 'row'})

    pares = []
    for repo in list_or_repos:
        para = {'name': repo.find('div', {'class': 'col-9'}).text.strip(), 'aud': repo.span.string.strip()}
        pares.append(para)

    message = date.strip()

    if main_card.find('span', {'badge badge-info'}) is not None:
        message = message + "\n" + main_card.find('span', {'badge badge-info'}).text.strip()

    if len(pares) == 0:
        message = message + "\n🌝Пар нет..."


    for x in pares:
        message = '{0}\n{1} — ауд. {2}'.format(message, x['name'].replace('  ', ''), x['aud'])

    bot.send_message(msg.chat.id, message)


# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(msg):
    bot.send_message(msg.chat.id, "Я не понимаю... \"" + msg.text + "\"\nМожет выбрать группу из списка ниже?")


bot.polling()
