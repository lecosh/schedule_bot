from bs4 import BeautifulSoup
import requests
from datetime import datetime
import telebot
import time
import logging
from constants import *

bot = telebot.TeleBot(API_KEY)
schedule = ""

@bot.message_handler(commands=["start"])

@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, "I'm ready to start")
    while True:
        time.sleep(120)
        if int(datetime.now().hour) == 22 and int(datetime.now().minute) <= 5:
            get_url()
            bot.send_message(message.chat.id, return_schedule())
            time.sleep(300)

def start(m, res=False):
    bot.send_message(m.chat.id, 'Hello')

def get_job():
    work_time = datetime.now().weekday() + 1
    if work_time > 3:
        return "Work - Chill"
    else:
        return work_schedule[work_time]

def get_day(href):
    return href.find("div", "schedule__date").text

def get_subjects(href):
    subj_arr = []
    all_subjects = href.find_all("div", "lesson__subject")
    for subject in all_subjects:
        subj_arr.append(subject.text)
    return subj_arr

def get_place(href):
    place_arr = []
    all_places = href.find_all("div", "lesson__places")
    for place in all_places:
        place_arr.append(place.text)
    return place_arr

def get_xml(url):
    logger.info("Requesting schedule...")
    try:
        response = requests.get(url)
    except Exception as e:
        logger.error("Bad request:", e)
    else:
        logger.info("Request is OK")
    bs = BeautifulSoup(response.text, "html.parser")
    all_hrefs = bs.find_all("li", "schedule__day")
    for href in all_hrefs:
        if int(href.find("div", "schedule__date").text[:2]) == int(datetime.now().day + 1):
            format_output(href)

def get_url():
    current_day = datetime.now()
    url = URL_BASE + str(current_day.year) + "-" + str(current_day.month) + "-" + str(current_day.day - current_day.weekday())
    get_xml(url)

def format_output(day):
    global schedule
    i = 0
    date = get_day(day)
    subjects = get_subjects(day)
    places = get_place(day)
    schedule = date + "\n"
    for subj in subjects:
        schedule += subj
        schedule += "\t" + places[i]
        schedule += "\n"
        i += 1

def return_schedule():
    global schedule
    if schedule == "":
        return "Polytech - chill" + "\n" + get_job()
    return schedule + "\n" + get_job()

if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(filename=LOG_FILE,filemode="a", level=logging.INFO, format='%(asctime)-15s %(levelname)-2s %(message)s')
    logger=logging.getLogger(__name__)
    try:
        logger.info("Bot has been started...")
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        logger.error(e, exc_info=True)