#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试计算机应用技术和中国少数民族语言文学论文的目录提取
"""

import sys
import os
sys.path.append(str(PROJECT_ROOT))

from src.thesis_inno_eval.ai_toc_extractor import AITocExtractor

def test_thesis_extraction(doc_path, thesis_type):
    """测试论文目录提取的通用函数"""
    print(f"📚 测试{thesis_type}学位论文目录提取")
    print(f"📁 文件: {os.path.basename(doc_path)}")
    print("=" * 80)
    
    try:
        print("🔄 开始提取目录...")
        extractor = AITocExtractor()
        result = extractor.extract_toc(doc_path)
        
        if result and result.entries:
            print(f"\n📊 总提取条目: {len(result.entries)}个")
            print(f"🎯 整体置信度: {result.confidence_score:.2f}")
            
            # 显示所有条目
            print(f"\n📋 完整目录条目列表:")
            print("-" * 80)
            
            for i, entry in enumerate(result.entries, 1):
                type_label = f"【{entry.section_type}】" if entry.section_type else "【unknown】"
                page_info = f"页码: {entry.page}" if entry.page else "页码: None"
                
                print(f"{i:2d}. {type_label} {entry.title}")
                print(f"     {page_info} | 级别: {entry.level}")
            
            # 检查参考文献后章节
            ref_found = False
            ref_index = -1
            for i, entry in enumerate(result.entries):
                if entry.section_type == 'references' or '参考文献' in entry.title:
                    ref_found = True
                    ref_index = i
                    break
            
            print(f"\n🔍 参考文献后章节检查:")
            print("-" * 50)
            
            if ref_found:
                print(f" 找到参考文献: {result.entries[ref_index].title} (页码: {result.entries[ref_index].page})")
                
                post_ref_sections = result.entries[ref_index + 1:]
                if post_ref_sections:
                    print(f"\n📖 参考文献后章节 ({len(post_ref_sections)}个):")
                    for i, section in enumerate(post_ref_sections, 1):
                        print(f"   {i}. {section.title} (页码: {section.page}, 类型: {section.section_type})")
                else:
                    print("❌ 没有找到参考文献后的章节")
            else:
                print("❌ 没有找到参考文献章节")
            
            # 检查是否包含常见的学术后章节
            academic_sections = [
                "致谢", "谢辞", "acknowledgment", "acknowledgments",
                "个人简历", "简历", "resume", "curriculum vitae",
                "攻读", "学术成果", "发表论文", "研究成果",
                "附录", "appendix", "后记", "epilogue"
            ]
            
            print(f"\n🎯 学术后章节检查:")
            print("-" * 50)
            
            found_academic = []
            for entry in result.entries:
                for academic in academic_sections:
                    if academic.lower() in entry.title.lower():
                        found_academic.append(entry)
                        print(f" 找到: {entry.title} (页码: {entry.page}, 类型: {entry.section_type})")
                        break
            
            if not found_academic:
                print("❌ 没有找到常见的学术后章节")
                
        else:
            print("❌ 提取失败或结果为空")
            
    except Exception as e:
        print(f"❌ 提取过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    # 测试计算机应用技术论文
    computer_doc = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    test_thesis_extraction(computer_doc, "计算机应用技术")
    
    print("\n" + "="*100 + "\n")
    
    # 测试中国少数民族语言文学论文
    minority_doc = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_18210104022_公太加_中国少数民族语言文学_藏族民间长歌研究.docx"
    test_thesis_extraction(minority_doc, "中国少数民族语言文学")

if __name__ == "__main__":
    main()
