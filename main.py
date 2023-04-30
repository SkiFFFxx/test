import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot("5358825419:AAEy4U_gS__ZZpINjw7NwJckTlwa-zyJIds")
bot.skip_pending = True
connection = sqlite3.connect("users.db", check_same_thread=False)
cursor = connection.cursor()


@bot.message_handler(
    func=lambda message: any(word in message.text.lower() for word in ['start', 'hi', 'hello', 'привет']))
def start_command(message):
    cat_png = open('cat.png', 'rb')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='booking', callback_data='booking'))
    bot.send_photo(message.chat.id, cat_png, caption='You are the best')
    bot.send_message(message.chat.id, 'Нажмите, что бы начать регистрацию', reply_markup=markup)
    bot.send_message(message.chat.id, "Привет! Если вы хотите начать заселение нажмите кнопку ВЫШЕ - booking\n"
                                      "Если вы хотите получить спавочную информацию напишите команду /help")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "booking":
        bot.send_message(call.message.chat.id, "/booking")
        booking_command(call.message)


@bot.message_handler(commands=['booking'])
def booking_command(message):
    bot.send_message(message.chat.id, "Введите ваше имя")
    bot.register_next_step_handler(message, process_name)


def process_name(message):
    if message.text == '/stop':
        bot.send_message(message.chat.id, "Заполнение данных отменено.")
        return
    if message.text.isalpha():
        name = message.text
        bot.send_message(message.chat.id, "Введите свою фамилию")
        bot.register_next_step_handler(message, process_surname, name)
    else:
        bot.send_message(message.chat.id, "Попробуйте еще раз. Используйте только буквы.")
        bot.register_next_step_handler(message, process_name)


def process_surname(message, name):
    if message.text == '/stop':
        bot.send_message(message.chat.id, "Заполнение данных отменено.")
        return
    if message.text.isalpha():
        surname = message.text
        bot.send_message(message.chat.id, "Введите номер своего дома")
        bot.register_next_step_handler(message, process_house_number, name, surname)
    else:
        bot.send_message(message.chat.id, "Попробуйте еще раз. Используйте только буквы. ")
        bot.register_next_step_handler(message, process_surname, name)


def process_house_number(message, name, surname):
    if message.text == '/stop':
        bot.send_message(message.chat.id, "Заполнение данных отменено.")
        return
    if message.text.isdigit():
        house_number = message.text
        bot.send_message(message.chat.id, "Время отдыха в неделях")
        bot.register_next_step_handler(message, process_weeks, name, surname, house_number)
    else:
        bot.send_message(message.chat.id, "Номер дома должен состоять только цифры. Попробуй еще раз.")
        bot.register_next_step_handler(message, process_house_number, name, surname)


def process_weeks(message, name, surname, house_number):
    if message.text == '/stop':
        bot.send_message(message.chat.id, "Заполнение данных отменено.")
        return
    if message.text.isdigit():
        weeks = message.text
        save_data(message.from_user.id, name, surname, house_number, weeks)
        bot.send_message(message.chat.id, "Данные успешно записаны в базу данных, для работы с записями введите /help")

    else:
        bot.send_message(message.chat.id, "Количество недель должны состоять из целых чисел. Попробуй еще раз.")
        bot.register_next_step_handler(message, process_weeks, name, surname, house_number)


def save_data(user_id, name, surname, house_number, weeks):
    values = (user_id, name, surname, house_number, weeks)
    cursor.execute("INSERT INTO users (user_id, name, surname, house_number, weeks) VALUES (?, ?, ?, ?, ?)", values)
    connection.commit()


@bot.message_handler(commands=["search"])
def search_command(message):
    bot.send_message(message.chat.id, "Введите нужную фамилию для поиска:")
    bot.register_next_step_handler(message, process_search)


def process_search(message):
    surname = message.text
    cursor.execute("SELECT * FROM users WHERE surname = ?", (surname,))
    results = cursor.fetchall()
    if len(results) == 0:
        bot.send_message(message.chat.id, "По вашему запросу ничего не найдено")
    else:
        for row in results:
            bot.send_message(message.chat.id,
                             f"ID: {row[1]}\nИмя: {row[2]}\nФамилия: {row[3]}\nНомер дома: {row[4]}\nНедели занятий: {row[5]}")


