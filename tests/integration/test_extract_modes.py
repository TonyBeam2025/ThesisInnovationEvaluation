#!/usr/bin/env python3
"""
测试新的批次抽取功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import subprocess
import sys
from pathlib import Path

def test_extract_modes():
    """测试不同的提取模式"""
    
    # 检查输入文件
    input_file = Path("data/input/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩.pdf")
    if not input_file.exists():
        print(f"❌ 测试文件不存在: {input_file}")
        return False
    
    print("🧪 测试extract命令的不同提取模式")
    print("=" * 50)
    
    # 测试模式配置
    test_configs = [
        {
            "name": "自动模式",
            "mode": "auto",
            "batch_size": 8000,
            "description": "系统自动选择最佳处理模式"
        },
        {
            "name": "全文模式", 
            "mode": "full-text",
            "batch_size": None,
            "description": "一次性处理整个文档"
        },
        {
            "name": "批次模式",
            "mode": "batch-sections", 
            "batch_size": 6000,
            "description": "按章节分批处理，每批6000字符"
        }
    ]
    
    results = []
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n📝 测试 {i}/3: {config['name']}")
        print(f"   描述: {config['description']}")
        
        # 构建命令
        cmd = [
            "uv", "run", "thesis-eval", "extract",
            str(input_file),
            "--format", "json",
            "--extraction-mode", config["mode"]
        ]
        
        if config["batch_size"]:
            cmd.extend(["--batch-size", str(config["batch_size"])])
        
        print(f"   命令: {' '.join(cmd[2:])}")  # 显示简化命令
        
        try:
            # 执行命令
            print("   🔄 执行中...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"    成功: {config['name']}")
                
                # 检查输出文件
                output_file = Path("data/output/基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩_extracted_info.json")
                if output_file.exists():
                    size = output_file.stat().st_size
                    print(f"   📄 输出文件: {size:,} 字节")
                    
                    # 备份当前结果文件
                    backup_file = output_file.with_name(f"{output_file.stem}_{config['mode']}{output_file.suffix}")
                    if backup_file.exists():
                        backup_file.unlink()
                    output_file.rename(backup_file)
                    print(f"   💾 备份为: {backup_file.name}")
                
                results.append({"config": config, "success": True, "output": result.stdout})
            else:
                print(f"   ❌ 失败: {config['name']}")
                print(f"   错误: {result.stderr[:200]}...")
                results.append({"config": config, "success": False, "error": result.stderr})
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ 超时: {config['name']} (5分钟)")
            results.append({"config": config, "success": False, "error": "超时"})
        except Exception as e:
            print(f"   💥 异常: {e}")
            results.append({"config": config, "success": False, "error": str(e)})
    
    # 显示测试总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    print(f"   总测试数: {total_count}")
    print(f"   成功数: {success_count}")
    print(f"   成功率: {(success_count/total_count)*100:.1f}%")
    
    if success_count > 0:
        print("\n 成功的模式:")
        for result in results:
            if result["success"]:
                config = result["config"]
                print(f"   - {config['name']} ({config['mode']})")
    
    if success_count < total_count:
        print("\n❌ 失败的模式:")
        for result in results:
            if not result["success"]:
                config = result["config"]
                print(f"   - {config['name']} ({config['mode']}): {result['error'][:50]}...")
    
    print(f"\n🎯 批次抽取功能测试完成!")
    print(f"💡 查看 data/output/ 目录中的备份文件来比较不同模式的结果")
    
    return success_count > 0

if __name__ == "__main__":
    success = test_extract_modes()
    sys.exit(0 if success else 1)
