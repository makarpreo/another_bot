import re
import telebot
import telebot.types as types
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
import config  # модуль с конфигурационными данными (токен бота и т.д.)
from main import Car, Note

# Инициализация бота
bot = telebot.TeleBot(config.TOKEN)
user_data = {'current_car_id': 0, 'chat_id': 0}


@bot.message_handler(commands=['start'])
def start_command(message):
    # Отправляем оба меню одно за другим
    show_main_menu(message.chat.id)
    # show_second_menu(message.chat.id)


def show_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)

    # Кнопки первого меню
    btn_create = types.InlineKeyboardButton(
        text="🚗 Создать машину",
        callback_data="command:/create_car"
    )
    # btn_delete = types.InlineKeyboardButton(
    #     text="🗑️ Удалить машину",
    #     callback_data="command:/delete_car"
    # )
    # btn_show_list = types.InlineKeyboardButton(
    #     text="📋 Список активных машин",
    #     callback_data="command:/show_car_list"
    # )
    btn_set_id = types.InlineKeyboardButton(
        text="🔢 ВЫБРАТЬ МАШИНУ",
        callback_data="command:/select_car"
    )
    btn_clear = types.InlineKeyboardButton(
        text=" ", callback_data=' '
    )
    btn_archive = types.InlineKeyboardButton(
        text="📁 Архив", callback_data='command:/archive'
    )
    btn_move_archive = types.InlineKeyboardButton(
        text="🚗➡️📁 ТЕКУЩУЮ МАШИНУ В АРХИВ", callback_data='car_to_archive'
    )
    markup.add(btn_create, btn_set_id, btn_move_archive, btn_archive)

    bot.send_message(
        chat_id,
        "🤖 <b>Главное меню</b>\n\n"
        f"<b>ТЕКУЩАЯ МАШИНА: ID {user_data['current_car_id']}</b>\n",
        # "• 🚗 <code>/create_car</code> - создание машины\n"
        # "• 🗑️ <code>/delete_car</code> - удаление машины\n"
        # "• 📋 <code>/show_car_list</code> - список активных машин\n"
        # "• 🔢 <code>/select_car</code> - выбрать машину из списка",
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
        text="🔢 Выбрать машину",
        callback_data="command:/select_car"
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
        f"<b>ТЕКУЩАЯ МАШИНА: ID {user_data['current_car_id']}</b>\n"
        "• 📋 <code>/show_car_list</code> - список активных машин\n"
        "• 🔢 <code>/select_car</code> - выбрать машину из списка\n"
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
    elif command == '/delete_car':
        delete_car(mock_message)
    elif command == '/show_car_list':
        show_car_command(mock_message)
    elif command == '/set_id':
        ask_id(mock_message)
    elif command == '/select_car':
        select_car_from_list(mock_message)
    elif command == '/archive':
        select_archive_car_from_list(mock_message)
    elif command == '/add_note':
        ask_note(mock_message)
    elif command == '/print_notes':
        print_notes_for_car()
    elif command == '/do_car_active_again':
        do_car_active_again()

    # Подтверждаем нажатие кнопки
    # bot.answer_callback_query(call.id, f"Выполняется: {command}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_car:'))
def handle_car_selection(call):
    """Обработчик выбора машины из списка"""
    chat_id = call.message.chat.id

    # Извлекаем ID машины из callback_data
    car_id = int(call.data.split(':')[1])

    # Устанавливаем выбранную машину
    user_data['current_car_id'] = car_id
    user_data['chat_id'] = chat_id

    # Получаем название машины для красивого сообщения
    car = Car()
    car_name = car.get_car_name(car_id) or f"ID {car_id}"

    # Отправляем подтверждение
    bot.send_message(chat_id, f"✅ Выбрана машина: {car_name} (ID: {car_id})")

    # Обновляем меню с новым ID
    show_main_menu(chat_id)
    # show_second_menu(chat_id)

    # Подтверждаем нажатие
    # bot.answer_callback_query(call.id, f"Выбрана машина: {car_name}")
    print_notes_for_car()


def select_car_from_list(message):
    """Показать список машин для выбора"""
    car = Car()
    results = car.show_active_list()

    if isinstance(results, str):  # Если вернулась ошибка
        bot.send_message(message.chat.id, results)
        return

    if not results:
        bot.send_message(message.chat.id, "Нет активных машин.")
        return

    # Создаем inline клавиатуру с машинами
    markup = types.InlineKeyboardMarkup(row_width=1)

    for row in results:
        car_id = row[0]  # ID машины
        car_name = row[1] if len(row) > 1 else f"Машина {car_id}"  # Название

        # Создаем кнопку для каждой машины
        btn_car = types.InlineKeyboardButton(
            text=f"{car_name} (ID: {car_id})",
            callback_data=f"select_car:{car_id}"
        )
        markup.add(btn_car)

    # Добавляем кнопку отмены
    # btn_cancel = types.InlineKeyboardButton(
    #     text="❌ Отмена",
    #     callback_data="cancel_select"
    # )
    # btn_archive = types.InlineKeyboardButton(
    #     text="🚗➡️📁 ТЕКУЩУЮ МАШИНУ В АРХИВ", callback_data='car_to_archive'
    # )
    # markup.add(btn_archive)

    bot.send_message(
        message.chat.id,
        "📋 <b>Выберите машину для работы:</b>\n\n"
        f"Текущая машина: ID {user_data['current_car_id']}",
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == 'do_car_active_again')
def do_car_active_again():
    car = Car()
    result = car.do_car_active_again(user_data['current_car_id'])
    bot.send_message(user_data['chat_id'], result)


@bot.callback_query_handler(func=lambda call: call.data == 'car_to_archive')
def confirm_car_to_archive(call):
    bot.send_message(
        user_data['chat_id'],
        "Введите 'Подтвердить', если хотите перенести машину в архив",
    )
    bot.register_next_step_handler(call.message, car_to_archive)


def car_to_archive(message):
    if message.text == 'Подтвердить':
        car = Car()
        result = car.move_car_to_archive(car_id=user_data['current_car_id'])
        bot.send_message(message.chat.id, result)
    else:
        markup = InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔢 Выбрать машину", callback_data="command:/select_car"))
        bot.send_message(message.chat.id, f'Вы отменили перемещение в архив машины ID:{user_data["current_car_id"]}')


#
# @bot.callback_query_handler(func=lambda call: call.data.startswith('select_archive_car:'))
# def handle_archive_car_selection(call):
#     """Обработчик выбора машины из списка"""
#     chat_id = call.message.chat.id
#
#     # Извлекаем ID машины из callback_data
#     car_id = int(call.data.split(':')[1])
#
#     # Устанавливаем выбранную машину
#     user_data['current_car_id'] = car_id
#     user_data['chat_id'] = chat_id
#
#     # Получаем название машины для красивого сообщения
#     car = Car()
#     car_name = car.get_car_name(car_id) or f"ID {car_id}"
#
#     # Отправляем подтверждение
#     bot.send_message(chat_id, f"✅ Выбрана машина: {car_name} (ID: {car_id})")
#
#     # Обновляем меню с новым ID
#     show_main_menu(chat_id)
#     # show_second_menu(chat_id)
#
#     # Подтверждаем нажатие
#     bot.answer_callback_query(call.id, f"Выбрана машина: {car_name}")
#     print_notes_for_car()

def select_archive_car_from_list(message):
    """Показать список машин для выбора"""
    car = Car()
    results = car.show_not_active_list()

    if isinstance(results, str):  # Если вернулась ошибка
        bot.send_message(message.chat.id, results)
        return

    if not results:
        bot.send_message(message.chat.id, "Нет машин в архиве.")
        return

    # Создаем inline клавиатуру с машинами
    markup = types.InlineKeyboardMarkup(row_width=1)

    for row in results:
        car_id = row[0]  # ID машины
        car_name = row[1] if len(row) > 1 else f"Машина {car_id}"  # Название

        # Создаем кнопку для каждой машины
        btn_car = types.InlineKeyboardButton(
            text=f"{car_name} (ID: {car_id})",
            callback_data=f"select_archive_car:{car_id}"
        )
        markup.add(btn_car)

    # Добавляем кнопку отмены
    # btn_cancel = types.InlineKeyboardButton(
    #     text="❌ Отмена",
    #     callback_data="cancel_select"
    # )
    # btn_archive = types.InlineKeyboardButton(
    #     text="🚗➡️📁 ТЕКУЩУЮ МАШИНУ В АРХИВ", callback_data='car_to_archive'
    # )
    # markup.add(btn_archive)

    bot.send_message(
        message.chat.id,
        "📋 <b>Архив</b>\n\n"
        f"Выберите машину для справки",
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_archive_car:'))
def handle_car_selection(call):
    """Обработчик выбора машины из списка"""
    chat_id = call.message.chat.id
    markup = InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="⚡Сделать машину снова активной", callback_data="command:/do_car_active_again"))
    # Извлекаем ID машины из callback_data
    car_id = int(call.data.split(':')[1])

    # Устанавливаем выбранную машину
    user_data['current_car_id'] = car_id
    user_data['chat_id'] = chat_id

    # Получаем название машины для красивого сообщения
    car = Car()
    car_name = car.get_car_name(car_id) or f"ID {car_id}"
    show_main_menu(chat_id)

    # Отправляем подтверждение
    bot.send_message(chat_id, f"✅ Выбрана машина: {car_name} (ID: {car_id})", reply_markup=markup)

    # Обновляем меню с новым ID
    # show_second_menu(chat_id)

    # Подтверждаем нажатие
    # bot.answer_callback_query(call.id, f"Выбрана машина: {car_name}")
    print_notes_for_archive_car()


