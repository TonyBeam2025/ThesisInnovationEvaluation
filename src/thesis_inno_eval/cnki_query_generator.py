"""
CNKI Query Generator

A professional academic analysis assistant and CNKI search expert that generates
targeted CNKI professional search queries based on thesis fragments.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

from .ai_client import get_ai_client, AIResponse, ConcurrentAIClient


logger = logging.getLogger(__name__)

class CNKIQueryGeneratorError(Exception):
    """Custom exception for CNKI Query Generator errors."""
    pass


class CNKIQueryGenerator:
    """
    A thread-safe class for generating CNKI search queries from thesis fragments.

    This class uses the Gemini AI model to analyze thesis content and generate
    multiple targeted CNKI search queries with proper syntax.

    Note:
        This class is designed for concurrent (multi-threaded or async) processing.
        Each instance is independent and thread-safe. The underlying
        ConcurrentAIClient is also designed for concurrent use.
    """

    SYSTEM_INSTRUCTION = """
        你是一名专业的学术分析助手和CNKI检索专家。你的任务是基于提供的学位论文片段，
        参考主题词提取方法及检索策略，并严格遵循知网（CNKI）的专业检索规则，
        生成多个（至少3-5个）有针对性的CNKI专业检索式，以辅助评估论文的创新性。
    """

    DEFAULT_STRATEGY_FILE = 'config/strategy.txt'
    DEFAULT_RULES_FILE = 'config/rules.txt'

    def __init__(
        self,
        ai_client: Optional[ConcurrentAIClient] = None,
        session_id: Optional[str] = None
    ) -> None:
        """Initialize the CNKI Query Generator with optional shared AI client and session."""
        self._ai_client: ConcurrentAIClient = ai_client or get_ai_client()
        self._session_id: str = session_id or self._ai_client.create_session()
        self._thesis_fragment = ''
        self._theme_extraction_strategy = ''
        self._cnki_syntax_rules = ''
        self._load_strategy_file()
        self._load_rules_file()

    def _load_file_content(self, file_path: Union[str, Path]) -> str:
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                logger.info(f"Successfully loaded content from: {file_path}")
                return content
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            raise CNKIQueryGeneratorError(f"Failed to load file {file_path}: {e}")

    def _load_strategy_file(self, file_path: Optional[Union[str, Path]] = None) -> None:
        path = file_path or self.DEFAULT_STRATEGY_FILE
        try:
            self._theme_extraction_strategy = self._load_file_content(path)
        except CNKIQueryGeneratorError:
            logger.warning(f"Could not load strategy file: {path}")
            self._theme_extraction_strategy = ""

    def _load_rules_file(self, file_path: Optional[Union[str, Path]] = None) -> None:
        path = file_path or self.DEFAULT_RULES_FILE
        try:
            self._cnki_syntax_rules = self._load_file_content(path)
        except CNKIQueryGeneratorError:
            logger.warning(f"Could not load rules file: {path}")
            self._cnki_syntax_rules = ""

    def load_thesis_fragment(self, file_path: Union[str, Path]) -> None:
        self._thesis_fragment = self._load_file_content(file_path)

    def set_thesis_fragment(self, content: str) -> None:
        self._thesis_fragment = content.strip()
        logger.info("Thesis fragment set directly")

    def set_strategy_content(self, content: str) -> None:
        self._theme_extraction_strategy = content.strip()
        logger.info("Strategy content set directly")

    def set_rules_content(self, content: str) -> None:
        self._cnki_syntax_rules = content.strip()
        logger.info("Rules content set directly")

    def _generate_prompt(self, lang='Chinese') -> str:
        """
        支持多语言检索，lang为'Chinese'或'English'。
        """
        if not self._thesis_fragment:
            raise CNKIQueryGeneratorError("Thesis fragment is required but not provided")

        # 多语言系统指令和步骤
        if lang == 'English':
            system_instruction = (
                "You are a professional academic analysis assistant and CNKI search expert. "
                "Your task is to generate multiple (at least 3-5) targeted CNKI professional search queries "
                "in English based on the provided thesis fragment, referring to subject term extraction methods "
                "and search strategies, and strictly following CNKI's professional search rules, "
                "to assist in evaluating the innovation of the thesis."
            )
            description_tip = "Provide a brief English description for each query."
            steps = [
                "1. Carefully read the thesis fragment to identify its core research questions, main research objects/key concepts, and adopted research methods/technologies.",
                "2. Refer to the subject term extraction methods and search strategies to extract effective search terms (including core concepts, methods, synonyms, related terms, etc.) from the thesis content.",
                "3. According to the combination principles in the strategy (such as core concept combination, method and object combination, etc.), conceive different search ideas.",
                "4. Strictly follow the CNKI professional search rules, including field codes (such as SU, KY, AB, FT, etc.), matching operators (=, %, %=), logical operators (AND, OR, NOT), composite operators (*, +, -), and necessary position descriptors. Only use composite operators within fields, do not use logical operators within fields. Transform the conceived search ideas into valid CNKI professional search queries.",
                "5. Generate at least 3 to 4 different queries, each targeting different aspects of the thesis (such as core concept combinations, specific method applications, problem context combinations, etc.).",
                f"6. {description_tip}",
                "7. Please output the generated queries as a strict JSON array. Each element in the array should be an object containing 'description' (query description) and 'query_string' (CNKI query string)."
            ]
            prompt = f"""{system_instruction}

