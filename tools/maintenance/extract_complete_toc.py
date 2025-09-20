#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的TOC提取器 - 基于XML书签方法
"""

from docx import Document
import xml.etree.ElementTree as ET
import re

def extract_complete_toc_from_bookmarks(doc_path):
    """通过书签完整提取目录结构"""
    print(f"📚 完整TOC提取: {doc_path}")
    print("=" * 80)
    
    doc = Document(doc_path)
    document_xml = doc._element.xml
    
    # 查找所有TOC书签和对应的文本
    # 改进的正则表达式，确保捕获书签之间的内容
    bookmark_start_pattern = r'<w:bookmarkStart[^>]*w:name="(_Toc\d+)"[^>]*/>'
    bookmark_starts = re.finditer(bookmark_start_pattern, document_xml)
    
    toc_entries = []
    bookmark_positions = []
    
    # 收集所有书签位置
    for match in bookmark_starts:
        bookmark_name = match.group(1)
        start_pos = match.end()
        bookmark_positions.append((bookmark_name, start_pos))
    
    print(f"找到 {len(bookmark_positions)} 个TOC书签位置")
    
    # 为每个书签提取后续文本内容
    for i, (bookmark_name, start_pos) in enumerate(bookmark_positions):
        # 确定提取文本的结束位置
        if i + 1 < len(bookmark_positions):
            end_pos = bookmark_positions[i + 1][1]
        else:
            end_pos = start_pos + 1000  # 最后一个书签，提取固定长度
        
        # 提取书签后的XML片段
        xml_fragment = document_xml[start_pos:end_pos]
        
        # 从XML中提取文本内容
        # 查找第一个文本运行
        text_pattern = r'<w:t[^>]*>(.*?)</w:t>'
        text_matches = re.findall(text_pattern, xml_fragment, re.DOTALL)
        
        if text_matches:
            # 取第一个非空文本
            text_content = ""
            for text in text_matches:
                clean_text = text.strip()
                if clean_text and not clean_text.isspace():
                    text_content = clean_text
                    break
            
            if text_content:
                toc_entries.append((bookmark_name, text_content))
    
    # 输出结果
    print(f"\n📋 成功提取 {len(toc_entries)} 个目录项:")
    print("-" * 60)
    
    # 按书签名排序（按数字排序）
    toc_entries.sort(key=lambda x: int(x[0].split('_Toc')[1]))
    
    for i, (bookmark, text) in enumerate(toc_entries, 1):
        print(f"{i:2d}. {bookmark}: {text}")
    
    # 过滤出真正的目录条目（通常从"摘要"、"目录"、"绪论"等开始）
    print(f"\n🎯 过滤有效目录条目:")
    print("-" * 60)
    
    # 查找目录起始位置
    start_keywords = ['摘要', '摘 要', 'ABSTRACT', '目录', '绪论', '第一章', '第1章', '1.', '1 ']
    start_index = -1
    
    for i, (bookmark, text) in enumerate(toc_entries):
        for keyword in start_keywords:
            if keyword in text:
                start_index = i
                break
        if start_index >= 0:
            break
    
    if start_index >= 0:
        filtered_toc = toc_entries[start_index:]
        print(f"从第 {start_index + 1} 个条目开始，找到 {len(filtered_toc)} 个有效目录项:")
        
        for i, (bookmark, text) in enumerate(filtered_toc, 1):
            print(f"{i:2d}. {text}")
        
        return filtered_toc
    else:
        print("未找到明确的目录起始点，返回所有条目")
        return toc_entries

def format_toc_output(toc_entries):
    """格式化TOC输出"""
    print(f"\n📄 格式化目录输出:")
    print("-" * 60)
    
    formatted_toc = []
    for i, (bookmark, text) in enumerate(toc_entries, 1):
        # 简单的层级判断
        level = 1
        if any(keyword in text for keyword in ['第一章', '第二章', '第三章', '第四章', '第五章', '第六章']):
            level = 1
        elif any(keyword in text for keyword in ['1.1', '2.1', '3.1', '4.1', '5.1', '6.1']):
            level = 2
        elif any(keyword in text for keyword in ['1.1.1', '2.1.1', '3.1.1']):
            level = 3
        
        indent = "  " * (level - 1)
        formatted_entry = f"{indent}{text}"
        formatted_toc.append(formatted_entry)
        print(f"{i:2d}. {formatted_entry}")
    
    return formatted_toc

if __name__ == "__main__":
    doc_path = "data/input/1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    
    # 完整提取TOC
    toc_entries = extract_complete_toc_from_bookmarks(doc_path)
    
    # 格式化输出
    if toc_entries:
        formatted_toc = format_toc_output(toc_entries)
        
        # 保存结果
        with open("extracted_toc_complete.txt", "w", encoding="utf-8") as f:
            f.write("完整提取的目录结构\n")
            f.write("=" * 50 + "\n\n")
            for i, entry in enumerate(formatted_toc, 1):
                f.write(f"{i:2d}. {entry}\n")
        
        print(f"\n 目录已保存到 extracted_toc_complete.txt")
        print(f"总共提取了 {len(formatted_toc)} 个目录条目")

