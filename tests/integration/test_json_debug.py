#!/usr/bin/env python3
"""
测试JSON解析问题的专用脚本
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append('src')
from thesis_inno_eval.extract_sections_with_ai import extract_sections_with_ai
from thesis_inno_eval.ai_client import get_ai_client
import logging

# 配置日志显示调试信息
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# 测试论文结构化提取
input_file = 'data/input/跨模态图像融合技术在医疗影像分析中的研究.docx'
print(f'开始测试JSON解析: {input_file}')

# 首先检查文件是否存在
if not os.path.exists(input_file):
    print(f'❌ 文件不存在: {input_file}')
    exit(1)

try:
    # 简单读取文档（这里用一个模拟内容）
    content = "测试论文内容，用于触发JSON解析错误"
    
    # 提取结构化信息
    ai_client = get_ai_client()
    result = extract_sections_with_ai(content, ai_client)
    if result:
        print(' 提取成功')
        print(f'字段: {list(result.keys())}')
    else:
        print('❌ 提取失败')
        
except Exception as e:
    print(f'❌ 异常: {e}')
    import traceback
    traceback.print_exc()
