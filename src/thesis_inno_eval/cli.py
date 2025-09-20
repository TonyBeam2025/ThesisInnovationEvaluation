#!/usr/bin/env python3
"""
论文评价系统命令行接口
支持并行处理多篇论文
"""

import click
from pathlib import Path
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 首先初始化日志配置
from .logging_config import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

from .config_manager import get_config_manager

def validate_file_format(file_path):
    """验证文件格式是否受支持"""
    config_mgr = get_config_manager()
    supported_formats = config_mgr.get_supported_formats()
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext not in supported_formats:
        if file_ext == '.pdf':
            raise click.BadParameter(f"暂不支持PDF格式文件。请使用Word文档(.docx)格式。")
        else:
            raise click.BadParameter(f"不支持的文件格式: {file_ext}。支持的格式: {', '.join(supported_formats)}")
    
    return True

def _detect_cached_search_results(base_name, output_dir):
    """检测并加载缓存的文献检索结果"""
    cached_results = {
        'papers_by_lang': {},
        'thesis_extracted_info': None,
        'literature_metadata_analysis': None
    }
    
    # 检测文献检索结果文件
    languages = ['Chinese', 'English']  # 支持的语言
    papers_found = False
    
    for lang in languages:
        # 检查TOP相关文献文件
        top_papers_file = output_dir / f"{base_name}_TOP30PAPERS_{lang}.json"
        if not top_papers_file.exists():
            top_papers_file = output_dir / f"{base_name}_TOP20PAPERS_{lang}.json"
        if not top_papers_file.exists():
            top_papers_file = output_dir / f"{base_name}_TOP50PAPERS_{lang}.json"
        
        if top_papers_file.exists():
            try:
                with open(top_papers_file, 'r', encoding='utf-8') as f:
                    papers_data = json.load(f)
                    cached_results['papers_by_lang'][lang] = papers_data
                    papers_found = True
            except Exception as e:
                click.echo(f"⚠️ 读取缓存文献文件失败 {top_papers_file}: {e}")
    
    return cached_results if papers_found else None

@click.group()
def cli():
    """论文创新度评价系统 - 使用AI和文献数据库分析论文创新性"""
    pass

@cli.command()
def info():
    """显示系统配置信息"""
    try:
        config_mgr = get_config_manager()
        
        # 获取模型配置
        openai_config = config_mgr.get_ai_model_config('openai')
        gemini_config = config_mgr.get_ai_model_config('gemini')
        
        click.echo("📋 系统配置信息:")
        click.echo(f"  🤖 OpenAI模型: {openai_config.get('model_name', 'N/A')}")
        click.echo(f"  🤖 OpenAI API Base: {openai_config.get('api_base', 'N/A')}")
        click.echo(f"  🤖 OpenAI max_tokens: {openai_config.get('max_tokens'):,}")
        click.echo(f"  🤖 Gemini模型: {gemini_config.get('model_name', 'N/A')}")
        click.echo(f"  🤖 Gemini max_tokens: {gemini_config.get('max_tokens'):,}")
        
        # 检查并发处理配置
        click.echo(f"  ⚡ 提取并发数: 最大4个")
        click.echo(f"  ⚡ 评估并发数: 最大3个")
        
        # 检查文档相关信息
        max_tokens = openai_config.get('max_tokens', 0)
        estimated_chars = max_tokens * 3  # 大致估算
        click.echo(f"  📄 最大处理字符数: ~{estimated_chars:,} 字符")
        
        # 检测当前API类型
        from .ai_client import get_ai_client
        try:
            ai_client = get_ai_client()
            if hasattr(ai_client, 'connection_pool'):
                api_type = ai_client.connection_pool._detected_api_type
                click.echo(f"  🔌 当前API类型: {api_type}")
        except Exception as e:
            click.echo(f"  ⚠️ API检测失败: {e}")
        
    except Exception as e:
        click.echo(f"❌ 获取配置信息失败: {e}", err=True)

@cli.command()
@click.argument('files', nargs=-1, required=True)
@click.option('--format', 'output_format', default='markdown',
              type=click.Choice(['markdown', 'json']),
              help='输出格式 (默认: markdown)')
@click.option('--force-search', is_flag=True, default=False,
              help='强制重新进行文献检索，忽略缓存')
@click.option('--force-extract', is_flag=True, default=False,
              help='强制重新提取论文信息，忽略缓存')
@click.option('--check-cache', is_flag=True, default=False,
              help='仅检查缓存状态，不执行评估')
def eval_cached(files, output_format, force_search, force_extract, check_cache):
    """基于缓存数据快速评估论文 (推荐使用)
    
    支持的文件格式: .docx (Word文档)
    
    注意: 暂不支持PDF格式文件，请使用Word文档格式。
    """
    from .cached_evaluator import create_cached_evaluator
    from .ai_client import get_ai_client
    
    # 验证所有文件格式
    for file_path in files:
        validate_file_format(file_path)
    
    click.echo(f"🚀 基于缓存的论文评估 ({len(files)} 个文件)")
    click.echo(f"📊 输出格式: {output_format}")
    if force_search:
        click.echo("🔧 强制重新搜索模式")
    if force_extract:
        click.echo("🔧 强制重新提取模式")
    
    try:
        config_mgr = get_config_manager()
        evaluator = create_cached_evaluator(config_mgr)
        
        success_count = 0
        failed_count = 0
        
        for file_path in files:
            click.echo(f"\n📄 处理文件: {file_path}")
            
            # 检查缓存状态
            cache_status = evaluator.get_cache_status(file_path)
            
            if check_cache:
                click.echo("📊 缓存状态检查:")
                click.echo(f"   论文信息缓存: {'✅ 已缓存' if cache_status['thesis_info_cached'] else '❌ 未缓存'}")
                click.echo(f"   文献搜索缓存: {'✅ 已缓存' if cache_status['search_results_cached'] else '❌ 未缓存'}")
                click.echo(f"   缓存文件数量: {len(cache_status['cache_files'])} 个")
                for cache_file in cache_status['cache_files']:
                    size_mb = cache_file['size'] / (1024 * 1024)
                    click.echo(f"     📁 {cache_file['type']}: {size_mb:.2f} MB")
                continue
            
            # 显示缓存状态
            click.echo(f"💾 论文信息缓存: {'✅' if cache_status['thesis_info_cached'] else '❌'}")
            click.echo(f"💾 文献搜索缓存: {'✅' if cache_status['search_results_cached'] else '❌'}")
            
            # 执行评估
            try:
                ai_client = get_ai_client()
                session_id = f"cached_eval_{int(time.time())}"
                
                result = evaluator.evaluate_with_cache(
                    file_path, ai_client, session_id,
                    force_search=force_search,
                    force_extract=force_extract,
                    output_format=output_format
                )
                
                if result['success']:
                    success_count += 1
                    click.echo("✅ 评估完成")
                    if result.get('report_path'):
                        click.echo(f"📄 报告文件: {result['report_path']}")
                    click.echo(f"💡 消息: {result.get('message', '')}")
                else:
                    failed_count += 1
                    click.echo(f"❌ 评估失败: {result['error']}")
                    if 'suggestions' in result:
                        click.echo("💡 建议:")
                        for suggestion in result['suggestions']:
                            click.echo(f"   • {suggestion}")
                            
            except Exception as e:
                failed_count += 1
                click.echo(f"❌ 处理异常: {e}")
        
        if not check_cache:
            # 显示总结
            click.echo(f"\n🎉 批量评估完成!")
            click.echo(f"✅ 成功: {success_count} 个文件")
            if failed_count > 0:
                click.echo(f"❌ 失败: {failed_count} 个文件")
        
    except Exception as e:
        click.echo(f"❌ 评估过程失败: {e}", err=True)


