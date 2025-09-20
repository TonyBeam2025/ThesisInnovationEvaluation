#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试目录内容提取，查看原始内容
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import docx
from src.thesis_inno_eval.ai_toc_extractor import AITocExtractor

def debug_toc_content():
    """调试目录内容提取"""
    print("🔍 调试目录内容提取")
    print("=" * 80)
    
    doc_path = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    
    try:
        # 读取文档内容
        doc = docx.Document(doc_path)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        
        # 创建提取器实例
        extractor = AITocExtractor()
        
        # 测试智能提取方法（直接实现而不依赖方法）
        print("🧠 测试智能目录提取...")
        
        lines = content.split('\n')
        extracted_lines = []
        
        # 标准目录模式
        chapter_patterns = [
            r'^(第[一二三四五六七八九十\d]+章)\s*(.+?)(?:\s+(\d+))?$',  # 第X章 标题 页码
            r'^(\d+\.)\s*(.+?)(?:\s+(\d+))?$',                           # 1. 标题 页码
            r'^(\d+\.\d+)\s*(.+?)(?:\s+(\d+))?$',                       # 1.1 标题 页码
            r'^(\d+\.\d+\.\d+)\s*(.+?)(?:\s+(\d+))?$',                  # 1.1.1 标题 页码
            r'^([A-Z]+)\s*(.+?)(?:\s+(\d+))?$',                         # ABSTRACT 标题 页码
            r'^(摘\s*要|目\s*录|参考文献|致\s*谢|攻读|附\s*录)\s*(.*)(?:\s+(\d+))?$'  # 特殊章节
        ]
        
        import re
        for line in lines:
            line = line.strip()
            if not line or len(line) < 2:
                continue
                
            # 检查是否匹配目录模式
            for pattern in chapter_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # 简单的目录行判断 - 检查是否包含页码或章节标识
                    if ('第' in line and '章' in line) or re.search(r'\d+$', line) or any(keyword in line for keyword in ['摘要', '参考文献', '致谢', '攻读', '附录']):
                        extracted_lines.append(line)
                        break
        
        if extracted_lines:
            print(f" 找到 {len(extracted_lines)} 行可能的目录内容:")
            print("-" * 60)
            for i, line in enumerate(extracted_lines, 1):
                print(f"{i:3d}: {line}")
        else:
            print("❌ 未找到目录内容")
        
        # 手动搜索您提到的目录项
        print(f"\n🔍 手动搜索特定目录项:")
        print("-" * 60)
        
        target_patterns = [
            r'第一章.*绪论',
            r'1\.1.*选题背景',
            r'参考文献',
            r'攻读.*硕士.*学位.*期间.*成果',
            r'致.*谢'
        ]
        
        lines = content.split('\n')
        found_items = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            for j, pattern in enumerate(target_patterns):
                import re
                if re.search(pattern, line, re.IGNORECASE):
                    found_items.append((i+1, line, pattern))
                    print(f"第{i+1:3d}行: {line} [匹配: {pattern}]")
        
        if found_items:
            print(f"\n 找到 {len(found_items)} 个目标目录项")
        else:
            print("\n❌ 未找到目标目录项")
            
        # 显示包含"第一章"的所有行
        print(f"\n🔍 搜索包含'第一章'的所有行:")
        print("-" * 60)
        for i, line in enumerate(lines):
            if '第一章' in line:
                print(f"第{i+1:3d}行: {line.strip()}")
        
        # 显示包含"1.1"的所有行
        print(f"\n🔍 搜索包含'1.1'的所有行:")
        print("-" * 60)
        for i, line in enumerate(lines):
            if '1.1' in line and len(line.strip()) < 100:  # 避免正文内容
                print(f"第{i+1:3d}行: {line.strip()}")
                
    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_toc_content()

