#!/usr/bin/env python3
"""
调试文件内容差异
"""
import os
import sys
import inspect

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def read_file_directly():
    """直接读取文件内容"""
    file_path = r"f:\MyProjects\thesis_Inno_Eval\src\thesis_inno_eval\extract_sections_with_gemini.py"
    print("=== 直接读取文件内容 ===")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[45:80], 46):  # 查看相关行
            if 'prompt = f"""' in line or '请从' in line:
                print(f"第{i}行: {line.rstrip()}")
    print()

def import_and_inspect():
    """导入模块并检查源代码"""
    print("=== 导入模块并检查 ===")
    try:
        from thesis_inno_eval.extract_sections_with_gemini import extract_sections_with_gemini
        
        # 获取函数源代码
        source = inspect.getsource(extract_sections_with_gemini)
        lines = source.split('\n')
        
        for i, line in enumerate(lines):
            if 'prompt = f"""' in line or '请从' in line:
                print(f"第{i+1}行: {line.rstrip()}")
        
        # 获取函数文件位置
        file_location = inspect.getfile(extract_sections_with_gemini)
        print(f"函数来源文件: {file_location}")
        
    except Exception as e:
        print(f"导入错误: {e}")
    print()

def check_sys_modules():
    """检查sys.modules中的模块"""
    print("=== 检查sys.modules ===")
    module_name = "thesis_inno_eval.extract_sections_with_gemini"
    if module_name in sys.modules:
        module = sys.modules[module_name]
        print(f"模块已加载: {module}")
        print(f"模块文件: {module.__file__}")
        
        # 检查模块的修改时间
        if hasattr(module, '__file__') and module.__file__:
            import os
            mtime = os.path.getmtime(module.__file__)
            import datetime
            print(f"模块文件修改时间: {datetime.datetime.fromtimestamp(mtime)}")
    else:
        print("模块未加载")
    print()

if __name__ == "__main__":
    read_file_directly()
    check_sys_modules()
    import_and_inspect()
