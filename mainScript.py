import requests
from bs4 import BeautifulSoup


class Parsebot:
    def __init__(self):
        self.__login = 'login'
        self.__password = 'password'
        self.__data = {
            'login': self.__login,
            'password': self.__password
        }
        self.__subject = []
        self.__url = "https://schools.dnevnik.ru/marks.aspx?school=35247&index=9&tab=period&homebasededucation=False"
        self.__login_url = "https://login.dnevnik.ru/"
        self.__header = {
            'Referer': 'https://dnevnik.ru/userfeed'
        }
        self.marks = {}

    def setuser(self, login, password):  # функция установки пользователя, по умолчанию пользователя нет
        self.__login = login
        self.__password = password
        self.__data = {
            'login': self.__login,
            'password': self.__password
        }

    def __getmarks(self):  # функция получения оценок, возвращает словарь с видом {предмет:[оценки]}

        # получение страницы с оценками
        with requests.Session() as s:
            s.post(self.__login_url, data=self.__data)
            req = s.get(self.__url, headers=self.__header)
            # создание файла, для удобного просмотра спарсенной информации, раскоментировать при необходимости
            '''with open('test.html', 'w') as output_file:
                output_file.write(req.text)'''

            soup = BeautifulSoup(req.content, features="lxml")
            # нахождение оценок
            mark = soup.find_all('tr')  # tr - полная линия информации предмета
            for line in range(2, len(mark)):
                self.marks[mark[line].find('td', class_='s2').text] = [item.get_text() for item in
                                                                       mark[line].select('span.mark')]
                # td.s2 - предмет, span.mark - все оценки, включая средний балл
        return self.marks

    def getsubjects(self):  # функция получения предметов, возвращает список предметов
        with requests.Session() as s:
            s.post(self.__login_url, data=self.__data)
            req = s.get(self.__url, headers=self.__header)

            soup = BeautifulSoup(req.content, features="lxml")

            mark = soup.find_all('tr')
            for line in range(2, len(mark)):
                self.__subject.append(mark[line].find('td', class_='s2').text)
        return self.__subject

    def callout_marks(self, choice: int):  # основная функция вызова списка предметов и дальнейший выбор нужного
        subj = self.getsubjects()
        mark = self.__getmarks()
        all_marks = mark[subj[choice]][:-1]  # Список оценок без среднего балла
        avg = mark[subj[choice]][-1:]  # Средний балл, пока не используется
        return all_marks
