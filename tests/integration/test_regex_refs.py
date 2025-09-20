#!/usr/bin/env python3
"""
直接正则表达式提取参考文献测试
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
import re
from pathlib import Path

def test_regex_extraction():
    """使用正则表达式直接提取参考文献"""
    # 读取缓存的文档
    cache_file = Path("cache/documents/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩_f28c5133e8a3bd43f6c85222b885a8ce.md")
    
    if not cache_file.exists():
        print(f"❌ 缓存文件不存在: {cache_file}")
        return
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"📄 文档长度: {len(text):,} 字符")
    
    # 定位参考文献部分
    print("🔍 定位参考文献部分...")
    
    # 查找"## 参考文献"
    ref_start = text.find("## 参考文献")
    if ref_start == -1:
        ref_start = text.find("参考文献")
    
    if ref_start == -1:
        print("❌ 未找到参考文献标题")
        return
    
    # 提取参考文献部分（从标题到文档结尾）
    ref_text = text[ref_start:]
    print(f"📍 参考文献部分长度: {len(ref_text):,} 字符")
    
    # 使用正则表达式查找所有参考文献
    print("\n🔍 使用正则表达式提取参考文献...")
    
    # 查找所有以［数字］开始的行（全角括号）
    pattern = r'［(\d+)］[^\n]*(?:\n(?!［\d+］)[^\n]*)*'
    matches = re.findall(pattern, ref_text, re.MULTILINE)
    
    print(f"📊 找到 {len(matches)} 个参考文献编号")
    
    # 更详细的提取
    pattern2 = r'(［\d+］[^\n]*(?:\n(?!［\d+］)[^\n]*)*?)(?=［\d+］|$)'
    full_matches = re.findall(pattern2, ref_text, re.MULTILINE | re.DOTALL)
    
    print(f"📊 完整提取到 {len(full_matches)} 条参考文献")
    
    if full_matches:
        print(f"\n📋 前5条参考文献:")
        for i, ref in enumerate(full_matches[:5]):
            # 清理多余的空白
            cleaned_ref = re.sub(r'\s+', ' ', ref.strip())
            print(f"   {i+1}. {cleaned_ref[:150]}...")
        
        if len(full_matches) > 5:
            print(f"   ... 还有 {len(full_matches)-5} 条")
            
        # 显示最后几条
        print(f"\n📋 最后3条参考文献:")
        for i, ref in enumerate(full_matches[-3:]):
            cleaned_ref = re.sub(r'\s+', ' ', ref.strip())
            ref_num = len(full_matches) - 3 + i + 1
            print(f"   {ref_num}. {cleaned_ref[:150]}...")
    
    # 检查特定的参考文献编号
    specific_refs = ['［87］', '［88］']
    for ref_num in specific_refs:
        if ref_num in ref_text:
            print(f" 找到参考文献 {ref_num}")
            # 查找该引用的上下文
            start = ref_text.find(ref_num)
            context = ref_text[start:start+200]
            print(f"   上下文: {context}")
        else:
            print(f"❌ 未找到参考文献 {ref_num}")

if __name__ == '__main__':
    test_regex_extraction()
