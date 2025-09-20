from .logging_config import setup_logging

# Call logging setup at the very top (before any logging usage)
setup_logging()

import json
import requests
import threading
from queue import Queue
import logging
import ssl
import http.client
import os
import re
from datetime import date, datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from .cnki_query_generator import get_query_generator
from .extract_sections_with_ai import extract_sections_with_ai, extract_text_from_word
from .ai_client import get_ai_client
from urllib.parse import urlparse
from .pandas_remove_duplicates import pandas_remove_duplicates
from sentence_transformers import SentenceTransformer
import numpy as np
import time
from .config_manager import get_config_manager, get_config

logger = logging.getLogger(__name__)


def normalize_cnki_pt_upper(value):
    """Normalize date-like values to CNKI PT format (YYYYMMDD)."""
    if value is None:
        return None
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value.strftime('%Y%m%d')
    if isinstance(value, (int, float)):
        value = str(int(value))
    if isinstance(value, str):
        chunk = value.strip()
        if not chunk:
            return None
        chunk = re.sub(r'（.*?）|\(.*?\)', '', chunk)
        translation = str.maketrans({
            '年': '-',
            '月': '-',
            '日': '',
            '/': '-',
            '.': '-',
            '．': '-',
        })
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
                    return dt.strftime('%Y%m%d')
                except ValueError:
                    continue
        match = re.search(r'(\d{4})(\d{1,2})(\d{1,2})', candidates[0])
        if match:
            year, month, day = map(int, match.groups())
            return f"{year:04d}{month:02d}{day:02d}"
    return None


