#!/usr/bin/env python3
"""
调试参考文献提取问题
"""

import re
from pathlib import Path

def debug_references_extraction():
    """调试参考文献提取问题"""
    # 读取缓存的markdown文件
    cache_file = Path("cache/documents/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩_f28c5133e8a3bd43f6c85222b885a8ce.md")
    
    if not cache_file.exists():
        print(f"❌ 缓存文件不存在: {cache_file}")
        return
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"📄 文档总长度: {len(text):,} 字符")
    
    # 查找所有"参考文献"位置
    ref_positions = []
    for match in re.finditer(r'参考文献', text):
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 100)
        context = text[start:end].replace('\n', '\\n')
        ref_positions.append({
            'position': match.start(),
            'context': context
        })
    
    print(f"\n🔍 找到 {len(ref_positions)} 个'参考文献'位置:")
    for i, pos in enumerate(ref_positions):
        print(f"   位置 {i+1}: 字符 {pos['position']:,}")
        print(f"   上下文: {pos['context']}")
        print()
    
    # 测试当前的正则表达式模式
    ref_patterns = [
        r'参考文献\s*([\s\S]*?)(?=\n\s*(?:缩略词表|文献综述|致谢|附录)|$)',
        r'参考文献\s*\n([\s\S]*?)(?=\n\s*(?:缩略词表|文献综述|致谢|附录)|$)',
        r'REFERENCES?\s*([\s\S]*?)(?=\n\s*(?:ACKNOWLEDGMENT|APPENDIX|文献综述)|$)',
        r'REFERENCES?\s*\n([\s\S]*?)(?=\n\s*(?:ACKNOWLEDGMENT|APPENDIX|文献综述)|$)',
        r'Bibliography\s*([\s\S]*?)(?=\n\s*(?:ACKNOWLEDGMENT|APPENDIX|文献综述)|$)',
    ]
    
    print("🧪 测试正则表达式模式:")
    for i, pattern in enumerate(ref_patterns):
        print(f"\n模式 {i+1}: {pattern}")
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
        print(f"   匹配数量: {len(matches)}")
        
        for j, match in enumerate(matches):
            ref_text = match.group(1).strip()
            print(f"   匹配 {j+1}: 位置 {match.start():,}-{match.end():,}, 长度 {len(ref_text)} 字符")
            if len(ref_text) > 0:
                # 显示前200字符
                preview = ref_text[:200].replace('\n', '\\n')
                print(f"   内容预览: {preview}...")
    
    # 手动提取参考文献部分（从第15175行开始）
    print(f"\n🎯 手动提取参考文献部分:")
    lines = text.split('\n')
    ref_start_line = None
    
    for i, line in enumerate(lines):
        if '## 参考文献' in line:
            ref_start_line = i
            print(f"   找到参考文献标题在第 {i+1} 行")
            break
    
    if ref_start_line:
        # 提取从参考文献开始到文档结尾的内容
        ref_lines = lines[ref_start_line+1:]  # 跳过标题行
        
        # 寻找结束位置
        end_markers = ['缩略词表', '文献综述', '致谢', 'ACKNOWLEDGMENT', 'APPENDIX', '附录', '作者简介', '个人简历']
        end_line = len(ref_lines)
        
        for i, line in enumerate(ref_lines):
            for marker in end_markers:
                if marker in line:
                    end_line = i
                    print(f"   找到结束标记 '{marker}' 在参考文献后第 {i+1} 行")
                    break
            if end_line < len(ref_lines):
                break
        
        ref_text = '\n'.join(ref_lines[:end_line])
        print(f"   手动提取的参考文献长度: {len(ref_text)} 字符")
        
        # 显示前500字符
        if len(ref_text) > 0:
            preview = ref_text[:500]
            print(f"   内容预览:\n{preview}")
            
            # 尝试解析参考文献条目
            print(f"\n📋 解析参考文献条目:")
            
            # 测试不同的解析模式
            patterns = [
                (r'\[(\d+)\]\s*([^\[]+?)(?=\[\d+\]|$)', '[数字]格式'),
                (r'^\[(\d+)\]\s*([^\n]+)', '行首[数字]格式'),
                (r'［(\d+)］\s*([^［]+?)(?=［\d+］|$)', '［数字］格式'),
            ]
            
            for pattern, desc in patterns:
                matches = re.findall(pattern, ref_text, re.MULTILINE | re.DOTALL)
                print(f"   {desc}: {len(matches)} 条")
                if matches:
                    for i, match in enumerate(matches[:3]):  # 显示前3条
                        if isinstance(match, tuple):
                            ref_num, ref_content = match
                            ref_preview = ref_content.strip()[:100]
                            print(f"     [{ref_num}] {ref_preview}...")
                    if len(matches) > 3:
                        print(f"     ... 还有 {len(matches)-3} 条")
                    break

if __name__ == '__main__':
    debug_references_extraction()
