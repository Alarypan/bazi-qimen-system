"""通义千问 API 封装"""

import os
import json
import requests
from pathlib import Path

# 优先从 Streamlit secrets 读取（云端部署），其次从 .env 文件读取（本地开发）
try:
    import streamlit as st
    API_KEY = st.secrets.get("TONGYI_API_KEY", "")
    MODEL = st.secrets.get("TONGYI_MODEL", "qwen-plus")
except Exception:
    API_KEY = ""
    MODEL = "qwen-plus"

if not API_KEY:
    from dotenv import load_dotenv
    _env_paths = [
        Path(__file__).resolve().parent.parent / ".env",
        Path.home() / "Desktop" / "bazi-qimen-system" / ".env",
        Path.home() / "Desktop" / "tarot-divination" / ".env",
    ]
    for p in _env_paths:
        if p.exists():
            load_dotenv(p)
            break
    API_KEY = os.environ.get("TONGYI_API_KEY", "")
    MODEL = os.environ.get("TONGYI_MODEL", "qwen-plus")
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"


def call_tongyi(prompt: str, system_prompt: str = "", temperature: float = 0.8) -> str:
    """调用通义千问 API
    返回: AI 生成的文本，失败时返回错误提示
    """
    if not API_KEY:
        return "[API Key 未配置，无法生成AI解读。请在 .env 文件中设置 TONGYI_API_KEY]"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
    }

    for attempt in range(2):
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            resp.encoding = "utf-8"
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                content = str(content)
            return content
        except requests.exceptions.Timeout:
            if attempt == 0:
                continue
            return "[AI解读生成失败（超时），请稍后重试]"
        except Exception as e:
            if attempt == 0:
                continue
            return f"[AI解读生成失败: {e}]"
    return "[AI解读生成失败，请稍后重试]"
