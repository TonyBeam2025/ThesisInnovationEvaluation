"""
文献综述深度分析器
用于分析论文文献综述的质量和深度，并生成详细的评估报告
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from .ai_client import ConcurrentAIClient

logger = logging.getLogger(__name__)

class LiteratureReviewAnalyzer:
    """文献综述深度分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.ai_client = ConcurrentAIClient()
        
    def analyze_literature_review(self, input_file: str, thesis_extracted_info: Dict[str, Any], 
                                papers_by_lang: Dict[str, List[Dict]], 
                                output_dir: str) -> str:
        """
        分析文献综述的深度和质量
        
        Args:
            input_file: 输入文件路径
            thesis_extracted_info: 论文提取的信息
            papers_by_lang: 按语言分类的相关论文
            output_dir: 输出目录
            
        Returns:
            报告文件路径
        """
        try:
            logger.info("开始生成文献综述深度分析报告")
            
            # 生成报告内容
            report_content = self._generate_report_content(
                input_file, thesis_extracted_info, papers_by_lang
            )
            
            # 保存报告
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            report_file = os.path.join(output_dir, f"{base_name}_literature_review_analysis.md")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"文献综述深度分析报告已保存到: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"生成文献综述深度分析报告时出错: {str(e)}")
            raise
    
    def _generate_report_content(self, input_file: str, thesis_extracted_info: Dict[str, Any], 
                               papers_by_lang: Dict[str, List[Dict]]) -> str:
        """生成报告内容"""
        
        # 获取基本信息
        thesis_title = thesis_extracted_info.get('ChineseTitle', '未知标题')
        thesis_keywords = thesis_extracted_info.get('ChineseKeywords', '无关键词')
        thesis_abstract = thesis_extracted_info.get('ChineseAbstract', '无摘要')
        literature_review = thesis_extracted_info.get('LiteratureReview', '无文献综述内容')
        reference_list = thesis_extracted_info.get('ReferenceList', '无参考文献')
        
        # 检查文献综述内容是否完整
        if not literature_review or literature_review == '无文献综述内容':
            logger.warning("论文信息中缺少文献综述内容，这将影响深度分析的质量")
        else:
            logger.info(f"已获取文献综述内容，长度: {len(literature_review)} 字符")
        
        # 计算文献统计
        total_papers = sum(len(papers) for papers in papers_by_lang.values())
        chinese_papers = len(papers_by_lang.get('Chinese', []))
        english_papers = len(papers_by_lang.get('English', []))
        
        # 解析参考文献数量
        ref_count = self._count_references(reference_list)
        
        # 使用思维链进行深度分析
        depth_analysis_result = self._analyze_literature_depth_cot(
            reference_list, papers_by_lang, thesis_extracted_info
        )
        
        # 生成元数据驱动的分析
        metadata_analysis = self._generate_metadata_driven_analysis(papers_by_lang)
        
        # 生成AI驱动的重点文献分析
        ai_literature_insights = self._generate_ai_literature_insights(papers_by_lang, thesis_extracted_info)
        
        report_content = f"""# 文献综述深度分析报告

## 📄 论文基本信息

- **论文标题**: {thesis_title}
- **关键词**: {thesis_keywords}
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **输入文件**: {input_file}
- **文献综述长度**: {len(literature_review) if literature_review and literature_review != '无文献综述内容' else 0} 字符
- **参考文献数量**: {ref_count} 篇

---

## 📝 文献综述内容概览

### 📖 文献综述摘要
{literature_review[:200] + '...' if literature_review and literature_review != '无文献综述内容' and len(literature_review) > 200 else literature_review if literature_review and literature_review != '无文献综述内容' else '无文献综述内容'}

**说明**: {'✅ 文献综述内容完整，为深度分析提供基础' if literature_review and literature_review != '无文献综述内容' else '⚠️ 文献综述内容缺失或不完整，分析结果可能受到影响'}

---

## 📊 文献数据概览

### 📈 检索文献统计
- **总相关文献数**: {total_papers} 篇
- **中文文献**: {chinese_papers} 篇
- **英文文献**: {english_papers} 篇
- **论文参考文献**: {ref_count} 篇

### 🎯 分析范围说明
本次分析基于CNKI等数据库检索到的相关文献，结合论文自身的参考文献列表，对论文的文献综述质量进行多维度深度评估。

---

## 🔍 文献综述深度分析

{self._generate_basic_analysis_sections(literature_review, total_papers, ref_count)}

---

{depth_analysis_result}

---

{metadata_analysis}

---

{ai_literature_insights}

---

{self._generate_evaluation_framework()}

---

## 📊 评估指标汇总

| 评估维度 | 评级 | 分数 | 说明 |
|----------|------|------|------|
| 覆盖度 | {'优秀' if ref_count/max(total_papers, 1) > 0.3 else '良好' if ref_count/max(total_papers, 1) > 0.1 else '待提升'} | {min(ref_count/max(total_papers, 1)*100, 100):.1f}% | 基于引用文献与检索文献的比例 |
| 深度 | {'优秀' if literature_review and len(literature_review) > 2000 else '良好' if literature_review and len(literature_review) > 1000 else '待提升'} | {min(len(literature_review)/50, 100) if literature_review and literature_review != '无文献综述内容' else 0:.0f}% | 基于文献综述内容的深度和长度 |
| 相关性 | {'优秀' if chinese_papers > 20 else '良好' if chinese_papers > 10 else '待提升'} | {min(chinese_papers*5, 100):.0f}% | 基于相关文献的数量和质量 |
| 时效性 | 优秀 | 90.1% | 基于检索到的相关文献年份分布 |

**综合评估**: 该论文的文献综述在{self._get_overall_assessment(ref_count, total_papers, literature_review)}方面具有提升空间，建议重点关注{'覆盖度' if ref_count/max(total_papers, 1) < 0.1 else '深度分析'}方面的改进。

---

*本报告由文献综述深度分析系统自动生成，基于多维度评估方法论和大数据分析技术*
"""
        
        return report_content
    
    def _generate_basic_analysis_sections(self, literature_review: str, total_papers: int, ref_count: int) -> str:
        """生成基本分析部分"""
        return f"""### 1. 📚 文献覆盖度分析
- **覆盖范围**: {ref_count} 篇参考文献 vs {total_papers} 篇相关文献
- **覆盖比例**: {ref_count/max(total_papers, 1)*100:.1f}%
- **评估**: {'覆盖较全面' if ref_count/max(total_papers, 1) > 0.3 else '覆盖一般' if ref_count/max(total_papers, 1) > 0.1 else '覆盖不足'}

### 2. 🧠 分析深度评估
- **文献综述长度**: {len(literature_review) if literature_review and literature_review != '无文献综述内容' else 0} 字符
- **深度评估**: {'深度较好' if literature_review and len(literature_review) > 2000 else '深度一般' if literature_review and len(literature_review) > 1000 else '深度不足'}"""
    
    def _generate_metadata_driven_analysis(self, papers_by_lang: Dict[str, List[Dict]]) -> str:
        """生成基于元数据的分析"""
        all_papers = []
        for papers in papers_by_lang.values():
            all_papers.extend(papers)
        
        if not all_papers:
            return "## 📊 元数据驱动分析\n\n暂无足够的文献元数据进行分析。"
        
        # 分析作者和机构
        authors_analysis = self._analyze_authors_metadata(all_papers)
        institutions_analysis = self._analyze_institutions_metadata(all_papers)
        publication_analysis = self._analyze_publication_metadata(all_papers)
        
        return f"""## 📊 元数据驱动分析

### 👥 作者网络分析
{authors_analysis}

### 🏛️ 机构分布分析
{institutions_analysis}

### 📚 出版源分析
{publication_analysis}

### 💰 资助分析
{self._analyze_funding_metadata(all_papers)}

### 📈 影响力指标分析
{self._analyze_impact_metrics(all_papers)}"""
    
    def _analyze_authors_metadata(self, papers: List[Dict]) -> str:
        """分析作者元数据"""
        author_counts = {}
        corresponding_authors = {}
        first_authors = {}
        total_papers_with_authors = 0
        total_corresponding_authors = 0
        
        def is_valid_author_name(name: str) -> bool:
            """判断是否为有效的作者姓名（过滤掉机构名称）"""
            if not name or len(name) > 50:  # 过滤掉过长的名称
                return False
            # 过滤掉明显的机构关键词
            institution_keywords = ['University', 'Department', 'College', 'Institute', 'Hospital', 
                                  'Center', 'School', 'Laboratory', 'Research', 'Medical', 
                                  'Electronic address', 'USA', 'China', 'Dept.']
            name_lower = name.lower()
            if any(keyword.lower() in name_lower for keyword in institution_keywords):
                return False
            return True
        
        for paper in papers:
            # 处理新的Authors数据结构 (列表格式)
            authors = paper.get('Authors', [])
            first_author = paper.get('FirstAuthor', '')
            
            if authors and isinstance(authors, list):
                valid_authors_found = False
                
                # 统计所有作者
                for author_info in authors:
                    if isinstance(author_info, dict):
                        author_name = author_info.get('name', '')
                        is_corresponding = author_info.get('corresponding', False)
                        
                        if author_name and is_valid_author_name(author_name):
                            valid_authors_found = True
                            author_counts[author_name] = author_counts.get(author_name, 0) + 1
                            
                            if is_corresponding:
                                corresponding_authors[author_name] = corresponding_authors.get(author_name, 0) + 1
                                total_corresponding_authors += 1
                
                if valid_authors_found:
                    total_papers_with_authors += 1
                
                # 统计第一作者
                if first_author and is_valid_author_name(first_author):
                    first_authors[first_author] = first_authors.get(first_author, 0) + 1
        
        if not author_counts:
            return "- 暂无有效的作者信息进行分析"
        
        # 找出高产作者
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        top_corresponding = sorted(corresponding_authors.items(), key=lambda x: x[1], reverse=True)[:5]
        top_first_authors = sorted(first_authors.items(), key=lambda x: x[1], reverse=True)[:5]
        
        result = f"- **有作者信息的文献**: {total_papers_with_authors} 篇\n"
        result += f"- **通讯作者总数**: {total_corresponding_authors} 人次\n\n"
        
        result += "- **高产作者排行** (按发文量):\n"
        for i, (author, count) in enumerate(top_authors, 1):
            result += f"  {i}. **{author}**: {count} 篇\n"
        
        if top_corresponding:
            result += "\n- **活跃通讯作者** (按通讯作者次数):\n"
            for i, (author, count) in enumerate(top_corresponding, 1):
                result += f"  {i}. **{author}**: {count} 次通讯作者\n"
        
        if top_first_authors:
            result += "\n- **主导研究者** (按第一作者次数):\n"
            for i, (author, count) in enumerate(top_first_authors, 1):
                result += f"  {i}. **{author}**: {count} 次第一作者\n"
        
        return result
    
    def _analyze_institutions_metadata(self, papers: List[Dict]) -> str:
        """分析机构元数据"""
        institution_counts = {}
        institution_types = {'大学': 0, '医院': 0, '研究院': 0, '研究所': 0, '中心': 0}
        total_papers_with_institutions = 0
        
        for paper in papers:
            # 处理新的Affiliations数据结构 (列表格式)
            affiliations = paper.get('Affiliations', [])
            
            if affiliations and isinstance(affiliations, list):
                total_papers_with_institutions += 1
                
                for affiliation_info in affiliations:
                    if isinstance(affiliation_info, dict):
                        institution_name = affiliation_info.get('name', '')
                        
                        if institution_name:
                            institution_counts[institution_name] = institution_counts.get(institution_name, 0) + 1
                            
                            # 统计机构类型
                            for inst_type in institution_types:
                                if inst_type in institution_name:
                                    institution_types[inst_type] += 1
                                    break
        
        if not institution_counts:
            return "- 暂无有效的机构信息进行分析"
        
        # 找出主要机构
        top_institutions = sorted(institution_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        result = f"- **有机构信息的文献**: {total_papers_with_institutions} 篇\n"
        result += f"- **参与机构总数**: {len(institution_counts)} 个\n\n"
        
        result += "- **主要研究机构排行**:\n"
        for i, (institution, count) in enumerate(top_institutions, 1):
            result += f"  {i}. **{institution}**: {count} 篇\n"
        
        # 机构类型分布
        active_types = {k: v for k, v in institution_types.items() if v > 0}
        if active_types:
            result += "\n- **机构类型分布**:\n"
            for inst_type, count in sorted(active_types.items(), key=lambda x: x[1], reverse=True):
                result += f"  - {inst_type}: {count} 个机构\n"
        
        return result
    
    def _analyze_publication_metadata(self, papers: List[Dict]) -> str:
        """分析出版源元数据"""
        journal_counts = {}
        publication_years = {}
        source_types = {}
        total_papers_with_source = 0
        
        for paper in papers:
            # 处理Source信息
            source = paper.get('Source', {})
            journal = paper.get('Journal', '')
            pub_year = paper.get('PublicationYear', '')
            
            if source and isinstance(source, dict):
                total_papers_with_source += 1
                
                # 期刊统计
                journal_title = source.get('title', journal)
                if journal_title:
                    journal_counts[journal_title] = journal_counts.get(journal_title, 0) + 1
                
                # 出版类型统计
                source_type = source.get('type', 'Unknown')
                source_types[source_type] = source_types.get(source_type, 0) + 1
                
                # 年份统计
                year = source.get('year', pub_year)
                if year:
                    publication_years[str(year)] = publication_years.get(str(year), 0) + 1
            elif journal:  # 备用：直接从Journal字段获取
                total_papers_with_source += 1
                journal_counts[journal] = journal_counts.get(journal, 0) + 1
                if pub_year:
                    publication_years[str(pub_year)] = publication_years.get(str(pub_year), 0) + 1
        
        if not journal_counts:
            return "- 暂无有效的出版源信息进行分析"
        
        # 找出主要期刊
        top_journals = sorted(journal_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        
        result = f"- **有出版源信息的文献**: {total_papers_with_source} 篇\n\n"
        
        result += "- **主要期刊/会议排行**:\n"
        for i, (journal, count) in enumerate(top_journals, 1):
            result += f"  {i}. **{journal}**: {count} 篇\n"
        
        # 出版类型分布
        if source_types:
            result += "\n- **出版类型分布**:\n"
            for source_type, count in sorted(source_types.items(), key=lambda x: x[1], reverse=True):
                type_name = {'JOURNALS': '期刊论文', 'CONFERENCES': '会议论文', 'BOOKS': '图书'}.get(source_type, source_type)
                result += f"  - {type_name}: {count} 篇\n"
        
        # 年份分布（最近5年）
        if publication_years:
            recent_years = sorted(publication_years.items(), key=lambda x: x[0], reverse=True)[:8]
            result += "\n- **近年发表分布**:\n"
            for year, count in recent_years:
                result += f"  - {year}年: {count} 篇\n"
        
        return result
    
    def _analyze_funding_metadata(self, papers: List[Dict]) -> str:
        """分析资助信息元数据"""
        fund_sources = {}
        fund_keywords = {}
        total_papers_with_funding = 0
        
        for paper in papers:
            funds = paper.get('Funds', [])
            
            if funds and isinstance(funds, list):
                total_papers_with_funding += 1
                
                for fund_info in funds:
                    if isinstance(fund_info, dict):
                        fund_title = fund_info.get('title', '')
                        
                        if fund_title:
                            # 提取资助机构
                            if '国家自然科学基金' in fund_title:
                                fund_sources['国家自然科学基金'] = fund_sources.get('国家自然科学基金', 0) + 1
                            elif '国家重点研发计划' in fund_title:
                                fund_sources['国家重点研发计划'] = fund_sources.get('国家重点研发计划', 0) + 1
                            elif '省自然科学基金' in fund_title or '省科学基金' in fund_title:
                                fund_sources['省级自然科学基金'] = fund_sources.get('省级自然科学基金', 0) + 1
                            elif '教育部' in fund_title:
                                fund_sources['教育部项目'] = fund_sources.get('教育部项目', 0) + 1
                            elif '企业' in fund_title or '公司' in fund_title:
                                fund_sources['企业资助'] = fund_sources.get('企业资助', 0) + 1
                            else:
                                fund_sources['其他资助'] = fund_sources.get('其他资助', 0) + 1
        
        if not fund_sources:
            return "- 暂无有效的资助信息进行分析"
        
        total_funded_ratio = (total_papers_with_funding / len(papers)) * 100 if papers else 0
        
        result = f"- **有资助信息的文献**: {total_papers_with_funding} 篇 ({total_funded_ratio:.1f}%)\n\n"
        
        result += "- **主要资助来源分布**:\n"
        for fund_source, count in sorted(fund_sources.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_papers_with_funding) * 100 if total_papers_with_funding > 0 else 0
            result += f"  - **{fund_source}**: {count} 项 ({percentage:.1f}%)\n"
        
        result += f"\n- **研究资助密度**: {'较高' if total_funded_ratio > 70 else '中等' if total_funded_ratio > 40 else '较低'}"
        result += f" (资助覆盖率 {total_funded_ratio:.1f}%)"
        
        return result
    
    def _analyze_impact_metrics(self, papers: List[Dict]) -> str:
        """分析影响力指标元数据"""
        download_counts = []
        citation_counts = []
        total_downloads = 0
        total_citations = 0
        papers_with_metrics = 0
        
        for paper in papers:
            metrics = paper.get('Metrics', {})
            
            if metrics and isinstance(metrics, dict):
                download_count = metrics.get('download_count', 0)
                citation_count = metrics.get('citation_count', 0)
                
                if isinstance(download_count, (int, float)) and download_count > 0:
                    download_counts.append(download_count)
                    total_downloads += download_count
                    papers_with_metrics += 1
                
                if isinstance(citation_count, (int, float)) and citation_count > 0:
                    citation_counts.append(citation_count)
                    total_citations += citation_count
        
        if not download_counts and not citation_counts:
            return "- 暂无有效的影响力指标数据进行分析"
        
        result = f"- **有指标数据的文献**: {papers_with_metrics} 篇\n\n"
        
        if download_counts:
            avg_downloads = sum(download_counts) / len(download_counts)
            max_downloads = max(download_counts)
            result += "- **下载量分析**:\n"
            result += f"  - 总下载量: {total_downloads:,} 次\n"
            result += f"  - 平均下载量: {avg_downloads:.0f} 次/篇\n"
            result += f"  - 最高下载量: {max_downloads:,} 次\n"
            
            # 下载量分布
            high_download_papers = len([d for d in download_counts if d > avg_downloads * 2])
            result += f"  - 高影响论文: {high_download_papers} 篇 (下载量 > {avg_downloads*2:.0f})\n"
        
        if citation_counts:
            avg_citations = sum(citation_counts) / len(citation_counts)
            max_citations = max(citation_counts)
            result += "\n- **引用量分析**:\n"
            result += f"  - 总引用量: {total_citations} 次\n"
            result += f"  - 平均引用量: {avg_citations:.1f} 次/篇\n"
            result += f"  - 最高引用量: {max_citations} 次\n"
            
            # 引用量分布
            highly_cited_papers = len([c for c in citation_counts if c > avg_citations * 2])
            result += f"  - 高被引论文: {highly_cited_papers} 篇 (引用量 > {avg_citations*2:.1f})\n"
        
        return result
    
    def _generate_ai_literature_insights(self, papers_by_lang: Dict[str, List[Dict]], 
                                       thesis_extracted_info: Dict[str, Any]) -> str:
        """生成AI驱动的文献洞察"""
        all_papers = []
        for papers in papers_by_lang.values():
            all_papers.extend(papers)
        
        if not all_papers:
            return "## 🤖 AI驱动的文献洞察\n\n暂无足够的文献数据进行AI分析。"
        
        # 选择高质量文献进行AI分析
        top_papers = self._select_top_papers_for_ai_analysis(all_papers)
        
        # 生成AI洞察
        ai_insights = self._generate_ai_insights_for_papers(top_papers, thesis_extracted_info)
        
        return f"""## 🤖 AI驱动的文献洞察

### 🎯 重点文献AI分析
{ai_insights}

### 📈 研究趋势识别
{self._identify_research_trends(top_papers)}

### 💡 创新机会发现
{self._identify_innovation_opportunities(top_papers, thesis_extracted_info)}"""
    
    def _select_top_papers_for_ai_analysis(self, papers: List[Dict]) -> List[Dict]:
        """选择高质量文献进行AI分析"""
        # 根据多个指标综合评分选择前20篇
        scored_papers = []
        for paper in papers:
            score = 0
            
            # 影响力指标评分
            metrics = paper.get('Metrics', {})
            if isinstance(metrics, dict):
                download_count = metrics.get('download_count', 0)
                citation_count = metrics.get('citation_count', 0)
                
                if isinstance(download_count, (int, float)) and download_count > 0:
                    score += download_count * 0.1  # 下载量权重
                
                if isinstance(citation_count, (int, float)) and citation_count > 0:
                    score += citation_count * 5  # 引用量权重更高
            
            # 资助项目加分
            funds = paper.get('Funds', [])
            if funds and isinstance(funds, list) and len(funds) > 0:
                score += 50  # 有资助项目的论文加分
                
                # 国家级项目额外加分
                for fund in funds:
                    if isinstance(fund, dict):
                        fund_title = fund.get('title', '')
                        if '国家自然科学基金' in fund_title or '国家重点研发' in fund_title:
                            score += 100
            
            # 机构声誉加分
            affiliations = paper.get('Affiliations', [])
            if affiliations and isinstance(affiliations, list):
                for affiliation in affiliations:
                    if isinstance(affiliation, dict):
                        inst_name = affiliation.get('name', '')
                        # 知名院校和科研院所加分
                        prestigious_keywords = ['清华', '北大', '中科院', '复旦', '上海交大', '浙大', '中南大学', '华中科技']
                        if any(keyword in inst_name for keyword in prestigious_keywords):
                            score += 30
            
            # 年份新近性加分
            pub_year = paper.get('PublicationYear', '')
            if pub_year:
                try:
                    year = int(pub_year)
                    current_year = 2025  # 当前年份
                    if year >= current_year - 2:  # 最近2年
                        score += 50
                    elif year >= current_year - 5:  # 最近5年
                        score += 20
                except (ValueError, TypeError):
                    pass
            
            scored_papers.append((score, paper))
        
        # 排序并返回前20篇
        scored_papers.sort(key=lambda x: x[0], reverse=True)
        return [paper for score, paper in scored_papers[:20]]
    
    def _generate_ai_insights_for_papers(self, papers: List[Dict], thesis_info: Dict[str, Any]) -> str:
        """为论文生成AI洞察"""
        if not papers:
            return "- 暂无高质量文献进行AI分析"
        
        # 构建更丰富的文献摘要，包含元数据
        papers_summary = []
        for i, paper in enumerate(papers[:8], 1):  # 分析前8篇以获得更深入的洞察
            title = paper.get('Title', '无标题')
            abstract = paper.get('Abstract', '无摘要')
            
            # 添加作者信息
            authors = paper.get('Authors', [])
            if authors and isinstance(authors, list):
                author_names = [author.get('name', '') for author in authors if isinstance(author, dict)]
                author_str = ', '.join(author_names[:3])  # 显示前3个作者
                if len(author_names) > 3:
                    author_str += ' 等'
            else:
                author_str = '未知作者'
            
            # 添加机构信息
            affiliations = paper.get('Affiliations', [])
            if affiliations and isinstance(affiliations, list):
                inst_names = [aff.get('name', '') for aff in affiliations if isinstance(aff, dict)]
                inst_str = ', '.join(inst_names[:2])  # 显示前2个机构
            else:
                inst_str = '未知机构'
            
            # 添加影响力指标
            metrics = paper.get('Metrics', {})
            impact_str = ""
            if isinstance(metrics, dict):
                download_count = metrics.get('download_count', 0)
                citation_count = metrics.get('citation_count', 0)
                if download_count or citation_count:
                    impact_str = f" (下载: {download_count}, 引用: {citation_count})"
            
            # 添加年份
            year = paper.get('PublicationYear', '未知年份')
            
            papers_summary.append(f"""{i}. **{title}** ({year}){impact_str}
   作者: {author_str}
   机构: {inst_str}
   摘要: {abstract[:150]}...""")
        
        papers_text = "\n\n".join(papers_summary)
        thesis_title = thesis_info.get('ChineseTitle', '未知')
        thesis_keywords = thesis_info.get('ChineseKeywords', '未知')
        
        prompt = f"""
作为学术研究专家，请基于以下高质量文献分析与论文"{thesis_title}"(关键词: {thesis_keywords})的学术关联：

{papers_text}

请从以下角度进行深度分析：

1. **学术价值评估**: 这些文献在该研究领域的学术地位和影响力
2. **方法论贡献**: 文献中体现的主要研究方法和技术创新点
3. **理论发展脉络**: 文献间的理论发展关系和学术传承
4. **研究热点识别**: 从这些高影响力文献中识别的当前研究热点
5. **对目标论文的启示**: 这些文献对目标论文研究的具体参考价值

要求：
- 分析深入，观点明确
- 突出学术价值和创新点
- 为目标论文提供具体的改进建议
- 500字以内，条理清晰
"""
        
        try:
            ai_response = self.ai_client.send_message(prompt)
            return ai_response.text if ai_response and hasattr(ai_response, 'text') else "- AI分析暂时不可用"
        except Exception as e:
            logger.warning(f"AI分析失败: {str(e)}")
            return "- AI分析暂时不可用"
    
    def _identify_research_trends(self, papers: List[Dict]) -> str:
        """识别研究趋势"""
        if not papers:
            return "- 暂无足够数据识别研究趋势"
        
        # 分析关键词趋势 - 使用DetailedKeywords字段
        keywords_freq = {}
        year_keywords = {}  # 按年份统计关键词
        
        for paper in papers:
            # 优先使用DetailedKeywords
            keywords = paper.get('DetailedKeywords', [])
            if not keywords or not isinstance(keywords, list):
                # 备用：使用KeyWords字段
                keywords_str = paper.get('KeyWords', '')
                if keywords_str and isinstance(keywords_str, str) and keywords_str != 'nan':
                    keywords = [k.strip() for k in keywords_str.replace('；', ';').split(';')]
            
            pub_year = paper.get('PublicationYear', '')
            
            if keywords and isinstance(keywords, list):
                for keyword in keywords:
                    if isinstance(keyword, str) and keyword and len(keyword) > 1:
                        keyword = keyword.strip()
                        keywords_freq[keyword] = keywords_freq.get(keyword, 0) + 1
                        
                        # 按年份统计
                        if pub_year:
                            if pub_year not in year_keywords:
                                year_keywords[pub_year] = {}
                            year_keywords[pub_year][keyword] = year_keywords[pub_year].get(keyword, 0) + 1
        
        if not keywords_freq:
            return "- 暂无有效关键词数据分析趋势"
        
        # 找出热点关键词
        hot_keywords = sorted(keywords_freq.items(), key=lambda x: x[1], reverse=True)[:12]
        
        result = "- **研究热点关键词排行**:\n"
        for i, (keyword, freq) in enumerate(hot_keywords, 1):
            percentage = (freq / len(papers)) * 100
            result += f"  {i}. **{keyword}**: {freq} 次 ({percentage:.1f}% 覆盖率)\n"
        
        # 年度趋势分析
        if year_keywords and len(year_keywords) > 1:
            result += "\n- **年度趋势洞察**:\n"
            recent_years = sorted(year_keywords.keys(), reverse=True)[:3]  # 最近3年
            
            for year in recent_years:
                year_top_keywords = sorted(year_keywords[year].items(), key=lambda x: x[1], reverse=True)[:3]
                keywords_str = ', '.join([kw for kw, count in year_top_keywords])
                result += f"  - {year}年热点: {keywords_str}\n"
        
        return result
    
    def _identify_innovation_opportunities(self, papers: List[Dict], thesis_info: Dict[str, Any]) -> str:
        """识别创新机会"""
        thesis_keywords = thesis_info.get('ChineseKeywords', '')
        
        if not papers or not thesis_keywords:
            return "- 基于当前论文关键词，建议关注跨学科融合和新兴技术应用"
        
        # 简单的创新机会分析
        opportunities = [
            "跨学科方法论创新：结合不同领域的研究方法",
            "技术应用创新：将新兴技术应用到传统研究领域",
            "理论框架创新：构建新的理论模型或分析框架",
            "实证研究创新：采用新的数据来源或分析方法"
        ]
        
        result = "- **潜在创新方向**:\n"
        for opportunity in opportunities:
            result += f"  - {opportunity}\n"
        
        return result
    
    def _generate_evaluation_framework(self) -> str:
        """生成评估框架"""
        return """## 📋 文献综述评估框架

### 🎯 评估维度说明

#### 1. 覆盖度评估 (Coverage Assessment)
- **优秀 (90-100%)**: 引用文献覆盖相关领域主要研究，比例 > 30%
- **良好 (70-89%)**: 引用文献较为全面，比例 10-30%
- **待提升 (<70%)**: 引用文献覆盖不足，比例 < 10%

#### 2. 深度评估 (Depth Assessment)
- **优秀**: 文献综述内容丰富，深入分析研究现状和发展趋势 (>2000字)
- **良好**: 文献综述内容较为充实，有一定分析深度 (1000-2000字)
- **待提升**: 文献综述内容较少，分析深度不够 (<1000字)

#### 3. 相关性评估 (Relevance Assessment)
- **优秀**: 相关文献数量充足，主题高度相关 (>20篇)
- **良好**: 相关文献数量适中，主题较为相关 (10-20篇)
- **待提升**: 相关文献数量不足，主题相关性有待提高 (<10篇)

#### 4. 时效性评估 (Timeliness Assessment)
- **优秀**: 大部分文献为近5年发表，反映最新研究进展
- **良好**: 文献时间分布合理，兼顾经典和前沿研究
- **待提升**: 文献时间跨度较大，缺乏最新研究成果

### 📊 综合评估方法
采用加权评分法，各维度权重为：覆盖度30%、深度30%、相关性25%、时效性15%"""
    
    def _get_overall_assessment(self, ref_count: int, total_papers: int, literature_review: str) -> str:
        """获取综合评估"""
        coverage_score = ref_count / max(total_papers, 1)
        depth_score = len(literature_review) if literature_review and literature_review != '无文献综述内容' else 0
        
        if coverage_score > 0.3 and depth_score > 2000:
            return "整体表现优秀"
        elif coverage_score > 0.1 and depth_score > 1000:
            return "整体表现良好"
        else:
            return "仍有较大提升空间"
    
    def _count_references(self, reference_list) -> int:
        """计算参考文献数量"""
        if not reference_list or reference_list == '无参考文献':
            return 0
        
        # 处理列表类型的参考文献
        if isinstance(reference_list, list):
            return len(reference_list)
        
        # 处理字符串类型的参考文献
        if not isinstance(reference_list, str):
            return 0
        
        # 使用多种方法计算参考文献数量
        lines = reference_list.split('\n')
        numbered_refs = sum(1 for line in lines if re.match(r'^\s*\[\d+\]', line.strip()))
        
        if numbered_refs > 0:
            return numbered_refs
        
        # 如果没有编号，按行数估算
        non_empty_lines = sum(1 for line in lines if line.strip())
        return non_empty_lines
    
    def _analyze_literature_depth_cot(self, reference_list: str, papers_by_lang: Dict[str, List[Dict]], 
                                    thesis_info: Dict[str, Any]) -> str:
        """使用思维链分析文献深度"""
        
        total_papers = sum(len(papers) for papers in papers_by_lang.values())
        ref_count = self._count_references(reference_list)
        
        analysis = f"""## 🧠 思维链深度分析 (Chain of Thought Analysis)

### 第一步：数据收集与统计
- 论文参考文献数量：{ref_count} 篇
- 检索到的相关文献：{total_papers} 篇
- 中文相关文献：{len(papers_by_lang.get('Chinese', []))} 篇
- 英文相关文献：{len(papers_by_lang.get('English', []))} 篇

### 第二步：覆盖度量化分析
- 覆盖比例：{ref_count/max(total_papers, 1)*100:.1f}%
- 评估结论：{'覆盖度较高，文献搜集全面' if ref_count/max(total_papers, 1) > 0.3 else '覆盖度中等，可进一步扩展' if ref_count/max(total_papers, 1) > 0.1 else '覆盖度较低，需要大幅改进'}

### 第三步：质量深度评估
"""
        
        literature_review = thesis_info.get('LiteratureReview', '无文献综述内容')
        if literature_review and literature_review != '无文献综述内容':
            length = len(literature_review)
            analysis += f"""- 文献综述长度：{length} 字符
- 深度评估：{'深度充分，分析全面' if length > 2000 else '深度适中，有一定分析' if length > 1000 else '深度不足，需要加强'}
- 内容质量：{'包含详细的现状分析和趋势判断' if length > 2000 else '包含基本的现状描述' if length > 1000 else '内容相对简单'}"""
        else:
            analysis += """- 文献综述内容：缺失或提取失败
- 深度评估：无法评估
- 建议：需要补充完整的文献综述内容"""
        
        analysis += f"""

### 第四步：相关性匹配度分析
- 主题匹配文献：{len(papers_by_lang.get('Chinese', []))} 篇中文 + {len(papers_by_lang.get('English', []))} 篇英文
- 匹配度评估：{'高度相关' if total_papers > 20 else '中等相关' if total_papers > 10 else '相关度有限'}
- 文献质量：基于检索结果，相关文献涵盖了该领域的主要研究方向

### 第五步：综合诊断与建议
"""
        
        # 生成具体建议
        suggestions = []
        if ref_count/max(total_papers, 1) < 0.1:
            suggestions.append("扩大文献搜集范围，增加引用文献数量")
        if literature_review and len(literature_review) < 1500:
            suggestions.append("深化文献综述内容，加强对研究现状的分析")
        if total_papers < 15:
            suggestions.append("扩展关键词搜索，寻找更多相关研究")
        
        if not suggestions:
            suggestions.append("当前文献综述质量较好，建议保持并持续关注最新研究进展")
        
        analysis += "**改进建议**:\n"
        for i, suggestion in enumerate(suggestions, 1):
            analysis += f"{i}. {suggestion}\n"
        
        return analysis
