#!/usr/bin/env python3
"""
测试章节边界识别功能 - 使用缓存的论文md文件
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

def load_cached_documents():
    """加载缓存的论文文档"""
    cache_dir = os.path.join(current_dir, 'cache', 'documents')
    documents = []
    
    if not os.path.exists(cache_dir):
        print(f"❌ 缓存目录不存在: {cache_dir}")
        return documents
    
    # 查找所有md文件
    md_files = glob.glob(os.path.join(cache_dir, "*.md"))
    
    for md_file in md_files:
        try:
            # 读取md文件内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试读取对应的metadata文件
            metadata_file = md_file.replace('.md', '_metadata.json')
            metadata = {}
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            documents.append({
                'filename': os.path.basename(md_file),
                'filepath': md_file,
                'content': content,
                'metadata': metadata,
                'size': len(content)
            })
            
        except Exception as e:
            print(f"⚠️ 读取文件失败 {md_file}: {e}")
    
    return documents

def simple_section_analysis(text: str) -> Dict[str, Any]:
    """简化的章节分析（不依赖复杂的类）"""
    sections = {}
    
    # 基本章节识别模式
    section_patterns = {
        'title': r'([^\n]{10,100})\n.*(?:作者|Author)',
        'abstract_cn': r'((?:中文)?摘\s*要[\s\S]{100,3000}?)(?=关键词|Keywords?|ABSTRACT)',
        'abstract_en': r'((?:ABSTRACT|Abstract)[\s\S]{100,3000}?)(?=Keywords?|关键词|第一章)',
        'keywords_cn': r'(关键词[：:\s]*[^\n\r]{5,200})',
        'keywords_en': r'((?:Keywords?|KEY\s+WORDS?)[：:\s]*[^\n\r]{5,200})',
        'chapter_1': r'((?:第一章|第1章|1\.|引\s*言|绪\s*论)[\s\S]{200,5000}?)(?=第二章|第2章|2\.)',
        'chapter_2': r'((?:第二章|第2章|2\.|文献综述|相关工作)[\s\S]{500,8000}?)(?=第三章|第3章|3\.)',
        'conclusion': r'((?:结\s*论|总\s*结|结论与展望)[\s\S]{100,3000}?)(?=参考文献|致谢|REFERENCES)',
        'references': r'((?:参考文献|REFERENCES?)[\s\S]{200,8000}?)(?=致谢|附录|$)',
    }
    
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            content = match.group(1).strip()
            sections[section_name] = {
                'content': content,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'length': len(content),
                'start_line': text[:match.start()].count('\n') + 1,
                'end_line': text[:match.end()].count('\n') + 1
            }
            
            # 提取标题
            if section_name == 'title':
                sections[section_name]['title'] = content.split('\n')[0].strip()
            elif section_name.startswith('abstract'):
                first_line = content.split('\n')[0].strip()
                sections[section_name]['title'] = first_line if len(first_line) < 50 else '摘要' if 'cn' in section_name else 'ABSTRACT'
            elif section_name.startswith('chapter'):
                first_line = content.split('\n')[0].strip()
                sections[section_name]['title'] = first_line if len(first_line) < 100 else f'第{section_name[-1]}章'
            else:
                first_line = content.split('\n')[0].strip()
                sections[section_name]['title'] = first_line if len(first_line) < 50 else section_name.replace('_', ' ').title()
    
    return sections

def extract_section_titles_and_boundaries(text: str) -> List[Dict[str, Any]]:
    """提取所有章节标题和边界"""
    titles = []
    
    # 匹配各种章节标题格式
    title_patterns = [
        (r'^(第[一二三四五六七八九十1-9]章)\s+([^\n\r]{5,100})', 'chapter'),
        (r'^(\d+\.)\s*([^\n\r]{5,100})', 'numbered'),
        (r'^(摘\s*要|ABSTRACT|Abstract)\s*$', 'abstract'),
        (r'^(关键词|Keywords?)\s*[：:\s]*', 'keywords'),
        (r'^(引\s*言|绪\s*论|前\s*言)\s*$', 'introduction'),
        (r'^(文献综述|相关工作|国内外研究现状)\s*$', 'literature'),
        (r'^(结\s*论|总\s*结|结论与展望)\s*$', 'conclusion'),
        (r'^(参考文献|REFERENCES?|References?)\s*$', 'references'),
        (r'^(致\s*谢|ACKNOWLEDGMENT)\s*$', 'acknowledgment'),
    ]
    
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        for pattern, section_type in title_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                char_pos = sum(len(l) + 1 for l in lines[:i])  # +1 for \n
                
                title_info = {
                    'line_number': i + 1,
                    'char_position': char_pos,
                    'section_type': section_type,
                    'full_match': match.group(0),
                    'title': line,
                    'confidence': 1.0 if match.group(0) == line else 0.8
                }
                
                # 如果有分组，提取章节号和标题
                if match.groups() and len(match.groups()) >= 2:
                    title_info['chapter_number'] = match.group(1)
                    title_info['chapter_title'] = match.group(2).strip()
                    title_info['full_title'] = f"{match.group(1)} {match.group(2)}".strip()
                
                titles.append(title_info)
                break
    
    return titles

def test_cached_documents():
    """测试缓存文档的章节边界识别"""
    
    print("🔍 开始测试缓存文档的章节边界识别...")
    print("=" * 80)
    
    # 加载缓存文档
    documents = load_cached_documents()
    
    if not documents:
        print("❌ 未找到任何缓存文档")
        return
    
    print(f"📚 找到 {len(documents)} 个缓存文档:")
    for doc in documents:
        print(f"   📄 {doc['filename']} ({doc['size']} 字符)")
    
    # 分析每个文档
    for i, doc in enumerate(documents, 1):
        print(f"\n{'='*80}")
        print(f"📖 分析文档 {i}/{len(documents)}: {doc['filename']}")
        print(f"📏 文档大小: {doc['size']} 字符")
        print(f"{'='*80}")
        
        # 显示元数据（如果有）
        if doc['metadata']:
            print("\n📋 元数据信息:")
            for key, value in doc['metadata'].items():
                if isinstance(value, str) and len(value) < 100:
                    print(f"   {key}: {value}")
                else:
                    print(f"   {key}: {type(value).__name__}")
        
        # 简化的章节分析
        print("\n🔍 章节识别分析:")
        sections = simple_section_analysis(doc['content'])
        
        if sections:
            print(f"    识别到 {len(sections)} 个章节:")
            for section_name, section_info in sections.items():
                print(f"\n   📝 {section_name}:")
                print(f"      📋 标题: {section_info.get('title', 'N/A')}")
                print(f"      📍 位置: 行 {section_info['start_line']}-{section_info['end_line']}")
                print(f"      📏 长度: {section_info['length']} 字符")
                
                # 显示内容预览
                content = section_info['content']
                preview = content[:150].replace('\n', ' ')
                if len(content) > 150:
                    preview += "..."
                print(f"      📄 预览: {preview}")
        else:
            print("   ❌ 未识别到任何章节")
        
        # 标题和边界检测
        print("\n🎯 标题边界检测:")
        titles = extract_section_titles_and_boundaries(doc['content'])
        
        if titles:
            print(f"    检测到 {len(titles)} 个标题:")
            for title_info in titles:
                print(f"\n   📌 行 {title_info['line_number']}: {title_info['title']}")
                print(f"      🏷️ 类型: {title_info['section_type']}")
                print(f"      📍 字符位置: {title_info['char_position']}")
                print(f"      🎯 置信度: {title_info['confidence']:.2f}")
                
                if 'chapter_number' in title_info:
                    print(f"      📖 章节号: {title_info['chapter_number']}")
                if 'chapter_title' in title_info:
                    print(f"      📝 章节标题: {title_info['chapter_title']}")
        else:
            print("   ❌ 未检测到任何标题")
        
        # 如果文档较多，只分析前3个
        if i >= 3:
            remaining = len(documents) - i
            if remaining > 0:
                print(f"\n⏭️ 跳过剩余 {remaining} 个文档的详细分析...")
            break
    
    print(f"\n{'='*80}")
    print(" 测试完成!")
    print(f"📊 总结: 分析了 {min(3, len(documents))} 个文档")
    print(f"{'='*80}")

def test_specific_document(filename: str = ""):
    """测试特定文档"""
    documents = load_cached_documents()
    
    if filename:
        target_docs = [doc for doc in documents if filename in doc['filename']]
    else:
        # 选择第一个文档
        target_docs = documents[:1] if documents else []
    
    if not target_docs:
        print(f"❌ 未找到文档: {filename}")
        return
    
    doc = target_docs[0]
    print(f"🔍 详细分析文档: {doc['filename']}")
    
    # 尝试导入完整的提取器
    try:
        import thesis_inno_eval.extract_sections_with_ai as extract_module
        extractor = extract_module.ThesisExtractorPro()
        
        print("\n🧠 使用AI提取器分析...")
        
        # 使用完整的分析方法
        if hasattr(extractor, '_analyze_document_structure'):
            sections = extractor._analyze_document_structure(doc['content'])
            print(f"    AI识别到 {len([k for k in sections.keys() if not k.endswith('_info')])} 个章节")
            
            # 显示章节信息
            for key, value in sections.items():
                if key.endswith('_info') and isinstance(value, dict):
                    section_name = key.replace('_info', '')
                    print(f"\n   📝 {section_name}:")
                    print(f"      📋 标题: {value.get('title', 'N/A')}")
                    boundaries = value.get('boundaries', {})
                    if isinstance(boundaries, dict):
                        print(f"      📍 位置: 行 {boundaries.get('start_line', 'N/A')}-{boundaries.get('end_line', 'N/A')}")
                    print(f"      📏 长度: {value.get('content_length', 0)} 字符")
                    print(f"      🎯 置信度: {value.get('boundary_confidence', 0):.2f}")
        
        # 使用精确边界检测
        if hasattr(extractor, 'find_precise_section_boundaries'):
            test_sections = ['摘要', '第一章', '第二章', '结论', '参考文献']
            
            print(f"\n🎯 精确边界检测:")
            for section_title in test_sections:
                try:
                    boundary_info = extractor.find_precise_section_boundaries(doc['content'], section_title)
                    
                    if boundary_info['found']:
                        print(f"\n    {section_title}:")
                        print(f"      📋 标题: {boundary_info['title']}")
                        print(f"      📍 位置: 字符 {boundary_info['start_pos']}-{boundary_info['end_pos']}")
                        print(f"      📏 行位置: {boundary_info['start_line']}-{boundary_info['end_line']}")
                        print(f"      🎯 置信度: {boundary_info['confidence']:.2f}")
                        if boundary_info['next_section']:
                            print(f"      ⏭️ 下一章节: {boundary_info['next_section']}")
                    else:
                        print(f"   ❌ 未找到: {section_title}")
                except Exception as e:
                    print(f"   ⚠️ 精确检测失败 {section_title}: {e}")
        else:
            print("\n⚠️ 精确边界检测方法不可用")
        
    except Exception as e:
        print(f"⚠️ AI提取器不可用: {e}")
        print("回退到简化分析...")
        
        # 使用简化分析
        sections = simple_section_analysis(doc['content'])
        titles = extract_section_titles_and_boundaries(doc['content'])
        
        print(f"\n📊 简化分析结果:")
        print(f"   章节数: {len(sections)}")
        print(f"   标题数: {len(titles)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='测试章节边界识别功能')
    parser.add_argument('--file', '-f', help='指定要分析的文件名（部分匹配）')
    parser.add_argument('--detailed', '-d', action='store_true', help='详细分析模式')
    
    args = parser.parse_args()
    
    if args.file:
        test_specific_document(args.file)
    elif args.detailed:
        test_cached_documents()
    else:
        # 默认快速测试
        documents = load_cached_documents()
        if documents:
            print(f"🚀 快速测试 - 分析第一个文档: {documents[0]['filename']}")
            test_specific_document()
        else:
            print("❌ 未找到缓存文档")
