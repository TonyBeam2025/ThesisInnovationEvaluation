#!/usr/bin/env python3
"""
测试增强的TOC提取功能
包括Word字段、样式和传统边界提取方法
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_enhanced_toc_extraction():
    """测试增强的TOC提取功能"""
    
    # 测试文件路径
    test_files = [
        "data/input/1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx",  # 藏文文本分类论文
        "data/input/51177.docx"  # 另一个论文文件
    ]
    
    extractor = AITocExtractor()
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"⚠️  文件不存在: {file_path}")
            continue
            
        print(f"\n{'='*60}")
        print(f"📄 测试文件: {file_path}")
        print(f"{'='*60}")
        
        try:
            # 测试增强提取
            result = extractor.extract_toc(file_path)
            
            if result and result.toc_content:
                print(f" 成功提取目录内容:")
                print(f"📋 目录条目数量: {len(result.entries)}")
                print(f"📄 论文标题: {result.title}")
                print(f"👤 作者: {result.author}")
                print(f"\n🔍 目录内容预览:")
                print("-" * 40)
                
                # 显示前10行目录内容
                toc_lines = result.toc_content.split('\n')
                for i, line in enumerate(toc_lines[:10]):
                    if line.strip():
                        print(f"{i+1:2d}. {line}")
                
                if len(toc_lines) > 10:
                    print(f"... (还有 {len(toc_lines)-10} 行)")
                
                print(f"\n📊 结构化目录条目:")
                print("-" * 40)
                for i, entry in enumerate(result.entries[:5]):
                    print(f"{i+1:2d}. [{entry.level}] {entry.title} - 页码: {entry.page}")
                
                if len(result.entries) > 5:
                    print(f"... (还有 {len(result.entries)-5} 个条目)")
                    
            else:
                print(f"❌ 提取失败或未找到目录内容")
                
        except Exception as e:
            print(f"❌ 处理文件时出错: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始测试增强的TOC提取功能...")
    test_enhanced_toc_extraction()
    print("\n 测试完成!")
