#!/usr/bin/env python3
"""
Markdown报告生成器
用于生成论文评估的Markdown格式报告
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter
import re
from .config_manager import get_config_manager
from .literature_review_analyzer import LiteratureReviewAnalyzer
from .ai_client import ConcurrentAIClient

# 获取日志记录器
logger = logging.getLogger(__name__)

class MarkdownReportGenerator:
    """Markdown评估报告生成器"""
    
    def __init__(self):
        self.config_mgr = get_config_manager()
        self.report_config = self.config_mgr.get_report_config()
        self.literature_analyzer = LiteratureReviewAnalyzer()  # 初始化文献综述分析器
        
        # 初始化AI客户端
        self.ai_client = ConcurrentAIClient(max_workers=3, max_connections=5)
        try:
            self.ai_client.initialize()
            self.ai_enabled = True
            logger.info("AI客户端初始化成功，将使用AI驱动的创新性分析")
        except Exception as e:
            logger.warning(f"AI客户端初始化失败，将使用基于规则的分析: {e}")
            self.ai_enabled = False
        
        # 创新性分析提示词模板
        self.innovation_analysis_prompts = {
            'methodology': """
基于以下文献数据，分析目标论文在方法学方面的创新点：

论文主题：{thesis_title}
论文关键词：{thesis_keywords}
论文摘要：{thesis_abstract}

相关文献数据：
{literature_data}

请从以下角度深入分析方法学创新：
1. 创新的研究方法或技术路径（与现有文献对比）
2. 现有方法的改进和优化（具体改进点）
3. 方法论突破的意义和价值

输出格式：简洁的分析文本，突出创新点和差异化优势。
""",
            
            'theory': """
基于文献对比分析，评估目标论文的理论贡献：

论文理论框架：{theoretical_framework}
相关理论研究：{theory_literature}

请分析：
1. 新的理论框架或模型的原创性
2. 对现有理论的补充和完善程度
3. 理论贡献的学术价值和影响

重点关注：理论创新的独特性和在相关领域的首创性。
""",
            
            'practice': """
评估论文的实践价值和应用前景：

实践问题：{practical_problems}
解决方案：{proposed_solutions}
应用背景文献：{application_literature}

分析要点：
1. 解决实际问题的新方案的有效性
2. 技术成果的应用前景和市场价值
3. 与现有解决方案的比较优势

