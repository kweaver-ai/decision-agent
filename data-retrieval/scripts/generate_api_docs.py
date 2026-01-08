# -*- coding: utf-8 -*-
"""
生成 API 文档的独立脚本

用法:
    python scripts/generate_api_docs.py [output_path] [server_url]

参数:
    output_path: 输出文件路径，默认为 ../api.json
    server_url: 服务地址，默认为 http://data-retrieval:9100

示例:
    python scripts/generate_api_docs.py
    python scripts/generate_api_docs.py ./api.json http://localhost:9100
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 设置路径以便导入 data_retrieval 模块
current_file_path = Path(__file__).resolve()
src_dir = current_file_path.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from data_retrieval.tools.registry import ALL_TOOLS_MAPPING


class APIDocsGenerator:
    """API 文档生成器"""
    
    name: str = "基础结构化数据分析工具箱2"
    description: str = "支持对结构话数据进行处理的工具箱"
    prefix: str = "/tools"
    
    def __init__(self, tools_mapping: dict = None):
        self.tools_mapping = tools_mapping or ALL_TOOLS_MAPPING
    
    async def generate(self, server_url: str = "http://data-retrieval:9100") -> dict:
        """生成 API 文档
        
        Parameters:
            server_url: 服务地址
            
        Returns:
            符合 OpenAPI 3.0 规范的 API 文档
        """
        tools = list(self.tools_mapping.keys())
        
        # 构建工具描述
        if self.description:
            toolbox_desc = self.description + "，工具包含: \n"
        else:
            toolbox_desc = "工具包含: \n"
        
        for idx, tool_name in enumerate(tools):
            toolbox_desc += f"{idx + 1}. {tool_name}\n"
        
        # 构建基础 schema
        schemas = {
            "openapi": "3.0.3",
            "info": {
                "title": self.name,
                "description": toolbox_desc,
                "version": "1.0.11"
            },
            "servers": [
                {
                    "url": server_url
                }
            ],
            "paths": {}
        }
        
        # 获取每个工具的 schema
        for tool_name in tools:
            tool_cls = self.tools_mapping[tool_name]
            if hasattr(tool_cls, "get_api_schema"):
                try:
                    schema = await tool_cls.get_api_schema()
                    schemas["paths"][f"{self.prefix}/{tool_name}"] = schema
                    print(f"✓ 已生成 {tool_name} 的 API schema")
                except Exception as e:
                    print(f"✗ 生成 {tool_name} 的 API schema 失败: {e}")
            else:
                print(f"⚠ {tool_name} 没有 get_api_schema 方法，跳过")
        
        return schemas


async def main():
    # 解析命令行参数
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    server_url = sys.argv[2] if len(sys.argv) > 2 else "http://data-retrieval:9100"
    
    # 默认输出路径
    if output_path is None:
        output_path = Path(__file__).resolve().parent.parent / "api.json"
    else:
        output_path = Path(output_path)
    
    print(f"正在生成 API 文档...")
    print(f"服务地址: {server_url}")
    print(f"输出路径: {output_path}")
    print("-" * 50)
    
    # 生成文档
    generator = APIDocsGenerator()
    docs = await generator.generate(server_url=server_url)
    
    # 保存到文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=4)
    
    print("-" * 50)
    print(f"✓ API 文档已保存到: {output_path}")
    print(f"✓ 共生成 {len(docs['paths'])} 个工具的 API schema")


if __name__ == "__main__":
    asyncio.run(main())
