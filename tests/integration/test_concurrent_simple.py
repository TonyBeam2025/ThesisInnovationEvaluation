#!/usr/bin/env python3
"""
简化版并发处理测试脚本
专门测试论文信息抽取的多线程并发功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
import time
import json
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径，支持uv环境
project_root = PROJECT_ROOT
sys.path.insert(0, str(project_root / "src"))

def test_concurrent_section_analysis():
    """测试并发章节分析功能"""
    print("🔬 测试并发章节分析功能")
    print("=" * 40)
    
    try:
        from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        print(" 成功导入 ThesisExtractorPro")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    
    # 创建测试提取器
    extractor = ThesisExtractorPro()
    
    # 模拟多个章节任务
    mock_section_tasks = [
        {
            'section_name': '摘要',
            'content': '本文研究了人工智能在学术论文分析中的应用...' * 50,
            'section_info': {'type': 'abstract', 'length': 2500}
        },
        {
            'section_name': '文献综述',
            'content': '当前研究领域的相关工作包括机器学习、自然语言处理...' * 100,
            'section_info': {'type': 'literature_review', 'length': 5000}
        },
        {
            'section_name': '研究方法',
            'content': '本研究采用了深度学习方法，具体包括卷积神经网络...' * 75,
            'section_info': {'type': 'methodology', 'length': 3750}
        },
        {
            'section_name': '实验结果',
            'content': '实验结果表明，提出的方法在多个数据集上都取得了...' * 60,
            'section_info': {'type': 'results', 'length': 3000}
        }
    ]
    
    print(f"📊 准备测试 {len(mock_section_tasks)} 个模拟章节")
    
    # 测试并发分析
    try:
        start_time = time.time()
        results = extractor._analyze_sections_concurrently(mock_section_tasks)
        elapsed_time = time.time() - start_time
        
        print(f"\n 并发章节分析完成!")
        print(f"   ⏱️ 总耗时: {elapsed_time:.2f}秒")
        print(f"   📊 处理结果: {len(results)}/{len(mock_section_tasks)} 个章节")
        
        for section_name, result in results.items():
            if result:
                print(f"    {section_name}: 分析成功")
            else:
                print(f"   ❌ {section_name}: 分析失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 并发分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concurrent_evaluation_tasks():
    """测试并发评估任务功能"""
    print("\n🔬 测试并发评估任务功能")
    print("=" * 40)
    
    try:
        from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        extractor = ThesisExtractorPro()
        
        # 模拟评估任务
        def mock_task_1(data):
            time.sleep(0.5)  # 模拟处理时间
            return {'task1_result': 'success', 'score': 85}
        
        def mock_task_2(data):
            time.sleep(0.8)  # 模拟不同的处理时间
            return {'task2_result': 'success', 'score': 92}
        
        def mock_task_3(data):
            time.sleep(0.3)
            return {'task3_result': 'success', 'score': 78}
        
        evaluation_tasks = [
            ('创新性评估', mock_task_1, {'content': 'test_data_1'}),
            ('技术深度评估', mock_task_2, {'content': 'test_data_2'}),
            ('写作质量评估', mock_task_3, {'content': 'test_data_3'})
        ]
        
        print(f"📊 准备测试 {len(evaluation_tasks)} 个评估任务")
        
        start_time = time.time()
        results = extractor._execute_evaluation_tasks_concurrently(evaluation_tasks)
        elapsed_time = time.time() - start_time
        
        print(f"\n 并发评估任务完成!")
        print(f"   ⏱️ 总耗时: {elapsed_time:.2f}秒")
        print(f"   📊 评估结果: {len(results)} 个任务完成")
        
        for task_name, result in results.items():
            if result:
                score = result.get('score', 'N/A')
                print(f"    {task_name}: 评估完成 (得分: {score})")
            else:
                print(f"   ❌ {task_name}: 评估失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 并发评估测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_thread_pool_functionality():
    """测试基本的线程池功能"""
    print("\n🔬 测试基本线程池功能")
    print("=" * 40)
    
    def worker_task(task_id, duration):
        """工作任务"""
        thread_id = threading.current_thread().ident
        print(f"   🔄 线程 {thread_id} 开始执行任务 {task_id}")
        time.sleep(duration)
        result = f"Task {task_id} completed by thread {thread_id}"
        print(f"    线程 {thread_id} 完成任务 {task_id}")
        return result
    
    # 测试任务
    tasks = [
        (1, 0.5),
        (2, 0.8),
        (3, 0.3),
        (4, 0.6),
        (5, 0.4)
    ]
    
    print(f"📊 测试 {len(tasks)} 个并发任务")
    
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            start_time = time.time()
            
            # 提交任务
            future_to_task = {
                executor.submit(worker_task, task_id, duration): task_id
                for task_id, duration in tasks
            }
            
            results = []
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"   ❌ 任务 {task_id} 异常: {e}")
            
            elapsed_time = time.time() - start_time
            
            print(f"\n 线程池测试完成!")
            print(f"   ⏱️ 总耗时: {elapsed_time:.2f}秒")
            print(f"   📊 完成任务: {len(results)}/{len(tasks)}")
            
            expected_sequential_time = sum(duration for _, duration in tasks)
            speedup = expected_sequential_time / elapsed_time
            print(f"   ⚡ 理论加速比: {speedup:.2f}x")
        
        return True
        
    except Exception as e:
        print(f"❌ 线程池测试失败: {e}")
        return False

def check_ai_client():
    """检查AI客户端是否可用"""
    print("🔧 检查AI客户端状态")
    print("=" * 40)
    
    try:
        from thesis_inno_eval.ai_client import get_ai_client
        ai_client = get_ai_client()
        
        if ai_client:
            print(" AI客户端初始化成功")
            print(f"   🔧 客户端类型: {type(ai_client).__name__}")
            return True
        else:
            print("⚠️ AI客户端为空")
            return False
            
    except Exception as e:
        print(f"❌ AI客户端检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 论文信息抽取并发处理测试")
    print("=" * 50)
    print(f"🕐 测试开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_tests_passed = True
    
    # 测试1: 检查AI客户端
    if not check_ai_client():
        print("⚠️ AI客户端不可用，但不影响并发功能测试")
    
    # 测试2: 基本线程池功能
    if not test_thread_pool_functionality():
        all_tests_passed = False
    
    # 测试3: 并发章节分析
    if not test_concurrent_section_analysis():
        all_tests_passed = False
    
    # 测试4: 并发评估任务
    if not test_concurrent_evaluation_tasks():
        all_tests_passed = False
    
    # 总结
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 所有并发功能测试通过!")
        print(" 论文信息抽取的并发处理功能正常工作")
    else:
        print("❌ 部分测试失败")
        print("⚠️ 请检查相关配置和依赖")
    
    print(f"🕐 测试结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
