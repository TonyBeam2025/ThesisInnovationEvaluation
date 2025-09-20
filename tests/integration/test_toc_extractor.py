#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试AI智能目录抽取器
使用data/input文件夹中的Word文档进行测试
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_word_documents():
    """测试Word文档目录抽取"""
    
    # 创建抽取器实例
    extractor = AITocExtractor()
    
    # 检查测试目录
    input_dir = Path("data/input")
    if not input_dir.exists():
        logger.error(f"测试目录不存在: {input_dir}")
        logger.info("请将Word文档放在 data/input 目录中")
        return
    
    # 查找Word文档，排除临时文件
    all_files = list(input_dir.glob("*.docx"))
    word_files = [f for f in all_files if not f.name.startswith("~$")]
    
    if not word_files:
        logger.warning(f"在 {input_dir} 中未找到Word文档（.docx格式）")
        return
    
    logger.info(f"找到 {len(word_files)} 个Word文档（已排除 {len(all_files) - len(word_files)} 个临时文件）")
    
    # 处理每个Word文档
    for word_file in word_files:
        logger.info(f"开始处理: {word_file.name}")
        
        try:
            # 抽取目录
            toc = extractor.extract_toc(str(word_file))
            
            # 保存结构化JSON
            output_file = f"{word_file.stem}_toc_structured.json"
            toc_json = extractor.save_toc_json(toc, output_file)
            
            # 打印结果摘要
            print(f"\n{'='*60}")
            print(f"文档: {word_file.name}")
            print(f"{'='*60}")
            print(f"论文标题: {toc.title or '未识别'}")
            print(f"作者: {toc.author or '未识别'}")
            print(f"总条目数: {toc.total_entries}")
            print(f"最大层级: {toc.max_level}")
            print(f"抽取方法: {toc.extraction_method}")
            print(f"置信度: {toc.confidence_score:.2f}")
            print(f"输出文件: {output_file}")
            
            # 显示前10个目录条目
            if toc.entries:
                print(f"\n目录结构预览（前10条）:")
                for i, entry in enumerate(toc.entries[:10]):
                    indent = "  " * (entry.level - 1) if entry.level > 0 else ""
                    page_info = f" (第{entry.page}页)" if entry.page else ""
                    print(f"   {i+1:2d}. {indent}{entry.number} {entry.title}{page_info}")
                
                if len(toc.entries) > 10:
                    print(f"   ... 还有 {len(toc.entries) - 10} 个条目")
            
            # 分析质量
            quality_analysis = analyze_extraction_quality(toc)
            print(f"\n质量分析:")
            for key, value in quality_analysis.items():
                print(f"   {key}: {value}")
            
        except Exception as e:
            logger.error(f"处理 {word_file.name} 失败: {e}")
            print(f"\n处理失败: {word_file.name}")
            print(f"   错误: {e}")

def analyze_extraction_quality(toc):
    """分析抽取质量"""
    analysis = {
        "整体评分": "优秀" if toc.confidence_score >= 0.8 else "良好" if toc.confidence_score >= 0.6 else "需改进",
        "条目完整性": "高" if toc.total_entries >= 10 else "中" if toc.total_entries >= 5 else "低",
        "层级结构": "复杂" if toc.max_level >= 3 else "中等" if toc.max_level >= 2 else "简单",
        "页码识别": f"{sum(1 for e in toc.entries if e.page)}/{toc.total_entries} 条目有页码"
    }
    
    # 检查编号规范性
    numbered_entries = sum(1 for e in toc.entries if e.number)
    analysis["编号规范性"] = f"{numbered_entries}/{toc.total_entries} 条目有编号"
    
    return analysis

def create_test_environment():
    """创建测试环境"""
    input_dir = Path("data/input")
    input_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"测试环境已创建")
    print(f"请将Word文档（.docx格式）放入: {input_dir.absolute()}")
    print(f"然后运行此脚本进行测试")

if __name__ == "__main__":
    print("AI智能论文目录抽取器测试")
    print("=" * 50)
    
    # 检查是否存在测试目录
    input_dir = Path("data/input")
    if not input_dir.exists():
        print("首次运行，创建测试环境...")
        create_test_environment()
        print("\n请将Word文档放入 data/input 目录后重新运行此脚本")
    else:
        test_word_documents()
    
    print("\n测试完成！")
