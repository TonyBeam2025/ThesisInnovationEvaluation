#!/usr/bin/env python3
"""
测试论文标题提取 - 专门解决封面标题问题
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
import re
from pathlib import Path

def extract_thesis_title(text):
    """提取论文真正的标题"""
    
    # 论文标题提取模式
    title_patterns = [
        # 匹配独立行的论文标题 - 包含常见论文关键词
        r'\n([^\n\r]*(?:技术|研究|分析|系统|方法|理论|应用|设计|开发|实现|性能|建模|优化|评估|探索|探讨)[^\n\r]*)\n',
        # 匹配标题格式
        r'\n([^\n\r]*(?:的|在|基于|关于)[^\n\r]*(?:研究|分析|应用|设计|系统|方法)[^\n\r]*)\n',
        # 匹配力学相关标题
        r'\n([^\n\r]*(?:力学|韧带|关节|材料|机械)[^\n\r]*(?:性能|特性|分析|研究)[^\n\r]*)\n',
    ]
    
    # 找到所有可能的标题
    candidates = []
    for pattern in title_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            title = match.strip()
            # 过滤掉不可能是标题的内容
            if (len(title) > 8 and len(title) < 100 and 
                not any(word in title for word in ['声明', '导师', '完成', '日期', '学号', '姓名', '作者', '签名', '承担', '法律'])):
                candidates.append(title)
    
    # 从文档开头查找标题
    lines = text.split('\n')[:50]  # 查看前50行
    for line in lines:
        line = line.strip()
        if (len(line) > 8 and len(line) < 100 and 
            any(keyword in line for keyword in ['技术', '研究', '分析', '系统', '方法', '理论', '应用', '设计', '开发', '实现', '性能', '力学', '韧带', '关节']) and
            not any(word in line for word in ['#', '**', '源文件', '转换', '学校', '学号', '声明', '导师', '完成', '日期', '姓名', '作者', '签名'])):
            candidates.append(line)
    
    return candidates

def test_title_extraction():
    """测试标题提取功能"""
    
    print("=== 测试论文标题提取 ===\n")
    
    # 测试文档
    md_file = r"cache\documents\1_工程力学_21703014_刘力夫_LW_76c5b96231292b26dbeab5065ab7f040.md"
    if not os.path.exists(md_file):
        print(f"❌ MD文档文件不存在: {md_file}")
        return
    
    print(f"📄 读取MD文档: {md_file}")
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f" 文档读取成功，长度: {len(text):,} 字符")
        
        # 提取候选标题
        candidates = extract_thesis_title(text)
        
        print(f"\n🔍 找到 {len(candidates)} 个候选标题:")
        for i, title in enumerate(candidates, 1):
            print(f"   {i:2d}. {title}")
        
        # 显示文档开头内容用于分析
        print(f"\n📋 文档开头内容（前20行）:")
        lines = text.split('\n')[:20]
        for i, line in enumerate(lines, 1):
            print(f"   {i:2d}: {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 设置环境
    os.chdir(r"c:\MyProjects\thesis_Inno_Eval")
    
    # 运行测试
    success = test_title_extraction()
    
    if success:
        print(f"\n 测试完成")
    else:
        print(f"\n❌ 测试失败")
