import json
import time
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

from fastapi import APIRouter, Header, Depends
from sse_starlette import EventSourceResponse

from app.common.config import Config
from app.common.stand_log import StandLogger
from app.domain.enum.common.user_account_header_key import set_user_account_id
from app.router.agent_controller_pkg.dependencies import (
    get_account_id,
    get_biz_domain_id,
)
from app.models.tool_requests import (
    DocQARequest,
    GetFileDownloadUrlRequest,
    GetFileFullContentRequest,
    GraphQARequest,
    ProcessFileIntelligentRequest,
    SearchFileSnippetsRequest,
    ZhipuSearchRequest,
    OnlineSearchCiteRequest,
)
from app.models.tool_responses import (
    FileUrlInfo,
    GetFileDownloadUrlResponse,
    OnlineSearchCiteResponse,
    ZhipuSearchResponse,
)


router = APIRouter(prefix=Config.app.host_prefix + "/tools", tags=["internal-tools"])


@asynccontextmanager
async def _track_processing_time(operation_name: str):
    """跟踪操作处理时间的上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        processing_time = time.time() - start_time
        StandLogger.info(f"{operation_name}耗时: {processing_time}秒")


def _build_request_headers(
    account_id: Optional[str], token: Optional[str]
) -> Dict[str, str]:
    """构建请求头"""
    headers: Dict[str, str] = {}
    if account_id:
        set_user_account_id(headers, account_id)
    if token:
        headers["token"] = token
    return headers


@router.post("/graph_qa", summary="图数据库问答")
async def graph_qa(request: GraphQARequest):
    """
    基于图数据库的问答

    - **query**: 查询问题
    - **props**: 额外属性（可选）

    返回问答结果
    """
    from app.logic.tool.graph_qa_tool import graph_qa_tool

    param = request.model_dump()
    res = await graph_qa_tool(param["query"], param.get("props", {}))

    return {
        "result": res.get("text", ""),
        "full_result": res,
    }


@router.post("/doc_qa", summary="文档问答")
async def doc_qa(request: DocQARequest):
    """
    基于文档的问答

    - **query**: 查询问题
    - **props**: 额外属性（可选）

    返回问答结果
    """
    from app.logic.tool.doc_qa_tool import doc_qa_tool

    param = request.model_dump()
    props = param.get("props", {})
    data_source = props.get("data_source", {})
    res = await doc_qa_tool(param["query"], props)

    # 文档元信息也返回，用于前端展示用（关联bug：777725）
    res["data_source"] = data_source

    return {
        "result": res.get("text", ""),
        "full_result": res,
    }


@router.post(
    "/zhipu_search_tool", response_model=ZhipuSearchResponse, summary="智谱搜索"
)
async def zhipu_search(
    request: ZhipuSearchRequest,
    api_key: str = Header(..., description="智谱API密钥", alias="api_key"),
) -> ZhipuSearchResponse:
    """
    执行智谱搜索

    - **query**: 搜索查询词

    返回搜索结果内容
    """
    from app.logic.tool.zhipu_search_tool import zhipu_search_tool

    param = request.model_dump()
    res = await zhipu_search_tool(param, {"api_key": api_key}, None, None, None)

    return ZhipuSearchResponse(**res)


# ==================== 文件处理工具 ====================


@router.post("/search_file_snippets", summary="搜索文件片段")
async def search_file_snippets(
    request: SearchFileSnippetsRequest,
    account_id: Optional[str] = Depends(get_account_id),
    biz_domain_id: Optional[str] = Depends(get_biz_domain_id),
    token: Optional[str] = Header(None, description="用户令牌"),
) -> str:
    """
    从文件中搜索与查询相关的片段

    - **query**: 搜索查询（如"如何预定会议室"）
    - **file_infos**: 文件信息列表
    - **llm**: 大模型配置（可选）

    返回与查询相关的文件片段内容
    """
    from app.logic.tool.parse_temporary_file import search_file_snippets

    async with _track_processing_time("搜索文件片段"):
        headers = _build_request_headers(account_id, token)
        content = await search_file_snippets(
            request.query, [file.model_dump() for file in request.file_infos], headers
        )

    return content


@router.post(
    "/get_file_full_content",
    summary="获取文件完整内容",
)
async def get_file_full_content(
    request: GetFileFullContentRequest,
    account_id: Optional[str] = Depends(get_account_id),
    biz_domain_id: Optional[str] = Depends(get_biz_domain_id),
    token: Optional[str] = Header(None, description="用户令牌"),
) -> str:
    """
    获取文件的完整内容，支持长文本处理策略

    - **file_infos**: 文件信息列表
    - **strategy**: 处理策略（"truncate"截断 或 "chunk"分块总结）
    - **llm**: 大模型配置（用于分块总结）

    返回文件的完整内容或总结内容
    """
    from app.logic.tool.parse_temporary_file import get_file_full_content

    async with _track_processing_time("获取文件完整内容"):
        headers = _build_request_headers(account_id, token)
        content = await get_file_full_content(
            [file.model_dump() for file in request.file_infos],
            headers,
            request.llm,
            request.strategy,
        )

    return content


@router.post(
    "/process_file_intelligent",
    summary="智能文件处理",
)
async def process_file_intelligent(
    request: ProcessFileIntelligentRequest,
    account_id: Optional[str] = Depends(get_account_id),
    biz_domain_id: Optional[str] = Depends(get_biz_domain_id),
    token: Optional[str] = Header(None, description="用户令牌"),
) -> str:
    """
    智能文件处理策略，自动选择召回或全文策略

    - **query**: 用户查询（如"总结这份报告的主要内容"）
    - **file_infos**: 文件信息列表
    - **llm**: 大模型配置（用于意图识别和分块总结）

    根据查询意图自动选择处理策略，返回处理结果
    """
    from app.logic.tool.parse_temporary_file import (
        process_file_with_intelligent_strategy,
    )

    async with _track_processing_time("智能文件处理"):
        headers = _build_request_headers(account_id, token)
        content = await process_file_with_intelligent_strategy(
            request.query,
            [file.model_dump() for file in request.file_infos],
            headers,
            request.llm,
        )

    return content


@router.post(
    "/get_file_download_url",
    response_model=GetFileDownloadUrlResponse,
    summary="获取文件下载URL",
)
async def get_file_download_url(
    request: GetFileDownloadUrlRequest,
    account_id: Optional[str] = Depends(get_account_id),
    biz_domain_id: Optional[str] = Depends(get_biz_domain_id),
    token: Optional[str] = Header(None, description="用户令牌"),
) -> GetFileDownloadUrlResponse:
    """
    获取文件的下载URL链接

    - **file_infos**: 文件信息列表

    返回每个文件的下载URL，其他人可以通过这些URL获取文件内容
    """
    from app.logic.tool.parse_temporary_file import get_file_download_url

    async with _track_processing_time("获取文件下载URL"):
        headers = _build_request_headers(account_id, token)
        file_urls_data = await get_file_download_url(
            [file.model_dump() for file in request.file_infos], headers
        )

    success_count = sum(1 for item in file_urls_data if item["error"] is None)

    file_urls = [
        FileUrlInfo(
            name=item["name"], id=item["id"], url=item["url"], error=item["error"]
        )
        for item in file_urls_data
    ]

    return GetFileDownloadUrlResponse(
        file_urls=file_urls,
        total_count=len(request.file_infos),
        success_count=success_count,
    )


from sse_starlette import EventSourceResponse


@router.post(
    "/online_search_cite_tool",
    response_model=OnlineSearchCiteResponse,
    summary="联网搜索添加引用工具",
)
async def online_search_cite_tool(
    request: OnlineSearchCiteRequest,
) -> OnlineSearchCiteResponse:
    """
    执行联网搜索并添加引用

    - **query**: 搜索查询词
    - **model_name**: 模型名称
    - **search_tool**: 搜索工具
    - **api_key**: 搜索工具API密钥
    - **user_id**: 用户id
    返回搜索结果内容
    """
    headers = {"x-account-id": request.user_id}
    if not request.stream:
        from app.logic.tool.online_search_cite_tool import online_search_cite_tool

        param = request.model_dump()
        res = await online_search_cite_tool(request=param, headers=headers)

        return OnlineSearchCiteResponse(**res)
    else:
        param = request.model_dump()

        async def generate_stream():
            from app.logic.tool.online_search_cite_tool import (
                get_answer,
                get_completion_stream,
                get_search_results,
            )

            search_results = await get_search_results(param, headers)
            final_references = []
            ref_list = search_results["choices"][0]["message"]["tool_calls"][1][
                "search_result"
            ]
            for index, ref in enumerate(ref_list):
                ref_item = {
                    "title": ref.get("title", "未知标题"),
                    "content": ref.get("content", ""),
                    "link": ref.get("link", ""),
                    "index": index,
                }
                final_references.append(ref_item)

            full_answer = ""
            current_response = OnlineSearchCiteResponse(
                answer=full_answer,
                references=final_references,
            )
            yield f"{json.dumps(current_response.model_dump(), ensure_ascii=False)}"

            answer, _ = await get_answer(param, headers, search_results)

            async for chunk in get_completion_stream(
                param, headers, answer, final_references
            ):
                full_answer += chunk
                current_response = OnlineSearchCiteResponse(
                    answer=full_answer,
                    references=final_references,
                )
                yield f"{json.dumps(current_response.model_dump(), ensure_ascii=False)}"

        return EventSourceResponse(generate_stream(), ping=3600)