@cli.command()
@click.argument('files', nargs=-1, required=True)
@click.option('--format', 'output_format', default='markdown',
              type=click.Choice(['markdown', 'json']),
              help='输出格式 (默认: markdown)')
@click.option('--skip-search', is_flag=True, default=False,
              help='跳过文献检索，仅基于现有数据生成报告')
@click.option('--force-extract', is_flag=True, default=False,
              help='强制重新提取论文结构化信息，忽略已有JSON文件')
@click.option('--use-cached-search/--no-use-cached-search', default=True,
              help='使用已有的文献检索缓存结果 (默认: 启用)')
@click.option('--force-search', is_flag=True, default=False,
              help='强制重新进行文献检索，忽略已有检索缓存')
@click.option('--extraction-mode', default='batch-sections',
              type=click.Choice(['batch-sections']),
              help='论文信息提取模式: batch-sections=专家策略处理模式 (默认: batch-sections)')
@click.option('--batch-size', default=10000, type=int,
              help='章节批次处理时每批次最大字符数 (默认: 10000)')
def evaluate(files, output_format, skip_search, force_extract, use_cached_search, force_search, extraction_mode, batch_size):
    """评估论文文件并生成报告 (完整流程)
    
    支持的文件格式: .docx (Word文档)
    
    注意: 暂不支持PDF格式文件，请使用Word文档格式。
    """
    # 验证所有文件格式
    for file_path in files:
        validate_file_format(file_path)
        
    logger.info(f"开始评估 {len(files)} 个文件，提取模式: {extraction_mode}")
    
    click.echo(f"📚 开始评估 {len(files)} 个文件:")
    click.echo(f"🔧 提取模式: {extraction_mode}")
    if extraction_mode == 'batch-sections':
        click.echo(f"📦 批次大小: {batch_size:,} 字符/批次")
        logger.info(f"使用章节批次处理模式，批次大小: {batch_size} 字符")
    
    # 如果只有一个文件，使用串行处理
    if len(files) == 1:
        return _evaluate_single_file(files[0], output_format, skip_search, force_extract, use_cached_search, force_search, extraction_mode, batch_size)
    
    # 多个文件时使用并行处理
    click.echo(f"🚀 启用并行处理模式 (最大{min(len(files), 3)}个并发)")
    
    try:
        # 准备并行处理任务
        success_count = 0
        failed_count = 0
        lock = threading.Lock()  # 用于保护共享计数器
        
        def process_file_with_session(file_info):
            """处理单个文件，使用独立的AI会话"""
            file_index, file_path = file_info
            session_id = f"eval_session_{file_index}_{int(time.time())}"
            
            try:
                result = _evaluate_single_file_parallel(
                    file_path, output_format, skip_search, force_extract, use_cached_search, force_search, session_id, extraction_mode, batch_size
                )
                return result
            except Exception as e:
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': str(e),
                    'session_id': session_id
                }
        
        # 执行并行处理
        max_workers = min(len(files), 3)  # 限制最大并发数 (评估比提取更资源密集)
        file_list = list(enumerate(files))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(process_file_with_session, file_info): file_info[1] 
                for file_info in file_list
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    
                    with lock:
                        if result['success']:
                            success_count += 1
                        else:
                            failed_count += 1
                            click.echo(f"❌ 评估文件失败 ({result['session_id']}): {result['error']}", err=True)
                            
                except Exception as exc:
                    with lock:
                        failed_count += 1
                        click.echo(f"❌ 评估文件异常: {file_path} - {exc}", err=True)
        
        # 显示总结
        click.echo(f"\n🎉 并行评估完成!")
        click.echo(f"✅ 成功: {success_count} 个文件")
        if failed_count > 0:
            click.echo(f"❌ 失败: {failed_count} 个文件")
        click.echo(f"💡 使用 'thesis-eval files' 查看所有生成的文件")
        
    except Exception as e:
        click.echo(f"❌ 并行评估过程失败: {e}", err=True)

def _evaluate_single_file(file_path, output_format, skip_search, force_extract=False, use_cached_search=True, force_search=False, extraction_mode='batch-sections', batch_size=10000):
    """处理单个文件（串行模式）"""
    try:
        result = _evaluate_single_file_parallel(
            file_path, output_format, skip_search, force_extract, use_cached_search, force_search, session_id=None, extraction_mode=extraction_mode, batch_size=batch_size
        )
        
        if result['success']:
            click.echo(f"\n🎉 评估完成!")
            click.echo(f"💡 使用 'thesis-eval files' 查看所有生成的文件")
        else:
            click.echo(f"❌ 评估失败: {result['error']}", err=True)
            
    except Exception as e:
        click.echo(f"❌ 评估过程失败: {e}", err=True)

