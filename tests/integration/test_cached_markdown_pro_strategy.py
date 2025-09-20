#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试 extract_from_cached_markdown 对专业版策略的支持
"""

import os
import sys
import time
from pathlib import Path

# 添加项目路径
project_root = PROJECT_ROOT
sys.path.insert(0, str(project_root))

def test_cached_markdown_pro_strategy():
    """测试缓存Markdown提取函数对专业版策略的支持"""
    
    print("🧪 测试 extract_from_cached_markdown 专业版策略支持")
    print("=" * 60)
    
    try:
        from src.thesis_inno_eval.extract_sections_with_ai import extract_from_cached_markdown
        from src.thesis_inno_eval.ai_client import get_ai_client
        from src.thesis_inno_eval.config_manager import reset_config_manager
        
        # 重置配置
        reset_config_manager()
        
        # 获取AI客户端
        ai_client = get_ai_client()
        print(f" AI客户端初始化成功: {ai_client.get_api_type()}")
        
        # 测试文件
        test_files = [
            r".\data\input\跨模态图像融合技术在医疗影像分析中的研究.docx",
            r".\data\input\50193.docx"
        ]
        
        for i, file_path in enumerate(test_files, 1):
            if not os.path.exists(file_path):
                print(f"❌ 测试文件不存在: {file_path}")
                continue
                
            print(f"\n📄 测试文件 {i}: {Path(file_path).name}")
            print("-" * 40)
            
            # 测试不同的抽取模式
            modes_to_test = [
                ("pro-strategy", "专业版策略模式"),
                ("batch-sections", "批次模式（应映射到专业版策略）"),
                ("auto", "自动模式"),
                ("full-text", "全文模式")
            ]
            
            for mode, description in modes_to_test:
                print(f"\n🔧 测试模式: {mode} ({description})")
                
                try:
                    import time
                    start_time = time.time()
                    
                    result = extract_from_cached_markdown(
                        file_path=file_path,
                        ai_client=ai_client,
                        session_id=f"test_{mode}_{i}",
                        extraction_mode=mode,
                        batch_size=10000,
                        use_cache=True
                    )
                    
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    if result:
                        # 分析结果
                        field_count = len([k for k, v in result.items() if v and str(v).strip()])
                        total_fields = len(result)
                        
                        print(f" 抽取成功!")
                        print(f"⏱️  处理时间: {processing_time:.2f} 秒")
                        print(f"📊 提取字段: {field_count}/{total_fields}")
                        
                        # 检查关键字段
                        key_fields = ['title_cn', 'author_cn', 'university_cn', 'ChineseTitle', 'ChineseKeywords']
                        found_fields = []
                        for field in key_fields:
                            if field in result and result[field]:
                                found_fields.append(field)
                        
                        if found_fields:
                            print(f"🔍 关键字段: {', '.join(found_fields)}")
                            # 显示第一个找到的字段内容预览
                            first_field = found_fields[0]
                            value = str(result[first_field])[:50] + "..." if len(str(result[first_field])) > 50 else str(result[first_field])
                            print(f"📋 {first_field}: {value}")
                        
                        # 检查是否是新格式（专业版策略格式）
                        new_format_indicators = ['discipline', 'multidisciplinary_features', 'quality_score']
                        is_new_format = any(indicator in result for indicator in new_format_indicators)
                        
                        if is_new_format:
                            print("🎓 检测到专业版策略格式特征")
                            if 'discipline' in result:
                                print(f"   🎯 学科: {result['discipline']}")
                            if 'quality_score' in result:
                                print(f"   ⭐ 质量分数: {result['quality_score']}")
                        else:
                            print("📝 传统格式")
                    else:
                        print(f"❌ 抽取失败: 返回空结果")
                        
                except Exception as e:
                    print(f"❌ 模式 {mode} 测试失败: {str(e)}")
                    import traceback
                    print(f"详细错误: {traceback.format_exc()}")
    
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def test_cli_integration():
    """测试CLI集成"""
    print("\n" + "=" * 60)
    print("🧪 测试CLI集成")
    print("=" * 60)
    
    try:
        # 测试CLI命令是否正常工作
        test_file = r".\data\input\跨模态图像融合技术在医疗影像分析中的研究.docx"
        
        if os.path.exists(test_file):
            print(f"📄 测试文件: {Path(test_file).name}")
            print("💡 可以运行以下命令测试CLI集成:")
            print(f"   uv run thesis-eval extract --extraction-mode batch-sections \"{test_file}\"")
            print(f"   uv run thesis-eval extract --extraction-mode auto \"{test_file}\"")
        else:
            print("❌ 测试文件不存在，跳过CLI集成测试")
            
    except Exception as e:
        print(f"❌ CLI集成测试失败: {e}")

if __name__ == "__main__":
    print("🔥 extract_from_cached_markdown 专业版策略支持测试")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # 运行测试
    test_cached_markdown_pro_strategy()
    test_cli_integration()
    
    print(f"\n🎉 测试完成!")
