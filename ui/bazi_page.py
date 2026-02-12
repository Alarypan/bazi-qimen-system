"""八字排盘页面"""

import streamlit as st
import sxtwl
from datetime import datetime, date
from shared.ganzhi import SHICHEN_NAMES, TIANGAN_WUXING, DIZHI_WUXING

LUNAR_MONTH_NAMES = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "腊月",
]


def _lunar_to_solar(l_year: int, l_month: int, l_day: int, is_leap: bool = False):
    """农历转公历，返回 (year, month, day) 或 None"""
    try:
        d = sxtwl.fromLunar(l_year, l_month, l_day, is_leap)
        return d.getSolarYear(), d.getSolarMonth(), d.getSolarDay()
    except Exception:
        return None


def render_bazi_page():
    # ===== 输入区 =====
    st.subheader("请输入出生信息")

    # 阴历/阳历切换
    cal_type = st.radio("日历类型", ["阳历（公历）", "阴历（农历）"], horizontal=True, key="bazi_cal_type")

    if cal_type == "阳历（公历）":
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            birth_date = st.date_input(
                "出生日期（公历）",
                value=date(1990, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date(2100, 12, 31),
                key="bazi_date",
            )
            solar_year, solar_month, solar_day = birth_date.year, birth_date.month, birth_date.day
    else:
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            l_year = st.number_input("农历年", 1900, 2100, 1990, key="bazi_lyear")
        with col2:
            l_month_sel = st.selectbox("农历月", LUNAR_MONTH_NAMES, key="bazi_lmonth")
            l_month = LUNAR_MONTH_NAMES.index(l_month_sel) + 1
        with col3:
            l_day = st.number_input("农历日", 1, 30, 1, key="bazi_lday")

        is_leap = st.checkbox("闰月", key="bazi_leap")

        result = _lunar_to_solar(l_year, l_month, l_day, is_leap)
        if result:
            solar_year, solar_month, solar_day = result
            st.caption(f"对应公历：{solar_year}-{solar_month:02d}-{solar_day:02d}")
        else:
            st.warning("该农历日期无效，请检查")
            solar_year, solar_month, solar_day = 1990, 1, 1
        col4 = st.columns(1)[0]  # 性别用新行

    # 时辰和性别（两种模式共用）
    if cal_type == "阳历（公历）":
        with col2:
            shichen_options = ["自动（按小时）"] + [
                f"{SHICHEN_NAMES[i]}（{h[0]:02d}:00-{h[1]:02d}:00）"
                for i, h in enumerate([
                    (23, 1), (1, 3), (3, 5), (5, 7), (7, 9), (9, 11),
                    (11, 13), (13, 15), (15, 17), (17, 19), (19, 21), (21, 23),
                ])
            ]
            shichen_sel = st.selectbox("时辰", shichen_options, key="bazi_shichen")
        with col3:
            if shichen_sel == "自动（按小时）":
                birth_hour = st.number_input("出生小时", 0, 23, 8, key="bazi_hour")
            else:
                idx = shichen_options.index(shichen_sel) - 1
                hour_map = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
                birth_hour = hour_map[idx]
                st.text(f"对应 {birth_hour}:00")
        with col4:
            gender = st.radio("性别", ["男", "女"], horizontal=True, key="bazi_gender")
    else:
        sc_col, hr_col, gd_col = st.columns([2, 1, 1])
        with sc_col:
            shichen_options = ["自动（按小时）"] + [
                f"{SHICHEN_NAMES[i]}（{h[0]:02d}:00-{h[1]:02d}:00）"
                for i, h in enumerate([
                    (23, 1), (1, 3), (3, 5), (5, 7), (7, 9), (9, 11),
                    (11, 13), (13, 15), (15, 17), (17, 19), (19, 21), (21, 23),
                ])
            ]
            shichen_sel = st.selectbox("时辰", shichen_options, key="bazi_shichen_l")
        with hr_col:
            if shichen_sel == "自动（按小时）":
                birth_hour = st.number_input("出生小时", 0, 23, 8, key="bazi_hour_l")
            else:
                idx = shichen_options.index(shichen_sel) - 1
                hour_map = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
                birth_hour = hour_map[idx]
                st.text(f"对应 {birth_hour}:00")
        with gd_col:
            gender = st.radio("性别", ["男", "女"], horizontal=True, key="bazi_gender_l")

    if st.button("开始排盘", type="primary", key="bazi_btn"):
        with st.spinner("正在排盘计算..."):
            from bazi.calculator import calculate_bazi
            chart = calculate_bazi(
                solar_year, solar_month, solar_day,
                birth_hour, gender,
            )
            st.session_state["bazi_chart"] = chart

    # ===== 展示区 =====
    if "bazi_chart" not in st.session_state:
        return

    chart = st.session_state["bazi_chart"]
    fp = chart.four_pillars
    lunar = chart.lunar_info

    st.divider()

    # 基本信息
    info_cols = st.columns(4)
    with info_cols[0]:
        st.markdown(f'<span class="info-tag">公历 {chart.solar_year}-{chart.solar_month:02d}-{chart.solar_day:02d}</span>', unsafe_allow_html=True)
    with info_cols[1]:
        st.markdown(f'<span class="info-tag">农历 {lunar["month_name"]}{lunar["day_name"]}</span>', unsafe_allow_html=True)
    with info_cols[2]:
        st.markdown(f'<span class="info-tag">{lunar["shichen"]}</span>', unsafe_allow_html=True)
    with info_cols[3]:
        if chart.jieqi_info:
            st.markdown(f'<span class="info-tag">节气: {chart.jieqi_info.get("name", "")}</span>', unsafe_allow_html=True)

    st.markdown("### 四柱八字")

    # 四柱表格 (HTML)
    html = '<table class="pillar-table">'
    html += '<tr><th></th><th>年柱</th><th>月柱</th><th>日柱</th><th>时柱</th></tr>'

    pillars = [fp.year, fp.month, fp.day, fp.hour]
    labels_cn = ["年柱", "月柱", "日柱", "时柱"]

    # 十神行
    html += '<tr><td style="color:#c8c0d8;">十神</td>'
    for p in pillars:
        html += f'<td>{p.ten_god}</td>'
    html += '</tr>'

    # 天干行
    html += '<tr><td style="color:#c8c0d8;">天干</td>'
    for p in pillars:
        wx = TIANGAN_WUXING.get(p.tiangan, "")
        color = _wuxing_color(wx)
        html += f'<td style="font-size:1.4em;color:{color};font-weight:bold;">{p.tiangan}</td>'
    html += '</tr>'

    # 地支行
    html += '<tr><td style="color:#c8c0d8;">地支</td>'
    for p in pillars:
        wx = DIZHI_WUXING.get(p.dizhi, "")
        color = _wuxing_color(wx)
        html += f'<td style="font-size:1.4em;color:{color};font-weight:bold;">{p.dizhi}</td>'
    html += '</tr>'

    # 藏干行
    html += '<tr><td style="color:#c8c0d8;">藏干</td>'
    for p in pillars:
        cg_str = " ".join(p.canggan)
        html += f'<td style="font-size:0.9em;">{cg_str}</td>'
    html += '</tr>'

    # 纳音行
    html += '<tr><td style="color:#c8c0d8;">纳音</td>'
    for p in pillars:
        html += f'<td style="font-size:0.85em;color:#c8c0d8;">{p.nayin}</td>'
    html += '</tr>'

    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)

    # 日主信息
    dm = fp.day_master
    dm_wx = TIANGAN_WUXING[dm]
    dm_color = _wuxing_color(dm_wx)
    st.markdown(
        f"**日主**: <span style='color:{dm_color};font-size:1.2em;font-weight:bold;'>"
        f"{dm}（{dm_wx}）</span> &nbsp; "
        f"大运方向: **{chart.dayun_direction}排** &nbsp; 起运年龄: **{chart.start_dayun_age}岁**",
        unsafe_allow_html=True,
    )

    # ===== 大运 =====
    if chart.dayun_list:
        st.markdown("### 大运排盘")
        current_age = datetime.now().year - chart.solar_year
        dayun_html = '<div style="display:flex;flex-wrap:wrap;">'
        for d in chart.dayun_list:
            is_current = d.start_age <= current_age <= d.end_age
            cls = "dayun-item current" if is_current else "dayun-item"
            dayun_html += (
                f'<div class="{cls}">'
                f'<div style="font-size:1.1em;font-weight:bold;">{d.ganzhi}</div>'
                f'<div style="font-size:0.75em;">{d.start_age}-{d.end_age}岁</div>'
                f'<div style="font-size:0.7em;opacity:0.6;">{d.nayin}</div>'
                f'</div>'
            )
        dayun_html += '</div>'
        st.markdown(dayun_html, unsafe_allow_html=True)

        # 流年
        from bazi.dayun import get_liunian_ganzhi
        from shared.ganzhi import get_nayin
        current_year = datetime.now().year
        liunian = get_liunian_ganzhi(current_year)
        st.markdown(f"**{current_year}年流年**: {liunian}（{get_nayin(liunian)}）")

    # ===== 命理解读 =====
    st.markdown("### 命理解读")
    if st.button("生成解读", key="bazi_ai_btn"):
        with st.spinner("正在生成解读..."):
            from bazi.prompts import build_bazi_prompt, BAZI_SYSTEM_PROMPT
            from shared.ai_client import call_tongyi
            prompt = build_bazi_prompt(chart)
            result = call_tongyi(prompt, system_prompt=BAZI_SYSTEM_PROMPT)
            st.session_state["bazi_ai_result"] = result

    if "bazi_ai_result" in st.session_state:
        st.markdown(st.session_state["bazi_ai_result"])


def _wuxing_color(wuxing: str) -> str:
    """五行对应颜色"""
    return {
        "木": "#66bb6a",  # 绿
        "火": "#ef5350",  # 红
        "土": "#ffa726",  # 黄橙
        "金": "#ffd54f",  # 金
        "水": "#42a5f5",  # 蓝
    }.get(wuxing, "#e8e0d0")
