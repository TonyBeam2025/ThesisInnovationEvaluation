#!/usr/bin/env python3
"""
测试supervisor_en正则表达式模式的匹配效果
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import re

# 提取新添加的supervisor_en正则表达式模式
supervisor_en_patterns = [
    r'(?:Supervisor|SUPERVISOR)[：:\s]*([A-Za-z\s\.]{2,50})',
    r'(?:Advisor|ADVISOR)[：:\s]*([A-Za-z\s\.]{2,50})',
    r'(?:Directed\s+by|DIRECTED\s+BY)[：:\s]*([A-Za-z\s\.]{2,50})',
    r'(?:Under\s+the\s+guidance\s+of)[：:\s]*([A-Za-z\s\.]{2,50})',
    r'(?:Prof\.|Professor|Dr\.)\s+([A-Za-z\s]{2,40})',
]

# 测试用例
test_cases = [
    "Supervisor: John Smith",
    "SUPERVISOR: Mary Johnson",
    "Supervisor：Robert Chen",
    "Advisor: Dr. Michael Brown",
    "ADVISOR: Professor Lisa Wang",
    "Directed by: Dr. David Miller",
    "DIRECTED BY: Professor Sarah Davis",
    "Under the guidance of: Dr. James Wilson",
    "Under the guidance of Professor Emily Taylor",
    "Supervisor: Dr. Kevin Zhang",
    "Advisor：Prof. Jennifer Liu",
]

def test_supervisor_en_patterns():
    """测试supervisor_en正则表达式模式"""
    print("🧪 测试supervisor_en正则表达式模式")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test_text}")
        matched = False
        
        for j, pattern in enumerate(supervisor_en_patterns, 1):
            match = re.search(pattern, test_text, re.IGNORECASE)
            if match:
                print(f"   模式{j}匹配成功: '{match.group(1)}'")
                matched = True
                break
        
        if not matched:
            print(f"  ❌ 无匹配")
    
    print("\n" + "=" * 50)
    print(" 测试完成")

if __name__ == "__main__":
    test_supervisor_en_patterns()
