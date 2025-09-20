#!/usr/bin/env python3
"""
测试论文全面抽取能力和Markdown格式转换能力
测试目标：高分子材料论文 - 唐金金
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
import time
from pathlib import Path

sys.path.append('./src')

# 导入必要的模块
import thesis_inno_eval.smart_reference_extractor as sre_module
from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word, ThesisExtractorPro
from thesis_inno_eval.ai_client import get_ai_client

def test_thesis_extraction_and_markdown():
    """测试论文抽取和Markdown转换的完整流程"""
    
    # 测试文件路径
    docx_path = r"C:\MyProjects\thesis_Inno_Eval\data\input\1_高分子材料_21807119_唐金金_LW.docx"
    
    print("🔬 测试高分子材料论文抽取和Markdown转换能力")
    print("=" * 80)
    print(f"📄 测试文件: {os.path.basename(docx_path)}")
    
    # 1. 检查文件存在性
    if not os.path.exists(docx_path):
        print(f"❌ 错误：文件不存在 - {docx_path}")
        return False
    
    # 2. 读取Word文档
    print("\n📚 步骤1：读取Word文档...")
    start_time = time.time()
    try:
        text = extract_text_from_word(docx_path)
        read_time = time.time() - start_time
        print(f"   ✅ 文档读取成功")
        print(f"   📊 文档总长度: {len(text):,} 字符")
        print(f"   ⏱️ 读取耗时: {read_time:.2f}秒")
        
        # 显示文档开头预览
        print(f"\n   📖 文档开头预览 (前500字符):")
        print("   " + "-" * 50)
        print("   " + text[:500].replace('\n', '\n   '))
        print("   " + "-" * 50)
        
    except Exception as e:
        print(f"   ❌ 文档读取失败: {str(e)}")
        return False
    
    # 3. 测试SmartReferenceExtractor参考文献抽取
    print("\n📖 步骤2：测试智能参考文献抽取...")
    try:
        # SmartReferenceExtractor专门用于DOCX，不需要AI客户端
        extractor = sre_module.SmartReferenceExtractor(ai_client=None)
        
        ref_start_time = time.time()
        references, ref_stats = extractor.extract_references(
            text, 
            source_format='docx',
            source_path=docx_path
        )
        ref_time = time.time() - ref_start_time
        
        print(f"   ✅ 参考文献抽取完成")
        print(f"   📊 提取数量: {len(references)} 条")
        print(f"   🔧 提取方法: {ref_stats.get('method_used', 'unknown')}")
        print(f"   ⏱️ 抽取耗时: {ref_time:.2f}秒")
        print(f"   ✅ 提取状态: {'成功' if ref_stats.get('success', False) else '失败'}")
        
        if references:
            print(f"\n   📝 参考文献预览 (前5条):")
            for i, ref in enumerate(references[:5], 1):
                print(f"   {i:2d}. {ref[:80]}{'...' if len(ref) > 80 else ''}")
                
    except Exception as e:
        print(f"   ❌ 参考文献抽取失败: {str(e)}")
        references = []
        ref_stats = {}
    
    # 4. 测试AI智能抽取功能
    print("\n🤖 步骤3：测试AI智能论文结构抽取...")
    try:
        # 初始化专业版提取器（包含AI功能）
        extractor_pro = ThesisExtractorPro()
        
        ai_start_time = time.time()
        # 调用AI智能抽取方法
        extracted_data = extractor_pro.extract_with_integrated_strategy(text, docx_path)
        ai_time = time.time() - ai_start_time
        
        print(f"   ✅ AI智能抽取完成")
        print(f"   📊 提取字段数: {len(extracted_data)} 个")
        print(f"   ⏱️ AI抽取耗时: {ai_time:.2f}秒")
        
        # 显示提取的关键信息
        key_fields = ['title_cn', 'author_cn', 'university_cn', 'major_cn', 'degree_level']
        print(f"\n   📋 关键信息预览:")
        for field in key_fields:
            if field in extracted_data and extracted_data[field]:
                value = extracted_data[field][:100] + "..." if len(str(extracted_data[field])) > 100 else extracted_data[field]
                print(f"      {field}: {value}")
        
        # 统计提取成功的字段
        extracted_fields = [k for k, v in extracted_data.items() if v and str(v).strip()]
        print(f"   📊 成功提取字段: {len(extracted_fields)}/{len(extracted_data)}")
        
    except Exception as e:
        print(f"   ❌ AI智能抽取失败: {str(e)}")
        extracted_data = {}
        ai_time = 0
    
    # 5. 测试章节结构分析
    print("\n📑 步骤4：分析论文结构...")
    try:
        # 查找可能的章节标题
        lines = text.split('\n')
        potential_chapters = []
        
        # 常见的学术论文章节模式
        chapter_patterns = [
            r'第[一二三四五六七八九十\d]+章',
            r'第[一二三四五六七八九十\d]+节',
            r'^\d+\s+\S+',
            r'^[一二三四五六七八九十]+、',
            r'^[一二三四五六七八九十]+\.',
            r'摘\s*要',
            r'Abstract',
            r'关键词',
            r'Keywords',
            r'引\s*言',
            r'前\s*言',
            r'绪\s*论',
            r'结\s*论',
            r'致\s*谢',
            r'参考文献',
            r'附\s*录'
        ]
        
        import re
        for i, line in enumerate(lines):
            line = line.strip()
            if len(line) > 0 and len(line) < 50:  # 可能的章节标题长度
                for pattern in chapter_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        potential_chapters.append((i+1, line))
                        break
        
        print(f"   ✅ 发现 {len(potential_chapters)} 个潜在章节标题")
        if potential_chapters:
            print(f"   📋 章节结构预览 (前10个):")
            for line_num, title in potential_chapters[:10]:
                print(f"   L{line_num:4d}: {title}")
                
    except Exception as e:
        print(f"   ⚠️ 章节结构分析遇到问题: {str(e)}")
        potential_chapters = []
    
    # 6. 测试Markdown转换能力
    print("\n📝 步骤5：测试Markdown格式转换...")
    try:
        markdown_content = convert_to_markdown(text, references, potential_chapters, extracted_data)
        
        # 保存Markdown文件
        output_path = docx_path.replace('.docx', '_converted.md')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"   ✅ Markdown转换完成")
        print(f"   📁 输出文件: {output_path}")
        print(f"   📊 Markdown长度: {len(markdown_content):,} 字符")
        
        # 显示Markdown预览
        print(f"\n   📖 Markdown预览 (前1000字符):")
        print("   " + "-" * 50)
        for line in markdown_content[:1000].split('\n'):
            print("   " + line)
        print("   " + "-" * 50)
        
    except Exception as e:
        print(f"   ❌ Markdown转换失败: {str(e)}")
        markdown_content = ""
        output_path = ""
        extracted_data = extracted_data if 'extracted_data' in locals() else {}
    
    # 7. 总结报告
    print("\n📊 测试总结报告")
    print("=" * 80)
    print(f"📄 源文件: {os.path.basename(docx_path)}")
    print(f"📝 文档长度: {len(text):,} 字符")
    print(f"📖 参考文献: {len(references)} 条")
    print(f"📑 章节标题: {len(potential_chapters)} 个")
    if 'extracted_data' in locals() and extracted_data:
        print(f"🤖 AI抽取字段: {len(extracted_data)} 个")
        success_fields = [k for k, v in extracted_data.items() if v and str(v).strip()]
        print(f"✅ 成功字段: {len(success_fields)} 个")
    print(f"📝 Markdown文件: {'✅ 已生成' if markdown_content else '❌ 生成失败'}")
    if output_path:
        print(f"📁 输出路径: {output_path}")
    
    total_time = time.time() - start_time
    print(f"⏱️ 总处理时间: {total_time:.2f}秒")
    
    return True

from typing import Optional

def convert_to_markdown(text: str, references: list, chapters: list, extracted_data: Optional[dict] = None) -> str:
    """将论文内容转换为Markdown格式"""
    
    markdown_lines = []
    
    # 使用AI提取的数据作为标题和元信息
    title = "高分子材料论文 - 唐金金"
    author = "唐金金"
    
    if extracted_data:
        title = extracted_data.get('title_cn', title)
        author = extracted_data.get('author_cn', author)
    
    # 添加标题和元信息
    markdown_lines.append(f"# {title}")
    markdown_lines.append("")
    markdown_lines.append(f"> 作者: {author}")
    markdown_lines.append("> 自动从DOCX文件转换为Markdown格式")
    markdown_lines.append(f"> 转换时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_lines.append("")
    
    # 添加AI提取的结构化信息
    if extracted_data:
        markdown_lines.append("## 📋 论文信息")
        markdown_lines.append("")
        info_fields = {
            'university_cn': '学校',
            'major_cn': '专业',
            'degree_level': '学位级别',
            'supervisor_cn': '导师',
            'defense_date': '答辩日期'
        }
        
        for field, label in info_fields.items():
            if field in extracted_data and extracted_data[field]:
                markdown_lines.append(f"- **{label}**: {extracted_data[field]}")
        markdown_lines.append("")
    
    # 添加目录
    if chapters:
        markdown_lines.append("## 📋 目录")
        markdown_lines.append("")
        for i, (line_num, title) in enumerate(chapters, 1):
            # 简单的目录生成
            anchor = title.replace(' ', '-').replace('、', '').replace('.', '')
            markdown_lines.append(f"{i}. [{title}](#{anchor})")
        markdown_lines.append("")
    
    # 处理正文内容
    markdown_lines.append("## 📄 论文正文")
    markdown_lines.append("")
    
    # 将文本按段落分割并格式化
    paragraphs = text.split('\n\n')
    for para in paragraphs:
        para = para.strip()
        if para:
            # 检查是否是章节标题
            is_chapter = False
            for _, chapter_title in chapters:
                if chapter_title in para and len(para) < 100:
                    # 转换为Markdown标题
                    level = "###" if any(word in para for word in ['第', '章', '节']) else "####"
                    markdown_lines.append(f"{level} {para}")
                    markdown_lines.append("")
                    is_chapter = True
                    break
            
            if not is_chapter:
                # 普通段落
                markdown_lines.append(para)
                markdown_lines.append("")
    
    # 添加参考文献部分
    if references:
        markdown_lines.append("## 📚 参考文献")
        markdown_lines.append("")
        for i, ref in enumerate(references, 1):
            markdown_lines.append(f"{i}. {ref}")
        markdown_lines.append("")
    
    # 添加生成信息
    markdown_lines.append("---")
    markdown_lines.append("")
    markdown_lines.append("*本文档由SmartReferenceExtractor自动生成*")
    markdown_lines.append("")
    
    return '\n'.join(markdown_lines)

if __name__ == "__main__":
    success = test_thesis_extraction_and_markdown()
    if success:
        print("\n🎉 测试完成！")
    else:
        print("\n❌ 测试失败！")
