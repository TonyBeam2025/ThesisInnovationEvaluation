#!/usr/bin/env python3
"""
分析cnki_auto_search生成的markdown文件使用情况
"""

import os
from pathlib import Path

def analyze_markdown_usage():
    """分析markdown文件的生成和使用情况"""
    
    print("🔍 分析cnki_auto_search生成的markdown文件使用情况")
    print("=" * 70)
    
    print("📋 现状分析:")
    print("1. cnki_auto_search函数会生成形如 '论文名.md' 的markdown文件")
    print("2. 这些文件包含论文的结构化信息（标题、摘要、关键词等）")
    print("3. 文件生成的目的是为cnki_query_generator提供文本内容")
    print()
    
    print("🎯 发现的问题:")
    print("1. 重复数据存储：")
    print("   - JSON文件已保存完整的结构化信息")
    print("   - Markdown文件只是JSON数据的另一种格式")
    print("   - 存在信息冗余")
    print()
    
    print("2. 性能优化已实现：")
    print("   - 系统已优化为直接使用内存中的结构化信息")
    print("   - cnki_query_generator不再需要读取markdown文件")
    print("   - markdown文件生成变得多余")
    print()
    
    print("3. 文件管理问题：")
    print("   - 增加了输出目录的文件数量")
    print("   - 用户可能会困惑哪些是核心文件")
    print("   - 维护成本增加")
    print()
    
    # 检查实际文件数量
    output_dir = Path("data/output")
    if output_dir.exists():
        md_files = list(output_dir.glob("*.md"))
        json_files = list(output_dir.glob("*_extracted_info.json"))
        pro_json_files = list(output_dir.glob("*_pro_extracted_info.json"))
        
        print(f"📊 当前文件统计:")
        print(f"   Markdown文件: {len(md_files)} 个")
        print(f"   标准版JSON文件: {len(json_files)} 个")
        print(f"   专家版JSON文件: {len(pro_json_files)} 个")
        print()
        
        if md_files:
            print("📁 Markdown文件列表:")
            for md_file in md_files[:5]:  # 显示前5个
                size_kb = md_file.stat().st_size / 1024
                print(f"   {md_file.name} ({size_kb:.1f} KB)")
            if len(md_files) > 5:
                print(f"   ... 以及其他 {len(md_files) - 5} 个文件")
    
    print("\n💡 精简建议:")
    print("1. 移除markdown文件生成：")
    print("   - 删除_generate_markdown_from_existing_info函数调用")
    print("   - 简化cnki_auto_search函数逻辑")
    print("   - 减少不必要的文件I/O操作")
    print()
    
    print("2. 保留的核心文件：")
    print("   - PDF/DOCX原始文件（输入）")
    print("   - _pro_extracted_info.json（专家版结构化信息）")
    print("   - _relevant_papers_*.json（文献检索结果）")
    print("   - _evaluation_report.md（最终评估报告）")
    print()
    
    print("3. 兼容性考虑：")
    print("   - 确保系统完全依赖内存中的结构化信息")
    print("   - 验证所有组件都不依赖markdown文件")
    print("   - 测试精简后的流程是否正常工作")
    print()
    
    print("🚀 优化效果预期:")
    print(" 减少磁盘空间占用")
    print(" 降低文件管理复杂度")
    print(" 提升用户体验（减少混淆文件）")
    print(" 简化代码维护")
    print(" 避免数据同步问题")

def recommend_optimization():
    """给出具体的优化建议"""
    
    print(f"\n🔧 具体实施建议:")
    print("=" * 70)
    
    print("1. 修改cnki_client_pool.py:")
    print("   - 移除所有_generate_markdown_from_existing_info调用")
    print("   - 将output_md_path参数改为可选")
    print("   - 专注于文献检索而非文件生成")
    print()
    
    print("2. 修改CLI接口:")
    print("   - evaluate命令不再生成中间markdown文件")
    print("   - 保持用户接口简洁")
    print("   - 专注于生成最终报告")
    print()
    
    print("3. 清理历史文件:")
    print("   - 提供清理工具移除现有markdown文件")
    print("   - 更新文档说明新的文件结构")
    print("   - 确保向后兼容性")
    print()
    
    print("4. 测试验证:")
    print("   - 完整流程测试（extract -> evaluate）")
    print("   - 确认文献检索功能正常")
    print("   - 验证报告生成质量不受影响")

if __name__ == "__main__":
    analyze_markdown_usage()
    recommend_optimization()

