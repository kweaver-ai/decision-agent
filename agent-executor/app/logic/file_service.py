import datetime
import hashlib
import re
from io import StringIO
from typing import List, Dict, Any

from fastapi import UploadFile
from tika import parser

from app.common import errors
from app.common.errors import CodeException
from app.common.stand_log import StandLogger
from app.driven.ad.model_factory_service import model_factory_service
from app.driven.anyshare.docset_service import docset_service
from app.driven.infrastructure.opensearch import opensearch_engine
from app.utils.regex_rules import RegexPatterns


# opensearch中存储文件全文的索引名
FILE_INDEX_NAME = "agent_temp_files_full_text"


class FileService(object):
    """文件服务类，处理文件上传、删除、内容获取等操作"""

    def __init__(self):
        self.file_index_name = FILE_INDEX_NAME

    async def upload_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        上传文件

        Args:
            file: 上传的文件对象

        Returns:
            包含文件ID、名称、大小和token数量的字典

        Raises:
            CodeException: 文件解析失败时抛出
        """
        file_size = file.size
        file_name = file.filename
        file_bytes = await file.read()
        file_md5 = hashlib.md5(file_bytes).hexdigest()

        parsed = parser.from_buffer(file_bytes)
        if parsed.get("content") is None:
            raise CodeException(errors.AgentExecutor_File_ParseError())

        file_content = parsed["content"].strip()
        file_token_size = int(len(file_content) / 1.5)

        await self._ensure_index_exists()
        await self._save_to_opensearch(
            file_name, file_md5, file_content, file_token_size
        )

        return {
            "id": file_md5,
            "name": file_name,
            "size": file_size,
            "token_size": file_token_size,
        }

    async def _ensure_index_exists(self) -> None:
        """确保OpenSearch索引存在，不存在则创建"""
        if await opensearch_engine.is_index_exists(self.file_index_name):
            return

        index_body = {
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": {
                "properties": {
                    "upload_time": {"type": "date"},
                    "content": {"type": "text"},
                    "doc_name": {"type": "text"},
                    "doc_md5": {"type": "keyword"},
                    "token_size": {"type": "integer"},
                }
            },
        }
        await opensearch_engine.create_index(self.file_index_name, index_body)

    async def _save_to_opensearch(
        self, file_name: str, file_md5: str, file_content: str, file_token_size: int
    ) -> None:
        """保存文件内容到OpenSearch"""
        body = {
            "doc_name": file_name,
            "doc_md5": file_md5,
            "content": file_content,
            "token_size": file_token_size,
            "upload_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }
        await opensearch_engine.insert_data(self.file_index_name, body, doc_id=file_md5)

    async def delete_temp_file(self) -> None:
        """删除24小时前的临时文件"""
        delete_time = datetime.datetime.now() - datetime.timedelta(days=1)
        delete_time_str = delete_time.strftime("%Y-%m-%dT%H:%M:%S")
        delete_body = {
            "query": {
                "range": {
                    "upload_time": {
                        "lt": delete_time_str,
                    }
                }
            }
        }
        await opensearch_engine.delete_by_query(self.file_index_name, delete_body)

    async def check_token_num(self, file_ids: List[str], agent_config: Dict[str, Any]) -> str:
        """
        判断大模型是否可以处理文件的所有内容，如果不能，则返回提示信息

        Args:
            file_ids: 文件ID列表
            agent_config: Agent配置字典

        Returns:
            空字符串表示可以处理，否则返回提示信息
        """
        file_var_name = self._get_file_variable_name(agent_config)
        if not file_var_name:
            StandLogger.info("agent配置中不存在文件变量，无法判断文件是否可以处理")
            return ""

        llm_names = self._get_llm_names_using_file(agent_config, file_var_name)
        if not llm_names:
            StandLogger.info("agent配置中不存在大模型，无法判断文件是否可以处理")
            return ""

        context_size = await self._get_min_context_size(llm_names)
        if context_size == 0:
            StandLogger.info(
                "大模型配置中不存在max_tokens_length，无法判断文件是否可以处理"
            )
            return ""

        return await self._check_file_tokens_fit(file_ids, context_size)

    def _get_file_variable_name(self, agent_config: Dict[str, Any]) -> str:
        """从agent配置中获取文件变量名"""
        for input_field in agent_config.get("input", {}).get("fields", []):
            if input_field.get("type") == "file":
                return input_field.get("name", "")
        return ""

    def _get_llm_names_using_file(self, agent_config: Dict[str, Any], file_var_name: str) -> set:
        """获取agent配置中使用了文件的大模型名称集合"""
        llm_names = set()
        for block in agent_config.get("logic_block", []):
            if block.get("type") != "llm_block":
                continue

            para_list = self._extract_parameters_from_block(block)
            if file_var_name in para_list:
                llm_config = block.get("llm_config", {})
                llm_name = llm_config.get("llm_model_name") or llm_config.get("name", "")
                if llm_name:
                    llm_names.add(llm_name)

        return llm_names

    def _extract_parameters_from_block(self, block: Dict[str, Any]) -> List[str]:
        """从LLM块中提取参数列表"""
        if block.get("mode") == "expert":
            para_list = re.findall(
                RegexPatterns.Simple_variable_with_dollar_sign,
                block.get("dolphin", [])[0]["value"],
            )
        else:
            para_list = re.findall(
                RegexPatterns.Variable_in_curly_braces,
                block.get("user_prompt", ""),
            )
            para_list.extend(
                re.findall(
                    RegexPatterns.Variable_in_curly_braces,
                    block.get("system_prompt", ""),
                )
            )
        return para_list

    async def _get_min_context_size(self, llm_names: set) -> int:
        """获取多个LLM中最小的上下文大小"""
        context_size = 0
        for llm_name in llm_names:
            try:
                llm_config = await model_factory_service.get_llm_config(llm_name)
                max_tokens_length = llm_config["max_tokens_length"]
            except Exception:
                max_tokens_length = 0

            if context_size == 0:
                context_size = max_tokens_length
            else:
                context_size = min(context_size, max_tokens_length)

        return context_size

    async def _check_file_tokens_fit(self, file_ids: List[str], context_size: int) -> str:
        """检查文件token数量是否适合LLM上下文"""
        supported_files_tokens = context_size / 2

        docs = await opensearch_engine.get_doc_by_ids(self.file_index_name, file_ids)
        file_tokens = sum(doc.get("_source", {}).get("token_size", 0) for doc in docs)

        if file_tokens < supported_files_tokens:
            StandLogger.info("文件token数量小于大模型支持的最大token数量，可以处理")
            return ""

        return "仅阅读全部文件的{}%，请删减后运行".format(
            int(supported_files_tokens / file_tokens * 100)
        )

    async def get_file_content(self, file_infos: List[Dict[str, Any]], headers: Dict[str, Any]) -> None:
        """
        获取文件内容，修改 file_infos，在其中加上 content 字段

        支持的文件源类型：
        - "as": AnyShare 文件系统
        - "local": 本地临时文件

        Args:
            file_infos: 文件信息列表，会被原地修改添加 content 字段
            headers: 请求头信息
        """
        StandLogger.info_log("开始获取文件内容")

        for file_info in file_infos:
            file_source = file_info.get("file_source")
            if file_source == "as":
                await self._get_as_file_content(file_info)
            elif file_source == "local":
                await self._get_local_file_content(file_info)

        StandLogger.info_log("获取文件内容结束")

    async def _get_as_file_content(self, file_info: Dict[str, Any]) -> None:
        """获取AnyShare文件内容"""
        for doc in file_info.get("fields", []):
            if doc.get("content") is not None:
                continue

            doc_id = doc["source"].split("/")[-1]
            file_content = await docset_service.get_full_text(doc_id)
            doc["content"] = file_content

    async def _get_local_file_content(self, file_info: Dict[str, Any]) -> None:
        """获取本地文件内容"""
        if file_info.get("content") is not None:
            return

        file_content = await opensearch_engine.get_doc_by_ids(
            self.file_index_name, [file_info.get("id", "")]
        )
        if file_content:
            file_info["content"] = file_content[0].get("_source", {}).get("content", "")

    async def get_file_content_text(self, file_infos: List[Dict[str, Any]], headers: Dict[str, Any]) -> str:
        """
        获取文件内容，返回文件内容字符串

        Args:
            file_infos: 文件信息列表
            headers: 请求头信息

        Returns:
            所有文件内容拼接的字符串
        """
        await self.get_file_content(file_infos, headers)
        file_content = StringIO()

        for file_info in file_infos:
            if file_info.get("file_source") == "as":
                for doc in file_info.get("fields", []):
                    file_content.write(doc.get("content", ""))
            elif file_info.get("file_source") == "local":
                file_content.write(file_info.get("content", ""))

        return file_content.getvalue()

    async def get_file_content_text_with_name(self, file_infos: List[Dict[str, Any]], headers: Dict[str, Any]) -> str:
        """
        获取文件内容，返回文件内容字符串，包含文件名

        Args:
            file_infos: 文件信息列表
            headers: 请求头信息

        Returns:
            所有文件内容（含文件名）拼接的字符串
        """
        await self.get_file_content(file_infos, headers)
        file_content = StringIO()

        for file_info in file_infos:
            if file_info.get("file_source") == "as":
                for doc in file_info.get("fields", []):
                    file_content.write(
                        f"《{doc.get('name', '')}》全文：\n{doc.get('content', '')}\n\n"
                    )
            elif file_info.get("file_source") == "local":
                file_content.write(
                    f"《{file_info.get('name', '')}》全文：\n{file_info.get('content', '')}\n\n"
                )

        return file_content.getvalue()


file_service = FileService()
