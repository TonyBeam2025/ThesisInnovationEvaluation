import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import time
from datetime import datetime
from src.thesis_inno_eval.ai_client import get_ai_client

print('📊 测试API失败频率和模式分析...')
print()

ai_client = get_ai_client()

# 测试数据收集
test_results = []
total_tests = 5

print(f'🎯 执行 {total_tests} 次快速连续测试:')

for i in range(total_tests):
    print(f'测试 {i+1}/{total_tests}', end=' ')
    
    start_time = time.time()
    timestamp = datetime.now()
    
    try:
        response = ai_client.send_message('Say "OK"')
        end_time = time.time()
        
        duration = end_time - start_time
        success = bool(response.content)
        content_preview = (response.content[:10] + '...') if response.content and len(response.content) > 10 else response.content
        
        test_results.append({
            'timestamp': timestamp,
            'duration': duration,
            'success': success,
            'content': response.content,
            'preview': content_preview
        })
        
        status = '' if success else '❌'
        print(f'{status} {duration:.1f}s "{content_preview}"')
        
    except Exception as e:
        test_results.append({
            'timestamp': timestamp,
            'duration': time.time() - start_time,
            'success': False,
            'error': str(e),
            'content': None
        })
        print(f'❌ 异常: {e}')
    
    # 短暂间隔
    time.sleep(1)

print()
print('📈 结果统计:')

successes = sum(1 for r in test_results if r['success'])
failures = len(test_results) - successes
success_rate = (successes / len(test_results)) * 100

print(f'   总测试数: {len(test_results)}')
print(f'   成功次数: {successes}')
print(f'   失败次数: {failures}')
print(f'   成功率: {success_rate:.1f}%')

if test_results:
    durations = [r['duration'] for r in test_results]
    avg_duration = sum(durations) / len(durations)
    print(f'   平均响应时间: {avg_duration:.1f}秒')
    print(f'   最快响应: {min(durations):.1f}秒')
    print(f'   最慢响应: {max(durations):.1f}秒')

print()
print('🔍 失败模式分析:')
failed_results = [r for r in test_results if not r['success']]
if failed_results:
    for i, result in enumerate(failed_results, 1):
        error_info = result.get('error', '空响应')
        print(f'   失败 {i}: {result["timestamp"].strftime("%H:%M:%S")} - {error_info}')
else:
    print('   无失败记录')
