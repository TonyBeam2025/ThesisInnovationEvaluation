#!/usr/bin/env python3
"""
检查计算机应用技术论文的语言内容
验证中文检测功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor, detect_non_chinese_content
import docx
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def analyze_chinese_content(file_path):
    """分析文档中文内容"""
    print(f"分析文件: {file_path}")
    
    # 读取文档内容
    try:
        doc = docx.Document(file_path)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
            
        print(f"文档总字符数: {len(content)}")
        
        # 检查中文字符
        chinese_chars = 0
        for char in content:
            if '\u4e00' <= char <= '\u9fff':
                chinese_chars += 1
        
        chinese_ratio = chinese_chars / len(content) if len(content) > 0 else 0
        print(f"中文字符数: {chinese_chars}")
        print(f"中文比例: {chinese_ratio:.2%}")
        
        # 显示前500字符
        print(f"\n前500字符内容:")
        print("-" * 50)
        print(content[:500])
        print("-" * 50)
        
        # 使用提取器的中文检测方法
        try:
            is_non_chinese, detected_lang = detect_non_chinese_content(content)
            print(f"\n中文检测结果: {'未通过' if is_non_chinese else '通过'}")
            print(f"检测到的语言: {detected_lang}")
        except Exception as e:
            print(f"\n中文检测错误: {e}")
            
    except Exception as e:
        print(f"读取文档失败: {e}")

if __name__ == "__main__":
    # 分析计算机应用技术论文
    analyze_chinese_content("data/input/1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx")
