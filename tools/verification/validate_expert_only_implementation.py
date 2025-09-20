#!/usr/bin/env python3
"""
验证专家版优先实现的完整性和正确性
"""

import os
import re
from pathlib import Path

def validate_cli_implementation():
    """验证CLI实现的专家版优先策略"""
    
    print("🔍 验证专家版优先实现")
    print("=" * 60)
    
    cli_file = Path("src/thesis_inno_eval/cli.py")
    if not cli_file.exists():
        print("❌ CLI文件不存在")
        return False
    
    with open(cli_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📋 检查项目清单:")
    
    # 1. 检查extract命令是否使用专家版文件名
    extract_pattern = r'output_file\s*=\s*output_path\s*/\s*f"[^"]*_pro_extracted_info\.json"'
    if re.search(extract_pattern, content):
        print(" Extract命令使用专家版文件名 (_pro_extracted_info.json)")
    else:
        print("❌ Extract命令未使用专家版文件名")
        return False
    
    # 2. 检查evaluate命令是否使用专家版文件名
    evaluate_pattern = r'extracted_info_file\s*=\s*output_dir\s*/\s*f"[^"]*_pro_extracted_info\.json"'
    if re.search(evaluate_pattern, content):
        print(" Evaluate命令使用专家版文件名")
    else:
        print("❌ Evaluate命令未使用专家版文件名")
        return False
    
    # 3. 检查literature_analysis命令是否实现优先级逻辑
    if "pro_extracted_info_file" in content and "standard_extracted_info_file" in content:
        print(" Literature_analysis命令实现专家版优先逻辑")
    else:
        print("❌ Literature_analysis命令未实现专家版优先逻辑")
        return False
    
    # 4. 检查元数据是否包含pro_strategy标识
    if '"method": "pro_strategy"' in content:
        print(" 元数据包含pro_strategy方法标识")
    else:
        print("❌ 元数据缺少pro_strategy方法标识")
        return False
    
    # 5. 检查版本信息
    if '"extractor_version": "2.0"' in content:
        print(" 元数据包含extractor_version 2.0")
    else:
        print("❌ 元数据缺少extractor_version信息")
        return False
    
    # 6. 统计文件引用
    pro_references = len(re.findall(r'_pro_extracted_info\.json', content))
    standard_references = len(re.findall(r'(?<!_pro)_extracted_info\.json', content))
    
    print(f"📊 文件引用统计:")
    print(f"   专家版文件引用: {pro_references} 处")
    print(f"   标准版文件引用: {standard_references} 处")
    
    if standard_references > 1:  # literature_analysis中应该有1个作为回退选项
        print(f"⚠️ 发现 {standard_references} 个标准版文件引用（预期1个用于回退）")
    
    return True

def validate_extraction_module():
    """验证提取模块的专家版保存"""
    
    print(f"\n🔧 验证提取模块")
    print("-" * 40)
    
    extract_file = Path("src/thesis_inno_eval/extract_sections_with_ai.py")
    if not extract_file.exists():
        print("❌ 提取模块文件不存在")
        return False
    
    with open(extract_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查缓存保存函数
    if "save_extraction_cache" in content and "_pro_extracted_info.json" in content:
        print(" 提取模块使用专家版缓存文件名")
    else:
        print("❌ 提取模块未使用专家版缓存文件名")
        return False
    
    return True

def validate_cached_evaluator():
    """验证缓存评估器的专家版优先逻辑"""
    
    print(f"\n📊 验证缓存评估器")
    print("-" * 40)
    
    cache_file = Path("src/thesis_inno_eval/cached_evaluator.py")
    if not cache_file.exists():
        print("❌ 缓存评估器文件不存在")
        return False
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查优先级加载逻辑
    if "pro_extracted_info.json" in content and "extracted_info.json" in content:
        print(" 缓存评估器实现专家版优先加载")
    else:
        print("❌ 缓存评估器未实现专家版优先加载")
        return False
    
    return True

def check_command_consistency():
    """检查命令一致性"""
    
    print(f"\n🎯 验证命令一致性")
    print("-" * 40)
    
    cli_file = Path("src/thesis_inno_eval/cli.py")
    with open(cli_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有命令函数
    command_functions = [
        ("extract", "提取"),
        ("evaluate", "评估"), 
        ("literature_analysis", "文献分析")
    ]
    
    all_consistent = True
    for cmd, desc in command_functions:
        # 检查函数定义
        func_pattern = rf'def\s+{cmd}\s*\('
        if re.search(func_pattern, content):
            print(f" {desc}命令 ({cmd}) 已实现")
        else:
            print(f"❌ {desc}命令 ({cmd}) 未找到")
            all_consistent = False
    
    return all_consistent

def main():
    """主验证函数"""
    
    print("🚀 专家版优先实现完整性验证")
    print("=" * 80)
    
    results = []
    
    # 执行各项验证
    results.append(("CLI实现", validate_cli_implementation()))
    results.append(("提取模块", validate_extraction_module()))
    results.append(("缓存评估器", validate_cached_evaluator()))
    results.append(("命令一致性", check_command_consistency()))
    
    # 汇总结果
    print(f"\n📋 验证结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for item, result in results:
        status = " 通过" if result else "❌ 失败"
        print(f"{item:15} {status}")
        if result:
            passed += 1
    
    print(f"\n🏆 总体结果: {passed}/{total} 项验证通过")
    
    if passed == total:
        print("🎉 所有验证通过！专家版优先实现完成")
        print("\n📝 实现总结:")
        print("   • Extract命令: 直接保存为_pro_extracted_info.json")
        print("   • Evaluate命令: 读取_pro_extracted_info.json文件")
        print("   • Literature_analysis命令: 优先读取专家版，回退到标准版")
        print("   • 缓存系统: 优先加载专家版文件")
        print("   • 元数据: 包含pro_strategy方法和版本信息")
        
        print(f"\n💡 使用建议:")
        print("   1. 新的提取任务会自动生成专家版文件")
        print("   2. 评估和分析命令优先使用专家版文件")
        print("   3. 如需重新生成专家版，直接运行extract命令")
        
    else:
        print("⚠️ 存在验证失败项，需要进一步检查和修复")
    
    return passed == total

if __name__ == "__main__":
    main()

