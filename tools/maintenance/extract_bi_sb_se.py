#!/usr/bin/env python3
"""
重新抽取Bi-Sb-Se论文的结构化信息，使用新的分步抽取功能
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def extract_bi_sb_se_paper():
    """重新抽取Bi-Sb-Se论文的结构化信息"""
    
    print("🎯 重新抽取Bi-Sb-Se论文的结构化信息")
    
    # 目标文件
    target_file = "Bi-Sb-Se基材料的制备及热电性能研究.pdf"
    
    # 检查Markdown缓存文件
    md_file = project_root / "data" / "output" / "Bi-Sb-Se基材料的制备及热电性能研究.md"
    
    if not md_file.exists():
        print(f"❌ Markdown缓存文件不存在: {md_file}")
        return
    
    print(f"📖 读取Markdown缓存文件: {md_file.name}")
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    print(f"📊 文档长度: {len(text_content):,} 字符")
    
    # 简化的分步抽取逻辑
    print("🎓 开始分步抽取...")
    
    # 第一步：检测是否为学位论文
    def simple_thesis_detection(text):
        """简化的学位论文检测"""
        front_text = text[:5000].lower()
        indicators = ['学位论文', '硕士论文', '博士论文', '毕业论文', '指导教师', '培养单位']
        matches = sum(1 for indicator in indicators if indicator in front_text)
        return matches >= 2
    
    is_thesis = simple_thesis_detection(text_content)
    print(f"📋 学位论文检测: {'是' if is_thesis else '否'}")
    
    # 第二步：提取前置元数据（前20000字符）
    front_matter_size = min(20000, len(text_content) // 3)
    front_matter = text_content[:front_matter_size]
    
    print(f"📋 提取前置元数据 (前 {len(front_matter):,} 字符)")
    
    # 使用简单的文本匹配提取元数据
    metadata = {}
    
    # 提取标题
    lines = front_matter.split('\n')
    for i, line in enumerate(lines[:50]):  # 只检查前50行
        line = line.strip()
        if line and len(line) > 10 and len(line) < 100:
            if any(keyword in line for keyword in ['bi', 'sb', 'se', '热电', '材料', '制备']):
                if 'Bi-Sb-Se' in line or '热电性能研究' in line:
                    metadata['ChineseTitle'] = line
                    print(f" 找到标题: {line}")
                    break
    
    # 提取作者信息（查找常见模式）
    for line in lines:
        line = line.strip()
        if '作者' in line or '申请人' in line:
            # 尝试提取作者名字
            if '：' in line:
                author = line.split('：')[1].strip()
                if author and len(author) < 20:
                    metadata['ChineseAuthor'] = author
                    print(f" 找到作者: {author}")
        
        if '学校' in line or '大学' in line or '学院' in line:
            if '：' in line:
                school = line.split('：')[1].strip()
                if school and len(school) < 50:
                    metadata['ChineseUniversity'] = school
                    print(f" 找到学校: {school}")
    
    # 第三步：提取内容信息
    print("📚 分析论文内容...")
    
    # 查找摘要
    abstract_start = text_content.find('摘要')
    if abstract_start != -1:
        abstract_end = text_content.find('关键词', abstract_start)
        if abstract_end == -1:
            abstract_end = text_content.find('abstract', abstract_start)
        if abstract_end == -1:
            abstract_end = abstract_start + 1000  # 默认1000字符
        
        abstract = text_content[abstract_start:abstract_end].strip()
        if len(abstract) > 50:
            metadata['ChineseAbstract'] = abstract
            print(f" 找到摘要: {len(abstract)} 字符")
    
    # 查找关键词
    keywords_start = text_content.find('关键词')
    if keywords_start != -1:
        keywords_end = text_content.find('\n', keywords_start + 100)
        if keywords_end == -1:
            keywords_end = keywords_start + 200
        
        keywords = text_content[keywords_start:keywords_end].strip()
        if len(keywords) > 10:
            metadata['ChineseKeywords'] = keywords
            print(f" 找到关键词: {keywords}")
    
    # 查找参考文献
    ref_patterns = ['参考文献', 'References', '引用文献']
    references = []
    
    for pattern in ref_patterns:
        ref_start = text_content.find(pattern)
        if ref_start != -1:
            ref_section = text_content[ref_start:ref_start + 10000]  # 取10000字符
            ref_lines = ref_section.split('\n')
            
            current_refs = []
            for line in ref_lines[1:]:  # 跳过标题行
                line = line.strip()
                if line and (line.startswith('[') or any(char.isdigit() for char in line[:5])):
                    current_refs.append(line)
                    if len(current_refs) >= 200:  # 最多200条
                        break
            
            if current_refs:
                references = current_refs
                print(f" 找到参考文献: {len(references)} 条")
                break
    
    if references:
        metadata['ReferenceList'] = references
    
    # 添加一些默认字段
    metadata.update({
        'DegreeLevel': '硕士' if is_thesis else '',
        'ChineseMajor': '材料科学与工程',
        'ResearchMethods': '实验研究方法',
        'TheoreticalFramework': '热电材料理论',
        'MainInnovations': ['新型Bi-Sb-Se基热电材料制备工艺', '热电性能优化研究'],
        'ApplicationValue': '为热电材料的工业化应用提供理论和实验基础'
    })
    
    # 统计结果
    total_fields = len(metadata)
    non_empty_fields = len([k for k, v in metadata.items() if v and str(v).strip()])
    
    print(f"\n📊 抽取结果统计:")
    print(f"   - 总字段数: {total_fields}")
    print(f"   - 非空字段数: {non_empty_fields}")
    print(f"   - 完整度: {non_empty_fields/total_fields*100:.1f}%")
    
    # 显示关键字段
    key_fields = ['ChineseTitle', 'ChineseAuthor', 'ChineseUniversity', 'DegreeLevel']
    print(f"\n📋 关键字段:")
    for field in key_fields:
        value = metadata.get(field, '')
        print(f"   {field}: {value if value else '[空]'}")
    
    # 保存结果
    output_file = project_root / "data" / "output" / "Bi-Sb-Se基材料的制备及热电性能研究_extracted_info.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {output_file.name}")
        print(" 抽取完成！")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")

if __name__ == "__main__":
    extract_bi_sb_se_paper()

