# 代码完善建议 - extract_sections_with_ai.py

# 1. 添加缺失的 JSON 清理函数
def _clean_json_content(json_str: str) -> str:
    """清理JSON字符串，移除常见的格式问题"""
    import re
    
    # 移除注释
    json_str = re.sub(r'//.*?\n', '\n', json_str)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    
    # 修复常见的JSON格式问题
    json_str = re.sub(r',\s*}', '}', json_str)  # 移除末尾逗号
    json_str = re.sub(r',\s*]', ']', json_str)  # 移除数组末尾逗号
    
    # 修复引号问题
    json_str = re.sub(r'([{,]\s*)(\w+):', r'\1"\2":', json_str)  # 为键添加引号
    
    return json_str.strip()

# 2. 统一返回值类型的修复建议
class ReturnValueFixes:
    """返回值一致性修复建议"""
    
    @staticmethod
    def fix_theoretical_framework_return():
        """修复理论框架提取的返回值不一致问题"""
        # 将 _analyze_theoretical_framework_with_ai 的返回值统一为字典类型
        # 失败时返回标准空字典而不是 None
        
        # 修复前：
        # return None
        
        # 修复后：
        return {
            'core_theories': [],
            'theoretical_models': [],
            'conceptual_foundations': [],
            'theoretical_contributions': []
        }
    
    @staticmethod
    def fix_author_contributions_return():
        """修复作者贡献提取的返回值不一致问题"""
        # 修复前：
        # return None
        
        # 修复后：
        return {
            'contribution_statement': '',
            'research_contributions': [],
            'publication_contributions': [],
            'innovation_points': []
        }
    
    @staticmethod
    def fix_main_extractor_return():
        """修复主提取方法的返回值"""
        # 为 extract_sections_with_pro_strategy 添加标准空结果返回
        # 失败时返回包含所有必需字段的空字典而不是 None
        
        standard_empty_result = {
            'thesis_number': '',
            'title_cn': '',
            'title_en': '',
            'author_cn': '',
            'author_en': '',
            'supervisor': '',
            'degree_type': '',
            'major': '',
            'submission_date': '',
            'institution': '',
            'abstract_cn': '',
            'abstract_en': '',
            'keywords_cn': '',
            'keywords_en': '',
            'references': []
        }
        return standard_empty_result

# 3. 错误处理增强建议
class ErrorHandlingImprovements:
    """错误处理改进建议"""
    
    @staticmethod
    def enhanced_json_parsing(json_str: str) -> dict:
        """增强的JSON解析，包含多级回退策略"""
        import json
        import re
        
        # 第一级：直接解析
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # 第二级：清理后解析
        try:
            cleaned = _clean_json_content(json_str)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # 第三级：使用正则表达式提取基本信息
        try:
            # 提取字符串值
            string_pattern = r'"([^"]+)":\s*"([^"]*)"'
            array_pattern = r'"([^"]+)":\s*\[(.*?)\]'
            
            result = {}
            
            # 提取字符串字段
            for match in re.finditer(string_pattern, json_str):
                key, value = match.groups()
                result[key] = value
            
            # 提取数组字段
            for match in re.finditer(array_pattern, json_str, re.DOTALL):
                key, array_content = match.groups()
                # 简单的数组解析
                items = re.findall(r'"([^"]*)"', array_content)
                result[key] = items
            
            return result
        except Exception:
            # 最后回退：返回空字典
            return {}
    
    @staticmethod
    def add_timeout_protection():
        """为AI调用添加超时保护"""
        import asyncio
        from concurrent.futures import TimeoutError
        
        # 建议为所有AI调用添加超时机制
        # 防止长时间等待导致程序hang住
        timeout_seconds = 30
        
        # 示例实现
        try:
            # response = await asyncio.wait_for(
            #     self.ai_client.send_message(prompt),
            #     timeout=timeout_seconds
            # )
            pass
        except TimeoutError:
            print(f"   ⚠️ AI调用超时 ({timeout_seconds}秒)")
            return None

# 4. 性能优化建议
class PerformanceOptimizations:
    """性能优化建议"""
    
    @staticmethod
    def optimize_text_processing():
        """优化文本处理性能"""
        # 1. 使用编译后的正则表达式
        import re
        
        # 编译常用的正则表达式
        COMPILED_PATTERNS = {
            'chapter': re.compile(r'第[一二三四五六七八九十\d]+章', re.IGNORECASE),
            'section': re.compile(r'[0-9]+\.[0-9]+', re.IGNORECASE),
            'reference': re.compile(r'\[\d+\]', re.IGNORECASE)
        }
        
        # 2. 分块处理大文档
        def process_large_document(text: str, chunk_size: int = 10000):
            """分块处理大文档，避免内存溢出"""
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            return chunks
        
        # 3. 缓存AI分析结果
        # 避免重复分析相同的内容块
    
    @staticmethod
    def optimize_ai_calls():
        """优化AI调用策略"""
        # 1. 批量处理小块内容
        # 2. 实现智能重试机制
        # 3. 添加结果缓存
        pass

# 5. 代码质量改进建议
class CodeQualityImprovements:
    """代码质量改进"""
    
    @staticmethod
    def add_type_hints():
        """添加更完整的类型注解"""
        from typing import Dict, List, Optional, Union, Any
        
        # 为所有方法添加完整的类型注解
        # 提高代码可读性和IDE支持
    
    @staticmethod
    def add_docstring_standards():
        """标准化文档字符串"""
        # 使用一致的docstring格式
        # 包含参数说明、返回值说明、异常说明
        
        example = '''
        def extract_method(self, text: str, options: Dict[str, Any]) -> Dict[str, Any]:
            """
            提取论文信息的核心方法
            
            Args:
                text (str): 论文全文文本
                options (Dict[str, Any]): 提取选项配置
                
            Returns:
                Dict[str, Any]: 提取的论文信息字典
                
            Raises:
                ValueError: 当输入文本为空时
                AIClientError: 当AI客户端不可用时
                
            Example:
                >>> extractor = ThesisExtractor()
                >>> result = extractor.extract_method(text, {})
                >>> print(result['title_cn'])
            """
            pass
        '''
    
    @staticmethod
    def add_configuration_validation():
        """添加配置验证"""
        # 在初始化时验证配置的完整性
        # 提前发现配置问题，避免运行时错误
        pass

# 总结：优先级排序的修复建议
PRIORITY_FIXES = [
    "1. 🔴 高优先级 - 修复 _clean_json_content 未定义问题",
    "2. 🟡 中优先级 - 统一返回值类型（None vs 空值）",
    "3. 🟢 低优先级 - 添加超时保护和性能优化",
    "4. 🔵 改进建议 - 完善类型注解和文档"
]

print("代码完善建议已生成！")
print("主要问题：")
for fix in PRIORITY_FIXES:
    print(f"  {fix}")
