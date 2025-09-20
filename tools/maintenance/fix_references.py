#!/usr/bin/env python3
"""
修正51177论文的参考文献提取逻辑
"""

import re
import json
from pathlib import Path

def extract_correct_references():
    """正确提取参考文献，排除其他章节"""
    
    project_root = Path(__file__).parent
    md_file = project_root / "cache" / "documents" / "51177_b6ac1c475108811bd4a31a6ebcd397df.md"
    
    print("🔧 修正参考文献提取逻辑")
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    lines = content.split('\n')
    
    # 找到真正的参考文献开始位置（第一个[1]条目）
    ref_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('[1]') and 'Costanza' in line:
            ref_start = i
            print(f"📍 参考文献实际开始: 第{i+1}行")
            break
    
    if not ref_start:
        print("❌ 未找到参考文献开始位置")
        return
    
    # 找到参考文献结束 (遇到其他章节标题)
    ref_end = len(lines)
    end_patterns = [
        '攻读博士学位', '致谢', '个人简历', '发表', '成果', 
        '附录', '声明', '简历', '会议', '项目', '作者简介'
    ]
    
    for i, line in enumerate(lines[ref_start:], ref_start):
        line = line.strip()
        if line and not re.match(r'^\[\d+\]', line):  # 不是参考文献条目
            for pattern in end_patterns:
                if pattern in line and len(line) < 100:
                    ref_end = i
                    print(f"📍 参考文献结束: 第{i}行 - '{line}'")
                    break
            if ref_end != len(lines):
                break
    
    # 提取参考文献条目
    ref_lines = lines[ref_start:ref_end]
    references = []
    current_ref = ""
    
    for line in ref_lines:
        line = line.strip()
        
        # 检查是否是新的参考文献条目
        if re.match(r'^\[\d+\]', line):
            if current_ref:
                references.append(current_ref.strip())
            current_ref = line
        elif line and current_ref:
            current_ref += " " + line
        elif not line and current_ref:
            # 空行，结束当前条目
            references.append(current_ref.strip())
            current_ref = ""
    
    # 添加最后一个条目
    if current_ref:
        references.append(current_ref.strip())
    
    # 清理参考文献条目
    cleaned_references = []
    for ref in references:
        # 移除多余的空格和换行
        ref = ' '.join(ref.split())
        if len(ref) > 20:  # 过滤太短的条目
            cleaned_references.append(ref)
    
    print(f" 提取到 {len(cleaned_references)} 条参考文献")
    
    # 显示统计
    ref_section_text = '\n'.join(ref_lines)
    actual_ref_chars = len(ref_section_text)
    
    print(f"📊 修正后统计:")
    print(f"   参考文献字符数: {actual_ref_chars:,}")
    print(f"   参考文献条目数: {len(cleaned_references)}")
    print(f"   平均条目长度: {actual_ref_chars/len(cleaned_references):.1f} 字符")
    
    # 显示前3条
    print(f"\n📝 前3条参考文献:")
    for i, ref in enumerate(cleaned_references[:3]):
        print(f"   [{i+1}] {ref}")
    
    # 更新JSON文件
    result_file = project_root / "data" / "output" / "51177_extracted_info.json"
    
    if result_file.exists():
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加正确的参考文献
        data['ReferenceList'] = cleaned_references
        
        # 重新计算统计
        total_fields = 24
        extracted_fields = len([k for k, v in data.items() if v and str(v).strip()])
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 已更新JSON文件:")
        print(f"   新增字段: ReferenceList ({len(cleaned_references)} 条)")
        print(f"   总字段数: {extracted_fields}")
        print(f"   完整度: {extracted_fields/total_fields*100:.1f}%")
    
    return cleaned_references

if __name__ == "__main__":
    extract_correct_references()

