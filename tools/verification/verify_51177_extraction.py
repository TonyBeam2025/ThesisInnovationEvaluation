#!/usr/bin/env python3
"""
验证51177论文的提取结果
"""

import json
from pathlib import Path

def verify_51177_extraction():
    """验证51177论文的提取结果"""
    
    project_root = Path(__file__).parent
    result_file = project_root / "data" / "output" / "51177_extracted_info.json"
    
    if not result_file.exists():
        print("❌ 结果文件不存在")
        return
    
    with open(result_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🎯 验证51177论文提取结果")
    print("=" * 60)
    
    # 关键字段验证
    key_fields = [
        'ChineseTitle', 'EnglishTitle', 'ChineseAuthor', 'EnglishAuthor',
        'ChineseUniversity', 'EnglishUniversity', 'DegreeLevel', 
        'ChineseMajor', 'ChineseSupervisor', 'ChineseAbstract', 'ChineseKeywords'
    ]
    
    print("📋 关键字段验证:")
    for field in key_fields:
        value = data.get(field, '')
        if value:
            if isinstance(value, str) and len(value) > 50:
                preview = value[:50] + "..."
            else:
                preview = str(value)
            print(f"    {field}: {preview}")
        else:
            print(f"   ❌ {field}: [空]")
    
    # 统计结果
    total_expected = 24  # 期望的总字段数
    extracted_count = len([k for k, v in data.items() if v and str(v).strip()])
    
    print(f"\n📊 统计结果:")
    print(f"   已提取字段: {extracted_count}")
    print(f"   期望字段: {total_expected}")
    print(f"   完整度: {extracted_count/total_expected*100:.1f}%")
    
    # 验证核心信息
    print(f"\n🔍 核心信息验证:")
    
    # 验证标题
    chinese_title = data.get('ChineseTitle', '')
    if 'Bi-Sb-Se' in chinese_title and '热电性能研究' in chinese_title:
        print(f"    中文标题正确: {chinese_title}")
    else:
        print(f"   ❌ 中文标题可能有误: {chinese_title}")
    
    # 验证作者
    author = data.get('ChineseAuthor', '')
    if author == '王思宁':
        print(f"    作者正确: {author}")
    else:
        print(f"   ❌ 作者信息: {author}")
    
    # 验证学校
    university = data.get('ChineseUniversity', '')
    if university == '北京航空航天大学':
        print(f"    学校正确: {university}")
    else:
        print(f"   ❌ 学校信息: {university}")
    
    # 验证学位
    degree = data.get('DegreeLevel', '')
    if '博士' in degree:
        print(f"    学位级别正确: {degree}")
    else:
        print(f"   ❌ 学位级别: {degree}")
    
    # 验证摘要
    abstract = data.get('ChineseAbstract', '')
    if len(abstract) > 500 and 'BiSbSe3' in abstract:
        print(f"    摘要完整: {len(abstract)} 字符")
    else:
        print(f"   ⚠️ 摘要: {len(abstract)} 字符")
    
    print("\n" + "=" * 60)
    
    # 缺失字段分析
    missing_important = []
    important_fields = ['ReferenceList', 'ResearchConclusions', 'TableOfContents']
    
    for field in important_fields:
        if not data.get(field):
            missing_important.append(field)
    
    if missing_important:
        print(f"⚠️ 重要字段缺失: {', '.join(missing_important)}")
        print(f"💡 建议: 可以进一步分析文档结构来补充这些字段")
    else:
        print(f" 所有重要字段都已提取")
    
    # 总体评价
    if extracted_count >= 10:
        print(f"\n🏆 总体评价: 提取效果良好，核心信息完整")
    elif extracted_count >= 7:
        print(f"\n👍 总体评价: 提取效果一般，基本信息完整")
    else:
        print(f"\n⚠️ 总体评价: 提取效果有待改进")

if __name__ == "__main__":
    verify_51177_extraction()

