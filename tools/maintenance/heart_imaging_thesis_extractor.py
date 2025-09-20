#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心脏成像论文专用提取器
专门针对心脏成像论文的复杂嵌套结构进行分析和提取
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SectionInfo:
    """章节信息"""
    name: str
    title: str
    level: int  # 1=主章节, 2=子章节
    number: str  # 章节编号 (如 "1", "1.1")
    start_pos: int
    end_pos: int
    content: str
    confidence: float

class HeartImagingThesisExtractor:
    """心脏成像论文专用提取器"""
    
    def __init__(self):
        self.sections = []
        self.setup_patterns()
    
    def setup_patterns(self):
        """设置匹配模式"""
        # 主章节模式 (数字 + 标题)
        self.main_chapter_patterns = {
            r'^(1)\s+(绪论)\s*$': ('chapter_1', 'introduction'),
            r'^(2)\s+(心脏建模的基础理论)\s*$': ('chapter_2', 'modeling_theory'),
            r'^(3)\s+(心脏CTA图像分割)\s*$': ('chapter_3', 'cta_segmentation'),
            r'^(4)\s+(四维动态统计体形心脏模型的构建)\s*$': ('chapter_4', 'dynamic_model'),
            r'^(5)\s+(结论)\s*$': ('chapter_5', 'conclusion'),
            # 通用模式
            r'^(\d+)\s+([^\n\r]+?)\s*$': ('chapter_generic', 'generic_chapter'),
        }
        
        # 子章节模式 (### + 编号 + 标题)
        self.subsection_patterns = {
            # 第1章子章节
            r'^###\s+(1\.1)\s+(研究背景)\s*$': ('subsection_1_1', 'research_background'),
            r'^###\s+(1\.2)\s+(国内外研究现状)\s*$': ('subsection_1_2', 'research_status'),
            
            # 第2章子章节  
            r'^###\s+(2\.1)\s+(全心建模)\s*$': ('subsection_2_1', 'full_heart_modeling'),
            r'^###\s+(2\.2)\s+(CTA图像预处理与增强)\s*$': ('subsection_2_2', 'cta_preprocessing'),
            r'^###\s+(2\.3)\s+(心脏图像分割)\s*$': ('subsection_2_3', 'heart_segmentation'),
            
            # 第3章子章节
            r'^###\s+(3\.1)\s+(基于深度学习的心脏CTA图像分割算法)\s*$': ('subsection_3_1', 'dl_segmentation'),
            r'^###\s+(3\.2)\s+(基于区域生长的心脏CTA图像分割算法)\s*$': ('subsection_3_2', 'region_growing'),
            r'^###\s+(3\.3)\s+(心脏CTA图像分割算法比较)\s*$': ('subsection_3_3', 'algorithm_comparison'),
            
            # 第4章子章节
            r'^###\s+(4\.1)\s+(心脏CTA图像的配准)\s*$': ('subsection_4_1', 'image_registration'),
            r'^###\s+(4\.2)\s+(四维动态统计体形心脏模型的构建方法)\s*$': ('subsection_4_2', 'model_construction'),
            r'^###\s+(4\.3)\s+(四维动态统计体形心脏模型的验证)\s*$': ('subsection_4_3', 'model_validation'),
            r'^###\s+(4\.4)\s+(四维动态统计体形心脏模型的应用)\s*$': ('subsection_4_4', 'model_application'),
            
            # 通用子章节模式
            r'^###\s+(\d+\.\d+)\s+([^\n\r]+?)\s*$': ('subsection_generic', 'generic_subsection'),
        }
    
    def extract_sections(self, text: str) -> List[SectionInfo]:
        """提取章节"""
        lines = text.split('\n')
        sections = []
        
        print("🔍 开始心脏成像论文结构分析...")
        print(f"📄 总行数: {len(lines)}")
        
        # 第一遍: 找到所有章节标题行
        section_markers = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 检查主章节
            for pattern, (section_type, section_key) in self.main_chapter_patterns.items():
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    number = match.group(1)
                    title = match.group(2) if len(match.groups()) > 1 else line
                    section_markers.append({
                        'line_num': i,
                        'type': section_type,
                        'key': section_key,
                        'level': 1,
                        'number': number,
                        'title': title,
                        'full_line': line,
                        'confidence': 0.9 if section_type != 'chapter_generic' else 0.7
                    })
                    print(f"   📍 主章节: {number} {title} (行 {i+1})")
                    break
            
            # 检查子章节
            for pattern, (section_type, section_key) in self.subsection_patterns.items():
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    number = match.group(1)
                    title = match.group(2) if len(match.groups()) > 1 else line.replace('###', '').strip()
                    section_markers.append({
                        'line_num': i,
                        'type': section_type, 
                        'key': section_key,
                        'level': 2,
                        'number': number,
                        'title': title,
                        'full_line': line,
                        'confidence': 0.9 if section_type != 'subsection_generic' else 0.7
                    })
                    print(f"      🔸 子章节: {number} {title} (行 {i+1})")
                    break
        
        # 第二遍: 确定章节边界和内容
        for i, marker in enumerate(section_markers):
            start_line = marker['line_num']
            
            # 找到下一个同级或更高级章节作为结束边界
            end_line = len(lines) - 1
            for j in range(i + 1, len(section_markers)):
                next_marker = section_markers[j]
                if (marker['level'] == 1 and next_marker['level'] == 1) or \
                   (marker['level'] == 2 and next_marker['level'] <= 2 and 
                    next_marker['number'].split('.')[0] != marker['number'].split('.')[0]):
                    end_line = next_marker['line_num'] - 1
                    break
                elif marker['level'] == 2 and next_marker['level'] == 1:
                    end_line = next_marker['line_num'] - 1
                    break
            
            # 提取内容
            content_lines = lines[start_line:end_line + 1]
            content = '\n'.join(content_lines)
            
            # 计算字符位置
            start_pos = sum(len(line) + 1 for line in lines[:start_line])
            end_pos = start_pos + len(content)
            
            section = SectionInfo(
                name=marker['type'],
                title=marker['title'],
                level=marker['level'],
                number=marker['number'],
                start_pos=start_pos,
                end_pos=end_pos,
                content=content,
                confidence=marker['confidence']
            )
            
            sections.append(section)
        
        print(f"\n📊 分析完成，共检测到 {len(sections)} 个章节")
        
        # 按层级和编号排序
        sections.sort(key=lambda x: (x.level, self._sort_key(x.number)))
        
        return sections
    
    def _sort_key(self, number: str) -> tuple:
        """生成排序键"""
        parts = number.split('.')
        return tuple(int(part) for part in parts)
    
    def analyze_hierarchy(self, sections: List[SectionInfo]) -> Dict:
        """分析章节层次结构"""
        hierarchy = {
            'main_chapters': [],
            'subsections': {},
            'statistics': {
                'total_sections': len(sections),
                'main_chapters': 0,
                'subsections': 0
            }
        }
        
        for section in sections:
            if section.level == 1:
                hierarchy['main_chapters'].append({
                    'number': section.number,
                    'title': section.title,
                    'name': section.name
                })
                hierarchy['subsections'][section.number] = []
                hierarchy['statistics']['main_chapters'] += 1
            elif section.level == 2:
                chapter_num = section.number.split('.')[0]
                if chapter_num not in hierarchy['subsections']:
                    hierarchy['subsections'][chapter_num] = []
                hierarchy['subsections'][chapter_num].append({
                    'number': section.number,
                    'title': section.title,
                    'name': section.name
                })
                hierarchy['statistics']['subsections'] += 1
        
        return hierarchy
    
    def print_results(self, sections: List[SectionInfo]):
        """打印结果"""
        print("\n" + "="*60)
        print("📋 心脏成像论文章节结构分析结果")
        print("="*60)
        
        current_chapter = None
        
        for i, section in enumerate(sections, 1):
            if section.level == 1:
                current_chapter = section.number
                print(f"\n📚 {section.number}. {section.title}")
                print(f"   └─ 位置: {section.start_pos:6d}-{section.end_pos:6d} | 长度: {len(section.content):5d} | 置信度: {section.confidence:.2f}")
            else:
                indent = "    "
                print(f"{indent}🔸 {section.number} {section.title}")
                print(f"{indent}   └─ 位置: {section.start_pos:6d}-{section.end_pos:6d} | 长度: {len(section.content):5d} | 置信度: {section.confidence:.2f}")
        
        # 统计信息
        main_chapters = [s for s in sections if s.level == 1]
        subsections = [s for s in sections if s.level == 2]
        
        print(f"\n📊 统计信息:")
        print(f"   总章节数: {len(sections)}")
        print(f"   主章节数: {len(main_chapters)}")
        print(f"   子章节数: {len(subsections)}")
        
        # 层次结构验证
        print(f"\n🔍 结构验证:")
        for chapter in main_chapters:
            chapter_subs = [s for s in subsections if s.number.startswith(chapter.number + '.')]
            print(f"   第{chapter.number}章: {len(chapter_subs)} 个子章节")
    
    def save_results(self, sections: List[SectionInfo], output_file: str):
        """保存结果"""
        results = {
            'extractor_type': 'HeartImagingThesisExtractor',
            'timestamp': str(pd.Timestamp.now()),
            'sections': []
        }
        
        for section in sections:
            results['sections'].append({
                'name': section.name,
                'title': section.title,
                'level': section.level,
                'number': section.number,
                'start_pos': section.start_pos,
                'end_pos': section.end_pos,
                'content_length': len(section.content),
                'confidence': section.confidence
            })
        
        # 添加层次结构分析
        results['hierarchy'] = self.analyze_hierarchy(sections)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {output_file}")

