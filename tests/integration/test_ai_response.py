#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
import sys
sys.path.append('src')
from thesis_inno_eval.gemini_client import ConcurrentAIClient
from docx import Document

def extract_text_from_word(word_path):
    doc = Document(word_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def main():
    # 提取内容
    filepath = 'data/input/跨模态图像融合技术在医疗影像分析中的研究.docx'
    content = extract_text_from_word(filepath)
    test_content = content[:5000]  # 增加内容长度
    
    # 初始化客户端
    client = ConcurrentAIClient()
    
    # 构建详细提示词
    prompt = """请提取以下论文的详细结构化信息，以JSON格式返回。请尽可能详细地填写每个字段，包含具体的技术细节、实验数据、引用信息等：

{
  "ChineseTitle": "论文的完整中文标题",
  "EnglishTitle": "论文的完整英文标题", 
  "ChineseKeywords": "详细的中文关键词列表，包含技术术语",
  "EnglishKeywords": "详细的英文关键词列表，包含技术术语",
  "ChineseAbstract": "详细完整的中文摘要，包含研究背景、目标、方法、主要结果和结论，至少200字",
  "EnglishAbstract": "详细完整的英文摘要，包含所有关键信息",
  "Research Background": "详细的研究背景，包含当前技术现状、存在问题、研究动机",
  "Research Objectives": "具体的研究目标和要解决的问题", 
  "Research Methods": "详细的研究方法，包含技术路线、实验设计、算法描述",
  "Main Contributions": "主要创新点和贡献，包含技术突破和理论贡献",
  "Experimental Results": "详细的实验结果，包含数据分析和性能指标",
  "Conclusions": "详细的结论，包含研究成果总结和意义",
  "Future Work": "未来研究方向和改进建议",
  "References": "主要参考文献列表，包含作者、标题、期刊信息",
  "Technical Details": "详细的技术实现细节，包含算法、公式、参数设置"
}

论文内容：""" + test_content

    try:
        print('正在生成AI响应...')
        response_obj = client.send_message(prompt)
        ai_response = response_obj.content  # 获取响应内容
        print(f'AI响应长度: {len(ai_response)}')
        
        # 保存到文件以便检查
        with open('ai_response_debug.txt', 'w', encoding='utf-8') as f:
            f.write(ai_response)
        print('AI响应已保存到 ai_response_debug.txt')
        
        # 检查控制字符
        control_chars = []
        for i, char in enumerate(ai_response):
            if ord(char) < 32 and char not in ['\t', '\n', '\r']:
                control_chars.append((i, ord(char), repr(char)))
        
        print(f'发现 {len(control_chars)} 个控制字符:')
        for pos, code, char in control_chars[:20]:
            print(f'  位置{pos}: ASCII-{code} {char}')
        
        # 检查第8行第141字符位置
        lines = ai_response.split('\n')
        if len(lines) >= 8 and len(lines[7]) >= 141:
            char141 = lines[7][140]
            print(f'第8行第141字符: {repr(char141)}, ASCII: {ord(char141)}')
        
        # 尝试JSON解析
        import json
        try:
            json.loads(ai_response)
            print('JSON解析成功')
        except json.JSONDecodeError as e:
            print(f'JSON解析失败: {e}')
            print(f'错误位置: {e.pos}')
            if hasattr(e, 'lineno') and hasattr(e, 'colno'):
                print(f'错误行列: 第{e.lineno}行第{e.colno}列')
            
            # 显示错误位置附近的内容
            if e.pos < len(ai_response):
                start = max(0, e.pos - 50)
                end = min(len(ai_response), e.pos + 50)
                snippet = ai_response[start:end]
                print(f'错误位置附近内容: {repr(snippet)}')
                
                problem_char = ai_response[e.pos] if e.pos < len(ai_response) else 'EOF'
                if e.pos < len(ai_response):
                    print(f'问题字符: {repr(problem_char)}, ASCII: {ord(problem_char)}')
        
    except Exception as e:
        print(f'错误: {e}')

if __name__ == '__main__':
    main()
