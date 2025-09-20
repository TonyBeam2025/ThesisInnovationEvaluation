#!/usr/bin/env python3
"""
调试英文导师正则表达式匹配
"""

import re

# 模拟封面文本内容
cover_text = """
Candidate：BI Jiazi

Supervisor： Assoc. Prof. LI Ran




School of Materials Science and Engineering
Beihang University, Beijing, China
"""

print("🔍 调试英文导师正则表达式匹配")
print("=" * 50)

print("封面文本片段:")
print(cover_text)
print("-" * 30)

# 测试不同的正则表达式
patterns = [
    r'Supervisor[：:\s]*([A-Z][A-Za-z\s\.]+?)(?=\n\n|\n\s*\n|School|University)',
    r'Supervisor[：:\s]*((?:Assoc\.\s+)?Prof\.\s+[A-Z]+\s+[A-Z][a-z]+)',
    r'Supervisor[：:\s]*(.*?)(?=\n\n)',
    r'Supervisor[：:\s]*(.+?)(?=\n\n)',
    r'Supervisor[：:\s]*([^\n]+)',
]

for i, pattern in enumerate(patterns, 1):
    print(f"模式 {i}: {pattern}")
    match = re.search(pattern, cover_text, re.MULTILINE)
    if match:
        result = match.group(1).strip()
        print(f"    匹配结果: '{result}'")
    else:
        print(f"   ❌ 无匹配")
    print()

# 测试具体的职称+姓名模式
print("测试职称+姓名模式:")
text_line = "Supervisor： Assoc. Prof. LI Ran"
patterns2 = [
    r'Assoc\.\s+Prof\.\s+([A-Z]+\s+[A-Z][a-z]+)',
    r'(Assoc\.\s+Prof\.\s+[A-Z]+\s+[A-Z][a-z]+)',
    r'Assoc\.\s+Prof\.\s+(.+)',
]

for i, pattern in enumerate(patterns2, 1):
    print(f"模式2-{i}: {pattern}")
    match = re.search(pattern, text_line)
    if match:
        result = match.group(1).strip()
        print(f"    匹配结果: '{result}'")
    else:
        print(f"   ❌ 无匹配")
    print()

