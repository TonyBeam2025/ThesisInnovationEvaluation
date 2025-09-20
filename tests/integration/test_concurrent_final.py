#!/usr/bin/env python3
"""
简化版论文信息结构化抽取并发测试
专门验证并发处理框架是否正常工作
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

def test_concurrent_ai_analysis():
    """测试并发AI分析功能"""
    print("🔬 测试论文信息抽取的并发AI分析功能")
    print("=" * 50)
    
    try:
        from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        from thesis_inno_eval.ai_client import get_ai_client
        
        print(" 成功导入提取器和AI客户端")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    
    # 检查AI客户端
    ai_client = get_ai_client()
    if not ai_client:
        print("⚠️ AI客户端不可用，跳过AI相关测试")
        return False
    else:
        print(" AI客户端可用")
    
    # 创建提取器实例
    extractor = ThesisExtractorPro()
    
    # 模拟章节分析任务
    mock_section_tasks = [
        {
            'section_name': '摘要分析',
            'content': '本文研究了基于深度学习的文本分类方法，提出了一种新的神经网络架构...' * 20,
            'section_info': {'type': 'abstract', 'length': 1200, 'confidence': 0.9}
        },
        {
            'section_name': '文献综述',
            'content': '当前文本分类领域的研究主要集中在传统机器学习和深度学习方法上...' * 30,
            'section_info': {'type': 'literature_review', 'length': 1800, 'confidence': 0.85}
        },
        {
            'section_name': '方法论',
            'content': '本研究采用了多层感知机(MLP)和可分离卷积神经网络(SepCNN)相结合的方法...' * 25,
            'section_info': {'type': 'methodology', 'length': 1500, 'confidence': 0.92}
        },
        {
            'section_name': '实验结果',
            'content': '通过在多个数据集上的实验验证，本文提出的方法在准确率和F1分数上都表现优异...' * 20,
            'section_info': {'type': 'results', 'length': 1200, 'confidence': 0.88}
        }
    ]
    
    print(f"\n📊 准备并发测试: {len(mock_section_tasks)} 个模拟章节")
    
    # 测试1: 并发章节分析
    print("\n🚀 测试1: 并发章节分析")
    try:
        start_time = time.time()
        
        # 直接调用并发分析方法
        concurrent_results = extractor._analyze_sections_concurrently(mock_section_tasks)
        
        elapsed_time = time.time() - start_time
        print(f" 并发章节分析完成: {len(concurrent_results)}/{len(mock_section_tasks)} 成功")
        print(f"⏱️ 总耗时: {elapsed_time:.2f}秒")
        
    except Exception as e:
        print(f"❌ 并发章节分析测试失败: {e}")
        return False
    
    # 测试2: 并发评估任务
    print("\n🚀 测试2: 并发评估任务")
    try:
        def mock_innovation_eval(data):
            """模拟创新性评估"""
            time.sleep(0.5)  # 模拟AI处理时间
            return {
                'innovation_score': 85,
                'novelty_aspects': ['新的网络架构', '改进的训练方法'],
                'evaluation_details': '该研究在网络设计上有一定创新性'
            }
        
        def mock_technical_eval(data):
            """模拟技术深度评估"""
            time.sleep(0.8)
            return {
                'technical_score': 78,
                'complexity_level': 'high',
                'technical_strengths': ['理论基础扎实', '实验设计合理']
            }
        
        def mock_writing_eval(data):
            """模拟写作质量评估"""
            time.sleep(0.3)
            return {
                'writing_score': 82,
                'clarity_score': 85,
                'structure_score': 80
            }
        
        # 准备评估任务
        evaluation_tasks = [
            ('创新性评估', mock_innovation_eval, {'content': 'test_data_1'}),
            ('技术深度评估', mock_technical_eval, {'content': 'test_data_2'}),
            ('写作质量评估', mock_writing_eval, {'content': 'test_data_3'})
        ]
        
        start_time = time.time()
        
        # 调用并发评估方法
        eval_results = extractor._execute_evaluation_tasks_concurrently(evaluation_tasks)
        
        elapsed_time = time.time() - start_time
        print(f" 并发评估任务完成: {len(eval_results)}/{len(evaluation_tasks)} 成功")
        print(f"⏱️ 总耗时: {elapsed_time:.2f}秒")
        
        # 显示评估结果
        for task_name, result in eval_results.items():
            if result:
                score = result.get('innovation_score') or result.get('technical_score') or result.get('writing_score')
                print(f"   📊 {task_name}: 得分 {score}")
        
    except Exception as e:
        print(f"❌ 并发评估测试失败: {e}")
        return False
    
    return True

def test_basic_concurrent_functionality():
    """测试基础并发功能"""
    print("\n🔬 测试基础ThreadPoolExecutor并发功能")
    print("=" * 50)
    
    def worker_task(task_id, processing_time):
        """模拟工作任务"""
        thread_id = threading.current_thread().ident
        print(f"   🔄 线程 {thread_id} 开始执行任务 {task_id}")
        
        # 模拟不同的处理时间
        time.sleep(processing_time)
        
        result = {
            'task_id': task_id,
            'thread_id': thread_id,
            'processing_time': processing_time,
            'result_data': f"Task {task_id} processed successfully",
            'timestamp': time.time()
        }
        
        print(f"    线程 {thread_id} 完成任务 {task_id} ({processing_time}s)")
        return result
    
    # 定义测试任务
    tasks = [
        (1, 0.5),  # 任务ID, 处理时间
        (2, 0.8),
        (3, 0.3),
        (4, 0.6),
        (5, 0.4)
    ]
    
    print(f"📊 准备测试 {len(tasks)} 个并发任务")
    
    try:
        # 并发执行
        print("\n🚀 并发执行:")
        concurrent_start = time.time()
        
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(worker_task, task_id, duration): task_id
                for task_id, duration in tasks
            }
            
            # 收集结果
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"   ❌ 任务 {task_id} 异常: {e}")
        
        concurrent_time = time.time() - concurrent_start
        
        # 顺序执行（对比）
        print(f"\n🔄 顺序执行（对比）:")
        sequential_start = time.time()
        
        for task_id, duration in tasks:
            worker_task(task_id, duration)
        
        sequential_time = time.time() - sequential_start
        
        # 性能分析
        print(f"\n📊 性能分析:")
        print(f"   🚀 并发执行时间: {concurrent_time:.2f}秒")
        print(f"   🔄 顺序执行时间: {sequential_time:.2f}秒")
        print(f"   ⚡ 加速比: {sequential_time/concurrent_time:.2f}x")
        print(f"   📈 并发效率: {(sequential_time/concurrent_time)/3*100:.1f}%")
        print(f"    成功处理: {len(results)}/{len(tasks)} 个任务")
        
        return True
        
    except Exception as e:
        print(f"❌ 基础并发测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 论文信息抽取并发处理验证测试")
    print("=" * 60)
    print(f"🕐 测试开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_tests_passed = True
    
    # 测试1: 基础并发功能
    if not test_basic_concurrent_functionality():
        all_tests_passed = False
    
    # 测试2: 论文抽取并发功能
    if not test_concurrent_ai_analysis():
        all_tests_passed = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 所有并发功能测试通过!")
        print(" 论文信息抽取的并发处理功能验证成功")
        print("📊 并发处理能够显著提升处理效率")
    else:
        print("❌ 部分测试失败")
        print("⚠️ 请检查相关配置和依赖")
    
    print(f"🕐 测试结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
