#!/usr/bin/env python3
"""
测试分批次抽取论文信息功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
import json
import time
from pathlib import Path

# 添加项目路径
project_root = PROJECT_ROOT
sys.path.insert(0, str(project_root))

try:
    from src.thesis_inno_eval.extract_sections_with_ai import (
        extract_sections_with_pro_strategy,  # 使用新的专业版策略
        extract_from_cached_markdown,
        extract_text_from_pdf
    )
    from src.thesis_inno_eval.ai_client import get_ai_client
    from src.thesis_inno_eval.config_manager import reset_config_manager
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

def test_pro_strategy_extraction():
    """测试专业版策略抽取功能"""
    
    print("🧪 测试分批次抽取论文信息")
    print("=" * 50)
    
    # 重置配置管理器
    reset_config_manager()
    
    # 获取AI客户端
    try:
        ai_client = get_ai_client()
        print(f" AI客户端初始化成功: {ai_client.get_api_type()}")
    except Exception as e:
        print(f"❌ AI客户端初始化失败: {e}")
        return
    
    # 测试文件
    test_files = [
        "基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩.pdf",
        "15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究.docx"
    ]
    
    # 测试不同的批次大小
    batch_sizes = [5000, 8000, 12000]
    
    for file_name in test_files:
        file_path = project_root / "data" / "input" / file_name
        
        if not file_path.exists():
            print(f"⚠️ 跳过不存在的文件: {file_name}")
            continue
            
        print(f"\n📄 测试文件: {file_name}")
        print("-" * 40)
        
        for batch_size in batch_sizes:
            print(f"\n🔧 批次大小: {batch_size:,} 字符")
            
            session_id = f"batch_test_{int(time.time())}"
            start_time = time.time()
            
            try:
                # 测试专业版策略方法
                print("   🎓 使用专业版策略方法...")
                result = extract_sections_with_pro_strategy(
                    file_path=str(file_path),
                    use_cache=True
                )
                
                process_time = time.time() - start_time
                
                if result:
                    # 分析结果
                    total_fields = len(result)
                    non_empty_fields = len([k for k, v in result.items() 
                                          if v and str(v).strip()])
                    
                    print(f"    抽取成功 ({process_time:.1f}s)")
                    print(f"      - 总字段: {total_fields}")
                    print(f"      - 非空字段: {non_empty_fields}")
                    print(f"      - 完整度: {non_empty_fields/total_fields*100:.1f}%")
                    
                    # 检查关键字段
                    key_fields = ['title_cn', 'author_cn', 'university_cn', 'degree_level']
                    available_keys = []
                    for field in key_fields:
                        if field in result and result[field]:
                            available_keys.append(field)
                    
                    print(f"      - 关键字段: {len(available_keys)}/{len(key_fields)}")
                    
                    # 保存结果
                    output_file = (project_root / "data" / "output" / 
                                 f"batch_test_{Path(file_name).stem}_{batch_size}.json")
                    output_file.parent.mkdir(exist_ok=True)
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    print(f"      💾 结果保存到: {output_file.name}")
                    
                else:
                    print(f"   ❌ 抽取失败 ({process_time:.1f}s)")
                    
            except Exception as e:
                print(f"   ❌ 处理出错: {e}")
            
            # 短暂休息
            time.sleep(2)

def test_batch_modes():
    """测试不同的批次模式"""
    
    print("\n\n🎯 测试不同批次模式")
    print("=" * 50)
    
    # 重置配置管理器
    reset_config_manager()
    
    # 获取AI客户端
    try:
        ai_client = get_ai_client()
        print(f" AI客户端初始化成功: {ai_client.get_api_type()}")
    except Exception as e:
        print(f"❌ AI客户端初始化失败: {e}")
        return
    
    # 测试文件
    test_file = "基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩.pdf"
    file_path = project_root / "data" / "input" / test_file
    
    if not file_path.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    # 测试模式配置
    test_configs = [
        {
            "name": "自动模式",
            "mode": "auto",
            "batch_size": 8000,
            "description": "系统自动选择处理模式"
        },
        {
            "name": "全文模式", 
            "mode": "full-text",
            "batch_size": None,
            "description": "一次性处理完整文档"
        },
        {
            "name": "分批章节模式",
            "mode": "batch-sections", 
            "batch_size": 6000,
            "description": "按章节分批处理"
        }
    ]
    
    results = {}
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n📝 测试 {i}/3: {config['name']}")
        print(f"   描述: {config['description']}")
        
        session_id = f"mode_test_{config['mode']}_{int(time.time())}"
        start_time = time.time()
        
        try:
            # 从PDF提取文本
            text = extract_text_from_pdf(str(file_path))
            
            if not text:
                print("   ❌ 文本提取失败")
                continue
                
            print(f"   📊 文档长度: {len(text):,} 字符")
            
            # 使用指定模式进行抽取
            result = extract_from_cached_markdown(
                str(file_path),
                ai_client,
                session_id=session_id,
                extraction_mode=config["mode"],
                batch_size=config["batch_size"] or 10000
            )
            
            process_time = time.time() - start_time
            
            if result:
                total_fields = len(result)
                non_empty_fields = len([k for k, v in result.items() 
                                      if v and str(v).strip()])
                
                print(f"    处理成功 ({process_time:.1f}s)")
                print(f"      - 总字段: {total_fields}")
                print(f"      - 非空字段: {non_empty_fields}")
                print(f"      - 完整度: {non_empty_fields/total_fields*100:.1f}%")
                
                results[config["name"]] = {
                    "success": True,
                    "time": process_time,
                    "total_fields": total_fields,
                    "non_empty_fields": non_empty_fields,
                    "completeness": non_empty_fields/total_fields*100
                }
                
                # 保存结果
                output_file = (project_root / "data" / "output" / 
                             f"mode_test_{config['mode']}.json")
                output_file.parent.mkdir(exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"      💾 结果保存到: {output_file.name}")
                
            else:
                print(f"   ❌ 处理失败 ({process_time:.1f}s)")
                results[config["name"]] = {
                    "success": False,
                    "time": process_time
                }
                
        except Exception as e:
            print(f"   ❌ 处理出错: {e}")
            results[config["name"]] = {
                "success": False,
                "error": str(e)
            }
        
        # 短暂休息
        time.sleep(2)
    
    # 总结测试结果
    print("\n📊 测试结果总结")
    print("=" * 30)
    
    for mode_name, result in results.items():
        if result.get("success"):
            print(f" {mode_name}:")
            print(f"   时间: {result['time']:.1f}s")
            print(f"   完整度: {result['completeness']:.1f}%")
        else:
            print(f"❌ {mode_name}: 失败")
            if "error" in result:
                print(f"   错误: {result['error']}")

if __name__ == "__main__":
    print("� 专业版策略抽取测试程序")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # 运行测试
    test_pro_strategy_extraction()
    test_batch_modes()
    
    print("\n🎉 测试完成！")
