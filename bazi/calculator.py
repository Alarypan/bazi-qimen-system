"""八字四柱计算器"""

from dataclasses import dataclass
from typing import List
from shared.ganzhi import (
    TIANGAN, DIZHI, get_nayin, get_canggan, TIANGAN_WUXING,
    TIANGAN_YINYANG, DIZHI_WUXING, hour_to_shichen_index,
    SHICHEN_NAMES,
)
from shared.calendar_utils import (
    get_four_pillars_raw, get_lunar_date, find_surrounding_jie,
    find_current_jieqi,
)


@dataclass
class Pillar:
    """单柱"""
    tiangan: str       # 天干
    dizhi: str         # 地支
    canggan: list      # 藏干
    nayin: str         # 纳音
    ten_god: str = ""  # 十神（相对日主）

    @property
    def ganzhi(self) -> str:
        return self.tiangan + self.dizhi

    @property
    def tg_wuxing(self) -> str:
        return TIANGAN_WUXING.get(self.tiangan, "")

    @property
    def dz_wuxing(self) -> str:
        return DIZHI_WUXING.get(self.dizhi, "")

    @property
    def tg_yinyang(self) -> str:
        return TIANGAN_YINYANG.get(self.tiangan, "")


@dataclass
class FourPillars:
    """四柱八字"""
    year: Pillar
    month: Pillar
    day: Pillar    # 日主
    hour: Pillar

    @property
    def day_master(self) -> str:
        """日主天干"""
        return self.day.tiangan

    def all_pillars(self) -> list:
        return [self.year, self.month, self.day, self.hour]


@dataclass
class BaziChart:
    """完整八字盘"""
    # 出生信息
    solar_year: int
    solar_month: int
    solar_day: int
    solar_hour: int
    gender: str  # "男" / "女"

    # 农历信息
    lunar_info: dict

    # 四柱
    four_pillars: FourPillars

    # 节气
    jieqi_info: dict

    # 大运（由 dayun 模块计算后填入）
    dayun_list: list = None
    start_dayun_age: int = 0
    dayun_direction: str = ""  # "顺" / "逆"


def build_pillar(ganzhi_str: str) -> Pillar:
    """从干支字符串构建 Pillar"""
    tg = ganzhi_str[0]
    dz = ganzhi_str[1]
    return Pillar(
        tiangan=tg,
        dizhi=dz,
        canggan=get_canggan(dz),
        nayin=get_nayin(ganzhi_str),
    )


def calculate_bazi(year: int, month: int, day: int, hour: int, gender: str = "男") -> BaziChart:
    """计算完整八字
    year, month, day: 公历
    hour: 0-23小时
    gender: "男" / "女"
    """
    # 获取四柱干支
    raw = get_four_pillars_raw(year, month, day, hour)

    # 构建四柱
    year_p = build_pillar(raw["year"])
    month_p = build_pillar(raw["month"])
    day_p = build_pillar(raw["day"])
    hour_p = build_pillar(raw["hour"])

    four_pillars = FourPillars(
        year=year_p,
        month=month_p,
        day=day_p,
        hour=hour_p,
    )

    # 计算十神
    from bazi.ten_gods import calculate_ten_gods
    calculate_ten_gods(four_pillars)

    # 农历信息
    lunar = get_lunar_date(year, month, day)

    # 时辰
    shichen_idx = hour_to_shichen_index(hour)
    shichen_name = SHICHEN_NAMES[shichen_idx]

    # 节气
    jieqi = find_current_jieqi(year, month, day)

    chart = BaziChart(
        solar_year=year,
        solar_month=month,
        solar_day=day,
        solar_hour=hour,
        gender=gender,
        lunar_info={**lunar, "shichen": shichen_name},
        four_pillars=four_pillars,
        jieqi_info=jieqi,
    )

    # 计算大运
    from bazi.dayun import calculate_dayun
    calculate_dayun(chart)

    return chart
