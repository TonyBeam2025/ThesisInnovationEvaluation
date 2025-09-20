#!/usr/bin/env python3
"""
验证分步抽取功能的效果
"""

import json
from pathlib import Path

def verify_extraction_results():
    """验证抽取结果"""
    
    project_root = Path(__file__).parent
    
    # 读取新抽取的结果
    new_file = project_root / "data" / "output" / "Bi-Sb-Se基材料的制备及热电性能研究_extracted_info.json"
    
    if not new_file.exists():
        print("❌ 新抽取的文件不存在")
        return
    
    with open(new_file, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    print("🎯 验证分步抽取结果")
    print("=" * 60)
    
    # 检查关键信息
    print("📋 标题信息:")
    chinese_title = new_data.get('ChineseTitle', '')
    print(f"   中文标题: {chinese_title}")
    
    # 验证标题是否正确
    expected_title = "Bi-Sb-Se基材料的制备及热电性能研究"
    is_title_correct = chinese_title == expected_title
    print(f"   标题正确性: {' 正确' if is_title_correct else '❌ 错误'}")
    
    if not is_title_correct and chinese_title:
        print(f"   期望标题: {expected_title}")
        print(f"   实际标题: {chinese_title}")
    
    print("\n📊 抽取统计:")
    total_fields = len(new_data)
    non_empty_fields = len([k for k, v in new_data.items() if v and str(v).strip()])
    print(f"   总字段数: {total_fields}")
    print(f"   非空字段数: {non_empty_fields}")
    print(f"   完整度: {non_empty_fields/total_fields*100:.1f}%")
    
    print("\n📖 内容预览:")
    
    # 显示摘要
    abstract = new_data.get('ChineseAbstract', '')
    if abstract:
        abstract_preview = abstract[:200] + "..." if len(abstract) > 200 else abstract
        print(f"   摘要: {abstract_preview}")
    else:
        print("   摘要: [空]")
    
    # 显示关键词
    keywords = new_data.get('ChineseKeywords', '')
    if keywords:
        keywords_preview = keywords[:100] + "..." if len(keywords) > 100 else keywords
        print(f"   关键词: {keywords_preview}")
    else:
        print("   关键词: [空]")
    
    # 显示创新点
    innovations = new_data.get('MainInnovations', [])
    if innovations:
        print(f"   主要创新点:")
        for i, innovation in enumerate(innovations, 1):
            print(f"     {i}. {innovation}")
    else:
        print("   主要创新点: [空]")
    
    print("\n🔍 字段详情:")
    for field, value in new_data.items():
        if value:
            if isinstance(value, list):
                print(f"   {field}: {len(value)} 项")
            elif isinstance(value, str):
                length = len(value)
                print(f"   {field}: {length} 字符")
        else:
            print(f"   {field}: [空]")
    
    print("\n" + "=" * 60)
    
    # 总结
    if is_title_correct:
        print(" 分步抽取功能工作正常，标题提取正确")
    else:
        print("⚠️ 标题提取可能仍有问题，需要进一步优化")
    
    if non_empty_fields >= 6:
        print(" 信息抽取较为完整，满足基本需求")
    else:
        print("⚠️ 信息抽取不够完整，建议优化提取策略")
    
    print(f"\n📝 建议改进方向:")
    
    missing_fields = []
    important_fields = ['ChineseAuthor', 'ChineseUniversity', 'DegreeLevel', 'ReferenceList']
    
    for field in important_fields:
        if not new_data.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        print(f"   - 补充缺失的重要字段: {', '.join(missing_fields)}")
    
    if len(abstract) < 500:
        print(f"   - 改进摘要提取（当前 {len(abstract)} 字符）")
    
    if not keywords or len(keywords) < 50:
        print(f"   - 改进关键词提取")

if __name__ == "__main__":
    verify_extraction_results()

