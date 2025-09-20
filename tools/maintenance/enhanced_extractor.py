#!/usr/bin/env python3
"""
改进版论文抽取模块
精准定位 + AI智能识别，解决抽取错误问题
"""

import re
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from typing import Dict, Any, Optional, List
from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word, ThesisExtractorPro

class EnhancedThesisExtractor(ThesisExtractorPro):
    """增强版论文提取器 - 精准定位 + AI智能识别"""
    
    def __init__(self):
        super().__init__()
        self.ai_client = None
        self._init_ai_client()
        
    def _init_ai_client(self):
        """初始化AI客户端"""
        try:
            from thesis_inno_eval.ai_client import get_ai_client
            self.ai_client = get_ai_client()
            print(" AI客户端初始化成功")
        except Exception as e:
            print(f"⚠️ AI客户端初始化失败: {e}")
            self.ai_client = None
    
    def extract_with_ai_enhanced_strategy(self, text: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        使用AI增强策略进行提取
        1. 精准定位候选区域
        2. AI智能识别和清理
        3. 多重验证
        """
        print("🚀 启动AI增强版论文信息提取系统")
        print("=" * 60)
        
        # 步骤1: 基础抽取 + 精准定位
        print("🎯 步骤1: 精准定位候选信息")
        candidates = self._precise_locate_candidates(text)
        
        # 步骤2: AI智能识别和清理
        print("🧠 步骤2: AI智能识别和清理")
        if self.ai_client:
            refined_result = self._ai_refine_extraction(candidates, text)
        else:
            refined_result = self._fallback_refine_extraction(candidates)
        
        # 步骤3: 多重验证
        print("🔍 步骤3: 多重验证和修复")
        final_result = self._multi_layer_validation(refined_result, text)
        
        # 步骤4: 补充提取
        print("📄 步骤4: 补充内容提取")
        final_result = self._supplement_extraction(final_result, text)
        
        self._generate_enhanced_report(final_result, file_path)
        
        return final_result
    
    def _precise_locate_candidates(self, text: str) -> Dict[str, List[str]]:
        """精准定位候选信息"""
        candidates = {}
        
        # 学号精准定位
        thesis_number_patterns = [
            r'学号[：:\s]*([A-Z0-9]{10,20})',
            r'学生证号[：:\s]*([A-Z0-9]{10,20})',
            r'(?:Student\s+)?(?:ID|Number)[：:\s]*([A-Z0-9]{10,20})',
        ]
        candidates['ThesisNumber'] = self._extract_by_patterns(text, thesis_number_patterns)
        
        # 中文标题精准定位
        chinese_title_patterns = [
            r'(?:论文题目|题目|Title)[：:\s]*\n*([^\n\r]{10,200}?)(?:\n|$)',
            r'^([^A-Za-z\n\r]{10,100})$',  # 独立行的中文标题
            r'(?:中文题目|Chinese\s+Title)[：:\s]*([^\n\r]{10,200})',
        ]
        candidates['ChineseTitle'] = self._extract_by_patterns(text, chinese_title_patterns)
        
        # 作者姓名精准定位
        chinese_author_patterns = [
            r'(?:作者|姓名|学生姓名)[：:\s]*([^\d\n\r]{2,10})(?:\s|$)',
            r'(?:研究生|学生)[：:\s]*([^\d\n\r]{2,10})(?:\s|$)',
            r'(?:Student|Author)[：:\s]*([^\d\n\r]{2,10})(?:\s|$)',
        ]
        candidates['ChineseAuthor'] = self._extract_by_patterns(text, chinese_author_patterns)
        
        # 英文标题精准定位
        english_title_patterns = [
            r'(?:English\s+Title|TITLE)[：:\s]*\n*([A-Za-z\s\-:]{15,200}?)(?:\n|$)',
            r'^([A-Z][A-Za-z\s\-:]{15,200})$',  # 独立行的英文标题
        ]
        candidates['EnglishTitle'] = self._extract_by_patterns(text, english_title_patterns)
        
        # 英文作者精准定位
        english_author_patterns = [
            r'(?:English\s+)?(?:Author|Name|By)[：:\s]*([A-Za-z\s]{3,30})(?:\n|$)',
            r'(?:Student|Candidate)[：:\s]*([A-Za-z\s]{3,30})(?:\n|$)',
        ]
        candidates['EnglishAuthor'] = self._extract_by_patterns(text, english_author_patterns)
        
        # 大学名称精准定位
        university_patterns = [
            r'([^A-Za-z\n\r]*大学)(?!\s*学位)',
            r'([^A-Za-z\n\r]*学院)(?!\s*专业)',
            r'(Beijing\s+University[^,\n]*)',
            r'(Beihang\s+University[^,\n]*)',
        ]
        candidates['ChineseUniversity'] = self._extract_by_patterns(text, university_patterns)
        
        print(f"   📍 候选信息定位完成: {len(candidates)} 个字段")
        for field, values in candidates.items():
            if values:
                print(f"      {field}: {len(values)} 个候选")
        
        return candidates
    
    def _extract_by_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """使用多个模式提取候选值"""
        candidates = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                cleaned = match.strip()
                if len(cleaned) > 1 and cleaned not in candidates:
                    candidates.append(cleaned)
        return candidates
    
    def _ai_refine_extraction(self, candidates: Dict[str, List[str]], text: str) -> Dict[str, Any]:
        """使用AI智能识别和清理抽取结果"""
        refined = {}
        
        for field, candidate_list in candidates.items():
            if not candidate_list:
                refined[field] = ""
                continue
            
            if len(candidate_list) == 1:
                # 单个候选，直接清理
                refined[field] = self._clean_field_value(candidate_list[0], field)
            else:
                # 多个候选，使用AI选择最佳
                best_candidate = self._ai_select_best_candidate(field, candidate_list, text)
                refined[field] = self._clean_field_value(best_candidate, field)
            
            if refined[field]:
                print(f"    {field}: {refined[field]}")
        
        return refined
    
    def _ai_select_best_candidate(self, field: str, candidates: List[str], context: str) -> str:
        """使用AI从多个候选中选择最佳结果"""
        if not self.ai_client or not candidates:
            return candidates[0] if candidates else ""
        
        try:
            prompt = f"""
请从以下候选项中选择最符合"{field}"字段要求的内容：

候选项：
{chr(10).join([f"{i+1}. {c}" for i, c in enumerate(candidates)])}

要求：
- 如果是标题，选择最完整、最正式的标题
- 如果是姓名，选择最干净、没有标签的姓名
- 如果是学校名称，选择最标准的校名
- 只返回选中的内容，不要包含序号或解释

选择结果："""

            response = self.ai_client.send_message(prompt)
            if response and response.content:
                result = response.content.strip()
                # 验证结果是否在候选项中
                for candidate in candidates:
                    if candidate in result or result in candidate:
                        return candidate
            
        except Exception as e:
            print(f"   ⚠️ AI选择失败: {e}")
        
        # 降级策略：选择最长的候选项
        return max(candidates, key=len) if candidates else ""
    
    def _clean_field_value(self, value: str, field: str) -> str:
        """清理字段值"""
        if not value:
            return ""
        
        # 移除常见的标签文字
        label_patterns = [
            r'^(?:学号|姓名|作者|标题|题目)[：:\s]*',
            r'^(?:Student|Author|Title|Name)[：:\s]*',
            r'^(?:专业|学院|大学)[：:\s]*',
            r'^(?:Major|College|University)[：:\s]*',
            r'^\*\*[^*]+\*\*[：:\s]*',  # Markdown标记
            r'^[\d\.\s]*',  # 前导数字
        ]
        
        cleaned = value
        for pattern in label_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip()
        
        # 特定字段的清理
        if field == 'ChineseAuthor':
            # 移除可能的多余文字
            cleaned = re.sub(r'(?:姓名|学生|研究生)', '', cleaned).strip()
        elif field == 'ChineseUniversity':
            # 保留核心大学名称
            match = re.search(r'([^，,\n\r]*大学)', cleaned)
            if match:
                cleaned = match.group(1)
        elif field in ['ChineseTitle', 'EnglishTitle']:
            # 移除转换时间等无关信息
            cleaned = re.sub(r'\*\*转换时间\*\*[^*]*', '', cleaned)
            cleaned = re.sub(r'^\d{4}-\d{2}-\d{2}.*', '', cleaned)
        
        return cleaned.strip()
    
    def _fallback_refine_extraction(self, candidates: Dict[str, List[str]]) -> Dict[str, Any]:
        """AI不可用时的降级策略"""
        refined = {}
        
        for field, candidate_list in candidates.items():
            if not candidate_list:
                refined[field] = ""
                continue
            
            # 选择最合适的候选项
            if field in ['ChineseTitle', 'EnglishTitle']:
                # 标题选择最长的
                best = max(candidate_list, key=len, default="")
            elif field in ['ChineseAuthor', 'EnglishAuthor']:
                # 姓名选择最短的（通常更干净）
                best = min([c for c in candidate_list if len(c) > 1], key=len, default="")
            else:
                # 其他字段选择第一个
                best = candidate_list[0]
            
            refined[field] = self._clean_field_value(best, field)
            if refined[field]:
                print(f"    {field}: {refined[field]}")
        
        return refined
    
    def _multi_layer_validation(self, result: Dict[str, Any], text: str) -> Dict[str, Any]:
        """多层次验证和修复"""
        validated = result.copy()
        
        # 验证学号格式
        if validated.get('ThesisNumber'):
            thesis_num = validated['ThesisNumber']
            if not re.match(r'^[A-Z0-9]{8,20}$', thesis_num):
                print(f"   ⚠️ 学号格式可能有误: {thesis_num}")
        
        # 验证姓名合理性
        if validated.get('ChineseAuthor'):
            author = validated['ChineseAuthor']
            if len(author) < 2 or len(author) > 8:
                print(f"   ⚠️ 中文姓名长度异常: {author}")
        
        # 验证标题长度
        if validated.get('ChineseTitle'):
            title = validated['ChineseTitle']
            if len(title) < 10:
                print(f"   ⚠️ 中文标题可能不完整: {title}")
        
        return validated
    
    def _supplement_extraction(self, result: Dict[str, Any], text: str) -> Dict[str, Any]:
        """补充提取其他字段"""
        # 使用父类方法补充其他内容
        parent_result = super().extract_with_integrated_strategy(text)
        
        # 合并结果，优先使用AI增强的结果
        for field in self.standard_fields:
            if field not in result or not result[field]:
                if field in parent_result and parent_result[field]:
                    result[field] = parent_result[field]
        
        return result
    
    def _generate_enhanced_report(self, result: Dict[str, Any], file_path: Optional[str]):
        """生成增强版提取报告"""
        non_empty_count = sum(1 for v in result.values() if v and str(v).strip())
        confidence = non_empty_count / len(self.standard_fields)
        
        print(f"\n AI增强提取完成")
        print(f"📊 提取字段数: {non_empty_count}/{len(self.standard_fields)}")
        print(f"📈 完整度: {confidence:.1%}")
        print(f"🎖️ 置信度: {confidence:.2f}")


def test_enhanced_extraction():
    """测试增强版提取器"""
    
    print("🧪 测试AI增强版论文抽取模块")
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
        
        # 使用增强版提取器
        extractor = EnhancedThesisExtractor()
        result = extractor.extract_with_ai_enhanced_strategy(text, file_path)
        
        # 保存结果
        output_file = "data/output/50286_enhanced_extracted_info.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        enhanced_data = {
            'extracted_info': result,
            'metadata': {
                'extraction_time': '2025-08-20T17:10:00',
                'method': 'ai_enhanced_strategy',
                'file_path': file_path
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 增强版提取结果已保存: {output_file}")
        
        # 对比显示改进效果
        print(f"\n📊 关键字段提取对比:")
        key_fields = ['ThesisNumber', 'ChineseTitle', 'ChineseAuthor', 'ChineseUniversity']
        for field in key_fields:
            value = result.get(field, '')
            print(f"   {field}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ 增强版提取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_enhanced_extraction()

