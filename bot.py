import re
import telebot
from telebot.types import ReplyKeyboardMarkup
import config  # модуль с конфигурационными данными (токен бота и т.д.)
from main import Car, Note

# Инициализация бота
bot = telebot.TeleBot(config.TOKEN)
user_data = {'current_car_id': 0, 'chat_id': 0}


@bot.message_handler(commands=['set_id'])
def ask_id(message):
    bot.send_message(
        message.chat.id,
        "Напишите ID машины с которой вы будете взаимодействовать:",
    )


def set_id(message):
    user_data['current_car_id'] = message.text


# Обработчик текстовых сообщений
@bot.message_handler(commands=['create_car'])
def init_car_command(message):
    markup = ReplyKeyboardMarkup()
    bot.send_message(
        message.chat.id,
        "Введите название машины:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, add_car)


def add_car(message):
    car = Car()
    if re.match(r'^/', message.text):
        bot.send_message(
            message.chat.id,
            'отправьте еще раз'
        )
        return None
    result = car.add_car(car_name=message.text)
    bot.send_message(
        message.chat.id,
        result
    )


@bot.message_handler(commands=['delete_car'])
def delete_car(message):
    car = Car()
    result = car.delete_car_by_id(car_id=user_data['current_car_id'])
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['add_note'])
def ask_note(message):
    markup = ReplyKeyboardMarkup()
    bot.send_message(
        message.chat.id,
        "Введите запись которую вы хотите добавить:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, add_note_to_car)


def add_note_to_car(message):
    note = Note()
    result = note.add_note(note_text=message.text, car_id=user_data['current_car_id'])
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['show_car_list'])
def show_car_command(message):
    car = Car()
    results = car.show_active_list()
    markup = ReplyKeyboardMarkup()
    bot.send_message(
        message.chat.id,
        "список активных машин:",
        reply_markup=markup
    )
    for row in results:
        bot.send_message(
            message.chat.id,
            *row,
            reply_markup=markup
        )


@bot.message_handler(commands=['print_notes'])
def print_notes_for_car(message):
    car = Car()
    result = car.print_note(user_data['current_car_id'])
    for row in result:
        bot.send_message(message.chat.id, row)


# Запуск бота
if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
