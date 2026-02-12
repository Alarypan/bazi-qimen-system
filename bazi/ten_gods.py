"""十神计算"""

from shared.ganzhi import TIANGAN_WUXING, TIANGAN_YINYANG, WUXING_SHENG, WUXING_KE


def get_ten_god(day_master: str, target: str) -> str:
    """计算 target 天干相对于 day_master 的十神
    day_master: 日主天干（如"甲"）
    target: 目标天干（如"丙"）
    返回: 十神名称
    """
    if day_master == target:
        return "比肩"

    wx_me = TIANGAN_WUXING[day_master]
    wx_other = TIANGAN_WUXING[target]
    yy_me = TIANGAN_YINYANG[day_master]
    yy_other = TIANGAN_YINYANG[target]
    same_yinyang = (yy_me == yy_other)

    # 同我五行
    if wx_me == wx_other:
        return "比肩" if same_yinyang else "劫财"
    # 我生
    if WUXING_SHENG[wx_me] == wx_other:
        return "食神" if same_yinyang else "伤官"
    # 我克
    if WUXING_KE[wx_me] == wx_other:
        return "偏财" if same_yinyang else "正财"
    # 克我
    if WUXING_KE[wx_other] == wx_me:
        return "七杀" if same_yinyang else "正官"
    # 生我
    if WUXING_SHENG[wx_other] == wx_me:
        return "偏印" if same_yinyang else "正印"

    return ""


def calculate_ten_gods(four_pillars):
    """为四柱设置十神（就地修改）"""
    dm = four_pillars.day_master

    four_pillars.year.ten_god = get_ten_god(dm, four_pillars.year.tiangan)
    four_pillars.month.ten_god = get_ten_god(dm, four_pillars.month.tiangan)
    four_pillars.day.ten_god = "日主"
    four_pillars.hour.ten_god = get_ten_god(dm, four_pillars.hour.tiangan)
