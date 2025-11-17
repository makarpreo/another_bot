import re
import telebot
import telebot.types as types
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
import config  # модуль с конфигурационными данными (токен бота и т.д.)
from main import Car, Note

user_sessions = {}

user_id_list = [5506674973, #макан
                997097309, #макар
                24260386,] #папа
#                 1576118658, #саша солома
#                 7645088510, #руслан
#                 1497728313, #alexnader
#                 1062205174] #денис
def id_handler(func):
    """Декоратор для обработки ошибок"""
    def wrapper(*args, **kwargs):
        user_info = None
        if args[0] in user_id_list:
            print('first if')
            return func(*args, **kwargs)
        if args and hasattr(args[0], 'from_user'):
            user = args[0].from_user
            print('second if')
            if user.id in user_id_list:
                return func(*args, **kwargs)
    return wrapper

# @id_handler
def get_user_data(user_id):
    """Получает или создает данные пользователя"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'current_car_id': 0,
            'chat_id': 0,
            'username': f"user_{user_id}",
            'notes_data': {},
            'editing_note_id': None,
            'editing_note_text': None
        }
    return user_sessions[user_id]


# Инициализация бота
bot = telebot.TeleBot(config.TOKEN)

@id_handler
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    username = message.from_user.username or message.from_user.first_name or f"user_{user_id}"
    user_data['username'] = username
    user_data['chat_id'] = message.chat.id

    # Отправляем оба меню одно за другим
    show_main_menu(message.chat.id, user_data)
    # show_second_menu(message.chat.id, user_data)


@id_handler
def show_main_menu(chat_id, user_data):
    markup = types.InlineKeyboardMarkup(row_width=1)

    # Кнопки первого меню
    btn_create = types.InlineKeyboardButton(
        text="🚗 Создать машину",
        callback_data="command:/create_car"
    )
    btn_set_id = types.InlineKeyboardButton(
        text="🔢 ВЫБРАТЬ МАШИНУ",
        callback_data="command:/select_car"
    )
    btn_clear = types.InlineKeyboardButton(
        text=" ", callback_data=' '
    )
    btn_archive = types.InlineKeyboardButton(
        text="📁 Архив", callback_data='/archive'
    )
    btn_move_archive = types.InlineKeyboardButton(
        text="🚗➡️📁 ТЕКУЩУЮ МАШИНУ В АРХИВ", callback_data='car_to_archive'
    )
    markup.add(btn_create, btn_set_id, btn_move_archive, btn_archive)

    bot.send_message(
        chat_id,
        "🤖 <b>Главное меню</b>\n\n"
        f"<b>ТЕКУЩАЯ МАШИНА: ID {user_data['current_car_id']}</b>\n",
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('command:'))
@id_handler
def handle_command_callback(call):
    """Обработчик нажатий на командные кнопки"""
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    user_data = get_user_data(user_id)

    # Извлекаем команду из callback_data
    command = call.data.split(':')[1]

    # Создаем mock-сообщение с командой
    class MockMessage:
        def __init__(self, chat_id, text):
            self.chat = type('Chat', (), {'id': chat_id})()
            self.text = text
            self.from_user = call.from_user

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
    elif '/archive' in command:
        show_archive_by_month(mock_message)
    elif command == '/add_note':
        ask_note(mock_message)
    elif command == '/print_notes':
        print_notes_for_car(user_id)
    elif command == '/do_car_active_again':
        do_car_active_again_command(mock_message)

    # Подтверждаем нажатие кнопки
    bot.answer_callback_query(call.id, f"Выполняется: {command}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_car:'))
@id_handler
def handle_car_selection(call):
    """Обработчик выбора машины из списка"""
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    user_data = get_user_data(user_id)

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
    show_main_menu(chat_id, user_data)
    print_notes_for_car(user_id)

    # Подтверждаем нажатие
    bot.answer_callback_query(call.id, f"Выбрана машина: {car_name}")

@bot.message_handler(commands=['select_car'])
@id_handler
def select_car_from_list(message):
    """Показать список машин для выбора"""
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

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

    bot.send_message(
        message.chat.id,
        "📋 <b>Выберите машину для работы:</b>\n\n"
        f"Текущая машина: ID {user_data['current_car_id']}",
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == 'do_car_active_again')
@id_handler
def handle_do_car_active_again(call):
    user_id = call.from_user.id
    user_data = get_user_data(user_id)
    car = Car()
    result = car.do_car_active_again(user_data['current_car_id'])
    bot.send_message(user_data['chat_id'], result)
    bot.answer_callback_query(call.id, "Машина активирована")


@id_handler
def do_car_active_again_command(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    car = Car()
    result = car.do_car_active_again(user_data['current_car_id'])
    bot.send_message(user_data['chat_id'], result)


@bot.callback_query_handler(func=lambda call: call.data == 'car_to_archive')
@id_handler
def confirm_car_to_archive(call):
    user_id = call.from_user.id
    user_data = get_user_data(user_id)
    bot.send_message(
        user_data['chat_id'],
        "Введите 'Подтвердить', если хотите перенести машину в архив",
    )
    bot.register_next_step_handler(call.message, car_to_archive)


@id_handler
def car_to_archive(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    if message.text == 'Подтвердить':
        car = Car()
        result = car.move_car_to_archive(car_id=user_data['current_car_id'])
        bot.send_message(message.chat.id, result)
    else:
        markup = InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔢 Выбрать машину", callback_data="command:/select_car"))
        bot.send_message(message.chat.id, f'Вы отменили перемещение в архив машины ID:{user_data["current_car_id"]}')

@bot.callback_query_handler(func=lambda call: call.data == '/archive')
def show_archive_by_month(call):
    markup = InlineKeyboardMarkup()
    markup.add(
    types.InlineKeyboardButton(text="Январь", callback_data="/archive:1"),
    types.InlineKeyboardButton(text="Февраль", callback_data="/archive:2"),
    types.InlineKeyboardButton(text="Март", callback_data="/archive:3"),
    types.InlineKeyboardButton(text="Апрель", callback_data="/archive:4"),
    types.InlineKeyboardButton(text="Май", callback_data="/archive:5"),
    types.InlineKeyboardButton(text="Июнь", callback_data="/archive:6"),
    types.InlineKeyboardButton(text="Июль", callback_data="/archive:7"),
    types.InlineKeyboardButton(text="Август", callback_data="/archive:8"),
    types.InlineKeyboardButton(text="Сентябрь", callback_data="/archive:9"),
    types.InlineKeyboardButton(text="Октябрь", callback_data="/archive:10"),
    types.InlineKeyboardButton(text="Ноябрь", callback_data="/archive:11"),
    types.InlineKeyboardButton(text="Декабрь", callback_data="/archive:12"),)
    bot.send_message(chat_id=call.from_user.id, text='Выберите месяц', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('/archive:'))
@id_handler
def select_archive_car_from_list(call):
    """Показать список машин для выбора"""
    user_id = call.from_user.id
    user_data = get_user_data(user_id)
    month = int(call.data.split(':')[1])

    car = Car()
    results = car.show_archive_by_month(month)

    if isinstance(results, str):  # Если вернулась ошибка
        bot.send_message(call.message.chat.id, results)
        return

    if not results:
        bot.send_message(call.message.chat.id, "Нет машин в архиве.")
        return

    # Создаем inline клавиатуру с машинами
    markup = types.InlineKeyboardMarkup(row_width=1)

    for row in results:
        car_id = row[1]  # ID машины
        car_name = row[0] if len(row) > 1 else f"Машина {car_id}"  # Название
        date = str(row[2])[5:10]
        # Создаем кнопку для каждой машины
        btn_car = types.InlineKeyboardButton(
            text=f"{car_name} {date[3]+date[4]}.{date[0]+date[1]} (ID: {car_id})",
            callback_data=f"select_archive_car:{car_id}"
        )
        markup.add(btn_car)

    bot.send_message(
        call.message.chat.id,
        "📋 <b>Архив</b>\n\n"
        f"Выберите машину для справки",
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_archive_car:'))
@id_handler
def handle_archive_car_selection(call):
    """Обработчик выбора машины из архива"""
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    user_data = get_user_data(user_id)

    # Извлекаем ID машины из callback_data
    car_id = int(call.data.split(':')[1])

    # Устанавливаем выбранную машину
    user_data['current_car_id'] = car_id
    user_data['chat_id'] = chat_id

    # Получаем название машины для красивого сообщения
    car = Car()
    car_name = car.get_car_name(car_id) or f"ID {car_id}"

    markup = InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="⚡Сделать машину снова активной", callback_data="do_car_active_again"))

    # Отправляем подтверждение
    bot.send_message(chat_id, f"✅ Выбрана машина из архива: {car_name} (ID: {car_id})", reply_markup=markup)

    # Обновляем меню с новым ID
    show_main_menu(chat_id, user_data)
    print_notes_for_archive_car(user_id)

    # Подтверждаем нажатие
    bot.answer_callback_query(call.id, f"Выбрана машина: {car_name}")


@bot.message_handler(commands=['set_id'])
@id_handler
def ask_id(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    bot.send_message(
        message.chat.id,
        "Напишите ID машины с которой вы будете взаимодействовать:",
    )
    bot.register_next_step_handler(message, set_id)


@id_handler
def set_id(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    if str(message.text).isdecimal():
        user_data['current_car_id'] = int(message.text)
        user_data['chat_id'] = message.chat.id

        # Получаем название машины для подтверждения
        car = Car()
        car_name = car.get_car_name(user_data['current_car_id']) or f"ID {user_data['current_car_id']}"

        bot.send_message(message.chat.id, f"✅ ID машины установлен: {car_name}")
    else:
        bot.send_message(message.chat.id, "❌ Операция отменена. Введите числовой ID.")


# @id_handler
# def select_car_command(message):
#     """Обработчик команды /select_car"""
#     select_car_from_list(message)


@bot.message_handler(commands=['create_car'])
@id_handler
def init_car_command(message):
    markup = ReplyKeyboardMarkup()
    bot.send_message(
        message.chat.id,
        "Введите название машины:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, add_car)


@id_handler
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
@id_handler
def delete_car(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    bot.send_message(
        user_data['chat_id'],
        "Введите 'Подтвердить', если хотите удалить машину",
    )
    bot.register_next_step_handler(message, delete)


@id_handler
def delete(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    if message.text == 'Подтвердить':
        car = Car()
        result = car.delete_car_by_id(car_id=user_data['current_car_id'])
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, f'Вы отменили удаление машины ID:{user_data["current_car_id"]}')


@bot.message_handler(commands=['add_note'])
@id_handler
def ask_note(message):
    markup = ReplyKeyboardMarkup()
    bot.send_message(
        message.chat.id,
        "Введите запись которую вы хотите добавить:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, add_note_to_car)


@id_handler
def add_note_to_car(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    note = Note()
    username = message.from_user.username or message.from_user.first_name or f"user_{message.from_user.id}"
    result = note.add_note(note_text=message.text, car_id=user_data['current_car_id'], user_id=username)
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['show_car_list'])
@id_handler
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


@id_handler
def print_notes_for_car(user_id):
    user_data = get_user_data(user_id)

    markup = InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="Редактировать сообщения",
        callback_data=f"edit_last_note:{user_id}"
    ))
    markup.add(types.InlineKeyboardButton(
        text="📝 Добавить запись",
        callback_data="command:/add_note"
    ))

    car = Car()
    note = Note()

    result = note.get_notes_with_ids(user_data['current_car_id'])

    if not result:
        bot.send_message(user_data['chat_id'], 'Для этой машины пока нет записей', reply_markup=markup)
        return None

    if isinstance(result, str) and 'Ошибка' in result:
        bot.send_message(user_data['chat_id'], result)
        return

    user_data['notes_data'] = {}
    for note_id, note_text, username in result:
        user_data['notes_data'][note_id] = (note_text, username)

    name = car.get_car_name(user_data['current_car_id']) or f"ID {user_data['current_car_id']}"
    summary = f'🚗 {name}\n\n'

    user_notes = {}
    for note_id, note_text, username in result:
        if username not in user_notes:
            user_notes[username] = []
        user_notes[username].append(note_text)

    for username, notes in user_notes.items():
        summary += f'👤 @{username}:\n'
        for i, note_text in enumerate(notes, 1):
            summary += f'    {i}. {note_text}\n'
        summary += '\n'

    bot.send_message(user_data['chat_id'], summary, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_last_note:'))
@id_handler
def ask_edit_last_note(call):
    """Показать список сообщений для редактирования"""
    user_id = int(call.data.split(':')[1])
    user_data = get_user_data(user_id)

    note = Note()
    result = note.get_notes_with_ids(user_data['current_car_id'])

    if not result or (isinstance(result, str) and 'Ошибка' in result):
        bot.send_message(user_data['chat_id'], "Нет сообщений для редактирования")
        bot.answer_callback_query(call.id, "Нет сообщений")
        return

    user_data['notes_data'] = {}
    for note_id, note_text, username in result:
        user_data['notes_data'][note_id] = (note_text, username)

    markup = types.InlineKeyboardMarkup(row_width=1)

    for note_id, note_text, username in result:
        truncated_text = (note_text[:17] + "...") if len(note_text) > 20 else note_text

        btn_note = types.InlineKeyboardButton(
            text=f"📝 #{note_id}: {truncated_text}",
            callback_data=f"select_note:{note_id}:{user_id}"
        )
        markup.add(btn_note)

    btn_cancel = types.InlineKeyboardButton(
        text="❌ Отмена",
        callback_data=f"cancel_note_select:{user_id}"
    )
    markup.add(btn_cancel)

    bot.send_message(
        user_data['chat_id'],
        "📋 <b>Выберите сообщение для редактирования:</b>\n\n"
        "💡 <i>Цифра перед текстом - ID сообщения в базе данных</i>",
        parse_mode='HTML',
        reply_markup=markup
    )

    bot.answer_callback_query(call.id, "Выберите сообщение")


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_note:'))
@id_handler
def handle_note_selection(call):
    """Обработчик выбора сообщения для редактирования"""
    parts = call.data.split(':')
    note_id = int(parts[1])
    user_id = int(parts[2])
    user_data = get_user_data(user_id)

    if note_id not in user_data.get('notes_data', {}):
        bot.send_message(user_data['chat_id'], "❌ Сообщение не найдено")
        bot.answer_callback_query(call.id, "Ошибка")
        return

    note_text, username = user_data['notes_data'][note_id]

    user_data['editing_note_id'] = note_id
    user_data['editing_note_text'] = note_text

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text="✏️ Редактировать текст", callback_data=f"edit_note_text:{note_id}:{user_id}"),
        types.InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_note:{note_id}:{user_id}")
    )
    markup.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_action:{user_id}"))

    display_text = note_text[:100] + "..." if len(note_text) > 100 else note_text

    bot.send_message(
        user_data['chat_id'],
        f"📝 <b>Сообщение для редактирования:</b>\n\n"
        f"<b>ID в БД:</b> {note_id}\n"
        f"<b>Пользователь:</b> @{username}\n"
        f"<b>Текст:</b>\n<i>{display_text}</i>\n\n"
        f"Выберите действие:",
        parse_mode='HTML',
        reply_markup=markup
    )

    bot.answer_callback_query(call.id, f"Выбрано сообщение #{note_id}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_note_text:'))
@id_handler
def start_edit_note_text(call):
    """Начинаем редактирование текста сообщения"""
    parts = call.data.split(':')
    note_id = int(parts[1])
    user_id = int(parts[2])
    user_data = get_user_data(user_id)

    if note_id not in user_data.get('notes_data', {}):
        bot.send_message(user_data['chat_id'], "❌ Сообщение не найдено")
        bot.answer_callback_query(call.id, "Ошибка")
        return

    note_text, username = user_data['notes_data'][note_id]
    user_data['editing_note_id'] = note_id
    user_data['editing_note_text'] = note_text

    display_text = note_text[:100] + "..." if len(note_text) > 100 else note_text

    bot.send_message(
        user_data['chat_id'],
        f"✏️ <b>Редактирование сообщения #{note_id}:</b>\n\n"
        f"<b>Текущий текст:</b>\n<i>{display_text}</i>\n\n"
        f"Введите новый текст сообщения:",
        parse_mode='HTML'
    )

    bot.register_next_step_handler(call.message, lambda m: edit_note_text(m, user_id))
    bot.answer_callback_query(call.id, "Введите новый текст")


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_note:'))
@id_handler
def delete_note(call):
    """Удаление сообщения"""
    parts = call.data.split(':')
    note_id = int(parts[1])
    user_id = int(parts[2])
    user_data = get_user_data(user_id)

    if note_id not in user_data.get('notes_data', {}):
        bot.send_message(user_data['chat_id'], "❌ Сообщение не найдено")
        bot.answer_callback_query(call.id, "Ошибка")
        return

    note_text, username = user_data['notes_data'][note_id]

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete:{note_id}:{user_id}"),
        types.InlineKeyboardButton(text="❌ Нет, отмена", callback_data=f"cancel_action:{user_id}")
    )

    display_text = note_text[:100] + "..." if len(note_text) > 100 else note_text

    bot.send_message(
        user_data['chat_id'],
        f"🗑️ <b>Подтвердите удаление:</b>\n\n"
        f"<b>ID:</b> {note_id}\n"
        f"<b>Текст:</b>\n<i>{display_text}</i>\n\n"
        f"Вы уверены, что хотите удалить это сообщение?",
        parse_mode='HTML',
        reply_markup=markup
    )

    bot.answer_callback_query(call.id, "Подтвердите удаление")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete:'))
@id_handler
def confirm_delete_note(call):
    """Подтверждение удаления сообщения"""
    parts = call.data.split(':')
    note_id = int(parts[1])
    user_id = int(parts[2])
    user_data = get_user_data(user_id)

    note = Note()
    result = note.delete_note_by_id(note_id)

    if "успешно" in result.lower() or "удален" in result.lower():
        bot.send_message(user_data['chat_id'], f"✅ Сообщение #{note_id} удалено")
        print_notes_for_car(user_id)
    else:
        bot.send_message(user_data['chat_id'], f"❌ Ошибка при удалении: {result}")

    bot.answer_callback_query(call.id, "Удаление выполнено")


@id_handler
def edit_note_text(message, user_id):
    """Обработчик ввода нового текста для сообщения"""
    user_data = get_user_data(user_id)

    if 'editing_note_id' not in user_data:
        bot.send_message(message.chat.id, "❌ Ошибка: сообщение не выбрано")
        return

    new_text = message.text
    note_id = user_data['editing_note_id']
    old_text = user_data.get('editing_note_text', '')

    note = Note()
    result = note.update_note_text(note_id, new_text)

    if "успешно" in result.lower() or "обновлен" in result.lower():
        old_display = old_text[:100] + "..." if len(old_text) > 100 else old_text
        new_display = new_text[:100] + "..." if len(new_text) > 100 else new_text

        bot.send_message(
            message.chat.id,
            f"✅ Сообщение обновлено:\n\n",
            parse_mode='HTML'
        )
        print_notes_for_car(user_id)
    else:
        bot.send_message(message.chat.id, f"❌ Ошибка при обновлении: {result}")

    user_data.pop('editing_note_id', None)
    user_data.pop('editing_note_text', None)


@id_handler
def print_notes_for_archive_car(user_id):
    user_data = get_user_data(user_id)

    car = Car()
    archive_result = car.print_note(user_data['current_car_id'])
    result = car.print_note(user_data['current_car_id'])

    if not result:
        bot.send_message(user_data['chat_id'], 'Для этой машины пока нет записей')
        return None
    if 'Ошибка' in result:
        bot.send_message(user_data['chat_id'], result)

    name = car.get_car_name(user_data['current_car_id'])
    data = []
    summary = f''

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
    bot.infinity_polling()