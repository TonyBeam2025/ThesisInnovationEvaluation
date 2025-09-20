#!/usr/bin/env python3
"""
简化的AI参考文献提取测试
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append('src')

from pathlib import Path
import re

def test_ai_references_simple():
    """简单测试AI参考文献提取"""
    # 读取缓存的文档
    cache_file = Path("cache/documents/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩_f28c5133e8a3bd43f6c85222b885a8ce.md")
    
    if not cache_file.exists():
        print(f"❌ 缓存文件不存在: {cache_file}")
        return
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"📄 文档长度: {len(text):,} 字符")
    
    # 定位参考文献部分
    print("🔍 定位参考文献部分...")
    
    # 查找"## 参考文献"
    ref_start = text.find("## 参考文献")
    if ref_start == -1:
        ref_start = text.find("参考文献")
    
    if ref_start == -1:
        print("❌ 未找到参考文献标题")
        return
    
    # 提取参考文献部分（从标题到文档结尾）
    ref_text = text[ref_start:]
    print(f"📍 参考文献部分长度: {len(ref_text):,} 字符")
    
    # 测试AI提取
    test_ai_extraction(ref_text[:10000])  # 限制为10k字符进行测试

def test_ai_extraction(ref_text):
    """测试AI提取功能"""
    try:
        from thesis_inno_eval.ai_client import get_ai_client
        
        print("🤖 初始化AI客户端...")
        ai_client = get_ai_client()
        
        prompt = f"""请从以下参考文献文本中提取所有参考文献条目。

要求：
1. 每个参考文献条目应该是完整的一条记录
2. 保持原有的编号格式（如［1］、[1]、1.等）
3. 清理多余的空白字符和换行符
4. 每条参考文献应该包含：作者、标题、期刊/会议/出版社、年份等信息
5. 输出格式：每行一条参考文献，不需要额外说明

参考文献文本：
{ref_text}

请提取所有参考文献条目："""

        print("🔥 发送AI请求...")
        response = ai_client.send_message(prompt)
        
        if response and hasattr(response, 'content'):
            content = response.content.strip()
            print(f"📄 AI响应长度: {len(content)} 字符")
            
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
            
            print(f"📊 AI提取结果:")
            print(f"   参考文献总数: {len(references)} 条")
            
            if references:
                print(f"\n📋 前5条参考文献:")
                for i, ref in enumerate(references[:5]):
                    print(f"   {i+1}. {ref[:100]}...")
                    
                if len(references) > 5:
                    print(f"   ... 还有 {len(references)-5} 条")
            else:
                print("   ❌ 没有提取到有效的参考文献")
                print("🔍 AI原始响应:")
                print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print("❌ AI响应为空")
            
    except Exception as e:
        print(f"❌ AI提取失败: {e}")

def is_valid_reference(line):
    """检查是否是有效的参考文献条目"""
    # 基本长度检查
    if len(line) < 20:
        return False
    
    # 检查是否包含编号格式（包括全角字符）
    has_number = bool(re.match(r'^\s*(?:［\d+］|\[\d+\]|\d+\.|（\d+）|\(\d+\))', line))
    
    # 检查是否包含期刊、会议、出版社等关键词
    has_publication = any(keyword in line for keyword in [
        'Journal', 'Proceedings', 'Conference', 'IEEE', 'ACM', 'Optics',
        '期刊', '会议', '学报', '大学学报', '论文集', '出版社', 'DOI', 'Ｊ］', 'Ｃ］'
    ])
    
    # 检查是否包含年份（包括全角数字）
    has_year = bool(re.search(r'(?:19|20|１９|２０)\d{2}', line))
    
    # 至少满足编号+年份，或者编号+出版物
    return has_number and (has_year or has_publication)

if __name__ == '__main__':
    test_ai_references_simple()
