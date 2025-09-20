"""
测试AI目录提取器 - 仅支持.docx格式
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor
import json

def test_docx_support():
    """测试.docx格式支持"""
    print("🚀 测试AI目录提取器 - 仅支持.docx格式")
    
    # 使用已知的.docx文件进行测试
    test_file = r"c:\MyProjects\thesis_Inno_Eval\data\input\51177.docx"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    try:
        # 初始化提取器
        extractor = AITocExtractor()
        
        # 提取目录
        print(f"🔄 开始提取目录: {os.path.basename(test_file)}")
        result = extractor.extract_toc(test_file)
        
        if result and result.entries:
            # 统计各类章节
            chapters = []
            special_sections = []
            post_references = []
            
            # 分类统计
            for entry in result.entries:
                if hasattr(entry, 'section_type'):
                    if entry.section_type in ['traditional_chapter', 'numeric_chapter', 'english_chapter']:
                        chapters.append(entry)
                    elif entry.section_type in ['abstract', 'references', 'conclusion']:
                        special_sections.append(entry)
                    elif entry.section_type in ['achievements', 'acknowledgment', 'author_profile']:
                        post_references.append(entry)
            
            print(f"\n📊 提取结果统计:")
            print(f"   正文章节: {len(chapters)}个")
            print(f"   特殊章节: {len(special_sections)}个") 
            print(f"   参考文献后章节: {len(post_references)}个")
            print(f"   总条目: {result.total_entries}个")
            print(f"   置信度: {result.confidence_score:.2f}")
            print(f"   提取方法: {result.extraction_method}")
            
            # 显示前5个条目作为示例
            print(f"\n📚 前5个条目示例:")
            for i, entry in enumerate(result.entries[:5], 1):
                print(f"   {i}. {entry.number} {entry.title} (页码: {entry.page}, 类型: {entry.section_type})")
                
            print("\n .docx格式测试成功!")
                
        else:
            print("❌ 提取失败或结果为空")
            
    except Exception as e:
        print(f"❌ 提取过程中出错: {str(e)}")

def test_unsupported_formats():
    """测试不支持的格式"""
    print(f"\n{'='*60}")
    print("🚫 测试不支持的格式")
    
    # 测试.doc格式 
    doc_file = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.doc"
    
    if os.path.exists(doc_file):
        try:
            extractor = AITocExtractor()
            result = extractor.extract_toc(doc_file)
            print("❌ 意外成功: .doc文件应该被拒绝")
        except ValueError as e:
            print(f" 正确拒绝.doc格式: {str(e)}")
        except Exception as e:
            print(f"❌ 意外错误: {str(e)}")
    else:
        print("ℹ️  .doc测试文件不存在，跳过测试")

def main():
    """主测试函数"""
    print("🔧 AI目录提取器格式支持测试")
    print("📋 当前仅支持: .docx格式")
    
    test_docx_support()
    test_unsupported_formats()
    
    print(f"\n{'='*60}")
    print(" 测试完成")
    print("💡 提示: 如需处理.doc文件，请先转换为.docx格式")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
