#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import sys
import json
import re
sys.path.append('src')

def test_control_character_json():
    # 模拟包含控制字符的AI响应
    # 在第8行第141字符位置插入一个控制字符
    ai_response_with_control = '''```json
{
  "ChineseTitle": "跨模态图像融合技术在医疗影像分析中的研究",
  "EnglishTitle": "Research on Cross-Modal Image Fusion Technology in Medical Image Analysis",
  "ChineseKeywords": ["跨模态融合", "深度学习", "医学影像分析"],
  "EnglishKeywords": ["Cross-modal fusion", "Deep learning", "Medical image analysis"],
  "ChineseAbstract": "影像学检查是医疗领域最重要的筛查手段，但仅凭医生经验难以\x08对影像学异常做出明确判断。人工智能技术通过深度神经网络分析影像数据，辅助诊断。",
  "EnglishAbstract": "Imaging examinations are the predominant screening method in medicine.",
  "Research Background": "医疗影像数据量巨大",
  "Research Objectives": "探索跨模态深度学习方法",
  "Research Methods": "使用深度学习技术",
  "Main Contributions": "提出了新方法",
  "Experimental Results": "提高了准确性",
  "Conclusions": "方法有效",
  "Future Work": "扩大数据集",
  "References": "参考文献",
  "Technical Details": "技术细节"
}
```'''

    print(f"原始响应长度: {len(ai_response_with_control)}")
    
    # 检查控制字符
    control_chars = []
    for i, char in enumerate(ai_response_with_control):
        if ord(char) < 32 and char not in ['\t', '\n', '\r']:
            control_chars.append((i, ord(char), repr(char)))
    
    print(f"发现 {len(control_chars)} 个控制字符:")
    for pos, code, char in control_chars:
        print(f"  位置{pos}: ASCII-{code} {char}")
    
    # 提取JSON
    info = ai_response_with_control
    if "```json" in info:
        match = re.search(r"```json\s*\n([\s\S]+?)\n\s*```", info)
        if match:
            info = match.group(1).strip()
    
    # 测试标准JSON解析
    print("\n=== 测试标准JSON解析 ===")
    try:
        parsed = json.loads(info)
        print("标准JSON解析成功！")
    except json.JSONDecodeError as e:
        print(f"标准JSON解析失败: {e}")
        print(f"错误位置: {e.pos}")
        
        # 计算行列位置
        lines = info[:e.pos].split('\n')
        line_num = len(lines)
        col_num = len(lines[-1]) + 1 if lines else 1
        print(f"错误位置: 第{line_num}行第{col_num}列")
        
        if e.pos < len(info):
            problem_char = info[e.pos]
            print(f"问题字符: {repr(problem_char)}, ASCII: {ord(problem_char)}")
    
    # 测试增强的JSON解析（清理控制字符）
    print("\n=== 测试增强JSON解析（清理控制字符） ===")
    
    # 清理控制字符
    cleaned_info = ""
    for char in info:
        if ord(char) < 32 and char not in ['\t', '\n', '\r']:
            # 跳过控制字符
            continue
        cleaned_info += char
    
    print(f"清理前长度: {len(info)}")
    print(f"清理后长度: {len(cleaned_info)}")
    
    try:
        parsed = json.loads(cleaned_info)
        print("增强JSON解析成功！")
        return True
    except json.JSONDecodeError as e:
        print(f"增强JSON解析也失败: {e}")
        return False

if __name__ == '__main__':
    success = test_control_character_json()
    print(f"\n测试结果: {'成功' if success else '失败'}")
