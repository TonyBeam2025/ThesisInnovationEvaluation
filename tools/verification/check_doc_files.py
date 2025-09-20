"""
检测和转换.doc文件格式
"""
import os
from pathlib import Path
import docx2txt

def check_and_convert_doc_files():
    """检查.doc文件并尝试转换"""
    
    doc_files = [
        r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.doc",
        r"c:\MyProjects\thesis_Inno_Eval\data\input\法律硕士_2018213020_王纪锋_学位论文.doc", 
        r"c:\MyProjects\thesis_Inno_Eval\data\input\1_音乐_20172001013韩柠灿（硕士毕业论文）.doc"
    ]
    
    for doc_file in doc_files:
        print(f"\n{'='*60}")
        print(f"检测文件: {os.path.basename(doc_file)}")
        print(f"{'='*60}")
        
        if not os.path.exists(doc_file):
            print(f"❌ 文件不存在: {doc_file}")
            continue
            
        # 检查文件大小
        file_size = os.path.getsize(doc_file)
        print(f"📊 文件大小: {file_size:,} 字节")
        
        try:
            # 尝试用docx2txt读取
            print("🔄 尝试使用docx2txt读取...")
            content = docx2txt.process(doc_file)
            
            if content:
                lines = content.split('\n')
                non_empty_lines = [line.strip() for line in lines if line.strip()]
                
                print(f" 成功读取内容")
                print(f"📝 总行数: {len(lines)}")
                print(f"📝 非空行数: {len(non_empty_lines)}")
                print(f"📄 内容长度: {len(content)} 字符")
                
                # 显示前几行内容示例
                print(f"\n📖 内容示例 (前10行):")
                for i, line in enumerate(non_empty_lines[:10], 1):
                    if line:
                        print(f"   {i:2d}. {line[:80]}{'...' if len(line) > 80 else ''}")
                
                # 查找可能的目录内容
                toc_keywords = ['目录', '目  录', 'Contents', '第一章', '第二章', '绪论', '引言']
                toc_lines = []
                
                for i, line in enumerate(non_empty_lines):
                    for keyword in toc_keywords:
                        if keyword in line:
                            toc_lines.append((i+1, line))
                            break
                
                if toc_lines:
                    print(f"\n🔍 发现可能的目录相关内容:")
                    for line_num, line in toc_lines[:5]:
                        print(f"   第{line_num}行: {line[:100]}{'...' if len(line) > 100 else ''}")
                else:
                    print(f"\n⚠️  未发现明显的目录标识")
                    
            else:
                print("❌ 读取内容为空")
                
        except Exception as e:
            print(f"❌ 读取失败: {str(e)}")
            print(f"   错误类型: {type(e).__name__}")

if __name__ == "__main__":
    check_and_convert_doc_files()

