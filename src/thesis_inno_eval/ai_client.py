import json
import asyncio
import threading
from typing import Optional, Dict, Any, List, Union
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from contextlib import asynccontextmanager
import requests
from dotenv import load_dotenv
import os
import logging
from queue import Queue
import time
from abc import ABC, abstractmethod

# Import configuration manager
try:
    from .config_manager import get_config_manager as _get_config_manager, get_config as _get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    _get_config_manager = None
    _get_config = None
    # Will log warning after logger is defined

# Try to import both AI libraries
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerateContentResponse
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    GenerateContentResponse = None

try:
    from openai import OpenAI
    from openai.types.chat import ChatCompletion
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None
    ChatCompletion = None

logger = logging.getLogger(__name__)

# Log warning if config manager is not available
if not CONFIG_AVAILABLE:
    logger.warning("Configuration manager not available, using default settings")

# Enum for circuit breaker states
from enum import Enum

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """熔断器模式实现"""
    
    def __init__(self, failure_threshold=5, reset_timeout=300, half_open_max_calls=3):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_max_calls = half_open_max_calls
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.half_open_calls = 0
        self._lock = threading.Lock()
    
    def get_state(self):
        """获取当前状态"""
        return self.state
    
    def can_execute(self):
        """检查是否可以执行操作"""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                if self.last_failure_time and time.time() - self.last_failure_time >= self.reset_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.info("熔断器状态转为半开")
                    return True
                return False
            else:  # HALF_OPEN
                return self.half_open_calls < self.half_open_max_calls
    
    def record_success(self):
        """记录成功的操作"""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_calls += 1
                if self.half_open_calls >= self.half_open_max_calls:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info("熔断器状态转为关闭")
            else:
                self.failure_count = 0
    
    def record_failure(self):
        """记录失败的操作"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                if self.state != CircuitBreakerState.OPEN:
                    self.state = CircuitBreakerState.OPEN
                    logger.warning(f"熔断器打开，失败次数: {self.failure_count}")
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning("半开状态下失败，重新打开熔断器")

@dataclass
class AIResponse:
    """Universal response wrapper for AI API calls"""
    content: str
    metadata: Dict[str, Any]
    session_id: str
    timestamp: float
    model_type: str  # 'gemini', 'openai', 'claude', etc.

class BaseSession(ABC):
    """Abstract base class for AI sessions"""
    
    def __init__(self, session_id: str, model_type: str):
        self.session_id = session_id
        self.model_type = model_type
        self.created_at = time.time()
        self.last_used = time.time()
        self._lock = threading.Lock()
        self.conversation_history: List[Dict[str, str]] = []
    
    @abstractmethod
    def send_message(self, message: str) -> AIResponse:
        """Send message in thread-safe manner"""
        pass
    
    @abstractmethod
    def get_model_client(self):
        """Get the underlying model/client for resource management"""
        pass
    
    def is_expired(self, max_idle_time: float = 3600) -> bool:
        """Check if session is expired (default 1 hour idle)"""
        return time.time() - self.last_used > max_idle_time
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()

class GeminiSession(BaseSession):
    """Session for Gemini AI"""
    
    def __init__(self, model, session_id: str):
        super().__init__(session_id, "gemini")
        self.model = model
        self.chat = model.start_chat() if hasattr(model, 'start_chat') else None
        
        # 从配置文件读取参数
        try:
            if CONFIG_AVAILABLE and _get_config_manager:
                config_mgr = _get_config_manager()
                gemini_config = config_mgr.get_ai_model_config('gemini')
                self.temperature = gemini_config.get('temperature', 0.7)
                self.max_tokens = gemini_config.get('max_tokens', 1048576)  # 使用1M tokens作为默认值
                logger.info(f"Gemini配置加载成功: temperature={self.temperature}, max_tokens={self.max_tokens}")
            else:
                raise Exception("Config manager not available")
        except Exception as e:
            logger.warning(f"Failed to load Gemini config, using defaults: {e}")
            self.temperature = 0.7
            self.max_tokens = 1048576  # 使用1M tokens作为默认值
    
    def send_message(self, message: str) -> AIResponse:
        """Send message to Gemini with retry logic and timeout handling"""
        with self._lock:
            self.last_used = time.time()
            
            # 获取重试配置
            max_retries = 3
            retry_delay = 1.0
            exponential_backoff = True
            backoff_factor = 2.0
            timeout = 120
            
            if CONFIG_AVAILABLE and _get_config_manager:
                try:
                    config_mgr = _get_config_manager()
                    gemini_config = config_mgr.get_ai_model_config('gemini')
                    max_retries = gemini_config.get('max_retries', 3)
                    retry_delay = gemini_config.get('retry_delay', 1.0)
                    exponential_backoff = gemini_config.get('exponential_backoff', True)
                    backoff_factor = gemini_config.get('backoff_factor', 2.0)
                    timeout = gemini_config.get('timeout', 120)
                except Exception as e:
                    logger.warning(f"Failed to load Gemini retry config, using defaults: {e}")
            
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    # 设置请求超时的开始时间
                    start_time = time.time()
                    
                    if self.chat:
                        # 使用配置的参数进行聊天
                        generation_config = {
                            'temperature': self.temperature,
                            'max_output_tokens': self.max_tokens
                        }
                        response = self.chat.send_message(message, generation_config=generation_config)
                        content = response.text
                        metadata = {
                            'usage_metadata': getattr(response, 'usage_metadata', {}),
                            'safety_ratings': getattr(response, 'safety_ratings', []),
                            'attempt': attempt + 1,
                            'total_attempts': max_retries + 1,
                            'response_time': time.time() - start_time
                        }
                    else:
                        # Fallback: direct model call
                        generation_config = {
                            'temperature': self.temperature,
                            'max_output_tokens': self.max_tokens
                        }
                        response = self.model.generate_content(message, generation_config=generation_config)
                        content = response.text
                        metadata = {
                            'attempt': attempt + 1,
                            'total_attempts': max_retries + 1,
                            'response_time': time.time() - start_time
                        }
                    
                    # 检查是否超时
                    elapsed_time = time.time() - start_time
                    if elapsed_time > timeout:
                        raise TimeoutError(f"Gemini API调用超时: {elapsed_time:.1f}秒 > {timeout}秒")
                    
                    # Update conversation history
                    self.conversation_history.append({"role": "user", "content": message})
                    self.conversation_history.append({"role": "assistant", "content": content})
                    
                    if attempt > 0:
                        logger.info(f"Gemini API调用在第{attempt + 1}次尝试成功")
                    
                    return AIResponse(
                        content=content,
                        metadata=metadata,
                        session_id=self.session_id,
                        timestamp=time.time(),
                        model_type="gemini"
                    )
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # 计算延迟时间
                        if exponential_backoff:
                            delay = retry_delay * (backoff_factor ** attempt)
                        else:
                            delay = retry_delay
                        
                        logger.warning(f"Gemini API调用失败 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)}")
                        logger.info(f"等待 {delay:.1f} 秒后重试...")
                        time.sleep(delay)
                    else:
                        logger.error(f"Gemini API调用在 {max_retries + 1} 次尝试后仍然失败")
                        break
            
            # 如果所有重试都失败了，抛出最后一个异常
            if last_exception:
                logger.error(f"Error in Gemini session {self.session_id} after {max_retries + 1} attempts: {last_exception}")
                raise last_exception
            else:
                raise RuntimeError(f"All {max_retries + 1} attempts failed without specific exception")
    
    def get_model_client(self):
        """Get the underlying model/client for resource management"""
        return self.model

class OpenAISession(BaseSession):
    """Session for OpenAI-compatible APIs"""
    
    def __init__(self, client, session_id: str, model_name: str = "gpt-3.5-turbo"):
        super().__init__(session_id, "openai")
        self.client = client
        self.model_name = model_name
        
        # 智能对话历史管理
        self.max_history_tokens = 8000  # 最大历史token数
        self.max_history_pairs = 5      # 最大历史对话轮数
        self.use_context_compression = True  # 启用上下文压缩
        
        # 从配置文件读取参数
        try:
            if CONFIG_AVAILABLE and _get_config_manager:
                config_mgr = _get_config_manager()
                openai_config = config_mgr.get_ai_model_config('openai')
                self.max_tokens = openai_config.get('max_tokens', 1048576)
                self.temperature = openai_config.get('temperature', 0.1)
                
                # 读取对话历史管理配置
                self.max_history_tokens = openai_config.get('max_history_tokens', 8000)
                self.max_history_pairs = openai_config.get('max_history_pairs', 5)
                self.use_context_compression = openai_config.get('use_context_compression', True)
                
                # 初始化熔断器
                circuit_config = openai_config.get('circuit_breaker', {})
                self.circuit_breaker = CircuitBreaker(
                    failure_threshold=circuit_config.get('failure_threshold', 5),
                    reset_timeout=circuit_config.get('reset_timeout', 300),
                    half_open_max_calls=circuit_config.get('half_open_max_calls', 3)
                )
                
                logger.info(f"OpenAI配置加载成功: temperature={self.temperature}, max_tokens={self.max_tokens}")
            else:
                raise Exception("Config manager not available")
        except Exception as e:
            logger.warning(f"Failed to load OpenAI config, using defaults: {e}")
            self.max_tokens = 1048576
            self.temperature = 0.1
            self.circuit_breaker = CircuitBreaker()  # 使用默认配置
            self.max_history_tokens = 8000
            self.max_history_pairs = 5
            self.use_context_compression = True
    
    def _manage_conversation_history(self) -> List[Dict[str, str]]:
        """智能管理对话历史，避免重复发送大量内容"""
        if not self.conversation_history:
            return []
        
        # 如果启用上下文压缩且对话历史较长
        if self.use_context_compression and len(self.conversation_history) > self.max_history_pairs * 2:
            # 保留最近的几轮对话
            recent_history = self.conversation_history[-(self.max_history_pairs * 2):]
            
            # 如果仍然有较早的对话，创建一个摘要
            if len(self.conversation_history) > len(recent_history):
                earlier_history = self.conversation_history[:-(self.max_history_pairs * 2)]
                
                # 简单的历史摘要策略
                summary_content = "之前的对话中，用户主要询问了论文分析相关问题，助手提供了相应的分析和建议。"
                summary_message = {"role": "assistant", "content": f"[历史对话摘要: {summary_content}]"}
                
                return [summary_message] + recent_history
            else:
                return recent_history
        else:
            # 直接限制历史长度
            return self.conversation_history[-(self.max_history_pairs * 2):]
    
    def _estimate_token_count(self, text: str) -> int:
        """粗略估算文本的token数量"""
        # 简单估算：中文字符约1.5个token，英文单词约1个token
        chinese_chars = len([c for c in text if ord(c) > 127])
        english_words = len(text.split()) - chinese_chars
        return int(chinese_chars * 1.5 + english_words)
    
    def send_message(self, message: str) -> AIResponse:
        """Send message to OpenAI-compatible API with retry logic and circuit breaker"""
        with self._lock:
            self.last_used = time.time()
            
            # 检查熔断器状态
            if not self.circuit_breaker.can_execute():
                circuit_state = self.circuit_breaker.get_state()
                raise RuntimeError(f"熔断器已开启，当前状态: {circuit_state.value}，暂时无法执行API调用")
            
            # 获取重试配置
            max_retries = 3
            retry_delay = 1
            exponential_backoff = True
            backoff_factor = 2.0
            
            if CONFIG_AVAILABLE and _get_config_manager:
                try:
                    config_mgr = _get_config_manager()
                    openai_config = config_mgr.get_ai_model_config('openai')
                    max_retries = openai_config.get('max_retries', 3)
                    retry_delay = openai_config.get('retry_delay', 1)
                    exponential_backoff = openai_config.get('exponential_backoff', True)
                    backoff_factor = openai_config.get('backoff_factor', 2.0)
                except Exception as e:
                    logger.warning(f"Failed to load retry config, using defaults: {e}")
            
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": message})
            
            # 使用智能历史管理
            managed_history = self._manage_conversation_history()
            
            # Create messages for API call - 只发送管理后的历史
            messages = [
                {"role": "system", "content": "You are a helpful assistant specialized in academic research and literature review."}
            ] + managed_history
            
            # 记录发送的消息数量和估算的token数量
            total_chars = sum(len(msg.get("content", "")) for msg in messages)
            estimated_tokens = self._estimate_token_count("".join(msg.get("content", "") for msg in messages))
            
            logger.debug(f"OpenAI请求: {len(messages)}条消息, 约{total_chars:,}字符, 估算{estimated_tokens:,}tokens")
            logger.debug(f"历史管理: 原始{len(self.conversation_history)}轮 -> 发送{len(managed_history)}轮")
            
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    # Make API call
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens
                    )
                    
                    content = response.choices[0].message.content
                    if not content:
                        error_msg = f"OpenAI API返回空内容 (尝试 {attempt + 1}/{max_retries + 1})"
                        logger.error(error_msg)
                        
                        # 将空响应视为失败，触发重试
                        if attempt < max_retries:
                            # 记录失败到熔断器
                            self.circuit_breaker.record_failure()
                            
                            # 计算延迟时间并重试
                            if exponential_backoff:
                                delay = retry_delay * (backoff_factor ** attempt)
                            else:
                                delay = retry_delay
                            
                            logger.warning(f"空响应重试延迟 {delay:.1f} 秒...")
                            time.sleep(delay)
                            continue  # 继续下一次重试
                        else:
                            # 最后一次尝试也失败，抛出异常
                            raise RuntimeError(f"OpenAI API在 {max_retries + 1} 次尝试后仍返回空内容")
                    
                    # 内容不为空时的正常处理
                    logger.debug(f"OpenAI API返回内容长度: {len(content)} 字符")
                    
                    metadata = {
                        'usage': response.usage.model_dump() if hasattr(response, 'usage') and response.usage else {},
                        'model': response.model if hasattr(response, 'model') else self.model_name,
                        'finish_reason': response.choices[0].finish_reason if response.choices else None,
                        'attempt': attempt + 1,
                        'total_attempts': max_retries + 1,
                        'circuit_breaker_state': self.circuit_breaker.get_state().value
                    }
                    
                    # Add assistant response to history
                    self.conversation_history.append({"role": "assistant", "content": content})
                    
                    # 记录成功
                    self.circuit_breaker.record_success()
                    
                    if attempt > 0:
                        logger.info(f"OpenAI API调用在第{attempt + 1}次尝试成功")
                    
                    return AIResponse(
                        content=content,
                        metadata=metadata,
                        session_id=self.session_id,
                        timestamp=time.time(),
                        model_type="openai"
                    )
                    
                except Exception as e:
                    last_exception = e
                    
                    # 记录失败
                    self.circuit_breaker.record_failure()
                    
                    # 详细记录错误信息
                    error_info = {
                        'attempt': attempt + 1,
                        'total_attempts': max_retries + 1,
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'session_id': self.session_id,
                        'circuit_breaker_state': self.circuit_breaker.get_state().value
                    }
                    
                    if attempt < max_retries:
                        # 计算延迟时间
                        if exponential_backoff:
                            delay = retry_delay * (backoff_factor ** attempt)
                        else:
                            delay = retry_delay
                        
                        logger.error(f"OpenAI API调用失败 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)}")
                        logger.error(f"错误详情: 类型={type(e).__name__}, 会话={self.session_id}, 熔断器状态={self.circuit_breaker.get_state().value}")
                        logger.info(f"等待 {delay:.1f} 秒后重试...")
                        time.sleep(delay)
                    else:
                        logger.error(f"OpenAI API调用在 {max_retries + 1} 次尝试后仍然失败")
                        break
            
            # 如果所有重试都失败了，抛出最后一个异常
            if last_exception:
                logger.error(f"Error in OpenAI session {self.session_id} after {max_retries + 1} attempts: {last_exception}")
                logger.error(f"熔断器当前状态: {self.circuit_breaker.get_state().value}")
                raise last_exception
            else:
                raise RuntimeError(f"All {max_retries + 1} attempts failed without specific exception")
    
    def get_model_client(self):
        """Get the underlying model/client for resource management"""
        return self.client

class AIConnectionPool:
    """Universal connection pool for managing AI model instances"""
    
    def __init__(self, max_connections: int = 10, api_type: str = "auto"):
        self.max_connections = max_connections
        self.api_type = api_type  # "gemini", "openai", "claude", or "auto"
        self.available_clients = Queue(maxsize=max_connections)
        self.active_sessions: Dict[str, BaseSession] = {}
        self._lock = threading.RLock()
        self._session_counter = 0
        self._cleanup_thread = None
        self._shutdown = False
        self._detected_api_type = None
        
    def _detect_api_type(self) -> str:
        """Auto-detect which API to use based on configuration and environment"""
        load_dotenv(override=True)
        
        # 优先从配置文件读取API类型偏好
        preferred_api = None
        api_configs = {}
        
        if CONFIG_AVAILABLE and _get_config_manager:
            try:
                config_mgr = _get_config_manager()
                
                # 获取所有可用的AI模型配置
                try:
                    openai_config = config_mgr.get_ai_model_config('openai')
                    if openai_config.get('enabled', True):  # 默认启用
                        api_configs['openai'] = openai_config
                        logger.debug(f"OpenAI配置可用: {openai_config}")
                except:
                    pass
                
                try:
                    gemini_config = config_mgr.get_ai_model_config('gemini')
                    if gemini_config.get('enabled', True):  # 默认启用
                        api_configs['gemini'] = gemini_config
                        logger.debug(f"Gemini配置可用: {gemini_config}")
                except:
                    pass
                
                # 检查是否有全局首选API设置
                try:
                    # 使用 _get_config 函数获取首选API配置
                    if _get_config:
                        preferred_api = _get_config('ai_models.preferred_api', None)
                        if preferred_api:
                            logger.info(f"配置文件指定首选API: {preferred_api}")
                except:
                    pass
                    
            except Exception as e:
                logger.warning(f"Failed to load config for API detection: {e}")
        
        # 环境变量检查
        google_api_key = os.getenv('GOOGLE_API_KEY')
        google_api_base = os.getenv('GOOGLE_API_BASE', '')
        
        # 决策逻辑：
        # 1. 如果配置文件指定了首选API且可用，使用它
        if preferred_api and preferred_api in api_configs:
            if preferred_api == 'openai' and OPENAI_AVAILABLE:
                return 'openai'
            elif preferred_api == 'gemini' and GEMINI_AVAILABLE:
                return 'gemini'
        
        # 2. 检查OpenAI兼容接口（包括通过API_BASE的Gemini接口）
        if 'openai' in api_configs and OPENAI_AVAILABLE:
            openai_config = api_configs['openai']
            api_base = openai_config.get('api_base', google_api_base)
            if api_base and google_api_key:
                logger.info(f"使用OpenAI兼容接口: {api_base}")
                return 'openai'
        
        # 3. 检查原生Gemini API
        if 'gemini' in api_configs and GEMINI_AVAILABLE and google_api_key:
            logger.info("使用原生Gemini API")
            return 'gemini'
        
        # 4. 环境变量回退检查
        if google_api_base and ('/v1' in google_api_base or 'openai' in google_api_base.lower()) and OPENAI_AVAILABLE:
            logger.info("基于环境变量使用OpenAI兼容接口")
            return 'openai'
        elif google_api_key and GEMINI_AVAILABLE:
            logger.info("基于环境变量使用Gemini API")
            return 'gemini'
        
        # 5. 如果都不可用，抛出错误
        error_msg = "No valid AI API configuration found. Please check:\n"
        error_msg += f"- OpenAI available: {OPENAI_AVAILABLE}\n"
        error_msg += f"- Gemini available: {GEMINI_AVAILABLE}\n"
        error_msg += f"- GOOGLE_API_KEY set: {bool(google_api_key)}\n"
        error_msg += f"- API configs found: {list(api_configs.keys())}"
        raise ValueError(error_msg)
    
    def _create_gemini_model(self):
        """Create a new Gemini model instance"""
        if not GEMINI_AVAILABLE or genai is None:
            raise ImportError("google-generativeai library not available")
        
        # Get model configuration from config file
        model_name = 'gemini-1.5-flash'  # default
        if CONFIG_AVAILABLE and _get_config_manager:
            try:
                config_mgr = _get_config_manager()
                model_config = config_mgr.get_ai_model_config('gemini')
                model_name = model_config.get('model_name', 'gemini-1.5-flash')
                logger.debug(f"使用Gemini模型: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load Gemini model config, using default: {e}")
        
        # The API key configuration will be handled elsewhere
        try:
            # Use dynamic attribute access to avoid type checker issues
            model_class = getattr(genai, 'GenerativeModel', None)
            if model_class is None:
                raise AttributeError("GenerativeModel not found in genai module")
            return model_class(model_name)
        except Exception as e:
            logger.error(f"Failed to create Gemini model: {e}")
            raise
    
    def _create_openai_client(self):
        """Create a new OpenAI client instance"""
        if not OPENAI_AVAILABLE or OpenAI is None:
            raise ImportError("openai library not available")
        
        load_dotenv(override=True)
        api_key = os.getenv('GOOGLE_API_KEY')
        
        # 优先从配置文件读取配置，允许环境变量覆盖
        base_url = None
        timeout = 120  # 默认2分钟超时
        max_retries = 3  # 默认重试3次
        
        if CONFIG_AVAILABLE and _get_config_manager:
            try:
                config_mgr = _get_config_manager()
                openai_config = config_mgr.get_ai_model_config('openai')
                base_url = openai_config.get('api_base', '')
                timeout = openai_config.get('timeout', 120)
                max_retries = openai_config.get('max_retries', 3)
                logger.debug(f"OpenAI客户端配置: api_base={base_url}, timeout={timeout}s, max_retries={max_retries}")
            except Exception as e:
                logger.warning(f"Failed to load config for OpenAI client, falling back to env: {e}")
        
        # 如果配置文件没有，再从环境变量读取（向后兼容）
        if not base_url:
            base_url = os.getenv('GOOGLE_API_BASE')
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        if not base_url:
            raise ValueError("API base URL not found in config or environment variables")
        
        logger.info(f"创建OpenAI客户端: {base_url}")
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries
        )
    
    def initialize_pool(self):
        """Initialize the connection pool"""
        with self._lock:
            # Detect API type if auto
            if self.api_type == "auto":
                self._detected_api_type = self._detect_api_type()
            else:
                self._detected_api_type = self.api_type
            
            logger.info(f"Initializing AI connection pool with API type: {self._detected_api_type}")
            
            # Create clients based on detected API type
            for i in range(self.max_connections):
                try:
                    if self._detected_api_type == "gemini":
                        client = self._create_gemini_model()
                    else:  # openai or other OpenAI-compatible
                        client = self._create_openai_client()
                    self.available_clients.put(client)
                    logger.debug(f"Created connection {i+1}/{self.max_connections}")
                except Exception as e:
                    logger.error(f"Failed to create connection {i+1}: {e}")
                    raise
            
            # Start cleanup thread
            self._cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
            self._cleanup_thread.start()
            logger.info(f"Initialized AI connection pool with {self.max_connections} {self._detected_api_type} connections")
    
    def get_session(self, session_id: Optional[str] = None) -> BaseSession:
        """Get or create a session"""
        with self._lock:
            if session_id and session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if not session.is_expired():
                    return session
                else:
                    # Clean up expired session
                    del self.active_sessions[session_id]
                    logger.debug(f"Cleaned up expired session: {session_id}")
            
            # Create new session
            if session_id is None:
                self._session_counter += 1
                session_id = f"session_{self._session_counter}_{int(time.time())}"
            
            try:
                client = self.available_clients.get_nowait()
            except:
                # If no available clients, create a new one (temporary expansion)
                try:
                    if self._detected_api_type == "gemini":
                        client = self._create_gemini_model()
                    else:
                        client = self._create_openai_client()
                    logger.warning("Connection pool exhausted, creating temporary connection")
                except Exception as e:
                    logger.error(f"Failed to create temporary connection: {e}")
                    raise
            
            # Create appropriate session type
            try:
                if self._detected_api_type == "gemini":
                    session = GeminiSession(client, session_id)
                else:
                    # For OpenAI, determine model name from config
                    model_name = 'gpt-3.5-turbo'  # default
                    if CONFIG_AVAILABLE and _get_config_manager:
                        try:
                            config_mgr = _get_config_manager()
                            model_config = config_mgr.get_ai_model_config('openai')
                            model_name = model_config.get('model_name', 'gpt-3.5-turbo')
                        except Exception as e:
                            logger.warning(f"Failed to load OpenAI model config, using default: {e}")
                            model_name = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
                    else:
                        model_name = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
                    session = OpenAISession(client, session_id, model_name)
                
                self.active_sessions[session_id] = session
                logger.debug(f"Created new {self._detected_api_type} session: {session_id}")
                return session
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                # Return client to pool if session creation failed
                try:
                    self.available_clients.put_nowait(client)
                except:
                    pass
                raise
    
    def release_session(self, session_id: str):
        """Release a session back to the pool"""
        with self._lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                try:
                    # Use the new get_model_client method
                    client_or_model = session.get_model_client()
                    try:
                        self.available_clients.put_nowait(client_or_model)
                        logger.debug(f"Released session {session_id} and returned client to pool")
                    except:
                        # Pool is full, this might be a temporary connection
                        # For temporary connections, we don't need to keep them
                        logger.debug(f"Released session {session_id}, pool full (temporary connection discarded)")
                except Exception as e:
                    logger.warning(f"Error releasing session {session_id}: {e}")
                
                del self.active_sessions[session_id]
    
    def _cleanup_expired_sessions(self):
        """Background thread to clean up expired sessions"""
        while not self._shutdown:
            try:
                with self._lock:
                    expired_sessions = [
                        sid for sid, session in self.active_sessions.items()
                        if session.is_expired()
                    ]
                    
                    for session_id in expired_sessions:
                        self.release_session(session_id)
                        logger.info(f"Cleaned up expired session: {session_id}")
                
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in cleanup thread: {e}")
    
    def shutdown(self):
        """Shutdown the connection pool"""
        self._shutdown = True
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        
        with self._lock:
            self.active_sessions.clear()
            # Clear the queue
            while not self.available_clients.empty():
                try:
                    self.available_clients.get_nowait()
                except:
                    break
        logger.info("AI connection pool shutdown complete")

class ConcurrentAIClient:
    """Main client class for concurrent AI API access (supports multiple AI providers)"""
    
    def __init__(self, max_workers: int = 5, max_connections: int = 10, api_type: str = "auto"):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.connection_pool = AIConnectionPool(max_connections, api_type)
        self._initialized = False
        self._lock = threading.Lock()
    
    def initialize(self):
        """Initialize the client with environment variables and configuration"""
        with self._lock:
            if self._initialized:
                return
            
            # Load environment variables
            load_dotenv(override=True)
            
            google_api_key = os.getenv('GOOGLE_API_KEY')
            
            if not google_api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            # Initialize connection pool first (it will detect the API type)
            self.connection_pool.initialize_pool()
            
            # Only configure Gemini if we're using Gemini API and library is available
            if (self.connection_pool._detected_api_type == "gemini" and 
                GEMINI_AVAILABLE and genai is not None):
                # Configure Gemini API key
                try:
                    configure_func = getattr(genai, 'configure', None)
                    if configure_func:
                        configure_func(api_key=google_api_key)
                        logger.info("Gemini API configured successfully")
                except Exception as e:
                    logger.warning(f"Could not configure Gemini: {e}")
                    # Will still try to proceed
            
            self._initialized = True
            logger.info(f"ConcurrentAIClient initialized successfully with {self.connection_pool._detected_api_type} API")
    
    def send_message(self, message: str, session_id: Optional[str] = None) -> AIResponse:
        """Send a message synchronously"""
        if not self._initialized:
            self.initialize()
        
        # Track if we created a new session vs. reused an existing one
        created_new_session = session_id is None
        
        session = self.connection_pool.get_session(session_id)
        try:
            response = session.send_message(message)
            
            # Only release if we created a new session (not if reusing an existing session)
            if created_new_session:
                self.connection_pool.release_session(session.session_id)
            
            return response
        except Exception as e:
            # Always release on error if we created a new session
            if created_new_session:
                try:
                    self.connection_pool.release_session(session.session_id)
                except:
                    pass  # Ignore release errors during exception handling
            logger.error(f"Error sending message: {e}")
            raise
    
    async def send_message_async(self, message: str, session_id: Optional[str] = None) -> AIResponse:
        """Send a message asynchronously"""
        if not self._initialized:
            self.initialize()
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.send_message, 
            message, 
            session_id
        )
    
    def send_messages_batch(self, messages: List[str], session_id: Optional[str] = None) -> List[AIResponse]:
        """Send multiple messages concurrently"""
        if not self._initialized:
            self.initialize()
        
        futures = []
        for message in messages:
            # For batch processing, each message gets its own session to avoid conflicts
            # Only reuse session_id if explicitly provided and it's a single message scenario
            if session_id and len(messages) == 1:
                future = self.executor.submit(self.send_message, message, session_id)
            else:
                future = self.executor.submit(self.send_message, message, None)
            futures.append(future)
        
        results = []
        for future in futures:
            try:
                result = future.result(timeout=60)  # 60 second timeout
                results.append(result)
            except Exception as e:
                logger.error(f"Batch message failed: {e}")
                results.append(None)
        
        return results
    
    async def send_messages_batch_async(self, messages: List[str], session_id: Optional[str] = None) -> List[AIResponse]:
        """Send multiple messages concurrently (async version)"""
        if not self._initialized:
            self.initialize()
        
        tasks = []
        for message in messages:
            task = self.send_message_async(message, session_id)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Async batch message failed: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def create_session(self) -> str:
        """Create a new session and return its ID"""
        if not self._initialized:
            self.initialize()
        
        session = self.connection_pool.get_session()
        return session.session_id
    
    def close_session(self, session_id: str):
        """Close a specific session"""
        self.connection_pool.release_session(session_id)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.connection_pool.active_sessions.keys())
    
    def get_api_type(self) -> str:
        """Get the detected/configured API type"""
        if not self._initialized:
            self.initialize()
        return self.connection_pool._detected_api_type or "unknown"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration"""
        if not self._initialized:
            self.initialize()
        
        api_type = self.get_api_type()
        info = {
            'api_type': api_type,
            'max_workers': self.max_workers,
            'max_connections': self.connection_pool.max_connections,
            'active_sessions': len(self.connection_pool.active_sessions)
        }
        
        # Add model-specific information
        if CONFIG_AVAILABLE and _get_config_manager:
            try:
                config_mgr = _get_config_manager()
                model_config = config_mgr.get_ai_model_config(api_type)
                info['model_config'] = model_config
            except:
                pass
        
        return info
    
    def shutdown(self):
        """Shutdown the client and clean up resources"""
        logger.info("Shutting down ConcurrentAIClient...")
        self.executor.shutdown(wait=True)
        self.connection_pool.shutdown()
        self._initialized = False

