#!/usr/bin/env python3
"""
基于缓存数据的论文评估模块
利用缓存的结构化论文信息JSON和CNKI文献搜索结果进行高效评估
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class CachedEvaluator:
    """基于缓存数据的论文评估器"""
    
    def __init__(self, config_manager):
        """
        初始化评估器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_mgr = config_manager
        self.output_dir = Path(self.config_mgr.get_output_dir())
        
    def evaluate_with_cache(self, file_path: str, ai_client, session_id: Optional[str] = None,
                           force_search: bool = False, force_extract: bool = False,
                           output_format: str = 'markdown') -> Dict:
        """
        使用缓存数据进行论文评估
        
        Args:
            file_path: 论文文件路径
            ai_client: AI客户端实例
            session_id: 会话ID
            force_search: 是否强制重新搜索
            force_extract: 是否强制重新提取
            output_format: 输出格式
            
        Returns:
            评估结果字典
        """
        try:
            input_path = Path(file_path)
            base_name = input_path.stem
            
            logger.info(f"开始基于缓存的论文评估: {file_path}")
            
            # 1. 加载缓存的结构化信息
            thesis_info = self._load_cached_thesis_info(base_name, force_extract)
            if not thesis_info and not force_extract:
                return {
                    'success': False,
                    'error': '未找到缓存的论文结构化信息，请先运行extract命令',
                    'suggestions': [
                        f'运行: uv run thesis-eval extract "{file_path}" --extraction-mode auto',
                        '或使用 --force-extract 参数强制重新提取'
                    ]
                }
            
            # 2. 加载缓存的文献搜索结果
            search_results = self._load_cached_search_results(base_name, force_search)
            
            # 3. 如果需要，执行缺失的步骤
            if not thesis_info:
                logger.info("执行论文信息提取...")
                thesis_info = self._extract_thesis_info(file_path, ai_client, session_id)
                if not thesis_info:
                    return {'success': False, 'error': '论文信息提取失败'}
            
            if not search_results and not force_search:
                logger.info("执行文献搜索...")
                search_results = self._perform_literature_search(thesis_info, ai_client, session_id, base_name)
            
            # 4. 生成评估报告
            report_result = self._generate_evaluation_report(
                thesis_info, search_results, base_name, output_format, ai_client, session_id
            )
            
            return {
                'success': True,
                'thesis_info': thesis_info,
                'search_results': search_results,
                'report_path': report_result.get('report_path'),
                'message': '评估完成'
            }
            
        except Exception as e:
            logger.error(f"缓存评估失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _load_cached_thesis_info(self, base_name: str, force_extract: bool = False) -> Optional[Dict]:
        """加载缓存的论文结构化信息 - 优先加载专家版"""
        if force_extract:
            return None
        
        # 优先查找专家版文件
        pro_info_file = self.output_dir / f"{base_name}_pro_extracted_info.json"
        standard_info_file = self.output_dir / f"{base_name}_extracted_info.json"
        
        # 按优先级尝试加载文件
        info_files = [
            (pro_info_file, "专家版"),
            (standard_info_file, "标准版")
        ]
        
        for info_file, file_type in info_files:
            if info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    extracted_info = data.get('extracted_info')
                    if extracted_info:
                        metadata = data.get('metadata', {})
                        extraction_time = metadata.get('extraction_time', '未知')
                        method = metadata.get('method', '未知')
                        
                        logger.info(f"✅ 加载缓存的{file_type}论文信息: {info_file}")
                        logger.info(f"   提取时间: {extraction_time}")
                        logger.info(f"   提取方法: {method}")
                        
                        # 验证必要字段 - 更新字段名称适配新格式
                        required_fields = ['title_cn', 'abstract_cn']
                        missing_fields = [f for f in required_fields if not extracted_info.get(f, '').strip()]
                        
                        if missing_fields:
                            logger.warning(f"缓存数据不完整，缺少字段: {missing_fields}")
                            # 如果是专家版文件不完整，尝试标准版
                            if file_type == "专家版":
                                continue
                            return None
                        
                        return extracted_info
                    else:
                        logger.warning(f"{file_type}缓存文件中没有有效的提取信息")
                        
                except Exception as e:
                    logger.error(f"读取{file_type}结构化信息缓存失败: {e}")
        
        logger.debug(f"未找到任何结构化信息缓存文件: {base_name}")
        return None
    
    def _load_cached_search_results(self, base_name: str, force_search: bool = False) -> Optional[Dict]:
        """加载缓存的文献搜索结果"""
        if force_search:
            return None
        
        search_results = {'papers_by_lang': {}, 'metadata': {}}
        found_any = False
        
        # 支持的语言
        languages = ['Chinese', 'English']
        
        for lang in languages:
            # 检查各种可能的TOP文献文件
            for top_count in [50, 30, 20]:
                papers_file = self.output_dir / f"{base_name}_TOP{top_count}PAPERS_{lang}.json"
                if papers_file.exists():
                    try:
                        with open(papers_file, 'r', encoding='utf-8') as f:
                            papers_data = json.load(f)
                            search_results['papers_by_lang'][lang] = papers_data
                            found_any = True
                            
                        logger.info(f"✅ 加载缓存的{lang}文献: {papers_file} ({len(papers_data)} 篇)")
                        break
                        
                    except Exception as e:
                        logger.warning(f"读取文献缓存失败 {papers_file}: {e}")
        
        # 加载文献元数据分析
        metadata_file = self.output_dir / f"{base_name}_literature_metadata_analysis.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_analysis = json.load(f)
                    search_results['metadata_analysis'] = metadata_analysis
                    logger.info(f"✅ 加载文献元数据分析: {metadata_file}")
            except Exception as e:
                logger.warning(f"读取文献元数据分析失败: {e}")
        
        if found_any:
            return search_results
        else:
            logger.debug("未找到缓存的文献搜索结果")
            return None
    
    def _extract_thesis_info(self, file_path: str, ai_client, session_id: Optional[str] = None) -> Optional[Dict]:
        """提取论文结构化信息"""
        try:
            from .extract_sections_with_ai import extract_from_cached_markdown
            
            logger.info("开始提取论文结构化信息...")
            
            # 使用新的缓存提取功能
            thesis_info = extract_from_cached_markdown(
                file_path, ai_client, session_id,
                extraction_mode='auto', use_cache=True
            )
            
            if thesis_info:
                logger.info("✅ 论文信息提取成功")
                return thesis_info
            else:
                logger.error("论文信息提取失败")
                return None
                
        except Exception as e:
            logger.error(f"提取论文信息时出错: {e}")
            return None
    
    def _perform_literature_search(self, thesis_info: Dict, ai_client, session_id: Optional[str], base_name: str) -> Optional[Dict]:
        """执行文献搜索"""
        try:
            from .cnki_client_pool import cnki_auto_search
            
            logger.info("开始执行文献搜索...")
            
            # 创建临时文件路径用于搜索
            temp_output = self.output_dir / f"{base_name}_temp.md"
            
            # 使用已有的论文信息进行搜索
            search_kwargs = {
                'languages': ['Chinese', 'English'],
                'session_id': session_id,
                'existing_thesis_info': thesis_info
            }
            
            # 由于我们已有论文信息，传递一个虚拟路径
            search_results = cnki_auto_search(
                str(temp_output),  # 这只是用于生成输出文件名
                str(temp_output),
                **search_kwargs
            )
            
            if search_results and search_results.get('papers_by_lang'):
                logger.info("✅ 文献搜索完成")
                for lang, papers in search_results['papers_by_lang'].items():
                    logger.info(f"   {lang}: {len(papers)} 篇文献")
                return search_results
            else:
                logger.warning("文献搜索未返回结果")
                return None
                
        except Exception as e:
            logger.error(f"文献搜索失败: {e}")
            return None
    
    def _generate_evaluation_report(self, thesis_info: Dict, search_results: Optional[Dict], 
                                  base_name: str, output_format: str, ai_client, 
                                  session_id: Optional[str] = None) -> Dict:
        """生成评估报告"""
        try:
            logger.info(f"开始生成{output_format}评估报告...")
            
            if output_format == 'markdown':
                return self._generate_markdown_report(thesis_info, search_results, base_name, ai_client, session_id)
            elif output_format == 'json':
                return self._generate_json_report(thesis_info, search_results, base_name)
            else:
                raise ValueError(f"不支持的输出格式: {output_format}")
                
        except Exception as e:
            logger.error(f"生成评估报告失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_markdown_report(self, thesis_info: Dict, search_results: Optional[Dict], 
                                base_name: str, ai_client, session_id: Optional[str] = None) -> Dict:
        """生成Markdown评估报告"""
        try:
            from .report_generator import MarkdownReportGenerator
            
            report_generator = MarkdownReportGenerator()
            
            # 准备数据
            papers_by_lang = search_results.get('papers_by_lang', {}) if search_results else {}
            literature_metadata_analysis = search_results.get('metadata_analysis') if search_results else None
            
            # 生成报告
            # 创建一个虚拟的输入文件路径用于报告生成
            dummy_input_path = str(self.output_dir / f"{base_name}.pdf")  # 虚拟路径
            
            report_path = report_generator.generate_evaluation_report(
                input_file=dummy_input_path,
                output_dir=str(self.output_dir),
                thesis_extracted_info=thesis_info,
                papers_by_lang=papers_by_lang,
                literature_metadata_analysis=literature_metadata_analysis
            )
            
            if report_path:
                logger.info(f"✅ Markdown报告生成成功: {report_path}")
                return {'success': True, 'report_path': report_path}
            else:
                return {'success': False, 'error': 'Markdown报告生成失败'}
                
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_json_report(self, thesis_info: Dict, search_results: Optional[Dict], base_name: str) -> Dict:
        """生成JSON评估报告"""
        try:
            report_data = {
                'metadata': {
                    'report_type': 'evaluation',
                    'generated_time': datetime.now().isoformat(),
                    'base_name': base_name
                },
                'thesis_info': thesis_info,
                'search_results': search_results or {},
                'evaluation_summary': {
                    'has_thesis_info': bool(thesis_info),
                    'has_search_results': bool(search_results),
                    'literature_count': sum(len(papers) for papers in search_results.get('papers_by_lang', {}).values()) if search_results else 0
                }
            }
            
            # 保存JSON报告
            report_file = self.output_dir / f"{base_name}_evaluation_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ JSON报告生成成功: {report_file}")
            return {'success': True, 'report_path': str(report_file)}
            
        except Exception as e:
            logger.error(f"生成JSON报告失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_cache_status(self, file_path: str) -> Dict:
        """获取指定文件的缓存状态"""
        input_path = Path(file_path)
        base_name = input_path.stem
        
        status = {
            'file_path': file_path,
            'base_name': base_name,
            'thesis_info_cached': False,
            'search_results_cached': False,
            'cache_files': []
        }
        
        # 检查论文信息缓存 - 优先检查专家版
        pro_thesis_info_file = self.output_dir / f"{base_name}_pro_extracted_info.json"
        standard_thesis_info_file = self.output_dir / f"{base_name}_extracted_info.json"
        
        if pro_thesis_info_file.exists():
            status['thesis_info_cached'] = True
            status['cache_files'].append({
                'type': 'thesis_info_pro',
                'path': str(pro_thesis_info_file),
                'size': pro_thesis_info_file.stat().st_size
            })
        elif standard_thesis_info_file.exists():
            status['thesis_info_cached'] = True
            status['cache_files'].append({
                'type': 'thesis_info_standard',
                'path': str(standard_thesis_info_file),
                'size': standard_thesis_info_file.stat().st_size
            })
        
        # 检查文献搜索缓存
        for lang in ['Chinese', 'English']:
            for top_count in [50, 30, 20]:
                papers_file = self.output_dir / f"{base_name}_TOP{top_count}PAPERS_{lang}.json"
                if papers_file.exists():
                    status['search_results_cached'] = True
                    status['cache_files'].append({
                        'type': f'search_results_{lang}',
                        'path': str(papers_file),
                        'size': papers_file.stat().st_size
                    })
                    break  # 只记录第一个找到的
        
        return status


def create_cached_evaluator(config_manager) -> CachedEvaluator:
    """创建缓存评估器实例"""
    return CachedEvaluator(config_manager)
