# -*- coding: utf-8 -*-
"""
知识网络 API 模块测试

测试内容:
1. build_object_type_view_mapping 函数
2. KnowledgeNetworkService 初始化
3. 完整知识网络映射构建逻辑
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestBuildObjectTypeViewMapping:
    """测试 build_object_type_view_mapping 函数"""

    def test_build_mapping_normal(self):
        """测试正常情况下构建映射"""
        from data_retrieval.api.knowledge_network import build_object_type_view_mapping

        kn_detail = {
            "object_types": [
                {
                    "id": "drug_product",
                    "name": "药物产品",
                    "data_source": {
                        "type": "data_view",
                        "id": "view_drug_001",
                        "name": "药物产品视图"
                    }
                },
                {
                    "id": "company",
                    "name": "公司",
                    "data_source": {
                        "type": "data_view",
                        "id": "view_company_001",
                        "name": "公司视图"
                    }
                },
                {
                    "id": "disease",
                    "name": "疾病",
                    "data_source": {
                        "type": "data_view",
                        "id": "view_disease_001",
                        "name": "疾病视图"
                    }
                }
            ]
        }

        mapping = build_object_type_view_mapping(kn_detail)

        assert len(mapping) == 3
        assert mapping["drug_product"] == "view_drug_001"
        assert mapping["company"] == "view_company_001"
        assert mapping["disease"] == "view_disease_001"

    def test_build_mapping_empty_object_types(self):
        """测试空 object_types 列表"""
        from data_retrieval.api.knowledge_network import build_object_type_view_mapping

        kn_detail = {
            "object_types": []
        }

        mapping = build_object_type_view_mapping(kn_detail)

        assert mapping == {}

    def test_build_mapping_no_object_types(self):
        """测试缺少 object_types 字段"""
        from data_retrieval.api.knowledge_network import build_object_type_view_mapping

        kn_detail = {}

        mapping = build_object_type_view_mapping(kn_detail)

        assert mapping == {}

    def test_build_mapping_non_data_view_type(self):
        """测试非 data_view 类型的 data_source"""
        from data_retrieval.api.knowledge_network import build_object_type_view_mapping

        kn_detail = {
            "object_types": [
                {
                    "id": "drug_product",
                    "name": "药物产品",
                    "data_source": {
                        "type": "other_type",
                        "id": "some_id"
                    }
                }
            ]
        }

        mapping = build_object_type_view_mapping(kn_detail)

        assert mapping == {}

    def test_build_mapping_missing_data_source(self):
        """测试缺少 data_source 字段"""
        from data_retrieval.api.knowledge_network import build_object_type_view_mapping

        kn_detail = {
            "object_types": [
                {
                    "id": "drug_product",
                    "name": "药物产品"
                }
            ]
        }

        mapping = build_object_type_view_mapping(kn_detail)

        assert mapping == {}

    def test_build_mapping_mixed_types(self):
        """测试混合类型（部分有 data_view，部分没有）"""
        from data_retrieval.api.knowledge_network import build_object_type_view_mapping

        kn_detail = {
            "object_types": [
                {
                    "id": "drug_product",
                    "name": "药物产品",
                    "data_source": {
                        "type": "data_view",
                        "id": "view_drug_001"
                    }
                },
                {
                    "id": "company",
                    "name": "公司",
                    "data_source": {
                        "type": "other_type",
                        "id": "other_id"
                    }
                },
                {
                    "id": "disease",
                    "name": "疾病"
                    # 没有 data_source
                }
            ]
        }

        mapping = build_object_type_view_mapping(kn_detail)

        assert len(mapping) == 1
        assert mapping["drug_product"] == "view_drug_001"
        assert "company" not in mapping
        assert "disease" not in mapping


class TestKnowledgeNetworkService:
    """测试 KnowledgeNetworkService 类"""

    def test_service_initialization_default(self):
        """测试默认初始化"""
        from data_retrieval.api.knowledge_network import KnowledgeNetworkService

        service = KnowledgeNetworkService()

        assert service.base_url is not None
        assert service.headers == {}
        assert "{kn_id}" in service.detail_url

    def test_service_initialization_custom_base_url(self):
        """测试自定义 base_url 初始化"""
        from data_retrieval.api.knowledge_network import KnowledgeNetworkService

        custom_url = "http://custom-service:8080"
        service = KnowledgeNetworkService(base_url=custom_url)

        assert service.base_url == custom_url

    def test_service_initialization_with_headers(self):
        """测试带 headers 初始化"""
        from data_retrieval.api.knowledge_network import KnowledgeNetworkService

        headers = {"Authorization": "Bearer token123"}
        service = KnowledgeNetworkService(headers=headers)

        assert service.headers == headers


class TestFullMappingIntegration:
    """测试完整映射集成逻辑"""

    def test_relation_view_id_resolution(self):
        """测试关系中的 view_id 解析"""
        # 模拟完整知识网络映射
        full_mapping = {
            "drug_product": "view_drug_001",
            "company": "view_company_001",
            "disease": "view_disease_001"
        }

        # 模拟 relation_type 概念
        relation_concept = {
            "concept_id": "produces",
            "concept_name": "生产药品",
            "concept_detail": {
                "source_object_type_id": "company",
                "source_object_type_name": "公司",
                "target_object_type_id": "drug_product",
                "target_object_type_name": "药物产品",
                "comment": "生产关系"
            }
        }

        concept_detail = relation_concept.get("concept_detail", {})
        source_object_type_id = concept_detail.get("source_object_type_id", "")
        target_object_type_id = concept_detail.get("target_object_type_id", "")

        source_view_id = full_mapping.get(source_object_type_id, "")
        target_view_id = full_mapping.get(target_object_type_id, "")

        assert source_view_id == "view_company_001"
        assert target_view_id == "view_drug_001"

    def test_relation_view_id_not_found(self):
        """测试关系中的 view_id 找不到时返回空"""
        # 模拟不完整的映射
        full_mapping = {
            "drug_product": "view_drug_001"
        }

        relation_concept = {
            "concept_detail": {
                "source_object_type_id": "unknown_type",
                "target_object_type_id": "drug_product"
            }
        }

        concept_detail = relation_concept.get("concept_detail", {})
        source_view_id = full_mapping.get(concept_detail.get("source_object_type_id", ""), "")
        target_view_id = full_mapping.get(concept_detail.get("target_object_type_id", ""), "")

        assert source_view_id == ""
        assert target_view_id == "view_drug_001"

    def test_fallback_mapping_from_recalled_concepts(self):
        """测试从召回结果补充映射"""
        # 模拟完整映射（可能获取失败导致为空）
        full_mapping = {}

        # 模拟召回的 object_type
        recalled_concept = {
            "concept_id": "drug_product",
            "concept_detail": {
                "data_source": {
                    "type": "data_view",
                    "id": "view_drug_001"
                }
            }
        }

        # 补充逻辑
        concept_id = recalled_concept.get("concept_id")
        ds = recalled_concept.get("concept_detail", {}).get("data_source", {})
        if ds.get("type") == "data_view":
            if concept_id and concept_id not in full_mapping:
                full_mapping[concept_id] = ds.get("id")

        assert full_mapping["drug_product"] == "view_drug_001"


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("知识网络 API 模块测试")
    print("=" * 60)

    test_classes = [
        TestBuildObjectTypeViewMapping,
        TestKnowledgeNetworkService,
        TestFullMappingIntegration,
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
