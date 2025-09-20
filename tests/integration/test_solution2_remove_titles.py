#!/usr/bin/env python3
"""
方案2：统一去除头衔的supervisor_en模式
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import re

# 方案2：统一去除头衔
patterns_remove_titles = [
    r'(?:Supervisor|SUPERVISOR)[：:\s]*(?:(?:Prof\.|Professor|Dr\.)\s+)?([A-Za-z\s]+?)(?:\n|$|[，,])',
    r'(?:Advisor|ADVISOR)[：:\s]*(?:(?:Prof\.|Professor|Dr\.)\s+)?([A-Za-z\s]+?)(?:\n|$|[，,])',
    r'(?:Directed\s+by|DIRECTED\s+BY)[：:\s]*(?:(?:Prof\.|Professor|Dr\.)\s+)?([A-Za-z\s]+?)(?:\n|$|[，,])',
    r'(?:Under\s+the\s+guidance\s+of)[：:\s]*(?:(?:Prof\.|Professor|Dr\.)\s+)?([A-Za-z\s]+?)(?:\n|$|[，,])',
    r'(?:Prof\.|Professor|Dr\.)\s+([A-Za-z\s]+?)(?:\n|$|[，,])',  # 保持原样：去除头衔
]

test_cases = [
    "Supervisor: Dr. John Smith",
    "Supervisor: Professor Mary Johnson", 
    "Advisor: Dr. Michael Brown",
    "Prof. Kevin Zhang",
    "Dr. Jennifer Liu",
    "Professor David Wilson",
]

def test_remove_titles():
    """测试去除头衔的方案"""
    print("🧪 方案2：统一去除头衔")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test_text}")
        
        for j, pattern in enumerate(patterns_remove_titles, 1):
            match = re.search(pattern, test_text, re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                print(f"   模式{j} 匹配: '{result}'")
                break
        else:
            print(f"  ❌ 无匹配")
    
    print("\n优点：")
    print("- 提供纯净的姓名信息")
    print("- 便于姓名比较和检索")
    print("- 减少格式差异")
    print("- 统一数据格式")

if __name__ == "__main__":
    test_remove_titles()
