#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-

import sys
sys.path.append(r'f:\MyProjects\thesis_Inno_Eval\src')

from thesis_inno_eval.literature_review_analyzer import LiteratureReviewAnalyzer

def test_ref_count_access():
    """测试 ref_count 变量访问"""
    
    analyzer = LiteratureReviewAnalyzer()
    
    # 测试不同类型的参考文献列表
    test_cases = [
        [],  # 空列表
        ["参考文献1", "参考文献2", "参考文献3"],  # 列表格式
        "参考文献1\n参考文献2\n参考文献3",  # 字符串格式
        "[1] 参考文献1\n[2] 参考文献2\n[3] 参考文献3",  # 编号格式
        None,  # None
        ""  # 空字符串
    ]
    
    print("=== 测试 _count_references 方法 ===")
    for i, ref_list in enumerate(test_cases):
        try:
            count = analyzer._count_references(ref_list)
            print(f"测试用例 {i+1}: {type(ref_list).__name__} -> 数量: {count}")
        except Exception as e:
            print(f"测试用例 {i+1}: {type(ref_list).__name__} -> 错误: {e}")
    
    # 测试在 literature_review_analyzer 中的使用
    print("\n=== 测试在分析器中的使用 ===")
    try:
        # 模拟一个简单的调用
        fake_papers_by_lang = {'Chinese': [], 'English': []}
        fake_thesis_info = {'title': '测试论文', 'keywords': '测试', 'literature_review': '测试综述'}
        
        # 这里不会真正生成完整报告，只是测试 ref_count 相关的逻辑
        ref_count = analyzer._count_references(["参考文献1", "参考文献2"])
        print(f" ref_count 正常获取: {ref_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ ref_count 访问错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ref_count_access()
    if success:
        print("\n🎉 ref_count 变量访问测试通过！")
    else:
        print("\n❌ ref_count 变量访问存在问题")
