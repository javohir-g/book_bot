from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def phone_button_uz():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_phone = KeyboardButton("Telefon raqamini yuboring", request_contact=True)
    markup.add(button_phone)
    return markup

def menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    books = KeyboardButton("Kitob")
    courses = KeyboardButton("Kurslar")
    markup.add(books, courses)
    return markup

def location_btn():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Joylashuvimni yuborish", request_location=True)
    markup.add(button)
    return markup

def kitob_buy():
    markup = InlineKeyboardMarkup()
    buy_button = InlineKeyboardButton("Ushbu kitobni sotib olish", callback_data="buy_book")
    markup.add(buy_button)
    return markup

def kitob_delivery():
    markup = InlineKeyboardMarkup()
    yandex_button = InlineKeyboardButton("Yandex Доставка", callback_data="yandex_delivery")
    bts_button = InlineKeyboardButton("BTS Доставка", callback_data="bts_delivery")
    markup.add(yandex_button, bts_button)
    return markup

def payment():
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("Click", url="https://indoor.click.uz/pay?id=054236&t=0&amount=10000")
    button2 = InlineKeyboardButton("Payme", url="https://payme.uz/fallback/merchant/?id=65200f1f5a8224b99c9a37e3")
    markup.add(button1, button2)
    return markup
