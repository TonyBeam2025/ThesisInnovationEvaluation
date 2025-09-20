#!/usr/bin/env python3
"""
测试修复后的参考文献提取功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append('src')

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
from pathlib import Path

def test_references_extraction():
    """测试修复后的参考文献提取"""
    
    # 读取缓存的文档
    cache_file = Path("cache/documents/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩_f28c5133e8a3bd43f6c85222b885a8ce.md")
    
    if not cache_file.exists():
        print(f"❌ 缓存文件不存在: {cache_file}")
        return
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"📄 测试参考文献提取功能")
    print(f"文档长度: {len(text):,} 字符")
    
    # 创建提取器实例
    extractor = ThesisExtractorPro()
    
    # 调用参考文献提取方法
    references = extractor._extract_references_enhanced(text)
    
    print(f"\n📊 提取结果:")
    print(f"   参考文献总数: {len(references)} 条")
    
    if references:
        print(f"\n📋 前10条参考文献:")
        for i, ref in enumerate(references[:10]):
            print(f"   {i+1}. {ref[:100]}...")
            
        if len(references) > 10:
            print(f"   ... 还有 {len(references)-10} 条")
    else:
        print("   ❌ 没有提取到参考文献")

if __name__ == '__main__':
    test_references_extraction()
