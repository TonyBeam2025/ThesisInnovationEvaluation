#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试多个文档的TOC提取
"""

from updated_toc_extractor import UpdatedTOCExtractor

def main():
    # 测试多个文件
    test_files = [
        "data/input/计算机应用技术_test2.docx",
        "data/input/计算机应用技术_test1.docx", 
        "data/input/1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    ]
    
    for test_file in test_files:
        print(f"🔍 测试文件: {test_file}")
        print("=" * 80)
        
        try:
            # 创建提取器
            extractor = UpdatedTOCExtractor(test_file)
            
            # 提取目录
            toc_data = extractor.extract()
            
            if toc_data:
                print(f" 成功提取到 {len(toc_data)} 个目录条目:")
                print("-" * 40)
                
                for i, entry in enumerate(toc_data, 1):
                    level_indent = "  " * (entry.get('level', 1) - 1)
                    print(f"{i:2d}. {level_indent}{entry['title']} - 第{entry['page']}页")
                    print(f"     类型: {entry['type']}")
                    print(f"     原文: {entry['raw_text'][:50]}...")
                    print()
                
                if len(toc_data) > 0:
                    print("-" * 40)
                    print("📋 格式化目录:")
                    print(extractor.get_formatted_toc())
                
            else:
                print("❌ 未提取到目录条目")
                
        except Exception as e:
            print(f"❌ 提取过程出错: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
