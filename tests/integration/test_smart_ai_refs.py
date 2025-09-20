#!/usr/bin/env python3
"""
基于大模型的智能参考文献提取
解决PDF转MD格式不规范的问题
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append('src')

from pathlib import Path
import re
import json

def test_smart_ai_references():
    """智能AI参考文献提取测试"""
    # 读取缓存的文档
    cache_file = Path("cache/documents/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩_f28c5133e8a3bd43f6c85222b885a8ce.md")
    
    if not cache_file.exists():
        print(f"❌ 缓存文件不存在: {cache_file}")
        return
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"📄 文档长度: {len(text):,} 字符")
    
    # 定位参考文献部分
    print("🔍 定位参考文献区域...")
    ref_section = locate_references_section(text)
    
    if not ref_section:
        print("❌ 未找到参考文献区域")
        return
    
    print(f"📍 参考文献区域长度: {len(ref_section):,} 字符")
    
    # 使用智能AI提取
    extract_with_smart_ai(ref_section)

def locate_references_section(text):
    """智能定位参考文献区域"""
    # 多种模式查找参考文献标题
    patterns = [
        r'#+\s*参考文献\s*\n',
        r'参考文献\s*\n',
        r'References\s*\n',
        r'REFERENCES\s*\n',
        r'Bibliography\s*\n'
    ]
    
    ref_start = -1
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            ref_start = match.start()
            print(f" 找到参考文献标题: {match.group().strip()}")
            break
    
    if ref_start == -1:
        print("⚠️ 未找到标准参考文献标题，尝试智能搜索...")
        # 搜索第一个参考文献条目
        first_ref_patterns = [
            r'［1］',
            r'\[1\]',
            r'^\s*1\.',
            r'^\s*\(1\)'
        ]
        
        for pattern in first_ref_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                # 向前搜索可能的标题
                before_text = text[max(0, match.start()-200):match.start()]
                if '参考文献' in before_text or 'References' in before_text:
                    ref_start = max(0, match.start()-200)
                    print(f" 通过第一个参考文献反推找到区域")
                    break
                else:
                    ref_start = match.start()
                    print(f" 直接从第一个参考文献开始")
                    break
    
    if ref_start == -1:
        return None
    
    # 返回从参考文献开始到文档结尾的部分
    return text[ref_start:]

def extract_with_smart_ai(ref_text):
    """使用智能AI提取参考文献"""
    try:
        from thesis_inno_eval.ai_client import get_ai_client
        
        print("🤖 初始化AI客户端...")
        ai_client = get_ai_client()
        
        # 分段处理长文本
        chunks = split_text_intelligently(ref_text)
        print(f"📝 分为 {len(chunks)} 个段落处理")
        
        all_references = []
        
        for i, chunk in enumerate(chunks):
            print(f"🔄 处理第 {i+1}/{len(chunks)} 段...")
            
            # 构建智能提示词
            prompt = build_smart_extraction_prompt(chunk, i+1, len(chunks))
            
            # 发送请求
            response = ai_client.send_message(prompt)
            
            if response and hasattr(response, 'content'):
                # 解析JSON响应
                refs = parse_ai_response(response.content)
                if refs:
                    all_references.extend(refs)
                    print(f"    提取到 {len(refs)} 条参考文献")
                else:
                    print(f"   ⚠️ 本段未提取到参考文献")
            else:
                print(f"   ❌ AI响应为空")
        
        # 去重和排序
        final_refs = deduplicate_and_sort(all_references)
        
        print(f"\n📊 最终提取结果:")
        print(f"   参考文献总数: {len(final_refs)} 条")
        
        if final_refs:
            print(f"\n📋 前10条参考文献:")
            for i, ref in enumerate(final_refs[:10]):
                print(f"   [{ref['number']}] {ref['content'][:100]}...")
            
            print(f"\n📋 最后5条参考文献:")
            for ref in final_refs[-5:]:
                print(f"   [{ref['number']}] {ref['content'][:100]}...")
                
            # 检查编号完整性
            check_completeness(final_refs)
        else:
            print("   ❌ 没有提取到有效的参考文献")
            
    except Exception as e:
        print(f"❌ AI提取失败: {e}")

def split_text_intelligently(text, max_chars=8000):
    """智能分割文本"""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_pos = 0
    
    while current_pos < len(text):
        end_pos = min(current_pos + max_chars, len(text))
        
        # 在段落边界分割
        if end_pos < len(text):
            # 向后查找合适的分割点
            for i in range(end_pos, min(end_pos + 500, len(text))):
                if text[i:i+2] == '\n\n' or (text[i] == '\n' and re.match(r'［\d+］', text[i+1:i+10])):
                    end_pos = i
                    break
        
        chunk = text[current_pos:end_pos]
        if chunk.strip():
            chunks.append(chunk)
        
        current_pos = end_pos
    
    return chunks

def build_smart_extraction_prompt(text, chunk_num, total_chunks):
    """构建智能提取提示词"""
    prompt = f"""你是一个专业的学术文献处理专家。请从以下文本中提取所有参考文献条目。

