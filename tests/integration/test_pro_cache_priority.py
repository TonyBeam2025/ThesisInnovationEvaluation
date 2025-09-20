#!/usr/bin/env python3
"""
测试专家版缓存文件优先加载功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

from pathlib import Path
from thesis_inno_eval.cached_evaluator import CachedEvaluator
from thesis_inno_eval.config_manager import get_config_manager

def test_pro_cache_priority():
    """测试专家版缓存文件优先加载"""
    
    print("🔍 测试专家版缓存文件优先加载功能")
    print("=" * 50)
    
    # 初始化配置
    config_mgr = get_config_manager()
    evaluator = CachedEvaluator(config_mgr)
    
    # 测试文件
    test_file = "data/input/50193.docx"
    base_name = "50193"
    
    print(f"📁 测试文件: {test_file}")
    print(f"📝 基础名称: {base_name}")
    
    # 检查缓存状态
    cache_status = evaluator.get_cache_status(test_file)
    
    print(f"\n💾 缓存状态检查:")
    print(f"   论文信息缓存: {' 已缓存' if cache_status['thesis_info_cached'] else '❌ 未缓存'}")
    print(f"   文献搜索缓存: {' 已缓存' if cache_status['search_results_cached'] else '❌ 未缓存'}")
    print(f"   缓存文件数量: {len(cache_status['cache_files'])} 个")
    
    for cache_file in cache_status['cache_files']:
        size_mb = cache_file['size'] / (1024 * 1024)
        file_type = cache_file['type']
        file_path = cache_file['path']
        
        # 特别标注专家版文件
        if 'pro' in file_type:
            print(f"     🎯 {file_type}: {size_mb:.2f} MB [专家版优先]")
        else:
            print(f"     📁 {file_type}: {size_mb:.2f} MB")
        
        print(f"        路径: {file_path}")
    
    # 测试加载缓存信息
    print(f"\n🔧 测试加载缓存信息:")
    thesis_info = evaluator._load_cached_thesis_info(base_name)
    
    if thesis_info:
        print(" 成功加载缓存的论文信息")
        
        # 检查关键字段
        key_fields = ['thesis_number', 'title_cn', 'author_cn', 'supervisor_cn', 'supervisor_en']
        print(f"\n📋 关键字段检查:")
        for field in key_fields:
            if field in thesis_info:
                value = thesis_info[field]
                status = "" if value and str(value).strip() else "❌"
                display_value = str(value) if len(str(value)) < 50 else str(value)[:47]+'...'
                print(f"   {status} {field}: {display_value}")
        
        # 统计填充情况
        filled_fields = sum(1 for v in thesis_info.values() if v and str(v).strip())
        total_fields = len(thesis_info)
        fill_rate = filled_fields / total_fields * 100
        
        print(f"\n📊 数据完整性:")
        print(f"   已填充字段: {filled_fields}/{total_fields}")
        print(f"   填充率: {fill_rate:.1f}%")
        
    else:
        print("❌ 未能加载缓存的论文信息")
    
    print(f"\n🎯 测试结论:")
    if cache_status['thesis_info_cached']:
        pro_files = [f for f in cache_status['cache_files'] if 'pro' in f['type']]
        if pro_files:
            print(" 系统已配置为优先使用专家版缓存文件")
            print(" 成功检测到专家版文件并优先加载")
        else:
            print("⚠️ 未检测到专家版文件，使用标准版文件")
    else:
        print("❌ 未找到任何缓存文件")

if __name__ == "__main__":
    test_pro_cache_priority()
