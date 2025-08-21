import re
import telebot
import telebot.types as types
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
import config  # модуль с конфигурационными данными (токен бота и т.д.)
from main import Car, Note

# Инициализация бота
bot = telebot.TeleBot(config.TOKEN)
user_data = {'current_car_id': 14, 'chat_id': 0}


@bot.message_handler(commands=['start'])
def start_command(message):
    # Отправляем оба меню одно за другим
    show_main_menu(message.chat.id)
    show_second_menu(message.chat.id)


def show_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)

    # Кнопки первого меню
    btn_create = types.InlineKeyboardButton(
        text="🚗 Создать машину",
        callback_data="command:/create_car"
    )
    btn_delete = types.InlineKeyboardButton(
        text="🗑️ Удалить машину",
        callback_data="command:/delete_car"
    )
    btn_show_list = types.InlineKeyboardButton(
        text="📋 Список активных машин",
        callback_data="command:/show_car_list"
    )
    btn_set_id = types.InlineKeyboardButton(
        text="🔢 ВЫБРАТЬ ID ДЛЯ ВЗАИМОДЕЙСТВИЯ",
        callback_data="command:/set_id"
    )
    btn_clear = types.InlineKeyboardButton(
        text=" ", callback_data=' '
    )
    markup.row(btn_create, btn_clear, btn_delete)
    markup.add(btn_clear, btn_show_list, btn_set_id)

    bot.send_message(
        chat_id,
        "🤖 <b>Главное меню</b>\n\n"
        f"<b>TЕКУЩЕЕ ID:{user_data['current_car_id']}</b>\n"
        "• 🚗 <code>/create_car</code> - создание машины\n"
        "• 🗑️ <code>/delete_car</code> - удаление машины\n"
        "• 📋 <code>/show_car_list</code> - список активных машин\n"
        "• 🔢 <code>/set_id</code> - выбрать ID для взаимодействия",
        parse_mode='HTML',
        reply_markup=markup
    )


def show_second_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)

    # Кнопки второго меню
    btn_show_list = types.InlineKeyboardButton(
        text="📋 Список активных машин",
        callback_data="command:/show_car_list"
    )
    btn_set_id = types.InlineKeyboardButton(
        text="🔢 Выбрать ID",
        callback_data="command:/set_id"
    )
    btn_add_note = types.InlineKeyboardButton(
        text="📝 Добавить запись",
        callback_data="command:/add_note"
    )
    btn_print_notes = types.InlineKeyboardButton(
        text="📄 Вывести записи",
        callback_data="command:/print_notes"
    )

    markup.add(btn_show_list, btn_set_id, btn_add_note, btn_print_notes)

    bot.send_message(
        chat_id,
        "📋 <b>Дополнительные команды</b>\n\n"
        f"<b>TЕКУЩЕЕ ID: {user_data['current_car_id']}</b>\n"
        "• 📋 <code>/show_car_list</code> - список активных машин\n"
        "• 🔢 <code>/set_id</code> - выбрать ID для взаимодействия\n"
        "• 📝 <code>/add_note</code> - добавить запись к машине\n"
        "• 📄 <code>/print_notes</code> - вывести записи машины",
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('command:'))
def handle_command_callback(call):
    """Обработчик нажатий на командные кнопки"""
    chat_id = call.message.chat.id

    # Извлекаем команду из callback_data
    command = call.data.split(':')[1]

    # Создаем mock-сообщение с командой
    class MockMessage:
        def __init__(self, chat_id, text):
            self.chat = type('Chat', (), {'id': chat_id})()
            self.text = text
            self.from_user = None

    # Создаем mock-сообщение с нужной командой
    mock_message = MockMessage(chat_id, command)

    # Вызываем соответствующий обработчик команд
    if command == '/create_car':
        init_car_command(mock_message)
        # bot.register_next_step_handler(call.message, start_command)
    elif command == '/delete_car':
        delete_car(mock_message)
        # bot.register_next_step_handler(call.message, start_command)
    elif command == '/show_car_list':
        show_car_command(mock_message)
    elif command == '/set_id':
        ask_id(mock_message)
        # bot.register_next_step_handler(call.message, start_command)
    elif command == '/add_note':
        ask_note(mock_message)
        # bot.register_next_step_handler(call.message, start_command)
    elif command == '/print_notes':
        print_notes_for_car(mock_message)
        # bot.register_next_step_handler(call.message, start_command)

    # Подтверждаем нажатие кнопки
    # bot.answer_callback_query(call.id, f"Выполняется: {command}")

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
        car = Car()
        result = car.delete_car_by_id(car_id=user_data['current_car_id'])
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, f'Вы отменили удаление машины ID:{user_data['current_car_id']}')
        return 1



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
    result = note.add_note(note_text=message.text, car_id=user_data['current_car_id'], user_id=message.from_user.username)
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

        #  Если есть дополнительные поля, добавляем их
        # if len(row) > 2:
        #     car_info += f"\nстатус: {row[2]}"

        bot.send_message(message.chat.id, car_info)

@bot.message_handler(commands=['print_notes'])
def print_notes_for_car(message):
    car = Car()
    print(user_data['current_car_id'])
    result = car.print_note(user_data['current_car_id'])
    name = car.get_car_name(user_data['current_car_id'])
    data = []
    summary = f'{name}\n'
    for n, i in result:
        data.append((i, n))
    prev_i = ''
    for i, n in sorted(data, key=lambda y: y[0]):
        if i != prev_i:
            summary += f'@{i}:\n    {n}\n'
        else:
            summary += f'   {n}\n'
        prev_i = i
    bot.send_message(message.chat.id, summary)


# Запуск бота
if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
