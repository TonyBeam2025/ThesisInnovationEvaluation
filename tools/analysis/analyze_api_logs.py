import re
from datetime import datetime

# 读取日志内容
with open('logs/app.log', 'r', encoding='utf-8') as f:
    log_content = f.read()

# 提取HTTP请求的发送和响应时间
send_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*Sending HTTP Request: POST'
response_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*HTTP Request: POST.*"HTTP/1.1 200 OK"'

send_times = re.findall(send_pattern, log_content)
response_times = re.findall(response_pattern, log_content)

print('📊 API请求响应时间分析:')
print(f'发送请求次数: {len(send_times)}')
print(f'收到响应次数: {len(response_times)}')
print()

# 计算响应时间
print('⏱️ 响应时间统计:')
for i, (send_time, resp_time) in enumerate(zip(send_times, response_times)):
    send_dt = datetime.strptime(send_time, '%Y-%m-%d %H:%M:%S,%f')
    resp_dt = datetime.strptime(resp_time, '%Y-%m-%d %H:%M:%S,%f')
    duration = (resp_dt - send_dt).total_seconds()
    print(f'请求 {i+1}: {duration:.1f} 秒')

print()
print('🔍 失败/成功模式分析:')
# 统计空响应和成功的比例
empty_responses = len(re.findall(r'API返回空内容', log_content))
successful_responses = len(re.findall(r'API调用.*成功', log_content))
print(f'空响应次数: {empty_responses}')
print(f'成功响应次数: {successful_responses}')
if empty_responses + successful_responses > 0:
    print(f'成功率: {successful_responses/(empty_responses+successful_responses)*100:.1f}%')

print()
print('📈 请求频率分析:')
# 分析请求间隔
request_times = []
for match in re.finditer(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*HTTP Request: POST', log_content):
    time_str = match.group(1)
    dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S,%f')
    request_times.append(dt)

intervals = []
for i in range(1, len(request_times)):
    interval = (request_times[i] - request_times[i-1]).total_seconds()
    intervals.append(interval)
    print(f'请求间隔 {i}: {interval:.1f} 秒')

if intervals:
    print(f'平均请求间隔: {sum(intervals)/len(intervals):.1f} 秒')
    print(f'最短间隔: {min(intervals):.1f} 秒')
    print(f'最长间隔: {max(intervals):.1f} 秒')
