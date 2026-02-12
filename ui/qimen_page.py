"""奇门遁甲阴盘排盘页面"""

import streamlit as st
import sxtwl
from datetime import datetime, date

LUNAR_MONTH_NAMES = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "腊月",
]


def _lunar_to_solar(l_year: int, l_month: int, l_day: int, is_leap: bool = False):
    """农历转公历"""
    try:
        d = sxtwl.fromLunar(l_year, l_month, l_day, is_leap)
        return d.getSolarYear(), d.getSolarMonth(), d.getSolarDay()
    except Exception:
        return None


def render_qimen_page():
    # ===== 输入区 =====
    st.subheader("请选择起局时间")

    cal_type = st.radio("日历类型", ["阳历（公历）", "阴历（农历）"], horizontal=True, key="qm_cal_type")

    if cal_type == "阳历（公历）":
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            qm_date = st.date_input(
                "日期（公历）",
                value=date.today(),
                min_value=date(1900, 1, 1),
                max_value=date(2100, 12, 31),
                key="qm_date",
            )
            solar_year, solar_month, solar_day = qm_date.year, qm_date.month, qm_date.day
        with col2:
            qm_hour = st.number_input("小时 (0-23)", 0, 23, datetime.now().hour, key="qm_hour")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            use_now = st.checkbox("使用当前时间", key="qm_now")
            if use_now:
                now = datetime.now()
                solar_year, solar_month, solar_day = now.year, now.month, now.day
                qm_hour = now.hour
    else:
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        with c1:
            l_year = st.number_input("农历年", 1900, 2100, datetime.now().year, key="qm_lyear")
        with c2:
            l_month_sel = st.selectbox("农历月", LUNAR_MONTH_NAMES, key="qm_lmonth")
            l_month = LUNAR_MONTH_NAMES.index(l_month_sel) + 1
        with c3:
            l_day = st.number_input("农历日", 1, 30, 1, key="qm_lday")
        with c4:
            qm_hour = st.number_input("小时 (0-23)", 0, 23, datetime.now().hour, key="qm_hour_l")

        is_leap = st.checkbox("闰月", key="qm_leap")
        result = _lunar_to_solar(l_year, l_month, l_day, is_leap)
        if result:
            solar_year, solar_month, solar_day = result
            st.caption(f"对应公历：{solar_year}-{solar_month:02d}-{solar_day:02d}")
        else:
            st.warning("该农历日期无效，请检查")
            solar_year, solar_month, solar_day = datetime.now().year, datetime.now().month, datetime.now().day

    # 占卜事项输入
    divination_topic = st.text_input(
        "占卜事项（选填）",
        placeholder="例如：近期是否适合跳槽、这笔投资能否获利、感情走向如何...",
        key="qm_topic",
    )

    if st.button("起盘", type="primary", key="qm_btn"):
        with st.spinner("正在起盘计算..."):
            try:
                from qimen.yinpan_engine import calculate_qimen
                chart = calculate_qimen(solar_year, solar_month, solar_day, qm_hour)
                st.session_state["qm_chart"] = chart
                st.session_state["qm_saved_topic"] = divination_topic
            except Exception as e:
                st.error(f"起盘计算出错：{e}")
                return

    # ===== 展示区 =====
    if "qm_chart" not in st.session_state:
        return

    chart = st.session_state["qm_chart"]
    st.divider()

    # 盘面基本信息
    from shared.ganzhi import SHICHEN_NAMES, hour_to_shichen_index
    shichen = SHICHEN_NAMES[hour_to_shichen_index(chart.solar_hour)]

    info_html = (
        f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">'
        f'<span class="info-tag">{chart.solar_year}-{chart.solar_month:02d}-{chart.solar_day:02d} {chart.solar_hour}:00</span>'
        f'<span class="info-tag">{shichen}</span>'
        f'<span class="info-tag">{chart.year_gz}年 {chart.month_gz}月 {chart.day_gz}日 {chart.hour_gz}时</span>'
        f'<span class="info-tag">{chart.jieqi_name}·{chart.yuan}元</span>'
        f'<span class="info-tag" style="color:#f0d890;font-weight:bold;">{chart.dun_type}遁{chart.ju_number}局</span>'
        f'<span class="info-tag">值符: {chart.zhifu_star}</span>'
        f'<span class="info-tag">值使: {chart.zhishi_door}</span>'
        f'</div>'
    )
    st.markdown(info_html, unsafe_allow_html=True)

    st.markdown("### 九宫格局")

    # 九宫格排列: 巽4 离9 坤2 / 震3 中5 兑7 / 艮8 坎1 乾6
    layout = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

    for row in layout:
        cols = st.columns(3)
        for col_idx, palace_num in enumerate(row):
            with cols[col_idx]:
                p = chart.palaces[palace_num]
                _render_palace(p)

    # ===== 奇门解读 =====
    st.markdown("### 奇门解读")

    # 获取保存的占卜事项
    saved_topic = st.session_state.get("qm_saved_topic", "")

    if st.button("生成解读", key="qm_ai_btn"):
        with st.spinner("正在生成解读..."):
            try:
                from qimen.prompts import build_qimen_prompt, QIMEN_SYSTEM_PROMPT
                from shared.ai_client import call_tongyi
                prompt = build_qimen_prompt(chart, divination_topic=saved_topic)
                result = call_tongyi(prompt, system_prompt=QIMEN_SYSTEM_PROMPT)
                st.session_state["qm_ai_result"] = result
            except Exception as e:
                st.error(f"解读生成出错：{e}")

    if "qm_ai_result" in st.session_state:
        st.markdown(st.session_state["qm_ai_result"])


