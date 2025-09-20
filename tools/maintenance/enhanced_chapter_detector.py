#!/usr/bin/env python3
"""
增强章节识别器 - 专门处理数字格式章节标题
"""

import sys
import os
import re
import json
from typing import Dict, Any, List, Tuple

# 添加源代码路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def enhanced_chapter_detection(text: str) -> Dict[str, Any]:
    """增强的章节检测，支持多种格式"""
    
    sections = {}
    
    # 扩展的章节识别模式
    enhanced_patterns = {
        # 传统格式保持不变
        'abstract_cn': r'((?:中文)?摘\s*要[\s\S]{100,5000}?)(?=关键词|英文摘要|ABSTRACT|目\s*录)',
        'abstract_en': r'((?:ABSTRACT|Abstract)[\s\S]{100,5000}?)(?=Keywords?|Key\s+Words?|目\s*录|1\s)',
        'keywords_cn': r'(关键词[：:\s]*[^\n\r]{5,200})',
        'keywords_en': r'((?:Keywords?|KEY\s+WORDS?|Key\s+Words?)[：:\s]*[^\n\r]{5,200})',
        
        # 增强的目录识别
        'toc': r'(目\s*录[\s\S]{100,2000}?)(?=1\s+绪论|1\s|摘\s*要)',
        
        # 数字章节格式 - 这是关键改进
        'chapter_1': r'((?:^|\n)\s*1\s+绪\s*论[\s\S]{500,10000}?)(?=2\s+|$)',
        'chapter_2': r'((?:^|\n)\s*2\s+[\u4e00-\u9fff].*?基础理论[\s\S]{1000,20000}?)(?=3\s+|$)',
        'chapter_3': r'((?:^|\n)\s*3\s+[\u4e00-\u9fff].*?CTA.*?分割[\s\S]{1000,15000}?)(?=4\s+|$)',
        'chapter_4': r'((?:^|\n)\s*4\s+四维动态[\s\S]{1000,15000}?)(?=5\s+|结\s*论|$)',
        'chapter_5': r'((?:^|\n)\s*5\s+结\s*论[\s\S]{200,8000}?)(?=参\s*考\s*文\s*献|致谢|$)',
        
        # 传统章节格式作为备选
        'introduction_alt': r'((?:第一章|第1章|引\s*言|绪\s*论)[\s\S]{500,10000}?)(?=第二章|第2章|2\s)',
        'literature_alt': r'((?:第二章|第2章|文献综述|相关工作|基础理论)[\s\S]{1000,20000}?)(?=第三章|第3章|3\s)',
        'methodology_alt': r'((?:第三章|第3章|研究方法|方法论|图像分割)[\s\S]{1000,15000}?)(?=第四章|第4章|4\s)',
        'results_alt': r'((?:第四章|第4章|实验结果|结果分析|模型构建)[\s\S]{1000,15000}?)(?=第五章|第5章|5\s|结论)',
        
        # 其他章节保持不变
        'conclusion': r'((?:结\s*论|总\s*结|结论与展望)[\s\S]{200,8000}?)(?=参\s*考\s*文\s*献|致谢|附录|$)',
        'references': r'((?:参\s*考\s*文\s*献|REFERENCES?|References?)(?:\s*\n+\s*(?:\[?\d+\]?|\d+\.|\【\d+】|\(\d+\))\s*[\s\S]*?)?)(?:\n+\s*(?:致\s*谢|附\s*录|ACKNOWLEDGMENT|$)|$)',
        'acknowledgement': r'(致\s*谢[\s\S]{100,2000}?)(?=附录|大连理工大学|$)',
    }
    
    print("🔍 增强章节检测开始...")
    
    # 识别章节
    detected_sections = {}
    for section_name, pattern in enhanced_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            section_content = match.group(1).strip()
            detected_sections[section_name] = {
                'content': section_content,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'length': len(section_content)
            }
            
            # 提取章节标题
            title = extract_chapter_title(section_content, section_name)
            detected_sections[section_name]['title'] = title
            
            print(f"    发现章节: {section_name} | 标题: {title} | 长度: {len(section_content)}")
    
    return detected_sections

def extract_chapter_title(content: str, section_name: str) -> str:
    """从章节内容中提取标题"""
    
    # 首先尝试提取第一行作为标题
    first_line = content.split('\n')[0].strip()
    
    # 针对不同类型的章节使用不同的标题提取策略
    if section_name.startswith('chapter_'):
        # 数字章节格式
        title_match = re.match(r'(\d+\s+[^\d\n\r]{2,50})', first_line)
        if title_match:
            return title_match.group(1).strip()
    
    elif section_name == 'abstract_cn':
        return '摘要'
    elif section_name == 'abstract_en':
        return 'Abstract'
    elif section_name == 'keywords_cn':
        return '关键词'
    elif section_name == 'keywords_en':
        return 'Keywords'
    elif section_name == 'toc':
        return '目录'
    elif section_name == 'conclusion':
        return '结论'
    elif section_name == 'references':
        return '参考文献'
    elif section_name == 'acknowledgement':
        return '致谢'
    
    # 通用标题提取
    if first_line and len(first_line) < 100:
        return first_line
    
    return section_name