class CNKIClient:
    """A simple CNKI API client for a single session."""
    def __init__(self, uniplatform, access_token):
        self.uniplatform = uniplatform
        self.access_token = access_token

    @staticmethod
    def clean_html(raw_html):
        """
        Removes HTML tags from a string.
        """
        return re.sub('<.*?>', '', raw_html) if raw_html else ""

    def rebuild_search_results(self, original_data):
        """
        Restructure the JSON data from CNKI API result to a new format.
        解析完整的CNKI数据结构，包括期刊、作者、单位、核心期刊等信息。

        Args:
            original_data (dict): The original JSON data from CNKI API.

        Returns:
            dict: The restructured JSON data.
        """
        new_json_structure = {
            "code": original_data.get("code"),
            "message": original_data.get("message"),
            "searchResultsCollections": {
                "total": original_data.get("data", {}).get("total"),
                "size": original_data.get("data", {}).get("size"),
                "items": []
            }
        }

        # Check if there is data to process in the original file
        if original_data.get("data") and original_data["data"].get("data"):
            # Iterate over each record in the original data
            for item in original_data["data"]["data"]:
                processed_item = {}
                
                # 处理基本元数据信息
                if "metadata" in item:
                    # Extract details from the metadata list
                    for meta in item["metadata"]:
                        name = meta.get("name")
                        value = meta.get("value")

                        if name == "YE":
                            processed_item["PublicationYear"] = value or ""
                        elif name == "TI":
                            processed_item["Title"] = self.clean_html(value)
                        elif name == "KY":
                            processed_item["KeyWords"] = self.clean_html(value)
                        elif name == "AB":
                            processed_item["Abstract"] = self.clean_html(value)
                        elif name == "LY":
                            processed_item["Journal"] = self.clean_html(value)  # 期刊名称
                        elif name == "DB":
                            processed_item["Database"] = value  # 数据库类型
                
                # 处理作者信息
                if "authors" in item and item["authors"]:
                    authors = []
                    for author in item["authors"]:
                        author_info = {
                            "name": author.get("title", ""),
                            "id": author.get("id", ""),
                            "corresponding": author.get("corresponding", False)
                        }
                        authors.append(author_info)
                    processed_item["Authors"] = authors
                    # 也保存第一作者的名字用于兼容性
                    if authors:
                        processed_item["FirstAuthor"] = authors[0]["name"]
                
                # 处理作者单位信息
                if "affiliations" in item and item["affiliations"]:
                    affiliations = []
                    for aff in item["affiliations"]:
                        aff_info = {
                            "id": aff.get("id", ""),
                            "name": aff.get("title", "")
                        }
                        affiliations.append(aff_info)
                    processed_item["Affiliations"] = affiliations
                
                # 处理核心期刊信息
                if "indexes" in item and item["indexes"]:
                    indexes = []
                    for index in item["indexes"]:
                        index_info = {
                            "name": index.get("name", ""),
                            "description": index.get("value", "")
                        }
                        indexes.append(index_info)
                    processed_item["CoreJournalIndexes"] = indexes
                
                # 处理来源信息
                if "source" in item:
                    source = item["source"]
                    processed_item["Source"] = {
                        "type": source.get("type", ""),
                        "title": source.get("title", ""),
                        "year": source.get("year", ""),
                        "volume": source.get("volume", ""),
                        "issue": source.get("issue", "")
                    }
                
                # 处理基金信息
                if "funds" in item and item["funds"]:
                    funds = []
                    for fund in item["funds"]:
                        fund_info = {
                            "title": fund.get("title", "")
                        }
                        funds.append(fund_info)
                    processed_item["Funds"] = funds
                
                # 处理关键词信息（更详细的关键词数据）
                if "keywords" in item and item["keywords"]:
                    detailed_keywords = []
                    for kw_group in item["keywords"]:
                        if "items" in kw_group:
                            for kw_item in kw_group["items"]:
                                detailed_keywords.append(self.clean_html(kw_item.get("item", "")))
                    if detailed_keywords:
                        processed_item["DetailedKeywords"] = detailed_keywords

                # 处理引用指标信息
                if "metrics" in item and item["metrics"]:
                    metrics = {}
                    for metric in item["metrics"]:
                        metric_name = metric.get("name", "")
                        metric_value = metric.get("value", "0")
                        if metric_name == "DTC":
                            metrics["download_count"] = int(metric_value) if metric_value.isdigit() else 0
                        elif metric_name == "CTC":
                            metrics["citation_count"] = int(metric_value) if metric_value.isdigit() else 0
                    processed_item["Metrics"] = metrics
                
                # 处理出版状态信息
                if "publishing" in item:
                    publishing = item["publishing"]
                    processed_item["Publishing"] = {
                        "status": publishing.get("status", ""),
                        "modes": publishing.get("modes", [])
                    }
                
                # 处理仓储信息（学科分类等）
                if "repository" in item:
                    repository = item["repository"]
                    processed_item["Repository"] = {
                        "resource": repository.get("resource", ""),
                        "dataset": repository.get("dataset", ""),
                        "type": repository.get("type", ""),
                        "subject_category_1": repository.get("ccl1", ""),  # 一级学科分类
                        "subject_category_2": repository.get("ccl2", "")   # 二级学科分类
                    }

                # Append the processed item to the 'items' list in the new structure
                new_json_structure["searchResultsCollections"]["items"].append(processed_item)

        return new_json_structure


    def call_cnki_api_raw_http(self, cnki_expression, lang='Chinese', pt_upper=None):
        """
        Raw HTTP CNKI API call, returns the parsed JSON or None.
        支持中文和英语检索，lang参数为'Chinese'或'English'。
        :param pt_upper: Optional publication date upper bound (YYYYMMDD) for PT filter.
        """
        # 优先从配置文件获取API端点
        search_api_url = None
        
        try:
            from .config_manager import get_config_manager
            config_mgr = get_config_manager()
            endpoints = config_mgr.get_cnki_api_endpoints()
            search_api_url = endpoints.get('search_url')
            logger.debug(f"使用配置文件中的CNKI检索端点: {search_api_url}")
        except Exception as e:
            logger.warning(f"从配置文件读取CNKI端点失败: {e}")
        
        # 如果配置文件没有，回退到环境变量
        if not search_api_url:
            search_api_url = os.environ.get("CNKI_SEARCH_API_BASE_URL")
            logger.debug(f"使用环境变量中的CNKI检索端点: {search_api_url}")
        
        if not search_api_url:
            logger.error("CNKI检索API端点未配置，请在config/conf.yaml或环境变量中设置")
            raise RuntimeError("CNKI检索API端点未配置")
            
        from urllib.parse import urlparse
        parsed = urlparse(search_api_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        path = parsed.path

        headers = {
            'uniplatform': self.uniplatform,
            'language': 'CHS',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        # 根据语言选择product参数
        if lang == 'English':
            product = "WWJD,WWPD"
        else:
            product = "CJFD,CDFD,CMFD,CPFD,CCND,IPFD,CAPJ"

        normalized_pt_upper = normalize_cnki_pt_upper(pt_upper) if pt_upper else None
        publication_upper = normalized_pt_upper or "20220101"

        raw_body = json.dumps({
            "resource": "CROSSDB",
            "product": product,
            "extend": 1,
            "start": 1,
            "size": 50,
            "sort": "PT",
            "sequence": "DESC",
            "select": "TI,AB,KY,DB,LY,YE,PT",
            "q": {
                "logic": "AND",
                "items": [{
                    "logic": "AND",
                    "operator": "",
                    "uf": "EXPERT",
                    "uv": cnki_expression
                },
                {
                    "logic": "AND",
                    "operator": "LE",
                    "uf": "PT",
                    "uv": publication_upper
                }],
                "childItems": []
            }
        })

        import ssl
        import http.client
        conn = None
        try:
            context = ssl.create_default_context()
            conn = http.client.HTTPSConnection(host, port=port, context=context)
            conn.request("POST", path, body=raw_body, headers=headers)
            response = conn.getresponse()

            if 200 <= response.status < 300:
                response_body_string = response.read().decode('utf-8')
                try:
                    original_json_data = json.loads(response_body_string)
                    # logger.debug(f"Raw HTTP Success: {original_json_data}")
                    json_data = self.rebuild_search_results(original_json_data)
                    return json_data
                except json.JSONDecodeError:
                    logger.error("Raw HTTP Success, but response is not valid JSON.")
                    logger.error(f"Response Body (String): {response_body_string}")
                    return None
            else:
                logger.error(f"Raw HTTP Error: {response.status} {response.reason}")
                logger.error(f"Response Body: {response.read().decode('utf-8')}")
                return None

        except Exception as e:
            logger.error(f"Raw HTTP Exception: {e}")
            return None

        finally:
            if conn:
                conn.close()


class CNKIClientPool:
    """Thread-safe pool for CNKIClient instances."""
    def __init__(self, uniplatform, access_token, max_clients=5):
        self._clients = Queue(maxsize=max_clients)
        for _ in range(max_clients):
            self._clients.put(CNKIClient(uniplatform, access_token))

    def acquire(self):
        return self._clients.get()

    def release(self, client):
        self._clients.put(client)

    def call_concurrent(self, expressions):
        """
        支持多语言模式的并发调用。
        expressions: 可以是字符串列表（仅中文），也可以是 (expr, lang[, pt_upper]) 元组列表。
        """
        results = [None] * len(expressions)

        def worker(idx, expr):
            client = self.acquire()
            try:
                # 支持 (expr, lang, pt_upper) 或 expr 两种调用方式
                if isinstance(expr, tuple):
                    if len(expr) == 3:
                        query_expr, expr_lang, expr_pt = expr
                        result = client.call_cnki_api_raw_http(query_expr, lang=expr_lang, pt_upper=expr_pt)
                    elif len(expr) == 2:
                        query_expr, expr_lang = expr
                        result = client.call_cnki_api_raw_http(query_expr, lang=expr_lang)
                    else:
                        query_expr = expr[0]
                        result = client.call_cnki_api_raw_http(query_expr)
                else:
                    result = client.call_cnki_api_raw_http(expr)
                results[idx] = result
            finally:
                self.release(client)

        threads = []
        for idx, expr in enumerate(expressions):
            t = threading.Thread(target=worker, args=(idx, expr))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        return results

def get_token(client_id, client_secret):
    """Get CNKI OAuth 2.0 access token."""
    # 优先从配置文件获取API端点
    oauth_api_url = None
    
    try:
        config_mgr = get_config_manager()
        endpoints = config_mgr.get_cnki_api_endpoints()
        oauth_api_url = endpoints.get('oauth_url')
        logger.info(f"使用配置文件中的CNKI OAuth端点: {oauth_api_url}")
    except Exception as e:
        logger.warning(f"从配置文件读取CNKI端点失败: {e}")
    
    # 如果配置文件没有，回退到环境变量
    if not oauth_api_url:
        oauth_api_url = os.environ.get("CNKI_OAUTH_API_BASE_URL")
        logger.info(f"使用环境变量中的CNKI OAuth端点: {oauth_api_url}")
    
    if not oauth_api_url:
        logger.error("CNKI OAuth API端点未配置，请在config/conf.yaml或环境变量中设置")
        raise RuntimeError("CNKI OAuth API端点未配置")
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    try:
        response = requests.post(oauth_api_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Token request error: {e}")
        if response is not None:
            try:
                logger.error(f"Error info: {response.json()}")
            except json.JSONDecodeError:
                logger.error(f"Response not JSON: {response.text}")
        return None

def analyze_literature_metadata(papers_by_lang):
    """
    分析文献的元数据信息，包括期刊分布、作者分布、单位分布、核心期刊分布等
    
    Args:
        papers_by_lang (dict): 按语言分类的文献数据
    
    Returns:
        dict: 包含各种统计分析结果的字典
    """
    analysis_result = {
        "journal_analysis": {},        # 期刊分析
        "author_analysis": {},         # 作者分析
        "affiliation_analysis": {},    # 单位分析
        "core_journal_analysis": {},   # 核心期刊分析
        "subject_analysis": {},        # 学科分析
        "year_analysis": {},           # 年份分析
        "citation_analysis": {},       # 引用分析
        "total_statistics": {}         # 总体统计
    }
    
    all_papers = []
    total_count = 0
    
    # 合并所有语言的文献
    for lang, papers in papers_by_lang.items():
        all_papers.extend(papers)
        total_count += len(papers)
    
    if not all_papers:
        logger.warning("没有找到任何文献数据进行分析")
        return analysis_result
    
    # 1. 期刊分析
    journal_counts = {}
    journal_types = {}
    
    # 2. 作者分析
    author_counts = {}
    corresponding_authors = {}
    
    # 3. 单位分析
    affiliation_counts = {}
    
    # 4. 核心期刊分析
    core_journal_types = {}
    
    # 5. 学科分析
    subject_l1_counts = {}
    subject_l2_counts = {}
    
    # 6. 年份分析
    year_counts = {}
    
    # 7. 引用分析
    citation_data = []
    download_data = []
    
    for paper in all_papers:
        # 期刊分析
        journal = paper.get("Journal", "")
        if journal:
            journal_counts[journal] = journal_counts.get(journal, 0) + 1
        
        source_type = paper.get("Source", {}).get("type", "")
        if source_type:
            journal_types[source_type] = journal_types.get(source_type, 0) + 1
        
        # 作者分析
        authors = paper.get("Authors", [])
        if not isinstance(authors, list):
            authors = []  # 确保authors是列表类型
        
        for author in authors:
            if isinstance(author, dict):
                author_name = author.get("name", "")
                if author_name:
                    author_counts[author_name] = author_counts.get(author_name, 0) + 1
                    if author.get("corresponding", False):
                        corresponding_authors[author_name] = corresponding_authors.get(author_name, 0) + 1
        
        # 单位分析
        affiliations = paper.get("Affiliations", [])
        if not isinstance(affiliations, list):
            affiliations = []  # 确保affiliations是列表类型
        
        for aff in affiliations:
            if isinstance(aff, dict):
                aff_name = aff.get("name", "")
                if aff_name:
                    affiliation_counts[aff_name] = affiliation_counts.get(aff_name, 0) + 1
        
        # 核心期刊分析
        core_indexes = paper.get("CoreJournalIndexes", [])
        if not isinstance(core_indexes, list):
            core_indexes = []  # 确保core_indexes是列表类型
        
        for index in core_indexes:
            if isinstance(index, dict):
                index_name = index.get("name", "")
                if index_name:
                    core_journal_types[index_name] = core_journal_types.get(index_name, 0) + 1
        
        # 学科分析
        repository = paper.get("Repository", {})
        subject_l1 = repository.get("subject_category_1", "")
        subject_l2 = repository.get("subject_category_2", "")
        
        if subject_l1:
            subject_l1_counts[subject_l1] = subject_l1_counts.get(subject_l1, 0) + 1
        if subject_l2:
            subject_l2_counts[subject_l2] = subject_l2_counts.get(subject_l2, 0) + 1
        
        # 年份分析
        year = paper.get("PublicationYear", "")
        if year and str(year).strip():
            # 确保年份是字符串格式，并过滤掉无效年份
            year_str = str(year).strip()
            try:
                # 验证是否为有效年份
                year_int = int(float(year_str))
                if 1900 <= year_int <= 2030:  # 合理的年份范围
                    year_counts[str(year_int)] = year_counts.get(str(year_int), 0) + 1
            except (ValueError, TypeError):
                logger.warning(f"无效年份格式: {year}")
                continue
        
        # 引用分析
        metrics = paper.get("Metrics", {})
        citation_count = metrics.get("citation_count", 0)
        download_count = metrics.get("download_count", 0)
        
        # 确保引用数据是数字类型
        try:
            citation_count = float(citation_count) if citation_count else 0
            download_count = float(download_count) if download_count else 0
        except (ValueError, TypeError):
            citation_count = 0
            download_count = 0
        
        citation_data.append(citation_count)
        download_data.append(download_count)
    
    # 生成分析结果
    def get_top_items(data_dict, top_n=10):
        """获取出现频次最高的前N项"""
        return sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    # 期刊分析结果
    analysis_result["journal_analysis"] = {
        "top_journals": get_top_items(journal_counts, 15),
        "journal_types": dict(journal_types),
        "total_journals": len(journal_counts)
    }
    
    # 作者分析结果
    analysis_result["author_analysis"] = {
        "top_authors": get_top_items(author_counts, 20),
        "top_corresponding_authors": get_top_items(corresponding_authors, 10),
        "total_authors": len(author_counts),
        "total_corresponding_authors": len(corresponding_authors)
    }
    
    # 单位分析结果
    analysis_result["affiliation_analysis"] = {
        "top_affiliations": get_top_items(affiliation_counts, 20),
        "total_affiliations": len(affiliation_counts)
    }
    
    # 核心期刊分析结果
    analysis_result["core_journal_analysis"] = {
        "index_distribution": dict(core_journal_types),
        "total_core_journals": sum(core_journal_types.values())
    }
    
    # 学科分析结果
    analysis_result["subject_analysis"] = {
        "level1_subjects": get_top_items(subject_l1_counts, 10),
        "level2_subjects": get_top_items(subject_l2_counts, 15),
        "total_l1_subjects": len(subject_l1_counts),
        "total_l2_subjects": len(subject_l2_counts)
    }
    
    # 年份分析结果
    earliest_year = ""
    latest_year = ""
    if year_counts:
        try:
            sorted_years = sorted(year_counts.keys())
            earliest_year = sorted_years[0] if sorted_years else ""
            latest_year = sorted_years[-1] if sorted_years else ""
        except Exception as e:
            logger.warning(f"年份分析排序失败: {e}")
    
    analysis_result["year_analysis"] = {
        "year_distribution": dict(sorted(year_counts.items())) if year_counts else {},
        "earliest_year": earliest_year,
        "latest_year": latest_year,
        "year_span": len(year_counts)
    }
    
    # 引用分析结果
    if citation_data and len(citation_data) > 0:
        try:
            import math
            valid_citations = [x for x in citation_data if isinstance(x, (int, float)) and not math.isnan(x)]
            valid_downloads = [x for x in download_data if isinstance(x, (int, float)) and not math.isnan(x)]
            
            analysis_result["citation_analysis"] = {
                "total_citations": sum(valid_citations) if valid_citations else 0,
                "avg_citations": sum(valid_citations) / len(valid_citations) if valid_citations else 0,
                "max_citations": max(valid_citations) if valid_citations else 0,
                "total_downloads": sum(valid_downloads) if valid_downloads else 0,
                "avg_downloads": sum(valid_downloads) / len(valid_downloads) if valid_downloads else 0,
                "max_downloads": max(valid_downloads) if valid_downloads else 0
            }
        except Exception as e:
            logger.warning(f"引用分析计算失败: {e}")
            analysis_result["citation_analysis"] = {
                "total_citations": 0,
                "avg_citations": 0,
                "max_citations": 0,
                "total_downloads": 0,
                "avg_downloads": 0,
                "max_downloads": 0
            }
    
    # 总体统计
    analysis_result["total_statistics"] = {
        "total_papers": total_count,
        "papers_by_language": {lang: len(papers) for lang, papers in papers_by_lang.items()},
        "papers_with_core_index": sum(1 for paper in all_papers if paper.get("CoreJournalIndexes")),
        "papers_with_citations": sum(1 for paper in all_papers if paper.get("Metrics", {}).get("citation_count", 0) > 0),
        "papers_with_funds": sum(1 for paper in all_papers if paper.get("Funds"))
    }
    
    logger.info(f"文献元数据分析完成：共分析{total_count}篇文献")
    logger.info(f"涉及期刊{len(journal_counts)}种，作者{len(author_counts)}人，单位{len(affiliation_counts)}个")
    
    return analysis_result


# 移除了_generate_markdown_from_existing_info函数
# 系统现在直接使用内存中的结构化信息，不再生成中间markdown文件

def cnki_auto_search(file_path, max_query_num=None, max_paper_num=None, languages=None, session_id=None, existing_thesis_info=None):
    """
    自动化CNKI检索API，分别进行中文检索和英文检索，结果集分别处理。
    :param file_path: 输入文件路径
    :param max_query_num: 最大检索轮数（从配置文件读取）
    :param max_paper_num: 最大相关文献数（从配置文件读取）
    :param languages: 需要支持的语言列表（从配置文件读取）
    :param session_id: AI会话ID（用于并行处理）
    :param existing_thesis_info: 已有的论文结构化信息（可选，如果提供则跳过重新提取）
    :return: {
        'papers_by_lang': {lang: top_papers},  # 每种语言对应相关度最高的TopN篇文献
        'thesis_extracted_info': thesis_info   # 论文抽取的结构化信息
    }
    """
    import os
    import json
    from sentence_transformers import SentenceTransformer
    import numpy as np

    # 获取配置管理器
    config_mgr = get_config_manager()
    
    
    # 从配置文件读取参数，如果没有传入的话
    if languages is None:
        languages = config_mgr.get_supported_languages()
    if max_query_num is None:
        max_query_num = get_config('cnki_config.search_params.max_query_rounds', 5)
    if max_paper_num is None:
        max_paper_num = get_config('cnki_config.search_params.max_papers', 500)
    
    # 获取TOP文献数量
    top_papers_count = get_config('cnki_config.search_params.top_papers', 30)

    # 环境变量配置
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    # print(GOOGLE_API_KEY)

    GOOGLE_API_BASE = os.environ.get("GOOGLE_API_BASE")
    # print(f"GOOGLE_API_BASE: {GOOGLE_API_BASE}")
    
    # 获取CNKI认证信息和平台配置
    try:
        config_mgr = get_config_manager()
        endpoints = config_mgr.get_cnki_api_endpoints()
        uniplatform = endpoints.get('uniplatform')
        logger.info(f"使用配置文件中的CNKI平台标识: {uniplatform}")
    except Exception as e:
        logger.warning(f"从配置文件读取CNKI配置失败: {e}")
        uniplatform = None
    
    # 如果配置文件没有，回退到环境变量
    if not uniplatform:
        uniplatform = os.environ.get("CNKI_UNIPLATFORM")
        logger.info(f"使用环境变量中的CNKI平台标识: {uniplatform}")
    
    # 从环境变量获取认证密钥（敏感信息）
    client_id = os.environ.get("CNKI_CLIENT_ID")
    client_secret = os.environ.get("CNKI_CLIENT_SECRET")
    
    if not uniplatform or not client_id or not client_secret:
        missing_items = []
        if not uniplatform:
            missing_items.append("CNKI平台标识")
        if not client_id:
            missing_items.append("CNKI_CLIENT_ID")
        if not client_secret:
            missing_items.append("CNKI_CLIENT_SECRET")
        
        logger.error(f"CNKI配置不完整，缺少: {', '.join(missing_items)}")
        logger.error("请检查config/conf.yaml中的cnki_config配置和.env文件中的认证信息")
        raise RuntimeError(f"CNKI配置不完整，缺少: {', '.join(missing_items)}")
    if not os.path.exists(file_path):
        logger.error(f"输入文件不存在: {file_path}")
        raise FileNotFoundError(f"输入文件不存在: {file_path}")

    # AI client/session
    ai_client = get_ai_client()
    # 使用传入的session_id，如果没有则创建新的
    ai_session_id = session_id if session_id else ai_client.create_session()

    # 用大模型抽取结构化信息并生成Markdown，支持多语言
    # 首先检查是否有已有的结构化信息
    thesis_extracted_info = existing_thesis_info
    
    if thesis_extracted_info:
        logger.info("使用已有的论文结构化信息，跳过重新提取")
        logger.info(f"已有结构化信息包含字段: {list(thesis_extracted_info.keys())}")
    else:
        # 没有已有信息，需要重新抽取
        try:
            # 提取文档文本
            logger.info("开始提取文档文本...")
            if str(file_path).lower().endswith('.pdf'):
                logger.error("不支持PDF文件格式，请使用Word文档(.docx)")
                return None
            else:
                document_text = extract_text_from_word(file_path)
            
            logger.info(f"文档文本提取完成 ({len(document_text):,} 字符)")
            
            # 使用AI提取结构化信息
            logger.info("开始使用AI提取结构化信息...")
            thesis_extracted_info = extract_sections_with_ai(
                document_text, ai_client, session_id=ai_session_id, languages=languages
            )
            
            if thesis_extracted_info is None:
                logger.error("大模型未能抽取论文结构化信息。请分析app.log日志，解决错误，如果需要可以打印更详细的日志。")
                raise RuntimeError("大模型未能抽取论文结构化信息")
            else:
                logger.info(f"成功抽取论文结构化信息，包含字段: {list(thesis_extracted_info.keys())}")
                # 不再生成Markdown文件，直接使用内存中的结构化信息
        except Exception as e:
            logger.error(f"论文结构化信息抽取过程中发生异常: {str(e)}")
            logger.error(f"异常类型: {type(e).__name__}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            raise
    
    publication_cutoff = None
    if thesis_extracted_info:
        cutoff_keys = [
            'search_cutoff_date',
            'defense_date',
            'defenseDate',
            'completion_date',
            'completionDate',
            'submission_date',
            'submissionDate',
        ]
        for key in cutoff_keys:
            normalized = normalize_cnki_pt_upper(thesis_extracted_info.get(key))
            if normalized:
                publication_cutoff = normalized
                break
        if publication_cutoff:
            logger.info(f"使用 PT<= {publication_cutoff} 作为文献检索时间上限")

    # 加载本地多语言句向量模型（从配置文件读取模型名称）
    lang_model_map = {}
    for lang in languages:
        lang_key = lang.lower()
        model_config = config_mgr.get_embedding_model_config(lang_key)
        model_name = model_config.get('model_name', 
                                     'shibing624/text2vec-base-chinese' if lang == 'Chinese' 
                                     else 'sentence-transformers/all-MiniLM-L6-v2')
        lang_model_map[lang] = SentenceTransformer(model_name)

    # 用info_json抽取各语言的标题、关键词、摘要组成长文本，计算向量
    lang_vecs = {}
    for lang in languages:
        text = (
            thesis_extracted_info.get(f'{lang}Title', '') + ' ' +
            thesis_extracted_info.get(f'{lang}Keywords', '') + ' ' +
            thesis_extracted_info.get(f'{lang}Abstract', '')
        )
        lang_vecs[lang] = lang_model_map[lang].encode(text)

    # 获取token
    token = get_token(client_id, client_secret)
    access_token = token.get("access_token") if token else None
    if not access_token:
        logger.error("未能获取access_token")
        raise RuntimeError("未能获取access_token")

    # 初始化检索
    query_generator = get_query_generator(ai_client=ai_client, session_id=ai_session_id)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    top_papers_by_lang = {}

    # 获取查询间隔配置
    query_interval = get_config('cnki_config.intervals.query_interval', 2)
    round_interval = get_config('cnki_config.intervals.round_interval', 5)


    for lang in languages:
        logger.info(f"开始{lang}检索流程")
        
        # 使用内存中的结构化信息，而不是重新从文件加载
        if thesis_extracted_info:
            # 从结构化信息中提取对应语言的内容
            title = thesis_extracted_info.get(f'title_{lang.lower()[:2]}', '')
            keywords = thesis_extracted_info.get(f'keywords_{lang.lower()[:2]}', '')
            abstract = thesis_extracted_info.get(f'abstract_{lang.lower()[:2]}', '')
            research_methods = thesis_extracted_info.get('research_methods', '')
            
            # 组合成完整的论文内容用于生成检索式
            thesis_content = f"""标题: {title}
关键词: {keywords}
摘要: {abstract}
研究方法: {research_methods}"""
            
            # 直接设置论文片段内容，避免重复读取文件
            query_generator.set_thesis_fragment(thesis_content)
            logger.info(f"使用内存中的{lang}结构化信息生成检索式")
        else:
            logger.warning(f"结构化信息为空，回退到文件读取方式")
        
        # 生成该语言的检索式，不传递文件路径
        queries = query_generator.generate_cnki_queries(lang=lang)
        if not queries or not isinstance(queries, list):
            logger.error(f"{lang}未能生成查询或返回结果格式不是列表")
            continue

        pool = CNKIClientPool(uniplatform, access_token, max_clients=5)
        relevant_papers = []
        query_num = 1

        # 检索相关文献（每种语言独立流程）
        while True:
            logger.info(f"\n第{query_num}轮{lang}检索，共有{len(queries)}个检索式。")
            expressions = [item["query_string"] for item in queries if "query_string" in item]
            # 关键：传递lang参数以及时间过滤条件
            if publication_cutoff:
                concurrent_inputs = [(expr, lang, publication_cutoff) for expr in expressions]
            else:
                concurrent_inputs = [(expr, lang) for expr in expressions]
            results = pool.call_concurrent(concurrent_inputs)

            if not results or not isinstance(results, list):
                logger.error(f"{lang}未能获取检索结果或返回结果格式不是列表")
                break
            logger.info(f"{lang}所有检索结果获取成功。")

            suggestions = []
            for idx, (query, result) in enumerate(zip(queries, results)):
                logger.info(f"分析第{idx+1}个{lang}检索式：")
                # 关键：分析时也传递lang参数
                is_valid, suggestion = query_generator.analyze_cnki_qurery(
                    original_query=query["query_string"],
                    result=result,
                    lang=lang
                )
                logger.info(f"{lang}检索式: {query['query_string']}")
                logger.info(f"{lang}分析建议: {suggestion}")
                suggestions.append(suggestion)
                if is_valid:
                    items = result.get("searchResultsCollections", {}).get("items", [])
                    relevant_papers.extend(items)
                    logger.info(f"第{idx+1}个{lang}检索有效，已添加{len(items)}条相关文献。")
                else:
                    logger.info(f"第{idx+1}个{lang}检索无效，未添加文献。")

            logger.info(f"当前已收集到{lang}相关文献 {len(relevant_papers)} 条。")

            if len(relevant_papers) >= max_paper_num:
                logger.info(f"收集到{lang}相关文献超出最大数量，结束检索。")
                break
            if query_num >= max_query_num:
                logger.info(f"{lang}检索轮数超出最大次数，结束检索。")
                break

            # 关键：优化检索式时也传递lang参数
            new_queries = query_generator.regenerate_cnki_queries(
                suggestions=suggestions,
                lang=lang
            )
            logger.info(f"{lang}优化后的检索式：{new_queries}")

            queries = new_queries
            query_num += 1
            # 使用配置文件中的轮次间隔
            time.sleep(round_interval)

        logger.info(f"最终共收集到{lang}相关文献 {len(relevant_papers)} 条。")

        # 使用配置文件中的文件名模式保存相关文献列表
        output_dir = config_mgr.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在
        
        relevant_papers_pattern = config_mgr.get_file_pattern('relevant_papers')
        dedup_papers_pattern = config_mgr.get_file_pattern('dedup_papers')
        
        relevant_papers_filename = relevant_papers_pattern.format(base_name=base_name, lang=lang)
        dedup_papers_filename = dedup_papers_pattern.format(base_name=base_name, lang=lang)
        
        relevant_papers_path = os.path.join(output_dir, relevant_papers_filename)
        dedup_papers_path = os.path.join(output_dir, dedup_papers_filename)
        
        if os.path.exists(relevant_papers_path):
            os.remove(relevant_papers_path)
        with open(relevant_papers_path, "w", encoding="utf-8") as f:
            json.dump(relevant_papers, f, ensure_ascii=False, indent=2)
        logger.info(f"{lang}相关文献列表已保存到 {relevant_papers_path}")
        if os.path.exists(dedup_papers_path):
            os.remove(dedup_papers_path)
        pandas_remove_duplicates(relevant_papers_path, dedup_papers_path)
        logger.info(f"{lang}去重后的相关文献列表已保存到 {dedup_papers_path}")

        # 读取去重后的相关文献
        with open(dedup_papers_path, "r", encoding="utf-8") as f:
            relevant_papers = json.load(f)

        # 检查是否有相关文献
        if not relevant_papers:
            logger.warning(f"{lang}去重后没有相关文献，跳过相关度分析")
            top_papers_by_lang[lang] = []
            continue

        # 相关度分析
        def get_text(paper):
            # 更健壮的文本提取，支持新的字段结构
            title = paper.get('Title', '')
            keywords = paper.get('KeyWords', '') or paper.get('DetailedKeywords', '')
            abstract = paper.get('Abstract', '')
            
            # 如果DetailedKeywords是列表，转换为字符串
            if isinstance(keywords, list):
                keywords = ' '.join(keywords)
            
            return f"{title} {keywords} {abstract}".strip()
    
        try:
            docs = [get_text(p) for p in relevant_papers]
            # 过滤空文档
            valid_papers = []
            valid_docs = []
            for i, doc in enumerate(docs):
                if doc.strip():  # 只保留非空文档
                    valid_papers.append(relevant_papers[i])
                    valid_docs.append(doc)
            
            if not valid_docs:
                logger.warning(f"{lang}没有有效的文档内容，跳过相关度分析")
                top_papers_by_lang[lang] = []
                continue
                
            doc_vecs = np.vstack([lang_model_map[lang].encode(doc) for doc in valid_docs])
            relevant_papers = valid_papers  # 使用过滤后的文献列表
            
        except Exception as e:
            logger.error(f"{lang}文档向量化失败: {str(e)}")
            top_papers_by_lang[lang] = []
            continue

        # 计算余弦相似度
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        similarities = [cosine_similarity(lang_vecs[lang], vec) for vec in doc_vecs]
        top_idx = np.argsort(similarities)[::-1]
        top_papers = []
        num_papers = min(top_papers_count, len(relevant_papers))
        for idx in top_idx[:num_papers]:
            paper = relevant_papers[idx]
            print(f"[{lang}] 相关度: {similarities[idx]:.3f}，标题: {paper.get('Title', '')}")
            logger.info(f"[{lang}] 相关度: {similarities[idx]:.3f}，标题: {paper.get('Title', '')}")
            top_papers.append(paper)
        logger.info(f"{lang}相关文献列表已生成。")
        
        # 使用配置文件中的文件名模式保存TOP文献
        output_dir = config_mgr.get_output_dir()
        os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在
        
        top_papers_pattern = config_mgr.get_file_pattern('top_papers')
        top_filename = top_papers_pattern.format(base_name=base_name, lang=lang, top_count=top_papers_count)
        top_filepath = os.path.join(output_dir, top_filename)
        if os.path.exists(top_filepath):
            os.remove(top_filepath)
        with open(top_filepath, "w", encoding="utf-8") as f:
            json.dump(top_papers, f, ensure_ascii=False, indent=2)
        logger.info(f"{lang} TOP{top_papers_count}相关文献已保存到 {top_filepath}")
        top_papers_by_lang[lang] = top_papers

    # 进行文献元数据分析
    logger.info("开始进行文献元数据分析...")
    literature_metadata_analysis = analyze_literature_metadata(top_papers_by_lang)
    logger.info("文献元数据分析完成")

    # 返回包含论文信息、抽取信息和元数据分析的结构化结果
    return {
        'papers_by_lang': top_papers_by_lang,
        'thesis_extracted_info': thesis_extracted_info,
        'literature_metadata_analysis': literature_metadata_analysis
    }

if __name__ == '__main__':
    import sys
    import os

    print("Usage: python cnki_client_pool.py <file_path>")

    if len(sys.argv) != 2:
        print("参数错误：请提供输入文件路径。")
        logger.error("参数错误：命令行参数数量不足。")
        sys.exit(1)

    file_path = sys.argv[1]

    # 从配置文件读取支持的语言
    config_mgr = get_config_manager()
    languages = config_mgr.get_supported_languages()

    try:
        search_results = cnki_auto_search(file_path, languages=languages)
        papers_by_lang = search_results['papers_by_lang']
        thesis_extracted_info = search_results['thesis_extracted_info']
        
        for lang, papers in papers_by_lang.items():
            print(f"{lang}强相关文献 {len(papers)} 条")
            logger.info(f"{lang}强相关文献 {len(papers)} 条")
            
        if thesis_extracted_info:
            print("论文结构化信息抽取成功")
            logger.info("论文结构化信息抽取成功")
        else:
            print("论文结构化信息抽取失败")
            logger.warning("论文结构化信息抽取失败")
    except Exception as e:
        print(f"检索失败: {e}")
        logger.error(f"检索失败: {e}")



