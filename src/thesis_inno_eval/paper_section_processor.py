"""
论文章节分段处理模块
按照论文逻辑章节进行分段，而不是简单按长度分段
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PaperSection:
    """论文章节数据结构"""
    title: str  # 章节标题
    content: str  # 章节内容
    section_type: str  # 章节类型
    level: int  # 章节层级 (1-标题, 2-一级标题, 3-二级标题等)
    order: int  # 章节顺序

class PaperSectionParser:
    """论文章节解析器"""
    
    def __init__(self):
        # 定义论文章节模式 - 中英文混合
        self.section_patterns = {
            # 摘要相关
            'abstract': [
                r'(?:摘\s*要|ABSTRACT|Abstract|abstract)',
                r'(?:中文摘要|英文摘要)',
                r'(?:关键词|Keywords|关键字)',
            ],
            
            # 引言/导论
            'introduction': [
                r'(?:引\s*言|导\s*论|前\s*言|绪\s*论)',
                r'(?:INTRODUCTION|Introduction|introduction)',
                r'(?:背景|研究背景|Background)',
            ],
            
            # 文献综述/相关工作
            'literature_review': [
                r'(?:文献综述|相关工作|研究现状)',
                r'(?:国内外研究现状|国内外发展现状)',
                r'(?:LITERATURE\s*REVIEW|Literature\s*Review|Related\s*Work)',
                r'(?:理论基础|理论背景)',
            ],
            
            # 理论框架/系统设计
            'theory_framework': [
                r'(?:理论框架|理论基础|概念框架)',
                r'(?:系统设计|系统架构|架构设计)',
                r'(?:THEORY|Theory|FRAMEWORK|Framework)',
                r'(?:设计思路|设计原理)',
            ],
            
            # 方法/算法
            'methodology': [
                r'(?:研究方法|方法|算法|模型)',
                r'(?:METHODOLOGY|Methodology|METHOD|Method)',
                r'(?:技术路线|实现方案|解决方案)',
                r'(?:算法设计|模型构建)',
            ],
            
            # 实验/实现
            'experiment': [
                r'(?:实验|试验|测试|验证)',
                r'(?:EXPERIMENT|Experiment|IMPLEMENTATION|Implementation)',
                r'(?:实验设计|实验方案|实验过程)',
                r'(?:性能测试|功能测试)',
            ],
            
            # 结果/分析
            'results': [
                r'(?:结果|实验结果|测试结果)',
                r'(?:RESULTS|Results|ANALYSIS|Analysis)',
                r'(?:数据分析|结果分析|性能分析)',
                r'(?:讨论|Discussion)',
            ],
            
            # 结论
            'conclusion': [
                r'(?:结论|总结|小结)',
                r'(?:CONCLUSION|Conclusion|SUMMARY|Summary)',
                r'(?:研究结论|主要结论)',
                r'(?:展望|未来工作|Future\s*Work)',
            ],
            
            # 参考文献
            'references': [
                r'(?:参考文献|引用文献|文献)',
                r'(?:REFERENCES|References|BIBLIOGRAPHY|Bibliography)',
            ],
            
            # 附录
            'appendix': [
                r'(?:附录|APPENDIX|Appendix)',
            ]
        }
        
        # 章节标题模式 - 检测各种章节标题格式
        self.title_patterns = [
            # 数字编号: 1. 1.1 1.1.1 等
            r'^(\d+(?:\.\d+)*\.?)\s*(.+?)(?:\s*\.{3,}.*)?$',
            # 中文编号: 一、二、三、（一）（二）等
            r'^([一二三四五六七八九十百]+[、．.]|（[一二三四五六七八九十百]+）)\s*(.+?)(?:\s*\.{3,}.*)?$',
            # 英文编号: I. II. III. A. B. C. 等
            r'^([IVX]+[\.、]|[A-Z][\.、])\s*(.+?)(?:\s*\.{3,}.*)?$',
            # 纯标题（无编号但有特殊格式）
            r'^([A-Z][A-Z\s]+|[^\w\s]*(.{1,50})[^\w\s]*)$',
        ]
    
    def parse_sections(self, text: str) -> List[PaperSection]:
        """解析论文文本为章节列表"""
        logger.info("开始解析论文章节...")
        
        sections = []
        lines = text.split('\n')
        current_section = None
        section_order = 0
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过空行
            if not line:
                i += 1
                continue
            
            # 检测是否为章节标题
            section_info = self._detect_section_title(line)
            
            if section_info:
                # 保存之前的章节
                if current_section and current_section.content.strip():
                    sections.append(current_section)
                
                # 创建新章节
                section_order += 1
                current_section = PaperSection(
                    title=section_info['title'],
                    content="",
                    section_type=section_info['type'],
                    level=section_info['level'],
                    order=section_order
                )
                logger.debug(f"发现章节: {current_section.title} (类型: {current_section.section_type})")
            else:
                # 添加内容到当前章节
                if current_section:
                    current_section.content += line + '\n'
                else:
                    # 创建默认的开头章节
                    if not sections:
                        section_order += 1
                        current_section = PaperSection(
                            title="论文开头",
                            content=line + '\n',
                            section_type='header',
                            level=1,
                            order=section_order
                        )
            
            i += 1
        
        # 添加最后一个章节
        if current_section and current_section.content.strip():
            sections.append(current_section)
        
        logger.info(f"共解析出 {len(sections)} 个章节")
        for section in sections:
            logger.debug(f"章节: {section.title} ({len(section.content)} 字符, 类型: {section.section_type})")
        
        return sections
    
    def _detect_section_title(self, line: str) -> Optional[Dict]:
        """检测是否为章节标题"""
        line_clean = line.strip()
        
        # 长度过长或过短的行不太可能是标题
        if len(line_clean) > 100 or len(line_clean) < 2:
            return None
        
        # 检测各种标题模式
        for pattern in self.title_patterns:
            match = re.match(pattern, line_clean, re.IGNORECASE)
            if match:
                # 提取标题文本
                if len(match.groups()) >= 2 and match.group(2):
                    title_text = match.group(2).strip()
                else:
                    title_text = match.group(1).strip() if match.group(1) else line_clean
                
                # 判断章节类型
                section_type = self._classify_section_type(title_text)
                
                # 判断章节层级
                level = self._determine_section_level(match.group(1) if match.group(1) else "")
                
                return {
                    'title': title_text,
                    'type': section_type,
                    'level': level
                }
        
        # 特殊情况：检查是否为明显的章节关键词
        section_type = self._classify_section_type(line_clean)
        if section_type != 'unknown':
            return {
                'title': line_clean,
                'type': section_type,
                'level': 2
            }
        
        return None
    
    def _classify_section_type(self, title: str) -> str:
        """根据标题内容分类章节类型"""
        title_lower = title.lower()
        
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, title, re.IGNORECASE):
                    return section_type
        
        return 'unknown'
    
    def _determine_section_level(self, number_part: str) -> int:
        """根据编号确定章节层级（限制到级别2）"""
        if not number_part:
            return 2
        
        # 计算数字编号的层级，但限制最大为2级
        dots = number_part.count('.')
        if dots == 0:
            return 1  # 一级标题
        else:
            return 2  # 二级及以下统一为二级
    
    def merge_small_sections(self, sections: List[PaperSection], min_length: int = 200) -> List[PaperSection]:
        """合并过小的章节到相邻章节"""
        if not sections:
            return sections
        
        merged_sections = []
        current_section = sections[0]
        
        for i in range(1, len(sections)):
            next_section = sections[i]
            
            # 如果当前章节太小，合并到下一个章节
            if len(current_section.content.strip()) < min_length and next_section.section_type != 'references':
                current_section.content += f"\n\n## {next_section.title}\n{next_section.content}"
                if current_section.section_type == 'unknown':
                    current_section.section_type = next_section.section_type
            else:
                merged_sections.append(current_section)
                current_section = next_section
        
        # 添加最后一个章节
        merged_sections.append(current_section)
        
        logger.info(f"章节合并后：{len(sections)} -> {len(merged_sections)} 个章节")
        return merged_sections

class PaperSectionProcessor:
    """论文章节处理器 - 协调解析和AI处理"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.parser = PaperSectionParser()
    
    def create_section_batches(self, sections: List[PaperSection], 
                             max_chars: int = 10000) -> List[List[PaperSection]]:
        """
        将章节按字符数和逻辑顺序打包成批次
        
        Args:
            sections: 章节列表（按照章节顺序排列）
            max_chars: 每批次最大字符数（默认1万字）
            
        Returns:
            批次列表，每个批次包含相邻的多个章节
        """
        batches = []
        current_batch = []
        current_chars = 0
        
        logger.info(f"开始创建章节批次，总章节数: {len(sections)}，每批次最大字符数: {max_chars:,}")
        
        for i, section in enumerate(sections):
            section_chars = len(section.content)
            
            # 如果单个章节就超过限制，单独成一批次
            if section_chars > max_chars:
                # 先保存当前批次（如果有内容）
                if current_batch:
                    batches.append(current_batch)
                    logger.info(f"批次 {len(batches)}: {len(current_batch)} 个章节, {current_chars:,} 字符")
                    current_batch = []
                    current_chars = 0
                
                # 大章节单独成批次
                batches.append([section])
                logger.info(f"批次 {len(batches)}: 1 个大章节 ('{section.title}'), {section_chars:,} 字符")
                continue
            
            # 如果添加当前章节会超过限制，先保存当前批次
            if current_chars + section_chars > max_chars and current_batch:
                batches.append(current_batch)
                logger.info(f"批次 {len(batches)}: {len(current_batch)} 个章节, {current_chars:,} 字符")
                current_batch = []
                current_chars = 0
            
            # 添加当前章节到批次
            current_batch.append(section)
            current_chars += section_chars
            
            logger.debug(f"章节 {i+1}: '{section.title}' ({section_chars:,} 字符) -> 当前批次: {current_chars:,} 字符")
        
        # 添加最后一个批次
        if current_batch:
            batches.append(current_batch)
            logger.info(f"批次 {len(batches)}: {len(current_batch)} 个章节, {current_chars:,} 字符")
        
        logger.info(f"章节批次创建完成，共 {len(batches)} 个批次")
        return batches
    
    def process_paper_by_batches(self, text: str, session_id: Optional[str] = None, 
                               max_chars_per_batch: int = 10000) -> Optional[Dict[str, Any]]:
        """
        按批次处理论文，将相邻章节打包成1万字以内的数据包
        
        Args:
            text: 论文文本
            session_id: 会话ID
            max_chars_per_batch: 每批次最大字符数
            
        Returns:
            合并后的结构化信息
        """
        logger.info("开始按批次处理论文...")
        
        # 1. 解析章节
        sections = self.parser.parse_sections(text)
        if not sections:
            logger.error("无法解析论文章节")
            return None
        
        # 2. 合并过小的章节
        sections = self.parser.merge_small_sections(sections, min_length=200)
        
        # 3. 创建章节批次
        batches = self.create_section_batches(sections, max_chars_per_batch)
        
        # 4. 逐批次处理
        all_results = {}
        total_batches = len(batches)
        
        for batch_idx, batch in enumerate(batches, 1):
            logger.info(f"处理批次 {batch_idx}/{total_batches}: {len(batch)} 个章节")
            
            try:
                # 添加请求间隔，避免API限流
                if batch_idx > 1:
                    import time
                    time.sleep(2)  # 2秒间隔
                
                batch_result = self._process_section_batch(batch, session_id)
                if batch_result:
                    # 合并结果
                    for key, value in batch_result.items():
                        if key in all_results:
                            if isinstance(value, str) and isinstance(all_results[key], str):
                                all_results[key] += f"\n\n{value}"
                            elif isinstance(value, list) and isinstance(all_results[key], list):
                                all_results[key].extend(value)
                            else:
                                all_results[key] = value
                        else:
                            all_results[key] = value
                    
                    logger.info(f"批次 {batch_idx} 处理成功，累计字段: {len(all_results)}")
                else:
                    logger.warning(f"批次 {batch_idx} 处理失败")
                    
            except Exception as e:
                logger.error(f"批次 {batch_idx} 处理出错: {e}")
                continue
        
        if all_results:
            logger.info(f"论文批次处理完成，共提取 {len(all_results)} 个字段")
            return all_results
        else:
            logger.error("所有批次处理都失败")
            return None
    
    def _process_section_batch(self, batch: List[PaperSection], session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        处理一个章节批次
        
        Args:
            batch: 章节批次（相邻的多个章节）
            session_id: 会话ID
            
        Returns:
            提取的结构化信息
        """
        if not batch:
            return None
        
        # 构建批次内容
        batch_content = ""
        section_titles = []
        
        for section in batch:
            section_titles.append(section.title)
            batch_content += f"\n\n## {section.title}\n{section.content}"
        
        batch_chars = len(batch_content)
        logger.info(f"处理批次: {', '.join(section_titles)} ({batch_chars:,} 字符)")
        
        # 构建针对批次的提示词
        prompt = f"""请从以下论文章节内容中提取结构化信息，并以JSON格式返回。

这个批次包含以下章节：
{', '.join(section_titles)}

请提取以下信息（如果章节中包含相关内容）：
{{
  "title_cn": "中文标题",
  "title_en": "英文标题", 
  "abstract_cn": "中文摘要",
  "abstract_en": "英文摘要",
  "keywords_cn": "中文关键词",
  "keywords_en": "英文关键词",
  "literature_review": "文献综述内容",
  "research_methods": "研究方法",
  "theoretical_framework": "理论框架",
  "main_innovations": "主要创新点",
  "practical_problems": "实践问题",
  "proposed_solutions": "提出的解决方案",
  "research_conclusions": "研究结论",
  "application_value": "应用价值",
  "references": "参考文献列表"
}}

输出要求：
- 只提取当前批次章节中包含的信息
- 如果某项信息不存在，请输出空字符串""
- 直接返回JSON对象，不要代码块标记
- 字符串值中不要包含控制字符

章节内容：
{batch_content}
"""
        
        try:
            # 发送请求到AI
            response = self.ai_client.send_message(prompt, session_id=session_id)
            if not response or not response.content:
                logger.error("AI返回空响应")
                return None
            
            response_text = response.content.strip()
            logger.debug(f"AI响应长度: {len(response_text)} 字符")
            
            # 解析JSON响应
            from .extract_sections_with_ai import _extract_json_from_response, _clean_json_content, _parse_json_with_fallback
            
            json_content = _extract_json_from_response(response_text)
            if not json_content:
                logger.error("无法从响应中提取JSON内容")
                return None
            
            cleaned_json = _clean_json_content(json_content)
            result = _parse_json_with_fallback(cleaned_json)
            
            if result:
                # 过滤掉空值
                filtered_result = {k: v for k, v in result.items() if v and v.strip()}
                logger.info(f"批次处理成功，提取字段: {list(filtered_result.keys())}")
                return filtered_result
            else:
                logger.error("JSON解析失败")
                return None
                
        except Exception as e:
            logger.error(f"处理批次时出错: {e}")
            return None
    
    def process_paper_by_sections(self, text: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """按章节处理论文，返回结构化信息"""
        logger.info(f"🚀 开始按章节处理论文，文本长度: {len(text):,} 字符")
        
        # 1. 解析章节
        logger.info("📖 第一步：解析论文章节结构...")
        sections = self.parser.parse_sections(text)
        if not sections:
            logger.error("❌ 无法解析论文章节")
            return None
        
        logger.info(f"✅ 解析到 {len(sections)} 个章节")
        for i, section in enumerate(sections, 1):
            logger.info(f"   章节 {i}: {section.title} ({section.section_type}, {len(section.content):,} 字符)")
        
        # 2. 合并过小的章节
        logger.info("🔗 第二步：合并过小的章节...")
        original_count = len(sections)
        sections = self.parser.merge_small_sections(sections, min_length=200)
        if len(sections) != original_count:
            logger.info(f"✅ 章节合并完成，从 {original_count} 个合并为 {len(sections)} 个")
        else:
            logger.info("✅ 无需合并章节")
        
        # 3. 按章节提取信息
        logger.info(f"🎯 第三步：逐个处理章节内容...")
        extraction_results = {}
        total_sections = len(sections)
        
        for i, section in enumerate(sections, 1):
            logger.info(f"📝 处理章节 {i}/{total_sections}: 《{section.title}》")
            logger.info(f"   ├─ 章节类型: {section.section_type}")
            logger.info(f"   ├─ 内容长度: {len(section.content):,} 字符")
            logger.info(f"   └─ 开始AI分析...")
            
            try:
                section_info = self._extract_section_info(section, session_id)
                if section_info:
                    extraction_results[section.section_type] = section_info
                    logger.info(f"   ✅ 章节《{section.title}》处理成功，提取到 {len(section_info)} 个字段")
                else:
                    logger.warning(f"   ❌ 章节《{section.title}》处理失败 - AI返回空结果")
            except Exception as e:
                logger.error(f"   💥 处理章节《{section.title}》时出错: {e}")
                continue
        
        # 4. 整合所有章节信息
        logger.info(f"🔗 第四步：整合所有章节信息...")
        logger.info(f"   成功处理的章节: {list(extraction_results.keys())}")
        
        final_result = self._integrate_section_results(extraction_results, sections)
        
        if final_result:
            logger.info(f"🎉 论文章节处理完成！")
            logger.info(f"   ├─ 处理成功: {len(extraction_results)}/{total_sections} 个章节")
            logger.info(f"   ├─ 最终字段: {len(final_result)} 个")
            logger.info(f"   └─ 字段列表: {list(final_result.keys())}")
        else:
            logger.error(f"❌ 章节信息整合失败")
        
        return final_result
    
    def _extract_section_info(self, section: PaperSection, session_id: Optional[str] = None) -> Optional[Dict]:
        """从单个章节提取信息"""
        # 根据章节类型生成特定的提示词
        logger.info(f"     🤖 为章节《{section.title}》生成AI提示词...")
        prompt = self._generate_section_prompt(section)
        prompt_length = len(prompt)
        logger.info(f"     📝 提示词长度: {prompt_length:,} 字符")
        
        try:
            logger.info(f"     🔗 发送AI请求...")
            import time
            start_time = time.time()
            
            response = self.ai_client.send_message(prompt, session_id=session_id)
            
            elapsed_time = time.time() - start_time
            logger.info(f"     ⏱️  AI响应时间: {elapsed_time:.2f} 秒")
            
            if response and response.content:
                response_length = len(response.content)
                logger.info(f"     📤 AI响应长度: {response_length:,} 字符")
                logger.info(f"     🔍 开始解析AI响应...")
                
                # 解析AI返回的结构化信息
                result = self._parse_section_response(response.content, section.section_type)
                if result:
                    logger.info(f"     ✅ 章节信息解析成功，提取字段: {list(result.keys())}")
                else:
                    logger.warning(f"     ❌ AI响应解析失败")
                return result
            else:
                logger.warning(f"     ❌ AI对章节《{section.title}》返回空响应")
                return None
        except Exception as e:
            logger.error(f"     💥 AI处理章节《{section.title}》失败: {e}")
            return None
    
    def _generate_section_prompt(self, section: PaperSection) -> str:
        """根据章节类型生成专门的提示词"""
        base_prompt = f"""请分析以下论文章节内容，并提取关键信息。

章节标题: {section.title}
章节类型: {section.section_type}

"""
        
        # 根据章节类型定制提示词
        if section.section_type == 'abstract':
            specific_prompt = """请提取以下信息并以JSON格式返回：
{
  "title_cn": "中文标题",
  "title_en": "英文标题", 
  "abstract_cn": "中文摘要",
  "abstract_en": "英文摘要",
  "keywords_cn": "中文关键词",
  "keywords_en": "英文关键词"
}"""
        
        elif section.section_type == 'literature_review':
            specific_prompt = """请提取以下信息并以JSON格式返回：
{
  "literature_review": "完整的文献综述内容",
  "theoretical_framework": "理论框架和基础理论",
  "research_gap": "识别的研究空白",
  "key_references": "主要参考文献"
}"""
        
        elif section.section_type == 'methodology':
            specific_prompt = """请提取以下信息并以JSON格式返回：
{
  "research_methods": "具体研究方法和技术路径",
  "theoretical_framework": "理论框架",
  "technical_approach": "技术实现方案",
  "tools": "使用的工具和平台"
}"""
        
        elif section.section_type == 'experiment':
            specific_prompt = """请提取以下信息并以JSON格式返回：
{
  "experiment_design": "实验设计方案",
  "experiment_process": "实验过程描述",
  "data_collection": "数据收集方法",
  "validation_method": "验证方法"
}"""
        
        elif section.section_type == 'results':
            specific_prompt = """请提取以下信息并以JSON格式返回：
{
  "research_results": "主要研究结果",
  "data_analysis": "数据分析结果",
  "performance_metrics": "性能指标",
  "key_findings": "关键发现"
}"""
        
        elif section.section_type == 'conclusion':
            specific_prompt = """请提取以下信息并以JSON格式返回：
{
  "research_conclusions": "主要研究结论",
  "main_innovations": "主要创新点",
  "application_value": "应用价值和实际意义",
  "future_work": "未来工作展望",
  "limitations": "研究局限性"
}"""
        
        else:
            specific_prompt = """请提取以下信息并以JSON格式返回：
{
  "section_content": "章节主要内容总结",
  "key_points": "关键要点",
  "important_info": "重要信息"
}"""
        
        full_prompt = base_prompt + specific_prompt + f"\n\n章节内容:\n{section.content[:4000]}"  # 限制长度避免超时
        return full_prompt
    
    def _parse_section_response(self, response_content: str, section_type: str) -> Optional[Dict]:
        """解析AI响应中的结构化信息"""
        try:
            import json
            import re
            
            # 提取JSON内容
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                logger.warning(f"无法从 {section_type} 章节响应中提取JSON")
                return None
        except Exception as e:
            logger.error(f"解析 {section_type} 章节响应失败: {e}")
            return None
    
    def _integrate_section_results(self, section_results: Dict, sections: List[PaperSection]) -> Dict:
        """整合所有章节的提取结果"""
        integrated = {
            # 初始化所有标准字段 - 使用新的命名规范
            'title_cn': '',
            'title_en': '',
            'abstract_cn': '',
            'abstract_en': '',
            'keywords_cn': '',
            'keywords_en': '',
            'literature_review': '',
            'research_methods': '',
            'theoretical_framework': '',
            'main_innovations': '',
            'practical_problems': '',
            'proposed_solutions': '',
            'research_conclusions': '',
            'application_value': '',
            'references': ''
        }
        
        # 整合各章节的信息
        for section_type, section_data in section_results.items():
            if not section_data:
                continue
            
            # 直接映射字段
            for key, value in section_data.items():
                if key in integrated and value:
                    if integrated[key]:
                        integrated[key] += f"\n\n{value}"
                    else:
                        integrated[key] = value
        
        # 特殊处理：如果某些字段为空，尝试从其他字段推断
        if not integrated['practical_problems']:
            # 从引言或结论中推断实践问题
            introduction_sections = [s for s in sections if s.section_type == 'introduction']
            if introduction_sections:
                integrated['practical_problems'] = f"根据引言分析，{introduction_sections[0].content[:500]}..."
        
        if not integrated['proposed_solutions']:
            # 从方法章节中提取解决方案
            if integrated['research_methods']:
                integrated['proposed_solutions'] = integrated['research_methods']
        
        # 生成参考文献列表
        ref_sections = [s for s in sections if s.section_type == 'references']
        if ref_sections:
            integrated['references'] = ref_sections[0].content
        
        return integrated

# 辅助函数：创建章节处理器
def create_section_processor(ai_client):
    """创建论文章节处理器实例"""
    return PaperSectionProcessor(ai_client)
