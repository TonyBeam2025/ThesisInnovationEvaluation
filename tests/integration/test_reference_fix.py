#!/usr/bin/env python3
"""
测试修复后的智能参考文献提取器
专门测试[5895]异常编号问题
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.smart_reference_extractor import SmartReferenceExtractor

def test_reference_extraction():
    """测试参考文献提取功能"""
    
    # 模拟问题文本：包含正常参考文献和错误识别的期刊号
    test_text = """
# 参考文献

[178] Wang S., Wang D., Su L., et al. Realizing synergistic optimization of thermoelectric properties in n-type BiSbSe3 polycrystals via co-doping zirconium and halogen [J]. Materials Today Physics, 2022, 22: 100608
[179] Wang S., Xiao Y., Ren D., et al. Enhancing thermoelectric performance of BiSbSe3 through improving carrier mobility via percolating carrier transports [J]. Journal of Alloys and Compounds, 2020, 836: 155473

攻读博士学位期间取得的研究成果
[4] Bell L. E. Cooling, heating, generating power, and recovering waste heat with thermoelectric systems [J]. Science, 2008, 321 (5895): 1457-1461
[5] Kraemer D., Jie Q., McEnaney K., et al. Concentrating solar thermoelectric generators with a peak efficiency of 7.4% [J]. Nature Energy, 2016, 1 (11): 16153
"""
    
    print("🧪 测试智能参考文献提取器修复...")
    print("="*60)
    
    # 初始化提取器
    extractor = SmartReferenceExtractor()
    
    # 提取参考文献
    references, stats = extractor.extract_references(test_text, source_format='docx')
    
    print(f"\n📊 提取结果:")
    print(f"提取到 {len(references)} 条参考文献")
    if 'processing_time' in stats:
        print(f"处理时间: {stats['processing_time']:.2f}秒")
    if 'method_used' in stats:
        print(f"使用方法: {stats['method_used']}")
    
    print(f"\n📖 参考文献列表:")
    for i, ref in enumerate(references, 1):
        print(f"{i:2d}. {ref}")
    
    # 验证修复效果
    print(f"\n 修复验证:")
    has_5895 = any('[5895]' in ref for ref in references)
    has_179 = any('[179]' in ref for ref in references)
    
    if not has_5895:
        print(" 成功修复: 未发现错误的[5895]编号")
    else:
        print("❌ 修复失败: 仍然包含错误的[5895]编号")
    
    if has_179:
        print(" 正确保留: 找到最后一条参考文献[179]")
    else:
        print("❌ 意外丢失: 缺少最后一条参考文献[179]")
    
    # 检查编号连续性
    numbers = []
    for ref in references:
        match = extractor._extract_number(ref)
        if match != 999999:
            numbers.append(match)
    
    if numbers:
        numbers.sort()
        print(f"参考文献编号范围: {min(numbers)} - {max(numbers)}")
        
        # 查找可能的问题
        gaps = []
        for i in range(len(numbers)-1):
            if numbers[i+1] - numbers[i] > 1:
                gaps.append((numbers[i], numbers[i+1]))
        
        if gaps:
            print(f"编号间隔: {gaps}")
        else:
            print("编号连续性:  连续")

if __name__ == "__main__":
    test_reference_extraction()
