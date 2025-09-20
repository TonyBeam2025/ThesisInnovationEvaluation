#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证SmartReferenceExtractor在主提取流程中的集成效果
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.thesis_inno_eval.extract_sections_with_ai import ThesisExtractorWithAI
from src.thesis_inno_eval.utils import extract_text_from_word

def main():
    print("============================================================")
    print("验证SmartReferenceExtractor在主提取流程中的集成效果")
    print("============================================================")
    
    # 初始化提取器
    print("🔧 初始化提取器...")
    extractor = ThesisExtractorWithAI()
    
    # 读取Word文档
    file_path = "data/input/1_音乐_20172001013韩柠灿（硕士毕业论文）.docx"
    print(f"📄 读取Word文档: {file_path}")
    
    try:
        text = extract_text_from_word(file_path)
        print(f"   ✅ 文档读取成功，总长度: {len(text):,} 字符")
    except Exception as e:
        print(f"   ❌ 文档读取失败: {e}")
        return
    
    # 只测试参考文献提取部分
    print("\n🔍 测试参考文献提取功能...")
    
    try:
        # 调用内部的参考文献提取方法
        print("   📚 开始智能参考文献提取...")
        references = extractor._extract_references_enhanced_disciplinary(text, "音乐")
        
        print(f"\n📊 参考文献提取结果:")
        print(f"   📋 提取数量: {len(references)} 条")
        
        if references:
            print(f"\n📝 前10条参考文献预览:")
            for i, ref in enumerate(references[:10], 1):
                print(f"{i:2d}. {ref[:100]}{'...' if len(ref) > 100 else ''}")
            
            if len(references) > 10:
                print(f"... 省略 {len(references) - 10} 条 ...")
        else:
            print("   ⚠️ 未提取到参考文献")
            
        # 测试是否使用了SmartReferenceExtractor
        if hasattr(extractor, 'smart_ref_extractor'):
            print(f"\n✅ SmartReferenceExtractor 已正确集成")
        else:
            print(f"\n❌ SmartReferenceExtractor 未集成")
            
        print(f"\n✅ 验证完成!")
        
    except Exception as e:
        print(f"   ❌ 参考文献提取失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
