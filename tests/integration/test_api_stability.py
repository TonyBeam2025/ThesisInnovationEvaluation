import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
from src.thesis_inno_eval.ai_client import get_ai_client
import time
import requests

print('🧪 测试API服务端稳定性...')
print()

# 1. 测试API端点连接性
api_url = 'https://api.skyi.cc/v1/models'
print('🌐 测试API端点连接性:')
try:
    response = requests.get(api_url, timeout=10)
    print(f'   状态码: {response.status_code}')
    print(f'   响应时间: {response.elapsed.total_seconds():.2f}秒')
    if response.status_code == 200:
        print('    API端点可达')
    else:
        print('   ⚠️ API端点响应异常')
except Exception as e:
    print(f'   ❌ 连接失败: {e}')

print()

# 2. 测试简单请求的重复性
print('🔄 重复测试简单请求 (带间隔):')
ai_client = get_ai_client()

for i in range(3):
    try:
        print(f'测试 {i+1}/3...')
        start_time = time.time()
        response = ai_client.send_message('Say hello in one word.')
        end_time = time.time()
        
        success = '' if response.content else '❌'
        content = (response.content[:20] + '...') if response.content and len(response.content) > 20 else response.content
        print(f'   {success} 时间: {end_time-start_time:.1f}秒 内容: "{content}"')
        
        # 间隔5秒
        if i < 2:
            print('   ⏳ 等待5秒...')
            time.sleep(5)
            
    except Exception as e:
        print(f'   ❌ 异常: {e}')
