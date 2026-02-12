"""奇门遁甲阴盘排盘核心引擎（转盘法）"""

from shared.ganzhi import (
    TIANGAN, DIZHI, JIAZI_60, find_xun_head,
    hour_to_shichen_index,
)
from shared.calendar_utils import (
    get_four_pillars_raw, get_lunar_date, get_hour_ganzhi,
)
from qimen.constants import (
    SANQI_LIUYI, LUOSHU_ORDER, NINE_STARS, EIGHT_DOORS,
    EIGHT_GODS, XUN_TO_LIUYI, PALACE_NAMES,
)
from qimen.ju_calculator import calculate_ju
from qimen.palace import Palace, QimenChart


# 八宫环序（不含5宫，用于转盘旋转）
RING_ORDER = [1, 8, 3, 4, 9, 2, 7, 6]


def _lay_dipan(dun_type: str, ju_number: int) -> dict:
    """布地盘：按局数将三奇六仪放入九宫
    阳遁：从局数宫起，按宫序1→2→3→4→5→6→7→8→9顺排
    阴遁：从局数宫起，按宫序9→8→7→6→5→4→3→2→1逆排
    返回: {宫位: 奇仪}
    """
    dipan = {}
    if dun_type == "阳":
        for i, element in enumerate(SANQI_LIUYI):
            palace_num = (ju_number - 1 + i) % 9 + 1
            dipan[palace_num] = element
    else:  # 阴遁
        for i, element in enumerate(SANQI_LIUYI):
            palace_num = (ju_number - 1 - i) % 9 + 1
            dipan[palace_num] = element
    return dipan


def _find_element_palace(dipan: dict, element: str) -> int:
    """在地盘中找到某个奇仪所在的宫位"""
    for palace, elem in dipan.items():
        if elem == element:
            return palace
    return 0


def _get_hour_element(hour_gz: str) -> str:
    """获取时干对应的奇仪
    如果时干是甲，使用旬首对应的六仪
    否则直接使用时干（它本身就是奇仪之一）
    """
    hour_tg = hour_gz[0]
    if hour_tg == "甲":
        # 甲遁入六仪，找旬首对应六仪
        xun_head = find_xun_head(hour_gz)
        return XUN_TO_LIUYI.get(xun_head, "戊")
    else:
        return hour_tg


def _ring_index(palace: int) -> int:
    """获取宫位在八宫环中的索引"""
    if palace == 5:
        return RING_ORDER.index(2)  # 5寄2
    return RING_ORDER.index(palace)


def _rotate_ring(original: dict, from_palace: int, to_palace: int) -> dict:
    """转盘旋转：将 from_palace 的内容转到 to_palace，其余跟着转
    只旋转8个外宫，5宫（中宫）内容保持不变
    """
    if from_palace == 5:
        from_palace = 2  # 5寄坤2
    if to_palace == 5:
        to_palace = 2

    from_idx = RING_ORDER.index(from_palace)
    to_idx = RING_ORDER.index(to_palace)
    offset = (to_idx - from_idx) % 8

    rotated = {}
    for palace, content in original.items():
        if palace == 5:
            continue  # 5宫不参与转盘旋转
        old_idx = RING_ORDER.index(palace)
        new_idx = (old_idx + offset) % 8
        new_palace = RING_ORDER[new_idx]
        rotated[new_palace] = content

    # 5宫内容保持不变
    if 5 in original:
        rotated[5] = original[5]

    return rotated


def _build_tianpan(dipan: dict, zhifu_palace: int, hour_element_palace: int) -> dict:
    """构建天盘：值符所带奇仪转到时干落宫，其余跟转"""
    # 构建原始天盘（等于地盘）
    original = {p: e for p, e in dipan.items()}
    return _rotate_ring(original, zhifu_palace, hour_element_palace)


def _build_stars(zhifu_palace: int, hour_element_palace: int) -> dict:
    """布九星：值符星转到时干落宫
    原始九星: NINE_STARS = {1: "天蓬", 2: "天芮", ...}
    """
    original = {p: s for p, s in NINE_STARS.items()}
    return _rotate_ring(original, zhifu_palace, hour_element_palace)


