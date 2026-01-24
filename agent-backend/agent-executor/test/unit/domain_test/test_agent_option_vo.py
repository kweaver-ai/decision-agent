"""单元测试 - domain/vo/agentvo/agent_option 模块"""

from unittest import TestCase

from app.domain.vo.agentvo.agent_option import AgentRunOptionsVo


class TestAgentRunOptionsVo(TestCase):
    """测试 AgentRunOptionsVo 类"""

    def test_init_minimal(self):
        """测试最小初始化"""
        options = AgentRunOptionsVo()
        self.assertIsNone(options.output_vars)
        self.assertIsNone(options.incremental_output)
        self.assertIsNone(options.data_source)
        self.assertIsNone(options.llm_config)
        self.assertIsNone(options.tmp_files)
        self.assertIsNone(options.agent_id)
        self.assertIsNone(options.conversation_id)
        self.assertIsNone(options.agent_run_id)
        self.assertIsNone(options.is_need_progress)
        self.assertIsNone(options.enable_dependency_cache)

    def test_init_with_output_vars(self):
        """测试带输出变量初始化"""
        output_vars = ["var1", "var2", "var3"]
        options = AgentRunOptionsVo(output_vars=output_vars)
        self.assertEqual(options.output_vars, output_vars)

    def test_init_with_incremental_output(self):
        """测试带增量输出初始化"""
        options = AgentRunOptionsVo(incremental_output=True)
        self.assertTrue(options.incremental_output)

    def test_init_with_data_source(self):
        """测试带数据源初始化"""
        data_source = {"type": "database", "config": {}}
        options = AgentRunOptionsVo(data_source=data_source)
        self.assertEqual(options.data_source, data_source)

    def test_init_with_llm_config(self):
        """测试带LLM配置初始化"""
        llm_config = {"model": "gpt-4", "temperature": 0.7}
        options = AgentRunOptionsVo(llm_config=llm_config)
        self.assertEqual(options.llm_config, llm_config)

    def test_init_with_tmp_files(self):
        """测试带临时文件初始化"""
        tmp_files = ["/path/to/file1", "/path/to/file2"]
        options = AgentRunOptionsVo(tmp_files=tmp_files)
        self.assertEqual(options.tmp_files, tmp_files)

    def test_init_with_agent_id(self):
        """测试带agent_id初始化"""
        options = AgentRunOptionsVo(agent_id="agent_123")
        self.assertEqual(options.agent_id, "agent_123")

    def test_init_with_conversation_id(self):
        """测试带conversation_id初始化"""
        options = AgentRunOptionsVo(conversation_id="conv_456")
        self.assertEqual(options.conversation_id, "conv_456")

    def test_init_with_agent_run_id(self):
        """测试带agent_run_id初始化"""
        options = AgentRunOptionsVo(agent_run_id="run_789")
        self.assertEqual(options.agent_run_id, "run_789")

    def test_init_with_is_need_progress(self):
        """测试带is_need_progress初始化"""
        options = AgentRunOptionsVo(is_need_progress=True)
        self.assertTrue(options.is_need_progress)

    def test_init_with_enable_dependency_cache(self):
        """测试带enable_dependency_cache初始化"""
        options = AgentRunOptionsVo(enable_dependency_cache=True)
        self.assertTrue(options.enable_dependency_cache)

    def test_init_with_all_fields(self):
        """测试带所有字段初始化"""
        options = AgentRunOptionsVo(
            output_vars=["var1", "var2"],
            incremental_output=True,
            data_source={"type": "database"},
            llm_config={"model": "gpt-4"},
            tmp_files=["file1", "file2"],
            agent_id="agent_123",
            conversation_id="conv_456",
            agent_run_id="run_789",
            is_need_progress=True,
            enable_dependency_cache=True,
        )

        self.assertEqual(options.output_vars, ["var1", "var2"])
        self.assertTrue(options.incremental_output)
        self.assertEqual(options.data_source, {"type": "database"})
        self.assertEqual(options.llm_config, {"model": "gpt-4"})
        self.assertEqual(options.tmp_files, ["file1", "file2"])
        self.assertEqual(options.agent_id, "agent_123")
        self.assertEqual(options.conversation_id, "conv_456")
        self.assertEqual(options.agent_run_id, "run_789")
        self.assertTrue(options.is_need_progress)
        self.assertTrue(options.enable_dependency_cache)

    def test_model_dump_minimal(self):
        """测试最小序列化"""
        options = AgentRunOptionsVo()
        data = options.model_dump()
        self.assertIsNone(data["output_vars"])
        self.assertIsNone(data["incremental_output"])

    def test_model_dump_with_fields(self):
        """测试带字段序列化"""
        options = AgentRunOptionsVo(
            output_vars=["var1"],
            incremental_output=True,
            agent_id="agent_123",
        )
        data = options.model_dump()
        self.assertEqual(data["output_vars"], ["var1"])
        self.assertTrue(data["incremental_output"])
        self.assertEqual(data["agent_id"], "agent_123")

    def test_model_dump_all_fields(self):
        """测试所有字段序列化"""
        options = AgentRunOptionsVo(
            output_vars=["var1", "var2"],
            incremental_output=False,
            data_source={"type": "file"},
            llm_config={"model": "gpt-4"},
            tmp_files=["file1"],
            agent_id="agent_123",
            conversation_id="conv_456",
            agent_run_id="run_789",
            is_need_progress=False,
            enable_dependency_cache=False,
        )
        data = options.model_dump()
        self.assertEqual(len(data), 10)
        self.assertEqual(data["output_vars"], ["var1", "var2"])
        self.assertFalse(data["incremental_output"])

    def test_model_dump_exclude_none(self):
        """测试序列化排除None值"""
        options = AgentRunOptionsVo(agent_id="agent_123")
        data = options.model_dump(exclude_none=True)
        self.assertIn("agent_id", data)
        self.assertNotIn("output_vars", data)
        self.assertNotIn("conversation_id", data)
