# 数据目录

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
