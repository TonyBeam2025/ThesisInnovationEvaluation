"""
专门测试马克思主义哲学论文的目录提取
检查是否正确提取了所有参考文献后章节
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor
import json

def test_marxism_thesis():
    """测试马克思主义哲学论文的详细目录提取"""
    doc_path = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.docx"
    
    print("🧠 测试马克思主义哲学学位论文详细目录提取")
    print(f"📁 文件: {os.path.basename(doc_path)}")
    print("="*80)
    
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
            print(f"\n📊 总提取条目: {len(result.entries)}个")
            print(f"🎯 整体置信度: {result.confidence_score:.2f}")
            
            # 显示所有条目的详细信息
            print(f"\n📋 完整目录条目列表:")
            print("-" * 80)
            
            for i, entry in enumerate(result.entries, 1):
                print(f"{i:2d}. 【{entry.section_type}】 {entry.number} {entry.title}")
                print(f"     页码: {entry.page} | 级别: {entry.level} | 置信度: {entry.confidence:.2f}")
            
            # 专门检查参考文献后章节
            print(f"\n🔍 参考文献后章节检查:")
            print("-" * 50)
            
            post_ref_sections = []
            references_found = False
            
            for entry in result.entries:
                if entry.section_type == 'references':
                    references_found = True
                    print(f" 找到参考文献: {entry.title} (页码: {entry.page})")
                elif entry.section_type in ['achievements', 'acknowledgment', 'author_profile', 'epilogue']:
                    post_ref_sections.append(entry)
            
            if references_found:
                print(f"\n📖 参考文献后章节 ({len(post_ref_sections)}个):")
                for i, section in enumerate(post_ref_sections, 1):
                    print(f"   {i}. {section.title} (页码: {section.page}, 类型: {section.section_type})")
            
            # 检查是否包含目标章节
            target_sections = [
                "个人简历和攻读硕士学位期间的主要学术成果",
                "后记", "后　记"
            ]
            
            print(f"\n🎯 目标章节检查:")
            print("-" * 50)
            
            found_targets = []
            for target in target_sections:
                for entry in result.entries:
                    # 更灵活的匹配逻辑 - 移除空格并比较
                    clean_title = entry.title.replace(" ", "").replace("　", "")
                    clean_target = target.replace(" ", "").replace("　", "")
                    
                    if (target in entry.title or entry.title in target or 
                        clean_target in clean_title or 
                        (target == "后记" and "后记" in clean_title) or
                        (target == "后　记" and "后记" in clean_title)):
                        found_targets.append((target, entry))
                        print(f" 找到: {entry.title} (页码: {entry.page})")
                        break
                else:
                    print(f"❌ 缺失: {target}")
            
            if len(found_targets) < 2:
                print(f"\n⚠️  可能需要调整识别模式以捕获更多参考文献后章节")
                
        else:
            print("❌ 提取失败或结果为空")
            
    except Exception as e:
        print(f"❌ 提取过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

def check_raw_content():
    """检查原始文档内容以确认目标章节存在"""
    print(f"\n🔍 检查原始文档内容...")
    doc_path = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.docx"
    
    try:
        import docx
        doc = docx.Document(doc_path)
        
        print("📄 搜索目标章节...")
        targets = ["个人简历", "攻读硕士学位", "后记", "后　记"]
        
        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if text and any(target in text for target in targets):
                print(f"第{i+1}行: {text}")
                
    except Exception as e:
        print(f"❌ 检查原始内容失败: {str(e)}")

if __name__ == "__main__":
    test_marxism_thesis()
    check_raw_content()
