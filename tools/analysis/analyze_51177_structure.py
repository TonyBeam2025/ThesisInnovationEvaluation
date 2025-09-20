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
    print(f"\n� 与心脏成像论文结构对比:")
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
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    print(f"📊 文件总长度: {len(content):,} 字符")
    
    # 分割成行进行分析
    lines = content.split('\n')
    print(f"📄 总行数: {len(lines):,} 行")
    
    # 定位关键部分
    sections = {
        "封面信息": [],
        "摘要部分": [],
        "目录部分": [],
        "正文开始": [],
        "参考文献": [],
        "结论部分": []
    }
    
    # 关键词模式
    patterns = {
        "封面信息": [
            r"学位论文", r"硕士论文", r"博士论文", r"毕业论文",
            r"申请学位", r"学位级别", r"培养单位", r"指导教师",
            r"学科专业", r"研究方向", r"答辩日期"
        ],
        "摘要部分": [
            r"摘\s*要", r"abstract", r"关键词", r"keywords"
        ],
        "目录部分": [
            r"目\s*录", r"contents", r"第.*章", r"第.*节",
            r"^\s*\d+\..*", r"^\s*\d+\.\d+.*"
        ],
        "正文开始": [
            r"引言", r"绪论", r"概述", r"第一章", r"第1章",
            r"1\s*引言", r"1\s*绪论"
        ],
        "参考文献": [
            r"参考文献", r"references", r"引用文献", r"文献", r"\[\d+\]"
        ],
        "结论部分": [
            r"结论", r"总结", r"conclusion", r"结语", r"小结"
        ]
    }
    
    # 扫描文件，查找关键部分
    for line_no, line in enumerate(lines, 1):
        line_clean = line.strip().lower()
        line_orig = line.strip()
        
        # 跳过空行
        if not line_clean:
            continue
        
        # 检查每个类别
        for section_name, section_patterns in patterns.items():
            for pattern in section_patterns:
                if re.search(pattern, line_clean, re.IGNORECASE):
                    sections[section_name].append({
                        'line_no': line_no,
                        'content': line_orig[:100] + "..." if len(line_orig) > 100 else line_orig,
                        'pattern': pattern
                    })
                    break
    
    # 输出结果
    print("\n" + "="*60)
    print("📍 关键部分定位结果")
    print("="*60)
    
    for section_name, matches in sections.items():
        print(f"\n🔸 {section_name}:")
        if matches:
            # 显示前5个匹配
            for i, match in enumerate(matches[:5]):
                print(f"   第{match['line_no']:,}行: {match['content']}")
                if i == 0:
                    # 显示第一个匹配周围的内容
                    start_line = max(0, match['line_no'] - 3)
                    end_line = min(len(lines), match['line_no'] + 2)
                    print(f"   📖 上下文 (第{start_line+1}-{end_line}行):")
                    for j in range(start_line, end_line):
                        prefix = "   >>> " if j == match['line_no'] - 1 else "       "
                        context_line = lines[j].strip()[:80]
                        if context_line:
                            print(f"{prefix}{context_line}")
            
            if len(matches) > 5:
                print(f"   ... 还有 {len(matches) - 5} 个匹配")
        else:
            print("   ❌ 未找到相关内容")
    
    # 提取具体信息
    print("\n" + "="*60)
    print("📋 提取的具体信息")
    print("="*60)
    
    # 尝试提取标题
    title_candidates = []
    for line_no in range(min(50, len(lines))):  # 前50行
        line = lines[line_no].strip()
        if line and len(line) > 10 and len(line) < 100:
            # 可能的标题特征
            if any(keyword in line.lower() for keyword in ['研究', '分析', '设计', '系统', '方法', '技术']):
                title_candidates.append({
                    'line_no': line_no + 1,
                    'content': line
                })
    
    print("\n🎯 可能的论文标题:")
    for candidate in title_candidates[:3]:
        print(f"   第{candidate['line_no']}行: {candidate['content']}")
    
    # 尝试提取作者信息
    author_candidates = []
    for line_no in range(min(100, len(lines))):  # 前100行
        line = lines[line_no].strip()
        if re.search(r'(作者|申请人|研究生|学生)[:：]', line):
            author_candidates.append({
                'line_no': line_no + 1,
                'content': line
            })
    
    print("\n👤 可能的作者信息:")
    for candidate in author_candidates[:3]:
        print(f"   第{candidate['line_no']}行: {candidate['content']}")
    
    # 尝试提取学校信息
    university_candidates = []
    for line_no in range(min(100, len(lines))):  # 前100行
        line = lines[line_no].strip()
        if re.search(r'(大学|学院|学校|university)', line, re.IGNORECASE):
            university_candidates.append({
                'line_no': line_no + 1,
                'content': line
            })
    
    print("\n🏫 可能的学校信息:")
    for candidate in university_candidates[:3]:
        print(f"   第{candidate['line_no']}行: {candidate['content']}")
    
    # 给出建议的文本分割策略
    print("\n" + "="*60)
    print("💡 建议的文本分割策略")
    print("="*60)
    
    # 找到第一个正文标志
    content_start = None
    for match in sections["正文开始"]:
        content_start = match['line_no']
        break
    
    if not content_start:
        # 如果没找到明确的正文开始，尝试找目录后的位置
        if sections["目录部分"]:
            content_start = sections["目录部分"][-1]['line_no'] + 20  # 目录后20行
    
    # 找到参考文献开始
    ref_start = None
    for match in sections["参考文献"]:
        ref_start = match['line_no']
        break
    
    print(f"📖 建议分割方案:")
    print(f"   前置部分 (封面+摘要): 第1行 - 第{content_start or 200}行")
    print(f"   正文部分: 第{content_start or 200}行 - 第{ref_start or len(lines)-100}行")
    print(f"   参考文献部分: 第{ref_start or len(lines)-100}行 - 第{len(lines)}行")
    
    # 字符统计
    if content_start:
        front_matter_chars = len('\n'.join(lines[:content_start]))
        print(f"   前置部分字符数: {front_matter_chars:,}")
    
    if content_start and ref_start:
        main_content_chars = len('\n'.join(lines[content_start:ref_start]))
        print(f"   正文部分字符数: {main_content_chars:,}")

if __name__ == "__main__":
    analyze_md_structure()
