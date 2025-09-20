"""
配置管理模块 - Configuration Management Module
用于读取和管理系统配置信息
"""

import yaml
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config/conf.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self._config = None
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            # 尝试多个可能的配置文件位置
            possible_paths = [
                self.config_path,  # 用户指定的路径
                "config/conf.yaml",  # 新的标准位置
                "conf.yaml",  # 旧的位置（向后兼容）
                os.path.join(os.path.dirname(__file__), "../../config/conf.yaml"),  # 相对于包的位置
            ]
            
            config_file = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_file = path
                    break
            
            if not config_file:
                raise FileNotFoundError(f"配置文件不存在，尝试过的路径: {possible_paths}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            
            logger.info(f"成功加载配置文件: {config_file}")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值，支持嵌套路径
        
        Args:
            key_path: 配置键路径，如 'ai_models.language_models.gemini.model_name'
            default: 默认值
            
        Returns:
            配置值
        """
        if self._config is None:
            return default
        
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_ai_model_config(self, api_type: str) -> Dict[str, Any]:
        """
        获取AI模型配置
        
        Args:
            api_type: API类型，'gemini' 或 'openai'
            
        Returns:
            模型配置字典
        """
        return self.get(f'ai_models.language_models.{api_type}', {})
    
    def get_embedding_model_config(self, language: str) -> Dict[str, Any]:
        """
        获取嵌入模型配置
        
        Args:
            language: 语言类型，'chinese' 或 'english'
            
        Returns:
            嵌入模型配置字典
        """
        return self.get(f'ai_models.embedding_models.{language}', {})
    
    def get_cnki_config(self) -> Dict[str, Any]:
        """获取CNKI配置"""
        return self.get('cnki_config', {})
    
    def get_cnki_api_endpoints(self) -> Dict[str, str]:
        """
        获取CNKI API端点配置
        优先从配置文件读取，允许环境变量覆盖
        
        Returns:
            包含API端点的字典
        """
        # 从配置文件获取默认值
        endpoints = self.get('cnki_config.api_endpoints', {})
        
        # 允许环境变量覆盖
        result = {
            'oauth_url': os.getenv('CNKI_OAUTH_API_BASE_URL', 
                                 endpoints.get('oauth_url', 'https://api.cnki.net/oauth/token')),
            'search_url': os.getenv('CNKI_SEARCH_API_BASE_URL', 
                                  endpoints.get('search_url', 'https://api.cnki.net/v1/search')),
            'uniplatform': os.getenv('CNKI_UNIPLATFORM', 
                                   endpoints.get('uniplatform', 'NZKPT'))
        }
        
        return result
    
    def get_ai_api_config(self, api_type: str) -> Dict[str, Any]:
        """
        获取AI API配置，包括端点和参数
        优先从配置文件读取，允许环境变量覆盖
        
        Args:
            api_type: API类型，'gemini' 或 'openai'
            
        Returns:
            AI API配置字典
        """
        config = self.get_ai_model_config(api_type)
        
        # 允许环境变量覆盖API端点
        if api_type == 'openai':
            api_base = os.getenv('GOOGLE_API_BASE', config.get('api_base', ''))
            if api_base:
                config = config.copy()  # 创建副本避免修改原配置
                config['api_base'] = api_base
        
        return config
    
    def get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        return self.get('supported_languages', ['Chinese', 'English'])
    
    def get_similarity_thresholds(self) -> Dict[str, float]:
        """获取相关度阈值配置"""
        return self.get('similarity_thresholds', {
            'high_relevance': 0.8,
            'medium_relevance': 0.6,
            'low_relevance': 0.4
        })
    
    def get_output_config(self) -> Dict[str, Any]:
        """获取输出配置"""
        return self.get('output_config', {})
    
    def get_file_pattern(self, pattern_name: str) -> str:
        """
        获取文件命名模式
        
        Args:
            pattern_name: 模式名称，如 'relevant_papers'
            
        Returns:
            文件命名模式字符串
        """
        return self.get(f'file_naming.output_patterns.{pattern_name}', 
                       f"{{base_name}}_{pattern_name}_{{lang}}.json")
    
    def get_top_papers_count(self) -> int:
        """
        获取TopN的N值
        
        Returns:
            TopN中的N值，默认为30
        """
        return self.get('cnki_config.search_params.top_papers', 30)
    
    def get_directory_config(self, dir_type: str) -> str:
        """
        获取目录配置
        
        Args:
            dir_type: 目录类型，如 'input_dir', 'output_dir', 'logs_dir' 等
            
        Returns:
            目录路径
        """
        return self.get(f'directories.{dir_type}', '')
    
    def get_input_dir(self) -> str:
        """获取输入目录路径"""
        return self.get_directory_config('input_dir')
    
    def get_output_dir(self) -> str:
        """获取输出目录路径"""
        return self.get_directory_config('output_dir')
    
    def get_logs_dir(self) -> str:
        """获取日志目录路径"""
        return self.get_directory_config('logs_dir')
    
    def get_config_dir(self) -> str:
        """获取配置目录路径"""
        return self.get_directory_config('config_dir')
    
    def get_docs_dir(self) -> str:
        """获取文档目录路径"""
        return self.get_directory_config('docs_dir')

    def get_reports_dir(self) -> str:
        """获取报告文档目录路径"""
        return self.get_directory_config('reports_dir')

    def get_tools_dir(self) -> str:
        """获取工具脚本目录路径"""
        return self.get_directory_config('tools_dir')

    def get_analysis_output_dir(self) -> str:
        """获取分析输出目录路径"""
        return self.get_directory_config('analysis_output_dir')

    def get_structured_output_dir(self) -> str:
        """获取结构化输出目录路径"""
        return self.get_directory_config('structured_output_dir')
    
    def get_temp_dir(self) -> str:
        """获取临时目录路径"""
        return self.get_directory_config('temp_dir')
    
    def get_supported_formats(self) -> list:
        """获取支持的文件格式列表"""
        return self.get('file_naming.supported_formats', ['.docx', '.pdf', '.md'])
    
    def get_log_file_name(self) -> str:
        """获取日志文件名"""
        return self.get('file_naming.log_file', 'app.log')
    
    def get_log_file_path(self) -> str:
        """获取完整的日志文件路径"""
        logs_dir = self.get_logs_dir()
        log_file = self.get_log_file_name()
        return os.path.join(logs_dir, log_file) if logs_dir else log_file
    
    def get_report_config(self) -> Dict[str, Any]:
        """获取报告配置"""
        return self.get('file_naming.report_config', {
            'default_format': 'markdown',
            'include_sections': ['summary', 'innovation_analysis', 'related_papers', 'recommendations'],
            'auto_generate': True
        })
    
    def get_evaluation_report_pattern(self) -> str:
        """获取评估报告文件名模式"""
        return self.get_file_pattern('evaluation_report')
    
    def generate_output_filename(self, input_file: str, pattern_type: str, **kwargs) -> str:
        """
        生成输出文件名
        
        Args:
            input_file: 输入文件路径
            pattern_type: 模式类型
            **kwargs: 额外的格式化参数
            
        Returns:
            生成的输出文件名
        """
        import os
        from pathlib import Path
        
        # 获取基础文件名（不含扩展名）
        base_name = Path(input_file).stem
        
        # 获取命名模式
        if pattern_type == 'evaluation_report':
            pattern = self.get_evaluation_report_pattern()
        else:
            pattern = self.get_file_pattern(pattern_type)
        
        # 准备格式化参数
        format_params = {
            'base_name': base_name,
            'top_count': self.get_top_papers_count(),
            **kwargs
        }
        
        # 格式化文件名
        return pattern.format(**format_params)
    
    def update_config(self, key_path: str, value: Any) -> None:
        """
        更新配置值
        
        Args:
            key_path: 配置键路径
            value: 新值
        """
        if self._config is None:
            self._config = {}
        
        keys = key_path.split('.')
        current = self._config
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 设置值
        current[keys[-1]] = value
        logger.info(f"配置已更新: {key_path} = {value}")
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            logger.info(f"配置已保存到: {self.config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取完整配置字典"""
        return self._config or {}


# 全局配置管理器实例
_config_manager = None

def get_config_manager(config_path: str = "config/conf.yaml") -> ConfigManager:
    """
    获取全局配置管理器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigManager实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager

def reset_config_manager():
    """重置全局配置管理器实例"""
    global _config_manager
    _config_manager = None

def get_config(key_path: str, default: Any = None) -> Any:
    """
    快捷方法获取配置值
    
    Args:
        key_path: 配置键路径
        default: 默认值
        
    Returns:
        配置值
    """
    return get_config_manager().get(key_path, default)
