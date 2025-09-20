#!/usr/bin/env python3
"""
简化版51177.docx文件抽取测试
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

def extract_51177_simple():
    """简化版抽取51177.docx"""
    
    target_file = "51177.docx"
    file_path = project_root / "data" / "input" / target_file
    
    print(f"🎯 开始简化抽取: {target_file}")
    
    try:
        # 使用extract_from_cached_markdown函数
        from src.thesis_inno_eval.extract_sections_with_ai import extract_from_cached_markdown
        from src.thesis_inno_eval.ai_client import get_ai_client
        
        # 获取AI客户端
        ai_client = get_ai_client()
        if not ai_client:
            print("❌ 无法获取AI客户端")
            return
        
        print("📖 开始从缓存抽取...")
        
        # 尝试从缓存抽取
        result = extract_from_cached_markdown(
            file_path=str(file_path),
            ai_client=ai_client,
            session_id="test_51177_simple",
            extraction_mode="full-text",  # 使用全文模式
            use_cache=True
        )
        
        if result:
            print(" 抽取成功！")
            
            # 分析结果
            total_fields = len(result)
            non_empty_fields = len([k for k, v in result.items() if v and str(v).strip()])
            
            print(f"📊 抽取结果统计:")
            print(f"   - 总字段数: {total_fields}")
            print(f"   - 非空字段数: {non_empty_fields}")
            print(f"   - 完整度: {non_empty_fields/total_fields*100:.1f}%")
            
            # 检查关键字段
            key_fields = [
                'ChineseTitle', 'ChineseAuthor', 'ChineseUniversity', 
                'DegreeLevel', 'ChineseAbstract', 'ReferenceList', 'ResearchConclusions'
            ]
            
            print(f"\n📋 关键字段:")
            for field in key_fields:
                value = result.get(field, '')
                if value:
                    if field == 'ReferenceList' and isinstance(value, list):
                        print(f"    {field}: {len(value)} 条")
                    elif isinstance(value, str):
                        preview = value[:60] + "..." if len(value) > 60 else value
                        print(f"    {field}: {preview}")
                    else:
                        print(f"    {field}: {str(value)[:60]}...")
                else:
                    print(f"   ❌ {field}: [空]")
            
            # 保存结果
            output_file = project_root / "data" / "output" / f"{target_file}_extracted_info.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 结果已保存到: {output_file.name}")
            
        else:
            print("❌ 抽取失败")
            
    except Exception as e:
        print(f"❌ 抽取过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_51177_simple()
