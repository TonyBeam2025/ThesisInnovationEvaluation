#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试修改后的AI TOC提取器中文检测功能
"""

import sys
import os
sys.path.append(str(PROJECT_ROOT))

from src.thesis_inno_eval.ai_toc_extractor import AITocExtractor

def test_chinese_only_extraction():
    """测试只支持中文论文的提取功能"""
    print("🧠 测试AI TOC提取器中文检测功能")
    print("=" * 80)
    
    # 测试文件列表
    test_files = [
        {
            "name": "马克思主义哲学论文（中文）",
            "path": r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.docx",
            "expected": "支持"
        },
        {
            "name": "计算机应用技术论文（藏文内容较多）",
            "path": r"c:\MyProjects\thesis_Inno_Eval\data\input\1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx",
            "expected": "可能支持"  # 需要检测实际内容
        },
        {
            "name": "中国少数民族语言文学论文（藏文内容）",
            "path": r"c:\MyProjects\thesis_Inno_Eval\data\input\1_18210104022_公太加_中国少数民族语言文学_藏族民间长歌研究.docx",
            "expected": "不支持"
        }
    ]
    
    extractor = AITocExtractor()
    
    for i, test_file in enumerate(test_files, 1):
        print(f"\n📄 测试 {i}: {test_file['name']}")
        print(f"📁 文件: {os.path.basename(test_file['path'])}")
        print(f"🎯 预期结果: {test_file['expected']}")
        print("-" * 60)
        
        try:
            # 尝试提取目录
            result = extractor.extract_toc(test_file['path'])
            
            # 如果成功提取，说明是中文论文
            print(f" 成功提取目录")
            print(f"📊 提取条目数: {len(result.entries)}")
            print(f"🎯 置信度: {result.confidence_score:.2f}")
            print(f"🔍 检测结果: 中文论文")
            
            # 显示前5个条目
            if result.entries:
                print(f"\n📋 前5个目录条目:")
                for j, entry in enumerate(result.entries[:5], 1):
                    print(f"  {j}. 【{entry.section_type}】{entry.title}")
                    
        except ValueError as e:
            # 捕获语言检测错误
            if "不支持的语言类型" in str(e) or "中文内容不足" in str(e):
                print(f"❌ 拒绝处理: {str(e)}")
                print(f"🔍 检测结果: 非中文论文")
            else:
                print(f"❌ 其他错误: {str(e)}")
                
        except Exception as e:
            print(f"❌ 处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n" + "=" * 80)
    print("🏁 测试完成")

if __name__ == "__main__":
    test_chinese_only_extraction()
