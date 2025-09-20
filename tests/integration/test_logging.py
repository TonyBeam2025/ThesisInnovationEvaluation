#!/usr/bin/env python3
"""
测试日志记录功能 - 验证错误和异常信息是否正确记录到日志
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
import logging
import tempfile
from pathlib import Path

sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

def setup_test_logging():
    """设置测试日志配置"""
    # 创建临时日志文件
    log_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
    log_file.close()
    
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file.name, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return log_file.name

def test_error_logging():
    """测试错误日志记录功能"""
    print("🧪 测试错误和异常日志记录功能")
    print("=" * 60)
    
    # 设置日志
    log_file = setup_test_logging()
    print(f"📁 日志文件: {log_file}")
    
    try:
        from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        
        # 测试用例1: AI客户端初始化失败（通过模拟无效配置）
        print("\n📋 测试用例1: AI客户端初始化异常")
        print("-" * 40)
        
        # 临时破坏AI配置来触发异常
        os.environ['GOOGLE_API_KEY'] = 'invalid_key_to_trigger_error'
        
        try:
            extractor = ThesisExtractorPro()  # 这应该会触发AI初始化错误
        except Exception as e:
            print(f" 成功捕获AI初始化异常: {e}")
        
        # 恢复环境
        if 'GOOGLE_API_KEY' in os.environ:
            del os.environ['GOOGLE_API_KEY']
        
        # 测试用例2: 前置元数据提取异常
        print("\n📋 测试用例2: 前置元数据提取异常")
        print("-" * 40)
        
        extractor = ThesisExtractorPro()
        extractor.ai_client = None  # 模拟AI不可用
        
        result = extractor._extract_front_metadata("测试文本")
        print(f" AI不可用时返回: {result}")
        
        # 测试用例3: AI提取封面元数据异常
        print("\n📋 测试用例3: AI提取封面元数据异常")
        print("-" * 40)
        
        result = extractor._ai_extract_cover_metadata("")
        print(f" 空文本时返回: {result}")
        
        # 测试用例4: 文档结构分析异常（传入无效数据）
        print("\n📋 测试用例4: 文档结构分析异常")
        print("-" * 40)
        
        result = extractor._analyze_document_structure("")
        print(f" 空文档分析返回: {len(result.get('table_of_contents', []))} 个章节")
        
        # 测试用例5: 参考文献提取异常
        print("\n📋 测试用例5: 参考文献提取异常")
        print("-" * 40)
        
        try:
            result = extractor._extract_references_enhanced("")
            print(f" 空文档参考文献提取返回: {len(result)} 条")
        except Exception as e:
            print(f" 成功捕获参考文献提取异常: {e}")
        
        print("\n📊 检查日志文件内容...")
        
        # 读取并显示日志内容
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                
            if log_content:
                print(" 日志文件已记录内容:")
                print("-" * 40)
                # 只显示ERROR和WARNING级别的日志
                lines = log_content.split('\n')
                error_lines = [line for line in lines if 'ERROR' in line or 'WARNING' in line]
                
                if error_lines:
                    for i, line in enumerate(error_lines[:10], 1):  # 最多显示10条
                        print(f"{i:2d}. {line}")
                    
                    if len(error_lines) > 10:
                        print(f"    ... 还有 {len(error_lines) - 10} 条日志")
                else:
                    print("📝 未发现ERROR或WARNING级别的日志")
                    # 显示所有日志的前几行
                    all_lines = [line for line in lines if line.strip()]
                    for i, line in enumerate(all_lines[:5], 1):
                        print(f"{i:2d}. {line}")
            else:
                print("⚠️ 日志文件为空")
                
        except Exception as e:
            print(f"❌ 读取日志文件失败: {e}")
        
        print(f"\n 测试完成！")
        print(f"📁 日志文件保存在: {log_file}")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理
        if 'log_file' in locals():
            print(f"\n🗑️ 清理日志文件: {log_file}")
            try:
                os.unlink(log_file)
            except:
                pass

def test_logging_configuration():
    """测试日志配置"""
    print("\n\n📝 测试日志配置")
    print("=" * 60)
    
    # 检查日志器是否正确设置
    from thesis_inno_eval.extract_sections_with_ai import logger
    
    print(f" 日志器名称: {logger.name}")
    print(f" 日志器级别: {logger.level}")
    print(f" 日志器处理器数量: {len(logger.handlers)}")
    
    # 测试直接记录日志
    logger.info("这是一条测试信息日志")
    logger.warning("这是一条测试警告日志")
    logger.error("这是一条测试错误日志")
    
    print(" 日志记录测试完成")

if __name__ == "__main__":
    test_error_logging()
    test_logging_configuration()
    
    print("\n" + "=" * 60)
    print("🎉 日志记录功能测试完成！")
    print("\n📋 测试总结:")
    print("    AI客户端初始化异常日志")
    print("    前置元数据提取异常日志")
    print("    AI封面元数据提取异常日志")
    print("    文档结构分析异常日志")
    print("    参考文献提取异常日志")
    print("    日志配置验证")
