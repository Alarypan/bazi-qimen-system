"""综合解读页面 - 整合八字与奇门遁甲的综述寄语"""

import streamlit as st


COMBINED_SYSTEM_PROMPT = (
    "你是一位融贯传统命理与奇门遁甲的资深术数研究者，"
    "擅长用温暖、严谨、富有人文关怀的语言，为人提供整体性的人生参考。"
    "你的文字有温度但不煽情，有力量但不虚妄，始终基于术数分析的事实说话。"
)


def _build_combined_prompt(bazi_text: str, qimen_text: str) -> str:
    """构建综合解读 Prompt"""
    return f"""下面分别是同一个人的八字命理分析和奇门遁甲盘局分析。请完成以下任务：

【任务一：八字综述】（150-200字）
从以下八字分析中，提取各点核心结论，融汇成一段连贯的、富有情感的文字。
不要逐条罗列，而是用叙事性的语言，把性格、事业、感情、运势编织成一幅完整的人生画面。
语气温暖而克制，给人以希望但不夸大，严谨但不冰冷。

--- 八字分析原文 ---
{bazi_text}
--- 八字分析结束 ---

【任务二：奇门综述】（150-200字）
从以下奇门遁甲分析中，提取各点核心结论，融汇成一段连贯的、富有情感的文字。
不要逐条罗列，而是用叙事性的语言，把当下格局、事业财运、方位建议、人际感情等编织成一幅完整的当下态势画面。
语气同上：温暖、严谨、给人以力量。

--- 奇门分析原文 ---
{qimen_text}
--- 奇门分析结束 ---

【任务三：综合寄语】（200-350字）
将上述八字综述和奇门综述进一步融合，写成一段完整的、一气呵成的文字。
这段话应该是一个人可以反复阅读、从中汲取力量的段落——
它既描绘了命主的天赋底色和人生基调（八字层面），也捕捉了当下时空的机遇与挑战（奇门层面），
最终汇成一段既关照过去、也照亮当下的温暖文字。

要求：
- 不要出现"八字显示""奇门盘面"等术数术语，用自然的人话说
- 不要分点、不要用标题，就写一段流畅的文字
- 严谨——每一句话都能在前面的分析中找到依据，不凭空编造
- 温暖——让人读完感到被理解、被鼓励，但不廉价地安慰
- 克制——不要过度修饰，朴素的力量比华丽的辞藻更打动人

请按以下格式输出：

### 八字综述
（八字综述文字）

### 奇门综述
（奇门综述文字）

### 综合寄语
（综合寄语文字）
"""


def render_combined_page():
    st.subheader("综合解读")
    st.caption("基于八字命理与奇门遁甲的分析结论，融合生成一段完整的、富有温度的文字表达")

    bazi_result = st.session_state.get("bazi_ai_result")
    qimen_result = st.session_state.get("qm_ai_result")

    has_bazi = bool(bazi_result)
    has_qimen = bool(qimen_result)

    # 状态提示
    col1, col2 = st.columns(2)
    with col1:
        if has_bazi:
            st.success("八字解读 - 已就绪", icon=None)
        else:
            st.warning("八字解读 - 未生成（请先在「八字排盘」中生成解读）")
    with col2:
        if has_qimen:
            st.success("奇门解读 - 已就绪", icon=None)
        else:
            st.warning("奇门解读 - 未生成（请先在「奇门遁甲阴盘」中生成解读）")

    if not (has_bazi and has_qimen):
        st.info("请先分别完成八字和奇门的排盘及解读，然后回到本页生成综合解读。")
        return

    if st.button("生成综合解读", type="primary", key="combined_btn"):
        with st.spinner("正在融合两套体系的分析，生成综合文字..."):
            try:
                from shared.ai_client import call_tongyi
                prompt = _build_combined_prompt(bazi_result, qimen_result)
                result = call_tongyi(prompt, system_prompt=COMBINED_SYSTEM_PROMPT, temperature=0.7)
                st.session_state["combined_result"] = result
            except Exception as e:
                st.error(f"综合解读生成出错：{e}")

    if "combined_result" in st.session_state:
        st.divider()
        st.markdown(st.session_state["combined_result"])
