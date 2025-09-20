"""
智能参考文献提取器
专门优化用于DOCX文件格式的参考文献提取
- 精确边界检测：智能识别"致谢与声明"等结束标记
- 多模式匹配：支持［1］、[1]、1.、(1)等多种编号格式
- 内容验证：验证参考文献的完整性和格式正确性
"""

import re
import os
import time
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path

class SmartReferenceExtractor:
    """智能参考文献提取器 - 专门用于DOCX文件"""
    
    def __init__(self, ai_client=None):
        # 不再使用AI客户端，专注于DOCX处理
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
    
    def _extract_with_ai(self, ref_text: str) -> List[str]:
        """使用AI智能提取参考文献（适合PDF格式）"""
        print("🤖 使用AI智能提取方法...")
        
        if not self.ai_client:
            print("❌ AI客户端不可用，回退到正则方法")
            return self._extract_with_regex(ref_text)
        
        # 分段处理大文档
        if len(ref_text) > 20000:
            return self._extract_with_ai_chunked(ref_text)
        
        # 构建智能提示词
        prompt = f"""请从以下参考文献文本中精确提取所有参考文献条目。这段文本可能来自PDF转换，格式可能不规整。

重要要求：
1. 识别所有参考文献条目，无论编号格式（［1］、[1]、(1)、1.等）
2. 处理全角半角字符混用问题
3. 清理PDF转换产生的格式错误（多余空格、断行等）
4. 每条参考文献重组为一行完整记录
5. 保持作者、标题、期刊、年份等关键信息完整
6. 按原编号顺序输出
7. 输出格式：每行一条参考文献，编号在前

文本内容：
{ref_text[:15000]}

请提取所有参考文献："""

        try:
            response = self.ai_client.send_message(prompt)
            if response and hasattr(response, 'content'):
                content = response.content.strip()
                references = self._parse_ai_response(content)
                print(f"   ✅ AI提取到 {len(references)} 条参考文献")
                return references
        except Exception as e:
            print(f"   ❌ AI提取失败: {e}")
        
        # AI失败时回退到正则方法
        return self._extract_with_regex(ref_text)
    
    def _extract_with_ai_chunked(self, ref_text: str) -> List[str]:
        """分块处理大型参考文献文本"""
        print("📦 文档较大，分块处理...")
        
        # 智能分块：在引用条目边界分割
        chunks = self._smart_chunk_text(ref_text, max_size=15000)
        all_references = []
        
        for i, chunk in enumerate(chunks, 1):
            print(f"🔄 处理第 {i}/{len(chunks)} 块...")
            
            prompt = f"""从以下参考文献片段中提取所有完整的参考文献条目：

要求：
1. 只提取完整的参考文献条目
2. 处理格式问题（全角括号、换行等）
3. 每行输出一条参考文献
4. 保持编号顺序

文本片段：
{chunk}

参考文献条目："""
            
            try:
                response = self.ai_client.send_message(prompt)
                if response and hasattr(response, 'content'):
                    chunk_refs = self._parse_ai_response(response.content)
                    all_references.extend(chunk_refs)
                    print(f"   ✅ 提取到 {len(chunk_refs)} 条参考文献")
            except Exception as e:
                print(f"   ❌ 第{i}块提取失败: {e}")
        
        # 去重并排序
        unique_refs = self._deduplicate_references(all_references)
        print(f"📊 合并结果: {len(unique_refs)} 条唯一参考文献")
        
        return unique_refs
    
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
    
    def _extract_with_hybrid(self, ref_text: str) -> List[str]:
        """混合策略提取"""
        print("🔄 使用混合策略提取...")
        
        # 先尝试正则方法
        regex_refs = self._extract_with_regex(ref_text)
        
        # 评估正则结果质量
        if len(regex_refs) >= 20:  # 如果找到足够多的引用
            # 检查格式质量
            quality_score = self._assess_reference_quality(regex_refs)
            if quality_score > 0.7:  # 质量良好
                print(f"   ✅ 正则方法质量良好 (评分: {quality_score:.2f})")
                return regex_refs
        
        # 正则结果不理想，使用AI方法
        print("   🤖 正则结果不理想，切换到AI方法...")
        return self._extract_with_ai(ref_text)
    
    def _smart_chunk_text(self, text: str, max_size: int = 15000) -> List[str]:
        """智能分块文本，在引用边界分割"""
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            end_pos = min(current_pos + max_size, len(text))
            
            # 如果不是最后一块，尝试在引用边界分割
            if end_pos < len(text):
                # 寻找最近的引用开始位置
                search_start = max(end_pos - 1000, current_pos + max_size // 2)
                ref_pattern = r'［\d+］|\[\d+\]|\n\d+\.'
                
                matches = list(re.finditer(ref_pattern, text[search_start:end_pos + 500]))
                if matches:
                    # 找到最合适的分割点
                    best_match = matches[len(matches) // 2]  # 选择中间的匹配
                    match_start = best_match.start()
                    if match_start is not None:
                        end_pos = search_start + match_start
            
            chunk = text[current_pos:end_pos].strip()
            if chunk:
                chunks.append(chunk)
            
            current_pos = end_pos
        
        return chunks
    
    def _parse_ai_response(self, content: str) -> List[str]:
        """解析AI响应内容"""
        references = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是有效的参考文献条目
            if self._is_valid_reference(line):
                # 清理格式
                cleaned_ref = re.sub(r'\s+', ' ', line).strip()
                references.append(cleaned_ref)
        
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
    
    def _deduplicate_references(self, references: List[str]) -> List[str]:
        """去重参考文献"""
        seen = set()
        unique_refs = []
        
        for ref in references:
            # 使用前50个字符作为重复检测的键
            key = re.sub(r'^\s*(?:［\d+］|\[\d+\]|\d+\.)', '', ref)[:50].strip()
            if key not in seen and key:
                seen.add(key)
                unique_refs.append(ref)
        
        # 按编号排序
        unique_refs.sort(key=lambda x: self._extract_number(x))
        return unique_refs
    
    def _extract_number(self, ref: str) -> int:
        """从参考文献中提取编号"""
        match = re.search(r'［(\d+)］|\[(\d+)\]|^(\d+)\.', ref)
        if match:
            for group in match.groups():
                if group:
                    return int(group)
        return 999999  # 无编号的放到最后
    
    def _assess_reference_quality(self, references: List[str]) -> float:
        """评估参考文献提取质量"""
        if not references:
            return 0.0
        
        score = 0.0
        total_checks = len(references)
        
        for ref in references:
            # 检查编号连续性
            if re.match(r'^\s*(?:［\d+］|\[\d+\]|\d+\.)', ref):
                score += 0.3
            
            # 检查包含关键信息
            if any(keyword in ref for keyword in ['Journal', '期刊', 'Conference', 'Proceedings']):
                score += 0.3
            
            # 检查包含年份
            if re.search(r'19\d{2}|20\d{2}', ref):
                score += 0.2
            
            # 检查长度合理
            if 30 <= len(ref) <= 500:
                score += 0.2
        
        return score / total_checks if total_checks > 0 else 0.0
