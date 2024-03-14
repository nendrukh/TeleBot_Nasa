import random
import re
from api import api_request_img_day, api_request_mars, ParamMars
from datetime import datetime
from config import BOT_TOKEN
from database import User
from states import States

import telebot
from telebot.storage import StateMemoryStorage
from telebot.types import Message
from telebot import custom_filters

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)


@bot.message_handler(commands=["start", "help"])
def start_bot(message: Message) -> None:
    r"""
    Message handler: '\help', '\start' from the user.
    We add the user to the database if we have not done this before
    """
    user_id: int = message.from_user.id
    username: str = message.from_user.username
    first_name: str = message.from_user.first_name
    last_name: str = message.from_user.last_name

    try:
        User.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        bot.send_message(message.chat.id, """
Привет! Я новый бот в телеграмме 🙂
Я интегрирован с NASA.
Доступные команды:
- /image_day Получить фото дня от NASA по дате
- /mars Получить фотки с Марса, а именно с марсоходов с разных камер
""")
    except:
        bot.send_message(message.chat.id, f"Рад снова видеть тебя, {username} 🙂")
        bot.send_message(message.chat.id, """
Доступные команды:
- /image_day Получить фото дня от NASA по дате
- /mars Получить фотки с Марса, а именно с марсоходов из разных камер
""")
    bot.set_state(message.from_user.id, States.base, message.chat.id)


@bot.message_handler(commands=["mars"])
def set_camera_for_mars(message: Message) -> None:
    r"""
    Message handler: '\mars' from user.
    We request the type of camera from which photographs are needed.
    Change the bot state to set_camera
    """
    bot.send_message(
        message.chat.id, """
Могу отправить тебе 5 фоток (может меньше) с Марса из архива NASA.
Укажи камеру, с которой тебе нужны фотки:
""")

    bot.send_message(
        message.chat.id, """
Для фронтальной камеры, напиши - Фронт
Для задней камеры, напиши - Задняя
Для мачтовой камеры, напиши - Мачта
""")

    bot.set_state(message.from_user.id, States.set_camera, message.chat.id)


@bot.message_handler(state=States.set_camera)
def set_sol_for_mars(message: Message) -> None:
    """
    Bot state handler set_camera.
    At the input to the function, we check that the camera type is correct and request the date.
    Change the bot state to send_pictures
    """
    if re.search(r"\b([Фф]ронт|[Зз]адняя|[Мм]ачта)\b", message.text):
        ParamMars.camera = message.text
        bot.send_message(message.chat.id, """
Теперь укажи, пожалуйста, дату за которую отправить фотки
В формате: 01.01.2023
""")
        bot.set_state(message.from_user.id, States.send_pictures, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Камера указана не в правильном формате.")
        bot.send_message(message.chat.id, """
Для выбора фронтальной камеры напиши: фронт
Для задней камеры напиши: задняя
Для мачтовой камеры напиши: мачта
""")
        bot.send_message(message.chat.id, "Посмотреть все команды можно через команду /start")


@bot.message_handler(state=States.send_pictures)
def send_pict_from_mars(message: Message) -> None:
    """
    Bot state handler send_pictures.
    At the input to the function, we check the correctness of the date and send photos from Mars
    """
    if re.search(r"\b\d{2}.\d{2}.\d{4}\b", message.text):
        ParamMars.earth_date = datetime.strptime(message.text, "%d.%m.%Y")
        pictures_from_mars: list = api_request_mars(ParamMars.earth_date, ParamMars.camera)

        for i_picture in pictures_from_mars:
            bot.send_message(message.chat.id, i_picture)
        bot.send_message(message.chat.id, """
Если хочешь сменить дату, просто напиши её
Если хочешь сменить камеру, введи заново /mars
Посмотреть все команды можно через команду /start
""")
    else:
        bot.send_message(message.chat.id, "Дата задана не в нужном формате. Пример: 01.01.2023. Попробуй ещё раз.")


@bot.message_handler(commands=["image_day"])
def set_date_for_img_day(message: Message) -> None:
    r"""
    Message handler: '\image_day' from the user.
    We ask the user for a date
    Change the bot state to send_img_day
    """
    bot.send_message(message.chat.id,
                     "Я могу отправить тебе фото дня из архива NASA, но для этого мне нужна от тебя дата. Введи дату, в формате: 01.01.2023")
    bot.set_state(message.from_user.id, States.send_img_day, message.chat.id)


@bot.message_handler(state=States.send_img_day)
def send_img_day(message: Message) -> None:
    """
    Bot state handler send_img_day.
    At the input to the function, we check that the date is correct and send a picture of the day
    """
    if re.search(r"\b\d{2}.\d{2}.\d{4}\b", message.text):
        date_time: datetime = datetime.strptime(message.text, "%d.%m.%Y")
        picture_and_description: str = api_request_img_day(date_time.date())
        bot.send_message(message.chat.id, picture_and_description)
        bot.send_message(message.chat.id, """
Если хочешь получить картинку за другую дату, можешь просто ввести её.
Посмотреть все команды можно через команду /start
""")
    else:
        bot.send_message(message.chat.id, """
Дата задана не в нужном формате. Пример: 01.01.2023. Попробуй ещё раз.
Посмотреть все команды можно через команду /start
""")


@bot.message_handler(content_types=["text"])
def hello_send(message: Message) -> None:
    """
    The handler for all user messages.
    If we catch a greeting from a user, we will greet you back
    """
    if re.search(r"[Пп]рив|[Зз]дравству[ий]|[Хх]а[ийю]|[Hh]i|[Hh]ello|[Зз]даров", message.text):
        user = User.select().where(User.username == message.from_user.username).first()
        hello_commands: tuple = ("Привет", "Здравствуй", "Хай", "Приветствую", "Хаю-хай", "Hello", "Hi", "Ну привет")
        if user:
            if message.from_user.first_name:
                user_name: str = message.from_user.first_name
            else:
                user_name: str = message.from_user.username
            bot.send_message(message.chat.id, random.choice(hello_commands) + ", " + user_name)
        else:
            bot.send_message(message.chat.id,
                             random.choice(hello_commands) + "\nДля регистрации, используй команду /start")
    else:
        bot.send_message(message.chat.id, "Не понял тебя. Для помощи и вызова команд можешь написать /start")
    bot.set_state(message.from_user.id, States.base, message.chat.id)


if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()
