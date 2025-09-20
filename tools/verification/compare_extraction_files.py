#!/usr/bin/env python3
"""
比较两个提取结果文件的差异
"""

import json
import os

def compare_extraction_files():
    """比较标准版和专业版提取结果的差异"""
    
    # 读取两个文件
    with open('data/output/50193_extracted_info.json', 'r', encoding='utf-8') as f:
        standard = json.load(f)
    
    with open('data/output/50193_pro_extracted_info.json', 'r', encoding='utf-8') as f:
        pro = json.load(f)
    
    print("🔍 文件结构对比")
    print("=" * 50)
    print(f"标准版字段数: {len(standard['extracted_info'])}")
    print(f"专业版字段数: {len(pro['extracted_info'])}")
    
    # 字段差异分析
    print("\n📊 字段差异分析")
    print("-" * 30)
    standard_keys = set(standard['extracted_info'].keys())
    pro_keys = set(pro['extracted_info'].keys())
    
    # 找出专业版独有的字段
    pro_only = pro_keys - standard_keys
    if pro_only:
        print(f"专业版独有字段: {list(pro_only)}")
    else:
        print("专业版没有独有字段")
    
    # 找出标准版独有的字段  
    standard_only = standard_keys - pro_keys
    if standard_only:
        print(f"标准版独有字段: {list(standard_only)}")
    else:
        print("标准版没有独有字段")
    
    # 内容一致性检查
    print("\n📄 内容一致性检查")
    print("-" * 30)
    
    different_fields = []
    for key in standard_keys & pro_keys:
        if standard['extracted_info'][key] != pro['extracted_info'][key]:
            different_fields.append(key)
    
    if different_fields:
        print(f"内容不同的字段: {different_fields}")
        for field in different_fields:
            print(f"\n字段 '{field}' 差异:")
            print(f"  标准版: {standard['extracted_info'][field]}")
            print(f"  专业版: {pro['extracted_info'][field]}")
    else:
        print(" 所有共同字段内容完全一致")
    
    # 文件大小对比
    print("\n📏 文件大小对比")
    print("-" * 30)
    size1 = os.path.getsize('data/output/50193_extracted_info.json')
    size2 = os.path.getsize('data/output/50193_pro_extracted_info.json')
    print(f"标准版: {size1:,} 字节")
    print(f"专业版: {size2:,} 字节")
    print(f"差异: {abs(size2-size1):,} 字节")
    
    # 检查metadata部分
    print("\n📋 元数据对比")
    print("-" * 30)
    
    if 'metadata' in standard and 'metadata' in pro:
        std_meta = standard['metadata']
        pro_meta = pro['metadata']
        
        print("标准版元数据:")
        for key, value in std_meta.items():
            print(f"  {key}: {value}")
        
        print("\n专业版元数据:")
        for key, value in pro_meta.items():
            print(f"  {key}: {value}")
    else:
        print("未找到metadata字段")
    
    # 总结
    print("\n🎯 总结")
    print("-" * 30)
    if len(standard_keys) == len(pro_keys) and not different_fields:
        print(" 两个文件在结构和内容上完全一致")
        print("🤔 这表明在专家策略模式下，两种输出实际上是相同的")
    else:
        print("❌ 两个文件存在差异")
        print("🔍 建议进一步检查提取逻辑")

if __name__ == "__main__":
    compare_extraction_files()

