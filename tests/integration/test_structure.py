#!/usr/bin/env python3
"""
目录结构和配置测试脚本
验证新的目录结构和配置管理功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
from pathlib import Path
from thesis_inno_eval.config_manager import get_config_manager

def test_directory_structure():
    """测试目录结构"""
    print("📁 测试目录结构...")
    
    # 期望的目录列表
    expected_dirs = [
        "src/thesis_inno_eval",
        "tests",
        "tests/integration",
        "data",
        "data/input",
        "data/output",
        "data/output/analysis",
        "data/output/structured",
        "logs",
        "config",
        "docs",
        "docs/reports",
        "tools",
        "tools/analysis",
        "tools/maintenance",
        "tools/verification",
        "tools/legacy"
    ]
    
    all_dirs_exist = True
    for dir_path in expected_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   {dir_path}")
        else:
            print(f"  ❌ {dir_path} (不存在)")
            all_dirs_exist = False
    
    return all_dirs_exist

def test_config_manager():
    """测试配置管理器的目录功能"""
    print("\n⚙️ 测试配置管理器...")
    
    try:
        config_mgr = get_config_manager()
        print("   配置管理器加载成功")
        
        # 测试目录配置
        directories = {
            'input_dir': config_mgr.get_input_dir(),
            'output_dir': config_mgr.get_output_dir(),
            'analysis_output_dir': config_mgr.get_analysis_output_dir(),
            'structured_output_dir': config_mgr.get_structured_output_dir(),
            'logs_dir': config_mgr.get_logs_dir(),
            'config_dir': config_mgr.get_config_dir(),
            'docs_dir': config_mgr.get_docs_dir(),
            'reports_dir': config_mgr.get_reports_dir(),
            'tools_dir': config_mgr.get_tools_dir(),
        }
        
        print("  📂 目录配置:")
        for name, path in directories.items():
            print(f"    {name}: {path}")
        
        # 测试文件格式配置
        formats = config_mgr.get_supported_formats()
        print(f"  📄 支持的文件格式: {formats}")
        
        # 测试日志配置
        log_file = config_mgr.get_log_file_path()
        print(f"  📋 日志文件路径: {log_file}")
        
        # 测试TopN配置
        top_count = config_mgr.get_top_papers_count()
        print(f"  📊 TopN论文数量: {top_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置管理器测试失败: {e}")
        return False

def test_file_organization():
    """测试文件组织情况"""
    print("\n📊 测试文件组织...")
    
    # 检查输入文件
    input_dir = Path("data/input")
    if input_dir.exists():
        input_files = list(input_dir.glob("*"))
        print(f"  📄 输入文件数量: {len(input_files)}")
        if len(input_files) > 0:
            print("    示例文件:")
            for file_path in input_files[:3]:  # 显示前3个文件
                print(f"      • {file_path.name}")
    
    # 检查分析输出
    analysis_dir = Path("data/output/analysis")
    if analysis_dir.exists():
        analysis_files = list(analysis_dir.glob("*.json"))
        print(f"  📊 分析输出数量: {len(analysis_files)}")
        if len(analysis_files) > 0:
            print("    分析示例:")
            for file_path in analysis_files[:3]:
                print(f"      • {file_path.name}")

    # 检查结构化输出
    structured_dir = Path("data/output/structured")
    if structured_dir.exists():
        structured_files = list(structured_dir.glob("*.json"))
        print(f"  📦 结构化输出数量: {len(structured_files)}")
        if len(structured_files) > 0:
            print("    结构化示例:")
            for file_path in structured_files[:3]:
                print(f"      • {file_path.name}")
    
    # 检查日志文件
    logs_dir = Path("logs")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log*"))
        print(f"  📋 日志文件数量: {len(log_files)}")
        if len(log_files) > 0:
            print("    日志文件:")
            for file_path in log_files:
                print(f"      • {file_path.name}")
    
    # 检查配置文件
    config_dir = Path("config")
    if config_dir.exists():
        config_files = list(config_dir.glob("*"))
        print(f"  ⚙️ 配置文件数量: {len(config_files)}")
        if len(config_files) > 0:
            print("    配置文件:")
            for file_path in config_files:
                print(f"      • {file_path.name}")

def test_cli_with_new_structure():
    """测试CLI工具在新目录结构下的工作情况"""
    print("\n🔧 测试CLI工具...")
    
    try:
        # 使用新的配置路径测试CLI功能
        from thesis_inno_eval.config_manager import get_config_manager
        config_mgr = get_config_manager()
        
        # 测试基本配置读取
        openai_config = config_mgr.get_ai_model_config('openai')
        gemini_config = config_mgr.get_ai_model_config('gemini')
        
        print("  🤖 AI模型配置:")
        print(f"    OpenAI max_tokens: {openai_config.get('max_tokens', 'N/A'):,}")
        print(f"    Gemini max_tokens: {gemini_config.get('max_tokens', 'N/A'):,}")
        
        # 测试目录配置
        print("  📁 目录配置验证:")
        print(f"    输入目录: {config_mgr.get_input_dir()}")
        print(f"    输出目录: {config_mgr.get_output_dir()}")
        print(f"    日志目录: {config_mgr.get_logs_dir()}")
        
        print("   CLI工具兼容新目录结构")
        return True
        
    except Exception as e:
        print(f"  ❌ CLI工具测试失败: {e}")
        return False

def show_new_project_structure():
    """显示新的项目结构"""
    print("\n📂 新的项目结构:")
    print("""
thesis-inno-eval/
├── src/thesis_inno_eval/     # 主要代码包
│   ├── __init__.py
│   ├── cli.py
│   └── ...
├── tests/                    # 测试文件 (含 integration/)
├── data/                     # 数据目录
│   ├── input/               # 输入文件 (论文文档)
│   └── output/              # 输出文件
│       ├── analysis/        # AI 分析与回归数据
│       └── structured/      # 结构化 TOC/章节
├── docs/                     # 文档与报告
│   └── reports/             # 研究与实施报告
├── tools/                    # 辅助脚本
│   ├── analysis/            # 数据分析
│   ├── maintenance/         # 维护与迁移
│   ├── verification/        # 验证脚本
│   └── legacy/              # 历史实验
├── config/                   # 配置与规则 (conf.yaml 等)
├── logs/                     # 运行日志
├── pyproject.toml            # 项目配置
├── README.md                 # 项目说明
└── uv.lock                   # 依赖锁定
    """)

if __name__ == "__main__":
    print("🎯 目录结构和配置测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        ("目录结构", test_directory_structure),
        ("配置管理器", test_config_manager),
        ("文件组织", test_file_organization),
        ("CLI工具", test_cli_with_new_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试出错: {e}")
            results.append((test_name, False))
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📋 测试结果:")
    all_passed = True
    for test_name, passed in results:
        status = " 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！项目目录结构整理成功！")
        show_new_project_structure()
        
        print("\n💡 使用建议:")
        print("• 输入文件放在 data/input/ 目录")
        print("• 分析结果在 data/output/analysis/ 查看")
        print("• 结构化数据在 data/output/structured/ 维护")
        print("• 文档与报告集中在 docs/ 与 docs/reports/")
        print("• 辅助脚本按类别位于 tools/ 下")
        print("• 运行: uv run thesis-eval config 查看当前配置")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和目录结构")
