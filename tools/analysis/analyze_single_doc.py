#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单个Word文档目录深度分析测试
"""

import sys
import os
import json
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_single_document(file_path: str):
    """深度分析单个Word文档"""
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    print(f"🔍 开始分析文档: {file_path_obj.name}")
    print("=" * 80)
    
    # 创建抽取器
    extractor = AITocExtractor()
    
    try:
        # 抽取目录
        toc = extractor.extract_toc(str(file_path_obj))
        
        # 基本信息
        print(f"📋 论文标题: {toc.title or '未识别'}")
        print(f"👤 作者: {toc.author or '未识别'}")
        print(f"📊 总条目数: {toc.total_entries}")
        print(f"📈 最大层级: {toc.max_level}")
        print(f"🔍 抽取方法: {toc.extraction_method}")
        print(f"⭐ 整体置信度: {toc.confidence_score:.3f}")
        
        # 层级统计
        print(f"\n📊 层级统计:")
        level_stats = {}
        for entry in toc.entries:
            level = entry.level
            if level not in level_stats:
                level_stats[level] = 0
            level_stats[level] += 1
        
        for level in sorted(level_stats.keys()):
            print(f"   第{level}级: {level_stats[level]} 个条目")
        
        # 页码统计
        with_page = sum(1 for e in toc.entries if e.page)
        print(f"\n📄 页码信息:")
        print(f"   有页码的条目: {with_page}/{toc.total_entries} ({with_page/toc.total_entries*100:.1f}%)")
        
        if with_page > 0:
            pages = [e.page for e in toc.entries if e.page]
            print(f"   页码范围: {min(pages)} - {max(pages)}")
        
        # 编号统计
        with_number = sum(1 for e in toc.entries if e.number)
        print(f"\n🔢 编号信息:")
        print(f"   有编号的条目: {with_number}/{toc.total_entries} ({with_number/toc.total_entries*100:.1f}%)")
        
        # 置信度分析
        print(f"\n⭐ 置信度分析:")
        high_conf = sum(1 for e in toc.entries if e.confidence >= 0.9)
        med_conf = sum(1 for e in toc.entries if 0.7 <= e.confidence < 0.9)
        low_conf = sum(1 for e in toc.entries if e.confidence < 0.7)
        
        print(f"   高置信度 (≥0.9): {high_conf} 个条目")
        print(f"   中置信度 (0.7-0.9): {med_conf} 个条目")
        print(f"   低置信度 (<0.7): {low_conf} 个条目")
        
        # 详细目录结构
        print(f"\n📖 完整目录结构:")
        print("-" * 80)
        for i, entry in enumerate(toc.entries):
            indent = "  " * (entry.level - 1) if entry.level > 0 else ""
            page_info = f" (第{entry.page}页)" if entry.page else ""
            conf_info = f" [{entry.confidence:.2f}]"
            number_part = f"{entry.number} " if entry.number else ""
            
            print(f"{i+1:3d}. {indent}{number_part}{entry.title}{page_info}{conf_info}")
        
        # 保存详细JSON
        output_file = f"{file_path_obj.stem}_detailed_analysis.json"
        toc_json = extractor.save_toc_json(toc, output_file)
        
        print(f"\n💾 详细分析已保存到: {output_file}")
        
        # 质量评估
        quality_score = assess_quality(toc)
        print(f"\n🎯 质量评估: {quality_score}/100")
        
        return toc
        
    except Exception as e:
        logger.error(f"分析失败: {e}")
        print(f"❌ 分析失败: {e}")
        return None

def assess_quality(toc) -> int:
    """评估目录质量，返回0-100的分数"""
    score = 0
    
    # 基础分数：有目录条目就给30分
    if toc.total_entries > 0:
        score += 30
    
    # 条目数量评分 (0-20分)
    if toc.total_entries >= 20:
        score += 20
    elif toc.total_entries >= 10:
        score += 15
    elif toc.total_entries >= 5:
        score += 10
    
    # 层级结构评分 (0-15分)
    if toc.max_level >= 3:
        score += 15
    elif toc.max_level >= 2:
        score += 10
    elif toc.max_level >= 1:
        score += 5
    
    # 编号规范性评分 (0-15分)
    with_number = sum(1 for e in toc.entries if e.number)
    number_ratio = with_number / toc.total_entries if toc.total_entries > 0 else 0
    score += int(number_ratio * 15)
    
    # 页码完整性评分 (0-10分)
    with_page = sum(1 for e in toc.entries if e.page)
    page_ratio = with_page / toc.total_entries if toc.total_entries > 0 else 0
    score += int(page_ratio * 10)
    
    # 置信度评分 (0-10分)
    score += int(toc.confidence_score * 10)
    
    return min(score, 100)

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python analyze_single_doc.py <文档路径>")
        print("示例: python analyze_single_doc.py data/input/51177.docx")
        return
    
    file_path = sys.argv[1]
    analyze_single_document(file_path)

if __name__ == "__main__":
    main()
