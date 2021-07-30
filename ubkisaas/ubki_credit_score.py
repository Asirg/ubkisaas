def get_useful_credit_score_fields(ubki: dict) -> dict:
    """ Функция получения полезных параметров из кредитного балла

    Parameters
    ----------
    ubki : dict
        УБКИ отчет в виде словаря

    Returns
    -------
    useful ubki fields : Словарь полезных параметром для скоринга из кредитного балла
    """
    res_dict = {
        k: None
        for k in [
            "ubki_score",           # УБКИ очки
            "ubki_scorelast",       # УБКИ последние очки
            "ubki_scorelevel",      # УБКИ уровень очков
            "ubki_all_credits",     # Все кредиты
            "ubki_open_credits",    # Открытые кредиты
            "ubki_closed_credits",  # Закрытые кредиты
            "ubki_expyear",         # Просрочка по кредитам
            "ubki_maxnowexp",       #
            "ubki_phone_deltatime", # Разница между первым упоминанием данного телефена и текущей датой
            "ubki_email_deltatime", # Разница между первым упоминанием данного почты и текущей датой
            "ubki_week_queries"     # Количество запросов в неделю
        ]
    }
    if not ubki:
        return res_dict
    try:
        if 'ubkidata' in ubki:
            ubki_response = ubki['ubkidata']

        if "comp" in ubki_response.keys():
            for comp in ubki_response["comp"]:
                comp_id = comp["@id"]
    
                if comp_id == "8": # Кредитный рейтинг УБКИ
                    try:
                        rating = comp["urating"]
                        for i in ["@score", "@scorelast", "@scorelevel"]:
                            res_dict["ubki_" + i[1:]] = int(float(rating[i])) \
                                if (check_null_value(rating[i])) else None

                        dinfo = rating["dinfo"]
                        res_dict["ubki_all_credits"] = int(float(dinfo["@all"])) \
                            if (check_null_value(rating[i])) else None
                        res_dict["ubki_open_credits"] = int(float(dinfo["@open"])) \
                            if (check_null_value(dinfo["@open"])) else None
                        res_dict["ubki_closed_credits"] = int(float(dinfo["@close"])) \
                            if (check_null_value(dinfo["@close"])) else None
                        res_dict["ubki_expyear"] = int(coding_no_yes(dinfo["@expyear"])) \
                            if (check_null_value(dinfo["@expyear"])) else None
                        res_dict["ubki_maxnowexp"] = int(float(coding_maxnowexp(dinfo["@maxnowexp"]))) \
                            if (check_null_value(dinfo["@maxnowexp"])) else None
                    finally:
                        break

    except:
        pass
    finally:
        return res_dict

def check_null_value(value: str) -> bool:
    return value != '' and value != "NA" and value != [] and value != "null"


def coding_no_yes(arg: str) -> int:
    return 0 if (arg.lower() == "нет") else 1


def coding_maxnowexp(arg: str) -> int:
    return 0 if (arg.lower() == "нет") else arg.split(" ")[0]