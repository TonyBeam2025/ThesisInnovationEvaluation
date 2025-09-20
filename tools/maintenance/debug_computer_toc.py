#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试计算机应用技术论文的目录提取调试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.thesis_inno_eval.ai_toc_extractor import AITocExtractor
import docx

def debug_computer_thesis_toc():
    """调试计算机应用技术论文目录提取"""
    print("🔧 调试计算机应用技术论文目录提取")
    print("=" * 80)
    
    doc_path = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    
    # 1. 先检查原始文档内容，找到真正的目录
    print("\n📄 步骤1：检查原始文档内容，寻找目录")
    print("-" * 60)
    
    doc = docx.Document(doc_path)
    lines = [p.text for p in doc.paragraphs]
    
    # 寻找包含"第一章"、"1.1"等目录特征的区域
    potential_toc_lines = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 检查是否包含目录特征
        if any(pattern in line for pattern in [
            "第一章", "第二章", "第三章", "第四章", "第五章", "第六章", "第七章",
            "1.1", "1.2", "2.1", "2.2", "3.1", "4.1", "5.1", "6.1", "7.1",
            "摘要", "Abstract", "目录", "参考文献", "致谢", "攻读"
        ]):
            # 检查是否包含页码（数字结尾）
            if line.endswith(('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X')) or \
               any(line.endswith(str(j)) for j in range(1, 100)):
                potential_toc_lines.append((i, line))
    
    if potential_toc_lines:
        print(f"🔍 找到 {len(potential_toc_lines)} 行潜在目录内容：")
        for i, (line_num, content) in enumerate(potential_toc_lines[:20]):  # 显示前20行
            print(f"  第{line_num+1:3d}行: {content}")
            if i >= 19:
                print(f"  ... 还有 {len(potential_toc_lines)-20} 行")
                break
    else:
        print("❌ 没有找到明显的目录特征")
    
    # 2. 测试AI TOC提取器
    print(f"\n📄 步骤2：测试AI TOC提取器")
    print("-" * 60)
    
    try:
        extractor = AITocExtractor()
        result = extractor.extract_toc(doc_path)
        
        print(f" 提取成功")
        print(f"📊 提取条目数: {len(result.entries)}")
        print(f"🎯 置信度: {result.confidence_score:.2f}")
        print(f"🔧 提取方法: {result.extraction_method}")
        
        # 显示提取的条目
        print(f"\n📋 提取的目录条目：")
        for i, entry in enumerate(result.entries, 1):
            print(f"  {i:2d}. 【{entry.section_type}】{entry.title}")
            if entry.page:
                print(f"      页码: {entry.page} | 级别: {entry.level}")
            else:
                print(f"      页码: None | 级别: {entry.level}")
                
        # 检查是否包含期望的章节
        expected_chapters = [
            "第一章", "第二章", "第三章", "第四章", "第五章", "第六章", "第七章",
            "绪论", "相关理论", "MLP", "SepCNN", "对比实验", "系统设计", "总结"
        ]
        
        print(f"\n🎯 期望章节检查：")
        found_chapters = []
        for entry in result.entries:
            for expected in expected_chapters:
                if expected in entry.title:
                    found_chapters.append(expected)
                    print(f"   找到: {expected} -> {entry.title}")
                    break
        
        missing_chapters = [ch for ch in expected_chapters if ch not in found_chapters]
        if missing_chapters:
            print(f"\n❌ 缺失的期望章节: {', '.join(missing_chapters)}")
        else:
            print(f"\n🎉 所有期望章节都已找到！")
            
    except Exception as e:
        print(f"❌ 提取失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 3. 手动分析目录边界
    print(f"\n📄 步骤3：手动分析目录边界")
    print("-" * 60)
    
    # 寻找"目录"标题
    toc_title_found = False
    for i, line in enumerate(lines):
        if line.strip() == "目录":
            print(f"📍 找到目录标题：第{i+1}行")
            toc_title_found = True
            
            # 显示目录标题后的内容
            print(f"📄 目录标题后的内容：")
            for j in range(i+1, min(i+21, len(lines))):
                content = lines[j].strip()
                if content:
                    print(f"  第{j+1:3d}行: {content}")
            break
    
    if not toc_title_found:
        print("❌ 没有找到独立的'目录'标题行")
        
        # 寻找"第一章绪论"作为正文开始
        for i, line in enumerate(lines):
            if "第一章" in line and "绪论" in line:
                print(f"📍 找到正文开始：第{i+1}行 - {line.strip()}")
                
                # 向前查找可能的目录区域
                print(f"📄 正文开始前的内容：")
                start_search = max(0, i-30)
                for j in range(start_search, i):
                    content = lines[j].strip()
                    if content and any(pattern in content for pattern in ["第", "章", "1.", "2.", "摘要", "Abstract"]):
                        print(f"  第{j+1:3d}行: {content}")
                break
    
    print(f"\n" + "=" * 80)
    print("🏁 调试完成")

if __name__ == "__main__":
    debug_computer_thesis_toc()

