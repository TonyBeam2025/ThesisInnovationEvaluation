#!/usr/bin/env python3
"""
测试PDF/Word转Markdown缓存功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
from pathlib import Path
import time

def test_cache_functionality():
    """测试缓存功能"""
    
    # 检查测试文件
    test_file = Path("data/input/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩.pdf")
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print("🧪 测试PDF转Markdown缓存功能")
    print("=" * 50)
    
    # 导入缓存相关模块
    sys.path.append('src')
    from thesis_inno_eval.extract_sections_with_ai import extract_text_with_cache, get_document_cache
    
    cache_manager = get_document_cache()
    
    # 1. 清除现有缓存
    print("🗑️ 清除现有缓存...")
    cache_manager.clear_cache()
    
    # 2. 第一次提取（应该创建缓存）
    print(f"\n📄 第一次提取: {test_file.name}")
    start_time = time.time()
    
    content1 = extract_text_with_cache(str(test_file), use_cache=True)
    
    first_time = time.time() - start_time
    print(f"⏱️ 耗时: {first_time:.2f} 秒")
    print(f"📊 内容长度: {len(content1):,} 字符")
    
    if not content1:
        print("❌ 第一次提取失败")
        return False
    
    # 检查缓存是否创建
    if cache_manager.is_cached(str(test_file)):
        print(" 缓存创建成功")
    else:
        print("❌ 缓存创建失败")
        return False
    
    # 3. 第二次提取（应该使用缓存）
    print(f"\n📄 第二次提取: {test_file.name}")
    start_time = time.time()
    
    content2 = extract_text_with_cache(str(test_file), use_cache=True)
    
    second_time = time.time() - start_time
    print(f"⏱️ 耗时: {second_time:.2f} 秒")
    print(f"📊 内容长度: {len(content2):,} 字符")
    
    # 4. 验证结果
    print("\n📋 结果验证:")
    
    # 检查内容一致性
    if content1 == content2:
        print(" 内容一致性: 通过")
    else:
        print("❌ 内容一致性: 失败")
        return False
    
    # 检查性能提升
    speedup = first_time / second_time if second_time > 0 else float('inf')
    print(f"🚀 性能提升: {speedup:.1f}x")
    
    if speedup > 2:
        print(" 缓存效果: 显著")
    elif speedup > 1.2:
        print("🟨 缓存效果: 一般")
    else:
        print("❌ 缓存效果: 无效")
    
    # 5. 测试缓存信息
    print("\n💾 缓存信息:")
    cache_info = cache_manager.get_cache_info()
    
    if cache_info:
        print(f"   缓存目录: {cache_info['cache_dir']}")
        print(f"   缓存文件数: {cache_info['cached_files']}")
        print(f"   总大小: {cache_info['total_size_mb']} MB")
    
    # 6. 测试禁用缓存
    print(f"\n📄 禁用缓存测试: {test_file.name}")
    start_time = time.time()
    
    content3 = extract_text_with_cache(str(test_file), use_cache=False)
    
    no_cache_time = time.time() - start_time
    print(f"⏱️ 耗时: {no_cache_time:.2f} 秒")
    
    if abs(no_cache_time - first_time) < 2:  # 允许2秒误差
        print(" 禁用缓存: 正常")
    else:
        print("🟨 禁用缓存: 时间异常")
    
    # 7. 测试Markdown格式
    print("\n📝 Markdown格式检查:")
    
    # 检查Markdown特征
    markdown_features = [
        content1.startswith('#'),  # 标题
        '**源文件**' in content1,  # 元数据
        '**转换时间**' in content1,  # 时间戳
        '---' in content1,  # 分隔符
    ]
    
    if all(markdown_features):
        print(" Markdown格式: 正确")
    else:
        print("❌ Markdown格式: 不完整")
        missing_features = []
        feature_names = ['标题', '源文件信息', '转换时间', '分隔符']
        for i, feature in enumerate(markdown_features):
            if not feature:
                missing_features.append(feature_names[i])
        print(f"   缺失特征: {', '.join(missing_features)}")
    
    # 8. 保存样例到输出目录
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sample_file = output_dir / f"{test_file.stem}_cached_markdown_sample.md"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(content1)
    
    print(f"\n💾 样例已保存: {sample_file}")
    
    print("\n" + "=" * 50)
    print("🎯 缓存功能测试完成!")
    
    return True

if __name__ == "__main__":
    success = test_cache_functionality()
    sys.exit(0 if success else 1)
