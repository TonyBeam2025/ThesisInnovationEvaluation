#!/usr/bin/env python3
"""
测试增强的主提取器 - 验证数字格式章节检测
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
import json
import time
from pathlib import Path

# 添加 src 目录到 Python 路径
src_path = PROJECT_ROOT / "src"
sys.path.insert(0, str(src_path))

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro

def test_enhanced_main_extractor():
    """测试增强的主提取器"""
    
    print("=== 测试增强的主提取器 ===\n")
    
    # 检查MD文档文件
    md_file = r"cache\documents\1_工程力学_21703014_刘力夫_LW_76c5b96231292b26dbeab5065ab7f040.md"
    if not os.path.exists(md_file):
        print(f"❌ MD文档文件不存在: {md_file}")
        return
    
    print(f"📄 读取MD文档: {md_file}")
    
    try:
        # 读取文档
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f" 文档读取成功，长度: {len(text):,} 字符")
        
        # 创建提取器（不使用AI客户端）
        extractor = ThesisExtractorPro()
        
        print("\n🔍 开始章节检测...")
        start_time = time.time()
        
        # 使用新的 _analyze_document_structure 方法
        structure_analysis = extractor._analyze_document_structure(text)
        
        detection_time = time.time() - start_time
        print(f"⏱️ 检测完成，耗时: {detection_time:.2f} 秒")
        
        # 统计结果
        info_sections = {k: v for k, v in structure_analysis.items() if k.endswith('_info')}
        content_sections = {k: v for k, v in structure_analysis.items() if not k.endswith('_info')}
        total_sections = len(content_sections)
        
        print(f"\n📊 检测结果统计:")
        print(f"   总计检测到 {total_sections} 个章节")
        
        # 详细显示每个章节
        print(f"\n📋 详细章节列表:")
        for i, (section_name, section_content) in enumerate(content_sections.items(), 1):
            # 获取对应的信息
            info_key = f"{section_name}_info"
            section_info = info_sections.get(info_key, {})
            
            title = section_info.get('title', '未知标题')
            start_pos = section_info.get('start_position', 0)
            end_pos = section_info.get('end_position', 0)
            length = section_info.get('content_length', len(section_content) if isinstance(section_content, str) else 0)
            confidence = section_info.get('boundary_confidence', 0.0)
            
            print(f"   {i:2d}. {section_name:<15} | {title:<25} | 位置: {start_pos:6d}-{end_pos:6d} | 长度: {length:5d} | 置信度: {confidence:.2f}")
        
        # 检查是否检测到数字格式章节
        numeric_chapters = [name for name in content_sections.keys() if name.startswith('chapter_')]
        if numeric_chapters:
            print(f"\n 成功检测到数字格式章节: {len(numeric_chapters)} 个")
            for chapter in numeric_chapters:
                info_key = f"{chapter}_info"
                chapter_info = info_sections.get(info_key, {})
                print(f"   - {chapter}: {chapter_info.get('title', '未知标题')}")
        else:
            print(f"\n⚠️ 未检测到数字格式章节")
        
        # 保存结果
        output_file = "enhanced_main_extractor_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure_analysis, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {output_file}")
        
        # 与原始结果对比
        original_file = "pro_extracted_info.json"
        if os.path.exists(original_file):
            print(f"\n🔄 与原始结果对比...")
            with open(original_file, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            original_sections = original_data.get('section_boundaries', {})
            original_count = len(original_sections)
            
            print(f"   原始检测: {original_count} 个章节")
            print(f"   增强检测: {total_sections} 个章节")
            print(f"   改进程度: +{total_sections - original_count} 个章节")
            
            if total_sections > original_count:
                print(f"   🎉 检测能力显著提升！")
            else:
                print(f"   📝 需要进一步优化")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 设置环境
    os.chdir(r"c:\MyProjects\thesis_Inno_Eval")
    
    # 运行测试
    success = test_enhanced_main_extractor()
    
    if success:
        print(f"\n 测试完成")
    else:
        print(f"\n❌ 测试失败")
