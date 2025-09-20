#!/usr/bin/env python3
"""
演示论文结构化信息抽取功能
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """运行命令并显示输出"""
    print(f"🔄 执行命令: {' '.join(cmd)}")
    print("-" * 50)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    print(result.stdout)
    if result.stderr:
        print(f"❌ 错误: {result.stderr}")
    print("=" * 50)
    return result.returncode == 0

def main():
    print("📄 论文结构化信息抽取功能演示")
    print("=" * 50)
    
    # 1. 显示帮助信息
    print("\n1️⃣ 查看extract命令帮助:")
    run_command(['uv', 'run', 'thesis-eval', 'extract', '--help'])
    
    # 2. 显示可用的输入文件
    print("\n2️⃣ 查看可用的输入文件:")
    run_command(['uv', 'run', 'thesis-eval', 'files'])
    
    # 3. 提取单个文件的结构化信息（JSON格式）
    print("\n3️⃣ 提取论文结构化信息（JSON格式）:")
    input_file = "data/input/跨模态图像融合技术在医疗影像分析中的研究.docx"
    if Path(input_file).exists():
        success = run_command(['uv', 'run', 'thesis-eval', 'extract', input_file])
        if success:
            print(" JSON文件生成成功！")
        else:
            print("❌ JSON文件生成失败")
    else:
        print(f"❌ 文件不存在: {input_file}")
    
    # 4. 检查生成的文件
    print("\n4️⃣ 检查生成的extracted_info文件:")
    output_dir = Path("data/output")
    extracted_files = list(output_dir.glob("*extracted_info*"))
    if extracted_files:
        print("📁 找到以下extracted_info文件:")
        for file in extracted_files:
            print(f"  • {file.name} ({file.stat().st_size:,} 字节)")
    else:
        print("❌ 未找到extracted_info文件")
    
    # 5. 显示JSON文件内容预览
    if extracted_files:
        print(f"\n5️⃣ JSON文件内容预览 ({extracted_files[0].name}):")
        try:
            import json
            with open(extracted_files[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("📋 元数据:")
            metadata = data.get('metadata', {})
            for key, value in metadata.items():
                print(f"  • {key}: {value}")
            
            print("\n📄 抽取的字段:")
            extracted_info = data.get('extracted_info', {})
            for field, content in extracted_info.items():
                if content and str(content).strip():
                    content_preview = str(content)[:100] + "..." if len(str(content)) > 100 else str(content)
                    print(f"  • {field}: {content_preview}")
                else:
                    print(f"  • {field}: (空)")
                    
        except Exception as e:
            print(f"❌ 读取JSON文件失败: {e}")
    
    print(f"\n🎉 演示完成!")
    print(f"💡 使用方法:")
    print(f"   • 提取单个文件: uv run thesis-eval extract <文件路径>")
    print(f"   • 提取多个文件: uv run thesis-eval extract <文件1> <文件2> ...")
    print(f"   • 指定输出目录: uv run thesis-eval extract <文件> -o <输出目录>")
    print(f"   • 生成Markdown: uv run thesis-eval extract <文件> --format markdown")

if __name__ == '__main__':
    main()

