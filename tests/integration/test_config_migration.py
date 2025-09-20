#!/usr/bin/env python3
"""
测试配置迁移后的系统功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
sys.path.insert(0, 'src')

from thesis_inno_eval.config_manager import get_config_manager
from thesis_inno_eval.gemini_client import get_ai_client

def test_config_migration():
    """测试配置迁移是否成功"""
    print("🧪 测试配置迁移...")
    
    # 1. 测试配置管理器
    print("\n📋 1. 测试配置文件读取:")
    try:
        config_mgr = get_config_manager()
        openai_config = config_mgr.get_ai_model_config('openai')
        gemini_config = config_mgr.get_ai_model_config('gemini')
        
        print(f"   OpenAI配置: {openai_config}")
        print(f"   Gemini配置: {gemini_config}")
        
        # 检查关键配置
        assert openai_config.get('api_base'), "OpenAI api_base 不应为空"
        assert openai_config.get('model_name'), "OpenAI model_name 不应为空"
        print(f"   OpenAI API Base: {openai_config.get('api_base')}")
        print(f"   OpenAI Model: {openai_config.get('model_name')}")
        
    except Exception as e:
        print(f"  ❌ 配置文件读取失败: {e}")
        return False
    
    # 2. 测试环境变量
    print("\n🔑 2. 测试环境变量:")
    google_api_key = os.getenv('GOOGLE_API_KEY')
    google_api_base = os.getenv('GOOGLE_API_BASE')  # 应该为空或None
    
    print(f"   GOOGLE_API_KEY: {'***' + google_api_key[-4:] if google_api_key else 'Not Set'}")
    print(f"   GOOGLE_API_BASE: {google_api_base or 'Not Set (Expected)'}")
    
    if not google_api_key:
        print("  ❌ GOOGLE_API_KEY 未设置")
        return False
    
    # 3. 测试AI客户端初始化
    print("\n🤖 3. 测试AI客户端初始化:")
    try:
        ai_client = get_ai_client()
        print(f"   AI客户端类型: {type(ai_client).__name__}")
        
        # 测试API类型检测
        if hasattr(ai_client, 'connection_pool'):
            api_type = ai_client.connection_pool._detected_api_type
            print(f"   检测到的API类型: {api_type}")
        
    except Exception as e:
        print(f"  ❌ AI客户端初始化失败: {e}")
        return False
    
    print("\n🎉 配置迁移测试完成!")
    return True

if __name__ == "__main__":
    success = test_config_migration()
    if success:
        print("\n 所有测试通过！配置迁移成功。")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！需要检查配置。")
        sys.exit(1)