def _evaluate_single_file_parallel(file_path, output_format, skip_search, force_extract, use_cached_search, force_search, session_id, extraction_mode='batch-sections', batch_size=10000):
    """处理单个文件的核心逻辑（支持并行）"""
    logger.info(f"开始处理文件: {file_path}, 会话ID: {session_id}, 提取模式: {extraction_mode}")
    
    click.echo(f"\n📄 处理文件: {file_path}")
    if session_id:
        click.echo(f"🔗 会话ID: {session_id}")
    
    try:
        config_mgr = get_config_manager()
        
        # 检查文件是否存在
        if not Path(file_path).exists():
            # 提供更详细的错误信息和建议
            error_msg = f"文件不存在: {file_path}"
            suggestions = []
            
            # 检查是否是命令格式错误
            if file_path in ['evaluate', 'extract', 'help', '--help', '-h']:
                error_msg = f"命令格式错误: '{file_path}' 不是文件路径"
                suggestions.extend([
                    "正确格式: thesis-eval evaluate <文件路径>",
                    "查看帮助: thesis-eval evaluate --help",
                    "查看可用文件: thesis-eval files"
                ])
            else:
                # 检查文件路径格式
                if not file_path.startswith(('data/', './', '/', 'C:', 'D:')):
                    suggestions.append("提示: 文件路径可能需要包含目录，如 'data/input/文件名.docx'")
                
                suggestions.extend([
                    "检查文件路径是否正确",
                    "使用 'thesis-eval files' 查看可用文件",
                    "确保文件扩展名为 .docx 或 .md (暂不支持PDF)"
                ])
            
            return {
                'success': False,
                'file_path': file_path,
                'error': error_msg,
                'suggestions': suggestions,
                'session_id': session_id
            }
        
        # 检查文件格式
        file_ext = Path(file_path).suffix
        supported_formats = config_mgr.get_supported_formats()
        if file_ext not in supported_formats:
            return {
                'success': False,
                'file_path': file_path,
                'error': f"不支持的文件格式: {file_ext}",
                'session_id': session_id
            }
        
        # 尝试读取专家版结构化信息JSON文件
        thesis_extracted_info = None
        input_path = Path(file_path)
        base_name = input_path.stem
        output_dir = Path(config_mgr.get_output_dir())
        # 只读取专家版文件
        extracted_info_file = output_dir / f"{base_name}_pro_extracted_info.json"
        
        # 根据参数决定是否使用已有JSON文件
        if force_extract:
            click.echo("🔧 强制重新提取模式，将忽略已有的结构化信息文件")
            thesis_extracted_info = None
        elif extracted_info_file.exists():
            try:
                click.echo(f"📖 发现已有的结构化信息文件: {extracted_info_file}")
                with open(extracted_info_file, 'r', encoding='utf-8') as f:
                    extracted_data = json.load(f)
                    thesis_extracted_info = extracted_data.get('extracted_info', None)
                    if thesis_extracted_info:
                        click.echo("✅ 成功读取已有的论文结构化信息，跳过重复提取")
                        # 显示基本信息
                        if 'title_cn' in thesis_extracted_info:
                            title = thesis_extracted_info['title_cn']
                            click.echo(f"📋 论文标题: {title[:50]}...")
                        metadata = extracted_data.get('metadata', {})
                        if 'extraction_time' in metadata:
                            click.echo(f"⏰ 原提取时间: {metadata['extraction_time']}")
            except Exception as e:
                click.echo(f"⚠️ 读取结构化信息文件失败: {e}")
                thesis_extracted_info = None
        else:
            thesis_extracted_info = None
        
        # 检测缓存的文献检索结果
        cached_search_results = None
        if not skip_search and not force_search and use_cached_search:
            cached_search_results = _detect_cached_search_results(base_name, output_dir)
            if cached_search_results:
                click.echo("📚 发现已有的文献检索缓存结果，将使用缓存数据")
                click.echo(f"   📋 缓存包含: {len(cached_search_results['papers_by_lang'])} 种语言的检索结果")
                for lang, papers in cached_search_results['papers_by_lang'].items():
                    click.echo(f"   📊 {lang}: {len(papers)} 篇相关文献")
        elif force_search:
            click.echo("🔧 强制重新检索模式，将忽略已有的文献检索缓存")
        elif not use_cached_search:
            click.echo("🔧 禁用文献检索缓存，将重新进行文献检索")
        
        # 初始化主要变量
        papers_by_lang = {}
        literature_metadata_analysis = None
        document_text = ""
        
        if not skip_search:
            # 检查是否使用缓存的检索结果
            if cached_search_results:
                click.echo("🔄 开始论文评估流程 (使用缓存的文献检索结果)...")
                if thesis_extracted_info:
                    click.echo("   步骤1: ✅ 论文结构化信息 (已存在)")
                elif force_extract:
                    click.echo("   步骤1: 🔧 论文结构化信息 (强制重新提取)")
                else:
                    click.echo("   步骤1: 📄 论文结构化信息 (需要提取)")
                click.echo("   步骤2: ✅ 文献检索结果 (使用缓存)")
                click.echo("   步骤3: 生成评估报告")
                
                # 使用缓存的检索结果
                papers_by_lang = cached_search_results['papers_by_lang']
                literature_metadata_analysis = cached_search_results.get('literature_metadata_analysis', None)
                
                click.echo("✅ 使用缓存的文献检索结果")
                for lang, papers in papers_by_lang.items():
                    click.echo(f"   {lang}: 使用缓存的 {len(papers)} 篇相关文献")
                
                # 检查是否需要提取论文信息
                if not thesis_extracted_info:
                    click.echo("📄 开始提取论文结构化信息...")
                    try:
                        # 提取文档文本 (仅支持Word文档)
                        from .extract_sections_with_ai import extract_text_from_word
                        click.echo("🔍 正在提取文档文本...")
                        
                        document_text = extract_text_from_word(file_path)
                        
                        click.echo(f"✅ 文档文本提取完成 ({len(document_text):,} 字符)")
                        
                        # 使用专家策略处理模式
                        click.echo(f"🤖 正在使用AI提取结构化信息 (专家策略模式)...")
                        
                        from .ai_client import get_ai_client
                        ai_client = get_ai_client()
                        
                        # 使用专家策略处理模式
                        from .extract_sections_with_ai import extract_sections_with_pro_strategy
                        extracted_info = extract_sections_with_pro_strategy(file_path=file_path, use_cache=True)
                        click.echo(f"   🎓 使用专家策略处理模式 (多学科支持)")
                        
                        if extracted_info:
                            click.echo("✅ 论文结构化信息提取成功")
                            thesis_extracted_info = extracted_info
                            
                            # 保存为JSON文件
                            extracted_info_data = {
                                "metadata": {
                                    "extraction_time": datetime.now().isoformat(),
                                    "file_path": str(file_path),
                                    "document_length": len(document_text),
                                    "extraction_method": "AI + force_extract" if force_extract else "AI",
                                    "session_id": session_id
                                },
                                "extracted_info": extracted_info
                            }
                            
                            with open(extracted_info_file, 'w', encoding='utf-8') as f:
                                json.dump(extracted_info_data, f, ensure_ascii=False, indent=2)
                            
                            click.echo(f"💾 结构化信息已保存: {extracted_info_file}")
                        else:
                            click.echo("⚠️ 论文结构化信息提取失败")
                            
                    except Exception as e:
                        click.echo(f"❌ 论文信息提取失败: {e}")
                        thesis_extracted_info = None
                
                if thesis_extracted_info:
                    click.echo("✅ 论文结构化信息可用")
                    
            else:
                # 执行完整的论文处理流程
                if thesis_extracted_info:
                    click.echo("🔄 开始论文评估流程 (使用已有结构化信息)...")
                    click.echo("   步骤1: ✅ 论文结构化信息 (已存在)")
                    click.echo("   步骤2: 生成检索策略")
                    click.echo("   步骤3: 执行文献检索")
                    click.echo("   步骤4: 计算文献相关性")
                    click.echo("   步骤5: 筛选TOP相关文献")
                    click.echo("   步骤6: 生成评估报告")
                else:
                    click.echo("🔄 开始完整的论文分析流程...")
                    click.echo("   步骤1: 提取论文内容")
                    click.echo("   步骤2: 使用AI提取结构化信息")
                    click.echo("   步骤3: 生成检索策略")
                    click.echo("   步骤4: 执行文献检索")
                    click.echo("   步骤5: 计算文献相关性")
                    click.echo("   步骤6: 筛选TOP相关文献")
                    click.echo("   步骤7: 生成评估报告")
                
                try:
                    # 调用完整的检索流程（传递session_id和已有的结构化信息）
                    from .cnki_client_pool import cnki_auto_search
                    languages = config_mgr.get_supported_languages()
                    
                    # 如果有已提取的信息，传递给检索函数
                    search_kwargs = {
                        'languages': languages, 
                        'session_id': session_id
                    }
                    if thesis_extracted_info:
                        search_kwargs['existing_thesis_info'] = thesis_extracted_info
                    
                    search_results = cnki_auto_search(
                        file_path, **search_kwargs
                    )
                    papers_by_lang = search_results['papers_by_lang']
                    # 如果没有传入已有信息，使用检索结果中的信息
                    if not thesis_extracted_info:
                        thesis_extracted_info = search_results['thesis_extracted_info']
                    literature_metadata_analysis = search_results.get('literature_metadata_analysis', None)
                    
                    click.echo("✅ 论文分析和文献检索完成")
                    for lang, papers in papers_by_lang.items():
                        click.echo(f"   {lang}: 检索到 {len(papers)} 篇相关文献")
                    
                    if thesis_extracted_info:
                        click.echo("✅ 论文结构化信息可用")
                    
                except Exception as e:
                    return {
                        'success': False,
                        'file_path': file_path,
                        'error': f"完整流程执行失败: {e}",
                        'session_id': session_id
                    }
        
        else:
            # 跳过检索，但如果没有结构化信息，仍需提取
            click.echo("⏭️ 跳过文献检索，基于现有数据生成报告...")
            
            # 如果没有结构化信息，需要先提取
            if not thesis_extracted_info:
                try:
                    click.echo("📄 没有现有结构化信息，开始提取论文信息...")
                    click.echo("   步骤1: 提取论文内容")
                    click.echo("   步骤2: 使用AI提取结构化信息")
                    
                    # 获取AI客户端
                    from .ai_client import get_ai_client
                    from .extract_sections_with_ai import extract_sections_with_ai, extract_text_from_word
                    
                    ai_client = get_ai_client()
                    # 使用传入的session_id，如果没有则创建新的
                    ai_session_id = session_id if session_id else ai_client.create_session()
                    
                    # 获取支持的语言
                    languages = config_mgr.get_supported_languages()
                    
                    # 提取文档文本 (仅支持Word文档)
                    click.echo("🔍 正在提取文档文本...")
                    
                    document_text = extract_text_from_word(file_path)
                    
                    click.echo(f"✅ 文档文本提取完成 ({len(document_text):,} 字符)")
                    
                    # 使用专家策略处理模式
                    click.echo(f"🤖 正在使用AI提取结构化信息 (专家策略模式)...")
                    
                    # 使用专家策略处理模式
                    from .extract_sections_with_ai import extract_sections_with_pro_strategy
                    thesis_extracted_info = extract_sections_with_pro_strategy(
                        file_path=file_path, 
                        use_cache=True
                    )
                    click.echo(f"   🎓 使用专家策略处理模式 (多学科支持)")
                    
                    if thesis_extracted_info:
                        click.echo("✅ 论文结构化信息提取完成")
                        # 保存提取的信息到专家版JSON文件
                        extracted_info_file = output_dir / f"{base_name}_pro_extracted_info.json"
                        extracted_data = {
                            'extracted_info': thesis_extracted_info,
                            'metadata': {
                                'extraction_time': datetime.now().isoformat(),
                                'file_path': str(file_path),
                                'method': 'pro_strategy',
                                'extractor_version': '2.0',
                                'session_id': ai_session_id
                            }
                        }
                        with open(extracted_info_file, 'w', encoding='utf-8') as f:
                            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
                        click.echo(f"💾 专家版结构化信息已保存: {extracted_info_file}")
                    else:
                        click.echo("⚠️ 论文结构化信息提取失败")
                        
                except Exception as e:
                    click.echo(f"❌ 论文信息提取失败: {e}")
                    thesis_extracted_info = None
        
        # 如果跳过检索或使用缓存，确保变量已初始化
        if skip_search or cached_search_results:
            if not 'papers_by_lang' in locals():
                papers_by_lang = cached_search_results['papers_by_lang'] if cached_search_results else {}
            if not 'literature_metadata_analysis' in locals():
                literature_metadata_analysis = cached_search_results.get('literature_metadata_analysis', None) if cached_search_results else None
        
        if output_format == 'markdown':
            try:
                # 生成Markdown报告
                click.echo("📝 正在生成Markdown评估报告...")
                from .report_generator import MarkdownReportGenerator
                
                report_generator = MarkdownReportGenerator()
                
                # 如果有结构化信息，传递给报告生成器
                if thesis_extracted_info:
                    report_file_path = report_generator.generate_evaluation_report(
                        file_path, 
                        thesis_extracted_info=thesis_extracted_info
                    )
                else:
                    report_file_path = report_generator.generate_evaluation_report(file_path)
                
                click.echo(f"✅ Markdown报告已保存: {report_file_path}")
                
                # 生成文献综述深度分析报告
                if thesis_extracted_info and papers_by_lang:
                    try:
                        click.echo("📊 正在生成文献综述深度分析报告...")
                        from .literature_review_analyzer import LiteratureReviewAnalyzer
                        
                        literature_analyzer = LiteratureReviewAnalyzer()
                        literature_report_path = literature_analyzer.analyze_literature_review(
                            str(file_path),
                            thesis_extracted_info,
                            papers_by_lang,
                            str(output_dir)
                        )
                        click.echo(f"✅ 文献综述分析报告已保存: {literature_report_path}")
                        
                    except Exception as e:
                        click.echo(f"⚠️ 文献综述分析报告生成失败: {e}")
                        # 不中断主流程，只是警告
                
            except Exception as e:
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': f"报告生成失败: {e}",
                    'session_id': session_id
                }
        
        else:
            # JSON格式输出（保持原有功能）
            output_dir = config_mgr.get_output_dir()
            base_name = Path(file_path).stem
            
            # 列出可能的输出文件
            potential_files = [
                f"{base_name}_relevant_papers_Chinese.json",
                f"{base_name}_relevant_papers_English.json",
                f"{base_name}_TOP{config_mgr.get_top_papers_count()}PAPERS_Chinese.json",
                f"{base_name}_TOP{config_mgr.get_top_papers_count()}PAPERS_English.json"
            ]
            
            click.echo(f"📊 JSON数据文件位置: {output_dir}")
            for filename in potential_files:
                file_path_full = Path(output_dir) / filename
                if file_path_full.exists():
                    click.echo(f"  ✅ {filename}")
                else:
                    click.echo(f"  ❓ {filename} (待生成)")
        
        return {
            'success': True,
            'file_path': file_path,
            'session_id': session_id
        }
        
    except Exception as e:
        return {
            'success': False,
            'file_path': file_path,
            'error': str(e),
            'session_id': session_id
        }

