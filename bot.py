import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import database as db
from buttons import phone_button_uz, menu, kitob_buy, kitob_delivery, location_btn, payment
from bts_offices import offices, kitob_post, FULL_COURSE_PRICE, SINGLE_VIDEO_PRICE, courses

from keep_alive import keep_alive
keep_alive()

from request_to_site import schedule_updater
from threading import Thread
updater_thread = Thread(target=schedule_updater)
updater_thread.daemon = True
updater_thread.start()


BOT_TOKEN = '7158493029:AAHs8WxBKJxw9yV4V85L80QoyW4LGBwhYr0'
book_group_id = -4614622677
course_group_id = -4782813903

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

user_data = {}
user_selected_courses = {}

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
    with open('photos/photo_2023-10-12_15-56-29.jpg', 'rb') as photo:
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
            "To‘lov uchun rekvizitlar:\n"
            "Karta raqam: 8600332962634972\n" 
            "Dilafruz Xidoyatova\n"
            "To‘lovni amalga oshirilgach, tasdiqlash uchun skrinshot yuboring.\n"
        )
        bot.send_message(message.chat.id, payment_details, reply_markup=payment())

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
            text="Hududni tanlang:"
        )
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(
            call.message.chat.id,
            "Hududni tanlang:",
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
            text=f"Hududdagi ofisni tanlang {region}:"
        )
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(
            call.message.chat.id,
            f"Hududdagi ofisni tanlang {region}:",
            reply_markup=markup
        )

    user_data[call.message.chat.id] = {"delivery_type": "bts", "region": region}
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("office_"))
def bts_payment(call):
    office = call.data.split("_", 1)[1]
    user_data[call.message.chat.id]["office"] = office

    payment_details = (
            "To‘lov uchun rekvizitlar:\n"
            "Karta raqam: 8600332962634972\n" 
            "Dilafruz Xidoyatova\n"
            "To‘lovni amalga oshirilgach, tasdiqlash uchun skrinshot yuboring.\n"
        )
    bot.send_message(call.message.chat.id, payment_details, reply_markup=payment())
    bot.answer_callback_query(call.id)

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

#---------------kurs-------------------
@bot.message_handler(func=lambda message: message.text == "Kurslar")
def send_welcome(message):
    # Создаем инлайн клавиатуру
    markup = InlineKeyboardMarkup()
    #full_course_btn = InlineKeyboardButton("Купить весь курс (10 уроков)", callback_data="full_course")
    part_course_btn = InlineKeyboardButton("Sotib olish", callback_data="part_course")

    #markup.row(full_course_btn)
    markup.row(part_course_btn)

    # Отправляем стартовое сообщение с фото и текстом
    with open('photos/Безымянный-1.jpg', 'rb') as photo:
        bot.send_photo(
            message.chat.id,
            photo,
            caption="Xarid qilmoqchi bo‘lgan kursingizni tanlang:",
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data == "full_course")
def handle_full_course(call):
    # Обработка покупки полного курса
    markup = InlineKeyboardMarkup()
    pay_btn = InlineKeyboardButton("Оплатить", callback_data="office_full_course")

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=f"Стоимость полного курса: {FULL_COURSE_PRICE} сум",
        reply_markup=markup.row(pay_btn)
    )


@bot.callback_query_handler(func=lambda call: call.data == "part_course")
def handle_part_course(call):
    # Создаем инлайн клавиатуру с уроками
    markup = InlineKeyboardMarkup()

    # Добавляем кнопки для каждого курса
    for course in courses:
        markup.add(InlineKeyboardButton(course, callback_data=f"select_{course}"))

    # Кнопка "Готово"
    markup.add(InlineKeyboardButton("Готово", callback_data="courses_done"))

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="Xarid qilmoqchi bo‘lgan kursingizni tanlang:",
        reply_markup=markup
    )

    # Инициализируем список выбранных курсов для пользователя
    user_selected_courses[call.from_user.id] = []


