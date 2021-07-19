from .ubki_credit_report import get_useful_credit_report_fields
from .ubki_credit_score import get_useful_credit_score_fields

from datetime import datetime
from typing import List

import xmltodict

class UbkiReport():
    """ Класс отчет УБКИ

    Parameters
    ----------
    xml_credit_report : str
        Кредитный отчет физической особы, предпринимателя
        
    xml_credit_score : str
        Кредитный балл 

    phone : str
        Телефон 

    email : str
        Электронная почта
    """
    def __init__(self, xml_credit_report:str, xml_credit_score:str, phone:str, email:str):
        self.xml = {'report': xml_credit_report, 'score': xml_credit_score}
        self.phone = phone
        self.email = email

    def get_report_xml(self) -> str:
        """ Метод получения кредитного отчета физической особы, предпринимателя

        Returns
        -------
        ubki report : Кредитный отчет физической особы, предпринимателя
        """
        return self.xml['report']
    def get_score_xml(self) -> str:
        """ Метод получения кредитный балл

        Returns
        -------
        ubki report : Кредитний бал
        """
        return self.xml['score']

    def get_useful_ubki_fields(self, fields_to_ignore: List[str] = []) -> dict:
        """ Метод получения полезных полей из УБКИ отчета

        Parameters
        ----------
        fields_to_ignore : List[str] = []
            Список не нужных параметров, который следует исключить из итогового набора

        Returns
        -------
        useful ubki fields : Словарь полезных параметром для скоринга
        """
        ubki = {
                **get_useful_credit_report_fields(xmltodict.parse(self.xml['report']), self.phone, self.email, datetime.now()),
                **get_useful_credit_score_fields(xmltodict.parse(self.xml['score']))
                }
        return {key: ubki[key] for key in ubki if not key in fields_to_ignore}