#!/usr/bin/env python3
"""
最终测试优化的supervisor_en正则表达式模式
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import re

# 优化后的supervisor_en正则表达式模式
supervisor_en_patterns = [
    r'(?:Supervisor|SUPERVISOR)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Advisor|ADVISOR)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Directed\s+by|DIRECTED\s+BY)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Under\s+the\s+guidance\s+of)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Prof\.|Professor|Dr\.)\s+([A-Za-z\s]+?)(?:\n|$|[，,])',
]

# 更真实的测试用例
test_cases = [
    "Supervisor: John Smith\nCollege: Engineering",
    "SUPERVISOR: Mary Johnson",
    "Supervisor：Robert Chen, PhD",
    "Advisor: Dr. Michael Brown\nDepartment: Computer Science",
    "ADVISOR: Professor Lisa Wang",
    "Directed by: Dr. David Miller\nYear: 2024",
    "DIRECTED BY: Professor Sarah Davis",
    "Under the guidance of: Dr. James Wilson\nThesis submitted",
    "Under the guidance of Professor Emily Taylor",
    "Prof. Kevin Zhang\nBeijing University",
    "Dr. Jennifer Liu，Professor of Mathematics",
]

def test_optimized_supervisor_en_patterns():
    """测试优化后的supervisor_en正则表达式模式"""
    print("🧪 测试优化后的supervisor_en正则表达式模式")
    print("=" * 60)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test_text}")
        matched = False
        
        for j, pattern in enumerate(supervisor_en_patterns, 1):
            match = re.search(pattern, test_text, re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                print(f"   模式{j}匹配成功: '{result}'")
                matched = True
                break
        
        if not matched:
            print(f"  ❌ 无匹配")
    
    print("\n" + "=" * 60)
    print(" 优化测试完成")

if __name__ == "__main__":
    test_optimized_supervisor_en_patterns()
