import datetime
from collections import defaultdict
from typing import Any, Dict

import pandas as pd
import xlsxwriter
from sqlalchemy import select, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Visit, User, Point, Category, Position, TypePay
from reports.helpers import formatted_full_name, get_formatted_year_and_month, get_days_in_month, get_final_cell, \
    get_name_month, get_unvisited_day, is_weekend, color_weekend, get_work_day_amount, rounding_down, rounding_up

DELTA_MOSCOW_TIME = datetime.timedelta(hours=3)


async def collecting_data(month, year, db: AsyncSession) -> (Dict, Dict):
    """Создание отчета о количестве отработанных часов."""

    query = (
        select(
            Visit.created_at,
            User.name + ' ' + User.surname + ' ' + User.patronymic,
            Point.name,
            Position.name,
            Category.name,
            TypePay.id
        ).select_from(Visit)
        .join(User, Visit.user_id == User.user_id)
        .join(Point, User.point == Point.id)
        .join(TypePay, User.type_pay == TypePay.id)
        .join(Position, User.position == Position.id)
        .join(Category, Position.category_id == Category.id)
        .where(and_(
            User.is_active == True,
            Point.is_active == True,
            Category.is_active == True,
            Visit.is_active == True,
            extract('month', Visit.created_at) == int(month),
            extract('year', Visit.created_at) == year
        )
        )
        .order_by(Visit.created_at.desc())
    )

    visits = await db.execute(query)
    visits = visits.all()

    # Преобразование данных в dataframe
    # v = (datetime, name + ' ' + surname + ' ' + patronymic , point, position, category, type_pay)
    # v = ( 0,                 1,                               2,      3,         4,         5   )
    df = pd.DataFrame(
        [(str(v[0].date()), v[4], v[3], v[1],v[5], v[2], v[0]) for v in visits],
        columns=['date', 'category', 'position', 'user', 'type_pay', 'point', 'time'])

    # группировка по категории, пользователю, должности и времени
    grouped = df.groupby(['category', 'user', 'position', 'type_pay', 'date'])

    result = grouped.agg({'time': ['min', 'max'], 'point': 'first'})

    # таблица выглядит так:
    # категория - сотрудник - должность -> дата его отметок + точка выхода (последняя если выход на разных)

    data_per_point = defaultdict(dict)
    total_hours_month = {}

    for (category, user, position, type_pay, date), row in result.iterrows():
        # min_time = (row[('time', 'min')] + DELTA_MOSCOW_TIME).hour + 1
        # max_time = (row[('time', 'max')] + DELTA_MOSCOW_TIME).hour
        min_time = rounding_down((row[('time', 'min')] + DELTA_MOSCOW_TIME))
        max_time = rounding_up((row[('time', 'max')] + DELTA_MOSCOW_TIME))

        if min_time > max_time:
            max_time = min_time

        total_hours_month.setdefault(formatted_full_name(user), [0, 0])
        if int(date.split('-')[-1]) < 16:
            total_hours_month[formatted_full_name(user)][0] += max_time - min_time
        else:
            total_hours_month[formatted_full_name(user)][1] += max_time - min_time

        data_per_point[row['point']['first']].setdefault(category, {})
        data_per_point[row['point']['first']][category].setdefault(formatted_full_name(user), [])

        data_per_point[row['point']['first']][category][formatted_full_name(user)].append(
            {
                'position': position,
                'type_pay': type_pay,
                'date': date,
                'total_hours': max_time - min_time,
            }
        )

    return data_per_point, total_hours_month


