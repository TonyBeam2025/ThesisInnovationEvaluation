#!/usr/bin/env python3
"""
测试分步学位论文抽取功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
import json
from pathlib import Path

# 添加项目路径
project_root = PROJECT_ROOT
sys.path.insert(0, str(project_root))

try:
    from src.thesis_inno_eval.extract_sections_with_ai import extract_thesis_with_staged_approach, _is_likely_thesis, extract_sections_with_ai
    from src.thesis_inno_eval.cached_evaluator import CachedEvaluator
    from src.thesis_inno_eval.gemini_client import GeminiClient
    from src.thesis_inno_eval.config_manager import ConfigManager
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

def test_staged_extraction():
    """测试分步抽取功能"""
    
    # 目标论文
    target_file = "15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究.docx"
    file_path = project_root / "data" / "input" / target_file
    
    if not file_path.exists():
        print(f"❌ 测试文件不存在: {file_path}")
        return
    
    print(f"🎯 开始测试分步抽取: {target_file}")
    
    # 初始化配置和客户端
    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        ai_client = GeminiClient(config)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 创建缓存评估器
    evaluator = CachedEvaluator(config)
    
    # 获取缓存的Markdown内容
    print("📖 读取缓存的Markdown内容...")
    try:
        cached_text = evaluator.document_cache.get_cached_markdown(str(file_path))
    except Exception as e:
        print(f"❌ 获取缓存内容失败: {e}")
        return
    
    if not cached_text:
        print("❌ 无法获取缓存的Markdown内容")
        return
    
    print(f"📊 文档长度: {len(cached_text):,} 字符")
    
    # 检测是否为学位论文
    is_thesis = _is_likely_thesis(cached_text)
    print(f"📋 学位论文检测结果: {'是' if is_thesis else '否'}")
    
    # 如果是学位论文，使用分步抽取
    if is_thesis:
        print("🎓 使用分步抽取模式...")
        result = extract_thesis_with_staged_approach(cached_text, ai_client, "test_staged")
    else:
        print("📄 使用常规抽取模式...")
        result = extract_sections_with_ai(cached_text, ai_client, "test_regular")
    
    if result:
        print(" 抽取成功！")
        
        # 分析结果
        total_fields = len(result)
        non_empty_fields = len([k for k, v in result.items() if v and str(v).strip()])
        
        print(f"📊 抽取结果统计:")
        print(f"   - 总字段数: {total_fields}")
        print(f"   - 非空字段数: {non_empty_fields}")
        print(f"   - 完整度: {non_empty_fields/total_fields*100:.1f}%")
        
        # 显示关键字段
        key_fields = ['ChineseTitle', 'ChineseAuthor', 'ChineseUniversity', 'DegreeLevel', 'ChineseAbstract']
        print(f"\n📋 关键字段预览:")
        for field in key_fields:
            value = result.get(field, '')
            if value:
                preview = value[:100] + "..." if len(value) > 100 else value
                print(f"   {field}: {preview}")
            else:
                print(f"   {field}: [空]")
        
        # 保存结果
        output_path = project_root / "data" / "output" / "staged_extraction_test.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 结果已保存到: {output_path}")
        
    else:
        print("❌ 抽取失败")

if __name__ == "__main__":
    test_staged_extraction()
