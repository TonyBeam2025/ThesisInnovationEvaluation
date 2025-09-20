#!/usr/bin/env python3
"""
分析51177论文参考文献部分异常长度的问题
"""

import re
from pathlib import Path

def analyze_references_section():
    """分析参考文献部分的异常长度"""
    
    project_root = Path(__file__).parent
    md_file = project_root / "cache" / "documents" / "51177_b6ac1c475108811bd4a31a6ebcd397df.md"
    
    print("🔍 分析参考文献部分异常长度问题")
    print("=" * 60)
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    lines = content.split('\n')
    total_chars = len(content)
    
    print(f"📊 文件基本信息:")
    print(f"   总字符数: {total_chars:,}")
    print(f"   总行数: {len(lines):,}")
    
    # 找到参考文献开始位置
    ref_start_line = None
    ref_patterns = ['参考文献', 'References', '## 参考文献']
    
    for i, line in enumerate(lines):
        for pattern in ref_patterns:
            if pattern in line and len(line.strip()) < 50:  # 避免匹配正文中的词
                ref_start_line = i
                print(f"   参考文献开始: 第{i+1}行 - '{line.strip()}'")
                break
        if ref_start_line is not None:
            break
    
    if ref_start_line is None:
        print("❌ 未找到参考文献开始位置")
        return
    
    # 计算参考文献部分的统计信息
    ref_section = '\n'.join(lines[ref_start_line:])
    ref_chars = len(ref_section)
    ref_lines = len(lines) - ref_start_line
    
    print(f"\n📖 参考文献部分统计:")
    print(f"   字符数: {ref_chars:,}")
    print(f"   行数: {ref_lines:,}")
    print(f"   占总文档比例: {ref_chars/total_chars*100:.1f}%")
    
    # 分析参考文献条目
    ref_entries = []
    current_entry = ""
    
    for i, line in enumerate(lines[ref_start_line+1:], ref_start_line+2):
        line = line.strip()
        
        # 检查是否是新的参考文献条目（以[数字]开头）
        if re.match(r'^\[\d+\]', line):
            if current_entry:
                ref_entries.append(current_entry)
            current_entry = line
        elif line and current_entry:  # 继续当前条目
            current_entry += " " + line
        elif not line and current_entry:  # 空行，结束当前条目
            ref_entries.append(current_entry)
            current_entry = ""
    
    # 添加最后一个条目
    if current_entry:
        ref_entries.append(current_entry)
    
    print(f"\n🔢 参考文献条目分析:")
    print(f"   识别到的条目数: {len(ref_entries)}")
    
    if ref_entries:
        # 分析条目长度
        entry_lengths = [len(entry) for entry in ref_entries]
        avg_length = sum(entry_lengths) / len(entry_lengths)
        max_length = max(entry_lengths)
        min_length = min(entry_lengths)
        
        print(f"   平均条目长度: {avg_length:.1f} 字符")
        print(f"   最长条目: {max_length} 字符")
        print(f"   最短条目: {min_length} 字符")
        
        # 显示前5个条目
        print(f"\n📝 前5个参考文献条目:")
        for i, entry in enumerate(ref_entries[:5]):
            preview = entry[:100] + "..." if len(entry) > 100 else entry
            print(f"   [{i+1}] {preview}")
        
        # 显示最长的3个条目
        sorted_entries = sorted(zip(ref_entries, entry_lengths), key=lambda x: x[1], reverse=True)
        print(f"\n📏 最长的3个条目:")
        for i, (entry, length) in enumerate(sorted_entries[:3]):
            preview = entry[:150] + "..." if len(entry) > 150 else entry
            print(f"   长度{length}: {preview}")
    
    # 检查是否有重复内容
    print(f"\n🔍 检查内容重复:")
    
    # 查找可能的重复段落
    ref_content_lines = lines[ref_start_line:]
    
    # 统计重复行
    line_counts = {}
    for line in ref_content_lines:
        line = line.strip()
        if len(line) > 20:  # 只统计有意义的行
            line_counts[line] = line_counts.get(line, 0) + 1
    
    repeated_lines = {line: count for line, count in line_counts.items() if count > 1}
    
    if repeated_lines:
        print(f"   发现重复行: {len(repeated_lines)} 种")
        print(f"   重复最多的行:")
        sorted_repeats = sorted(repeated_lines.items(), key=lambda x: x[1], reverse=True)
        for line, count in sorted_repeats[:5]:
            preview = line[:80] + "..." if len(line) > 80 else line
            print(f"     重复{count}次: {preview}")
    else:
        print(f"   未发现明显的重复行")
    
    # 分析参考文献后是否还有其他内容
    print(f"\n📋 内容结构分析:")
    
    # 查找参考文献后的章节
    post_ref_sections = []
    for i, line in enumerate(lines[ref_start_line+1:], ref_start_line+2):
        line = line.strip()
        if line and not re.match(r'^\[\d+\]', line) and not line.startswith('http') and len(line) < 100:
            # 可能的章节标题
            if any(keyword in line for keyword in ['攻读', '致谢', '个人简历', '发表', '成果', '附录']):
                post_ref_sections.append((i, line))
    
    if post_ref_sections:
        print(f"   参考文献后的章节:")
        for line_no, section in post_ref_sections:
            print(f"     第{line_no}行: {section}")
    
    # 给出诊断结论
    print(f"\n" + "=" * 60)
    print(f"🎯 诊断结论:")
    
    if ref_chars > 50000:  # 参考文献超过5万字符
        print(f"   ⚠️ 参考文献部分异常长 ({ref_chars:,} 字符)")
        
        possible_reasons = []
        
        if len(ref_entries) > 300:
            possible_reasons.append(f"参考文献条目过多 ({len(ref_entries)} 条)")
        
        if avg_length > 500:
            possible_reasons.append(f"单条目平均长度过长 ({avg_length:.0f} 字符)")
        
        if repeated_lines:
            possible_reasons.append(f"存在重复内容 ({len(repeated_lines)} 种重复)")
        
        if post_ref_sections:
            possible_reasons.append("可能包含了其他章节内容")
        
        if possible_reasons:
            print(f"   可能原因:")
            for reason in possible_reasons:
                print(f"     - {reason}")
        
        # 建议的修正方案
        print(f"\n💡 建议修正方案:")
        if len(ref_entries) > 200:
            print(f"     - 检查是否误将正文内容包含在参考文献中")
        if post_ref_sections:
            correct_ref_end = post_ref_sections[0][0] - 1
            print(f"     - 参考文献应该结束在第{correct_ref_end}行")
            
            # 重新计算正确的参考文献长度
            correct_ref_section = '\n'.join(lines[ref_start_line:correct_ref_end])
            correct_ref_chars = len(correct_ref_section)
            print(f"     - 修正后参考文献长度: {correct_ref_chars:,} 字符")
    else:
        print(f"    参考文献长度正常")

if __name__ == "__main__":
    analyze_references_section()

