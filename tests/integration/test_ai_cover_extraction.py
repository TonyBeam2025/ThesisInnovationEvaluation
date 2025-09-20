#!/usr/bin/env python3
"""
专门测试AI智能识别封面信息
解决导入问题，直接使用AI进行智能识别
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

import json
from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word

# 直接导入AI客户端
try:
    from thesis_inno_eval.gemini_client import get_ai_client
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

def extract_cover_with_ai(cover_text: str) -> dict:
    """使用AI直接智能识别封面信息"""
    
    if not AI_AVAILABLE:
        print("❌ AI客户端不可用")
        return {}
    
    try:
        ai_client = get_ai_client()
        
        prompt = f"""
请从以下学位论文封面内容中提取论文的基本信息。请严格按照JSON格式返回，只提取确实存在的信息，不要编造：

封面内容：
{cover_text[:2000]}

请提取以下字段（如果某个字段不存在，请设为空字符串）：
{{
  "ThesisNumber": "学号",
  "ChineseTitle": "中文论文标题",
  "EnglishTitle": "英文论文标题", 
  "ChineseAuthor": "作者中文姓名",
  "EnglishAuthor": "作者英文姓名",
  "ChineseUniversity": "中文学校名称",
  "EnglishUniversity": "英文学校名称",
  "DegreeLevel": "学位级别（如：博士、硕士）",
  "ChineseMajor": "中文专业名称",
  "EnglishMajor": "英文专业名称",
  "College": "学院名称",
  "ChineseSupervisor": "中文导师姓名",
  "EnglishSupervisor": "英文导师姓名",
  "DefenseDate": "答辩日期",
  "SubmissionDate": "提交日期"
}}

注意：
- 只提取明确存在的信息，不要推测
- 姓名不要包含"姓名："等标签
- 学校名称不要包含"学位授予单位："等标签
- 标题要完整，不要包含时间戳等无关信息
- 日期格式为YYYY-MM-DD，如果只有年份则为YYYY

返回JSON："""

        response = ai_client.send_message(prompt)
        if response and response.content:
            # 提取JSON内容
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            metadata = json.loads(content.strip())
            
            # 验证和清理结果
            for key, value in metadata.items():
                if value and isinstance(value, str):
                    metadata[key] = value.strip()
            
            return metadata
        
    except Exception as e:
        print(f"❌ AI识别失败: {e}")
        return {}

def test_ai_cover_extraction():
    """测试AI封面信息提取"""
    
    print("🧠 测试AI智能识别封面信息")
    print("=" * 60)
    
    file_path = "data/input/50286.docx"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    try:
        # 提取文档文本
        print("📄 提取文档文本...")
        text = extract_text_from_word(file_path)
        
        if not text:
            print("❌ 文档文本提取失败")
            return
        
        print(f"📊 文档长度: {len(text):,} 字符")
        
        # 精准定位封面区域
        print("\n🎯 精准定位封面区域...")
        cover_end_markers = [
            '学位论文使用授权书',
            '学位论文原创性声明',
            '独创性声明',
            '版权使用授权书',
            '中文摘要',
            '摘要',
            'ABSTRACT'
        ]
        
        cover_text = text
        for marker in cover_end_markers:
            pos = text.find(marker)
            if pos > 0:
                cover_text = text[:pos]
                print(f"   封面区域定位: 在'{marker}'之前，长度 {len(cover_text)} 字符")
                break
        
        # 显示封面内容片段
        print(f"\n📄 封面内容片段:")
        print("-" * 40)
        print(cover_text[:500] + "..." if len(cover_text) > 500 else cover_text)
        print("-" * 40)
        
        # 使用AI智能识别
        print(f"\n🧠 使用AI智能识别...")
        if AI_AVAILABLE:
            ai_result = extract_cover_with_ai(cover_text)
            
            print(f"\n AI识别结果:")
            print("-" * 40)
            for field, value in ai_result.items():
                status = "" if value else "❌"
                print(f"   {status} {field}: {value}")
            
            # 保存AI结果
            output_file = "data/output/50286_ai_cover_extracted_info.json"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            result_data = {
                'ai_cover_metadata': ai_result,
                'extraction_method': 'ai_intelligent_recognition',
                'extraction_time': '2025-08-20T17:20:00',
                'file_path': file_path
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 AI识别结果已保存: {output_file}")
            
            # 质量评估
            non_empty_count = sum(1 for v in ai_result.values() if v and str(v).strip())
            total_fields = len(ai_result)
            completeness = non_empty_count / total_fields
            
            print(f"\n📊 AI识别质量评估:")
            print(f"   提取字段数: {non_empty_count}/{total_fields}")
            print(f"   完整度: {completeness:.1%}")
            print(f"   是否包含标签文字: {'否' if not any('：' in str(v) for v in ai_result.values() if v) else '是'}")
            
            return ai_result
        else:
            print("❌ AI不可用，跳过AI识别测试")
        
    except Exception as e:
        print(f"❌ AI封面提取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_ai_cover_extraction()
