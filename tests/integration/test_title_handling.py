#!/usr/bin/env python3
"""
测试头衔保留问题的演示
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import re

# 当前的supervisor_en正则表达式模式
current_patterns = [
    r'(?:Supervisor|SUPERVISOR)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Advisor|ADVISOR)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Directed\s+by|DIRECTED\s+BY)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Under\s+the\s+guidance\s+of)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Prof\.|Professor|Dr\.)\s+([A-Za-z\s]+?)(?:\n|$|[，,])',
]

# 测试用例
test_cases = [
    "Supervisor: Dr. John Smith",
    "Supervisor: Professor Mary Johnson", 
    "Advisor: Dr. Michael Brown",
    "Advisor: Professor Lisa Wang",
    "Prof. Kevin Zhang",
    "Dr. Jennifer Liu",
    "Professor David Wilson",
]

def test_title_handling():
    """测试头衔处理的问题"""
    print("🧪 测试头衔保留问题")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test_text}")
        
        for j, pattern in enumerate(current_patterns, 1):
            match = re.search(pattern, test_text, re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                print(f"   模式{j} 匹配: '{result}'")
                
                # 分析头衔是否保留
                if 'Dr.' in result or 'Professor' in result or 'Prof.' in result:
                    print(f"     头衔已保留")
                else:
                    print(f"    ❌ 头衔丢失")
                break
        else:
            print(f"  ❌ 无匹配")
    
    print("\n" + "=" * 50)
    print("📊 头衔处理分析完成")

if __name__ == "__main__":
    test_title_handling()
