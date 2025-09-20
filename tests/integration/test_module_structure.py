"""
测试src目录结构中的智能参考文献提取器模块规范性
验证模块导入和功能的正确性
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
from pathlib import Path

def test_module_structure():
    """测试模块结构规范性"""
    print("🔍 测试src目录结构中的模块规范性\n")
    
    # 测试直接从包导入
    try:
        from src.thesis_inno_eval import SmartReferenceExtractor
        print(" 从包根目录导入成功: from src.thesis_inno_eval import SmartReferenceExtractor")
    except ImportError as e:
        print(f"❌ 包根目录导入失败: {e}")
    
    # 测试从模块导入
    try:
        from src.thesis_inno_eval.smart_reference_extractor import SmartReferenceExtractor
        print(" 从具体模块导入成功: from src.thesis_inno_eval.smart_reference_extractor import SmartReferenceExtractor")
    except ImportError as e:
        print(f"❌ 具体模块导入失败: {e}")
    
    # 测试模块位置
    try:
        from src.thesis_inno_eval.smart_reference_extractor import SmartReferenceExtractor
        module_file = SmartReferenceExtractor.__module__
        print(f" 模块位置: {module_file}")
        
        # 检查文件路径
        import src.thesis_inno_eval.smart_reference_extractor as sre_module
        module_path = Path(sre_module.__file__)
        print(f" 文件路径: {module_path}")
        print(f" 文件存在: {module_path.exists()}")
        
        # 验证在正确的src结构中
        expected_path = Path("src/thesis_inno_eval/smart_reference_extractor.py")
        if str(module_path).endswith(str(expected_path)):
            print(" 文件位于正确的src目录结构中")
        else:
            print(f"⚠️ 文件路径可能不符合预期: {module_path}")
            
    except Exception as e:
        print(f"❌ 模块位置检查失败: {e}")
    
    # 测试模块功能
    try:
        from src.thesis_inno_eval.smart_reference_extractor import SmartReferenceExtractor
        
        # 创建实例
        extractor = SmartReferenceExtractor()
        print(" 模块实例化成功")
        
        # 测试基本方法
        if hasattr(extractor, 'extract_references'):
            print(" 核心方法 extract_references 存在")
        else:
            print("❌ 核心方法 extract_references 不存在")
            
        if hasattr(extractor, '_detect_source_format'):
            print(" 格式检测方法 _detect_source_format 存在")
        else:
            print("❌ 格式检测方法 _detect_source_format 不存在")
            
    except Exception as e:
        print(f"❌ 模块功能测试失败: {e}")

def test_package_structure():
    """测试包结构"""
    print("\n📦 测试包结构:")
    
    try:
        import src.thesis_inno_eval
        package_path = Path(src.thesis_inno_eval.__file__).parent
        print(f" 包路径: {package_path}")
        
        # 检查关键文件
        key_files = [
            "__init__.py",
            "smart_reference_extractor.py",
            "ai_client.py",
            "extract_sections_with_ai.py",
            "cli.py"
        ]
        
        for file_name in key_files:
            file_path = package_path / file_name
            if file_path.exists():
                print(f" {file_name}: 存在")
            else:
                print(f"❌ {file_name}: 不存在")
                
    except Exception as e:
        print(f"❌ 包结构检查失败: {e}")

def test_integration_with_main_extractor():
    """测试与主提取器的集成"""
    print("\n🔗 测试与主提取器的集成:")
    
    try:
        from src.thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        
        # 创建主提取器实例
        main_extractor = ThesisExtractorPro()
        
        # 检查是否包含智能参考文献提取器
        if hasattr(main_extractor, 'smart_ref_extractor'):
            print(" 主提取器包含智能参考文献提取器属性")
            
            if main_extractor.smart_ref_extractor is not None:
                print(" 智能参考文献提取器已初始化")
                
                # 检查类型
                from src.thesis_inno_eval.smart_reference_extractor import SmartReferenceExtractor
                if isinstance(main_extractor.smart_ref_extractor, SmartReferenceExtractor):
                    print(" 智能参考文献提取器类型正确")
                else:
                    print(f"⚠️ 智能参考文献提取器类型: {type(main_extractor.smart_ref_extractor)}")
            else:
                print("⚠️ 智能参考文献提取器为None (可能是AI客户端不可用)")
        else:
            print("❌ 主提取器不包含智能参考文献提取器属性")
            
    except Exception as e:
        print(f"❌ 主提取器集成测试失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("智能参考文献提取器模块规范性测试")
    print("=" * 60)
    
    test_module_structure()
    test_package_structure()
    test_integration_with_main_extractor()
    
    print("\n 模块规范性测试完成!")
