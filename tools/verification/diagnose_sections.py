#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断参考文献和致谢章节的提取问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy

def diagnose_sections_extraction():
    """诊断章节提取问题"""
    print("🔍 诊断参考文献和致谢章节提取问题...")
    
    # 测试文件路径
    test_file = r".\data\input\跨模态图像融合技术在医疗影像分析中的研究.docx"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    try:
        # 使用专业版策略提取
        result = extract_sections_with_pro_strategy(test_file)
        
        if not result:
            print("❌ 提取失败，结果为空")
            return False
        
        print("\n📊 所有字段检查:")
        
        # 检查所有相关字段
        references = result.get('references', [])
        acknowledgement = result.get('acknowledgement', '')
        
        print(f"   📚 references: {len(references)} 条")
        print(f"   🙏 acknowledgement: {len(acknowledgement)} 字符")
        
        # 检查章节摘要中是否有相关信息
        chapter_summaries = result.get('chapter_summaries', {})
        print(f"\n📖 章节摘要中的章节:")
        for chapter_name in chapter_summaries.keys():
            print(f"   - {chapter_name}")
        
        # 检查目录信息
        table_of_contents = result.get('table_of_contents', [])
        print(f"\n📋 目录信息:")
        for toc_item in table_of_contents:
            print(f"   {toc_item.get('number', '')}: {toc_item.get('title', '')}")
        
        # 诊断问题
        print(f"\n🔍 问题诊断:")
        
        if len(references) == 0:
            print("   ❌ 参考文献未提取到")
        else:
            print(f"    参考文献已提取: {len(references)} 条")
            
        if len(acknowledgement) == 0:
            print("   ❌ 致谢未提取到")
        else:
            print(f"    致谢已提取: {len(acknowledgement)} 字符")
        
        # 检查是否在章节摘要中存在
        has_ref_in_chapters = any('参考文献' in name or 'reference' in name.lower() for name in chapter_summaries.keys())
        has_ack_in_chapters = any('致谢' in name or 'acknowledgement' in name.lower() for name in chapter_summaries.keys())
        
        print(f"   {'' if has_ref_in_chapters else '❌'} 章节摘要中是否有参考文献: {has_ref_in_chapters}")
        print(f"   {'' if has_ack_in_chapters else '❌'} 章节摘要中是否有致谢: {has_ack_in_chapters}")
        
        # 检查目录中是否存在
        has_ref_in_toc = any('参考文献' in item.get('title', '') or 'reference' in item.get('title', '').lower() for item in table_of_contents)
        has_ack_in_toc = any('致谢' in item.get('title', '') or 'acknowledgement' in item.get('title', '').lower() for item in table_of_contents)
        
        print(f"   {'' if has_ref_in_toc else '❌'} 目录中是否有参考文献: {has_ref_in_toc}")
        print(f"   {'' if has_ack_in_toc else '❌'} 目录中是否有致谢: {has_ack_in_toc}")
        
        return True
        
    except Exception as e:
        print(f"❌ 诊断过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    diagnose_sections_extraction()

