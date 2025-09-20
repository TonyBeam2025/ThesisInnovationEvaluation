# 🔧 CLI命令错误解决方案

## ❌ 遇到的错误

```
🔧 提取模式: batch-sections
📊 批次大小: 10,000 字符
❌ 处理文件失败 (extract_session_0_1755785902): 文件不存在: evaluate
```

## 🎯 问题分析

这个错误表明用户可能执行了错误的命令格式，系统将 "evaluate" 误认为是要处理的文件名。

## ✅ 立即解决方案

### 1. **查看可用文件**
```bash
uv run thesis-eval files
```
这会显示 `data/input/` 和 `data/output/` 目录中的所有文件。

### 2. **正确的命令格式**

#### 提取论文结构化信息:
```bash
# 替换 "你的文件.pdf" 为实际文件名
uv run thesis-eval extract data/input/你的文件.pdf
```

#### 完整评估流程:
```bash
# 评估包含提取步骤
uv run thesis-eval evaluate data/input/你的文件.pdf
```

#### 基于缓存的快速评估:
```bash
# 如果已经有提取结果，使用这个更快
uv run thesis-eval eval-cached data/input/你的文件.pdf
```

### 3. **查看命令帮助**
```bash
# 查看所有命令
uv run thesis-eval --help

# 查看具体命令帮助
uv run thesis-eval extract --help
uv run thesis-eval evaluate --help
```

## 📋 常见错误和解决方法

### ❌ 错误命令
```bash
# 这些都是错误的
uv run thesis-eval extract evaluate
uv run thesis-eval evaluate extract  
uv run thesis-eval extract --help evaluate
```

### ✅ 正确命令
```bash
# 这些是正确的
uv run thesis-eval extract data/input/论文.pdf
uv run thesis-eval evaluate data/input/论文.pdf
uv run thesis-eval extract --help
```

## 🎯 根据你的情况的具体建议

1. **首先查看可用文件**:
   ```bash
   uv run thesis-eval files
   ```

2. **如果你想提取论文信息**:
   ```bash
   # 用你的实际文件名替换
   uv run thesis-eval extract data/input/你的论文文件.pdf
   ```

3. **如果你想完整评估论文**:
   ```bash
   # 用你的实际文件名替换
   uv run thesis-eval evaluate data/input/你的论文文件.pdf
   ```

## 🔍 文件路径格式

确保使用正确的文件路径格式：

### ✅ 正确格式
- `data/input/文件名.pdf`
- `data/input/文件名.docx`
- `./data/input/文件名.pdf`
- `/完整路径/文件名.pdf`

### ❌ 常见错误
- `文件名.pdf` (缺少路径)
- `evaluate` (这是命令，不是文件)
- `extract` (这是命令，不是文件)

## 📊 命令速查表

| 目的 | 命令 | 说明 |
|------|------|------|
| 查看文件 | `thesis-eval files` | 列出所有输入输出文件 |
| 提取信息 | `thesis-eval extract <文件>` | 提取论文结构化信息 |
| 完整评估 | `thesis-eval evaluate <文件>` | 提取+检索+评估 |
| 快速评估 | `thesis-eval eval-cached <文件>` | 基于缓存的快速评估 |
| 查看帮助 | `thesis-eval --help` | 显示所有命令 |
| 系统信息 | `thesis-eval info` | 显示系统配置 |

## 💡 下一步操作

1. 运行 `uv run thesis-eval files` 查看可用文件
2. 选择要处理的文件
3. 使用正确的命令格式处理文件
4. 如果仍有问题，使用 `--help` 查看详细帮助