def test_heart_imaging_extractor():
    """测试心脏成像提取器"""
    # 创建测试文档
    test_content = """
摘要

本文研究心脏成像技术...

1 绪论

心脏疾病是当今世界的主要健康威胁之一...

### 1.1 研究背景

心血管疾病已成为全球死亡率最高的疾病类型...

### 1.2 国内外研究现状

在心脏建模领域，国外研究起步较早...

2 心脏建模的基础理论

心脏建模是心脏成像技术的理论基础...

### 2.1 全心建模

全心建模是指对整个心脏结构的三维重建...

### 2.2 CTA图像预处理与增强

CTA图像通常包含噪声和伪影...

### 2.3 心脏图像分割

心脏图像分割是从医学图像中提取心脏结构...

3 心脏CTA图像分割

本章详细介绍心脏CTA图像分割算法...

### 3.1 基于深度学习的心脏CTA图像分割算法

深度学习在医学图像分割领域取得了显著进展...

### 3.2 基于区域生长的心脏CTA图像分割算法

区域生长算法是一种传统的图像分割方法...

### 3.3 心脏CTA图像分割算法比较

本节对前述算法进行比较分析...

4 四维动态统计体形心脏模型的构建

四维动态模型能够描述心脏的时空变化...

### 4.1 心脏CTA图像的配准

图像配准是构建动态模型的关键步骤...

### 4.2 四维动态统计体形心脏模型的构建方法

本节介绍模型构建的具体方法...

### 4.3 四维动态统计体形心脏模型的验证

模型验证是确保模型可靠性的重要环节...

### 4.4 四维动态统计体形心脏模型的应用

本节展示模型在实际应用中的效果...

5 结论

本文的主要贡献和结论如下...

参考文献

[1] Smith J. Heart modeling techniques...
"""
    
    print("=== 心脏成像论文提取器测试 ===")
    
    extractor = HeartImagingThesisExtractor()
    sections = extractor.extract_sections(test_content)
    
    extractor.print_results(sections)
    extractor.save_results(sections, 'heart_imaging_extraction_result.json')
    
    return sections

if __name__ == "__main__":
    import pandas as pd
    test_heart_imaging_extractor()
