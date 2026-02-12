"""八字 & 奇门遁甲阴盘排盘系统 - Streamlit 主入口"""

import streamlit as st

st.set_page_config(
    page_title="八字奇门排盘系统",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 注入自定义样式
from ui.styles import inject_styles
inject_styles()

st.markdown("<h1 style='text-align:center;'>八字 · 奇门遁甲阴盘 排盘系统</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.6;'>基于寿星天文历 · 张志春奇门体系 · 通义千问AI解读</p>", unsafe_allow_html=True)
st.divider()

tab1, tab2, tab3 = st.tabs(["📅 八字排盘", "⚡ 奇门遁甲阴盘", "✨ 综合解读"])

with tab1:
    from ui.bazi_page import render_bazi_page
    render_bazi_page()

with tab2:
    from ui.qimen_page import render_qimen_page
    render_qimen_page()

with tab3:
    from ui.combined_page import render_combined_page
    render_combined_page()
