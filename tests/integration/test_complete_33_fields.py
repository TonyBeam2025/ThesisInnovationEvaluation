#!/usr/bin/env python3
"""
完整测试：33个字段的论文信息抽取
验证改进后的提取系统性能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

import json
import time
from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word, ThesisExtractorPro

def test_complete_33_fields_extraction():
    """测试完整的33个字段信息抽取"""
    
    print("🎯 完整33个字段论文信息抽取测试")
    print("=" * 80)
    
    file_path = "data/input/50286.docx"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    try:
        start_time = time.time()
        
        # 提取文档文本
        print("📄 提取文档文本...")
        text = extract_text_from_word(file_path)
        
        if not text:
            print("❌ 文档文本提取失败")
            return
        
        print(f"📊 文档长度: {len(text):,} 字符")
        
        # 使用改进后的专业提取器
        print("\n🚀 启动专业版论文信息提取器...")
        extractor = ThesisExtractorPro()
        
        # 执行完整提取
        result = extractor.extract_with_integrated_strategy(text, file_path)
        
        processing_time = time.time() - start_time
        
        # 分类显示结果
        print(f"\n📊 提取结果分析 (耗时: {processing_time:.2f}秒)")
        print("=" * 80)
        
        # 封面基本信息字段
        cover_fields = {
            'ThesisNumber': '学号/论文编号',
            'ChineseTitle': '中文标题', 
            'EnglishTitle': '英文标题',
            'ChineseAuthor': '中文作者',
            'EnglishAuthor': '英文作者',
            'ChineseUniversity': '中文学校',
            'EnglishUniversity': '英文学校',
            'DegreeLevel': '学位级别',
            'ChineseMajor': '中文专业',
            'EnglishMajor': '英文专业',
            'College': '学院',
            'ChineseSupervisor': '中文导师',
            'EnglishSupervisor': '英文导师',
            'DefenseDate': '答辩日期',
            'SubmissionDate': '提交日期',
        }
        
        # 摘要和关键词字段
        abstract_fields = {
            'ChineseAbstract': '中文摘要',
            'EnglishAbstract': '英文摘要',
            'ChineseKeywords': '中文关键词',
            'EnglishKeywords': '英文关键词',
        }
        
        # 内容分析字段
        content_fields = {
            'LiteratureReview': '文献综述',
            'ChineseResearchDirection': '中文研究方向',
            'EnglishResearchDirection': '英文研究方向',
            'ResearchMethods': '研究方法',
            'TheoreticalFramework': '理论框架',
            'MainInnovations': '主要创新',
            'PracticalProblems': '实际问题',
            'ProposedSolutions': '解决方案',
            'ResearchConclusions': '研究结论',
            'ApplicationValue': '应用价值',
            'FutureWork': '未来工作',
            'Acknowledgement': '致谢',
            'ReferenceList': '参考文献',
            'AuthorContributions': '作者贡献'
        }
        
        # 1. 封面信息提取结果
        print("📋 1. 封面基本信息 (15个字段)")
        print("-" * 60)
        cover_success = 0
        for field, description in cover_fields.items():
            value = result.get(field, '')
            status = "" if value else "❌"
            if value:
                cover_success += 1
                print(f"   {status} {description:12}: {value}")
            else:
                print(f"   {status} {description:12}: (未提取)")
        
        print(f"   📈 封面信息成功率: {cover_success}/15 ({cover_success/15:.1%})")
        
        # 2. 摘要和关键词提取结果
        print(f"\n📝 2. 摘要和关键词 (4个字段)")
        print("-" * 60)
        abstract_success = 0
        for field, description in abstract_fields.items():
            value = result.get(field, '')
            status = "" if value else "❌"
            if value:
                abstract_success += 1
                preview = value[:100] + "..." if len(value) > 100 else value
                print(f"   {status} {description:12}: {preview}")
            else:
                print(f"   {status} {description:12}: (未提取)")
        
        print(f"   📈 摘要关键词成功率: {abstract_success}/4 ({abstract_success/4:.1%})")
        
        # 3. 内容分析提取结果
        print(f"\n📚 3. 内容分析字段 (14个字段)")
        print("-" * 60)
        content_success = 0
        for field, description in content_fields.items():
            value = result.get(field, '')
            status = "" if value else "❌"
            if value:
                content_success += 1
                if field == 'ReferenceList' and isinstance(value, list):
                    print(f"   {status} {description:12}: {len(value)} 条参考文献")
                else:
                    preview = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
                    print(f"   {status} {description:12}: {preview}")
            else:
                print(f"   {status} {description:12}: (未提取)")
        
        print(f"   📈 内容分析成功率: {content_success}/14 ({content_success/14:.1%})")
        
        # 4. 总体统计
        total_success = cover_success + abstract_success + content_success
        total_fields = len(cover_fields) + len(abstract_fields) + len(content_fields)
        overall_rate = total_success / total_fields
        
        print(f"\n🏆 4. 总体提取统计")
        print("=" * 60)
        print(f"   总字段数: {total_fields}")
        print(f"   成功提取: {total_success}")
        print(f"   总成功率: {overall_rate:.1%}")
        print(f"   处理时间: {processing_time:.2f}秒")
        print(f"   置信度: {overall_rate:.3f}")
        
        # 5. 质量评估
        print(f"\n🔍 5. 质量评估")
        print("-" * 60)
        
        # 检查关键字段
        key_fields_status = {
            '学号': '' if result.get('ThesisNumber') else '❌',
            '中文标题': '' if result.get('ChineseTitle') else '❌',
            '英文标题': '' if result.get('EnglishTitle') else '❌',
            '作者姓名': '' if result.get('ChineseAuthor') else '❌',
            '学校名称': '' if result.get('ChineseUniversity') else '❌',
            '中文摘要': '' if result.get('ChineseAbstract') else '❌',
            '中文关键词': '' if result.get('ChineseKeywords') else '❌',
        }
        
        for field, status in key_fields_status.items():
            print(f"   {status} {field}")
        
        # 检查数据质量
        has_label_issues = False
        for field, value in result.items():
            if value and isinstance(value, str):
                if any(marker in value for marker in ['：', '姓名', '学位授予单位', '**转换时间**']):
                    has_label_issues = True
                    break
        
        print(f"   🔧 数据清理: {'完成' if not has_label_issues else '仍有标签残留'}")
        
        # 6. 保存完整结果
        output_file = "data/output/50286_complete_33_fields_extracted.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        complete_data = {
            'extracted_info': result,
            'metadata': {
                'extraction_time': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'method': 'integrated_strategy_enhanced',
                'file_path': file_path,
                'processing_time': processing_time,
                'extractor_version': '2.1_enhanced'
            },
            'statistics': {
                'total_fields': total_fields,
                'extracted_fields': total_success,
                'overall_success_rate': overall_rate,
                'cover_success_rate': cover_success/15,
                'abstract_success_rate': abstract_success/4,
                'content_success_rate': content_success/14,
                'confidence': overall_rate
            },
            'field_categories': {
                'cover_fields': {field: result.get(field, '') for field in cover_fields.keys()},
                'abstract_fields': {field: result.get(field, '') for field in abstract_fields.keys()},
                'content_fields': {field: result.get(field, '') for field in content_fields.keys()}
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 完整提取结果已保存: {output_file}")
        
        # 7. 改进建议
        print(f"\n💡 改进建议:")
        if cover_success < 12:
            print("   - 继续优化封面信息提取模式")
        if abstract_success < 3:
            print("   - 加强摘要和关键词定位算法")
        if content_success < 8:
            print("   - 改进内容章节识别和AI分析")
        
        print(f"\n🎯 测试完成！整体表现: {'优秀' if overall_rate > 0.7 else '良好' if overall_rate > 0.5 else '需要改进'}")
        
        return result
        
    except Exception as e:
        print(f"❌ 完整提取测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_complete_33_fields_extraction()