def _render_palace(palace):
    """渲染单个宫位"""
    highlight = "highlight" if palace.is_zhifu else ""
    is_center = palace.number == 5

    god_color = _god_color(palace.god)
    star_color = _star_color(palace.star)
    door_color = _door_color(palace.door)

    if is_center:
        html = f'''
        <div class="palace-cell {highlight}">
            <div class="palace-header">{palace.number}宫 · {palace.name} · {palace.direction}</div>
            <div style="text-align:center;padding:20px 0;">
                <div class="palace-star" style="color:{star_color};">{palace.star}</div>
                <div style="margin-top:8px;">
                    <span class="palace-tianpan">天: {palace.tianpan}</span>
                    <span class="palace-dipan" style="margin-left:8px;">地: {palace.dipan}</span>
                </div>
            </div>
        </div>
        '''
    else:
        html = f'''
        <div class="palace-cell {highlight}">
            <div class="palace-header">{palace.number}宫 · {palace.name} · {palace.direction}</div>
            <div style="display:flex;justify-content:space-between;margin:4px 0;">
                <span class="palace-god" style="color:{god_color};">{palace.god}</span>
                <span class="palace-star" style="color:{star_color};">{palace.star}</span>
            </div>
            <div class="palace-door" style="color:{door_color};text-align:center;font-size:1.1em;margin:6px 0;">
                {palace.door}
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.95em;">
                <span class="palace-tianpan">天: {palace.tianpan}</span>
                <span class="palace-dipan">地: {palace.dipan}</span>
            </div>
        </div>
        '''
    st.markdown(html, unsafe_allow_html=True)


def _god_color(god: str) -> str:
    return {
        "值符": "#f0d890",
        "腾蛇": "#ef5350",
        "太阴": "#ce93d8",
        "六合": "#66bb6a",
        "白虎": "#ffd54f",
        "玄武": "#42a5f5",
        "九地": "#a1887f",
        "九天": "#90caf9",
    }.get(god, "#e8a0a0")


def _star_color(star: str) -> str:
    from qimen.constants import STAR_JIXI
    jixi = STAR_JIXI.get(star, "")
    if jixi == "吉":
        return "#66bb6a"
    elif jixi == "凶":
        return "#ef5350"
    return "#a0c8e8"


def _door_color(door: str) -> str:
    from qimen.constants import DOOR_JIXI
    jixi = DOOR_JIXI.get(door, "")
    if jixi == "吉":
        return "#66bb6a"
    elif jixi == "凶":
        return "#ef5350"
    return "#a0e8a0"
