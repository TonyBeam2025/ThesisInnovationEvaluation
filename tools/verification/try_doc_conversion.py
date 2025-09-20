"""
使用Win32COM处理.doc文件
"""
import os
import sys

def try_win32_word_conversion():
    """尝试使用Win32COM转换.doc文件"""
    
    try:
        import win32com.client
        print(" 找到win32com模块")
        
        doc_files = [
            r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.doc",
            r"c:\MyProjects\thesis_Inno_Eval\data\input\法律硕士_2018213020_王纪锋_学位论文.doc", 
            r"c:\MyProjects\thesis_Inno_Eval\data\input\1_音乐_20172001013韩柠灿（硕士毕业论文）.doc"
        ]
        
        for doc_file in doc_files:
            print(f"\n{'='*60}")
            print(f"处理文件: {os.path.basename(doc_file)}")
            print(f"{'='*60}")
            
            if not os.path.exists(doc_file):
                print(f"❌ 文件不存在: {doc_file}")
                continue
                
            try:
                # 创建Word应用程序对象
                word_app = win32com.client.Dispatch('Word.Application')
                word_app.Visible = False
                
                # 打开文档
                doc = word_app.Documents.Open(doc_file)
                
                # 获取文档内容
                content = doc.Content.Text
                
                # 关闭文档
                doc.Close()
                word_app.Quit()
                
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
                print(f"❌ 处理失败: {str(e)}")
                try:
                    word_app.Quit()
                except:
                    pass
                    
    except ImportError:
        print("❌ 未找到win32com模块，需要安装: pip install pywin32")
        return False
        
    return True

def try_simple_text_extraction():
    """尝试简单的文本提取"""
    print("\n" + "="*60)
    print("尝试简单的二进制文本提取")
    print("="*60)
    
    doc_files = [
        r"c:\MyProjects\thesis_Inno_Eval\data\input\1_马克思主义哲学86406_010101_81890101_LW.doc",
        r"c:\MyProjects\thesis_Inno_Eval\data\input\法律硕士_2018213020_王纪锋_学位论文.doc", 
        r"c:\MyProjects\thesis_Inno_Eval\data\input\1_音乐_20172001013韩柠灿（硕士毕业论文）.doc"
    ]
    
    for doc_file in doc_files:
        print(f"\n处理文件: {os.path.basename(doc_file)}")
        
        if not os.path.exists(doc_file):
            print(f"❌ 文件不存在")
            continue
            
        try:
            with open(doc_file, 'rb') as f:
                data = f.read()
                
            # 尝试解码为文本（忽略错误）
            text_content = data.decode('utf-8', errors='ignore')
            
            # 提取可能的中文文本
            import re
            chinese_pattern = r'[\u4e00-\u9fff]+'
            chinese_matches = re.findall(chinese_pattern, text_content)
            
            if chinese_matches:
                print(f"🔍 发现{len(chinese_matches)}个中文文本片段")
                
                # 查找目录相关内容
                toc_keywords = ['目录', '第一章', '第二章', '绪论', '引言', '摘要']
                found_toc = []
                
                for match in chinese_matches:
                    if len(match) > 2:  # 过滤太短的匹配
                        for keyword in toc_keywords:
                            if keyword in match:
                                found_toc.append(match)
                                break
                
                if found_toc:
                    print(f"📖 发现可能的目录内容:")
                    for toc in found_toc[:10]:
                        print(f"   {toc[:100]}{'...' if len(toc) > 100 else ''}")
                else:
                    print(f"📝 中文内容示例:")
                    for match in chinese_matches[:10]:
                        if len(match) > 2:
                            print(f"   {match[:100]}{'...' if len(match) > 100 else ''}")
            else:
                print("❌ 未发现可读的中文内容")
                
        except Exception as e:
            print(f"❌ 处理失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 尝试处理.doc文件")
    
    # 首先尝试Win32COM
    if not try_win32_word_conversion():
        # 如果Win32COM不可用，尝试简单的文本提取
        try_simple_text_extraction()