Here is the thesis fragment:
{self._thesis_fragment}

Here are the subject term extraction methods and search strategies:
{self._theme_extraction_strategy}

Here are the CNKI professional search rules:
{self._cnki_syntax_rules}

Please follow the instructions below:
{chr(10).join(steps)}

Please output a JSON array directly, without any additional explanation.

Example output format (strictly follow this structure):
"""
        else:
            system_instruction = self.SYSTEM_INSTRUCTION
            description_tip = "为每个生成的检索式提供一个简要的中文注释或描述，说明其目的。"
            steps = [
                "1. 仔细阅读学位论文片段，识别其核心研究问题、主要研究对象/关键概念和采用的研究方法/技术。",
                "2. 参考主题词提取方法及检索策略，思考如何从论文内容中提炼出有效的检索词（包括核心概念、方法、同义词、近义词等）。",
                "3. 依据策略中的组合原则（如核心概念组合、方法与对象组合等），构思不同的检索思路。",
                "4. 严格遵循知网专业检索规则中定义的字段代码（如 SU, KY, AB, FT等）、匹配运算符（=, %, %=）、逻辑运算符（AND, OR, NOT）、复合运算符（*, +, -）以及必要的位置描述符，字段内只能用复合运算符，一定不要用逻辑运算符，将构思的检索思路转化为合法的CNKI专业检索式。",
                "5. 生成至少 3 到 4 个不同的检索式，每个检索式应针对论文的不同方面（如核心概念组合、特定方法应用、问题情境结合等）。",
                f"6. {description_tip}",
                "7. 请以严格的JSON格式输出生成的检索式列表。JSON数组中的每个元素应该是一个对象，包含 \"description\" (检索式描述) 和 \"query_string\" (CNKI检索式字符串)。"
            ]
            prompt = f"""{system_instruction}

以下是学位论文片段：
{self._thesis_fragment}

以下是主题词提取方法及检索策略：
{self._theme_extraction_strategy}

以下是知网专业检索规则：
{self._cnki_syntax_rules}

请根据上述输入，执行以下步骤：
{chr(10).join(steps)}

请直接输出JSON数组，不要包含任何其他说明文字。

