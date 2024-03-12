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
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    user = User.select().where(User.username == username).first()
    if not user:
        User.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        bot.send_message(message.chat.id, "Я новый бот в телеграмме. Пока что я в процессе разработки 🙂"
                                          "Меня планируют интегрировать с NASA\n"
                                          "- /image_day. Получить фото дня от NASA по дате")
    else:
        bot.send_message(message.chat.id, f"Рад снова видеть тебя, {username} 🙂\n"
                                          "Напомню команды:\n"
                                          "- /image_day Получить фото дня от NASA по дате\n"
                                          "- /mars Получить фотки с Марса, а именно с марсоходов из разных камер")
    bot.set_state(message.from_user.id, States.base, message.chat.id)


@bot.message_handler(commands=["mars"])
def set_camera_for_mars(message: Message) -> None:
    bot.send_message(
        message.chat.id,
        "Могу отправить тебе 5 фоток (может и меньше) с Марса от марсоходов из архива NASA, "
        "но для этого мне понадобится, чтобы ты "
        "указал камеру, с которой тебе нужны фотки:")

    bot.send_message(
        message.chat.id,
        "\nДля фронтальной камеры, напиши - Фронт\n"
        "Для задней камеры, напиши - Задняя\n"
        "Для мачтовой камеры, напиши - Мачта")

    bot.set_state(message.from_user.id, States.set_camera, message.chat.id)


@bot.message_handler(state=States.set_camera)
def set_sol_for_mars(message: Message) -> None:
    if re.search(r"\b([Фф]ронт|[Зз]адняя|[Мм]ачта)\b", message.text):
        ParamMars.camera = message.text
        bot.send_message(message.chat.id, "Теперь укажи, пожалуйста, дату за которую отправить фотки\n"
                                          "В формате: 01.01.2023")
        bot.set_state(message.from_user.id, States.send_pictures, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Камера указана не в нужном формате. Необходимо ввести так:\n"
                                          "Камера предотвращения фронтальной опасности, напиши - фронт\n"
                                          "Задняя камера предотвращения опасностей, напиши - задняя\n"
                                          "Мачтовая камера, напиши - мачта"
                         )
        return


@bot.message_handler(state=States.send_pictures)
def send_pict_from_mars(message: Message) -> None:
    if re.search(r"\b\d{2}.\d{2}.\d{4}\b", message.text):
        ParamMars.earth_date = datetime.strptime(message.text, "%d.%m.%Y")
        pictures_from_mars = api_request_mars(ParamMars.earth_date, ParamMars.camera)

        for i_picture in pictures_from_mars:
            bot.send_message(message.chat.id, i_picture)
        bot.send_message(message.chat.id, "Если хочешь сменить дату, просто напиши её\n"
                                          "Если хочешь сменить камеру, введи заново /mars\n"
                                          "Посмотреть все команды можно через команду /start")
    else:
        bot.send_message(message.chat.id, "Дата задана не в нужном формате. Пример: 01.01.2023. Попробуй ещё раз.\n")
        return


@bot.message_handler(commands=["image_day"])
def set_date_for_img_day(message: Message) -> None:
    bot.send_message(
        message.chat.id,
        "Я могу отправить тебе фото дня из архива NASA, но для этого мне понадобится твоя дата."
        "\nВведи дату, в формате: 01.01.2023 "
    )
    bot.set_state(message.from_user.id, States.send_img_day, message.chat.id)


@bot.message_handler(state=States.send_img_day)
def send_img_day(message: Message) -> None:
    count = 0
    if count == 2:
        bot.set_state(message.from_user.id, States.base, message.chat.id)
    elif re.search(r"\b\d{2}.\d{2}.\d{4}\b", message.text):
        date_time = datetime.strptime(message.text, "%d.%m.%Y")
        picture_and_description = api_request_img_day(date_time.date())
        bot.send_message(message.chat.id, picture_and_description)
    else:
        bot.send_message(message.chat.id, "Дата задана не в нужном формате. Пример: 01.01.2023. Попробуй ещё раз.\n"
                                          "Посмотреть все команды можно через команду /start")
        count += 1
        return


@bot.message_handler(content_types=["text"])
def hello_send(message: Message) -> None:
    if re.search(r"[Пп]рив|[Зз]дравству[ий]|[Хх]а[ийю]|[Hh]i|[Hh]ello|[Зз]даров", message.text):
        user = User.select().where(User.username == message.from_user.username).first()
        hello_commands = ("Привет", "Здравствуй", "Хай", "Приветствую", "Хаю-хай", "Hello", "Hi",
                          "Ну привет")
        if user:
            bot.send_message(message.chat.id, random.choice(hello_commands) + ", " + message.from_user.first_name)
        else:
            bot.send_message(message.chat.id, random.choice(hello_commands) + "\nДля регистрации, "
                                                                              "используй команду /start")
    else:
        bot.send_message(message.chat.id, "Не понял тебя. Для помощи и вызова команд можешь написать /start")
    bot.set_state(message.from_user.id, States.base, message.chat.id)


if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()
