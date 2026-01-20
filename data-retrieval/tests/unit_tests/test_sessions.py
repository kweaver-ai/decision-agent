# -*- coding: utf-8 -*-
"""
Sessions 模块测试

测试内容:
1. InMemoryChatSession 单例模式
2. 会话历史管理
3. Agent 日志管理
4. 会话 ID 生成
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestGetSessionId:
    """测试会话 ID 生成"""
    
    def test_from_user_id(self):
        """测试从用户 ID 生成会话 ID"""
        from data_retrieval.sessions.base import GetSessionId
        
        session_id = GetSessionId.from_user_id("test_user")
        
        assert session_id is not None
        assert len(session_id) == 32  # MD5 哈希长度
        assert isinstance(session_id, str)
    
    def test_different_users_different_ids(self):
        """测试不同用户生成不同的会话 ID"""
        from data_retrieval.sessions.base import GetSessionId
        import time
        
        # 同一时间不同用户
        id1 = GetSessionId.from_user_id("user1")
        time.sleep(1)  # 确保时间戳不同
        id2 = GetSessionId.from_user_id("user2")
        
        # 由于时间戳的存在，ID 应该不同
        assert id1 != id2


class TestInMemoryChatSession:
    """测试内存会话管理"""
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        from data_retrieval.sessions.in_memory_session import InMemoryChatSession
        
        session1 = InMemoryChatSession()
        session2 = InMemoryChatSession()
        
        assert session1 is session2
    
    def test_get_chat_history_new_session(self):
        """测试获取新会话历史"""
        from data_retrieval.sessions.in_memory_session import InMemoryChatSession
        
        session = InMemoryChatSession()
        test_session_id = "test_new_session_001"
        
        # 清理可能存在的旧数据
        try:
            session.delete_chat_history(test_session_id)
        except Exception:
            pass
        
        history = session.get_chat_history(test_session_id)
        
        assert history is not None
        assert len(history.messages) == 0
    
    def test_add_human_message(self):
        """测试添加人类消息"""
        from data_retrieval.sessions.in_memory_session import InMemoryChatSession
        
        session = InMemoryChatSession()
        test_session_id = "test_human_msg_001"
        
        # 清理旧数据
        try:
            session.delete_chat_history(test_session_id)
        except Exception:
            pass
        
        session.add_chat_history(test_session_id, "human", "你好")
        
        history = session.get_chat_history(test_session_id)
        assert len(history.messages) == 1
        assert history.messages[0].content == "你好"
    
    def test_add_ai_message(self):
        """测试添加 AI 消息"""
        from data_retrieval.sessions.in_memory_session import InMemoryChatSession
        
        session = InMemoryChatSession()
        test_session_id = "test_ai_msg_001"
        
        try:
            session.delete_chat_history(test_session_id)
        except Exception:
            pass
        
        session.add_chat_history(test_session_id, "ai", "你好，我是 AI 助手")
        
        history = session.get_chat_history(test_session_id)
        assert len(history.messages) == 1
    
    def test_add_multiple_messages(self):
        """测试添加多条消息"""
        from data_retrieval.sessions.in_memory_session import InMemoryChatSession
        
        session = InMemoryChatSession()
        test_session_id = "test_multi_msg_001"
        
        try:
            session.delete_chat_history(test_session_id)
        except Exception:
            pass
        
        session.add_chat_history(test_session_id, "human", "问题1")
        session.add_chat_history(test_session_id, "ai", "回答1")
        session.add_chat_history(test_session_id, "human", "问题2")
        
        history = session.get_chat_history(test_session_id)
        assert len(history.messages) == 3
    
    def test_delete_chat_history(self):
        """测试删除会话历史"""
        from data_retrieval.sessions.in_memory_session import InMemoryChatSession
        
        session = InMemoryChatSession()
        test_session_id = "test_delete_001"
        
        # 创建会话
        session.add_chat_history(test_session_id, "human", "测试消息")
        
        # 删除会话
        session.delete_chat_history(test_session_id)
        
        # 验证删除后获取的是新的空历史
        history = session.get_chat_history(test_session_id)
        assert len(history.messages) == 0
    
    def test_agent_logs(self):
        """测试 Agent 日志管理"""
        from data_retrieval.sessions.in_memory_session import InMemoryChatSession
        
        session = InMemoryChatSession()
        test_session_id = "test_agent_logs_001"
        
        test_logs = {"step": 1, "action": "search", "result": "success"}
        session.add_agent_logs(test_session_id, test_logs)
        
        retrieved_logs = session.get_agent_logs(test_session_id)
        assert retrieved_logs == test_logs
    
    def test_clean_session(self):
        """测试清理所有会话"""
        from data_retrieval.sessions.in_memory_session import InMemoryChatSession
        
        session = InMemoryChatSession()
        
        # 添加一些数据
        session.add_chat_history("clean_test_1", "human", "msg1")
        session.add_chat_history("clean_test_2", "human", "msg2")
        
        # 清理所有
        session.clean_session()
        
        # 验证被清理
        history1 = session.get_chat_history("clean_test_1")
        history2 = session.get_chat_history("clean_test_2")
        
        assert len(history1.messages) == 0
        assert len(history2.messages) == 0


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Sessions 模块测试")
    print("=" * 60)
    
    test_classes = [
        TestGetSessionId,
        TestInMemoryChatSession,
    ]
    
    total = 0
    passed = 0
    failed = []
    
    for cls in test_classes:
        print(f"\n--- {cls.__name__} ---")
        instance = cls()
        
        for method in dir(instance):
            if method.startswith('test_'):
                total += 1
                try:
                    getattr(instance, method)()
                    print(f"  ✅ {method}")
                    passed += 1
                except Exception as e:
                    print(f"  ❌ {method}: {e}")
                    failed.append((cls.__name__, method, str(e)))
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    if failed:
        print("\n失败的测试:")
        for c, m, e in failed:
            print(f"  - {c}.{m}: {e}")
    else:
        print("🎉 所有测试通过！")
    print("=" * 60)
    
    return len(failed) == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
