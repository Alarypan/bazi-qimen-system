"""八字 AI 解读 Prompt 模板"""


def build_bazi_prompt(chart) -> str:
    """构建八字解读的 Prompt"""
    fp = chart.four_pillars
    lunar = chart.lunar_info

    # 四柱信息
    pillars_text = f"""
年柱: {fp.year.ganzhi}（{fp.year.ten_god}）纳音:{fp.year.nayin} 藏干:{','.join(fp.year.canggan)}
月柱: {fp.month.ganzhi}（{fp.month.ten_god}）纳音:{fp.month.nayin} 藏干:{','.join(fp.month.canggan)}
日柱: {fp.day.ganzhi}（日主 {fp.day_master}）纳音:{fp.day.nayin} 藏干:{','.join(fp.day.canggan)}
时柱: {fp.hour.ganzhi}（{fp.hour.ten_god}）纳音:{fp.hour.nayin} 藏干:{','.join(fp.hour.canggan)}
""".strip()

    # 大运
    dayun_text = ""
    if chart.dayun_list:
        dayun_text = f"起运年龄: {chart.start_dayun_age}岁，{chart.dayun_direction}排\n"
        for d in chart.dayun_list:
            dayun_text += f"  {d.start_age}-{d.end_age}岁: {d.ganzhi}（{d.nayin}）\n"

    # 流年
    from bazi.dayun import get_liunian_ganzhi
    from datetime import date
    current_year = date.today().year
    liunian = get_liunian_ganzhi(current_year)

    prompt = f"""你是一位学养深厚的八字命理师，擅长用现代语言解读传统命理，语风沉稳温和。

【出生信息】
公历：{chart.solar_year}年{chart.solar_month}月{chart.solar_day}日 {lunar['shichen']}
农历：{lunar['year']}年{lunar['month_name']}{lunar['day_name']}
性别：{chart.gender}

【四柱八字】
{pillars_text}

日主: {fp.day_master}（{fp.day.tg_wuxing}{fp.day.tg_yinyang}）

【大运】
{dayun_text}

【当前流年】
{current_year}年 {liunian}

【解读要求】
这是一份用于学习的命理分析。请在每个分析点中，先展示你的"推理过程"（即你是怎样一步步得出结论的），再给出结论。
请使用以下格式：
  → 思路：列出你观察到的关键信息、采用的分析方法、推理的每一步
  → 结论：基于上述推理得出的判断

请从以下几个方面进行分析（约800-1200字）：

1.【日主强弱判断】
  → 思路：①先看日干是什么五行、什么阴阳；②看月令（月支）对日主是生扶还是克泄，得令否；③看年支、日支、时支中有无生扶日主的力量（得地否）；④数四柱天干中生扶与克泄日主的个数（得势否）；⑤综合三个维度判断身强还是身弱。
  → 结论：身强/身弱，喜用神是什么，忌神是什么。

2.【性格特质】
  → 思路：①日干本身五行的性格基调（如甲木主仁直、丙火主热情等）；②四柱十神的组合如何影响性格（如食伤多主聪明善表达、印多主内敛好学等）；③日支藏干与日主的关系透露出的内在性格。
  → 结论：性格特点总结。

3.【事业财运】
  → 思路：①看正财偏财的位置与力量，判断财运类型；②看正官七杀的力量，判断适合体制内还是创业；③看食神伤官与财星的配合，判断生财方式；④结合喜用神推断有利行业的五行方向。
  → 结论：适合的方向和财运特点。

4.【感情婚姻】
  → 思路：①看日支（配偶宫）的五行和十神，判断配偶特征；②男看正财/偏财、女看正官/七杀作为配偶星，看其力量和位置；③看配偶星与日主的关系，是近是远、是强是弱；④有无合冲刑破影响婚姻宫的因素。
  → 结论：感情倾向和婚姻提示。

5.【当前运势】
  → 思路：①当前大运天干地支与命局的作用关系（生克合冲）；②{current_year}年流年{liunian}与命局、大运的三方交互；③流年对喜用神是助力还是压制。
  → 结论：近期运势提示和实用建议。

格式要求：每个分析点务必先写"→ 思路"再写"→ 结论"，让学习者能看懂推理链路。语言专业但易懂，不堆砌术语。避免宿命论，强调命理是参考框架。

最后，请在所有分析点之后，写一段【综述寄语】（150-250字）：
将上述各点结论融汇为一段连贯、温暖而严谨的文字。不要逐条重复，而是用自然流畅的叙事语言，把性格底色、事业方向、感情态度、当前运势等内容编织成一段完整的人生画面。语气要给人以希望和力量，但不夸大、不虚假，基于盘面事实说话。
"""
    return prompt


BAZI_SYSTEM_PROMPT = "你是一位专业的八字命理分析师，精通子平八字，擅长用温和、专业的语言为人解读命理。你的分析基于传统命理学理论，同时注重现代语境下的实用性。"
