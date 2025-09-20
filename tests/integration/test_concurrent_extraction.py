#!/usr/bin/env python3
"""
测试论文信息结构化抽取的并发处理功能
验证多线程并发分析是否正常工作
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

# 确保在uv环境中能正确导入模块
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))

try:
    from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
    from thesis_inno_eval.ai_client import get_ai_client
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

class ConcurrentExtractionTester:
    """并发抽取测试器"""
    
    def __init__(self):
        self.results = {}
        self.timing_stats = {}
        self.thread_usage = {}
        
    def find_test_documents(self) -> list:
        """查找可用于测试的文档"""
        # 指定测试文档
        target_doc = "1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
        target_path = project_root / "data" / "input" / target_doc
        
        test_docs = []
        
        # 检查指定文档是否存在
        if target_path.exists():
            test_docs.append(str(target_path))
            print(f"    找到指定测试文档: {target_doc}")
        else:
            print(f"   ❌ 未找到指定文档: {target_path}")
            print("   📁 正在搜索其他可用文档...")
            
            # 备用方案：查找其他文档
            for file_path in (project_root / "data" / "input").glob("*.docx"):
                if file_path.stat().st_size > 100000:  # 文件大小大于100KB
                    test_docs.append(str(file_path))
                    if len(test_docs) >= 1:  # 只需要一个测试文档
                        break
        
        return test_docs
    
    def extract_single_document(self, doc_path: str, doc_id: str) -> dict:
        """提取单个文档的信息（用于测试并发）"""
        thread_id = threading.current_thread().ident
        start_time = time.time()
        
        print(f"🔍 线程 {thread_id} 开始处理文档: {Path(doc_path).name}")
        
        try:
            # 创建提取器实例
            extractor = ThesisExtractorPro()
            
            # 先读取文档内容
            if doc_path.lower().endswith('.pdf'):
                from thesis_inno_eval.extract_sections_with_ai import extract_text_from_pdf
                text = extract_text_from_pdf(doc_path)
            elif doc_path.lower().endswith(('.docx', '.doc')):
                from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word
                text = extract_text_from_word(doc_path)
            else:
                raise ValueError(f"不支持的文件格式: {doc_path}")
            
            # 执行提取
            result = extractor.extract_with_integrated_strategy(text, doc_path)
            
            elapsed_time = time.time() - start_time
            
            # 记录线程使用情况
            if thread_id not in self.thread_usage:
                self.thread_usage[thread_id] = []
            self.thread_usage[thread_id].append({
                'doc_id': doc_id,
                'doc_name': Path(doc_path).name,
                'processing_time': elapsed_time,
                'success': bool(result and result.get('extracted_fields', 0) > 0)
            })
            
            print(f" 线程 {thread_id} 完成文档处理: {Path(doc_path).name} ({elapsed_time:.1f}s)")
            
            return {
                'doc_id': doc_id,
                'doc_path': doc_path,
                'result': result,
                'processing_time': elapsed_time,
                'thread_id': thread_id,
                'success': bool(result and result.get('extracted_fields', 0) > 0)
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ 线程 {thread_id} 处理文档失败: {Path(doc_path).name} - {e}")
            
            return {
                'doc_id': doc_id,
                'doc_path': doc_path,
                'result': None,
                'processing_time': elapsed_time,
                'thread_id': thread_id,
                'success': False,
                'error': str(e)
            }
    
    def test_concurrent_processing(self, test_docs: list, max_workers: int = 3) -> dict:
        """测试并发处理 - 针对单篇论文多次并发分析"""
        print(f"\n🚀 开始并发测试...")
        print(f"   📄 测试文档: {Path(test_docs[0]).name}")
        print(f"   🔧 最大并发数: {max_workers}")
        print(f"   🔄 并发任务数: {max_workers} (同一文档多次处理)")
        print(f"   ⏰ 开始时间: {time.strftime('%H:%M:%S')}")
        
        concurrent_start = time.time()
        results = []
        
        # 对同一文档启动多个并发任务来测试并发功能
        doc_path = test_docs[0]
        
        # 使用ThreadPoolExecutor进行并发处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交多个相同文档的处理任务（模拟并发处理场景）
            future_to_doc = {
                executor.submit(self.extract_single_document, doc_path, f"concurrent_task_{i+1}"): f"task_{i+1}"
                for i in range(max_workers)
            }
            
            print(f"   📤 已提交 {len(future_to_doc)} 个并发任务")
            
            # 收集结果
            for future in as_completed(future_to_doc):
                task_name = future_to_doc[future]
                try:
                    result = future.result(timeout=300)  # 5分钟超时
                    results.append(result)
                    
                    status = " 成功" if result['success'] else "❌ 失败"
                    print(f"   {status} {task_name} ({result['processing_time']:.1f}s, 线程{result['thread_id']})")
                    
                except Exception as e:
                    print(f"   ❌ 并发任务异常: {task_name} - {e}")
                    results.append({
                        'doc_id': f"{task_name}_error",
                        'doc_path': doc_path,
                        'result': None,
                        'processing_time': 0,
                        'thread_id': None,
                        'success': False,
                        'error': str(e)
                    })
        
        concurrent_total_time = time.time() - concurrent_start
        
        return {
            'concurrent_results': results,
            'concurrent_total_time': concurrent_total_time,
            'max_workers': max_workers,
            'success_count': sum(1 for r in results if r['success']),
            'total_docs': len(test_docs),
            'concurrent_tasks': len(results)
        }
    
    def test_sequential_processing(self, test_docs: list, task_count: int = 3) -> dict:
        """测试顺序处理（用于对比） - 对同一文档进行多次顺序处理"""
        print(f"\n🔄 开始顺序测试（对比基准）...")
        print(f"   📄 测试文档: {Path(test_docs[0]).name}")
        print(f"   🔄 顺序任务数: {task_count}")
        
        sequential_start = time.time()
        results = []
        doc_path = test_docs[0]
        
        for i in range(task_count):
            print(f"   📄 顺序处理任务 {i+1}/{task_count}")
            result = self.extract_single_document(doc_path, f"seq_task_{i+1}")
            results.append(result)
            
            status = " 成功" if result['success'] else "❌ 失败"
            print(f"   {status} 任务{i+1} ({result['processing_time']:.1f}s)")
        
        sequential_total_time = time.time() - sequential_start
        
        return {
            'sequential_results': results,
            'sequential_total_time': sequential_total_time,
            'success_count': sum(1 for r in results if r['success']),
            'total_docs': len(test_docs),
            'sequential_tasks': len(results)
        }
    
    def analyze_concurrency_performance(self, concurrent_data: dict, sequential_data: dict):
        """分析并发性能"""
        print(f"\n📊 并发性能分析报告")
        print("=" * 60)
        
        # 基本统计
        print(f"📄 测试文档: 1篇 (多次处理)")
        print(f"🔧 并发工作线程: {concurrent_data['max_workers']}")
        print(f"� 并发任务数: {concurrent_data.get('concurrent_tasks', 0)}")
        print(f"🔄 顺序任务数: {sequential_data.get('sequential_tasks', 0)}")
        print(f" 并发成功率: {concurrent_data['success_count']}/{concurrent_data.get('concurrent_tasks', 0)} ({concurrent_data['success_count']/concurrent_data.get('concurrent_tasks', 1)*100:.1f}%)")
        print(f" 顺序成功率: {sequential_data['success_count']}/{sequential_data.get('sequential_tasks', 0)} ({sequential_data['success_count']/sequential_data.get('sequential_tasks', 1)*100:.1f}%)")
        
        # 时间对比
        print(f"\n⏱️ 时间性能对比:")
        print(f"   🚀 并发总时间: {concurrent_data['concurrent_total_time']:.1f}s")
        print(f"   🔄 顺序总时间: {sequential_data['sequential_total_time']:.1f}s")
        
        if sequential_data['sequential_total_time'] > 0:
            speedup = sequential_data['sequential_total_time'] / concurrent_data['concurrent_total_time']
            efficiency = speedup / concurrent_data['max_workers'] * 100
            print(f"   ⚡ 加速比: {speedup:.2f}x")
            print(f"   📈 并发效率: {efficiency:.1f}%")
            
            if speedup > 1.5:
                print(f"   🎉 并发处理显著提升性能!")
            elif speedup > 1.1:
                print(f"   👍 并发处理有一定效果")
            else:
                print(f"   ⚠️ 并发效果不明显，可能受限于I/O或API限制")
        
        # 线程使用分析
        print(f"\n🧵 线程使用情况:")
        for thread_id, tasks in self.thread_usage.items():
            total_time = sum(task['processing_time'] for task in tasks)
            success_count = sum(1 for task in tasks if task['success'])
            print(f"   线程 {thread_id}: 处理 {len(tasks)} 个任务, 总时间 {total_time:.1f}s, 成功 {success_count} 个")
        
        # 详细结果
        print(f"\n📋 详细处理结果:")
        for result in concurrent_data['concurrent_results']:
            status = "" if result['success'] else "❌"
            print(f"   {status} {result['doc_id']} - {result['processing_time']:.1f}s (线程{result['thread_id']})")
            
            if result['result']:
                extracted_count = result['result'].get('extracted_fields', 0)
                confidence = result['result'].get('confidence', 0)
                print(f"      📊 提取字段: {extracted_count}, 置信度: {confidence:.1f}%")
    
    def save_test_results(self, concurrent_data: dict, sequential_data: dict):
        """保存测试结果"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        report_file = project_root / f"concurrent_test_report_{timestamp}.json"
        
        report_data = {
            'test_timestamp': timestamp,
            'test_config': {
                'max_workers': concurrent_data['max_workers'],
                'total_docs': concurrent_data['total_docs']
            },
            'concurrent_performance': {
                'total_time': concurrent_data['concurrent_total_time'],
                'success_count': concurrent_data['success_count'],
                'results': concurrent_data['concurrent_results']
            },
            'sequential_performance': {
                'total_time': sequential_data['sequential_total_time'],
                'success_count': sequential_data['success_count'],
                'results': sequential_data['sequential_results']
            },
            'thread_usage': self.thread_usage,
            'performance_metrics': {
                'speedup': sequential_data['sequential_total_time'] / concurrent_data['concurrent_total_time'] if concurrent_data['concurrent_total_time'] > 0 else 0,
                'efficiency': (sequential_data['sequential_total_time'] / concurrent_data['concurrent_total_time'] / concurrent_data['max_workers'] * 100) if concurrent_data['concurrent_total_time'] > 0 else 0
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 测试报告已保存: {report_file}")

def main():
    """主测试函数"""
    print("🔬 论文信息结构化抽取并发处理测试")
    print("=" * 50)
    
    # 检查AI客户端
    print("🔧 检查AI客户端...")
    try:
        ai_client = get_ai_client()
        if ai_client:
            print("    AI客户端初始化成功")
        else:
            print("   ⚠️ AI客户端不可用，部分功能可能受限")
    except Exception as e:
        print(f"   ❌ AI客户端检查失败: {e}")
    
    # 创建测试器
    tester = ConcurrentExtractionTester()
    
    # 查找测试文档
    print("\n📁 查找测试文档...")
    test_docs = tester.find_test_documents()
    
    if not test_docs:
        print("   ❌ 未找到适合的测试文档")
        print("   💡 请在项目根目录放置一些 .docx 或 .pdf 论文文件")
        return
    
    print(f"    找到 {len(test_docs)} 个测试文档:")
    for doc in test_docs:
        print(f"      📄 {Path(doc).name}")
    
    # 执行测试
    try:
        # 并发测试 - 对同一文档启动3个并发任务
        concurrent_data = tester.test_concurrent_processing(test_docs, max_workers=3)
        
        # 顺序测试 - 对同一文档进行3次顺序处理
        sequential_data = tester.test_sequential_processing(test_docs, task_count=3)
        
        # 分析结果
        tester.analyze_concurrency_performance(concurrent_data, sequential_data)
        
        # 保存结果
        tester.save_test_results(concurrent_data, sequential_data)
        
        print(f"\n🎉 并发测试完成!")
        print(f"📋 测试总结:")
        print(f"   📄 测试文档: {Path(test_docs[0]).name}")
        print(f"   🚀 并发处理: {concurrent_data['success_count']}/{concurrent_data.get('concurrent_tasks', 0)} 成功")
        print(f"   🔄 顺序处理: {sequential_data['success_count']}/{sequential_data.get('sequential_tasks', 0)} 成功")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
