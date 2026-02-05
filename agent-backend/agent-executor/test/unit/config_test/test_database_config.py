"""单元测试 - config/config_v2/models/database_config 模块"""

from unittest import TestCase

from app.config.config_v2.models.database_config import (
    RdsConfig,
    RedisConfig,
    GraphDBConfig,
    OpenSearchConfig,
)


class TestRdsConfig(TestCase):
    """测试 RdsConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = RdsConfig()
        self.assertIsNone(config.host)
        self.assertEqual(config.port, 3330)
        self.assertIsNone(config.dbname)
        self.assertIsNone(config.user)
        self.assertIsNone(config.password)
        self.assertEqual(config.db_type, "")

    def test_init_with_values(self):
        """测试带值初始化"""
        config = RdsConfig(
            host="127.0.0.1",
            port=3306,
            dbname="test_db",
            user="root",
            password="password",
            db_type="mysql",
        )
        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 3306)
        self.assertEqual(config.dbname, "test_db")
        self.assertEqual(config.user, "root")
        self.assertEqual(config.password, "password")
        self.assertEqual(config.db_type, "mysql")

    def test_from_dict_empty(self):
        """测试从空字典创建"""
        config = RdsConfig.from_dict({})
        self.assertIsNone(config.host)
        self.assertEqual(config.port, 3330)

    def test_from_dict_with_values(self):
        """测试从字典创建"""
        data = {
            "host": "127.0.0.1",
            "port": "3306",
            "dbname": "test_db",
            "user": "root",
            "password": "password",
            "db_type": "mysql",
        }
        config = RdsConfig.from_dict(data)
        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 3306)
        self.assertEqual(config.dbname, "test_db")


class TestRedisConfig(TestCase):
    """测试 RedisConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = RedisConfig()
        self.assertEqual(config.cluster_mode, "")
        self.assertEqual(config.host, "")
        self.assertEqual(config.port, "")
        self.assertEqual(config.user, "")
        self.assertEqual(config.password, "")

    def test_init_with_values(self):
        """测试带值初始化"""
        config = RedisConfig(
            cluster_mode="standalone",
            host="127.0.0.1",
            port="6379",
            user="user",
            password="password",
        )
        self.assertEqual(config.cluster_mode, "standalone")
        self.assertEqual(config.host, "127.0.0.1")

    def test_from_dict_sentinel_mode(self):
        """测试sentinel模式配置"""
        data = {
            "cluster_mode": "sentinel",
            "sentinel_master": "mymaster",
            "sentinel_user": "sentinel_user",
            "sentinel_password": "sentinel_pass",
        }
        config = RedisConfig.from_dict(data)
        self.assertEqual(config.cluster_mode, "sentinel")
        self.assertEqual(config.sentinel_master, "mymaster")

    def test_from_dict_master_slave_mode(self):
        """测试master-slave模式配置"""
        data = {
            "cluster_mode": "master-slave",
            "read_host": "read-host",
            "read_port": "6379",
            "write_host": "write-host",
            "write_port": "6379",
        }
        config = RedisConfig.from_dict(data)
        self.assertEqual(config.cluster_mode, "master-slave")
        self.assertEqual(config.read_host, "read-host")
        self.assertEqual(config.write_host, "write-host")


class TestGraphDBConfig(TestCase):
    """测试 GraphDBConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = GraphDBConfig()
        self.assertEqual(config.host, "")
        self.assertEqual(config.port, "")
        self.assertEqual(config.type, "nebulaGraph")
        self.assertEqual(config.read_only_user, "")
        self.assertEqual(config.read_only_password, "")

    def test_init_with_values(self):
        """测试带值初始化"""
        config = GraphDBConfig(
            host="127.0.0.1",
            port="9669",
            type="nebulaGraph",
            read_only_user="user",
            read_only_password="password",
        )
        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, "9669")

    def test_from_dict_with_custom_type(self):
        """测试自定义类型"""
        data = {"host": "127.0.0.1", "port": "9669", "type": "custom-graph"}
        config = GraphDBConfig.from_dict(data)
        self.assertEqual(config.type, "custom-graph")


class TestOpenSearchConfig(TestCase):
    """测试 OpenSearchConfig 类"""

    def test_init_default(self):
        """测试默认初始化"""
        config = OpenSearchConfig()
        self.assertEqual(config.host, "")
        self.assertEqual(config.port, "")
        self.assertEqual(config.user, "")
        self.assertEqual(config.password, "")

    def test_init_with_values(self):
        """测试带值初始化"""
        config = OpenSearchConfig(
            host="127.0.0.1",
            port="9200",
            user="admin",
            password="password",
        )
        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, "9200")
        self.assertEqual(config.user, "admin")
        self.assertEqual(config.password, "password")
