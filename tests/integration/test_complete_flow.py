#!/usr/bin/env python3
"""
测试完整的cnki_auto_search + report_generation流程
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
sys.path.insert(0, 'src')

def test_complete_flow():
    """测试完整流程"""
    print("测试完整的文献检索 + 论文抽取 + 报告生成流程")
    print("注意：此测试需要有效的API密钥和网络连接")
    
    input_file = "data/input/15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究.docx"
    
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    try:
        # 导入必要的模块
        from src.thesis_inno_eval.cnki_client_pool import cnki_auto_search
        from src.thesis_inno_eval.report_generator import MarkdownReportGenerator
        from src.thesis_inno_eval.config_manager import get_config_manager
        
        config_mgr = get_config_manager()
        output_dir = config_mgr.get_output_dir()
        output_md_path = os.path.join(output_dir, "test_output.md")
        
        print("1. 开始文献检索和论文信息抽取...")
        
        # 调用cnki_auto_search，获取文献和论文信息
        search_results = cnki_auto_search(
            input_file, 
            output_md_path, 
            languages=['Chinese', 'English']
        )
        
        papers_by_lang = search_results['papers_by_lang']
        thesis_extracted_info = search_results['thesis_extracted_info']
        
        print(" 文献检索完成")
        for lang, papers in papers_by_lang.items():
            print(f"   {lang}: {len(papers)} 篇相关文献")
        
        if thesis_extracted_info:
            print(" 论文结构化信息抽取成功")
            print(f"   标题: {thesis_extracted_info.get('ChineseTitle', 'N/A')[:50]}...")
            print(f"   关键词: {thesis_extracted_info.get('ChineseKeywords', 'N/A')}")
        else:
            print("⚠️ 论文结构化信息抽取失败")
        
        print("\n2. 开始生成评估报告...")
        
        # 生成评估报告
        generator = MarkdownReportGenerator()
        report_path = generator.generate_evaluation_report(
            input_file,
            thesis_extracted_info=thesis_extracted_info
        )
        
        print(f" 评估报告生成成功: {report_path}")
        
        # 验证报告内容
        print("\n3. 验证报告内容...")
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查是否包含论文信息
        if thesis_extracted_info:
            title = thesis_extracted_info.get('ChineseTitle', '')
            if title and title in content:
                print(" 报告正确包含了论文标题信息")
            else:
                print("⚠️ 报告可能未正确使用论文信息")
                
        # 检查创新性分析
        if 'PMC指数评价模型' in content:
            print(" 报告包含了基于论文内容的创新性分析")
        else:
            print("⚠️ 报告的创新性分析可能使用了默认内容")
        
        print(f"\n📄 报告文件大小: {len(content)} 字符")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("测试新的集成流程")
    print("=" * 60)
    
    success = test_complete_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 完整流程测试成功！")
        print(" cnki_auto_search 现在返回包含论文抽取信息的结构化结果")
        print(" MarkdownReportGenerator 可以接收和使用这些信息进行文献对比分析")
    else:
        print("💥 完整流程测试失败")
        print("请检查API配置和网络连接")
    print("=" * 60)
