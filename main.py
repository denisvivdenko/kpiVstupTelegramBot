import telebot
import os
import numpy as np
import pandas as pd
import scipy.stats as st

# data = [188.1, 187.55, 190.7]
# conf_int = st.t.interval(alpha=0.80, df=len(data)-1, loc=np.mean(data), scale=st.sem(data))

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

data = pd.read_csv('data.csv')


@bot.message_handler(commands=['start'])
def start_command(message):
    greeting = ""

    with open('greeting.txt', encoding='utf-8') as f:
        greeting = f.read()

    bot.send_message(message.chat.id, greeting)


def check_score_speciality_input(message):
    tokens = message.text.split()

    if len(tokens) < 2:
        return False

    for token in tokens:
        try:
            float(token)
        except ValueError:
            bot.send_message(message.chat.id, 'Невірно введено данні. Будь ласка, повторіть операцію.\nКонкурсний бал '
                                              '| Номер спеціальності')
            return False

    return True


def get_chances(message, data, score):

    results = []
    for confidence_interval in range(50, 5, -1):
        confidence_interval_result = st.t.interval(alpha=(1 - confidence_interval / 200), df=len(data) - 1,
                                                   loc=np.mean(data), scale=st.sem(data))
        right_tail = confidence_interval_result[1]

        if score > right_tail:
            results.append(100 - confidence_interval / 2)

    if score < min(data):
        return -1
    elif len(results) == 0 and score > min(data):
        # bot.send_message(message.chat.id, '<75%')
        return 0
    else:
        return max(results)


def send_chances_info(message, results, speciality):
    chances_info = ''
    for faculty, chance in results.items():
        if chance == -1:
            chance = 'з Божою допомогою'
        elif chance == 0:
            chance = '50% < X < 70%'
        else:
            chance = str(chance) + ' %'

        chances_info += '{0}:\n{1}: {2}\n\n'.format(faculty, str(speciality), str(chance))

    bot.send_message(message.chat.id, chances_info)


@bot.message_handler(func=check_score_speciality_input)
def get_chances_for_all_faculties(message):

    tokens = message.text.split()
    score = float(tokens[0])
    speciality_code = int(tokens[1])
    speciality_data = data[data.Speciality == speciality_code]

    results = {}
    for faculty in speciality_data.to_numpy():
        print(faculty[0])
        faculty_data = faculty[2:]
        print(faculty_data)

        chance = get_chances(message, faculty_data, score)
        results[faculty[0]] = chance

    send_chances_info(message, results, speciality_code)


bot.polling()