@bot.message_handler(commands=['set_id'])
def ask_id(message):
    bot.send_message(
        message.chat.id,
        "Напишите ID машины с которой вы будете взаимодействовать:",
    )
    bot.register_next_step_handler(message, set_id)


def set_id(message):
    global user_data
    if str(message.text).isdecimal():
        user_data['current_car_id'] = int(message.text)
        user_data['chat_id'] = message.chat.id

        # Получаем название машины для подтверждения
        car = Car()
        car_name = car.get_car_name(user_data['current_car_id']) or f"ID {user_data['current_car_id']}"

        bot.send_message(message.chat.id, f"✅ ID машины установлен: {car_name}")
    else:
        bot.send_message(message.chat.id, "❌ Операция отменена. Введите числовой ID.")


@bot.message_handler(commands=['select_car'])
def select_car_command(message):
    """Обработчик команды /select_car"""
    select_car_from_list(message)


# Остальные функции остаются без изменений
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
        "Введите 'Подтвердить', если хотите удалить машину",
    )
    bot.register_next_step_handler(message, delete)


def delete(message):
    if message.text == 'Подтвердить':
        car = Car()
        result = car.delete_car_by_id(car_id=user_data['current_car_id'])
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, f'Вы отменили удаление машины ID:{user_data["current_car_id"]}')


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
    username = message.from_user.username or message.from_user.first_name or f"user_{message.from_user.id}"
    result = note.add_note(note_text=message.text, car_id=user_data['current_car_id'], user_id=username)
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['show_car_list'])
def show_car_command(message):
    car = Car()
    results = car.show_active_list()

    if isinstance(results, str):
        bot.send_message(message.chat.id, results)
        return

    if not results:
        bot.send_message(message.chat.id, "Нет активных машин.")
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    bot.send_message(message.chat.id, "Список активных машин:", reply_markup=markup)

    for row in results:
        car_id = row[0]
        car_name = row[1] if len(row) > 1 else "Без названия"
        car_info = f"ID: {car_id}\nНазвание: {car_name}"
        bot.send_message(message.chat.id, car_info)


@bot.message_handler(commands=['print_notes'])
def print_notes_for_car():
    car = Car()
    result = car.print_note(user_data['current_car_id'])
    if not result:
        bot.send_message(user_data['chat_id'], 'Для этой машины пока нет записей')
        return None
    if 'Ошибка' in result:
        bot.send_message(user_data['chat_id'], result)
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
    bot.send_message(user_data['chat_id'], summary)


def print_notes_for_archive_car():
    car = Car()
    archive_result = car.archive_car_info(user_data['current_car_id'])
    result = car.print_note(user_data['current_car_id'])
    if not result:
        bot.send_message(user_data['chat_id'], 'Для этой машины пока нет записей')
        return None
    if 'Ошибка' in result:
        bot.send_message(user_data['chat_id'], result)
    name = car.get_car_name(user_data['current_car_id'])
    data = []
    summary = f'{archive_result}\n\n{name}\n'
    for n, i in result:
        data.append((i, n))
    prev_i = ''
    for i, n in sorted(data, key=lambda y: y[0]):
        if i != prev_i:
            summary += f'@{i}:\n    {n}\n'
        else:
            summary += f'   {n}\n'
        prev_i = i
    bot.send_message(user_data['chat_id'], summary)


# Запуск бота
if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
