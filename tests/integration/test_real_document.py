#!/usr/bin/env python3
"""
测试真实文档的参考文献提取
使用实际的MD文件测试修复效果
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.smart_reference_extractor import SmartReferenceExtractor

def test_real_document():
    """测试真实文档的参考文献提取"""
    
    print("🧪 测试真实文档的参考文献提取修复...")
    print("="*60)
    
    # 读取真实的MD文件
    md_file = r"c:\MyProjects\thesis_Inno_Eval\cache\documents\51177_b6ac1c475108811bd4a31a6ebcd397df.md"
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
        print(f" 成功读取文档: {len(text):,} 字符")
    except Exception as e:
        print(f"❌ 读取文档失败: {e}")
        return
    
    # 初始化提取器
    extractor = SmartReferenceExtractor()
    
    # 提取参考文献
    references, stats = extractor.extract_references(text, source_format='docx')
    
    print(f"\n📊 提取结果:")
    print(f"提取到 {len(references)} 条参考文献")
    if 'processing_time' in stats:
        print(f"处理时间: {stats['processing_time']:.2f}秒")
    if 'method_used' in stats:
        print(f"使用方法: {stats['method_used']}")
    
    # 查找关键参考文献
    ref_179 = None
    ref_5895 = None
    
    for ref in references:
        if '[179]' in ref:
            ref_179 = ref
        if '[5895]' in ref:
            ref_5895 = ref
    
    print(f"\n🔍 关键检查:")
    
    # 检查最后一条正确的参考文献[179]
    if ref_179:
        print(" 找到参考文献[179]:")
        print(f"   {ref_179}")
    else:
        print("❌ 未找到参考文献[179]")
    
    # 检查错误的[5895]
    if ref_5895:
        print("❌ 仍然存在错误的[5895]:")
        print(f"   {ref_5895}")
    else:
        print(" 已成功过滤掉错误的[5895]")
    
    # 显示最后几条参考文献
    print(f"\n📖 最后5条参考文献:")
    for i, ref in enumerate(references[-5:], len(references)-4):
        print(f"{i:3d}. {ref}")
    
    # 统计编号范围
    numbers = []
    for ref in references:
        match = extractor._extract_number(ref)
        if match != 999999:
            numbers.append(match)
    
    if numbers:
        numbers.sort()
        print(f"\n📊 编号统计:")
        print(f"编号范围: {min(numbers)} - {max(numbers)}")
        print(f"编号数量: {len(numbers)}")
        
        # 查找异常大的编号（可能是误识别的期刊号）
        large_numbers = [n for n in numbers if n > 500]
        if large_numbers:
            print(f"⚠️ 发现异常大的编号: {large_numbers}")
        else:
            print(" 所有编号都在合理范围内")

if __name__ == "__main__":
    test_real_document()
