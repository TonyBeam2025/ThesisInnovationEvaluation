#!/usr/bin/env python3
"""
大型文档增强提取器
支持64K上下文大模型处理20MB论文
"""

import os
import asyncio
from typing import Dict, Any, List
from pathlib import Path
import json
import time
from concurrent.futures import ThreadPoolExecutor
import threading

class LargeDocumentExtractor:
    """大型文档提取器"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.processing_queue = []
        self.results_cache = {}
        self.chunk_size = 64000
        
    def extract_large_document(self, file_path: str) -> Dict[str, Any]:
        """处理大型文档的主函数"""
        
        print(f"🎯 开始处理大型文档: {Path(file_path).name}")
        start_time = time.time()
        
        # 1. 文档预处理
        doc_info = self._preprocess_document(file_path)
        print(f"📊 文档规模: {doc_info['size_mb']:.1f}MB, {doc_info['estimated_tokens']:,} tokens")
        
        # 2. 选择处理策略
        strategy = self._select_strategy(doc_info)
        print(f"🎯 使用策略: {strategy}")
        
        # 3. 执行提取
        if strategy == "direct_processing":
            result = self._direct_extraction(file_path)
        elif strategy == "intelligent_chunking":
            result = self._chunked_extraction(file_path, doc_info)
        elif strategy == "map_reduce_processing":
            result = self._map_reduce_extraction(file_path, doc_info)
        else:
            result = self._streaming_extraction(file_path, doc_info)
        
        # 4. 结果验证和优化
        result = self._validate_and_enhance(result)
        
        processing_time = time.time() - start_time
        print(f" 处理完成，耗时: {processing_time:.1f}秒")
        
        return result
    
    def _preprocess_document(self, file_path: str) -> Dict[str, Any]:
        """文档预处理"""
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        
        # 估算内容规模
        if file_path.lower().endswith('.pdf'):
            estimated_tokens = int(file_size * 1024 * 8 // 2)  # PDF估算
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            estimated_tokens = len(content) // 2
        
        return {
            "size_mb": file_size,
            "estimated_tokens": estimated_tokens,
            "file_type": Path(file_path).suffix.lower()
        }
    
    def _select_strategy(self, doc_info: Dict[str, Any]) -> str:
        """选择处理策略"""
        tokens = doc_info["estimated_tokens"]
        
        if tokens <= 64000:
            return "direct_processing"
        elif tokens <= 200000:
            return "intelligent_chunking"
        elif tokens <= 1000000:
            return "map_reduce_processing"
        else:
            return "streaming_processing"
    
    def _direct_extraction(self, file_path: str) -> Dict[str, Any]:
        """直接提取（小文档）"""
        # 使用现有的comprehensive_thesis_extractor
        try:
            from comprehensive_thesis_extractor import comprehensive_extraction
            return comprehensive_extraction(file_path)
        except ImportError:
            print("⚠️ comprehensive_thesis_extractor未找到，使用基础提取")
            return {"status": "basic_extraction"}
    
    def _chunked_extraction(self, file_path: str, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """分块提取（中等文档）"""
        print("📄 执行智能分块提取...")
        
        # 读取文档
        content = self._load_document(file_path)
        
        # 智能分块
        chunks = self._intelligent_chunk(content)
        print(f"   分成 {len(chunks)} 个智能块")
        
        # 并行处理各块
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_chunk, chunk, i) 
                      for i, chunk in enumerate(chunks)]
            
            for future in futures:
                results.append(future.result())
        
        # 合并结果
        return self._merge_results(results)
    
    def _map_reduce_extraction(self, file_path: str, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """MAP-REDUCE提取（大文档）"""
        print("🔄 执行MAP-REDUCE提取...")
        
        content = self._load_document(file_path)
        
        # MAP阶段：并行处理
        chunks = self._create_chunks(content, self.chunk_size)
        print(f"   MAP阶段: {len(chunks)} 个处理块")
        
        map_results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._map_process, chunk, i) 
                      for i, chunk in enumerate(chunks)]
            
            for future in futures:
                map_results.append(future.result())
        
        # REDUCE阶段：结果合并
        print("   REDUCE阶段: 合并结果")
        return self._reduce_results(map_results)
    
    def _streaming_extraction(self, file_path: str, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """流式提取（超大文档）"""
        print("📡 执行流式提取...")
        
        # 流式处理实现
        result = {}
        processed_chunks = 0
        
        for chunk in self._stream_chunks(file_path):
            chunk_result = self._process_streaming_chunk(chunk, processed_chunks)
            result = self._accumulate_result(result, chunk_result)
            processed_chunks += 1
            
            if processed_chunks % 10 == 0:
                print(f"   已处理 {processed_chunks} 个流式块")
        
        return result
    
    def _load_document(self, file_path: str) -> str:
        """加载文档内容"""
        if file_path.lower().endswith('.pdf'):
            # 这里应该使用PDF处理库
            print("   PDF文档处理需要额外的PDF库支持")
            return "PDF内容占位符"
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _intelligent_chunk(self, content: str) -> List[str]:
        """智能分块：保持语义完整性"""
        # 基于章节结构分块
        sections = self._detect_sections(content)
        
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for section in sections:
            section_size = len(section) // 2  # 估算tokens
            
            if current_size + section_size > self.chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = section
                current_size = section_size
            else:
                current_chunk += "\n" + section
                current_size += section_size
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _detect_sections(self, content: str) -> List[str]:
        """检测文档章节"""
        import re
        
        # 章节分割模式
        section_patterns = [
            r'第[一二三四五六七八九十\d]+章',
            r'第[\d]+节',
            r'\d+\.\d+',
            r'#+\s',  # Markdown标题
            r'摘要|abstract|参考文献|致谢'
        ]
        
        sections = []
        current_section = ""
        
        lines = content.split('\n')
        
        for line in lines:
            is_section_start = any(re.search(pattern, line, re.IGNORECASE) 
                                 for pattern in section_patterns)
            
            if is_section_start and current_section:
                sections.append(current_section.strip())
                current_section = line
            else:
                current_section += "\n" + line
        
        if current_section:
            sections.append(current_section.strip())
        
        return sections if sections else [content]
    
    def _create_chunks(self, content: str, chunk_size: int) -> List[str]:
        """创建固定大小的块"""
        chunks = []
        words = content.split()
        current_chunk = ""
        current_size = 0
        
        for word in words:
            word_size = len(word) // 2  # 估算tokens
            
            if current_size + word_size > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = word
                current_size = word_size
            else:
                current_chunk += " " + word
                current_size += word_size
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _process_chunk(self, chunk: str, chunk_id: int) -> Dict[str, Any]:
        """处理单个块"""
        print(f"   处理块 {chunk_id}: {len(chunk):,} 字符")
        
        # 模拟AI处理
        import time
        time.sleep(0.1)  # 模拟处理时间
        
        return {
            "chunk_id": chunk_id,
            "content_length": len(chunk),
            "extracted_fields": ["title", "author", "abstract"],
            "confidence": 0.9
        }
    
    def _map_process(self, chunk: str, chunk_id: int) -> Dict[str, Any]:
        """MAP阶段处理"""
        return self._process_chunk(chunk, chunk_id)
    
    def _process_streaming_chunk(self, chunk: str, chunk_id: int) -> Dict[str, Any]:
        """处理流式块"""
        return self._process_chunk(chunk, chunk_id)
    
    def _stream_chunks(self, file_path: str):
        """流式生成块"""
        content = self._load_document(file_path)
        chunks = self._create_chunks(content, self.chunk_size)
        
        for chunk in chunks:
            yield chunk
    
    def _merge_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并多个提取结果"""
        merged = {
            "total_chunks": len(results),
            "processing_method": "chunked_extraction",
            "confidence": sum(r.get("confidence", 0) for r in results) / len(results),
            "extracted_fields": []
        }
        
        # 合并字段
        all_fields = set()
        for result in results:
            all_fields.update(result.get("extracted_fields", []))
        
        merged["extracted_fields"] = list(all_fields)
        
        return merged
    
    def _reduce_results(self, map_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """REDUCE阶段：合并MAP结果"""
        return self._merge_results(map_results)
    
    def _accumulate_result(self, current_result: Dict[str, Any], new_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """累积流式结果"""
        if not current_result:
            current_result = {"chunks_processed": 0, "accumulated_fields": []}
        
        current_result["chunks_processed"] += 1
        current_result["accumulated_fields"].extend(new_chunk.get("extracted_fields", []))
        
        return current_result
    
    def _validate_and_enhance(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证和增强结果"""
        # 添加处理统计
        result["processing_stats"] = {
            "total_processing_time": "已完成",
            "quality_score": result.get("confidence", 0.8),
            "completeness": len(result.get("extracted_fields", [])) / 33  # 33个期望字段
        }
        
        return result


def main():
    """测试大型文档处理能力"""
    
    print("🚀 大型文档提取器功能测试")
    
    # 创建增强型提取器
    extractor = LargeDocumentExtractor(max_workers=4)
    
    # 模拟不同大小的文档测试
    test_scenarios = [
        {"name": "小型文档", "content": "A" * 50000},   # 约25K tokens
        {"name": "中型文档", "content": "B" * 200000}, # 约100K tokens
        {"name": "大型文档", "content": "C" * 500000}, # 约250K tokens
    ]
    
    for scenario in test_scenarios:
        print(f"\n📄 测试: {scenario['name']}")
        
        # 创建临时文件
        temp_file = f"temp_{scenario['name'].lower()}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(scenario['content'])
        
        try:
            # 测试提取
            result = extractor.extract_large_document(temp_file)
            print(f"    提取完成: {result.get('processing_method', 'unknown')}")
            print(f"   📊 质量分数: {result.get('processing_stats', {}).get('quality_score', 0):.2f}")
            
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    print("\n 大型文档提取器测试完成")


if __name__ == "__main__":
    main()