示例输出格式（请严格遵循此结构）：
"""
        return prompt

    def generate_cnki_queries(
        self,
        thesis_fragment_file: Optional[Union[str, Path]] = None,
        ai_client: Optional[ConcurrentAIClient] = None,
        session_id: Optional[str] = None,
        lang: str = 'Chinese'
    ) -> List[Dict[str, str]]:
        """
        Generate CNKI queries from the thesis fragment.
        支持多语言，lang为'Chinese'或'English'。

        Args:
            thesis_fragment_file: Optional path to a thesis fragment file. If provided, loads and uses it.
            ai_client: Optionally override the AI client for this call.
            session_id: Optionally override the AI session for this call.
            lang: 检索语言，'Chinese'或'English'

        Returns:
            List of dicts with 'description' and 'query_string'.

        Raises:
            CNKIQueryGeneratorError: If generation fails.
        """
        # 只有在提供文件路径时才加载文件
        if thesis_fragment_file:
            self.load_thesis_fragment(thesis_fragment_file)
        
        # 检查是否有论文内容（可能通过文件加载或直接设置）
        if not self._thesis_fragment:
            raise CNKIQueryGeneratorError(
                "No thesis content available. Please either provide thesis_fragment_file "
                "or use set_thesis_fragment() to set content directly."
            )
            
        prompt = self._generate_prompt(lang=lang)
        client = ai_client or self._ai_client
        sid = session_id or self._session_id
        try:
            response: AIResponse = client.send_message(
                prompt, session_id=sid
            )
            result = response.content.strip()
            logger.info(f"Raw Gemini response: {result}")
            if not result:
                logger.error("Gemini response is empty.")
                raise CNKIQueryGeneratorError("Gemini response is empty.")

            if result.startswith("```json") and result.endswith("```"):
                result = result.split("\n", 1)[1].rsplit("\n", 1)[0]
                
            queries = json.loads(result)
            if not isinstance(queries, list):
                raise ValueError("Response is not a list")
            
            # 修复和验证查询格式
            for q in queries:
                if not isinstance(q, dict) or "description" not in q:
                    raise ValueError("Invalid query format in response")
                
                # 处理字段名差异：将"query"重命名为"query_string"
                if "query" in q and "query_string" not in q:
                    q["query_string"] = q.pop("query")
                
                if "query_string" not in q:
                    raise ValueError("Invalid query format in response")
            
            return queries
        except Exception as e:
            logger.error(f"Failed to generate CNKI queries: {e}")
            raise CNKIQueryGeneratorError(f"Failed to generate CNKI queries: {e}")

    def regenerate_cnki_queries(
        self,
        suggestions: list,
        ai_client: Optional[ConcurrentAIClient] = None,
        session_id: Optional[str] = None,
        lang: str = 'Chinese'
    ) -> list:
        """
        根据分析结果自动优化并重新生成CNKI检索式，支持中文和英文多语言。

        Args:
            suggestions: 分析结果列表，包含上一次检索的结果分析。
            ai_client: 可选，AI客户端
            session_id: 可选，AI会话ID
            lang: 检索语言，'Chinese'或'English'

        Returns:
            新的检索式列表
        """
        # 多语言优化提示
        if lang == 'English':
            optimize_prompt = (
                f"The analysis of the previous search results is as follows:\n{suggestions}\n\n"
                "Please optimize the search strategy based on the above analysis, regenerate 3-4 improved CNKI search queries in English, "
                "and strictly output a JSON array. Each element should contain 'description' and 'query_string' fields."
            )
        else:
            optimize_prompt = (
                f"上一次检索的结果分析如下：\n{suggestions}\n\n"
                "请根据上述分析优化检索策略，重新生成3-4个更优的中文CNKI检索式，并严格输出JSON数组，每个元素包含'description'和'query_string'字段。"
            )

        client = ai_client or self._ai_client
        sid = session_id or self._session_id
        try:
            response: AIResponse = client.send_message(
                optimize_prompt, session_id=sid
            )
            result = response.content.strip()
            logger.info(f"Raw Gemini response (regenerate): {result}")
            if not result:
                logger.error("Gemini response is empty.")
                raise CNKIQueryGeneratorError("Gemini response is empty.")

            if result.startswith("```json") and result.endswith("```"):
                result = result.split("\n", 1)[1].rsplit("\n", 1)[0]

            queries = json.loads(result)
            if not isinstance(queries, list):
                raise ValueError("Response is not a list")
            
            # 修复和验证查询格式
            for q in queries:
                if not isinstance(q, dict) or "description" not in q:
                    raise ValueError("Invalid query format in response")
                
                # 处理字段名差异：将"query"重命名为"query_string"
                if "query" in q and "query_string" not in q:
                    q["query_string"] = q.pop("query")
                
                if "query_string" not in q:
                    raise ValueError("Invalid query format in response")
            
            return queries
        except Exception as e:
            logger.error(f"Failed to regenerate CNKI queries: {e}")
            raise CNKIQueryGeneratorError(f"Failed to regenerate CNKI queries: {e}")

    def analyze_cnki_qurery(
        self,
        original_query: str,
        result: dict,
        lang: str = 'Chinese'
    ):
        """
        检验CNKI检索结果并根据分析自动调整检索策略，支持中文和英文多语言模式。
        :param original_query: 原始检索式字符串
        :param result: dict The restructured JSON data.（如rebuild_search_results的输出）
        :param lang: 检索语言，'Chinese'或'English'
        :return: (is_valid, suggestion)
        """
        items = result.get("searchResultsCollections", {}).get("items", [])
        total = result.get("searchResultsCollections", {}).get("total", 0)

        if lang == 'English':
            suggestion = original_query
            # 1. Check if there are results
            if total == 0 or not items:
                suggestion += "\nNo search results. Suggestions for expansion:\n"
                suggestion += "- Add synonyms or related terms, reduce specificity\n"
                suggestion += "- Use broader or related terms\n"
                suggestion += "- Simplify logic, reduce number of concepts\n"
                return False, suggestion
            # 2. Check if results are too many
            elif total > 200:
                suggestion = "Too many search results. Suggestions for narrowing:\n"
                suggestion += "- Increase specificity of search terms\n"
                suggestion += "- Use logical AND to combine concepts\n"
                suggestion += "- Use logical NOT to exclude irrelevant items\n"
                return False, suggestion
            # 3. Valid search
            else:
                suggestion = "Valid search. Closely related literature found. You may further use classification search, other fields, or add new data for cross-validation."
                return True, suggestion
        else:
            suggestion = original_query
            # 1. 检查是否有结果
            if total == 0 or not items:
                suggestion += "检索结果为0，建议进行扩检：\n"
                suggestion += "- 增加同义词、近义词，降低检索词专指度\n"
                suggestion += "- 用上位词或相关词放宽检索\n"
                suggestion += "- 简化逻辑关系，减少概念数\n"
                return False, suggestion
            # 2. 检查结果是否过多
            elif total > 200:
                suggestion = "检索结果过多，建议进行缩检：\n"
                suggestion += "- 提高检索词专指度\n"
                suggestion += "- 用逻辑“与”限定主题概念\n"
                suggestion += "- 用逻辑“非”排除无关项\n"
                return False, suggestion
            # 3. 检索有效
            else:
                suggestion = "检索有效，发现密切相关文献。可进一步用分类检索、其他字段或增加新数据进行交叉检验。"
                return True, suggestion

# Convenience function for easy access
def get_query_generator(
    ai_client: Optional[ConcurrentAIClient] = None,
    session_id: Optional[str] = None
) -> CNKIQueryGenerator:
    """Create a new CNKIQueryGenerator instance (thread-safe, supports shared AI client/session)."""
    return CNKIQueryGenerator(ai_client=ai_client, session_id=session_id)
