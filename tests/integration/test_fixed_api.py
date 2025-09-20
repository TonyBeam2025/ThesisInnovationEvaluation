import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
from src.thesis_inno_eval.ai_client import get_ai_client
from src.thesis_inno_eval.config_manager import reset_config_manager
import time

print('🔧 修复配置后的API稳定性测试')
print('=' * 40)

# 重置配置管理器以加载新配置
reset_config_manager()

# 获取AI客户端
ai_client = get_ai_client()
print(f'🤖 使用API类型: {ai_client.get_api_type()}')
print()

# 简单测试
test_cases = [
    "Hello",
    "用中文说你好",
    "What is 2+2?",
    "Generate a simple example",
    "Test message for stability check"
]

success_count = 0
total_count = len(test_cases)

for i, message in enumerate(test_cases, 1):
    print(f'测试 {i}/{total_count}: ', end='')
    
    start_time = time.time()
    try:
        response = ai_client.send_message(message)
        duration = time.time() - start_time
        
        if response.content:
            preview = response.content[:50].replace('\n', ' ')
            print(f' {duration:.1f}s "{preview}..."')
            success_count += 1
        else:
            print(f'❌ {duration:.1f}s 空响应')
            
    except Exception as e:
        duration = time.time() - start_time
        print(f'❌ {duration:.1f}s 异常: {str(e)[:50]}...')
    
    time.sleep(1)  # 短暂间隔

print()
print('📊 测试结果:')
print(f'   成功: {success_count}/{total_count}')
print(f'   成功率: {(success_count/total_count)*100:.1f}%')

if success_count == total_count:
    print('    新代理服务器稳定性: 优秀')
elif success_count >= total_count * 0.8:
    print('   🟨 新代理服务器稳定性: 良好')
else:
    print('   ⚠️ 新代理服务器稳定性: 需要改进')

print()
print('🎯 配置修复测试完成!')
