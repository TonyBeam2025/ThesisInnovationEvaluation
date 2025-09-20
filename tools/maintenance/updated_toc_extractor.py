#!/usr/bin/env python3
"""
更新的TOC字段提取器
专门处理已更新的Word目录字段（显示为超链接格式）
"""

import re
from docx import Document
import logging

class UpdatedTOCExtractor:
    """处理已更新的TOC字段的提取器"""
    
    def __init__(self, file_path):
        self.doc = Document(file_path)
        self.toc_entries = []
        self.logger = logging.getLogger(__name__)
        
    def extract(self):
        """提取已更新的目录内容"""
        self.logger.info("开始提取已更新的TOC字段内容")
        
        for paragraph in self.doc.paragraphs:
            if self._is_toc_paragraph(paragraph):
                self._parse_toc_paragraph(paragraph)
                
        self.logger.info(f"提取到 {len(self.toc_entries)} 个目录条目")
        return self.toc_entries
    
    def _is_toc_paragraph(self, paragraph):
        """判断是否为目录段落"""
        text = paragraph.text.strip()
        if not text:
            return False
            
        # 目录特征检测
        conditions = [
            # 包含目录关键词
            '目录' in text,
            'Contents' in text.upper(),
            'TABLE OF CONTENTS' in text.upper(),
            
            # 包含超链接格式特征：方括号、井号、页码等
            '[' in text and ']' in text and '#' in text,
            
            # 包含常见学术论文章节关键词
            any(keyword in text for keyword in [
                'ABSTRACT', '摘要', '绪论', '引言', 'Introduction',
                '参考文献', 'References', '致谢', 'Acknowledgments',
                '附录', 'Appendix', '结论', 'Conclusion'
            ]),
            
            # 包含章节编号模式
            re.search(r'第[一二三四五六七八九十\d]+章', text),
            re.search(r'Chapter\s+\d+', text, re.IGNORECASE),
            re.search(r'^\d+\.', text),
            
            # 检查是否包含页码引用格式
            re.search(r'\[\d+\]', text),
            re.search(r'\.{3,}\s*\d+', text),  # 点线加页码
        ]
        
        # 排除明显不是目录的内容
        exclusions = [
            text.startswith('#'),
            text.startswith('*'),
            text.startswith('-'),
            len(text) < 3,
            text.isdigit(),
        ]
        
        is_toc = any(conditions) and not any(exclusions)
        
        if is_toc:
            self.logger.debug(f"识别为目录段落: {text[:50]}...")
            
        return is_toc
    
    def _parse_toc_paragraph(self, paragraph):
        """解析目录段落"""
        text = paragraph.text
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 尝试多种目录格式解析
            parsed = self._try_parse_formats(line)
            if parsed:
                self.toc_entries.extend(parsed)
    
    def _try_parse_formats(self, line):
        """尝试解析多种目录格式"""
        entries = []
        
        # 格式1: [标题 [页码](#锚点)]
        pattern1 = r'\[([^\]]+)\s+\[(\d+)\]\(#([^)]+)\)\]'
        matches1 = re.findall(pattern1, line)
        for match in matches1:
            title, page, anchor = match
            entries.append({
                'type': 'hyperlink_format',
                'title': title.strip(),
                'page': int(page),
                'anchor': anchor,
                'raw_text': line,
                'level': self._determine_level(title.strip())
            })
        
        # 格式2: 标题 [页码]
        if not entries:
            pattern2 = r'(.+?)\s+\[(\d+)\]'
            matches2 = re.findall(pattern2, line)
            for match in matches2:
                title, page = match
                if title.strip() and page.isdigit():
                    entries.append({
                        'type': 'simple_format',
                        'title': title.strip(),
                        'page': int(page),
                        'raw_text': line,
                        'level': self._determine_level(title.strip())
                    })
        
        # 格式3: 标题...页码
        if not entries:
            pattern3 = r'^(.+?)\.{3,}\s*(\d+)\s*$'
            match3 = re.match(pattern3, line)
            if match3:
                title, page = match3.groups()
                entries.append({
                    'type': 'dotted_format',
                    'title': title.strip(),
                    'page': int(page),
                    'raw_text': line,
                    'level': self._determine_level(title.strip())
                })
        
        # 格式4: 数字编号 标题 页码
        if not entries:
            pattern4 = r'^(\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)\s*$'
            match4 = re.match(pattern4, line)
            if match4:
                number, title, page = match4.groups()
                entries.append({
                    'type': 'numbered_format',
                    'number': number,
                    'title': title.strip(),
                    'page': int(page),
                    'raw_text': line,
                    'level': self._determine_level_by_number(number)
                })
        
        # 格式5: 第X章 标题 页码
        if not entries:
            pattern5 = r'^(第[一二三四五六七八九十\d]+章)\s+(.+?)\s+(\d+)\s*$'
            match5 = re.match(pattern5, line)
            if match5:
                chapter, title, page = match5.groups()
                entries.append({
                    'type': 'chapter_format',
                    'chapter': chapter,
                    'title': title.strip(),
                    'page': int(page),
                    'raw_text': line,
                    'level': 1
                })
        
        return entries
    
    def _determine_level(self, title):
        """根据标题确定层级"""
        title = title.strip()
        
        # 一级标题（章）
        if (re.match(r'^第[一二三四五六七八九十\d]+章', title) or
            re.match(r'^Chapter\s+\d+', title, re.IGNORECASE) or
            title.upper() in ['ABSTRACT', 'INTRODUCTION', 'CONCLUSION', 'REFERENCES',
                            '摘要', '绪论', '结论', '参考文献', '致谢']):
            return 1
        
        # 二级标题
        if (re.match(r'^\d+\.\d+\s', title) or
            title.count('.') == 1):
            return 2
        
        # 三级标题
        if (re.match(r'^\d+\.\d+\.\d+\s', title) or
            title.count('.') == 2):
            return 3
        
        # 四级标题
        if title.count('.') >= 3:
            return 4
        
        return 1  # 默认一级
    
    def _determine_level_by_number(self, number):
        """根据编号确定层级"""
        parts = number.split('.')
        return len(parts)
    
    def get_formatted_toc(self):
        """获取格式化的目录文本"""
        if not self.toc_entries:
            return ""
        
        formatted_lines = []
        for entry in self.toc_entries:
            if entry['type'] == 'hyperlink_format':
                formatted_lines.append(f"{entry['title']} {entry['page']}")
            elif entry['type'] == 'numbered_format':
                formatted_lines.append(f"{entry['number']} {entry['title']} {entry['page']}")
            elif entry['type'] == 'chapter_format':
                formatted_lines.append(f"{entry['chapter']} {entry['title']} {entry['page']}")
            else:
                formatted_lines.append(f"{entry['title']} {entry['page']}")
        
        return '\n'.join(formatted_lines)


def test_updated_toc_extractor():
    """测试更新的TOC提取器"""
    import os
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试文件
    test_file = "data/input/计算机应用技术_test2.docx"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    print(f"🔍 测试已更新TOC字段提取器")
    print(f"📄 文件: {test_file}")
    print("=" * 60)
    
    try:
        # 创建提取器
        extractor = UpdatedTOCExtractor(test_file)
        
        # 提取目录
        toc_data = extractor.extract()
        
        if toc_data:
            print(f" 成功提取到 {len(toc_data)} 个目录条目:")
            print("-" * 40)
            
            for i, entry in enumerate(toc_data, 1):
                level_indent = "  " * (entry.get('level', 1) - 1)
                print(f"{i:2d}. {level_indent}{entry['title']} - 第{entry['page']}页")
                print(f"     类型: {entry['type']}")
                print(f"     原文: {entry['raw_text'][:50]}...")
                print()
            
            print("-" * 40)
            print("📋 格式化目录:")
            print(extractor.get_formatted_toc())
            
        else:
            print("❌ 未提取到目录条目")
            
    except Exception as e:
        print(f"❌ 提取过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_updated_toc_extractor()

