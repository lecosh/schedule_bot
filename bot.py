from constants import *

bot = telebot.TeleBot(API_KEY)
study_schedule = ""
logger = logging.getLogger()
logging.basicConfig(filename=LOG_FILE,filemode="a", level=logging.INFO, format='%(asctime)-15s %(levelname)-2s %(message)s')
logger=logging.getLogger(__name__)

def get_tomorrow_weekday():
    day = datetime.now().weekday() % 6
    if day != 0:
        return day + 1
    return day

def get_gym():
    next_day = get_tomorrow_weekday()
    return gym_schedule[next_day]

def get_job():
    next_day = get_tomorrow_weekday()
    return work_schedule[next_day]

def get_study_date(href):
    return href.find("div", "schedule__date").text

def get_class_data(href, div_class):
    class_data_arr = []
    class_data = href.find_all("div", div_class)
    for data in class_data:
        class_data_arr.append(data.text)
    return class_data_arr

def get_xml(url):
    try:
        logger.info("Requesting schedule...")
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
            return 
    bot.send_message(chat_id, "Your schedule for tommorow is:\n" + \
                              "Polytech: chill" + get_job()+ "\n" + get_gym())
    
            
def get_url():
    if datetime.now().weekday() == 6:
        monday_date = datetime.now().today() + timedelta(days=1)
    else:
        monday_date = datetime.now().today() - timedelta(days=datetime.now().weekday())
    url = URL_BASE + str(monday_date.year) + "-" + str(monday_date.month) + "-" + str(monday_date.day)
    get_xml(url)

def format_output(day):
    global study_schedule
    date = get_study_date(day)
    subjects = get_class_data(day, "lesson__subject")
    places = get_class_data(day, "lesson__places")
    lesson_types = get_class_data(day, "lesson__type")
    study_schedule = date + "\n"
    for subject, place, types in zip(subjects, places, lesson_types):
        study_schedule += subject
        study_schedule += "\n"
        study_schedule += types
        study_schedule += "\n"
        study_schedule += place
        study_schedule += "\n"
        
    if study_schedule == "":
        study_schedule = "Polytech - chill"
    bot.send_message(chat_id, "Your schedule for tomorrow is:\n" + \
                              study_schedule + get_job()+ "\n" + get_gym())
    study_schedule = ""
    time.sleep(60)

def job():
    get_url()

if __name__ == "__main__":
    bot.send_message(chat_id, "Bot has been started.")
    schedule.every().day.at("22:00").do(job)
    logger.info("Bot has been started...")
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)