def _build_doors(zhifu_palace: int, hour_element_palace: int) -> dict:
    """布八门：值使门转到时干落宫
    原始八门: EIGHT_DOORS = {1: "休门", 2: "死门", ...}
    值使门的原始宫位与值符相同
    """
    original = {p: d for p, d in EIGHT_DOORS.items() if d}  # 排除5宫空门
    return _rotate_ring(original, zhifu_palace, hour_element_palace)


def _build_gods(dun_type: str, zhifu_final_palace: int) -> dict:
    """布八神：从值符最终宫位起排
    阳遁顺排，阴遁逆排
    """
    gods = {}
    if zhifu_final_palace == 5:
        start_palace = 2
    else:
        start_palace = zhifu_final_palace
    start_idx = RING_ORDER.index(start_palace)

    for i, god_name in enumerate(EIGHT_GODS):
        if dun_type == "阳":
            idx = (start_idx + i) % 8
        else:
            idx = (start_idx - i) % 8
        palace = RING_ORDER[idx]
        gods[palace] = god_name

    return gods


def calculate_qimen(year: int, month: int, day: int, hour: int) -> QimenChart:
    """计算完整奇门遁甲阴盘

    参数:
        year, month, day: 公历日期
        hour: 0-23 小时

    返回: QimenChart 完整奇门盘
    """
    # 1. 计算局数
    ju_info = calculate_ju(year, month, day, hour)
    dun_type = ju_info["dun_type"]
    ju_number = ju_info["ju_number"]

    # 2. 获取四柱干支
    pillars = get_four_pillars_raw(year, month, day, hour)
    hour_gz = pillars["hour"]

    # 3. 布地盘
    dipan = _lay_dipan(dun_type, ju_number)

    # 4. 确定时干对应奇仪及落宫
    hour_element = _get_hour_element(hour_gz)
    hour_element_palace = _find_element_palace(dipan, hour_element)
    if hour_element_palace == 0:
        hour_element_palace = 1  # 降级处理

    # 5. 确定值符值使
    #    旬首六仪在地盘的宫位 = 值符宫
    xun_head = find_xun_head(hour_gz)
    xun_liuyi = XUN_TO_LIUYI.get(xun_head, "戊")
    zhifu_palace = _find_element_palace(dipan, xun_liuyi)
    if zhifu_palace == 0:
        zhifu_palace = 1

    # 值符星 = 值符宫的原始九星
    zhifu_star_palace = zhifu_palace if zhifu_palace != 5 else 2
    zhifu_star = NINE_STARS.get(zhifu_star_palace, "天禽")
    # 值使门 = 值符宫的原始八门
    zhishi_door = EIGHT_DOORS.get(zhifu_star_palace, "")

    # 6. 布天盘
    tianpan = _build_tianpan(dipan, zhifu_palace, hour_element_palace)

    # 7. 布九星
    stars = _build_stars(zhifu_palace, hour_element_palace)

    # 8. 布八门
    doors = _build_doors(zhifu_palace, hour_element_palace)

    # 9. 布八神（从值符最终位置起）
    zhifu_final = hour_element_palace if hour_element_palace != 5 else 2
    gods = _build_gods(dun_type, zhifu_final)

    # 10. 组装九宫
    palaces = {}
    for num in range(1, 10):
        p = Palace(number=num)
        p.dipan = dipan.get(num, "")
        p.tianpan = tianpan.get(num, dipan.get(num, ""))
        p.star = stars.get(num, NINE_STARS.get(num, ""))
        p.door = doors.get(num, "")
        p.god = gods.get(num, "")
        p.is_zhifu = (num == hour_element_palace)
        p.is_zhishi = (num == hour_element_palace)
        palaces[num] = p

    # 组装 QimenChart
    lunar = get_lunar_date(year, month, day)
    chart = QimenChart(
        solar_year=year,
        solar_month=month,
        solar_day=day,
        solar_hour=hour,
        year_gz=pillars["year"],
        month_gz=pillars["month"],
        day_gz=pillars["day"],
        hour_gz=hour_gz,
        jieqi_name=ju_info["jieqi_name"],
        yuan=ju_info["yuan"],
        dun_type=dun_type,
        ju_number=ju_number,
        zhifu_star=zhifu_star,
        zhishi_door=zhishi_door,
        zhifu_palace=hour_element_palace,
        zhishi_palace=hour_element_palace,
        palaces=palaces,
    )

    return chart
