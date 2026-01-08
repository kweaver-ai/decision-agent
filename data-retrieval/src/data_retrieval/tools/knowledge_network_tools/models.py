# -*- coding: utf-8 -*-
"""
知识网络工具的Pydantic数据模型

文件结构（从上到下）：
- 通用类型别名 / 通用基础模型
- 召回配置（概念/语义实例/属性过滤）
- 工具输入（KnowledgeNetworkRetrievalInput）
- Schema/概念召回输出（知识网络/对象类型/关系类型）
- FastAPI Header 依赖（HeaderParams）
- Rerank/查询理解（QueryUnderstanding / RerankInput）
"""

import uuid
from typing import Any, Dict, List, Optional, Union

from fastapi import Header
from pydantic import BaseModel, Field, model_validator, ConfigDict

# =========================================================
# 通用类型别名
# =========================================================


class KnowledgeNetworkIdConfig(BaseModel):
    """知识网络ID配置"""
    knowledge_network_id: str = Field(description="知识网络ID")


# =========================================================
# 召回配置（概念/语义实例/属性过滤）
# =========================================================

class SemanticInstanceRetrievalConfig(BaseModel):
    """
    语义实例召回配置参数
    
    用于控制语义实例召回（当不提供conditions参数时）的实例数据阈值和数量。
    """
    # 核心配置项
    initial_candidate_count: int = Field(
        default=50,
        ge=1,
        description="语义实例召回的初始召回数量上限（重排序前的候选数量）。作用阶段：基础召回阶段，在调用API时使用。作用：控制从知识网络API中初始召回多少个候选实例，这些候选实例会经过向量重排序后筛选出per_type_instance_limit个。建议值：一般设置为per_type_instance_limit的3-5倍，确保有足够的候选进行重排序。"
    )
    per_type_instance_limit: int = Field(
        default=5,
        ge=1,
        description="每个对象类型最终返回的实例数量上限（重排序后的数量）。作用阶段：基础召回阶段。作用范围：每个对象类型单独控制。例如：如果有3个对象类型，每个对象类型最多返回per_type_instance_limit个实例，总共最多返回3×per_type_instance_limit个实例。注意：此参数在基础模式和增强模式的基础召回阶段都会使用。"
    )

    # -----------------------------------------------------
    # 语义实例召回：字段（属性）语义筛选与查询条件控制（防止 sub_conditions 爆炸）
    # -----------------------------------------------------
    max_semantic_sub_conditions: int = Field(
        default=10,
        ge=1,
        le=100,
        description=(
            "语义实例召回构造查询条件时，sub_conditions 的最大数量上限（用于适配后端限制与控成本）。"
            "当字段很多/字段支持多种操作符时，系统会先用重排序模型对字段做语义打分，再按比例截断并分配条件，"
            "最终确保 sub_conditions 不超过该上限。默认10（与历史后端限制对齐）。"
        ),
    )
    semantic_field_keep_ratio: float = Field(
        default=0.2,
        ge=0.01,
        le=1.0,
        description="语义字段筛选保留比例（按重排序分数Top-K保留）。例如0.2表示保留前20%的字段。",
    )
    semantic_field_keep_min: int = Field(
        default=5,
        ge=1,
        le=200,
        description="语义字段筛选最少保留字段数（字段较少时兜底，避免过度截断）。",
    )
    semantic_field_keep_max: int = Field(
        default=15,
        ge=1,
        le=500,
        description="语义字段筛选最多保留字段数（字段很多时强力限流，避免条件/成本爆炸）。",
    )
    semantic_field_rerank_batch_size: int = Field(
        default=128,
        ge=1,
        le=1024,
        description="字段语义打分（rerank）时的批处理大小，字段数很大时会分批调用重排序服务。",
    )
    
    # 实例过滤配置参数（扁平化，直接放在semantic_instance_retrieval层级）
    # 过滤阈值
    min_direct_relevance: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="直接相关性最低阈值（0-1之间）。作用：过滤掉直接相关性分数低于此阈值的实例。直接相关性分数是使用Rerank模型计算的实例与查询的语义相似度。增大此值会过滤更严格，只保留高相关性实例；减小此值会过滤更宽松，保留更多实例。"
    )

    # -----------------------------------------------------
    # 语义实例召回：最终输出的全局分数过滤（抑制“强头部+弱尾巴”噪声）
    # -----------------------------------------------------
    enable_global_final_score_ratio_filter: bool = Field(
        default=True,
        description=(
            "是否启用“全局 final_score 相对阈值过滤”。"
            "启用后：在生成最终 nodes 之前，基于 rerank/增强过滤产生的 final_score 做一次全局过滤，"
            "仅保留满足 final_score >= max_final_score * global_final_score_ratio 的实例，"
            "用于在分数差距过大时抑制低质尾部噪声。"
        ),
    )
    global_final_score_ratio: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description=(
            "全局 final_score 相对阈值比例 r（0~1）。当启用 enable_global_final_score_ratio_filter 时，"
            "仅保留 final_score >= max_final_score * r 的实例。"
            "建议：0.2~0.35。"
        ),
    )
    exact_name_match_score: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description=(
            "多关键词检索场景下的实例名完全相等保底分（0~1）。"
            "当 query 被拆分为多个关键词时，只要任一关键词与 instance_name 完全相等，"
            "则会将该实例的基础语义分提升到该值，以避免被其他关键词（如症状词）稀释后丢失。"
            "建议：0.75~0.95。"
        ),
    )
    # enable_rerank 参数已移至外层 KnowledgeNetworkRetrievalInput，不再在 SemanticInstanceRetrievalConfig 中定义
    # 外层的 enable_rerank 参数会在 retrieval_tool.py 中传递到各个函数

    # 注意：返回格式（是否包含 instance_id/instance_name、是否保留主键字段）当前在实现中固定为"精简输出"，
    # 以减少与类型字段重复；如需改回可自行调整输出阶段的字段处理逻辑。
    
    @model_validator(mode='before')
    @classmethod
    def validate_candidate_limit(cls, values):
        """验证并自动调整initial_candidate_count，确保其大于等于per_type_instance_limit"""
        if isinstance(values, dict):
            initial_candidate_count = values.get('initial_candidate_count', 50)
            per_type_instance_limit = values.get('per_type_instance_limit', 10)
            if initial_candidate_count < per_type_instance_limit:
                # 自动调整initial_candidate_count为per_type_instance_limit，确保有足够的候选进行重排序
                values['initial_candidate_count'] = per_type_instance_limit
        return values


