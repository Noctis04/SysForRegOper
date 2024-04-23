import re
from datetime import datetime


def contains_only_numb(text, double=None):
    if double is not None:
        return re.match(r'^-?\d+(\.\d+)?$', text) is not None
    else:
        return re.match(r'^\d+$', text) is not None


def contains_only_cor_text(text):
    return not re.search(r'[!@#\$%\^&\*\(\)_\+=\[\]{};:"\\|<>\?/~]', text) is not None


def is_empty(text):
    return len(text) == 0


def has_correct_length( text, length, type=None):
    #type нужен чтобы указать должна ли строка иметь строгое огрнаничение на длину или не допускать больше какого-то кол-ва симоволов
    if type == None:
        return len(text) <= length
    else:
        return len(text) == length


def correct_cod_aprtmt(cod):
    return re.match(r'^[0-9:]+$', cod) is not None


def is_cor_date(date_text):
    # Проверяем формат "ГГГГ-ММ-ДД"
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_text):
        return False

    # Теперь проверяем, соответствует ли дата реальной дате
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return False  # Если не удалось преобразовать в реальную дату, значит дата недействительна

    return True