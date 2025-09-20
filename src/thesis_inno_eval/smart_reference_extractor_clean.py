"""
智能参考文献提取器
专门优化用于DOCX文件格式的参考文献提取
- 精确边界检测：智能识别"致谢与声明"等结束标记
- 多模式匹配：支持［1］、[1]、1.、(1)等多种编号格式
- 内容验证：验证参考文献的完整性和格式正确性
"""

import re
import time
from typing import List, Optional, Tuple, Dict, Any

class SmartReferenceExtractor:
    """智能参考文献提取器 - 专门用于DOCX文件"""
    
    def __init__(self, ai_client=None):
        # 不使用AI客户端，专注于DOCX处理
        self.extraction_stats = {
            'method_used': '',
            'total_found': 0,
            'processing_time': 0.0,
            'success': False
        }
    
    def extract_references(self, text: str, source_format: str = 'docx', 
                          source_path: str = '') -> Tuple[List[str], Dict[str, Any]]:
        """
        智能提取参考文献（专门用于DOCX文件）
        
        Args:
            text: 文档文本内容
            source_format: 源格式 (固定为'docx')
            source_path: 源文件路径
        
        Returns:
            Tuple[List[str], Dict[str, Any]]: (参考文献列表, 提取统计信息)
        """
        start_time = time.time()
        
        print(f"📄 检测到文档格式: DOCX")
        
        # 定位参考文献区域
        ref_section = self._locate_reference_section(text)
        if not ref_section:
            print("❌ 未找到参考文献区域")
            return [], {'error': '未找到参考文献区域'}
        
        print(f"📍 参考文献区域长度: {len(ref_section):,} 字符")
        
        # 使用优化的正则提取方法
        references = self._extract_with_regex(ref_section)
        method = '传统正则提取'
        
        # 计算统计信息
        processing_time = time.time() - start_time
        self.extraction_stats.update({
            'method_used': method,
            'total_found': len(references),
            'processing_time': processing_time,
            'success': len(references) > 0
        })
        
        print(f"✅ 提取完成: {len(references)} 条参考文献 (用时 {processing_time:.2f}秒)")
        print(f"🔧 使用方法: {method}")
        
        return references, self.extraction_stats
    
    def _locate_reference_section(self, text: str) -> str:
        """智能定位参考文献区域，专门优化用于docx格式"""
        start_pos, end_pos = self._get_reference_boundaries(text)
        if start_pos != -1 and end_pos != -1:
            return text[start_pos:end_pos]
        return ""
    
    def _get_reference_boundaries(self, text: str) -> tuple[int, int]:
        """获取参考文献的开始和结束位置坐标"""
        print("🔍 开始定位参考文献区域...")
        
        # 多种模式查找参考文献标题
        patterns = [
            r'#+\s*参考文献\s*\n',
            r'参考文献\s*\n',
            r'References\s*\n',
            r'REFERENCES\s*\n',
            r'参\s*考\s*文\s*献',
        ]
        
        ref_start_pos = None
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                ref_start_pos = match.start()
                print(f"✅ 找到参考文献标题: '{match.group().strip()}' (位置: {ref_start_pos})")
                break
        
        if ref_start_pos is None:
            print("❌ 未找到参考文献标题")
            return -1, -1
        
        # 查找参考文献结束位置
        # 专门处理"致谢与声明"边界问题
        end_markers = [
            '致谢与声明',     # 优先匹配完整的"致谢与声明"
            '致谢',          # 其次匹配"致谢"
            'ACKNOWLEDGMENT',
            'ACKNOWLEDGEMENT', 
            '附录',
            'APPENDIX',
            '个人简历',
            '作者简介',
            '攻读学位期间发表',
        ]
        
        remaining_text = text[ref_start_pos:]
        ref_end_relative = len(remaining_text)  # 默认到文档末尾
        
        print("🔍 查找参考文献结束标记...")
        for marker in end_markers:
            marker_pos = remaining_text.find(marker)
            if marker_pos != -1:
                print(f"   ✅ 找到结束标记: '{marker}' (相对位置: {marker_pos})")
                ref_end_relative = marker_pos
                break
        
        # 计算绝对结束位置
        ref_end_pos = ref_start_pos + ref_end_relative
        
        print(f"📍 参考文献区域定位完成:")
        print(f"   📏 总长度: {ref_end_relative:,} 字符")
        print(f"   📋 开始位置: {ref_start_pos}")
        print(f"   📋 结束位置: {ref_end_pos}")
        
        # 验证提取的内容
        if ref_end_relative < 100:
            print("⚠️ 参考文献区域过短，可能提取有误")
            return -1, -1
        
        # 统计参考文献条目数量（粗略估计）
        ref_section = text[ref_start_pos:ref_end_pos]
        ref_count_estimate = len(re.findall(r'［\d+］|\[\d+\]|\n\d+\.', ref_section))
        print(f"   📊 估计参考文献条目数: {ref_count_estimate}")
        
        return ref_start_pos, ref_end_pos
    
    def _extract_with_regex(self, ref_text: str) -> List[str]:
        """使用传统正则表达式提取（专门优化用于Word格式）"""
        print("⚡ 使用传统正则提取方法 (docx优化版)...")

        references = []

        # 专门为docx优化的正则模式 - 更精确，处理致谢与声明边界
        patterns = [
            # 全角括号 - 行首或换行后，避免匹配期刊号
            r'(?:^|\n)［(\d+)］([^\n]+(?:\n(?!［\d+］|致谢与声明|致谢|个人简历)[^\n]+)*)',  
            # 半角括号 - 行首或换行后
            r'(?:^|\n)\[(\d+)\]([^\n]+(?:\n(?!\[\d+\]|致谢与声明|致谢|个人简历)[^\n]+)*)',   
            # 数字点号 - 行首
            r'(?:^|\n)(\d+)\.([^\n]+(?:\n(?!^\d+\.|致谢与声明|致谢|个人简历)[^\n]+)*)',     
            # 圆括号 - 行首或换行后
            r'(?:^|\n)\((\d+)\)([^\n]+(?:\n(?!\(\d+\)|致谢与声明|致谢|个人简历)[^\n]+)*)',   
        ]

        print(f"📄 参考文献区域总长度: {len(ref_text):,} 字符")

        # 记录所有匹配的编号及其位置
        all_matches = []
        for i, pattern in enumerate(patterns):
            matches = list(re.finditer(pattern, ref_text, re.MULTILINE))
            print(f"   🔍 模式 {i+1}: 找到 {len(matches)} 个匹配")
            
            for m in matches:
                try:
                    num = int(m.group(1))
                    content = m.group(2).strip()
                    start = m.start()
                    end = m.end()
                    all_matches.append((num, content, start, end, i))
                except (ValueError, IndexError):
                    continue

        print(f"📊 总共找到 {len(all_matches)} 个潜在参考文献")

        # 按位置排序，确保顺序
        all_matches.sort(key=lambda x: x[2])  # 按start位置排序
        
        # 智能过滤：只保留编号连续且合理的参考文献
        valid_refs = []
        expected_num = 1
        tolerance = 5  # 允许的编号跳跃容忍度
        
        for num, content, start, end, pattern_type in all_matches:
            # 检查编号是否过大（可能是期刊号等）
            if num > 1000:
                print(f"   ⚠️ 跳过异常编号 [{num}]（可能是期刊号等）")
                continue
                
            # 检查编号是否大致连续
            if valid_refs and num > expected_num + tolerance:
                print(f"   ⚠️ 跳过不连续编号 [{num}]（期望≤{expected_num + tolerance}，实际{num}）")
                continue
                
            # 检查内容长度
            if len(content) < 20:
                print(f"   ⚠️ 跳过过短内容 [{num}]（{len(content)} 字符）")
                continue
                
            # 清理内容
            clean_content = re.sub(r'\s+', ' ', content).strip()
            
            # 验证是否为有效参考文献
            if self._is_valid_reference(f"[{num}] {clean_content}"):
                ref_line = f"[{num}] {clean_content}"
                valid_refs.append((num, ref_line, end))
                expected_num = max(expected_num, num + 1)
                print(f"   ✅ 添加参考文献 [{num}]: {clean_content[:50]}...")

        # 按编号排序
        valid_refs.sort(key=lambda x: x[0])
        references = [ref for _, ref, _ in valid_refs]

        # 质量检查
        if references:
            min_num = min(ref[0] for ref in valid_refs)
            max_num = max(ref[0] for ref in valid_refs)
            print(f"   📋 提取质量报告:")
            print(f"      - 参考文献数量: {len(references)}")
            print(f"      - 编号范围: {min_num}-{max_num}")
            print(f"      - 平均长度: {sum(len(ref) for _, ref, _ in valid_refs) // len(valid_refs)} 字符")
        
        return references
    
    def _is_valid_reference(self, line: str) -> bool:
        """检查是否是有效的参考文献条目"""
        # 基本长度检查
        if len(line) < 20:
            return False
        
        # 检查是否包含编号格式
        has_number = bool(re.match(r'^\s*(?:［\d+］|\[\d+\]|\d+\.|（\d+）|\(\d+\))', line))
        if not has_number:
            return False
        
        # 提取编号
        number_match = re.search(r'(?:［(\d+)］|\[(\d+)\]|^(\d+)\.|（(\d+)）|\((\d+)\))', line)
        if number_match:
            num = None
            for group in number_match.groups():
                if group:
                    num = int(group)
                    break
            
            # 如果编号过大，可能是期刊号误识别
            if num and num > 500:
                return False
        
        # 检查是否包含期刊、会议、出版社等关键词（扩展中文关键词）
        publication_keywords = [
            # 英文关键词
            'Journal', 'Proceedings', 'Conference', 'IEEE', 'ACM', 'Optics',
            'Nature', 'Science', 'Physical Review', 'Applied Physics', 'et al',
            # 中文关键词
            '期刊', '会议', '学报', '大学学报', '论文集', '出版社', '学院学报',
            '音乐学院', '艺术学院', '师范大学', '大学出版社', '人民出版社',
            '文艺出版社', '音乐出版社', '上海音乐', '中央音乐', '沧桑',
            '戏剧', '音乐', '艺术', '文化', '研究', '分析', '探讨', '论文',
            '硕士', '博士', '学位论文', '毕业论文', '年第', '期', '页',
            '编', '著', '主编', '总编', '卷', '册', '版'
        ]
        
        has_publication = any(keyword in line for keyword in publication_keywords)
        
        # 检查是否包含年份
        has_year = bool(re.search(r'19\d{2}|20\d{2}', line))
        
        # 检查是否包含作者信息（扩展中文作者模式）
        author_patterns = [
            r'[A-Z]\.\s*[A-Z]',  # 英文缩写
            r'et al',            # 英文等
            r'等',               # 中文等
            r'[\u4e00-\u9fff]{2,4}：',  # 中文姓名后跟冒号
            r'[\u4e00-\u9fff]{2,4}编',  # 编者
            r'[\u4e00-\u9fff]{2,4}著',  # 著者
            r'[\u4e00-\u9fff]{2,4}主编', # 主编
        ]
        
        has_author = any(re.search(pattern, line) for pattern in author_patterns)
        
        # 放宽验证条件：只需要满足其中两个条件即可
        valid_conditions = [has_publication, has_year, has_author]
        return sum(valid_conditions) >= 2
