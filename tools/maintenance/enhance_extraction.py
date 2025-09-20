#!/usr/bin/env python3
"""
增强Bi-Sb-Se论文的结构化信息抽取，补充缺失字段
"""

import os
import sys
import json
import re
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def extract_missing_fields():
    """补充缺失的重要字段"""
    
    print("🎯 增强Bi-Sb-Se论文信息抽取 - 补充缺失字段")
    
    # 读取原始Markdown文件
    md_file = project_root / "data" / "output" / "Bi-Sb-Se基材料的制备及热电性能研究.md"
    
    if not md_file.exists():
        print(f"❌ Markdown文件不存在: {md_file}")
        return
    
    print(f"📖 读取原始文档: {md_file.name}")
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    print(f"📊 文档长度: {len(text_content):,} 字符")
    
    # 读取现有的抽取结果
    existing_file = project_root / "data" / "output" / "Bi-Sb-Se基材料的制备及热电性能研究_extracted_info.json"
    
    if existing_file.exists():
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        print(f"📋 读取现有数据: {len(existing_data)} 个字段")
    else:
        existing_data = {}
        print("📋 未找到现有数据，从零开始")
    
    # 增强字段提取
    enhanced_data = existing_data.copy()
    
    print("\n🔍 开始补充缺失字段...")
    
    # 1. 提取作者信息
    author_patterns = [
        r'作者[：:]\s*([^\n\r]{2,20})',
        r'申请人[：:]\s*([^\n\r]{2,20})',
        r'研究生[：:]\s*([^\n\r]{2,20})',
        r'学生姓名[：:]\s*([^\n\r]{2,20})',
        r'姓\s*名[：:]\s*([^\n\r]{2,20})',
    ]
    
    for pattern in author_patterns:
        match = re.search(pattern, text_content[:5000], re.MULTILINE)
        if match:
            author = match.group(1).strip()
            if author and len(author) < 20 and not any(char in author for char in ['：', ':', '，', '。']):
                enhanced_data['ChineseAuthor'] = author
                print(f" 找到作者: {author}")
                break
    
    # 2. 提取学校信息
    university_patterns = [
        r'([^，。\n\r]*大学[^，。\n\r]{0,10})',
        r'([^，。\n\r]*学院[^，。\n\r]{0,10})',
        r'培养单位[：:]\s*([^\n\r]{5,50})',
        r'学校[：:]\s*([^\n\r]{5,50})',
        r'院校[：:]\s*([^\n\r]{5,50})',
    ]
    
    for pattern in university_patterns:
        matches = re.findall(pattern, text_content[:8000])
        for match in matches:
            university = match.strip()
            if university and len(university) > 4 and len(university) < 50:
                if '大学' in university or '学院' in university:
                    enhanced_data['ChineseUniversity'] = university
                    print(f" 找到学校: {university}")
                    break
        if 'ChineseUniversity' in enhanced_data:
            break
    
    # 3. 提取学位级别
    degree_patterns = [
        r'申请.*?学位级别[：:]\s*(博士|硕士|学士)',
        r'学位.*?级别[：:]\s*(博士|硕士|学士)',
        r'(博士|硕士|学士).*?学位论文',
        r'(博士|硕士|学士).*?论文',
        r'申请.*?(博士|硕士|学士).*?学位',
    ]
    
    for pattern in degree_patterns:
        match = re.search(pattern, text_content[:5000])
        if match:
            degree = match.group(1)
            enhanced_data['DegreeLevel'] = degree
            print(f" 找到学位级别: {degree}")
            break
    
    # 4. 提取结论部分
    conclusion_patterns = [
        r'# 结论[\s\S]*?(?=# [^结]|$)',
        r'# 总结[\s\S]*?(?=# [^总]|$)',
        r'## 结论[\s\S]*?(?=## [^结]|$)',
        r'结论[：:][\s\S]*?(?=\n#|\n[0-9]+\.|\n[一二三四五六七八九十]|$)',
        r'## 小结[\s\S]*?(?=## [^小]|$)',
    ]
    
    conclusions = []
    for pattern in conclusion_patterns:
        matches = re.findall(pattern, text_content, re.MULTILINE | re.DOTALL)
        for match in matches:
            conclusion = match.strip()
            if len(conclusion) > 100:  # 结论应该有一定长度
                conclusions.append(conclusion)
    
    if conclusions:
        # 选择最长的结论
        best_conclusion = max(conclusions, key=len)
        enhanced_data['ResearchConclusions'] = best_conclusion
        print(f" 找到研究结论: {len(best_conclusion)} 字符")
    
    # 5. 增强参考文献提取
    ref_patterns = [
        r'参考文献([\s\S]*?)(?=\n#|$)',
        r'References([\s\S]*?)(?=\n#|$)',
        r'引用文献([\s\S]*?)(?=\n#|$)',
    ]
    
    for pattern in ref_patterns:
        match = re.search(pattern, text_content, re.MULTILINE | re.DOTALL)
        if match:
            ref_section = match.group(1).strip()
            ref_lines = []
            
            for line in ref_section.split('\n'):
                line = line.strip()
                if line:
                    # 检查是否是参考文献条目
                    if (line.startswith('[') or 
                        re.match(r'^\d+\.', line) or
                        re.match(r'^\[\d+\]', line)):
                        ref_lines.append(line)
            
            if len(ref_lines) > 10:  # 至少10条参考文献才认为有效
                enhanced_data['ReferenceList'] = ref_lines
                print(f" 找到参考文献: {len(ref_lines)} 条")
                break
    
    # 6. 提取研究目标/问题
    research_problem_patterns = [
        r'研究.*?目标[：:][\s\S]*?(?=\n#|\n[0-9]+\.|\n[一二三四五六七八九十])',
        r'研究.*?问题[：:][\s\S]*?(?=\n#|\n[0-9]+\.|\n[一二三四五六七八九十])',
        r'主要.*?问题[：:][\s\S]*?(?=\n#|\n[0-9]+\.|\n[一二三四五六七八九十])',
    ]
    
    for pattern in research_problem_patterns:
        match = re.search(pattern, text_content, re.MULTILINE | re.DOTALL)
        if match:
            problem = match.group(0).strip()
            if len(problem) > 50:
                enhanced_data['PracticalProblems'] = problem
                print(f" 找到研究问题: {len(problem)} 字符")
                break
    
    # 7. 提取创新点（如果现有不够详细）
    if 'MainInnovations' not in enhanced_data or len(enhanced_data.get('MainInnovations', [])) < 3:
        innovation_patterns = [
            r'创新.*?点[：:][\s\S]*?(?=\n#|\n[0-9]+\.)',
            r'主要.*?贡献[：:][\s\S]*?(?=\n#|\n[0-9]+\.)',
            r'技术.*?创新[：:][\s\S]*?(?=\n#|\n[0-9]+\.)',
        ]
        
        for pattern in innovation_patterns:
            match = re.search(pattern, text_content, re.MULTILINE | re.DOTALL)
            if match:
                innovation_text = match.group(0).strip()
                # 尝试分点提取
                innovation_points = []
                for line in innovation_text.split('\n'):
                    line = line.strip()
                    if (line.startswith('(') or line.startswith('（') or 
                        re.match(r'^[0-9]+[\.、]', line) or
                        re.match(r'^[①②③④⑤⑥⑦⑧⑨⑩]', line)):
                        innovation_points.append(line)
                
                if len(innovation_points) >= 2:
                    enhanced_data['MainInnovations'] = innovation_points
                    print(f" 增强创新点: {len(innovation_points)} 个")
                    break
    
    # 统计增强结果
    original_fields = len(existing_data)
    enhanced_fields = len(enhanced_data)
    new_fields = enhanced_fields - original_fields
    
    original_non_empty = len([k for k, v in existing_data.items() if v and str(v).strip()])
    enhanced_non_empty = len([k for k, v in enhanced_data.items() if v and str(v).strip()])
    
    print(f"\n📊 增强结果统计:")
    print(f"   - 原有字段数: {original_fields}")
    print(f"   - 增强后字段数: {enhanced_fields}")
    print(f"   - 新增字段数: {new_fields}")
    print(f"   - 原有非空字段: {original_non_empty}")
    print(f"   - 增强后非空字段: {enhanced_non_empty}")
    print(f"   - 非空字段增长: +{enhanced_non_empty - original_non_empty}")
    
    # 显示新增/更新的字段
    print(f"\n📋 新增/更新字段:")
    target_fields = ['ChineseAuthor', 'ChineseUniversity', 'DegreeLevel', 'ReferenceList', 'ResearchConclusions']
    
    for field in target_fields:
        value = enhanced_data.get(field, '')
        if value:
            if isinstance(value, list):
                print(f"    {field}: {len(value)} 项")
            elif isinstance(value, str):
                preview = value[:100] + "..." if len(value) > 100 else value
                print(f"    {field}: {preview}")
        else:
            print(f"   ❌ {field}: [仍为空]")
    
    # 保存增强后的结果
    output_file = project_root / "data" / "output" / "Bi-Sb-Se基材料的制备及热电性能研究_extracted_info_enhanced.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 增强结果已保存到: {output_file.name}")
        
        # 也更新原文件
        with open(existing_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 原文件已更新: {existing_file.name}")
        print(" 字段补充完成！")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")

if __name__ == "__main__":
    extract_missing_fields()