**重要说明：**
1. 这是第 {chunk_num}/{total_chunks} 段文本
2. 文本可能包含PDF转换错误、格式不规范等问题
3. 参考文献编号可能使用全角字符：［1］、［2］等
4. 参考文献可能跨行显示或格式混乱
5. 需要智能识别和重构完整的参考文献条目

**提取要求：**
1. 识别所有参考文献条目，包括格式不规范的
2. 重构每个条目为完整、规范的格式
3. 保持原有编号（如果有的话）
4. 提取完整信息：作者、标题、期刊/会议、年份、页码等
5. 清理多余空白、换行和格式错误

**输出格式：**
请以JSON数组格式输出，每个参考文献为一个对象：
```json
[
  {{
    "number": "1",
    "content": "作者名. 文章标题[J]. 期刊名, 年份, 卷(期): 页码.",
    "type": "journal|conference|book|other",
    "confidence": 0.95
  }}
]
```

**文本内容：**
{text}

请开始提取："""
    
    return prompt

def parse_ai_response(content):
    """解析AI响应"""
    try:
        # 尝试直接解析JSON
        if content.strip().startswith('['):
            return json.loads(content)
        
        # 查找JSON块
        json_match = re.search(r'```json\s*(\[.*?\])\s*```', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # 查找简单的JSON数组
        json_match = re.search(r'(\[.*?\])', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # 如果没有JSON格式，尝试解析文本格式
        return parse_text_response(content)
        
    except json.JSONDecodeError as e:
        print(f"   ⚠️ JSON解析失败: {e}")
        return parse_text_response(content)

def parse_text_response(content):
    """解析文本格式的响应"""
    references = []
    lines = content.split('\n')
    
    current_ref = ""
    ref_number = None
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_ref and ref_number:
                references.append({
                    "number": ref_number,
                    "content": current_ref.strip(),
                    "type": "unknown",
                    "confidence": 0.8
                })
                current_ref = ""
                ref_number = None
            continue
        
        # 检查是否是新的参考文献开始
        number_match = re.match(r'^\s*(?:［(\d+)］|\[(\d+)\]|(\d+)\.)', line)
        if number_match:
            # 保存之前的参考文献
            if current_ref and ref_number:
                references.append({
                    "number": ref_number,
                    "content": current_ref.strip(),
                    "type": "unknown", 
                    "confidence": 0.8
                })
            
            # 开始新的参考文献
            ref_number = number_match.group(1) or number_match.group(2) or number_match.group(3)
            current_ref = line
        else:
            # 继续当前参考文献
            if current_ref:
                current_ref += " " + line
    
    # 保存最后一个参考文献
    if current_ref and ref_number:
        references.append({
            "number": ref_number,
            "content": current_ref.strip(),
            "type": "unknown",
            "confidence": 0.8
        })
    
    return references

def deduplicate_and_sort(references):
    """去重和排序"""
    # 按编号去重
    seen_numbers = set()
    unique_refs = []
    
    for ref in references:
        if ref['number'] not in seen_numbers:
            seen_numbers.add(ref['number'])
            unique_refs.append(ref)
    
    # 按编号排序
    try:
        unique_refs.sort(key=lambda x: int(x['number']))
    except ValueError:
        # 如果编号不是纯数字，按字符串排序
        unique_refs.sort(key=lambda x: x['number'])
    
    return unique_refs

def check_completeness(references):
    """检查编号完整性"""
    numbers = [int(ref['number']) for ref in references if ref['number'].isdigit()]
    
    if not numbers:
        print("   ⚠️ 无法检查编号完整性（编号非数字）")
        return
    
    min_num = min(numbers)
    max_num = max(numbers)
    expected = set(range(min_num, max_num + 1))
    actual = set(numbers)
    
    missing = expected - actual
    if missing:
        print(f"   ⚠️ 缺失编号: {sorted(missing)}")
    else:
        print(f"    编号完整: {min_num}-{max_num}")
    
    duplicates = len(numbers) - len(actual)
    if duplicates > 0:
        print(f"   ⚠️ 重复编号: {duplicates} 个")

if __name__ == '__main__':
    test_smart_ai_references()
