"""sxtwl 日历引擎封装 - 提供公历转农历、节气查询、干支转换"""

import sxtwl
from shared.ganzhi import TIANGAN, DIZHI, get_ganzhi_str, hour_to_shichen_index

# sxtwl 节气索引 → 名称（从冬至=0开始）
JIEQI_NAMES = [
    "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
    "春分", "清明", "谷雨", "立夏", "小满", "芒种",
    "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪",
]

# 节（非中气），用于八字定月柱 —— 只取"节"不取"气"
# 节气中的"节"：立春、惊蛰、清明、立夏、芒种、小暑、立秋、白露、寒露、立冬、大雪、小寒
JIE_INDICES = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]  # sxtwl index
# 对应月份（寅月=1月起）：
# 小寒(1)→丑月(12), 立春(3)→寅月(1), 惊蛰(5)→卯月(2), 清明(7)→辰月(3),
# 立夏(9)→巳月(4), 芒种(11)→午月(5), 小暑(13)→未月(6), 立秋(15)→申月(7),
# 白露(17)→酉月(8), 寒露(19)→戌月(9), 立冬(21)→亥月(10), 大雪(23)→子月(11)

JIE_TO_MONTH = {
    1: 12,   # 小寒 → 丑月(农历十二月)
    3: 1,    # 立春 → 寅月(农历正月)
    5: 2,    # 惊蛰 → 卯月
    7: 3,    # 清明 → 辰月
    9: 4,    # 立夏 → 巳月
    11: 5,   # 芒种 → 午月
    13: 6,   # 小暑 → 未月
    15: 7,   # 立秋 → 申月
    17: 8,   # 白露 → 酉月
    19: 9,   # 寒露 → 戌月
    21: 10,  # 立冬 → 亥月
    23: 11,  # 大雪 → 子月
}


