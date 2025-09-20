#!/usr/bin/env python3
"""
测试抽取51177.docx文件的结构化信息
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
import json
from pathlib import Path
import time

# 添加项目路径
project_root = PROJECT_ROOT
sys.path.insert(0, str(project_root))

def test_extract_51177():
    """测试抽取51177.docx文件"""
    
    target_file = "51177.docx"
    file_path = project_root / "data" / "input" / target_file
    
    if not file_path.exists():
        print(f"❌ 测试文件不存在: {file_path}")
        return
    
    print(f"🎯 开始测试抽取: {target_file}")
    file_size_mb = file_path.stat().st_size / 1024 / 1024
    print(f"📊 文件大小: {file_size_mb:.1f} MB")
    
    try:
        # 使用现有的评估系统
        from src.thesis_inno_eval.cached_evaluator import CachedEvaluator
        from src.thesis_inno_eval.config_manager import ConfigManager
        
        # 初始化配置
        config_file = project_root / "config" / "conf.yaml"
        config_mgr = ConfigManager(str(config_file))
        
        # 创建缓存评估器
        evaluator = CachedEvaluator(config_mgr)
        
        print("📋 开始结构化信息抽取...")
        start_time = time.time()
        
        # 先获取AI客户端
        from src.thesis_inno_eval.ai_client import get_ai_client
        ai_client = get_ai_client()
        
        if not ai_client:
            print("❌ 无法获取AI客户端")
            return
        
        # 执行抽取
        result = evaluator._extract_thesis_info(str(file_path), ai_client, "test_51177")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if result:
            print(f" 抽取成功！耗时: {processing_time:.1f} 秒")
            
            # 分析结果
            total_fields = len(result)
            non_empty_fields = len([k for k, v in result.items() if v and str(v).strip()])
            
            print(f"\n📊 抽取结果统计:")
            print(f"   - 总字段数: {total_fields}")
            print(f"   - 非空字段数: {non_empty_fields}")
            print(f"   - 完整度: {non_empty_fields/total_fields*100:.1f}%")
            
            # 显示关键字段
            key_fields = [
                'ChineseTitle', 'ChineseAuthor', 'ChineseUniversity', 
                'DegreeLevel', 'ChineseAbstract', 'ReferenceList', 'ResearchConclusions'
            ]
            
            print(f"\n📋 关键字段检查:")
            for field in key_fields:
                value = result.get(field, '')
                if value:
                    if field == 'ReferenceList' and isinstance(value, list):
                        print(f"    {field}: {len(value)} 条参考文献")
                    elif isinstance(value, str):
                        preview = value[:80] + "..." if len(value) > 80 else value
                        print(f"    {field}: {preview}")
                    else:
                        print(f"    {field}: {str(value)[:80]}...")
                else:
                    print(f"   ❌ {field}: [空]")
            
            # 检查学位论文特征
            is_thesis_detected = any([
                result.get('DegreeLevel'),
                result.get('ChineseUniversity'),
                '学位论文' in str(result.get('ChineseTitle', '')),
                '硕士' in str(result.get('ChineseTitle', '')),
                '博士' in str(result.get('ChineseTitle', ''))
            ])
            
            print(f"\n🎓 学位论文检测: {'是' if is_thesis_detected else '否'}")
            
            # 保存结果
            output_file = project_root / "data" / "output" / f"{target_file}_extracted_info.json"
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 结果已保存到: {output_file.name}")
                
            except Exception as e:
                print(f"❌ 保存失败: {e}")
            
            # 检查是否使用了分步抽取
            print(f"\n🔍 抽取方式分析:")
            if result.get('ChineseTitle') and result.get('ChineseAbstract'):
                print(f"   - 标题和摘要都已提取，可能使用了分步抽取")
            
            if result.get('ReferenceList'):
                print(f"   - 参考文献已提取，正文处理成功")
            else:
                print(f"   - 参考文献缺失，可能需要优化正文处理")
            
        else:
            print(f"❌ 抽取失败，耗时: {processing_time:.1f} 秒")
            return
            
    except Exception as e:
        print(f"❌ 抽取过程出错: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n🎉 测试完成！")

def check_cache_status():
    """检查缓存状态"""
    
    print("\n📁 检查缓存状态:")
    
    target_file = "51177.docx"
    
    # 检查文档缓存
    cache_dir = project_root / "cache" / "documents"
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*51177*"))
        print(f"   文档缓存: {len(cache_files)} 个相关文件")
        for file in cache_files:
            size_kb = file.stat().st_size / 1024
            print(f"     - {file.name} ({size_kb:.1f} KB)")
    else:
        print(f"   文档缓存目录不存在")
    
    # 检查输出缓存
    output_dir = project_root / "data" / "output"
    if output_dir.exists():
        output_files = list(output_dir.glob("*51177*"))
        print(f"   输出缓存: {len(output_files)} 个相关文件")
        for file in output_files:
            size_kb = file.stat().st_size / 1024
            print(f"     - {file.name} ({size_kb:.1f} KB)")
    else:
        print(f"   输出目录不存在")

if __name__ == "__main__":
    check_cache_status()
    test_extract_51177()
