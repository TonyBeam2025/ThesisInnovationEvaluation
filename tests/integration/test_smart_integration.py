"""
测试智能参考文献提取集成
验证PDF和Word文档的不同处理策略
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

def test_smart_integration():
    """测试智能参考文献提取集成"""
    print("🧪 测试智能参考文献提取集成\n")
    
    try:
        # 导入模块
        from src.thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        print(" 模块导入成功")
        
        # 初始化提取器
        print("\n🔧 初始化智能提取器...")
        extractor = ThesisExtractorPro()
        
        # 检查智能提取器状态
        if extractor.smart_ref_extractor:
            print(" 智能参考文献提取器: 可用")
        else:
            print("⚠️ 智能参考文献提取器: 不可用")
        
        if extractor.ai_client:
            print(" AI客户端: 可用")
        else:
            print("⚠️ AI客户端: 不可用")
        
        # 读取测试文档
        test_file = "data/input/51177.docx"
        if not os.path.exists(test_file):
            print(f"❌ 测试文件不存在: {test_file}")
            return
        
        print(f"\n📄 使用Word文档进行测试: {test_file}")
        
        # 由于这是Word文档，我们需要先提取文本
        # 但为了简化测试，我们使用已有的markdown版本（如果存在）
        markdown_file = "data/output/51177_extracted.md"
        if os.path.exists(markdown_file):
            print(f"📄 使用已提取的markdown版本: {markdown_file}")
            with open(markdown_file, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            print("⚠️ 未找到已提取的markdown版本，使用模拟文本进行测试")
            # 使用包含参考文献的模拟文本
            text = """
# 测试论文

## 摘要
这是一个测试文档用于验证智能参考文献提取功能。

## 参考文献

［１］ Zhang, J., Smith, A. B., & Johnson, C. D. Machine Learning Approaches in Data Science[J]. Journal of Computer Science, 2023, 45(3): 123-145.

［２］ Li, M., Wang, H., & Chen, Y. Deep Learning for Natural Language Processing[C]//Proceedings of the International Conference on Artificial Intelligence. IEEE, 2023: 456-467.

［３］ 王明, 李华, 张三. 人工智能在医疗诊断中的应用研究[J]. 计算机学报, 2023, 44(2): 234-248.

［４］ Brown, R., Davis, K., & Wilson, L. Advanced Algorithms for Big Data Processing[M]. MIT Press, 2023: 89-112.

［５］ 刘强, 陈亮. 基于深度学习的图像识别技术[J]. 软件学报, 2023, 34(1): 45-58.
"""
        
        print(f"📏 文档长度: {len(text):,} 字符")
        
        # 测试智能参考文献提取
        print("\n🔍 测试智能参考文献提取...")
        start_time = time.time()
        
        # 模拟PDF文档路径
        pdf_test_path = "test_document.pdf"
        references_result = extractor._extract_references_enhanced_disciplinary(
            text, 'engineering', pdf_test_path
        )
        
        processing_time = time.time() - start_time
        
        # 显示结果
        print(f"\n📊 提取结果:")
        print(f"   参考文献数量: {references_result['total_count']} 条")
        print(f"   学科领域: {references_result['discipline']}")
        print(f"   处理时间: {processing_time:.2f} 秒")
        
        if 'extraction_stats' in references_result:
            stats = references_result['extraction_stats']
            print(f"   提取方法: {stats.get('method_used', 'unknown')}")
            print(f"   成功状态: {stats.get('success', False)}")
            print(f"   内部处理时间: {stats.get('processing_time', 0):.2f} 秒")
        
        # 显示前几条参考文献
        references = references_result['references']
        if references:
            print(f"\n📋 前5条参考文献:")
            for i, ref in enumerate(references[:5], 1):
                print(f"   {i}. {ref[:100]}...")
        
        # 测试Word文档路径
        print(f"\n🔍 测试Word文档处理...")
        word_test_path = "test_document.docx"
        references_result_word = extractor._extract_references_enhanced_disciplinary(
            text, 'engineering', word_test_path
        )
        
        print(f"   Word处理结果: {references_result_word['total_count']} 条参考文献")
        if 'extraction_stats' in references_result_word:
            stats = references_result_word['extraction_stats']
            print(f"   Word提取方法: {stats.get('method_used', 'unknown')}")
        
        # 对比分析
        print(f"\n📈 对比分析:")
        print(f"   PDF策略提取: {references_result['total_count']} 条")
        print(f"   Word策略提取: {references_result_word['total_count']} 条")
        
        if references_result['total_count'] == references_result_word['total_count']:
            print("    两种策略结果一致")
        else:
            print("   ⚠️ 两种策略结果不同，符合预期（不同优化策略）")
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("   请确保所有依赖模块都已正确安装")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_format_detection():
    """测试格式检测功能"""
    print("\n🔍 测试格式检测功能")
    
    try:
        from src.thesis_inno_eval.smart_reference_extractor import SmartReferenceExtractor
        
        # 创建提取器实例
        extractor = SmartReferenceExtractor()
        
        # 测试不同文件路径
        test_paths = [
            "document.pdf",
            "document.docx", 
            "document.doc",
            "unknown.txt",
            ""
        ]
        
        for path in test_paths:
            format_detected = extractor._detect_source_format("", path)
            print(f"   {path:15} -> {format_detected}")
            
    except Exception as e:
        print(f"❌ 格式检测测试失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("智能参考文献提取集成测试")
    print("=" * 60)
    
    test_smart_integration()
    test_format_detection()
    
    print("\n 测试完成!")
