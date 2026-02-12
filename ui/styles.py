"""Streamlit 自定义 CSS 样式"""

import streamlit as st


def inject_styles():
    st.markdown("""
    <style>
    /* 整体深色主题增强 */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%);
    }

    /* 全局文字颜色提亮 */
    .stApp, .stApp > div, .stApp .stMarkdown p,
    .stApp .stMarkdown li, .stApp .stMarkdown span,
    .stApp .element-container p {
        color: #f0ece4 !important;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        color: #f5f0e8 !important;
    }
    /* 所有输入控件文字统一用浅色（深色背景下可见） */
    .stApp input, .stApp textarea, .stApp select,
    .stApp [data-baseweb="input"] input,
    .stApp [data-baseweb="textarea"] textarea,
    .stApp [data-baseweb="select"] div,
    .stApp [data-baseweb="select"] span,
    .stApp .stSelectbox *,
    .stApp .stNumberInput input,
    .stApp .stDateInput input,
    .stApp .stTextInput input,
    .stApp [data-testid="stDateInput"] input {
        color: #f0ece4 !important;
    }
    /* placeholder 文字用中灰色 */
    .stApp input::placeholder, .stApp textarea::placeholder {
        color: #999 !important;
    }
    /* 按钮文字加深加粗 */
    .stApp button[kind="primary"],
    .stApp .stButton > button[kind="primary"] {
        color: #1a1a2e !important;
        font-weight: bold !important;
    }
    /* 下拉菜单弹出层（白底用深色字） */
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] [role="option"],
    [data-baseweb="menu"] li,
    ul[role="listbox"] li {
        color: #1a1a2e !important;
    }
    /* 日期选择器弹出 */
    [data-baseweb="calendar"] * {
        color: #f0ece4 !important;
    }
    .stDateInput [data-baseweb="popover"] > div {
        background: #1a1a3e !important;
    }
    [data-baseweb="calendar"] ul li {
        color: #f0ece4 !important;
        background: #1a1a3e !important;
    }
    [data-baseweb="calendar"] ul li:hover {
        background: #2a2a5c !important;
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        padding: 12px 24px;
    }

    /* 九宫格单元格 */
    .palace-cell {
        border: 1px solid #3a3a5c;
        border-radius: 8px;
        padding: 10px;
        margin: 4px;
        background: rgba(20, 20, 50, 0.6);
        min-height: 140px;
    }
    .palace-cell.highlight {
        border: 2px solid #f0d890;
        box-shadow: 0 0 10px rgba(240, 216, 144, 0.3);
    }
    .palace-header {
        font-size: 0.8em;
        color: #c8c0d8 !important;
        margin-bottom: 4px;
    }
    .palace-god {
        font-weight: bold;
    }
    .palace-star {
        font-weight: bold;
    }
    .palace-door {
        font-weight: bold;
    }
    .palace-tianpan {
        color: #f0d890 !important;
    }
    .palace-dipan {
        color: #d8d0e0 !important;
    }

    /* 四柱表格 */
    .pillar-table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
    }
    .pillar-table th {
        background: rgba(40, 40, 80, 0.8);
        color: #f0d890 !important;
        padding: 10px 16px;
        text-align: center;
        font-size: 1.05em;
    }
    .pillar-table td {
        padding: 8px 16px;
        text-align: center;
        border-bottom: 1px solid #2a2a4c;
        color: #f0ece4 !important;
    }
    .pillar-table tr:hover td {
        background: rgba(60, 60, 100, 0.3);
    }

    /* 大运条 */
    .dayun-item {
        display: inline-block;
        padding: 6px 14px;
        margin: 3px;
        border-radius: 6px;
        background: rgba(30, 30, 60, 0.7);
        border: 1px solid #3a3a5c;
        color: #e0d8e8 !important;
        font-size: 0.9em;
    }
    .dayun-item.current {
        background: rgba(240, 216, 144, 0.15);
        border-color: #f0d890;
        color: #f0d890 !important;
        font-weight: bold;
    }

    /* 信息标签 */
    .info-tag {
        display: inline-block;
        padding: 4px 12px;
        margin: 2px 4px;
        border-radius: 4px;
        background: rgba(40, 40, 80, 0.6);
        color: #c8ddf0 !important;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)
