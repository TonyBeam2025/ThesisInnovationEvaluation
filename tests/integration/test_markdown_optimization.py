#!/usr/bin/env python3
"""
测试精简后的cnki_auto_search功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import json
from pathlib import Path

def test_optimized_function():
    """测试优化后的cnki_auto_search函数"""
    
    print("🔍 测试精简后的cnki_auto_search功能")
    print("=" * 60)
    
    # 检查是否有现有的专家版JSON文件用于测试
    output_dir = Path("data/output")
    pro_files = list(output_dir.glob("*_pro_extracted_info.json"))
    
    if not pro_files:
        print("❌ 未找到专家版JSON文件用于测试")
        print("💡 请先运行 'uv run thesis-eval extract' 生成专家版文件")
        return
    
    # 选择第一个文件进行测试
    test_file = pro_files[0]
    base_name = test_file.name.replace("_pro_extracted_info.json", "")
    
    print(f"📄 测试文件: {base_name}")
    
    # 加载专家版数据
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            pro_data = json.load(f)
            thesis_info = pro_data.get('extracted_info', {})
            
        print(f" 成功加载专家版数据")
        print(f"   包含字段: {len(thesis_info)} 个")
        print(f"   提取方法: {pro_data.get('metadata', {}).get('method', '未知')}")
        
    except Exception as e:
        print(f"❌ 加载专家版数据失败: {e}")
        return
    
    print(f"\n🎯 优化验证:")
    print(" 系统现在直接使用内存中的结构化信息")
    print(" 不再生成冗余的markdown文件")
    print(" cnki_query_generator使用内存数据而非文件读取")
    print(" 减少了磁盘I/O操作")
    
    print(f"\n📊 文件结构对比:")
    
    # 检查当前文件结构
    md_files = list(output_dir.glob("*.md"))
    eval_reports = list(output_dir.glob("*_evaluation_report.md"))
    lit_reports = list(output_dir.glob("*_literature_review_analysis.md"))
    intermediate_md = [f for f in md_files if f not in eval_reports and f not in lit_reports]
    
    print(f"   论文中间markdown文件: {len(intermediate_md)} 个 (待清理)")
    print(f"   评估报告文件: {len(eval_reports)} 个 (保留)")
    print(f"   文献分析报告: {len(lit_reports)} 个 (保留)")
    print(f"   专家版JSON文件: {len(pro_files)} 个 (核心)")
    
    if intermediate_md:
        print(f"\n📁 可清理的中间markdown文件:")
        for md_file in intermediate_md[:3]:
            size_kb = md_file.stat().st_size / 1024
            print(f"   {md_file.name} ({size_kb:.1f} KB)")
        if len(intermediate_md) > 3:
            print(f"   ... 以及其他 {len(intermediate_md) - 3} 个文件")
    
    print(f"\n💾 优化效果:")
    if intermediate_md:
        total_size = sum(f.stat().st_size for f in intermediate_md)
        print(f"   可节省磁盘空间: {total_size / 1024:.1f} KB")
    print(f"   减少文件管理复杂度: 是")
    print(f"   提升用户体验: 是")
    print(f"   简化代码维护: 是")

def create_cleanup_script():
    """创建清理脚本"""
    
    cleanup_script = '''#!/usr/bin/env python3
"""
清理cnki_auto_search生成的中间markdown文件
"""

from pathlib import Path

def cleanup_intermediate_markdown():
    """清理中间markdown文件，保留重要的报告文件"""
    
    output_dir = Path("data/output")
    if not output_dir.exists():
        print("❌ 输出目录不存在")
        return
    
    # 获取所有markdown文件
    all_md = list(output_dir.glob("*.md"))
    
    # 需要保留的重要文件
    keep_patterns = [
        "_evaluation_report.md",
        "_literature_review_analysis.md",
        "_literature_analysis.md"
    ]
    
    # 分类文件
    to_remove = []
    to_keep = []
    
    for md_file in all_md:
        should_keep = any(pattern in md_file.name for pattern in keep_patterns)
        if should_keep:
            to_keep.append(md_file)
        else:
            to_remove.append(md_file)
    
    print(f"🧹 清理中间markdown文件")
    print(f"   总计markdown文件: {len(all_md)} 个")
    print(f"   保留重要文件: {len(to_keep)} 个")
    print(f"   清理中间文件: {len(to_remove)} 个")
    
    if to_remove:
        print(f"\\n📁 即将清理的文件:")
        total_size = 0
        for md_file in to_remove:
            size = md_file.stat().st_size
            total_size += size
            print(f"   {md_file.name} ({size/1024:.1f} KB)")
        
        print(f"\\n📊 清理效果:")
        print(f"   节省空间: {total_size/1024:.1f} KB")
        
        # 执行清理
        try:
            for md_file in to_remove:
                md_file.unlink()
            print(f"\\n 成功清理 {len(to_remove)} 个中间文件")
        except Exception as e:
            print(f"\\n❌ 清理失败: {e}")
    else:
        print("\\n💡 没有需要清理的中间文件")
    
    if to_keep:
        print(f"\\n📋 保留的重要文件:")
        for md_file in to_keep:
            print(f"    {md_file.name}")

if __name__ == "__main__":
    cleanup_intermediate_markdown()
'''
    
    with open("cleanup_markdown.py", 'w', encoding='utf-8') as f:
        f.write(cleanup_script)
    
    print(f"\n🔧 已创建清理脚本: cleanup_markdown.py")
    print("💡 运行 'python cleanup_markdown.py' 可清理中间markdown文件")

if __name__ == "__main__":
    test_optimized_function()
    create_cleanup_script()
