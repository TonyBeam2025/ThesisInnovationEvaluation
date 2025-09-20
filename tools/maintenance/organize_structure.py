#!/usr/bin/env python3
"""
项目目录结构整理脚本
将文件移动到适当的目录中
"""

import os
import shutil
from pathlib import Path
import glob

def organize_project_structure():
    """整理项目目录结构"""
    
    print("📁 开始整理项目目录结构...")
    
    # 定义目录路径
    root_dir = Path(".")
    data_dir = Path("data")
    input_dir = data_dir / "input"
    output_dir = data_dir / "output"
    logs_dir = Path("logs")
    docs_dir = Path("docs")
    config_dir = Path("config")
    
    # 确保目录存在
    for dir_path in [data_dir, input_dir, output_dir, logs_dir, docs_dir, config_dir]:
        dir_path.mkdir(exist_ok=True)
    
    # 1. 移动输入文件 (论文文档)
    print("\n📄 整理输入文件...")
    input_patterns = ["*.docx", "*.pdf", "*.md"]
    for pattern in input_patterns:
        for file_path in root_dir.glob(pattern):
            if file_path.name not in ["README.md"]:  # 排除项目文档
                dest_path = input_dir / file_path.name
                print(f"  📄 {file_path.name} -> {dest_path.relative_to(root_dir)}")
                shutil.move(str(file_path), str(dest_path))
    
    # 2. 移动输出文件 (JSON结果文件)
    print("\n📊 整理输出文件...")
    output_patterns = ["*_relevant_papers_*.json", "*_TOP*PAPERS_*.json", "*_dedup_*.json"]
    for pattern in output_patterns:
        for file_path in root_dir.glob(pattern):
            dest_path = output_dir / file_path.name
            print(f"  📊 {file_path.name} -> {dest_path.relative_to(root_dir)}")
            shutil.move(str(file_path), str(dest_path))
    
    # 3. 移动日志文件
    print("\n📋 整理日志文件...")
    log_patterns = ["*.log", "*.log.*"]
    for pattern in log_patterns:
        for file_path in root_dir.glob(pattern):
            dest_path = logs_dir / file_path.name
            print(f"  📋 {file_path.name} -> {dest_path.relative_to(root_dir)}")
            shutil.move(str(file_path), str(dest_path))
    
    # 4. 移动配置文件
    print("\n⚙️ 整理配置文件...")
    config_files = ["conf.yaml", "rules.txt", "strategy.txt"]
    for filename in config_files:
        file_path = root_dir / filename
        if file_path.exists():
            dest_path = config_dir / filename
            print(f"  ⚙️ {filename} -> {dest_path.relative_to(root_dir)}")
            shutil.move(str(file_path), str(dest_path))
    
    # 5. 移动文档文件
    print("\n📚 整理文档文件...")
    doc_files = ["MIGRATION_REPORT.md"]
    for filename in doc_files:
        file_path = root_dir / filename
        if file_path.exists():
            dest_path = docs_dir / filename
            print(f"  📚 {filename} -> {dest_path.relative_to(root_dir)}")
            shutil.move(str(file_path), str(dest_path))
    
    # 6. 清理根目录的旧Python文件（可选）
    print("\n🧹 清理旧文件...")
    old_python_files = [
        "cnki_client_pool.py",
        "cnki_query_generator.py", 
        "config_manager.py",
        "extract_sections_with_gemini.py",
        "gemini_client.py",
        "logging_config.py",
        "pandas_remove_duplicates.py",
        "test_ai_client.py",
        "test_config_system.py",
        "migrate_structure.py"
    ]
    
    for filename in old_python_files:
        file_path = root_dir / filename
        if file_path.exists():
            print(f"  🗑️ 删除旧文件: {filename}")
            file_path.unlink()
    
    print("\n 项目目录结构整理完成！")
    
    # 显示新的目录结构
    print("\n📂 新的项目结构:")
    print("""
thesis-inno-eval/
├── src/thesis_inno_eval/     # 主要代码包
├── tests/                    # 测试文件
├── data/                     # 数据目录
│   ├── input/               # 输入文件 (论文文档)
│   └── output/              # 输出文件 (分析结果)
├── logs/                     # 日志文件
├── config/                   # 配置文件
├── docs/                     # 文档文件
├── pyproject.toml           # 项目配置
├── README.md                # 项目说明
└── uv.lock                  # 依赖锁定
    """)

def create_directory_readme_files():
    """为各个目录创建README文件"""
    
    readme_contents = {
        "data/README.md": """# 数据目录

此目录包含论文评估系统的输入输出数据。

## 目录结构

- `input/` - 输入文件（论文文档）
- `output/` - 输出文件（分析结果）

## 文件类型

### input/
- `.docx` - Word文档格式的论文
- `.pdf` - PDF格式的论文
- `.md` - Markdown格式的论文

### output/
- `*_relevant_papers_Chinese.json` - 中文相关论文
- `*_relevant_papers_English.json` - 英文相关论文
- `*_relevant_papers_dedup_*.json` - 去重后的相关论文
- `*_TOP*PAPERS_*.json` - TopN论文结果
""",
        "logs/README.md": """# 日志目录

此目录包含系统运行日志。

## 日志文件

- `app.log` - 当前日志文件
- `app.log.1`, `app.log.2` - 历史日志文件（轮转）

## 日志级别

- ERROR: 错误信息
- WARNING: 警告信息
- INFO: 一般信息
- DEBUG: 调试信息
""",
        "config/README.md": """# 配置目录

此目录包含系统配置文件。

## 配置文件

- `conf.yaml` - 主配置文件
- `rules.txt` - 评估规则
- `strategy.txt` - 评估策略

## 配置说明

主要配置项：
- AI模型设置
- CNKI搜索参数
- 文件命名规则
- TopN值设置
""",
        "docs/README.md": """# 文档目录

此目录包含项目文档。

## 文档文件

- `MIGRATION_REPORT.md` - 项目迁移报告
- 其他技术文档

## 文档类型

- 迁移报告
- API文档
- 使用指南
- 开发文档
"""
    }
    
    for file_path, content in readme_contents.items():
        path = Path(file_path)
        path.write_text(content, encoding='utf-8')
        print(f"📝 创建: {file_path}")

if __name__ == "__main__":
    organize_project_structure()
    create_directory_readme_files()
    print("\n🎉 项目目录结构整理完成！")

