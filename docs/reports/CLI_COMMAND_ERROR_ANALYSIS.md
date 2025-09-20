# CLI 命令错误分析和解决方案

## 🔍 错误分析

**错误信息**:
```
🔧 提取模式: batch-sections
📊 批次大小: 10,000 字符
❌ 处理文件失败 (extract_session_0_1755785902): 文件不存在: evaluate
```

**问题原因**:
用户可能执行了错误的命令格式，系统将 "evaluate" 误认为是文件名参数。

## 🎯 可能的错误命令

用户可能执行了以下错误命令之一：

### ❌ 错误命令 1:
```bash
uv run thesis-eval extract evaluate --help
```

### ❌ 错误命令 2:
```bash
uv run thesis-eval extract evaluate 文件路径
```

## ✅ 正确的命令格式

### 1. **查看 extract 命令帮助**:
```bash
uv run thesis-eval extract --help
```

### 2. **查看 evaluate 命令帮助**:
```bash
uv run thesis-eval evaluate --help
```

### 3. **提取论文信息**:
```bash
uv run thesis-eval extract 文件路径
```

### 4. **评估论文**:
```bash
uv run thesis-eval evaluate 文件路径
```

### 5. **基于缓存快速评估**:
```bash
uv run thesis-eval eval-cached 文件路径
```

## 🔧 建议的解决方案

### 立即解决
1. **检查命令格式**:
   ```bash
   # 正确的提取命令
   uv run thesis-eval extract data/input/你的文件.pdf
   
   # 正确的评估命令  
   uv run thesis-eval evaluate data/input/你的文件.pdf
   ```

2. **查看可用文件**:
   ```bash
   uv run thesis-eval files
   ```

3. **查看命令帮助**:
   ```bash
   uv run thesis-eval --help
   uv run thesis-eval extract --help
   uv run thesis-eval evaluate --help
   ```

### 代码改进建议

在 CLI 中添加更好的错误处理和用户提示。

## 📋 命令参考

| 命令 | 用途 | 示例 |
|------|------|------|
| `extract` | 提取论文结构化信息 | `thesis-eval extract file.pdf` |
| `evaluate` | 完整评估流程 | `thesis-eval evaluate file.pdf` |
| `eval-cached` | 基于缓存的快速评估 | `thesis-eval eval-cached file.pdf` |
| `files` | 查看输入输出文件 | `thesis-eval files` |
| `info` | 查看系统配置 | `thesis-eval info` |

## 🎯 用户应该执行的正确命令

根据错误信息，用户想要提取论文信息，应该执行：

```bash
# 列出可用文件
uv run thesis-eval files

# 提取特定文件的信息
uv run thesis-eval extract data/input/你的论文文件.pdf

# 或者评估文件（包含提取步骤）
uv run thesis-eval evaluate data/input/你的论文文件.pdf
```
