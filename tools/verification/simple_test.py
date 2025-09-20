#!/usr/bin/env python3
"""
简单测试分步学位论文抽取功能
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_thesis_detection():
    """测试学位论文检测功能"""
    
    print("🎯 测试学位论文检测功能")
    
    # 测试文本样本
    thesis_text = """
    学位论文
    
    Bi-Sb-Se基材料的制备及热电性能研究
    
    申请学位级别：硕士
    专业：材料科学与工程
    指导教师：张教授
    培养单位：某大学材料学院
    
    摘要
    本论文研究了Bi-Sb-Se基材料的制备工艺及其热电性能...
    """
    
    non_thesis_text = """
    这是一篇普通的学术论文
    
    机器学习在自然语言处理中的应用
    
    作者：李明
    单位：研究所
    
    摘要
    本文介绍了机器学习技术...
    """
    
    try:
        from src.thesis_inno_eval.extract_sections_with_ai import _is_likely_thesis
        
        # 测试学位论文检测
        result1 = _is_likely_thesis(thesis_text)
        result2 = _is_likely_thesis(non_thesis_text)
        
        print(f"📋 学位论文样本检测结果: {'是' if result1 else '否'}")
        print(f"📄 普通论文样本检测结果: {'是' if result2 else '否'}")
        
        if result1 and not result2:
            print(" 学位论文检测功能正常工作")
        else:
            print("❌ 学位论文检测可能有问题")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def check_existing_cache():
    """检查现有的缓存文件"""
    
    print("\n📁 检查现有缓存文件")
    
    # 检查输出目录
    output_dir = project_root / "data" / "output"
    if output_dir.exists():
        json_files = list(output_dir.glob("*.json"))
        print(f"📊 找到 {len(json_files)} 个JSON文件:")
        
        for file in json_files[:5]:  # 只显示前5个
            print(f"   - {file.name}")
            
            # 检查文件大小
            size_kb = file.stat().st_size / 1024
            print(f"     大小: {size_kb:.1f} KB")
            
            # 尝试读取第一个文件的内容
            if file.name.startswith("Bi-Sb-Se"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print(f"     字段数: {len(data)}")
                    
                    # 检查关键字段
                    key_fields = ['ChineseTitle', 'ReferenceList']
                    for field in key_fields:
                        if field in data:
                            value = data[field]
                            if value:
                                if field == 'ReferenceList' and isinstance(value, list):
                                    print(f"     {field}: {len(value)} 条参考文献")
                                else:
                                    preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                                    print(f"     {field}: {preview}")
                            else:
                                print(f"     {field}: [空]")
                        else:
                            print(f"     {field}: [缺失]")
                            
                except Exception as e:
                    print(f"     ❌ 读取失败: {e}")
                    
                break
    else:
        print("❌ 输出目录不存在")

if __name__ == "__main__":
    test_thesis_detection()
    check_existing_cache()

