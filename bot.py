from bs4 import BeautifulSoup
import requests
from datetime import datetime
import telebot
import time

url_base = "https://ruz.spbstu.ru/faculty/125/groups/38684?date="
bot = telebot.TeleBot('6942429393:AAFfPt6qtu6HhzjGT5p4A48-CIg5QXnNo58')
schedule = ""
url = ""
week = ""
work_schedule = ["Work: 12:00 - 17:00",
                 "Work: 10:00 - 17:00",
                 "Work: 10:00 - 14:00",
                 "Work: 12:00 - 16:00"]

@bot.message_handler(commands=["start"])



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
    response = requests.get(url)
    bs = BeautifulSoup(response.text, "html.parser")
    all_hrefs = bs.find_all("li", "schedule__day")
    for href in all_hrefs:
        if int(href.find("div", "schedule__date").text[:2]) == int(datetime.now().day + 1):
            format_output(href)

def get_url():
    global url
    current_day = datetime.now()
    url = url_base + str(current_day.year) + "-" + str(current_day.month) + "-" + str(current_day.day - current_day.weekday())
    get_xml(url)

def format_output(day):
    global schedule
    global week
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

@bot.message_handler(content_types=["text"])
def handle_text(message):
    get_url()
    while True:
        time.sleep(60)
        if int(datetime.now().hour) == 22 and int(datetime.now().minute) == 0:
            bot.send_message(message.chat.id, return_schedule())
            time.sleep(60)


bot.infinity_polling()