@bot.message_handler(commands=['showallsurname'])
def show_all_surnames(message):
    # markup = types.InlineKeyboardMarkup()
    # markup.add(types.InlineKeyboardButton(text='Edit surnames', callback_data='editbysurname'))
    # bot.send_message(message.chat.id, 'Нажмите, что бы начать редактирование записей', reply_markup=markup)
    cursor.execute("SELECT surname FROM users")
    results = cursor.fetchall()
    if len(results) == 0:
        bot.send_message(message.chat.id, "Список фамилий пуст.")
    else:
        surnames_list = "\n".join([row[0] for row in results])
        bot.send_message(message.chat.id, f"Список фамилий:\n{surnames_list}")




# @bot.callback_query_handler(func=lambda call: True)
# def callback_handler(call):
#     if call.data == "editbysurname":
#         bot.send_message(call.message.chat.id, "/editbysurname")
#         process_edit_surname(call.message)


@bot.message_handler(commands=['editbysurname'])
def edit_by_surname_command(message):
    bot.send_message(message.chat.id, "Введите фамилию:")
    bot.register_next_step_handler(message, process_edit_surname)


def process_edit_surname(message):
    surname = message.text
    cursor.execute("SELECT * FROM users WHERE surname=?", (surname,))
    results = cursor.fetchall()
    if len(results) == 0:
        bot.send_message(message.chat.id, "К сожалению, фамилии нет в базе данных.")
    else:
        bot.send_message(message.chat.id, "Введите новое имя:")
        bot.register_next_step_handler(message, process_edit_name, results[0])


def process_edit_name(message, user_data):
    name = message.text
    bot.send_message(message.chat.id, "Введите новый номер дома:")
    bot.register_next_step_handler(message, process_edit_house_number, user_data, name)


def process_edit_house_number(message, user_data, name):
    house_number = message.text
    bot.send_message(message.chat.id, "Введите новое количество недель:")
    bot.register_next_step_handler(message, process_edit_weeks, user_data, name, house_number)


def process_edit_weeks(message, user_data, name, house_number):
    weeks = message.text
    user_id = user_data[0]
    values = (name, house_number, weeks, user_id)
    cursor.execute("UPDATE users SET name=?, house_number=?, weeks=? WHERE user_id=?", values)
    connection.commit()
    bot.send_message(message.chat.id, "Данные успешно изменены!")


@bot.message_handler(func=lambda message: message.text.lower() == 'telebotdocs')
def show_document(message):
    docs = open('docs-python-telegram-bot-org-en-latest.pdf', 'rb')
    bot.send_document(message.chat.id, docs, caption='Here is the PDF file about TeleBot')


@bot.message_handler(commands=['help'])
def show_help(message):
    markup2 = types.InlineKeyboardMarkup()
    markup2.add(types.InlineKeyboardButton('Visit our site\n',
                                           url='https://www.google.ru/'))
    bot.send_message(message.chat.id, 'Check the site', reply_markup=markup2)
    bot.send_message(message.chat.id, '/booking - Команда для регистрации заселения в домик\n'
                                      '/start - Команда для начала работы с ботом\n'
                                      '/showallsurname - Команда для вывода всех регистраций по фамилиям\n'
                                      '/search - Команда для поиска по заселившегося по фамилии\n'
                                      '/delete - Команда для удаления регистрации по фамилии \n'
                                      '/stop - Команда для отмены в ходе регистрации заселения в домик\n'
                                      '/telebotdocs - Команда для регистрации заселения в домик '
                                      '/editbysurname - Команда для редактирования записей в таблице по фамилии'
                     )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
    show_all_surnames_command_ = types.KeyboardButton('/showallsurname')
    booking_command_ = types.KeyboardButton("/booking")
    search_command_ = types.KeyboardButton("/search")
    delete_command_ = types.KeyboardButton("/delete")
    stop_command_ = types.KeyboardButton("/stop")
    edit_by_surname_command_command_ = types.KeyboardButton("/editbysurname")
    telebotdocs_command_ = types.KeyboardButton("/telebotdocs")
    markup.add(show_all_surnames_command_,
               booking_command_,
               search_command_,
               delete_command_,
               stop_command_,
               edit_by_surname_command_command_,
               telebotdocs_command_)
    bot.send_message(message.chat.id, 'List of commands', reply_markup=markup)


@bot.message_handler(commands=["delete"])
def delete_command(message):
    bot.send_message(message.chat.id, "Введите фамилию для удаления записей:")
    bot.register_next_step_handler(message, process_delete)


def process_delete(message):
    surname = message.text
    cursor.execute("DELETE FROM users WHERE surname = ?", (surname,))
    if cursor.rowcount == 0:
        bot.send_message(message.chat.id, f"Ни одной записи с фамилией '{surname}' не было найдено в ходе поиска")
    else:
        bot.send_message(message.chat.id, f"Удалено записей: {cursor.rowcount}")
    connection.commit()


bot.polling(none_stop=True)