@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def select_course(call):
    user_id = call.from_user.id
    course = call.data.split("_")[1]

    # Если курс уже выбран, удаляем, иначе добавляем
    if course in user_selected_courses.get(user_id, []):
        user_selected_courses[user_id].remove(course)
    else:
        user_selected_courses[user_id].append(course)

    # Обновляем клавиатуру
    markup = InlineKeyboardMarkup()

    # Добавляем кнопки для каждого курса
    for course in courses:
        # Помечаем выбранные курсы
        btn_text = f"✅ {course}" if course in user_selected_courses.get(user_id, []) else course
        markup.add(InlineKeyboardButton(btn_text, callback_data=f"select_{course}"))

    # Кнопка "Готово"
    markup.add(InlineKeyboardButton("Tayyor", callback_data="courses_done"))

    # Обновляем сообщение
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "courses_done")
def courses_done(call):
    user_id = call.from_user.id
    selected_courses = user_selected_courses.get(user_id, [])

    # Рассчитываем стоимость
    kitob_narxi = len(selected_courses) * SINGLE_VIDEO_PRICE

    # Создаем клавиатуру для оплаты
    markup = InlineKeyboardMarkup()
    pay_btn = InlineKeyboardButton("Оплатить", callback_data="office_part_course")

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=f"Video tanlandi: {len(selected_courses)}\n"
                f"Qiymati: {kitob_narxi} сум\n"
                f"Kurslar ro‘yxati: {', '.join(selected_courses)}",
        reply_markup=markup.row(pay_btn)
    )

    # Сохраняем данные о выбранных курсах
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["selected_courses"] = selected_courses
    user_data[user_id]["total_price"] = kitob_narxi


@bot.callback_query_handler(func=lambda call: call.data.startswith("office_"))
def course_payment(call):
    # Определяем тип оплаты (полный или частичный курс)
    office = call.data.split("_", 1)[1]
    user_id = call.message.chat.id

    # Устанавливаем офис
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["office"] = office

    # Определяем стоимость курса
    if office == "full_course":
        kitob_narxi = FULL_COURSE_PRICE
    else:
        kitob_narxi = user_data[user_id].get("total_price", SINGLE_VIDEO_PRICE)

    # Формируем реквизиты для оплаты
    payment_details = (
            "To‘lov uchun rekvizitlar:\n"
            "Karta raqam: 8600332962634972\n" 
            "Dilafruz Xidoyatova\n"
            "To‘lovni amalga oshirilgach, tasdiqlash uchun skrinshot yuboring.\n"
        )

    # Отправляем реквизиты с кнопками оплаты
    bot.send_message(user_id, payment_details, reply_markup=payment())
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

        bot.send_message(user_id, "Arizangiz administratorga yuborildi. Tez orada siz bilan bog‘lanamiz.", reply_markup=menu())

        # Создаем инлайн-кнопку
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("❌ariza qabul qilinmagan❌", callback_data=f"order_{user_id}_pending")
        markup.add(button)

        # Общий обработчик для разных типов заказов
        if user_order.get("delivery_type") == "yandex":
            admin_message = (
                "#yandex #kitob\n"
                "Новая заявка (Yandex Доставка):\n"
                f"Пользователь: <b>{name}</b>\n"
                f"Телефон: +{phone_number}\n"
                f"Username: @{message.from_user.username}\n"
                f"Локация: ⬇️"
            )
            bot.send_photo(book_group_id, message.photo[-1].file_id, caption=admin_message, reply_markup=markup)
            bot.send_location(book_group_id, user_order['location'].latitude, user_order['location'].longitude)

        elif user_order.get("delivery_type") == "bts":
            admin_message = (
                "#bts #kitob\n"
                "Новая заявка (BTS Доставка):\n"
                f"Пользователь: <b>{name}</b>\n"
                f"Телефон: +{phone_number}\n"
                f"Username: @{message.from_user.username}\n"
                f"Регион: {user_order.get('region', 'Не указан')}\n"
                f"Офис: {user_order.get('office', 'Не указан')}"
            )
            bot.send_photo(
                book_group_id,
                message.photo[-1].file_id,
                caption=admin_message,
                reply_markup=markup
            )

        # Обработка курсов
        elif user_order.get("selected_courses"):
            selected_courses = user_order.get("selected_courses", ["Полный курс"])
            kitob_narxi = user_order.get("total_price", SINGLE_VIDEO_PRICE)

            admin_message = (
                "#курс\n"
                "Новая заявка:\n"
                f"Пользователь: <b>{name}</b>\n"
                f"Телефон: +{phone_number}\n"
                f"Username: @{message.from_user.username}\n"
                f"Сумма для оплаты: {kitob_narxi} сум\n"
                f"Выбранные уроки: {', '.join(selected_courses)}"
            )

            bot.send_photo(
                course_group_id,  # Отдельная группа для курсов
                message.photo[-1].file_id,
                caption=admin_message,
                reply_markup=markup
            )

        else:
            bot.send_message(user_id, "Тип заказа не определен.")

    else:
        bot.send_message(user_id, "Ваши данные не найдены в системе. "
                                  "Пожалуйста, зарегистрируйтесь заново с помощью команды /start.")

bot.polling(none_stop=True)