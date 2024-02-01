from constants import *

bot = telebot.TeleBot(API_KEY)
study_schedule = ""

def get_tomorrow_weekday():
    day = datetime.now().weekday() % 6
    if day != 0:
        return day + 1
    return day

def get_gym():
    day = get_tomorrow_weekday()
    if day == 0:
        return gym_schedule[0]
    elif day == 3:
        return gym_schedule[1]
    elif day == 5:
        return gym_schedule[2]
    else:
        return gym_schedule[3]

def get_job():
    work_time = get_tomorrow_weekday()
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
    time_obj = (datetime.now().today() + timedelta(days=1)).day
    for href in all_hrefs:
        if int(href.find("div", "schedule__date").text[:2]) == int(time_obj):
            format_output(href)
            break
            
def get_url():
    if datetime.now().weekday() == 6:
        current_day = datetime.now().today() + timedelta(days=1)
    else:
        current_day = datetime.now().today() - timedelta(days=datetime.now().weekday())
    logger.info(current_day)
    url = URL_BASE + str(current_day.year) + "-" + str(current_day.month) + "-" + str(current_day.day)
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

if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(filename=LOG_FILE,filemode="a", level=logging.INFO, format='%(asctime)-15s %(levelname)-2s %(message)s')
    logger=logging.getLogger(__name__)
    bot.send_message(chat_id, "Bot has been started.")
    schedule.every().day.at("11:43").do(job)
    logger.info("Bot has been started...")
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)