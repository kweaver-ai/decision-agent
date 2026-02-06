"""单元测试 - domain/vo/agentvo/agent_option 模块"""

import pytest

from app.domain.vo.agentvo.agent_option import AgentRunOptionsVo


class TestAgentRunOptionsVo:
    """测试 AgentRunOptionsVo 模型"""

    def test_default_initialization(self):
        """测试默认初始化"""
        options = AgentRunOptionsVo()
        assert options.output_vars is None
        assert options.incremental_output is None
        assert options.data_source is None
        assert options.llm_config is None
        assert options.tmp_files is None
        assert options.agent_id is None
        assert options.conversation_id is None
        assert options.agent_run_id is None
        assert options.is_need_progress is None
        assert options.enable_dependency_cache is None
        assert options.resume_info is None

    def test_with_output_vars(self):
        """测试设置输出变量"""
        options = AgentRunOptionsVo(output_vars=["result", "status"])
        assert options.output_vars == ["result", "status"]
        assert len(options.output_vars) == 2

    def test_with_incremental_output(self):
        """测试增量输出"""
        options = AgentRunOptionsVo(incremental_output=True)
        assert options.incremental_output is True

    def test_with_data_source(self):
        """测试数据源"""
        data_source = {"type": "database", "connection": "localhost"}
        options = AgentRunOptionsVo(data_source=data_source)
        assert options.data_source == data_source
        assert options.data_source["type"] == "database"

    def test_with_llm_config(self):
        """测试LLM配置"""
        llm_config = {"model": "gpt-4", "temperature": 0.7}
        options = AgentRunOptionsVo(llm_config=llm_config)
        assert options.llm_config == llm_config
        assert options.llm_config["temperature"] == 0.7

    def test_with_tmp_files(self):
        """测试临时文件"""
        tmp_files = ["/tmp/file1.txt", "/tmp/file2.pdf"]
        options = AgentRunOptionsVo(tmp_files=tmp_files)
        assert options.tmp_files == tmp_files
        assert len(options.tmp_files) == 2

    def test_with_agent_id(self):
        """测试Agent ID"""
        options = AgentRunOptionsVo(agent_id="agent_123")
        assert options.agent_id == "agent_123"

    def test_with_conversation_id(self):
        """测试会话ID"""
        options = AgentRunOptionsVo(conversation_id="conv_456")
        assert options.conversation_id == "conv_456"

    def test_with_agent_run_id(self):
        """测试Agent运行ID"""
        options = AgentRunOptionsVo(agent_run_id="run_789")
        assert options.agent_run_id == "run_789"

    def test_with_is_need_progress(self):
        """测试是否需要进度"""
        options = AgentRunOptionsVo(is_need_progress=True)
        assert options.is_need_progress is True

    def test_with_enable_dependency_cache(self):
        """测试启用依赖缓存"""
        options = AgentRunOptionsVo(enable_dependency_cache=False)
        assert options.enable_dependency_cache is False

    def test_with_all_fields(self):
        """测试所有字段都有值"""
        options = AgentRunOptionsVo(
            output_vars=["result"],
            incremental_output=True,
            data_source={"type": "db"},
            llm_config={"model": "gpt-4"},
            tmp_files=["/tmp/file.txt"],
            agent_id="agent_123",
            conversation_id="conv_456",
            agent_run_id="run_789",
            is_need_progress=True,
            enable_dependency_cache=True,
            resume_info={"frame_id": "frame_1"}
        )
        assert options.output_vars == ["result"]
        assert options.incremental_output is True
        assert options.data_source == {"type": "db"}
        assert options.llm_config == {"model": "gpt-4"}
        assert options.tmp_files == ["/tmp/file.txt"]
        assert options.agent_id == "agent_123"
        assert options.conversation_id == "conv_456"
        assert options.agent_run_id == "run_789"
        assert options.is_need_progress is True
        assert options.enable_dependency_cache is True
        assert options.resume_info == {"frame_id": "frame_1"}

    def test_empty_lists(self):
        """测试空列表"""
        options = AgentRunOptionsVo(
            output_vars=[],
            tmp_files=[]
        )
        assert options.output_vars == []
        assert options.tmp_files == []

    def test_empty_dict(self):
        """测试空字典"""
        options = AgentRunOptionsVo(
            data_source={},
            llm_config={}
        )
        assert options.data_source == {}
        assert options.llm_config == {}

    def test_model_dump(self):
        """测试模型序列化"""
        options = AgentRunOptionsVo(agent_id="agent_123")
        data = options.model_dump()
        assert data["agent_id"] == "agent_123"
        assert isinstance(data, dict)

    def test_none_values_stay_none(self):
        """测试None值保持为None"""
        options = AgentRunOptionsVo()
        # Ensure None values don't get converted to empty lists/dicts
        assert options.output_vars is None
        assert options.data_source is None
