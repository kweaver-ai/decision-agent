"""
检索会话管理器（门面类）

目录重构后，将超长的 `session_manager.py` 拆分为多个小模块：
- `_base.py`: 内存存储与 TTL / 初始化结构
- `_retrieval_history.py`: 检索历史、schema 汇总等
- `_scores.py`: 关系/属性分数
- `_sample_data.py`: 样例数据
- `_cache.py`: 三类缓存

对外仍通过 `RetrievalSessionManager` 提供 classmethod 接口，调用点无需变化。
"""

from ._base import _SessionBase
from ._cache import _CacheMixin
from ._retrieval_history import _RetrievalHistoryMixin
from ._semantic_nodes import _SemanticNodesMixin
from ._sample_data import _SampleDataMixin
from ._scores import _ScoresMixin


class RetrievalSessionManager(
    _CacheMixin,
    _SampleDataMixin,
    _ScoresMixin,
    _RetrievalHistoryMixin,
    _SemanticNodesMixin,
    _SessionBase,
):
    """检索会话管理器（门面类）。"""

    pass