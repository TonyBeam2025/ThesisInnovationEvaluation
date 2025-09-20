#!/usr/bin/env python3
"""
测试 _extract_front_metadata 和 _ai_extract_cover_metadata 函数的容错处理
确保它们不会返回 None
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro

def test_front_metadata_no_none():
    """测试 _extract_front_metadata 不返回None"""
    print("🧪 测试 _extract_front_metadata 函数的容错处理")
    print("=" * 60)
    
    extractor = ThesisExtractorPro()
    
    # 测试用例1: 正常文本（有AI客户端）
    print("\n📋 测试用例1: 正常文本（有AI客户端）")
    print("-" * 40)
    
    normal_text = """
    北京航空航天大学
    硕士学位论文
    
    高温合金成分优化与性能预测研究
    
    作者姓名：张三
    指导教师：李四教授
    学科专业：材料科学与工程
    
    学位论文使用授权书
    本人完全了解...
    """
    
    # 确保有AI客户端
    assert hasattr(extractor, 'ai_client') and extractor.ai_client is not None
    
    result1 = extractor._extract_front_metadata(normal_text)
    print(f" 返回类型: {type(result1)}")
    print(f" 是否为None: {result1 is None}")
    print(f" 是否为字典: {isinstance(result1, dict)}")
    print(f" 字段数量: {len(result1)}")
    
    assert result1 is not None, "❌ _extract_front_metadata 返回了 None!"
    assert isinstance(result1, dict), "❌ _extract_front_metadata 未返回字典!"
    
    # 测试用例2: 无AI客户端
    print("\n📋 测试用例2: 无AI客户端")
    print("-" * 40)
    
    # 临时移除AI客户端
    original_client = extractor.ai_client
    extractor.ai_client = None
    
    result2 = extractor._extract_front_metadata(normal_text)
    print(f" 返回类型: {type(result2)}")
    print(f" 是否为None: {result2 is None}")
    print(f" 是否为字典: {isinstance(result2, dict)}")
    print(f" 字段数量: {len(result2)}")
    
    assert result2 is not None, "❌ _extract_front_metadata 在无AI时返回了 None!"
    assert isinstance(result2, dict), "❌ _extract_front_metadata 在无AI时未返回字典!"
    
    # 恢复AI客户端
    extractor.ai_client = original_client
    
    # 测试用例3: 空文本
    print("\n📋 测试用例3: 空文本")
    print("-" * 40)
    
    result3 = extractor._extract_front_metadata("")
    print(f" 返回类型: {type(result3)}")
    print(f" 是否为None: {result3 is None}")
    print(f" 是否为字典: {isinstance(result3, dict)}")
    print(f" 字段数量: {len(result3)}")
    
    assert result3 is not None, "❌ _extract_front_metadata 对空文本返回了 None!"
    assert isinstance(result3, dict), "❌ _extract_front_metadata 对空文本未返回字典!"

def test_ai_extract_cover_metadata_no_none():
    """测试 _ai_extract_cover_metadata 不返回None"""
    print("\n\n🧪 测试 _ai_extract_cover_metadata 函数的容错处理")
    print("=" * 60)
    
    extractor = ThesisExtractorPro()
    
    # 测试用例1: 正常文本
    print("\n📋 测试用例1: 正常文本（AI可用）")
    print("-" * 40)
    
    normal_cover = """
    北京航空航天大学
    硕士学位论文
    
    高温合金成分优化与性能预测研究
    
    作者姓名：张三
    指导教师：李四教授
    """
    
    result1 = extractor._ai_extract_cover_metadata(normal_cover)
    print(f" 返回类型: {type(result1)}")
    print(f" 是否为None: {result1 is None}")
    print(f" 是否为字典: {isinstance(result1, dict)}")
    print(f" 字段数量: {len(result1)}")
    
    assert result1 is not None, "❌ _ai_extract_cover_metadata 返回了 None!"
    assert isinstance(result1, dict), "❌ _ai_extract_cover_metadata 未返回字典!"
    
    # 测试用例2: AI客户端故意设为None
    print("\n📋 测试用例2: AI客户端为None")
    print("-" * 40)
    
    # 临时创建一个没有AI客户端的提取器
    extractor_no_ai = ThesisExtractorPro()
    extractor_no_ai.ai_client = None
    
    result2 = extractor_no_ai._ai_extract_cover_metadata(normal_cover)
    print(f" 返回类型: {type(result2)}")
    print(f" 是否为None: {result2 is None}")
    print(f" 是否为字典: {isinstance(result2, dict)}")
    print(f" 字段数量: {len(result2)}")
    
    assert result2 is not None, "❌ _ai_extract_cover_metadata 在无AI时返回了 None!"
    assert isinstance(result2, dict), "❌ _ai_extract_cover_metadata 在无AI时未返回字典!"
    
    # 测试用例3: 空文本
    print("\n📋 测试用例3: 空文本")
    print("-" * 40)
    
    result3 = extractor._ai_extract_cover_metadata("")
    print(f" 返回类型: {type(result3)}")
    print(f" 是否为None: {result3 is None}")
    print(f" 是否为字典: {isinstance(result3, dict)}")
    print(f" 字段数量: {len(result3)}")
    
    assert result3 is not None, "❌ _ai_extract_cover_metadata 对空文本返回了 None!"
    assert isinstance(result3, dict), "❌ _ai_extract_cover_metadata 对空文本未返回字典!"
    
    # 测试用例4: 无效JSON响应（模拟AI返回错误格式）
    print("\n📋 测试用例4: 模拟AI响应异常")
    print("-" * 40)
    
    # 这里我们通过传入一些可能导致JSON解析失败的情况来测试
    # 实际上由于AI的容错处理，这应该也返回空字典
    
    malformed_text = "这是一些可能导致AI解析失败的文本 <<<>>> %%% &&&"
    
    result4 = extractor._ai_extract_cover_metadata(malformed_text)
    print(f" 返回类型: {type(result4)}")
    print(f" 是否为None: {result4 is None}")
    print(f" 是否为字典: {isinstance(result4, dict)}")
    print(f" 字段数量: {len(result4)}")
    
    assert result4 is not None, "❌ _ai_extract_cover_metadata 在异常情况下返回了 None!"
    assert isinstance(result4, dict), "❌ _ai_extract_cover_metadata 在异常情况下未返回字典!"

def test_front_metadata_with_discipline():
    """测试 _extract_front_metadata_with_discipline 不返回None"""
    print("\n\n🧪 测试 _extract_front_metadata_with_discipline 函数的容错处理")
    print("=" * 60)
    
    extractor = ThesisExtractorPro()
    
    test_text = """
    北京航空航天大学
    硕士学位论文
    
    材料科学研究
    """
    
    result = extractor._extract_front_metadata_with_discipline(test_text, "材料科学")
    print(f" 返回类型: {type(result)}")
    print(f" 是否为None: {result is None}")
    print(f" 是否为字典: {isinstance(result, dict)}")
    print(f" 字段数量: {len(result)}")
    print(f" 包含学科字段: {'discipline' in result}")
    
    assert result is not None, "❌ _extract_front_metadata_with_discipline 返回了 None!"
    assert isinstance(result, dict), "❌ _extract_front_metadata_with_discipline 未返回字典!"
    assert 'discipline' in result, "❌ _extract_front_metadata_with_discipline 未添加学科字段!"

if __name__ == "__main__":
    try:
        test_front_metadata_no_none()
        test_ai_extract_cover_metadata_no_none()
        test_front_metadata_with_discipline()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！函数已确保不会返回None")
        print("\n📋 容错处理总结:")
        print("    _extract_front_metadata: 在AI不可用时返回空字典")
        print("    _ai_extract_cover_metadata: 在任何异常情况下都返回空字典")
        print("    _extract_front_metadata_with_discipline: 继承了容错处理")
        print("    所有函数都确保返回 Dict[str, Any] 类型")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试出现异常: {e}")
        sys.exit(1)
