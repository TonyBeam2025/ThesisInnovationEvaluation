#!/usr/bin/env python3
"""
修复后的参考文献提取功能
"""

import re
from typing import List, Optional
from pathlib import Path

def extract_references_with_ai_fixed(text: str, ai_client=None) -> List[str]:
    """使用AI智能提取参考文献的修复版本"""
    print("   🔍 启动AI智能参考文献解析...")
    
    # 定位参考文献部分
    ref_text = locate_references_section(text)
    
    if not ref_text:
        print("   ⚠️ 未找到参考文献部分")
        return []
    
    print(f"   📍 找到参考文献部分，长度: {len(ref_text)} 字符")
    
    # 使用AI智能提取参考文献条目
    references = extract_references_with_ai(ref_text, ai_client)
    
    print(f"    AI提取参考文献: {len(references)} 条")
    return references

def locate_references_section(text: str) -> str:
    """定位参考文献部分"""
    # 查找参考文献标题的多种模式
    ref_patterns = [
        r'(?:^|\n)(?:##\s*)?参考文献\s*\n([\s\S]*?)(?=\n\s*(?:缩略词表|文献综述|致谢|附录|作者简介|个人简历)|$)',
        r'(?:^|\n)(?:##\s*)?REFERENCES?\s*\n([\s\S]*?)(?=\n\s*(?:ACKNOWLEDGMENT|APPENDIX|文献综述|致谢)|$)',
        r'(?:^|\n)(?:##\s*)?Bibliography\s*\n([\s\S]*?)(?=\n\s*(?:ACKNOWLEDGMENT|APPENDIX|文献综述|致谢)|$)',
    ]
    
    for pattern in ref_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
        if matches:
            best_match = max(matches, key=lambda m: len(m.group(1)))
            ref_text = best_match.group(1).strip()
            if len(ref_text) >= 1000:
                return ref_text
    
    # 备用方法：关键词定位
    ref_keywords = ['参考文献', 'References', 'REFERENCES', 'Bibliography']
    for keyword in ref_keywords:
        pos = text.find(keyword)
        if pos != -1:
            remaining_text = text[pos+len(keyword):]
            end_markers = ['缩略词表', '文献综述', '致谢', 'ACKNOWLEDGMENT', 'APPENDIX', '附录', '作者简介', '个人简历']
            end_pos = len(remaining_text)
            
            for marker in end_markers:
                marker_pos = remaining_text.find(marker)
                if marker_pos != -1 and marker_pos < end_pos:
                    end_pos = marker_pos
            
            ref_text = remaining_text[:end_pos]
            if len(ref_text) >= 1000:
                return ref_text
    
    return ""

def extract_references_with_ai(ref_text: str, ai_client=None) -> List[str]:
    """使用AI大模型提取参考文献条目"""
    try:
        # 限制输入长度以避免token超限
        max_length = 50000  # 约50k字符，对应大约12-15k tokens
        if len(ref_text) > max_length:
            print(f"   📏 参考文献内容过长({len(ref_text)}字符)，截取前{max_length}字符")
            ref_text = ref_text[:max_length]
        
        prompt = f"""请从以下参考文献文本中提取所有参考文献条目。

要求：
1. 每个参考文献条目应该是完整的一条记录
2. 保持原有的编号格式（如［1］、[1]、1.等）
3. 清理多余的空白字符和换行符
4. 每条参考文献应该包含：作者、标题、期刊/会议/出版社、年份等信息
5. 如果格式混乱，请智能重组成标准格式
6. 按编号顺序排列
7. 输出格式：每行一条参考文献，不需要额外说明

参考文献文本：
{ref_text}

请提取所有参考文献条目："""

        if ai_client:
            print("   🤖 调用AI大模型提取参考文献...")
            response = ai_client.send_message(prompt)
            
            if response and hasattr(response, 'content'):
                content = response.content.strip()
                
                # 解析AI返回的结果
                references = []
                lines = content.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 检查是否像参考文献条目
                    if is_valid_reference(line):
                        # 清理格式
                        cleaned_ref = re.sub(r'\s+', ' ', line).strip()
                        references.append(cleaned_ref)
                
                print(f"    AI成功提取 {len(references)} 条参考文献")
                return references
            else:
                print("   ⚠️ AI响应为空")
        else:
            print("   ⚠️ AI客户端不可用")
            
    except Exception as e:
        print(f"   ❌ AI提取失败: {e}")
    
    # 备用方法：使用改进的正则表达式
    print("   🔄 使用备用正则表达式方法...")
    return extract_references_fallback(ref_text)

def is_valid_reference(line: str) -> bool:
    """检查是否是有效的参考文献条目"""
    # 基本长度检查
    if len(line) < 20:
        return False
    
    # 检查是否包含编号格式
    has_number = bool(re.match(r'^\s*(?:［\d+］|\[\d+\]|\d+\.|（\d+）|\(\d+\))', line))
    
    # 检查是否包含期刊、会议、出版社等关键词
    has_publication = any(keyword in line for keyword in [
        'Journal', 'Proceedings', 'Conference', 'IEEE', 'ACM', 'Optics',
        '期刊', '会议', '学报', '大学学报', '论文集', '出版社', 'DOI'
    ])
    
    # 检查是否包含年份
    has_year = bool(re.search(r'(?:19|20)\d{2}', line))
    
    # 至少满足编号+年份，或者编号+出版物
    return has_number and (has_year or has_publication)

def extract_references_fallback(ref_text: str) -> List[str]:
    """备用的参考文献提取方法"""
    references = []
    
    # 智能段落分割和重组
    print("   🔧 使用智能段落重组方法...")
    
    # 按空行分割段落
    paragraphs = re.split(r'\n\s*\n', ref_text)
    current_ref = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # 检查是否是新的参考文献开始
        if re.match(r'^\s*(?:［\d+］|\[\d+\]|\d+\.)', para):
            # 保存之前的参考文献
            if current_ref and len(current_ref) > 20:
                cleaned_ref = re.sub(r'\s+', ' ', current_ref).strip()
                references.append(cleaned_ref)
            
            # 开始新的参考文献
            current_ref = para
        else:
            # 继续当前参考文献
            if current_ref:
                current_ref += " " + para
    
    # 添加最后一条参考文献
    if current_ref and len(current_ref) > 20:
        cleaned_ref = re.sub(r'\s+', ' ', current_ref).strip()
        references.append(cleaned_ref)
    
    return references[:100]  # 限制数量

# 测试函数
def test_fixed_extraction():
    """测试修复后的提取功能"""
    cache_file = Path("cache/documents/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩_f28c5133e8a3bd43f6c85222b885a8ce.md")
    
    if not cache_file.exists():
        print(f"❌ 缓存文件不存在: {cache_file}")
        return
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 获取AI客户端
    try:
        import sys
        sys.path.append('src')
        from thesis_inno_eval.ai_client import get_ai_client
        ai_client = get_ai_client()
        print(" AI客户端初始化成功")
    except Exception as e:
        print(f"⚠️ AI客户端初始化失败: {e}")
        ai_client = None
    
    # 测试提取
    references = extract_references_with_ai_fixed(text, ai_client)
    
    print(f"\n📊 测试结果:")
    print(f"   提取到参考文献: {len(references)} 条")
    
    if references:
        print(f"\n📋 前3条参考文献:")
        for i, ref in enumerate(references[:3]):
            print(f"   {i+1}. {ref[:100]}...")

if __name__ == '__main__':
    test_fixed_extraction()