class InstancePropertyFilterConfig(BaseModel):
    """
    实例属性过滤配置（通用，适用于所有实例召回）
    
    用于控制实例属性字段的过滤，减少返回结果大小。
    """
    max_properties_per_instance: int = Field(
        default=20,
        ge=1,
        description="每个实例最多返回的属性字段数量。用于过滤实例属性，减少返回结果大小。"
    )
    max_property_value_length: int = Field(
        default=500,
        ge=1,
        description="属性值的最大长度（字符数），超过此长度的字段值会被过滤。"
    )
    enable_property_filter: bool = Field(
        default=False,
        description="是否启用实例属性过滤。如果为False，返回所有属性字段。"
    )


class ConceptRetrievalConfig(BaseModel):
    """
    概念召回/概念流程配置参数（原来散落在最外层的参数已收敛到这里）
    """
    top_k: int = Field(
        default=10,
        ge=1,
        description="概念召回返回最相关关系类型数量（对象类型会随关系类型自动过滤）。"
    )
    skip_llm: bool = Field(
        default=True,
        description="是否跳过LLM筛选相关关系类型，直接使用前top_k个关系类型（高召回/低成本）。"
    )
    return_union: bool = Field(
        default=False,
        description="概念召回多轮检索时是否返回并集。True返回所有轮次并集；False仅返回当前轮次增量（默认False）。"
    )
    include_sample_data: bool = Field(
        default=False,
        description="是否获取对象类型的样例数据。True会为每个召回对象类型获取一条样例数据（可能增加耗时/体积）。"
    )
    schema_brief: bool = Field(
        default=True,
        description="概念召回时是否返回精简schema。True仅返回必要字段（概念ID/名称/关系source&target），不返回大字段。"
    )
    enable_coarse_recall: bool = Field(
        default=True,
        description="是否在概念召回前启用对象/关系粗召回，用于在大规模知识网络中先裁剪候选集合。"
    )
    coarse_object_limit: int = Field(
        default=2000,
        ge=1,
        description="对象类型粗召回的最大返回数量，用于限制候选对象规模。"
    )
    coarse_relation_limit: int = Field(
        default=300,
        ge=1,
        description="关系类型粗召回的最大返回数量，用于限制候选关系规模。"
    )
    coarse_min_relation_count: int = Field(
        default=5000,
        ge=1,
        description="仅当知识网络内关系类型总数达到该阈值时才启用粗召回；小规模网络直接走精排流程。"
    )
    # 最终 schema 与 LLM 提示中属性裁剪配置：
    # - LLM 提示词属性TopK：始终使用 per_object_property_top_k / global_property_top_k 控制
    # - 最终 schema 返回属性TopK：仅在 schema_brief=True 且 enable_property_brief=True 时生效
    enable_property_brief: bool = Field(
        default=True,
        description="在 schema_brief=True 时，是否对返回的对象属性做相关性裁剪（每对象TopK，全局TopK）。"
    )
    per_object_property_top_k: int = Field(
        default=8,
        ge=1,
        description="属性裁剪时，每个对象类型最多保留的属性数量。生产环境建议值：8-10，适配表多、字段多的场景。"
    )
    global_property_top_k: int = Field(
        default=30,
        ge=1,
        description="属性裁剪时，全局最多保留的属性总数量。生产环境建议值：30-50，确保在多对象类型场景下保留足够的全局属性信息。"
    )
    # NOTE:
    # - 历史上通过 only_schema 控制“只返回 schema / 返回语义实例 nodes 二选一”
    # - 当前实现：schema 与语义实例解耦，schema 仍返回 object_types/relation_types，
    #   语义实例统一通过 nodes 返回，多轮由 return_union 控制并集/增量。


