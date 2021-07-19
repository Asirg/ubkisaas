from dotenv import dotenv_values, load_dotenv, set_key, find_dotenv
from .ubki_report import UbkiReport

from datetime import datetime
from ast import literal_eval
from typing import Optional
import requests
import json

class UbkiRequest ():
    """ Класс инициализатор подключения к УБКИ.
    Предоставляет авторизацию и возможность посылания запросов на УБКИ, с целью
    получения кредитной истории конкретной персоны.

    Parameters
    ----------
    login : str
        Логин партнера для авторизации
        
    password : str
        Пароль партнера для авторизации
    
    is_test : bool = False
        Логическое выражения для опрделения запросов на тестовый сервер или оригинальный
    """
    def __init__ (self, login:str, password:str, is_test:Optional[bool] = False):
        self.is_test = is_test
        if is_test:
            self.ubki_url = "https://test.ubki.ua/b2_api_xml/ubki/xml"
        else: 
            self.ubki_url = "https://secure.ubki.ua/b2_api_xml/ubki/xml"

        config, dotenv_file = self._env()
        pref = "test" if is_test else "real"

        last_key = datetime.strptime(config[pref + '_last_key'],'%Y-%m-%d')
        now = datetime.now().date()

        if last_key.date() == now:
            self.sessid = config[pref + '_key']
        else:
            self.sessid = self.ubki_authorization(login, password)
            set_key(dotenv_file, pref + "_last_key", now.strftime('%Y-%m-%d'))
            set_key(dotenv_file, pref + "_key", self.sessid)
            print("Успешная Авторизация!!!")

    def ubki_authorization(self, login: str, password: str) -> str:
        """ Метод авторизации и получения сессионого ключа

        Parameters
        ----------
        login : str
            Логин партнера для авторизации
        
        password : str
            Пароль партнера для авторизации

        Returns
        -------
        sessid : Сессионный ключ
        """
        if self.is_test:
            url = "https://test.ubki.ua/b2_api_xml/ubki/auth"
        else:
            url = "https://secure.ubki.ua/b2_api_xml/ubki/auth"
        request_text = json.dumps(
        {
            "doc": {
                "auth": {
                    "login": login,
                    "pass": password
                }
            }
        })
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=request_text)
        return literal_eval(response.text)['doc']['auth']['sessid']

    def get_person_credit_report(self, person_data:Optional[dict] = None) -> UbkiReport:
        """ Метод получения отчета убки об интересующей персоне

        Parameters
        ----------
        person_data : dict = None
            Словарь с необходимыми данными о искомой персоне

        Returns
        -------
        ubki report : Отчет с получеными данными о искомой персоне
        """
        if person_data != None and not self.is_test:
            data = person_data
        elif person_data == None and self.is_test:
            data = \
            {"okpo":"2111118724", 
            "lname":"РИБАЧКА", "fname":"АННА", "mname":"ІГОРЕВНА", "bdate":"1957-10-19", 
            "dtype":"1", "dser":"ВВ", "dnom":"142228", 
            "cval":"+380111656411", "ctype":"3", 'email':"email@gmail.com", 'reqidout':'00001'}
        else:
            raise Exception("ERROR, mode mismatch!!")
        return UbkiReport(self._request(10, data), self._request(11, data), data['cval'], data['email'])

    def _request(self, reqtype:int, data:dict) -> str:
        """ Метод отправки запроса на получения убки отчета о искомой персоне

        Parameters
        ----------
        reqtype : int
            Номер шаблона отчета убки, который требуется получить

        data : dict
            Данные о искомой персоне, необходимые для запроса

        Returns
        -------
        response : Отчет убки полученный по запросу на искомою персону
        """
        request_text =  "<?xml version=\"1.0\" encoding=\"utf-8\" ?>"\
        "<doc>"\
            f"<ubki sessid=\"{self.sessid}\">"\
                "<req_envelope descr=\"Конверт запиту\">"\
                    "<req_xml descr=\"Об'єкт запиту\">"\
                         f"<request version=\"1.0\" reqtype=\"{reqtype}\" reqreason=\"2\" "\
                                                   f"reqdate=\"{datetime.now().strftime('%Y-%m-%d')}\" "\
                                                   f"reqidout=\"{data['reqidout']}\" reqsource=\"1\">"\
                            "<i reqlng=\"1\">"\
                                f"<ident okpo=\"{data['okpo']}\" lname=\"{data['lname']}\" "\
                                    f"fname=\"{data['fname']}\" mname=\"{data['mname']}\" bdate=\"{data['bdate']}\" />"\
                                f"<spd inn=\"{data['okpo']}\" />"\
                                "<docs>"\
                                    f"<doc dtype=\"{data['dtype']}\" dser=\"{data['dser']}\" dnom=\"{data['dnom']}\" />"\
                                "</docs>"\
                                "<contacts>"\
                                    f"<cont cval=\"{data['cval']}\" ctype=\"{data['ctype']}\" />"\
                                "</contacts>"\
                            "</i>"\
                        "</request>"\
                    "</req_xml>"\
                "</req_envelope>"\
            "</ubki>"\
        "</doc>"
        return requests.request("POST", self.ubki_url, data=request_text.encode('utf-8')).text

    def _env(self):
        """ 
        Метод подключения к .env и получения необходимых переменных среды, для работы
        """
        dotenv_file = find_dotenv()
        if dotenv_file == '': # Создание .env файла в случае отсуствия оного
                with open('.env', 'w') as file:
                    file.write("test_key=1\nreal_key=1\n")
                    file.write('test_last_key=2000-1-1\nreal_last_key=2000-1-1')
                dotenv_file = find_dotenv()
        load_dotenv(dotenv_file)
        return dotenv_values(), dotenv_file