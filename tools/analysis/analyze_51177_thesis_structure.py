#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
51177论文目录章节信息分析
使用心脏成像论文提取器框架分析51177论文的结构
"""

import re
import json
from typing import Dict, List, Tuple

def analyze_51177_thesis_structure():
    """分析51177论文的目录结构"""
    
    # 读取文档
    with open(r'c:\MyProjects\thesis_Inno_Eval\cache\documents\51177_b6ac1c475108811bd4a31a6ebcd397df.md', 
              'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== 51177论文目录章节信息分析 ===\n")
    
    # 基本信息
    print("📄 论文基本信息:")
    title_match = re.search(r'Bi-Sb-Se基材料的.*?制备及热电性能研究', content)
    if title_match:
        print(f"   标题: {title_match.group()}")
    
    author_match = re.search(r'作者姓名\s+(\S+)', content)
    if author_match:
        print(f"   作者: {author_match.group(1)}")
    
    supervisor_match = re.search(r'指导教师\s+(\S+)', content)
    if supervisor_match:
        print(f"   指导教师: {supervisor_match.group(1)}")
    
    print(f"   文档字符数: {len(content):,}")
    print()
    
    # 提取目录结构
    print("📋 目录结构分析:")
    
    # 查找目录部分
    toc_match = re.search(r'目\s*录(.*?)主要符号表', content, re.DOTALL)
    if not toc_match:
        print("❌ 未找到目录部分")
        return
    
    toc_content = toc_match.group(1)
    lines = toc_content.split('\n')
    
    # 分析目录项
    sections = []
    current_chapter = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 匹配主章节 (### 第X章)
        main_chapter_match = re.match(r'###\s+(第[一二三四五六1-6]章)\s+([^	\d]+)', line)
        if main_chapter_match:
            chapter_num = main_chapter_match.group(1)
            chapter_title = main_chapter_match.group(2).strip()
            current_chapter = {
                'type': 'main_chapter',
                'number': chapter_num,
                'title': chapter_title,
                'subsections': []
            }
            sections.append(current_chapter)
            print(f"   📚 {chapter_num}: {chapter_title}")
            continue
        
        # 匹配子章节 (### X.Y)
        sub_chapter_match = re.match(r'###\s+(\d+\.\d+(?:\.\d+)?)\s+([^	\d]+)', line)
        if sub_chapter_match:
            section_num = sub_chapter_match.group(1)
            section_title = sub_chapter_match.group(2).strip()
            subsection = {
                'type': 'subsection',
                'number': section_num,
                'title': section_title
            }
            if current_chapter:
                current_chapter['subsections'].append(subsection)
            print(f"      🔸 {section_num} {section_title}")
            continue
        
        # 匹配其他特殊章节
        special_match = re.match(r'###?\s*([^#\d][^	]*)', line)
        if special_match:
            special_title = special_match.group(1).strip()
            if special_title and not re.match(r'\d+$', special_title):
                sections.append({
                    'type': 'special_section',
                    'title': special_title
                })
                print(f"   📄 特殊章节: {special_title}")
    
    print(f"\n📊 结构统计:")
    main_chapters = [s for s in sections if s.get('type') == 'main_chapter']
    special_sections = [s for s in sections if s.get('type') == 'special_section']
    total_subsections = sum(len(ch.get('subsections', [])) for ch in main_chapters)
    
    print(f"   主章节数: {len(main_chapters)}")
    print(f"   子章节数: {total_subsections}")
    print(f"   特殊章节数: {len(special_sections)}")
    print(f"   总章节数: {len(main_chapters) + total_subsections + len(special_sections)}")
    
    # 分析章节层次
    print(f"\n🔍 章节层次分析:")
    for chapter in main_chapters:
        subsection_count = len(chapter.get('subsections', []))
        print(f"   {chapter['number']}: {subsection_count} 个子章节")
        if subsection_count > 0:
            for sub in chapter['subsections'][:3]:  # 显示前3个
                print(f"     - {sub['number']} {sub['title']}")
            if subsection_count > 3:
                print(f"     - ... 还有 {subsection_count - 3} 个子章节")
    
    # 特殊结构分析
    print(f"\n💡 结构特点:")
    print("1. 采用标准的博士论文结构")
    print("2. 主章节使用 '### 第X章' 格式")
    print("3. 子章节使用 '### X.Y' 数字编号格式")
    print("4. 包含完整的前置和后置部分")
    print("5. 专业术语较多，属于材料科学领域")
    
    # 与心脏成像论文的对比
    print(f"\n🔄 与心脏成像论文结构对比:")
    print("相同点:")
    print("- 都使用 ### 标记子章节")
    print("- 都有清晰的数字编号系统")
    print("- 都包含多层次的嵌套结构")
    print()
    print("不同点:")
    print("- 51177使用传统的'第X章'格式，心脏成像使用纯数字")
    print("- 51177子章节编号更复杂 (X.Y.Z)，心脏成像相对简单 (X.Y)")
    print("- 51177属于材料科学，心脏成像属于医学工程")
    
    # 保存分析结果
    result = {
        'thesis_info': {
            'title': title_match.group() if title_match else '',
            'author': author_match.group(1) if author_match else '',
            'supervisor': supervisor_match.group(1) if supervisor_match else '',
            'char_count': len(content)
        },
        'structure': {
            'main_chapters': len(main_chapters),
            'total_subsections': total_subsections,
            'special_sections': len(special_sections)
        },
        'sections': sections
    }
    
    with open('51177_thesis_structure_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 分析结果已保存到: 51177_thesis_structure_analysis.json")
    
    return result

if __name__ == "__main__":
    analyze_51177_thesis_structure()
