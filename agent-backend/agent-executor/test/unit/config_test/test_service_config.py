"""单元测试 - config/config_v2/models/service_config 模块"""

from unittest import TestCase

from app.config.config_v2.models.service_config import (
    ServiceEndpoint,
    ServicesConfig,
    ExternalServicesConfig,
)


class TestServiceEndpoint(TestCase):
    """测试 ServiceEndpoint 类"""

    def test_init_default(self):
        """测试默认初始化"""
        endpoint = ServiceEndpoint()
        self.assertEqual(endpoint.host, "")
        self.assertEqual(endpoint.port, "")

    def test_init_with_values(self):
        """测试带值初始化"""
        endpoint = ServiceEndpoint(host="127.0.0.1", port="8080")
        self.assertEqual(endpoint.host, "127.0.0.1")
        self.assertEqual(endpoint.port, "8080")


class TestServicesConfig(TestCase):
    """测试 ServicesConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = ServicesConfig()
        self.assertIsNotNone(config.mf_model_factory)
        self.assertIsNotNone(config.mf_model_manager)
        self.assertIsNotNone(config.mf_model_api)
        self.assertIsNotNone(config.agent_app)
        self.assertIsNotNone(config.agent_executor)
        self.assertIsNotNone(config.agent_factory)
        self.assertIsNotNone(config.agent_operator_integration)
        self.assertIsNotNone(config.agent_memory)
        self.assertIsNotNone(config.kn_data_query)
        self.assertIsNotNone(config.kn_knowledge_data)
        self.assertIsNotNone(config.data_connection)
        self.assertIsNotNone(config.search_engine)
        self.assertIsNotNone(config.ecosearch)
        self.assertIsNotNone(config.ecoindex_public)
        self.assertIsNotNone(config.ecoindex_private)
        self.assertIsNotNone(config.docset_private)
        self.assertIsNotNone(config.datahub)

    def test_init_with_values(self):
        """测试带值初始化"""
        config = ServicesConfig(
            mf_model_factory=ServiceEndpoint("host1", "port1"),
            mf_model_manager=ServiceEndpoint("host2", "port2"),
        )
        self.assertEqual(config.mf_model_factory.host, "host1")
        self.assertEqual(config.mf_model_manager.host, "host2")

    def test_default_values(self):
        """测试默认值"""
        config = ServicesConfig()
        self.assertEqual(config.mf_model_factory.host, "mf-model-factory")
        self.assertEqual(config.mf_model_factory.port, "9898")
        self.assertEqual(config.agent_app.host, "agent-app")
        self.assertEqual(config.agent_app.port, "30777")
        self.assertEqual(config.agent_factory.host, "agent-factory")
        self.assertEqual(config.agent_factory.port, "13020")
        self.assertEqual(config.agent_memory.host, "agent-memory")
        self.assertEqual(config.agent_memory.port, "30790")

    def test_from_dict_empty(self):
        """测试从空字典创建"""
        config = ServicesConfig.from_dict({})
        self.assertIsNotNone(config.mf_model_factory)
        self.assertEqual(config.mf_model_factory.host, "")
        self.assertEqual(config.mf_model_factory.port, "")

    def test_from_dict_with_values(self):
        """测试从字典创建"""
        data = {
            "mf_model_factory": {"host": "host1", "port": "port1"},
            "agent_app": {"host": "host2", "port": "port2"},
            "agent_factory": {"host": "host3"},
        }
        config = ServicesConfig.from_dict(data)
        self.assertEqual(config.mf_model_factory.host, "host1")
        self.assertEqual(config.mf_model_factory.port, "port1")
        self.assertEqual(config.agent_app.host, "host2")
        self.assertEqual(config.agent_app.port, "port2")
        self.assertEqual(config.agent_factory.host, "host3")
        self.assertEqual(config.agent_factory.port, "")

    def test_from_dict_partial(self):
        """测试从字典创建（部分值）"""
        data = {"agent_app": {"host": "test-host", "port": "1234"}}
        config = ServicesConfig.from_dict(data)
        self.assertEqual(config.agent_app.host, "test-host")
        self.assertEqual(config.agent_app.port, "1234")
        self.assertEqual(config.mf_model_factory.host, "")
        self.assertEqual(config.mf_model_factory.port, "")

    def test_from_dict_port_conversion(self):
        """测试端口类型转换"""
        data = {"agent_app": {"host": "host", "port": 8080}}
        config = ServicesConfig.from_dict(data)
        self.assertEqual(config.agent_app.port, "8080")
        self.assertIsInstance(config.agent_app.port, str)

    def test_all_services_initialized(self):
        """测试所有服务端点初始化"""
        config = ServicesConfig()
        services = [
            "mf_model_factory",
            "mf_model_manager",
            "mf_model_api",
            "agent_app",
            "agent_executor",
            "agent_factory",
            "agent_operator_integration",
            "agent_memory",
            "kn_data_query",
            "kn_knowledge_data",
            "data_connection",
            "search_engine",
            "ecosearch",
            "ecoindex_public",
            "ecoindex_private",
            "docset_private",
            "datahub",
        ]
        for service in services:
            self.assertIsNotNone(
                getattr(config, service), f"{service} should be initialized"
            )

    def test_default_agent_services_ports(self):
        """测试Agent服务默认端口"""
        config = ServicesConfig()
        self.assertEqual(config.agent_app.port, "30777")
        self.assertEqual(config.agent_executor.port, "30778")
        self.assertEqual(config.agent_factory.port, "13020")
        self.assertEqual(config.agent_operator_integration.port, "9000")
        self.assertEqual(config.agent_memory.port, "30790")

    def test_default_model_services_ports(self):
        """测试模型服务默认端口"""
        config = ServicesConfig()
        self.assertEqual(config.mf_model_factory.port, "9898")
        self.assertEqual(config.mf_model_manager.port, "9898")
        self.assertEqual(config.mf_model_api.port, "9898")

    def test_default_knowledge_services_ports(self):
        """测试知识服务默认端口"""
        config = ServicesConfig()
        self.assertEqual(config.kn_data_query.port, "6480")
        self.assertEqual(config.kn_knowledge_data.port, "6475")
        self.assertEqual(config.data_connection.port, "8098")
        self.assertEqual(config.search_engine.port, "6479")

    def test_default_search_services_ports(self):
        """测试搜索服务默认端口"""
        config = ServicesConfig()
        self.assertEqual(config.ecosearch.port, "32126")
        self.assertEqual(config.ecoindex_public.port, "32129")
        self.assertEqual(config.ecoindex_private.port, "32130")
        self.assertEqual(config.docset_private.port, "32597")


class TestExternalServicesConfig(TestCase):
    """测试 ExternalServicesConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = ExternalServicesConfig()
        self.assertEqual(config.emb_url, "")
        self.assertEqual(config.embedding_dimension, 768)
        self.assertEqual(config.rerank_url, "")

    def test_init_with_values(self):
        """测试带值初始化"""
        config = ExternalServicesConfig(
            emb_url="http://embedding-service",
            embedding_dimension=1536,
            rerank_url="http://rerank-service",
        )
        self.assertEqual(config.emb_url, "http://embedding-service")
        self.assertEqual(config.embedding_dimension, 1536)
        self.assertEqual(config.rerank_url, "http://rerank-service")

    def test_from_dict_empty(self):
        """测试从空字典创建"""
        config = ExternalServicesConfig.from_dict({})
        self.assertEqual(config.emb_url, "")
        self.assertEqual(config.embedding_dimension, 768)
        self.assertEqual(config.rerank_url, "")

    def test_from_dict_with_values(self):
        """测试从字典创建"""
        data = {
            "emb_url": "http://embedding-service",
            "embedding_dimension": 1536,
            "rerank_url": "http://rerank-service",
        }
        config = ExternalServicesConfig.from_dict(data)
        self.assertEqual(config.emb_url, "http://embedding-service")
        self.assertEqual(config.embedding_dimension, 1536)
        self.assertEqual(config.rerank_url, "http://rerank-service")

    def test_from_dict_partial(self):
        """测试从字典创建（部分值）"""
        data = {"emb_url": "http://embedding-service"}
        config = ExternalServicesConfig.from_dict(data)
        self.assertEqual(config.emb_url, "http://embedding-service")
        self.assertEqual(config.embedding_dimension, 768)
        self.assertEqual(config.rerank_url, "")

    def test_from_dict_dimension_conversion(self):
        """测试维度类型转换"""
        data = {"embedding_dimension": "1024"}
        config = ExternalServicesConfig.from_dict(data)
        self.assertEqual(config.embedding_dimension, 1024)
        self.assertIsInstance(config.embedding_dimension, int)

    def test_from_dict_partial_embedding_dimension(self):
        """测试仅部分embedding_dimension"""
        data = {"embedding_dimension": 1024}
        config = ExternalServicesConfig.from_dict(data)
        self.assertEqual(config.embedding_dimension, 1024)
        self.assertEqual(config.emb_url, "")
        self.assertEqual(config.rerank_url, "")

    def test_from_dict_partial_rerank_url(self):
        """测试仅部分rerank_url"""
        data = {"rerank_url": "http://rerank-service"}
        config = ExternalServicesConfig.from_dict(data)
        self.assertEqual(config.rerank_url, "http://rerank-service")
        self.assertEqual(config.emb_url, "")
        self.assertEqual(config.embedding_dimension, 768)
