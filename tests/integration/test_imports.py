#!/usr/bin/env python3
"""
简单的包导入测试
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

def test_basic_imports():
    """测试基本导入功能"""
    
    print("🔍 测试基本包导入...")
    
    # 测试主包导入
    try:
        import thesis_inno_eval
        print(f" thesis_inno_eval 导入成功，版本: {thesis_inno_eval.__version__}")
    except ImportError as e:
        print(f"❌ thesis_inno_eval 导入失败: {e}")
        return False
    
    # 测试配置管理器
    try:
        from thesis_inno_eval.config_manager import get_config_manager
        config_mgr = get_config_manager()
        print(f" config_manager 导入成功，TopN: {config_mgr.get_top_papers_count()}")
    except ImportError as e:
        print(f"❌ config_manager 导入失败: {e}")
        return False
    
    # 测试AI客户端
    try:
        from thesis_inno_eval.gemini_client import ConcurrentAIClient
        print(" gemini_client 导入成功")
    except ImportError as e:
        print(f"❌ gemini_client 导入失败: {e}")
        return False
    
    # 测试其他模块
    modules = [
        'cnki_query_generator',
        'extract_sections_with_gemini', 
        'logging_config',
        'pandas_remove_duplicates'
    ]
    
    for module in modules:
        try:
            __import__(f'thesis_inno_eval.{module}')
            print(f" {module} 导入成功")
        except ImportError as e:
            print(f"⚠️ {module} 导入失败: {e}")
    
    print("\n🎉 基本导入测试完成！")
    return True

if __name__ == "__main__":
    test_basic_imports()
