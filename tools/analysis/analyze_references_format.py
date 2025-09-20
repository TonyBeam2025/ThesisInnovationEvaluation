#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析参考文献提取的具体内容和格式
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy

def analyze_references_format():
    """分析参考文献格式"""
    print("🔍 分析参考文献提取格式...")
    
    # 测试文件路径
    test_file = r".\data\input\跨模态图像融合技术在医疗影像分析中的研究.docx"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    try:
        # 使用专业版策略提取
        result = extract_sections_with_pro_strategy(test_file)
        
        if not result:
            print("❌ 提取失败，结果为空")
            return False
        
        references = result.get('references', [])
        
        print(f"\n📚 提取到 {len(references)} 条参考文献")
        print("=" * 80)
        
        # 分析每条参考文献的详细格式
        for i, ref in enumerate(references):
            print(f"\n参考文献 {i+1}:")
            print(f"原始内容: {repr(ref)}")
            print(f"显示内容: {ref}")
            
            # 分析格式特征
            has_bracket = ref.strip().startswith('[') and ']' in ref[:10]
            has_number_dot = ref.strip().split('.')[0].isdigit() if '.' in ref[:5] else False
            
            if has_bracket:
                print(" 格式: [数字] 编号")
            elif has_number_dot:
                print(" 格式: 数字. 编号")
            else:
                print("⚠️ 格式: 无标准编号")
            
            print("-" * 40)
            
            if i >= 9:  # 只显示前10条
                print(f"... 还有 {len(references)-10} 条参考文献")
                break
        
        # 保存完整结果到文件供查看
        output_file = "references_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_count': len(references),
                'references': references,
                'analysis_time': str(result.get('metadata', {}).get('extraction_time'))
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 完整参考文献保存到: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    analyze_references_format()

