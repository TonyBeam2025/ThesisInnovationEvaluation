#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试50193.docx书签提取，查找缺失的"结论"和"作者简介"章节
"""

from src.thesis_inno_eval.ai_toc_extractor import AITocExtractor
import docx
import re

def debug_bookmark_extraction():
    print('🔍 详细分析50193.docx所有书签内容')
    print('=' * 80)

    # 读取文档
    doc_path = 'data/input/50193.docx'
    document = docx.Document(doc_path)
    document_xml = document._element.xml

    # 查找所有TOC书签 - 简化正则表达式
    bookmark_pattern = r'<w:bookmarkStart[^>]*w:name="(_Toc\d+)"[^>]*/>'
    bookmark_starts = re.finditer(bookmark_pattern, document_xml)

    bookmark_positions = []

    # 收集所有书签位置
    for match in bookmark_starts:
        bookmark_name = match.group(1)
        start_pos = match.end()
        bookmark_positions.append((bookmark_name, start_pos))

    print(f'📊 找到 {len(bookmark_positions)} 个TOC书签')
    print()

    # 提取每个书签的文本内容
    toc_entries = []
    conclusion_found = False
    author_found = False

    for i, (bookmark_name, start_pos) in enumerate(bookmark_positions):
        # 确定提取文本的结束位置
        if i + 1 < len(bookmark_positions):
            end_pos = bookmark_positions[i + 1][1]
        else:
            end_pos = start_pos + 2000
        
        # 提取书签后的XML片段
        xml_fragment = document_xml[start_pos:end_pos]
        
        # 从XML中提取文本内容
        text_pattern = r'<w:t[^>]*>(.*?)</w:t>'
        text_matches = re.findall(text_pattern, xml_fragment, re.DOTALL)
        
        if text_matches:
            text_parts = []
            for text in text_matches:
                clean_text = text.strip()
                if clean_text and not clean_text.isspace():
                    text_parts.append(clean_text)
                if len(' '.join(text_parts)) > 100:
                    break
            
            if text_parts:
                text_content = ' '.join(text_parts)
                toc_entries.append((bookmark_name, text_content))
                
                # 检查是否包含结论或作者简介
                if '结' in text_content and '论' in text_content:
                    conclusion_found = True
                    print(f'🎯 找到结论书签: {bookmark_name} -> {text_content[:50]}...')
                
                if '作者' in text_content and '简介' in text_content:
                    author_found = True
                    print(f'🎯 找到作者简介书签: {bookmark_name} -> {text_content[:50]}...')

    print()
    print(f'📊 分析结果:')
    print(f'   总书签数: {len(toc_entries)}')
    print(f'   包含结论: {"" if conclusion_found else "❌"}')
    print(f'   包含作者简介: {"" if author_found else "❌"}')

    if not conclusion_found or not author_found:
        print()
        print('🔍 显示最后20个书签，查找可能遗漏的内容:')
        for i, (bookmark, text) in enumerate(toc_entries[-20:], len(toc_entries)-19):
            display_text = text[:60].replace('\n', ' ')
            print(f'[{i:2d}] {bookmark}: {display_text}...')
        
        print()
        print('🔍 搜索所有书签中包含"结"或"作者"的条目:')
        for i, (bookmark, text) in enumerate(toc_entries):
            if '结' in text or '作者' in text or '论' in text:
                display_text = text[:80].replace('\n', ' ')
                print(f'[{i+1:2d}] {bookmark}: {display_text}...')

if __name__ == "__main__":
    debug_bookmark_extraction()

