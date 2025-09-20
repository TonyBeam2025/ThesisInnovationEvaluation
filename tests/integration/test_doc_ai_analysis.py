"""
测试.doc文件的AI目录分析
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.doc_processor import process_doc_file
from thesis_inno_eval.ai_toc_extractor import AITocExtractor
import re

def analyze_doc_with_ai():
    """使用AI分析.doc文件的目录结构"""
    
    # 测试第一个文件
    doc_file = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.doc"
    
    print(f"AI分析文件: {os.path.basename(doc_file)}")
    print("="*60)
    
    try:
        # 提取内容
        content = process_doc_file(doc_file)
        
        if not content:
            print("❌ 无法提取文件内容")
            return
            
        print(f" 成功提取内容 ({len(content)} 字符)")
        
        # 预处理内容，查找可能的目录部分
        lines = content.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        # 查找包含章节信息的行
        chapter_lines = []
        chapter_patterns = [
            r'第[一二三四五六七八九十\d]+章.*',
            r'[1-9]\d*\.[1-9]\d*.*',
            r'[1-9]\d*\s+[^\d\s].*',
            r'.*目录.*',
            r'.*摘要.*',
            r'.*参考文献.*',
            r'.*致谢.*'
        ]
        
        for line in non_empty_lines:
            for pattern in chapter_patterns:
                if re.search(pattern, line):
                    chapter_lines.append(line)
                    break
        
        if chapter_lines:
            print(f"\n🔍 发现可能的目录行 ({len(chapter_lines)}个):")
            for i, line in enumerate(chapter_lines[:15], 1):
                print(f"   {i:2d}. {line[:100]}{'...' if len(line) > 100 else ''}")
            
            # 构建目录内容片段用于AI分析
            toc_content = '\n'.join(chapter_lines[:20])  # 取前20行
            
            print(f"\n🤖 准备AI分析的目录内容:")
            print("-" * 40)
            print(toc_content[:500] + "..." if len(toc_content) > 500 else toc_content)
            print("-" * 40)
            
            # 使用AI提取器分析
            extractor = AITocExtractor()
            
            # 手动调用AI分析方法
            extractor.init_ai_client()
            
            if extractor.ai_client:
                print(f"\n🔄 开始AI分析...")
                try:
                    entries = extractor._ai_extract_entries_with_llm(toc_content)
                    
                    if entries:
                        print(f" AI提取了 {len(entries)} 个目录条目:")
                        for i, entry in enumerate(entries, 1):
                            print(f"   {i}. 级别{entry.level}: {entry.number} {entry.title} (页码: {entry.page})")
                    else:
                        print("❌ AI未提取到任何目录条目")
                        
                        # 尝试传统方法
                        print("\n🔄 尝试传统模式识别...")
                        traditional_entries = extractor._ai_extract_entries_traditional(chapter_lines)
                        
                        if traditional_entries:
                            print(f" 传统方法提取了 {len(traditional_entries)} 个目录条目:")
                            for i, entry in enumerate(traditional_entries, 1):
                                print(f"   {i}. 级别{entry.level}: {entry.number} {entry.title} (类型: {entry.section_type})")
                        else:
                            print("❌ 传统方法也未提取到目录条目")
                            
                except Exception as e:
                    print(f"❌ AI分析失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ AI客户端初始化失败")
        else:
            print("❌ 未发现可能的目录内容")
            
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_doc_with_ai()
