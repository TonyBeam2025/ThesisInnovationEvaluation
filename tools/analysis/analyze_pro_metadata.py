#!/usr/bin/env python3
"""
详细分析专业版提取结果的元数据
"""

import json

def analyze_pro_metadata():
    """分析专业版提取的详细元数据"""
    
    with open('data/output/50193_pro_extracted_info.json', 'r', encoding='utf-8') as f:
        pro_data = json.load(f)
    
    metadata = pro_data['metadata']
    
    print("🔬 专业版提取详细分析")
    print("=" * 50)
    
    print(f"📅 提取时间: {metadata['extraction_time']}")
    print(f"📁 文件路径: {metadata['file_path']}")
    print(f"🔧 提取方法: {metadata['method']}")
    print(f"📦 提取器版本: {metadata['extractor_version']}")
    
    # 详细分析统计信息
    if 'stats' in metadata:
        stats = metadata['stats']
        print("\n📊 提取统计信息")
        print("-" * 30)
        print(f"总字段数: {stats['total_fields']}")
        print(f"成功提取字段数: {stats['extracted_fields']}")
        print(f"提取成功率: {stats['confidence']:.2%}")
        print(f"处理耗时: {stats['processing_time']:.2f} 秒")
        print(f"学科分类: {stats['discipline']}")
        
        print(f"\n🎯 多学科特征检测 ({len(stats['multidisciplinary_features'])}个):")
        for i, feature in enumerate(stats['multidisciplinary_features'], 1):
            print(f"  {i}. {feature}")
    
    # 检查提取内容的质量
    extracted_info = pro_data['extracted_info']
    print(f"\n📄 提取内容概览")
    print("-" * 30)
    
    filled_fields = 0
    for key, value in extracted_info.items():
        if value and str(value).strip():
            filled_fields += 1
    
    print(f"有内容的字段: {filled_fields}/{len(extracted_info)}")
    print(f"字段填充率: {filled_fields/len(extracted_info):.2%}")
    
    # 显示一些关键字段
    key_fields = ['thesis_title_zh', 'thesis_title_en', 'author', 'supervisor_zh', 'supervisor_en', 'university']
    print(f"\n🔑 关键字段检查")
    print("-" * 30)
    for field in key_fields:
        if field in extracted_info:
            value = extracted_info[field]
            status = "" if value and str(value).strip() else "❌"
            display_value = str(value) if len(str(value)) < 50 else str(value)[:47]+'...'
            print(f"{status} {field}: {display_value}")

if __name__ == "__main__":
    analyze_pro_metadata()

