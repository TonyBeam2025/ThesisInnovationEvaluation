#!/usr/bin/env python3
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
        print(f"\n📁 即将清理的文件:")
        total_size = 0
        for md_file in to_remove:
            size = md_file.stat().st_size
            total_size += size
            print(f"   {md_file.name} ({size/1024:.1f} KB)")
        
        print(f"\n📊 清理效果:")
        print(f"   节省空间: {total_size/1024:.1f} KB")
        
        # 执行清理
        try:
            for md_file in to_remove:
                md_file.unlink()
            print(f"\n 成功清理 {len(to_remove)} 个中间文件")
        except Exception as e:
            print(f"\n❌ 清理失败: {e}")
    else:
        print("\n💡 没有需要清理的中间文件")
    
    if to_keep:
        print(f"\n📋 保留的重要文件:")
        for md_file in to_keep:
            print(f"    {md_file.name}")

if __name__ == "__main__":
    cleanup_intermediate_markdown()

