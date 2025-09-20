"""
简单测试.doc文件内容提取
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.doc_processor import process_doc_file

def test_single_doc():
    """测试单个.doc文件的内容提取"""
    
    # 测试第一个文件（之前成功的）
    doc_file = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.doc"
    
    print(f"测试文件: {os.path.basename(doc_file)}")
    print("="*60)
    
    try:
        content = process_doc_file(doc_file)
        
        if content:
            lines = content.split('\n')
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            
            print(f" 成功提取内容")
            print(f"📝 总行数: {len(lines)}")
            print(f"📝 非空行数: {len(non_empty_lines)}")
            print(f"📄 内容长度: {len(content)} 字符")
            
            # 显示前20行内容
            print(f"\n📖 内容示例 (前20行):")
            for i, line in enumerate(non_empty_lines[:20], 1):
                if line:
                    print(f"   {i:2d}. {line[:80]}{'...' if len(line) > 80 else ''}")
            
            # 查找目录相关内容
            toc_keywords = ['目录', '目  录', '第一章', '第二章', '第三章', '绪论', '引言', '摘要', '参考文献']
            toc_lines = []
            
            for i, line in enumerate(non_empty_lines):
                for keyword in toc_keywords:
                    if keyword in line:
                        toc_lines.append((i+1, line))
                        break
            
            if toc_lines:
                print(f"\n🔍 发现可能的目录相关内容 ({len(toc_lines)}个):")
                for line_num, line in toc_lines[:10]:
                    print(f"   第{line_num}行: {line[:100]}{'...' if len(line) > 100 else ''}")
            else:
                print(f"\n⚠️  未发现明显的目录标识")
                
            # 检查是否有章节编号模式
            import re
            chapter_patterns = [
                r'第[一二三四五六七八九十\d]+章',
                r'[1-9]\d*\.[1-9]\d*',
                r'[1-9]\d*\s+[^\d\s]',
            ]
            
            for pattern in chapter_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"\n📋 发现章节模式 '{pattern}': {len(matches)}个匹配")
                    for match in matches[:5]:
                        print(f"   {match}")
                        
        else:
            print("❌ 提取内容为空")
            
    except Exception as e:
        print(f"❌ 提取失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_doc()
