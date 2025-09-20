"""
测试三个学位论文的目录提取
音乐、马克思主义哲学、法律硕士
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor
import json

def test_document(doc_path, doc_name):
    """测试单个文档的目录提取"""
    print(f"\n{'='*80}")
    print(f"📖 测试文档: {doc_name}")
    print(f"📁 文件路径: {os.path.basename(doc_path)}")
    print(f"{'='*80}")
    
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
            level2_sections = []
            level3_sections = []
            
            # 分类统计
            for entry in result.entries:
                if hasattr(entry, 'section_type'):
                    if entry.section_type in ['traditional_chapter', 'numeric_chapter', 'english_chapter', 'chapter']:
                        chapters.append(entry)
                    elif entry.section_type in ['abstract', 'references', 'conclusion']:
                        special_sections.append(entry)
                    elif entry.section_type in ['achievements', 'acknowledgment', 'author_profile']:
                        post_references.append(entry)
                    elif entry.section_type == 'level2_section':
                        level2_sections.append(entry)
                    elif entry.section_type == 'level3_section':
                        level3_sections.append(entry)
            
            print(f"\n📊 提取结果统计:")
            print(f"   📚 正文章节: {len(chapters)}个")
            print(f"   📄 二级章节: {len(level2_sections)}个")
            print(f"   📝 三级章节: {len(level3_sections)}个")
            print(f"   🔍 特殊章节: {len(special_sections)}个") 
            print(f"   📖 参考文献后章节: {len(post_references)}个")
            print(f"   📈 总条目: {result.total_entries}个")
            print(f"   🎯 置信度: {result.confidence_score:.2f}")
            print(f"   🤖 提取方法: {result.extraction_method}")
            
            # 显示正文章节
            if chapters:
                print(f"\n📚 正文章节详情:")
                for i, chapter in enumerate(chapters, 1):
                    print(f"   {i}. 【{chapter.number}】 {chapter.title}")
                    print(f"      页码: {chapter.page} | 置信度: {chapter.confidence:.2f}")
            
            # 显示特殊章节
            if special_sections:
                print(f"\n🔍 特殊章节详情:")
                for i, section in enumerate(special_sections, 1):
                    print(f"   {i}. 【{section.section_type}】 {section.title}")
                    print(f"      页码: {section.page} | 置信度: {section.confidence:.2f}")
            
            # 显示参考文献后章节
            if post_references:
                print(f"\n📖 参考文献后章节详情:")
                for i, section in enumerate(post_references, 1):
                    print(f"   {i}. 【{section.section_type}】 {section.title}")
                    print(f"      页码: {section.page} | 置信度: {section.confidence:.2f}")
            else:
                print(f"\n⚠️  未检测到参考文献后章节")
            
            # 显示结构概览
            print(f"\n🏗️  文档结构概览:")
            level_counts = {}
            for entry in result.entries:
                level = entry.level
                if level not in level_counts:
                    level_counts[level] = 0
                level_counts[level] += 1
            
            for level in sorted(level_counts.keys()):
                print(f"   第{level}级: {level_counts[level]}个条目")
                
            print(f"\n 目录提取成功!")
                
        else:
            print("❌ 提取失败或结果为空")
            
    except Exception as e:
        print(f"❌ 提取过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    documents = [
        {
            'path': r"c:\MyProjects\thesis_Inno_Eval\data\input\1_音乐_20172001013韩柠灿（硕士毕业论文）.docx",
            'name': "音乐学硕士论文"
        },
        {
            'path': r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.docx", 
            'name': "马克思主义哲学学位论文"
        },
        {
            'path': r"c:\MyProjects\thesis_Inno_Eval\data\input\法律硕士_2018213020_王纪锋_学位论文.docx",
            'name': "法律硕士学位论文"
        }
    ]
    
    print("🚀 开始测试三个学位论文的目录提取")
    print("📋 包括: 音乐学、马克思主义哲学、法律硕士")
    
    for doc_info in documents:
        if doc_info['path'].endswith('.doc'):
            print(f"\n{'='*80}")
            print(f"📖 测试文档: {doc_info['name']}")
            print(f"📁 文件路径: {os.path.basename(doc_info['path'])}")
            print(f"{'='*80}")
            print("❌ .doc格式不支持，请先转换为.docx格式")
            continue
            
        test_document(doc_info['path'], doc_info['name'])
    
    print(f"\n{'='*80}")
    print(" 测试完成")
    print("💡 提示: 如发现.doc文件，请手动转换为.docx格式后重新测试")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