def jd_to_datetime(jd: float):
    """儒略日转公历日期时间 (年,月,日,时,分)"""
    jd = jd + 0.5
    z = int(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - int(alpha / 4)
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day = b - d - int(30.6001 * e)
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    hour_frac = f * 24
    hour = int(hour_frac)
    minute = int((hour_frac - hour) * 60)
    return year, month, day, hour, minute


def get_day(year: int, month: int, day: int):
    """获取 sxtwl Day 对象"""
    return sxtwl.fromSolar(year, month, day)


def get_year_ganzhi(year: int, month: int, day: int) -> str:
    """获取年干支（考虑立春分界）"""
    d = get_day(year, month, day)
    gz = d.getYearGZ()
    return get_ganzhi_str(gz.tg, gz.dz)


def get_month_ganzhi(year: int, month: int, day: int) -> str:
    """获取月干支（节气定月 + sxtwl直接提供）"""
    d = get_day(year, month, day)
    gz = d.getMonthGZ()
    return get_ganzhi_str(gz.tg, gz.dz)


def get_day_ganzhi(year: int, month: int, day: int) -> str:
    """获取日干支"""
    d = get_day(year, month, day)
    gz = d.getDayGZ()
    return get_ganzhi_str(gz.tg, gz.dz)


def get_hour_ganzhi(year: int, month: int, day: int, hour: int) -> str:
    """获取时干支（sxtwl直接提供，hour为0-23小时）"""
    d = get_day(year, month, day)
    gz = d.getHourGZ(hour)
    return get_ganzhi_str(gz.tg, gz.dz)


def get_lunar_date(year: int, month: int, day: int) -> dict:
    """获取农历日期信息"""
    d = get_day(year, month, day)
    lunar_y = d.getLunarYear()
    lunar_m = d.getLunarMonth()
    lunar_d = d.getLunarDay()
    is_leap = d.isLunarLeap()

    # 农历日中文
    lunar_day_names = [
        "", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
        "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
        "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十",
    ]
    lunar_month_names = [
        "", "正月", "二月", "三月", "四月", "五月", "六月",
        "七月", "八月", "九月", "十月", "冬月", "腊月",
    ]

    return {
        "year": lunar_y,
        "month": lunar_m,
        "day": lunar_d,
        "is_leap": is_leap,
        "month_name": ("闰" if is_leap else "") + lunar_month_names[lunar_m],
        "day_name": lunar_day_names[lunar_d],
    }


def get_four_pillars_raw(year: int, month: int, day: int, hour: int) -> dict:
    """获取四柱原始数据
    hour: 0-23 小时
    返回: {"year": "甲子", "month": "丙寅", "day": "戊午", "hour": "壬子"}
    """
    return {
        "year": get_year_ganzhi(year, month, day),
        "month": get_month_ganzhi(year, month, day),
        "day": get_day_ganzhi(year, month, day),
        "hour": get_hour_ganzhi(year, month, day, hour),
    }


def find_jieqi_in_range(year: int, month_start: int, month_end: int) -> list:
    """查找指定年份月份范围内的所有节气
    返回: [(jieqi_index, jieqi_name, year, month, day, hour, minute), ...]
    """
    results = []
    for m in range(month_start, month_end + 1):
        for d_num in range(1, 32):
            try:
                day = get_day(year, m, d_num)
                if day.hasJieQi():
                    jq_idx = day.getJieQi()
                    jq_jd = day.getJieQiJD()
                    y, mo, da, h, mi = jd_to_datetime(jq_jd)
                    results.append((jq_idx, JIEQI_NAMES[jq_idx], y, mo, da, h, mi))
            except Exception:
                pass
    return results


def find_surrounding_jie(year: int, month: int, day: int) -> dict:
    """找到指定日期前后最近的两个'节'（非中气），用于八字定月和大运起运
    返回: {"prev_jie": {...}, "next_jie": {...}, "current_jie_index": int}
    """
    from datetime import date, timedelta

    target = date(year, month, day)
    prev_jie = None
    next_jie = None

    # 向前搜索60天，找前一个节
    for delta in range(0, 60):
        check = target - timedelta(days=delta)
        d = get_day(check.year, check.month, check.day)
        if d.hasJieQi():
            jq_idx = d.getJieQi()
            if jq_idx in JIE_INDICES:
                jq_jd = d.getJieQiJD()
                y, mo, da, h, mi = jd_to_datetime(jq_jd)
                jie_dt = date(y, mo, da)
                if jie_dt <= target:
                    prev_jie = {
                        "index": jq_idx,
                        "name": JIEQI_NAMES[jq_idx],
                        "date": jie_dt,
                        "year": y, "month": mo, "day": da,
                        "hour": h, "minute": mi,
                    }
                    break

    # 向后搜索60天，找下一个节
    for delta in range(1, 60):
        check = target + timedelta(days=delta)
        d = get_day(check.year, check.month, check.day)
        if d.hasJieQi():
            jq_idx = d.getJieQi()
            if jq_idx in JIE_INDICES:
                jq_jd = d.getJieQiJD()
                y, mo, da, h, mi = jd_to_datetime(jq_jd)
                next_jie = {
                    "index": jq_idx,
                    "name": JIEQI_NAMES[jq_idx],
                    "date": date(y, mo, da),
                    "year": y, "month": mo, "day": da,
                    "hour": h, "minute": mi,
                }
                break

    return {"prev_jie": prev_jie, "next_jie": next_jie}


def find_current_jieqi(year: int, month: int, day: int) -> dict:
    """找到当前日期所属的节气（所有24节气，含节和气）
    返回: {"index": int, "name": str, "date": date, ...}
    """
    from datetime import date, timedelta

    target = date(year, month, day)

    # 向前搜索40天找当前所属节气
    for delta in range(0, 40):
        check = target - timedelta(days=delta)
        d = get_day(check.year, check.month, check.day)
        if d.hasJieQi():
            jq_idx = d.getJieQi()
            jq_jd = d.getJieQiJD()
            y, mo, da, h, mi = jd_to_datetime(jq_jd)
            jie_dt = date(y, mo, da)
            if jie_dt <= target:
                return {
                    "index": jq_idx,
                    "name": JIEQI_NAMES[jq_idx],
                    "date": jie_dt,
                    "year": y, "month": mo, "day": da,
                    "hour": h, "minute": mi,
                    "days_since": (target - jie_dt).days,
                }
    return {}