def analyze_document_structure(file_path: str):
    """分析文档结构"""
    
    print(f"📖 分析文档: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   📄 文档长度: {len(content)} 字符")
        
        # 执行增强章节检测
        sections = enhanced_chapter_detection(content)
        
        print(f"\n📊 检测结果汇总:")
        print(f"   发现章节数量: {len(sections)}")
        
        # 按章节顺序排序
        ordered_sections = []
        
        # 首先添加前置章节
        for section_name in ['abstract_cn', 'abstract_en', 'keywords_cn', 'keywords_en', 'toc']:
            if section_name in sections:
                ordered_sections.append((section_name, sections[section_name]))
        
        # 添加主要章节
        for i in range(1, 6):
            chapter_key = f'chapter_{i}'
            if chapter_key in sections:
                ordered_sections.append((chapter_key, sections[chapter_key]))
        
        # 添加备选主要章节
        for section_name in ['introduction_alt', 'literature_alt', 'methodology_alt', 'results_alt']:
            if section_name in sections and f"chapter_{section_name.split('_')[0]}" not in sections:
                ordered_sections.append((section_name, sections[section_name]))
        
        # 添加后置章节
        for section_name in ['conclusion', 'references', 'acknowledgement']:
            if section_name in sections:
                ordered_sections.append((section_name, sections[section_name]))
        
        # 显示检测结果
        print(f"\n📋 章节详情:")
        for section_name, section_info in ordered_sections:
            title = section_info['title']
            length = section_info['length']
            start_pos = section_info['start_pos']
            
            print(f"   📖 {section_name:15} | {title:30} | {length:>5} 字符 | 位置: {start_pos}")
        
        # 生成边界信息
        boundaries = {}
        for section_name, section_info in sections.items():
            # 计算行号
            start_line = content[:section_info['start_pos']].count('\n') + 1
            end_line = content[:section_info['end_pos']].count('\n') + 1
            
            boundaries[section_name] = {
                'section_name': section_name,
                'title': section_info['title'],
                'start_position': section_info['start_pos'],
                'end_position': section_info['end_pos'],
                'content_length': section_info['length'],
                'boundaries': {
                    'start_line': start_line,
                    'end_line': end_line
                },
                'boundary_confidence': 0.9  # 高置信度，因为是精确匹配
            }
        
        return {
            'sections': {name: info['content'] for name, info in sections.items()},
            'boundaries': boundaries,
            'ordered_sections': [name for name, _ in ordered_sections]
        }
        
    except Exception as e:
        print(f"   ❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_enhanced_detection():
    """测试增强检测功能"""
    
    print("🔍 增强章节检测测试")
    print("=" * 80)
    
    # 测试缓存文档
    cache_dir = os.path.join(current_dir, 'cache', 'documents')
    if not os.path.exists(cache_dir):
        print("   ⚠️ 缓存目录不存在")
        return
    
    # 找到目标文档
    target_file = None
    for file in os.listdir(cache_dir):
        if file.endswith('.md') and 'HUSSEIN' in file:
            target_file = os.path.join(cache_dir, file)
            break
    
    if not target_file:
        print("   ⚠️ 未找到目标文档")
        return
    
    # 分析文档结构
    result = analyze_document_structure(target_file)
    
    if result:
        print(f"\n 分析完成!")
        
        # 保存分析结果
        output_file = os.path.join(current_dir, 'enhanced_section_detection_result.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            # 只保存边界信息，因为内容太大
            json.dump({
                'boundaries': result['boundaries'],
                'ordered_sections': result['ordered_sections'],
                'section_count': len(result['sections']),
                'detection_method': 'enhanced_numeric_chapters'
            }, f, ensure_ascii=False, indent=2)
        
        print(f"   💾 结果已保存到: {os.path.basename(output_file)}")
        
        # 对比原始结果
        original_json = os.path.join(current_dir, 'data', 'output', '1_生物医学工程_21709201_HUSSEIN Y. Y. ALGHALBAN_LW_pro_extracted_info.json')
        if os.path.exists(original_json):
            with open(original_json, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            original_boundaries = original_data.get('extracted_info', {}).get('section_boundaries', {})
            
            print(f"\n📊 对比分析:")
            print(f"   原始识别: {len(original_boundaries)} 个章节")
            print(f"   增强识别: {len(result['boundaries'])} 个章节")
            print(f"   改进提升: +{len(result['boundaries']) - len(original_boundaries)} 个章节")
            
            # 显示新识别的章节
            original_keys = set(original_boundaries.keys())
            enhanced_keys = set(result['boundaries'].keys())
            new_sections = enhanced_keys - original_keys
            
            if new_sections:
                print(f"\n🆕 新识别的章节:")
                for section in sorted(new_sections):
                    info = result['boundaries'][section]
                    print(f"   📖 {section}: {info['title']}")

if __name__ == "__main__":
    test_enhanced_detection()

