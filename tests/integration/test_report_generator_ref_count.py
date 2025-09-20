#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-

import sys
sys.path.append(r'f:\MyProjects\thesis_Inno_Eval\src')

def test_report_generator_ref_count():
    """测试 report_generator.py 中的 ref_count 处理"""
    
    try:
        from thesis_inno_eval.report_generator import MarkdownReportGenerator
        
        generator = MarkdownReportGenerator()
        
        # 测试不同类型的参考文献数据
        test_cases = [
            [],  # 空列表
            ["参考文献1", "参考文献2"],  # 列表格式
            "参考文献1\n参考文献2\n参考文献3",  # 字符串格式
        ]
        
        print("=== 测试 ReportGenerator 中的 ref_count 处理 ===")
        
        for i, ref_list in enumerate(test_cases):
            try:
                # 测试时效性分析方法（这个方法中包含了 ref_count 逻辑）
                result = generator._analyze_literature_timeliness(ref_list, {})
                print(f"测试用例 {i+1}: {type(ref_list).__name__} -> 成功")
            except Exception as e:
                print(f"测试用例 {i+1}: {type(ref_list).__name__} -> 错误: {e}")
                if "ref_count" in str(e):
                    print(f"  ❌ ref_count 相关错误: {e}")
                    return False
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_report_generator_ref_count()
    if success:
        print("\n🎉 ReportGenerator ref_count 测试通过！")
    else:
        print("\n❌ ReportGenerator ref_count 存在问题")
