import requests
import schedule
import time


def update_website():
    try:
        response = requests.get("https://book-bot-1.onrender.com/")
        if response.status_code == 200:
            print("Сайт успешно обновлен")
        else:
            print(f"Ошибка при обновлении сайта: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при попытке обновить сайт: {e}")

def schedule_updater():
    schedule.every(10).minutes.do(update_website)
    while True:
        schedule.run_pending()
        time.sleep(1)
