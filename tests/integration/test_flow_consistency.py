#!/usr/bin/env python3
"""
测试分析流程一致性
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

def test_flow_descriptions():
    """测试流程描述的一致性"""
    import re
    
    # 读取CLI文件
    with open('src/thesis_inno_eval/cli.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有流程描述
    step_patterns = [
        r'步骤\d+:.*',
        r'step \d+:.*',
    ]
    
    flow_sections = []
    
    # 查找主要流程描述部分
    lines = content.split('\n')
    in_flow = False
    current_flow = []
    current_context = ""
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 检测流程开始
        if '开始' in line and ('流程' in line or '分析' in line):
            if current_flow:
                flow_sections.append({
                    'context': current_context,
                    'steps': current_flow.copy()
                })
            current_flow = []
            current_context = line
            in_flow = True
        
        # 检测步骤
        elif in_flow and '步骤' in line and ':' in line:
            current_flow.append(line)
        
        # 检测流程结束
        elif in_flow and (line.startswith('try:') or line.startswith('except:') or 
                         line.startswith('if ') or line.startswith('else:') or
                         'papers_by_lang' in line):
            if current_flow:
                flow_sections.append({
                    'context': current_context,
                    'steps': current_flow.copy()
                })
                current_flow = []
            in_flow = False
    
    # 分析流程一致性
    print("🔍 分析流程描述一致性")
    print("="*50)
    
    issues = []
    
    for i, flow in enumerate(flow_sections):
        print(f"\n📋 流程 {i+1}: {flow['context']}")
        for j, step in enumerate(flow['steps']):
            print(f"   {step}")
        
        # 检查是否包含过时的描述
        full_text = ' '.join(flow['steps'])
        if 'Markdown格式' in full_text:
            issues.append(f"流程 {i+1} 仍然提到Markdown格式转换")
        
        if '转换为Markdown' in full_text:
            issues.append(f"流程 {i+1} 仍然提到转换为Markdown")
    
    print(f"\n📊 发现的问题:")
    if issues:
        for issue in issues:
            print(f"   ❌ {issue}")
    else:
        print("    所有流程描述都已正确更新")
    
    return len(issues) == 0

def test_markdown_references():
    """检查是否还有对markdown生成的引用"""
    import re
    
    with open('src/thesis_inno_eval/cli.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n🔍 检查markdown相关引用")
    print("="*50)
    
    # 检查可能的问题模式
    patterns = [
        (r'output_md_path', 'output_md_path参数引用'),
        (r'markdown.*生成', 'markdown生成描述'),
        (r'转换.*markdown', '转换为markdown描述'),
        (r'Markdown格式', 'Markdown格式提及'),
    ]
    
    issues = []
    
    for pattern, description in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            line_content = content.split('\n')[line_num-1].strip()
            
            # 排除注释、文档字符串和缓存管理代码
            if not (line_content.startswith('#') or '"""' in line_content or "'''" in line_content or
                   'cache' in line_content.lower() or 'glob' in line_content):
                issues.append({
                    'pattern': pattern,
                    'description': description,
                    'line': line_num,
                    'content': line_content
                })
    
    if issues:
        for issue in issues:
            print(f"   ❌ 第{issue['line']}行: {issue['description']}")
            print(f"      内容: {issue['content']}")
    else:
        print("    没有发现markdown相关的问题引用")
    
    return len(issues) == 0

if __name__ == '__main__':
    print("🧪 测试CLI流程一致性")
    print("="*60)
    
    # 测试流程描述
    flow_ok = test_flow_descriptions()
    
    # 测试markdown引用
    md_ok = test_markdown_references()
    
    print(f"\n📋 测试结果:")
    print(f"   流程描述: {' 正常' if flow_ok else '❌ 有问题'}")
    print(f"   Markdown引用: {' 已清理' if md_ok else '❌ 仍有引用'}")
    
    if flow_ok and md_ok:
        print("\n🎉 所有测试通过！分析流程已正确修正。")
    else:
        print("\n⚠️ 发现问题，需要进一步修正。")
