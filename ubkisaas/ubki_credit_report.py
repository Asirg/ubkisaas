from typing import List
import datetime as dt
import numpy as np
import datetime

def get_useful_credit_report_fields(ubki: dict, phone: str, email: str, our_date: datetime) -> dict:
    """ Функция получения полезных параметров из кредитного отчета физического лица

    Parameters
    ----------
    ubki : dict
        УБКИ отчет в виде словаря

    phone : str
        Телефон, для вычисления самой раннего упоминания даного контакта

    email : str
        Электронная почта, для вычисления самой раннего упоминания даного контакта

    our_date : datetime
        Дата получения отчета

    Returns
    -------
    useful ubki fields : Словарь полезных параметром для скоринга из кредитного отчета
    """
    res_dict = {
        k: None
        for k in [
            "median_day_credit",    # Медианна по дате начала соглашения
            "mean_credit_summ",     # Средняя сумма по кредитам
            "mean_credit_debt",     # Средння задолжность по кредитам
            "cdolgn",               # Последняя зафиксированая должность на работе
            "wdohod",               # Последний зафиксированый доход на работе
            "wstag",                # Последний зафиксированый стаж на работе
            "max_wdohod",           # Максимальный зафиксировынный доход
            "cgrag",                # Код странны (категориальный)
            "sstate",               # Социальный статус (категориальный)
            "family",               # Симейный статус (категориальный)
            "ceduc",                # Образование (категориальный)
            "ubki_balance_value",   # Текущий баланс
            "ubki_phone_deltatime", # Разница между первым упоминанием данного телефена и текущей датой
            "ubki_email_deltatime", # Разница между первым упоминанием данного почты и текущей датой
            "ubki_week_queries"     # Количество запросов в неделю
        ]
    }
    try:
        if 'ubkidata' in ubki:
            ubki_response = ubki['ubkidata']
        try: # Системные данные
            if "tech" in ubki_response.keys() and "billing" in ubki_response['tech'].keys(): 
                res_dict["ubki_balance_value"] = int(
                    float(ubki_response['tech']["billing"]["balance"]["@value"]))  # Баланс 
        except:
            pass
        # Персональные данные
        if "comp" in ubki_response.keys():
            for comp in ubki_response["comp"]:
                comp_id = comp["@id"]
                
                if comp_id == '1': # Блок персональных данных

                    try: # Данные про субьект
                        comp_ident = comp['cki']['ident']
                        if type(comp_ident) == list:
                            for ident in comp_ident:
                                fill_dict_by_key(ident, ["@cgrag", '@sstate', '@family', '@ceduc'], res_dict)
                        else:
                            fill_dict_by_key(ident, ["@cgrag", '@sstate', '@family', '@ceduc'], res_dict)
                    except:
                        pass
                    
                    try: # Данные про роботу
                        comp_work = comp['cki']['work']
                        if type(comp_work) == list:
                            for work in comp_work:
                                fill_dict_by_key(work, ['@cdolgn', '@wdohod', '@wstag'], res_dict)
                        else:
                            fill_dict_by_key(comp_work, ['@cdolgn', '@wdohod', '@wstag'], res_dict)
                    except :
                        pass

                elif comp_id == '2': # Блок информации про кредитные соглашения
                    try:
                        ubki_crdeal = comp['crdeal']
                        credit_sum = credits = 0        # Сумма кредита и количество кредитов
                        credit_debt = debts = 0         # Сумма задолжности по кредиту
                        median_days = np.array([0, 0])  # Сумма по дням в половинах месяца
                        if type(ubki_crdeal) == list:   # Проверка на количество кредитов
                            for credit in ubki_crdeal:
                                amount, debt, days = get_credit_ubki_fields(credit)
                                if amount > 0:          # Проверка на наличие кредитной суммы
                                    credit_sum += amount
                                    credits += 1
                                if debt > 0:            # Проверка на наличие задолжности по кредитному соглашению
                                    credit_debt += debt
                                    debts += 1
                                median_days += days
                        else:                           # Только один кредит
                            credit_sum, credit_debt, median_days = get_credit_ubki_fields(ubki_crdeal)
                            credits = 1 if (credit_sum > 0) else 0
                            debts = 1 if (credit_debt > 0) else 0

                        res_dict['median_day_credit'] = int(np.argmax(median_days))
                        res_dict['mean_credit_summ'] = int(credit_sum / credits)
                        res_dict['mean_credit_debt'] = int(credit_debt / debts)
                    except:
                        pass

                elif comp_id == "4": # Блок регестрации запросов
                    try:
                        res_dict["ubki_week_queries"] = int(comp["reestrtime"]["@wk"])  # Количество запросов в неделю
                        res_dict["req_credit"] = sum([1 for i in comp['credres'] if i['@reqreason'] in ['2', '4']]) # Количество запросов на кредит
                    except:
                        pass

                if comp_id == "10": # Блок истории контактных данных
                    try:
                        big_datetime = dt.datetime(dt.datetime.today().year + 1, 1, 1)
                        first_datetime_phone = first_datetime_email = big_datetime
                        for contact in comp["cont"]:
                            cval = contact["@cval"]
                            vdate = contact["@vdate"]

                            # Нахождения самого раннего упоминания телефона
                            if cval.replace('+', '') == str(phone).replace('+', ''):
                                if format_date(vdate) < first_datetime_phone:
                                    first_datetime_phone = format_date(vdate)

                            # Нахождения самого раннего упоминания електронной почты
                            elif str(cval.lower()) == str(email):
                                if format_date(vdate) < first_datetime_email:
                                    first_datetime_email = format_date(vdate)

                        res_dict["ubki_phone_deltatime"] = int((our_date - first_datetime_phone).days) if (
                                first_datetime_phone != big_datetime) else None
                        res_dict["ubki_email_deltatime"] = int((our_date - first_datetime_email).days) if (
                                first_datetime_email != big_datetime) else None
                    except:
                        pass
    except:
        print("Ошибка УБКИ")
    finally:
        return res_dict

def fill_dict_by_key(values:dict, keys:List[str], full_dict:dict) -> dict:
    """ Функция получения списка значения по списку ключей

    Parameters
    ----------
    values : dict
        Словарь с данными

    keys : List[str] 
        Список необходимых ключей

    full_dict : dict
        Полный словарь, к которому добавяться данные

    Returns
    -------
    full dict: Словарь с полученными всеми или присутствубщимы данными
    """
    for key in keys:
        full_dict[key[1:]] = float(values[key]) if check_null_value(values[key]) else full_dict[key[1:]]
    return full_dict

def get_credit_ubki_fields(credit: dict) -> float:
    """ Функция получения полезной информации о каждом кредите

    Parameters
    ----------
    credit : dict
        Кредит, который будет источником информации

    Returns
    -------
    userful credit fields : Полезные значения для скоринга о кредитных соглашениях"""
    credit_amount = float(credit['@dlamt']) # Сумма кредита
    credit = credit['deallife']

    # Проверка на количество записей в кредитной истории
    if type(credit) == list:
        credit_date = format_date(credit[0]['@dlds'])
        credit_debt = max([float(dl['@dlamtcur']) for dl in credit]) # Вычесление максимальной задолжности
    else:
        credit_date = format_date(credit['@dlds'])
        credit_debt = float(credit['@dlamtcur'])
    median_days =  [1, 0] if credit_date.day < 15 else [0, 1]
    
    return credit_amount, credit_debt, median_days

def format_date(attribute: str) -> datetime:
    return dt.datetime.strptime(attribute, "%Y-%m-%d")

def check_null_value(value: str) -> bool:
    return value != '' and value != "NA" and value != [] and value != "null"
