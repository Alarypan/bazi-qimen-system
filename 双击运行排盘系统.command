#!/bin/bash
cd "$(dirname "$0")"
echo "正在启动排盘系统..."
python3 -m streamlit run main.py --server.port 8501