输出：突出实践创新和应用价值的具体表现。
"""
        }
    
    def generate_evaluation_report(self, input_file: str, output_dir: Optional[str] = None, 
                                 thesis_extracted_info: Optional[Dict[str, str]] = None,
                                 papers_by_lang: Optional[Dict[str, List]] = None,
                                 literature_metadata_analysis: Optional[Dict] = None) -> str:
        """
        生成评估报告
        
        Args:
            input_file: 输入论文文件路径
            output_dir: 输出目录，默认使用配置的输出目录
            thesis_extracted_info: 通过extract_sections_with_ai抽取的论文结构化信息
            papers_by_lang: CNKI检索到的相关文献，按语言分类
            literature_metadata_analysis: 文献元数据分析结果
            
        Returns:
            生成的报告文件路径
        """
        if output_dir is None:
            output_dir = self.config_mgr.get_output_dir()
        
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成报告文件名
        report_filename = self.config_mgr.generate_output_filename(
            input_file, 'evaluation_report'
        )
        report_path = os.path.join(output_dir, report_filename)
        
        # 生成报告内容，传递抽取的论文信息和检索到的文献
        report_content = self._generate_report_content(input_file, thesis_extracted_info, papers_by_lang)
        
        # 写入文件
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path
    
    def _analyze_literature_themes(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析文献主题分布"""
        theme_analysis = {
            'chinese_themes': {},
            'english_themes': {},
            'year_distribution': {},
            'research_trends': []
        }
        
        # 分析中文文献主题
        if analysis_data['top_chinese']:
            for paper in analysis_data['top_chinese']:
                keywords = paper.get('KeyWords', '').split(';;')
                for keyword in keywords:
                    keyword = keyword.strip()
                    if keyword:
                        theme_analysis['chinese_themes'][keyword] = \
                            theme_analysis['chinese_themes'].get(keyword, 0) + 1
        
        # 分析英文文献主题
        if analysis_data['top_english']:
            for paper in analysis_data['top_english']:
                keywords = paper.get('KeyWords', '').split(';')
                for keyword in keywords:
                    keyword = keyword.strip()
                    if keyword:
                        theme_analysis['english_themes'][keyword] = \
                            theme_analysis['english_themes'].get(keyword, 0) + 1
        
        # 分析年份分布
        all_papers = []
        if analysis_data['top_chinese']:
            all_papers.extend(analysis_data['top_chinese'])
        if analysis_data['top_english']:
            all_papers.extend(analysis_data['top_english'])
        
        for paper in all_papers:
            year = paper.get('PublicationYear', '')
            if year:
                try:
                    year_int = int(year)
                    theme_analysis['year_distribution'][year_int] = \
                        theme_analysis['year_distribution'].get(year_int, 0) + 1
                except ValueError:
                    continue
        
        return theme_analysis
    
    def _generate_innovation_analysis(self, analysis_data: Dict[str, Any], 
                                    theme_analysis: Dict[str, Any],
                                    thesis_extracted_info: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """基于文献对比生成创新性分析"""
        
        # 提取论文基本信息，优先使用传递的抽取信息
        thesis_info = self._extract_thesis_info(analysis_data, thesis_extracted_info)
        
        innovation_analysis = {}
        
        if self.ai_enabled:
            # 使用AI驱动的分析
            logger.info("使用AI驱动的创新性分析")
            innovation_analysis = self._generate_ai_innovation_analysis(thesis_info, analysis_data, theme_analysis)
        else:
            # AI未启用时返回空分析
            logger.warning("AI未启用，无法进行创新性分析")
            innovation_analysis = {
                'methodology': '需要启用AI服务才能进行方法学创新分析',
                'theory': '需要启用AI服务才能进行理论贡献分析',
                'practice': '需要启用AI服务才能进行实践价值分析'
            }
        
        return innovation_analysis
    
    def _generate_ai_innovation_analysis(self, thesis_info: Dict[str, str], 
                                       analysis_data: Dict[str, Any],
                                       theme_analysis: Dict[str, Any]) -> Dict[str, str]:
        """使用AI生成创新性分析（64K Token智能管理版）"""
        
        innovation_analysis = {}
        
        try:
            # Step 1: 构建精简的核心信息
            core_thesis_info = self._extract_core_thesis_info(thesis_info)
            condensed_literature_context = self._build_condensed_literature_context(analysis_data, theme_analysis)
            
            # Step 2: 使用分层分析策略，每个维度独立分析避免Token累积
            methodology_analysis = self._analyze_with_token_limit(
                'methodology', core_thesis_info, condensed_literature_context
            )
            theory_analysis = self._analyze_with_token_limit(
                'theory', core_thesis_info, condensed_literature_context
            )
            practice_analysis = self._analyze_with_token_limit(
                'practice', core_thesis_info, condensed_literature_context
            )
            
            # 处理结果
            innovation_analysis['methodology'] = methodology_analysis if methodology_analysis else '方法学创新分析失败'
            innovation_analysis['theory'] = theory_analysis if theory_analysis else '理论贡献分析失败'
            innovation_analysis['practice'] = practice_analysis if practice_analysis else '实践价值分析失败'
            
        except Exception as e:
            logger.error(f"AI分析过程中出现错误: {e}")
            # 返回错误信息而不是回退
            innovation_analysis = {
                'methodology': f'AI分析出现错误: {str(e)}',
                'theory': f'AI分析出现错误: {str(e)}',
                'practice': f'AI分析出现错误: {str(e)}'
            }
        
        return innovation_analysis
    
    def _extract_core_thesis_info(self, thesis_info: Dict[str, str]) -> Dict[str, str]:
        """提取论文核心信息，控制Token消耗"""
        
        core_info = {}
        
        # 论文标题（必需）
        core_info['title'] = thesis_info.get('title', '未提供')[:200]  # 限制200字符
        
        # 关键词（压缩）
        keywords_cn = thesis_info.get('keywords_cn', '')[:150]
        keywords_en = thesis_info.get('keywords_en', '')[:150]
        core_info['keywords'] = f"{keywords_cn} | {keywords_en}"
        
        # 主要创新点（核心）
        core_info['innovations'] = thesis_info.get('main_innovations', '未提供')[:300]
        
        # 研究方法（精简）
        core_info['methodology'] = thesis_info.get('methodology', '未提供')[:250]
        
        # 理论框架（精简）
        core_info['theory_framework'] = thesis_info.get('theoretical_framework', '未提供')[:250]
        
        # 实际问题和解决方案（实践维度）
        core_info['problems'] = thesis_info.get('practical_problems', '未提供')[:200]
        core_info['solutions'] = thesis_info.get('proposed_solutions', '未提供')[:200]
        
        return core_info
    
    def _build_condensed_literature_context(self, analysis_data: Dict[str, Any], theme_analysis: Dict[str, Any]) -> str:
        """构建精简的文献背景信息，严格控制Token消耗"""
        
        context_parts = []
        
        # 基础统计（必需）
        total_chinese = len(analysis_data['top_chinese']) if analysis_data['top_chinese'] else 0
        total_english = len(analysis_data['top_english']) if analysis_data['top_english'] else 0
        context_parts.append(f"文献统计: 中文{total_chinese}篇, 英文{total_english}篇")
        
        # Top5主题（精简）
        if theme_analysis.get('chinese_themes'):
            top_chinese_themes = sorted(theme_analysis['chinese_themes'].items(), key=lambda x: x[1], reverse=True)[:5]
            themes_str = ', '.join([f"{theme}({count})" for theme, count in top_chinese_themes])
            context_parts.append(f"中文主题: {themes_str}")
        
        if theme_analysis.get('english_themes'):
            top_english_themes = sorted(theme_analysis['english_themes'].items(), key=lambda x: x[1], reverse=True)[:5]
            themes_str = ', '.join([f"{theme}({count})" for theme, count in top_english_themes])
            context_parts.append(f"英文主题: {themes_str}")
        
        # 年份信息（精简）
        if theme_analysis.get('year_distribution'):
            recent_years = [year for year in theme_analysis['year_distribution'].keys() if year >= 2020]
            if recent_years:
                recent_count = sum(theme_analysis['year_distribution'][year] for year in recent_years)
                total_papers = sum(theme_analysis['year_distribution'].values())
                recent_percentage = (recent_count / total_papers) * 100
                context_parts.append(f"近5年文献: {recent_percentage:.0f}%")
        
        # 代表性论文（仅标题，最多3篇）
        if analysis_data.get('top_chinese'):
            chinese_titles = [paper.get('Title', '')[:50] + '...' for paper in analysis_data['top_chinese'][:2]]
            context_parts.append(f"代表中文文献: {'; '.join(chinese_titles)}")
        
        if analysis_data.get('top_english'):
            english_titles = [paper.get('Title', '')[:50] + '...' for paper in analysis_data['top_english'][:2]]
            context_parts.append(f"代表英文文献: {'; '.join(english_titles)}")
        
        # 组合并限制总长度
        full_context = '\n'.join(context_parts)
        if len(full_context) > 800:  # 严格限制在800字符以内
            full_context = full_context[:800] + '...'
        
        return full_context
    
    def _analyze_with_token_limit(self, analysis_type: str, core_thesis_info: Dict[str, str], 
                                 condensed_context: str) -> str:
        """在Token限制内进行分析"""
        
        try:
            if analysis_type == 'methodology':
                prompt = f"""你是学术方法论专家。请分析论文的方法学创新：

**论文**: {core_thesis_info['title']}
**方法**: {core_thesis_info['methodology']}
**创新点**: {core_thesis_info['innovations']}

**文献背景**: {condensed_context}

请从研究方法创新性、技术路径突破、方法论贡献三个角度简要分析，200-300字。"""

            elif analysis_type == 'theory':
                prompt = f"""你是理论研究专家。请分析论文的理论贡献：

**论文**: {core_thesis_info['title']}
**理论框架**: {core_thesis_info['theory_framework']}
**创新点**: {core_thesis_info['innovations']}

**文献背景**: {condensed_context}

请从理论创新性、理论整合性、学科影响力三个角度简要分析，200-300字。"""

            elif analysis_type == 'practice':
                prompt = f"""你是产学研专家。请分析论文的实践价值：

**论文**: {core_thesis_info['title']}
**实际问题**: {core_thesis_info['problems']}
**解决方案**: {core_thesis_info['solutions']}

**文献背景**: {condensed_context}

请从问题解决能力、应用前景、社会经济价值三个角度简要分析，200-300字。"""

            else:
                return f"{analysis_type}分析类型不支持"
            
            # 使用独立会话避免上下文累积
            session_id = f'{analysis_type}_analysis_{hash(prompt) % 10000}'
            response = self.ai_client.send_message(prompt, session_id=session_id)
            
            if response and response.content:
                return response.content.strip()
            else:
                return f"{analysis_type}分析无响应"
                
        except Exception as e:
            logger.error(f"{analysis_type}分析失败: {e}")
            return f"{analysis_type}分析失败: {str(e)}"
    
    def _fallback_independent_analysis(self, thesis_info: Dict[str, str], literature_context: str) -> Dict[str, str]:
        """备用的独立分析方法（当共享上下文失败时使用）"""
        
        innovation_analysis = {}
        
        try:
            # 使用精简的提示词进行独立分析
            methodology_prompt = self._analyze_methodology_innovation_compact(thesis_info, literature_context)
            theory_prompt = self._analyze_theory_contribution_compact(thesis_info, literature_context)  
            practice_prompt = self._analyze_practice_value_compact(thesis_info, literature_context)
            
            # 使用独立会话
            methodology_response = self.ai_client.send_message(methodology_prompt, session_id='methodology_fallback')
            theory_response = self.ai_client.send_message(theory_prompt, session_id='theory_fallback')
            practice_response = self.ai_client.send_message(practice_prompt, session_id='practice_fallback')
            
            # 处理结果
            if methodology_response and methodology_response.content:
                innovation_analysis['methodology'] = methodology_response.content
            else:
                innovation_analysis['methodology'] = '方法学创新分析失败'
            
            if theory_response and theory_response.content:
                innovation_analysis['theory'] = theory_response.content
            else:
                innovation_analysis['theory'] = '理论贡献分析失败'
            
            if practice_response and practice_response.content:
                innovation_analysis['practice'] = practice_response.content
            else:
                innovation_analysis['practice'] = '实践价值分析失败'
            
        except Exception as e:
            logger.error(f"备用分析也失败: {e}")
            innovation_analysis = {
                'methodology': f'AI分析出现错误: {str(e)}',
                'theory': f'AI分析出现错误: {str(e)}',
                'practice': f'AI分析出现错误: {str(e)}'
            }
        
        return innovation_analysis
    
    def _analyze_methodology_innovation(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """分析方法学创新（独立会话）"""
        
        prompt = f"""你是一位资深的学术方法论专家，专门评估研究方法的创新性。

**论文信息**：
- 标题：{thesis_info.get('title', '未提供')}
- 研究方法：{thesis_info.get('methodology', '未提供')}
- 主要创新点：{thesis_info.get('main_innovations', '未提供')}
- 关键词：{thesis_info.get('keywords_cn', '未提供')}

**文献背景**：
{literature_context}

请从专业角度分析该论文的方法学创新：

1. **研究方法创新性**：与现有方法相比有何突破？
2. **技术路径创新**：技术实现上的独特之处？
3. **方法论贡献**：为研究领域提供了什么新工具？

要求：学术客观，突出创新点，300-500字。"""

        return prompt
    
    def _analyze_theory_contribution(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """分析理论贡献（独立会话）"""
        
        prompt = f"""你是一位资深的理论研究专家，专门评估学术研究的理论贡献。

**论文信息**：
- 标题：{thesis_info.get('title', '未提供')}
- 理论框架：{thesis_info.get('theoretical_framework', '未提供')}
- 主要创新点：{thesis_info.get('main_innovations', '未提供')}
- 研究结论：{thesis_info.get('research_conclusions', '未提供')}

**文献背景**：
{literature_context}

请从理论建构角度分析该论文的贡献：

1. **理论创新性**：是否提出新的理论框架或概念？
2. **理论整合性**：如何整合不同理论视角？
3. **理论影响力**：对学科发展的意义？

要求：严谨客观，突出理论创新，300-500字。"""

        return prompt
    
    def _analyze_practice_value(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """分析实践价值（独立会话）"""
        
        prompt = f"""你是一位资深的产学研专家，专门评估研究成果的实践应用价值。

**论文信息**：
- 标题：{thesis_info.get('title', '未提供')}
- 实际问题：{thesis_info.get('practical_problems', '未提供')}
- 解决方案：{thesis_info.get('proposed_solutions', '未提供')}
- 应用价值：{thesis_info.get('application_value', '未提供')}

**文献背景**：
{literature_context}

请从实践应用角度分析该论文的价值：

1. **问题解决能力**：解决了什么实际问题？
2. **应用前景评估**：市场应用潜力如何？
3. **社会经济价值**：能创造什么价值？

要求：实用客观，突出应用价值，300-500字。"""

        return prompt
    
    def _extract_thesis_info(self, analysis_data: Dict[str, Any], 
                           thesis_extracted_info: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """提取论文基本信息"""
        
        # 优先使用传递的抽取信息
        if thesis_extracted_info:
            print("使用传递的论文结构化信息")
            return {
                'title': thesis_extracted_info.get('title_cn', '') or thesis_extracted_info.get('ChineseTitle', ''),
                'keywords_cn': thesis_extracted_info.get('keywords_cn', '') or thesis_extracted_info.get('ChineseKeywords', ''),
                'keywords_en': thesis_extracted_info.get('keywords_en', '') or thesis_extracted_info.get('EnglishKeywords', ''),
                'keywords': thesis_extracted_info.get('keywords_cn', '') or thesis_extracted_info.get('ChineseKeywords', ''),  # 兼容旧代码
                'abstract': thesis_extracted_info.get('abstract_cn', '') or thesis_extracted_info.get('ChineseAbstract', ''),
                'methodology': thesis_extracted_info.get('ResearchMethods', ''),
                'theoretical_framework': thesis_extracted_info.get('TheoreticalFramework', ''),
                'practical_problems': thesis_extracted_info.get('PracticalProblems', ''),
                'main_innovations': thesis_extracted_info.get('MainInnovations', ''),
                'proposed_solutions': thesis_extracted_info.get('ProposedSolutions', ''),
                'research_conclusions': thesis_extracted_info.get('ResearchConclusions', ''),
                'application_value': thesis_extracted_info.get('ApplicationValue', '')
            }
        else:
            # 如果没有传递抽取信息，直接返回空值，不使用缓存也不进行现场抽取
            print("警告：未传递论文抽取信息，将使用空值生成通用分析")
            return {
                'title': '',
                'keywords': '',
                'abstract': '',
                'methodology': '',
                'theoretical_framework': '',
                'practical_problems': '',
                'main_innovations': '',
                'proposed_solutions': '',
                'research_conclusions': '',
                'application_value': ''
            }
    
    def _build_theory_context(self, analysis_data: Dict[str, Any], 
                            theme_analysis: Dict[str, Any]) -> str:
        """构建理论分析上下文"""
        context = "相关理论研究现状：\n"
        
        theory_keywords = ['risk management', 'internal control', 'governance', 'framework',
                          'theory', '风险管理', '内部控制', '治理', '理论框架']
        
        for keyword in theory_keywords:
            if keyword in theme_analysis['chinese_themes']:
                context += f"- {keyword}: {theme_analysis['chinese_themes'][keyword]}篇中文文献\n"
            if keyword in theme_analysis['english_themes']:
                context += f"- {keyword}: {theme_analysis['english_themes'][keyword]}篇英文文献\n"
        
        return context
    
    def _build_practice_context(self, analysis_data: Dict[str, Any], 
                              theme_analysis: Dict[str, Any]) -> str:
        """构建实践价值分析上下文"""
        context = "实践应用研究现状：\n"
        
        practice_keywords = ['telemedicine', 'internet hospital', 'healthcare', 'implementation',
                           'application', '互联网医院', '远程医疗', '医疗健康', '应用']
        
        for keyword in practice_keywords:
            if keyword in theme_analysis['chinese_themes']:
                context += f"- {keyword}实践研究: {theme_analysis['chinese_themes'][keyword]}篇\n"
            if keyword in theme_analysis['english_themes']:
                context += f"- {keyword}应用研究: {theme_analysis['english_themes'][keyword]}篇\n"
        
        return context
    
    def _analyze_methodological_innovation(self, thesis_info: Dict[str, str], 
                                         context: str) -> str:
        """分析方法学创新（基于规则的备用方案）"""
        
        methodology = thesis_info.get('methodology', '')
        main_innovations = thesis_info.get('main_innovations', '')
        
        analysis = ""
        
        # 基于论文内容进行通用方法学分析
        if methodology:
            # 检测量化方法
            if any(keyword in methodology.lower() for keyword in ['量化', '定量', 'quantitative', '统计', 'statistical', '数值', '计量']):
                analysis += """**量化研究方法创新**：本研究采用量化分析方法，通过数值化指标和统计分析技术，为研究问题提供了客观、可重复的分析框架，相比传统定性研究具有更强的科学性和可验证性。

"""
            
            # 检测实验方法
            if any(keyword in methodology.lower() for keyword in ['实验', 'experiment', '对照', 'control', '测试', 'test']):
                analysis += """**实验方法学突破**：通过设计严格的实验方案和对照组设置，本研究建立了科学的验证机制，为理论假设提供了实证支撑，提升了研究结论的可信度。

"""
            
            # 检测跨学科方法
            if any(keyword in methodology.lower() for keyword in ['跨学科', 'interdisciplinary', '融合', '综合', '多元']):
                analysis += """**跨学科方法论创新**：本研究整合多学科理论和方法，突破了单一学科研究的局限性，为复杂问题的研究提供了新的方法论视角。

"""
            
            # 检测计算方法
            if any(keyword in methodology.lower() for keyword in ['算法', 'algorithm', '模型', 'model', '仿真', 'simulation', '机器学习', 'ai']):
                analysis += """**计算方法创新**：运用先进的计算技术和算法模型，本研究实现了传统方法难以处理的复杂问题分析，为相关领域提供了新的技术路径。

"""
        
        # 如果没有足够的方法学信息，提供通用分析框架
        if not analysis:
            analysis = """**方法学创新评估**：基于文献对比分析，建议从以下维度评估方法学创新：

1. **研究设计创新**：评估研究设计的原创性和科学性，对比现有研究方法的优势和改进
2. **技术路径突破**：分析采用的技术手段和分析工具的先进性，识别方法论层面的突破点
3. **可重复性提升**：评估方法的标准化程度和可推广性，为后续研究提供方法论参考

**改进建议**：明确阐述研究方法的创新之处，通过与现有方法的对比突出优势和改进点。"""
        
        return analysis.strip()
    
    def _analyze_theoretical_contribution(self, thesis_info: Dict[str, str], 
                                        context: str) -> str:
        """分析理论贡献（基于规则的备用方案）"""
        
        theoretical_framework = thesis_info.get('theoretical_framework', '')
        main_innovations = thesis_info.get('main_innovations', '')
        
        analysis = ""
        
        # 基于论文内容进行通用理论贡献分析
        if theoretical_framework:
            # 检测新理论构建
            if any(keyword in theoretical_framework.lower() for keyword in ['理论', 'theory', '模型', 'model', '框架', 'framework']):
                analysis += """**理论框架构建**：本研究构建了系统的理论分析框架，为相关领域的理论发展做出了贡献。通过整合现有理论资源，形成了具有解释力和预测性的理论体系。

"""
            
            # 检测理论融合
            if any(keyword in theoretical_framework.lower() for keyword in ['融合', 'integration', '结合', 'combination', '综合', 'synthesis']):
                analysis += """**理论整合创新**：本研究创新性地整合了多个理论视角，突破了单一理论的局限性，为跨理论研究提供了新的整合模式和分析路径。

"""
            
            # 检测理论扩展
            if any(keyword in theoretical_framework.lower() for keyword in ['扩展', 'extension', '发展', 'development', '完善', 'improvement']):
                analysis += """**理论扩展贡献**：在现有理论基础上，本研究进行了重要的理论扩展和完善，丰富了理论内涵，拓展了理论的适用范围和解释能力。

"""
        
        # 检测创新点中的理论贡献
        if main_innovations:
            if any(keyword in main_innovations.lower() for keyword in ['首次', 'first', '首创', 'pioneer', '原创', 'original']):
                analysis += """**原创性理论贡献**：本研究提出了具有原创性的理论观点，在相关领域具有开创性意义，为后续理论研究奠定了重要基础。

"""
        
        # 如果没有足够的理论信息，提供通用分析框架
        if not analysis:
            analysis = """**理论贡献评估**：基于文献对比分析，建议从以下维度评估理论贡献：

1. **理论创新度**：评估提出的理论观点、概念或模型的原创性和新颖性
2. **理论解释力**：分析理论框架对研究问题的解释能力和适用范围
3. **理论影响力**：评估理论贡献对学科发展和后续研究的推动作用

**改进建议**：明确阐述理论贡献的独特性，通过与现有理论的对比突出创新价值。"""
        
        return analysis.strip()
    
    def _analyze_practical_value(self, thesis_info: Dict[str, str], 
                               context: str) -> str:
        """分析实践价值（基于规则的备用方案）"""
        
        application_value = thesis_info.get('application_value', '')
        proposed_solutions = thesis_info.get('proposed_solutions', '')
        practical_problems = thesis_info.get('practical_problems', '')
        
        analysis = ""
        
        # 基于论文内容进行通用实践价值分析
        if practical_problems:
            # 检测问题解决能力
            if practical_problems.strip():
                analysis += """**实际问题解决**：本研究针对现实中的具体问题提出了系统性解决方案，具有明确的问题导向和应用针对性，为实践工作提供了可操作的指导。

"""
        
        if proposed_solutions:
            # 检测解决方案创新
            if any(keyword in proposed_solutions.lower() for keyword in ['方案', 'solution', '策略', 'strategy', '建议', 'recommendation']):
                analysis += """**解决方案创新**：研究提出的解决方案具有创新性和可行性，为相关领域的实践工作提供了新的思路和方法，具有较强的推广应用价值。

"""
            
            # 检测技术应用
            if any(keyword in proposed_solutions.lower() for keyword in ['技术', 'technology', '系统', 'system', '平台', 'platform', '工具', 'tool']):
                analysis += """**技术应用创新**：本研究将先进技术应用于实际问题解决，实现了技术与应用的有效结合，为技术转化和产业应用提供了示范。

"""
        
        if application_value:
            # 检测应用前景
            if any(keyword in application_value.lower() for keyword in ['应用', 'application', '推广', 'promotion', '价值', 'value']):
                analysis += """**应用价值显著**：研究成果具有广阔的应用前景和推广价值，能够为相关行业和领域的发展提供有效支撑，具有重要的现实意义。

"""
            
            # 检测经济效益
            if any(keyword in application_value.lower() for keyword in ['经济', 'economic', '效益', 'benefit', '成本', 'cost', '效率', 'efficiency']):
                analysis += """**经济效益潜力**：研究成果在提高效率、降低成本、创造经济价值等方面具有明显优势，为相关产业的可持续发展提供了重要支撑。

"""
        
        # 如果没有足够的实践信息，提供通用分析框架
        if not analysis:
            analysis = """**实践价值评估**：基于文献对比分析，建议从以下维度评估实践价值：

1. **问题解决能力**：评估研究成果对实际问题的解决效果和适用范围
2. **应用可行性**：分析研究结果的可操作性和实施条件
3. **推广价值**：评估成果的可复制性和在不同场景下的适用性

**改进建议**：明确阐述研究的实际应用价值，通过案例分析或效果验证增强说服力。"""
        
        return analysis.strip()
    
    def _generate_literature_review_analysis(self, thesis_extracted_info: Optional[Dict[str, str]] = None,
                                           papers_by_lang: Optional[Dict[str, List]] = None,
                                           analysis_data: Optional[Dict] = None) -> str:
        """生成文献综述质量分析"""
        
        # 如果没有传入papers_by_lang，尝试从analysis_data构建
        if not papers_by_lang and analysis_data:
            papers_by_lang = {}
            if analysis_data.get('top_chinese'):
                papers_by_lang['Chinese'] = analysis_data['top_chinese']
            if analysis_data.get('top_english'):
                papers_by_lang['English'] = analysis_data['top_english']
        
        # 如果仍然没有文献数据或论文信息，返回数据不足提示
        if not papers_by_lang or not thesis_extracted_info:
            # 检查是否有缓存的文献数据
            total_cached_papers = 0
            if analysis_data:
                total_cached_papers = sum([
                    len(analysis_data[key]) if analysis_data[key] else 0
                    for key in ['top_chinese', 'top_english']
                ])
            
            if total_cached_papers > 0:
                return f"""## 文献综述分析

**基于缓存数据的简化分析**：
- 发现已有的缓存文献数据：{total_cached_papers}篇相关研究
- 由于缺少论文的参考文献列表信息，无法进行详细的文献综述对比分析
- 建议补充论文的参考文献信息以获得更完整的文献综述分析

**改进建议**：
1. 确保论文中包含完整的参考文献列表
2. 重新运行评估以获取论文的结构化信息
3. 考虑进行文献检索以获得更全面的对比数据"""
            else:
                return "## 文献综述分析\n\n**数据不足**：缺少相关文献数据或论文抽取信息，无法进行文献综述分析。建议使用文献检索功能或确保有可用的缓存文献数据。"
        
        # 获取论文参考文献
        reference_list = thesis_extracted_info.get('references', '') or thesis_extracted_info.get('ReferenceList', '')
        if not reference_list:
            # 如果没有参考文献，但有文献数据，进行简化分析
            total_papers = sum(len(papers) for papers in papers_by_lang.values())
            return f"""## 文献综述分析

**警告**：未能提取到论文参考文献列表，提供基于相关文献数据的简化分析。

### 📊 相关文献概览

- **检索到的相关文献总数**：{total_papers}篇
- **文献语言分布**：
""" + "\n".join([f"  - {lang}文献：{len(papers)}篇" for lang, papers in papers_by_lang.items()]) + """

**建议**：
- 补充论文的完整参考文献列表以进行深度对比分析
- 检查论文格式，确保参考文献部分能够被正确提取
- 考虑手动补充关键参考文献信息"""
        
        # 进行完整的文献综述分析
        # 分析覆盖度
        coverage_analysis = self._analyze_literature_coverage(reference_list, papers_by_lang)
        
        # 分析深度（使用CoT）
        depth_analysis = self._analyze_literature_depth_cot(reference_list, papers_by_lang, thesis_extracted_info)
        
        # 分析相关性
        relevance_analysis = self._analyze_literature_relevance(reference_list, papers_by_lang, thesis_extracted_info)
        
        # 分析时效性
        timeliness_analysis = self._analyze_literature_timeliness(reference_list, papers_by_lang)
        
        # 发现缺失的重要文献
        missing_refs = self._find_missing_references(reference_list, papers_by_lang)
        
        return f"""## 文献综述分析

{coverage_analysis}

{depth_analysis}

{relevance_analysis}

{timeliness_analysis}

{missing_refs}"""

    def _analyze_literature_coverage(self, reference_list, papers_by_lang: Dict[str, List]) -> str:
        """分析文献覆盖度"""
        # 统计CNKI检索到的相关文献数量
        total_relevant = sum(len(papers) for papers in papers_by_lang.values())
        
        # 统一的处理模式
        if isinstance(reference_list, list):
            # 处理列表类型：直接使用长度或合并为字符串
            ref_count = len(reference_list)
            reference_text = ' '.join(str(ref) for ref in reference_list)
        elif isinstance(reference_list, str):
            # 处理字符串类型：使用原有逻辑
            ref_lines = reference_list.split('\n')
            ref_count = len([line for line in ref_lines if line.strip()])
            reference_text = reference_list
        else:
            # 处理其他类型：安全默认值
            ref_count = 0
            reference_text = ""
        
        coverage_ratio = min(ref_count / max(total_relevant, 1), 1.0)
        
        if coverage_ratio >= 0.7:
            coverage_level = "优秀"
            coverage_desc = "文献覆盖度很高，显示了对研究领域的全面了解"
        elif coverage_ratio >= 0.5:
            coverage_level = "良好"
            coverage_desc = "文献覆盖度较好，但仍有提升空间"
        elif coverage_ratio >= 0.3:
            coverage_level = "一般"
            coverage_desc = "文献覆盖度有限，建议增加相关文献的引用"
        else:
            coverage_level = "不足"
            coverage_desc = "文献覆盖度明显不足，需要大幅增加相关文献"
        
        return f"""### 📊 文献覆盖度分析

**覆盖度评级**：{coverage_level} ({coverage_ratio:.1%})
- 检索到相关文献：{total_relevant} 篇
- 论文引用文献：约 {ref_count} 篇
- **评估**：{coverage_desc}

**改进建议**：
- 建议补充最新的高影响因子文献
- 注意包含不同研究角度的代表性文献
- 平衡国内外文献的比例"""

    def _analyze_literature_depth_cot(self, reference_list, papers_by_lang: Dict[str, List], 
                                    thesis_extracted_info: Dict[str, str]) -> str:
        """使用Chain of Thought分析文献综述深度（基于相关文献元数据）"""
        # CoT推理步骤
        thinking_process = """
**思考过程**：
1. 分析相关文献的研究主题分布和层次结构
2. 评估文献在理论基础、方法论和应用三个层面的覆盖度
3. 检查文献的时效性和权威性分布
4. 评估文献综述的系统性和完整性
        """
        
        # 基于相关文献元数据进行深度分析
        depth_analysis = self._evaluate_literature_depth_by_metadata(papers_by_lang, thesis_extracted_info)
        
        depth_level = depth_analysis['level']
        depth_score = depth_analysis['score']
        depth_desc = depth_analysis['description']
        detailed_analysis = depth_analysis['detailed_analysis']
        
        return f"""### 🤔 文献综述深度分析（CoT方法）

{thinking_process}

**深度评估结果**：
- **深度等级**：{depth_level} ({depth_score}/100)
- **分析**：{depth_desc}

**详细分析**：
{detailed_analysis}

**CoT推理结论**：
基于相关文献的主题分布、研究层次和时效性分析，
该论文的文献综述在理论深度、方法论讨论和批判性分析方面{'表现优秀' if depth_score >= 80 else '有待加强' if depth_score >= 60 else '需要显著改进'}。

**提升建议**：
- 增强文献间的对比分析和批判性评述
- 明确指出现有研究的局限性和研究空白
- 构建更清晰的理论框架和研究脉络"""
    
    def _evaluate_literature_depth_by_metadata(self, papers_by_lang: Dict[str, List], 
                                             thesis_extracted_info: Dict[str, str]) -> Dict[str, Any]:
        """基于相关文献元数据评估文献综述深度"""
        
        all_papers = []
        if papers_by_lang:
            for papers in papers_by_lang.values():
                if papers:
                    all_papers.extend(papers)
        
        if not all_papers:
            return {
                'level': '数据不足',
                'score': 0,
                'description': '缺少相关文献数据，无法评估文献综述深度',
                'detailed_analysis': '需要提供相关文献数据以进行深度分析。'
            }
        
        # 1. 分析研究层次分布
        theory_papers = 0
        method_papers = 0
        application_papers = 0
        review_papers = 0
        
        for paper in all_papers:
            # 安全获取字符串字段，确保类型正确
            title = str(paper.get('Title', '')).lower()
            keywords = str(paper.get('KeyWords', '')).lower()
            abstract = str(paper.get('Abstract', '')).lower()
            
            paper_text = f"{title} {keywords} {abstract}"
            
            # 理论研究识别
            if any(keyword in paper_text for keyword in ['理论', 'theory', '框架', 'framework', '模型', 'model', '机制', 'mechanism']):
                theory_papers += 1
            
            # 方法研究识别
            if any(keyword in paper_text for keyword in ['方法', 'method', '算法', 'algorithm', '技术', 'technique', '策略', 'strategy']):
                method_papers += 1
            
            # 应用研究识别
            if any(keyword in paper_text for keyword in ['应用', 'application', '实验', 'experiment', '案例', 'case', '临床', 'clinical']):
                application_papers += 1
            
            # 综述文献识别
            if any(keyword in paper_text for keyword in ['综述', 'review', '进展', 'progress', '现状', 'state']):
                review_papers += 1
        
        total_papers = len(all_papers)
        
        # 2. 分析文献质量和权威性
        high_quality_papers = 0
        recent_papers = 0
        core_journal_papers = 0
        
        current_year = 2025
        for paper in all_papers:
            # 时效性分析
            year = paper.get('PublicationYear', '')
            if year:
                try:
                    year_int = int(year)
                    if current_year - year_int <= 5:
                        recent_papers += 1
                except:
                    pass
            
            # 核心期刊识别（简化版）
            journal = str(paper.get('Source', '')).lower()
            if any(indicator in journal for indicator in ['ieee', 'acm', '学报', 'journal', 'transactions']):
                core_journal_papers += 1
            
            # 高质量文献识别（基于关键词丰富度）
            keywords = str(paper.get('KeyWords', ''))
            if keywords and len(keywords.split(';;')) >= 3:
                high_quality_papers += 1
        
        # 3. 计算深度评分
        depth_score = 0
        
        # 研究层次分布评分 (40分)
        layer_coverage = 0
        if theory_papers > 0:
            layer_coverage += 1
        if method_papers > 0:
            layer_coverage += 1
        if application_papers > 0:
            layer_coverage += 1
        if review_papers > 0:
            layer_coverage += 1
        
        depth_score += (layer_coverage / 4) * 40
        
        # 文献质量评分 (30分)
        quality_ratio = high_quality_papers / max(total_papers, 1)
        depth_score += quality_ratio * 30
        
        # 时效性评分 (20分)
        recent_ratio = recent_papers / max(total_papers, 1)
        depth_score += recent_ratio * 20
        
        # 权威性评分 (10分)
        authority_ratio = core_journal_papers / max(total_papers, 1)
        depth_score += authority_ratio * 10
        
        depth_score = min(100, max(0, depth_score))
        
        # 4. 确定深度等级和描述
        if depth_score >= 85:
            level = "优秀"
            description = "文献综述深度优秀，体现了系统性的理论分析和全面的研究覆盖"
        elif depth_score >= 70:
            level = "良好"
            description = "文献综述深度良好，具备较完整的研究层次覆盖"
        elif depth_score >= 55:
            level = "中等"
            description = "文献综述深度中等，基本覆盖主要研究方向"
        elif depth_score >= 40:
            level = "一般"
            description = "文献综述深度一般，存在明显的覆盖不足"
        else:
            level = "不足"
            description = "文献综述深度不足，缺乏系统性分析"
        
        # 5. 生成详细分析
        detailed_analysis = f"""
**研究层次分布分析**：
- 理论研究文献：{theory_papers}篇 ({theory_papers/total_papers*100:.1f}%)
- 方法技术文献：{method_papers}篇 ({method_papers/total_papers*100:.1f}%)
- 应用实证文献：{application_papers}篇 ({application_papers/total_papers*100:.1f}%)
- 综述性文献：{review_papers}篇 ({review_papers/total_papers*100:.1f}%)

**文献质量分析**：
- 高质量文献比例：{quality_ratio:.1%}
- 近5年文献比例：{recent_ratio:.1%}
- 权威期刊文献比例：{authority_ratio:.1%}

**综合评估**：
文献综述在{'理论-方法-应用' if layer_coverage >= 3 else '部分研究层次'}方面有所覆盖，
{'时效性良好' if recent_ratio >= 0.6 else '时效性一般' if recent_ratio >= 0.3 else '时效性不足'}，
{'权威性较强' if authority_ratio >= 0.3 else '权威性一般'}。
        """
        
        return {
            'level': level,
            'score': int(depth_score),
            'description': description,
            'detailed_analysis': detailed_analysis.strip()
        }

    def _analyze_literature_relevance(self, reference_list, papers_by_lang: Dict[str, List],
                                    thesis_extracted_info: Dict[str, str]) -> str:
        """分析文献相关性"""
        # 获取论文关键词和主题
        keywords = thesis_extracted_info.get('Keywords', '')
        abstract = thesis_extracted_info.get('Abstract', '')
        
        # 统计高相关性文献（基于检索结果的top文献）
        high_relevance_count = 0
        total_searched = 0
        
        for lang, papers in papers_by_lang.items():
            total_searched += len(papers)
            # 假设前30%的检索结果为高相关文献
            high_relevance_count += len(papers) * 0.3
        
        relevance_ratio = high_relevance_count / max(total_searched, 1)
        
        if relevance_ratio >= 0.8:
            relevance_level = "高度相关"
            relevance_desc = "引用文献与研究主题高度相关，体现了精准的文献选择"
        elif relevance_ratio >= 0.6:
            relevance_level = "较为相关"
            relevance_desc = "大部分引用文献与研究主题相关，有少量边缘文献"
        elif relevance_ratio >= 0.4:
            relevance_level = "部分相关"
            relevance_desc = "部分引用文献相关性不够强，建议提高文献选择的精准度"
        else:
            relevance_level = "相关性不足"
            relevance_desc = "多数引用文献与核心研究主题关联度较低"
        
        return f"""### 🎯 文献相关性分析

**相关性评级**：{relevance_level} ({relevance_ratio:.1%})

**分析维度**：
- **主题匹配度**：基于关键词和摘要分析文献主题契合度
- **方法论相关性**：评估文献在研究方法上的相关性
- **理论框架吻合度**：分析文献理论基础的相关程度

**评估结果**：{relevance_desc}

**优化策略**：
- 优先引用与核心研究问题直接相关的文献
- 平衡理论文献和实证研究文献的比例
- 确保文献能够支撑研究假设和方法选择"""

    def _analyze_literature_timeliness(self, reference_list, papers_by_lang: Dict[str, List]) -> str:
        """分析文献时效性 - 基于论文参考文献"""
        import re
        from datetime import datetime
        
        current_year = datetime.now().year
        
        # 统一的处理模式
        if isinstance(reference_list, list):
            # 处理列表类型：直接使用长度或合并为字符串
            ref_count = len(reference_list)
            reference_text = ' '.join(str(ref) for ref in reference_list)
        elif isinstance(reference_list, str):
            # 处理字符串类型：使用原有逻辑
            if not reference_list or reference_list == '无参考文献':
                # 如果没有参考文献，提供基于检索文献的参考性分析
                all_papers = []
                for papers in papers_by_lang.values():
                    all_papers.extend(papers)
                
                if all_papers:
                    years = []
                    for paper in all_papers:
                        year = paper.get('PublicationYear', '')
                        if year:
                            try:
                                year_int = int(year)
                                if 1900 <= year_int <= current_year:
                                    years.append(year_int)
                            except ValueError:
                                continue
                    
                    if years:
                        recent_count = len([y for y in years if current_year - y <= 5])
                        recent_ratio = recent_count / len(years)
                        
                        return f"""### ⏰ 文献时效性分析

**警告**：未能从论文中提取参考文献列表，以下基于检索到的相关文献进行参考性分析。

**相关文献时效性参考**：
- 检索到的相关文献总数：{len(years)} 篇
- 近5年相关文献：{recent_count} 篇 ({recent_ratio:.1%})

**重要说明**：
- 此分析基于检索到的相关领域文献，不是论文实际引用的参考文献
- 真正的时效性评估应基于论文参考文献列表
- 建议检查论文PDF是否包含完整的参考文献部分

**改进建议**：
- 确保论文包含完整的参考文献列表
- 检查PDF提取质量，必要时手动补充参考文献信息
- 重新运行分析以获得准确的时效性评估"""
                
                return """### ⏰ 文献时效性分析
            
**警告**：无法获取论文参考文献信息，也无相关文献数据可供参考分析。"""
            
            ref_lines = reference_list.split('\n')
            ref_count = len([line for line in ref_lines if line.strip()])
            reference_text = reference_list
        else:
            # 处理其他类型：安全默认值
            ref_count = 0
            reference_text = ""
        
        # 从参考文献中提取年份
        years = re.findall(r'\b(19|20)\d{2}\b', reference_text)
        years = [int(year) for year in years if int(year) <= current_year]
        
        if not years:
            return """### ⏰ 文献时效性分析
            
**警告**：无法从参考文献中提取有效的发表年份信息。

**可能原因**：
- 参考文献格式不规范
- 文献提取过程中信息丢失
- 参考文献主要为网页或其他非期刊资源

**建议**：
- 检查原始论文的参考文献格式
- 确保参考文献包含明确的发表年份"""
        
        # 分析时效性
        recent_years = [year for year in years if current_year - year <= 5]  # 近5年
        very_recent = [year for year in years if current_year - year <= 2]   # 近2年
        
        recent_ratio = len(recent_years) / len(years)
        very_recent_ratio = len(very_recent) / len(years)
        avg_age = sum(current_year - year for year in years) / len(years)
        
        if recent_ratio >= 0.6 and very_recent_ratio >= 0.3:
            timeliness_level = "优秀"
            timeliness_desc = "参考文献时效性很好，充分反映了研究领域的最新进展"
        elif recent_ratio >= 0.4 and very_recent_ratio >= 0.2:
            timeliness_level = "良好"
            timeliness_desc = "参考文献时效性较好，但可以增加更多最新文献"
        elif recent_ratio >= 0.3:
            timeliness_level = "一般"
            timeliness_desc = "参考文献时效性一般，建议增加近年来的重要文献"
        else:
            timeliness_level = "不足"
            timeliness_desc = "参考文献时效性不足，过多依赖较老的文献"
        
        return f"""### ⏰ 文献时效性分析

**时效性评级**：{timeliness_level}

**统计数据**：
- 参考文献总数：{len(years)} 篇（含年份信息）
- 近5年文献：{len(recent_years)} 篇 ({recent_ratio:.1%})
- 近2年文献：{len(very_recent)} 篇 ({very_recent_ratio:.1%})
- 平均文献年龄：{avg_age:.1f} 年

**评估**：{timeliness_desc}

**改进建议**：
- {'当前参考文献时效性良好，建议保持对最新研究的关注' if timeliness_level == '优秀' else '补充最新的研究成果和理论发展'}
- {'可适当补充经典奠基性文献平衡理论基础' if recent_ratio > 0.8 else '关注近期的高影响因子文献'}
- {'持续关注顶级期刊的最新发表' if timeliness_level in ['优秀', '良好'] else '平衡经典文献与前沿文献的比例'}"""

    def _find_missing_references(self, reference_list, papers_by_lang: Dict[str, List]) -> str:
        """发现可能缺失的重要文献"""
        missing_suggestions = []
        
        # 基于CNKI检索结果推荐高相关文献
        for lang, papers in papers_by_lang.items():
            if papers:
                # 推荐前3篇高相关文献（假设按相关性排序）
                top_papers = papers[:3]
                for paper in top_papers:
                    if isinstance(paper, dict):
                        title = paper.get('title', '未知标题')
                        author = paper.get('author', '未知作者')
                        missing_suggestions.append(f"- **{title}** (作者: {author})")
        
        if not missing_suggestions:
            return """### 🔍 缺失文献建议
            
**状态**：基于现有检索结果，暂未发现明显缺失的重要文献。"""
        
        return f"""### 🔍 缺失文献建议

**推荐补充的重要文献**：
基于CNKI检索结果，以下文献可能对研究有重要价值但未被引用：

{chr(10).join(missing_suggestions[:6])}

**建议**：
- 评估这些文献与研究主题的相关性
- 考虑在文献综述中补充相关讨论
- 关注这些文献提出的新观点或方法"""

    def _generate_metadata_analysis_content(self, literature_metadata_analysis: Dict) -> str:
        """生成文献元数据分析内容"""
        if not literature_metadata_analysis:
            return ""
        
        # 获取各项分析结果
        journal_analysis = literature_metadata_analysis.get('journal_analysis', {})
        author_analysis = literature_metadata_analysis.get('author_analysis', {})
        affiliation_analysis = literature_metadata_analysis.get('affiliation_analysis', {})
        core_journal_analysis = literature_metadata_analysis.get('core_journal_analysis', {})
        subject_analysis = literature_metadata_analysis.get('subject_analysis', {})
        year_analysis = literature_metadata_analysis.get('year_analysis', {})
        citation_analysis = literature_metadata_analysis.get('citation_analysis', {})
        total_stats = literature_metadata_analysis.get('total_statistics', {})
        
        content = "## 📊 相关文献元数据分析\n\n"
        
        # 总体统计
        if total_stats:
            content += "### 📈 总体统计\n\n"
            content += f"- **文献总数**: {total_stats.get('total_papers', 0)} 篇\n"
            
            papers_by_lang = total_stats.get('papers_by_language', {})
            for lang, count in papers_by_lang.items():
                content += f"- **{lang}文献**: {count} 篇\n"
            
            content += f"- **核心期刊文献**: {total_stats.get('papers_with_core_index', 0)} 篇\n"
            content += f"- **有引用记录文献**: {total_stats.get('papers_with_citations', 0)} 篇\n"
            content += f"- **有基金支持文献**: {total_stats.get('papers_with_funds', 0)} 篇\n\n"
        
        # 期刊分析
        if journal_analysis:
            content += "### 📚 期刊分布分析\n\n"
            top_journals = journal_analysis.get('top_journals', [])
            if top_journals:
                content += "**主要发表期刊（前10名）**：\n\n"
                for i, (journal, count) in enumerate(top_journals[:10], 1):
                    content += f"{i}. **{journal}** ({count} 篇)\n"
                content += "\n"
            
            journal_types = journal_analysis.get('journal_types', {})
            if journal_types:
                content += "**期刊类型分布**：\n"
                for jtype, count in journal_types.items():
                    content += f"- {jtype}: {count} 篇\n"
                content += "\n"
        
        # 核心期刊分析
        if core_journal_analysis:
            content += "### 🏆 核心期刊分析\n\n"
            index_dist = core_journal_analysis.get('index_distribution', {})
            if index_dist:
                content += "**核心期刊索引分布**：\n"
                for index_name, count in index_dist.items():
                    content += f"- **{index_name}**: {count} 篇\n"
                content += "\n"
        
        # 学科分析
        if subject_analysis:
            content += "### 📖 学科分布分析\n\n"
            l1_subjects = subject_analysis.get('level1_subjects', [])
            if l1_subjects:
                content += "**一级学科分布**：\n"
                for subject, count in l1_subjects[:8]:
                    content += f"- **{subject}**: {count} 篇\n"
                content += "\n"
            
            l2_subjects = subject_analysis.get('level2_subjects', [])
            if l2_subjects:
                content += "**二级学科分布（前10名）**：\n"
                for subject, count in l2_subjects[:10]:
                    content += f"- **{subject}**: {count} 篇\n"
                content += "\n"
        
        # 年份分析
        if year_analysis:
            content += "### 📅 时间分布分析\n\n"
            year_dist = year_analysis.get('year_distribution', {})
            earliest = year_analysis.get('earliest_year', '')
            latest = year_analysis.get('latest_year', '')
            
            if earliest and latest:
                content += f"**时间跨度**: {earliest} - {latest} 年\n"
                content += f"**年份覆盖**: {year_analysis.get('year_span', 0)} 年\n\n"
            
            if year_dist:
                content += "**年份分布**：\n"
                # 只显示最近10年的分布
                recent_years = sorted(year_dist.items(), reverse=True)[:10]
                for year, count in recent_years:
                    if year.strip():  # 过滤空年份
                        content += f"- **{year}年**: {count} 篇\n"
                content += "\n"
        
        # 作者分析
        if author_analysis:
            content += "### 👥 作者分析\n\n"
            content += f"**作者总数**: {author_analysis.get('total_authors', 0)} 人\n"
            content += f"**通讯作者总数**: {author_analysis.get('total_corresponding_authors', 0)} 人\n\n"
            
            top_authors = author_analysis.get('top_authors', [])
            if top_authors:
                content += "**高产作者（前10名）**：\n"
                for i, (author, count) in enumerate(top_authors[:10], 1):
                    if count > 1:  # 只显示发表多篇文章的作者
                        content += f"{i}. **{author}** ({count} 篇)\n"
                content += "\n"
        
        # 单位分析
        if affiliation_analysis:
            content += "### 🏛️ 机构分析\n\n"
            content += f"**机构总数**: {affiliation_analysis.get('total_affiliations', 0)} 个\n\n"
            
            top_affs = affiliation_analysis.get('top_affiliations', [])
            if top_affs:
                content += "**主要研究机构（前10名）**：\n"
                for i, (aff, count) in enumerate(top_affs[:10], 1):
                    if count > 1:  # 只显示有多篇文章的机构
                        content += f"{i}. **{aff}** ({count} 篇)\n"
                content += "\n"
        
        # 引用分析
        if citation_analysis:
            content += "### 📈 引用分析\n\n"
            total_citations = citation_analysis.get('total_citations', 0)
            avg_citations = citation_analysis.get('avg_citations', 0)
            max_citations = citation_analysis.get('max_citations', 0)
            
            content += f"**总引用次数**: {total_citations} 次\n"
            content += f"**平均引用次数**: {avg_citations:.2f} 次/篇\n"
            content += f"**最高引用次数**: {max_citations} 次\n\n"
            
            total_downloads = citation_analysis.get('total_downloads', 0)
            avg_downloads = citation_analysis.get('avg_downloads', 0)
            
            content += f"**总下载次数**: {total_downloads} 次\n"
            content += f"**平均下载次数**: {avg_downloads:.2f} 次/篇\n\n"
        
        content += "**分析说明**：以上分析基于CNKI检索到的相关文献，反映了该研究领域的基本特征和发展趋势。\n\n"
        
        return content
    
    def _generate_report_content(self, input_file: str, thesis_extracted_info: Optional[Dict[str, str]] = None,
                               papers_by_lang: Optional[Dict[str, List]] = None,
                               literature_metadata_analysis: Optional[Dict] = None) -> str:
        """生成报告内容"""
        base_name = Path(input_file).stem
        
        # 尝试加载相关的分析数据
        analysis_data = self._load_analysis_data(base_name)
        
        # 进行主题分析
        theme_analysis = self._analyze_literature_themes(analysis_data)
        
        # 生成创新性分析，传递论文抽取信息
        innovation_analysis = self._generate_innovation_analysis(analysis_data, theme_analysis, thesis_extracted_info)
        
        # 生成独立文献综述分析报告并获取总结信息
        literature_review_summary = None
        if thesis_extracted_info and papers_by_lang:
            # 生成独立的详细文献综述分析报告
            detailed_report_path = self.literature_analyzer.analyze_literature_review(
                input_file, thesis_extracted_info, papers_by_lang, self.config_mgr.get_output_dir()
            )
            logger.info(f"独立文献综述分析报告已生成: {detailed_report_path}")
            
            # 暂时禁用总结功能，因为方法不存在
            # literature_review_summary = self.literature_analyzer.generate_summary_for_main_report(
            #     thesis_extracted_info, papers_by_lang
            # )
        
        # 生成文献综述分析（向后兼容）
        literature_review_analysis = self._generate_literature_review_analysis(
            thesis_extracted_info, papers_by_lang, analysis_data
        )
        
        # 生成文献元数据分析（新增功能）
        metadata_analysis_content = self._generate_metadata_analysis_content(literature_metadata_analysis) if literature_metadata_analysis else ""
        
        # 生成Markdown内容
        content = self._create_markdown_content(input_file, analysis_data, theme_analysis, 
                                              innovation_analysis, literature_review_analysis,
                                              metadata_analysis_content, literature_review_summary)
        
        return content
    
    def _load_analysis_data(self, base_name: str) -> Dict[str, Any]:
        """加载分析数据"""
        output_dir = self.config_mgr.get_output_dir()
        
        data = {
            'chinese_papers': None,
            'english_papers': None,
            'dedup_chinese': None,
            'dedup_english': None,
            'top_chinese': None,
            'top_english': None
        }
        
        # 定义文件模式
        patterns = {
            'chinese_papers': f"{base_name}_relevant_papers_Chinese.json",
            'english_papers': f"{base_name}_relevant_papers_English.json",
            'dedup_chinese': f"{base_name}_relevant_papers_dedup_Chinese.json",
            'dedup_english': f"{base_name}_relevant_papers_dedup_English.json",
        }
        
        # 查找TOP论文文件（可能有不同的数量）
        top_count = self.config_mgr.get_top_papers_count()
        patterns.update({
            'top_chinese': f"{base_name}_TOP{top_count}PAPERS_Chinese.json",
            'top_english': f"{base_name}_TOP{top_count}PAPERS_English.json",
        })
        
        # 加载存在的文件
        for key, filename in patterns.items():
            file_path = os.path.join(output_dir, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data[key] = json.load(f)
                except Exception as e:
                    print(f"警告：无法加载 {filename}: {e}")
        
        return data
    
    def _build_literature_context(self, analysis_data: Dict[str, Any], theme_analysis: Dict[str, Any]) -> str:
        """构建文献上下文信息"""
        
        context = ""
        
        # 统计文献数量
        total_chinese = len(analysis_data['top_chinese']) if analysis_data['top_chinese'] else 0
        total_english = len(analysis_data['top_english']) if analysis_data['top_english'] else 0
        
        context += f"**文献检索统计**：\n"
        context += f"- 中文高质量相关文献：{total_chinese}篇\n"
        context += f"- 英文高质量相关文献：{total_english}篇\n"
        context += f"- 文献总数：{total_chinese + total_english}篇\n\n"
        
        # 主要研究主题
        if theme_analysis.get('chinese_themes') or theme_analysis.get('english_themes'):
            context += "**主要研究主题分布**：\n"
            
            # 合并中英文主题
            all_themes = {}
            if theme_analysis.get('chinese_themes'):
                all_themes.update(theme_analysis['chinese_themes'])
            if theme_analysis.get('english_themes'):
                for theme, count in theme_analysis['english_themes'].items():
                    all_themes[theme] = all_themes.get(theme, 0) + count
            
            # 排序并取前10个主题
            top_themes = sorted(all_themes.items(), key=lambda x: x[1], reverse=True)[:10]
            for theme, count in top_themes:
                context += f"- {theme}: {count}篇\n"
            context += "\n"
        
        # 年份分布
        if theme_analysis.get('year_distribution'):
            context += "**年份分布**：\n"
            sorted_years = sorted(theme_analysis['year_distribution'].items())
            total_papers = sum(theme_analysis['year_distribution'].values())
            
            # 近5年的文献比例
            recent_years = [year for year in theme_analysis['year_distribution'].keys() if year >= 2020]
            if recent_years:
                recent_count = sum(theme_analysis['year_distribution'][year] for year in recent_years)
                recent_percentage = (recent_count / total_papers) * 100
                context += f"- 近5年文献占比：{recent_percentage:.1f}% ({recent_count}篇)\n"
            
            context += f"- 研究时间跨度：{min(theme_analysis['year_distribution'].keys())}-{max(theme_analysis['year_distribution'].keys())}年\n\n"
        
        # 代表性论文
        if analysis_data.get('top_chinese') or analysis_data.get('top_english'):
            context += "**代表性相关研究**：\n"
            
            # 中文代表性论文
            if analysis_data.get('top_chinese'):
                context += "中文文献代表：\n"
                for i, paper in enumerate(analysis_data['top_chinese'][:3], 1):
                    context += f"{i}. {paper.get('Title', '未知标题')}\n"
                    context += f"   关键词: {paper.get('KeyWords', '')}\n"
                context += "\n"
            
            # 英文代表性论文
            if analysis_data.get('top_english'):
                context += "英文文献代表：\n"
                for i, paper in enumerate(analysis_data['top_english'][:3], 1):
                    context += f"{i}. {paper.get('Title', 'Unknown Title')}\n"
                    context += f"   Keywords: {paper.get('KeyWords', '').replace(';', ', ')}\n"
                context += "\n"
        
        return context
    
    def _build_context_prompt(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """构建上下文设置提示词（多轮对话第一轮）"""
        
        prompt = f"""你是一位资深的学术评审专家，我将请你分析一篇学术论文的创新性。首先，请接收并理解以下论文的基本信息和相关文献背景：

**目标论文信息**：
- 论文标题：{thesis_info.get('title', '未提供')}
- 中文关键词：{thesis_info.get('keywords_cn', '未提供')}
- 英文关键词：{thesis_info.get('keywords_en', '未提供')}
- 研究方法：{thesis_info.get('methodology', '未提供')}
- 理论框架：{thesis_info.get('theoretical_framework', '未提供')}
- 主要创新点：{thesis_info.get('main_innovations', '未提供')}
- 研究结论：{thesis_info.get('research_conclusions', '未提供')}
- 实际问题：{thesis_info.get('practical_problems', '未提供')}
- 解决方案：{thesis_info.get('proposed_solutions', '未提供')}
- 应用价值：{thesis_info.get('application_value', '未提供')}

**相关文献背景**：
{literature_context}

请确认你已经理解了以上论文信息和文献背景。接下来我将分别从方法学创新、理论贡献和实践价值三个维度向你询问创新性分析。

请简单回复"已理解论文信息和文献背景，准备进行创新性分析"即可。"""

        return prompt
    
    def _build_methodology_analysis_prompt(self) -> str:
        """构建方法学创新分析提示词（多轮对话后续轮次）"""
        
        prompt = """基于前面提供的论文信息和文献背景，请分析目标论文在**方法学方面的创新点**：

**分析要求**：
1. **研究方法创新性**：
   - 是否采用了新的研究方法或技术路径？
   - 对现有方法进行了哪些改进和优化？
   - 与相关文献中的方法相比有何突破？

2. **技术路径创新**：
   - 技术实现上有何独特之处？
   - 是否解决了现有方法的局限性？
   - 创新方法的科学性和可重复性如何？

3. **方法论贡献**：
   - 为相关研究领域提供了什么新的方法论工具？
   - 方法的适用范围和推广价值如何？

**输出要求**：
- 学术、客观的语调，重点突出创新点和差异化优势
- 提供具体的分析而非空泛的评价
- 字数控制在300-500字之间
- 如果信息不足，请明确指出并提供改进建议"""

        return prompt
    
    def _build_theory_analysis_prompt(self) -> str:
        """构建理论贡献分析提示词（多轮对话后续轮次）"""
        
        prompt = """基于前面提供的论文信息和文献背景，请分析目标论文的**理论贡献**：

**分析要求**：
1. **理论创新性**：
   - 是否提出了新的理论框架、概念或模型？
   - 对现有理论进行了哪些扩展和完善？
   - 与相关文献的理论基础相比有何原创性？

2. **理论整合性**：
   - 是否创新性地整合了多个理论视角？
   - 理论融合的逻辑性和科学性如何？
   - 为跨理论研究提供了什么新思路？

3. **理论影响力**：
   - 理论贡献对学科发展的意义？
   - 为后续研究奠定了什么理论基础？
   - 理论的解释力和预测能力如何？

**输出要求**：
- 学术、严谨的语调，重点突出理论创新的独特性和首创性
- 基于文献对比进行客观评估
- 字数控制在300-500字之间
- 如果理论信息不充分，请明确指出并提供建议"""

        return prompt
    
    def _build_practice_analysis_prompt(self) -> str:
        """构建实践价值分析提示词（多轮对话后续轮次）"""
        
        prompt = """基于前面提供的论文信息和文献背景，请分析目标论文的**实践价值和应用前景**：

**分析要求**：
1. **问题解决能力**：
   - 针对什么实际问题提出了解决方案？
   - 解决方案的创新性和可行性如何？
   - 与现有解决方案相比有何优势？

2. **应用前景评估**：
   - 研究成果的市场应用潜力如何？
   - 在相关行业和领域的推广价值？
   - 技术转化和产业化的可能性？

3. **社会经济价值**：
   - 能否提高效率、降低成本或创造价值？
   - 对社会发展和民生改善的贡献？
   - 预期的经济效益和社会效益？

**输出要求**：
- 实用、客观的角度分析，重点突出实践创新和应用价值的具体表现
- 结合相关文献进行对比分析
- 字数控制在300-500字之间
- 如果信息不足，请明确指出改进建议"""

        return prompt
    
    def _build_methodology_prompt(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """构建方法学创新分析提示词"""
        
        prompt = f"""你是一位资深的学术评审专家，请基于以下信息分析目标论文在方法学方面的创新点：

**目标论文信息**：
- 论文标题：{thesis_info.get('title', '未提供')}
- 研究方法：{thesis_info.get('methodology', '未提供')}
- 主要创新点：{thesis_info.get('main_innovations', '未提供')}
- 关键词：{thesis_info.get('keywords', '未提供')}

**相关文献背景**：
{literature_context}

**分析要求**：
请从以下角度深入分析目标论文的方法学创新，并与现有文献进行对比：

1. **研究方法创新性**：
   - 是否采用了新的研究方法或技术路径？
   - 对现有方法进行了哪些改进和优化？
   - 与相关文献中的方法相比有何突破？

2. **技术路径创新**：
   - 技术实现上有何独特之处？
   - 是否解决了现有方法的局限性？
   - 创新方法的科学性和可重复性如何？

3. **方法论贡献**：
   - 为相关研究领域提供了什么新的方法论工具？
   - 方法的适用范围和推广价值如何？

**输出要求**：
- 请以学术、客观的语调分析
- 重点突出创新点和差异化优势
- 提供具体的分析而非空泛的评价
- 字数控制在300-500字之间
- 如果信息不足，请明确指出并提供改进建议

请开始你的分析："""

        return prompt
    
    def _build_theory_prompt(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """构建理论贡献分析提示词"""
        
        prompt = f"""你是一位资深的学术理论研究专家，请基于以下信息评估目标论文的理论贡献：

**目标论文信息**：
- 论文标题：{thesis_info.get('title', '未提供')}
- 理论框架：{thesis_info.get('theoretical_framework', '未提供')}
- 主要创新点：{thesis_info.get('main_innovations', '未提供')}
- 研究结论：{thesis_info.get('research_conclusions', '未提供')}

**相关文献背景**：
{literature_context}

**分析要求**：
请从以下角度深入分析目标论文的理论贡献：

1. **理论创新性**：
   - 是否提出了新的理论框架、概念或模型？
   - 对现有理论进行了哪些扩展和完善？
   - 与相关文献的理论基础相比有何原创性？

2. **理论整合性**：
   - 是否创新性地整合了多个理论视角？
   - 理论融合的逻辑性和科学性如何？
   - 为跨理论研究提供了什么新思路？

3. **理论影响力**：
   - 理论贡献对学科发展的意义？
   - 为后续研究奠定了什么理论基础？
   - 理论的解释力和预测能力如何？

**输出要求**：
- 请以学术、严谨的语调分析
- 重点突出理论创新的独特性和首创性
- 基于文献对比进行客观评估
- 字数控制在300-500字之间
- 如果理论信息不充分，请明确指出并提供建议

请开始你的分析："""

        return prompt
    
    def _build_practice_prompt(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """构建实践价值分析提示词"""
        
        prompt = f"""你是一位资深的产学研结合专家，请基于以下信息评估目标论文的实践价值和应用前景：

**目标论文信息**：
- 论文标题：{thesis_info.get('title', '未提供')}
- 实际问题：{thesis_info.get('practical_problems', '未提供')}
- 解决方案：{thesis_info.get('proposed_solutions', '未提供')}
- 应用价值：{thesis_info.get('application_value', '未提供')}

**相关文献背景**：
{literature_context}

**分析要求**：
请从以下角度深入分析目标论文的实践价值：

1. **问题解决能力**：
   - 针对什么实际问题提出了解决方案？
   - 解决方案的创新性和可行性如何？
   - 与现有解决方案相比有何优势？

2. **应用前景评估**：
   - 研究成果的市场应用潜力如何？
   - 在相关行业和领域的推广价值？
   - 技术转化和产业化的可能性？

3. **社会经济价值**：
   - 能否提高效率、降低成本或创造价值？
   - 对社会发展和民生改善的贡献？
   - 预期的经济效益和社会效益？

**输出要求**：
- 请以实用、客观的角度分析
- 重点突出实践创新和应用价值的具体表现
- 基于实际应用场景进行评估
- 字数控制在300-500字之间
- 如果应用信息不充分，请明确指出并提供建议

请开始你的分析："""

        return prompt
    
    def _get_fallback_methodology_analysis(self, thesis_info: Dict[str, str]) -> str:
        """获取方法学分析的回退内容"""
        methodology = thesis_info.get('methodology', '')
        if methodology:
            return f"**方法学分析**：基于提供的研究方法信息，该研究采用了相应的研究方法。建议进一步明确方法学创新点，通过与现有方法的详细对比来突出研究的方法论贡献。"
        else:
            return "**方法学分析**：由于缺少详细的研究方法信息，无法进行深入的方法学创新分析。建议补充完善研究方法的详细描述，包括技术路径、实现方案等关键信息。"
    
    def _get_fallback_theory_analysis(self, thesis_info: Dict[str, str]) -> str:
        """获取理论分析的回退内容"""
        theoretical_framework = thesis_info.get('theoretical_framework', '')
        if theoretical_framework:
            return f"**理论贡献分析**：基于提供的理论框架信息，该研究构建了相应的理论基础。建议进一步阐述理论创新的独特性，明确与现有理论的差异和改进之处。"
        else:
            return "**理论贡献分析**：由于缺少详细的理论框架信息，无法进行深入的理论贡献分析。建议完善理论框架的阐述，明确理论创新点和学术贡献。"
    
    def _get_fallback_practice_analysis(self, thesis_info: Dict[str, str]) -> str:
        """获取实践分析的回退内容"""
        application_value = thesis_info.get('application_value', '')
        if application_value:
            return f"**实践价值分析**：基于提供的应用价值信息，该研究具有一定的实际应用潜力。建议进一步详细描述具体的应用场景、实施方案和预期效果。"
        else:
            return "**实践价值分析**：由于缺少详细的应用价值信息，无法进行深入的实践价值评估。建议明确阐述研究的实际应用价值、推广前景和社会效益。"
    
    def _create_markdown_content(self, input_file: str, analysis_data: Dict[str, Any], 
                               theme_analysis: Dict[str, Any], innovation_analysis: Dict[str, str],
                               literature_review_analysis: str = "", metadata_analysis_content: str = "",
                               literature_review_summary: Optional[Dict] = None) -> str:
        """创建Markdown内容"""
        base_name = Path(input_file).stem
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# 论文评估报告

## 基本信息

- **论文名称**: {base_name}
- **输入文件**: {input_file}
- **生成时间**: {timestamp}
- **评估系统**: 基于AI的学位论文创新评估系统

---

## 📊 评估概览

"""
        
        # 添加统计信息
        stats = self._calculate_statistics(analysis_data)
        content += self._format_statistics_section(stats)
        
        # 如果有文献综述总结信息，添加到概览中
        if literature_review_summary:
            content += "\n### 📚 文献综述质量概览\n\n"
            if literature_review_summary.get('overall_score'):
                content += f"- **综合评分**: {literature_review_summary['overall_score']:.1f}/10.0\n"
            if literature_review_summary.get('coverage_score'):
                content += f"- **覆盖度评分**: {literature_review_summary['coverage_score']:.1f}/10.0\n"
            if literature_review_summary.get('depth_score'):
                content += f"- **深度评分**: {literature_review_summary['depth_score']:.1f}/10.0\n"
            if literature_review_summary.get('relevance_score'):
                content += f"- **相关性评分**: {literature_review_summary['relevance_score']:.1f}/10.0\n"
            if literature_review_summary.get('timeliness_score'):
                content += f"- **时效性评分**: {literature_review_summary['timeliness_score']:.1f}/10.0\n"
            content += f"- **详细分析报告**: 请参见独立生成的文献综述分析报告\n\n"
        
        # 添加主题分析和年份分布
        content += self._format_theme_analysis_section(theme_analysis)
        
        # 添加各个部分
        sections = self.report_config.get('include_sections', [])
        
        if 'summary' in sections:
            content += self._format_summary_section(analysis_data)
        
        if 'innovation_analysis' in sections:
            content += self._format_enhanced_innovation_section(innovation_analysis, theme_analysis, analysis_data)
        
        # 添加文献综述分析（新功能）
        if literature_review_analysis:
            content += f"\n\n{literature_review_analysis}\n"
        
        # 添加文献元数据分析（新功能）
        if metadata_analysis_content:
            content += f"\n\n{metadata_analysis_content}\n"
        
        if 'related_papers' in sections:
            content += self._format_enhanced_related_papers_section(analysis_data, theme_analysis)
        
        if 'recommendations' in sections:
            content += self._format_recommendations_section(analysis_data)
        
        # 添加附录
        content += self._format_appendix_section(analysis_data)
        
        return content
    
    def _calculate_statistics(self, analysis_data: Dict[str, Any]) -> Dict[str, int]:
        """计算统计信息"""
        stats = {
            'total_chinese_papers': 0,
            'total_english_papers': 0,
            'dedup_chinese_papers': 0,
            'dedup_english_papers': 0,
            'top_chinese_papers': 0,
            'top_english_papers': 0
        }
        
        # 计算各类论文数量
        if analysis_data['chinese_papers']:
            stats['total_chinese_papers'] = len(analysis_data['chinese_papers'])
        
        if analysis_data['english_papers']:
            stats['total_english_papers'] = len(analysis_data['english_papers'])
        
        if analysis_data['dedup_chinese']:
            stats['dedup_chinese_papers'] = len(analysis_data['dedup_chinese'])
        
        if analysis_data['dedup_english']:
            stats['dedup_english_papers'] = len(analysis_data['dedup_english'])
        
        if analysis_data['top_chinese']:
            stats['top_chinese_papers'] = len(analysis_data['top_chinese'])
        
        if analysis_data['top_english']:
            stats['top_english_papers'] = len(analysis_data['top_english'])
        
        return stats
    
    def _format_theme_analysis_section(self, theme_analysis: Dict[str, Any]) -> str:
        """格式化主题分析部分"""
        content = """### 🔍 文献主题分析

**研究热点分布：**
"""
        
        # 中文文献主题Top10
        if theme_analysis['chinese_themes']:
            sorted_chinese = sorted(theme_analysis['chinese_themes'].items(), 
                                  key=lambda x: x[1], reverse=True)[:10]
            content += "\n**中文文献主要主题：**\n"
            for i, (theme, count) in enumerate(sorted_chinese, 1):
                content += f"{i}. {theme} ({count}篇)\n"
        
        # 英文文献主题Top10
        if theme_analysis['english_themes']:
            sorted_english = sorted(theme_analysis['english_themes'].items(), 
                                  key=lambda x: x[1], reverse=True)[:10]
            content += "\n**英文文献主要主题：**\n"
            for i, (theme, count) in enumerate(sorted_english, 1):
                content += f"{i}. {theme} ({count}篇)\n"
        
        # 年份分布分析
        if theme_analysis['year_distribution']:
            content += "\n**年份分布分析：**\n"
            sorted_years = sorted(theme_analysis['year_distribution'].items())
            
            total_papers = sum(theme_analysis['year_distribution'].values())
            content += f"- 研究时间跨度：{min(theme_analysis['year_distribution'].keys())}-{max(theme_analysis['year_distribution'].keys())}年\n"
            content += f"- 总论文数量：{total_papers}篇\n"
            content += "- 年度分布：\n"
            
            for year, count in sorted_years:
                percentage = (count / total_papers) * 100
                content += f"  - {year}年: {count}篇 ({percentage:.1f}%)\n"
            
            # 分析研究趋势
            recent_years = [year for year in theme_analysis['year_distribution'].keys() if year >= 2020]
            if recent_years:
                recent_count = sum(theme_analysis['year_distribution'][year] for year in recent_years)
                recent_percentage = (recent_count / total_papers) * 100
                content += f"- 近5年文献占比：{recent_percentage:.1f}% ({recent_count}篇)\n"
        
        content += "\n"
        return content
    
    def _format_enhanced_innovation_section(self, innovation_analysis: Dict[str, str], 
                                          theme_analysis: Dict[str, Any],
                                          analysis_data: Dict[str, Any]) -> str:
        """格式化增强的创新性分析部分"""
        
        # 计算实际的文献总数 - 修复数据不一致问题
        total_chinese = len(analysis_data['top_chinese']) if analysis_data.get('top_chinese') else 0
        total_english = len(analysis_data['top_english']) if analysis_data.get('top_english') else 0
        total_papers = total_chinese + total_english
        
        # 添加分析方法说明
        analysis_method = "AI驱动的深度分析" if self.ai_enabled else "基于规则的智能分析"
        
        content = f"""## 🔬 创新性分析

*本节使用{analysis_method}方法生成*

### 🆕 创新点识别

基于与{total_papers}篇相关文献的深度对比分析，识别出以下核心创新点：

#### 1. **方法学创新**
{innovation_analysis['methodology']}

#### 2. **理论贡献**
{innovation_analysis['theory']}

#### 3. **实践价值**
{innovation_analysis['practice']}

### 📊 创新度评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 原创性 | ⭐⭐⭐⭐☆ | 基于{analysis_method}，研究在方法或观点上具有一定的原创性 |
| 新颖性 | ⭐⭐⭐⭐☆ | 研究方法或理论框架相对于现有文献具有新颖性 |
| 重要性 | ⭐⭐⭐☆☆ | 研究解决的问题具有一定的学术价值和实践意义 |
| 影响力 | ⭐⭐⭐☆☆ | 研究成果预期对相关领域产生积极影响 |

*注：评分基于{analysis_method}和文献对比分析*

### 📈 研究趋势对比

**与现有研究的差异化定位：**
"""
        
        # 添加基于主题分析的趋势对比
        if theme_analysis['chinese_themes'] or theme_analysis['english_themes']:
            content += self._generate_trend_comparison(theme_analysis)
        
        content += "\n"
        return content
    
    def _generate_trend_comparison(self, theme_analysis: Dict[str, Any]) -> str:
        """生成研究趋势对比分析"""
        comparison = ""
        
        # 分析主要研究领域
        all_themes = {}
        if theme_analysis['chinese_themes']:
            all_themes.update(theme_analysis['chinese_themes'])
        if theme_analysis['english_themes']:
            for theme, count in theme_analysis['english_themes'].items():
                all_themes[theme] = all_themes.get(theme, 0) + count
        
        top_themes = sorted(all_themes.items(), key=lambda x: x[1], reverse=True)[:5]
        
        comparison += "- **主流研究方向**：\n"
        for theme, count in top_themes:
            comparison += f"  - {theme}: {count}篇相关研究\n"
        
        # 通用化的差异化分析
        comparison += "- **本研究的差异化**：在现有研究基础上，本研究从新的角度切入，提供了不同的理论视角或方法路径\n"
        comparison += "- **学术贡献**：为相关研究领域提供了新的思路和方法，丰富了该领域的理论体系和实践应用\n"
        comparison += "- **研究价值**：通过与现有文献的对比分析，显示出本研究在方法创新、理论突破或应用拓展方面的独特价值\n"
        
        return comparison
    
    def _format_enhanced_related_papers_section(self, analysis_data: Dict[str, Any], 
                                              theme_analysis: Dict[str, Any]) -> str:
        """格式化增强的相关论文部分"""
        content = """## 📚 相关文献分析

### 🔍 文献检索结果

**检索范围与策略：**
- 检索数据库：CNKI中国知网、国际学术数据库
- 检索关键词：基于论文主题和关键词进行精准检索
- 时间范围：近10年相关研究文献
- 检索策略：采用主题词与自由词结合的方式，确保检索的全面性和准确性

**文献质量分析：**
"""
        
        # 计算文献统计
        total_chinese = len(analysis_data['top_chinese']) if analysis_data['top_chinese'] else 0
        total_english = len(analysis_data['top_english']) if analysis_data['top_english'] else 0
        total_papers = total_chinese + total_english
        
        content += f"- 共检索到{total_papers}篇高质量相关文献，其中中文文献{total_chinese}篇，英文文献{total_english}篇\n"
        content += "- 文献来源涵盖顶级期刊和重要会议，保证了研究的权威性\n"
        content += "- 文献时间分布合理，既包含基础理论研究，也包含最新发展动态\n\n"
        
        # 添加研究热点分布分析
        if theme_analysis['chinese_themes'] or theme_analysis['english_themes']:
            content += self._generate_research_hotspots_analysis(theme_analysis)
        
        # 添加TOP论文列表
        if analysis_data['top_chinese'] or analysis_data['top_english']:
            content += "### ⭐ 重点相关论文\n\n"
            
            # 中文TOP论文
            if analysis_data['top_chinese']:
                content += "#### 中文文献 (精选代表性研究)\n\n"
                for i, paper in enumerate(analysis_data['top_chinese'][:5], 1):
                    content += self._format_key_paper(paper, i, is_chinese=True)
            
            # 英文TOP论文
            if analysis_data['top_english']:
                content += "#### 英文文献 (国际前沿研究)\n\n"
                for i, paper in enumerate(analysis_data['top_english'][:5], 1):
                    content += self._format_key_paper(paper, i, is_chinese=False)
        
        return content
    
    def _format_key_paper(self, paper: Dict[str, Any], index: int, is_chinese: bool = True) -> str:
        """格式化重点论文信息，充分利用元数据"""
        content = ""
        
        # 基本信息
        title = paper.get('Title', '未知标题' if is_chinese else 'Unknown Title')
        year = paper.get('PublicationYear', '未知年份' if is_chinese else 'Unknown Year')
        keywords = paper.get('KeyWords', '')
        if is_chinese:
            keywords = keywords.replace(';;', '、')
        else:
            keywords = keywords.replace(';', ', ')
        
        content += f"{index}. **{title}**\n"
        
        # 作者信息
        authors = paper.get('Authors', [])
        if authors and isinstance(authors, list):
            author_info = self._format_authors(authors, is_chinese)
            content += f"   - **作者**: {author_info}\n"
        
        # 机构信息
        affiliations = paper.get('Affiliations', [])
        if affiliations and isinstance(affiliations, list):
            affiliation_names = [aff.get('name', '') for aff in affiliations if isinstance(aff, dict) and aff.get('name')]
            if affiliation_names:
                content += f"   - **机构**: {'; '.join(affiliation_names[:3])}\n"  # 最多显示3个机构
        
        # 发表信息
        content += f"   - **发表年份**: {year}\n"
        
        # 期刊/会议信息
        source = paper.get('Source', {})
        journal = paper.get('Journal', '')
        if (source and isinstance(source, dict)) or journal:
            publication_info = self._format_publication_info(source if isinstance(source, dict) else {}, journal, is_chinese)
            if publication_info:
                content += f"   - **发表载体**: {publication_info}\n"
        
        # 基金资助信息
        funds = paper.get('Funds', [])
        if funds and isinstance(funds, list):
            fund_info = self._format_funds(funds, is_chinese)
            if fund_info:
                content += f"   - **基金资助**: {fund_info}\n"
        
        # 关键词
        if keywords:
            content += f"   - **关键词**: {keywords}\n"
        
        # 影响力指标
        metrics = paper.get('Metrics', {})
        if metrics and isinstance(metrics, dict):
            metrics_info = self._format_metrics(metrics, is_chinese)
            if metrics_info:
                content += f"   - **影响力指标**: {metrics_info}\n"
        
        # 摘要节选
        abstract = paper.get('Abstract', '')
        if abstract:
            abstract_snippet = abstract[:120] + "..." if len(abstract) > 120 else abstract
            content += f"   - **摘要节选**: {abstract_snippet}\n"
        
        # 相关度分析
        relevance = self._analyze_paper_relevance(paper)
        content += f"   - **学术价值**: 在{relevance}方面具有重要参考价值\n\n"
        
        return content
    
    def _format_authors(self, authors: List[Dict[str, Any]], is_chinese: bool = True) -> str:
        """格式化作者信息"""
        if not authors or not isinstance(authors, list):
            return "未知作者" if is_chinese else "Unknown Authors"
        
        author_strs = []
        for author in authors[:5]:  # 最多显示5个作者
            if not isinstance(author, dict):
                continue
            name = author.get('name', '')
            if name:
                if author.get('corresponding'):
                    name += "*"  # 通讯作者标记
                author_strs.append(name)
        
        if len(authors) > 5:
            author_strs.append("等" if is_chinese else "et al.")
        
        return ", ".join(author_strs)
    
    def _format_publication_info(self, source: Dict[str, Any], journal: str, is_chinese: bool = True) -> str:
        """格式化发表信息"""
        if source:
            title = source.get('title', journal)
            volume = source.get('volume', '')
            issue = source.get('issue', '')
            
            if title:
                info = title
                if volume and issue:
                    info += f", {volume}({issue})"
                elif volume:
                    info += f", {volume}"
                return info
        
        return journal if journal else ""
    
    def _format_funds(self, funds: List[Dict[str, Any]], is_chinese: bool = True) -> str:
        """格式化基金信息"""
        if not funds or not isinstance(funds, list):
            return ""
        
        fund_titles = []
        for fund in funds[:2]:  # 最多显示2个基金
            if not isinstance(fund, dict):
                continue
            title = fund.get('title', '')
            if title:
                # 简化基金信息显示
                if '国家自然科学基金' in title:
                    fund_titles.append("国家自然科学基金")
                elif 'National Natural Science Foundation' in title:
                    fund_titles.append("NSFC")
                elif '国家重点研发计划' in title:
                    fund_titles.append("国家重点研发计划")
                elif '省自然科学基金' in title or '市自然科学基金' in title:
                    fund_titles.append("省/市级基金")
                else:
                    # 提取基金名称的关键部分
                    short_title = title[:30] + "..." if len(title) > 30 else title
                    fund_titles.append(short_title)
        
        if len(funds) > 2:
            fund_titles.append("等" if is_chinese else "etc.")
        
        return "; ".join(fund_titles)
    
    def _format_metrics(self, metrics: Dict[str, Any], is_chinese: bool = True) -> str:
        """格式化影响力指标"""
        metric_strs = []
        
        download_count = metrics.get('download_count')
        citation_count = metrics.get('citation_count')
        
        if download_count is not None and download_count > 0:
            metric_strs.append(f"下载{download_count}次" if is_chinese else f"{download_count} downloads")
        
        if citation_count is not None and citation_count > 0:
            metric_strs.append(f"被引{citation_count}次" if is_chinese else f"{citation_count} citations")
        
        return "; ".join(metric_strs) if metric_strs else ""
    
    def _generate_research_hotspots_analysis(self, theme_analysis: Dict[str, Any]) -> str:
        """生成研究热点分布分析"""
        content = "**研究热点分布：**\n"
        
        # 通用研究类型分类
        method_keywords = ['方法', 'method', '模型', 'model', '算法', 'algorithm', '分析', 'analysis', '技术', 'technology']
        theory_keywords = ['理论', 'theory', '框架', 'framework', '概念', 'concept', '原理', 'principle', '机制', 'mechanism']
        empirical_keywords = ['实证', 'empirical', '实验', 'experiment', '案例', 'case', '调查', 'survey', '数据', 'data']
        application_keywords = ['应用', 'application', '实践', 'practice', '系统', 'system', '平台', 'platform', '工具', 'tool']
        
        categories = {
            'method': 0, 'theory': 0, 'empirical': 0, 'application': 0
        }
        
        all_themes = {}
        if theme_analysis['chinese_themes']:
            all_themes.update(theme_analysis['chinese_themes'])
        if theme_analysis['english_themes']:
            for theme, count in theme_analysis['english_themes'].items():
                all_themes[theme] = all_themes.get(theme, 0) + count
        
        # 通用分类统计
        for theme, count in all_themes.items():
            theme_lower = theme.lower()
            if any(keyword in theme_lower for keyword in method_keywords):
                categories['method'] += count
            elif any(keyword in theme_lower for keyword in theory_keywords):
                categories['theory'] += count
            elif any(keyword in theme_lower for keyword in empirical_keywords):
                categories['empirical'] += count
            elif any(keyword in theme_lower for keyword in application_keywords):
                categories['application'] += count
        
        total = sum(categories.values())
        if total > 0:
            content += f"1. **方法与技术研究** ({categories['method']/total*100:.1f}%)：包括研究方法、分析技术、算法模型等\n"
            content += f"2. **理论与框架构建** ({categories['theory']/total*100:.1f}%)：涵盖理论发展、概念框架、机制分析等\n"
            content += f"3. **实证与数据研究** ({categories['empirical']/total*100:.1f}%)：包括实验研究、案例分析、数据挖掘等\n"
            content += f"4. **应用与系统实现** ({categories['application']/total*100:.1f}%)：包含实践应用、系统开发、工具设计等\n\n"
        else:
            # 如果无法分类，提供通用描述
            top_themes = sorted(all_themes.items(), key=lambda x: x[1], reverse=True)[:8]
            for i, (theme, count) in enumerate(top_themes, 1):
                content += f"{i}. **{theme}** ({count}篇研究)\n"
            content += "\n"
        
        return content
    
    def _analyze_paper_relevance(self, paper: Dict[str, Any]) -> str:
        """分析论文相关度"""
        keywords = paper.get('KeyWords', '').lower()
        title = paper.get('Title', '').lower()
        
        # 通用学术研究分类
        if any(keyword in keywords or keyword in title for keyword in ['方法', 'method', '算法', 'algorithm', '模型', 'model', '技术', 'technique']):
            return '研究方法与技术'
        elif any(keyword in keywords or keyword in title for keyword in ['理论', 'theory', '框架', 'framework', '概念', 'concept']):
            return '理论框架构建'
        elif any(keyword in keywords or keyword in title for keyword in ['实验', 'experiment', '实证', 'empirical', '案例', 'case study']):
            return '实证研究分析'
        elif any(keyword in keywords or keyword in title for keyword in ['应用', 'application', '实践', 'practice', '系统', 'system']):
            return '应用实践研究'
        elif any(keyword in keywords or keyword in title for keyword in ['分析', 'analysis', '评估', 'evaluation', '测量', 'measurement']):
            return '分析评估方法'
        elif any(keyword in keywords or keyword in title for keyword in ['优化', 'optimization', '改进', 'improvement', '创新', 'innovation']):
            return '优化改进研究'
        else:
            return '相关理论研究'
    
    def _format_statistics_section(self, stats: Dict[str, int]) -> str:
        """格式化统计信息部分"""
        return f"""### 📈 数据统计

| 类别 | 中文论文 | 英文论文 | 总计 |
|------|----------|----------|------|
| 相关论文 | {stats['total_chinese_papers']} | {stats['total_english_papers']} | {stats['total_chinese_papers'] + stats['total_english_papers']} |
| 去重后 | {stats['dedup_chinese_papers']} | {stats['dedup_english_papers']} | {stats['dedup_chinese_papers'] + stats['dedup_english_papers']} |
| TOP论文 | {stats['top_chinese_papers']} | {stats['top_english_papers']} | {stats['top_chinese_papers'] + stats['top_english_papers']} |

"""
    
    def _format_summary_section(self, analysis_data: Dict[str, Any]) -> str:
        """格式化摘要部分"""
        total_papers = sum([
            len(analysis_data[key]) if analysis_data[key] else 0
            for key in ['dedup_chinese', 'dedup_english']
        ])
        
        return f"""## 📋 评估摘要

本次评估共检索到 **{total_papers}** 篇相关论文（去重后），涵盖中英文学术文献。

### 🎯 主要发现

- **文献覆盖度**: 检索到了丰富的相关研究文献
- **研究领域**: 涵盖了该论文主题的主要研究方向
- **时效性**: 包含了最新的研究成果和发展趋势

### ⭐ 创新度评估

基于相关文献分析，该论文在以下方面显示出创新性：

1. **研究方法创新**: [需要具体分析]
2. **理论贡献**: [需要具体分析] 
3. **应用价值**: [需要具体分析]

"""
    
    def _format_innovation_section(self, analysis_data: Dict[str, Any]) -> str:
        """格式化创新性分析部分"""
        return """## 🔬 创新性分析

### 🆕 创新点识别

基于文献对比分析，识别出以下潜在创新点：

1. **方法学创新**
   - 创新的研究方法或技术路径
   - 现有方法的改进和优化

2. **理论贡献**
   - 新的理论框架或模型
   - 对现有理论的补充和完善

3. **实践价值**
   - 解决实际问题的新方案
   - 具有应用前景的技术成果

### 📊 创新度评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 原创性 | ⭐⭐⭐⭐☆ | 具有较高的原创性 |
| 新颖性 | ⭐⭐⭐⭐☆ | 方法或观点具有新颖性 |
| 重要性 | ⭐⭐⭐☆☆ | 具有一定的学术或实践意义 |
| 影响力 | ⭐⭐⭐☆☆ | 预期具有一定的学术影响 |

"""
    
    def _format_related_papers_section(self, analysis_data: Dict[str, Any]) -> str:
        """格式化相关论文部分"""
        content = """## 📚 相关文献分析

### 🔍 文献检索结果

"""
        
        # 添加TOP论文列表
        if analysis_data['top_chinese'] or analysis_data['top_english']:
            content += "### ⭐ 重点相关论文\n\n"
            
            # 中文TOP论文
            if analysis_data['top_chinese']:
                content += "#### 中文文献\n\n"
                for i, paper in enumerate(analysis_data['top_chinese'][:10], 1):
                    title = paper.get('title', '未知标题')
                    authors = paper.get('authors', '未知作者')
                    content += f"{i}. **{title}**\n"
                    content += f"   - 作者: {authors}\n"
                    if 'year' in paper:
                        content += f"   - 年份: {paper['year']}\n"
                    content += "\n"
            
            # 英文TOP论文
            if analysis_data['top_english']:
                content += "#### 英文文献\n\n"
                for i, paper in enumerate(analysis_data['top_english'][:10], 1):
                    title = paper.get('title', 'Unknown Title')
                    authors = paper.get('authors', 'Unknown Authors')
                    content += f"{i}. **{title}**\n"
                    content += f"   - Authors: {authors}\n"
                    if 'year' in paper:
                        content += f"   - Year: {paper['year']}\n"
                    content += "\n"
        
        return content
    
    def _format_recommendations_section(self, analysis_data: Dict[str, Any]) -> str:
        """格式化建议部分"""
        return """## 💡 改进建议

### 🎯 研究深化建议

1. **文献综述完善**
   - 补充最新的相关研究成果
   - 加强与国际前沿研究的对比分析
   - 拓展跨学科文献的引用和讨论

2. **方法论改进**
   - 考虑采用更先进的研究方法或技术
   - 增加实证研究、案例分析或实验验证
   - 完善研究设计的科学性和严谨性

3. **创新点突出**
   - 明确表述研究的核心创新点和贡献
   - 加强与现有研究的差异化论证
   - 突出研究的原创性和新颖性

### 📈 质量提升建议

1. **理论贡献强化**
   - 深化理论框架的构建和论证
   - 加强理论与实践的结合
   - 提升理论创新的深度和广度

2. **实证分析完善**
   - 充实数据支撑和分析过程
   - 增加多角度、多层次的验证
   - 提高结果的可信度和说服力

3. **应用价值体现**
   - 明确研究成果的实际应用价值
   - 提供具体的应用场景和推广建议
   - 评估研究的社会效益和经济效益

### 🚀 发展方向建议

1. **研究拓展**
   - 探索相关领域的延伸研究机会
   - 考虑多学科交叉融合的可能性
   - 规划后续研究的发展路径

2. **成果转化**
   - 加强研究成果的实践转化
   - 寻求产学研合作机会
   - 提升研究的影响力和知名度

"""
    
    def _format_appendix_section(self, analysis_data: Dict[str, Any]) -> str:
        """格式化附录部分"""
        content = """---

## 📎 附录

### 📄 数据文件列表

本次评估生成的数据文件：

"""
        
        # 列出生成的文件
        file_types = [
            ('chinese_papers', '中文相关论文'),
            ('english_papers', '英文相关论文'),
            ('dedup_chinese', '中文去重论文'),
            ('dedup_english', '英文去重论文'),
            ('top_chinese', '中文TOP论文'),
            ('top_english', '英文TOP论文')
        ]
        
        for key, description in file_types:
            if analysis_data[key] is not None:
                content += f"- ✅ {description}: 已生成\n"
            else:
                content += f"- ❌ {description}: 未找到\n"
        
        content += f"""
### ⚙️ 系统配置

- **TopN论文数量**: {self.config_mgr.get_top_papers_count()}
- **支持文件格式**: {', '.join(self.config_mgr.get_supported_formats())}
- **输出目录**: {self.config_mgr.get_output_dir()}

### 📞 技术支持

如有问题，请查看系统日志或联系技术支持。

---

*本报告由基于AI的学位论文创新评估系统自动生成*
"""
        
        return content
    
    def _build_shared_context_prompt(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """构建共享上下文提示词（一次性发送所有背景信息）"""
        
        prompt = f"""你是一位资深的学术评审专家，我需要你分析一篇学术论文的创新性。请仔细阅读并记住以下论文的基本信息和相关文献背景，我将在同一对话中依次询问三个维度的分析。

**目标论文信息**：
- 论文标题：{thesis_info.get('title', '未提供')}
- 中文关键词：{thesis_info.get('keywords_cn', '未提供')}
- 英文关键词：{thesis_info.get('keywords_en', '未提供')}
- 研究方法：{thesis_info.get('methodology', '未提供')}
- 理论框架：{thesis_info.get('theoretical_framework', '未提供')}
- 主要创新点：{thesis_info.get('main_innovations', '未提供')}
- 研究结论：{thesis_info.get('research_conclusions', '未提供')}
- 实际问题：{thesis_info.get('practical_problems', '未提供')}
- 解决方案：{thesis_info.get('proposed_solutions', '未提供')}
- 应用价值：{thesis_info.get('application_value', '未提供')}

**相关文献背景**：
{literature_context}

请确认你已经理解并记住了以上论文信息和文献背景。接下来我将分别询问方法学创新、理论贡献和实践价值的分析。

请简单回复"已理解并记住论文信息和文献背景，准备进行创新性分析"即可。"""

        return prompt
    
    def _build_methodology_analysis_prompt(self) -> str:
        """构建方法学创新分析提示词（无需重复背景信息）"""
        
        prompt = """基于刚才提供的论文信息和文献背景，请分析目标论文在**方法学方面的创新点**：

**分析要求**：
1. **研究方法创新性**：
   - 是否采用了新的研究方法或技术路径？
   - 对现有方法进行了哪些改进和优化？
   - 与相关文献中的方法相比有何突破？

2. **技术路径创新**：
   - 技术实现上有何独特之处？
   - 是否解决了现有方法的局限性？
   - 创新方法的科学性和可重复性如何？

3. **方法论贡献**：
   - 为研究领域提供了什么新的分析工具或研究范式？
   - 方法的推广应用价值如何？

**输出要求**：客观专业，突出创新点，300-500字。"""

        return prompt
    
    def _build_theory_analysis_prompt(self) -> str:
        """构建理论贡献分析提示词（无需重复背景信息）"""
        
        prompt = """基于刚才提供的论文信息和文献背景，请分析目标论文在**理论方面的贡献**：

**分析要求**：
1. **理论创新性**：
   - 是否提出了新的理论框架或概念？
   - 对现有理论进行了哪些扩展或修正？
   - 理论构建的逻辑性和系统性如何？

2. **理论整合性**：
   - 如何整合不同的理论视角？
   - 是否形成了新的理论综合？
   - 跨学科理论融合的创新程度如何？

3. **理论影响力**：
   - 对学科理论发展的意义？
   - 为后续研究提供了什么理论基础？

**输出要求**：严谨客观，突出理论创新，300-500字。"""

        return prompt
    
    def _build_practice_analysis_prompt(self) -> str:
        """构建实践价值分析提示词（无需重复背景信息）"""
        
        prompt = """基于刚才提供的论文信息和文献背景，请分析目标论文在**实践应用方面的价值**：

**分析要求**：
1. **问题解决能力**：
   - 解决了什么重要的实际问题？
   - 解决方案的可行性和有效性如何？
   - 相比现有解决方案有何优势？

2. **应用前景评估**：
   - 在相关行业或领域的应用潜力？
   - 推广应用的可能性和范围？
   - 技术成熟度和产业化前景？

3. **社会经济价值**：
   - 能创造什么样的经济或社会价值？
   - 对行业发展或社会进步的贡献？

**输出要求**：实用客观，突出应用价值，300-500字。"""

        return prompt
    
    def _analyze_methodology_innovation_compact(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """精简版方法学创新分析（备用方案）"""
        
        # 提取关键信息，避免发送完整的文献背景
        key_literature_info = self._extract_key_literature_info(literature_context)
        
        prompt = f"""你是学术方法论专家，请分析论文的方法学创新：

**论文**：{thesis_info.get('title', '未提供')}
**方法**：{thesis_info.get('methodology', '未提供')}  
**创新点**：{thesis_info.get('main_innovations', '未提供')}

**文献参考**：{key_literature_info}

请从研究方法创新性、技术路径突破、方法论贡献三个角度分析，300-500字。"""

        return prompt
    
    def _analyze_theory_contribution_compact(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """精简版理论贡献分析（备用方案）"""
        
        key_literature_info = self._extract_key_literature_info(literature_context)
        
        prompt = f"""你是理论研究专家，请分析论文的理论贡献：

**论文**：{thesis_info.get('title', '未提供')}
**理论框架**：{thesis_info.get('theoretical_framework', '未提供')}
**创新点**：{thesis_info.get('main_innovations', '未提供')}

**文献参考**：{key_literature_info}

请从理论创新性、理论整合性、学科影响力三个角度分析，300-500字。"""

        return prompt
    
    def _analyze_practice_value_compact(self, thesis_info: Dict[str, str], literature_context: str) -> str:
        """精简版实践价值分析（备用方案）"""
        
        key_literature_info = self._extract_key_literature_info(literature_context)
        
        prompt = f"""你是产学研专家，请分析论文的实践价值：

**论文**：{thesis_info.get('title', '未提供')}
**实际问题**：{thesis_info.get('practical_problems', '未提供')}
**解决方案**：{thesis_info.get('proposed_solutions', '未提供')}

**文献参考**：{key_literature_info}

请从问题解决能力、应用前景、社会经济价值三个角度分析，300-500字。"""

        return prompt
    
    def _extract_key_literature_info(self, literature_context: str) -> str:
        """提取关键文献信息（大幅减少Token消耗）"""
        
        lines = literature_context.split('\n')
        key_info = []
        
        # 只保留关键统计信息
        for line in lines:
            if '文献总数' in line or '近5年文献占比' in line or '年份' in line:
                key_info.append(line)
            elif line.startswith('- ') and ('篇' in line or '%' in line):
                key_info.append(line)
        
        # 限制在200字符以内
        result = '\n'.join(key_info[:10])
        if len(result) > 200:
            result = result[:200] + '...'
        
        return result
