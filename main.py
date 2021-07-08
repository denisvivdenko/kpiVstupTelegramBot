import telebot
import os
import numpy as np
import scipy.stats as st

# data = [188.1, 187.55, 190.7]
# conf_int = st.t.interval(alpha=0.80, df=len(data)-1, loc=np.mean(data), scale=st.sem(data))


API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)


def check_score_speciality_input(message):
    tokens = message.text.split()

    if len(tokens) < 2:
        return False

    for token in tokens:
        try:
            float(token)
        except ValueError:
            bot.send_message(message.chat.id, 'Невірно введено данні. Будь ласка, повторіть операцію.\nКонкурсний бал | Номер спеціальності')
            return False

    return True


@bot.message_handler(func=check_score_speciality_input)
def get_chances(message):
    data = [175.800, 177.750, 180.500]

    tokens = message.text.split()
    score = float(tokens[0])
    speciality_code = float(tokens[1])

    results = []
    for confidence_interval in range(50, 1, -1):
        confidence_interval_result = st.t.interval(alpha=(1 - confidence_interval/200), df=len(data) - 1, loc=np.mean(data), scale=st.sem(data))
        right_tail = confidence_interval_result[1]

        if score > right_tail:
            results.append(100 - confidence_interval/2)

    if score < min(data):
        bot.send_message(message.chat.id, 'No chances')
    elif len(results) == 0 and score > min(data):
        bot.send_message(message.chat.id, '<75%')
    else:
        bot.send_message(message.chat.id, str(max(results)) + '%')


bot.polling()

