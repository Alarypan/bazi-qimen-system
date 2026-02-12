"""大运流年计算"""

from dataclasses import dataclass
from datetime import date
from shared.ganzhi import TIANGAN, DIZHI, JIAZI_60, get_nayin, TIANGAN_YINYANG
from shared.calendar_utils import find_surrounding_jie


@dataclass
class DayunPeriod:
    """一步大运"""
    ganzhi: str
    nayin: str
    start_age: int
    end_age: int


def calculate_dayun(chart):
    """计算大运并填入 chart 对象

    规则:
    - 阳男阴女: 顺排（从出生日到下一个节的天数/3 = 起运年龄）
    - 阴男阳女: 逆排（从出生日到上一个节的天数/3 = 起运年龄）
    """
    year_tg = chart.four_pillars.year.tiangan
    year_yy = TIANGAN_YINYANG[year_tg]
    gender = chart.gender

    # 判断排运方向
    if (year_yy == "阳" and gender == "男") or (year_yy == "阴" and gender == "女"):
        direction = "顺"
    else:
        direction = "逆"

    chart.dayun_direction = direction

    # 找前后节
    jies = find_surrounding_jie(chart.solar_year, chart.solar_month, chart.solar_day)
    birth_date = date(chart.solar_year, chart.solar_month, chart.solar_day)

    if direction == "顺":
        # 顺排：到下一个节的天数
        if jies["next_jie"]:
            delta_days = (jies["next_jie"]["date"] - birth_date).days
        else:
            delta_days = 15  # 默认
    else:
        # 逆排：到上一个节的天数
        if jies["prev_jie"]:
            delta_days = (birth_date - jies["prev_jie"]["date"]).days
        else:
            delta_days = 15

    # 起运年龄：天数 / 3（四舍五入）
    start_age = round(delta_days / 3)
    if start_age < 1:
        start_age = 1
    chart.start_dayun_age = start_age

    # 月柱干支在六十甲子中的位置
    month_gz = chart.four_pillars.month.ganzhi
    month_idx = JIAZI_60.index(month_gz)

    # 排8步大运
    dayun_list = []
    for i in range(1, 9):
        if direction == "顺":
            idx = (month_idx + i) % 60
        else:
            idx = (month_idx - i) % 60

        gz = JIAZI_60[idx]
        period = DayunPeriod(
            ganzhi=gz,
            nayin=get_nayin(gz),
            start_age=start_age + (i - 1) * 10,
            end_age=start_age + i * 10 - 1,
        )
        dayun_list.append(period)

    chart.dayun_list = dayun_list


def get_liunian_ganzhi(year: int) -> str:
    """获取流年干支"""
    # 基准：1984年为甲子年
    idx = (year - 1984) % 60
    return JIAZI_60[idx]
