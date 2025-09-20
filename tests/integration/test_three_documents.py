"""
测试三个新文档的目录提取
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor
import json

def test_document(doc_path):
    """测试单个文档的目录提取"""
    print(f"\n{'='*60}")
    print(f"测试文档: {os.path.basename(doc_path)}")
    print(f"{'='*60}")
    
    if not os.path.exists(doc_path):
        print(f"❌ 文件不存在: {doc_path}")
        return
    
    try:
        # 初始化提取器
        extractor = AITocExtractor()
        
        # 提取目录
        print("🔄 开始提取目录...")
        result = extractor.extract_toc(doc_path)
        
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
            
            # 显示正文章节
            if chapters:
                print(f"\n📚 正文章节:")
                for i, chapter in enumerate(chapters, 1):
                    print(f"   {i}. {chapter.number} {chapter.title} (页码: {chapter.page})")
            
            # 显示特殊章节
            if special_sections:
                print(f"\n🔍 特殊章节:")
                for i, section in enumerate(special_sections, 1):
                    print(f"   {i}. {section.title} (类型: {section.section_type}, 页码: {section.page})")
            
            # 显示参考文献后章节
            if post_references:
                print(f"\n📖 参考文献后章节:")
                for i, section in enumerate(post_references, 1):
                    print(f"   {i}. {section.title} (类型: {section.section_type}, 页码: {section.page})")
            else:
                print(f"\n⚠️  未检测到参考文献后章节")
                
        else:
            print("❌ 提取失败或结果为空")
            
    except Exception as e:
        print(f"❌ 提取过程中出错: {str(e)}")

def main():
    """主测试函数"""
    documents = [
        r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.doc",
        r"c:\MyProjects\thesis_Inno_Eval\data\input\法律硕士_2018213020_王纪锋_学位论文.doc", 
        r"c:\MyProjects\thesis_Inno_Eval\data\input\1_音乐_20172001013韩柠灿（硕士毕业论文）.doc"
    ]
    
    print("🚀 开始测试三个新文档的目录提取")
    
    for doc_path in documents:
        test_document(doc_path)
    
    print(f"\n{'='*60}")
    print(" 测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