def create_list_by_point(wb,
                         name_list,
                         data,
                         total_hours_month,
                         month,
                         year,
                         # types_pay,
                         main_fontstyle_bold_year,
                         main_fontstyle_bold_month,
                         main_fontstyle_bold_total,
                         main_fontstyle_total,
                         main_fontstyle_bold,
                         main_fontstyle_bold_gray,
                         main_fontstyle_position_gray,
                         main_fontstyle_people,
                         main_fontstyle_hour,
                         main_fontstyle_hour_weekends):

    # month, year = get_formatted_year_and_month()
    # days_amount = get_days_in_month(year, int(month))
    # month, year = '10', 2023
    days_amount = get_days_in_month(year, int(month))

    str_month = get_name_month(month)

    if len(name_list) > 23:
        name_list = name_list.split(' ')[0]

    ws = wb.add_worksheet(name_list + ' ' + month + ' ' + str(year))

    row = 1

    # Желтый год
    ws.merge_range(f"C{row}:{get_final_cell('C1', days_amount + 3)}", year, main_fontstyle_bold_year)

    row += 1
    # Зеленый месяц
    ceil = get_final_cell(f'C{row}', days_amount - 1)
    ws.merge_range(f"C{row}:{ceil}", str_month, main_fontstyle_bold_month)

    # итоги заголовок
    ceil = get_final_cell(f'C{row}', days_amount)
    ws.merge_range(f"{ceil}:{get_final_cell(ceil, 3)}", f"Итого {str_month}", main_fontstyle_bold_total)

    column = 0
    ws.write(row, column, 'ФИО', main_fontstyle_bold)
    column += 1
    ws.write(row, column, 'Должность', main_fontstyle_bold)

    # дни + итоги
    column += 1
    col_index = 1
    for col in range(column, column + days_amount):
        ws.write(row, col, col_index, main_fontstyle_bold_gray)
        col_index += 1

    column += days_amount

    ws.write(row, column, 'Часы с 1-15', main_fontstyle_total)
    column += 1
    ws.write(row, column, 'Норма часов', main_fontstyle_total)
    column += 1
    ws.write(row, column, 'Часы с 16-31', main_fontstyle_total)
    column += 1
    ws.write(row, column, 'Норма часов', main_fontstyle_total)

    # # должности + инфа
    row += 1

    for category in data:
        column = 0
        ws.write(row, column, category, main_fontstyle_position_gray)
        ws.write(row, column + 1, '', main_fontstyle_position_gray)
        ws.merge_range(f'C{row + 1}:{get_final_cell("C" + str(row + 1), days_amount + 3)}', '',
                       main_fontstyle_position_gray)
        row += 1

        # работники + посещаемость на категорию
        for employee in data[category]:
            ws.write(row, column, employee, main_fontstyle_people)
            ws.write(row, column + 1, data[category][employee][0]['position'], main_fontstyle_people)

            # проставление посещаемости
            visited_day = set()
            employee_type_pay = 0
            for day_info in data[category][employee]:
                employee_type_pay = day_info['type_pay']
                day = int(day_info['date'].split('-')[-1])
                visited_day.add(day)

                day_hours = day_info['total_hours']

                # if day_info['type_pay'] in (3, 4) and day_hours != 0: # оклад или ставка за выход
                #     day_hours = 8

                color_weekend(year, month, day, day_hours, row, main_fontstyle_hour, main_fontstyle_hour_weekends, ws)

            rest_day = get_unvisited_day(days_amount, visited_day)
            for day in rest_day:
                color_weekend(year, month, day, 0, row, main_fontstyle_hour, main_fontstyle_hour_weekends, ws)

            total1, total2 = total_hours_month[employee]

            ws.write(row, (column + 2) + days_amount, total1, main_fontstyle_bold_month)

            work_day_amount_1, work_day_amount_2 = get_work_day_amount(year, month)
            # норма часов с 1-15
            if employee_type_pay in (3, 4):
                ws.write(row, (column + 2) + days_amount + 1, 8 * work_day_amount_1, main_fontstyle_bold_month)
                ws.write(row, (column + 2) + days_amount + 3, 8 * work_day_amount_2, main_fontstyle_bold_month)
            else:
                ws.write(row, (column + 2) + days_amount + 1, '——', main_fontstyle_bold_month)
                ws.write(row, (column + 2) + days_amount + 3, '——', main_fontstyle_bold_month)
            ws.write(row, (column + 2) + days_amount + 2, total2, main_fontstyle_bold_month)

            row += 1

    ws.set_column("A:A", 23)
    ws.set_column("B:B", 23)

    start_ceil = "C1"
    end_ceil = get_final_cell(start_ceil, days_amount)
    start_ceil_total = get_final_cell(start_ceil, days_amount)
    end_ceil_total = get_final_cell(start_ceil_total, 3)
    print(start_ceil, end_ceil, start_ceil_total, end_ceil_total)

    ws.set_column(f"{start_ceil[:-1]}:{end_ceil[:-1]}", 3)
    ws.set_column(f"{start_ceil_total[:-1]}:{end_ceil_total[:-1]}", 5)
    ws.set_row(2, 23)


def create_report(month: str, year: int, data: Dict, total_hours_month: Dict, db: AsyncSession):
    """
    Создание отчета о количестве отработанных часов. На новой странице - новый месяц.
    """

    # 'point' : {'category':['date': '2023-10-20', 'full_name': 'Степанов В.',
    # 'position': 'Бариста', 'total_hours': 0}]

    wb = xlsxwriter.Workbook(f'static/reports/report_{month}_{year}.xlsx')

    # для желтого года
    main_fontstyle_bold_year = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 10,
            "bold": True,
            "bg_color": "ffff99",
            "align": "center",
            'border': 1
        }
    )

    main_fontstyle_bold_month = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 10,
            "bold": True,
            "bg_color": "ccffcc",
            "align": "center",
            'border': 1
        }
    )

    main_fontstyle_bold_total = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 10,
            "bold": True,
            "bg_color": "00ff00",
            "align": "center",
            'border': 1
        }
    )

    main_fontstyle_total = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 7,
            "bold": False,
            "bg_color": "00ff00",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "text_wrap": True
        }
    )

    main_fontstyle_bold = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 10,
            "bold": True,
            "align": "center",
            'border': 1
        }
    )

    main_fontstyle_bold_gray = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 10,
            "bold": True,
            'bg_color': 'c0c0c0',
            "align": "center",
            'border': 1
        }
    )

    main_fontstyle_position_gray = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 10,
            "bold": False,
            'bg_color': '969696',
            "align": "center",
            'border': 1
        }
    )

    main_fontstyle_people = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 10,
            "bold": False,
            "align": "left",
            'border': 1
        }
    )

    main_fontstyle_hour = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 10,
            "bold": False,
            "align": "center",
            'border': 1
        }
    )

    main_fontstyle_hour_weekends = wb.add_format(
        {
            "font_name": "Arial",
            "font_size": 10,
            "bold": False,
            "align": "center",
            'border': 1,
            "bg_color": "ff0000"
        }
    )

    # types_pay = get_all_type_pays(db)

    for point in data:

        create_list_by_point(wb,
                             point,
                             data[point],
                             total_hours_month,
                             month,
                             year,
                             # types_pay,
                             main_fontstyle_bold_year,
                             main_fontstyle_bold_month,
                             main_fontstyle_bold_total,
                             main_fontstyle_total,
                             main_fontstyle_bold,
                             main_fontstyle_bold_gray,
                             main_fontstyle_position_gray,
                             main_fontstyle_people,
                             main_fontstyle_hour,
                             main_fontstyle_hour_weekends)

    wb.close()
    return "Upload successful!"