@cli.command()
@click.argument('files', nargs=-1, required=True)
@click.option('--output-dir', '-o', 
              help='输出目录 (默认使用配置文件中的输出目录)')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'markdown']),
              help='输出格式 (默认: json)')
@click.option('--extraction-mode', default='batch-sections',
              type=click.Choice(['batch-sections']),
              help='论文信息提取模式: batch-sections=专家策略处理模式 (默认: batch-sections)')
@click.option('--batch-size', default=10000, type=int,
              help='章节批次处理时每批次最大字符数 (默认: 10000)')
@click.option('--use-cache/--no-cache', default=True,
              help='是否使用文档缓存 (默认: 启用)')
@click.option('--clear-cache', is_flag=True, default=False,
              help='清除文档缓存后重新处理')
def extract(files, output_dir, output_format, extraction_mode, batch_size, use_cache, clear_cache):
    """提取论文结构化信息并生成JSON文件
    
    支持的文件格式: .docx (Word文档)
    
    注意: 暂不支持PDF格式文件，请使用Word文档格式。
    """
    # 验证所有文件格式
    for file_path in files:
        validate_file_format(file_path)
        
    click.echo(f"📄 开始提取 {len(files)} 个文件的结构化信息:")
    click.echo(f"🔧 提取模式: {extraction_mode}")
    if extraction_mode == 'batch-sections':
        click.echo(f"📊 批次大小: {batch_size:,} 字符")
    click.echo(f"💾 缓存设置: {'启用' if use_cache else '禁用'}")
    
    # 处理缓存清除
    if clear_cache:
        click.echo("🗑️ 清除文档缓存...")
        from .extract_sections_with_ai import get_document_cache
        cache_manager = get_document_cache()
        cache_manager.clear_cache()
        click.echo("✅ 缓存已清除")
    
    # 如果只有一个文件，使用串行处理
    if len(files) == 1:
        return _extract_single_file(files[0], output_dir, output_format, extraction_mode, batch_size, use_cache)
    
    # 多个文件时使用并行处理
    click.echo(f"🚀 启用并行处理模式 (最大{min(len(files), 4)}个并发)")
    
    try:
        config_mgr = get_config_manager()
        
        # 确定输出目录
        if not output_dir:
            output_dir = config_mgr.get_output_dir()
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 准备并行处理任务
        extraction_time = datetime.now().isoformat()
        success_count = 0
        failed_count = 0
        lock = threading.Lock()  # 用于保护共享计数器
        
        def process_file_with_session(file_info):
            """处理单个文件，使用独立的AI会话"""
            file_index, file_path = file_info
            session_id = f"extract_session_{file_index}_{int(time.time())}"
            
            try:
                result = _extract_single_file_parallel(
                    file_path, output_path, output_format, 
                    extraction_time, session_id, extraction_mode, batch_size, use_cache
                )
                return result
            except Exception as e:
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': str(e),
                    'session_id': session_id
                }
        
        # 执行并行处理
        max_workers = min(len(files), 4)  # 限制最大并发数
        file_list = list(enumerate(files))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(process_file_with_session, file_info): file_info[1] 
                for file_info in file_list
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    
                    with lock:
                        if result['success']:
                            success_count += 1
                        else:
                            failed_count += 1
                            click.echo(f"❌ 处理文件失败 ({result['session_id']}): {result['error']}", err=True)
                            # 显示建议信息（如果有）
                            if 'suggestions' in result:
                                click.echo("💡 建议:")
                                for suggestion in result['suggestions']:
                                    click.echo(f"   • {suggestion}")
                            
                except Exception as exc:
                    with lock:
                        failed_count += 1
                        click.echo(f"❌ 处理文件异常: {file_path} - {exc}", err=True)
        
        # 显示总结
        click.echo(f"\n🎉 并行提取完成!")
        click.echo(f"✅ 成功: {success_count} 个文件")
        if failed_count > 0:
            click.echo(f"❌ 失败: {failed_count} 个文件")
        click.echo(f"📁 输出目录: {output_path}")
        
    except Exception as e:
        import traceback
        click.echo(f"❌ 并行提取过程失败: {e}", err=True)
        click.echo(f"详细错误: {traceback.format_exc()}", err=True)

