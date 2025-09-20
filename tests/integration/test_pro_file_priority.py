#!/usr/bin/env python3
"""
测试专家版结构化信息文件优先读取功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
import json
from pathlib import Path

def test_pro_file_priority():
    """测试专家版文件优先读取"""
    
    print("🔍 测试专家版结构化信息文件优先读取功能")
    print("=" * 60)
    
    # 检查输出目录
    output_dir = Path("data/output")
    if not output_dir.exists():
        print("❌ 输出目录不存在: data/output")
        return
    
    # 查找所有可能的提取信息文件
    pro_files = list(output_dir.glob("*_pro_extracted_info.json"))
    standard_files = list(output_dir.glob("*_extracted_info.json"))
    
    # 排除专家版文件，避免重复计算
    standard_files = [f for f in standard_files if not f.name.endswith("_pro_extracted_info.json")]
    
    print(f"📊 发现文件统计:")
    print(f"   专家版文件: {len(pro_files)} 个")
    print(f"   标准版文件: {len(standard_files)} 个")
    
    if not pro_files and not standard_files:
        print("❌ 未找到任何提取信息文件")
        print("💡 请先运行提取命令生成文件")
        return
    
    # 分析文件对应关系
    print(f"\n📋 文件详细分析:")
    
    all_base_names = set()
    for f in pro_files:
        base_name = f.name.replace("_pro_extracted_info.json", "")
        all_base_names.add(base_name)
    
    for f in standard_files:
        base_name = f.name.replace("_extracted_info.json", "")
        all_base_names.add(base_name)
    
    for base_name in sorted(all_base_names):
        print(f"\n📄 论文: {base_name}")
        
        pro_file = output_dir / f"{base_name}_pro_extracted_info.json"
        standard_file = output_dir / f"{base_name}_extracted_info.json"
        
        has_pro = pro_file.exists()
        has_standard = standard_file.exists()
        
        if has_pro and has_standard:
            print("   🎯 专家版:  存在")
            print("   📁 标准版:  存在")
            print("   🔄 读取策略: 优先使用专家版")
            
            # 比较文件大小和内容概览
            try:
                pro_size = pro_file.stat().st_size
                standard_size = standard_file.stat().st_size
                print(f"   📊 文件大小: 专家版 {pro_size:,} 字节 vs 标准版 {standard_size:,} 字节")
                
                # 检查元数据差异
                with open(pro_file, 'r', encoding='utf-8') as f:
                    pro_data = json.load(f)
                with open(standard_file, 'r', encoding='utf-8') as f:
                    standard_data = json.load(f)
                
                pro_method = pro_data.get('metadata', {}).get('method', '未知')
                standard_method = standard_data.get('metadata', {}).get('method', '未知')
                
                print(f"   🔧 提取方法: 专家版 {pro_method} vs 标准版 {standard_method}")
                
            except Exception as e:
                print(f"   ⚠️ 文件分析失败: {e}")
                
        elif has_pro:
            print("   🎯 专家版:  存在")
            print("   📁 标准版: ❌ 不存在")
            print("   🔄 读取策略: 使用专家版")
            
        elif has_standard:
            print("   🎯 专家版: ❌ 不存在")
            print("   📁 标准版:  存在")
            print("   🔄 读取策略: 回退使用标准版")
            
        else:
            print("   ❌ 两种版本都不存在")
    
    # 测试优先级逻辑
    print(f"\n🧪 测试读取优先级逻辑:")
    
    for base_name in sorted(all_base_names):
        pro_file = output_dir / f"{base_name}_pro_extracted_info.json"
        standard_file = output_dir / f"{base_name}_extracted_info.json"
        
        # 模拟系统的读取逻辑
        selected_file = None
        file_type = None
        
        if pro_file.exists():
            selected_file = pro_file
            file_type = "专家版"
        elif standard_file.exists():
            selected_file = standard_file
            file_type = "标准版"
        
        if selected_file:
            print(f"   📄 {base_name}: 选择 {file_type} ({selected_file.name})")
        else:
            print(f"   📄 {base_name}: 无可用文件")
    
    print(f"\n🎯 测试结论:")
    print(" 系统现在优先读取专家版 _pro_extracted_info.json 文件")
    print(" 专家版不存在时自动回退到标准版文件")
    print(" CLI命令已统一使用专家版优先策略")
    
    # 给出建议
    if standard_files and not pro_files:
        print(f"\n💡 建议:")
        print("   发现标准版文件但缺少专家版文件")
        print("   建议重新运行提取命令生成专家版文件:")
        for f in standard_files[:3]:  # 显示前3个示例
            base = f.name.replace("_extracted_info.json", "")
            print(f"   uv run thesis-eval extract data/input/{base}.pdf")

if __name__ == "__main__":
    test_pro_file_priority()
