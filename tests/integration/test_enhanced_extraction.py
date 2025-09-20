#!/usr/bin/env python3
"""
测试增强版字段补充功能
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

def test_enhanced_extraction():
    """测试增强版字段补充功能"""
    
    print("🎯 测试增强版字段补充功能")
    
    # 检查是否有可用的AI客户端
    try:
        from src.thesis_inno_eval.gemini_client import get_ai_client
        ai_client = get_ai_client()
        
        if not ai_client:
            print("❌ 无法获取AI客户端")
            return
            
        print(f" AI客户端初始化成功: {ai_client.get_api_type()}")
        
    except Exception as e:
        print(f"❌ AI客户端初始化失败: {e}")
        return
    
    # 读取原始Markdown文件
    md_file = project_root / "data" / "output" / "Bi-Sb-Se基材料的制备及热电性能研究.md"
    
    if not md_file.exists():
        print(f"❌ Markdown文件不存在: {md_file}")
        return
    
    print(f"📖 读取文档: {md_file.name}")
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    print(f"📊 文档长度: {len(text_content):,} 字符")
    
    # 调用增强版提取函数
    try:
        from src.thesis_inno_eval.extract_sections_with_ai import _extract_enhanced_metadata
        
        print("🔍 开始增强版元数据提取...")
        result = _extract_enhanced_metadata(text_content, ai_client, "test_enhanced")
        
        if result:
            print(" 增强版提取成功！")
            
            # 显示结果
            total_fields = len(result)
            non_empty_fields = len([k for k, v in result.items() if v and str(v).strip()])
            
            print(f"\n📊 增强版提取结果:")
            print(f"   - 总字段数: {total_fields}")
            print(f"   - 非空字段数: {non_empty_fields}")
            print(f"   - 完整度: {non_empty_fields/total_fields*100:.1f}%")
            
            # 检查关键字段
            critical_fields = ['ChineseAuthor', 'ChineseUniversity', 'DegreeLevel', 'ReferenceList', 'ResearchConclusions']
            
            print(f"\n🔍 关键字段检查:")
            for field in critical_fields:
                value = result.get(field, '')
                if value:
                    if isinstance(value, list):
                        print(f"    {field}: {len(value)} 项")
                        if field == 'ReferenceList' and len(value) > 0:
                            print(f"      示例: {value[0][:50]}...")
                    else:
                        preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                        print(f"    {field}: {preview}")
                else:
                    print(f"   ❌ {field}: [空]")
            
            # 保存增强版结果
            output_file = project_root / "data" / "output" / "Bi-Sb-Se基材料的制备及热电性能研究_enhanced_extraction.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 增强版结果已保存到: {output_file.name}")
            
            # 与现有结果对比
            existing_file = project_root / "data" / "output" / "Bi-Sb-Se基材料的制备及热电性能研究_extracted_info.json"
            
            if existing_file.exists():
                with open(existing_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                print(f"\n📊 与现有结果对比:")
                
                existing_non_empty = len([k for k, v in existing_data.items() if v and str(v).strip()])
                enhanced_non_empty = len([k for k, v in result.items() if v and str(v).strip()])
                
                print(f"   - 现有非空字段: {existing_non_empty}")
                print(f"   - 增强后非空字段: {enhanced_non_empty}")
                print(f"   - 改进程度: +{enhanced_non_empty - existing_non_empty}")
                
                # 显示新补充的字段
                new_fields = []
                for field in critical_fields:
                    if not existing_data.get(field) and result.get(field):
                        new_fields.append(field)
                
                if new_fields:
                    print(f"   - 新补充字段: {', '.join(new_fields)}")
                else:
                    print(f"   - 暂无新补充字段")
        
        else:
            print("❌ 增强版提取失败")
            
    except Exception as e:
        print(f"❌ 增强版提取异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_extraction()
