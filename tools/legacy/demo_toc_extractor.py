#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能目录抽取器使用示例
演示如何使用AITocExtractor抽取不同格式论文的目录
"""

import sys
import os
from pathlib import Path

# 添加src路径到系统路径
sys.path.append(str(Path(__file__).parent / "src"))

from thesis_toc_extractor import AITocExtractor

def demo_usage():
    """演示AI目录抽取器的使用方法"""
    
    print("🚀 AI智能学位论文目录抽取器演示\n")
    
    # 创建抽取器实例
    extractor = AITocExtractor()
    
    # 测试文件列表
    test_files = [
        "cache/documents/51177_b6ac1c475108811bd4a31a6ebcd397df.md",
        # 可以添加更多测试文件
        # "path/to/your/thesis.docx",
        # "path/to/your/thesis.md"
    ]
    
    for file_path in test_files:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"⚠️ 文件不存在，跳过: {file_path}")
            continue
        
        print(f"📄 正在处理: {file_path.name}")
        print("=" * 60)
        
        try:
            # 抽取目录
            toc = extractor.extract_toc(str(file_path))
            
            # 显示抽取结果
            extractor.print_toc(toc)
            
            # 保存到多种格式
            output_base = file_path.stem + "_extracted_toc"
            
            # JSON格式 - 适合程序处理
            json_file = f"{output_base}.json"
            extractor.save_toc(toc, json_file, 'json')
            print(f" JSON格式已保存: {json_file}")
            
            # Markdown格式 - 适合阅读和展示
            md_file = f"{output_base}.md"
            extractor.save_toc(toc, md_file, 'markdown')
            print(f" Markdown格式已保存: {md_file}")
            
            # 文本格式 - 适合简单查看
            txt_file = f"{output_base}.txt"
            extractor.save_toc(toc, txt_file, 'txt')
            print(f" 文本格式已保存: {txt_file}")
            
            # 统计信息
            print(f"\n📊 抽取统计:")
            print(f"   - 总条目数: {toc.total_entries}")
            print(f"   - 最大层级: {toc.max_level}")
            print(f"   - 置信度: {toc.confidence_score:.2f}")
            
            # 各层级统计
            level_stats = {}
            for entry in toc.entries:
                level_stats[entry.level] = level_stats.get(entry.level, 0) + 1
            
            print(f"   - 层级分布:")
            for level in sorted(level_stats.keys()):
                print(f"     第{level}级: {level_stats[level]}个")
            
            print("\n" + "="*60 + "\n")
            
        except Exception as e:
            print(f"❌ 抽取失败: {e}")
            print("\n" + "="*60 + "\n")

def analyze_extraction_quality():
    """分析抽取质量"""
    
    print("🔍 AI抽取质量分析\n")
    
    extractor = AITocExtractor()
    test_file = "cache/documents/51177_b6ac1c475108811bd4a31a6ebcd397df.md"
    
    if not Path(test_file).exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    toc = extractor.extract_toc(test_file)
    
    print("📋 质量分析报告:")
    print("-" * 40)
    
    # 1. 置信度分析
    high_conf = [e for e in toc.entries if e.confidence >= 0.9]
    medium_conf = [e for e in toc.entries if 0.7 <= e.confidence < 0.9]
    low_conf = [e for e in toc.entries if e.confidence < 0.7]
    
    print(f"🎯 置信度分布:")
    print(f"   高置信度 (≥0.9): {len(high_conf)} 个 ({len(high_conf)/len(toc.entries)*100:.1f}%)")
    print(f"   中置信度 (0.7-0.9): {len(medium_conf)} 个 ({len(medium_conf)/len(toc.entries)*100:.1f}%)")
    print(f"   低置信度 (<0.7): {len(low_conf)} 个 ({len(low_conf)/len(toc.entries)*100:.1f}%)")
    
    # 2. 章节结构分析
    print(f"\n📚 章节结构分析:")
    main_chapters = [e for e in toc.entries if e.level == 1]
    print(f"   主章节数: {len(main_chapters)}")
    
    for chapter in main_chapters[:5]:  # 显示前5个主章节
        sub_count = len([e for e in toc.entries if e.number.startswith(chapter.number.replace('第', '').replace('章', '')) and e.level > 1])
        print(f"   - {chapter.number} {chapter.title}: {sub_count} 个子章节")
    
    # 3. 问题识别
    print(f"\n⚠️ 潜在问题:")
    issues = []
    
    # 检查缺失标题
    missing_titles = [e for e in toc.entries if not e.title.strip()]
    if missing_titles:
        issues.append(f"缺失标题: {len(missing_titles)} 个")
    
    # 检查异常编号
    unusual_numbers = [e for e in toc.entries if e.number and not any(c.isdigit() for c in e.number)]
    if unusual_numbers:
        issues.append(f"异常编号: {len(unusual_numbers)} 个")
    
    if issues:
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"    未发现明显问题")
    
    print(f"\n📈 总体评价: {'优秀' if toc.confidence_score >= 0.85 else '良好' if toc.confidence_score >= 0.7 else '需要改进'}")

def main():
    """主函数"""
    
    print("🎓 AI智能学位论文目录抽取器")
    print("=" * 50)
    print("功能特点:")
    print("• 支持Word文档(.docx)和Markdown文档(.md)")
    print("• AI智能识别复杂的章节结构")
    print("• 多种输出格式(JSON/Markdown/Text)")
    print("• 置信度评估和质量分析")
    print("• 支持中英文混合目录")
    print("=" * 50)
    print()
    
    # 演示使用
    demo_usage()
    
    # 质量分析
    analyze_extraction_quality()
    
    print("🎉 演示完成！")
    print("\n💡 使用提示:")
    print("1. 将你的论文文件放入适当目录")
    print("2. 修改test_files列表中的文件路径")
    print("3. 运行程序自动抽取目录")
    print("4. 查看生成的JSON/Markdown/Text文件")

if __name__ == "__main__":
    main()

