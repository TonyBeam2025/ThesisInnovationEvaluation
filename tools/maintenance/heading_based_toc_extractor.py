#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于标题样式的目录提取器
适用于使用Word标题样式(Heading 1, Heading 2等)构建的文档
"""

import logging
from dataclasses import dataclass
from typing import List, Optional
from docx import Document
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HeadingEntry:
    """标题条目"""
    title: str
    level: int
    paragraph_index: int
    style_name: str
    page: Optional[int] = None  # 页码可能无法直接获取

class HeadingBasedTOCExtractor:
    """基于标题样式的TOC提取器"""
    
    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        self.doc = None
        
    def load_document(self):
        """加载Word文档"""
        try:
            self.doc = Document(self.docx_path)
            logger.info(f"成功加载文档: {self.docx_path}")
            return True
        except Exception as e:
            logger.error(f"加载文档失败: {e}")
            return False
    
    def extract_headings(self) -> List[HeadingEntry]:
        """提取所有标题"""
        if not self.doc:
            if not self.load_document():
                return []
        
        if not self.doc:  # 再次检查
            logger.error("文档加载失败")
            return []
        
        headings = []
        
        # 定义标题样式模式
        heading_patterns = [
            r'^Heading\s+(\d+)$',           # Heading 1, Heading 2, etc.
            r'^标题\s*(\d+)$',              # 标题1, 标题2
            r'^Heading(\d+)$',              # Heading1, Heading2 (无空格)
        ]
        
        logger.info("开始提取标题样式段落")
        
        for i, paragraph in enumerate(self.doc.paragraphs):
            text = paragraph.text.strip()
            
            # 跳过空段落
            if not text:
                continue
            
            # 获取样式名称
            style_name = paragraph.style.name if paragraph.style and paragraph.style.name else 'Normal'
            
            # 检查是否是标题样式
            heading_level = self._get_heading_level(style_name)
            
            if heading_level > 0:
                # 过滤明显不是标题的内容
                if self._is_valid_heading(text):
                    entry = HeadingEntry(
                        title=text,
                        level=heading_level,
                        paragraph_index=i + 1,
                        style_name=style_name,
                        page=self._estimate_page_number(i + 1)
                    )
                    
                    headings.append(entry)
                    logger.info(f"找到标题 [{style_name}]: {text}")
        
        logger.info(f"总共提取到 {len(headings)} 个标题")
        return headings
    
    def _get_heading_level(self, style_name: str) -> int:
        """获取标题级别"""
        if not style_name:
            return 0
        
        # 标准Word标题样式
        heading_patterns = [
            (r'^Heading\s+(\d+)$', 1),      # Heading 1 -> level 1
            (r'^标题\s*(\d+)$', 1),         # 标题1 -> level 1
            (r'^Heading(\d+)$', 1),         # Heading1 -> level 1
        ]
        
        for pattern, base_level in heading_patterns:
            match = re.match(pattern, style_name, re.IGNORECASE)
            if match:
                level_num = int(match.group(1))
                return level_num
        
        return 0
    
    def _is_valid_heading(self, text: str) -> bool:
        """判断文本是否是有效的标题"""
        # 过滤条件
        if len(text) > 200:  # 标题太长
            return False
        
        if len(text) < 2:    # 标题太短
            return False
        
        # 过滤明显不是标题的内容模式
        invalid_patterns = [
            r'^\d+[\.\)]\s*$',              # 仅数字编号
            r'^[，。！？；：""''（）【】]+$',     # 仅标点符号
            r'^\s*$',                       # 仅空白字符
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, text):
                return False
        
        return True
    
    def _estimate_page_number(self, paragraph_index: int) -> int:
        """估算页码（简单估算）"""
        # 假设每页大约25-30个段落
        return max(1, (paragraph_index - 1) // 28 + 1)
    
    def get_formatted_toc(self, headings: Optional[List[HeadingEntry]] = None) -> str:
        """获取格式化的目录"""
        if headings is None:
            headings = self.extract_headings()
        
        if not headings:
            return "未找到标题内容"
        
        toc_lines = []
        toc_lines.append("📋 基于标题样式的目录")
        toc_lines.append("=" * 50)
        
        for i, entry in enumerate(headings, 1):
            # 根据级别添加缩进
            indent = "  " * (entry.level - 1)
            page_info = f"第{entry.page}页" if entry.page else "页码未知"
            
            toc_lines.append(f"{i:2d}. {indent}{entry.title} ... {page_info}")
        
        return "\n".join(toc_lines)
    
    def extract_structured_toc(self) -> List[dict]:
        """提取结构化的目录数据"""
        headings = self.extract_headings()
        
        structured_data = []
        for entry in headings:
            structured_data.append({
                'title': entry.title,
                'level': entry.level,
                'page': entry.page or 1,
                'style': entry.style_name,
                'paragraph_index': entry.paragraph_index,
                'type': 'heading_based'
            })
        
        return structured_data

def main():
    """测试基于标题样式的TOC提取器"""
    
    test_files = [
        "data/input/1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx",
        "data/input/计算机应用技术_test1.docx"
    ]
    
    for test_file in test_files:
        print(f"🔍 测试基于标题样式的TOC提取: {test_file}")
        print("=" * 80)
        
        try:
            # 创建提取器
            extractor = HeadingBasedTOCExtractor(test_file)
            
            # 提取标题
            headings = extractor.extract_headings()
            
            if headings:
                print(f" 成功提取到 {len(headings)} 个标题:")
                print()
                
                for entry in headings:
                    indent = "  " * (entry.level - 1)
                    print(f"[{entry.style_name}] {indent}{entry.title}")
                
                print("\n" + "-" * 60)
                print(extractor.get_formatted_toc(headings))
                
                # 获取结构化数据
                structured_data = extractor.extract_structured_toc()
                print(f"\n📊 结构化数据: {len(structured_data)} 个条目")
                
            else:
                print("❌ 未提取到标题")
                
        except Exception as e:
            print(f"❌ 提取过程出错: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()

