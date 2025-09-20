#!/usr/bin/env python3
"""
参考文献章节识别和格式处理测试
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
import json
import glob
import re
from typing import Dict, Any, List

# 添加源代码路径
current_dir = str(PROJECT_ROOT)
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def test_references_recognition():
    """测试参考文献识别功能"""
    
    print("📚 参考文献章节识别和格式处理测试")
    print("=" * 80)
    
    # 测试用的参考文献文本样例
    test_cases = [
        {
            'name': '标准格式 - 无空格',
            'text': '''
参考文献

[1] 张三, 李四. 机器学习理论与实践[M]. 北京: 清华大学出版社, 2020.
[2] Smith J, Brown K. Deep Learning Applications[J]. Nature, 2021, 589: 123-145.
[3] 王五. 神经网络算法优化研究[D]. 北京: 北京大学, 2019.

致谢
感谢所有帮助过我的人...
'''
        },
        {
            'name': '带空格格式 - 标题有空格',
            'text': '''
参 考 文 献

[1] 张三, 李四. 机器学习理论与实践[M]. 北京: 清华大学出版社, 2020.

[2] Smith J, Brown K. Deep Learning Applications[J]. Nature, 2021, 589: 123-145.


[3] 王五. 神经网络算法优化研究[D]. 北京: 北京大学, 2019.

致谢
'''
        },
        {
            'name': '混合格式 - 不同编号方式',
            'text': '''
参考文献

1. 张三, 李四. 机器学习理论与实践[M]. 北京: 清华大学出版社, 2020.
2. Smith J, Brown K. Deep Learning Applications[J]. Nature, 2021, 589: 123-145.
【3】王五. 神经网络算法优化研究[D]. 北京: 北京大学, 2019.
(4) 赵六. 计算机视觉基础[M]. 上海: 复旦大学出版社, 2018.

致谢
'''
        },
        {
            'name': '英文格式',
            'text': '''
REFERENCES

[1] Zhang S, Li S. Machine Learning Theory and Practice[M]. Beijing: Tsinghua University Press, 2020.
[2] Smith J, Brown K. Deep Learning Applications[J]. Nature, 2021, 589: 123-145.
[3] Wang W. Neural Network Algorithm Optimization Research[D]. Beijing: Peking University, 2019.

ACKNOWLEDGMENT
'''
        },
        {
            'name': '复杂格式 - 多种问题',
            'text': '''
参   考   文   献

[1] 张三, 李四. 机器学习理论与实践[M]. 北京: 清华大学出版社, 2020.


[2] Smith J, Brown K. Deep Learning Applications[J]. 
    Nature, 2021, 589: 123-145.



【3】王五. 神经网络算法优化研究[D]. 北京: 北京大学, 2019.

(4) 赵六. 计算机视觉基础[M]. 
    上海: 复旦大学出版社, 2018.

致   谢
'''
        }
    ]
    
    # 导入改进后的提取器
    try:
        import thesis_inno_eval.extract_sections_with_ai as extract_module
        extractor = extract_module.ThesisExtractorPro()
        ai_available = True
    except Exception as e:
        print(f"⚠️ AI提取器不可用: {e}")
        ai_available = False
    
    # 测试每个样例
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"📖 测试案例 {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        text = test_case['text']
        print(f"📄 原始文本:")
        print(text)
        
        # 简单正则测试
        print(f"\n🔍 正则匹配测试:")
        
        # 测试不同的参考文献标题模式
        title_patterns = [
            (r'参考文献', '标准中文'),
            (r'参\s*考\s*文\s*献', '带空格中文'),
            (r'REFERENCES?', '英文大写'),
            (r'References?', '英文首字母大写'),
        ]
        
        found_titles = []
        for pattern, desc in title_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                for match in matches:
                    line_num = text[:match.start()].count('\n') + 1
                    found_titles.append({
                        'pattern': desc,
                        'text': match.group(0),
                        'line': line_num,
                        'position': match.start()
                    })
        
        if found_titles:
            for title in found_titles:
                print(f"    {title['pattern']}: '{title['text']}' (行 {title['line']})")
        else:
            print(f"   ❌ 未找到参考文献标题")
        
        # 测试条目识别
        print(f"\n📝 条目识别测试:")
        
        # 提取参考文献内容
        if found_titles:
            start_pos = min(title['position'] for title in found_titles)
            # 查找结束位置
            end_patterns = [r'致\s*谢', r'ACKNOWLEDGMENT', r'附\s*录']
            end_pos = len(text)
            for pattern in end_patterns:
                match = re.search(pattern, text[start_pos:], re.IGNORECASE)
                if match:
                    end_pos = start_pos + match.start()
                    break
            
            ref_content = text[start_pos:end_pos]
            
            # 识别不同的条目格式
            item_patterns = [
                (r'\[\s*\d+\s*\]', '方括号编号'),
                (r'\(\s*\d+\s*\)', '圆括号编号'),
                (r'【\s*\d+\s*】', '中文方括号'),
                (r'^\s*\d+\.\s*', '数字点号'),
            ]
            
            total_items = 0
            for pattern, desc in item_patterns:
                items = re.findall(pattern, ref_content, re.MULTILINE)
                if items:
                    print(f"   📌 {desc}: {len(items)} 个 - {', '.join(items[:3])}{'...' if len(items) > 3 else ''}")
                    total_items = max(total_items, len(items))
            
            print(f"   📊 估计总条目数: {total_items}")
            
            # 检测格式问题
            print(f"\n⚠️ 格式问题检测:")
            issues = []
            
            # 检查标题空格
            for title in found_titles:
                if re.search(r'参\s+考|考\s+文|文\s+献', title['text']):
                    issues.append(f"标题异常空格: '{title['text']}'")
            
            # 检查条目间空行
            lines = ref_content.split('\n')
            empty_line_count = 0
            for i, line in enumerate(lines):
                if line.strip() == '':
                    empty_line_count += 1
                    if i > 0 and i < len(lines) - 1:
                        prev_line = lines[i-1].strip()
                        next_line = lines[i+1].strip()
                        if (re.match(r'[\[\(【]?\d+[\]\)】]?', prev_line) and 
                            re.match(r'[\[\(【]?\d+[\]\)】]?', next_line)):
                            issues.append(f"条目间多余空行: 行 {i+1}")
            
            if issues:
                for issue in issues:
                    print(f"   🔴 {issue}")
            else:
                print(f"    格式检查通过")
            
            print(f"   📊 空行统计: {empty_line_count} 行")
        
        # AI提取器测试
        if ai_available and 'extractor' in locals():
            print(f"\n🤖 AI提取器测试:")
            try:
                sections = extractor._analyze_document_structure(text)
                
                if 'references' in sections:
                    ref_info = sections.get('references_info', {})
                    print(f"    AI识别成功")
                    if isinstance(ref_info, dict):
                        print(f"   📋 标题: {ref_info.get('title', 'N/A')}")
                        print(f"   📏 长度: {ref_info.get('content_length', 0)} 字符")
                        print(f"   🎯 置信度: {ref_info.get('boundary_confidence', 0):.2f}")
                    
                    ref_content = sections['references']
                    preview = ref_content[:150].replace('\n', ' ')
                    print(f"   📄 内容预览: {preview}...")
                else:
                    print(f"   ❌ AI未识别到参考文献")
            except Exception as e:
                print(f"   ⚠️ AI测试失败: {e}")
    
    # 测试真实文档
    print(f"\n{'='*80}")
    print(f"📚 真实文档测试")
    print(f"{'='*80}")
    
    # 获取缓存文档
    cache_dir = os.path.join(current_dir, 'cache', 'documents')
    if os.path.exists(cache_dir):
        md_files = glob.glob(os.path.join(cache_dir, "*.md"))
        md_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        for md_file in md_files[:2]:  # 测试最新的2个文档
            filename = os.path.basename(md_file)
            print(f"\n📖 测试文档: {filename}")
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找参考文献
                ref_patterns = [
                    r'参\s*考\s*文\s*献',
                    r'REFERENCES?',
                    r'References?'
                ]
                
                found = False
                for pattern in ref_patterns:
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        found = True
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            print(f"    找到: '{match.group(0)}' (行 {line_num})")
                        break
                
                if not found:
                    print(f"   ❌ 未找到参考文献章节")
                
                # AI测试
                if ai_available and 'extractor' in locals():
                    try:
                        sections = extractor._analyze_document_structure(content)
                        if 'references' in sections:
                            ref_info = sections.get('references_info', {})
                            if isinstance(ref_info, dict):
                                print(f"   🤖 AI识别: {ref_info.get('title', 'N/A')} (置信度: {ref_info.get('boundary_confidence', 0):.2f})")
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ⚠️ 读取失败: {e}")
    
    print(f"\n 参考文献测试完成!")

if __name__ == "__main__":
    test_references_recognition()
