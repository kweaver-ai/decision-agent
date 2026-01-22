#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行所有自动化单元测试

使用方法:
    python tests/unit_tests/run_all_tests.py
    
    或者使用 uv:
    uv run python tests/unit_tests/run_all_tests.py
    
    或者使用 pytest:
    uv run python -m pytest tests/unit_tests/ -v
"""

import sys
import os
import time
import importlib.util

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# 测试模块列表
TEST_MODULES = [
    'test_prompts',
    'test_parsers',
    'test_sessions',
    'test_utils',
    'test_tools',
    'test_api',
    'test_settings',
    'test_tools_without_prompt_manager',
]


def load_test_module(module_name):
    """动态加载测试模块"""
    test_dir = os.path.dirname(__file__)
    module_path = os.path.join(test_dir, f"{module_name}.py")
    
    if not os.path.exists(module_path):
        return None
    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


def run_module_tests(module):
    """运行单个模块的测试"""
    if hasattr(module, 'run_tests'):
        return module.run_tests()
    return True


def main():
    """主函数"""
    print("=" * 70)
    print("  Data Retrieval 单元测试套件")
    print("=" * 70)
    print(f"\n开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试模块数: {len(TEST_MODULES)}")
    print("-" * 70)
    
    start_time = time.time()
    
    results = {}
    total_modules = 0
    passed_modules = 0
    
    for module_name in TEST_MODULES:
        print(f"\n{'#' * 70}")
        print(f"# 运行测试模块: {module_name}")
        print(f"{'#' * 70}")
        
        try:
            module = load_test_module(module_name)
            if module is None:
                print(f"⚠️  模块 {module_name} 未找到，跳过")
                results[module_name] = 'SKIPPED'
                continue
            
            total_modules += 1
            success = run_module_tests(module)
            
            if success:
                results[module_name] = 'PASSED'
                passed_modules += 1
            else:
                results[module_name] = 'FAILED'
                
        except Exception as e:
            print(f"❌ 模块 {module_name} 执行出错: {e}")
            results[module_name] = f'ERROR: {e}'
            total_modules += 1
    
    elapsed_time = time.time() - start_time
    
    # 打印总结
    print("\n")
    print("=" * 70)
    print("  测试总结")
    print("=" * 70)
    print(f"\n总模块数: {total_modules}")
    print(f"通过模块: {passed_modules}")
    print(f"失败模块: {total_modules - passed_modules}")
    print(f"总用时: {elapsed_time:.2f} 秒")
    
    print("\n模块详情:")
    print("-" * 50)
    for module_name, status in results.items():
        icon = "✅" if status == 'PASSED' else "⚠️" if status == 'SKIPPED' else "❌"
        print(f"  {icon} {module_name}: {status}")
    
    print("\n" + "=" * 70)
    
    if passed_modules == total_modules:
        print("🎉 所有测试通过！")
        return 0
    else:
        print(f"⚠️  有 {total_modules - passed_modules} 个模块测试失败")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