# Global client instance (singleton pattern with proper initialization)
_global_client = None
_client_lock = threading.Lock()

def get_ai_client(max_workers: int = 5, max_connections: int = 10, api_type: str = "auto") -> ConcurrentAIClient:
    """Get or create the global AI client instance"""
    global _global_client
    
    with _client_lock:
        if _global_client is None:
            _global_client = ConcurrentAIClient(max_workers, max_connections, api_type)
            _global_client.initialize()
        return _global_client

def reset_ai_client():
    """Reset the global AI client (useful for testing or configuration changes)"""
    global _global_client
    
    with _client_lock:
        if _global_client is not None:
            _global_client.shutdown()
            _global_client = None
    logger.info("Global AI client reset")

# Context manager for automatic resource cleanup
@asynccontextmanager
async def ai_client_context(max_workers: int = 5, max_connections: int = 10, api_type: str = "auto"):
    """Async context manager for AI client"""
    client = ConcurrentAIClient(max_workers, max_connections, api_type)
    client.initialize()
    try:
        yield client
    finally:
        client.shutdown()

# Example usage functions
def example_sync_usage():
    """Example of synchronous usage"""
    client = get_ai_client()
    
    # Single message
    response = client.send_message("Hello, what is CNKI ?")
    logger.info("Hello, what is CNKI ?")
    logger.info(f"Response: {response.content}")
    
    # Batch messages
    messages = ["Explain Literature Review", "How to build a research assistant system to automate the task of conducting systematic literature reviews?"]
    responses = client.send_messages_batch(messages)
    
    for i, response in enumerate(responses):
        if response:
            logger.info(f"Response {i+1}: {response.content}...")

async def example_async_usage():
    """Example of asynchronous usage"""
    async with ai_client_context() as client:
        # Single async message
        response = await client.send_message_async("Can you code in C++?")
        logger.info("Can you code in C++?")
        logger.info(f"Async Response: {response.content}")
        
        # Batch async messages
        messages = ["What is AI Agent?", "How to build an AI Agent?", "Tell me about Claude AI."]
        responses = await client.send_messages_batch_async(messages)
        
        for i, response in enumerate(responses):
            if response:
                logger.info(f"Async Response {i+1}: {response.content}...")

if __name__ == "__main__":
    # Run synchronous example
    logger.info("=== Synchronous Example ===")
    example_sync_usage()
    
    # Run asynchronous example
    logger.info("\n=== Asynchronous Example ===")
    asyncio.run(example_async_usage())
