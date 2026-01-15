from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ZhipuSearchRequest(BaseModel):
    """智谱搜索请求"""

    query: str = Field(..., description="搜索查询词", example="机器学习")


class GetSchemaRequest(BaseModel):
    """获取模式请求"""

    database: str = Field(..., description="数据库名称", example="test_db")


class CheckRequest(BaseModel):
    """检查工具请求"""

    value: Any = Field(..., description="检查值", example="test_value")
    field: str = Field(..., description="检查字段", example="test_field")


class DocQARequest(BaseModel):
    """文档问答请求"""

    query: str = Field(..., description="查询问题", example="什么是机器学习？")
    props: Optional[Dict[str, Any]] = Field(default={}, description="额外属性")


class GraphQARequest(BaseModel):
    """图数据库问答请求"""

    query: str = Field(..., description="查询问题", example="查询所有用户")
    props: Optional[Dict[str, Any]] = Field(default={}, description="额外属性")


class FileInfo(BaseModel):
    """文件信息"""

    name: str = Field(..., description="文件名", example="document.pdf")
    id: str = Field(..., description="文件ID", example="file_123")

    class Config:
        # 允许额外的字段，不会报错
        extra = "allow"


class SearchFileSnippetsRequest(BaseModel):
    """搜索文件片段请求"""

    query: str = Field(..., description="搜索查询", example="如何预定会议室")
    file_infos: List[FileInfo] = Field(..., description="文件信息列表")
    llm: Optional[Dict[str, Any]] = Field(default={}, description="大模型配置")


class GetFileFullContentRequest(BaseModel):
    """获取文件完整内容请求"""

    file_infos: List[FileInfo] = Field(..., description="文件信息列表")
    strategy: str = Field(default="chunk", description="处理策略", example="chunk")
    llm: Optional[Dict[str, Any]] = Field(default={}, description="大模型配置")


class ProcessFileIntelligentRequest(BaseModel):
    """智能文件处理请求"""

    query: str = Field(..., description="用户查询", example="总结这份报告的主要内容")
    file_infos: List[FileInfo] = Field(..., description="文件信息列表")
    llm: Optional[Dict[str, Any]] = Field(default={}, description="大模型配置")


class GetFileDownloadUrlRequest(BaseModel):
    """获取文件下载URL请求"""

    file_infos: List[FileInfo] = Field(..., description="文件信息列表")


class OnlineSearchCiteRequest(BaseModel):
    """联网搜索添加引用请求"""

    query: str = Field(..., description="搜索查询词", example="机器学习")
    model_name: str = Field(..., description="模型名称", example="deepseek-v3")
    search_tool: str = Field(..., description="搜索工具", example="zhipu_search_tool")
    api_key: str = Field(
        ...,
        description="搜索工具的API KEY",
        example="18286",
    )
    user_id: str = Field(..., description="userid", example="bdb7")
    stream: bool = Field(default=False, description="是否流式返回", example=False)
