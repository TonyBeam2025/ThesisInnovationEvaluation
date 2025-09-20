#!/usr/bin/env python3
"""
方案1：统一保留头衔的supervisor_en模式
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import re

# 方案1：统一保留头衔
patterns_keep_titles = [
    r'(?:Supervisor|SUPERVISOR)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Advisor|ADVISOR)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Directed\s+by|DIRECTED\s+BY)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Under\s+the\s+guidance\s+of)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'((Prof\.|Professor|Dr\.)\s+[A-Za-z\s]+?)(?:\n|$|[，,])',  # 修改：保留头衔
]

test_cases = [
    "Supervisor: Dr. John Smith",
    "Supervisor: Professor Mary Johnson", 
    "Advisor: Dr. Michael Brown",
    "Prof. Kevin Zhang",
    "Dr. Jennifer Liu",
    "Professor David Wilson",
]

def test_keep_titles():
    """测试保留头衔的方案"""
    print("🧪 方案1：统一保留头衔")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test_text}")
        
        for j, pattern in enumerate(patterns_keep_titles, 1):
            match = re.search(pattern, test_text, re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                print(f"   模式{j} 匹配: '{result}'")
                break
        else:
            print(f"  ❌ 无匹配")
    
    print("\n优点：")
    print("- 保留完整的学术信息")
    print("- 提供更多上下文信息")
    print("- 有助于区分不同级别的导师")
    print("- 符合学术规范")

if __name__ == "__main__":
    test_keep_titles()
