#!/usr/bin/env python3
"""
调试参考文献提取的详细过程
"""

import re
from pathlib import Path

def debug_detailed_extraction():
    """详细调试参考文献提取过程"""
    
    cache_file = Path("cache/documents/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩_f28c5133e8a3bd43f6c85222b885a8ce.md")
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 手动提取参考文献部分
    lines = text.split('\n')
    ref_start_line = None
    
    for i, line in enumerate(lines):
        if '## 参考文献' in line:
            ref_start_line = i
            break
    
    if ref_start_line:
        ref_lines = lines[ref_start_line+1:]
        ref_text = '\n'.join(ref_lines)
        
        print(f"📄 参考文献部分长度: {len(ref_text)} 字符")
        
        # 测试修复后的模式
        pattern = r'［\s*(\d+)\s*］([\s\S]*?)(?=［\s*\d+\s*］|$)'
        matches = re.findall(pattern, ref_text, re.MULTILINE | re.DOTALL)
        
        print(f"\n🔍 全角括号模式匹配结果: {len(matches)} 条")
        
        references = []
        for i, match in enumerate(matches[:5]):  # 只看前5条
            if isinstance(match, tuple) and len(match) >= 2:
                ref_num, ref_content = match[0], match[1]
                ref = f"［{ref_num}］ {ref_content.strip()}"
                
                print(f"\n匹配 {i+1}:")
                print(f"   编号: {ref_num}")
                print(f"   内容长度: {len(ref_content)} 字符")
                print(f"   内容预览: {ref_content[:200].replace(chr(10), ' ')}")
                print(f"   完整引用长度: {len(ref)} 字符")
                
                # 应用过滤条件
                if len(ref) > 20:
                    ref = re.sub(r'\s+', ' ', ref).strip()
                    references.append(ref)
                    print(f"    通过过滤，最终长度: {len(ref)} 字符")
                else:
                    print(f"   ❌ 被过滤：长度 {len(ref)} <= 20")
        
        print(f"\n📊 最终提取结果: {len(references)} 条")
        
        # 显示最终结果的前3条
        for i, ref in enumerate(references[:3]):
            print(f"\n最终引用 {i+1}: {ref[:150]}...")

if __name__ == '__main__':
    debug_detailed_extraction()

