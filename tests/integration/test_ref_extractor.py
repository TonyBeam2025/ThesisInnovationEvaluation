#!/usr/bin/env python3
"""
测试SmartReferenceExtractor的参考文献提取功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append('./src')

import thesis_inno_eval.smart_reference_extractor as sre_module
from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word

def test_reference_extraction():
    """测试参考文献提取"""
    
    # 读取Word文档
    print("📄 读取Word文档...")
    # docx_path = "./data/input/1_音乐_20172001013韩柠灿（硕士毕业论文）.docx"
    docx_path = "./data/input/1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    if not os.path.exists(docx_path):
        print(f"❌ 文件不存在: {docx_path}")
        return
    
    text = extract_text_from_word(docx_path)
    print(f"   ✅ 文档读取成功，总长度: {len(text):,} 字符")
    
    # 初始化智能参考文献提取器
    print("🤖 初始化SmartReferenceExtractor...")
    extractor = sre_module.SmartReferenceExtractor(ai_client=None)  # 专门测试docx，不需要AI
    
    # 执行参考文献提取
    print("🔍 开始提取参考文献...")
    references, stats = extractor.extract_references(
        text, 
        source_format='docx',  # 明确指定docx格式
        source_path=docx_path
    )
    
    # 调试：检查参考文献区域内容
    print("\n🔍 调试信息 - 检查参考文献区域内容:")
    if hasattr(extractor, '_last_ref_section'):
        ref_section = extractor._last_ref_section
        print(f"参考文献区域长度: {len(ref_section)}")
        print("参考文献区域开头500字符:")
        print(ref_section[:500])
        print("\n参考文献区域结尾500字符:")
        print(ref_section[-500:] if len(ref_section) > 500 else ref_section)
    else:
        print("⚠️ 无法获取参考文献区域内容进行调试")
    
    # 输出结果
    print("\n" + "="*60)
    print("📊 参考文献提取结果")
    print("="*60)
    print(f"📋 提取方法: {stats.get('method_used', 'unknown')}")
    print(f"📊 参考文献数量: {len(references)}")
    print(f"⏱️ 处理时间: {stats.get('processing_time', 0):.2f}秒")
    print(f"✅ 提取状态: {'成功' if stats.get('success', False) else '失败'}")
    
    if references:
        print(f"\n📝 前10条参考文献预览:")
        for i, ref in enumerate(references[:10], 1):
            print(f"{i:2d}. {ref[:80]}{'...' if len(ref) > 80 else ''}")
        
        if len(references) > 10:
            print(f"... 省略 {len(references) - 10} 条 ...")
    else:
        print("❌ 未提取到任何参考文献")
    
    print("\n" + "="*60)
    
    return references, stats

if __name__ == "__main__":
    test_reference_extraction()
