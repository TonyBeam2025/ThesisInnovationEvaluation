#!/usr/bin/env python3
"""
最新论文文档章节边界测试分析
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

def get_latest_documents(count=2):
    """获取最新的文档"""
    cache_dir = os.path.join(current_dir, 'cache', 'documents')
    if not os.path.exists(cache_dir):
        return []
    
    md_files = glob.glob(os.path.join(cache_dir, "*.md"))
    # 按修改时间排序
    md_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    documents = []
    for md_file in md_files[:count]:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 读取元数据
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
                'size': len(content),
                'mtime': os.path.getmtime(md_file)
            })
            
        except Exception as e:
            print(f"⚠️ 读取文件失败 {md_file}: {e}")
    
    return documents

def analyze_document_structure(content: str):
    """分析文档结构"""
    # 基本统计
    stats = {
        'total_chars': len(content),
        'total_lines': content.count('\n'),
        'total_words': len(content.split()),
        'paragraphs': len([p for p in content.split('\n\n') if p.strip()]),
        'chinese_chars': len(re.findall(r'[\u4e00-\u9fff]', content)),
        'english_words': len(re.findall(r'\b[a-zA-Z]+\b', content))
    }
    
    # 章节标题检测
    chapter_patterns = [
        (r'^第[一二三四五六七八九十\d]+章\s+(.+)', 'traditional_chapter'),
        (r'^\d+\.\s*(.{5,50})', 'numbered_section'),
        (r'^(摘\s*要|Abstract|关键词|Keywords?)', 'standard_section'),
        (r'^(引\s*言|绪\s*论|前\s*言|背景)', 'introduction_section'),
        (r'^(文献综述|相关工作|国内外研究现状)', 'literature_section'),
        (r'^(研究方法|方法论|实验方法)', 'methodology_section'),
        (r'^(实验结果|结果分析|实验与分析)', 'results_section'),
        (r'^(结\s*论|总\s*结|结论与展望)', 'conclusion_section'),
        (r'^(参考文献|REFERENCES?)', 'references_section'),
        (r'^(致\s*谢|ACKNOWLEDGMENT)', 'acknowledgment_section'),
    ]
    
    detected_sections = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        for pattern, section_type in chapter_patterns:
            match = re.match(pattern, line_stripped, re.IGNORECASE)
            if match:
                detected_sections.append({
                    'line_number': i + 1,
                    'line_content': line_stripped,
                    'section_type': section_type,
                    'matched_content': match.group(0),
                    'extracted_title': match.group(1) if match.groups() else line_stripped
                })
                break
    
    return stats, detected_sections

def test_references_parsing(content: str) -> Dict[str, Any]:
    """专门测试参考文献识别和解析"""
    references_info = {
        'found': False,
        'title_variations': [],
        'total_references': 0,
        'reference_formats': [],
        'spacing_issues': [],
        'content_preview': ''
    }
    
    # 多种参考文献标题格式
    title_patterns = [
        r'参\s*考\s*文\s*献',  # 允许字间空格
        r'REFERENCES?',
        r'References?',
        r'文\s*献',
        r'Bibliography'
    ]
    
    # 查找参考文献标题
    for pattern in title_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            references_info['title_variations'].append({
                'pattern': pattern,
                'matched_text': match.group(0),
                'position': match.start(),
                'line_number': content[:match.start()].count('\n') + 1
            })
    
    if references_info['title_variations']:
        references_info['found'] = True
        
        # 选择最可能的参考文献开始位置
        best_match = min(references_info['title_variations'], 
                        key=lambda x: x['position'])
        start_pos = best_match['position']
        
        # 查找参考文献结束位置
        end_patterns = [r'致\s*谢', r'附\s*录', r'ACKNOWLEDGMENT', r'附件']
        end_pos = len(content)
        
        for pattern in end_patterns:
            match = re.search(pattern, content[start_pos:], re.IGNORECASE)
            if match:
                end_pos = start_pos + match.start()
                break
        
        # 提取参考文献内容
        ref_content = content[start_pos:end_pos]
        references_info['content_preview'] = ref_content[:500]
        
        # 分析参考文献条目格式
        ref_patterns = [
            (r'\[\s*\d+\s*\]', '方括号编号'),
            (r'\(\s*\d+\s*\)', '圆括号编号'),
            (r'【\s*\d+\s*】', '中文方括号编号'),
            (r'^\s*\d+\.\s*', '数字点号'),
            (r'^\s*\d+\s+', '纯数字')
        ]
        
        found_formats = set()
        reference_count = 0
        
        for pattern, format_name in ref_patterns:
            matches = re.findall(pattern, ref_content, re.MULTILINE)
            if matches:
                found_formats.add(format_name)
                reference_count = max(reference_count, len(matches))
        
        references_info['reference_formats'] = list(found_formats)
        references_info['total_references'] = reference_count
        
        # 检测空格和空行问题
        lines = ref_content.split('\n')
        for i, line in enumerate(lines):
            # 检查标题中的异常空格
            if i < 5 and '参' in line and '文' in line and '献' in line:
                spaces = re.findall(r'参\s+考|考\s+文|文\s+献', line)
                if spaces:
                    references_info['spacing_issues'].append({
                        'type': 'title_spacing',
                        'line': i + 1,
                        'content': line.strip(),
                        'spaces_found': spaces
                    })
            
            # 检查条目间异常空行
            if line.strip() == '' and i > 0 and i < len(lines) - 1:
                prev_line = lines[i-1].strip()
                next_line = lines[i+1].strip()
                if (re.match(r'[\[\(【]?\d+[\]\)】]?', prev_line) and 
                    re.match(r'[\[\(【]?\d+[\]\)】]?', next_line)):
                    references_info['spacing_issues'].append({
                        'type': 'item_spacing',
                        'line': i + 1,
                        'context': f"...{prev_line}... [空行] ...{next_line}..."
                    })
    
    return references_info

def test_latest_documents():
    """测试最新的2个文档"""
    print("🔍 测试最新的2个论文文档章节边界识别")
    print("=" * 80)
    
    # 获取最新文档
    documents = get_latest_documents(2)
    
    if len(documents) < 2:
        print(f"❌ 只找到 {len(documents)} 个文档，需要至少2个")
        return
    
    print(f"📚 找到最新的2个文档:")
    for i, doc in enumerate(documents, 1):
        import datetime
        mtime = datetime.datetime.fromtimestamp(doc['mtime'])
        print(f"   {i}. {doc['filename']}")
        print(f"      📅 修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      📏 大小: {doc['size']:,} 字符")
    
    # 分析每个文档
    for i, doc in enumerate(documents, 1):
        print(f"\n{'='*80}")
        print(f"📖 文档 {i}: {doc['filename']}")
        print(f"{'='*80}")
        
        # 显示元数据
        if doc['metadata']:
            print(f"\n📋 元数据信息:")
            key_fields = ['source_file', 'file_type', 'cached_time']
            for key in key_fields:
                if key in doc['metadata']:
                    print(f"   {key}: {doc['metadata'][key]}")
        
        # 结构分析
        stats, sections = analyze_document_structure(doc['content'])
        
        print(f"\n📊 文档统计:")
        print(f"   📝 总字符数: {stats['total_chars']:,}")
        print(f"   📐 总行数: {stats['total_lines']:,}")
        print(f"   📄 段落数: {stats['paragraphs']:,}")
        print(f"   🔤 英文单词: {stats['english_words']:,}")
        print(f"   🈶 中文字符: {stats['chinese_chars']:,}")
        
        print(f"\n🔍 章节结构分析:")
        if sections:
            print(f"    检测到 {len(sections)} 个章节标题:")
            
            section_types = {}
            for section in sections:
                section_type = section['section_type']
                if section_type not in section_types:
                    section_types[section_type] = []
                section_types[section_type].append(section)
            
            for section_type, items in section_types.items():
                print(f"\n   📝 {section_type}:")
                for item in items[:3]:  # 只显示前3个
                    print(f"      行 {item['line_number']}: {item['line_content'][:50]}{'...' if len(item['line_content']) > 50 else ''}")
                if len(items) > 3:
                    print(f"      ... 还有 {len(items) - 3} 个")
        else:
            print(f"   ❌ 未检测到明显的章节结构")
        
        # 内容预览
        print(f"\n📄 内容预览 (前500字符):")
        preview = doc['content'][:500].replace('\n', ' ')
        print(f"   {preview}{'...' if len(doc['content']) > 500 else ''}")
        
        # AI提取器测试
        try:
            import thesis_inno_eval.extract_sections_with_ai as extract_module
            extractor = extract_module.ThesisExtractorPro()
            
            print(f"\n🧠 AI提取器分析:")
            sections_ai = extractor._analyze_document_structure(doc['content'])
            
            non_info_sections = [k for k in sections_ai.keys() if not k.endswith('_info')]
            print(f"    AI识别到 {len(non_info_sections)} 个章节:")
            
            for section_name in non_info_sections:
                if f'{section_name}_info' in sections_ai:
                    info = sections_ai[f'{section_name}_info']
                    if isinstance(info, dict):
                        title = info.get('title', 'N/A')
                        length = info.get('content_length', 0)
                        confidence = info.get('boundary_confidence', 0)
                        print(f"      📝 {section_name}: {title} ({length}字符, 置信度:{confidence:.2f})")
            
            # 参考文献专项测试
            print(f"\n📚 参考文献专项测试:")
            references_test = test_references_parsing(doc['content'])
            
            if references_test['found']:
                print(f"    找到参考文献章节")
                print(f"   📝 标题变体: {len(references_test['title_variations'])} 个")
                for var in references_test['title_variations']:
                    print(f"      行 {var['line_number']}: '{var['matched_text']}' (模式: {var['pattern']})")
                
                print(f"   📊 参考文献统计:")
                print(f"      条目数量: ~{references_test['total_references']} 个")
                print(f"      编号格式: {', '.join(references_test['reference_formats']) if references_test['reference_formats'] else '未识别'}")
                
                if references_test['spacing_issues']:
                    print(f"   ⚠️ 发现格式问题 ({len(references_test['spacing_issues'])} 个):")
                    for issue in references_test['spacing_issues'][:3]:  # 只显示前3个
                        if issue['type'] == 'title_spacing':
                            print(f"      标题空格: 行 {issue['line']} - {issue['content']}")
                        elif issue['type'] == 'item_spacing':
                            print(f"      条目空行: 行 {issue['line']} - {issue['context']}")
                    if len(references_test['spacing_issues']) > 3:
                        print(f"      ... 还有 {len(references_test['spacing_issues']) - 3} 个问题")
                else:
                    print(f"    格式检查通过，无明显问题")
                
                print(f"   📄 内容预览:")
                preview_lines = references_test['content_preview'].split('\n')[:3]
                for line in preview_lines:
                    if line.strip():
                        print(f"      {line.strip()[:80]}{'...' if len(line.strip()) > 80 else ''}")
            else:
                print(f"   ❌ 未找到参考文献章节")
            
        except Exception as e:
            print(f"   ⚠️ AI提取器不可用: {e}")    # 对比分析
    print(f"\n{'='*80}")
    print(f"📊 两文档对比分析")
    print(f"{'='*80}")
    
    if len(documents) >= 2:
        doc1, doc2 = documents[0], documents[1]
        
        print(f"\n📏 规模对比:")
        print(f"   文档1: {doc1['size']:,} 字符")
        print(f"   文档2: {doc2['size']:,} 字符")
        print(f"   差异: {abs(doc1['size'] - doc2['size']):,} 字符")
        
        # 学科领域分析
        print(f"\n🎓 学科分析:")
        for i, doc in enumerate([doc1, doc2], 1):
            filename = doc['filename']
            if '生物医学' in filename:
                print(f"   文档{i}: 生物医学工程领域")
            elif '跨模态' in filename:
                print(f"   文档{i}: 计算机视觉/医学影像领域")
            elif '神经网络' in filename:
                print(f"   文档{i}: 人工智能/通信工程领域")
            elif '工程力学' in filename:
                print(f"   文档{i}: 工程力学领域")
            else:
                print(f"   文档{i}: 未明确识别的领域")
    
    print(f"\n 测试完成!")

if __name__ == "__main__":
    test_latest_documents()
