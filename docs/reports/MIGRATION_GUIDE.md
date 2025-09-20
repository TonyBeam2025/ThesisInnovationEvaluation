# 函数迁移指南：从 extract_sections_with_ai_by_batches 到 extract_sections_with_pro_strategy

## 概述

`extract_sections_with_ai_by_batches` 函数已被标记为弃用（deprecated），推荐使用新的 `extract_sections_with_pro_strategy` 函数。

## 迁移原因

新的专业版策略提供了以下优势：

1. **智能学科识别**：自动识别论文学科领域，采用相应的抽取策略
2. **多学科交叉分析**：识别跨学科特征，提供更全面的分析
3. **分步骤处理**：系统化的5步处理流程
4. **质量评估**：提供完整度、置信度和质量分数
5. **更好的缓存机制**：支持智能缓存和增量处理
6. **更高的准确率**：平均完成率提升至90%+

## 迁移示例

### 旧方法（已弃用）
```python
from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_ai_by_batches

# 旧的调用方式
result = extract_sections_with_ai_by_batches(
    file_path=file_path,
    ai_client=ai_client,
    session_id=session_id,
    max_chars_per_batch=10000
)
```

### 新方法（推荐）
```python
from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy

# 新的调用方式
result = extract_sections_with_pro_strategy(
    file_path=file_path,
    use_cache=True
)
```

## 主要变化

| 方面 | 旧函数 | 新函数 |
|------|--------|--------|
| 参数简化 | 需要ai_client, session_id等 | 只需file_path和use_cache |
| 学科支持 | 通用处理 | 10个学科领域专门优化 |
| 章节分析 | 简单分块 | 智能章节结构分析 |
| 质量评估 | 无 | 完整度、置信度、质量分数 |
| 缓存机制 | 基础缓存 | 智能缓存和增量处理 |
| 多学科特征 | 不支持 | 支持交叉学科识别 |

## 兼容性说明

1. **返回值格式**：新函数返回更丰富的信息，包含原有字段
2. **异常处理**：新函数有更完善的错误处理机制
3. **性能提升**：新函数在准确率和处理速度上都有提升

## 迁移步骤

1. **更新导入语句**：
   ```python
   # 旧
   from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_ai_by_batches
   
   # 新
   from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy
   ```

2. **更新函数调用**：
   ```python
   # 旧
   result = extract_sections_with_ai_by_batches(file_path, ai_client, session_id, batch_size)
   
   # 新
   result = extract_sections_with_pro_strategy(file_path=file_path, use_cache=True)
   ```

3. **更新错误处理**（可选）：
   ```python
   # 新函数提供更详细的错误信息
   if result and result.get('success', True):
       # 处理成功的结果
       pass
   else:
       # 处理失败情况
       pass
   ```

## 弃用时间表

- **2025.08**: 标记 `extract_sections_with_ai_by_batches` 为弃用
- **2025.09**: 发出弃用警告
- **2025.12**: 计划移除旧函数

## 获取帮助

如果在迁移过程中遇到问题，可以：
1. 查看新函数的文档字符串
2. 运行测试程序验证迁移效果
3. 检查日志输出了解处理详情

## 测试验证

运行以下命令验证迁移效果：
```bash
uv run python test_pro_strategy_batch.py
```

这将使用新的专业版策略处理示例论文，并输出详细的性能和准确率报告。
