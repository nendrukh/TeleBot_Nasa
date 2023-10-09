from telebot.handler_backends import State, StatesGroup


class States(StatesGroup):
    base = State()
    send_img_day = State()
    set_camera = State()
    send_pictures = State()
