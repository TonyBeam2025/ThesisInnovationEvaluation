#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import sys
import json
import re
sys.path.append('src')

def test_json_parsing():
    # 模拟AI返回的Markdown JSON响应
    ai_response = '''```json
{
  "ChineseTitle": "跨模态图像融合技术在医疗影像分析中的研究",
  "EnglishTitle": "Research on Cross-Modal Image Fusion Technology in Medical Image Analysis",
  "ChineseKeywords": ["跨模态融合", "深度学习", "医学影像分析"],
  "EnglishKeywords": ["Cross-modal fusion", "Deep learning", "Medical image analysis"],
  "ChineseAbstract": "影像学检查是医疗领域最重要的筛查手段，但仅凭医生经验难以对影像学异常做出明确判断。人工智能技术通过深度神经网络分析影像数据，辅助诊断。",
  "EnglishAbstract": "Imaging examinations are the predominant screening method in medicine, but relying solely on clinician experience often leads to inconclusive judgments.",
  "Research Background": "医疗影像数据量巨大，超过90%为影像数据。",
  "Research Objectives": "1. 探索跨模态深度学习方法；2. 研究跨模态数据融合方法",
  "Research Methods": "使用深度学习和图像处理技术",
  "Main Contributions": "提出了新的跨模态融合方法",
  "Experimental Results": "显著提高了诊断准确性",
  "Conclusions": "跨模态融合方法有效",
  "Future Work": "扩大数据集规模，提高模型泛化能力",
  "References": "参考文献待补充",
  "Technical Details": "技术细节待补充"
}
```'''

    print(f"原始响应长度: {len(ai_response)}")
    print(f"包含```json: {'```json' in ai_response}")
    
    # 测试提取JSON的逻辑
    info = ai_response
    
    if "```json" in info:
        print("检测到```json标记")
        # 处理 ```json ... ``` 格式，使用更灵活的正则表达式
        # 首先尝试严格匹配
        print("尝试严格匹配...")
        match = re.search(r"```json\s*\n([\s\S]+?)\n\s*```", info)
        if not match:
            print("严格匹配失败，尝试宽松匹配...")
            match = re.search(r"```json\s*([\s\S]+?)\s*```", info)
        if not match:
            # 尝试找到 ```json 后的内容到下一个 ``` 
            print("宽松匹配失败，尝试查找模式...")
            json_start = info.find("```json")
            if json_start != -1:
                json_start += len("```json")
                json_end = info.find("```", json_start)
                if json_end != -1:
                    info = info[json_start:json_end].strip()
                    print("找到JSON内容")
                else:
                    print("未找到结束标记")
        else:
            info = match.group(1).strip()
            print("匹配成功")
    
    print(f"提取的JSON长度: {len(info)}")
    print("提取的JSON内容:")
    print(info[:500] + "..." if len(info) > 500 else info)
    
    # 尝试解析JSON
    try:
        parsed = json.loads(info)
        print(f"JSON解析成功！字段数量: {len(parsed)}")
        return True
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"错误位置: {e.pos}")
        if e.pos < len(info):
            problem_char = info[e.pos]
            print(f"问题字符: {repr(problem_char)}, ASCII: {ord(problem_char)}")
            
            # 显示错误位置附近的内容
            start = max(0, e.pos - 30)
            end = min(len(info), e.pos + 30)
            snippet = info[start:end]
            print(f"错误位置附近: {repr(snippet)}")
        return False

if __name__ == '__main__':
    success = test_json_parsing()
    print(f"测试结果: {'成功' if success else '失败'}")
