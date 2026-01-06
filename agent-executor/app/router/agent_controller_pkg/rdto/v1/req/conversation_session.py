# -*- coding:utf-8 -*-
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator

from app.domain.vo.agentvo import AgentConfigVo


class ConversationSessionAction(str, Enum):
    """对话Session操作类型"""

    CREATE = "create"
    GET_INFO_OR_CREATE = "get_info_or_create"
    EXTEND_LIFETIME = "extend_lifetime"


class ConversationSessionManageReq(BaseModel):
    """对话Session管理请求

    至少需要提供agent_id或agent_config之一
    agent_config优先级高于agent_id
    """

    action: ConversationSessionAction = Field(
        ...,
        description="操作类型: get_info_or_create(获取或创建), extend_lifetime(延长有效期)",
    )

    agent_id: Optional[str] = Field(
        None,
        description="Agent ID，与agent_config二选一，agent_config优先",
        json_schema_extra={"example": "xxx"},
    )

    agent_version: Optional[str] = Field(
        default=None,
        title="agent_version",
        description="agent版本号,与agent_id配合使用",
        json_schema_extra={"example": "latest"},
    )

    agent_config: Optional[AgentConfigVo] = Field(
        None, description="Agent配置，与agent_id二选一，优先级更高"
    )

    @model_validator(mode="after")
    def validate_agent_params(self) -> "ConversationSessionManageReq":
        """验证agent_id和agent_config至少有一个"""
        if not self.agent_id and not self.agent_config:
            raise ValueError("agent_id和agent_config至少需要提供一个")

        if self.agent_id and not self.agent_version:
            raise ValueError("当agent_id提供时，agent_version不能为空")

        return self


# 保留旧的类名以兼容
ConversationSessionInitReq = ConversationSessionManageReq
