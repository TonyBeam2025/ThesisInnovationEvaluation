#!/usr/bin/env python3
"""
调试模块路径
"""

import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

import thesis_inno_eval.extract_sections_with_gemini as extract_module

def debug_module_location():
    """调试模块的实际位置"""
    
    print("模块文件路径:", extract_module.__file__)
    print("模块文档:", extract_module.__doc__)
    
    # 检查extract_sections_with_gemini函数
    func = extract_module.extract_sections_with_gemini
    print("函数对象:", func)
    print("函数代码文件:", func.__code__.co_filename)
    print("函数代码行号:", func.__code__.co_firstlineno)
    
    # 尝试读取实际的函数源代码
    import inspect
    try:
        source = inspect.getsource(func)
        print("=== 函数源代码 ===")
        lines = source.split('\n')
        for i, line in enumerate(lines[:50], func.__code__.co_firstlineno):
            print(f"{i:3d}: {line}")
        print("=== 源代码结束 ===")
    except Exception as e:
        print(f"无法获取源代码: {e}")

if __name__ == "__main__":
    debug_module_location()
