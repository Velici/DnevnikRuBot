import telebot
import config
import mainScript

bot = telebot.TeleBot(config.token)  # основная инициализация бота
pars = mainScript.Parsebot()  # объект класса mainScript, который парсит дневник.ру
data = {}  # словарь с данными о пользователе вида user_id: [login, password]
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)  # клавиатура со значениями, приведенными ниже
item1 = telebot.types.KeyboardButton("Логин")
item2 = telebot.types.KeyboardButton("Оценки")
item3 = telebot.types.KeyboardButton("Домашнее задание")
markup.add(item1, item2, item3)
subj_dict = {}  # словарь с предметами и порядковым номером вида subject: id(предмет: номер)


@bot.message_handler(commands=['go', 'start'])  # обработчик команд /start /go
def welcome(message):  # функция, которая вызывается после команд сверху
    bot.send_message(message.chat.id, "Приветствую, для начала задайте логин для вашего аккаунта тг "
                                      "после вы сможете запрашивать как оценки, так и домашнее задание",
                     reply_markup=markup)  # приветственное сообщение


@bot.message_handler(content_types=["text"])  # обработчик любых текстовых сообщений
def send_messages(message):  # основная функция бота
    subj_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # создание доп клавиатуры для предметов при вызове функции оценок
    a = 0
    if message.chat.type == "private":  # бот принимает только личные сообщения
        if message.text == "Логин":
            # если боту отправлено логин - отправляет сообщение и активирует функцию add_login

            bot.send_message(message.chat.id, "Введите логин и пароль")
            bot.register_next_step_handler(message, add_login)  # обработчик "следующего шага" для слова "Логин"
        elif message.text == "Оценки":
            pars.setuser(data[message.chat.id][0], data[message.chat.id][1])  # логин в дневник.ру через mainScript
            subj = pars.getsubjects()  # получение списка предметов
            for i in subj:  # добавление в доп клавиатуру и в словарь предметы
                subj_markup.add(i)
                subj_dict[i] = a
                a += 1
            bot.send_message(message.chat.id, "Выберите предмет", reply_markup=subj_markup)
            bot.register_next_step_handler(message, show_marks)  # обработчик "следующего шага" для слова "Оценки"
            """ если боту отправлено оценки - отправляет сообщение с выбором предмета, изменяет клавиатуру
            и активирует функцию show_marks"""
        elif message.text == "Домашнее задание":  # пока не доделано, WiP
            bot.send_message(message.chat.id, "Работа в процессе")
        if message.text == "Назад":
            bot.send_message(message.chat.id, "Отмена", reply_markup=markup)


def add_login(message):
    """ добавляет данные пользователя в список data
    (в планах ввести проверку правильности введенного логина и пароля)"""
    auth = list(message.text.split(" "))
    data[message.chat.id] = auth
    bot.send_message(message.chat.id, "Готово")


def show_marks(message):  # функция показа оценок по предмету
    choice = message.text
    pars.setuser(data[message.chat.id][0], data[message.chat.id][1])
    marks = pars.callout_marks(subj_dict[choice])
    if len(marks) > 0:
        bot.send_message(message.chat.id, "Ваши оценки по предмету {}:\n {}".format(choice, marks), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Нет оценок", reply_markup=markup)


if __name__ == "__main__":  # главная функция вызова
    try:
        bot.enable_save_next_step_handlers()  # включение сохранения обработчика "следующего шага"
        bot.load_next_step_handlers()  # загрузка обработчика "следующего шага"
        bot.polling(none_stop=True)  # чтобы бот не останавливался
    except ConnectionError as e:
        print("Ошибка подключения, ", e)
    except Exception as r:
        print("Ошибка, ", r)
    finally:
        print("Конец программы")