class RetrievalConfig(BaseModel):
    """
    召回配置参数类，用于控制不同类型的召回场景。
    
    结构说明：
    - concept_retrieval: 概念召回/概念流程配置（原最外层参数收敛）
    - semantic_instance_retrieval: 语义实例召回配置
    - property_filter: 实例属性过滤配置（通用，适用于所有实例召回）
    
    参数说明：
    - 如果semantic_instance_retrieval未配置，使用默认值
    - 如果property_filter未配置，使用默认值
    """
    # 概念召回配置
    concept_retrieval: Optional[ConceptRetrievalConfig] = Field(
        default=None,
        description="概念召回/概念流程配置参数。如果不提供，使用默认值。"
    )
    
    # 语义实例召回配置
    semantic_instance_retrieval: Optional[SemanticInstanceRetrievalConfig] = Field(
        default=None,
        description="语义实例召回配置参数。如果不提供，使用默认值。"
    )
    
    # 实例属性过滤配置（通用）
    property_filter: Optional[InstancePropertyFilterConfig] = Field(
        default=None,
        description="实例属性过滤配置。如果不提供，使用默认值。"
    )
    
    
    @model_validator(mode='before')
    @classmethod
    def compute_defaults(cls, values):
        """
        自动计算默认值和回退逻辑
        """
        if isinstance(values, dict):
            # 如果concept_retrieval未提供，创建默认配置
            if values.get('concept_retrieval') is None:
                values['concept_retrieval'] = ConceptRetrievalConfig()
            elif isinstance(values.get('concept_retrieval'), dict):
                values['concept_retrieval'] = ConceptRetrievalConfig(**values['concept_retrieval'])
            
            # 如果semantic_instance_retrieval未提供，创建默认配置
            if values.get('semantic_instance_retrieval') is None:
                values['semantic_instance_retrieval'] = SemanticInstanceRetrievalConfig()
            elif isinstance(values.get('semantic_instance_retrieval'), dict):
                # 如果是字典，转换为SemanticInstanceRetrievalConfig对象
                values['semantic_instance_retrieval'] = SemanticInstanceRetrievalConfig(**values['semantic_instance_retrieval'])
            
            # 如果property_filter未提供，创建默认配置
            if values.get('property_filter') is None:
                values['property_filter'] = InstancePropertyFilterConfig()
            elif isinstance(values.get('property_filter'), dict):
                # 如果是字典，转换为InstancePropertyFilterConfig对象
                values['property_filter'] = InstancePropertyFilterConfig(**values['property_filter'])
        
        return values

    def get_concept_config(self) -> ConceptRetrievalConfig:
        """获取概念召回配置"""
        return self.concept_retrieval or ConceptRetrievalConfig()
    
    def get_semantic_config(self) -> SemanticInstanceRetrievalConfig:
        """获取语义实例召回配置"""
        return self.semantic_instance_retrieval or SemanticInstanceRetrievalConfig()
    
    def get_property_filter_config(self) -> InstancePropertyFilterConfig:
        """获取属性过滤配置"""
        return self.property_filter or InstancePropertyFilterConfig()
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional['RetrievalConfig']:
        """
        从字典创建RetrievalConfig实例
        
        Args:
            data: 配置字典，如果为None则返回None
            
        Returns:
            RetrievalConfig实例或None
        """
        if data is None:
            return None
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式，用于向后兼容。
        
        Returns:
            配置字典
        """
        return self.model_dump(exclude_none=True)


# =========================================================
# 工具输入（HTTP/Tool 调用入参）
# =========================================================

class KnowledgeNetworkRetrievalInput(BaseModel):
    """知识网络检索工具输入参数"""
    query: str = Field(description="用户查询问题")
    enable_rerank: bool = Field(
        default=True,
        description="是否启用向量重排序。False时使用降级策略（粗召回分数、关键词匹配等）。适用于没有重排序模型的环境。"
    )
    kn_ids: List[KnowledgeNetworkIdConfig] = Field(description="指定的知识网络配置列表，必须传递，每个配置包含knowledge_network_id字段")
    session_id: Optional[str] = Field(
        default=None, 
        description="会话ID，用于维护多轮对话存储的历史召回记录。如果不提供，将自动生成一个随机ID"
    )
    additional_context: Optional[str] = Field(
        default=None, 
        description="""
        当需要多轮召回使用，当第一轮召回的结果，用于下游任务时，发现错误，或查不到信息，就需要将问题query进行重写，
        然后额外提供对召回有任何帮助的上下文信息，越丰富越好"""
    )
    retrieval_config: Optional[RetrievalConfig] = Field(
        default=None,
        description="""
        召回配置参数，用于控制不同类型的召回场景。
        可以传入RetrievalConfig对象或字典（Pydantic会自动将字典转换为RetrievalConfig对象）。
        如果不提供，将使用系统默认配置。
        
        配置结构：
        {
          "semantic_instance_retrieval": {
            "initial_candidate_count": 50,          // 语义召回的初始召回数量
            "per_type_instance_limit": 10,          // 每个对象类型最终返回的实例数量
            "min_direct_relevance": 0.3,             // 直接相关性最低阈值
          },
          "property_filter": {
            "max_properties_per_instance": 20,  // 每个实例最多返回的属性数量（可选）
            "max_property_value_length": 500,   // 属性值最大长度（可选）
            "enable_property_filter": true      // 是否启用属性过滤（可选）
          }
        }
        
        使用示例（HTTP API JSON格式）：
        {
          "retrieval_config": {
            "semantic_instance_retrieval": {
              "initial_candidate_count": 50,
              "per_type_instance_limit": 10
            }
          }
        }
        
        注意：
        - 概念召回参数已收敛到 retrieval_config.concept_retrieval
        """
    )
    only_schema: bool = Field(
        default=False,
        description="是否只召回概念（schema），不召回语义实例。如果为True，则只返回object_types和relation_types，不返回nodes。默认为False。"
    )
    
    def __init__(self, **data):
        # session_id 处理策略：
        # - 未提供或提供空串，都视为需要自动生成会话ID（保持有状态能力）
        # - 提供非空 session_id 则按传入值使用
        provided_session_id = "session_id" in (data or {})
        super().__init__(**data)
        if not self.session_id:
            # 包含：未传、传 None、传空串
            self.session_id = f"auto_session_{uuid.uuid4().hex[:16]}"

    model_config = ConfigDict(extra="forbid")


# =========================================================
# Schema/概念召回输出（知识网络/对象类型/关系类型）
# =========================================================

class KnowledgeNetworkInfo(BaseModel):
    """知识网络信息"""
    id: str = Field(description="知识网络ID")
    name: str = Field(description="知识网络名称")
    comment: str = Field(description="知识网络描述")
    tags: List[str] = Field(description="标签")


class ObjectTypeInfo(BaseModel):
    """对象类型信息"""
    id: str = Field(description="对象类型ID")
    name: str = Field(description="对象类型名称")
    comment: str = Field(description="对象类型描述")


class RelationTypeInfo(BaseModel):
    """关系类型信息"""
    id: str = Field(description="关系类型ID")
    name: str = Field(description="关系类型名称")
    comment: str = Field(description="关系类型描述")
    source_object_type_id: str = Field(description="源对象类型ID")
    target_object_type_id: str = Field(description="目标对象类型ID")


class KnowledgeNetworkRetrievalResult(BaseModel):
    """知识网络检索结果"""
    concept_type: str = Field(description="概念类型: object_type 或 relation_type")
    concept_id: str = Field(description="概念ID")
    concept_name: str = Field(description="概念名称")
    comment: Optional[str] = Field(default=None, description="概念描述（对象/关系）")
    source_object_type_id: Optional[str] = Field(default=None, description="源对象类型ID（仅关系类型有）")
    target_object_type_id: Optional[str] = Field(default=None, description="目标对象类型ID（仅关系类型有）")
    data_properties: Optional[List[Dict[str, Any]]] = Field(default=None, description="对象属性列表（仅对象类型有），对象类型返回列表，关系类型不包含此字段")
    logic_properties: Optional[List[Dict[str, Any]]] = Field(default=None, description="逻辑属性列表（仅对象类型有），非精简模式返回")
    primary_keys: Optional[List[str]] = Field(default=None, description="主键字段列表（仅对象类型有，支持多个主键）")
    sample_data: Optional[Dict[str, Any]] = Field(default=None, description="样例数据（仅对象类型有），当include_sample_data=True时返回，展示对象类型的实际数据样例")


class KnowledgeNetworkRetrievalResponse(BaseModel):
    """知识网络检索响应"""
    object_types: List[KnowledgeNetworkRetrievalResult] = Field(description="对象类型列表，包含属性信息")
    relation_types: List[KnowledgeNetworkRetrievalResult] = Field(description="关系类型列表")
    action_types: Optional[List[Dict[str, Any]]] = Field(default=None, description="操作类型列表")
    # 兼容字段：历史语义实例召回会返回 nodes/message（不返回 schema）
    nodes: Optional[List[Dict[str, Any]]] = Field(default=None, description="语义实例召回扁平节点列表（兼容历史输出）")
    message: Optional[str] = Field(default=None, description="提示信息（例如未召回到实例数据）")


# =========================================================
# FastAPI Header 依赖（路由入参）
# =========================================================

class HeaderParams:
    """请求头参数依赖类"""
    
    def __init__(
        self,
        # x_user: str = Header(None, alias="x-user"),
        account_type: str = Header(..., alias="x-account-type"),
        account_id: str = Header(..., alias="x-account-id"),
        content_type: str = Header("application/json"),
        # 如果有其他 headers 参数，可以继续添加在这里
        # authorization: Optional[str] = Header(None),
        # user_agent: Optional[str] = Header(None),
    ):
        self.content_type = content_type
        self.account_type = account_type
        self.account_id = account_id
            # self.authorization = authorization
        # self.user_agent = user_agent


class QueryUnderstanding(BaseModel):
    """查询理解结果"""
    origin_query: str = Field(description="原始查询")
    processed_query: str = Field(description="处理后的查询")
    intent: Optional[List[Dict[str, Any]]] = Field(default=[], description="意图列表")


class RerankInput(BaseModel):
    """重排序输入参数"""
    query_understanding: QueryUnderstanding = Field(description="查询理解结果")
    concepts: List[Dict[str, Any]] = Field(description="需要重排序的概念列表")
    action: str = Field(default="llm", description="重排序方法，可选值: 'llm' 或 'vector'")
    batch_size: Optional[int] = Field(default=128, description="批处理大小，可选")