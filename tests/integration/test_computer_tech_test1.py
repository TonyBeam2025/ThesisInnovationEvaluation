#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试计算机应用技术_test1.docx文件的目录识别
"""

import sys
import os
sys.path.append(str(PROJECT_ROOT))

from src.thesis_inno_eval.ai_toc_extractor import AITocExtractor
import docx

def analyze_document_structure():
    """分析文档结构，寻找目录"""
    doc_path = r"c:\MyProjects\thesis_Inno_Eval\data\input\计算机应用技术_test1.docx"
    
    print("📄 分析计算机应用技术_test1.docx文档结构")
    print("=" * 80)
    
    try:
        doc = docx.Document(doc_path)
        lines = [p.text for p in doc.paragraphs]
        
        print(f"📊 文档总行数: {len(lines)}")
        
        # 显示前100行，寻找目录模式
        print(f"\n📋 前100行内容分析:")
        print("-" * 60)
        
        for i, line in enumerate(lines[:100]):
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # 检查是否包含目录相关关键词
            if any(keyword in line_clean for keyword in [
                '目录', '摘要', 'ABSTRACT', 'Abstract', 
                '第一章', '第二章', '第三章', '第四章', '第五章', '第六章', '第七章',
                '1.1', '1.2', '2.1', '2.2', '3.1', '3.2',
                '参考文献', '致谢', '攻读', '学位'
            ]):
                print(f"第{i+1:3d}行: {line_clean}")
        
        # 特别寻找目录格式的行（标题+页码）
        print(f"\n🔍 寻找目录格式的行（标题+页码）:")
        print("-" * 60)
        
        toc_lines = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # 检查是否是目录条目格式
            # 格式1: 标题\t页码
            if '\t' in line_clean:
                parts = line_clean.split('\t')
                if len(parts) >= 2:
                    title_part = parts[0].strip()
                    page_part = parts[-1].strip()
                    
                    # 检查页码部分是否包含数字或罗马数字
                    if (page_part.isdigit() or 
                        any(roman in page_part.upper() for roman in ['I', 'II', 'III', 'IV', 'V', 'VI']) or
                        any(str(j) in page_part for j in range(1, 100))):
                        print(f"第{i+1:3d}行: {line_clean}")
                        toc_lines.append((i+1, line_clean))
            
            # 格式2: 标题...页码 或 标题 页码
            import re
            if re.search(r'第[一二三四五六七八九十\d]+章|^\d+\.\d+|\b(摘要|ABSTRACT|目录|参考文献|致谢|攻读)\b', line_clean):
                # 检查行末是否有页码
                if re.search(r'\b\d+\s*$|[IVX]+\s*$', line_clean):
                    print(f"第{i+1:3d}行: {line_clean}")
                    toc_lines.append((i+1, line_clean))
        
        print(f"\n📈 找到 {len(toc_lines)} 个可能的目录条目")
        return toc_lines
        
    except Exception as e:
        print(f"❌ 分析文档失败: {str(e)}")
        return []

def test_toc_extraction():
    """测试目录提取"""
    doc_path = r"c:\MyProjects\thesis_Inno_Eval\data\input\计算机应用技术_test1.docx"
    
    print(f"\n\n🧠 测试AI TOC提取器")
    print("=" * 80)
    
    try:
        extractor = AITocExtractor()
        result = extractor.extract_toc(doc_path)
        
        if result and result.entries:
            print(f" 成功提取目录")
            print(f"📊 提取条目数: {len(result.entries)}")
            print(f"🎯 置信度: {result.confidence_score:.2f}")
            
            print(f"\n📋 提取的目录条目:")
            print("-" * 60)
            
            for i, entry in enumerate(result.entries, 1):
                type_label = f"【{entry.section_type}】" if entry.section_type else "【unknown】"
                page_info = f"页码: {entry.page}" if entry.page else "页码: None"
                
                print(f"{i:2d}. {type_label} {entry.title}")
                print(f"     {page_info} | 级别: {entry.level}")
                
        else:
            print("❌ 提取失败或结果为空")
            
    except Exception as e:
        print(f"❌ 提取过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 先分析文档结构
    toc_lines = analyze_document_structure()
    
    # 然后测试目录提取
    test_toc_extraction()
