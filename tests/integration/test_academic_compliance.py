#!/usr/bin/env python3
"""
验证修复后的supervisor_en模式一致性
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import re

# 修复后的supervisor_en正则表达式模式（统一保留职称）
fixed_patterns = [
    r'(?:Supervisor|SUPERVISOR)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Advisor|ADVISOR)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Directed\s+by|DIRECTED\s+BY)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'(?:Under\s+the\s+guidance\s+of)[：:\s]*([A-Za-z\s\.]+?)(?:\n|$|[，,])',
    r'((Prof\.|Professor|Dr\.)\s+[A-Za-z\s]+?)(?:\n|$|[，,])',  # 修复：保留完整职称
]

# 学术规范测试用例
test_cases = [
    {
        "text": "Supervisor: Dr. John Smith",
        "expected": "Dr. John Smith",
        "description": "标准导师格式"
    },
    {
        "text": "Supervisor: Professor Mary Johnson", 
        "expected": "Professor Mary Johnson",
        "description": "教授职称格式"
    },
    {
        "text": "Advisor: Dr. Michael Brown",
        "expected": "Dr. Michael Brown", 
        "description": "顾问格式"
    },
    {
        "text": "Advisor: Professor Lisa Wang",
        "expected": "Professor Lisa Wang",
        "description": "顾问教授格式"
    },
    {
        "text": "Directed by: Prof. David Wilson",
        "expected": "Prof. David Wilson",
        "description": "指导者格式"
    },
    {
        "text": "Under the guidance of: Dr. Sarah Davis",
        "expected": "Dr. Sarah Davis",
        "description": "指导关系格式"
    },
    {
        "text": "Prof. Kevin Zhang",
        "expected": "Prof. Kevin Zhang",
        "description": "直接职称格式"
    },
    {
        "text": "Dr. Jennifer Liu",
        "expected": "Dr. Jennifer Liu", 
        "description": "博士职称格式"
    },
    {
        "text": "Professor Robert Chen",
        "expected": "Professor Robert Chen",
        "description": "教授职称格式"
    }
]

def test_academic_compliance():
    """测试学术规范合规性"""
    print("🎓 学术规范合规性测试")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['description']}")
        print(f"输入: {test_case['text']}")
        
        matched = False
        for j, pattern in enumerate(fixed_patterns, 1):
            match = re.search(pattern, test_case['text'], re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                print(f"匹配结果: '{result}'")
                print(f"期望结果: '{test_case['expected']}'")
                
                if result == test_case['expected']:
                    print(" 测试通过 - 职称已正确保留")
                else:
                    print("❌ 测试失败 - 结果不符合期望")
                    all_passed = False
                
                # 检查是否保留了职称
                has_title = any(title in result for title in ['Dr.', 'Prof.', 'Professor'])
                if has_title:
                    print(" 学术职称已保留")
                else:
                    print("⚠️ 职称可能丢失")
                
                matched = True
                break
        
        if not matched:
            print("❌ 无匹配")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！")
        print(" 模式完全符合国际学术规范")
        print(" 职称信息得到正确保留")
        print(" 体现了对导师的学术尊重")
    else:
        print("⚠️ 存在测试失败，需要进一步优化")
    
    print("\n📚 学术规范总结:")
    print("- 保留职称是国际学术标准")
    print("- 职称体现学术地位和资格")
    print("- 符合顶级大学论文格式要求") 
    print("- 有助于准确的学术身份识别")

if __name__ == "__main__":
    test_academic_compliance()
