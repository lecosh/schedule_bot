from bs4 import BeautifulSoup
import requests
from datetime import datetime
import telebot
import time
import logging
import schedule
from constants import *

bot = telebot.TeleBot(API_KEY)
study_schedule = ""

def get_gym():
    day = datetime.now().weekday() + 1
    if day == 1:
        return gym_schedule[0]
    elif day == 3:
        return gym_schedule[1]
    elif day == 6:
        return gym_schedule[2]
    else:
        return gym_schedule[3]

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
    global study_schedule
    i = 0
    date = get_day(day)
    subjects = get_subjects(day)
    places = get_place(day)
    study_schedule = date + "\n"
    for subj in subjects:
        study_schedule += subj
        study_schedule += "\t" + places[i]
        study_schedule += "\n"
        i += 1

def job():
    get_url()
    return_schedule()

def return_schedule():
    global study_schedule
    if study_schedule == "":
        bot.send_message(chat_id, "Your schedule for tommorow is:\n" + "\t\t\tPolytech - chill" + "\n" + "\t\t\t" + get_job()+ "\n" + "\t\t\t" + get_gym())
    else:
        bot.send_message(chat_id, "Your schedule for tommorow is:\n" + "\t\t\t" + study_schedule + "\n" + "\t\t\t" + get_job()+ "\n" + "\t\t\t" + get_gym())
    time.sleep(60)

@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Hello, text something to start bot')

@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(chat_id, "Schedule has started...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(filename=LOG_FILE,filemode="a", level=logging.INFO, format='%(asctime)-15s %(levelname)-2s %(message)s')
    logger=logging.getLogger(__name__)
    bot.send_message(chat_id, "Bot has been started. Send something to start schedule...")
    schedule.every().day.at("22:00").do(job)
    while True:
        try:
            logger.info("Bot has been started...")
            bot.infinity_polling()
        except Exception as e:
            # logger.error(e, exc_info=False)
            logger.error("Bot has been crushed. Trying to start again...")
            time.sleep(120)