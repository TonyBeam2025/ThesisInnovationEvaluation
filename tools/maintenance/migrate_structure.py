#!/usr/bin/env python3
"""
项目结构迁移脚本
将现有的Python文件迁移到新的包结构中
"""

import shutil
import os
from pathlib import Path

def migrate_project_structure():
    """迁移项目结构到标准Python包布局"""
    
    # 当前目录和目标目录
    current_dir = Path(".")
    src_dir = Path("src/thesis_inno_eval")
    
    # 需要迁移的Python文件
    python_files = [
        "cnki_client_pool.py",
        "cnki_query_generator.py", 
        "config_manager.py",
        "extract_sections_with_gemini.py",
        "gemini_client.py",
        "logging_config.py",
        "pandas_remove_duplicates.py",
        "test_ai_client.py",
        "test_config_system.py"
    ]
    
    print("🔄 开始迁移Python文件...")
    
    # 迁移Python文件
    for file_name in python_files:
        src_file = current_dir / file_name
        dst_file = src_dir / file_name
        
        if src_file.exists():
            print(f"   迁移: {file_name} -> {dst_file.relative_to(current_dir)}")
            shutil.copy2(src_file, dst_file)
        else:
            print(f"  ⚠️  文件不存在: {file_name}")
    
    # 创建tests目录并迁移测试文件
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    
    test_files = ["test_ai_client.py", "test_config_system.py"]
    for test_file in test_files:
        src_file = current_dir / test_file
        dst_file = tests_dir / test_file
        
        if src_file.exists():
            print(f"   迁移测试文件: {test_file} -> {dst_file.relative_to(current_dir)}")
            shutil.copy2(src_file, dst_file)
    
    # 创建测试初始化文件
    test_init = tests_dir / "__init__.py"
    if not test_init.exists():
        test_init.write_text("# Test package\n")
        print(f"   创建: {test_init.relative_to(current_dir)}")
    
    print("\n📁 项目结构迁移完成！")
    print("\n新的项目结构:")
    print("thesis-inno-eval/")
    print("├── src/thesis_inno_eval/      # 主要代码包")
    print("├── tests/                     # 测试文件")  
    print("├── conf.yaml                  # 配置文件")
    print("├── pyproject.toml            # 项目配置")
    print("├── README.md                 # 项目说明")
    print("└── requirements.txt          # 旧依赖文件（可删除）")
    
    print("\n🎯 下一步:")
    print("1. 运行: uv sync  # 安装依赖")
    print("2. 运行: uv run pytest  # 运行测试")
    print("3. 删除根目录下的旧Python文件（可选）")

if __name__ == "__main__":
    migrate_project_structure()

