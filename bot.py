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
    bot.register_next_step_handler(message, set_id)

def set_id(message):
    global user_data  # Объявляем доступ к глобальной переменной
    if str(message.text).isdecimal():
        user_data['current_car_id'] = int(message.text)  # Преобразуем в число
    else:
        bot.send_message(message.chat.id, f"операция отменена, повторите команду")
    user_data['chat_id'] = message.chat.id
    bot.send_message(message.chat.id, f"ID машины установлен: {user_data['current_car_id']}")


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
            'отправьте команду еще раз'
        )
        return None
    result = car.add_car(car_name=message.text)
    bot.send_message(
        message.chat.id,
        result
    )


@bot.message_handler(commands=['delete_car'])
def delete_car(message):
    bot.send_message(
        user_data['chat_id'],
        "Введите Подтвердить, если хотите удалить машину",
    )
    bot.register_next_step_handler(message, delete)

def delete(message):
    if message.text == 'Подтвердить':
        bot.send_message(message.chat.id, f'Машина ID:{user_data['current_car_id']} удалена')
    else:
        bot.send_message(message.chat.id, f'Вы отменили удаление машины ID:{user_data['current_car_id']}')
        return 1
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

    if isinstance(results, str):  # Если вернулась ошибка
        bot.send_message(message.chat.id, results)
        return

    if not results:
        bot.send_message(message.chat.id, "Нет активных машин.")
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    # Отправляем заголовок
    bot.send_message(
        message.chat.id,
        "Список активных машин:",
        reply_markup=markup
    )

    # Форматируем каждую запись
    for row in results:
        # Предполагаемая структура таблицы cars: (id, name, ...)
        car_id = row[0]  # ID машины (первый столбец)
        car_name = row[1] if len(row) > 1 else "Без названия"  # Название (второй столбец)

        # Форматируем сообщение
        car_info = f"ID: {car_id}\nНазвание: {car_name}"

        # Если есть дополнительные поля, добавляем их
        if len(row) > 2:
            car_info += f"\nстатус: {row[2]}"

        bot.send_message(message.chat.id, car_info)

@bot.message_handler(commands=['print_notes'])
def print_notes_for_car(message):
    car = Car()
    print(user_data['current_car_id'])
    result = car.print_note(user_data['current_car_id'])
    for row in result:
        bot.send_message(message.chat.id, row)


# Запуск бота
if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
