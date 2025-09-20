import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import time
import requests
from datetime import datetime
from src.thesis_inno_eval.ai_client import get_ai_client

print('🔄 新代理服务器API稳定性测试')
print('=' * 50)

# 1. 基础连接测试
print('🌐 测试新API端点连接性:')
new_api_base = 'https://llmxapi.com/v1'
models_endpoint = f'{new_api_base}/models'

try:
    response = requests.get(models_endpoint, 
                          headers={'Authorization': 'Bearer sk-RTbrA013BC1idMIfHwmMhDdwSqzXdpmR89v8sbmhl1dVkhWV'},
                          timeout=10)
    print(f'   状态码: {response.status_code}')
    print(f'   响应时间: {response.elapsed.total_seconds():.2f}秒')
    
    if response.status_code == 200:
        print('    新API端点连接正常')
        if response.json():
            models = response.json().get('data', [])
            print(f'   📋 可用模型数量: {len(models)}')
    else:
        print(f'   ⚠️ API返回状态: {response.status_code}')
        print(f'   响应内容: {response.text[:200]}...')
        
except Exception as e:
    print(f'   ❌ 连接测试失败: {e}')

print()

# 2. AI客户端稳定性测试
print('🤖 AI客户端稳定性测试:')
ai_client = get_ai_client()

test_messages = [
    "Hello, test message 1",
    "请用中文回答：什么是人工智能？",
    "Generate a simple JSON example",
    "测试长一点的内容处理能力，这是一个包含更多文字的测试消息，用来验证API对于不同长度请求的响应稳定性。",
    "Final test message"
]

test_results = []

for i, message in enumerate(test_messages, 1):
    print(f'测试 {i}/{len(test_messages)}: ', end='')
    
    start_time = time.time()
    try:
        response = ai_client.send_message(message)
        end_time = time.time()
        
        duration = end_time - start_time
        success = bool(response.content)
        
        test_results.append({
            'test_num': i,
            'message': message[:30] + '...' if len(message) > 30 else message,
            'success': success,
            'duration': duration,
            'response_length': len(response.content) if response.content else 0
        })
        
        if success:
            preview = response.content[:50].replace('\n', ' ')
            print(f' {duration:.1f}s "{preview}..."')
        else:
            print(f'❌ {duration:.1f}s 空响应')
            
    except Exception as e:
        test_results.append({
            'test_num': i,
            'message': message[:30] + '...' if len(message) > 30 else message,
            'success': False,
            'duration': time.time() - start_time,
            'error': str(e)
        })
        print(f'❌ 异常: {e}')
    
    # 短暂间隔避免过快请求
    time.sleep(2)

print()

# 3. 统计分析
print('📊 测试结果统计:')
total_tests = len(test_results)
successful_tests = sum(1 for r in test_results if r['success'])
failed_tests = total_tests - successful_tests

print(f'   总测试次数: {total_tests}')
print(f'   成功次数: {successful_tests}')
print(f'   失败次数: {failed_tests}')
print(f'   成功率: {(successful_tests/total_tests)*100:.1f}%')

if successful_tests > 0:
    successful_durations = [r['duration'] for r in test_results if r['success']]
    avg_duration = sum(successful_durations) / len(successful_durations)
    min_duration = min(successful_durations)
    max_duration = max(successful_durations)
    
    print(f'   平均响应时间: {avg_duration:.1f}秒')
    print(f'   最快响应: {min_duration:.1f}秒')
    print(f'   最慢响应: {max_duration:.1f}秒')

print()

# 4. 对比评估
print('🔄 与之前服务对比:')
if successful_tests == total_tests:
    print('    新服务稳定性: 优秀 (100% 成功率)')
elif successful_tests >= total_tests * 0.8:
    print('   🟨 新服务稳定性: 良好 (80%+ 成功率)')
else:
    print('   ⚠️ 新服务稳定性: 需要改进')

print()
print('📋 详细测试结果:')
for result in test_results:
    status = '' if result['success'] else '❌'
    duration = result['duration']
    message = result['message']
    print(f'   {status} 测试{result["test_num"]}: {duration:.1f}s - {message}')

print()
print('🎯 新代理服务器评估完成!')
