import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import database as db
from buttons import phone_button_uz, menu, kitob_buy, kitob_delivery, location_btn, payment
from bts_offices import offices, kitob_post

BOT_TOKEN = '7927478236:AAEaWaz1v2rNK9W5Oc2cZ7PPRjDhaZZMUHk'
yandex_group_id = -4736821812
bts_group_id = -4736821812

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

user_data = {}


#---------------registration-------------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    checker = False
    if checker:
        bot.send_message(user_id, "Asosiy menyu", reply_markup=menu())
    elif not checker:
        bot.send_message(user_id, "Assalomu alaykum.\nMen kitob va kurslarni sotish botiman!\n")
        bot.send_message(user_id, "Iltimos, ismingizni yuboring\n")

    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_id = message.from_user.id
    name = message.text
    bot.send_message(user_id, f"{name} tanishganimdan xursandman endi raqamingizni pastdagi tugma orqali yuboring",reply_markup=phone_button_uz())
    bot.register_next_step_handler(message, contact_handler, name)

def contact_handler(message, name):
    user_id = message.from_user.id
    if message.contact:
        phone_number = message.contact.phone_number
        bot.send_message(user_id, "Tizimda muvaffaqiyatli ro‘yxatdan o‘tdingiz!")
        bot.send_message(user_id, "pastdagi tugmalar orqali harakatni tanlang", reply_markup=menu())
        db.add_user(name, phone_number, user_id)
    else:
        bot.send_message(user_id, "Raqamingizni pastdagi tugma orqali yuboring",
                         reply_markup=phone_button_uz())
        bot.register_next_step_handler(message, contact_handler, name)

#---------------kitob-------------------
@bot.message_handler(func=lambda message: message.text == "Kitob")
def books(message):
    with open('photos/pick_tasty1.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=kitob_post, reply_markup=kitob_buy())

@bot.callback_query_handler(func=lambda call: call.data == "buy_book")
def delivery_selection(call):
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=kitob_delivery()
        )
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(
            call.message.chat.id,
            "Yetkazib berish usulini tanlang:",
            reply_markup=kitob_delivery()
        )

    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "yandex_delivery")
def request_location(call):
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Iltimos, joylashuvingizni yuboring"
        )
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(
            call.message.chat.id,
            "Iltimos, joylashuvingizni yuboring",
            reply_markup=location_btn()
        )

    user_data[call.message.chat.id] = {"delivery_type": "yandex"}
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    if message.chat.id in user_data and user_data[message.chat.id].get("delivery_type") == "yandex":
        user_data[message.chat.id]["location"] = message.location

        payment_details = (
            "Реквизиты для оплаты:\n"
            "Банк: Хумо\n"
            "Номер счета: 1234 5678 9012 3456\n"
            "Сумма: 20 000 сум\n"
            "\nПосле оплаты отправьте скриншот подтверждения."
        )
        bot.send_message(message.chat.id, payment_details)

@bot.callback_query_handler(func=lambda call: call.data == "bts_delivery")
def select_bts_region(call):
    markup = InlineKeyboardMarkup(row_width=2)
    for region in offices.keys():
        button = InlineKeyboardButton(region, callback_data=f"region_{region}")
        markup.add(button)

    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите регион:"
        )
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(
            call.message.chat.id,
            "Выберите регион:",
            reply_markup=markup
        )

    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("region_"))
def select_bts_office(call):
    region = call.data.split("_")[1]
    markup = InlineKeyboardMarkup(row_width=2)

    for office in offices[region]:
        button = InlineKeyboardButton(office, callback_data=f"office_{office}")
        markup.add(button)

    # Добавляем кнопку "Назад"
    back_button = InlineKeyboardButton("◀️ Назад", callback_data="buy_book")
    markup.add(back_button)

    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Выберите офис в регионе {region}:"
        )
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(
            call.message.chat.id,
            f"Выберите офис в регионе {region}:",
            reply_markup=markup
        )

    user_data[call.message.chat.id] = {"delivery_type": "bts", "region": region}
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("office_"))
def bts_payment(call):
    office = call.data.split("_", 1)[1]
    user_data[call.message.chat.id]["office"] = office

    payment_details = (
        "Реквизиты для оплаты:\n"
        "Банк: Хумо\n"
        "Номер счета: 1234 5678 9012 3456\n"
        "Сумма: 20 000 сум\n"
        "\nПосле оплаты отправьте скриншот подтверждения."
    )
    bot.send_message(call.message.chat.id, payment_details, reply_markup=payment())
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['photo'])
def handle_payment_confirmation(message):
    user_id = message.chat.id
    user_info = db.get_user(user_id)  # Получаем данные пользователя из базы

    if user_info:
        user_order = user_data.get(user_id, {})
        if not user_order:
            bot.send_message(user_id, "Ваш заказ не найден. Попробуйте оформить его заново.")
            return

        name = user_info["name"]
        phone_number = user_info["phone_number"]

        bot.send_message(user_id, "Ваша заявка отправлена администратору.")

        # Создаем инлайн-кнопку
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("❌ariza qabul qilinmagan❌", callback_data=f"order_{user_id}_pending")
        markup.add(button)

        if user_order["delivery_type"] == "yandex":
            admin_message = (
                "#yandex #kitob\n"
                "Новая заявка (Yandex Доставка):\n"
                f"Пользователь: <b>{name}</b>\n"
                f"Телефон: +{phone_number}\n"
                f"Username: @{message.from_user.username}\n"
                f"Локация: ⬇️"
            )
            bot.send_photo(yandex_group_id, message.photo[-1].file_id, caption=admin_message, reply_markup=markup)
            bot.send_location(yandex_group_id, user_order['location'].latitude, user_order['location'].longitude)

        elif user_order["delivery_type"] == "bts":
            admin_message = (
                "#bts #kitob\n"
                "Новая заявка (BTS Доставка):\n"
                f"Пользователь: <b>{name}</b>\n"
                f"Телефон: +{phone_number}\n"
                f"Username: @{message.from_user.username}\n"
                f"ID пользователя: {user_id}\n"
                f"Регион: {user_order['region']}\n"
                f"Офис: {user_order['office']}"
            )
            bot.send_photo(
                bts_group_id,
                message.photo[-1].file_id,
                caption=admin_message,
                reply_markup=markup
            )
    else:
        bot.send_message(user_id, "Ваши данные не найдены в системе. "
                                  "Пожалуйста, зарегистрируйтесь заново с помощью команды /start.")

# Обработчик нажатия на инлайн-кнопку
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_order_status_change(call):
    callback_data = call.data
    user_id, status = callback_data.split("_")[1], callback_data.split("_")[2]

    if status == "pending":
        # Меняем статус на обработано
        new_markup = InlineKeyboardMarkup()
        new_button = InlineKeyboardButton("✅ariza qabul qilindi✅", callback_data=f"order_{user_id}_processed")
        new_markup.add(new_button)

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=new_markup
        )
    elif status == "processed":
        bot.answer_callback_query(call.id, "Заявка уже обработана.")


bot.polling(none_stop=True)