"""局数计算器 - 根据节气和三元确定阳遁/阴遁第X局"""

from datetime import date, timedelta
from shared.calendar_utils import find_current_jieqi, JIEQI_NAMES, get_day
from shared.ganzhi import TIANGAN, DIZHI, JIAZI_60, find_xun_head
from qimen.constants import JU_TABLE


def get_yuan_from_day_ganzhi(day_ganzhi: str) -> str:
    """根据日干支判断上中下元
    
    规则（张志春体系）:
    - 甲子/甲午旬的日子 → 上元
    - 甲寅/甲申旬的日子 → 中元  
    - 甲辰/甲戌旬的日子 → 下元
    """
    xun_head = find_xun_head(day_ganzhi)
    if xun_head in ("甲子", "甲午"):
        return "上"
    elif xun_head in ("甲寅", "甲申"):
        return "中"
    elif xun_head in ("甲辰", "甲戌"):
        return "下"
    return "上"


def calculate_ju(year: int, month: int, day: int, hour: int = 12) -> dict:
    """计算奇门遁甲局数
    
    返回: {
        "jieqi_index": int,      # sxtwl节气索引
        "jieqi_name": str,       # 节气名称
        "yuan": str,             # "上"/"中"/"下"
        "dun_type": str,         # "阳"/"阴"
        "ju_number": int,        # 局数 1-9
        "days_since_jieqi": int, # 距节气天数
    }
    """
    # 1. 找到当前所属节气
    jieqi_info = find_current_jieqi(year, month, day)
    if not jieqi_info:
        # 降级：默认使用冬至上元阳遁1局
        return {
            "jieqi_index": 0, "jieqi_name": "冬至",
            "yuan": "上", "dun_type": "阳", "ju_number": 1,
            "days_since_jieqi": 0,
        }

    jq_idx = jieqi_info["index"]

    # 2. 根据日干支判断上中下元
    from shared.calendar_utils import get_day_ganzhi
    day_gz = get_day_ganzhi(year, month, day)
    yuan = get_yuan_from_day_ganzhi(day_gz)

    # 3. 查局数表
    if jq_idx in JU_TABLE:
        ju_info = JU_TABLE[jq_idx]
        dun_type, ju_number = ju_info[yuan]
    else:
        dun_type, ju_number = "阳", 1

    return {
        "jieqi_index": jq_idx,
        "jieqi_name": jieqi_info["name"],
        "yuan": yuan,
        "dun_type": dun_type,
        "ju_number": ju_number,
        "days_since_jieqi": jieqi_info.get("days_since", 0),
        "day_ganzhi": day_gz,
    }
