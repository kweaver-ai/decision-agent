# -*- coding: utf-8 -*-
"""
DIP DataView 模块测试

测试内容:
1. kn_data_view_fields 参数初始化
2. kn_data_view_fields 字段过滤逻辑
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestDataViewKnFieldsFilter:
    """测试 DataView 的 kn_data_view_fields 过滤功能"""

    def test_kn_data_view_fields_initialization_none(self):
        """测试 kn_data_view_fields 初始化为 None"""
        from data_retrieval.datasource.dip_dataview import DataView

        data_view = DataView(
            view_list=[],
            base_url="http://test.com",
            user_id="test_user",
            token="test_token"
        )

        assert data_view.kn_data_view_fields is None

    def test_kn_data_view_fields_initialization_with_data(self):
        """测试 kn_data_view_fields 初始化带数据"""
        from data_retrieval.datasource.dip_dataview import DataView

        kn_fields = {
            "view_id_1": ["field_a", "field_b"],
            "view_id_2": ["field_c"]
        }

        data_view = DataView(
            view_list=[],
            base_url="http://test.com",
            user_id="test_user",
            token="test_token",
            kn_data_view_fields=kn_fields
        )

        assert data_view.kn_data_view_fields is not None
        assert data_view.kn_data_view_fields == kn_fields
        assert "view_id_1" in data_view.kn_data_view_fields
        assert len(data_view.kn_data_view_fields["view_id_1"]) == 2

    def test_kn_data_view_fields_empty_dict(self):
        """测试 kn_data_view_fields 初始化为空字典"""
        from data_retrieval.datasource.dip_dataview import DataView

        data_view = DataView(
            view_list=[],
            base_url="http://test.com",
            user_id="test_user",
            token="test_token",
            kn_data_view_fields={}
        )

        assert data_view.kn_data_view_fields == {}


class TestGetViewEn2Type:
    """测试 get_view_en2type 函数"""

    def test_get_view_en2type_success(self):
        """测试正常情况：有 meta_table_name 时返回正确结果"""
        from data_retrieval.datasource.dip_dataview import get_view_en2type

        resp_column = {
            "name": "测试视图",
            "id": "view_001",
            "meta_table_name": "catalog.schema.table_name",
            "fields": [
                {"original_name": "col1", "type": "string"},
                {"original_name": "col2", "type": "integer"},
            ]
        }

        en2type, column_name, table, zh_table = get_view_en2type(resp_column)

        assert en2type == {"col1": "string", "col2": "integer"}
        assert column_name == ['"col1"', '"col2"']
        assert table == "catalog.schema.table_name"
        assert zh_table == "测试视图"

    def test_get_view_en2type_raises_error_when_no_table(self):
        """测试异常情况：没有 meta_table_name 时抛出 AfDataSourceError"""
        from data_retrieval.datasource.dip_dataview import get_view_en2type
        from data_retrieval.api.error import AfDataSourceError
        import pytest

        resp_column = {
            "name": "自定义视图",
            "id": "view_002",
            "meta_table_name": "",  # 空字符串
            "fields": [
                {"original_name": "col1", "type": "string"},
            ]
        }

        with pytest.raises(AfDataSourceError) as exc_info:
            get_view_en2type(resp_column)

        assert "自定义视图" in str(exc_info.value.reason)
        assert "can't be used as a table" in str(exc_info.value.reason)

    def test_get_view_en2type_raises_error_for_custom_view(self):
        """测试异常情况：custom 类型视图没有 meta_table_name 时抛出错误"""
        from data_retrieval.datasource.dip_dataview import get_view_en2type
        from data_retrieval.api.error import AfDataSourceError
        import pytest

        resp_column = {
            "name": "自定义视图",
            "id": "view_003",
            "type": "custom",
            "meta_table_name": None,  # None 值
            "fields": [
                {"original_name": "col1", "type": "string"},
            ]
        }

        with pytest.raises(AfDataSourceError):
            get_view_en2type(resp_column)

    def test_get_view_en2type_missing_meta_table_name_key(self):
        """测试异常情况：缺少 meta_table_name 键时抛出错误"""
        from data_retrieval.datasource.dip_dataview import get_view_en2type
        from data_retrieval.api.error import AfDataSourceError
        import pytest

        resp_column = {
            "name": "测试视图",
            "id": "view_004",
            # 没有 meta_table_name 键
            "fields": [
                {"original_name": "col1", "type": "string"},
            ]
        }

        with pytest.raises(AfDataSourceError):
            get_view_en2type(resp_column)


class TestKnFieldsFilterLogic:
    """测试 kn_data_view_fields 过滤逻辑"""

    def test_filter_fields_by_original_name(self):
        """测试根据 original_name 过滤字段"""
        # 模拟字段过滤逻辑
        fields = [
            {"original_name": "field_a", "name": "字段A", "display_name": "字段A显示名"},
            {"original_name": "field_b", "name": "字段B", "display_name": "字段B显示名"},
            {"original_name": "field_c", "name": "字段C", "display_name": "字段C显示名"},
        ]

        kn_field_names = {"field_a", "field_c"}

        filtered_fields = []
        for field in fields:
            if field["original_name"] in kn_field_names:
                filtered_fields.append(field)

        assert len(filtered_fields) == 2
        assert filtered_fields[0]["original_name"] == "field_a"
        assert filtered_fields[1]["original_name"] == "field_c"

    def test_filter_fields_no_match(self):
        """测试没有匹配字段时的过滤"""
        fields = [
            {"original_name": "field_a", "name": "字段A", "display_name": "字段A显示名"},
            {"original_name": "field_b", "name": "字段B", "display_name": "字段B显示名"},
        ]

        kn_field_names = {"field_x", "field_y"}

        filtered_fields = []
        for field in fields:
            if field["original_name"] in kn_field_names:
                filtered_fields.append(field)

        assert len(filtered_fields) == 0

    def test_filter_fields_all_match(self):
        """测试所有字段都匹配时的过滤"""
        fields = [
            {"original_name": "field_a", "name": "字段A", "display_name": "字段A显示名"},
            {"original_name": "field_b", "name": "字段B", "display_name": "字段B显示名"},
        ]

        kn_field_names = {"field_a", "field_b"}

        filtered_fields = []
        for field in fields:
            if field["original_name"] in kn_field_names:
                filtered_fields.append(field)

        assert len(filtered_fields) == 2

    def test_filter_fields_empty_kn_fields(self):
        """测试空 kn_field_names 时不过滤"""
        fields = [
            {"original_name": "field_a", "name": "字段A", "display_name": "字段A显示名"},
            {"original_name": "field_b", "name": "字段B", "display_name": "字段B显示名"},
        ]

        kn_field_names = set()

        # 当 kn_field_names 为空时，不应进行过滤
        if kn_field_names:
            filtered_fields = []
            for field in fields:
                if field["original_name"] in kn_field_names:
                    filtered_fields.append(field)
        else:
            filtered_fields = fields

        assert len(filtered_fields) == 2


class TestKnDataViewFieldsExtraction:
    """测试从 concept_detail 中提取 kn_data_view_fields"""

    def test_extract_kn_fields_from_data_views(self):
        """测试从 data_views 中提取 kn_data_view_fields"""
        data_views = [
            {
                "id": "view_1",
                "view_name": "视图1",
                "concept_detail": {
                    "data_properties": [
                        {
                            "name": "prop_a",
                            "display_name": "属性A",
                            "mapped_field": {
                                "name": "field_a",
                                "type": "varchar"
                            }
                        },
                        {
                            "name": "prop_b",
                            "display_name": "属性B",
                            "mapped_field": {
                                "name": "field_b",
                                "type": "integer"
                            }
                        }
                    ]
                }
            },
            {
                "id": "view_2",
                "view_name": "视图2",
                "concept_detail": {
                    "data_properties": [
                        {
                            "name": "prop_c",
                            "display_name": "属性C",
                            "mapped_field": {
                                "name": "field_c",
                                "type": "varchar"
                            }
                        }
                    ]
                }
            }
        ]

        kn_data_view_fields = {}
        for view in data_views:
            view_id = view.get("id")
            concept_detail = view.get("concept_detail", {})
            data_properties = concept_detail.get("data_properties", [])
            if data_properties and view_id:
                field_names = []
                for prop in data_properties:
                    mapped_field = prop.get("mapped_field", {})
                    if mapped_field and mapped_field.get("name"):
                        field_names.append(mapped_field["name"])
                if field_names:
                    kn_data_view_fields[view_id] = field_names

        assert "view_1" in kn_data_view_fields
        assert "view_2" in kn_data_view_fields
        assert kn_data_view_fields["view_1"] == ["field_a", "field_b"]
        assert kn_data_view_fields["view_2"] == ["field_c"]

    def test_extract_kn_fields_empty_data_properties(self):
        """测试 data_properties 为空时的处理"""
        data_views = [
            {
                "id": "view_1",
                "view_name": "视图1",
                "concept_detail": {
                    "data_properties": []
                }
            }
        ]

        kn_data_view_fields = {}
        for view in data_views:
            view_id = view.get("id")
            concept_detail = view.get("concept_detail", {})
            data_properties = concept_detail.get("data_properties", [])
            if data_properties and view_id:
                field_names = []
                for prop in data_properties:
                    mapped_field = prop.get("mapped_field", {})
                    if mapped_field and mapped_field.get("name"):
                        field_names.append(mapped_field["name"])
                if field_names:
                    kn_data_view_fields[view_id] = field_names

        assert "view_1" not in kn_data_view_fields

    def test_extract_kn_fields_missing_mapped_field(self):
        """测试缺少 mapped_field 时的处理"""
        data_views = [
            {
                "id": "view_1",
                "view_name": "视图1",
                "concept_detail": {
                    "data_properties": [
                        {
                            "name": "prop_a",
                            "display_name": "属性A"
                            # 没有 mapped_field
                        }
                    ]
                }
            }
        ]

        kn_data_view_fields = {}
        for view in data_views:
            view_id = view.get("id")
            concept_detail = view.get("concept_detail", {})
            data_properties = concept_detail.get("data_properties", [])
            if data_properties and view_id:
                field_names = []
                for prop in data_properties:
                    mapped_field = prop.get("mapped_field", {})
                    if mapped_field and mapped_field.get("name"):
                        field_names.append(mapped_field["name"])
                if field_names:
                    kn_data_view_fields[view_id] = field_names

        assert "view_1" not in kn_data_view_fields

    def test_extract_kn_fields_no_concept_detail(self):
        """测试缺少 concept_detail 时的处理"""
        data_views = [
            {
                "id": "view_1",
                "view_name": "视图1"
                # 没有 concept_detail
            }
        ]

        kn_data_view_fields = {}
        for view in data_views:
            view_id = view.get("id")
            concept_detail = view.get("concept_detail", {})
            data_properties = concept_detail.get("data_properties", [])
            if data_properties and view_id:
                field_names = []
                for prop in data_properties:
                    mapped_field = prop.get("mapped_field", {})
                    if mapped_field and mapped_field.get("name"):
                        field_names.append(mapped_field["name"])
                if field_names:
                    kn_data_view_fields[view_id] = field_names

        assert "view_1" not in kn_data_view_fields


class TestRelationBackgroundBuilder:
    """测试关系背景信息构建"""

    def test_build_relation_background_with_relations(self):
        """测试从关系数据构建背景信息"""
        relations = [
            {
                "concept_id": "rel_1",
                "concept_name": "可用药物",
                "name": "available_drug",
                "source_object_type_id": "disease",
                "source_object_type_name": "疾病",
                "source_view_id": "view_disease_001",
                "target_object_type_id": "drug",
                "target_object_type_name": "药物",
                "target_view_id": "view_drug_001",
                "comment": ""
            },
            {
                "concept_id": "rel_2",
                "concept_name": "检查项",
                "name": "check_item",
                "source_object_type_id": "disease",
                "source_object_type_name": "疾病",
                "source_view_id": "",
                "target_object_type_id": "checklist",
                "target_object_type_name": "检查项目",
                "target_view_id": "view_checklist_001",
                "comment": "疾病相关检查"
            }
        ]

        relation_background = ""
        if relations:
            relation_descriptions = []
            for rel in relations:
                if rel.get("source_object_type_name") and rel.get("target_object_type_name"):
                    source_name = rel.get('source_object_type_name')
                    target_name = rel.get('target_object_type_name')
                    source_view_id = rel.get('source_view_id', '')
                    target_view_id = rel.get('target_view_id', '')

                    if source_view_id:
                        source_name = f"{source_name}(view_id: {source_view_id})"
                    if target_view_id:
                        target_name = f"{target_name}(view_id: {target_view_id})"

                    desc = f"- {source_name} 与 {target_name} 存在关系：{rel.get('concept_name', '')}"
                    if rel.get("comment"):
                        desc += f"（{rel.get('comment')}）"
                    relation_descriptions.append(desc)
            if relation_descriptions:
                relation_background = "\n数据视图之间的关系：\n" + "\n".join(relation_descriptions)

        assert "数据视图之间的关系" in relation_background
        assert "疾病(view_id: view_disease_001) 与 药物(view_id: view_drug_001) 存在关系：可用药物" in relation_background
        assert "疾病 与 检查项目(view_id: view_checklist_001) 存在关系：检查项（疾病相关检查）" in relation_background

    def test_build_relation_background_empty_relations(self):
        """测试空关系列表"""
        relations = []

        relation_background = ""
        if relations:
            relation_descriptions = []
            for rel in relations:
                if rel.get("source_object_type_name") and rel.get("target_object_type_name"):
                    desc = (f"- {rel.get('source_object_type_name')} 与 "
                            f"{rel.get('target_object_type_name')} 存在关系：{rel.get('concept_name', '')}")
                    if rel.get("comment"):
                        desc += f"（{rel.get('comment')}）"
                    relation_descriptions.append(desc)
            if relation_descriptions:
                relation_background = "\n数据视图之间的关系：\n" + "\n".join(relation_descriptions)

        assert relation_background == ""

    def test_build_relation_background_missing_object_type_name(self):
        """测试缺少对象类型名称时的处理"""
        relations = [
            {
                "concept_id": "rel_1",
                "concept_name": "可用药物",
                "name": "available_drug",
                "source_object_type_id": "disease",
                "source_object_type_name": "",  # 空
                "source_view_id": "",
                "target_object_type_id": "drug",
                "target_object_type_name": "药物",
                "target_view_id": "",
                "comment": ""
            }
        ]

        relation_background = ""
        if relations:
            relation_descriptions = []
            for rel in relations:
                if rel.get("source_object_type_name") and rel.get("target_object_type_name"):
                    source_name = rel.get('source_object_type_name')
                    target_name = rel.get('target_object_type_name')
                    source_view_id = rel.get('source_view_id', '')
                    target_view_id = rel.get('target_view_id', '')

                    if source_view_id:
                        source_name = f"{source_name}(view_id: {source_view_id})"
                    if target_view_id:
                        target_name = f"{target_name}(view_id: {target_view_id})"

                    desc = f"- {source_name} 与 {target_name} 存在关系：{rel.get('concept_name', '')}"
                    if rel.get("comment"):
                        desc += f"（{rel.get('comment')}）"
                    relation_descriptions.append(desc)
            if relation_descriptions:
                relation_background = "\n数据视图之间的关系：\n" + "\n".join(relation_descriptions)

        assert relation_background == ""

    def test_populate_relations_from_concept(self):
        """测试从概念中提取关系信息"""
        concept = {
            "concept_id": "checks",
            "concept_name": "检查项",
            "concept_type": "relation_type",
            "concept_detail": {
                "name": "check_item",
                "source_object_type_id": "disease",
                "source_object_type_name": "疾病",
                "target_object_type_id": "checklist",
                "target_object_type_name": "检查项目",
                "comment": "检查项目关系"
            }
        }

        # Simulate concept_data_view_mapping
        concept_data_view_mapping = {
            "disease": "view_disease_001",
            "checklist": "view_checklist_001"
        }

        concept_detail = concept.get("concept_detail", {})
        source_object_type_id = concept_detail.get("source_object_type_id", "")
        target_object_type_id = concept_detail.get("target_object_type_id", "")

        relation_info = {
            "concept_id": concept.get("concept_id", ""),
            "concept_name": concept.get("concept_name", ""),
            "name": concept_detail.get("name", ""),
            "source_object_type_id": source_object_type_id,
            "source_object_type_name": concept_detail.get("source_object_type_name", ""),
            "source_view_id": concept_data_view_mapping.get(source_object_type_id, ""),
            "target_object_type_id": target_object_type_id,
            "target_object_type_name": concept_detail.get("target_object_type_name", ""),
            "target_view_id": concept_data_view_mapping.get(target_object_type_id, ""),
            "comment": concept_detail.get("comment", "")
        }

        assert relation_info["concept_id"] == "checks"
        assert relation_info["concept_name"] == "检查项"
        assert relation_info["name"] == "check_item"
        assert relation_info["source_object_type_id"] == "disease"
        assert relation_info["source_object_type_name"] == "疾病"
        assert relation_info["source_view_id"] == "view_disease_001"
        assert relation_info["target_object_type_id"] == "checklist"
        assert relation_info["target_object_type_name"] == "检查项目"
        assert relation_info["target_view_id"] == "view_checklist_001"
        assert relation_info["comment"] == "检查项目关系"


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("DIP DataView 模块测试")
    print("=" * 60)

    test_classes = [
        TestDataViewKnFieldsFilter,
        TestKnFieldsFilterLogic,
        TestKnDataViewFieldsExtraction,
        TestRelationBackgroundBuilder,
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
