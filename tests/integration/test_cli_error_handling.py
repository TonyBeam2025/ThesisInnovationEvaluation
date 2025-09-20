#!/usr/bin/env python3
"""
测试CLI命令错误处理改进
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import subprocess
import sys

def test_cli_error_handling():
    """测试CLI错误处理功能"""
    
    print("🔍 测试CLI命令错误处理改进")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        {
            'name': '错误命令格式 - extract evaluate',
            'command': ['uv', 'run', 'thesis-eval', 'extract', 'evaluate'],
            'expected_error': '命令格式错误'
        },
        {
            'name': '错误命令格式 - evaluate extract', 
            'command': ['uv', 'run', 'thesis-eval', 'evaluate', 'extract'],
            'expected_error': '命令格式错误'
        },
        {
            'name': '不存在的文件',
            'command': ['uv', 'run', 'thesis-eval', 'extract', 'nonexistent.pdf'],
            'expected_error': '文件不存在'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: {test_case['name']}")
        print(f"命令: {' '.join(test_case['command'])}")
        
        try:
            # 执行命令
            result = subprocess.run(
                test_case['command'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stderr + result.stdout
            print(f"退出码: {result.returncode}")
            
            # 检查是否包含预期的错误信息
            if test_case['expected_error'] in output:
                print(" 错误处理正确")
            else:
                print("❌ 错误处理不符合预期")
            
            # 检查是否包含建议信息
            if "💡 建议:" in output or "建议" in output:
                print(" 包含用户建议")
            else:
                print("⚠️ 缺少用户建议")
            
            # 显示部分输出
            print("输出摘要:")
            lines = output.split('\n')
            for line in lines[:5]:  # 显示前5行
                if line.strip():
                    print(f"  {line}")
            
        except subprocess.TimeoutExpired:
            print("❌ 命令执行超时")
        except Exception as e:
            print(f"❌ 执行异常: {e}")
    
    print(f"\n🎯 正确的命令示例:")
    print(" 查看可用文件: uv run thesis-eval files")
    print(" 提取论文信息: uv run thesis-eval extract data/input/文件.pdf")  
    print(" 评估论文: uv run thesis-eval evaluate data/input/文件.pdf")
    print(" 查看帮助: uv run thesis-eval --help")

if __name__ == "__main__":
    test_cli_error_handling()
