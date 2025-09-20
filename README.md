# 基于AI的学位论文创新评估系统

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

基于人工智能技术的学位论文创新点评估和文献分析系统，支持中英文论文处理，提供全自动化的学术价值评估。

## ✨ 主要功能

- 🔍 **智能文献检索**: 集成CNKI API，自动检索相关学术论文
- 🤖 **AI内容分析**: 支持Gemini和OpenAI双AI引擎，提供深度内容理解
- 📊 **相似度分析**: 基于语义向量的论文相似度比较和排序
- 🌐 **多语言支持**: 中英文双语论文处理和跨语言文献匹配
- ⚙️ **配置化管理**: 完全可配置的参数系统，支持大规模论文处理
- 📄 **多格式支持**: 支持PDF、DOCX、Markdown等多种文档格式

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/thesis-inno-eval.git
cd thesis-inno-eval

# 安装依赖（推荐使用uv）
uv sync

# 或使用pip
pip install -e .
```

### 配置

1. 编辑 `config/conf.yaml`，根据部署环境配置 AI 模型、目录路径以及 CNKI 相关参数。
2. 若需自定义规则或策略，可更新 `config/rules.txt` 与 `config/strategy.txt`。
3. 设置环境变量：
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
export OPENAI_API_KEY="your_openai_api_key"
export CNKI_USERNAME="your_cnki_username"
export CNKI_PASSWORD="your_cnki_password"
```

### 使用示例

```python
from thesis_inno_eval import ThesisEvaluator

# 创建评估器
evaluator = ThesisEvaluator()

# 评估论文
result = evaluator.evaluate_thesis("path/to/thesis.pdf")

# 查看结果
print(f"创新度评分: {result.innovation_score}")
print(f"相关文献数量: {len(result.related_papers)}")
```

## 📋 系统要求

- Python 3.10+
- 4GB+ RAM （处理大型论文时建议8GB+）
- 稳定的网络连接（用于API调用）

## 🛠 开发

### 开发环境设置

```bash
# 安装开发依赖
uv sync --group dev

# 运行测试
uv run pytest

# 代码格式化
uv run black .
uv run isort .

# 类型检查
uv run mypy .
```

### 项目结构

```
thesis-inno-eval/
├── src/thesis_inno_eval/      # 核心源码
├── tests/                     # 单元 & 集成测试
│   └── integration/           # 回归脚本（默认跳过）
├── data/
│   ├── input/                # 原始论文
│   └── output/
│       ├── analysis/         # AI 分析与回归 JSON
│       └── structured/       # 结构化 TOC/章节
├── docs/
│   └── reports/              # 研究/更新报告
├── tools/                    # 辅助脚本
│   ├── analysis/
│   ├── maintenance/
│   ├── verification/
│   └── legacy/
├── config/                   # 配置与规则文件
├── logs/                     # 运行日志
├── pyproject.toml            # 构建配置
└── README.md                 # 项目说明
```

## 📊 性能特性

- **大容量处理**: 支持1M+ token，可处理1000+页论文
- **并发处理**: 多线程文献检索和AI分析
- **内存优化**: 流式处理大型文档，避免内存溢出
- **容错机制**: 自动重试和错误恢复

## 🤝 贡献

欢迎提交Issue和Pull Request！请查看[贡献指南](CONTRIBUTING.md)。

## 📄 许可证

本项目采用MIT许可证。详情请见[LICENSE](LICENSE)文件。

## 🙏 致谢

- [CNKI](https://www.cnki.net/) - 学术资源支持
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI分析引擎
- [OpenAI](https://openai.com/) - AI分析引擎
- [Sentence Transformers](https://www.sbert.net/) - 语义向量计算
