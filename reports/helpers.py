import calendar
import datetime
from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import TypePay
from collections import defaultdict


def formatted_full_name(full_name: str) -> str:
    """ Преобразовывает ФИО в формат Фамилия И. О."""
    name, surname, patronymic = full_name.split(' ')
    return f'{surname} {name[0]}.{" " + patronymic[0] if patronymic else ""}'


def get_days_in_month(year, month) -> int:
    """ Возращате количество дней в месяце"""
    return calendar.monthrange(year, month)[1]


def get_formatted_year_and_month() -> (str, str):
    """ Форматирует месяц чтобы был 0 если цифра однознакчная"""
    year = datetime.date.today().year
    month = datetime.date.today().month
    month = ('0' + str(month)) if 1 < month < 10 else str(month)
    return month, year


def get_column_letter(column_index):
    """Получает букву столбца по его индексу (1-based)."""
    column_letter = ''
    while column_index > 0:
        column_index, remainder = divmod(column_index - 1, 26)
        column_letter = chr(65 + remainder) + column_letter
    return column_letter


def get_final_cell(start_cell, n) -> str:
    """Вычисляет конечную ячейку на основе стартовой ячейки и количества ячеек."""
    column_part = ''.join(filter(str.isalpha, start_cell))
    row_part = ''.join(filter(str.isdigit, start_cell))

    start_column_index = sum((ord(char) - 64) * (26 ** i) for i, char in enumerate(reversed(column_part)))
    end_column_index = start_column_index + n
    end_column_letter = get_column_letter(end_column_index)
    final_cell = f'{end_column_letter}{row_part}'
    return final_cell


def get_name_month(number: str) -> str:
    """Возвращает название месяца на русском языке по его номеру."""

    months = (
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    )
    return months[int(number) - 1]


def get_unvisited_day(days_amount: int, days: set) -> set:
    """ Возращает непосещенные дни в месяце"""
    all_days = set([_ for _ in range(1, days_amount + 1)])
    return all_days.difference(days)


def is_weekend(year, month, day) -> bool:
    """ Возращает True если выхлодной день (сб, вскр) и False иначе"""
    res = datetime.date(year, month, day)
    week = res.weekday()
    return week == 5 or week == 6


def color_weekend(year, month, day, day_hours, row,  main_fontstyle_hour, main_fontstyle_hour_weekends, ws) -> None:
    """ Красит выходные в красный цвет"""
    if is_weekend(year, int(month), day):
        if day_hours > 0:
            write_hour = day_hours
        else:
            write_hour = ""
        ws.write(row, 1 + day, write_hour, main_fontstyle_hour_weekends)
    else:
        ws.write(row, 1 + day, day_hours, main_fontstyle_hour)


def get_work_day_amount(year: int, month: str) -> (int, int):
    """ Считает количество рабочих дней в месяце"""
    days = get_days_in_month(year, int(month))
    weekend_counter_1 = weekend_counter_2 = 0

    for day in range(1, 16):
        if not is_weekend(year, int(month), day):
            weekend_counter_1 += 1

    for day in range(16, days + 1):
        if not is_weekend(year, int(month), day):
            weekend_counter_2 += 1

    return weekend_counter_1, weekend_counter_2

# async def get_all_type_pays(db: AsyncSession) -> Dict:
#     types_pay = await db.scalars(select(TypePay).where(TypePay.is_active == True))
#     types_pay = types_pay.all()
#
#     all_types = {}
#
#     for iter_type in types_pay:
#         all_types[iter_type.id] = iter_type.name
#     return all_types


def rounding_down(time_in) -> int:
    """ Округляет вниз если работник отемтился в течение получаса от начала смены """

    if time_in.minute <= 30:
        return time_in.hour
    return time_in.hour + 1


def rounding_up(time_out) -> int:
    """ Округляет вверх если работник отемтился в течение получаса до конца смены """

    if time_out.minute >= 30:
        return time_out.hour + 1
    return time_out.hour