def _extract_single_file(file_path, output_dir, output_format, extraction_mode='batch-sections', batch_size=10000, use_cache=True):
    """处理单个文件（串行模式）"""
    try:
        config_mgr = get_config_manager()
        
        # 确定输出目录
        if not output_dir:
            output_dir = config_mgr.get_output_dir()
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        extraction_time = datetime.now().isoformat()
        
        result = _extract_single_file_parallel(
            file_path, output_path, output_format, 
            extraction_time, session_id=None, extraction_mode=extraction_mode, batch_size=batch_size, use_cache=use_cache
        )
        
        if result['success']:
            click.echo(f"\n🎉 提取完成!")
            click.echo(f"✅ 成功: 1 个文件")
            click.echo(f"📁 输出目录: {output_path}")
        else:
            click.echo(f"❌ 提取失败: {result['error']}", err=True)
            
    except Exception as e:
        import traceback
        click.echo(f"❌ 提取过程失败: {e}", err=True)
        click.echo(f"详细错误: {traceback.format_exc()}", err=True)

def _extract_single_file_parallel(file_path, output_path, output_format, extraction_time, session_id, extraction_mode='batch-sections', batch_size=10000, use_cache=True):
    """处理单个文件的核心逻辑（支持并行）"""
    click.echo(f"\n📄 处理文件: {file_path}")
    if session_id:
        click.echo(f"🔗 会话ID: {session_id}")
    click.echo(f"🔧 提取模式: {extraction_mode}")
    if extraction_mode == 'batch-sections':
        click.echo(f"📊 批次大小: {batch_size:,} 字符")
    
    # 检查文件是否存在
    input_file = Path(file_path)
    if not input_file.exists():
        # 提供更详细的错误信息和建议
        error_msg = f"文件不存在: {file_path}"
        suggestions = []
        
        # 检查是否是命令格式错误
        if file_path in ['evaluate', 'extract', 'help', '--help', '-h']:
            error_msg = f"命令格式错误: '{file_path}' 不是文件路径"
            suggestions.extend([
                "正确格式: thesis-eval extract <文件路径>",
                "查看帮助: thesis-eval extract --help",
                "查看可用文件: thesis-eval files"
            ])
        else:
            # 检查文件路径格式
            if not file_path.startswith(('data/', './', '/', 'C:', 'D:')):
                suggestions.append("提示: 文件路径可能需要包含目录，如 'data/input/文件名.docx'")
            
            suggestions.extend([
                "检查文件路径是否正确",
                "使用 'thesis-eval files' 查看可用文件",
                "确保文件扩展名为 .docx 或 .md (暂不支持PDF)"
            ])
        
        return {
            'success': False,
            'file_path': file_path,
            'error': error_msg,
            'suggestions': suggestions,
            'session_id': session_id
        }
    
    # 检查文件格式
    file_ext = input_file.suffix.lower()
    if file_ext not in ['.docx']:
        return {
            'success': False,
            'file_path': file_path,
            'error': f"不支持的文件格式: {file_ext}，当前仅支持 .docx 格式",
            'session_id': session_id
        }
    
    try:
        # 使用专家策略处理模式提取论文信息
        from .extract_sections_with_ai import extract_sections_with_pro_strategy
        
        click.echo(f"🤖 正在使用专家策略提取结构化信息...")
        extracted_info = extract_sections_with_pro_strategy(
            file_path=file_path, 
            use_cache=use_cache
        )
        
        if extracted_info:
            # 保存提取结果 - 使用专家版文件名
            base_name = input_file.stem
            output_file = output_path / f"{base_name}_pro_extracted_info.json"
            
            output_data = {
                'extracted_info': extracted_info,
                'metadata': {
                    'extraction_time': extraction_time,
                    'file_path': str(file_path),
                    'extraction_mode': extraction_mode,
                    'method': 'pro_strategy',
                    'extractor_version': '2.0',
                    'session_id': session_id
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            click.echo(f"✅ 提取成功: {output_file}")
            return {
                'success': True,
                'file_path': file_path,
                'output_file': str(output_file),
                'session_id': session_id
            }
        else:
            return {
                'success': False,
                'file_path': file_path,
                'error': "提取失败：未获得有效的结构化信息",
                'session_id': session_id
            }
            
    except Exception as e:
        return {
            'success': False,
            'file_path': file_path,
            'error': f"提取过程出错: {str(e)}",
            'session_id': session_id
        }


@cli.command()
def files():
    """列出输入和输出文件"""
    click.echo("📁 文件列表:")
    
    try:
        config_mgr = get_config_manager()
        
        # 列出输入文件
        input_dir = Path(config_mgr.get_input_dir())
        if input_dir.exists():
            click.echo(f"\n📥 输入文件 ({input_dir}):")
            input_files = list(input_dir.glob("*"))
            if input_files:
                for file in sorted(input_files):
                    if file.is_file():
                        size = file.stat().st_size
                        click.echo(f"  📄 {file.name} ({size:,} bytes)")
            else:
                click.echo("  (无文件)")
        else:
            click.echo(f"\n❌ 输入目录不存在: {input_dir}")
        
        # 列出输出文件
        output_dir = Path(config_mgr.get_output_dir())
        if output_dir.exists():
            click.echo(f"\n📤 输出文件 ({output_dir}):")
            output_files = list(output_dir.glob("*"))
            if output_files:
                for file in sorted(output_files):
                    if file.is_file():
                        size = file.stat().st_size
                        click.echo(f"  📄 {file.name} ({size:,} bytes)")
            else:
                click.echo("  (无文件)")
        else:
            click.echo(f"\n❌ 输出目录不存在: {output_dir}")
            
    except Exception as e:
        click.echo(f"❌ 列出文件失败: {e}", err=True)


@cli.command(name='md-cnki-search-cn')
@click.option('--input-dir', default=None, help='输入目录，默认读取配置中的 input_dir')
def md_cnki_search_cn(input_dir):
    """读取 data/input 下所有 .md，生成中文检索式并调用CNKI检索。

    - 仅中文检索（languages=['Chinese']）
    - 不进行章节分析；从 .md 中粗提题名/关键词/摘要/方法
    - 结果写入 data/output 下相关文献与TOP文献JSON
    """
    try:
        import re
        from datetime import date, datetime
        from pathlib import Path
        from typing import Optional
        from .cnki_client_pool import cnki_auto_search

        def first_heading(md: str) -> str:
            for line in md.splitlines():
                m = re.match(r'^\s{0,3}#\s+(.+)$', line.strip())
                if m:
                    return m.group(1).strip()
            return ''

        def find_keywords(md: str, labels) -> str:
            for line in md.splitlines():
                if any(lbl.lower() in line.lower() for lbl in labels):
                    m = re.search(r'(?:关键词|关键字|Keywords?)[:：]\s*(.+)', line, re.I)
                    if m:
                        return m.group(1).strip()
            return ''

        def extract_block(md: str, headers) -> str:
            # 提取“## 摘要 … 到下一个标题”
            pat_h = re.compile(r'^\s{0,3}#{1,6}\s*(' + '|'.join(map(re.escape, headers)) + r')\b.*$', re.I | re.M)
            m = pat_h.search(md)
            if m:
                start = m.end()
            else:
                pat_l = re.compile(r'^(?:' + '|'.join(map(re.escape, headers)) + r')\s*[:：]?\s*$', re.I | re.M)
                m = pat_l.search(md)
                if not m:
                    return ''
                start = m.end()
            nxt = re.search(r'^\s{0,3}#{1,6}\s+\S+', md[start:], re.M)
            end = start + (nxt.start() if nxt else len(md) - start)
            return md[start:end].strip()

        def normalize_label(line: str) -> str:
            cleaned = line.strip()
            cleaned = re.sub(r'^[#\*\s]+', '', cleaned)
            cleaned = re.sub(r'[\*\s]+$', '', cleaned)
            return cleaned.strip()

        def match_date_value(text: str) -> Optional[date]:
            if not text:
                return None
            chunk = text.strip()
            if not chunk:
                return None
            parts = re.split(r'[：:]', chunk, maxsplit=1)
            if len(parts) == 2:
                chunk = parts[1]
            chunk = re.sub(r'（.*?）|\(.*?\)', '', chunk)
            translation = str.maketrans({'年': '-', '月': '-', '日': '', '/': '-', '.': '-', '．': '-'})
            chunk = chunk.translate(translation)
            chunk = re.sub(r'\s+', '', chunk)
            if not chunk:
                return None
            candidates = [chunk, chunk.replace('-', '')]
            formats = ('%Y-%m-%d', '%Y%m%d', '%Y-%m', '%Y%m')
            for candidate in candidates:
                for fmt in formats:
                    try:
                        dt = datetime.strptime(candidate, fmt)
                        if fmt in ('%Y-%m', '%Y%m'):
                            dt = datetime(dt.year, dt.month, 1)
                        return dt.date()
                    except ValueError:
                        continue
            match = re.search(r'(\d{4})(\d{1,2})(\d{1,2})', candidates[0])
            if match:
                year, month, day = map(int, match.groups())
                return date(year, month, day)
            return None

        def extract_date(md: str, labels) -> Optional[date]:
            lines = md.splitlines()
            label_lower = [lbl.lower() for lbl in labels]
            for idx, line in enumerate(lines):
                normalized = normalize_label(line).lower()
                if any(lbl in normalized for lbl in label_lower):
                    dv = match_date_value(line)
                    if not dv and idx + 1 < len(lines):
                        dv = match_date_value(lines[idx + 1])
                    if dv:
                        return dv
            return None

        # 准备输入目录
        config_mgr = get_config_manager()
        base_input = input_dir or config_mgr.get_input_dir()
        input_path = Path(base_input)
        if not input_path.exists():
            click.echo(f"❌ 输入目录不存在: {input_path}")
            return

        md_files = sorted(input_path.glob('*.md'))
        if not md_files:
            click.echo("(未找到 .md 文件) 目录: " + str(input_path))
            return

        click.echo(f"📄 发现 {len(md_files)} 个 .md 文件，开始中文检索…")

        success = 0
        failed = 0

        for md_file in md_files:
            click.echo(f"\n📄 处理: {md_file.name}")
            try:
                md = md_file.read_text('utf-8', errors='ignore')
                h1 = first_heading(md) or md_file.stem
                abs_cn = extract_block(md, ['中文摘要', '摘要']) or ''
                kw_cn = find_keywords(md, ['关键词', '关键字']) or ''
                has_cn = bool(re.search(r'[\u4e00-\u9fa5]', h1))
                title_cn = h1 if has_cn else ''
                methods = extract_block(md, ['研究方法', '方法']) or ''

                defense_dt = extract_date(md, ['论文答辩日期', '答辩日期', '答辩时间', '答辩'])
                completion_dt = extract_date(md, ['论文完成日期', '完成日期', '完成时间'])
                submission_dt = extract_date(md, ['论文提交日期', '提交日期', '提交时间'])
                search_cutoff = defense_dt or completion_dt or submission_dt

                thesis_info = {
                    'title_ch': title_cn,
                    'keywords_ch': kw_cn,
                    'abstract_ch': abs_cn,
                    'title_cn': title_cn,
                    'keywords_cn': kw_cn,
                    'abstract_cn': abs_cn,
                    'ChineseTitle': title_cn,
                    'ChineseKeywords': kw_cn,
                    'ChineseAbstract': abs_cn,
                    'research_methods': methods,
                }

                if defense_dt:
                    thesis_info['defense_date'] = defense_dt.isoformat()
                if completion_dt:
                    thesis_info['completion_date'] = completion_dt.isoformat()
                if submission_dt:
                    thesis_info['submission_date'] = submission_dt.isoformat()
                if search_cutoff:
                    thesis_info['search_cutoff_date'] = search_cutoff.strftime('%Y%m%d')

                # 仅中文检索
                res = cnki_auto_search(
                    file_path=str(md_file),
                    languages=['Chinese'],
                    existing_thesis_info=thesis_info,
                )

                papers_by_lang = res.get('papers_by_lang', {}) if res else {}
                click.echo(f"  Chinese: Top papers = {len(papers_by_lang.get('Chinese', []))}")
                success += 1
            except Exception as e:
                failed += 1
                click.echo(f"❌ 失败: {e}")

        click.echo(f"\n🎉 完成。成功 {success}，失败 {failed}")

    except Exception as e:
        click.echo(f"❌ 执行失败: {e}", err=True)

@cli.command()
@click.argument('files', nargs=-1, required=True)
@click.option('--output-dir', '-o', default=None,
              help='输出目录 (默认使用配置的输出目录)')
def literature_analysis(files, output_dir):
    """生成文献综述深度分析报告
    
    仅生成文献综述分析报告，需要已有的论文提取信息和文献检索结果。
    
    支持的文件格式: .docx (Word文档)
    
    注意: 暂不支持PDF格式文件，请使用Word文档格式。
    """
    # 验证所有文件格式
    for file_path in files:
        validate_file_format(file_path)
        
    try:
        config_mgr = get_config_manager()
        
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = Path(config_mgr.get_output_dir())
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"📊 开始生成文献综述深度分析报告，共 {len(files)} 个文件:")
        
        for file_path in files:
            click.echo(f"\n📄 处理文件: {file_path}")
            
            # 检查文件是否存在
            if not Path(file_path).exists():
                click.echo(f"❌ 文件不存在: {file_path}")
                continue
            
            base_name = Path(file_path).stem
            
            # 优先加载专家版论文提取信息
            pro_extracted_info_file = output_path / f"{base_name}_pro_extracted_info.json"
            standard_extracted_info_file = output_path / f"{base_name}_extracted_info.json"
            
            thesis_extracted_info = None
            if pro_extracted_info_file.exists():
                try:
                    with open(pro_extracted_info_file, 'r', encoding='utf-8') as f:
                        extracted_data = json.load(f)
                        thesis_extracted_info = extracted_data.get('extracted_info', {})
                        click.echo(f"✅ 加载专家版论文信息: {pro_extracted_info_file}")
                except Exception as e:
                    click.echo(f"⚠️ 读取专家版文件失败: {e}")
            
            if not thesis_extracted_info and standard_extracted_info_file.exists():
                try:
                    with open(standard_extracted_info_file, 'r', encoding='utf-8') as f:
                        extracted_data = json.load(f)
                        thesis_extracted_info = extracted_data.get('extracted_info', {})
                        click.echo(f"✅ 加载标准版论文信息: {standard_extracted_info_file}")
                except Exception as e:
                    click.echo(f"⚠️ 读取标准版文件失败: {e}")
            
            if not thesis_extracted_info:
                click.echo(f"❌ 找不到论文提取信息文件")
                click.echo("   请先运行 'thesis-eval evaluate' 或 'thesis-eval extract' 生成提取信息")
                continue
            
            # 加载文献数据
            papers_by_lang = {}
            
            # 检查中文文献
            chinese_file = output_path / f"{base_name}_relevant_papers_Chinese.json"
            if chinese_file.exists():
                with open(chinese_file, 'r', encoding='utf-8') as f:
                    chinese_papers = json.load(f)
                    papers_by_lang['Chinese'] = chinese_papers
                    click.echo(f"✅ 加载中文文献: {len(chinese_papers)} 篇")
            
            # 检查英文文献
            english_file = output_path / f"{base_name}_relevant_papers_English.json"
            if english_file.exists():
                with open(english_file, 'r', encoding='utf-8') as f:
                    english_papers = json.load(f)
                    papers_by_lang['English'] = english_papers
                    click.echo(f"✅ 加载英文文献: {len(english_papers)} 篇")
            
            if not papers_by_lang:
                click.echo(f"❌ 找不到文献数据文件")
                click.echo("   请先运行 'thesis-eval evaluate' 生成文献检索结果")
                continue
            
            # 生成文献综述分析报告
            try:
                from .literature_review_analyzer import LiteratureReviewAnalyzer
                
                analyzer = LiteratureReviewAnalyzer()
                report_file = analyzer.analyze_literature_review(
                    str(file_path),
                    thesis_extracted_info,
                    papers_by_lang,
                    str(output_path)
                )
                click.echo(f"✅ 文献综述分析报告已保存: {report_file}")
                
            except Exception as e:
                click.echo(f"❌ 生成文献综述分析报告失败: {e}")
        
        click.echo(f"\n🎉 文献综述分析完成!")
        
    except Exception as e:
        click.echo(f"❌ 处理失败: {e}", err=True)


@cli.command()
@click.option('--info', is_flag=True, default=False,
              help='显示缓存统计信息')
@click.option('--clear', is_flag=True, default=False,
              help='清除所有文档缓存')
@click.option('--clear-file', type=str, default=None,
              help='清除指定文件的缓存')
def cache(info, clear, clear_file):
    """管理文档缓存"""
    from .extract_sections_with_ai import get_document_cache
    
    cache_manager = get_document_cache()
    
    if clear:
        click.echo("🗑️ 清除所有文档缓存...")
        success = cache_manager.clear_cache()
        if success:
            click.echo("✅ 所有缓存已清除")
        else:
            click.echo("❌ 清除缓存失败", err=True)
    
    elif clear_file:
        click.echo(f"🗑️ 清除文件缓存: {clear_file}")
        if not Path(clear_file).exists():
            click.echo(f"❌ 文件不存在: {clear_file}", err=True)
            return
            
        success = cache_manager.clear_cache(clear_file)
        if success:
            click.echo("✅ 文件缓存已清除")
        else:
            click.echo("❌ 清除文件缓存失败", err=True)
    
    elif info:
        click.echo("📊 文档缓存统计信息:")
        cache_info = cache_manager.get_cache_info()
        
        if cache_info:
            click.echo(f"   缓存目录: {cache_info['cache_dir']}")
            click.echo(f"   已缓存文件: {cache_info['cached_files']} 个")
            click.echo(f"   元数据文件: {cache_info['metadata_files']} 个")
            click.echo(f"   总大小: {cache_info['total_size_mb']} MB ({cache_info['total_size_bytes']:,} 字节)")
            
            if cache_info['cached_files'] > 0:
                click.echo("\n📁 缓存文件列表:")
                cache_dir = Path(cache_info['cache_dir'])
                for md_file in sorted(cache_dir.glob("*.md")):
                    size = md_file.stat().st_size
                    click.echo(f"   📄 {md_file.name} ({size:,} 字节)")
        else:
            click.echo("❌ 无法获取缓存信息")
    
    else:
        click.echo("💾 文档缓存管理")
        click.echo("使用 --info 查看缓存信息")
        click.echo("使用 --clear 清除所有缓存")
        click.echo("使用 --clear-file <文件路径> 清除指定文件缓存")


if __name__ == '__main__':
    cli()
