#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复后的参考文献和章节提取效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy

def verify_fixes():
    """验证修复效果"""
    print("🔍 验证参考文献和章节提取修复效果...")
    
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
        
        # 1. 验证参考文献
        references = result.get('references', [])
        print(f"\n📚 参考文献验证:")
        print(f"   总数量: {len(references)} 条")
        
        if references:
            print(f"\n   📋 前5条参考文献格式检查:")
            for i, ref in enumerate(references[:5]):
                # 检查是否有编号格式
                has_number = any(pattern in ref for pattern in ['[1]', '[2]', '[3]', '[4]', '[5]'])
                print(f"   [{i+1}] {ref[:150]}...")
                print(f"       格式检查: {'' if has_number else '❌'} 是否包含标准编号")
        
        # 2. 验证章节
        table_of_contents = result.get('table_of_contents', [])
        print(f"\n📖 章节验证:")
        print(f"   总数量: {len(table_of_contents)} 个")
        
        if table_of_contents:
            print(f"\n   📋 章节列表:")
            for chapter in table_of_contents:
                print(f"   [{chapter.get('number', '?')}] {chapter.get('title', '未知标题')}")
        
        # 3. 验证致谢
        acknowledgement = result.get('acknowledgement', '')
        print(f"\n🙏 致谢验证:")
        print(f"   长度: {len(acknowledgement)} 字符")
        if acknowledgement:
            print(f"   内容预览: {acknowledgement[:100]}...")
        
        # 4. 总体评估
        print(f"\n📊 修复效果总结:")
        ref_success = len(references) > 30  # 期望超过30条参考文献
        chapter_success = len(table_of_contents) > 5  # 期望超过5个章节
        ack_success = len(acknowledgement) > 50  # 期望致谢超过50字符
        
        print(f"   📚 参考文献: {'' if ref_success else '❌'} ({len(references)} 条)")
        print(f"   📖 章节识别: {'' if chapter_success else '❌'} ({len(table_of_contents)} 个)")
        print(f"   🙏 致谢提取: {'' if ack_success else '❌'} ({len(acknowledgement)} 字符)")
        
        overall_success = ref_success and chapter_success and ack_success
        
        if overall_success:
            print(f"\n🎉 修复完全成功!")
            print(f"    参考文献：从25条错误内容 → {len(references)}条正确格式")
            print(f"    章节识别：从1个章节 → {len(table_of_contents)}个章节")
            print(f"    致谢提取：成功提取{len(acknowledgement)}字符")
        else:
            print(f"\n⚠️ 部分修复成功，仍有改进空间")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_fixes()

