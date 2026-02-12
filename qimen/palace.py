"""九宫数据结构"""

from dataclasses import dataclass, field
from qimen.constants import PALACE_NAMES, PALACE_DIRECTIONS, STAR_JIXI, DOOR_JIXI


@dataclass
class Palace:
    """单个宫位"""
    number: int        # 宫位序号 1-9
    name: str = ""     # 坎宫/坤宫...
    direction: str = ""

    dipan: str = ""    # 地盘奇仪
    tianpan: str = ""  # 天盘奇仪
    star: str = ""     # 九星
    door: str = ""     # 八门
    god: str = ""      # 八神

    is_zhifu: bool = False   # 是否值符所在宫
    is_zhishi: bool = False  # 是否值使所在宫

    def __post_init__(self):
        if not self.name:
            self.name = PALACE_NAMES.get(self.number, "")
        if not self.direction:
            self.direction = PALACE_DIRECTIONS.get(self.number, "")

    @property
    def star_jixi(self) -> str:
        return STAR_JIXI.get(self.star, "")

    @property
    def door_jixi(self) -> str:
        return DOOR_JIXI.get(self.door, "")


@dataclass
class QimenChart:
    """完整奇门盘"""
    # 时间信息
    solar_year: int = 0
    solar_month: int = 0
    solar_day: int = 0
    solar_hour: int = 0

    # 干支信息
    year_gz: str = ""
    month_gz: str = ""
    day_gz: str = ""
    hour_gz: str = ""

    # 局信息
    jieqi_name: str = ""
    yuan: str = ""        # 上/中/下
    dun_type: str = ""    # 阳/阴
    ju_number: int = 0

    # 值符值使
    zhifu_star: str = ""
    zhishi_door: str = ""
    zhifu_palace: int = 0
    zhishi_palace: int = 0

    # 九宫
    palaces: dict = field(default_factory=dict)  # {1: Palace, 2: Palace, ...}

    # AI 解读
    ai_reading: str = ""
